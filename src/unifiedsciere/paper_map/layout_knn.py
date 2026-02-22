"""Compute kNN graph and spring layout from embeddings."""

import logging

import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

logger = logging.getLogger(__name__)


def build_knn_graph(
    embeddings: np.ndarray,
    k: int = 12,
    symmetrize: bool = True,
) -> nx.Graph:
    """Build a kNN graph with cosine similarity edge weights."""
    nn = NearestNeighbors(n_neighbors=k + 1, metric="cosine", algorithm="brute")
    nn.fit(embeddings)
    distances, indices = nn.kneighbors(embeddings)

    sim_matrix = cosine_similarity(embeddings)

    G = nx.Graph()
    G.add_nodes_from(range(len(embeddings)))

    for i in range(len(embeddings)):
        for j_idx in range(1, k + 1):  # skip self (index 0)
            j = indices[i, j_idx]
            weight = float(sim_matrix[i, j])
            if symmetrize:
                G.add_edge(i, j, weight=weight)
            else:
                G.add_edge(i, j, weight=weight)

    logger.info(
        "kNN graph: %d nodes, %d edges (k=%d)",
        G.number_of_nodes(),
        G.number_of_edges(),
        k,
    )
    return G


def compute_knn_layout(
    embeddings: np.ndarray,
    k: int = 12,
    symmetrize: bool = True,
    seed: int = 42,
) -> tuple[np.ndarray, nx.Graph]:
    """Build kNN graph and compute spring layout.

    Returns (coords, graph) where coords has shape (N, 2).
    """
    G = build_knn_graph(embeddings, k=k, symmetrize=symmetrize)

    pos = nx.spring_layout(G, weight="weight", seed=seed, iterations=100)

    coords = np.array([pos[i] for i in range(len(embeddings))])
    logger.info("kNN spring layout: %d points", len(coords))
    return coords, G
