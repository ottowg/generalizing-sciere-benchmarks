"""Generate cross-dataset entity performance overview (partial match).

Produces a matrix of entity partial F1 for each label across
train->test dataset pairs on test splits.

Usage:
    uv run python scripts/ere_performance/entity_performance_overview.py
"""

from typing import Literal

import pandas as pd
import yaml

import gsaphub as gh

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import mention_to_gsaphub
from unifiedsciere.paths import project_root
from unifiedsciere.reporting import MarkdownReport
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap", "scier", "scinlp"]] = ["gsap", "scier", "scinlp"]


def _get_f1_column(df: pd.DataFrame) -> object:
    for col in df.columns:
        if "f1" in str(col).lower():
            return col
    raise ValueError(f"F1 column not found in metrics DataFrame: {list(df.columns)}")


def _evaluate_pair(train_ds: str, test_ds: str, split: str) -> pd.DataFrame | None:
    gold_corpus = load_corpus(test_ds, split, data_type="gold")
    pred_corpus = load_corpus(
        test_ds, split, data_type="predictions", trained_on=train_ds
    )

    gold_corpus, _ = apply_unification_pipeline(
        gold_corpus, test_ds, apply_to_gold=True, apply_to_predicted=False
    )
    pred_corpus, _ = apply_unification_pipeline(
        pred_corpus, train_ds, apply_to_gold=False, apply_to_predicted=True
    )

    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]

    results = gh.evaluate.entities.precision_recall_f1(
        ents_gold, ents_pred, partial=True
    )
    return results


def _format_cell(val: float | None, is_diag: bool, is_max: bool) -> str:
    if val is None:
        return "NA"
    text = f"{val:.1f}"
    if is_diag and is_max:
        return f"**_{text}_**"
    if is_diag:
        return f"_{text}_"
    if is_max:
        return f"**{text}**"
    return text


def main() -> None:
    split = "test"

    mappings_path = (
        project_root() / "src" / "unifiedsciere" / "unification" / "label_mappings.yaml"
    )
    label_mappings = yaml.safe_load(mappings_path.read_text())
    labels = list(label_mappings.get("unified_labels", [])) + ["micro"]

    metrics_by_pair: dict[tuple[str, str], pd.DataFrame] = {}
    for train_ds in DATASETS:
        for test_ds in DATASETS:
            metrics_by_pair[(train_ds, test_ds)] = _evaluate_pair(
                train_ds, test_ds, split
            )

    header = ["Label", "Train→Test", "GSAP", "SciER", "SciNLP"]
    rows: list[list[str]] = []

    for label in labels:
        for test_ds in DATASETS:
            row = [label if test_ds == DATASETS[0] else "", test_ds.upper()]
            values: list[float | None] = []
            for train_ds in DATASETS:
                metrics = metrics_by_pair.get((train_ds, test_ds))
                if metrics is None:
                    values.append(None)
                    continue
                f1_col = _get_f1_column(metrics)
                match = metrics[metrics["label"] == label]
                if match.empty:
                    values.append(None)
                else:
                    values.append(float(match.iloc[0][f1_col]) * 100)
            max_val = max([v for v in values if v is not None], default=None)
            for idx, val in enumerate(values):
                is_diag = DATASETS[idx] == test_ds
                is_max = max_val is not None and val == max_val
                row.append(_format_cell(val, is_diag, is_max))
            rows.append(row)

    df = pd.DataFrame(rows, columns=header)

    report = MarkdownReport("Entity Performance Overview (Partial Match)")
    report.bullet_list(
        [
            "Metric: entity partial match, F1",
            f"Split: {split}",
            f"Datasets: {', '.join(d.upper() for d in DATASETS)}",
        ]
    )
    report.table(df)
    report.write("reports/ere_performance/entity_performance_overview.md")


if __name__ == "__main__":
    main()
