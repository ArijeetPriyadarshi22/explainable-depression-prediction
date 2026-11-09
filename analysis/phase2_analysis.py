"""Phase 2 inspection and later analysis steps."""

from __future__ import annotations

import math
import warnings
from pathlib import Path

from common_utils import (
    append_section,
    count_by,
    crosstab,
    duplicate_key_summary,
    exact_duplicate_count,
    format_count_table,
    missing_value_summary,
    participant_condition_counts,
    participant_condition_means,
    participant_trial_summary,
    read_csv_rows,
    reliability_tables,
    validate_ratings,
    condition_descriptives,
    condition_mean_differences,
    paired_participant_summary,
    write_table,
    write_ci_svg,
    write_distribution_svg,
    write_interaction_svg,
    write_phase2_paired_svg,
)


PHASE2_RATING_COLUMNS = [
    "rating_answered",
    "rating_supported",
    "rating_understandable",
    "rating_confidence",
]

PHASE2_RATING_CONCEPTS = {
    "rating_answered": "Helpfulness",
    "rating_supported": "Correctness",
    "rating_understandable": "Clarity",
    "rating_confidence": "Trust",
}

PHASE2_REQUIRED_COLUMNS = [
    "participant_id",
    "session_id",
    "trial_number",
    "passage_id",
    "severity",
    "question_type",
    "explanation_system",
    "assigned_system",
    *PHASE2_RATING_COLUMNS,
]
PHASE2_SYSTEM_ORDER = ["mentallama", "agentic_xai"]
PHASE2_QUESTION_TYPE_ORDER = ["shap", "counterfactual", "rag", "hybrid"]
PHASE2_QUESTION_TYPE_LABELS = {
    "shap": "SHAP",
    "counterfactual": "Counterfactual",
    "rag": "RAG",
    "hybrid": "Hybrid",
}
PHASE2_SEVERITY_ORDER = ["none", "moderate", "severe"]
PHASE2_SEVERITY_LABELS = {
    "none": "no depression",
    "no depression": "no depression",
    "not depression": "no depression",
    "moderate": "moderate",
    "severe": "severe",
}


