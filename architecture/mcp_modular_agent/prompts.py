"""
Prompt text for the Use Case 5 ReAct-style MCP controller.

The prompts here are intentionally narrow: the model chooses one operational
action at a time and returns JSON for logging/debugging. User-facing wording is
still produced by the existing explainer modules.
"""

SYSTEM_REACT_CONTROLLER = (
    "You are an explanation-tool controller for an AI depression screening "
    "study. Choose exactly one next tool action, or finish, using strict JSON "
    "only. Do not provide hidden reasoning. The reason field must be one short "
    "operational justification suitable for logs."
)

TOOL_DESCRIPTIONS = {
    "explain_shap": (
        "Use when the question asks which words, phrases, or features "
        "influenced the prediction, or why the model produced the prediction."
    ),
    "explain_rag": (
        "Use when the question asks which symptoms, behavioural patterns, or "
        "domain knowledge relate to the prediction."
    ),
    "explain_counterfactual": (
        "Use when the question asks what would have to change in the passage "
        "for the prediction to change."
    ),
}


def build_react_decision_prompt(
    user_text: str,
    user_question: str,
    prediction: dict,
    observations: list[dict],
    used_tools: list[str],
    available_tools: list[str],
    step: int,
    max_steps: int,
) -> str:
    observation_lines = []
    for obs in observations:
        summary = str(obs.get("observation_summary") or obs.get("result") or "").strip()
        observation_lines.append(
            f"- step {obs.get('step')}: {obs.get('tool')} -> {summary[:700]}"
        )
    observation_block = "\n".join(observation_lines) if observation_lines else "None yet"

    available_block = "\n".join(
        f"- {name}: {TOOL_DESCRIPTIONS.get(name, 'Available MCP tool.')}"
        for name in available_tools
    )

    prediction_label = prediction.get("label") or prediction.get("prediction") or "unknown"
    severity_score = prediction.get("severity_score", "")
    confidence = prediction.get("confidence", "")

    return f"""
User text:
"{user_text}"

Participant question:
"{user_question or 'Explain the prediction.'}"

Prediction context:
- predicted_label: {prediction_label}
- severity_score: {severity_score}
- confidence: {confidence}

Available actions:
{available_block}
- finish: Use when the available observations are sufficient to answer the question.

Already used tools:
{', '.join(used_tools) if used_tools else 'None'}

Previous observations:
{observation_block}

Step {step} of {max_steps}.

Choose exactly ONE next action. Normally do not repeat a tool that has already
been used. If the question asks for an overall explanation and only one narrow
evidence type has been observed, choose another complementary tool when steps
remain. If the evidence is sufficient, choose finish.

Return strict JSON only:
{{
  "action": "explain_shap | explain_rag | explain_counterfactual | finish",
  "reason": "one short operational justification",
  "evidence_sufficient": true
}}
""".strip()
