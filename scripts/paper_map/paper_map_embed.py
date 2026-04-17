"""CLI entry point: compute embeddings and layouts, save artifacts."""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from unifiedsciere.paper_map.embed import (
    compute_embeddings,
    load_cached_embedding_dict,
    load_cached_embeddings,
    load_papers,
    normalize_embeddings,
    save_embeddings,
)
from unifiedsciere.paper_map.layout_knn import compute_knn_layout
from unifiedsciere.paper_map.layout_umap import compute_umap

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    config_path = Path(__file__).resolve().parents[2] / "configs" / "paper_map" / "paper_map_config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    out_dir = Path(cfg["artifacts_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load papers
    papers = load_papers(cfg["data_path"])
    doc_ids = [p["doc_id"] for p in papers]

    # Embeddings: load cache and only embed papers that are missing
    embeddings = load_cached_embeddings(out_dir, doc_ids)
    if embeddings is None:
        cache = load_cached_embedding_dict(out_dir)
        missing_papers = [p for p in papers if p["doc_id"] not in cache]
        if missing_papers:
            logger.info("Embedding %d new papers", len(missing_papers))
            new_embeddings = compute_embeddings(
                missing_papers,
                model_name=cfg["model_name"],
                adapter_name=cfg["adapter_name"],
                batch_size=cfg["batch_size"],
            )
            for p, emb in zip(missing_papers, new_embeddings):
                cache[p["doc_id"]] = emb.tolist()
        # Drop stale entries and reorder to match current doc_ids
        embeddings = np.array([cache[did] for did in doc_ids])
        save_embeddings(embeddings, doc_ids, out_dir)

    # Normalize
    embeddings_norm = normalize_embeddings(embeddings)
    save_embeddings_norm = {
        did: vec.tolist() for did, vec in zip(doc_ids, embeddings_norm)
    }
    with open(out_dir / "embeddings_norm.json", "w") as f:
        json.dump(save_embeddings_norm, f)

    # UMAP layout
    umap_cfg = cfg["umap"]
    umap_coords = compute_umap(
        embeddings_norm,
        n_neighbors=umap_cfg["n_neighbors"],
        min_dist=umap_cfg["min_dist"],
        metric=umap_cfg["metric"],
        random_state=umap_cfg["random_state"],
    )

    # kNN layout
    knn_cfg = cfg["knn"]
    knn_coords, knn_graph = compute_knn_layout(
        embeddings_norm,
        k=knn_cfg["k"],
        symmetrize=knn_cfg["symmetrize"],
    )

    # Save layouts as doc_id-keyed JSON
    umap_layout = {
        did: {"x": float(umap_coords[i, 0]), "y": float(umap_coords[i, 1])}
        for i, did in enumerate(doc_ids)
    }
    with open(out_dir / "layout_umap.json", "w") as f:
        json.dump(umap_layout, f, indent=2)
    logger.info("Saved UMAP layout to %s", out_dir / "layout_umap.json")

    knn_layout = {
        did: {"x": float(knn_coords[i, 0]), "y": float(knn_coords[i, 1])}
        for i, did in enumerate(doc_ids)
    }
    with open(out_dir / "layout_knn.json", "w") as f:
        json.dump(knn_layout, f, indent=2)
    logger.info("Saved kNN layout to %s", out_dir / "layout_knn.json")

    # Save kNN graph edges as doc_id pairs
    edges = []
    for u, v, data in knn_graph.edges(data=True):
        edges.append(
            {
                "source": doc_ids[u],
                "target": doc_ids[v],
                "weight": round(data["weight"], 6),
            }
        )
    with open(out_dir / "knn_edges.json", "w") as f:
        json.dump(edges, f, indent=2)
    logger.info("Saved %d kNN edges to %s", len(edges), out_dir / "knn_edges.json")

    # Build merged table (parquet + csv) for convenience
    df = pd.DataFrame(
        {
            "doc_id": doc_ids,
            "title": [p["title"] for p in papers],
            "label": [p["label"] for p in papers],
            "x_umap": umap_coords[:, 0],
            "y_umap": umap_coords[:, 1],
            "x_knn": knn_coords[:, 0],
            "y_knn": knn_coords[:, 1],
        }
    )
    df.to_parquet(out_dir / "paper_map.parquet", index=False)
    df.to_csv(out_dir / "paper_map.csv", index=False)
    logger.info("Saved paper_map table (%d rows)", len(df))

    print(f"\nDone! {len(df)} papers embedded and laid out.")
    print(f"  Artifacts: {out_dir}/")
    print(f"  Launch viewer: uv run streamlit run paper_map/viewer.py")


if __name__ == "__main__":
    main()
