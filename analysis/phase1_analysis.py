"""Phase 1 inspection and later analysis steps."""

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
    write_table,
    write_ci_svg,
    write_distribution_svg,
    write_interaction_svg,
)


PHASE1_RATING_COLUMNS = [
    "rating_clarity",
    "rating_correctness",
    "rating_helpfulness",
    "rating_trust",
]

PHASE1_REQUIRED_COLUMNS = [
    "user_id",
    "session_id",
    "paragraph_id",
    "prediction_label",
    "selected_use_case_name",
    *PHASE1_RATING_COLUMNS,
]

PHASE1_RATING_MAP = {
    "rating_clarity": "Clarity",
    "rating_correctness": "Correctness",
    "rating_helpfulness": "Helpfulness",
    "rating_trust": "Trust",
}

PHASE1_CONDITION_ORDER = ["SHAP", "COUNTERFACTUAL", "RAG", "HYBRID"]
PHASE1_PAIRWISE_COMPARISONS = [
    ("SHAP", "COUNTERFACTUAL"),
    ("SHAP", "RAG"),
    ("SHAP", "HYBRID"),
    ("COUNTERFACTUAL", "RAG"),
    ("COUNTERFACTUAL", "HYBRID"),
    ("RAG", "HYBRID"),
]
PHASE1_SEVERITY_ORDER = ["no depression", "moderate", "severe"]
RAW_TO_REPORT_SEVERITY = {
    "not depression": "no depression",
    "no depression": "no depression",
    "moderate": "moderate",
    "severe": "severe",
}


