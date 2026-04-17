"""Compute UMAP layouts from OpenAlex topic assignments.

Two layouts are produced:

Paper map (topic-based)
    Each paper is represented as a weighted topic vector (score per topic).
    UMAP reduces this to 2-D, placing topically similar papers close together.
    Columns ``x_topic_umap`` / ``y_topic_umap`` are written into paper_map.parquet.

Topic map
    Each topic is represented as a weighted paper vector (same scores, transposed).
    UMAP on the topic×paper matrix groups topics that co-occur on the same papers.
    Saved to ``topic_map.parquet`` in the same artefacts directory.

Topic filtering
    --min-papers INT     Keep only topics assigned to >= INT papers (default: 2)
    --exclude-top INT    Drop the INT most common topics before building the matrix
                         (removes broad umbrella topics like "Computer Science")

Steps
-----
  1. Load openalex_topics from all_papers.jsonl.
  2. Build vocabulary (apply filters).
  3. Build sparse paper×topic score matrix.
  4. UMAP on paper rows  → paper layout (written to paper_map.parquet).
  5. UMAP on topic rows  → topic layout (written to topic_map.parquet).

Usage
-----
    uv run python scripts/paper_map/compute_topic_layout.py
    uv run python scripts/paper_map/compute_topic_layout.py --min-papers 3 --exclude-top 5
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import umap

from unifiedsciere.metadata.read_metadata import load_papers

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "data" / "doc_embeddings"


def build_matrix(
    papers: list,
    min_papers: int = 2,
    exclude_top: int = 0,
) -> tuple[np.ndarray, list[str], list[str]]:
    """Build a paper×topic score matrix.

    Returns
    -------
    matrix : shape (n_papers, n_topics), float32
    doc_ids : list of doc_id strings (row order)
    topics  : list of topic name strings (column order)
    """
    # Collect per-paper topic scores
    paper_topics: list[tuple[str, list[dict]]] = []
    for p in papers:
        t_list = p.openalex_topics or []
        if t_list:
            paper_topics.append((p.doc_id, t_list))

    # Count how many papers each topic appears in
    topic_counts: Counter = Counter()
    for _, t_list in paper_topics:
        for t in t_list:
            topic_counts[t["name"]] += 1

    # Determine vocabulary
    # Sort by descending frequency so exclude_top removes the most common ones
    sorted_topics = [name for name, _ in topic_counts.most_common()]

    if exclude_top:
        print(f"  Excluding top {exclude_top} topics: {sorted_topics[:exclude_top]}")
        sorted_topics = sorted_topics[exclude_top:]

    vocab = [t for t in sorted_topics if topic_counts[t] >= min_papers]

    topic_idx = {name: i for i, name in enumerate(vocab)}
    n_topics = len(vocab)

    # Only keep papers that have at least one topic in vocab
    valid = [(did, tl) for did, tl in paper_topics
             if any(t["name"] in topic_idx for t in tl)]

    doc_ids = [did for did, _ in valid]
    n_papers = len(doc_ids)

    matrix = np.zeros((n_papers, n_topics), dtype=np.float32)
    for row, (_, t_list) in enumerate(valid):
        for t in t_list:
            col = topic_idx.get(t["name"])
            if col is not None:
                matrix[row, col] = float(t.get("score") or 0.0)

    return matrix, doc_ids, vocab


def run_umap(
    data: np.ndarray,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    random_state: int = 42,
    metric: str = "cosine",
) -> np.ndarray:
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        random_state=random_state,
        metric=metric,
    )
    return reducer.fit_transform(data)


def main(
    min_papers: int = 2,
    exclude_top: int = 0,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    random_state: int = 42,
) -> None:
    # ------------------------------------------------------------------
    # Step 1: Load topics
    # ------------------------------------------------------------------
    print("=== Step 1: Load paper topics ===")
    papers = load_papers()
    with_topics = [p for p in papers if p.openalex_topics]
    print(f"  {len(with_topics)} / {len(papers)} papers have topic data")

    # ------------------------------------------------------------------
    # Step 2: Build matrix
    # ------------------------------------------------------------------
    print("\n=== Step 2: Build paper×topic matrix ===")
    matrix, doc_ids, vocab = build_matrix(
        papers, min_papers=min_papers, exclude_top=exclude_top
    )
    n_papers, n_topics = matrix.shape
    print(f"  Matrix shape: {n_papers} papers × {n_topics} topics")
    print(f"  (min_papers={min_papers}, exclude_top={exclude_top})")
    density = (matrix > 0).sum() / matrix.size
    print(f"  Non-zero entries: {(matrix > 0).sum()} ({100*density:.1f}%)")

    if n_papers < 4 or n_topics < 2:
        print("  ERROR: too few papers/topics — nothing to compute.")
        return

    # ------------------------------------------------------------------
    # Step 3: Paper UMAP
    # ------------------------------------------------------------------
    print("\n=== Step 3: Paper UMAP (topic-based) ===")
    paper_coords = run_umap(
        matrix,
        n_neighbors=min(n_neighbors, n_papers - 1),
        min_dist=min_dist,
        random_state=random_state,
    )
    print(f"  Done — {paper_coords.shape}")

    # ------------------------------------------------------------------
    # Step 4: Write paper coords to parquet
    # ------------------------------------------------------------------
    print("\n=== Step 4: Write paper coords to parquet ===")
    parquet_path = ARTIFACTS_DIR / "paper_map.parquet"
    base_df = pd.read_parquet(parquet_path)

    coord_lookup = {did: (float(xy[0]), float(xy[1])) for did, xy in zip(doc_ids, paper_coords)}
    nan = float("nan")
    base_df["x_topic_umap"] = base_df["doc_id"].map(lambda d: coord_lookup.get(d, (nan, nan))[0])
    base_df["y_topic_umap"] = base_df["doc_id"].map(lambda d: coord_lookup.get(d, (nan, nan))[1])
    base_df.to_parquet(parquet_path, index=False)
    print(f"  Updated: {parquet_path}")
    print(f"  Papers with topic coords: {base_df['x_topic_umap'].notna().sum()} / {len(base_df)}")

    # ------------------------------------------------------------------
    # Step 5: Topic UMAP
    # ------------------------------------------------------------------
    print("\n=== Step 5: Topic UMAP (paper-based) ===")
    topic_matrix = matrix.T  # shape: (n_topics, n_papers)
    topic_coords = run_umap(
        topic_matrix,
        n_neighbors=min(n_neighbors, n_topics - 1),
        min_dist=min_dist,
        random_state=random_state,
    )
    print(f"  Done — {topic_coords.shape}")

    # Count papers per topic, overall and per dataset
    papers_per_topic = (matrix > 0).sum(axis=0)  # shape: (n_topics,)

    # Build doc_id → dataset / selection lookups
    doc_dataset = {p.doc_id: p.dataset for p in papers}
    doc_selection = {p.doc_id: p.selection for p in papers}

    # Sub-dataset masks (rows in the matrix)
    sub_defs = {
        "gsap_hf":    lambda d: doc_dataset.get(d, "") == "gsap-ere" and doc_selection.get(d, "") == "huggingface_selection",
        "gsap_arxiv": lambda d: doc_dataset.get(d, "") == "gsap-ere" and doc_selection.get(d, "") == "arxiv_random_selection",
        "gsap-ere":       lambda d: doc_dataset.get(d, "") == "gsap-ere",
        "scier":      lambda d: doc_dataset.get(d, "") == "scier",
        "scinlp":     lambda d: doc_dataset.get(d, "") == "scinlp",
    }

    per_ds_counts: dict[str, np.ndarray] = {}
    totals: dict[str, int] = {}
    for sub, pred in sub_defs.items():
        mask = np.array([pred(d) for d in doc_ids])
        per_ds_counts[sub] = (matrix[mask] > 0).sum(axis=0).astype(int)
        totals[sub] = int(mask.sum())

    topic_df = pd.DataFrame({
        "topic": vocab,
        "n_papers": papers_per_topic.astype(int),
        "n_gsap": per_ds_counts["gsap-ere"],
        "n_gsap_hf": per_ds_counts["gsap_hf"],
        "n_gsap_arxiv": per_ds_counts["gsap_arxiv"],
        "n_scier": per_ds_counts["scier"],
        "n_scinlp": per_ds_counts["scinlp"],
        # Dataset totals (papers with ≥1 topic in vocabulary) — constant per row
        "total_gsap_hf": totals["gsap_hf"],
        "total_gsap_arxiv": totals["gsap_arxiv"],
        "total_scier": totals["scier"],
        "total_scinlp": totals["scinlp"],
        "x_topic_umap": topic_coords[:, 0].astype(float),
        "y_topic_umap": topic_coords[:, 1].astype(float),
    })
    topic_path = ARTIFACTS_DIR / "topic_map.parquet"
    topic_df.to_parquet(topic_path, index=False)
    print(f"  Written: {topic_path}  ({len(topic_df)} topics)")
    print(f"  Dataset totals (papers with topics): GSAP-HF={totals['gsap_hf']}, GSAP-arXiv={totals['gsap_arxiv']}, SciER={totals['scier']}, SciNLP={totals['scinlp']}")

    print(f"\nDone.")
    print(f"  Paper layout: x_topic_umap / y_topic_umap in paper_map.parquet")
    print(f"  Topic layout: {topic_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--min-papers", type=int, default=2,
        help="Minimum number of paper assignments for a topic to be included (default: 2)",
    )
    parser.add_argument(
        "--exclude-top", type=int, default=0,
        help="Exclude the N most-assigned topics (removes broad umbrella topics, default: 0)",
    )
    parser.add_argument(
        "--n-neighbors", type=int, default=15,
        help="UMAP n_neighbors (default: 15)",
    )
    parser.add_argument(
        "--min-dist", type=float, default=0.1,
        help="UMAP min_dist (default: 0.1)",
    )
    args = parser.parse_args()
    main(
        min_papers=args.min_papers,
        exclude_top=args.exclude_top,
        n_neighbors=args.n_neighbors,
        min_dist=args.min_dist,
    )
