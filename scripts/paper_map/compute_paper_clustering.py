"""Cluster annotated publications by topical similarity to reveal cross-dataset overlap.

Three feature types:
  - SPECTER2 embeddings (semantic similarity)
  - Reference lists as TF-IDF, filtered to top N most-cited within the corpus
  - LLM-annotated entities as TF-IDF: concept and artifact treated separately

Outlier detection: LOF per feature type, vote across types.

Clustering: GMM-BIC sweep (k=2..15) per feature + HDBSCAN on combined.

Outputs:
  data/webapp/publication_map/cluster_data.json   — centroids + top terms per cluster
  data/webapp/publication_map/paper_map.parquet   — updated with cluster/outlier columns

Usage
-----
    uv run python scripts/paper_map/compute_paper_clustering.py
    uv run python scripts/paper_map/compute_paper_clustering.py --dry-run
    uv run python scripts/paper_map/compute_paper_clustering.py --top-refs 400
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import hdbscan
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack as sp_hstack
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import normalize
from umap import UMAP

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "data" / "webapp" / "publication_map"
METADATA_PATH = ROOT / "data" / "metadata" / "unified" / "all_papers.jsonl"
LLM_DATASETS = ["scier_LLM_gpt-5.4_v3", "gsap-ere_LLM_gpt-5.4_v3", "scinlp_LLM_gpt-5.4_v3"]
SPLITS = ["train", "dev", "test"]


# ---------------------------------------------------------------------------
# Feature loading
# ---------------------------------------------------------------------------

def load_papers() -> tuple[list[str], list[str], dict[str, str], dict[str, str]]:
    """Return (doc_ids, dataset_labels, titles, openalex_ids)."""
    doc_ids, datasets, titles, openalex_ids = [], [], {}, {}
    with open(METADATA_PATH) as f:
        for line in f:
            rec = json.loads(line)
            doc_ids.append(rec["doc_id"])
            datasets.append(rec["dataset"])
            titles[rec["doc_id"]] = rec.get("title", "")
            if rec.get("openalex_id"):
                openalex_ids[rec["openalex_id"]] = rec.get("title", "")
    return doc_ids, datasets, titles, openalex_ids


def load_specter_embeddings(doc_ids: list[str]) -> np.ndarray:
    """Load pre-computed normalised SPECTER2 embeddings (N × 768)."""
    path = ARTIFACTS_DIR / "embeddings_norm.json"
    with open(path) as f:
        emb_dict = json.load(f)
    missing = [d for d in doc_ids if d not in emb_dict]
    if missing:
        print(f"  WARNING: {len(missing)} doc_ids missing from SPECTER embeddings")
    return np.array([emb_dict.get(d, [0.0] * 768) for d in doc_ids])


def load_reference_features(
    doc_ids: list[str],
    min_papers: int = 3,
    max_papers: int = 40,
    max_vocab: int = 500,
) -> tuple[csr_matrix, list[str]]:
    """Build binary doc × reference matrix using a mid-frequency band.

    Keeps references cited by [min_papers, max_papers] corpus papers — excluding
    universal non-discriminative refs (cited by almost everyone) and noise refs
    (cited by only 1-2 papers). Caps at max_vocab by favouring higher-frequency refs.

    Returns (sparse matrix, vocabulary list of OpenAlex reference IDs).
    """
    ref_lists: dict[str, list[str]] = {}
    with open(METADATA_PATH) as f:
        for line in f:
            rec = json.loads(line)
            ref_lists[rec["doc_id"]] = rec.get("references", [])

    from collections import Counter
    citation_counts: Counter = Counter()
    for refs in ref_lists.values():
        citation_counts.update(refs)

    # Mid-frequency band: discriminative but not universal
    band = {ref for ref, count in citation_counts.items() if min_papers <= count <= max_papers}
    if len(band) > max_vocab:
        # Trim to top max_vocab by frequency (upper end of band = more papers → more stable signal)
        band = set(sorted(band, key=lambda r: citation_counts[r], reverse=True)[:max_vocab])

    vocab = sorted(band)
    ref_idx = {r: i for i, r in enumerate(vocab)}

    rows, cols, data = [], [], []
    for row_idx, doc_id in enumerate(doc_ids):
        for ref in ref_lists.get(doc_id, []):
            if ref in ref_idx:
                rows.append(row_idx)
                cols.append(ref_idx[ref])
                data.append(1.0)

    mat = csr_matrix((data, (rows, cols)), shape=(len(doc_ids), len(vocab)))
    print(f"  Reference vocab: {len(vocab)} (band {min_papers}–{max_papers} papers,"
          f" {len(citation_counts)} unique total)")
    print(f"  Reference matrix: {mat.shape}, nnz={mat.nnz}")
    return mat, vocab


def _normalise_entity_text(text: str) -> str:
    """Lowercase, collapse whitespace, strip trailing 's' for naive depluralization."""
    text = " ".join(text.lower().split())
    words = text.split()
    words = [
        w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w
        for w in words
    ]
    return " ".join(words)


def _load_llm_raw_counts(doc_ids: list[str]) -> dict[str, dict[str, dict[str, int]]]:
    """Load all LLM entity annotations (no filtering).

    Returns {doc_id: {"concept": {term: count}, "artifact": {term: count}}}.
    """
    datasets_dir = ROOT / "datasets"
    raw: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: {"concept": defaultdict(int), "artifact": defaultdict(int)}
    )
    for ds in LLM_DATASETS:
        for split in SPLITS:
            fpath = datasets_dir / ds / f"{split}.jsonl"
            if not fpath.exists():
                continue
            with open(fpath) as f:
                for line in f:
                    rec = json.loads(line)
                    doc_key = rec["doc_key"]
                    for sent_idx, sent_ner in enumerate(rec.get("ner", [])):
                        sent_tokens = rec["sentences"][sent_idx]
                        for span in sent_ner:
                            start, end, lbl = span[0], span[1], span[2]
                            if lbl not in ("concept", "artifact"):
                                continue
                            text = _normalise_entity_text(" ".join(sent_tokens[start:end + 1]))
                            if len(text) < 3 or not any(c.isalpha() for c in text):
                                continue
                            raw[doc_key][lbl][text] += 1
    return dict(raw)


def load_llm_entity_features(
    doc_ids: list[str],
    raw_counts: dict[str, dict[str, dict[str, int]]],
    min_papers: int = 3,
    max_papers: int = 80,
) -> dict[str, tuple[csr_matrix, list[str]]]:
    """Build filtered TF-IDF sparse matrices for clustering from pre-loaded raw counts.

    Keeps terms in a mid-frequency band [min_papers, max_papers]: rare terms
    add noise, very common terms (e.g. "model", "network") are non-discriminative.

    Returns {label: (sparse_matrix, vocab_list)}.
    """
    results: dict[str, tuple[csr_matrix, list[str]]] = {}
    for label in ("concept", "artifact"):
        term_doc_count: dict[str, int] = defaultdict(int)
        for doc_tc in raw_counts.values():
            for term in doc_tc[label]:
                term_doc_count[term] += 1

        kept = {t for t, c in term_doc_count.items() if min_papers <= c <= max_papers}
        vocab = sorted(kept)
        term_idx = {t: i for i, t in enumerate(vocab)}

        rows, cols, data = [], [], []
        for row_idx, doc_id in enumerate(doc_ids):
            for term, count in raw_counts.get(doc_id, {}).get(label, {}).items():
                if term in term_idx:
                    rows.append(row_idx)
                    cols.append(term_idx[term])
                    data.append(float(count))

        mat = csr_matrix((data, (rows, cols)), shape=(len(doc_ids), len(vocab)))
        print(f"  {label}: {len(vocab)} terms (band {min_papers}–{max_papers} papers), matrix {mat.shape}, nnz={mat.nnz}")
        results[label] = (mat, vocab)

    return results


# ---------------------------------------------------------------------------
# Dimensionality reduction
# ---------------------------------------------------------------------------

def apply_tfidf(X: csr_matrix) -> csr_matrix:
    return TfidfTransformer().fit_transform(X)


def reduce_pca(X: np.ndarray, n_components: int = 50, random_state: int = 42) -> np.ndarray:
    """PCA reduction for outlier detection — linear, preserves global structure."""
    from sklearn.decomposition import PCA
    n = min(n_components, X.shape[1], X.shape[0] - 1)
    return PCA(n_components=n, random_state=random_state).fit_transform(X)


def reduce_svd_only(X: csr_matrix, n_components: int = 50, random_state: int = 42) -> np.ndarray:
    """TruncatedSVD only (no UMAP) — for outlier detection on sparse matrices."""
    n = min(n_components, X.shape[1] - 1, X.shape[0] - 1)
    return TruncatedSVD(n_components=n, random_state=random_state).fit_transform(X)


def reduce_dense(X: np.ndarray, n_components: int = 20, random_state: int = 42, metric: str = "cosine") -> np.ndarray:
    reducer = UMAP(n_components=n_components, metric=metric, random_state=random_state, verbose=False)
    return reducer.fit_transform(X)


def reduce_sparse(X: csr_matrix, svd_components: int = 50, umap_components: int = 20, random_state: int = 42) -> np.ndarray:
    n_svd = min(svd_components, X.shape[1] - 1, X.shape[0] - 1)
    svd = TruncatedSVD(n_components=n_svd, random_state=random_state)
    X_svd = svd.fit_transform(X)
    reducer = UMAP(n_components=umap_components, metric="cosine", random_state=random_state, verbose=False)
    return reducer.fit_transform(X_svd)


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------

def lof_outliers(X: np.ndarray, n_neighbors: int = 10, contamination: float = 0.05) -> np.ndarray:
    return LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination).fit_predict(X)


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def gmm_bic_sweep(X: np.ndarray, k_range: range, random_state: int = 42) -> tuple[np.ndarray, int, list[float]]:
    """GMM with diagonal covariance; BIC-optimal k. Returns (labels, best_k, bics)."""
    bics = []
    for k in k_range:
        gm = GaussianMixture(n_components=k, covariance_type="diag", random_state=random_state, n_init=3, reg_covar=1e-4)
        gm.fit(X)
        bics.append(gm.bic(X))
    best_k = list(k_range)[int(np.argmin(bics))]
    best_gm = GaussianMixture(n_components=best_k, covariance_type="diag", random_state=random_state, n_init=5, reg_covar=1e-4)
    return best_gm.fit_predict(X), best_k, bics


def hdbscan_cluster(X: np.ndarray, min_cluster_size: int = 5) -> np.ndarray:
    return hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=3).fit_predict(X)


def compute_meta_clusters(
    X_high_dim: np.ndarray,
    outlier_mask: np.ndarray,
    n_clusters: int,
    random_state: int = 42,
) -> np.ndarray:
    """Partition inlier papers into n_clusters broad meta-clusters.

    Runs GMM on the high-dimensional combined feature space (SPECTER + refs +
    entities, normalized, before any UMAP step) so global topology is preserved.
    Outlier papers keep label -1.

    Returns per-paper meta-cluster labels (0..n_clusters-1, or -1 for noise).
    """
    from sklearn.cluster import KMeans
    meta_labels = np.full(len(X_high_dim), -1, dtype=int)
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=20)
    inlier_labels = km.fit_predict(X_high_dim[~outlier_mask])
    meta_labels[~outlier_mask] = inlier_labels
    return meta_labels


# ---------------------------------------------------------------------------
# Cluster-level Inverse Topic Mention (ITM) scoring
# ---------------------------------------------------------------------------

def cluster_itm_top_terms(
    labels: np.ndarray,
    doc_ids: list[str],
    raw_counts: dict[str, dict[str, dict[str, int]]],
    entity_label: str,
    top_n: int = 10,
) -> dict[int, list[tuple[str, float]]]:
    """Score entity terms per cluster using TF × inverse-cluster-frequency.

    Uses raw (unfiltered) entity counts so every cluster can show its most
    characteristic terms, even for rare vocabulary.

    Returns {cluster_id: [(term, score), ...]} sorted descending.
    """
    from collections import Counter
    unique_clusters = [c for c in sorted(set(labels)) if c != -1]
    C = len(unique_clusters)
    cluster_idx = {c: i for i, c in enumerate(unique_clusters)}

    cluster_counts: list[Counter] = [Counter() for _ in range(C)]
    for i, (doc_id, label) in enumerate(zip(doc_ids, labels)):
        if label == -1:
            continue
        for term, count in raw_counts.get(doc_id, {}).get(entity_label, {}).items():
            cluster_counts[cluster_idx[label]][term] += count

    # ICF: how many clusters contain this term at all
    term_cluster_df: Counter = Counter()
    for cc in cluster_counts:
        for term in cc:
            term_cluster_df[term] += 1

    result: dict[int, list[tuple[str, float]]] = {}
    for c, ci in cluster_idx.items():
        cc = cluster_counts[ci]
        if not cc:
            result[int(c)] = []
            continue
        total = sum(cc.values()) + 1e-10
        scores = {
            term: (count / total) * np.log((C + 1) / (term_cluster_df[term] + 1))
            for term, count in cc.items()
        }
        # Fall back to raw TF if all ICF scores are zero (term in every cluster)
        if max(scores.values()) == 0:
            scores = {term: count / total for term, count in cc.items()}
        top = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
        result[int(c)] = [(t, round(float(s), 4)) for t, s in top if s > 0]
    return result


def cluster_itm_refs(
    labels: np.ndarray,
    X_refs_tfidf: csr_matrix,
    ref_vocab: list[str],
    top_n: int = 10,
) -> dict[int, list[tuple[str, float]]]:
    """ITM for reference IDs using the filtered reference TF-IDF matrix."""
    unique_clusters = [c for c in sorted(set(labels)) if c != -1]
    C = len(unique_clusters)
    V = len(ref_vocab)
    cluster_idx = {c: i for i, c in enumerate(unique_clusters)}

    cluster_counts = np.zeros((C, V))
    for i, label in enumerate(labels):
        if label == -1:
            continue
        row = np.asarray(X_refs_tfidf[i].todense()).flatten()
        cluster_counts[cluster_idx[label]] += row

    row_sums = cluster_counts.sum(axis=1, keepdims=True) + 1e-10
    cluster_tf = cluster_counts / row_sums
    df_cluster  = (cluster_counts > 0).sum(axis=0)
    icf = np.log((C + 1) / (df_cluster + 1))
    tf_icf = cluster_tf * icf

    result: dict[int, list[tuple[str, float]]] = {}
    for c, ci in cluster_idx.items():
        scores = tf_icf[ci]
        if scores.max() == 0:
            scores = cluster_tf[ci]
        top_idx = np.argsort(scores)[::-1][:top_n]
        result[int(c)] = [(ref_vocab[j], round(float(scores[j]), 4)) for j in top_idx if scores[j] > 0]
    return result


# ---------------------------------------------------------------------------
# Centroid computation (in 2D paper_map space)
# ---------------------------------------------------------------------------

def compute_centroids(
    labels: np.ndarray,
    doc_ids: list[str],
    pm_df: pd.DataFrame,
) -> dict[int, dict]:
    """Compute mean 2D position per cluster in the paper_map coordinate space."""
    id_to_row = {d: i for i, d in enumerate(pm_df["doc_id"].tolist())}
    x_umap = pm_df["x_umap"].values
    y_umap = pm_df["y_umap"].values
    x_knn  = pm_df["x_knn"].values
    y_knn  = pm_df["y_knn"].values

    centroids: dict[int, dict] = {}
    for c in sorted(set(labels)):
        if c == -1:
            continue
        indices = [id_to_row[d] for i, d in enumerate(doc_ids) if labels[i] == c and d in id_to_row]
        if not indices:
            continue
        centroids[int(c)] = {
            "umap": [float(np.mean(x_umap[indices])), float(np.mean(y_umap[indices]))],
            "knn":  [float(np.mean(x_knn[indices])),  float(np.mean(y_knn[indices]))],
        }
    return centroids


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def cluster_composition(labels: np.ndarray, dataset_labels: list[str]) -> dict[int, dict[str, int]]:
    comp: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for cl, ds in zip(labels, dataset_labels):
        comp[int(cl)][ds] += 1
    return {k: dict(v) for k, v in comp.items()}


def print_cluster_report(
    feature_name: str,
    labels: np.ndarray,
    dataset_labels: list[str],
    best_k: int | None,
    bics: list[float] | None,
    X_reduced: np.ndarray,
    outlier_mask: np.ndarray,
) -> None:
    inlier_labels   = labels[~outlier_mask]
    inlier_datasets = [d for d, o in zip(dataset_labels, outlier_mask) if not o]
    n_clusters = len(set(inlier_labels) - {-1})
    noise_count = (inlier_labels == -1).sum()
    sil = silhouette_score(X_reduced[~outlier_mask], inlier_labels) if n_clusters > 1 else float("nan")

    print(f"\n{'='*60}")
    print(f"Feature: {feature_name}")
    print(f"  Best k={best_k}, silhouette={sil:.3f}, noise={noise_count}")
    if bics:
        bic_items = "  BIC: " + ", ".join(f"k={k}:{b:.0f}" for k, b in zip(range(2, 2 + len(bics)), bics))
        print(bic_items[:130])

    comp = cluster_composition(inlier_labels, inlier_datasets)
    print(f"\n  {'Cluster':>8} | {'gsap':>6} | {'scier':>6} | {'scinlp':>7} | {'total':>6}")
    print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*7}-+-{'-'*6}")
    for cl in sorted(c for c in comp if c != -1):
        c = comp[cl]
        total = sum(c.values())
        print(f"  {cl:>8} | {c.get('gsap',0):>6} | {c.get('scier',0):>6} | {c.get('scinlp',0):>7} | {total:>6}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(dry_run: bool = False, k_max: int = 15) -> None:
    doc_ids, dataset_labels, titles, openalex_titles = load_papers()
    print(f"Total papers: {len(doc_ids)}")

    # -------------------------------------------------------------------------
    print("\n=== Step 1: Load features ===")

    print("SPECTER2 embeddings...")
    X_specter = load_specter_embeddings(doc_ids)

    print("Reference features (mid-frequency band)...")
    X_refs_raw, ref_vocab = load_reference_features(doc_ids)
    X_refs_tfidf = apply_tfidf(X_refs_raw)

    print("LLM entity features (concept / artifact)...")
    raw_entity_counts = _load_llm_raw_counts(doc_ids)
    entity_mats = load_llm_entity_features(doc_ids, raw_entity_counts, min_papers=3)
    X_concept_raw,  concept_vocab  = entity_mats["concept"]
    X_artifact_raw, artifact_vocab = entity_mats["artifact"]
    X_concept_tfidf  = apply_tfidf(X_concept_raw)
    X_artifact_tfidf = apply_tfidf(X_artifact_raw)
    # Combined entity matrix for UMAP/clustering (more signal than either alone)
    X_entities_combined = sp_hstack([X_concept_raw, X_artifact_raw])
    X_entities_tfidf    = apply_tfidf(X_entities_combined)

    if dry_run:
        print("\n(dry-run: stopping after feature load)")
        return

    # -------------------------------------------------------------------------
    print("\n=== Step 2: Dimensionality reduction (UMAP to 20D) ===")

    print("  SPECTER2 → UMAP (20D)...")
    X_specter_umap = reduce_dense(X_specter, n_components=20)

    print("  SPECTER2 → UMAP (2D, for meta-clustering)...")
    X_specter_2d = UMAP(
        n_components=2, metric="cosine", n_neighbors=15, min_dist=0.1,
        random_state=42, verbose=False,
    ).fit_transform(X_specter)

    print("  References → SVD → UMAP...")
    X_refs_umap = reduce_sparse(X_refs_tfidf, svd_components=50, umap_components=20)

    print("  Entities (concept+artifact combined) → SVD → UMAP...")
    n_svd_ent = min(40, X_entities_tfidf.shape[1] - 1, X_entities_tfidf.shape[0] - 1)
    X_entities_umap = reduce_sparse(X_entities_tfidf, svd_components=n_svd_ent, umap_components=15)

    print("  Concepts (separate) → SVD → UMAP...")
    n_svd_concept = min(40, X_concept_tfidf.shape[1] - 1, X_concept_tfidf.shape[0] - 1)
    X_concept_umap = reduce_sparse(X_concept_tfidf, svd_components=n_svd_concept, umap_components=15)

    print("  Artifacts (separate) → SVD → UMAP...")
    n_svd_artifact = min(40, X_artifact_tfidf.shape[1] - 1, X_artifact_tfidf.shape[0] - 1)
    X_artifact_umap = reduce_sparse(X_artifact_tfidf, svd_components=n_svd_artifact, umap_components=15)

    print("  Combined (specter + refs + concepts + artifacts) → UMAP...")
    X_combined_raw = np.hstack([
        normalize(X_specter_umap) * 2.0,   # up-weight SPECTER for tighter semantic layout
        normalize(X_refs_umap),
        normalize(X_concept_umap),
        normalize(X_artifact_umap),
    ])
    X_combined_umap = reduce_dense(X_combined_raw, n_components=20, metric="euclidean")

    print("  Combined → 2D UMAP (visualization layout)...")
    X_combined_2d = UMAP(
        n_components=2, metric="euclidean",
        n_neighbors=50, min_dist=0.5,
        random_state=42, verbose=False,
    ).fit_transform(X_combined_umap)

    # -------------------------------------------------------------------------
    print("\n=== Step 3: Outlier detection (LOF on pre-UMAP spaces) ===")

    # LOF must run on the pre-UMAP feature space: UMAP's non-linear compression
    # can fold outliers into the main distribution, hiding them from LOF.
    X_specter_pca  = reduce_pca(X_specter, n_components=50)
    X_refs_svd     = reduce_svd_only(X_refs_tfidf, n_components=50)
    X_entities_svd = reduce_svd_only(apply_tfidf(sp_hstack([X_concept_raw, X_artifact_raw])), n_components=50)

    lof_specter  = lof_outliers(X_specter_pca)
    lof_refs     = lof_outliers(X_refs_svd)
    lof_entities = lof_outliers(X_entities_svd)

    outlier_votes = (lof_specter == -1).astype(int) + (lof_refs == -1).astype(int) + (lof_entities == -1).astype(int)
    outlier_mask  = outlier_votes >= 2

    print(f"  Outliers flagged by >= 2 feature types: {outlier_mask.sum()}")
    for i, doc_id in enumerate(doc_ids):
        if outlier_mask[i]:
            print(f"    [{dataset_labels[i]:>8}] {doc_id:30s} | votes={outlier_votes[i]} | {titles.get(doc_id,'')[:60]}")

    # -------------------------------------------------------------------------
    k_range = range(2, k_max + 1)
    print(f"\n=== Step 4: GMM-BIC sweep k=2..{k_max} ===")

    all_labels: dict[str, np.ndarray] = {}
    all_bics:   dict[str, list[float]] = {}
    all_best_k: dict[str, int] = {}

    for fname, X_umap in [
        ("specter",   X_specter_umap),
        ("refs",      X_refs_umap),
        ("concepts",  X_concept_umap),
        ("artifacts", X_artifact_umap),
        ("combined",  X_combined_umap),
    ]:
        X_inliers = X_umap[~outlier_mask]
        labels_inlier, best_k, bics = gmm_bic_sweep(X_inliers, k_range)
        labels_full = np.full(len(doc_ids), -1, dtype=int)
        labels_full[~outlier_mask] = labels_inlier
        all_labels[fname]  = labels_full
        all_bics[fname]    = bics
        all_best_k[fname]  = best_k
        print_cluster_report(fname, labels_full, dataset_labels, best_k, bics, X_umap, outlier_mask)

    # -------------------------------------------------------------------------
    print("\n=== Step 5: HDBSCAN on combined UMAP ===")

    # HDBSCAN requires low-dimensional input — density estimation collapses in
    # high dimensions (curse of dimensionality). X_combined_umap (20D) is used.
    hdb_inlier = hdbscan_cluster(X_combined_umap[~outlier_mask])
    hdb_full   = np.full(len(doc_ids), -1, dtype=int)
    hdb_full[~outlier_mask] = hdb_inlier
    all_labels["hdbscan"] = hdb_full
    n_hdb = len(set(hdb_inlier) - {-1})
    print(f"  HDBSCAN: {n_hdb} clusters, {(hdb_inlier==-1).sum()} noise points")
    print_cluster_report("hdbscan", hdb_full, dataset_labels, n_hdb, None, X_combined_umap, outlier_mask)

    # -------------------------------------------------------------------------
    print("\n=== Step 5b: Meta-clustering (k=2 and k=3, SPECTER + refs only) ===")

    # Raw SPECTER embeddings (768D) — no compression, no distortion.
    X_meta_raw = X_specter

    for n_meta in (2, 3):
        key = f"meta_{n_meta}"
        labels = compute_meta_clusters(X_meta_raw, outlier_mask, n_clusters=n_meta)
        all_labels[key] = labels
        print_cluster_report(key, labels, dataset_labels, n_meta, None, X_meta_raw, outlier_mask)

    # -------------------------------------------------------------------------
    print("\n=== Step 6: Cluster-level ITM top terms ===")

    itm_concept  = cluster_itm_top_terms(all_labels["hdbscan"], doc_ids, raw_entity_counts, "concept",  top_n=10)
    itm_artifact = cluster_itm_top_terms(all_labels["hdbscan"], doc_ids, raw_entity_counts, "artifact", top_n=10)
    itm_refs     = cluster_itm_refs(all_labels["hdbscan"], X_refs_tfidf, ref_vocab, top_n=10)

    print(f"  ITM computed for {len(itm_concept)} concept clusters, {len(itm_artifact)} artifact clusters")

    # -------------------------------------------------------------------------
    print("\n=== Step 7: Compute 2D centroids + build cluster_data.json ===")

    parquet_path = ARTIFACTS_DIR / "paper_map.parquet"
    pm_df = pd.read_parquet(parquet_path)

    cluster_data: dict[str, dict] = {}
    outlier_doc_ids = [d for d, o in zip(doc_ids, outlier_mask) if o]

    for fname, labels in all_labels.items():
        centroids = compute_centroids(labels, doc_ids, pm_df)
        comp      = cluster_composition(labels, dataset_labels)
        clusters_out: dict[str, dict] = {}

        for c in sorted(centroids):
            entry: dict = {
                "centroid":      centroids[c],
                "size":          int((labels == c).sum()),
                "datasets":      comp.get(c, {}),
            }
            if fname == "hdbscan":
                entry["top_concepts"]  = itm_concept.get(c, [])
                entry["top_artifacts"] = itm_artifact.get(c, [])
                # Enrich reference IDs with titles where available
                entry["top_references"] = [
                    [ref_id, round(score, 4), openalex_titles.get(ref_id, "")]
                    for ref_id, score in itm_refs.get(c, [])
                ]
            clusters_out[str(c)] = entry

        cluster_data[fname] = {
            "clusters":      clusters_out,
            "best_k":        all_best_k.get(fname, len(clusters_out)),
            "outlier_doc_ids": outlier_doc_ids,
        }

    # Also compute ITM for other clusterings (combined at minimum)
    for fname in ["combined", "specter", "refs", "concepts", "artifacts", "meta_2", "meta_3"]:
        labels = all_labels[fname]
        itm_c = cluster_itm_top_terms(labels, doc_ids, raw_entity_counts, "concept",  top_n=8)
        itm_a = cluster_itm_top_terms(labels, doc_ids, raw_entity_counts, "artifact", top_n=8)
        itm_r = cluster_itm_refs(labels, X_refs_tfidf, ref_vocab, top_n=8)
        for c_str, entry in cluster_data[fname]["clusters"].items():
            c = int(c_str)
            entry["top_concepts"]  = itm_c.get(c, [])
            entry["top_artifacts"] = itm_a.get(c, [])
            entry["top_references"] = [
                [ref_id, round(score, 4), openalex_titles.get(ref_id, "")]
                for ref_id, score in itm_r.get(c, [])
            ]

    # Enrich centroids with combined-layout 2D positions
    doc_to_comb_idx = {d: i for i, d in enumerate(doc_ids)}
    for fname, labels in all_labels.items():
        for c_str, entry in cluster_data[fname]["clusters"].items():
            c = int(c_str)
            comb_idxs = [doc_to_comb_idx[d] for i, d in enumerate(doc_ids)
                         if labels[i] == c and d in doc_to_comb_idx]
            if comb_idxs:
                entry["centroid"]["combined"] = [
                    float(np.mean(X_combined_2d[comb_idxs, 0])),
                    float(np.mean(X_combined_2d[comb_idxs, 1])),
                ]

    out_json = ARTIFACTS_DIR / "cluster_data.json"
    with open(out_json, "w") as f:
        json.dump(cluster_data, f, ensure_ascii=False)
    print(f"  Written: {out_json}")

    # -------------------------------------------------------------------------
    print("\n=== Step 8: Update paper_map.parquet ===")

    def _clean(v):
        import math
        if isinstance(v, float) and math.isnan(v):
            return None
        if hasattr(v, "item"):
            return v.item()
        return v

    id_to_idx = {d: i for i, d in enumerate(doc_ids)}
    pm_df["outlier_score"] = pm_df["doc_id"].map(
        lambda d: int(outlier_votes[id_to_idx[d]]) if d in id_to_idx else None
    )
    for fname, labels in all_labels.items():
        pm_df[f"cluster_{fname}"] = pm_df["doc_id"].map(
            lambda d, L=labels: int(L[id_to_idx[d]]) if d in id_to_idx else None
        )
    pm_df["x_combined"] = pm_df["doc_id"].map(
        lambda d: float(X_combined_2d[id_to_idx[d], 0]) if d in id_to_idx else None
    )
    pm_df["y_combined"] = pm_df["doc_id"].map(
        lambda d: float(X_combined_2d[id_to_idx[d], 1]) if d in id_to_idx else None
    )

    pm_df.to_parquet(parquet_path, index=False)
    cluster_cols = [c for c in pm_df.columns if "cluster" in c or "outlier" in c]
    print(f"  Updated: {parquet_path}")
    print(f"  Columns added: {cluster_cols}")

    print(f"\nDone. {len(doc_ids)} papers clustered.")
    print(f"Cluster data written to {out_json}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Load features only, no clustering or output")
    parser.add_argument("--k-max",  type=int, default=15, help="Maximum k for GMM-BIC sweep (default: 15)")
    args = parser.parse_args()
    main(dry_run=args.dry_run, k_max=args.k_max)
