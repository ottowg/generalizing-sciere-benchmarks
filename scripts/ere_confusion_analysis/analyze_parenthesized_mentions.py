"""Analyze predicted mentions containing parenthesized abbreviations.

Finds mentions like "Bidirectional Encoder Representations from Transformers ( BERT )"
across all unified predictions and gold annotations on train/dev/test splits.
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from typing import Literal

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import reports_dir
from unifiedsciere.unification.pipeline import apply_unification_pipeline

PAREN_PATTERN = re.compile(r"\(.*?\)")

DATASETS: list[Literal["scier", "scinlp", "gsap-ere"]] = ["scier", "scinlp", "gsap-ere"]
MODELS:   list[Literal["scier", "scinlp", "gsap-ere"]] = ["scier", "scinlp", "gsap-ere"]
SPLITS:   list[Literal["train", "dev", "test"]]        = ["train", "dev", "test"]
MAX_EXAMPLES = 5


def _collect_rows(mentions, dataset: str, annotator: str, split: str) -> list[dict]:
    """Count parenthesized mentions per label and return flat rows."""
    by_label: dict[str, list] = defaultdict(list)
    total_by_label: dict[str, int] = defaultdict(int)

    for m in mentions:
        total_by_label[m.label] += 1
        if PAREN_PATTERN.search(m.text):
            by_label[m.label].append(m.text)

    rows = []
    for label in sorted(set(by_label) | set(total_by_label)):
        matches = by_label.get(label, [])
        total = total_by_label.get(label, 0)
        count = len(matches)
        pct = (count / total * 100) if total > 0 else 0.0
        examples = "; ".join(f'"{t}"' for t in matches[:MAX_EXAMPLES]).replace("|", "\\|")
        rows.append({
            "dataset":   dataset,
            "annotator": annotator,
            "split":     split,
            "label":     label,
            "count":     count,
            "total":     total,
            "pct":       round(pct, 1),
            "examples":  examples,
        })
    return rows


def _run_split(split: str) -> tuple[list[dict], list[str]]:
    """Collect all rows and errors for one split."""
    all_rows: list[dict] = []
    errors: list[str] = []

    for dataset in DATASETS:
        try:
            corpus = load_corpus(dataset, split, data_type="gold")
            unified, _ = apply_unification_pipeline(
                corpus, dataset=dataset, apply_to_gold=True, apply_to_predicted=False
            )
            all_rows.extend(_collect_rows(unified.mentions, dataset, "gold", split))
        except Exception as e:
            errors.append(f"gold / {dataset} / {split}: {e}")

        for model in MODELS:
            try:
                corpus = load_corpus(dataset, split, data_type="predictions", trained_on=model)
                unified, _ = apply_unification_pipeline(
                    corpus, dataset=model, apply_to_gold=False, apply_to_predicted=True
                )
                all_rows.extend(_collect_rows(unified.mentions_predicted, dataset, model, split))
            except Exception as e:
                errors.append(f"{model} → {dataset} / {split}: {e}")

    return all_rows, errors


def main():
    output_dir = reports_dir("ere_confusion_analysis")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Generated: {timestamp}")

    all_rows: list[dict] = []
    all_errors: list[str] = []

    for split in SPLITS:
        print(f"Processing split: {split}")
        rows, errors = _run_split(split)
        all_rows.extend(rows)
        all_errors.extend(errors)

    report = {
        "title":     "Parenthesized Mentions Analysis",
        "generated": timestamp,
        "info": (
            "Parenthesized mentions reveal a systematic annotation difference across datasets. "
            "Some annotators group a full name and its abbreviation into a single span — "
            "e.g. \"Sequential Question Generation ( SQG )\" — while others annotate them as "
            "two separate mentions: \"Sequential Question Generation\" and \"SQG\". "
            "A high parenthesis rate therefore indicates a tendency toward longer, self-contained "
            "spans that bundle the abbreviation alongside its expansion, rather than splitting "
            "them into distinct entities."
        ),
        "notes": [
            "Pattern: Any mention text containing (...) is counted",
            "Tokens are space-joined, so abbreviations appear as ( BERT ) rather than (BERT)",
            "All metrics computed after full unification pipeline (merge, drop, map, dataset-specific corrections)",
            "Annotator: gold = gold annotations; otherwise the dataset the model was trained on",
        ],
        "columns": [
            {"key": "dataset",   "label": "Dataset"},
            {"key": "annotator", "label": "Annotator"},
            {"key": "split",     "label": "Split"},
            {"key": "label",     "label": "Entity Type"},
            {"key": "count",     "label": "Count",    "align": "end"},
            {"key": "total",     "label": "Total",    "align": "end"},
            {"key": "pct",       "label": "%",        "align": "end"},
            {"key": "examples",  "label": "Examples"},
        ],
        "rows":   all_rows,
        "errors": all_errors,
    }
    json_path = output_dir / "parenthesized_mentions.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"JSON report saved: {json_path}")


if __name__ == "__main__":
    main()
