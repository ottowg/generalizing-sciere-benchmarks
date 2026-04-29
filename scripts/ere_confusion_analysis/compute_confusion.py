"""Compute entity and relation confusion matrices between two annotation sources.

Writes JSON to --output file (stdout is left for any print() noise from imports).

Usage:
    uv run python scripts/ere_confusion_analysis/compute_confusion.py \
        --dataset gsap-ere --split dev --annot1 gold --annot2 gsap-ere \
        --labelset unified --output data/confusion_matrices/gsap-ere_dev_gold_gsap-ere_unified.json
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from gsaphub.match.entities import partial as partial_match
from gsaphub.match.relations import get_matches_bidirectional as _match_relations

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import mention_to_gsaphub, relation_to_gsaphub
from unifiedsciere.unification.pipeline import apply_unification_pipeline

VALID_ANNOTATIONS = ["gold", "gsap-ere", "scier", "scinlp"]
VALID_DATASETS    = ["gsap-ere", "scier", "scinlp"]
VALID_SPLITS      = ["train", "dev", "test"]
VALID_LABELSETS   = ["unified", "original"]


def load_data(dataset: str, split: str, annot: str, labelset: str):
    if annot == "gold":
        corpus = load_corpus(dataset, split, data_type="gold")
        if labelset == "unified":
            corpus, _ = apply_unification_pipeline(
                corpus, dataset, apply_to_gold=True, apply_to_predicted=False
            )
        return corpus.mentions, corpus.relation
    else:
        corpus = load_corpus(dataset, split, data_type="predictions", trained_on=annot)
        if labelset == "unified":
            corpus, _ = apply_unification_pipeline(
                corpus, annot, apply_to_gold=False, apply_to_predicted=True
            )
        return corpus.mentions_predicted, corpus.relations_predicted


def to_fmt(mentions):
    return [{"id": m.id, "doc_id": m.document_id, "begin": m.begin, "end": m.end, "label": m.label} for m in mentions]


def compute_entity_confusion(mentions1, mentions2) -> dict:
    fmt1 = to_fmt(mentions1)
    fmt2 = to_fmt(mentions2)

    partial_match(fmt1, fmt2, target_key="matched", only_same_annotator=False)
    by_id2 = {m["id"]: m for m in fmt2}

    confusion: dict = defaultdict(lambda: defaultdict(int))
    for m in fmt1:
        matched = m.get("matched", [])
        if not matched:
            confusion[m["label"]]["NIL"] += 1
        else:
            confusion[m["label"]][by_id2[matched[0]]["label"]] += 1

    partial_match(fmt2, fmt1, target_key="matched", only_same_annotator=False)
    for m in fmt2:
        if not m.get("matched", []):
            confusion["NIL"][m["label"]] += 1

    return {r: dict(c) for r, c in confusion.items()}


def compute_relation_confusion(mentions1, relations1, mentions2, relations2) -> dict:
    ents1 = [mention_to_gsaphub(m) for m in mentions1]
    ents2 = [mention_to_gsaphub(m) for m in mentions2]
    rels1 = [relation_to_gsaphub(r, i, "annot1") for i, r in enumerate(relations1)]
    rels2 = [relation_to_gsaphub(r, i, "annot2") for i, r in enumerate(relations2)]

    matches, not_matched = _match_relations(rels1, ents1, rels2, ents2)

    confusion: dict = defaultdict(lambda: defaultdict(int))
    for m in matches:
        confusion[m["relation_label"]][m["relation_match_label"]] += 1
    for m in not_matched:
        confusion["NIL"][m["relation_label"]] += 1

    return {r: dict(c) for r, c in confusion.items()}


def to_matrix(confusion: dict) -> dict:
    row_labels = sorted(k for k in confusion if k != "NIL")
    col_set: set = set()
    for row in confusion.values():
        col_set.update(row.keys())
    col_labels = sorted(c for c in col_set if c != "NIL")

    if "NIL" in confusion:
        row_labels.append("NIL")
    if "NIL" in col_set:
        col_labels.append("NIL")

    matrix = []
    totals1: dict = {}
    for r in row_labels:
        row_data = confusion.get(r, {})
        row = [row_data.get(c, 0) for c in col_labels]
        matrix.append(row)
        totals1[r] = sum(row_data.values())

    totals2: dict = {}
    for c in col_labels:
        totals2[c] = sum(confusion.get(r, {}).get(c, 0) for r in row_labels)

    return {
        "labels_annot1": row_labels,
        "labels_annot2": col_labels,
        "matrix": matrix,
        "totals_annot1": totals1,
        "totals_annot2": totals2,
    }


def compute(dataset: str, split: str, annot1: str, annot2: str, labelset: str) -> dict:
    mentions1, relations1 = load_data(dataset, split, annot1, labelset)
    mentions2, relations2 = load_data(dataset, split, annot2, labelset)

    return {
        "entities":  to_matrix(compute_entity_confusion(mentions1, mentions2)),
        "relations": to_matrix(compute_relation_confusion(mentions1, relations1, mentions2, relations2)),
        "params": {"dataset": dataset, "split": split, "annot1": annot1, "annot2": annot2, "labelset": labelset},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset",  required=True, choices=VALID_DATASETS)
    parser.add_argument("--split",    required=True, choices=VALID_SPLITS)
    parser.add_argument("--annot1",   required=True, choices=VALID_ANNOTATIONS)
    parser.add_argument("--annot2",   required=True, choices=VALID_ANNOTATIONS)
    parser.add_argument("--labelset", required=True, choices=VALID_LABELSETS)
    parser.add_argument("--output",   required=True)
    args = parser.parse_args()

    result = compute(args.dataset, args.split, args.annot1, args.annot2, args.labelset)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result))
    print(f"Written: {out}", flush=True)


if __name__ == "__main__":
    main()
