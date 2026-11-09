"""Create thesis-ready tables and figures from regenerated analysis outputs."""

from __future__ import annotations

import os
import subprocess
import tempfile
import warnings
from pathlib import Path

from common_utils import append_section


DIMENSION_ORDER = ["Helpfulness", "Correctness", "Clarity", "Trust"]
EXPLANATION_ORDER = ["SHAP", "COUNTERFACTUAL", "RAG", "HYBRID"]
EXPLANATION_LABELS = {
    "SHAP": "SHAP",
    "COUNTERFACTUAL": "Counterfactual",
    "RAG": "RAG",
    "HYBRID": "Hybrid",
}
SYSTEM_ORDER = ["agentic_xai", "mentallama"]
SYSTEM_LABELS = {
    "agentic_xai": "Agentic XAI",
    "mentallama": "MentaLLaMA",
}
SEVERITY_ORDER = ["no depression", "moderate", "severe"]
SEVERITY_LABELS = {
    "no depression": "No depression",
    "moderate": "Moderate",
    "severe": "Severe",
}
QUESTION_ORDER = ["SHAP", "Counterfactual", "RAG", "Hybrid"]


def create_final_outputs(paths, summaries: dict[str, object]) -> dict[str, object]:
    pd, plt = import_plot_stack()

    final_tables = create_final_tables(paths, pd)
    final_figures = create_final_figures(paths, pd, plt)
    report_path = paths.results_dir / "task11_final_tables_and_figures.md"
    report_path.write_text("\n".join(final_outputs_report(final_tables, final_figures, summaries)), encoding="utf-8")
    return {"report_path": str(report_path), "tables": final_tables, "figures": final_figures}


def import_plot_stack():
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "thesis-analysis-matplotlib"))
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Pandas requires version.*")
            import pandas as pd
        original_check_output = subprocess.check_output

        def check_output_without_fc_list(cmd, *args, **kwargs):
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "fc-list":
                raise FileNotFoundError("Skip optional fontconfig scan for reproducible thesis plotting.")
            return original_check_output(cmd, *args, **kwargs)

        subprocess.check_output = check_output_without_fc_list
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        subprocess.check_output = original_check_output
    except ImportError as exc:
        raise RuntimeError(
            "Task 11 requires pandas and matplotlib. Install them with "
            "`python -m pip install pandas matplotlib` or `python -m pip install -r requirements.txt`."
        ) from exc
    finally:
        if "original_check_output" in locals():
            subprocess.check_output = original_check_output
    return pd, plt


def create_final_tables(paths, pd) -> list[str]:
    tables_dir = paths.tables_dir
    output_paths: list[str] = []

    phase1_summary = build_phase1_participant_trial_summary(tables_dir, pd)
    output_paths.append(write_final_table(phase1_summary, tables_dir / "thesis_phase1_participant_trial_summary.csv"))

    phase1_ratings = read_table(tables_dir / "phase1_task2_trial_level_descriptives.csv", pd)
    phase1_ratings = label_phase1_ratings(phase1_ratings)
    output_paths.append(write_final_table(phase1_ratings, tables_dir / "thesis_phase1_ratings_by_explanation_type.csv"))

    phase1_main = read_table(tables_dir / "phase1_task4_mixed_model_overall.csv", pd)
    phase1_main["dimension"] = phase1_main["dimension"].map(dimension_label)
    phase1_main["pairwise_rule"] = phase1_main["pairwise_rule"].map(pairwise_rule_label)
    phase1_main = phase1_main.rename(columns=title_columns)
    output_paths.append(write_final_table(phase1_main, tables_dir / "thesis_phase1_main_statistical_comparison.csv"))

    phase1_pairwise = read_table(tables_dir / "phase1_task4_mixed_model_pairwise_holm.csv", pd)
    if not phase1_pairwise.empty:
        phase1_pairwise["dimension"] = phase1_pairwise["dimension"].map(dimension_label)
        phase1_pairwise["comparison"] = phase1_pairwise["comparison"].map(explanation_comparison_label)
        phase1_pairwise = phase1_pairwise.rename(columns=title_columns)
    output_paths.append(write_final_table(phase1_pairwise, tables_dir / "thesis_phase1_pairwise_comparisons.csv"))

    phase2_summary = build_phase2_participant_trial_summary(tables_dir, pd)
    output_paths.append(write_final_table(phase2_summary, tables_dir / "thesis_phase2_participant_trial_summary.csv"))

    phase2_descriptive = read_table(tables_dir / "phase2_task2_trial_level_descriptives.csv", pd)
    phase2_descriptive = label_phase2_descriptive(phase2_descriptive)
    output_paths.append(write_final_table(phase2_descriptive, tables_dir / "thesis_phase2_agentic_xai_vs_mentallama_descriptive.csv"))

    phase2_main = read_table(tables_dir / "phase2_task6_primary_mixed_model.csv", pd)
    phase2_main["dimension"] = phase2_main["dimension"].map(dimension_label)
    phase2_main = phase2_main.rename(columns=title_columns)
    output_paths.append(write_final_table(phase2_main, tables_dir / "thesis_phase2_main_statistical_comparison.csv"))

    phase2_paired = read_table(tables_dir / "phase2_task7_participant_paired_tests.csv", pd)
    phase2_paired["dimension"] = phase2_paired["dimension"].map(dimension_label)
    phase2_paired = phase2_paired.rename(columns=title_columns)
    output_paths.append(write_final_table(phase2_paired, tables_dir / "thesis_phase2_participant_level_paired_table.csv"))

    return output_paths


