"""Entry point for the paper map Streamlit app.

Usage:
    uv run streamlit run scripts/streamlit_paper_map.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
import streamlit as st
import yaml

from unifiedsciere.metadata.read_metadata import read_as_dataframe
from unifiedsciere.paper_map.layout_knn import compute_knn_layout
from unifiedsciere.paper_map.layout_umap import compute_umap

ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT / "configs" / "paper_map" / "paper_map_config.yaml"

COLOR_BY_OPTIONS = [
    "dataset_detail",
    "dataset",
    "year",
    "article_type",
    "outlet_type",
    "outlet_topic",
    "outlet_abbr",
    "split",
]


@st.cache_data
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


@st.cache_data
def load_data():
    cfg = load_config()
    data_dir = ROOT / cfg["artifacts_dir"]
    df = pd.read_parquet(data_dir / "paper_map.parquet")

    # Merge rich metadata
    meta_df = read_as_dataframe()
    # title already in parquet — exclude from merge to avoid suffix
    extra_cols = [
        "dataset",
        "split",
        "authors",
        "year",
        "venue",
        "article_type",
        "doi",
        "arxiv_id",
        "outlet_name",
        "outlet_abbr",
        "outlet_type",
        "outlet_topic",
        "selection",
    ]
    merge_cols = [c for c in extra_cols if c in meta_df.columns]
    df = df.merge(meta_df[["doc_id"] + merge_cols], on="doc_id", how="left")

    # Build dataset_detail: split gsap into gsap-huggingface / gsap-arxiv-ml
    selection_map = {
        "huggingface_selection": "gsap-huggingface",
        "arxiv_random_selection": "gsap-arxiv-ml",
    }
    df["dataset_detail"] = df.apply(
        lambda r: selection_map.get(r["selection"], r["dataset"])
        if r["dataset"] == "gsap"
        else r["dataset"],
        axis=1,
    )

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


def _hover_template():
    return (
        "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
        "%{customdata[2]}–%{customdata[3]}<br>"
        "%{customdata[4]}–%{customdata[5]}: %{customdata[6]}"
        "<extra></extra>"
    )


def _hover_customdata(df):
    """Build customdata array: title, year, outlet_abbr, outlet_type, dataset, split, doc_id."""
    cols = ["title", "year", "outlet_abbr", "outlet_type", "dataset", "split", "doc_id"]
    return df[cols].fillna("").astype(str).values


DATASET_SYMBOLS = {
    "gsap": "circle",
    "gsap-huggingface": "circle",
    "gsap-arxiv-ml": "triangle-up",
    "scier": "square",
    "scinlp": "diamond",
}


def make_scatter(df, x_col, y_col, color_col, show_edges=False, edges=None):
    """Build a plotly figure with colored scatter + hover."""
    # Fill missing values for the color column
    color_series = df[color_col].fillna("unknown").astype(str).replace("", "unknown")
    categories = sorted(color_series.unique(), key=str)

    # Build a color palette from Plotly qualitative colors
    palette = pc.qualitative.Plotly + pc.qualitative.D3 + pc.qualitative.Set3
    colors = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    dataset_details = sorted(df["dataset_detail"].dropna().unique())

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

    # Use continuous colorscale for year, one trace per dataset_detail for shape
    if color_col == "year":
        year_vals = pd.to_numeric(df[color_col], errors="coerce")
        for ds in dataset_details:
            ds_mask = df["dataset_detail"] == ds
            sub = df[ds_mask]
            fig.add_trace(
                go.Scatter(
                    x=sub[x_col],
                    y=sub[y_col],
                    mode="markers",
                    marker=dict(
                        size=7,
                        symbol=DATASET_SYMBOLS.get(ds, "circle"),
                        color=year_vals[ds_mask],
                        colorscale="Viridis",
                        cmin=year_vals.min(),
                        cmax=year_vals.max(),
                        colorbar=dict(title="Year")
                        if ds == dataset_details[0]
                        else None,
                        showscale=(ds == dataset_details[0]),
                        line=dict(width=0.5, color="white"),
                    ),
                    name=ds,
                    legendgroup=ds,
                    customdata=_hover_customdata(sub),
                    hovertemplate=_hover_template(),
                )
            )
    else:
        # One trace per (category, dataset_detail) for color + shape
        shown_cats = set()
        for cat in categories:
            for ds in dataset_details:
                mask = (color_series == cat) & (df["dataset_detail"] == ds)
                sub = df[mask]
                if sub.empty:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=sub[x_col],
                        y=sub[y_col],
                        mode="markers",
                        marker=dict(
                            size=7,
                            symbol=DATASET_SYMBOLS.get(ds, "circle"),
                            color=colors[cat],
                            line=dict(width=0.5, color="white"),
                        ),
                        name=str(cat),
                        legendgroup=cat,
                        showlegend=(cat not in shown_cats),
                        customdata=_hover_customdata(sub),
                        hovertemplate=_hover_template(),
                    )
                )
                shown_cats.add(cat)

    fig.update_layout(
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


st.set_page_config(page_title="UnifiedSciERE Paper Map", layout="wide")
st.title("UnifiedSciERE Paper Map")

df, embeddings_norm, edges = load_data()
cfg = load_config()

# Sidebar controls
st.sidebar.header("Layout")
layout = st.sidebar.selectbox("Layout", ["UMAP", "kNN"], index=0)

st.sidebar.header("Color")
color_by = st.sidebar.selectbox("Color by", COLOR_BY_OPTIONS, index=0)

show_edges = False

if layout == "UMAP":
    st.sidebar.subheader("UMAP parameters")
    n_neighbors = st.sidebar.slider("n_neighbors", 5, 50, cfg["umap"]["n_neighbors"])
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

tab_map, tab_papers, tab_outlets = st.tabs(["Map", "Papers", "Outlets"])

# ---------------------------------------------------------------------------
# Map tab
# ---------------------------------------------------------------------------
with tab_map:
    fig = make_scatter(df, x_col, y_col, color_by, show_edges=show_edges, edges=edges)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{len(df)} papers | Layout: {layout} | Color: {color_by}")

# ---------------------------------------------------------------------------
# Papers tab
# ---------------------------------------------------------------------------
TABLE_COLUMNS = [
    "title",
    "year",
    "dataset_detail",
    "split",
    "outlet_abbr",
    "outlet_type",
    "outlet_topic",
    "doc_id",
]

FILTER_COLUMNS = ["dataset_detail", "year", "outlet_type", "outlet_topic", "split"]
GROUP_BY_OPTIONS = ["dataset_detail", "year", "outlet_type", "outlet_topic"]

with tab_papers:
    # Search
    search_query = st.text_input("Search titles", "")

    # Filters
    filter_cols = st.columns(len(FILTER_COLUMNS))
    active_filters = {}
    for col_widget, col_name in zip(filter_cols, FILTER_COLUMNS):
        with col_widget:
            unique_vals = sorted(df[col_name].dropna().astype(str).unique())
            selected = st.multiselect(col_name, unique_vals, default=[])
            if selected:
                active_filters[col_name] = selected

    # Apply filters
    filtered = df.copy()
    if search_query:
        filtered = filtered[
            filtered["title"].str.contains(search_query, case=False, na=False)
        ]
    for col_name, selected_vals in active_filters.items():
        filtered = filtered[filtered[col_name].astype(str).isin(selected_vals)]

    st.caption(f"{len(filtered)} of {len(df)} papers")

    # Table view
    display_cols = [c for c in TABLE_COLUMNS if c in filtered.columns]
    st.dataframe(
        filtered[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

    # Grouped view
    st.markdown("---")
    group_by = st.selectbox("Group by", GROUP_BY_OPTIONS, index=0)
    grouped = filtered.groupby(
        filtered[group_by].fillna("unknown").astype(str), sort=True
    )
    for group_name, group_df in grouped:
        with st.expander(f"{group_name} ({len(group_df)} papers)"):
            for _, row in group_df.iterrows():
                year_str = str(int(row["year"])) if pd.notna(row["year"]) else ""
                outlet = row.get("outlet_abbr", "") or ""
                st.markdown(
                    f"- **{row['title']}** ({year_str}) "
                    f"— {outlet} · `{row['doc_id']}`"
                )

# ---------------------------------------------------------------------------
# Outlets tab
# ---------------------------------------------------------------------------
with tab_outlets:
    st.markdown("### Publications per Outlet and Dataset")

    # Build a label combining long name and abbreviation
    outlets_df = df.copy()
    outlets_df["outlet_label"] = outlets_df.apply(
        lambda r: (
            f"{r['outlet_name']} ({r['outlet_abbr']})"
            if pd.notna(r.get("outlet_name")) and r.get("outlet_name")
            else (r.get("outlet_abbr") or "Unknown")
        ),
        axis=1,
    )
    outlets_df["outlet_label"] = outlets_df["outlet_label"].fillna("Unknown").replace("", "Unknown")

    # Count papers per outlet_label × dataset
    counts = (
        outlets_df.groupby(["outlet_label", "dataset"])
        .size()
        .reset_index(name="count")
    )

    # Pivot so datasets become columns
    pivot = counts.pivot(index="outlet_label", columns="dataset", values="count").fillna(0).astype(int)

    # Sort by total descending
    pivot["_total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("_total", ascending=True).drop(columns="_total")

    datasets = list(pivot.columns)
    dataset_colors = {"gsap": "#636EFA", "scier": "#EF553B", "scinlp": "#00CC96"}

    fig_outlets = go.Figure()
    for ds in datasets:
        fig_outlets.add_trace(
            go.Bar(
                name=ds,
                x=pivot[ds],
                y=pivot.index,
                orientation="h",
                marker_color=dataset_colors.get(ds, "#999"),
                text=pivot[ds].where(pivot[ds] > 0),
                textposition="inside",
                insidetextanchor="middle",
            )
        )

    fig_outlets.update_layout(
        barmode="stack",
        height=max(400, len(pivot) * 28),
        margin=dict(l=20, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Number of papers",
        yaxis_title=None,
    )

    st.plotly_chart(fig_outlets, use_container_width=True)

    # Summary table
    summary = pivot.copy()
    summary["Total"] = summary.sum(axis=1)
    summary = summary.sort_values("Total", ascending=False)
    st.dataframe(summary, use_container_width=True)

# ---------------------------------------------------------------------------
# References (shared, below tabs)
# ---------------------------------------------------------------------------
st.markdown("---")

st.markdown(
    "**Visualization Methods**\n\n"
    "- **Embeddings:** Singh et al. (2023). "
    "*SciRepEval: A Multi-Format Benchmark for Scientific Document Representations.* "
    "EMNLP 2023. [arXiv:2211.13308](https://arxiv.org/abs/2211.13308)\n"
    "- **UMAP:** McInnes, Healy & Melville (2018). "
    "*UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction.* "
    "[arXiv:1802.03426](https://arxiv.org/abs/1802.03426)\n"
    "- **kNN Layout:** Fruchterman & Reingold (1991). "
    "*Graph Drawing by Force-Directed Placement.* "
    "Software: Practice and Experience, 21(11), 1129–1164. "
    "[PDF](https://emr.reingold.co/force-directed.pdf)"
)

st.markdown(
    "**Datasets**\n\n"
    "- **GSAP-ERE:** Otto et al. (2025). "
    "*GSAP-ERE: Fine-Grained Scholarly Entity and Relation Extraction Focused on Machine Learning.* "
    "AAAI 2026. [arXiv:2511.09411](https://arxiv.org/abs/2511.09411)\n"
    "- **SciER:** Zhang et al. (2024). "
    "*SciER: An Entity and Relation Extraction Dataset for Datasets, Methods, and Tasks in Scientific Documents.* "
    "EMNLP 2024. [arXiv:2410.21155](https://arxiv.org/abs/2410.21155)\n"
    "- **SciNLP:** (2025). "
    "*SciNLP: A Domain-Specific Benchmark for Full-Text Scientific Entity and Relation Extraction in NLP.* "
    "EMNLP 2025. [arXiv:2509.07801](https://arxiv.org/abs/2509.07801)"
)
