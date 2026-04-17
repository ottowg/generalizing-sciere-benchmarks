"""Generate cross-dataset relation performance overview (RE partial).

Produces a matrix of RE partial F1 for each relation label across
train->test dataset pairs on test splits.

Usage:
    python scripts/relation_performance_overview.py
"""

from pathlib import Path
from typing import Literal

import pandas as pd
import yaml

import gsaphub as gh

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]


def _get_f1_column(df: pd.DataFrame) -> object:
    def is_f1_col(col) -> bool:
        if isinstance(col, tuple):
            return any("f1" in str(part).lower() for part in col)
        return "f1" in str(col).lower()

    for col in df.columns:
        if is_f1_col(col):
            return col
    raise ValueError(f"F1 column not found in metrics DataFrame: {list(df.columns)}")


def _get_relation_label_col(df: pd.DataFrame) -> object:
    for col in df.columns:
        if isinstance(col, tuple) and col == ("relation", "label"):
            return col
        if not isinstance(col, tuple) and str(col).lower() == "relation_label":
            return col
    raise ValueError("Relation label column not found in metrics DataFrame.")


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

    rels_gold = [
        relation_to_gsaphub(r, idx, "gold")
        for idx, r in enumerate(gold_corpus.relation)
    ]
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]

    rels_pred = [
        relation_to_gsaphub(r, idx, "pred")
        for idx, r in enumerate(pred_corpus.relations_predicted)
    ]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]

    rels_pred = filter_relations_with_valid_entities(
        rels_pred, {e["id"] for e in ents_pred}
    )
    rels_gold = filter_relations_with_valid_entities(
        rels_gold, {e["id"] for e in ents_gold}
    )
    print(f"{train_ds} {test_ds} {len(rels_gold)} {len(rels_pred)}")
    results = gh.evaluate.relations.precision_recall_f1(
        rels_gold,
        ents_gold,
        rels_pred,
        ents_pred,
        re_metrics=[
            gh.evaluate.relations.RelationExtractionMetric.RELAXED_PARTIAL_MATCH
        ],
        score_types=[gh.evaluate.relations.ScoreType.F1],
        show_counts=False,
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
    output_path = Path("reports/ere_performance/relation_performance_overview.md")
    print("=== Relation Performance Overview (RE partial) ===")
    print(f"Output: {output_path}")
    split = "test"

    mappings_path = (
        Path(__file__).parent.parent.parent
        / "src"
        / "unifiedsciere"
        / "unification"
        / "relation_mappings.yaml"
    )
    relation_mappings = yaml.safe_load(mappings_path.read_text())
    relation_labels = relation_mappings.get("canonical_relations", [])
    relation_labels = list(relation_labels) + ["micro"]

    # Collect metrics per train->test
    metrics_by_pair: dict[tuple[str, str], pd.DataFrame] = {}
    for train_ds in DATASETS:
        for test_ds in DATASETS:
            metrics_by_pair[(train_ds, test_ds)] = _evaluate_pair(
                train_ds, test_ds, split
            )

    # Build table rows
    header = [
        "Label",
        "Train→Test",
        "GSAP",
        "SciER",
        "SciNLP",
    ]
    rows: list[list[str]] = []

    for label in relation_labels:
        for train_ds in DATASETS:
            row = [label, train_ds.upper()]
            values: list[float | None] = []
            for test_ds in DATASETS:
                metrics = metrics_by_pair.get((train_ds, test_ds))
                if metrics is None:
                    values.append(None)
                    continue
                f1_col = _get_f1_column(metrics)
                label_col = _get_relation_label_col(metrics)
                match = metrics[metrics[label_col] == label]
                if match.empty:
                    values.append(None)
                else:
                    values.append(float(match.iloc[0][f1_col]) * 100)
            max_val = max([v for v in values if v is not None], default=None)
            for idx, val in enumerate(values):
                is_diag = DATASETS[idx] == train_ds
                is_max = max_val is not None and val == max_val
                row.append(_format_cell(val, is_diag, is_max))
            rows.append(row)

    df = pd.DataFrame(rows, columns=header)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    md = [
        "# Relation Performance Overview (RE Partial)",
        "",
        f"- Metric: RE partial (relaxed partial match), F1",
        f"- Split: {split}",
        f"- Datasets: {', '.join([d.upper() for d in DATASETS])}",
        "",
        df.to_markdown(index=False),
        "",
    ]
    output_path.write_text("\n".join(md))
    print(f"\n✓ Markdown report written to: {output_path}")


if __name__ == "__main__":
    main()
