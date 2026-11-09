"""Generate a concise thesis-ready interpretation from analysis tables."""

from __future__ import annotations

import warnings
from datetime import datetime

from common_utils import append_section


DIMENSION_ORDER = ["Helpfulness", "Correctness", "Clarity", "Trust"]


def create_thesis_interpretation(paths) -> str:
    pd = import_pandas()
    tables = paths.tables_dir
    report_path = paths.results_dir / "task12_thesis_interpretation.md"

    phase1_desc = pd.read_csv(tables / "phase1_task2_trial_level_descriptives.csv")
    phase1_main = pd.read_csv(tables / "phase1_task4_mixed_model_overall.csv")
    phase1_pairwise = pd.read_csv(tables / "phase1_task4_mixed_model_pairwise_holm.csv")
    phase1_severity = pd.read_csv(tables / "phase1_task5_severity_mixed_model.csv")
    phase1_severity_interaction = pd.read_csv(tables / "phase1_task5_interaction_mixed_model.csv")

    phase2_desc = pd.read_csv(tables / "phase2_task2_agentic_minus_mentallama.csv")
    phase2_primary = pd.read_csv(tables / "phase2_task6_primary_mixed_model.csv")
    phase2_paired = pd.read_csv(tables / "phase2_task7_participant_paired_tests.csv")
    phase2_question_interaction = pd.read_csv(tables / "phase2_task8_interaction_mixed_model.csv")
    phase2_severity_interaction = pd.read_csv(tables / "phase2_task9_interaction_mixed_model.csv")

    lines = build_interpretation(
        phase1_desc,
        phase1_main,
        phase1_pairwise,
        phase1_severity,
        phase1_severity_interaction,
        phase2_desc,
        phase2_primary,
        phase2_paired,
        phase2_question_interaction,
        phase2_severity_interaction,
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)


def import_pandas():
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Pandas requires version.*")
            import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "Task 12 requires pandas. Install it with `python -m pip install pandas` "
            "or `python -m pip install -r requirements.txt`."
        ) from exc
    return pd


def build_interpretation(
    phase1_desc,
    phase1_main,
    phase1_pairwise,
    phase1_severity,
    phase1_severity_interaction,
    phase2_desc,
    phase2_primary,
    phase2_paired,
    phase2_question_interaction,
    phase2_severity_interaction,
) -> list[str]:
    lines = [
        "# Task 12 - Thesis Interpretation",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This interpretation keeps Phase 1 and Phase 2 separate. It distinguishes statistically supported findings, descriptive trends, and exploratory findings. Non-significant results are not interpreted as proof that conditions are equivalent.",
        "",
    ]

    append_section(lines, "Phase 1 - Descriptive Results", phase1_descriptive_text(phase1_desc))
    append_section(lines, "Phase 1 - Statistical Results", phase1_statistical_text(phase1_main, phase1_pairwise))
    append_section(lines, "Phase 1 - Severity Findings", phase1_severity_text(phase1_severity, phase1_severity_interaction))
    append_section(lines, "Phase 1 - Interpretation", phase1_interpretation_text())
    append_section(lines, "Phase 2 - Descriptive Agentic XAI vs MentaLLaMA Results", phase2_descriptive_text(phase2_desc))
    append_section(lines, "Phase 2 - Primary Statistical Comparison", phase2_primary_text(phase2_primary))
    append_section(lines, "Phase 2 - Participant-Level Robustness Check", phase2_paired_text(phase2_paired))
    append_section(lines, "Phase 2 - Question-Type Findings", phase2_question_text(phase2_question_interaction))
    append_section(lines, "Phase 2 - Severity Findings", phase2_severity_text(phase2_severity_interaction))
    append_section(lines, "Phase 2 - Interpretation", phase2_interpretation_text())
    append_section(lines, "Stop Point", ["Task 12 is complete. No further analyses were run."])
    return lines


