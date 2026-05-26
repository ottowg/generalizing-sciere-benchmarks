"""Build annotation lookup files for the webapp annotation review feature.

For each trained_on × dataset × split combination found in DATA_PREDICTIONS_FOLDER,
loads gold and predictions via load_corpus, computes per-sample TP/FP/FN outcomes,
and writes structured JSON lookups to:

    data/annotation_lookup/{trained_on}_{dataset}_{split}.json          (original labels)
    data/annotation_lookup/{trained_on}_{dataset}_{split}_unified.json  (unified labels)

Each file contains flat lists of mention and relation samples, each annotated with
their outcome (tp/fp/fn), label, confidence score, span text, and sentence context.
These files are queried by the server API to serve annotation review samples.

Usage:
    uv run scripts/ere_performance/build_annotation_lookup.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import project_root
from unifiedsciere.types import Corpus, Mention, Relation
from unifiedsciere.unification.pipeline import apply_unification_pipeline

load_dotenv()

DATASETS = {"gsap-ere", "scier", "scinlp"}
SPLITS = {"train", "dev", "test"}

OUTPUT_DIR = project_root() / "data" / "webapp" / "annotation_lookup"


# ── helpers ───────────────────────────────────────────────────────────────────

def sent_key(doc_id: str, sent_idx) -> str:
    return f"{doc_id} {sent_idx}"


def mention_key(m: Mention) -> tuple:
    return (m.document_id, m.begin_token, m.end_token, m.label)


def relation_key(r: Relation) -> tuple:
    return (
        r.document_id,
        r.sent_idx,
        r.subject.begin_token,
        r.subject.end_token,
        r.label,
        r.object.begin_token,
        r.object.end_token,
    )


def mention_sample(m: Mention, outcome: str, sentence: str) -> dict:
    return {
        "id": m.id,
        "outcome": outcome,
        "label": m.label,
        "split": m.split,
        "score": round(m.score, 4),
        "text": m.text,
        "sentence": sentence,
        "doc_id": m.document_id,
        "sent_idx": m.sent_idx,
        "begin_token": m.begin_token,
        "end_token": m.end_token,
    }


def relation_sample(r: Relation, outcome: str, sentence: str, context_spans: list) -> dict:
    key = relation_key(r)
    rid = " ".join(str(k) for k in key)
    return {
        "id": rid,
        "outcome": outcome,
        "label": r.label,
        "score": round(r.score, 4),
        "subject": {
            "text": r.subject.text,
            "label": r.subject.label,
            "begin_token": r.subject.begin_token,
            "end_token": r.subject.end_token,
        },
        "object": {
            "text": r.object.text,
            "label": r.object.label,
            "begin_token": r.object.begin_token,
            "end_token": r.object.end_token,
        },
        "context_spans": context_spans,
        "sentence": sentence,
        "split": r.split,
        "doc_id": r.document_id,
        "sent_idx": r.sent_idx,
    }


# ── core builder ──────────────────────────────────────────────────────────────

def _build_from_corpus(corpus: Corpus, trained_on: str, dataset: str, split: str) -> dict:
    """Build a lookup dict from an already-loaded (and optionally unified) corpus."""
    sentences = {sent_key(s.doc_id, s.idx): s.text for s in corpus.sentences}

    # ── Mentions ──────────────────────────────────────────────────────────────
    gold_mention_keys = {mention_key(m) for m in corpus.mentions}
    pred_mention_keys = {mention_key(m) for m in corpus.mentions_predicted}
    gold_by_key = {mention_key(m): m for m in corpus.mentions}
    pred_by_key = {mention_key(m): m for m in corpus.mentions_predicted}

    mention_samples = []
    for key, m in pred_by_key.items():
        outcome = "tp" if key in gold_mention_keys else "fp"
        mention_samples.append(mention_sample(m, outcome, sentences.get(sent_key(m.document_id, m.sent_idx), "")))
    for key, m in gold_by_key.items():
        if key not in pred_mention_keys:
            mention_samples.append(mention_sample(m, "fn", sentences.get(sent_key(m.document_id, m.sent_idx), "")))

    # Gold mentions indexed by sentence for context span rendering
    gold_mentions_by_sent: dict[tuple, list] = {}
    for m in corpus.mentions:
        gold_mentions_by_sent.setdefault((m.document_id, str(m.sent_idx)), []).append(m)

    def context_spans_for(r: Relation) -> list:
        all_mentions = gold_mentions_by_sent.get((r.document_id, str(r.sent_idx)), [])
        return [
            {"text": m.text, "label": m.label, "begin_token": m.begin_token, "end_token": m.end_token}
            for m in all_mentions
            if not (m.begin_token == r.subject.begin_token and m.end_token == r.subject.end_token)
            and not (m.begin_token == r.object.begin_token and m.end_token == r.object.end_token)
        ]

    # ── Relations ─────────────────────────────────────────────────────────────
    gold_relation_keys = {relation_key(r) for r in corpus.relation}
    pred_relation_keys = {relation_key(r) for r in corpus.relations_predicted}
    gold_rel_by_key = {relation_key(r): r for r in corpus.relation}
    pred_rel_by_key = {relation_key(r): r for r in corpus.relations_predicted}

    relation_samples = []
    for key, r in pred_rel_by_key.items():
        outcome = "tp" if key in gold_relation_keys else "fp"
        relation_samples.append(relation_sample(r, outcome, sentences.get(sent_key(r.document_id, r.sent_idx), ""), context_spans_for(r)))
    for key, r in gold_rel_by_key.items():
        if key not in pred_relation_keys:
            relation_samples.append(relation_sample(r, "fn", sentences.get(sent_key(r.document_id, r.sent_idx), ""), context_spans_for(r)))

    return {
        "meta": {"trained_on": trained_on, "dataset": dataset, "split": split},
        "mentions": mention_samples,
        "relations": relation_samples,
    }


def build_lookup(trained_on: str, dataset: str, split: str) -> dict:
    """Build original-label lookup for a trained_on × dataset × split combination."""
    corpus = load_corpus(dataset, split, data_type="predictions", trained_on=trained_on)
    return _build_from_corpus(corpus, trained_on, dataset, split)


def build_unified_lookup(trained_on: str, dataset: str, split: str) -> dict:
    """Build unified-label lookup for a trained_on × dataset × split combination.

    Unification is applied per origin:
    - Gold annotations are unified using the dataset's own scheme.
    - Predicted annotations are unified using the trained_on (model) scheme.
    """
    corpus = load_corpus(dataset, split, data_type="predictions", trained_on=trained_on)
    corpus, _ = apply_unification_pipeline(corpus, dataset, apply_to_gold=True, apply_to_predicted=False)
    corpus, _ = apply_unification_pipeline(corpus, trained_on, apply_to_gold=False, apply_to_predicted=True)
    return _build_from_corpus(corpus, trained_on, dataset, split)


# ── main ──────────────────────────────────────────────────────────────────────

def discover_combinations() -> list[tuple[str, str, str]]:
    """Scan datasets directory structure to discover valid trained_on × dataset × split combos."""
    from unifiedsciere.data_loader import TRAINED_ON_ALIASES

    datasets_folder = os.getenv("DATA_DATASETS_FOLDER")
    if not datasets_folder:
        raise ValueError("DATA_DATASETS_FOLDER not set in .env")
    datasets_root = Path(datasets_folder)
    if not datasets_root.is_absolute():
        datasets_root = project_root() / datasets_root

    combos = []
    for dataset_dir in sorted(datasets_root.iterdir()):
        if not dataset_dir.is_dir() or dataset_dir.name not in DATASETS:
            continue
        dataset = dataset_dir.name
        for pred_dir in sorted(dataset_dir.iterdir()):
            if not pred_dir.is_dir() or not pred_dir.name.startswith("pred_"):
                continue
            raw_trained_on = pred_dir.name[len("pred_"):]
            trained_on = TRAINED_ON_ALIASES.get(raw_trained_on, raw_trained_on)
            if trained_on not in DATASETS:
                continue
            for split_file in sorted(pred_dir.glob("*.jsonl")):
                if split_file.stem in SPLITS:
                    combos.append((trained_on, dataset, split_file.stem))
    return combos


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combos = discover_combinations()
    print(f"Found {len(combos)} combinations to process\n")

    for trained_on, dataset, split in combos:
        label = f"{trained_on}_{dataset}_{split}"

        for variant, builder, suffix in [
            ("original", build_lookup,         ""),
            ("unified",  build_unified_lookup, "_unified"),
        ]:
            out_path = OUTPUT_DIR / f"{label}{suffix}.json"
            print(f"  Building {label}{suffix} ({variant}) ...", end=" ", flush=True)
            try:
                lookup = builder(trained_on, dataset, split)
                n_m = len(lookup["mentions"])
                n_r = len(lookup["relations"])
                out_path.write_text(json.dumps(lookup, ensure_ascii=False))
                print(f"{n_m} mention samples, {n_r} relation samples → {out_path.relative_to(project_root())}")
            except Exception as e:
                print(f"ERROR: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
