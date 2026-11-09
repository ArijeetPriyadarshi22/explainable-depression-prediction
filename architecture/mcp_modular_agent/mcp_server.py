"""
MCP server exposing existing XAI pipeline results as thin tools.

The server runs prediction/explanation pipelines and returns serialized raw
result objects. Participant-facing response generation stays client-side.
"""

from typing import Any, Dict

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover - exercised only without deps
    raise RuntimeError(
        "The official MCP Python SDK is required. Install project dependencies "
        "with: pip install -r requirements.txt"
    ) from exc

import numpy as np

from shared.depression_model import classify_severity, predict_proba
from architecture.mcp_modular_agent.serialization import (
    serialize_counterfactual_result,
    serialize_rag_result,
    serialize_shap_result,
)

mcp = MCPServer("agentic-mcp-xai")


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


@mcp.tool()
def predict_depression(text: str) -> Dict[str, Any]:
    """Return the existing depression prediction for the supplied text."""
    probs = predict_proba([text])[0]
    label, severity_score, reason = classify_severity(probs)
    idx = int(probs.argmax()) if probs is not None else 0
    confidence = float(probs[idx]) if probs is not None else 0.0
    return {
        "label": label,
        "prediction": label,
        "confidence": confidence,
        "severity_score": severity_score,
        "severity_reason": reason,
        "probabilities": _jsonable(probs),
    }


@mcp.tool()
def explain_shap(text: str) -> Dict[str, Any]:
    """Run the existing SHAP pipeline and return its serialized raw result."""
    from shared.depression_model import explain_with_shap

    result = explain_with_shap(text)
    return serialize_shap_result(result)


@mcp.tool()
def explain_rag(text: str) -> Dict[str, Any]:
    """Run the existing RAG pipeline with top_k=3 and return its raw result."""
    from architecture.rag_explainer.rag_explainer import run_rag_pipeline

    result = run_rag_pipeline(text, top_k=3)
    return serialize_rag_result(result)


@mcp.tool()
def explain_counterfactual(text: str) -> Dict[str, Any]:
    """Run the existing counterfactual pipeline and return its raw result."""
    from architecture.shap_counterfactual_explainer.cf_generator import generate_counterfactuals

    result = generate_counterfactuals(text, n_candidates=3, n_attempts=2)
    return serialize_counterfactual_result(result)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
