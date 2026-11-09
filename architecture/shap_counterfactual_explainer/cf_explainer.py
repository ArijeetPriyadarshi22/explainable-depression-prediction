"""
counterfactual_explainer/cf_explainer.py
────────────────────────────────────────────────────────────────────
Use Case 4: Counterfactual explanation narrator.

Takes a CounterfactualResult and generates a user-facing explanation
that answers:
  "What would need to change in what I described for the AI to see
   me as less depressed?"

Counterfactuals provide wording-change evidence tied to concrete language
patterns — not just "you scored X", but "if the passage described X
differently, the model would read Y differently".

The explanation covers:
  1. What the model predicted and why (brief, referencing SHAP tokens)
  2. The counterfactual — what minimal change shifts the prediction
  3. What that change means clinically (connecting CF words to PHQ-8 symptoms)
  4. Whether the generated change did or did not alter the prediction
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.llm_client import call_gemini
from shared.depression_model import LABEL_DESCRIPTIONS
from architecture.shap_counterfactual_explainer.cf_generator import CounterfactualResult
from architecture.shap_explainer.shap_explainer import filter_explainable_tokens

import logging
logger = logging.getLogger("cf_explainer")

SYSTEM_PROMPT = (
    "You explain AI assessment factors in warm, plain, everyday language. "
    "Use only the evidence provided from the study passage and generated wording changes. "
    "Use the strongest clearly supported evidence; do not force weak signals into the explanation. "
    "Prefer meaningful phrases over isolated words when context is needed to make the evidence clear. "
    "Describe the passage, not the reader; do not address the reader as if the passage is their own experience. "
    "Explain what changed the model prediction only when the candidate actually changed it. "
    "Avoid jargon, avoid scores/percentages, and do not give advice."
)


def build_cf_explanation_prompt(user_query: str, result: CounterfactualResult) -> str:
    """
    Builds a structured prompt for the CF explanation.
    Grounds the LLM in the actual counterfactual candidates found.
    """
    # Best CF block
    if result.best_cf and result.best_cf["flip_success"]:
        best = result.best_cf
        cf_block = (
            "  Status: prediction changed in the intended direction\n"
            f"  Original prediction: {result.original_label.upper()}\n"
            f"  New prediction: {best['label'].upper()}\n"
            f"  Modified text: \"{best['text']}\""
        )
    elif result.best_cf:
        best = result.best_cf
        cf_block = (
            "  Status: generated changes did NOT change the predicted label\n"
            f"  Prediction remained: {best['label'].upper()}\n"
            f"  Closest modified text: \"{best['text']}\"\n"
            "  Interpretation: summarize the changed symptom areas in plain language, then explain "
            "that these edits were not enough."
        )
    else:
        cf_block = "  No valid counterfactual was generated."

    token_names = [t["token"] for t in filter_explainable_tokens(result.shap_guided_tokens, 4)]

    # Label descriptions
    orig_desc   = LABEL_DESCRIPTIONS.get(result.original_label, "")
    target_desc = LABEL_DESCRIPTIONS.get(result.target_label, "")

    return f"""You are explaining an AI depression screening result for a study passage.

ORIGINAL STUDY PASSAGE:
"{result.original_text}"

CURRENT MODEL PREDICTION: {result.original_label.upper()}
{orig_desc}

KEY WORDS THAT MOST INFLUENCED THE RESULT:
{', '.join(token_names) if token_names else 'No specific words identified'}

WHAT CHANGE COULD SHIFT THE RESULT:
Target label: {result.target_label.upper()}
{target_desc}

Best example change:
{cf_block}

YOUR TASK — write a short, user-friendly response in the same plain style as a SHAP explanation:
1. Starts with the current predicted level in plain words.
2. Mentions 2-3 strongest meaningful words or short phrases from the original passage and explains
   why they mattered in context.
3. Explains the generated wording-change test briefly. If it changed the prediction, name the new
   level and what became milder. If it did not change, say the edit was not enough.
4. Keeps the focus on explaining the result, not giving advice.

Constraints:
- Highlight the key words/phrases by wrapping them in **double asterisks**.
- Bold only the phrase itself, without quotation marks inside the bold markers.
- When a key word is only meaningful in context, use the shortest natural phrase from the
  original passage. Never output broken fragments.
- Do not use bare life-detail words like "daughter", "job", "work", or "therapy" by themselves;
  use a clear phrase such as "daughter is currently battling cancer" or skip that evidence.
- For unchanged predictions, do not list word-by-word replacements. Summarize the changed areas
  in one simple sentence.
- When a direct word replacement would sound unnatural, explain the phrase or surrounding context
  that changed instead of presenting it as a one-word swap.
- Refer to "the passage", "the text", or "the person in the passage".
- Do NOT say "your message", "you shared", "your symptoms", or "your screening result".
- Do not present unchanged predictions as successful changes.
- Ignore generic filler unless it is part of a meaningful phrase.
- Do NOT mention "counterfactual", SHAP, scores, probabilities, technical terms,
  self-care tips, support suggestions, or disclaimers.
- Length: 2 short paragraphs, about 90-120 words total.
"""


def generate_cf_explanation(user_query: str, result: CounterfactualResult) -> str:
    """Calls Gemini with the CF-augmented prompt."""
    prompt = build_cf_explanation_prompt(user_query, result)
    return call_gemini(prompt, system=SYSTEM_PROMPT)


def format_cf_telegram_preview(result: CounterfactualResult) -> str:
    """
    Short preview message sent to Telegram while Gemini processes.
    """
    label      = result.original_label
    target     = result.target_label
    confidence = result.original_probs[result.original_probs.argmax()] * 100
    n_valid    = sum(1 for c in result.candidates if c["flip_success"])
    n_total    = len(result.candidates)

    if result.best_cf and result.best_cf["flip_success"]:
        flip_status = f"Label flip achieved in {n_valid}/{n_total} candidates"
    else:
        flip_status = f"No label flip (strong decision boundary) — {n_total} candidates analysed"

    token_str = ", ".join(f"'{t['token']}'" for t in result.shap_guided_tokens[:3])

    return (
        f"Counterfactual Analysis\n"
        f"  Current level    : {label} ({confidence:.1f}%)\n"
        f"  Target level     : {target}\n"
        f"  Key SHAP tokens  : {token_str}\n"
        f"  {flip_status}\n\n"
        "Generating full explanation..."
    )


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    from cf_generator import generate_counterfactuals, format_cf_debug

    text  = "I feel empty and tired every day. Nothing makes sense anymore."
    query = "Can you help me understand what I could do differently?"

    print("Generating counterfactuals...")
    result = generate_counterfactuals(text)
    print(format_cf_debug(result))

    print("\nGenerating Gemini CF explanation...\n")
    explanation = generate_cf_explanation(query, result)
    print("── CF Explanation ───────────────────────────────────────────")
    print(explanation)
