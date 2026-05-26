"""Compute per-paper entity sets (Task / Dataset / Method) from unified gold annotations.

For each paper across all three datasets and all splits:
  1. Load gold annotations and apply the unification pipeline.
  2. Extract (label, normalised_text) tuples for the three unified types.
  3. Filter out tuples that appear in fewer than `--min-papers` publications
     (default 2 — removes hapax legomena that carry no shared signal).
  4. Compute pairwise Jaccard similarity matrices — one per entity type and
     one combined — then reduce to 2-D with classical metric MDS.
  5. Write
       data/doc_embeddings/entity_sets.json       — dict doc_id → {task/dataset/method}
       data/doc_embeddings/entity_paper_map.parquet — MDS coordinates appended to existing
                                                       paper_map.parquet columns

Usage
-----
    uv run python scripts/paper_map/compute_entity_sets.py
    uv run python scripts/paper_map/compute_entity_sets.py --min-papers 3
    uv run python scripts/paper_map/compute_entity_sets.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.manifold import MDS

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.unification.pipeline import apply_unification_pipeline

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "data" / "webapp" / "publication_map"

DATASETS = ["gsap-ere", "scier", "scinlp"]
SPLITS = ["train", "dev", "test"]
ENTITY_TYPES = ["Task", "Dataset", "Method"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lower-case and collapse whitespace."""
    return " ".join(text.lower().split())


def _jaccard(a: set, b: set) -> float:
    # Both empty → no shared signal, treat as 0 not 1
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _mds_coords(dissim: np.ndarray, random_state: int = 42) -> np.ndarray:
    """Run classical metric MDS; return (n, 2) array."""
    mds = MDS(n_components=2, dissimilarity="precomputed",
              random_state=random_state, n_init=4, normalized_stress="auto")
    return mds.fit_transform(dissim)


# ---------------------------------------------------------------------------
# Step 1 — Load and unify all gold annotations
# ---------------------------------------------------------------------------

def load_all_entity_sets(min_papers: int = 2) -> dict[str, dict[str, set]]:
    """Return entity_sets[doc_id][entity_type] = set of normalised mention texts.

    Mentions that appear in fewer than `min_papers` distinct documents are
    removed from every paper's set (they carry no cross-paper similarity signal).
    """
    raw: dict[str, dict[str, set]] = defaultdict(lambda: {t: set() for t in ENTITY_TYPES})

    for dataset in DATASETS:
        for split in SPLITS:
            print(f"  Loading {dataset}/{split} ...", end=" ", flush=True)
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
            except FileNotFoundError:
                print("not found, skipping")
                continue

            corpus, _ = apply_unification_pipeline(
                corpus, dataset,
                apply_to_gold=True,
                apply_to_predicted=False,
            )

            for m in corpus.mentions:
                if m.label in ENTITY_TYPES:
                    raw[m.document_id][m.label].add(_normalise(m.text))

            print(f"{len(corpus.mentions)} mentions → "
                  f"{len({m.document_id for m in corpus.mentions})} docs")

    # Count how many documents each (type, text) pair appears in
    pair_doc_counts: Counter[tuple[str, str]] = Counter()
    for doc_sets in raw.values():
        for etype, texts in doc_sets.items():
            for t in texts:
                pair_doc_counts[(etype, t)] += 1

    # Filter — keep only pairs present in >= min_papers documents
    kept = {pair for pair, cnt in pair_doc_counts.items() if cnt >= min_papers}
    print(f"\n  Unique (type, text) pairs before filter: {len(pair_doc_counts)}")
    print(f"  Pairs in >= {min_papers} papers (kept):   {len(kept)}")

    filtered: dict[str, dict[str, set]] = {}
    for doc_id, doc_sets in raw.items():
        filtered[doc_id] = {
            etype: {t for t in texts if (etype, t) in kept}
            for etype, texts in doc_sets.items()
        }

    return filtered


# ---------------------------------------------------------------------------
# Step 2 — Compute Jaccard similarity matrices
# ---------------------------------------------------------------------------

