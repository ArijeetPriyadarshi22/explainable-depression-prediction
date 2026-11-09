"""
hybrid_shap_rag_cf/hybrid_explainer.py
────────────────────────────────────────────────────────────────────
Use Case 3: Unified prompt builder that fuses SHAP + RAG + CF signals
into one structured context block and sends it to Gemini in ONE call.

Evidence layers sent to the LLM:

  Layer 1 — SHAP  : which tokens drove the prediction and how strongly
  Layer 2 — RAG   : which PHQ-8 clinical symptoms match the user's text
  Layer 3 — CF    : what minimal text edit would shift the label

The LLM is instructed to SYNTHESISE — not section-by-section, but as one
flowing narrative where each layer informs the others:
  "The word 'empty' [SHAP] aligns with Depressed Mood [RAG].
   Replacing it with 'a bit flat' [CF] would shift the prediction,
   suggesting the intensity marker 'empty' is what the model latches on to."
"""

import sys
import os
import logging
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.depression_model         import LABEL_DESCRIPTIONS
from shared.llm_client               import call_gemini
from architecture.shap_explainer.shap_explainer import filter_explainable_tokens
# Correct package-qualified import — works whether called from root or subfolder
from architecture.hybrid_shap_rag_counterfactual.hybrid_pipeline import HybridResult

logger = logging.getLogger("hybrid_explainer")

SYSTEM_PROMPT = (
    "You explain AI assessment factors in warm, plain, everyday language. "
    "Use only the evidence provided from the study passage, matched themes, and generated wording changes. "
    "Use the strongest clearly supported evidence; do not force weak signals into the explanation. "
    "Prefer meaningful phrases over isolated words when context is needed to make the evidence clear. "
    "Describe the passage, not the reader; do not address the reader as if the passage is their own experience. "
    "Give equal attention to key wording, matched symptom themes, and wording-change results. "
    "Explain what changed the model prediction only when the candidate actually changed it. "
    "Avoid jargon, avoid scores/percentages, and do not give advice."
)


def _format_rag_themes(result: HybridResult) -> str:
    if not result.rag_result or result.rag_error:
        return f"  [Related symptom themes unavailable: {result.rag_error}]"

    lines = []
    for doc in result.rag_result.retrieved_docs[:3]:
        patterns = "; ".join(doc.natural_language_patterns[:3])
        impacts = "; ".join(doc.functional_impact_examples[:2])
        lines.append(
            f"  - {doc.symptom_name}: connect this theme to the passage's own wording; "
            f"typical signs include {patterns or doc.clinical_definition}; "
            f"daily impact can include {impacts or doc.clinical_definition}"
        )
    return "\n".join(lines) if lines else "  None"


def _context_for_token(text: str, token: str) -> str:
    token = str(token).strip()
    if not token:
        return ""

    cleaned_text = re.sub(r"\s+", " ", text).strip()
    if not cleaned_text:
        return token

    token_pattern = re.escape(token)
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned_text)
        if sentence.strip()
    ] or [cleaned_text]

    for sentence in sentences:
        if re.search(token_pattern, sentence, flags=re.IGNORECASE):
            if len(sentence) <= 170:
                return sentence

            match = re.search(token_pattern, sentence, flags=re.IGNORECASE)
            if not match:
                continue
            start = max(0, match.start() - 65)
            end = min(len(sentence), match.end() + 65)
            return sentence[start:end].strip(" ,;:")

    return token


