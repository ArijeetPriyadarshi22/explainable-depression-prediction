"""Run the reproducible thesis analysis pipeline.

Current implementation regenerates the complete analysis through Task 11 final
thesis-ready tables and figures.
"""

from __future__ import annotations

from datetime import datetime

from common_utils import append_section, ensure_output_dirs, get_paths
from final_outputs import create_final_outputs
from phase1_analysis import (
    analyze_phase1_reliability,
    analyze_phase1_statistics,
    analyze_phase1_severity,
    describe_phase1,
    inspect_phase1,
    phase1_descriptive_markdown,
    phase1_markdown,
    phase1_reliability_markdown,
    phase1_severity_markdown,
    phase1_statistics_markdown,
)
from phase2_analysis import (
    analyze_phase2_participant_paired,
    analyze_phase2_primary,
    analyze_phase2_question_type,
    analyze_phase2_reliability,
    analyze_phase2_severity,
    describe_phase2,
    inspect_phase2,
    phase2_descriptive_markdown,
    phase2_markdown,
    phase2_participant_paired_markdown,
    phase2_primary_markdown,
    phase2_question_type_markdown,
    phase2_reliability_markdown,
    phase2_severity_markdown,
)
from thesis_interpretation import create_thesis_interpretation


def main() -> None:
    paths = get_paths()
    ensure_output_dirs(paths)

    phase1 = inspect_phase1(paths.phase1_csv, paths.tables_dir)
    phase2 = inspect_phase2(paths.phase2_csv, paths.tables_dir)
    phase1_descriptives = describe_phase1(paths.phase1_csv, paths.tables_dir, paths.figures_dir)
    phase2_descriptives = describe_phase2(paths.phase2_csv, paths.tables_dir, paths.figures_dir)

    task1_report_path = paths.results_dir / "task1_data_inspection.md"
    task1_report_path.write_text("\n".join(build_task1_report(phase1, phase2)), encoding="utf-8")

    report_lines = build_task2_report(phase1, phase2, phase1_descriptives, phase2_descriptives)
    report_path = paths.results_dir / "task2_descriptive_statistics.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    task3_report_path = paths.results_dir / "task3_statistical_method_recommendation.md"
    task3_report_path.write_text("\n".join(build_task3_report(phase1, phase2)), encoding="utf-8")

    phase1_statistics = analyze_phase1_statistics(paths.phase1_csv, paths.tables_dir)
    task4_report_path = paths.results_dir / "task4_phase1_statistical_analysis.md"
    task4_report_path.write_text(
        "\n".join(build_task4_phase1_report(phase1, phase1_descriptives, phase1_statistics)),
        encoding="utf-8",
    )

    phase1_severity = analyze_phase1_severity(paths.phase1_csv, paths.tables_dir, paths.figures_dir)
    task5_report_path = paths.results_dir / "task5_phase1_severity_analysis.md"
    task5_report_path.write_text(
        "\n".join(build_task5_phase1_severity_report(phase1, phase1_descriptives, phase1_severity)),
        encoding="utf-8",
    )

    phase2_primary = analyze_phase2_primary(paths.phase2_csv, paths.tables_dir)
    task6_report_path = paths.results_dir / "task6_phase2_primary_analysis.md"
    task6_report_path.write_text(
        "\n".join(build_task6_phase2_primary_report(phase2, phase2_descriptives, phase2_primary)),
        encoding="utf-8",
    )

    phase2_participant_paired = analyze_phase2_participant_paired(paths.phase2_csv, paths.tables_dir)
    task7_report_path = paths.results_dir / "task7_phase2_participant_paired_analysis.md"
    task7_report_path.write_text(
        "\n".join(
            build_task7_phase2_participant_paired_report(
                phase2,
                phase2_descriptives,
                phase2_primary,
                phase2_participant_paired,
            )
        ),
        encoding="utf-8",
    )

    phase2_question_type = analyze_phase2_question_type(paths.phase2_csv, paths.tables_dir, paths.figures_dir)
    task8_report_path = paths.results_dir / "task8_phase2_question_type_analysis.md"
    task8_report_path.write_text(
        "\n".join(
            build_task8_phase2_question_type_report(
                phase2,
                phase2_descriptives,
                phase2_primary,
                phase2_question_type,
            )
        ),
        encoding="utf-8",
    )

    phase2_severity = analyze_phase2_severity(paths.phase2_csv, paths.tables_dir, paths.figures_dir)
    task9_report_path = paths.results_dir / "task9_phase2_severity_analysis.md"
    task9_report_path.write_text(
        "\n".join(
            build_task9_phase2_severity_report(
                phase2,
                phase2_descriptives,
                phase2_primary,
                phase2_severity,
            )
        ),
        encoding="utf-8",
    )

    phase1_reliability = analyze_phase1_reliability(paths.phase1_csv, paths.tables_dir)
    phase2_reliability = analyze_phase2_reliability(paths.phase2_csv, paths.tables_dir)
    task10_report_path = paths.results_dir / "task10_reliability_overall_score.md"
    task10_report_path.write_text(
        "\n".join(build_task10_reliability_report(phase1_reliability, phase2_reliability)),
        encoding="utf-8",
    )

    final_outputs = create_final_outputs(paths, {"phase1": phase1, "phase2": phase2})
    task11_report_path = final_outputs["report_path"]
    task12_report_path = create_thesis_interpretation(paths)

    print("Task 12 thesis interpretation complete.")
    print(f"Phase 1: {phase1['n_rows']} trials from {phase1['n_participants']} participants.")
    print(f"Phase 2: {phase2['n_rows']} trials from {phase2['n_participants']} participants.")
    print(f"Task 1 report: {task1_report_path}")
    print(f"Task 2 report: {report_path}")
    print(f"Task 3 report: {task3_report_path}")
    print(f"Task 4 report: {task4_report_path}")
    print(f"Task 5 report: {task5_report_path}")
    print(f"Task 6 report: {task6_report_path}")
    print(f"Task 7 report: {task7_report_path}")
    print(f"Task 8 report: {task8_report_path}")
    print(f"Task 9 report: {task9_report_path}")
    print(f"Task 10 report: {task10_report_path}")
    print(f"Task 11 report: {task11_report_path}")
    print(f"Task 12 report: {task12_report_path}")
    print(f"Tables: {paths.tables_dir}")
    print(f"Figures: {paths.figures_dir}")
    print("Stop point reached after Task 12.")


