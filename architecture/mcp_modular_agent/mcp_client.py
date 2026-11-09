"""
Use Case 5: ReAct-style MCP agent/controller.

Flow:
  1) Connect to the local MCP server over stdio.
  2) Discover available tools.
  3) Get prediction through the MCP predict_depression tool.
  4) Ask the controller for exactly one next action.
  5) Call one MCP tool, record the observation, then reason again.
  6) Return the existing user-facing explanation text plus internal trace data.
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from threading import Thread
from typing import Any, Dict, List

from architecture.mcp_modular_agent.agent_controller import (
    MAX_STEPS,
    decide_next_action,
    deterministic_fallback_action,
)
from architecture.mcp_modular_agent.serialization import deserialize_result

logger = logging.getLogger("mcp_modular_agent")

TOOL_TO_SHORT_NAME = {
    "explain_shap": "shap",
    "explain_rag": "rag",
    "explain_counterfactual": "counterfactual",
}
SHORT_NAME_TO_TOOL = {value: key for key, value in TOOL_TO_SHORT_NAME.items()}
VALID_TOOLS = set(SHORT_NAME_TO_TOOL)
VALID_FIXED_TOOLS = VALID_TOOLS | {"hybrid"}
DEFAULT_QUESTION = "Explain the prediction."


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _server_env() -> dict:
    env = os.environ.copy()
    root = _project_root()
    env["PYTHONPATH"] = root + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _run_async_blocking(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict = {}

    def runner():
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:
            result["error"] = exc

    thread = Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")


def _extract_tool_payload(tool_result: Any) -> Any:
    for attr in ("structured_content", "structuredContent"):
        value = getattr(tool_result, attr, None)
        if value:
            return _unwrap_mcp_result(value)

    content = getattr(tool_result, "content", None)
    if content is None and isinstance(tool_result, dict):
        content = tool_result.get("content")

    if isinstance(content, list) and content:
        texts = []
        for item in content:
            text = getattr(item, "text", None)
            if text is None and isinstance(item, dict):
                text = item.get("text")
            if text is not None:
                texts.append(str(text))
        joined = "\n".join(texts).strip()
        if joined:
            try:
                return _unwrap_mcp_result(json.loads(joined))
            except Exception:
                return {"text": joined}

    return _unwrap_mcp_result(tool_result)


def _unwrap_mcp_result(payload: Any) -> Any:
    if isinstance(payload, dict) and set(payload.keys()) == {"result"}:
        return payload["result"]
    return payload


def _summarize_observation(payload: Any, limit: int = 260) -> str:
    if isinstance(payload, dict):
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        if payload.get("result_type") == "shap":
            text = f"SHAP raw result: prediction={data.get('pred_label')}, risk_tokens={data.get('risk_tokens', [])[:3]}"
        elif payload.get("result_type") == "rag":
            docs = data.get("retrieved_docs", [])
            themes = [doc.get("symptom_name", "") for doc in docs[:3]]
            text = f"RAG raw result: prediction={data.get('pred_label')}, themes={themes}"
        elif payload.get("result_type") == "counterfactual":
            best = data.get("best_cf") or {}
            text = (
                "Counterfactual raw result: "
                f"original={data.get('original_label')}, target={data.get('target_label')}, "
                f"best_label={best.get('label')}, flip={best.get('flip_success')}"
            )
        else:
            text = payload.get("text") or payload.get("prediction") or str(payload)
    else:
        text = str(payload)
    text = " ".join(str(text).split())
    return text[:limit]


def _prediction_index(prediction: Dict[str, Any], fallback_result: Any = None) -> int:
    probs = prediction.get("probabilities") or prediction.get("pred_probs")
    if probs:
        import numpy as np

        return int(np.asarray(probs, dtype=float).argmax())
    if fallback_result is not None and hasattr(fallback_result, "pred_label_idx"):
        return int(fallback_result.pred_label_idx)
    return 0


def _build_hybrid_result(user_text: str, prediction: Dict[str, Any], shap_result, rag_result, cf_result):
    import numpy as np

    from architecture.hybrid_shap_rag_counterfactual.hybrid_pipeline import HybridResult

    probs = prediction.get("probabilities") or []
    if not probs and shap_result is not None:
        probs = shap_result.pred_probs
    pred_label = prediction.get("label") or prediction.get("prediction") or getattr(shap_result, "pred_label", "")
    severity_score = prediction.get("severity_score", getattr(shap_result, "severity_score", 0.0))
    severity_reason = prediction.get("severity_reason", getattr(shap_result, "severity_reason", ""))
    return HybridResult(
        text=user_text,
        pred_label=pred_label,
        pred_label_idx=_prediction_index(prediction, fallback_result=shap_result),
        pred_probs=np.asarray(probs, dtype=float),
        severity_score=float(severity_score or 0.0),
        severity_reason=severity_reason or "",
        shap_result=shap_result,
        rag_result=rag_result,
        cf_result=cf_result,
        shap_error="" if shap_result is not None else "unavailable",
        rag_error="" if rag_result is not None else "unavailable",
        cf_error="" if cf_result is not None else "unavailable",
    )


def _generate_final_explanation(user_text: str, prediction: Dict[str, Any], raw_results: Dict[str, Any]) -> str:
    shap_result = raw_results.get("shap")
    rag_result = raw_results.get("rag")
    cf_result = raw_results.get("counterfactual")
    available = [name for name, value in raw_results.items() if value is not None]
    logger.info("Generating final Agentic XAI response from raw results: %s", available)

    if available == ["shap"]:
        from architecture.shap_explainer.shap_explainer import generate_shap_explanation

        logger.info("Final generator selected: generate_shap_explanation")
        return generate_shap_explanation(user_text, shap_result)
    if available == ["rag"]:
        from architecture.rag_explainer.rag_explainer import generate_rag_explanation

        logger.info("Final generator selected: generate_rag_explanation")
        return generate_rag_explanation(user_text, rag_result)
    if available == ["counterfactual"]:
        from architecture.shap_counterfactual_explainer.cf_explainer import generate_cf_explanation

        logger.info("Final generator selected: generate_cf_explanation")
        return generate_cf_explanation(user_text, cf_result)

    from architecture.hybrid_shap_rag_counterfactual.hybrid_explainer import generate_hybrid_explanation

    logger.info("Final generator selected: generate_hybrid_explanation")
    hybrid_result = _build_hybrid_result(
        user_text=user_text,
        prediction=prediction,
        shap_result=shap_result,
        rag_result=rag_result,
        cf_result=cf_result,
    )
    return generate_hybrid_explanation(user_text, hybrid_result)


def _fallback_prediction(user_text: str) -> Dict[str, Any]:
    from shared.depression_model import classify_severity, predict_proba

    probs = predict_proba([user_text])[0]
    label, severity_score, reason = classify_severity(probs)
    idx = int(probs.argmax()) if probs is not None else 0
    confidence = float(probs[idx]) if probs is not None else 0.0
    return {
        "label": label,
        "prediction": label,
        "confidence": confidence,
        "severity_score": severity_score,
        "severity_reason": reason,
        "probabilities": probs.tolist() if hasattr(probs, "tolist") else probs,
    }


@asynccontextmanager
async def _stdio_mcp_session():
    try:
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ImportError as exc:
        raise RuntimeError(
            "The official MCP Python SDK is required. Install project dependencies "
            "with: pip install -r requirements.txt"
        ) from exc

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "architecture.mcp_modular_agent.mcp_server"],
        cwd=_project_root(),
        env=_server_env(),
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


class MCPToolClient:
    def __init__(self, session):
        self.session = session

    async def list_tools(self) -> List[dict]:
        result = await self.session.list_tools()
        tools = getattr(result, "tools", result)
        return [
            {
                "name": getattr(tool, "name", ""),
                "description": getattr(tool, "description", ""),
            }
            for tool in tools
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        result = await self.session.call_tool(name, arguments)
        return _extract_tool_payload(result)


def _tool_arguments(action: str, user_text: str, top_k: int) -> Dict[str, Any]:
    return {"text": user_text}


def _trace_entry(step: int, action: str, reason: str, payload: Any = None) -> Dict[str, Any]:
    entry = {
        "step": step,
        "action": action,
        "reason": reason,
    }
    if payload is not None:
        entry["observation_summary"] = _summarize_observation(payload)
    return entry


async def _run_agent_loop(
    client: MCPToolClient,
    user_text: str,
    user_question: str,
    fallback: bool,
    top_k: int,
) -> Dict[str, Any]:
    discovered = await client.list_tools()
    available_tool_names = [tool["name"] for tool in discovered if tool.get("name")]
    available_actions = [
        name for name in available_tool_names
        if name in {"explain_shap", "explain_rag", "explain_counterfactual"}
    ]
    logger.info("MCP tools discovered: %s", available_tool_names)
    logger.info("MCP explanation actions available: %s", available_actions)

    errors: List[str] = []
    try:
        logger.info("Calling MCP tool: predict_depression")
        prediction = await client.call_tool("predict_depression", {"text": user_text})
        logger.info(
            "MCP prediction observed: label=%s confidence=%s severity_score=%s",
            prediction.get("label") if isinstance(prediction, dict) else "",
            prediction.get("confidence") if isinstance(prediction, dict) else "",
            prediction.get("severity_score") if isinstance(prediction, dict) else "",
        )
    except Exception as exc:
        if not fallback:
            raise
        logger.warning("MCP prediction failed; using local prediction fallback: %s", exc)
        prediction = _fallback_prediction(user_text)
        errors.append(f"predict_depression fallback: {exc}")

    observations: List[Dict[str, Any]] = []
    tool_outputs: List[Dict[str, Any]] = []
    shap_result = None
    rag_result = None
    counterfactual_result = None
    used_actions: List[str] = []
    agent_trace: List[Dict[str, Any]] = []

    for step in range(1, MAX_STEPS + 1):
        decision = decide_next_action(
            user_text=user_text,
            user_question=user_question,
            prediction=prediction if isinstance(prediction, dict) else {},
            observations=observations,
            used_tools=used_actions,
            available_tools=available_actions,
            step=step,
            max_steps=MAX_STEPS,
        )

        action = decision["action"]
        reason = decision.get("reason", "")
        logger.info("ReAct decision step=%s action=%s reason=%s", step, action, reason)
        if action == "finish":
            agent_trace.append(_trace_entry(step, "finish", reason))
            break

        if action not in available_actions:
            if not fallback:
                raise RuntimeError(f"Controller selected unavailable MCP tool: {action}")
            decision = deterministic_fallback_action(
                user_question=user_question,
                observations=observations,
                used_tools=used_actions,
                available_tools=available_actions,
            )
            action = decision["action"]
            reason = decision.get("reason", "")
            if action == "finish":
                agent_trace.append(_trace_entry(step, "finish", reason))
                break

        try:
            logger.info("Calling MCP tool: %s", action)
            payload = await client.call_tool(action, _tool_arguments(action, user_text, top_k))
        except Exception as exc:
            errors.append(f"{action}: {exc}")
            logger.warning("MCP tool failed (%s): %s", action, exc)
            if not fallback:
                raise
            continue

        used_actions.append(action)
        output = payload if isinstance(payload, dict) else {"text": str(payload)}
        raw_result = deserialize_result(action, output)
        short_tool = TOOL_TO_SHORT_NAME.get(action, action)
        if short_tool == "shap":
            shap_result = raw_result
        elif short_tool == "rag":
            rag_result = raw_result
        elif short_tool == "counterfactual":
            counterfactual_result = raw_result
        tool_outputs.append({
            "tool": short_tool,
            "action": action,
            "raw_result_type": output.get("result_type"),
            "result": output,
        })
        observation = {
            "step": step,
            "tool": action,
            "result": output,
            "observation_summary": _summarize_observation(output),
        }
        logger.info(
            "MCP observation step=%s tool=%s summary=%s",
            step,
            action,
            observation["observation_summary"],
        )
        observations.append(observation)
        agent_trace.append(_trace_entry(step, action, reason, output))

    if not tool_outputs and fallback and "explain_shap" in available_actions:
        payload = await client.call_tool("explain_shap", {"text": user_text})
        output = payload if isinstance(payload, dict) else {"text": str(payload)}
        shap_result = deserialize_result("explain_shap", output)
        tool_outputs.append({
            "tool": "shap",
            "action": "explain_shap",
            "raw_result_type": output.get("result_type"),
            "result": output,
        })
        agent_trace.append(_trace_entry(1, "explain_shap", "Fallback ensured one explanation was available.", output))
        used_actions.append("explain_shap")
        errors.append("fallback: used shap explanation")

    if not tool_outputs:
        raise RuntimeError(f"No MCP explanation tools produced output. Errors: {' | '.join(errors)}")

    raw_results = {
        "shap": shap_result,
        "rag": rag_result,
        "counterfactual": counterfactual_result,
    }
    explanation = _generate_final_explanation(user_text, prediction if isinstance(prediction, dict) else {}, raw_results)
    selected_tools = [output["tool"] for output in tool_outputs]

    return {
        "selected_server": "+".join(selected_tools),
        "selected_tools": selected_tools,
        "executed_tools": selected_tools,
        "fallback_used": any("fallback" in e for e in errors) or any(item.get("reason", "").lower().startswith("fallback") for item in agent_trace),
        "prediction": prediction.get("label") if isinstance(prediction, dict) else "",
        "confidence": prediction.get("confidence") if isinstance(prediction, dict) else None,
        "severity_score": prediction.get("severity_score") if isinstance(prediction, dict) else None,
        "intent": "react",
        "planner_json": None,
        "planner_validation": None,
        "explanation": explanation,
        "tool_outputs": tool_outputs,
        "raw_results": raw_results,
        "observations": observations,
        "agent_trace": agent_trace,
        "rationale": agent_trace[-1]["reason"] if agent_trace else "",
        "errors": errors,
        "available_tools": available_tool_names,
    }


async def _run_fixed_tool(
    client: MCPToolClient,
    user_text: str,
    selected_tool: str,
    fallback: bool,
) -> Dict[str, Any]:
    discovered = await client.list_tools()
    available_tool_names = [tool["name"] for tool in discovered if tool.get("name")]
    errors: List[str] = []
    shap_result = None
    rag_result = None
    counterfactual_result = None
    tool_outputs: List[Dict[str, Any]] = []
    observations: List[Dict[str, Any]] = []
    trace: List[Dict[str, Any]] = []

    logger.info("MCP tools discovered: %s", available_tool_names)
    logger.info("Calling MCP tool: predict_depression")
    prediction = await client.call_tool("predict_depression", {"text": user_text})
    logger.info(
        "MCP prediction observed: label=%s confidence=%s severity_score=%s",
        prediction.get("label") if isinstance(prediction, dict) else "",
        prediction.get("confidence") if isinstance(prediction, dict) else "",
        prediction.get("severity_score") if isinstance(prediction, dict) else "",
    )

    actions = (
        ["explain_shap", "explain_rag", "explain_counterfactual"]
        if selected_tool == "hybrid" else
        [SHORT_NAME_TO_TOOL[selected_tool]]
    )

    for step, action in enumerate(actions, 1):
        try:
            logger.info("Fixed Agentic XAI step=%s selected_tool=%s calling=%s", step, selected_tool, action)
            payload = await client.call_tool(action, _tool_arguments(action, user_text, top_k=3))
        except Exception as exc:
            if not fallback:
                raise
            errors.append(f"{action}: {exc}")
            if selected_tool != "hybrid":
                payload = await client.call_tool("explain_shap", {"text": user_text})
                selected_tool = "shap"
                action = "explain_shap"
                errors.append("fallback: used shap raw result")
            else:
                continue

        output = payload if isinstance(payload, dict) else {"text": str(payload)}
        short_tool = TOOL_TO_SHORT_NAME.get(action, action)
        raw_result = deserialize_result(action, output)
        if short_tool == "shap":
            shap_result = raw_result
        elif short_tool == "rag":
            rag_result = raw_result
        elif short_tool == "counterfactual":
            counterfactual_result = raw_result
        tool_outputs.append({
            "tool": short_tool,
            "action": action,
            "raw_result_type": output.get("result_type"),
            "result": output,
        })
        observation = {
            "step": step,
            "tool": action,
            "result": output,
            "observation_summary": _summarize_observation(output),
        }
        logger.info(
            "MCP observation step=%s tool=%s summary=%s",
            step,
            action,
            observation["observation_summary"],
        )
        observations.append(observation)
        trace.append(_trace_entry(step, action, "Fixed controlled study mapping.", output))

    if not tool_outputs:
        raise RuntimeError(f"No MCP explanation tools produced output. Errors: {' | '.join(errors)}")

    raw_results = {
        "shap": shap_result,
        "rag": rag_result,
        "counterfactual": counterfactual_result,
    }
    explanation = _generate_final_explanation(user_text, prediction if isinstance(prediction, dict) else {}, raw_results)
    intent_by_tool = {
        "shap": "prediction_reason",
        "rag": "knowledge",
        "counterfactual": "actionable",
        "hybrid": "hybrid",
    }

    return {
        "selected_server": selected_tool,
        "selected_tools": [selected_tool],
        "executed_tools": [selected_tool],
        "fallback_used": any(e.startswith("fallback:") for e in errors),
        "prediction": prediction.get("label") if isinstance(prediction, dict) else "",
        "confidence": prediction.get("confidence") if isinstance(prediction, dict) else None,
        "severity_score": prediction.get("severity_score") if isinstance(prediction, dict) else None,
        "intent": intent_by_tool[selected_tool],
        "planner_json": None,
        "planner_validation": None,
        "explanation": explanation,
        "tool_outputs": tool_outputs,
        "raw_results": raw_results,
        "observations": observations,
        "agent_trace": trace,
        "rationale": "Fixed controlled study mapping.",
        "errors": errors,
        "available_tools": available_tool_names,
    }


async def run_mcp_pipeline_async(
    user_text: str,
    fallback: bool = True,
    top_k: int = 2,
    user_question: str = "",
) -> Dict[str, Any]:
    async with _stdio_mcp_session() as session:
        client = MCPToolClient(session)
        return await _run_agent_loop(
            client=client,
            user_text=user_text,
            user_question=user_question or DEFAULT_QUESTION,
            fallback=fallback,
            top_k=top_k,
        )


def run_mcp_pipeline(
    user_text: str,
    fallback: bool = True,
    top_k: int = 2,
    user_question: str = "",
) -> Dict[str, Any]:
    """
    Backward-compatible synchronous entry point for Use Case 5.
    """
    return _run_async_blocking(
        run_mcp_pipeline_async(
            user_text=user_text,
            fallback=fallback,
            top_k=top_k,
            user_question=user_question,
        )
    )


async def run_fixed_tool_pipeline_async(
    user_text: str,
    question_type: str,
    user_question: str,
    fallback: bool = True,
) -> Dict[str, Any]:
    selected_tool = str(question_type).strip().lower()
    if selected_tool not in VALID_FIXED_TOOLS:
        raise ValueError(f"Unsupported fixed question_type={question_type!r}")

    async with _stdio_mcp_session() as session:
        client = MCPToolClient(session)
        return await _run_fixed_tool(
            client=client,
            user_text=user_text,
            selected_tool=selected_tool,
            fallback=fallback,
        )


def run_fixed_tool_pipeline(
    user_text: str,
    question_type: str,
    user_question: str,
    fallback: bool = True,
) -> Dict[str, Any]:
    """
    Controlled study generation path.

    The mapping remains fixed by question type, but execution now goes through
    the MCP server instead of directly importing explanation implementations.
    """
    return _run_async_blocking(
        run_fixed_tool_pipeline_async(
            user_text=user_text,
            question_type=question_type,
            user_question=user_question,
            fallback=fallback,
        )
    )
