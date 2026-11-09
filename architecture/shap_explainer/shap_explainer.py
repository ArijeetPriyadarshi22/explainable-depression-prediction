"""
shap_explainer/shap_explainer.py
────────────────────────────────────────────────────────────────────
Use Case 1: SHAP-only explanation.
Refactored to use shared/depression_model.py and shared/llm_client.py.
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.depression_model import SHAPResult, LABEL_MAP, LABEL_DESCRIPTIONS
from shared.llm_client       import call_gemini

SYSTEM_PROMPT = (
    "You explain AI assessment factors in warm, plain, everyday language. "
    "Use only the evidence provided from the study passage. "
    "Use the strongest clearly supported evidence; do not force weak signals into the explanation. "
    "Describe the passage, not the reader; do not address the reader as if the passage is their own experience. "
    "Avoid jargon, avoid scores/percentages, and do not give advice."
)

LOW_EXPLANATION_VALUE_TOKENS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "can", "could", "couldnt", "couldn't", "did", "do", "does", "doing",
    "dont", "don't", "every",
    "feel", "feeling", "felt", "for", "from", "get", "go", "had", "has", "have",
    "having", "i", "i'm", "in", "is", "it", "it's", "just", "kind", "like",
    "lot", "make", "makes", "me", "my", "of", "on", "or", "really", "seem",
    "seems", "so", "something", "stuff", "that", "the", "then", "thing",
    "things", "this", "to", "very", "was", "were", "with", "would", "wouldnt",
    "wouldn't", "you", "currently", "today", "now", "lately", "recently",
}


def filter_explainable_tokens(tokens: list[dict], limit: int) -> list[dict]:
    filtered = []
    for token in tokens:
        text = str(token.get("token", "")).strip()
        terms = [
            term.lower().replace("'", "")
            for term in re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", text.replace("’", "'"))
            if term.strip()
        ]
        if not terms:
            continue
        if all(term in LOW_EXPLANATION_VALUE_TOKENS for term in terms):
            continue
        filtered.append(token)
    return (filtered or tokens)[:limit]


def build_shap_prompt(user_query: str, result: SHAPResult) -> str:
    # Risk tokens
    risk_lines = []
    for t in filter_explainable_tokens(result.risk_tokens, 5):
        risk_lines.append(f"  '{t['token']}'")
    risk_block  = "\n".join(risk_lines) if risk_lines else "  None detected"

    # Protective tokens
    prot_lines  = [f"  '{t['token']}'" for t in filter_explainable_tokens(result.protective_tokens, 3)]
    prot_block  = "\n".join(prot_lines) if prot_lines else "  None detected"

    label_meaning = LABEL_DESCRIPTIONS.get(result.pred_label, "")

    return f"""You are explaining an AI depression screening result for a study passage.

STUDY PASSAGE:
"{user_query}"

MODEL PREDICTION:
  Result  : {result.pred_label.upper()}
  Meaning : {label_meaning}

KEY WORDS THAT RAISED THE RISK SIGNAL:
{risk_block}

KEY WORDS THAT LOWERED THE RISK SIGNAL:
{prot_block}

YOUR TASK — write a clear, user-friendly response that:
1. Starts with the predicted level in plain words.
2. Explains the strongest words/phrases that raised the risk signal and what human meaning
   the model likely took from them, grouping related evidence naturally.
3. Mentions meaningful words/phrases that lowered the risk signal only if they are clear.
4. Keeps the focus on explaining the result, not giving advice.

Constraints:
- Prefer meaningful phrases or content words; ignore generic filler unless it is part of
  a meaningful phrase.
- When an isolated word needs context, quote the shortest surrounding phrase that makes
  the meaning clear.
- If a risk or protective block says "None detected", do not invent evidence for it.
- Highlight the key words/phrases by wrapping them in **double asterisks**.
- Refer to "the passage", "the text", or "the person in the passage".
- Do NOT say "your message", "you shared", "your symptoms", or "your screening result".
- Do NOT mention SHAP, probabilities, scores, technical terms, self-care tips, support
  suggestions, or disclaimers.
- Length: 1-2 short paragraphs, about 130-150 words unless there is very little evidence.
"""


def generate_shap_explanation(user_query: str, result: SHAPResult) -> str:
    """Calls Gemini with the SHAP-augmented prompt."""
    return call_gemini(build_shap_prompt(user_query, result), system=SYSTEM_PROMPT)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from shared.depression_model import explain_with_shap, format_debug

    text  = "I feel empty and tired every day. Nothing makes sense anymore."
    query = "Can you help me understand how I'm feeling?"

    result = explain_with_shap(text)
    print(format_debug(result))
    print("\n── SHAP Explanation ──────────────────────────────────────────")
    print(generate_shap_explanation(query, result))