def build_task1_report(phase1: dict[str, object], phase2: dict[str, object]) -> list[str]:
    lines = [
        "# Task 1 - Data Inspection",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report inspects the two study datasets separately. It does not run statistical tests.",
        "",
    ]

    append_section(
        lines,
        "Why Trial Rows Are Not Independent",
        [
            "Each participant rated more than one explanation. Ratings from the same participant tend to be related because the same person brings the same expectations, rating habits, attention level, and interpretation style across trials.",
            "That means 20 rows from one participant do not contain the same amount of independent information as 20 rows from 20 different participants.",
            "For the later primary analysis, the correct approach is therefore participant-aware: keep every valid trial, but use a repeated-measures or mixed-effects method that accounts for participant ID.",
            "The participant-level summaries are still useful as a descriptive and robustness check, but they should not replace the primary trial-level analysis.",
        ],
    )

    lines.extend(phase1_markdown(phase1))
    lines.extend(phase2_markdown(phase2))

    append_section(
        lines,
        "Stop Point",
        [
            "Task 1 is complete. The next phase should add statistical tests only after explicit confirmation.",
        ],
    )
    return lines


def build_task2_report(
    phase1: dict[str, object],
    phase2: dict[str, object],
    phase1_descriptives: dict[str, object],
    phase2_descriptives: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 2 - Descriptive Statistics",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report includes Task 1 inspection context and Task 2 descriptive statistics. It does not run statistical tests and does not describe anything as statistically significant.",
        "",
    ]
    append_section(
        lines,
        "Plain-Language Reading Guide",
        [
            "The trial-level tables summarize every valid row, so they preserve the full amount of observed rating information.",
            "The participant-level tables first average ratings within each participant and condition. This is easier to explain and useful as a secondary descriptive view.",
            "Confidence intervals here are descriptive intervals around observed means. They are not hypothesis tests.",
            "Use cautious wording: higher descriptive mean, lower descriptive mean, or similar ratings.",
        ],
    )
    lines.extend(phase1_markdown(phase1))
    lines.extend(phase1_descriptive_markdown(phase1_descriptives))
    lines.extend(phase2_markdown(phase2))
    lines.extend(phase2_descriptive_markdown(phase2_descriptives))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 2 is complete. The next phase should add statistical tests only after explicit confirmation.",
        ],
    )
    return lines


