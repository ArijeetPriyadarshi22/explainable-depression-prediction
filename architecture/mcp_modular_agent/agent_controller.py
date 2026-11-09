"""
Lightweight ReAct-style controller for Use Case 5.

This module chooses one action at a time. It never runs explanation algorithms;
those are exposed through the MCP server and invoked by mcp_client.py.
"""

import json
import logging
from typing import Any, Dict, List

from shared import llm_client

from architecture.mcp_modular_agent.prompts import (
    SYSTEM_REACT_CONTROLLER,
    build_react_decision_prompt,
)

logger = logging.getLogger("mcp_modular_agent.controller")

MAX_STEPS = 3
VALID_ACTIONS = {
    "explain_shap",
    "explain_rag",
    "explain_counterfactual",
    "finish",
}
EXPLANATION_ACTIONS = {
    "explain_shap",
    "explain_rag",
    "explain_counterfactual",
}


def safe_json_parse(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("```"):
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _normalize_action(action: Any) -> str:
    aliases = {
        "shap": "explain_shap",
        "rag": "explain_rag",
        "cf": "explain_counterfactual",
        "counterfactual": "explain_counterfactual",
        "counter factual": "explain_counterfactual",
        "done": "finish",
    }
    normalized = aliases.get(str(action).strip().lower(), str(action).strip().lower())
    return normalized if normalized in VALID_ACTIONS else ""


def deterministic_fallback_action(
    user_question: str,
    observations: List[Dict[str, Any]],
    used_tools: List[str],
    available_tools: List[str],
) -> Dict[str, Any]:
    available = set(available_tools)
    used = set(used_tools)
    question = (user_question or "").lower()

    def choose(action: str, reason: str) -> Dict[str, Any]:
        if action in available and action not in used:
            return {"action": action, "reason": reason, "evidence_sufficient": False}
        return {"action": "finish", "reason": "No unused matching tool remains.", "evidence_sufficient": True}

    if observations:
        if any(word in question for word in ("overall", "complete", "comprehensive", "all", "full")):
            for action in ("explain_shap", "explain_rag", "explain_counterfactual"):
                if action in available and action not in used:
                    return choose(action, "Fallback adds complementary evidence for an overall question.")
        return {"action": "finish", "reason": "Fallback found available observations sufficient.", "evidence_sufficient": True}

    if any(word in question for word in ("change", "different", "shift", "alter")):
        return choose("explain_counterfactual", "Fallback selected wording-change evidence.")
    if any(word in question for word in ("symptom", "pattern", "theme", "behaviour", "behavior")):
        return choose("explain_rag", "Fallback selected symptom-theme evidence.")
    if any(word in question for word in ("overall", "complete", "comprehensive", "all", "full")):
        return choose("explain_shap", "Fallback starts overall explanation with word-level evidence.")
    return choose("explain_shap", "Fallback selected word-level prediction evidence.")


def decide_next_action(
    user_text: str,
    user_question: str,
    prediction: Dict[str, Any],
    observations: List[Dict[str, Any]],
    used_tools: List[str],
    available_tools: List[str],
    step: int,
    max_steps: int = MAX_STEPS,
) -> Dict[str, Any]:
    available = [tool for tool in available_tools if tool in VALID_ACTIONS]
    prompt = build_react_decision_prompt(
        user_text=user_text,
        user_question=user_question,
        prediction=prediction,
        observations=observations,
        used_tools=used_tools,
        available_tools=available,
        step=step,
        max_steps=max_steps,
    )

    try:
        raw = llm_client.call_gemini(prompt, system=SYSTEM_REACT_CONTROLLER)
        parsed = safe_json_parse(raw)
        action = _normalize_action(parsed.get("action"))
        if not action:
            raise ValueError(f"Unsupported action: {parsed.get('action')!r}")
        if action != "finish" and action not in available:
            raise ValueError(f"Action unavailable: {action}")
        if action in used_tools and action in EXPLANATION_ACTIONS:
            raise ValueError(f"Repeated action without explicit allowance: {action}")
        return {
            "action": action,
            "reason": str(parsed.get("reason", "")).strip()[:300],
            "evidence_sufficient": bool(parsed.get("evidence_sufficient", action == "finish")),
            "raw_decision": parsed,
            "fallback": False,
        }
    except Exception as exc:
        logger.warning("Controller decision failed; using deterministic fallback. Error: %s", exc)
        decision = deterministic_fallback_action(
            user_question=user_question,
            observations=observations,
            used_tools=used_tools,
            available_tools=available,
        )
        decision["raw_decision"] = {}
        decision["fallback"] = True
        return decision