def phase1_descriptive_text(df) -> list[str]:
    best_by_dimension = []
    for dimension in ["Clarity", "Correctness", "Helpfulness", "Trust"]:
        sub = df[df["dimension"] == dimension].sort_values("mean", ascending=False)
        top = sub.iloc[0]
        low = sub.iloc[-1]
        best_by_dimension.append(
            f"For {dimension}, {explanation_label(top['condition'])} had the highest descriptive mean "
            f"({top['mean']:.3f}), while {explanation_label(low['condition'])} had the lowest descriptive mean "
            f"({low['mean']:.3f})."
        )
    return [
        "Across Phase 1, ratings were generally around the positive middle-to-upper part of the 1-5 scale, with medians usually at 4.",
        *best_by_dimension,
        "These are descriptive patterns only. They show observed mean differences but do not by themselves establish that explanation types differed statistically.",
    ]


def phase1_statistical_text(main, pairwise) -> list[str]:
    clarity = row_for(main, "Clarity")
    correctness = row_for(main, "Correctness")
    helpfulness = row_for(main, "Helpfulness")
    trust = row_for(main, "Trust")
    pairwise_supported = pairwise[pairwise["holm_adjusted_p_value"] < 0.05]
    supported_text = (
        "No individual pairwise comparison remained below 0.05 after Holm correction."
        if pairwise_supported.empty
        else "At least one individual pairwise comparison remained below 0.05 after Holm correction."
    )
    return [
        f"The primary participant-aware mixed-effects analysis found evidence of an overall explanation-type effect for Clarity, "
        f"chi-square({int(clarity['df'])})={clarity['lr_chi2']:.3f}, p={clarity['p_value']:.3f}.",
        supported_text,
        f"For Correctness, the overall explanation-type test was close to but did not cross the 0.05 threshold "
        f"(p={correctness['p_value']:.3f}).",
        f"For Helpfulness (p={helpfulness['p_value']:.3f}) and Trust (p={trust['p_value']:.3f}), the primary analysis did not provide statistical evidence of explanation-type differences.",
        "The participant-level Friedman analysis suggested a secondary signal for Correctness, but this robustness check should not override the primary trial-level mixed-effects result.",
    ]


def phase1_severity_text(severity, interaction) -> list[str]:
    severity_ps = ", ".join(f"{row['dimension']} p={row['p_value']:.3f}" for _, row in severity.iterrows())
    interaction_ps = ", ".join(f"{row['dimension']} p={row['p_value']:.3f}" for _, row in interaction.iterrows())
    return [
        f"The exploratory main severity models did not show evidence of severity-related rating differences: {severity_ps}.",
        f"The exploratory explanation-type by severity interaction tests also did not show evidence below 0.05: {interaction_ps}.",
        "Therefore, Phase 1 does not provide clear evidence that ratings depended on depression severity, or that explanation-type differences changed by severity.",
    ]


def phase1_interpretation_text() -> list[str]:
    return [
        "The main Phase 1 conclusion is cautious. There is statistically supported evidence that explanation type mattered for Clarity at the overall level, but the follow-up comparisons did not identify a specific pair of explanation types that clearly differed after correction.",
        "For Correctness, Helpfulness, and Trust, the primary analysis does not support a strong claim that the four explanation types differed.",
        "Descriptively, RAG and Hybrid often had higher mean ratings than SHAP and Counterfactual, but these trends should be presented as observed patterns rather than definitive differences.",
    ]


def phase2_descriptive_text(df) -> list[str]:
    rows = []
    for dimension in ["Helpfulness", "Correctness", "Clarity", "Trust"]:
        row = row_for(df, dimension)
        direction = "higher" if row["mean_difference"] > 0 else "lower"
        rows.append(
            f"For {dimension}, Agentic XAI had a {direction} descriptive mean than MentaLLaMA "
            f"(Agentic XAI={row['agentic_xai_mean']:.3f}, MentaLLaMA={row['mentallama_mean']:.3f}, "
            f"difference={row['mean_difference']:.3f})."
        )
    return [
        "Phase 2 directly compared Agentic XAI with MentaLLaMA within participants.",
        *rows,
        "Overall, Agentic XAI showed small higher descriptive means for Correctness, Clarity, and Trust, while Helpfulness was essentially similar and slightly lower descriptively.",
    ]


