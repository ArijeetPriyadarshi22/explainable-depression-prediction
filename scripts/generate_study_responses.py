#!/usr/bin/env python
"""
Generate saved user-study responses for every passage, question, and system.

The study bot should read the generated JSON and must not call live generation
during the final user study.
"""

import argparse
import logging
import os
import re
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from shared.training_examples import PARAGRAPHS, get_cached_prediction
from study.response_store import (
    AGENTIC_TOOL_BY_QUESTION,
    QUESTION_TEXTS,
    SCHEMA_VERSION,
    SYSTEM_AGENTIC_XAI,
    SYSTEM_MENTALLAMA,
    SYSTEMS,
    atomic_write_json,
    empty_payload,
    load_payload,
)


logger = logging.getLogger("generate_study_responses")

_MENTALLAMA_PIPELINE = None
_MENTALLAMA_DEFAULT_CACHE_DIR = "/scratch/apriyadar/huggingface"
_GEMINI_DELAY_SECONDS = 40
_GEMINI_MAX_ATTEMPTS = 1
_ORIGINAL_CALL_GEMINI = None


def _extract_status_code(exc: Exception) -> int | None:
    for attr in ("status_code", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    response = getattr(exc, "response", None)
    value = getattr(response, "status_code", None)
    if isinstance(value, int):
        return value
    match = re.search(r"\b(429|5\d\d|4\d\d)\b", str(exc))
    return int(match.group(1)) if match else None


def _short_error_message(exc: Exception, limit: int = 300) -> str:
    message = re.sub(r"\s+", " ", str(exc)).strip()
    return message[:limit]


def _call_gemini_with_delay_and_retry(prompt: str, system: str = "") -> str:
    if _ORIGINAL_CALL_GEMINI is None:
        raise RuntimeError("Gemini guard was not initialized.")

    last_exc = None
    for attempt in range(1, _GEMINI_MAX_ATTEMPTS + 1):
        logger.info(
            "Waiting %d seconds before Gemini request (attempt %d/%d).",
            _GEMINI_DELAY_SECONDS,
            attempt,
            _GEMINI_MAX_ATTEMPTS,
        )
        time.sleep(_GEMINI_DELAY_SECONDS)
        try:
            return _ORIGINAL_CALL_GEMINI(prompt, system=system)
        except Exception as exc:
            last_exc = exc
            status_code = _extract_status_code(exc)
            if status_code != 429 or attempt == _GEMINI_MAX_ATTEMPTS:
                raise
            logger.warning("Gemini rate limit hit (429). Retrying after delay.")

    raise last_exc


def _install_gemini_call_guard() -> None:
    global _ORIGINAL_CALL_GEMINI

    import shared.llm_client as llm_client

    if _ORIGINAL_CALL_GEMINI is None:
        _ORIGINAL_CALL_GEMINI = llm_client.call_gemini

    llm_client.call_gemini = _call_gemini_with_delay_and_retry
    for module_name in (
        "architecture.mcp_modular_agent.mcp_client",
        "architecture.shap_counterfactual_explainer.cf_generator",
        "architecture.shap_counterfactual_explainer.cf_explainer",
        "architecture.shap_explainer.shap_explainer",
        "architecture.rag_explainer.rag_explainer",
        "architecture.hybrid_shap_rag_counterfactual.hybrid_explainer",
    ):
        module = sys.modules.get(module_name)
        if module is not None and hasattr(module, "call_gemini"):
            module.call_gemini = _call_gemini_with_delay_and_retry


def _prediction_from_text(passage_id: str, text: str) -> tuple[str, float]:
    cached_label, cached_conf = get_cached_prediction(passage_id)
    if cached_label is not None and cached_conf is not None:
        return cached_label, float(cached_conf)
    from shared.depression_model import classify_severity, predict_proba

    probs = predict_proba([text])[0]
    label, _, _ = classify_severity(probs)
    idx = int(probs.argmax()) if probs is not None else 0
    conf = float(probs[idx]) if probs is not None else 0.0
    return label, conf


def _clean_mentallama_answer(answer: str) -> str:
    answer = (answer or "").strip()
    answer = re.sub(
        r"^\s*(?:[?¿]\s*)?(?:reasoning|reason|answer|response)\s*:\s*",
        "",
        answer,
        flags=re.IGNORECASE,
    ).strip()
    return answer


def _get_mentallama_pipeline():
    global _MENTALLAMA_PIPELINE
    if _MENTALLAMA_PIPELINE is not None:
        return _MENTALLAMA_PIPELINE

    import torch
    from transformers import LlamaForCausalLM, LlamaTokenizer

    cache_dir = os.environ.get("MENTALLAMA_CACHE_DIR", _MENTALLAMA_DEFAULT_CACHE_DIR)
    os.environ.setdefault("HF_HOME", cache_dir)
    os.environ.setdefault("HF_HUB_CACHE", os.path.join(cache_dir, "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", os.path.join(cache_dir, "transformers"))
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.makedirs(cache_dir, exist_ok=True)

    model_id = os.environ.get("MENTALLAMA_MODEL_ID", "klyang/MentaLLaMA-chat-7B")
    load_kwargs = {
        "cache_dir": cache_dir,
        "local_files_only": True,
        "use_safetensors": False,
    }

    tokenizer = LlamaTokenizer.from_pretrained(model_id, **load_kwargs)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs = dict(load_kwargs)
    torch_dtype = os.environ.get("MENTALLAMA_TORCH_DTYPE", "").strip()
    if torch_dtype:
        if not hasattr(torch, torch_dtype):
            raise ValueError(f"Unsupported MENTALLAMA_TORCH_DTYPE={torch_dtype!r}")
        model_kwargs["torch_dtype"] = getattr(torch, torch_dtype)
    model_kwargs["device_map"] = "auto"
    offload_dir = os.path.join(cache_dir, "offload")
    os.makedirs(offload_dir, exist_ok=True)
    model_kwargs["offload_folder"] = offload_dir
    model_kwargs["offload_state_dict"] = True

    model = LlamaForCausalLM.from_pretrained(model_id, **model_kwargs)
    device = next(model.parameters()).device
    model.eval()
    _MENTALLAMA_PIPELINE = tokenizer, model, device
    return _MENTALLAMA_PIPELINE


def _run_mentallama_answer(passage_text: str, question_text: str) -> str:
    tokenizer, model, device = _get_mentallama_pipeline()
    model_input = f"Consider this post: {passage_text.strip()} Question: {question_text.strip()}"
    inputs = tokenizer(
        model_input,
        return_tensors="pt",
        max_length=int(os.environ.get("MENTALLAMA_MAX_INPUT_TOKENS", "2048")),
        truncation=True,
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    do_sample = os.environ.get("MENTALLAMA_DO_SAMPLE", "false").lower() == "true"
    generation_kwargs = {
        "max_new_tokens": int(os.environ.get("MENTALLAMA_MAX_NEW_TOKENS", "256")),
        "do_sample": do_sample,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if do_sample:
        generation_kwargs["temperature"] = float(os.environ.get("MENTALLAMA_TEMPERATURE", "0.7"))

    outputs = model.generate(**inputs, **generation_kwargs)
    generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    answer = _clean_mentallama_answer(tokenizer.decode(generated_tokens, skip_special_tokens=True))
    return answer or "No response returned."


def _run_agentic_xai_answer(passage_text: str, question_type: str, question_text: str) -> dict[str, Any]:
    _install_gemini_call_guard()
    from architecture.mcp_modular_agent import mcp_client
    _install_gemini_call_guard()

    return mcp_client.run_fixed_tool_pipeline(
        passage_text,
        question_type=question_type,
        user_question=question_text,
        fallback=True,
    )


def _validate_unique_passage_ids(passages: list[dict]) -> None:
    seen = set()
    duplicates = []
    for passage in passages:
        passage_id = passage.get("id")
        if passage_id in seen:
            duplicates.append(passage_id)
        seen.add(passage_id)
    if duplicates:
        raise ValueError(f"Duplicate passage IDs found: {', '.join(sorted(set(duplicates)))}")


def _filter_passages(passage_id: str | None) -> list[dict]:
    passages = list(PARAGRAPHS)
    _validate_unique_passage_ids(passages)
    if passage_id:
        passages = [p for p in passages if p.get("id") == passage_id]
        if not passages:
            raise ValueError(f"No passage found with id={passage_id!r}")
    return passages


def _record_for_passage(payload: dict, passage: dict) -> dict:
    passage_id = passage["id"]
    for record in payload["records"]:
        if record.get("id") == passage_id:
            if "prediction" not in record:
                record["prediction"] = {
                    "label": record.pop("prediction_label", ""),
                    "confidence": record.pop("prediction_confidence", None),
                }
            if "responses" not in record:
                record["responses"] = record.pop("questions", [])
            return record

    label, conf = _prediction_from_text(passage_id, passage.get("text") or "")
    record = {
        "id": passage_id,
        "text": passage.get("text") or "",
        "severity": passage.get("severity", ""),
        "prediction": {
            "label": label,
            "confidence": conf,
        },
        "responses": [],
    }
    payload["records"].append(record)
    return record


def _question_entry(record: dict, question_type: str) -> dict:
    question_text = QUESTION_TEXTS[question_type]
    record.setdefault("responses", record.pop("questions", []))
    for entry in record["responses"]:
        if entry.get("question") == question_text or entry.get("type") == question_type:
            entry.pop("type", None)
            entry["question"] = question_text
            entry.setdefault(SYSTEM_AGENTIC_XAI, {"status": "missing", "response": None})
            entry.setdefault(SYSTEM_MENTALLAMA, {"status": "missing", "response": None})
            return entry
    entry = {
        "question": question_text,
        SYSTEM_AGENTIC_XAI: {
            "status": "missing",
            "response": None,
        },
        SYSTEM_MENTALLAMA: {
            "status": "missing",
            "response": None,
        },
    }
    record["responses"].append(entry)
    return entry


def _system_entry(question_entry: dict, system: str) -> dict:
    return question_entry.setdefault(system, {"status": "missing", "response": None})


def _is_done(entry: dict) -> bool:
    return entry.get("status") == "success" and bool(entry.get("response"))


def _should_generate(entry: dict, overwrite: bool, retry_failed: bool) -> bool:
    if overwrite:
        return True
    if _is_done(entry):
        return False
    if entry.get("status") == "error":
        return True
    return True


def _save_success(question_entry: dict, system: str, response: str, question_type: str) -> None:
    entry = {
        "status": "success",
        "response": response,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if system == SYSTEM_AGENTIC_XAI:
        entry["selected_tool"] = AGENTIC_TOOL_BY_QUESTION[question_type]
    question_entry[system] = entry


def _save_error(question_entry: dict, system: str, exc: Exception) -> None:
    question_entry[system] = {
        "status": "error",
        "response": None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "error": {
            "type": exc.__class__.__name__,
            "status_code": _extract_status_code(exc),
            "message": _short_error_message(exc),
        },
    }


def _generate_one(system: str, passage: dict, question_type: str, question_text: str) -> tuple[str, dict[str, Any]]:
    if system == SYSTEM_AGENTIC_XAI:
        result = _run_agentic_xai_answer(passage["text"], question_type, question_text)
        return result.get("explanation", "") or "No explanation returned.", {
            "agentic_xai_selected_tool": AGENTIC_TOOL_BY_QUESTION[question_type],
            "agentic_xai_result": result,
        }
    if system == SYSTEM_MENTALLAMA:
        return _run_mentallama_answer(passage["text"], question_text), {
            "model_input_format": "Consider this post: {post} Question: {question}",
        }
    raise ValueError(f"Unsupported system={system!r}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--systems", nargs="+", choices=SYSTEMS, default=list(SYSTEMS))
    parser.add_argument("--question-types", nargs="+", choices=list(QUESTION_TEXTS), default=list(QUESTION_TEXTS))
    parser.add_argument("--passage-id", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--output", default=os.path.join(_ROOT, "data", "study_responses.json"))
    parser.add_argument("--log-file", default=os.path.join(_ROOT, "logs", "generate_study_responses.log"))
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.log_file)), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(args.log_file, encoding="utf-8"),
        ],
        force=True,
    )
    logger.info("Writing logs to %s", args.log_file)

    passages = _filter_passages(args.passage_id)
    print(f"Discovered {len(passages)} passage(s).")
    if len(passages) != len({p["id"] for p in passages}):
        raise ValueError("Passage IDs must be unique.")

    payload = load_payload(args.output) if os.path.exists(args.output) else empty_payload()
    payload["schema_version"] = SCHEMA_VERSION
    payload["question_catalog"] = deepcopy(QUESTION_TEXTS)
    payload.pop("questions", None)
    payload.setdefault("records", [])

    total = len(passages) * len(args.question_types) * len(args.systems)
    success = skipped = errors = missing = 0
    progress = 0

    for passage in passages:
        record = _record_for_passage(payload, passage)
        for question_type in args.question_types:
            question_entry = _question_entry(record, question_type)
            question_text = QUESTION_TEXTS[question_type]
            for system in args.systems:
                progress += 1
                entry = _system_entry(question_entry, system)
                label = f"[{progress}/{total}] {passage['id']} | {question_type} | {system}"

                if args.validate_only:
                    if _is_done(entry):
                        success += 1
                        print(f"{label} | present")
                    else:
                        missing += 1
                        print(f"{label} | missing")
                    continue

                if not _should_generate(entry, args.overwrite, args.retry_failed):
                    skipped += 1
                    print(f"{label} | skipped")
                    continue

                try:
                    response, _ = _generate_one(system, passage, question_type, question_text)
                    _save_success(question_entry, system, response, question_type)
                    success += 1
                    print(f"{label} | success")
                except Exception as exc:
                    _save_error(question_entry, system, exc)
                    errors += 1
                    logger.exception("%s failed: %s", label, exc)
                    print(f"{label} | error: {exc}")
                finally:
                    atomic_write_json(args.output, payload)

    if args.validate_only:
        complete = missing == 0
        print(f"Validation summary: complete={complete} present={success} missing={missing} expected={total}")
    else:
        print(
            "Final validation summary: "
            f"generated_success={success} skipped={skipped} errors={errors} expected={total} "
            f"output={args.output}"
        )


if __name__ == "__main__":
    main()
