"""Build example papers data for the webapp.

Picks N random papers from each test set. For each paper, captures:
  - gold annotations (original labels + unified labels)
  - predictions from all 3 models (original labels + unified labels each)

Usage:
    uv run python scripts/ere_quality/build_example_papers.py
    uv run python scripts/ere_quality/build_example_papers.py --n 5 --seed 42
"""

import argparse
import json
import random

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import ensure_output, project_root
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS = ["gsap-ere", "scier", "scinlp"]


def load_paper_metadata() -> dict:
    """Load all_papers.jsonl and return a dict keyed by doc_id."""
    path = project_root() / "data" / "metadata" / "unified" / "all_papers.jsonl"
    meta = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                meta[obj["doc_id"]] = obj
            except Exception:
                pass
    return meta


def extract_paper_data(corpus, doc_id: str, use_predicted: bool) -> dict:
    """Extract deduplicated entities and relations for one document."""
    if use_predicted:
        mentions  = [m for m in corpus.mentions_predicted if m.document_id == doc_id]
        relations = [r for r in corpus.relations_predicted if r.document_id == doc_id]
    else:
        mentions  = [m for m in corpus.mentions if m.document_id == doc_id]
        relations = [r for r in corpus.relation  if r.document_id == doc_id]

    ent_counts: dict[tuple, int] = {}
    for m in mentions:
        key = (m.text, m.label)
        ent_counts[key] = ent_counts.get(key, 0) + 1

    entities = [
        {"id": f"{text}|{label}", "text": text, "label": label, "count": cnt}
        for (text, label), cnt in ent_counts.items()
    ]

    rel_counts: dict[tuple, int] = {}
    for r in relations:
        subj_id = f"{r.subject.text}|{r.subject.label}"
        obj_id  = f"{r.object.text}|{r.object.label}"
        key     = (subj_id, r.label, obj_id)
        rel_counts[key] = rel_counts.get(key, 0) + 1

    rels = [
        {"subject_id": subj_id, "label": rel_label, "object_id": obj_id, "count": cnt}
        for (subj_id, rel_label, obj_id), cnt in rel_counts.items()
    ]

    return {"entities": entities, "relations": rels}


def process_dataset(dataset: str, n: int, rng: random.Random, paper_meta: dict) -> list[dict]:
    print(f"  {dataset} …")

    # ── Gold ──────────────────────────────────────────────────────────────────
    gold = load_corpus(dataset, "test", data_type="gold")
    doc_ids  = sorted({s.doc_id for s in gold.sentences})
    selected = rng.sample(doc_ids, min(n, len(doc_ids)))

    sentences_map = {}
    for doc_id in selected:
        sents = sorted(
            [s for s in gold.sentences if s.doc_id == doc_id], key=lambda s: s.idx
        )
        sentences_map[doc_id] = [s.text for s in sents]

    # Extract original gold BEFORE applying unification
    orig_gold = {doc_id: extract_paper_data(gold, doc_id, False) for doc_id in selected}
    # Apply unification in-place, then extract unified gold
    gold, _ = apply_unification_pipeline(gold, dataset, apply_to_gold=True, apply_to_predicted=False)
    unif_gold = {doc_id: extract_paper_data(gold, doc_id, False) for doc_id in selected}

    # ── Predictions from all 3 models ─────────────────────────────────────────
    all_preds: dict[str, dict] = {}
    for trained_on in DATASETS:
        print(f"    predictions trained_on={trained_on} …")
        try:
            pred = load_corpus(dataset, "test", data_type="predictions", trained_on=trained_on)
            # Extract original predictions BEFORE unification
            orig_pred = {doc_id: extract_paper_data(pred, doc_id, True) for doc_id in selected}
            # Apply unification using trained_on scheme, then extract unified
            pred, _ = apply_unification_pipeline(pred, trained_on, apply_to_gold=False, apply_to_predicted=True)
            unif_pred = {doc_id: extract_paper_data(pred, doc_id, True) for doc_id in selected}
            all_preds[trained_on] = {
                doc_id: {"original": orig_pred[doc_id], "unified": unif_pred[doc_id]}
                for doc_id in selected
            }
        except Exception as e:
            print(f"    Warning: predictions unavailable (trained_on={trained_on}): {e}")
            empty = {"entities": [], "relations": []}
            all_preds[trained_on] = {doc_id: {"original": empty, "unified": empty} for doc_id in selected}

    # ── Assemble papers ───────────────────────────────────────────────────────
    papers = []
    for doc_id in selected:
        m = paper_meta.get(doc_id, {})
        metadata = {
            "title":     m.get("title", ""),
            "authors":   m.get("authors", []),
            "year":      m.get("year", None),
            "venue":     m.get("venue", ""),
            "outlet_id": m.get("outlet_id", ""),
        }
        ug = unif_gold[doc_id]
        print(
            f"    {doc_id[:50]}: "
            f"{len(ug['entities'])}e/{len(ug['relations'])}r gold unified"
        )
        papers.append({
            "doc_id":      doc_id,
            "dataset":     dataset,
            "metadata":    metadata,
            "sentences":   sentences_map[doc_id],
            "gold": {
                "original": orig_gold[doc_id],
                "unified":  unif_gold[doc_id],
            },
            "predictions": {
                trained_on: all_preds[trained_on][doc_id]
                for trained_on in DATASETS
            },
        })

    return papers


def main() -> None:
    parser = argparse.ArgumentParser(description="Build example papers for webapp.")
    parser.add_argument("--n",    type=int, default=5,  help="Papers per dataset")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    print("=== Building example papers ===")
    paper_meta = load_paper_metadata()
    print(f"  Loaded metadata for {len(paper_meta)} papers")

    result: dict = {"papers": {}}
    for dataset in DATASETS:
        result["papers"][dataset] = process_dataset(dataset, args.n, rng, paper_meta)

    out_path = ensure_output("data/webapp/example_papers.json")
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nWritten {sum(len(v) for v in result['papers'].values())} papers → {out_path}")


if __name__ == "__main__":
    main()