def build_task3_report(phase1: dict[str, object], phase2: dict[str, object]) -> list[str]:
    phase1_trials = phase1["trials_per_participant"]
    phase2_trials = phase2["trials_per_participant"]
    assert isinstance(phase1_trials, dict)
    assert isinstance(phase2_trials, dict)

    lines = [
        "# Task 3 - Statistical Method Recommendation",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report chooses the simplest defensible statistical approach before hypothesis testing. It does not run tests or fit models.",
        "",
    ]

    append_section(
        lines,
        "Data Features That Matter",
        [
            "Ratings are 1-5 Likert-style responses. They are ordered categories, but in small user studies it is common to summarize them with means and use simple participant-aware models when the goal is an interpretable thesis analysis.",
            f"Phase 1 has {phase1['n_rows']} trial rows from {phase1['n_participants']} participants. The design is repeated because each participant rated multiple explanations. It is also unbalanced: participants contributed between {phase1_trials['min_trials']} and {phase1_trials['max_trials']} trials, and not every participant rated every explanation type equally often.",
            f"Phase 2 has {phase2['n_rows']} trial rows from {phase2['n_participants']} participants. It is a within-participant comparison because participants rated both Agentic XAI and MentaLLaMA, with one incomplete participant in the current file.",
            "Independent-samples tests are not appropriate as the primary analysis because rows from the same participant are related.",
        ],
    )

    append_section(
        lines,
        "Plain-English Concepts",
        [
            "Repeated measures means the same participant gives more than one rating. Their ratings are connected because the same person may consistently rate higher, lower, more cautiously, or more generously than another person.",
            "Participant ID must be accounted for because otherwise the analysis treats repeated rows from one participant as if they came from different people. That would overstate the amount of independent evidence.",
            "Row-level analysis is useful because it keeps every valid trial. This preserves information about explanation type or system, passage, severity, question type, and trial-to-trial variation.",
            "Participant-level analysis is also useful because it averages each participant within each condition. This gives an easy-to-explain robustness check and directly shows whether the pattern is consistent across people.",
            "A p-value answers this kind of question: if there were really no difference between conditions, how surprising would data like this be under the model? It is not the probability that the hypothesis is true.",
            "A confidence interval gives a plausible range for an estimated quantity, such as a mean difference. Narrow intervals mean the estimate is more precise; wide intervals mean more uncertainty.",
            "An effect size describes how large a difference is, not just whether it is detectable. For thesis reporting, effect sizes help explain practical importance.",
        ],
    )

    append_section(
        lines,
        "Recommended Primary Method",
        [
            "Use a simple linear mixed-effects model for each rating dimension separately.",
            "Phase 1 primary model: rating ~ explanation_type + (1 | participant). In Python/statsmodels wording, this is a mixed model with explanation type as a fixed effect and a random participant intercept.",
            "Phase 2 primary model: rating ~ explanation_system + (1 | participant). The main fixed effect is Agentic XAI vs MentaLLaMA, with a random participant intercept.",
            "The random participant intercept lets each participant have their own baseline rating level. This directly handles repeated ratings without making the model complicated.",
            "This approach is simpler and more defensible for the current data than a large model with many interactions.",
        ],
    )

    append_section(
        lines,
        "Why This Is Defensible With Likert Ratings",
        [
            "The ratings are ordinal, so an ordinal mixed model would be theoretically attractive. In practice, ordinal mixed models are harder to explain, less available in the requested Python stack, and can be unstable with small samples.",
            "A linear mixed-effects model treats the 1-5 scale approximately as numeric. That is a pragmatic and common choice when the scale has several ordered points, the thesis needs clear interpretation, and results are reported cautiously.",
            "To avoid overclaiming, report means, confidence intervals, effect sizes, and robustness checks. Avoid claiming that a one-point change has exactly equal meaning everywhere on the scale.",
        ],
    )

    append_section(
        lines,
        "Secondary Variables",
        [
            "Severity and question type should be treated as secondary variables, not automatically added into the main model.",
            "For Phase 1, severity can be inspected descriptively and optionally added in a sensitivity model: rating ~ explanation_type + severity + (1 | participant).",
            "For Phase 2, question type and severity can be inspected descriptively and optionally added in sensitivity models. The primary research question should remain Agentic XAI vs MentaLLaMA.",
            "Avoid high-order interactions unless there is a strong thesis reason and enough data in every cell. The current sample is small, so complicated models would be fragile.",
        ],
    )

    append_section(
        lines,
        "Recommended Secondary Checks",
        [
            "Participant-level Phase 1 check: average each participant within each explanation type and rating dimension, then run a repeated-measures comparison only where participants have data for all explanation types. If too much data is missing, report it mainly as descriptive.",
            "Participant-level Phase 2 check: average each participant's Agentic XAI and MentaLLaMA ratings, calculate paired differences, and use a paired test as a robustness check.",
            "For Phase 2 participant-level robustness, a paired t-test is easy to explain if differences are reasonably symmetric. A Wilcoxon signed-rank test is a non-parametric alternative for the small Likert-scale sample.",
            "These checks should support interpretation. They should not replace the primary mixed-effects model or be selected only because they give a more favorable p-value.",
        ],
    )

    append_section(
        lines,
        "What To Report Later",
        [
            "For each rating dimension, report the estimated condition means or mean differences, 95% confidence intervals, p-values, and effect sizes.",
            "For Phase 1, report the overall explanation-type test first, then pairwise comparisons between explanation types with multiplicity correction.",
            "For Phase 2, report the Agentic XAI minus MentaLLaMA estimate for each dimension.",
            "Use careful language: evidence of a difference, no clear evidence of a difference, higher estimated rating, lower estimated rating. Do not imply clinical conclusions from explanation-quality ratings.",
        ],
    )

    append_section(
        lines,
        "Stop Point",
        [
            "Task 3 is complete. The next phase should run hypothesis tests only after explicit confirmation.",
        ],
    )
    return lines


