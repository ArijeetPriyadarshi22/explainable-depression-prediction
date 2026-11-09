# Architecture Notes

These notes summarize the implemented architecture inspected from the current repository. They are intended to ground the diagram set in the actual code rather than in older design descriptions.

## Verified Implementation

- The main runtime entry point is `bot.py`, a Telegram study bot.
- The current participant study flow is evaluation-first. A participant starts with `/begin`, receives eight text samples, sees the model prediction, selects one fixed explanation question, receives one saved explanation, and rates it.
- Saved participant-facing study explanations are loaded from `data/study_responses.json` through `study/response_store.py`. Missing saved responses are treated as administrator errors during the study flow.
- The Agentic XAI generation path is implemented in `architecture/mcp_modular_agent/`.
- The MCP server is `architecture/mcp_modular_agent/mcp_server.py` and runs over stdio as `agentic-mcp-xai`.
- The MCP server exposes four tools:
  - `predict_depression`
  - `explain_shap`
  - `explain_rag`
  - `explain_counterfactual`
- There is no implemented `explain_hybrid` MCP tool or hybrid MCP server in the current MCP architecture.
- The MCP server returns structured/raw result payloads for the explanation tools. It does not generate the final participant-facing natural-language explanation.
- The MCP client is `architecture/mcp_modular_agent/mcp_client.py`. It starts the local MCP server process, discovers tools, calls MCP tools, unwraps MCP responses, deserializes raw results, stores observations, and invokes final response generators.
- The ReAct-style controller is `architecture/mcp_modular_agent/agent_controller.py`. It uses Gemini through `shared/llm_client.py` to choose one next action from `explain_shap`, `explain_rag`, `explain_counterfactual`, or `finish`.
- The controller has a deterministic fallback when the LLM decision fails.
- The maximum ReAct loop length is `MAX_STEPS = 3`.
- The controlled study generation path uses `run_fixed_tool_pipeline()`. It maps the fixed question type directly to a tool. For `hybrid`, it calls `explain_shap`, `explain_rag`, and `explain_counterfactual` through MCP, then generates one hybrid explanation client-side.

## Prediction Model

- The shared prediction implementation is in `shared/depression_model.py`.
- The model is a local TF-IDF centroid-similarity style classifier trained from `shared/training_examples.py`, with a cached persisted model at `shared/model_cache/depression_tfidf_lr.joblib`.
- Prediction output includes label, confidence, probability vector, severity score, and severity reason.
- Labels are derived from training examples at load time.
- The system should be described as a depression-prediction and explanation research system, not as a diagnostic system.

## Explanation Tools and Raw Results

- SHAP:
  - Raw computation is exposed via `shared.depression_model.explain_with_shap()`.
  - It returns a `SHAPResult` with tokens, SHAP matrix, predicted label, probabilities, severity score, top tokens, risk tokens, and protective tokens.
  - Final text generation is `architecture/shap_explainer/shap_explainer.py::generate_shap_explanation()`.
- RAG:
  - Raw pipeline is `architecture/rag_explainer/rag_explainer.py::run_rag_pipeline()`.
  - Retrieval is implemented in `architecture/rag_explainer/rag_retriever.py`.
  - The knowledge source is `shared/phq8_knowledge_base.csv`.
  - The retriever builds a FAISS `IndexFlatL2` over sentence-transformer embeddings from `all-MiniLM-L6-v2`.
  - MCP uses `top_k=3` for RAG retrieval.
  - Final text generation is `generate_rag_explanation()`.
- Counterfactual:
  - Raw pipeline is `architecture/shap_counterfactual_explainer/cf_generator.py::generate_counterfactuals()`.
  - It predicts the original label, uses SHAP risk tokens as guidance, prompts Gemini to generate candidate rewrites, evaluates candidates with the classifier, minimality, and semantic or lexical similarity, then selects `best_cf`.
  - MCP uses `n_candidates=3` and `n_attempts=2`.
  - Final text generation is `architecture/shap_counterfactual_explainer/cf_explainer.py::generate_cf_explanation()`.
