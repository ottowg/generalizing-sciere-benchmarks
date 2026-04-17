"""Generate the unified UnifiedSciERE dataset.

Loads gold annotations for all three source datasets (gsap-ere, scier, scinlp),
applies the unification pipeline to each, then combines and shuffles to produce
split-level output files.

Output files:
  data/unified/unified_train.jsonl  — all three train sets combined, shuffled
  data/unified/unified_dev.jsonl    — all three dev sets combined, shuffled
  data/unified/unified_test.jsonl   — all three test sets combined, shuffled

Each document has:
  doc_id            — original document identifier
  original_dataset  — source dataset ("gsap-ere", "scier", "scinlp")
  sentences         — list of token lists, one per sentence
  ner               — list of [[begin_token, end_token, label], ...] per sentence
  relations         — list of [[s_begin, s_end, o_begin, o_end, label], ...] per sentence

Usage:
    uv run python scripts/create_unified_dataset.py
"""

import json
import os
import random
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import ensure_output, project_root
from unifiedsciere.unification.pipeline import apply_unification_pipeline

load_dotenv()

DATASETS = ["gsap-ere", "scier", "scinlp"]
SPLITS = ["train", "dev", "test"]
SEED = 42


# ── raw document loading ───────────────────────────────────────────────────────

def _load_raw_docs(dataset: str, split: str) -> list[dict]:
    """Load raw JSONL documents, normalising the document key."""
    data_folder = os.getenv("DATA_GOLD_FOLDER", "data/gold")
    data_path = Path(data_folder)
    if not data_path.is_absolute():
        data_path = project_root() / data_path

    filename = f"{dataset}_{split}.jsonl"
    docs = []
    with open(data_path / filename) as fh:
        for line in fh:
            doc = json.loads(line)
            # Normalise: every doc gets a "_key" used for lookup
            if "doc_key" in doc:
                doc["_key"] = doc["doc_key"]
            elif "doc_id" in doc:
                doc["_key"] = doc["doc_id"]
            else:
                raise ValueError(f"Document in {filename} has neither doc_id nor doc_key")
            docs.append(doc)
    return docs


# ── annotation maps from unified corpus ───────────────────────────────────────

def _build_annotation_maps(corpus):
    """Return (ner_map, rel_map) indexed by (doc_id, sent_idx).

    ner_map[doc_id][sent_idx] = [[begin_token, end_token, label], ...]
    rel_map[doc_id][sent_idx] = [[s_begin, s_end, o_begin, o_end, label], ...]
    """
    ner_map: dict[str, dict[int, list]] = defaultdict(lambda: defaultdict(list))
    for mention in corpus.mentions:
        ner_map[mention.document_id][mention.sent_idx].append(
            [mention.begin_token, mention.end_token, mention.label]
        )

    rel_map: dict[str, dict[int, list]] = defaultdict(lambda: defaultdict(list))
    for relation in corpus.relation:
        rel_map[relation.document_id][relation.sent_idx].append(
            [
                relation.subject.begin_token,
                relation.subject.end_token,
                relation.object.begin_token,
                relation.object.end_token,
                relation.label,
            ]
        )

    return ner_map, rel_map


# ── document assembly ─────────────────────────────────────────────────────────

def _assemble_docs(raw_docs: list[dict], ner_map, rel_map, dataset_name: str) -> list[dict]:
    """Merge unified annotations back into the raw document structure."""
    result = []
    for doc in raw_docs:
        key = doc["_key"]
        n_sents = len(doc["sentences"])

        unified_ner = [ner_map[key].get(i, []) for i in range(n_sents)]
        unified_rel = [rel_map[key].get(i, []) for i in range(n_sents)]

        out = {
            "doc_id": key,
            "original_dataset": dataset_name,
            "sentences": doc["sentences"],
            "ner": unified_ner,
            "relations": unified_rel,
        }
        result.append(out)

    return result


# ── per-dataset pipeline ───────────────────────────────────────────────────────

def process_dataset_split(dataset: str, split: str) -> list[dict]:
    """Load, unify, and assemble documents for one dataset+split."""
    print(f"  Loading {dataset} {split} …")
    raw_docs = _load_raw_docs(dataset, split)

    corpus = load_corpus(dataset, split, data_type="gold")
    corpus, stats = apply_unification_pipeline(
        corpus, dataset, apply_to_gold=True, apply_to_predicted=False
    )

    merged = stats.get("merge", {}).get("gold_merged", 0)
    dropped = stats.get("drop", {}).get("gold_mentions_dropped", 0)
    mapped = stats.get("map", {}).get("gold_mentions_mapped", 0)
    print(
        f"    → {len(raw_docs)} docs | "
        f"merged {merged}, dropped {dropped}, mapped {mapped} mentions"
    )

    ner_map, rel_map = _build_annotation_maps(corpus)
    return _assemble_docs(raw_docs, ner_map, rel_map, dataset)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    rng = random.Random(SEED)

    for split in SPLITS:
        print(f"\n=== {split} ===")
        all_docs: list[dict] = []

        for dataset in DATASETS:
            docs = process_dataset_split(dataset, split)
            all_docs.extend(docs)

        rng.shuffle(all_docs)

        out_path = ensure_output(f"data/unified/unified_{split}.jsonl")
        with open(out_path, "w") as fh:
            for doc in all_docs:
                fh.write(json.dumps(doc, ensure_ascii=False) + "\n")

        total_ner = sum(len(ent) for doc in all_docs for ent in doc["ner"])
        total_rel = sum(len(rel) for doc in all_docs for rel in doc["relations"])
        print(
            f"  Written {len(all_docs)} docs, "
            f"{total_ner} mentions, {total_rel} relations → {out_path}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