def compute_similarity_matrices(
    entity_sets: dict[str, dict[str, set]],
    doc_ids: list[str],
) -> dict[str, np.ndarray]:
    """Return sim[type_name] = (n, n) Jaccard similarity matrix.

    Also returns 'combined' key with equal-weight average over all types.
    """
    n = len(doc_ids)
    idx = {did: i for i, did in enumerate(doc_ids)}

    sim: dict[str, np.ndarray] = {t: np.zeros((n, n)) for t in ENTITY_TYPES}
    sim["combined"] = np.zeros((n, n))

    for i, di in enumerate(doc_ids):
        for j in range(i, n):
            dj = doc_ids[j]
            per_type = []
            for etype in ENTITY_TYPES:
                j_val = _jaccard(entity_sets[di][etype], entity_sets[dj][etype])
                sim[etype][i, j] = sim[etype][j, i] = j_val
                per_type.append(j_val)
            sim["combined"][i, j] = sim["combined"][j, i] = sum(per_type) / len(per_type)

    return sim


# ---------------------------------------------------------------------------
# Step 3 — MDS layout
# ---------------------------------------------------------------------------

def compute_mds_layouts(
    sim: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Return coords[type_name] = (n, 2) array from MDS on 1-sim dissimilarity."""
    coords = {}
    for name, s in sim.items():
        dissim = 1.0 - s
        np.fill_diagonal(dissim, 0.0)
        print(f"  MDS for '{name}' ...", end=" ", flush=True)
        coords[name] = _mds_coords(dissim)
        print("done")
    return coords


def compute_spring_layouts(
    sim: dict[str, np.ndarray],
    min_sim: float = 0.0,
    random_state: int = 42,
) -> dict[str, np.ndarray]:
    """Return coords[type_name] = (n, 2) from Fruchterman-Reingold on Jaccard similarity graph.

    Only edges with sim > min_sim are included. Edge weight = Jaccard similarity.
    """
    coords = {}
    for name, s in sim.items():
        n = s.shape[0]
        G = nx.Graph()
        G.add_nodes_from(range(n))
        rows, cols = np.where(np.triu(s > min_sim, 1))
        for i, j in zip(rows, cols):
            G.add_edge(int(i), int(j), weight=float(s[i, j]))
        print(f"  Spring for '{name}' ({G.number_of_edges()} edges) ...", end=" ", flush=True)
        pos = nx.spring_layout(G, weight="weight", seed=random_state, iterations=100)
        coords[name] = np.array([pos[i] for i in range(n)])
        print("done")
    return coords


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(min_papers: int = 2, dry_run: bool = False) -> None:
    print("=== Step 1: Load and unify gold annotations ===")
    entity_sets = load_all_entity_sets(min_papers=min_papers)
    print(f"\n  Total papers with entity sets: {len(entity_sets)}")

    # Serialise sets to lists for JSON
    entity_sets_json: dict[str, dict[str, list]] = {
        doc_id: {etype: sorted(texts) for etype, texts in sets.items()}
        for doc_id, sets in entity_sets.items()
    }

    # Load existing paper_map.parquet to get the canonical doc_id order
    parquet_path = ARTIFACTS_DIR / "paper_map.parquet"
    base_df = pd.read_parquet(parquet_path)
    all_doc_ids = base_df["doc_id"].tolist()

    # Only keep doc_ids that have entity data (others will get NaN coords)
    doc_ids_with_data = [did for did in all_doc_ids if did in entity_sets]
    missing = [did for did in all_doc_ids if did not in entity_sets]
    print(f"\n  Papers in parquet:          {len(all_doc_ids)}")
    print(f"  Papers with entity data:    {len(doc_ids_with_data)}")
    print(f"  Papers without entity data: {len(missing)}")

    print("\n=== Step 2: Compute Jaccard similarity matrices ===")
    sim = compute_similarity_matrices(entity_sets, doc_ids_with_data)

    # Report sparsity
    for name, s in sim.items():
        n = len(doc_ids_with_data)
        nonzero = int((s > 0).sum() - n)  # exclude diagonal
        print(f"  {name:10s}: {nonzero}/{n*(n-1)} non-zero off-diagonal pairs "
              f"({100*nonzero/(n*(n-1)+1e-9):.1f}%)")

    print("\n=== Step 3: MDS layouts ===")
    coords = compute_mds_layouts(sim)

    print("\n=== Step 3b: Spring layouts ===")
    spring_coords = compute_spring_layouts(sim)

    if dry_run:
        print("\n(dry-run: not writing files)")
        return

    print("\n=== Step 4: Write outputs ===")

    # 4a. entity_sets.json
    out_json = ARTIFACTS_DIR / "entity_sets.json"
    with open(out_json, "w") as f:
        json.dump(entity_sets_json, f, ensure_ascii=False)
    print(f"  Written: {out_json}")

    # 4b. Add MDS columns to paper_map.parquet
    # Build doc_id -> coord lookup (NaN for papers without data)
    coord_lookup: dict[str, dict[str, tuple]] = {}
    for name, c in coords.items():
        for did, xy in zip(doc_ids_with_data, c):
            coord_lookup.setdefault(did, {})[name] = (float(xy[0]), float(xy[1]))

    col_map = {
        "Task":     ("x_entity_task",     "y_entity_task"),
        "Dataset":  ("x_entity_dataset",  "y_entity_dataset"),
        "Method":   ("x_entity_method",   "y_entity_method"),
        "combined": ("x_entity_combined", "y_entity_combined"),
    }
    for name, (xcol, ycol) in col_map.items():
        base_df[xcol] = base_df["doc_id"].map(
            lambda did, n=name: coord_lookup.get(did, {}).get(n, (float("nan"), float("nan")))[0]
        )
        base_df[ycol] = base_df["doc_id"].map(
            lambda did, n=name: coord_lookup.get(did, {}).get(n, (float("nan"), float("nan")))[1]
        )

    # Spring layout columns
    spring_lookup: dict[str, dict[str, tuple]] = {}
    for name, c in spring_coords.items():
        for did, xy in zip(doc_ids_with_data, c):
            spring_lookup.setdefault(did, {})[name] = (float(xy[0]), float(xy[1]))

    spring_col_map = {
        "Task":     ("x_spring_task",     "y_spring_task"),
        "Dataset":  ("x_spring_dataset",  "y_spring_dataset"),
        "Method":   ("x_spring_method",   "y_spring_method"),
        "combined": ("x_spring_combined", "y_spring_combined"),
    }
    for name, (xcol, ycol) in spring_col_map.items():
        base_df[xcol] = base_df["doc_id"].map(
            lambda did, n=name: spring_lookup.get(did, {}).get(n, (float("nan"), float("nan")))[0]
        )
        base_df[ycol] = base_df["doc_id"].map(
            lambda did, n=name: spring_lookup.get(did, {}).get(n, (float("nan"), float("nan")))[1]
        )

    # Also save entity count summaries
    base_df["n_entity_task"] = base_df["doc_id"].map(
        lambda did: len(entity_sets.get(did, {}).get("Task", set()))
    )
    base_df["n_entity_dataset"] = base_df["doc_id"].map(
        lambda did: len(entity_sets.get(did, {}).get("Dataset", set()))
    )
    base_df["n_entity_method"] = base_df["doc_id"].map(
        lambda did: len(entity_sets.get(did, {}).get("Method", set()))
    )

    base_df.to_parquet(parquet_path, index=False)
    print(f"  Updated: {parquet_path}")

    # Also save a separate similarity matrix file for interactive use
    sim_out = ARTIFACTS_DIR / "entity_similarity.npz"
    np.savez_compressed(
        sim_out,
        doc_ids=np.array(doc_ids_with_data),
        **{f"sim_{k}": v for k, v in sim.items()},
    )
    print(f"  Written: {sim_out}")

    print(f"\nDone. min_papers={min_papers}, {len(doc_ids_with_data)} papers indexed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-papers", type=int, default=2,
                        help="Min number of papers a (type, text) pair must appear in to be kept "
                             "(default: 2 — removes hapax legomena)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run without writing any output files")
    args = parser.parse_args()
    main(min_papers=args.min_papers, dry_run=args.dry_run)
