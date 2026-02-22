#!/usr/bin/env python3
"""Compare classification results from two experiments (with_schema).

Reads JSONL output files, computes validity rates, timing stats,
label distributions, confidence distributions, and schema feedback,
then writes a markdown report.

Usage:
    python scripts/compare_classifications.py \
        --a data/classifications/exp02_qwen3_schema/with_schema.jsonl \
        --b data/classifications/exp02_llama4_schema/with_schema.jsonl \
        --output reports/paper_classification/exp02_schema_comparison.md
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def load_results(path: Path) -> list[dict]:
    results = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def meta_stats(results: list[dict]) -> dict:
    valid = [r for r in results if r.get("_meta", {}).get("valid", False)]
    invalid = [r for r in results if not r.get("_meta", {}).get("valid", False)]
    times = [
        r["_meta"]["elapsed_seconds"]
        for r in results
        if "elapsed_seconds" in r.get("_meta", {})
    ]

    validation_errors: Counter = Counter()
    for r in invalid:
        for err in r.get("_meta", {}).get("validation_errors", []):
            validation_errors[err] += 1
        if r.get("_parse_error"):
            validation_errors["_parse_error"] += 1

    return {
        "total": len(results),
        "valid": len(valid),
        "invalid": len(invalid),
        "validity_pct": round(100 * len(valid) / max(len(results), 1), 1),
        "time_mean": round(sum(times) / max(len(times), 1), 1),
        "time_min": round(min(times), 1) if times else 0,
        "time_max": round(max(times), 1) if times else 0,
        "time_total_min": round(sum(times) / 60, 1) if times else 0,
        "top_validation_errors": validation_errors.most_common(10),
    }


def label_distribution(results: list[dict], field_path: list[str]) -> Counter:
    counter: Counter = Counter()
    for r in results:
        val = r
        for key in field_path:
            if isinstance(val, dict):
                val = val.get(key)
            else:
                val = None
                break
        if val is None:
            counter["_MISSING_"] += 1
        elif isinstance(val, list):
            for v in val:
                counter[str(v)] += 1
        else:
            counter[str(val)] += 1
    return counter


def confidence_stats(results: list[dict]) -> dict:
    overall = []
    by_field: dict[str, list[int]] = {}
    for r in results:
        conf = r.get("confidence", {})
        if isinstance(conf.get("overall"), (int, float)):
            overall.append(conf["overall"])
        for field, val in conf.get("by_field", {}).items():
            if isinstance(val, (int, float)):
                by_field.setdefault(field, []).append(val)

    def _stats(vals):
        if not vals:
            return {"mean": 0, "min": 0, "max": 0, "n": 0}
        return {
            "mean": round(sum(vals) / len(vals), 2),
            "min": min(vals),
            "max": max(vals),
            "n": len(vals),
        }

    return {
        "overall": _stats(overall),
        "by_field": {k: _stats(v) for k, v in sorted(by_field.items())},
    }


def flag_counts(results: list[dict]) -> dict:
    counts = Counter()
    for r in results:
        flags = r.get("flags", {})
        for key, val in flags.items():
            if val:
                counts[key] += 1
    return dict(counts)


def schema_feedback_summary(results: list[dict]) -> dict:
    suggested = 0
    rephrases = 0
    new_area: Counter = Counter()
    new_task: Counter = Counter()
    new_contrib: Counter = Counter()
    for r in results:
        fb = r.get("schema_feedback", {})
        suggested += len(fb.get("suggested_changes", []))
        rephrases += len(fb.get("rephrases", []))
        for item in fb.get("new_labels", {}).get("area", []):
            v = item.get("value", str(item)) if isinstance(item, dict) else str(item)
            new_area[v] += 1
        for item in fb.get("new_labels", {}).get("task_topic", []):
            v = item.get("value", str(item)) if isinstance(item, dict) else str(item)
            new_task[v] += 1
        for item in fb.get("new_labels", {}).get("contribution", []):
            v = item.get("value", str(item)) if isinstance(item, dict) else str(item)
            new_contrib[v] += 1
    return {
        "suggested_changes": suggested,
        "rephrases": rephrases,
        "new_area_labels": new_area.most_common(15),
        "new_task_labels": new_task.most_common(15),
        "new_contribution_labels": new_contrib.most_common(15),
    }


def unmatched_summary(results: list[dict]) -> dict:
    area: Counter = Counter()
    task: Counter = Counter()
    contrib: Counter = Counter()
    other_notes = 0
    for r in results:
        um = r.get("labels", {}).get("unmatched", {})
        for v in um.get("area", []):
            area[v] += 1
        for v in um.get("task_topic", []):
            task[v] += 1
        for v in um.get("contribution", []):
            contrib[v] += 1
        if um.get("other_notes", "").strip():
            other_notes += 1
    return {
        "area": area.most_common(15),
        "task_topic": task.most_common(15),
        "contribution": contrib.most_common(15),
        "papers_with_other_notes": other_notes,
    }


def _counter_table(
    counter_items: list[tuple], col1: str = "Value", col2: str = "Count"
) -> str:
    if not counter_items:
        return "_none_\n"
    lines = [f"| {col1} | {col2} |", "| --- | ---: |"]
    for val, count in counter_items:
        lines.append(f"| {val} | {count} |")
    return "\n".join(lines) + "\n"


def generate_report(
    name_a: str,
    results_a: list[dict],
    name_b: str,
    results_b: list[dict],
) -> str:
    ms_a = meta_stats(results_a)
    ms_b = meta_stats(results_b)

    lines = [
        f"# Classification Comparison: {name_a} vs {name_b}",
        "",
        "## Overview",
        "",
        "| Metric | " + name_a + " | " + name_b + " |",
        "| --- | ---: | ---: |",
        f"| Total papers | {ms_a['total']} | {ms_b['total']} |",
        f"| Valid | {ms_a['valid']} ({ms_a['validity_pct']}%) | {ms_b['valid']} ({ms_b['validity_pct']}%) |",
        f"| Invalid | {ms_a['invalid']} | {ms_b['invalid']} |",
        f"| Mean time (s) | {ms_a['time_mean']} | {ms_b['time_mean']} |",
        f"| Min / Max time (s) | {ms_a['time_min']} / {ms_a['time_max']} | {ms_b['time_min']} / {ms_b['time_max']} |",
        f"| Total time (min) | {ms_a['time_total_min']} | {ms_b['time_total_min']} |",
        "",
    ]

    # Validation errors
    lines.append("## Top Validation Errors")
    lines.append("")
    for name, ms in [(name_a, ms_a), (name_b, ms_b)]:
        lines.append(f"### {name}")
        lines.append("")
        lines.append(_counter_table(ms["top_validation_errors"], "Error", "Count"))
        lines.append("")

    # Label distributions
    label_fields = [
        ("Area", ["labels", "area"]),
        ("Task/Topic", ["labels", "task_topic"]),
        ("Contribution (primary)", ["labels", "contribution", "primary"]),
        ("Paper Type (primary)", ["labels", "paper_type_primary"]),
    ]

    lines.append("## Label Distributions")
    lines.append("")
    for label_name, field_path in label_fields:
        dist_a = label_distribution(results_a, field_path)
        dist_b = label_distribution(results_b, field_path)
        all_keys = sorted(set(dist_a.keys()) | set(dist_b.keys()))
        lines.append(f"### {label_name}")
        lines.append("")
        lines.append(f"| Value | {name_a} | {name_b} |")
        lines.append("| --- | ---: | ---: |")
        for k in all_keys:
            lines.append(f"| {k} | {dist_a.get(k, 0)} | {dist_b.get(k, 0)} |")
        lines.append("")

    # Confidence
    conf_a = confidence_stats(results_a)
    conf_b = confidence_stats(results_b)
    lines.append("## Confidence Scores")
    lines.append("")
    lines.append(f"| Field | {name_a} (mean) | {name_b} (mean) |")
    lines.append("| --- | ---: | ---: |")
    lines.append(
        f"| overall | {conf_a['overall']['mean']} (n={conf_a['overall']['n']}) | {conf_b['overall']['mean']} (n={conf_b['overall']['n']}) |"
    )
    all_conf_fields = sorted(
        set(conf_a["by_field"].keys()) | set(conf_b["by_field"].keys())
    )
    for f in all_conf_fields:
        sa = conf_a["by_field"].get(f, {"mean": "-", "n": 0})
        sb = conf_b["by_field"].get(f, {"mean": "-", "n": 0})
        lines.append(
            f"| {f} | {sa['mean']} (n={sa['n']}) | {sb['mean']} (n={sb['n']}) |"
        )
    lines.append("")

    # Flags
    flags_a = flag_counts(results_a)
    flags_b = flag_counts(results_b)
    all_flags = sorted(set(flags_a.keys()) | set(flags_b.keys()))
    lines.append("## Flags")
    lines.append("")
    lines.append(f"| Flag | {name_a} | {name_b} |")
    lines.append("| --- | ---: | ---: |")
    for f in all_flags:
        lines.append(f"| {f} | {flags_a.get(f, 0)} | {flags_b.get(f, 0)} |")
    lines.append("")

    # Unmatched labels
    um_a = unmatched_summary(results_a)
    um_b = unmatched_summary(results_b)
    lines.append("## Unmatched Labels (top 15)")
    lines.append("")
    for category in ["area", "task_topic", "contribution"]:
        lines.append(f"### Unmatched: {category}")
        lines.append("")
        lines.append(f"**{name_a}**")
        lines.append("")
        lines.append(_counter_table(um_a[category]))
        lines.append(f"**{name_b}**")
        lines.append("")
        lines.append(_counter_table(um_b[category]))

    # Schema feedback
    sf_a = schema_feedback_summary(results_a)
    sf_b = schema_feedback_summary(results_b)
    lines.append("## Schema Feedback Summary")
    lines.append("")
    lines.append(f"| Metric | {name_a} | {name_b} |")
    lines.append("| --- | ---: | ---: |")
    lines.append(
        f"| Suggested changes | {sf_a['suggested_changes']} | {sf_b['suggested_changes']} |"
    )
    lines.append(f"| Rephrases | {sf_a['rephrases']} | {sf_b['rephrases']} |")
    lines.append("")

    for category, key in [
        ("Area", "new_area_labels"),
        ("Task/Topic", "new_task_labels"),
        ("Contribution", "new_contribution_labels"),
    ]:
        lines.append(f"### Proposed new labels: {category}")
        lines.append("")
        lines.append(f"**{name_a}**")
        lines.append("")
        lines.append(_counter_table(sf_a[key]))
        lines.append(f"**{name_b}**")
        lines.append("")
        lines.append(_counter_table(sf_b[key]))

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two classification result sets."
    )
    parser.add_argument("--a", type=Path, required=True, help="First results JSONL.")
    parser.add_argument("--b", type=Path, required=True, help="Second results JSONL.")
    parser.add_argument("--name-a", default=None, help="Display name for first set.")
    parser.add_argument("--name-b", default=None, help="Display name for second set.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/paper_classification/exp02_schema_comparison.md"),
    )
    args = parser.parse_args()

    name_a = args.name_a or args.a.parent.name
    name_b = args.name_b or args.b.parent.name

    results_a = load_results(args.a)
    results_b = load_results(args.b)

    report = generate_report(name_a, results_a, name_b, results_b)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
