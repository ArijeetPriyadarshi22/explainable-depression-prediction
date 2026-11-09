"""
counterfactual_explainer/cf_generator.py
────────────────────────────────────────────────────────────────────
Use Case 4: Counterfactual-Only Explanation

Research basis:
  - FIZLE (Bhattacharjee et al., 2024): LLM-based CF generation using
    structured prompts with classifier integration, no fine-tuning needed.
  - FitCF / CGG (2024): Use SHAP to identify high-impact tokens BEFORE
    prompting the LLM, giving it explicit guidance on what to change.
  - Wachter et al. (2017): CFs must be minimal, plausible, label-flipping.
  - UbiComp '24 (Gyuwon Jung et al.): CFs for mental health should produce
    actionable coping strategies tied to concrete language patterns.

Pipeline:
  1. predict_proba(raw_text)        → label + probs (no reframing)
  2. explain_with_shap(raw_text)    → SHAP risk tokens (on raw text)
  3. _build_cf_prompt()             → SHAP-guided Gemini prompt
  4. call_gemini()                  → CF candidates
  5. _evaluate_candidates()         → flip rate, minimality, semantic sim
  6. Return ranked CounterfactualResult

Evaluation metrics (CEVAL benchmark, Nguyen et al., 2024):
  - Flip Rate     : % of CFs that change the predicted label
  - Minimality    : 1 - (word Levenshtein / max_len)
  - Semantic Sim. : cosine similarity of sentence embeddings
"""

import sys
import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.depression_model import (
    predict_proba, classify_severity, explain_with_shap,
    LABEL_MAP,
)
from shared.llm_client import call_gemini

logger = logging.getLogger("cf_generator")

_SEMANTIC_EMBEDDER = None
_SEMANTIC_MODE = os.environ.get("CF_SEMANTIC_MODE", "lexical").strip().lower()
_LABEL_ORDER = {"severe": 0, "moderate": 1, "not depression": 2}
_MIN_PROBABILITY_MOVEMENT = 0.01
_GENERIC_CF_TOKENS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can", "could",
    "day", "did", "do", "does", "doing", "for", "from", "get", "go", "had", "has",
    "have", "having", "i", "if", "in", "is", "it", "just", "me", "my", "of", "on",
    "or", "our", "right", "so", "that", "the", "their", "them", "then", "there",
    "this", "to", "was", "were", "what", "when", "with", "you",
}
# ── Target label strategy ─────────────────────────────────────────────
CF_TARGET_MAP = {
    "severe":         "moderate",
    "moderate":       "not depression",
    "not depression": "moderate",
}

# ── Recovery hints keyed to common depression tokens ─────────────────
SYMPTOM_RECOVERY_HINTS = {
    "hopeless":    "Replace hopelessness with signs of purpose or hope",
    "empty":       "Replace emotional emptiness with small moments of connection",
    "tired":       "Replace persistent fatigue with energy recovery language",
    "worthless":   "Replace self-worth deficit with self-compassion phrasing",
    "nothing":     "Replace nihilism with acknowledgment of small positives",
    "anymore":     "Replace 'anymore' patterns with openness to change",
    "forever":     "Replace permanence language with temporary framing",
    "die":         "Replace ideation language with help-seeking or coping language",
    "disappear":   "Replace disappearance wish with desire for relief from pain",
    "sad":         "Replace pervasive sadness with mood variability",
    "lonely":      "Replace isolation with mention of social connection",
    "sleep":       "Replace sleep disruption with stabilised sleep routine",
    "numb":        "Replace emotional blunting with mild re-engagement",
    "concentrate": "Replace concentration difficulty with focused activity",
    "appetite":    "Replace appetite change with stabilised eating patterns",
}


def _is_meaningful_cf_token(token: str) -> bool:
    normalized = token.strip(".,!?'\"()[]{}:;").lower()
    if len(normalized) < 3:
        return False
    return normalized not in _GENERIC_CF_TOKENS


