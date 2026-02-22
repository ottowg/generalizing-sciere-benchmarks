"""Streamlit interactive viewer for paper map."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

from .layout_knn import compute_knn_layout
from .layout_umap import compute_umap

ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_PATH = Path(__file__).parent / "config.yaml"


@st.cache_data
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


@st.cache_data
def load_data():
    cfg = load_config()
    data_dir = ROOT / cfg["artifacts_dir"]
    df = pd.read_parquet(data_dir / "paper_map.parquet")

    # Load normalized embeddings (doc_id-keyed JSON)
    with open(data_dir / "embeddings_norm.json") as f:
        emb_dict = json.load(f)
    # Build array in same order as df
    doc_ids = df["doc_id"].tolist()
    embeddings_norm = np.array([emb_dict[did] for did in doc_ids])

    # Load kNN edges
    edges_path = data_dir / "knn_edges.json"
    edges = []
    if edges_path.exists():
        with open(edges_path) as f:
            edges = json.load(f)

    return df, embeddings_norm, edges


def make_scatter(df, x_col, y_col, show_edges=False, edges=None):
    """Build a plotly figure with colored scatter + hover."""
    labels = sorted(df["label"].unique())
    colors = {
        "gsap": "#636EFA",
        "scier": "#EF553B",
        "scinlp": "#00CC96",
    }
    fallback_colors = ["#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]
    for i, lab in enumerate(labels):
        if lab not in colors:
            colors[lab] = fallback_colors[i % len(fallback_colors)]

    fig = go.Figure()

    # Draw kNN edges if requested
    if show_edges and edges:
        doc_id_to_idx = {did: i for i, did in enumerate(df["doc_id"])}
        edge_x, edge_y = [], []
        for e in edges:
            si, ti = doc_id_to_idx.get(e["source"]), doc_id_to_idx.get(e["target"])
            if si is not None and ti is not None:
                edge_x.extend([df[x_col].iloc[si], df[x_col].iloc[ti], None])
                edge_y.extend([df[y_col].iloc[si], df[y_col].iloc[ti], None])
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=0.3, color="rgba(150,150,150,0.3)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # One trace per label for legend
    for lab in labels:
        mask = df["label"] == lab
        sub = df[mask]
        fig.add_trace(
            go.Scatter(
                x=sub[x_col],
                y=sub[y_col],
                mode="markers",
                marker=dict(
                    size=7,
                    color=colors.get(lab, "#999"),
                    line=dict(width=0.5, color="white"),
                ),
                name=lab,
                text=sub["title"],
                customdata=sub["doc_id"],
                hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
            )
        )

    fig.update_layout(
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


def main():
    st.set_page_config(page_title="Paper Map", layout="wide")
    st.title("Paper Map — SPECTER2 Embeddings")

    df, embeddings_norm, edges = load_data()
    cfg = load_config()

    # Sidebar controls
    st.sidebar.header("Layout")
    layout = st.sidebar.selectbox("Layout", ["UMAP", "kNN"], index=0)

    show_edges = False

    if layout == "UMAP":
        st.sidebar.subheader("UMAP parameters")
        n_neighbors = st.sidebar.slider(
            "n_neighbors", 5, 50, cfg["umap"]["n_neighbors"]
        )
        min_dist = st.sidebar.slider(
            "min_dist", 0.0, 1.0, cfg["umap"]["min_dist"], step=0.05
        )
        recompute = st.sidebar.button("Recompute UMAP")

        if recompute:
            with st.spinner("Computing UMAP..."):
                coords = compute_umap(
                    embeddings_norm, n_neighbors=n_neighbors, min_dist=min_dist
                )
            df = df.copy()
            df["x_umap"] = coords[:, 0]
            df["y_umap"] = coords[:, 1]

        x_col, y_col = "x_umap", "y_umap"

    else:  # kNN
        st.sidebar.subheader("kNN parameters")
        k = st.sidebar.slider("k (neighbors)", 5, 30, cfg["knn"]["k"])
        show_edges = st.sidebar.checkbox("Show edges", value=False)
        recompute = st.sidebar.button("Recompute kNN layout")

        if recompute:
            with st.spinner("Computing kNN layout..."):
                coords, graph = compute_knn_layout(embeddings_norm, k=k)
            df = df.copy()
            df["x_knn"] = coords[:, 0]
            df["y_knn"] = coords[:, 1]
            # Update edges from recomputed graph
            doc_ids = df["doc_id"].tolist()
            edges = [
                {
                    "source": doc_ids[u],
                    "target": doc_ids[v],
                    "weight": round(d["weight"], 6),
                }
                for u, v, d in graph.edges(data=True)
            ]

        x_col, y_col = "x_knn", "y_knn"

    fig = make_scatter(df, x_col, y_col, show_edges=show_edges, edges=edges)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"{len(df)} papers | Layout: {layout}")


if __name__ == "__main__":
    main()
