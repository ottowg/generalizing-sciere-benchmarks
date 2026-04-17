"""Compute bibliographic coupling layout for the Paper Map.

Two papers are coupled when they cite many of the same works (shared OpenAlex
reference IDs).  For each pair we compute Jaccard similarity over their
reference sets, build a similarity graph, and reduce to 2-D with a
Fruchterman-Reingold spring layout.

Steps
-----
  1. Load paper metadata (references field from all_papers.jsonl).
  2. Compute pairwise Jaccard similarity on reference sets.
  3. Build a weighted graph (edge weight = Jaccard) and run spring layout.
  4. Write x_spring_refs / y_spring_refs columns into paper_map.parquet.

Usage
-----
    uv run python scripts/paper_map/compute_reference_layout.py
    uv run python scripts/paper_map/compute_reference_layout.py --min-refs 3 --min-sim 0.05
"""

from __future__ import annotations

import argparse
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from unifiedsciere.metadata.read_metadata import load_papers

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "data" / "doc_embeddings"


def main(min_refs: int = 1, min_sim: float = 0.0, power: float = 1.0, random_state: int = 42) -> None:
    # ------------------------------------------------------------------
    # Step 1: Load reference sets
    # ------------------------------------------------------------------
    print("=== Step 1: Load paper references ===")
    papers = load_papers()
    ref_map: dict[str, set[str]] = {
        p.doc_id: set(p.references) for p in papers if p.references
    }
    print(f"  {len(ref_map)} / {len(papers)} papers have references")

    parquet_path = ARTIFACTS_DIR / "paper_map.parquet"
    base_df = pd.read_parquet(parquet_path)
    all_doc_ids = base_df["doc_id"].tolist()

    doc_ids = [did for did in all_doc_ids if len(ref_map.get(did, set())) >= min_refs]
    refs = [ref_map[did] for did in doc_ids]
    n = len(doc_ids)
    print(f"  Using {n} papers with >= {min_refs} reference(s)")

    # ------------------------------------------------------------------
    # Step 2: Pairwise Jaccard similarity
    # ------------------------------------------------------------------
    print("\n=== Step 2: Compute pairwise Jaccard similarity ===")
    sim = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            union = refs[i] | refs[j]
            if union:
                val = len(refs[i] & refs[j]) / len(union)
                sim[i, j] = sim[j, i] = val

    nonzero = int((sim > 0).sum() - n) // 2
    print(f"  Non-zero pairs: {nonzero} / {n * (n - 1) // 2} "
          f"({100 * nonzero / (n * (n - 1) // 2 + 1e-9):.1f}%)")
    if nonzero:
        nz = sim[sim > 0]
        print(f"  Similarity range: {nz.min():.4f} – {nz.max():.4f}  "
              f"median {np.median(nz):.4f}")

    # ------------------------------------------------------------------
    # Step 3: Spring layout
    # ------------------------------------------------------------------
    print("\n=== Step 3: Spring layout ===")
    G = nx.Graph()
    G.add_nodes_from(range(n))
    rows, cols = np.where(np.triu(sim > min_sim, 1))
    for i, j in zip(rows, cols):
        G.add_edge(int(i), int(j), weight=float(sim[i, j] ** power))
    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges "
          f"(min_sim={min_sim})")

    pos = nx.spring_layout(G, weight="weight", seed=random_state, iterations=200)
    coords = np.array([pos[i] for i in range(n)])

    # ------------------------------------------------------------------
    # Step 4: Write to parquet
    # ------------------------------------------------------------------
    print("\n=== Step 4: Write parquet ===")
    coord_lookup = {
        did: (float(xy[0]), float(xy[1]))
        for did, xy in zip(doc_ids, coords)
    }
    base_df["x_spring_refs"] = base_df["doc_id"].map(
        lambda d: coord_lookup.get(d, (float("nan"), float("nan")))[0]
    )
    base_df["y_spring_refs"] = base_df["doc_id"].map(
        lambda d: coord_lookup.get(d, (float("nan"), float("nan")))[1]
    )
    base_df.to_parquet(parquet_path, index=False)
    print(f"  Updated: {parquet_path}")

    # Also save the similarity matrix for interactive edge overlays
    sim_out = ARTIFACTS_DIR / "reference_similarity.npz"
    np.savez_compressed(sim_out, doc_ids=np.array(doc_ids), sim=sim)
    print(f"  Written: {sim_out}")

    print(f"\nDone. {n} papers with reference coupling layout.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--min-refs", type=int, default=1,
        help="Minimum number of references a paper must have to be included (default: 1)",
    )
    parser.add_argument(
        "--min-sim", type=float, default=0.0,
        help="Minimum Jaccard similarity for an edge in the spring graph (default: 0.0)",
    )
    parser.add_argument(
        "--power", type=float, default=1.0,
        help="Exponent applied to Jaccard weights (default: 1.0). "
             "Values > 1 sharpen cluster contrast by amplifying strong connections "
             "and suppressing weak ones.",
    )
    args = parser.parse_args()
    main(min_refs=args.min_refs, min_sim=args.min_sim, power=args.power)