def inspect_phase2(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    rows = read_csv_rows(csv_path)
    validate_required_columns(rows, PHASE2_REQUIRED_COLUMNS, csv_path)

    participant_summary = participant_trial_summary(rows, "participant_id")
    missing = missing_value_summary(rows)
    invalid_ratings = validate_ratings(rows, PHASE2_RATING_COLUMNS)
    exact_duplicates = exact_duplicate_count(rows)
    duplicate_trials = duplicate_key_summary(rows, ["participant_id", "session_id", "trial_number"])

    outputs = {
        "participant_trials": participant_summary["participant_trial_rows"],
        "missing_values": missing,
        "invalid_ratings": invalid_ratings,
        "system_counts": count_by(rows, ["explanation_system"]),
        "assigned_system_counts": count_by(rows, ["assigned_system"]),
        "severity_counts": count_by(rows, ["severity"]),
        "question_type_counts": count_by(rows, ["question_type"]),
        "participant_by_system": participant_condition_counts(rows, "participant_id", "explanation_system"),
        "system_by_question_type": crosstab(rows, "explanation_system", "question_type"),
        "system_by_severity": crosstab(rows, "explanation_system", "severity"),
        "question_type_by_severity": crosstab(rows, "question_type", "severity"),
        "duplicate_trial_keys": duplicate_trials,
    }

    prefix = tables_dir / "phase2_task1"
    for name, table_rows in outputs.items():
        write_table(prefix.with_name(f"{prefix.name}_{name}.csv"), table_rows)

    return {
        "name": "Phase 2",
        "csv_path": str(csv_path),
        "n_rows": len(rows),
        "n_participants": participant_summary["n_participants"],
        "n_sessions": len({row["session_id"].strip() for row in rows if row.get("session_id", "").strip()}),
        "trials_per_participant": participant_summary,
        "missing_values": missing,
        "exact_duplicate_rows": exact_duplicates,
        "duplicate_trial_key_rows": len(duplicate_trials),
        "invalid_ratings": invalid_ratings,
        "incomplete_participants": participant_summary["incomplete_participants"],
        "tables": outputs,
    }


def describe_phase2(csv_path: Path, tables_dir: Path, figures_dir: Path) -> dict[str, object]:
    rows = read_csv_rows(csv_path)
    validate_required_columns(rows, PHASE2_REQUIRED_COLUMNS, csv_path)

    descriptives = condition_descriptives(
        rows,
        participant_column="participant_id",
        condition_column="explanation_system",
        rating_map=PHASE2_RATING_CONCEPTS,
    )
    participant_means = participant_condition_means(
        rows,
        participant_column="participant_id",
        condition_column="explanation_system",
        rating_map=PHASE2_RATING_CONCEPTS,
    )
    differences = condition_mean_differences(
        descriptives,
        first_condition="agentic_xai",
        second_condition="mentallama",
        first_label="agentic_xai",
        second_label="mentallama",
    )
    paired = paired_participant_summary(
        participant_means,
        first_condition="agentic_xai",
        second_condition="mentallama",
        first_label="agentic_xai",
        second_label="mentallama",
    )

    write_table(tables_dir / "phase2_task2_trial_level_descriptives.csv", descriptives)
    write_table(tables_dir / "phase2_task2_agentic_minus_mentallama.csv", differences)
    write_table(tables_dir / "phase2_task2_participant_level_means_long.csv", participant_means)
    write_table(tables_dir / "phase2_task2_participant_paired_means.csv", paired)
    write_distribution_svg(
        figures_dir / "phase2_task2_rating_distributions.svg",
        rows,
        condition_column="explanation_system",
        rating_map=PHASE2_RATING_CONCEPTS,
        title="Phase 2 Rating Distributions by Explanation System",
    )
    write_ci_svg(
        figures_dir / "phase2_task2_descriptive_ci.svg",
        descriptives,
        title="Phase 2 Descriptive Means with 95% CIs",
    )
    write_phase2_paired_svg(
        figures_dir / "phase2_task2_participant_paired_means.svg",
        paired,
        title="Phase 2 Participant-Level Paired Means",
    )

    return {
        "trial_level_descriptives": descriptives,
        "mean_differences": differences,
        "participant_level_means": participant_means,
        "participant_paired_means": paired,
        "figure_paths": [
            str(figures_dir / "phase2_task2_rating_distributions.svg"),
            str(figures_dir / "phase2_task2_descriptive_ci.svg"),
            str(figures_dir / "phase2_task2_participant_paired_means.svg"),
        ],
    }


def analyze_phase2_primary(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    pd, smf, stats = import_stats_stack()
    df = pd.read_csv(csv_path)
    validate_required_columns(df.to_dict("records"), PHASE2_REQUIRED_COLUMNS, csv_path)

    df["participant"] = df["participant_id"].astype(str)
    df["system"] = pd.Categorical(df["explanation_system"], categories=PHASE2_SYSTEM_ORDER, ordered=False)

    rows: list[dict[str, object]] = []
    model_notes: list[dict[str, object]] = []
    for rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
        model_df = df[["participant", "system", rating_column]].dropna().copy()
        model_df["rating"] = pd.to_numeric(model_df[rating_column], errors="coerce")
        model_df = model_df.dropna(subset=["rating", "system"])

        agentic_mean = float(model_df.loc[model_df["system"] == "agentic_xai", "rating"].mean())
        mentallama_mean = float(model_df.loc[model_df["system"] == "mentallama", "rating"].mean())

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = smf.mixedlm(
                'rating ~ C(system, Treatment(reference="mentallama"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=200, disp=False)
        append_model_warnings(model_notes, caught, dimension)

        term = 'C(system, Treatment(reference="mentallama"))[T.agentic_xai]'
        estimate = float(model.fe_params[term])
        se = float(model.bse[term])
        ci_low = estimate - 1.96 * se
        ci_high = estimate + 1.96 * se
        p_value = float(model.pvalues[term])
        residual_sd = math.sqrt(float(model.scale))

        rows.append(
            {
                "dimension": dimension,
                "agentic_xai_descriptive_mean": round(agentic_mean, 3),
                "mentallama_descriptive_mean": round(mentallama_mean, 3),
                "estimated_difference_agentic_minus_mentallama": round(estimate, 4),
                "ci95_low": round(ci_low, 4),
                "ci95_high": round(ci_high, 4),
                "raw_p_value": round(p_value, 6),
                "holm_adjusted_p_value": "",
                "effect_size_metric": "standardized difference using model residual SD",
                "effect_size": round(estimate / residual_sd, 4) if residual_sd > 0 else "",
                "n_trials": len(model_df),
                "n_participants": model_df["participant"].nunique(),
                "converged": bool(model.converged),
                "model": "rating ~ explanation_system + (1 | participant)",
            }
        )

    rows = add_holm_adjustment(rows)
    model_notes = unique_note_rows(model_notes)
    write_table(tables_dir / "phase2_task6_primary_mixed_model.csv", rows)
    write_table(tables_dir / "phase2_task6_model_notes.csv", model_notes)
    return {"primary": rows, "model_notes": model_notes}


def analyze_phase2_participant_paired(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    pd, _smf, stats = import_stats_stack()
    df = pd.read_csv(csv_path)
    validate_required_columns(df.to_dict("records"), PHASE2_REQUIRED_COLUMNS, csv_path)
    df["participant"] = df["participant_id"].astype(str)

    participant_rows = []
    participant_index = sorted(df["participant"].unique())
    for participant in participant_index:
        participant_df = df[df["participant"] == participant]
        row: dict[str, object] = {"participant_id": participant}
        for rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
            agentic_values = participant_df.loc[
                participant_df["explanation_system"] == "agentic_xai",
                rating_column,
            ]
            mentallama_values = participant_df.loc[
                participant_df["explanation_system"] == "mentallama",
                rating_column,
            ]
            agentic_mean = pd.to_numeric(agentic_values, errors="coerce").mean()
            mentallama_mean = pd.to_numeric(mentallama_values, errors="coerce").mean()
            row[f"agentic_xai_{dimension.lower()}_mean"] = round(float(agentic_mean), 3) if pd.notna(agentic_mean) else ""
            row[f"mentallama_{dimension.lower()}_mean"] = round(float(mentallama_mean), 3) if pd.notna(mentallama_mean) else ""
            row[f"{dimension.lower()}_difference"] = (
                round(float(agentic_mean - mentallama_mean), 3)
                if pd.notna(agentic_mean) and pd.notna(mentallama_mean)
                else ""
            )
        participant_rows.append(row)

    test_rows = []
    test_notes: list[dict[str, object]] = []
    for _rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
        diff_column = f"{dimension.lower()}_difference"
        diffs = [float(row[diff_column]) for row in participant_rows if row[diff_column] != ""]
        positive = sum(1 for value in diffs if value > 0)
        negative = sum(1 for value in diffs if value < 0)
        tied = sum(1 for value in diffs if value == 0)
        nonzero = [value for value in diffs if value != 0]

        if nonzero:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                wilcoxon = stats.wilcoxon(diffs, zero_method="wilcox", alternative="two-sided", method="auto")
            append_model_warnings(test_notes, caught, dimension)
            statistic = float(wilcoxon.statistic)
            p_value = float(wilcoxon.pvalue)
            effect_size = wilcoxon_rank_biserial(nonzero)
            note = "Wilcoxon signed-rank test on participant-level paired differences."
        else:
            statistic = ""
            p_value = 1.0
            effect_size = 0.0
            note = "All paired differences were zero; no Wilcoxon statistic was needed."

        test_rows.append(
            {
                "dimension": dimension,
                "n_paired_participants": len(diffs),
                "mean_paired_difference": round(float(pd.Series(diffs).mean()), 4) if diffs else "",
                "median_paired_difference": round(float(pd.Series(diffs).median()), 4) if diffs else "",
                "agentic_xai_higher_n": positive,
                "mentallama_higher_n": negative,
                "tied_n": tied,
                "test": "Wilcoxon signed-rank",
                "test_statistic": round(statistic, 4) if statistic != "" else "",
                "raw_p_value": round(p_value, 6),
                "holm_adjusted_p_value": "",
                "effect_size_metric": "rank-biserial correlation",
                "effect_size": round(effect_size, 4),
                "interpretation_note": note,
            }
        )

    test_rows = add_holm_adjustment(test_rows)
    test_notes = unique_note_rows(test_notes)
    write_table(tables_dir / "phase2_task7_participant_level_wide_means.csv", participant_rows)
    write_table(tables_dir / "phase2_task7_participant_paired_tests.csv", test_rows)
    write_table(tables_dir / "phase2_task7_test_notes.csv", test_notes)
    return {
        "participant_means_wide": participant_rows,
        "paired_tests": test_rows,
        "test_notes": test_notes,
        "test_selection": [
            "The Wilcoxon signed-rank test was selected for the participant-level robustness check.",
            "Reason: the data are paired within participant, the sample is small, and the values are means of 1-5 Likert ratings, so a non-parametric paired test is easier to defend than assuming normally distributed paired differences.",
            "The primary thesis inference remains the trial-level mixed-effects model from Task 6.",
        ],
    }


def analyze_phase2_question_type(csv_path: Path, tables_dir: Path, figures_dir: Path) -> dict[str, object]:
    pd, smf, stats = import_stats_stack()
    df = pd.read_csv(csv_path)
    validate_required_columns(df.to_dict("records"), PHASE2_REQUIRED_COLUMNS, csv_path)
    df["participant"] = df["participant_id"].astype(str)
    df["system"] = pd.Categorical(df["explanation_system"], categories=PHASE2_SYSTEM_ORDER, ordered=False)
    df["question_type_clean"] = pd.Categorical(
        df["question_type"].astype(str).str.strip().str.lower(),
        categories=PHASE2_QUESTION_TYPE_ORDER,
        ordered=False,
    )
    df["question_type_label"] = df["question_type_clean"].astype(str).map(PHASE2_QUESTION_TYPE_LABELS)

    descriptives = []
    support = []
    for system in PHASE2_SYSTEM_ORDER:
        for question_type in PHASE2_QUESTION_TYPE_ORDER:
            subset = df[(df["system"] == system) & (df["question_type_clean"] == question_type)]
            support.append(
                {
                    "system": system,
                    "question_type": PHASE2_QUESTION_TYPE_LABELS[question_type],
                    "n_trials": len(subset),
                    "n_participants": subset["participant"].nunique() if len(subset) else 0,
                }
            )
            for rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
                descriptives.append(
                    phase2_descriptive_row(
                        subset,
                        rating_column,
                        dimension,
                        system=system,
                        question_type=PHASE2_QUESTION_TYPE_LABELS[question_type],
                    )
                )

    interaction_rows, model_notes = phase2_question_type_interaction_rows(df, smf, stats)
    write_table(tables_dir / "phase2_task8_system_by_question_type_descriptives.csv", descriptives)
    write_table(tables_dir / "phase2_task8_system_by_question_type_support.csv", support)
    write_table(tables_dir / "phase2_task8_interaction_mixed_model.csv", interaction_rows)
    write_table(tables_dir / "phase2_task8_model_notes.csv", model_notes)
    write_interaction_svg(
        figures_dir / "phase2_task8_system_by_question_type_interaction.svg",
        descriptives,
        x_column="question_type",
        line_column="system",
        value_column="mean",
        panel_column="dimension",
        title="Phase 2 Exploratory System by Question Type Means",
        x_order=[PHASE2_QUESTION_TYPE_LABELS[item] for item in PHASE2_QUESTION_TYPE_ORDER],
        line_order=PHASE2_SYSTEM_ORDER,
    )
    return {
        "descriptives": descriptives,
        "support": support,
        "interaction_models": interaction_rows,
        "model_notes": model_notes,
        "figure_paths": [str(figures_dir / "phase2_task8_system_by_question_type_interaction.svg")],
    }


def analyze_phase2_severity(csv_path: Path, tables_dir: Path, figures_dir: Path) -> dict[str, object]:
    pd, smf, stats = import_stats_stack()
    df = pd.read_csv(csv_path)
    validate_required_columns(df.to_dict("records"), PHASE2_REQUIRED_COLUMNS, csv_path)
    df["participant"] = df["participant_id"].astype(str)
    df["system"] = pd.Categorical(df["explanation_system"], categories=PHASE2_SYSTEM_ORDER, ordered=False)
    df["severity_clean"] = df["severity"].astype(str).str.strip().str.lower()
    df["severity_label"] = df["severity_clean"].map(PHASE2_SEVERITY_LABELS)
    df["severity_label"] = pd.Categorical(
        df["severity_label"],
        categories=[PHASE2_SEVERITY_LABELS[item] for item in PHASE2_SEVERITY_ORDER],
        ordered=True,
    )

    descriptives = []
    support = []
    severity_labels = [PHASE2_SEVERITY_LABELS[item] for item in PHASE2_SEVERITY_ORDER]
    for system in PHASE2_SYSTEM_ORDER:
        for severity in severity_labels:
            subset = df[(df["system"] == system) & (df["severity_label"] == severity)]
            support.append(
                {
                    "system": system,
                    "severity": severity,
                    "n_trials": len(subset),
                    "n_participants": subset["participant"].nunique() if len(subset) else 0,
                }
            )
            for rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
                descriptives.append(
                    phase2_descriptive_row(
                        subset,
                        rating_column,
                        dimension,
                        system=system,
                        severity=severity,
                    )
                )

    interaction_supported = all(int(row["n_trials"]) >= 10 for row in support)
    if interaction_supported:
        interaction_rows, model_notes = phase2_severity_interaction_rows(df, smf, stats)
    else:
        interaction_rows = []
        model_notes = [
            {
                "dimension": "All",
                "note": "System x severity model was not run because at least one cell had fewer than 10 trials.",
            }
        ]

    write_table(tables_dir / "phase2_task9_system_by_severity_descriptives.csv", descriptives)
    write_table(tables_dir / "phase2_task9_system_by_severity_support.csv", support)
    write_table(tables_dir / "phase2_task9_interaction_mixed_model.csv", interaction_rows)
    write_table(tables_dir / "phase2_task9_model_notes.csv", model_notes)
    write_interaction_svg(
        figures_dir / "phase2_task9_system_by_severity_interaction.svg",
        descriptives,
        x_column="severity",
        line_column="system",
        value_column="mean",
        panel_column="dimension",
        title="Phase 2 Exploratory System by Severity Means",
        x_order=severity_labels,
        line_order=PHASE2_SYSTEM_ORDER,
    )
    return {
        "descriptives": descriptives,
        "support": support,
        "interaction_supported": interaction_supported,
        "interaction_models": interaction_rows,
        "model_notes": model_notes,
        "figure_paths": [str(figures_dir / "phase2_task9_system_by_severity_interaction.svg")],
    }


def analyze_phase2_reliability(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    rows = read_csv_rows(csv_path)
    validate_required_columns(rows, PHASE2_REQUIRED_COLUMNS, csv_path)
    alpha_rows, correlation_rows, composite_rows = reliability_tables(
        rows,
        PHASE2_RATING_CONCEPTS,
        id_columns=["participant_id", "session_id", "trial_number", "passage_id", "explanation_system", "severity", "question_type"],
    )
    composite_summary = []
    if composite_rows:
        composite_rows_with_condition = [
            {
                **row,
                "condition": row["explanation_system"],
            }
            for row in composite_rows
        ]
        composite_summary = condition_descriptives(
            composite_rows_with_condition,
            participant_column="participant_id",
            condition_column="condition",
            rating_map={"overall_composite": "Overall explanation quality"},
        )

    overall_column_check = [
        {
            "existing_overall_column_present": False,
            "checked_column": "",
            "note": "No existing overall-average column was present in Phase 2; any composite is computed from the four mapped rating dimensions.",
        }
    ]
    write_table(tables_dir / "phase2_task10_reliability_alpha.csv", alpha_rows)
    write_table(tables_dir / "phase2_task10_rating_correlations.csv", correlation_rows)
    write_table(tables_dir / "phase2_task10_existing_overall_avg_verification.csv", overall_column_check)
    write_table(tables_dir / "phase2_task10_secondary_composite_scores.csv", composite_rows)
    write_table(tables_dir / "phase2_task10_secondary_composite_descriptives.csv", composite_summary)
    return {
        "alpha": alpha_rows,
        "correlations": correlation_rows,
        "overall_avg_verification": overall_column_check,
        "composite_scores": composite_rows,
        "composite_descriptives": composite_summary,
    }


def phase2_descriptive_row(df, rating_column: str, dimension: str, **labels) -> dict[str, object]:
    from common_utils import descriptive_stats

    values = df[rating_column].dropna().astype(float).tolist()
    stats = descriptive_stats(values)
    row: dict[str, object] = {**labels, "dimension": dimension}
    row.update(
        {
            "n_trials": stats["n_trials"],
            "n_participants": df["participant"].nunique() if len(df) else 0,
            "mean": stats["mean"],
            "sd": stats["sd"],
            "median": stats["median"],
            "iqr": stats["iqr"],
            "ci95_low": stats["ci95_low"],
            "ci95_high": stats["ci95_high"],
        }
    )
    return row


def phase2_question_type_interaction_rows(df, smf, stats) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    notes: list[dict[str, object]] = []
    for rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
        model_df = df[["participant", "system", "question_type_clean", rating_column]].dropna().copy()
        model_df["rating"] = model_df[rating_column].astype(float)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            additive_model = smf.mixedlm(
                'rating ~ C(system, Treatment(reference="mentallama")) + C(question_type_clean, Treatment(reference="shap"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
            interaction_model = smf.mixedlm(
                'rating ~ C(system, Treatment(reference="mentallama")) * C(question_type_clean, Treatment(reference="shap"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
        append_model_warnings(notes, caught, dimension)
        lr_statistic = max(0.0, 2 * (interaction_model.llf - additive_model.llf))
        df_effect = len(PHASE2_QUESTION_TYPE_ORDER) - 1
        rows.append(
            {
                "dimension": dimension,
                "method": "Exploratory mixed-model interaction likelihood-ratio test",
                "model_comparison": "system + question_type vs system * question_type",
                "n_trials": len(model_df),
                "n_participants": model_df["participant"].nunique(),
                "lr_chi2": round(lr_statistic, 4),
                "df": df_effect,
                "p_value": round(float(stats.chi2.sf(lr_statistic, df_effect)), 6),
                "converged": bool(additive_model.converged and interaction_model.converged),
                "interpretation_note": "Secondary/exploratory; do not overinterpret individual question-type subgroups.",
            }
        )
    return rows, unique_note_rows(notes)


def phase2_severity_interaction_rows(df, smf, stats) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    notes: list[dict[str, object]] = []
    for rating_column, dimension in PHASE2_RATING_CONCEPTS.items():
        model_df = df[["participant", "system", "severity_label", rating_column]].dropna().copy()
        model_df["rating"] = model_df[rating_column].astype(float)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            additive_model = smf.mixedlm(
                'rating ~ C(system, Treatment(reference="mentallama")) + C(severity_label, Treatment(reference="no depression"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
            interaction_model = smf.mixedlm(
                'rating ~ C(system, Treatment(reference="mentallama")) * C(severity_label, Treatment(reference="no depression"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
        append_model_warnings(notes, caught, dimension)
        lr_statistic = max(0.0, 2 * (interaction_model.llf - additive_model.llf))
        df_effect = 2
        rows.append(
            {
                "dimension": dimension,
                "method": "Exploratory mixed-model interaction likelihood-ratio test",
                "model_comparison": "system + severity vs system * severity",
                "n_trials": len(model_df),
                "n_participants": model_df["participant"].nunique(),
                "lr_chi2": round(lr_statistic, 4),
                "df": df_effect,
                "p_value": round(float(stats.chi2.sf(lr_statistic, df_effect)), 6),
                "converged": bool(additive_model.converged and interaction_model.converged),
                "interpretation_note": "Secondary/exploratory; do not overstate subgroup findings.",
            }
        )
    return rows, unique_note_rows(notes)


def wilcoxon_rank_biserial(nonzero_differences: list[float]) -> float:
    ranked = sorted((abs(value), value) for value in nonzero_differences)
    ranks: list[tuple[float, float]] = []
    index = 0
    while index < len(ranked):
        tie_end = index
        while tie_end < len(ranked) and ranked[tie_end][0] == ranked[index][0]:
            tie_end += 1
        average_rank = (index + 1 + tie_end) / 2
        for tie_index in range(index, tie_end):
            ranks.append((average_rank, ranked[tie_index][1]))
        index = tie_end

    positive_rank_sum = sum(rank for rank, value in ranks if value > 0)
    negative_rank_sum = sum(rank for rank, value in ranks if value < 0)
    total_rank_sum = positive_rank_sum + negative_rank_sum
    if total_rank_sum == 0:
        return 0.0
    return (positive_rank_sum - negative_rank_sum) / total_rank_sum


def import_stats_stack():
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Pandas requires version.*")
            import pandas as pd
        import statsmodels.formula.api as smf
        from scipy import stats
    except ImportError as exc:
        raise RuntimeError(
            "Task 6 requires pandas, scipy, and statsmodels. Install them with "
            "`python -m pip install pandas scipy statsmodels` or `python -m pip install -r requirements.txt`."
        ) from exc
    return pd, smf, stats


def add_holm_adjustment(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    indexed = list(enumerate(rows))
    indexed.sort(key=lambda item: float(item[1]["raw_p_value"]))
    m = len(indexed)
    previous = 0.0
    adjusted_by_index = {}
    for rank, (original_index, row) in enumerate(indexed, start=1):
        adjusted = min(1.0, (m - rank + 1) * float(row["raw_p_value"]))
        adjusted = max(previous, adjusted)
        previous = adjusted
        adjusted_by_index[original_index] = round(adjusted, 6)
    for index, row in enumerate(rows):
        row["holm_adjusted_p_value"] = adjusted_by_index[index]
    return rows


def append_model_warnings(notes: list[dict[str, object]], caught, dimension: str) -> None:
    for warning_item in caught:
        message = str(warning_item.message)
        if "Pandas requires" in message:
            continue
        note = {"dimension": dimension, "note": message}
        if note not in notes:
            notes.append(note)


def unique_note_rows(notes: list[dict[str, object]]) -> list[dict[str, object]]:
    unique = []
    for note in notes:
        if note not in unique:
            unique.append(note)
    return unique


def phase2_markdown(summary: dict[str, object]) -> list[str]:
    trials = summary["trials_per_participant"]
    assert isinstance(trials, dict)

    lines: list[str] = []
    append_section(
        lines,
        "Phase 2 Data Inspection",
        [
            f"- Rows/trials: {summary['n_rows']}",
            f"- Participants: {summary['n_participants']}",
            f"- Sessions: {summary['n_sessions']}",
            (
                "- Trials per participant: "
                f"min={trials['min_trials']}, median={trials['median_trials']}, "
                f"mean={trials['mean_trials']}, max={trials['max_trials']}"
            ),
            f"- Incomplete participants by observed maximum trial count: {len(summary['incomplete_participants'])}",
            f"- Exact duplicate rows: {summary['exact_duplicate_rows']}",
            f"- Repeated participant/session/trial-number keys: {summary['duplicate_trial_key_rows']}",
            f"- Invalid rating cells: {len(summary['invalid_ratings'])}",
            "- Rating concept mapping: rating_answered=Helpfulness, rating_supported=Correctness, "
            "rating_understandable=Clarity, rating_confidence=Trust.",
            "- Important interpretation: rating_confidence is participant trust in the explanation, "
            "not model prediction confidence.",
        ],
    )

    append_table_section(lines, "System Counts", summary["tables"]["system_counts"])
    append_table_section(lines, "Assigned System Counts", summary["tables"]["assigned_system_counts"])
    append_table_section(lines, "Severity Counts", summary["tables"]["severity_counts"])
    append_table_section(lines, "Question Type Counts", summary["tables"]["question_type_counts"])
    append_table_section(lines, "Participant x System", summary["tables"]["participant_by_system"])
    append_table_section(lines, "System x Question Type", summary["tables"]["system_by_question_type"])
    append_table_section(lines, "System x Severity", summary["tables"]["system_by_severity"])
    append_table_section(lines, "Question Type x Severity", summary["tables"]["question_type_by_severity"])
    append_table_section(lines, "Missing Values", summary["missing_values"])
    append_table_section(lines, "Invalid Ratings", summary["invalid_ratings"])
    append_table_section(lines, "Incomplete Participants", incomplete_rows(summary))
    return lines


def phase2_descriptive_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 2 Descriptive Statistics",
        [
            "These are descriptive summaries only. They compare observed rating patterns but do not test whether differences are statistically significant.",
            "Mean difference is Agentic XAI mean minus MentaLLaMA mean. Positive values mean Agentic XAI has the higher descriptive mean; negative values mean MentaLLaMA has the higher descriptive mean.",
            "rating_confidence is treated as Trust in the explanation, not model prediction confidence.",
        ],
    )
    append_table_section(lines, "Phase 2 Trial-Level Descriptives", summary["trial_level_descriptives"])
    append_table_section(lines, "Agentic XAI Mean Minus MentaLLaMA Mean", summary["mean_differences"])
    append_table_section(lines, "Phase 2 Participant-Level Paired Means", summary["participant_paired_means"])
    append_table_section(lines, "Phase 2 Participant-Level Means Long Format", summary["participant_level_means"])
    append_section(lines, "Phase 2 Figures", [f"- {path}" for path in summary["figure_paths"]])
    return lines


def phase2_primary_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 2 Primary Statistical Analysis",
        [
            "This is the main Phase 2 thesis comparison: Agentic XAI versus MentaLLaMA.",
            "The analysis uses trial-level linear mixed-effects models, one per rating dimension, with participant ID as a random intercept.",
            "The estimated difference is Agentic XAI minus MentaLLaMA on the 1-5 rating scale. Positive values favor Agentic XAI descriptively; negative values favor MentaLLaMA descriptively.",
            "Holm correction is applied across the four primary outcomes.",
        ],
    )
    append_section(lines, "Task 6 Result Summary", phase2_primary_summary_lines(summary))
    append_table_section(lines, "Primary Mixed-Model Results", summary["primary"])
    append_table_section(lines, "Model Notes", summary["model_notes"])
    return lines


def phase2_participant_paired_markdown(
    summary: dict[str, object],
    primary_summary: dict[str, object],
) -> list[str]:
    lines: list[str] = []
    append_section(lines, "Phase 2 Participant-Level Paired Analysis", summary["test_selection"])
    append_section(lines, "Task 7 Result Summary", phase2_participant_paired_summary_lines(summary, primary_summary))
    append_table_section(lines, "Participant-Level Wide Means", summary["participant_means_wide"])
    append_table_section(lines, "Participant-Level Paired Tests", summary["paired_tests"])
    append_table_section(lines, "Paired-Test Notes", summary["test_notes"])
    return lines


def phase2_question_type_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 2 Question-Type Analysis",
        [
            "This is a secondary analysis asking whether the Agentic XAI versus MentaLLaMA difference depends on question type.",
            "Question types are SHAP, Counterfactual, RAG, and Hybrid.",
            "The interaction model compares an additive model with system and question type to a model that also includes system x question type.",
            "Individual question-type cells are small, so subgroup patterns should be treated as exploratory.",
        ],
    )
    append_section(lines, "Task 8 Result Summary", phase2_question_type_summary_lines(summary))
    append_table_section(lines, "System x Question Type Cell Support", summary["support"])
    append_table_section(lines, "System x Question Type Descriptives", summary["descriptives"])
    append_table_section(lines, "Exploratory System x Question Type Interaction Tests", summary["interaction_models"])
    append_table_section(lines, "Task 8 Model Notes", summary["model_notes"])
    append_section(lines, "Task 8 Figure", [f"- {path}" for path in summary["figure_paths"]])
    return lines


def phase2_question_type_summary_lines(summary: dict[str, object]) -> list[str]:
    min_trials = min(int(row["n_trials"]) for row in summary["support"]) if summary["support"] else 0
    min_participants = min(int(row["n_participants"]) for row in summary["support"]) if summary["support"] else 0
    interaction_evidence = [row for row in summary["interaction_models"] if float(row["p_value"]) < 0.05]
    lines = [
        f"The smallest system x question-type subgroup has {min_trials} trials from {min_participants} participants.",
    ]
    if interaction_evidence:
        dimensions = ", ".join(f"{row['dimension']} (p={row['p_value']})" for row in interaction_evidence)
        lines.append(
            f"The exploratory interaction model showed evidence below 0.05 for: {dimensions}. This may suggest system differences vary by question type, but individual subgroup means should still be interpreted cautiously."
        )
        lines.extend(question_type_difference_lines(summary, only_largest=True))
    else:
        lines.append(
            "The exploratory interaction models did not show evidence below 0.05 that the Agentic XAI versus MentaLLaMA difference depended on question type."
        )
        lines.append(
            "Therefore, these results do not provide clear statistical evidence that Agentic XAI's tool selection was particularly useful for one specific question type."
        )
        lines.extend(question_type_difference_lines(summary, only_largest=False))
    if summary["model_notes"]:
        lines.append("Some model fits produced warnings; see the model notes table before using this exploratory analysis in the thesis.")
    return lines


def question_type_difference_lines(summary: dict[str, object], only_largest: bool) -> list[str]:
    grouped: dict[str, list[tuple[str, float]]] = {}
    for row in summary["descriptives"]:
        key = (row["dimension"], row["question_type"])
        grouped.setdefault(key[0], [])
    index = {
        (row["dimension"], row["question_type"], row["system"]): row
        for row in summary["descriptives"]
    }
    lines = []
    for dimension in PHASE2_RATING_CONCEPTS.values():
        differences = []
        for question_type in PHASE2_QUESTION_TYPE_LABELS.values():
            agentic = index.get((dimension, question_type, "agentic_xai"), {}).get("mean", "")
            mentallama = index.get((dimension, question_type, "mentallama"), {}).get("mean", "")
            if agentic == "" or mentallama == "":
                continue
            differences.append((question_type, round(float(agentic) - float(mentallama), 3)))
        if not differences:
            continue
        largest = max(differences, key=lambda item: abs(item[1]))
        if only_largest:
            lines.append(
                f"For {dimension}, the largest descriptive system gap was {largest[1]:+.3f} for {largest[0]} questions."
            )
        else:
            formatted = ", ".join(f"{question_type} {difference:+.3f}" for question_type, difference in differences)
            lines.append(f"Descriptive Agentic XAI minus MentaLLaMA gaps for {dimension}: {formatted}.")
    return lines


def phase2_severity_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 2 Severity Analysis",
        [
            "This is a secondary analysis asking whether the Agentic XAI versus MentaLLaMA difference depends on passage severity.",
            "Severity is reported as no depression, moderate, and severe. The raw Phase 2 label none is reported as no depression here for consistency with the thesis wording.",
            "The interaction model compares an additive model with system and severity to a model that also includes system x severity.",
            "Individual severity subgroups are small, so subgroup patterns should not be overstated.",
        ],
    )
    append_section(lines, "Task 9 Result Summary", phase2_severity_summary_lines(summary))
    append_table_section(lines, "System x Severity Cell Support", summary["support"])
    append_table_section(lines, "System x Severity Descriptives", summary["descriptives"])
    append_table_section(lines, "Exploratory System x Severity Interaction Tests", summary["interaction_models"])
    append_table_section(lines, "Task 9 Model Notes", summary["model_notes"])
    append_section(lines, "Task 9 Figure", [f"- {path}" for path in summary["figure_paths"]])
    return lines


def phase2_reliability_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 2 Reliability / Overall Score",
        [
            "Cronbach's alpha measures whether the four mapped rating dimensions tend to move together as a set.",
            "The Phase 2 dimensions are Helpfulness, Correctness, Clarity, and Trust, where rating_confidence means participant trust in the explanation.",
            "This does not automatically replace the four individual outcomes. The primary Phase 2 results should still report each dimension separately.",
            "An overall composite is created only as a secondary summary when alpha is at least 0.70.",
        ],
    )
    append_section(lines, "Phase 2 Reliability Summary", phase2_reliability_summary_lines(summary))
    append_table_section(lines, "Phase 2 Cronbach's Alpha", summary["alpha"])
    append_table_section(lines, "Phase 2 Rating-Dimension Correlations", summary["correlations"])
    append_table_section(lines, "Phase 2 Existing Overall Average Verification", summary["overall_avg_verification"])
    append_table_section(lines, "Phase 2 Secondary Composite Descriptives", summary["composite_descriptives"])
    return lines


def phase2_reliability_summary_lines(summary: dict[str, object]) -> list[str]:
    alpha_row = summary["alpha"][0]
    alpha = alpha_row["cronbach_alpha"]
    lines = [
        f"Cronbach's alpha was {alpha} ({alpha_row['interpretation']}).",
    ]
    if alpha_row["composite_created"]:
        lines.append(
            "Reliability is acceptable for a secondary overall explanation-quality composite, but this composite should not replace Helpfulness, Correctness, Clarity, and Trust."
        )
    else:
        lines.append(
            "Reliability is below the pre-set 0.70 threshold, so no secondary overall composite should be emphasized."
        )
    lines.append(summary["overall_avg_verification"][0]["note"])
    return lines


def phase2_severity_summary_lines(summary: dict[str, object]) -> list[str]:
    min_trials = min(int(row["n_trials"]) for row in summary["support"]) if summary["support"] else 0
    min_participants = min(int(row["n_participants"]) for row in summary["support"]) if summary["support"] else 0
    interaction_evidence = [row for row in summary["interaction_models"] if float(row["p_value"]) < 0.05]
    lines = [
        f"The smallest system x severity subgroup has {min_trials} trials from {min_participants} participants.",
    ]
    if summary["interaction_supported"]:
        lines.append("Because every subgroup has at least 10 trials, the exploratory system x severity model was run.")
    else:
        lines.append("The exploratory system x severity model was not run because at least one subgroup had fewer than 10 trials.")

    if interaction_evidence:
        dimensions = ", ".join(f"{row['dimension']} (p={row['p_value']})" for row in interaction_evidence)
        lines.append(
            f"The exploratory interaction model showed evidence below 0.05 for: {dimensions}. Interpret this cautiously because severity subgroups are small."
        )
    elif summary["interaction_models"]:
        lines.append(
            "The exploratory interaction models did not show evidence below 0.05 that the Agentic XAI versus MentaLLaMA difference depended on severity."
        )

    lines.extend(severity_difference_lines(summary))
    if not interaction_evidence:
        lines.append(
            "Overall, this does not provide clear statistical evidence that Agentic XAI was particularly different from MentaLLaMA at one severity level."
        )
    if summary["model_notes"]:
        lines.append("Some model fits produced warnings; see the model notes table before using this exploratory analysis in the thesis.")
    return lines


def severity_difference_lines(summary: dict[str, object]) -> list[str]:
    index = {
        (row["dimension"], row["severity"], row["system"]): row
        for row in summary["descriptives"]
    }
    severity_labels = [PHASE2_SEVERITY_LABELS[item] for item in PHASE2_SEVERITY_ORDER]
    lines = []
    for dimension in PHASE2_RATING_CONCEPTS.values():
        differences = []
        for severity in severity_labels:
            agentic = index.get((dimension, severity, "agentic_xai"), {}).get("mean", "")
            mentallama = index.get((dimension, severity, "mentallama"), {}).get("mean", "")
            if agentic == "" or mentallama == "":
                continue
            differences.append((severity, round(float(agentic) - float(mentallama), 3)))
        if differences:
            formatted = ", ".join(f"{severity} {difference:+.3f}" for severity, difference in differences)
            lines.append(f"Descriptive Agentic XAI minus MentaLLaMA gaps for {dimension}: {formatted}.")
    return lines


def phase2_participant_paired_summary_lines(
    summary: dict[str, object],
    primary_summary: dict[str, object],
) -> list[str]:
    primary_any = any(float(row["holm_adjusted_p_value"]) < 0.05 for row in primary_summary["primary"])
    paired_any = any(float(row["holm_adjusted_p_value"]) < 0.05 for row in summary["paired_tests"])
    lines = []

    if paired_any:
        dimensions = ", ".join(
            f"{row['dimension']} (Holm p={row['holm_adjusted_p_value']})"
            for row in summary["paired_tests"]
            if float(row["holm_adjusted_p_value"]) < 0.05
        )
        lines.append(f"The participant-level robustness check showed evidence below 0.05 after Holm correction for: {dimensions}.")
    else:
        lines.append(
            "The participant-level robustness check did not show evidence below 0.05 after Holm correction for any rating dimension."
        )

    for row in summary["paired_tests"]:
        diff = float(row["mean_paired_difference"])
        if float(row["holm_adjusted_p_value"]) < 0.05:
            direction = "higher" if diff > 0 else "lower"
            lines.append(
                f"For {row['dimension']}, Agentic XAI was {direction} than MentaLLaMA in the participant-level paired check."
            )
        elif diff > 0:
            lines.append(
                f"For {row['dimension']}, Agentic XAI received a higher participant-level descriptive rating, but there was insufficient statistical evidence of a difference."
            )
        elif diff < 0:
            lines.append(
                f"For {row['dimension']}, Agentic XAI received a lower participant-level descriptive rating, but there was insufficient statistical evidence of a difference."
            )
        else:
            lines.append(f"For {row['dimension']}, the participant-level paired mean difference was zero.")

    if primary_any == paired_any:
        lines.append("The finding is consistent across both approaches: neither the primary trial-level mixed model nor the participant-level robustness check showed Holm-adjusted evidence of a system difference.")
    else:
        lines.append(
            "The primary and participant-level analyses differ. This can happen because the primary model uses every trial while accounting for participant ID, whereas the participant-level check compresses each participant-system combination into one mean before testing."
        )
    return lines


def phase2_primary_summary_lines(summary: dict[str, object]) -> list[str]:
    lines = []
    adjusted_evidence = [row for row in summary["primary"] if float(row["holm_adjusted_p_value"]) < 0.05]
    if adjusted_evidence:
        dimensions = ", ".join(
            f"{row['dimension']} (Holm p={row['holm_adjusted_p_value']})" for row in adjusted_evidence
        )
        lines.append(f"After Holm correction, there was statistical evidence of a Phase 2 system difference for: {dimensions}.")
    else:
        lines.append(
            "After Holm correction across the four primary outcomes, there was insufficient statistical evidence that participants rated Agentic XAI differently from MentaLLaMA."
        )

    for row in summary["primary"]:
        diff = float(row["estimated_difference_agentic_minus_mentallama"])
        dimension = row["dimension"]
        adjusted_p = float(row["holm_adjusted_p_value"])
        if adjusted_p < 0.05:
            direction = "higher" if diff > 0 else "lower"
            lines.append(
                f"For {dimension}, Agentic XAI was estimated {direction} than MentaLLaMA by {abs(diff):.3f} rating points."
            )
        elif diff > 0:
            lines.append(
                f"For {dimension}, Agentic XAI received a higher descriptive rating, but there was insufficient statistical evidence of a difference."
            )
        elif diff < 0:
            lines.append(
                f"For {dimension}, Agentic XAI received a lower descriptive rating, but there was insufficient statistical evidence of a difference."
            )
        else:
            lines.append(f"For {dimension}, the estimated ratings were essentially identical.")

    if summary["model_notes"]:
        lines.append(
            "The mixed models converged, but random-effects covariance warnings occurred; mention this as a small-sample/boundary-model caution."
        )
    return lines


def validate_required_columns(rows: list[dict[str, str]], required_columns: list[str], csv_path: Path) -> None:
    if not rows:
        raise ValueError(f"{csv_path} has no data rows.")
    missing = [column for column in required_columns if column not in rows[0]]
    if missing:
        raise ValueError(f"{csv_path} is missing required columns: {', '.join(missing)}")


def append_table_section(lines: list[str], title: str, rows: list[dict[str, object]]) -> None:
    append_section(lines, title, ["```", format_count_table(rows), "```"])


def incomplete_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    trial_rows = summary["trials_per_participant"]["participant_trial_rows"]
    return [row for row in trial_rows if not row["complete_by_observed_max"]]