def build_task4_phase1_report(
    phase1: dict[str, object],
    phase1_descriptives: dict[str, object],
    phase1_statistics: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 4 - Phase 1 Statistical Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report analyzes Phase 1 only. Phase 2 hypothesis tests are not run here.",
        "",
    ]
    append_section(
        lines,
        "Analysis Plan",
        [
            "Primary question: do SHAP, Counterfactual, RAG, and Hybrid explanations differ in perceived explanation quality?",
            "The four rating dimensions are tested separately: Clarity, Correctness, Helpfulness, and Trust.",
            "The primary model is participant-aware: rating ~ explanation_type + (1 | participant).",
            "The model keeps every valid trial row while accounting for repeated ratings from the same participant.",
            "Overall explanation-type effects are tested first. Pairwise comparisons are only run after an overall p-value below 0.05 and are Holm-corrected.",
        ],
    )
    lines.extend(phase1_markdown(phase1))
    lines.extend(phase1_descriptive_markdown(phase1_descriptives))
    lines.extend(phase1_statistics_markdown(phase1_statistics))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 4 is complete. No Phase 2 statistical tests were run.",
        ],
    )
    return lines


def build_task5_phase1_severity_report(
    phase1: dict[str, object],
    phase1_descriptives: dict[str, object],
    phase1_severity: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 5 - Phase 1 Severity Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report examines Phase 1 severity as a secondary/exploratory analysis. Phase 2 hypothesis tests are not run here.",
        "",
    ]
    append_section(
        lines,
        "Analysis Plan",
        [
            "First, ratings are summarized by severity category: no depression, moderate, and severe.",
            "Then severity is checked with a simple participant-aware mixed model: rating ~ severity + (1 | participant).",
            "Because the explanation type x severity cells are populated, an exploratory interaction model is also compared against an additive model.",
            "The interaction analysis is exploratory. Small subgroups should not be used for strong claims.",
        ],
    )
    lines.extend(phase1_markdown(phase1))
    lines.extend(phase1_descriptive_markdown(phase1_descriptives))
    lines.extend(phase1_severity_markdown(phase1_severity))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 5 is complete. No Phase 2 statistical tests were run.",
        ],
    )
    return lines


def build_task6_phase2_primary_report(
    phase2: dict[str, object],
    phase2_descriptives: dict[str, object],
    phase2_primary: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 6 - Phase 2 Primary Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report performs the main Phase 2 comparison: Agentic XAI versus MentaLLaMA.",
        "",
    ]
    append_section(
        lines,
        "Analysis Plan",
        [
            "The four primary outcomes are Helpfulness, Correctness, Clarity, and Trust.",
            "Each outcome is analyzed with a trial-level mixed-effects model: rating ~ explanation_system + (1 | participant).",
            "The model keeps all valid Phase 2 trial rows while accounting for repeated ratings from the same participant.",
            "Holm correction is applied across the four primary outcomes.",
        ],
    )
    lines.extend(phase2_markdown(phase2))
    lines.extend(phase2_descriptive_markdown(phase2_descriptives))
    lines.extend(phase2_primary_markdown(phase2_primary))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 6 is complete. No secondary Phase 2 analyses were run.",
        ],
    )
    return lines