def inspect_phase1(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    rows = read_csv_rows(csv_path)
    validate_required_columns(rows, PHASE1_REQUIRED_COLUMNS, csv_path)

    participant_summary = participant_trial_summary(rows, "user_id")
    missing = missing_value_summary(rows)
    invalid_ratings = validate_ratings(rows, PHASE1_RATING_COLUMNS)
    exact_duplicates = exact_duplicate_count(rows)
    duplicate_trials = duplicate_key_summary(
        rows,
        ["user_id", "session_id", "paragraph_id", "selected_use_case_name"],
    )

    outputs = {
        "participant_trials": participant_summary["participant_trial_rows"],
        "missing_values": missing,
        "invalid_ratings": invalid_ratings,
        "explanation_counts": count_by(rows, ["selected_use_case_name"]),
        "severity_counts": count_by(rows, ["prediction_label"]),
        "explanation_by_severity": crosstab(rows, "selected_use_case_name", "prediction_label"),
        "participant_by_explanation": participant_condition_counts(rows, "user_id", "selected_use_case_name"),
        "duplicate_trial_keys": duplicate_trials,
    }

    prefix = tables_dir / "phase1_task1"
    for name, table_rows in outputs.items():
        write_table(prefix.with_name(f"{prefix.name}_{name}.csv"), table_rows)

    return {
        "name": "Phase 1",
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


def describe_phase1(csv_path: Path, tables_dir: Path, figures_dir: Path) -> dict[str, object]:
    rows = read_csv_rows(csv_path)
    validate_required_columns(rows, PHASE1_REQUIRED_COLUMNS, csv_path)

    descriptives = condition_descriptives(
        rows,
        participant_column="user_id",
        condition_column="selected_use_case_name",
        rating_map=PHASE1_RATING_MAP,
    )
    participant_means = participant_condition_means(
        rows,
        participant_column="user_id",
        condition_column="selected_use_case_name",
        rating_map=PHASE1_RATING_MAP,
    )

    write_table(tables_dir / "phase1_task2_trial_level_descriptives.csv", descriptives)
    write_table(tables_dir / "phase1_task2_participant_level_means.csv", participant_means)
    write_distribution_svg(
        figures_dir / "phase1_task2_rating_distributions.svg",
        rows,
        condition_column="selected_use_case_name",
        rating_map=PHASE1_RATING_MAP,
        title="Phase 1 Rating Distributions by Explanation Type",
    )
    write_ci_svg(
        figures_dir / "phase1_task2_descriptive_ci.svg",
        descriptives,
        title="Phase 1 Descriptive Means with 95% CIs",
    )

    return {
        "trial_level_descriptives": descriptives,
        "participant_level_means": participant_means,
        "figure_paths": [
            str(figures_dir / "phase1_task2_rating_distributions.svg"),
            str(figures_dir / "phase1_task2_descriptive_ci.svg"),
        ],
    }


def analyze_phase1_statistics(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    pd, smf, stats = import_stats_stack()
    df = pd.read_csv(csv_path)
    validate_required_columns(df.to_dict("records"), PHASE1_REQUIRED_COLUMNS, csv_path)

    df["participant"] = df["user_id"].astype(str)
    df["explanation_type"] = pd.Categorical(
        df["selected_use_case_name"],
        categories=PHASE1_CONDITION_ORDER,
        ordered=False,
    )

    overall_rows: list[dict[str, object]] = []
    pairwise_rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []
    model_note_rows: list[dict[str, object]] = []

    for rating_column, dimension in PHASE1_RATING_MAP.items():
        model_df = df[["participant", "explanation_type", rating_column]].dropna().copy()
        model_df["rating"] = pd.to_numeric(model_df[rating_column], errors="coerce")
        model_df = model_df.dropna(subset=["rating", "explanation_type"])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            full_model = smf.mixedlm(
                'rating ~ C(explanation_type, Treatment(reference="SHAP"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=200, disp=False)
            null_model = smf.mixedlm(
                "rating ~ 1",
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=200, disp=False)

        for warning_item in caught:
            message = str(warning_item.message)
            if "Pandas requires" not in message:
                note = {"dimension": dimension, "note": message}
                if note not in model_note_rows:
                    model_note_rows.append(note)

        lr_statistic = max(0.0, 2 * (full_model.llf - null_model.llf))
        df_effect = len(PHASE1_CONDITION_ORDER) - 1
        p_value = stats.chi2.sf(lr_statistic, df_effect)
        residual_sd = math.sqrt(float(full_model.scale))
        random_intercept_variance = float(full_model.cov_re.iloc[0, 0]) if full_model.cov_re.size else 0.0

        overall_rows.append(
            {
                "dimension": dimension,
                "method": "Linear mixed-effects model, likelihood-ratio test",
                "model": "rating ~ explanation_type + (1 | participant)",
                "n_trials": len(model_df),
                "n_participants": model_df["participant"].nunique(),
                "lr_chi2": round(lr_statistic, 4),
                "df": df_effect,
                "p_value": round(p_value, 6),
                "residual_sd": round(residual_sd, 4),
                "participant_intercept_variance": round(random_intercept_variance, 4),
                "converged": bool(full_model.converged and null_model.converged),
                "pairwise_rule": "Pairwise comparisons run only if overall p < 0.05",
            }
        )

        if p_value < 0.05:
            dimension_pairwise = phase1_pairwise_rows(full_model, stats, dimension, residual_sd)
            dimension_pairwise = add_holm_adjustment(dimension_pairwise)
            pairwise_rows.extend(dimension_pairwise)
        else:
            skipped_rows.append(
                {
                    "dimension": dimension,
                    "overall_p_value": round(p_value, 6),
                    "reason": "Overall explanation-type p-value was not below 0.05, so post-hoc pairwise comparisons were not run.",
                }
            )

    secondary_rows, secondary_note_rows = phase1_participant_level_secondary(df, stats)

    write_table(tables_dir / "phase1_task4_mixed_model_overall.csv", overall_rows)
    write_table(tables_dir / "phase1_task4_mixed_model_pairwise_holm.csv", pairwise_rows)
    write_table(tables_dir / "phase1_task4_pairwise_not_run.csv", skipped_rows)
    write_table(tables_dir / "phase1_task4_participant_level_friedman.csv", secondary_rows)
    write_table(tables_dir / "phase1_task4_participant_level_notes.csv", secondary_note_rows)
    write_table(tables_dir / "phase1_task4_model_notes.csv", model_note_rows)

    return {
        "overall": overall_rows,
        "pairwise": pairwise_rows,
        "pairwise_not_run": skipped_rows,
        "participant_level": secondary_rows,
        "participant_level_notes": secondary_note_rows,
        "model_notes": model_note_rows,
    }


def analyze_phase1_severity(csv_path: Path, tables_dir: Path, figures_dir: Path) -> dict[str, object]:
    pd, smf, stats = import_stats_stack()
    df = pd.read_csv(csv_path)
    validate_required_columns(df.to_dict("records"), PHASE1_REQUIRED_COLUMNS, csv_path)
    df["participant"] = df["user_id"].astype(str)
    df["explanation_type"] = pd.Categorical(
        df["selected_use_case_name"],
        categories=PHASE1_CONDITION_ORDER,
        ordered=False,
    )
    df["severity"] = df["prediction_label"].astype(str).str.strip().map(RAW_TO_REPORT_SEVERITY)
    df["severity"] = pd.Categorical(df["severity"], categories=PHASE1_SEVERITY_ORDER, ordered=True)

    severity_descriptives = []
    interaction_descriptives = []
    for rating_column, dimension in PHASE1_RATING_MAP.items():
        for severity in PHASE1_SEVERITY_ORDER:
            subset = df[df["severity"] == severity]
            severity_descriptives.append(descriptive_row(subset, rating_column, dimension, severity=severity))
        for explanation in PHASE1_CONDITION_ORDER:
            for severity in PHASE1_SEVERITY_ORDER:
                subset = df[(df["explanation_type"] == explanation) & (df["severity"] == severity)]
                interaction_descriptives.append(
                    descriptive_row(
                        subset,
                        rating_column,
                        dimension,
                        explanation_type=explanation,
                        severity=severity,
                    )
                )

    support = cell_support_rows(df)
    supported = all(int(row["n_trials"]) >= 10 for row in support)

    severity_model_rows, severity_model_notes = phase1_severity_model_rows(df, smf, stats)
    if supported:
        interaction_model_rows, interaction_model_notes = phase1_interaction_model_rows(df, smf, stats)
    else:
        interaction_model_rows = []
        interaction_model_notes = [
            {
                "dimension": "All",
                "note": "Explanation type x severity model was not run because at least one cell had fewer than 10 trials.",
            }
        ]
    model_notes = unique_note_rows(severity_model_notes + interaction_model_notes)

    write_table(tables_dir / "phase1_task5_severity_descriptives.csv", severity_descriptives)
    write_table(tables_dir / "phase1_task5_explanation_by_severity_descriptives.csv", interaction_descriptives)
    write_table(tables_dir / "phase1_task5_explanation_by_severity_support.csv", support)
    write_table(tables_dir / "phase1_task5_severity_mixed_model.csv", severity_model_rows)
    write_table(tables_dir / "phase1_task5_interaction_mixed_model.csv", interaction_model_rows)
    write_table(tables_dir / "phase1_task5_model_notes.csv", model_notes)
    write_interaction_svg(
        figures_dir / "phase1_task5_explanation_by_severity_interaction.svg",
        interaction_descriptives,
        x_column="severity",
        line_column="explanation_type",
        value_column="mean",
        panel_column="dimension",
        title="Phase 1 Exploratory Explanation Type by Severity Means",
        x_order=PHASE1_SEVERITY_ORDER,
        line_order=PHASE1_CONDITION_ORDER,
    )

    return {
        "severity_descriptives": severity_descriptives,
        "interaction_descriptives": interaction_descriptives,
        "support": support,
        "interaction_supported": supported,
        "severity_models": severity_model_rows,
        "interaction_models": interaction_model_rows,
        "model_notes": model_notes,
        "figure_paths": [str(figures_dir / "phase1_task5_explanation_by_severity_interaction.svg")],
    }


def analyze_phase1_reliability(csv_path: Path, tables_dir: Path) -> dict[str, object]:
    rows = read_csv_rows(csv_path)
    validate_required_columns(rows, [*PHASE1_REQUIRED_COLUMNS, "rating_overall_avg"], csv_path)
    alpha_rows, correlation_rows, composite_rows = reliability_tables(
        rows,
        PHASE1_RATING_MAP,
        id_columns=["user_id", "session_id", "paragraph_id", "selected_use_case_name", "prediction_label"],
    )
    verification_rows = verify_phase1_overall_average(rows)
    composite_summary = []
    if composite_rows:
        composite_rows_with_condition = [
            {
                **row,
                "condition": row["selected_use_case_name"],
            }
            for row in composite_rows
        ]
        composite_summary = condition_descriptives(
            composite_rows_with_condition,
            participant_column="user_id",
            condition_column="condition",
            rating_map={"overall_composite": "Overall explanation quality"},
        )

    write_table(tables_dir / "phase1_task10_reliability_alpha.csv", alpha_rows)
    write_table(tables_dir / "phase1_task10_rating_correlations.csv", correlation_rows)
    write_table(tables_dir / "phase1_task10_existing_overall_avg_verification.csv", verification_rows)
    write_table(tables_dir / "phase1_task10_secondary_composite_scores.csv", composite_rows)
    write_table(tables_dir / "phase1_task10_secondary_composite_descriptives.csv", composite_summary)
    return {
        "alpha": alpha_rows,
        "correlations": correlation_rows,
        "overall_avg_verification": verification_rows,
        "composite_scores": composite_rows,
        "composite_descriptives": composite_summary,
    }


def verify_phase1_overall_average(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    mismatches = []
    checked = 0
    max_abs_difference = 0.0
    for row_number, row in enumerate(rows, start=2):
        values = [float(row[column]) for column in PHASE1_RATING_COLUMNS]
        computed = sum(values) / len(values)
        try:
            existing = float(row["rating_overall_avg"])
        except ValueError:
            mismatches.append(
                {
                    "csv_row": row_number,
                    "existing_rating_overall_avg": row["rating_overall_avg"],
                    "computed_average": round(computed, 4),
                    "absolute_difference": "",
                    "note": "Existing value is not numeric.",
                }
            )
            continue
        checked += 1
        difference = abs(existing - computed)
        max_abs_difference = max(max_abs_difference, difference)
        if difference > 0.0001:
            mismatches.append(
                {
                    "csv_row": row_number,
                    "existing_rating_overall_avg": existing,
                    "computed_average": round(computed, 4),
                    "absolute_difference": round(difference, 6),
                    "note": "Existing overall average differs from computed four-rating average.",
                }
            )
    return [
        {
            "checked_rows": checked,
            "mismatch_count": len(mismatches),
            "max_absolute_difference": round(max_abs_difference, 6),
            "verification_result": "matches computed average" if not mismatches else "mismatches found",
        },
        *mismatches,
    ]


def descriptive_row(df, rating_column: str, dimension: str, **labels) -> dict[str, object]:
    from common_utils import descriptive_stats

    values = df[rating_column].dropna().astype(float).tolist()
    stats = descriptive_stats(values)
    participants = df["participant"].astype(str).nunique() if len(df) else 0
    row: dict[str, object] = {**labels, "dimension": dimension}
    row.update(
        {
            "n_trials": stats["n_trials"],
            "n_participants": participants,
            "mean": stats["mean"],
            "sd": stats["sd"],
            "median": stats["median"],
            "iqr": stats["iqr"],
            "ci95_low": stats["ci95_low"],
            "ci95_high": stats["ci95_high"],
        }
    )
    return row


def cell_support_rows(df) -> list[dict[str, object]]:
    rows = []
    for explanation in PHASE1_CONDITION_ORDER:
        for severity in PHASE1_SEVERITY_ORDER:
            subset = df[(df["explanation_type"] == explanation) & (df["severity"] == severity)]
            rows.append(
                {
                    "explanation_type": explanation,
                    "severity": severity,
                    "n_trials": len(subset),
                    "n_participants": subset["participant"].astype(str).nunique() if len(subset) else 0,
                }
            )
    return rows


def phase1_severity_model_rows(df, smf, stats) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    notes = []
    for rating_column, dimension in PHASE1_RATING_MAP.items():
        model_df = df[["participant", "severity", rating_column]].dropna().copy()
        model_df["rating"] = model_df[rating_column].astype(float)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            full_model = smf.mixedlm(
                'rating ~ C(severity, Treatment(reference="no depression"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=200, disp=False)
            null_model = smf.mixedlm("rating ~ 1", model_df, groups=model_df["participant"]).fit(
                reml=False,
                method="lbfgs",
                maxiter=200,
                disp=False,
            )
        append_model_warnings(notes, caught, dimension)
        lr_statistic = max(0.0, 2 * (full_model.llf - null_model.llf))
        df_effect = len(PHASE1_SEVERITY_ORDER) - 1
        rows.append(
            {
                "dimension": dimension,
                "method": "Exploratory linear mixed-effects model, likelihood-ratio test",
                "model": "rating ~ severity + (1 | participant)",
                "n_trials": len(model_df),
                "n_participants": model_df["participant"].nunique(),
                "lr_chi2": round(lr_statistic, 4),
                "df": df_effect,
                "p_value": round(float(stats.chi2.sf(lr_statistic, df_effect)), 6),
                "converged": bool(full_model.converged and null_model.converged),
                "interpretation_note": "Secondary severity check; not the main Phase 1 research question.",
            }
        )
    return rows, notes


def phase1_interaction_model_rows(df, smf, stats) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    notes = []
    for rating_column, dimension in PHASE1_RATING_MAP.items():
        model_df = df[["participant", "explanation_type", "severity", rating_column]].dropna().copy()
        model_df["rating"] = model_df[rating_column].astype(float)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            additive_model = smf.mixedlm(
                'rating ~ C(explanation_type, Treatment(reference="SHAP")) + C(severity, Treatment(reference="no depression"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
            interaction_model = smf.mixedlm(
                'rating ~ C(explanation_type, Treatment(reference="SHAP")) * C(severity, Treatment(reference="no depression"))',
                model_df,
                groups=model_df["participant"],
            ).fit(reml=False, method="lbfgs", maxiter=300, disp=False)
        append_model_warnings(notes, caught, dimension)
        lr_statistic = max(0.0, 2 * (interaction_model.llf - additive_model.llf))
        df_effect = 6
        rows.append(
            {
                "dimension": dimension,
                "method": "Exploratory mixed-model interaction likelihood-ratio test",
                "model_comparison": "explanation_type + severity vs explanation_type * severity",
                "n_trials": len(model_df),
                "n_participants": model_df["participant"].nunique(),
                "lr_chi2": round(lr_statistic, 4),
                "df": df_effect,
                "p_value": round(float(stats.chi2.sf(lr_statistic, df_effect)), 6),
                "converged": bool(additive_model.converged and interaction_model.converged),
                "interpretation_note": "Exploratory only; do not make strong claims from small subgroups.",
            }
        )
    return rows, notes


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


def import_stats_stack():
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Pandas requires version.*")
            import pandas as pd
        import statsmodels.formula.api as smf
        from scipy import stats
    except ImportError as exc:
        raise RuntimeError(
            "Task 4 requires pandas, scipy, and statsmodels. Install them with "
            "`python -m pip install pandas scipy statsmodels` or `python -m pip install -r requirements.txt`."
        ) from exc
    return pd, smf, stats


def phase1_pairwise_rows(model, stats, dimension: str, residual_sd: float) -> list[dict[str, object]]:
    fe_params = model.fe_params
    fe_names = list(fe_params.index)
    cov_fe = model.cov_params().loc[fe_names, fe_names]
    vectors = {
        condition: fixed_effect_vector(condition, fe_names)
        for condition in PHASE1_CONDITION_ORDER
    }

    rows = []
    for first, second in PHASE1_PAIRWISE_COMPARISONS:
        contrast = vectors[first] - vectors[second]
        estimate = float(contrast @ fe_params)
        se = math.sqrt(max(0.0, float(contrast @ cov_fe @ contrast)))
        z_value = estimate / se if se > 0 else float("nan")
        p_value = 2 * stats.norm.sf(abs(z_value)) if se > 0 else float("nan")
        ci_low = estimate - 1.96 * se
        ci_high = estimate + 1.96 * se
        rows.append(
            {
                "dimension": dimension,
                "comparison": f"{first} - {second}",
                "mean_difference": round(estimate, 4),
                "ci95_low": round(ci_low, 4),
                "ci95_high": round(ci_high, 4),
                "raw_p_value": round(p_value, 6),
                "holm_adjusted_p_value": "",
                "effect_size_metric": "standardized difference using model residual SD",
                "effect_size": round(estimate / residual_sd, 4) if residual_sd > 0 else "",
            }
        )
    return rows


def fixed_effect_vector(condition: str, fe_names: list[str]):
    import numpy as np

    vector = np.zeros(len(fe_names))
    vector[fe_names.index("Intercept")] = 1.0
    if condition != "SHAP":
        term = f'C(explanation_type, Treatment(reference="SHAP"))[T.{condition}]'
        vector[fe_names.index(term)] = 1.0
    return vector


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


def phase1_participant_level_secondary(df, stats) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    notes: list[dict[str, object]] = []
    for rating_column, dimension in PHASE1_RATING_MAP.items():
        participant_means = (
            df.groupby(["participant", "selected_use_case_name"], observed=False)[rating_column]
            .mean()
            .unstack()
        )
        complete = participant_means.dropna(subset=PHASE1_CONDITION_ORDER)
        excluded = sorted(set(participant_means.index.astype(str)) - set(complete.index.astype(str)))
        notes.append(
            {
                "dimension": dimension,
                "complete_participants_used": len(complete),
                "participants_excluded_due_to_missing_condition": len(excluded),
                "excluded_participant_ids": ";".join(excluded),
                "note": "No missing condition means were filled or imputed.",
            }
        )

        if len(complete) < 2:
            rows.append(
                {
                    "dimension": dimension,
                    "method": "Friedman repeated-measures test on participant-level means",
                    "n_participants": len(complete),
                    "df": len(PHASE1_CONDITION_ORDER) - 1,
                    "chi2": "",
                    "p_value": "",
                    "effect_size_metric": "Kendall's W",
                    "effect_size": "",
                    "interpretation_note": "Too few complete participants for a valid participant-level repeated comparison.",
                }
            )
            continue

        friedman = stats.friedmanchisquare(*(complete[condition] for condition in PHASE1_CONDITION_ORDER))
        chi2 = float(friedman.statistic)
        kendalls_w = chi2 / (len(complete) * (len(PHASE1_CONDITION_ORDER) - 1))
        rows.append(
            {
                "dimension": dimension,
                "method": "Friedman repeated-measures test on participant-level means",
                "n_participants": len(complete),
                "df": len(PHASE1_CONDITION_ORDER) - 1,
                "chi2": round(chi2, 4),
                "p_value": round(float(friedman.pvalue), 6),
                "effect_size_metric": "Kendall's W",
                "effect_size": round(kendalls_w, 4),
                "interpretation_note": "Secondary complete-case robustness check; primary inference remains the trial-level mixed model.",
            }
        )
    return rows, notes


def phase1_markdown(summary: dict[str, object]) -> list[str]:
    trials = summary["trials_per_participant"]
    assert isinstance(trials, dict)

    lines: list[str] = []
    append_section(
        lines,
        "Phase 1 Data Inspection",
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
            f"- Repeated participant/session/passage/explanation keys: {summary['duplicate_trial_key_rows']}",
            f"- Invalid rating cells: {len(summary['invalid_ratings'])}",
        ],
    )

    append_table_section(lines, "Explanation Counts", summary["tables"]["explanation_counts"])
    append_table_section(lines, "Severity Counts", summary["tables"]["severity_counts"])
    append_table_section(lines, "Explanation Type x Severity", summary["tables"]["explanation_by_severity"])
    append_table_section(lines, "Participant x Explanation Type", summary["tables"]["participant_by_explanation"])
    append_table_section(lines, "Missing Values", summary["missing_values"])
    append_table_section(lines, "Invalid Ratings", summary["invalid_ratings"])
    append_table_section(lines, "Incomplete Participants", incomplete_rows(summary))
    return lines


def phase1_descriptive_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 1 Descriptive Statistics",
        [
            "These are descriptive summaries only. They compare observed rating patterns but do not test whether differences are statistically significant.",
            "Use wording such as higher descriptive mean, lower descriptive mean, or similar ratings.",
        ],
    )
    append_table_section(lines, "Phase 1 Trial-Level Descriptives", summary["trial_level_descriptives"])
    append_table_section(lines, "Phase 1 Participant-Level Means", summary["participant_level_means"])
    append_section(lines, "Phase 1 Figures", [f"- {path}" for path in summary["figure_paths"]])
    return lines


def phase1_statistics_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 1 Statistical Analysis",
        [
            "Primary analysis uses trial-level linear mixed-effects models with a random intercept for participant ID.",
            "Each rating dimension is tested separately. The overall explanation-type effect is tested first.",
            "Pairwise comparisons use Holm correction and are run only for dimensions where the overall explanation-type p-value is below 0.05.",
            "Mean differences are model-estimated differences on the 1-5 rating scale. Positive values mean the first explanation type has the higher estimated rating.",
        ],
    )
    append_section(lines, "Phase 1 Result Summary", phase1_result_summary_lines(summary))
    append_table_section(lines, "Primary Overall Mixed-Model Tests", summary["overall"])
    append_table_section(lines, "Primary Pairwise Comparisons With Holm Correction", summary["pairwise"])
    append_table_section(lines, "Pairwise Comparisons Not Run", summary["pairwise_not_run"])
    append_section(
        lines,
        "Secondary Participant-Level Analysis",
        [
            "This check averages ratings within each participant and explanation type first.",
            "Participants are not forced into conditions they never rated. Complete-case repeated comparisons use only participants with means for all four explanation types.",
        ],
    )
    append_table_section(lines, "Participant-Level Friedman Tests", summary["participant_level"])
    append_table_section(lines, "Participant-Level Completeness Notes", summary["participant_level_notes"])
    append_table_section(lines, "Model Notes", summary["model_notes"])
    return lines


def phase1_severity_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 1 Severity Analysis",
        [
            "This is a secondary/exploratory analysis. The main Phase 1 research question remains explanation type.",
            "Severity categories are reported as no depression, moderate, and severe. The raw Phase 1 label not depression is reported as no depression here for consistency with the thesis wording.",
            "The main severity effect is inspected descriptively and with a simple participant-aware exploratory mixed model.",
            "The explanation type x severity interaction is explored only because all cells have at least 10 trials. These subgroup results should be described cautiously.",
        ],
    )
    append_section(lines, "Task 5 Result Summary", phase1_severity_summary_lines(summary))
    append_table_section(lines, "Severity Descriptives", summary["severity_descriptives"])
    append_table_section(lines, "Explanation Type x Severity Descriptives", summary["interaction_descriptives"])
    append_table_section(lines, "Explanation Type x Severity Cell Support", summary["support"])
    append_table_section(lines, "Exploratory Severity Mixed-Model Tests", summary["severity_models"])
    append_table_section(lines, "Exploratory Interaction Mixed-Model Tests", summary["interaction_models"])
    append_table_section(lines, "Task 5 Model Notes", summary["model_notes"])
    append_section(lines, "Task 5 Figure", [f"- {path}" for path in summary["figure_paths"]])
    return lines


def phase1_reliability_markdown(summary: dict[str, object]) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "Phase 1 Reliability / Overall Score",
        [
            "Cronbach's alpha measures whether the four rating dimensions tend to move together as a set. Higher values mean the items are more internally consistent.",
            "This does not automatically replace Clarity, Correctness, Helpfulness, and Trust. The primary results should still report the four dimensions separately.",
            "An overall composite is created only as a secondary summary when alpha is at least 0.70.",
        ],
    )
    append_section(lines, "Phase 1 Reliability Summary", reliability_summary_lines(summary, has_existing_average=True))
    append_table_section(lines, "Phase 1 Cronbach's Alpha", summary["alpha"])
    append_table_section(lines, "Phase 1 Rating-Dimension Correlations", summary["correlations"])
    append_table_section(lines, "Phase 1 Existing Overall Average Verification", summary["overall_avg_verification"])
    append_table_section(lines, "Phase 1 Secondary Composite Descriptives", summary["composite_descriptives"])
    return lines


def reliability_summary_lines(summary: dict[str, object], has_existing_average: bool) -> list[str]:
    alpha_row = summary["alpha"][0]
    alpha = alpha_row["cronbach_alpha"]
    lines = [
        f"Cronbach's alpha was {alpha} ({alpha_row['interpretation']}).",
    ]
    if alpha_row["composite_created"]:
        lines.append(
            "Reliability is acceptable for a secondary overall explanation-quality composite, but this composite should not replace the four primary rating dimensions."
        )
    else:
        lines.append(
            "Reliability is below the pre-set 0.70 threshold, so no secondary overall composite should be emphasized."
        )
    if has_existing_average:
        verification = summary["overall_avg_verification"][0]
        lines.append(
            f"The existing rating_overall_avg column was checked in {verification['checked_rows']} rows: {verification['verification_result']}."
        )
    return lines


def phase1_severity_summary_lines(summary: dict[str, object]) -> list[str]:
    min_trials = min(int(row["n_trials"]) for row in summary["support"]) if summary["support"] else 0
    min_participants = min(int(row["n_participants"]) for row in summary["support"]) if summary["support"] else 0
    lines = [
        f"The smallest explanation-type by severity subgroup has {min_trials} trials from {min_participants} participants.",
    ]
    if summary["interaction_supported"]:
        lines.append(
            "Because every subgroup has at least 10 trials, the exploratory interaction model was run. This does not make the subgroup analysis primary."
        )
    else:
        lines.append(
            "The exploratory interaction model was not run because at least one subgroup had fewer than 10 trials."
        )

    severity_evidence = [row for row in summary["severity_models"] if float(row["p_value"]) < 0.05]
    if severity_evidence:
        dimensions = ", ".join(f"{row['dimension']} (p={row['p_value']})" for row in severity_evidence)
        lines.append(f"The exploratory main severity model showed evidence below 0.05 for: {dimensions}.")
    else:
        lines.append("The exploratory main severity models did not show evidence below 0.05 for any rating dimension.")

    interaction_evidence = [row for row in summary["interaction_models"] if float(row["p_value"]) < 0.05]
    if interaction_evidence:
        dimensions = ", ".join(f"{row['dimension']} (p={row['p_value']})" for row in interaction_evidence)
        lines.append(
            f"The exploratory explanation type x severity model showed evidence below 0.05 for: {dimensions}. Interpret this cautiously because subgroup sizes are small."
        )
    elif summary["interaction_models"]:
        lines.append(
            "The exploratory explanation type x severity models did not show evidence below 0.05 for any rating dimension."
        )

    if summary["model_notes"]:
        lines.append("Some model fits produced warnings; see the model notes table before using these exploratory results in the thesis.")
    return lines


def phase1_result_summary_lines(summary: dict[str, object]) -> list[str]:
    lines = []
    primary_evidence = [row for row in summary["overall"] if float(row["p_value"]) < 0.05]
    if primary_evidence:
        dimensions = ", ".join(f"{row['dimension']} (p={row['p_value']})" for row in primary_evidence)
        lines.append(f"Primary mixed-model overall tests showed evidence of an explanation-type effect for: {dimensions}.")
    else:
        lines.append("Primary mixed-model overall tests did not show evidence of an explanation-type effect for any rating dimension.")

    if summary["pairwise"]:
        adjusted = [row for row in summary["pairwise"] if float(row["holm_adjusted_p_value"]) < 0.05]
        if adjusted:
            comparisons = ", ".join(
                f"{row['dimension']} {row['comparison']} (Holm p={row['holm_adjusted_p_value']})"
                for row in adjusted
            )
            lines.append(f"After Holm correction, these pairwise comparisons remained below 0.05: {comparisons}.")
        else:
            lines.append("For dimensions that passed the overall-test gate, no pairwise comparison remained below 0.05 after Holm correction.")

    secondary_evidence = [
        row for row in summary["participant_level"] if row["p_value"] != "" and float(row["p_value"]) < 0.05
    ]
    if secondary_evidence:
        dimensions = ", ".join(f"{row['dimension']} (p={row['p_value']})" for row in secondary_evidence)
        lines.append(
            "The secondary participant-level complete-case check showed evidence for "
            f"{dimensions}. This is a robustness check and should not override the primary trial-level mixed model."
        )
    else:
        lines.append("The secondary participant-level complete-case checks did not show evidence below 0.05.")

    if summary["model_notes"]:
        lines.append(
            "Some model fits reported a random-effects covariance warning. The models converged, but this should be mentioned as a small-sample or boundary-model caution."
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
