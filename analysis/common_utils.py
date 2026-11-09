"""Shared helpers for the thesis analysis pipeline.

Task 1 deliberately uses only the Python standard library so data inspection can
run even before the full statistical environment has been installed.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Iterable


RATING_MIN = 1
RATING_MAX = 5


@dataclass(frozen=True)
class Paths:
    repo_root: Path
    phase1_csv: Path
    phase2_csv: Path
    results_dir: Path
    tables_dir: Path
    figures_dir: Path


def get_paths() -> Paths:
    repo_root = Path(__file__).resolve().parents[1]
    analysis_dir = repo_root / "analysis"
    return Paths(
        repo_root=repo_root,
        phase1_csv=repo_root / "logs" / "evaluation_records.csv",
        phase2_csv=repo_root / "logs" / "within_participant_experiment_records.csv",
        results_dir=analysis_dir / "results",
        tables_dir=analysis_dir / "tables",
        figures_dir=analysis_dir / "figures",
    )


def ensure_output_dirs(paths: Paths) -> None:
    paths.results_dir.mkdir(parents=True, exist_ok=True)
    paths.tables_dir.mkdir(parents=True, exist_ok=True)
    paths.figures_dir.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required CSV file not found: {path}")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if not reader.fieldnames:
        raise ValueError(f"CSV has no header row: {path}")

    return rows


def write_table(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def missing_value_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    if not rows:
        return []

    summary = []
    total = len(rows)
    for column in rows[0].keys():
        count = sum(1 for row in rows if is_missing(row.get(column)))
        if count:
            summary.append(
                {
                    "column": column,
                    "missing_count": count,
                    "missing_percent": round(100 * count / total, 2),
                }
            )
    return summary


def is_missing(value: object) -> bool:
    return value is None or str(value).strip() == ""


def exact_duplicate_count(rows: list[dict[str, str]]) -> int:
    seen = set()
    duplicates = 0
    for row in rows:
        marker = tuple((key, row.get(key, "")) for key in sorted(row))
        if marker in seen:
            duplicates += 1
        else:
            seen.add(marker)
    return duplicates


def duplicate_key_summary(rows: list[dict[str, str]], key_columns: list[str]) -> list[dict[str, object]]:
    counts = Counter(tuple(row.get(column, "") for column in key_columns) for row in rows)
    output = []
    for key, count in counts.items():
        if count > 1:
            item = {column: value for column, value in zip(key_columns, key)}
            item["row_count"] = count
            output.append(item)
    return sorted(output, key=lambda item: (-int(item["row_count"]), tuple(str(v) for v in item.values())))


def validate_ratings(rows: list[dict[str, str]], rating_columns: list[str]) -> list[dict[str, object]]:
    invalid = []
    for row_number, row in enumerate(rows, start=2):
        for column in rating_columns:
            raw = row.get(column, "")
            try:
                value = float(raw)
            except ValueError:
                invalid.append({"csv_row": row_number, "column": column, "value": raw, "reason": "not numeric"})
                continue

            if not value.is_integer() or value < RATING_MIN or value > RATING_MAX:
                invalid.append(
                    {
                        "csv_row": row_number,
                        "column": column,
                        "value": raw,
                        "reason": "expected integer from 1 to 5",
                    }
                )
    return invalid


def numeric_rating(row: dict[str, str], column: str) -> float | None:
    raw = row.get(column, "")
    if is_missing(raw):
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def descriptive_stats(values: list[float]) -> dict[str, object]:
    clean = sorted(value for value in values if value is not None and not math.isnan(value))
    n = len(clean)
    if n == 0:
        return {"n_trials": 0, "mean": "", "sd": "", "median": "", "iqr": "", "ci95_low": "", "ci95_high": ""}

    avg = mean(clean)
    sd = sample_sd(clean)
    med = median(clean)
    q1 = percentile(clean, 25)
    q3 = percentile(clean, 75)
    se = sd / math.sqrt(n) if n > 1 else 0
    return {
        "n_trials": n,
        "mean": round(avg, 3),
        "sd": round(sd, 3),
        "median": round(med, 3),
        "iqr": round(q3 - q1, 3),
        "ci95_low": round(avg - 1.96 * se, 3),
        "ci95_high": round(avg + 1.96 * se, 3),
    }


def sample_sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def percentile(sorted_values: list[float], percent: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * percent / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[int(position)]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def condition_descriptives(
    rows: list[dict[str, str]],
    participant_column: str,
    condition_column: str,
    rating_map: dict[str, str],
) -> list[dict[str, object]]:
    conditions = sorted({clean_label(row.get(condition_column, "")) for row in rows})
    output: list[dict[str, object]] = []
    for condition in conditions:
        condition_rows = [row for row in rows if clean_label(row.get(condition_column, "")) == condition]
        participants = {
            clean_label(row.get(participant_column, ""))
            for row in condition_rows
            if clean_label(row.get(participant_column, "")) != "<missing>"
        }
        for rating_column, dimension in rating_map.items():
            values = [
                value
                for row in condition_rows
                if (value := numeric_rating(row, rating_column)) is not None
            ]
            stats = descriptive_stats(values)
            output.append(
                {
                    "condition": condition,
                    "dimension": dimension,
                    "n_trials": stats["n_trials"],
                    "n_participants": len(participants),
                    "mean": stats["mean"],
                    "sd": stats["sd"],
                    "median": stats["median"],
                    "iqr": stats["iqr"],
                    "ci95_low": stats["ci95_low"],
                    "ci95_high": stats["ci95_high"],
                }
            )
    return output


def participant_condition_means(
    rows: list[dict[str, str]],
    participant_column: str,
    condition_column: str,
    rating_map: dict[str, str],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        participant = clean_label(row.get(participant_column, ""))
        condition = clean_label(row.get(condition_column, ""))
        grouped[(participant, condition)].append(row)

    output = []
    for (participant, condition), grouped_rows in sorted(grouped.items()):
        for rating_column, dimension in rating_map.items():
            values = [
                value
                for row in grouped_rows
                if (value := numeric_rating(row, rating_column)) is not None
            ]
            output.append(
                {
                    "participant_id": participant,
                    "condition": condition,
                    "dimension": dimension,
                    "n_trials": len(values),
                    "mean": round(mean(values), 3) if values else "",
                }
            )
    return output


def paired_participant_summary(
    participant_means: list[dict[str, object]],
    first_condition: str,
    second_condition: str,
    first_label: str,
    second_label: str,
) -> list[dict[str, object]]:
    index: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for row in participant_means:
        mean_value = row.get("mean", "")
        if mean_value == "":
            continue
        key = (str(row["participant_id"]), str(row["dimension"]))
        index[key][str(row["condition"])] = float(mean_value)

    output = []
    for (participant, dimension), values in sorted(index.items()):
        first = values.get(first_condition)
        second = values.get(second_condition)
        output.append(
            {
                "participant_id": participant,
                "dimension": dimension,
                f"{first_label}_mean": round(first, 3) if first is not None else "",
                f"{second_label}_mean": round(second, 3) if second is not None else "",
                "mean_difference": round(first - second, 3) if first is not None and second is not None else "",
            }
        )
    return output


def condition_mean_differences(
    descriptives: list[dict[str, object]],
    first_condition: str,
    second_condition: str,
    first_label: str,
    second_label: str,
) -> list[dict[str, object]]:
    index = {(str(row["condition"]), str(row["dimension"])): row for row in descriptives}
    dimensions = sorted({str(row["dimension"]) for row in descriptives})
    output = []
    for dimension in dimensions:
        first = index.get((first_condition, dimension), {}).get("mean", "")
        second = index.get((second_condition, dimension), {}).get("mean", "")
        output.append(
            {
                "dimension": dimension,
                f"{first_label}_mean": first,
                f"{second_label}_mean": second,
                "mean_difference": round(float(first) - float(second), 3)
                if first != "" and second != ""
                else "",
            }
        )
    return output


def cronbach_alpha(matrix: list[list[float]]) -> float | None:
    complete_rows = [row for row in matrix if all(value is not None and not math.isnan(value) for value in row)]
    if len(complete_rows) < 2:
        return None
    n_items = len(complete_rows[0])
    if n_items < 2:
        return None

    item_columns = [[row[index] for row in complete_rows] for index in range(n_items)]
    item_variances = [sample_sd(column) ** 2 for column in item_columns]
    total_scores = [sum(row) for row in complete_rows]
    total_variance = sample_sd(total_scores) ** 2
    if total_variance == 0:
        return None
    return (n_items / (n_items - 1)) * (1 - sum(item_variances) / total_variance)


def pearson_correlation(x_values: list[float], y_values: list[float]) -> float | None:
    pairs = [
        (x, y)
        for x, y in zip(x_values, y_values)
        if x is not None and y is not None and not math.isnan(x) and not math.isnan(y)
    ]
    if len(pairs) < 2:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    sd_x = sample_sd(xs)
    sd_y = sample_sd(ys)
    if sd_x == 0 or sd_y == 0:
        return None
    avg_x = mean(xs)
    avg_y = mean(ys)
    covariance = sum((x - avg_x) * (y - avg_y) for x, y in pairs) / (len(pairs) - 1)
    return covariance / (sd_x * sd_y)


def reliability_tables(
    rows: list[dict[str, str]],
    rating_map: dict[str, str],
    id_columns: list[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rating_columns = list(rating_map.keys())
    dimensions = list(rating_map.values())
    matrix = []
    complete_case_rows = []
    for row in rows:
        values = [numeric_rating(row, column) for column in rating_columns]
        matrix.append(values)
        if all(value is not None and not math.isnan(value) for value in values):
            composite = mean(values)
            item = {column: row.get(column, "") for column in id_columns if column in row}
            item.update({dimension: value for dimension, value in zip(dimensions, values)})
            item["overall_composite"] = round(composite, 4)
            complete_case_rows.append(item)

    alpha = cronbach_alpha(matrix)
    alpha_rows = [
        {
            "n_items": len(rating_columns),
            "n_complete_rows": len(complete_case_rows),
            "cronbach_alpha": round(alpha, 4) if alpha is not None else "",
            "interpretation": alpha_interpretation(alpha),
            "composite_created": alpha is not None and alpha >= 0.7,
        }
    ]

    correlation_rows = []
    for i, first_column in enumerate(rating_columns):
        for second_column in rating_columns[i + 1 :]:
            xs = [numeric_rating(row, first_column) for row in rows]
            ys = [numeric_rating(row, second_column) for row in rows]
            n_pairwise = sum(
                1
                for x, y in zip(xs, ys)
                if x is not None and y is not None and not math.isnan(x) and not math.isnan(y)
            )
            corr = pearson_correlation(xs, ys)
            correlation_rows.append(
                {
                    "dimension_1": rating_map[first_column],
                    "dimension_2": rating_map[second_column],
                    "n_pairwise_rows": n_pairwise,
                    "pearson_r": round(corr, 4) if corr is not None else "",
                }
            )

    if not (alpha is not None and alpha >= 0.7):
        complete_case_rows = []
    return alpha_rows, correlation_rows, complete_case_rows


def alpha_interpretation(alpha: float | None) -> str:
    if alpha is None:
        return "not estimable"
    if alpha >= 0.9:
        return "excellent internal consistency"
    if alpha >= 0.8:
        return "good internal consistency"
    if alpha >= 0.7:
        return "acceptable internal consistency"
    if alpha >= 0.6:
        return "questionable internal consistency"
    return "low internal consistency"


def write_distribution_svg(
    path: Path,
    rows: list[dict[str, str]],
    condition_column: str,
    rating_map: dict[str, str],
    title: str,
) -> None:
    conditions = sorted({clean_label(row.get(condition_column, "")) for row in rows})
    dimensions = list(rating_map.items())
    panel_width = 260
    panel_height = 210
    margin_left = 44
    margin_top = 46
    width = margin_left + panel_width * len(conditions) + 24
    height = margin_top + panel_height * len(dimensions) + 30
    colors = ["#2f6f73", "#9b4d3d", "#5c6f99", "#7a6a2f"]

    parts = svg_header(width, height, title)
    for d_idx, (rating_column, dimension) in enumerate(dimensions):
        for c_idx, condition in enumerate(conditions):
            x0 = margin_left + c_idx * panel_width
            y0 = margin_top + d_idx * panel_height
            values = [
                value
                for row in rows
                if clean_label(row.get(condition_column, "")) == condition
                and (value := numeric_rating(row, rating_column)) is not None
            ]
            bins = Counter(int(value) for value in values)
            max_count = max(bins.values()) if bins else 1
            parts.append(f'<text x="{x0 + 6}" y="{y0 - 12}" class="small">{escape_svg(dimension)} - {escape_svg(condition)}</text>')
            parts.append(f'<line x1="{x0 + 20}" y1="{y0 + 150}" x2="{x0 + 230}" y2="{y0 + 150}" class="axis"/>')
            parts.append(f'<line x1="{x0 + 20}" y1="{y0 + 18}" x2="{x0 + 20}" y2="{y0 + 150}" class="axis"/>')
            for rating in range(1, 6):
                count = bins[rating]
                bar_height = 120 * count / max_count if max_count else 0
                x = x0 + 28 + (rating - 1) * 39
                y = y0 + 150 - bar_height
                parts.append(
                    f'<rect x="{x}" y="{y:.2f}" width="26" height="{bar_height:.2f}" '
                    f'fill="{colors[c_idx % len(colors)]}" opacity="0.82"/>'
                )
                parts.append(f'<text x="{x + 13}" y="{y0 + 168}" class="tick" text-anchor="middle">{rating}</text>')
                parts.append(f'<text x="{x + 13}" y="{y - 5:.2f}" class="tick" text-anchor="middle">{count}</text>')
            parts.append(f'<text x="{x0 + 125}" y="{y0 + 190}" class="tick" text-anchor="middle">rating</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_ci_svg(path: Path, descriptives: list[dict[str, object]], title: str) -> None:
    dimensions = list(dict.fromkeys(str(row["dimension"]) for row in descriptives))
    conditions = list(dict.fromkeys(str(row["condition"]) for row in descriptives))
    width = 920
    row_height = 92
    height = 70 + row_height * len(dimensions) + 40
    x_min, x_max = 1.0, 5.0
    plot_left, plot_right = 170, 840
    colors = ["#2f6f73", "#9b4d3d", "#5c6f99", "#7a6a2f"]

    parts = svg_header(width, height, title)
    for rating in range(1, 6):
        x = scale(rating, x_min, x_max, plot_left, plot_right)
        parts.append(f'<line x1="{x:.2f}" y1="46" x2="{x:.2f}" y2="{height - 35}" class="grid"/>')
        parts.append(f'<text x="{x:.2f}" y="{height - 16}" class="tick" text-anchor="middle">{rating}</text>')
    for d_idx, dimension in enumerate(dimensions):
        y_base = 76 + d_idx * row_height
        parts.append(f'<text x="18" y="{y_base + 16}" class="label">{escape_svg(dimension)}</text>')
        for c_idx, condition in enumerate(conditions):
            row = next(
                item for item in descriptives if str(item["dimension"]) == dimension and str(item["condition"]) == condition
            )
            mean_value = float(row["mean"])
            low = max(x_min, float(row["ci95_low"]))
            high = min(x_max, float(row["ci95_high"]))
            y = y_base + 18 + c_idx * 18
            x_mean = scale(mean_value, x_min, x_max, plot_left, plot_right)
            x_low = scale(low, x_min, x_max, plot_left, plot_right)
            x_high = scale(high, x_min, x_max, plot_left, plot_right)
            color = colors[c_idx % len(colors)]
            parts.append(f'<line x1="{x_low:.2f}" y1="{y}" x2="{x_high:.2f}" y2="{y}" stroke="{color}" stroke-width="3"/>')
            parts.append(f'<circle cx="{x_mean:.2f}" cy="{y}" r="5" fill="{color}"/>')
            parts.append(f'<text x="{plot_right + 12}" y="{y + 4}" class="small">{escape_svg(condition)} mean={mean_value:.2f}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_phase2_paired_svg(path: Path, paired_rows: list[dict[str, object]], title: str) -> None:
    dimensions = list(dict.fromkeys(str(row["dimension"]) for row in paired_rows))
    width = 920
    panel_height = 175
    height = 58 + panel_height * len(dimensions) + 30
    plot_left, plot_right = 160, 790
    x_min, x_max = 1.0, 5.0
    parts = svg_header(width, height, title)
    for d_idx, dimension in enumerate(dimensions):
        y0 = 60 + d_idx * panel_height
        rows = [row for row in paired_rows if str(row["dimension"]) == dimension and row["agentic_xai_mean"] != "" and row["mentallama_mean"] != ""]
        parts.append(f'<text x="18" y="{y0 + 12}" class="label">{escape_svg(dimension)}</text>')
        parts.append(f'<text x="{plot_left}" y="{y0 + 12}" class="small" text-anchor="middle">Agentic XAI</text>')
        parts.append(f'<text x="{plot_right}" y="{y0 + 12}" class="small" text-anchor="middle">MentaLLaMA</text>')
        for idx, row in enumerate(rows):
            y = y0 + 32 + idx * 9
            first = float(row["agentic_xai_mean"])
            second = float(row["mentallama_mean"])
            x1 = scale(first, x_min, x_max, plot_left - 90, plot_left + 90)
            x2 = scale(second, x_min, x_max, plot_right - 90, plot_right + 90)
            color = "#2f6f73" if first >= second else "#9b4d3d"
            parts.append(f'<line x1="{x1:.2f}" y1="{y}" x2="{x2:.2f}" y2="{y}" stroke="{color}" stroke-width="1.4" opacity="0.68"/>')
            parts.append(f'<circle cx="{x1:.2f}" cy="{y}" r="3" fill="#2f6f73"/>')
            parts.append(f'<circle cx="{x2:.2f}" cy="{y}" r="3" fill="#9b4d3d"/>')
        parts.append(f'<line x1="{plot_left - 90}" y1="{y0 + 156}" x2="{plot_left + 90}" y2="{y0 + 156}" class="axis"/>')
        parts.append(f'<line x1="{plot_right - 90}" y1="{y0 + 156}" x2="{plot_right + 90}" y2="{y0 + 156}" class="axis"/>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_interaction_svg(
    path: Path,
    rows: list[dict[str, object]],
    x_column: str,
    line_column: str,
    value_column: str,
    panel_column: str,
    title: str,
    x_order: list[str],
    line_order: list[str],
) -> None:
    panels = list(dict.fromkeys(str(row[panel_column]) for row in rows))
    width = 940
    panel_height = 210
    height = 58 + panel_height * len(panels) + 30
    plot_left, plot_right = 110, 760
    colors = ["#2f6f73", "#9b4d3d", "#5c6f99", "#7a6a2f"]
    parts = svg_header(width, height, title)
    index = {
        (str(row[panel_column]), str(row[line_column]), str(row[x_column])): row
        for row in rows
    }

    for p_idx, panel in enumerate(panels):
        y0 = 60 + p_idx * panel_height
        plot_top = y0 + 24
        plot_bottom = y0 + 150
        parts.append(f'<text x="18" y="{y0 + 12}" class="label">{escape_svg(panel)}</text>')
        for rating in range(1, 6):
            y = scale(rating, 1, 5, plot_bottom, plot_top)
            parts.append(f'<line x1="{plot_left}" y1="{y:.2f}" x2="{plot_right}" y2="{y:.2f}" class="grid"/>')
            parts.append(f'<text x="{plot_left - 12}" y="{y + 4:.2f}" class="tick" text-anchor="end">{rating}</text>')
        x_positions = {
            label: scale(idx, 0, max(1, len(x_order) - 1), plot_left, plot_right)
            for idx, label in enumerate(x_order)
        }
        for label, x in x_positions.items():
            parts.append(f'<text x="{x:.2f}" y="{plot_bottom + 24}" class="tick" text-anchor="middle">{escape_svg(label)}</text>')
        parts.append(f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" class="axis"/>')
        parts.append(f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}" class="axis"/>')

        for l_idx, line_value in enumerate(line_order):
            points = []
            for x_value in x_order:
                row = index.get((panel, line_value, x_value))
                if row is None or row[value_column] == "":
                    continue
                x = x_positions[x_value]
                y = scale(float(row[value_column]), 1, 5, plot_bottom, plot_top)
                points.append((x, y))
            if len(points) >= 2:
                points_text = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
                parts.append(
                    f'<polyline points="{points_text}" fill="none" stroke="{colors[l_idx % len(colors)]}" '
                    'stroke-width="2.4" opacity="0.9"/>'
                )
            for x, y in points:
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{colors[l_idx % len(colors)]}"/>')
            legend_y = y0 + 25 + l_idx * 16
            parts.append(f'<line x1="790" y1="{legend_y}" x2="814" y2="{legend_y}" stroke="{colors[l_idx % len(colors)]}" stroke-width="2.4"/>')
            parts.append(f'<text x="820" y="{legend_y + 4}" class="small">{escape_svg(line_value)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#202020}.title{font-size:18px;font-weight:700}.label{font-size:13px;font-weight:700}.small{font-size:11px}.tick{font-size:10px}.axis{stroke:#333;stroke-width:1}.grid{stroke:#dedede;stroke-width:1}",
        "</style>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="18" y="28" class="title">{escape_svg(title)}</text>',
    ]


def scale(value: float, source_min: float, source_max: float, target_min: float, target_max: float) -> float:
    return target_min + (value - source_min) * (target_max - target_min) / (source_max - source_min)


def escape_svg(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def count_by(rows: list[dict[str, str]], columns: list[str]) -> list[dict[str, object]]:
    counts = Counter(tuple(clean_label(row.get(column, "")) for column in columns) for row in rows)
    output = []
    for key, count in counts.items():
        item = {column: value for column, value in zip(columns, key)}
        item["n_trials"] = count
        output.append(item)
    return sorted(output, key=lambda item: tuple(str(item[column]) for column in columns))


def participant_trial_summary(rows: list[dict[str, str]], participant_column: str) -> dict[str, object]:
    counts = Counter(clean_label(row.get(participant_column, "")) for row in rows)
    values = list(counts.values())
    if not values:
        return {
            "n_participants": 0,
            "min_trials": 0,
            "median_trials": 0,
            "mean_trials": 0,
            "max_trials": 0,
            "incomplete_participants": [],
            "participant_trial_rows": [],
        }

    max_trials = max(values)
    incomplete = [participant for participant, count in counts.items() if count < max_trials]
    participant_rows = [
        {"participant_id": participant, "n_trials": count, "complete_by_observed_max": count == max_trials}
        for participant, count in sorted(counts.items(), key=lambda item: item[0])
    ]
    return {
        "n_participants": len(counts),
        "min_trials": min(values),
        "median_trials": median(values),
        "mean_trials": round(mean(values), 2),
        "max_trials": max_trials,
        "incomplete_participants": sorted(incomplete),
        "participant_trial_rows": participant_rows,
    }


def crosstab(rows: list[dict[str, str]], row_column: str, column_column: str) -> list[dict[str, object]]:
    row_values = sorted({clean_label(row.get(row_column, "")) for row in rows})
    column_values = sorted({clean_label(row.get(column_column, "")) for row in rows})
    counts = Counter((clean_label(row.get(row_column, "")), clean_label(row.get(column_column, ""))) for row in rows)

    table = []
    for row_value in row_values:
        item: dict[str, object] = {row_column: row_value}
        total = 0
        for column_value in column_values:
            count = counts[(row_value, column_value)]
            item[column_value] = count
            total += count
        item["total"] = total
        table.append(item)
    return table


def participant_condition_counts(
    rows: list[dict[str, str]], participant_column: str, condition_column: str
) -> list[dict[str, object]]:
    condition_values = sorted({clean_label(row.get(condition_column, "")) for row in rows})
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[clean_label(row.get(participant_column, ""))][clean_label(row.get(condition_column, ""))] += 1

    output = []
    for participant in sorted(grouped):
        item: dict[str, object] = {participant_column: participant}
        total = 0
        for condition in condition_values:
            count = grouped[participant][condition]
            item[condition] = count
            total += count
        item["total"] = total
        output.append(item)
    return output


def clean_label(value: object) -> str:
    text = "" if value is None else str(value).strip()
    return text if text else "<missing>"


def format_count_table(rows: list[dict[str, object]], max_rows: int = 30) -> str:
    if not rows:
        return "No rows."

    fieldnames = list(rows[0].keys())
    visible = rows[:max_rows]
    widths = {
        field: max(len(str(field)), *(len(str(row.get(field, ""))) for row in visible))
        for field in fieldnames
    }
    header = " | ".join(str(field).ljust(widths[field]) for field in fieldnames)
    separator = " | ".join("-" * widths[field] for field in fieldnames)
    body = [" | ".join(str(row.get(field, "")).ljust(widths[field]) for field in fieldnames) for row in visible]
    extra = []
    if len(rows) > max_rows:
        extra.append(f"... {len(rows) - max_rows} more rows not shown")
    return "\n".join([header, separator, *body, *extra])


def append_section(lines: list[str], title: str, body: Iterable[str]) -> None:
    lines.append(f"## {title}")
    lines.extend(body)
    lines.append("")