def build_task7_phase2_participant_paired_report(
    phase2: dict[str, object],
    phase2_descriptives: dict[str, object],
    phase2_primary: dict[str, object],
    phase2_participant_paired: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 7 - Phase 2 Participant-Level Paired Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report performs the secondary participant-level robustness check for Phase 2.",
        "",
    ]
    append_section(
        lines,
        "Analysis Plan",
        [
            "For every participant, ratings are averaged separately for Agentic XAI and MentaLLaMA.",
            "For each dimension, the paired difference is Agentic XAI mean minus MentaLLaMA mean.",
            "The paired test is applied to participant-level differences, not to raw trial rows.",
            "This is a robustness check. The primary thesis inference remains the Task 6 trial-level mixed-effects analysis.",
        ],
    )
    lines.extend(phase2_markdown(phase2))
    lines.extend(phase2_descriptive_markdown(phase2_descriptives))
    lines.extend(phase2_primary_markdown(phase2_primary))
    lines.extend(phase2_participant_paired_markdown(phase2_participant_paired, phase2_primary))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 7 is complete. No additional Phase 2 exploratory analyses were run.",
        ],
    )
    return lines


def build_task8_phase2_question_type_report(
    phase2: dict[str, object],
    phase2_descriptives: dict[str, object],
    phase2_primary: dict[str, object],
    phase2_question_type: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 8 - Phase 2 Question-Type Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report examines whether the Agentic XAI versus MentaLLaMA difference depends on question type.",
        "",
    ]
    append_section(
        lines,
        "Analysis Plan",
        [
            "First, ratings are summarized for each system x question-type cell.",
            "Then an exploratory mixed-effects interaction model is run for each rating dimension.",
            "The interaction test asks whether the system difference changes across SHAP, Counterfactual, RAG, and Hybrid questions.",
            "This is secondary to the Task 6 primary Phase 2 comparison.",
        ],
    )
    lines.extend(phase2_markdown(phase2))
    lines.extend(phase2_descriptive_markdown(phase2_descriptives))
    lines.extend(phase2_primary_markdown(phase2_primary))
    lines.extend(phase2_question_type_markdown(phase2_question_type))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 8 is complete. No further analyses were run.",
        ],
    )
    return lines


def build_task9_phase2_severity_report(
    phase2: dict[str, object],
    phase2_descriptives: dict[str, object],
    phase2_primary: dict[str, object],
    phase2_severity: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 9 - Phase 2 Severity Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report examines whether the Agentic XAI versus MentaLLaMA difference depends on passage severity.",
        "",
    ]
    append_section(
        lines,
        "Analysis Plan",
        [
            "First, ratings are summarized for each system x severity cell.",
            "Then an exploratory mixed-effects interaction model is run for each rating dimension.",
            "The interaction test asks whether the system difference changes across no depression, moderate, and severe passages.",
            "This is secondary to the Task 6 primary Phase 2 comparison.",
        ],
    )
    lines.extend(phase2_markdown(phase2))
    lines.extend(phase2_descriptive_markdown(phase2_descriptives))
    lines.extend(phase2_primary_markdown(phase2_primary))
    lines.extend(phase2_severity_markdown(phase2_severity))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 9 is complete. No further analyses were run.",
        ],
    )
    return lines


def build_task10_reliability_report(
    phase1_reliability: dict[str, object],
    phase2_reliability: dict[str, object],
) -> list[str]:
    lines = [
        "# Task 10 - Reliability / Overall Score",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report checks whether the four rating dimensions are sufficiently related to justify an overall explanation-quality score as a secondary summary.",
        "",
    ]
    append_section(
        lines,
        "Plain-Language Guide",
        [
            "Cronbach's alpha measures internal consistency: whether several rating items tend to behave like they are measuring the same broader concept.",
            "A higher alpha means the four ratings move together more strongly. A common practical threshold is 0.70 for an acceptable secondary composite.",
            "Alpha does not prove that the items are identical, and it does not mean the individual dimensions should be discarded.",
            "The primary thesis results should still report Clarity, Correctness, Helpfulness, and Trust separately.",
            "Any overall score created here is only a secondary summary.",
        ],
    )
    lines.extend(phase1_reliability_markdown(phase1_reliability))
    lines.extend(phase2_reliability_markdown(phase2_reliability))
    append_section(
        lines,
        "Stop Point",
        [
            "Task 10 is complete. The four individual rating dimensions remain the primary outcomes.",
        ],
    )
    return lines


if __name__ == "__main__":
    main()
