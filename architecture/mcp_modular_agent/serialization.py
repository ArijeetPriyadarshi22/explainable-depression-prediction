"""
JSON serialization for MCP transport of existing XAI result dataclasses.

The server serializes original pipeline result objects. The client reconstructs
the same result classes expected by the existing response generators.
"""

from typing import Any, Dict


def _jsonable(value: Any) -> Any:
    try:
        import numpy as np

        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
    except ImportError:
        pass
    if isinstance(value, dict):
        return {key: _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _candidate_from_payload(candidate: dict | None) -> dict | None:
    import numpy as np

    if candidate is None:
        return None
    restored = dict(candidate)
    if "probs" in restored and restored["probs"] is not None:
        restored["probs"] = np.asarray(restored["probs"], dtype=float)
    return restored


def serialize_shap_result(result) -> Dict[str, Any]:
    return {
        "result_type": "shap",
        "data": {
            "text": result.text,
            "tokens": result.tokens,
            "shap_matrix": _jsonable(result.shap_matrix),
            "pred_label_idx": result.pred_label_idx,
            "pred_label": result.pred_label,
            "pred_probs": _jsonable(result.pred_probs),
            "severity_score": result.severity_score,
            "severity_reason": result.severity_reason,
            "top_tokens": _jsonable(result.top_tokens),
            "risk_tokens": _jsonable(result.risk_tokens),
            "protective_tokens": _jsonable(result.protective_tokens),
        },
    }


def deserialize_shap_result(payload: Dict[str, Any]):
    import numpy as np

    from shared.depression_model import SHAPResult

    data = payload.get("data", payload)
    return SHAPResult(
        text=data["text"],
        tokens=list(data.get("tokens") or []),
        shap_matrix=np.asarray(data.get("shap_matrix") or [], dtype=float),
        pred_label_idx=int(data.get("pred_label_idx", 0)),
        pred_label=data.get("pred_label", ""),
        pred_probs=np.asarray(data.get("pred_probs") or [], dtype=float),
        severity_score=float(data.get("severity_score", 0.0)),
        severity_reason=data.get("severity_reason", ""),
        top_tokens=list(data.get("top_tokens") or []),
        risk_tokens=list(data.get("risk_tokens") or []),
        protective_tokens=list(data.get("protective_tokens") or []),
    )


def serialize_rag_result(result) -> Dict[str, Any]:
    return {
        "result_type": "rag",
        "data": {
            "text": result.text,
            "pred_label": result.pred_label,
            "pred_label_idx": result.pred_label_idx,
            "pred_probs": _jsonable(result.pred_probs),
            "severity_score": result.severity_score,
            "severity_reason": result.severity_reason,
            "retrieved_docs": [
                {
                    "symptom_name": doc.symptom_name,
                    "symptom_type": doc.symptom_type,
                    "clinical_definition": doc.clinical_definition,
                    "natural_language_patterns": doc.natural_language_patterns,
                    "functional_impact_examples": doc.functional_impact_examples,
                    "severity_indicators": doc.severity_indicators,
                    "denial_patterns": doc.denial_patterns,
                    "distance": doc.distance,
                }
                for doc in result.retrieved_docs
            ],
        },
    }


def deserialize_rag_result(payload: Dict[str, Any]):
    import numpy as np

    from architecture.rag_explainer.rag_explainer import RAGResult
    from architecture.rag_explainer.rag_retriever import RetrievedDoc

    data = payload.get("data", payload)
    docs = [
        RetrievedDoc(
            symptom_name=doc.get("symptom_name", ""),
            symptom_type=doc.get("symptom_type", ""),
            clinical_definition=doc.get("clinical_definition", ""),
            natural_language_patterns=list(doc.get("natural_language_patterns") or []),
            functional_impact_examples=list(doc.get("functional_impact_examples") or []),
            severity_indicators=list(doc.get("severity_indicators") or []),
            denial_patterns=list(doc.get("denial_patterns") or []),
            distance=float(doc.get("distance", 0.0)),
        )
        for doc in data.get("retrieved_docs", [])
    ]
    return RAGResult(
        text=data["text"],
        pred_label=data.get("pred_label", ""),
        pred_label_idx=int(data.get("pred_label_idx", 0)),
        pred_probs=np.asarray(data.get("pred_probs") or [], dtype=float),
        severity_score=float(data.get("severity_score", 0.0)),
        severity_reason=data.get("severity_reason", ""),
        retrieved_docs=docs,
    )


def serialize_counterfactual_result(result) -> Dict[str, Any]:
    return {
        "result_type": "counterfactual",
        "data": {
            "original_text": result.original_text,
            "original_label": result.original_label,
            "original_probs": _jsonable(result.original_probs),
            "severity_score": result.severity_score,
            "target_label": result.target_label,
            "candidates": _jsonable(result.candidates),
            "best_cf": _jsonable(result.best_cf),
            "shap_guided_tokens": _jsonable(result.shap_guided_tokens),
            "already_well": result.already_well,
        },
    }


def deserialize_counterfactual_result(payload: Dict[str, Any]):
    import numpy as np

    from architecture.shap_counterfactual_explainer.cf_generator import CounterfactualResult

    data = payload.get("data", payload)
    return CounterfactualResult(
        original_text=data["original_text"],
        original_label=data.get("original_label", ""),
        original_probs=np.asarray(data.get("original_probs") or [], dtype=float),
        severity_score=float(data.get("severity_score", 0.0)),
        target_label=data.get("target_label", ""),
        candidates=[
            _candidate_from_payload(candidate)
            for candidate in data.get("candidates", [])
        ],
        best_cf=_candidate_from_payload(data.get("best_cf")),
        shap_guided_tokens=list(data.get("shap_guided_tokens") or []),
        already_well=bool(data.get("already_well", False)),
    )


def deserialize_result(action: str, payload: Dict[str, Any]):
    if isinstance(payload, dict) and set(payload.keys()) == {"result"}:
        payload = payload["result"]
    result_type = payload.get("result_type")
    if action == "explain_shap" or result_type == "shap":
        return deserialize_shap_result(payload)
    if action == "explain_rag" or result_type == "rag":
        return deserialize_rag_result(payload)
    if action == "explain_counterfactual" or result_type == "counterfactual":
        return deserialize_counterfactual_result(payload)
    raise ValueError(f"Unsupported serialized result type for action={action!r}")
