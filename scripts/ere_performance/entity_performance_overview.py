"""Generate cross-dataset entity performance overview (partial match).

Produces a matrix of entity partial F1 for each label across
train->test dataset pairs on dev and test splits.

Usage:
    uv run python scripts/ere_performance/entity_performance_overview.py
"""

from typing import Literal

import gsaphub as gh
import pandas as pd
import yaml

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import mention_to_gsaphub
from unifiedsciere.paths import project_root
from unifiedsciere.reporting import MarkdownReport
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]


def _get_f1_column(df: pd.DataFrame) -> object:
    for col in df.columns:
        if "f1" in str(col).lower():
            return col
    raise ValueError(f"F1 column not found in metrics DataFrame: {list(df.columns)}")


def _load_unified_pair(train_ds: str, test_ds: str, split: str) -> tuple:
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
    return gold_corpus, pred_corpus


def _evaluate_pair(train_ds: str, test_ds: str, split: str) -> pd.DataFrame | None:
    try:
        gold_corpus, pred_corpus = _load_unified_pair(train_ds, test_ds, split)
        ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]
        ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]
        return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)
    except Exception as e:
        print(f"  SKIP {train_ds}→{test_ds} {split}: {e}")
        return None


def _evaluate_unified(train_ds: str, split: str) -> pd.DataFrame | None:
    all_gold_mentions = []
    all_pred_mentions = []
    for test_ds in DATASETS:
        try:
            gold_corpus, pred_corpus = _load_unified_pair(train_ds, test_ds, split)
            all_gold_mentions.extend(gold_corpus.mentions)
            all_pred_mentions.extend(pred_corpus.mentions_predicted)
        except Exception as e:
            print(f"  SKIP unified {train_ds}→{test_ds} {split}: {e}")
    if not all_gold_mentions:
        return None
    ents_gold = [mention_to_gsaphub(m) for m in all_gold_mentions]
    ents_pred = [mention_to_gsaphub(m) for m in all_pred_mentions]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)


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
    splits = ["dev", "test"]

    mappings_path = (
        project_root() / "src" / "unifiedsciere" / "unification" / "label_mappings.yaml"
    )
    label_mappings = yaml.safe_load(mappings_path.read_text())
    labels = list(label_mappings.get("unified_labels", [])) + ["micro"]

    metrics_by_pair: dict[tuple[str, str, str], pd.DataFrame] = {}
    metrics_unified: dict[tuple[str, str], pd.DataFrame] = {}
    for split in splits:
        for train_ds in DATASETS:
            for test_ds in DATASETS:
                metrics_by_pair[(split, train_ds, test_ds)] = _evaluate_pair(
                    train_ds, test_ds, split
                )
            metrics_unified[(split, train_ds)] = _evaluate_unified(train_ds, split)

    report = MarkdownReport("Entity Performance Overview (Partial Match)")
    report.bullet_list(
        [
            "Metric: entity partial match, F1",
            f"Splits: {', '.join(splits)}",
            f"Datasets: {', '.join(d.upper() for d in DATASETS)}",
        ]
    )

    for split in splits:
        header = [
            "Label",
            "Train Data",
            f"GSAP ({split})",
            f"SciER ({split})",
            f"SciNLP ({split})",
            f"Unified ({split})",
        ]
        rows: list[list[str]] = []
        for label in labels:
            for train_ds in DATASETS:
                row = [
                    label if train_ds == DATASETS[0] else "",
                    train_ds.upper(),
                ]
                values: list[float | None] = []
                for test_ds in DATASETS:
                    metrics = metrics_by_pair.get((split, train_ds, test_ds))
                    if metrics is None:
                        values.append(None)
                        continue
                    f1_col = _get_f1_column(metrics)
                    match = metrics[metrics["label"] == label]
                    if match.empty:
                        values.append(None)
                    else:
                        values.append(float(match.iloc[0][f1_col]) * 100)
                # Unified column
                unified_metrics = metrics_unified.get((split, train_ds))
                if unified_metrics is not None:
                    f1_col = _get_f1_column(unified_metrics)
                    match = unified_metrics[unified_metrics["label"] == label]
                    values.append(
                        float(match.iloc[0][f1_col]) * 100 if not match.empty else None
                    )
                else:
                    values.append(None)
                max_val = max([v for v in values if v is not None], default=None)
                for idx, val in enumerate(values):
                    is_diag = idx < len(DATASETS) and DATASETS[idx] == train_ds
                    is_max = max_val is not None and val == max_val
                    row.append(_format_cell(val, is_diag, is_max))
                rows.append(row)

        df = pd.DataFrame(rows, columns=header)
        report.heading(f"Split: {split}", level=2)
        report.table(df)

    report.write("reports/ere_performance/entity_performance_overview.md")


if __name__ == "__main__":
    main()