def build_phase1_participant_trial_summary(tables_dir: Path, pd):
    participant_trials = read_table(tables_dir / "phase1_task1_participant_trials.csv", pd)
    explanation_counts = read_table(tables_dir / "phase1_task1_explanation_counts.csv", pd)
    severity_counts = read_table(tables_dir / "phase1_task1_severity_counts.csv", pd)
    rows = [
        {"Measure": "Participants", "Value": participant_trials["participant_id"].nunique()},
        {"Measure": "Trials", "Value": int(participant_trials["n_trials"].sum())},
        {"Measure": "Median trials per participant", "Value": float(participant_trials["n_trials"].median())},
        {"Measure": "Minimum trials per participant", "Value": int(participant_trials["n_trials"].min())},
        {"Measure": "Maximum trials per participant", "Value": int(participant_trials["n_trials"].max())},
    ]
    for _, row in explanation_counts.iterrows():
        rows.append({"Measure": f"Trials: {EXPLANATION_LABELS.get(row['selected_use_case_name'], row['selected_use_case_name'])}", "Value": int(row["n_trials"])})
    for _, row in severity_counts.iterrows():
        label = "No depression" if row["prediction_label"] == "not depression" else str(row["prediction_label"]).capitalize()
        rows.append({"Measure": f"Trials: {label}", "Value": int(row["n_trials"])})
    return pd.DataFrame(rows)


def build_phase2_participant_trial_summary(tables_dir: Path, pd):
    participant_trials = read_table(tables_dir / "phase2_task1_participant_trials.csv", pd)
    system_counts = read_table(tables_dir / "phase2_task1_system_counts.csv", pd)
    severity_counts = read_table(tables_dir / "phase2_task1_severity_counts.csv", pd)
    question_counts = read_table(tables_dir / "phase2_task1_question_type_counts.csv", pd)
    rows = [
        {"Measure": "Participants", "Value": participant_trials["participant_id"].nunique()},
        {"Measure": "Trials", "Value": int(participant_trials["n_trials"].sum())},
        {"Measure": "Median trials per participant", "Value": float(participant_trials["n_trials"].median())},
        {"Measure": "Minimum trials per participant", "Value": int(participant_trials["n_trials"].min())},
        {"Measure": "Maximum trials per participant", "Value": int(participant_trials["n_trials"].max())},
    ]
    for _, row in system_counts.iterrows():
        rows.append({"Measure": f"Trials: {SYSTEM_LABELS.get(row['explanation_system'], row['explanation_system'])}", "Value": int(row["n_trials"])})
    for _, row in severity_counts.iterrows():
        label = "No depression" if row["severity"] == "none" else str(row["severity"]).capitalize()
        rows.append({"Measure": f"Trials: {label}", "Value": int(row["n_trials"])})
    for _, row in question_counts.iterrows():
        rows.append({"Measure": f"Trials: {question_label(row['question_type'])} questions", "Value": int(row["n_trials"])})
    return pd.DataFrame(rows)