def phase2_primary_text(df) -> list[str]:
    lines = []
    for dimension in ["Helpfulness", "Correctness", "Clarity", "Trust"]:
        row = row_for(df, dimension)
        lines.append(
            f"{dimension}: estimated Agentic XAI - MentaLLaMA difference={row['estimated_difference_agentic_minus_mentallama']:.3f}, "
            f"95% CI [{row['ci95_low']:.3f}, {row['ci95_high']:.3f}], raw p={row['raw_p_value']:.3f}, "
            f"Holm-adjusted p={row['holm_adjusted_p_value']:.3f}."
        )
    return [
        "The primary trial-level mixed-effects analysis did not find Holm-adjusted statistical evidence that Agentic XAI and MentaLLaMA received different explanation-quality ratings across the four primary outcomes.",
        *lines,
        "This means the data are not strong enough to support the claim that participants rated Agentic XAI differently from MentaLLaMA on the primary outcomes. It does not prove that the two systems are equivalent.",
    ]


def phase2_paired_text(df) -> list[str]:
    lines = []
    for dimension in ["Helpfulness", "Correctness", "Clarity", "Trust"]:
        row = row_for(df, dimension)
        lines.append(
            f"{dimension}: {int(row['n_paired_participants'])} paired participants, mean paired difference={row['mean_paired_difference']:.3f}, "
            f"median paired difference={row['median_paired_difference']:.3f}, Agentic XAI higher for {int(row['agentic_xai_higher_n'])}, "
            f"MentaLLaMA higher for {int(row['mentallama_higher_n'])}, tied for {int(row['tied_n'])}, "
            f"Holm-adjusted p={row['holm_adjusted_p_value']:.3f}."
        )
    return [
        "The participant-level analysis used Wilcoxon signed-rank tests because the sample was small and the paired differences came from ordinal 1-5 ratings.",
        *lines,
        "This robustness check agrees with the primary trial-level analysis: it does not provide statistical evidence of a system difference after correction.",
    ]


def phase2_question_text(interaction) -> list[str]:
    ps = ", ".join(f"{row['dimension']} p={row['p_value']:.3f}" for _, row in interaction.iterrows())
    return [
        f"The exploratory system by question-type interaction tests did not show evidence below 0.05: {ps}.",
        "This does not support a claim that Agentic XAI's mechanism selection was particularly more useful for one question type than another in this dataset.",
        "Question-type subgroup patterns should be treated as descriptive because the cell sizes are small.",
    ]


def phase2_severity_text(interaction) -> list[str]:
    ps = ", ".join(f"{row['dimension']} p={row['p_value']:.3f}" for _, row in interaction.iterrows())
    return [
        f"The exploratory system by severity interaction tests showed subgroup-dependent patterns for some outcomes: {ps}.",
        "The descriptive pattern suggested larger Agentic XAI advantages for no-depression passages, with smaller or negative differences for moderate and severe passages.",
        "Because this was a secondary subgroup analysis with small cells, it should be framed as an exploratory finding that motivates further study rather than as a firm conclusion.",
    ]


def phase2_interpretation_text() -> list[str]:
    return [
        "The main Phase 2 conclusion is that Agentic XAI did not receive statistically supported different ratings from MentaLLaMA in the primary participant-aware analysis.",
        "Agentic XAI had higher descriptive means for Correctness, Clarity, and Trust, but the confidence intervals included zero and Holm-adjusted p-values were not below 0.05.",
        "The participant-level robustness check was consistent with the primary analysis. The question-type analysis did not indicate that the system difference depended on question type.",
        "The severity analysis suggested possible subgroup differences, especially for Correctness, Clarity, and Trust, but these findings are exploratory and should not be overstated.",
    ]


def row_for(df, dimension: str):
    return df[df["dimension"] == dimension].iloc[0]


def explanation_label(value: str) -> str:
    return {
        "COUNTERFACTUAL": "Counterfactual",
        "HYBRID": "Hybrid",
        "RAG": "RAG",
        "SHAP": "SHAP",
    }.get(str(value), str(value))
