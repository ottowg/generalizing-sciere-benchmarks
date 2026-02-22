"""Report false predictions for relation types on unified GSAP test set.

This script matches gold and predicted relations using gsaphub partial matching
and reports false positives/negatives for each unified relation label.

Usage:
    python scripts/false_predictions_report.py
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import gsaphub as gh
import pandas as pd
import yaml

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.unification.pipeline import apply_unification_pipeline


def _mention_to_gsaphub_annotated(m, annotator: str) -> dict[str, object]:
    d = mention_to_gsaphub(m)
    d["annotator"] = annotator
    return d


def _relation_to_gsaphub_annotated(r, idx: int, annotator: str) -> dict[str, object]:
    d = relation_to_gsaphub(r, idx)
    d["score"] = r.score
    d["annotator"] = annotator
    d["url_inception"] = ""
    d["text_unit_text"] = ""
    return d


def main():
    print("=== False Predictions Report ===")

    datasets = ["gsap", "scier", "scinlp"]
    split = "test"

    mappings_path = (
        Path(__file__).parent.parent
        / "src"
        / "unifiedsciere"
        / "unification"
        / "relation_mappings.yaml"
    )
    relation_mappings = yaml.safe_load(mappings_path.read_text())
    relation_labels = relation_mappings.get("canonical_relations", [])

    def _sample_indices(rel_ids, rels, sample_size):
        type_to_indices = {"Method": [], "Task": [], "Dataset": []}
        for rel_id in rel_ids:
            rel = rels[rel_id]
            ent_type = rel.subject.label
            if ent_type in type_to_indices:
                type_to_indices[ent_type].append(rel_id)
        sampled = {}
        for ent_type, indices in type_to_indices.items():
            if len(indices) <= sample_size:
                sampled[ent_type] = indices
            else:
                sampled[ent_type] = random.sample(indices, sample_size)
        return sampled

    random.seed(13)

    for dataset in datasets:
        trained_on = dataset
        output_dir = Path("reports/ere_performance/false_predictions") / dataset
        output_dir.mkdir(parents=True, exist_ok=True)

        gold_corpus = load_corpus(dataset, split, data_type="gold")
        pred_corpus = load_corpus(
            dataset, split, data_type="predictions", trained_on=trained_on
        )

        gold_corpus, _ = apply_unification_pipeline(
            gold_corpus, dataset, apply_to_gold=True, apply_to_predicted=False
        )
        pred_corpus, _ = apply_unification_pipeline(
            pred_corpus, dataset, apply_to_gold=False, apply_to_predicted=True
        )

        rels_gold_all = [
            _relation_to_gsaphub_annotated(r, idx, "gold")
            for idx, r in enumerate(gold_corpus.relation)
        ]
        ents_gold = [_mention_to_gsaphub_annotated(m, "gold") for m in gold_corpus.mentions]

        rels_pred_all = [
            _relation_to_gsaphub_annotated(r, idx, "gsap_predictions")
            for idx, r in enumerate(pred_corpus.relations_predicted)
        ]
        ents_pred = [
            _mention_to_gsaphub_annotated(m, "gsap_predictions")
            for m in pred_corpus.mentions_predicted
        ]

        gold_ent_ids = {e["id"] for e in ents_gold}
        pred_ent_ids = {e["id"] for e in ents_pred}
        rels_gold_all = filter_relations_with_valid_entities(
            rels_gold_all, gold_ent_ids
        )
        rels_pred_all = filter_relations_with_valid_entities(
            rels_pred_all, pred_ent_ids
        )

        for relation_label in relation_labels:
            print(f"Generating report for {dataset}:{relation_label}")
            output_path = output_dir / f"{relation_label}_false_predictions.md"

            rels_gold = [
                r for r in rels_gold_all if r["relation_label"] == relation_label
            ]
            rels_pred = [
                r for r in rels_pred_all if r["relation_label"] == relation_label
            ]

            _ = gh.match.relations.partial(rels_gold, ents_gold, rels_pred, ents_pred)

            false_pos_indices = []
            true_pos_indices = []
            for rel in rels_pred:
                best_match = rel["all_matches"][0] if rel["all_matches"] else None
                relation_match_type = (
                    best_match["relation_match_type"] if best_match else "NIL"
                )
                if relation_match_type == "same":
                    true_pos_indices.append(rel["id"])
                elif relation_match_type == "NIL":
                    false_pos_indices.append(rel["id"])

            false_neg_indices = []
            for rel in rels_gold:
                best_match = rel["all_matches"][0] if rel["all_matches"] else None
                relation_match_type = (
                    best_match["relation_match_type"] if best_match else "NIL"
                )
                if relation_match_type == "NIL":
                    false_neg_indices.append(rel["id"])

            fp_samples = _sample_indices(
                false_pos_indices, pred_corpus.relations_predicted, 5
            )
            fn_samples = _sample_indices(false_neg_indices, gold_corpus.relation, 5)

            md_parts = [
                f"# {relation_label} False Predictions (Unified {dataset.upper()} Test)",
                "",
                f"Dataset: {dataset}",
                f"Split: {split}",
                f"Trained on: {trained_on}",
                "",
                f"Total predicted relations: {len(rels_pred)}",
                f"Total gold relations: {len(rels_gold)}",
                f"True positive predictions: {len(true_pos_indices)}",
                f"False positive predictions: {len(false_pos_indices)}",
                f"False negative predictions: {len(false_neg_indices)}",
                "",
            ]

            md_parts.append("## False Positives")
            md_parts.append("")
            for ent_type in ("Method", "Task", "Dataset"):
                md_parts.append(f"### {ent_type}")
                md_parts.append("")
                indices = fp_samples.get(ent_type, [])
                if not indices:
                    md_parts.append("No false positives found.")
                    md_parts.append("")
                    continue
                for rel_idx in indices:
                    formatted = pred_corpus.format_relation(rel_idx, predicted=True)
                    md_parts.append(f"- {formatted.replace(chr(10), '<br><br>')}")
                md_parts.append("")

            md_parts.append("## False Negatives")
            md_parts.append("")
            for ent_type in ("Method", "Task", "Dataset"):
                md_parts.append(f"### {ent_type}")
                md_parts.append("")
                indices = fn_samples.get(ent_type, [])
                if not indices:
                    md_parts.append("No false negatives found.")
                    md_parts.append("")
                    continue
                for rel_idx in indices:
                    formatted = gold_corpus.format_relation(rel_idx, predicted=False)
                    md_parts.append(f"- {formatted.replace(chr(10), '<br><br>')}")
                md_parts.append("")

            output_path.write_text("
".join(md_parts))
            print(f"✓ Markdown report written to: {output_path}")

if __name__ == "__main__":
    main()

    main()
