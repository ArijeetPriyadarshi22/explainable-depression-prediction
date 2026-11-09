# Thesis Diagrams

This directory contains editable Mermaid source diagrams for the current MCP-based Agentic XAI depression-prediction research system. Mermaid is the canonical source format. Generated SVG or PDF files, when available, should be treated as exports.

## Canonical Terminology

- **MCP**: Model Context Protocol. It is the tool communication protocol, not a machine-learning model.
- **MCP Client**: `architecture/mcp_modular_agent/mcp_client.py`; starts the stdio MCP server, discovers tools, calls tools, deserializes raw results, records observations, and calls final explanation generators.
- **ReAct Controller**: `architecture/mcp_modular_agent/agent_controller.py`; selects the next explanation action or `finish`.
- **MCP Server**: `architecture/mcp_modular_agent/mcp_server.py`; exposes prediction, SHAP, RAG, and counterfactual tools over stdio.
- **MCP Tool**: one server-exposed function, such as `explain_shap`.
- **Explanation Method**: SHAP, RAG, counterfactual, or hybrid strategy.
- **Raw Result**: structured serialized/deserialized tool output before final natural-language generation.
- **Explanation Generator**: client-side prompt builder and Gemini call, such as `generate_hybrid_explanation()`.
- **Agentic XAI**: the MCP client, controller, tool calls, raw evidence, and final explanation generation path.
- **Baseline**: MentaLLaMA response generation through Hugging Face Transformers.

## Files and Captions

| File | Suggested caption | Suggested label | Purpose |
|---|---|---|---|
| `01_system_overview.mmd` | Figure X. High-level architecture of the MCP-based agentic explainable AI system for depression prediction. | `fig:system-overview` | Introduces the system in a compact form, separating prediction, evidence tools, and final explanation generation. |
| `02_agentic_architecture.mmd` | Figure X. Detailed architecture of the implemented Agentic XAI system and its MCP, explanation, and data layers. | `fig:agentic-architecture` | Shows runtime components, server/client boundaries, explanation generators, persistent resources, and the saved study-response store. |
| `03_request_processing_flow.mmd` | Figure X. End-to-end request processing flow for adaptive MCP-based explanation generation. | `fig:request-processing` | Describes how a question is interpreted, tools are selected, raw observations are collected, and the final explanation is generated. |
| `04_mcp_tool_interaction.mmd` | Figure X. Sequence of MCP tool discovery, execution, raw-result transfer, and client-side explanation generation. | `fig:mcp-interaction` | Shows the interaction among user/caller, bot, MCP client, controller, MCP server, tools, Gemini, and final generator. |
| `05_explanation_selection_flow.mmd` | Figure X. Mapping between explanation question types and implemented explanation strategies. | `fig:explanation-selection` | Clarifies that SHAP, RAG, counterfactual, and hybrid are explanation strategies rather than separate prediction models. |
| `06_hybrid_explanation_flow.mmd` | Figure X. Hybrid explanation generation through composition of SHAP, RAG, and counterfactual MCP tool results. | `fig:hybrid-generation` | Highlights that hybrid explanation generation is client-side and does not use a separate hybrid MCP server or tool. |
| `07_rag_pipeline.mmd` | Figure X. Retrieval-augmented explanation pipeline using the PHQ-8 knowledge base, sentence embeddings, and FAISS retrieval. | `fig:rag-pipeline` | Details the implemented RAG evidence pipeline from CSV knowledge source to retrieved symptom themes and final explanation. |
| `08_user_study_pipeline.mmd` | Figure X. Within-participant user-study pipeline comparing Agentic XAI and MentaLLaMA explanations. | `fig:user-study-pipeline` | Summarizes the participant-facing study process, saved-response retrieval, hidden system assignment, and rating collection. |
| `09_baseline_comparison.mmd` | Figure X. Architectural comparison between Agentic XAI and the MentaLLaMA baseline. | `fig:baseline-comparison` | Communicates the structural difference between tool-grounded Agentic XAI and the LLM-only baseline without making performance claims. |
| `system_architecture.mmd` | Figure X. Overall system architecture of the Telegram-based MCP Agentic XAI study system. | `fig:system-architecture` | Presents the complete system at a readable level: Telegram study interface, MCP client and ReAct evidence collection, MCP server tools, shared model resources, final response generation, and rating logs. |

## Editing Mermaid

Edit the `.mmd` files directly. They can be rendered by Mermaid CLI, Mermaid Live Editor, diagrams.net Mermaid import, or many Markdown editors. Keep the class names and color scheme consistent when adding components.

Recommended workflow:

```bash
cd docs/diagrams
./render_mermaid.sh
```

If Mermaid CLI is unavailable, install or run it with your preferred Node setup. A typical command is:

```bash
npx -y @mermaid-js/mermaid-cli -i 01_system_overview.mmd -o exports/01_system_overview.svg -b transparent
```

## Editing in diagrams.net / draw.io

Mermaid remains the source of truth. To edit visually in diagrams.net:

1. Open diagrams.net.
2. Choose **Arrange > Insert > Advanced > Mermaid**.
3. Paste the contents of a `.mmd` file.
4. Adjust the visual layout if needed.
5. Save the edited diagram as `.drawio` next to the Mermaid source if you want a visual-editing fork.

Visual `.drawio` files are not generated automatically because Mermaid is the canonical editable source and diagrams.net does not preserve Mermaid source as a normal editable diagram in a stable round-trip format.

## Exporting SVG and PDF

Use the included script:

```bash
cd docs/diagrams
./render_mermaid.sh
```

The script writes SVG exports to `docs/diagrams/exports/`. To create PDFs manually with Mermaid CLI:

```bash
mmdc -i 01_system_overview.mmd -o exports/01_system_overview.pdf -b white
```

## LaTeX Example

Place exported files under your thesis figure directory, for example `figures/diagrams/`, then include them as follows:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=\textwidth]{figures/diagrams/01_system_overview.pdf}
    \caption{High-level architecture of the MCP-based agentic explainable AI system for depression prediction.}
    \label{fig:system-overview}
\end{figure}
```

For SVG in LaTeX, use an SVG-capable workflow such as `\includesvg` from the `svg` package, or convert SVG to PDF before compiling.