def label_phase1_ratings(df):
    df = df.copy()
    df["condition"] = df["condition"].map(EXPLANATION_LABELS).fillna(df["condition"])
    df["dimension"] = df["dimension"].map(dimension_label)
    df = df.rename(columns={"condition": "Explanation type", "dimension": "Rating dimension", **title_columns_map()})
    return df


def label_phase2_descriptive(df):
    df = df.copy()
    df["condition"] = df["condition"].map(SYSTEM_LABELS).fillna(df["condition"])
    df["dimension"] = df["dimension"].map(dimension_label)
    df = df.rename(columns={"condition": "System", "dimension": "Rating dimension", **title_columns_map()})
    return df


def create_final_figures(paths, pd, plt) -> list[str]:
    output_paths: list[str] = []
    output_paths.extend(plot_phase1_explanation(paths, pd, plt))
    output_paths.extend(plot_phase1_severity(paths, pd, plt))
    output_paths.extend(plot_phase2_system(paths, pd, plt))
    output_paths.extend(plot_phase2_paired(paths, pd, plt))
    output_paths.extend(plot_phase2_question_type(paths, pd, plt))
    output_paths.extend(plot_phase2_severity(paths, pd, plt))
    return output_paths


def plot_phase1_explanation(paths, pd, plt) -> list[str]:
    df = read_table(paths.tables_dir / "phase1_task2_trial_level_descriptives.csv", pd)
    df["Explanation type"] = df["condition"].map(EXPLANATION_LABELS)
    df = order_dimension(df)
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7), sharey=True)
    for ax, dimension in zip(axes.flat, DIMENSION_ORDER):
        sub = df[df["dimension"] == dimension].set_index("Explanation type").reindex(EXPLANATION_LABELS.values())
        ax.bar(sub.index, sub["mean"], color="#4c78a8")
        ax.errorbar(sub.index, sub["mean"], yerr=[sub["mean"] - sub["ci95_low"], sub["ci95_high"] - sub["mean"]], fmt="none", ecolor="#222222", capsize=4)
        ax.set_title(dimension)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Mean rating")
        ax.tick_params(axis="x", rotation=25)
    fig.suptitle("Phase 1 Ratings by Explanation Type")
    fig.tight_layout()
    return save_figure(fig, paths.figures_dir / "thesis_phase1_explanation_type")