# ── Prompt builder ────────────────────────────────────────────────────
def build_hybrid_prompt(user_query: str, result: HybridResult) -> str:
    """
    Assembles the full fused prompt from all three XAI signals.
    Layers that errored are clearly marked [unavailable] so the LLM
    can degrade gracefully rather than hallucinating missing data.
    """

    label_meaning = LABEL_DESCRIPTIONS.get(result.pred_label, "")

    # ── Layer 1: SHAP ─────────────────────────────────────────────────
    if result.shap_result and not result.shap_error:
        sr         = result.shap_result
        risk_lines = []
        for t in filter_explainable_tokens(sr.risk_tokens, 5):
            phrase = _context_for_token(result.text, t["token"])
            risk_lines.append(
                f"    '{phrase}' — increases the depression signal"
            )
        prot_lines = [
            f"    '{_context_for_token(result.text, t['token'])}' — reduces the depression signal"
            for t in filter_explainable_tokens(sr.protective_tokens, 3)
        ]
        shap_block = (
            "  Risk wording/phrases (increase depression signal):\n"
            + ("\n".join(risk_lines) if risk_lines else "    None")
            + "\n\n  Protective wording/phrases (reduce depression signal):\n"
            + ("\n".join(prot_lines) if prot_lines else "    None")
        )
    else:
        shap_block = f"  [Key-word evidence unavailable: {result.shap_error}]"

    # ── Layer 2: RAG ──────────────────────────────────────────────────
    rag_block = _format_rag_themes(result)

    # ── Layer 3: Counterfactual ───────────────────────────────────────
    if result.cf_result and not result.cf_error:
        cr    = result.cf_result
        best  = cr.best_cf
        if best and best["flip_success"]:
            cf_block = (
                f"  Target label  : {cr.target_label.upper()}\n"
                "  Status        : prediction changed in the intended direction\n"
                f"  New label     : {best['label'].upper()}\n"
                f"  Modified text : \"{best['text']}\""
            )
        elif best:
            cf_block = (
                f"  Target label  : {cr.target_label.upper()}\n"
                "  Status        : generated changes did NOT change the predicted label\n"
                f"  Label remained: {best['label'].upper()}\n"
                f"  Closest modified text: \"{best['text']}\"\n"
                "  Interpretation: summarize the changed symptom areas in plain language, then explain "
                "that these edits were not enough."
            )
        else:
            cf_block = "  [No counterfactual candidates generated]"
    else:
        cf_block = f"  [Wording-change evidence unavailable: {result.cf_error}]"

    flip_achieved = (
        result.cf_result is not None
        and result.cf_result.best_cf is not None
        and result.cf_result.best_cf["flip_success"]
    )

    cf_note = (
        "The generated wording change DID change the predicted label. Explain what changed in "
        "the symptom evidence and name the new predicted level."
        if flip_achieved else
        "The generated wording change did NOT change the predicted label. Do not imply that it did. "
        "Explain which original evidence still keeps the prediction the same, and what broader "
        "symptom evidence would need to change."
    )

    # ── Assemble full prompt ──────────────────────────────────────────
    prompt = f"""You are explaining an AI depression screening result for a study passage using several sources of evidence.

STUDY PASSAGE:
"{user_query}"

MODEL PREDICTION: {result.pred_label.upper()}
{label_meaning}

EVIDENCE (for you):
- Key words/phrases that influenced the result:
{shap_block}

- Matched symptom themes:
{rag_block}

- Example wording change that could shift the result:
{cf_block}

WORDING-CHANGE GUIDANCE:
{cf_note}

WRITE ONE CLEAR, USER-FRIENDLY EXPLANATION with equal coverage of all three parts:
1. Starts with the predicted level in plain words.
2. Explains the key wording as meaningful phrases from the passage, not as isolated tokens.
3. Connects those same passage details to matched symptom themes in plain everyday language.
4. Explains the wording-change test by saying what areas were changed and whether the label changed.
5. Keeps the focus on explaining the result, not giving advice.

Constraints:
- Use only available evidence sources that contain clearly supported information.
- Blend the three evidence sources into one natural explanation; do not make a raw token list.
- Highlight the key words/phrases by wrapping them in **double asterisks**.
- Bold only the phrase itself, without quotation marks inside the bold markers.
- When a key word is only meaningful in context, quote the shortest surrounding phrase that
  makes its meaning clear instead of the isolated word.
- Do not use bare life-detail words like "daughter", "job", "work", or "therapy" by themselves;
  use a clear phrase such as "daughter is currently battling cancer" or skip that evidence.
- Do not force neutral or positive details into unrelated symptom themes. Mention them only
  when their role in the prediction is direct and clear.
- For unchanged predictions, do not list word-by-word replacements. Summarize the changed areas
  in one simple sentence.
- When a direct word replacement would sound unnatural, explain the phrase or surrounding context
  that changed instead of presenting it as a one-word swap.
- Refer to "the passage", "the text", or "the person in the passage".
- Do NOT say "your message", "you shared", "your symptoms", or "your screening result".
- Do not present unchanged predictions as successful changes.
- Do not say vague phrases like "moved closer" unless you also explain what symptom evidence changed.
- Ignore generic filler unless it is part of a meaningful phrase.
- Do NOT mention SHAP, RAG, counterfactual, probabilities, scores, self-care tips,
  support suggestions, knowledge bases, or disclaimers.
- Length: 3 short paragraphs, about 140-170 words total. If this is tight, keep the
  strongest supported point from each evidence source.
"""
    return prompt


# ── Gemini call ───────────────────────────────────────────────────────
def generate_hybrid_explanation(user_query: str, result: HybridResult) -> str:
    """Calls Gemini with the fused three-signal prompt. Returns explanation string."""
    prompt = build_hybrid_prompt(user_query, result)
    logger.info("Sending hybrid prompt to Gemini (%d chars)", len(prompt))
    return call_gemini(prompt, system=SYSTEM_PROMPT)


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    from architecture.hybrid_shap_rag_counterfactual.hybrid_pipeline import run_hybrid_pipeline, format_hybrid_debug

    text  = "I feel empty and tired every day. I don't go out much anymore and I've lost interest in my hobbies."
    query = "Can you help me understand what's going on with me?"

    print("Running hybrid pipeline (SHAP + RAG + CF)...")
    result = run_hybrid_pipeline(text, cf_candidates=3, cf_attempts=2)
    print(format_hybrid_debug(result))

    print("\nGenerating unified Gemini explanation...\n")
    explanation = generate_hybrid_explanation(query, result)
    print("── Hybrid Explanation ───────────────────────────────────────")
    print(explanation)
