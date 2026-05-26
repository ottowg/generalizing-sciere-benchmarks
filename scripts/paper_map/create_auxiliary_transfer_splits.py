"""Create dataset splits for the auxiliary transfer domain-shift experiment.

Splits SciER by NLP / non-NLP domain (cluster_meta_2 from paper_map.parquet):
  - Cluster 1  = NLP domain
  - Cluster 0  = non-NLP domain
  - Cluster -1 = outlier (treated as NLP for SciER, as non-NLP for GSAP-ERE)

Output JSONL files (written to DATA_DATASETS_FOLDER):
  domain-shift-scier/
    train.jsonl          66 non-NLP SciER docs (shuffled by document)
    dev.jsonl            10 non-NLP SciER docs (shuffled by document)
    test.jsonl           22 NLP SciER docs (24 minus 2 excluded due to GSAP-ERE leakage)

  domain-shift-gsap-ere-auxiliary/
    train_non_nlp.jsonl  46 non-NLP GSAP-ERE docs (all available, shuffled)
    train_nlp.jsonl      46 NLP GSAP-ERE docs (sampled from 54 available, shuffled)
    train_mixed.jsonl    23 NLP + 23 non-NLP GSAP-ERE docs (shuffled)

JSON manifest for webapp:
  data/webapp/static/auxiliary_transfer_docs.json

Usage:
    uv run python scripts/paper_map/create_auxiliary_transfer_splits.py
"""

import json
import random
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
import os

from unifiedsciere.paths import project_root

SEED = 42

# SciER documents excluded from the test set due to data leakage:
# both appear verbatim in the GSAP-ERE NLP auxiliary data.
SCIER_TEST_EXCLUSIONS: set[str] = {
    "201646309",  # Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
    "201646244",  # FinBERT: Financial Sentiment Analysis with Pre-trained Language Models
}

ROOT = project_root()
load_dotenv(ROOT / ".env")

DATA_DATASETS_FOLDER = Path(os.environ["DATA_DATASETS_FOLDER"])
PAPER_MAP_PARQUET = ROOT / "data" / "webapp" / "publication_map" / "paper_map.parquet"
METADATA_JSONL = ROOT / "data" / "metadata" / "unified" / "all_papers.jsonl"
MANIFEST_OUT = ROOT / "data" / "webapp" / "static" / "auxiliary_transfer_docs.json"


def load_cluster_map() -> dict[str, int]:
    """Return {doc_id -> cluster_meta_2} from paper_map.parquet."""
    df = pd.read_parquet(PAPER_MAP_PARQUET)
    return {str(row.doc_id): int(row.cluster_meta_2) for row in df.itertuples()}


def load_metadata() -> dict[str, dict]:
    """Return {doc_id -> metadata_record} from all_papers.jsonl."""
    metadata = {}
    with open(METADATA_JSONL) as f:
        for line in f:
            rec = json.loads(line)
            metadata[str(rec["doc_id"])] = rec
    return metadata


def load_ere_docs(dataset: str, split: str) -> list[dict]:
    """Load all ERE records from DATA_DATASETS_FOLDER/{dataset}/{split}.jsonl."""
    path = DATA_DATASETS_FOLDER / dataset / f"{split}.jsonl"
    docs = []
    with open(path) as f:
        for line in f:
            docs.append(json.loads(line))
    return docs


