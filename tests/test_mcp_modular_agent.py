import asyncio
import importlib.util
import json
import pathlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.modules.setdefault("openai", types.SimpleNamespace(OpenAI=object))
sys.modules.setdefault("google", types.ModuleType("google"))
sys.modules.setdefault("google.generativeai", types.SimpleNamespace(configure=lambda **kwargs: None))

from architecture.mcp_modular_agent import agent_controller
from architecture.mcp_modular_agent import mcp_client
from architecture.mcp_modular_agent.mcp_client import _run_agent_loop, _run_fixed_tool
from architecture.mcp_modular_agent.serialization import deserialize_result


class FakeMCPClient:
    def __init__(self):
        self.calls = []

    async def list_tools(self):
        return [
            {"name": "predict_depression", "description": "Predict depression"},
            {"name": "explain_shap", "description": "SHAP evidence"},
            {"name": "explain_rag", "description": "RAG evidence"},
            {"name": "explain_counterfactual", "description": "Counterfactual evidence"},
        ]

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "predict_depression":
            return {
                "label": "moderate",
                "prediction": "moderate",
                "confidence": 0.7,
                "severity_score": 0.5,
            }
        return {"result_type": name.replace("explain_", ""), "data": {"text": arguments["text"]}}


class MCPModularAgentTests(unittest.TestCase):
    def test_mcp_server_defines_expected_tools(self):
        server_path = pathlib.Path("architecture/mcp_modular_agent/mcp_server.py")
        source = server_path.read_text(encoding="utf-8")
        for name in (
            "predict_depression",
            "explain_shap",
            "explain_rag",
            "explain_counterfactual",
        ):
            self.assertIn(f"def {name}", source)
        self.assertNotIn("def explain_hybrid", source)
        self.assertNotIn("generate_shap_explanation", source)
        self.assertNotIn("generate_rag_explanation", source)
        self.assertNotIn("generate_cf_explanation", source)
        self.assertIn("run_rag_pipeline(text, top_k=3)", source)
        self.assertIn("generate_counterfactuals(text, n_candidates=3, n_attempts=2)", source)
        self.assertGreaterEqual(source.count("@mcp.tool()"), 4)

    def test_mcp_sdk_server_import_when_dependency_available(self):
        if importlib.util.find_spec("mcp") is None:
            self.skipTest("mcp SDK is not installed in this environment")
        import architecture.mcp_modular_agent.mcp_server as server

        self.assertIsNotNone(server.mcp)

    def test_client_contract_can_invoke_required_tools(self):
        fake = FakeMCPClient()

        async def invoke_all():
            return [
                await fake.call_tool("predict_depression", {"text": "I feel sad."}),
                await fake.call_tool("explain_shap", {"text": "I feel sad."}),
                await fake.call_tool("explain_rag", {"text": "I feel sad."}),
                await fake.call_tool("explain_counterfactual", {"text": "I feel sad."}),
            ]

        results = asyncio.run(invoke_all())

        self.assertEqual(
            [name for name, _ in fake.calls],
            ["predict_depression", "explain_shap", "explain_rag", "explain_counterfactual"],
        )
        self.assertEqual(results[0]["label"], "moderate")
        self.assertTrue(all(result for result in results))

    def test_agent_discovers_and_invokes_mcp_tools_iteratively(self):
        fake = FakeMCPClient()
        decisions = [
            {"action": "explain_shap", "reason": "Start with word evidence.", "evidence_sufficient": False},
            {"action": "explain_rag", "reason": "Add symptom-theme evidence.", "evidence_sufficient": False},
            {"action": "finish", "reason": "Evidence is sufficient.", "evidence_sufficient": True},
        ]

        with (
            patch.object(agent_controller.llm_client, "call_gemini", side_effect=[json.dumps(d) for d in decisions]),
            patch.object(mcp_client, "deserialize_result", side_effect=lambda action, payload: SimpleNamespace(action=action)),
            patch.object(mcp_client, "_generate_final_explanation", return_value="final generated explanation") as final_gen,
        ):
            result = asyncio.run(
                _run_agent_loop(
                    client=fake,
                    user_text="I feel sad and tired.",
                    user_question="Provide an overall explanation.",
                    fallback=True,
                    top_k=2,
                )
            )

        self.assertEqual(
            [name for name, _ in fake.calls],
            ["predict_depression", "explain_shap", "explain_rag"],
        )
        self.assertEqual(result["executed_tools"], ["shap", "rag"])
        self.assertEqual([item["action"] for item in result["agent_trace"]], ["explain_shap", "explain_rag", "finish"])
        self.assertEqual(result["explanation"], "final generated explanation")
        final_gen.assert_called_once()

    def test_observation_from_first_tool_reaches_second_decision(self):
        fake = FakeMCPClient()
        seen_prompt = {}

        def fake_gemini(prompt, system=""):
            if "Previous observations:\nNone yet" in prompt:
                return '{"action":"explain_shap","reason":"Need word evidence.","evidence_sufficient":false}'
            seen_prompt["prompt"] = prompt
            return '{"action":"finish","reason":"Observed word evidence.","evidence_sufficient":true}'

        with (
            patch.object(agent_controller.llm_client, "call_gemini", side_effect=fake_gemini),
            patch.object(mcp_client, "deserialize_result", return_value=SimpleNamespace(action="explain_shap")),
            patch.object(mcp_client, "_generate_final_explanation", return_value="final generated explanation"),
        ):
            asyncio.run(
                _run_agent_loop(
                    client=fake,
                    user_text="I feel sad and tired.",
                    user_question="Why did it predict this?",
                    fallback=True,
                    top_k=2,
                )
            )

        self.assertIn("SHAP raw result", seen_prompt["prompt"])

    def test_agent_never_exceeds_max_steps_without_finish(self):
        fake = FakeMCPClient()

        def fake_gemini(prompt, system=""):
            if "explain_shap" not in prompt.split("Already used tools:", 1)[1].split("Previous observations:", 1)[0]:
                return '{"action":"explain_shap","reason":"Need word evidence.","evidence_sufficient":false}'
            if "explain_rag" not in prompt.split("Already used tools:", 1)[1].split("Previous observations:", 1)[0]:
                return '{"action":"explain_rag","reason":"Need symptom evidence.","evidence_sufficient":false}'
            return '{"action":"explain_counterfactual","reason":"Need change evidence.","evidence_sufficient":false}'

        with (
            patch.object(agent_controller.llm_client, "call_gemini", side_effect=fake_gemini),
            patch.object(mcp_client, "deserialize_result", side_effect=lambda action, payload: SimpleNamespace(action=action)),
            patch.object(mcp_client, "_generate_final_explanation", return_value="final generated explanation"),
        ):
            result = asyncio.run(
                _run_agent_loop(
                    client=fake,
                    user_text="I feel sad and tired.",
                    user_question="Provide a complete explanation.",
                    fallback=True,
                    top_k=2,
                )
            )

        self.assertLessEqual(len(result["agent_trace"]), agent_controller.MAX_STEPS)
        self.assertEqual(result["executed_tools"], ["shap", "rag", "counterfactual"])

    def test_fixed_tool_pipeline_uses_assigned_mcp_tool(self):
        fake = FakeMCPClient()

        with (
            patch.object(mcp_client, "deserialize_result", return_value=SimpleNamespace(action="explain_counterfactual")),
            patch.object(mcp_client, "_generate_final_explanation", return_value="final generated explanation") as final_gen,
        ):
            result = asyncio.run(
                _run_fixed_tool(
                    client=fake,
                    user_text="I feel sad and tired.",
                    selected_tool="counterfactual",
                    fallback=True,
                )
            )

        self.assertEqual(
            [name for name, _ in fake.calls],
            ["predict_depression", "explain_counterfactual"],
        )
        self.assertEqual(result["selected_tools"], ["counterfactual"])
        self.assertEqual(result["intent"], "actionable")
        self.assertEqual(result["explanation"], "final generated explanation")
        final_gen.assert_called_once()

    def test_fixed_hybrid_uses_three_raw_tools_and_one_final_generator(self):
        fake = FakeMCPClient()

        with (
            patch.object(mcp_client, "deserialize_result", side_effect=lambda action, payload: SimpleNamespace(action=action)),
            patch.object(mcp_client, "_generate_final_explanation", return_value="hybrid final explanation") as final_gen,
        ):
            result = asyncio.run(
                _run_fixed_tool(
                    client=fake,
                    user_text="I feel sad and tired.",
                    selected_tool="hybrid",
                    fallback=True,
                )
            )

        self.assertEqual(
            [name for name, _ in fake.calls],
            ["predict_depression", "explain_shap", "explain_rag", "explain_counterfactual"],
        )
        self.assertEqual(result["selected_tools"], ["hybrid"])
        self.assertEqual(result["explanation"], "hybrid final explanation")
        final_gen.assert_called_once()

    def test_controller_actions_exclude_prediction_and_hybrid(self):
        self.assertNotIn("predict_depression", agent_controller.VALID_ACTIONS)
        self.assertNotIn("explain_hybrid", agent_controller.VALID_ACTIONS)

    def test_mcp_v2_result_envelope_is_unwrapped(self):
        wrapped = {"result": {"result_type": "shap", "data": {"text": "x"}}}
        self.assertEqual(mcp_client._unwrap_mcp_result(wrapped)["result_type"], "shap")
        with patch("architecture.mcp_modular_agent.serialization.deserialize_shap_result", return_value="shap-object") as deser:
            self.assertEqual(deserialize_result("explain_shap", wrapped), "shap-object")
        deser.assert_called_once_with({"result_type": "shap", "data": {"text": "x"}})

    def test_single_raw_result_calls_matching_existing_generator(self):
        shap_generator = Mock(return_value="shap final")
        shap_module = types.SimpleNamespace(generate_shap_explanation=shap_generator)

        with patch.dict(sys.modules, {"architecture.shap_explainer.shap_explainer": shap_module}):
            explanation = mcp_client._generate_final_explanation(
                "text",
                {"label": "moderate"},
                {"shap": SimpleNamespace(kind="shap"), "rag": None, "counterfactual": None},
            )

        self.assertEqual(explanation, "shap final")
        shap_generator.assert_called_once()

    def test_three_raw_results_call_existing_hybrid_generator_once(self):
        class FakeHybridResult:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        fake_numpy = types.SimpleNamespace(
            asarray=lambda value, dtype=None: value,
        )
        hybrid_generator = Mock(return_value="hybrid final")
        hybrid_pipeline_module = types.SimpleNamespace(HybridResult=FakeHybridResult)
        hybrid_explainer_module = types.SimpleNamespace(generate_hybrid_explanation=hybrid_generator)

        with patch.dict(
            sys.modules,
            {
                "numpy": fake_numpy,
                "architecture.hybrid_shap_rag_counterfactual.hybrid_pipeline": hybrid_pipeline_module,
                "architecture.hybrid_shap_rag_counterfactual.hybrid_explainer": hybrid_explainer_module,
            },
        ):
            explanation = mcp_client._generate_final_explanation(
                "text",
                {"label": "moderate", "severity_score": 0.5},
                {
                    "shap": SimpleNamespace(pred_label_idx=1, pred_probs=[0.1, 0.8, 0.1]),
                    "rag": SimpleNamespace(),
                    "counterfactual": SimpleNamespace(),
                },
            )

        self.assertEqual(explanation, "hybrid final")
        hybrid_generator.assert_called_once()


if __name__ == "__main__":
    unittest.main()
