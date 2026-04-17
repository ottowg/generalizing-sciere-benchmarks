"""Generate entity performance overview for the majority-vote ensemble model.

For each split (dev, test) and each test dataset (GSAP, SciER, SciNLP, Unified),
combines unified predictions from all three models via majority vote and evaluates
against the gold standard using partial entity matching.

Usage:
    uv run python scripts/ere_performance/ensemble_performance_overview.py
"""

from typing import Literal

import pandas as pd
import yaml

import gsaphub as gh

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.ensemble import majority_vote_ensemble
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


def _get_precision_column(df: pd.DataFrame) -> object | None:
    for col in df.columns:
        if "precision" in str(col).lower():
            return col
    return None


def _load_unified_corpus(train_ds: str, test_ds: str, split: str):
    """Load and unify a single train/test corpus pair."""
    gold_corpus = load_corpus(test_ds, split, data_type="gold")
    pred_corpus = load_corpus(test_ds, split, data_type="predictions", trained_on=train_ds)
    gold_corpus, _ = apply_unification_pipeline(
        gold_corpus, test_ds, apply_to_gold=True, apply_to_predicted=False
    )
    pred_corpus, _ = apply_unification_pipeline(
        pred_corpus, train_ds, apply_to_gold=False, apply_to_predicted=True
    )
    return gold_corpus, pred_corpus


def _evaluate_ensemble_on_test_ds(test_ds: str, split: str) -> pd.DataFrame:
    """Ensemble all three models' predictions on a single test dataset."""
    corpora = []
    for train_ds in DATASETS:
        gold_corpus, pred_corpus = _load_unified_corpus(train_ds, test_ds, split)
        # Attach gold to pred_corpus so ensemble can access it
        pred_corpus.mentions = gold_corpus.mentions
        pred_corpus.relation = gold_corpus.relation
        corpora.append(pred_corpus)

    ensemble_corpus = majority_vote_ensemble(corpora)
    ents_gold = [mention_to_gsaphub(m) for m in corpora[0].mentions]
    ents_pred = [mention_to_gsaphub(m) for m in ensemble_corpus.mentions_predicted]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)


def _evaluate_ensemble_unified(split: str) -> pd.DataFrame:
    """Ensemble all three models on all three datasets combined."""
    all_gold_mentions = []
    all_pred_mentions = []
    for test_ds in DATASETS:
        corpora = []
        for train_ds in DATASETS:
            gold_corpus, pred_corpus = _load_unified_corpus(train_ds, test_ds, split)
            pred_corpus.mentions = gold_corpus.mentions
            pred_corpus.relation = gold_corpus.relation
            corpora.append(pred_corpus)
        ensemble_corpus = majority_vote_ensemble(corpora)
        all_gold_mentions.extend(corpora[0].mentions)
        all_pred_mentions.extend(ensemble_corpus.mentions_predicted)

    ents_gold = [mention_to_gsaphub(m) for m in all_gold_mentions]
    ents_pred = [mention_to_gsaphub(m) for m in all_pred_mentions]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)


def _format_cell(val: float | None, prec: float | None, is_max: bool) -> str:
    if val is None:
        return "NA"
    prec_str = f" ({prec:.1f})" if prec is not None else ""
    text = f"{val:.1f}{prec_str}"
    return f"**{text}**" if is_max else text


def main() -> None:
    splits = ["dev", "test"]

    mappings_path = (
        project_root() / "src" / "unifiedsciere" / "unification" / "label_mappings.yaml"
    )
    label_mappings = yaml.safe_load(mappings_path.read_text())
    labels = list(label_mappings.get("unified_labels", [])) + ["micro"]

    # Pre-compute all metrics
    metrics_by_test: dict[tuple[str, str], pd.DataFrame] = {}
    metrics_unified: dict[str, pd.DataFrame] = {}
    for split in splits:
        for test_ds in DATASETS:
            print(f"Evaluating ensemble: split={split}, test={test_ds}")
            metrics_by_test[(split, test_ds)] = _evaluate_ensemble_on_test_ds(test_ds, split)
        print(f"Evaluating ensemble: split={split}, unified")
        metrics_unified[split] = _evaluate_ensemble_unified(split)

    report = MarkdownReport("Ensemble Performance Overview (Majority Vote, Partial Match)")
    report.bullet_list(
        [
            "Metric: entity partial match, F1 (Precision)",
            "Method: majority vote across all three models (GSAP, SciER, SciNLP)",
            f"Splits: {', '.join(splits)}",
            f"Datasets: {', '.join(d.upper() for d in DATASETS)}",
        ]
    )

    for split in splits:
        header = [
            "Label",
            f"GSAP ({split})",
            f"SciER ({split})",
            f"SciNLP ({split})",
            f"Unified ({split})",
        ]
        rows: list[list[str]] = []

        for label in labels:
            values: list[float | None] = []
            precs: list[float | None] = []
            for test_ds in DATASETS:
                metrics = metrics_by_test.get((split, test_ds))
                if metrics is None:
                    values.append(None)
                    precs.append(None)
                    continue
                f1_col = _get_f1_column(metrics)
                prec_col = _get_precision_column(metrics)
                match = metrics[metrics["label"] == label]
                if match.empty:
                    values.append(None)
                    precs.append(None)
                else:
                    values.append(float(match.iloc[0][f1_col]) * 100)
                    precs.append(float(match.iloc[0][prec_col]) * 100 if prec_col is not None else None)
            # Unified column
            unified = metrics_unified.get(split)
            if unified is not None:
                f1_col = _get_f1_column(unified)
                prec_col = _get_precision_column(unified)
                match = unified[unified["label"] == label]
                if not match.empty:
                    values.append(float(match.iloc[0][f1_col]) * 100)
                    precs.append(float(match.iloc[0][prec_col]) * 100 if prec_col is not None else None)
                else:
                    values.append(None)
                    precs.append(None)
            else:
                values.append(None)
                precs.append(None)

            max_val = max([v for v in values if v is not None], default=None)
            row = [label] + [
                _format_cell(v, p, max_val is not None and v == max_val)
                for v, p in zip(values, precs)
            ]
            rows.append(row)

        df = pd.DataFrame(rows, columns=header)
        report.heading(f"Split: {split}", level=2)
        report.table(df)

    report.write("reports/ere_performance/ensemble_performance_overview.md")


if __name__ == "__main__":
    main()
