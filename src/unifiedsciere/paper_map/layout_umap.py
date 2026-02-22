"""Compute UMAP 2D layout from embeddings."""

import logging

import numpy as np
import umap

logger = logging.getLogger(__name__)


def compute_umap(
    embeddings: np.ndarray,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    metric: str = "cosine",
    random_state: int = 42,
) -> np.ndarray:
    """Run UMAP to get 2D coordinates.

    Returns array of shape (N, 2) with [x_umap, y_umap].
    """
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
    )
    coords = reducer.fit_transform(embeddings)
    logger.info("UMAP layout: %d points", len(coords))
    return coords