@dataclass
class CounterfactualResult:
    original_text:      str
    original_label:     str
    original_probs:     np.ndarray
    severity_score:     float
    target_label:       str
    candidates:         List[dict] = field(default_factory=list)
    best_cf:            Optional[dict] = None
    shap_guided_tokens: List[dict] = field(default_factory=list)
    already_well:       bool = False


# ── Evaluation metrics ────────────────────────────────────────────────
def _levenshtein(s1: str, s2: str) -> int:
    """Word-level Levenshtein distance."""
    w1, w2 = s1.lower().split(), s2.lower().split()
    m, n   = len(w1), len(w2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if w1[i-1] == w2[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[m][n]


def _minimality_score(original: str, cf: str) -> float:
    dist    = _levenshtein(original, cf)
    max_len = max(len(original.split()), len(cf.split()), 1)
    return round(1.0 - (dist / max_len), 3)


def _lexical_similarity(original: str, cf: str) -> float:
    s1 = set(original.lower().split())
    s2 = set(cf.lower().split())
    return round(len(s1 & s2) / max(len(s1 | s2), 1), 3)


def _get_semantic_embedder():
    global _SEMANTIC_EMBEDDER
    if _SEMANTIC_EMBEDDER is None:
        from sentence_transformers import SentenceTransformer
        _SEMANTIC_EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
    return _SEMANTIC_EMBEDDER


def _semantic_similarity_many(original: str, candidates: Sequence[str]) -> List[float]:
    if not candidates:
        return []

    if _SEMANTIC_MODE not in {"transformer", "sentence_transformer"}:
        return [_lexical_similarity(original, cf) for cf in candidates]

    try:
        model = _get_semantic_embedder()
        embs = model.encode([original, *candidates], convert_to_numpy=True)
        original_emb = embs[0]
        scores = []
        for cf_emb in embs[1:]:
            cos = float(np.dot(original_emb, cf_emb) /
                        (np.linalg.norm(original_emb) * np.linalg.norm(cf_emb) + 1e-9))
            scores.append(round(cos, 3))
        return scores
    except Exception as exc:
        logger.warning("Transformer semantic similarity failed; using lexical fallback: %s", exc)
        return [_lexical_similarity(original, cf) for cf in candidates]


def _movement_toward_target(original_label: str, cf_label: str, target_label: str) -> int:
    """Positive if cf_label moves from original_label toward target_label."""
    orig_pos = _LABEL_ORDER.get(original_label, 0)
    cf_pos = _LABEL_ORDER.get(cf_label, 0)
    target_pos = _LABEL_ORDER.get(target_label, 0)
    direction = 1 if target_pos > orig_pos else -1
    return (cf_pos - orig_pos) * direction


def _label_idx(label: str) -> int:
    for idx, name in LABEL_MAP.items():
        if name == label:
            return idx
    return -1


def _probability_movement_toward_target(
    original_probs: np.ndarray,
    cf_probs: np.ndarray,
    original_label: str,
    target_label: str,
) -> float:
    orig_idx = _label_idx(original_label)
    target_idx = _label_idx(target_label)
    if orig_idx < 0 or target_idx < 0:
        return 0.0

    target_gain = float(cf_probs[target_idx] - original_probs[target_idx])
    original_drop = float(original_probs[orig_idx] - cf_probs[orig_idx])
    return max(target_gain, original_drop)


def _evaluate_candidates(
    original: str,
    original_label: str,
    candidate_texts: Sequence[str],
    target_label: str,
) -> List[dict]:
    """Batch-score CF candidates to avoid repeated model/vectorizer calls."""
    if not candidate_texts:
        return []

    cf_probs_batch = predict_proba(list(candidate_texts))
    original_probs = predict_proba([original])[0]
    semantic_scores = _semantic_similarity_many(original, candidate_texts)
    evaluated = []

    for candidate_text, cf_probs, semantic_sim in zip(candidate_texts, cf_probs_batch, semantic_scores):
        cf_label, _, _ = classify_severity(cf_probs)
        movement = _movement_toward_target(original_label, cf_label, target_label)
        probability_movement = _probability_movement_toward_target(
            original_probs,
            cf_probs,
            original_label,
            target_label,
        )
        flip_success = cf_label != original_label and movement > 0
        minimality = _minimality_score(original, candidate_text)

        if flip_success:
            score = 1.0 + 0.5 * minimality + 0.5 * semantic_sim
        else:
            score = max(0.0, probability_movement) + 0.01 * minimality

        evaluated.append({
            "text":         candidate_text,
            "label":        cf_label,
            "probs":        cf_probs,
            "flip_success": flip_success,
            "probability_movement": round(probability_movement, 4),
            "minimality":   minimality,
            "semantic_sim": semantic_sim,
            "score":        round(score, 4),
        })

    return evaluated


# ── SHAP-guided CF prompt (FitCF / FIZLE approach) ───────────────────
def _build_cf_prompt(
    original_text:  str,
    original_label: str,
    target_label:   str,
    shap_tokens:    List[dict],
    n_candidates:   int = 3,
    flip_focused:   bool = False,
) -> str:
    token_hints = []
    for t in shap_tokens[:5]:
        evidence = str(t.get("token", "")).strip()
        word = evidence.strip(".,!?'\"").lower()
        if not _is_meaningful_cf_token(word):
            continue
        hint = SYMPTOM_RECOVERY_HINTS.get(word, f"Soften the symptom meaning around '{evidence}'")
        token_hints.append(f"  - '{evidence}': {hint}")
    token_block = "\n".join(token_hints) or "  (No reliable symptom phrase targets; make holistic symptom-level edits)"
    output_lines = "\n".join(["CF: <counterfactual text>" for _ in range(n_candidates)])

    if flip_focused:
        task = (
            f"Generate {n_candidates} revised versions of the text below that are strong enough "
            f"to make the model predict \"{target_label}\" instead of \"{original_label}\"."
        )
        edit_count = "Change 3-6 meaningful symptom-bearing phrases if needed"
        edit_boundary = "keep the original structure, but make the symptom pattern milder"
        target_note = "For long or severe texts, a single word swap is usually not enough."
    else:
        task = (
            f"Generate {n_candidates} targeted phrase-level versions of the text below that would "
            f"make the model predict \"{target_label}\" instead of \"{original_label}\", or at least move "
            f"the model clearly toward \"{target_label}\"."
        )
        edit_count = "Change only 1-3 meaningful symptom-bearing phrases"
        edit_boundary = "only targeted changes, not a complete rewrite"
        target_note = "Do not force a label flip with unnatural or exaggerated wording."

    edit_scope = (
        f"1. {edit_count}; {target_note}\n"
        "2. Use the high-impact tokens only to locate the relevant symptom context. If changing the\n"
        "   token alone sounds awkward, rewrite the shortest natural phrase around it.\n"
        f"3. Preserve the overall topic, personal voice, and structure: {edit_boundary}\n"
        "4. Keep anchoring life details unchanged, such as family roles, relationships, jobs, places,\n"
        "   and dates. If an anchor appears inside a stressful phrase, keep the anchor and change the\n"
        "   surrounding context, e.g. \"daughter is sick\" -> \"daughter is doing well\".\n"
        "5. Reflect genuine emotional, behavioural, or physical improvement; avoid random synonyms,\n"
        "   filler-word edits, and fabricated details."
    )

    return f"""You are a Counterfactual Explanation Generator for a depression screening AI.

TASK: {task}

ORIGINAL TEXT (current prediction: {original_label.upper()}):
"{original_text}"

HIGH-IMPACT WORDS/PHRASES — use these only to locate symptom meaning in the original text:
{token_block}

CONSTRAINTS — each counterfactual MUST:
{edit_scope}

OUTPUT FORMAT — exactly {n_candidates} lines, each starting with "CF:":
{output_lines}

No explanation, preamble, or extra text. Only the CF: lines."""


def _parse_candidates(llm_response: str) -> List[str]:
    candidates = []
    for line in llm_response.strip().splitlines():
        line = line.strip()
        if line.lower().startswith("cf:"):
            text = line[3:].strip().strip('"\'')
            if len(text.split()) >= 4:
                candidates.append(text)
    return candidates


# ── Main pipeline ─────────────────────────────────────────────────────
def generate_counterfactuals(
    user_text:    str,
    n_candidates: int = 3,
    n_attempts:   int = 2,
) -> CounterfactualResult:
    """
    Runs on RAW user text — no reframing.
    SHAP explains the user's actual words.
    CFs are edits to the user's actual words.
    """
    # Step 1: predict on raw text
    probs                          = predict_proba([user_text])[0]
    original_label, score, _       = classify_severity(probs)
    target_label                   = CF_TARGET_MAP[original_label]

    logger.info("CF pipeline: %s (score=%.3f) → target: %s", original_label, score, target_label)

    result = CounterfactualResult(
        original_text  = user_text,
        original_label = original_label,
        original_probs = probs,
        severity_score = score,
        target_label   = target_label,
        already_well   = (original_label == "not depression"),
    )

    # Step 2: SHAP on raw text for token guidance
    shap_result                = explain_with_shap(user_text)
    result.shap_guided_tokens  = shap_result.risk_tokens[:5]
    logger.info("SHAP risk tokens: %s", [t["token"] for t in result.shap_guided_tokens])

    # Step 3: LLM generation. Keep attempts separate so a weak first response
    # does not block later candidates that may actually cross the label boundary.
    all_candidates = []
    for attempt in range(max(n_attempts, 1)):
        prompt = _build_cf_prompt(
            original_text  = user_text,
            original_label = original_label,
            target_label   = target_label,
            shap_tokens    = result.shap_guided_tokens,
            n_candidates   = n_candidates,
            flip_focused   = attempt > 0,
        )
        try:
            parsed = _parse_candidates(call_gemini(prompt))
            logger.info("Attempt %d: %d candidates", attempt + 1, len(parsed))
            all_candidates.extend(parsed)
        except Exception as e:
            logger.warning("Attempt %d failed: %s", attempt + 1, e)

    # Deduplicate
    seen, unique = set(), []
    for c in all_candidates:
        if c not in seen and c != user_text:
            seen.add(c)
            unique.append(c)

    # Step 4: evaluate in batch
    evaluated = _evaluate_candidates(user_text, original_label, unique, target_label)
    evaluated.sort(key=lambda x: (x["flip_success"], x["score"]), reverse=True)

    result.candidates = evaluated
    valid             = [c for c in evaluated if c["flip_success"]]
    influenced        = [
        c for c in evaluated
        if c["flip_success"] or float(c.get("probability_movement", 0.0)) >= _MIN_PROBABILITY_MOVEMENT
    ]
    result.best_cf    = valid[0] if valid else (influenced[0] if influenced else None)

    logger.info("CF done: %d candidates, %d valid flips", len(evaluated), len(valid))
    return result


def format_cf_debug(result: CounterfactualResult) -> str:
    probs = ", ".join(f"{LABEL_MAP[i]}={result.original_probs[i]:.3f}" for i in range(3))
    lines = [
        f"Original : {result.original_label} (score={result.severity_score:.3f}, {probs})",
        f"Target   : {result.target_label}",
        f"Tokens   : {[t['token'] for t in result.shap_guided_tokens]}",
        f"Candidates: {len(result.candidates)} ({sum(1 for c in result.candidates if c['flip_success'])} flips)",
    ]
    if result.best_cf:
        c = result.best_cf
        lines.append(
            f"Best CF  : [{c['label']}] flip={c['flip_success']} "
            f"min={c['minimality']} sim={c['semantic_sim']}\n"
            f"           '{c['text'][:80]}'"
        )
    return "\n".join(lines)