def plot_phase1_severity(paths, pd, plt) -> list[str]:
    df = read_table(paths.tables_dir / "phase1_task5_explanation_by_severity_descriptives.csv", pd)
    df["Explanation type"] = df["explanation_type"].map(EXPLANATION_LABELS)
    df["Severity"] = df["severity"].map(SEVERITY_LABELS)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
    colors = ["#4c78a8", "#f58518", "#54a24b", "#b279a2"]
    for ax, dimension in zip(axes.flat, DIMENSION_ORDER):
        sub = df[df["dimension"] == dimension]
        for color, explanation in zip(colors, EXPLANATION_LABELS.values()):
            line = sub[sub["Explanation type"] == explanation].set_index("Severity").reindex(SEVERITY_LABELS.values())
            ax.plot(line.index, line["mean"], marker="o", label=explanation, color=color)
        ax.set_title(dimension)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Mean rating")
    axes.flat[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Phase 1 Ratings by Explanation Type and Severity")
    fig.tight_layout()
    return save_figure(fig, paths.figures_dir / "thesis_phase1_severity")


def plot_phase2_system(paths, pd, plt) -> list[str]:
    df = read_table(paths.tables_dir / "phase2_task2_trial_level_descriptives.csv", pd)
    df["System"] = df["condition"].map(SYSTEM_LABELS)
    df = order_dimension(df)
    fig, axes = plt.subplots(2, 2, figsize=(8.5, 7), sharey=True)
    colors = ["#4c78a8", "#f58518"]
    for ax, dimension in zip(axes.flat, DIMENSION_ORDER):
        sub = df[df["dimension"] == dimension].set_index("System").reindex(SYSTEM_LABELS.values())
        ax.bar(sub.index, sub["mean"], color=colors)
        ax.errorbar(sub.index, sub["mean"], yerr=[sub["mean"] - sub["ci95_low"], sub["ci95_high"] - sub["mean"]], fmt="none", ecolor="#222222", capsize=4)
        ax.set_title(dimension)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Mean rating")
    fig.suptitle("Phase 2 Ratings: Agentic XAI vs MentaLLaMA")
    fig.tight_layout()
    return save_figure(fig, paths.figures_dir / "thesis_phase2_agentic_xai_vs_mentallama")


def plot_phase2_paired(paths, pd, plt) -> list[str]:
    df = read_table(paths.tables_dir / "phase2_task7_participant_level_wide_means.csv", pd)
    fig, axes = plt.subplots(2, 2, figsize=(8.5, 7), sharey=True)
    for ax, dimension in zip(axes.flat, DIMENSION_ORDER):
        dim = dimension.lower()
        agentic = f"agentic_xai_{dim}_mean"
        mentallama = f"mentallama_{dim}_mean"
        for _, row in df.iterrows():
            ax.plot(["Agentic XAI", "MentaLLaMA"], [row[agentic], row[mentallama]], color="#7f7f7f", alpha=0.55, linewidth=1)
        ax.scatter(["Agentic XAI"] * len(df), df[agentic], color="#4c78a8", s=18)
        ax.scatter(["MentaLLaMA"] * len(df), df[mentallama], color="#f58518", s=18)
        ax.set_title(dimension)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Participant mean rating")
    fig.suptitle("Phase 2 Participant-Level Paired Ratings")
    fig.tight_layout()
    return save_figure(fig, paths.figures_dir / "thesis_phase2_participant_paired")


def plot_phase2_question_type(paths, pd, plt) -> list[str]:
    df = read_table(paths.tables_dir / "phase2_task8_system_by_question_type_descriptives.csv", pd)
    df["System"] = df["system"].map(SYSTEM_LABELS)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
    colors = {"Agentic XAI": "#4c78a8", "MentaLLaMA": "#f58518"}
    for ax, dimension in zip(axes.flat, DIMENSION_ORDER):
        sub = df[df["dimension"] == dimension]
        for system in SYSTEM_LABELS.values():
            line = sub[sub["System"] == system].set_index("question_type").reindex(QUESTION_ORDER)
            ax.plot(line.index, line["mean"], marker="o", label=system, color=colors[system])
        ax.set_title(dimension)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Mean rating")
        ax.tick_params(axis="x", rotation=20)
    axes.flat[0].legend(frameon=False)
    fig.suptitle("Phase 2 Ratings by System and Question Type")
    fig.tight_layout()
    return save_figure(fig, paths.figures_dir / "thesis_phase2_question_type")


def plot_phase2_severity(paths, pd, plt) -> list[str]:
    df = read_table(paths.tables_dir / "phase2_task9_system_by_severity_descriptives.csv", pd)
    df["System"] = df["system"].map(SYSTEM_LABELS)
    df["Severity"] = df["severity"].map(SEVERITY_LABELS).fillna(df["severity"].str.capitalize())
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7), sharey=True)
    colors = {"Agentic XAI": "#4c78a8", "MentaLLaMA": "#f58518"}
    for ax, dimension in zip(axes.flat, DIMENSION_ORDER):
        sub = df[df["dimension"] == dimension]
        for system in SYSTEM_LABELS.values():
            line = sub[sub["System"] == system].set_index("Severity").reindex(SEVERITY_LABELS.values())
            ax.plot(line.index, line["mean"], marker="o", label=system, color=colors[system])
        ax.set_title(dimension)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Mean rating")
    axes.flat[0].legend(frameon=False)
    fig.suptitle("Phase 2 Ratings by System and Severity")
    fig.tight_layout()
    return save_figure(fig, paths.figures_dir / "thesis_phase2_severity")