- Hybrid:
  - In the current MCP path, hybrid is not a separate MCP server/tool.
  - Hybrid explanation generation combines already obtained SHAP, RAG, and counterfactual raw results in the MCP client.
  - The client builds a `HybridResult` with `_build_hybrid_result()` and calls `generate_hybrid_explanation()`.
  - A standalone legacy-compatible `run_hybrid_pipeline()` still exists under `architecture/hybrid_shap_rag_counterfactual/`, but it is not exposed as a hybrid MCP tool.

## LLM Responsibilities

- Gemini is used for:
  - ReAct controller action selection.
  - SHAP natural-language explanation generation.
  - RAG natural-language explanation generation.
  - Counterfactual candidate generation.
  - Counterfactual natural-language explanation generation.
  - Hybrid natural-language explanation generation.
- Gemini does not compute the classifier probabilities.
- Gemini does not compute SHAP values.
- Gemini does not execute FAISS retrieval.
- Gemini generates counterfactual text candidates, but the local classifier evaluates whether the candidates move or change the predicted label.

## Baseline and Study Flow

- The baseline system is MentaLLaMA loaded through Hugging Face Transformers in `bot.py` and `scripts/generate_study_responses.py`.
- MentaLLaMA receives input in the format `Consider this post: <text> Question: <question>`.
- The saved study response generation script is `scripts/generate_study_responses.py`.
- For Agentic XAI, the response generation script calls `run_fixed_tool_pipeline()`.
- For MentaLLaMA, the script calls the local MentaLLaMA model directly.
- Study ratings currently logged in `logs/within_participant_experiment_records.csv` are:
  - explanation directly answered the question,
  - explanation was supported by passage details and consistent with the prediction,
  - explanation was easy to understand,
  - explanation gave an appropriate level of confidence in the prediction.
- An older `shared/eval_logger.py` and `analysis/statistical_analysis.py` refer to clarity, correctness, helpfulness, and trust for `logs/evaluation_records.csv`. The current Telegram within-participant study uses the four `answered`, `supported`, `understandable`, and `confidence` statements in `bot.py`.

## Discrepancies and Legacy Elements

- Some comments in `rag_explainer.py` mention "deproberta", but the current implementation uses the local TF-IDF centroid-similarity predictor in `shared/depression_model.py`.
- The standalone `architecture/hybrid_shap_rag_counterfactual/run_hybrid_pipeline()` remains in the repository. It is useful for standalone use cases and caching, but the MCP server does not expose a hybrid tool.
- `mcp_client.run_mcp_pipeline()` defaults `top_k=2`, but `_tool_arguments()` currently returns only `{"text": user_text}` and the MCP server hardcodes RAG retrieval to `top_k=3`. Diagrams therefore show MCP RAG retrieval as `k = 3`.
- The Telegram bot contains helper functions for live planner and MentaLLaMA answers, but the current final study callback path retrieves saved responses from `data/study_responses.json`.
- README wording describes "Multi-Use-Case Bot"; the current bot flow is study-oriented and saved-response based.

## Boundary Decisions Used in the Diagrams

- "MCP Client" refers to `architecture/mcp_modular_agent/mcp_client.py`.
- "ReAct Controller" refers to `architecture/mcp_modular_agent/agent_controller.py`.
- "MCP Server" refers to `architecture/mcp_modular_agent/mcp_server.py`.
- "MCP Tool" refers to one server-exposed function decorated with `@mcp.tool()`.
- "Explanation Generator" refers to client-side Gemini prompt builders/generators such as `generate_shap_explanation()`, `generate_rag_explanation()`, `generate_cf_explanation()`, and `generate_hybrid_explanation()`.
- "Raw result" refers to serialized/deserialized result dataclasses or dictionaries returned by MCP tools before participant-facing wording is generated.