def write_jsonl(docs: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for doc in docs:
            f.write(json.dumps(doc) + "\n")
    print(f"  Wrote {len(docs):3d} docs → {path.relative_to(DATA_DATASETS_FOLDER)}")


def shuffle_docs(docs: list[dict], seed: int) -> list[dict]:
    """Return a copy of docs shuffled with the given seed."""
    rng = random.Random(seed)
    shuffled = list(docs)
    rng.shuffle(shuffled)
    return shuffled


def build_scier_splits(
    cluster_map: dict[str, int],
    metadata: dict[str, dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Return (nlp_docs, non_nlp_train, non_nlp_dev, non_nlp_test_orig).

    nlp_docs       — all SciER NLP docs (cluster=1 or outlier -1) → experiment test
    non_nlp_train  — SciER non-NLP train docs
    non_nlp_dev    — SciER non-NLP dev docs
    non_nlp_test   — SciER non-NLP test docs (7 docs, split 5→train / 2→dev by caller)
    """
    splits = {"train": [], "dev": [], "test": []}
    for split in ("train", "dev", "test"):
        for doc in load_ere_docs("scier", split):
            doc_id = str(doc["doc_id"])
            cluster = cluster_map.get(doc_id, 0)
            doc["_cluster"] = cluster
            doc["_original_split"] = split
            splits[split].append(doc)

    nlp_docs = []
    non_nlp_train_orig = []
    non_nlp_dev_orig = []
    non_nlp_test_orig = []

    for split, docs in splits.items():
        for doc in docs:
            cluster = doc["_cluster"]
            # Outliers (cluster=-1) appear only in SciER train; treat as NLP.
            is_nlp = cluster == 1 or cluster == -1
            if is_nlp:
                if str(doc["doc_id"]) in SCIER_TEST_EXCLUSIONS:
                    continue  # leakage: doc also present in GSAP-ERE NLP auxiliary
                nlp_docs.append(doc)
            elif split == "train":
                non_nlp_train_orig.append(doc)
            elif split == "dev":
                non_nlp_dev_orig.append(doc)
            else:
                non_nlp_test_orig.append(doc)

    return nlp_docs, non_nlp_train_orig, non_nlp_dev_orig, non_nlp_test_orig


def build_gsap_splits(
    cluster_map: dict[str, int],
) -> tuple[list[dict], list[dict]]:
    """Return (nlp_docs, non_nlp_docs) for GSAP-ERE (all splits combined)."""
    nlp_docs = []
    non_nlp_docs = []
    for split in ("train", "dev", "test"):
        for doc in load_ere_docs("gsap-ere", split):
            doc_id = str(doc["doc_id"])
            cluster = cluster_map.get(doc_id, 0)
            doc["_cluster"] = cluster
            doc["_original_split"] = split
            # Outliers (cluster=-1) in GSAP-ERE treated as non-NLP.
            is_nlp = cluster == 1
            if is_nlp:
                nlp_docs.append(doc)
            else:
                non_nlp_docs.append(doc)
    return nlp_docs, non_nlp_docs


def build_manifest(
    scier_train: list[dict],
    scier_dev: list[dict],
    scier_test: list[dict],
    gsap_non_nlp: list[dict],
    gsap_nlp_sample: list[dict],
    gsap_mixed: list[dict],
    metadata: dict[str, dict],
    cluster_map: dict[str, int],
) -> dict:
    """Build the JSON manifest for the webapp."""

    gsap_nlp_ids = {str(d["doc_id"]) for d in gsap_nlp_sample}
    gsap_non_nlp_ids = {str(d["doc_id"]) for d in gsap_non_nlp}
    gsap_mixed_ids = {str(d["doc_id"]) for d in gsap_mixed}

    documents = []

    for exp_split, docs in [
        ("train", scier_train),
        ("dev", scier_dev),
        ("test", scier_test),
    ]:
        for doc in docs:
            doc_id = str(doc["doc_id"])
            meta = metadata.get(doc_id, {})
            cluster = doc["_cluster"]
            documents.append({
                "doc_id": doc_id,
                "title": meta.get("title", ""),
                "original_dataset": "scier",
                "original_split": doc["_original_split"],
                "cluster": cluster,
                "cluster_label": "NLP" if cluster >= 1 or cluster == -1 else "non-NLP",
                "experiment_dataset": "domain-shift-scier",
                "experiment_split": exp_split,
                "in_nlp_aux": False,
                "in_non_nlp_aux": False,
                "in_mixed_aux": False,
            })

    for doc in gsap_non_nlp:
        doc_id = str(doc["doc_id"])
        meta = metadata.get(doc_id, {})
        cluster = doc["_cluster"]
        documents.append({
            "doc_id": doc_id,
            "title": meta.get("title", ""),
            "original_dataset": "gsap-ere",
            "original_split": doc["_original_split"],
            "cluster": cluster,
            "cluster_label": "non-NLP",
            "experiment_dataset": "domain-shift-gsap-ere-auxiliary",
            "experiment_split": None,
            "in_nlp_aux": doc_id in gsap_nlp_ids,
            "in_non_nlp_aux": True,
            "in_mixed_aux": doc_id in gsap_mixed_ids,
        })

    # GSAP NLP docs that are in the sample but not in non-NLP (avoid duplicates)
    for doc in gsap_nlp_sample:
        doc_id = str(doc["doc_id"])
        if doc_id in gsap_non_nlp_ids:
            continue
        meta = metadata.get(doc_id, {})
        cluster = doc["_cluster"]
        documents.append({
            "doc_id": doc_id,
            "title": meta.get("title", ""),
            "original_dataset": "gsap-ere",
            "original_split": doc["_original_split"],
            "cluster": cluster,
            "cluster_label": "NLP",
            "experiment_dataset": "domain-shift-gsap-ere-auxiliary",
            "experiment_split": None,
            "in_nlp_aux": True,
            "in_non_nlp_aux": False,
            "in_mixed_aux": doc_id in gsap_mixed_ids,
        })

    # GSAP NLP docs NOT in sample (for completeness — not used in any auxiliary set)
    # (omitted — only include documents actually in an experiment file)

    stats = {
        "scier_train": len(scier_train),
        "scier_dev": len(scier_dev),
        "scier_test": len(scier_test),
        "gsap_non_nlp_aux": len(gsap_non_nlp),
        "gsap_nlp_aux": len(gsap_nlp_sample),
        "gsap_mixed_aux": len(gsap_mixed),
    }

    return {"documents": documents, "statistics": stats}


def main() -> None:
    print("Loading cluster map …")
    cluster_map = load_cluster_map()
    print("Loading metadata …")
    metadata = load_metadata()

    # ── SciER ──────────────────────────────────────────────────────────────────
    print("\nBuilding SciER domain-shift splits …")
    nlp_docs, non_nlp_train_orig, non_nlp_dev_orig, non_nlp_test_orig = (
        build_scier_splits(cluster_map, metadata)
    )

    print(f"  SciER NLP docs (→ test):       {len(nlp_docs)}")
    print(f"  SciER non-NLP train (original): {len(non_nlp_train_orig)}")
    print(f"  SciER non-NLP dev (original):   {len(non_nlp_dev_orig)}")
    print(f"  SciER non-NLP test (original):  {len(non_nlp_test_orig)}")

    # Split the 7 non-NLP test docs: 5 → new train, 2 → new dev
    rng = random.Random(SEED)
    test_non_nlp_shuffled = list(non_nlp_test_orig)
    rng.shuffle(test_non_nlp_shuffled)
    test_to_train = test_non_nlp_shuffled[:5]
    test_to_dev = test_non_nlp_shuffled[5:]

    scier_train = non_nlp_train_orig + test_to_train
    scier_dev = non_nlp_dev_orig + test_to_dev
    scier_test = nlp_docs

    print(f"  → experiment train: {len(scier_train)} (target: 66)")
    print(f"  → experiment dev:   {len(scier_dev)} (target: 10)")
    print(f"  → experiment test:  {len(scier_test)} (target: 24)")

    # ── GSAP-ERE auxiliary ─────────────────────────────────────────────────────
    print("\nBuilding GSAP-ERE auxiliary sets …")
    gsap_nlp_all, gsap_non_nlp = build_gsap_splits(cluster_map)
    print(f"  GSAP-ERE NLP docs available:     {len(gsap_nlp_all)}")
    print(f"  GSAP-ERE non-NLP docs available: {len(gsap_non_nlp)} (target: 46)")

    # Sample 46 NLP docs from 54 available
    rng2 = random.Random(SEED)
    gsap_nlp_shuffled = list(gsap_nlp_all)
    rng2.shuffle(gsap_nlp_shuffled)
    gsap_nlp_sample = gsap_nlp_shuffled[:46]

    # Mixed: first 23 from NLP sample + first 23 from non-NLP
    rng3 = random.Random(SEED)
    non_nlp_for_mixed = list(gsap_non_nlp)
    rng3.shuffle(non_nlp_for_mixed)
    gsap_mixed = gsap_nlp_sample[:23] + non_nlp_for_mixed[:23]

    print(f"  → NLP auxiliary:     {len(gsap_nlp_sample)} (target: 46)")
    print(f"  → non-NLP auxiliary: {len(gsap_non_nlp)} (target: 46)")
    print(f"  → mixed auxiliary:   {len(gsap_mixed)} (target: 46)")

    # ── Shuffle all splits by document ─────────────────────────────────────────
    scier_train_out = shuffle_docs(scier_train, SEED)
    scier_dev_out   = shuffle_docs(scier_dev, SEED)
    scier_test_out  = shuffle_docs(scier_test, SEED)
    gsap_non_nlp_out  = shuffle_docs(gsap_non_nlp, SEED)
    gsap_nlp_out      = shuffle_docs(gsap_nlp_sample, SEED)
    gsap_mixed_out    = shuffle_docs(gsap_mixed, SEED)

    # ── Strip internal _cluster / _original_split fields before writing ────────
    def strip(docs: list[dict]) -> list[dict]:
        return [{k: v for k, v in d.items() if not k.startswith("_")} for d in docs]

    # ── Write JSONL files ──────────────────────────────────────────────────────
    print("\nWriting JSONL files …")
    write_jsonl(strip(scier_train_out), DATA_DATASETS_FOLDER / "domain-shift-scier" / "train.jsonl")
    write_jsonl(strip(scier_dev_out),   DATA_DATASETS_FOLDER / "domain-shift-scier" / "dev.jsonl")
    write_jsonl(strip(scier_test_out),  DATA_DATASETS_FOLDER / "domain-shift-scier" / "test.jsonl")
    write_jsonl(strip(gsap_non_nlp_out),  DATA_DATASETS_FOLDER / "domain-shift-gsap-ere-auxiliary" / "train_non_nlp.jsonl")
    write_jsonl(strip(gsap_nlp_out),      DATA_DATASETS_FOLDER / "domain-shift-gsap-ere-auxiliary" / "train_nlp.jsonl")
    write_jsonl(strip(gsap_mixed_out),    DATA_DATASETS_FOLDER / "domain-shift-gsap-ere-auxiliary" / "train_mixed.jsonl")

    # ── Build and write JSON manifest ──────────────────────────────────────────
    print("\nBuilding manifest …")
    manifest = build_manifest(
        scier_train_out,
        scier_dev_out,
        scier_test_out,
        gsap_non_nlp,       # unshuffled — for consistent membership flags
        gsap_nlp_sample,
        gsap_mixed,
        metadata,
        cluster_map,
    )
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_OUT, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  Wrote manifest → {MANIFEST_OUT.relative_to(ROOT)}")
    print(f"  Total documents in manifest: {len(manifest['documents'])}")
    print(f"\nDone. Statistics: {manifest['statistics']}")


if __name__ == "__main__":
    main()