def save_figure(fig, base_path: Path) -> list[str]:
    png = base_path.with_suffix(".png")
    pdf = base_path.with_suffix(".pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    fig.clf()
    return [str(png), str(pdf)]


def read_table(path: Path, pd):
    return pd.read_csv(path)


def write_final_table(df, path: Path) -> str:
    df.to_csv(path, index=False)
    return str(path)


def title_columns(column: str) -> str:
    return title_columns_map().get(column, column.replace("_", " ").title())


def title_columns_map() -> dict[str, str]:
    return {
        "dimension": "Rating dimension",
        "method": "Method",
        "model": "Model",
        "lr_chi2": "Likelihood-ratio chi-square",
        "df": "Degrees of freedom",
        "residual_sd": "Residual SD",
        "participant_intercept_variance": "Participant intercept variance",
        "converged": "Model converged",
        "pairwise_rule": "Pairwise comparison rule",
        "comparison": "Comparison",
        "mean_difference": "Mean difference",
        "n_trials": "N trials",
        "n_participants": "N participants",
        "n_paired_participants": "N paired participants",
        "mean": "Mean",
        "sd": "SD",
        "median": "Median",
        "iqr": "IQR",
        "ci95_low": "95% CI lower",
        "ci95_high": "95% CI upper",
        "p_value": "p-value",
        "raw_p_value": "Raw p-value",
        "holm_adjusted_p_value": "Holm-adjusted p-value",
        "effect_size": "Effect size",
        "effect_size_metric": "Effect size metric",
        "mean_paired_difference": "Mean paired difference",
        "median_paired_difference": "Median paired difference",
        "agentic_xai_higher_n": "Agentic XAI higher (n)",
        "mentallama_higher_n": "MentaLLaMA higher (n)",
        "tied_n": "Tied (n)",
        "test": "Test",
        "test_statistic": "Test statistic",
        "interpretation_note": "Interpretation note",
        "estimated_difference_agentic_minus_mentallama": "Estimated difference: Agentic XAI - MentaLLaMA",
        "agentic_xai_descriptive_mean": "Agentic XAI descriptive mean",
        "mentallama_descriptive_mean": "MentaLLaMA descriptive mean",
    }


def dimension_label(value: str) -> str:
    value = str(value)
    return {
        "helpfulness": "Helpfulness",
        "correctness": "Correctness",
        "clarity": "Clarity",
        "trust": "Trust",
    }.get(value.lower(), value)


def explanation_comparison_label(value: str) -> str:
    value = str(value)
    for raw, label in EXPLANATION_LABELS.items():
        value = value.replace(raw, label)
    return value


def pairwise_rule_label(value: str) -> str:
    if str(value) == "Pairwise comparisons run only if overall p < 0.05":
        return "Pairwise comparisons run only if the overall p-value is below 0.05"
    return str(value)


def question_label(value: str) -> str:
    return {
        "shap": "SHAP",
        "counterfactual": "Counterfactual",
        "rag": "RAG",
        "hybrid": "Hybrid",
    }.get(str(value), str(value).title())


def order_dimension(df):
    df = df.copy()
    df["dimension"] = df["dimension"].astype("category").cat.set_categories(DIMENSION_ORDER, ordered=True)
    return df.sort_values("dimension")


def final_outputs_report(table_paths: list[str], figure_paths: list[str], summaries: dict[str, object]) -> list[str]:
    lines = [
        "# Task 11 - Final Tables and Figures",
        "",
        "This report lists the thesis-ready CSV tables and PNG/PDF figures generated by the reproducible pipeline.",
        "",
    ]
    append_section(lines, "Scope", [
        "Phase 1 outputs cover participant/trial summaries, ratings by explanation type, main statistical comparisons, relevant pairwise comparisons, explanation-type figures, and severity figures.",
        "Phase 2 outputs cover participant/trial summaries, Agentic XAI vs MentaLLaMA descriptive and statistical tables, participant-level paired results, system figures, paired plots, question-type plots, and severity plots.",
        "Figures use human-readable labels and avoid internal variable names.",
    ])
    append_section(lines, "Final Tables", [f"- {path}" for path in table_paths])
    append_section(lines, "Final Figures", [f"- {path}" for path in figure_paths])
    append_section(lines, "Checks", [
        f"Phase 1 rows/trials: {summaries['phase1']['n_rows']}; participants: {summaries['phase1']['n_participants']}.",
        f"Phase 2 rows/trials: {summaries['phase2']['n_rows']}; participants: {summaries['phase2']['n_participants']}.",
        "Task 11 is complete. Tables are CSV; final figures are saved as both PNG and PDF.",
    ])
    return lines
