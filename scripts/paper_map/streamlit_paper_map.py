"""Entry point for the paper map Streamlit app.

Usage:
    uv run streamlit run scripts/streamlit_paper_map.py
"""

import json
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
import streamlit as st
import yaml
from sklearn.manifold import MDS

from unifiedsciere.metadata.read_metadata import load_outlets, read_as_dataframe
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

_DS_COLORS = {
    "gsap": "#636EFA",
    "gsap_hf": "#AB63FA",    # purple — HuggingFace GSAP
    "gsap_arxiv": "#19D3F3",  # cyan — arXiv GSAP
    "scier": "#EF553B",
    "scier_ood": "#FF9F1C",  # orange — SciER out-of-domain
    "scinlp": "#00CC96",
}


@st.cache_data
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


@st.cache_data
def _load_outlets_cached():
    return load_outlets()


@st.cache_data
def _load_topic_map() -> "pd.DataFrame | None":
    path = ROOT / "data" / "doc_embeddings" / "topic_map.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


@st.cache_data
def _load_full_meta_df() -> "pd.DataFrame":
    """Load full metadata including SciER-OOD (not in parquet embeddings)."""
    return read_as_dataframe()


@st.cache_data
def _load_entity_cocitation() -> dict:
    path = ROOT / "data" / "doc_embeddings" / "entity_cocitation.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


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
        "acl_id",
        "dblp_id",
        "dblp_preprint_id",
        "s2_paper_id",
        "s2_corpus_id",
        "openalex_id",
        "cited_by_count",
        "openalex_topics",
        "outlet_id",
        "outlet_name",
        "outlet_abbr",
        "outlet_type",
        "outlet_topic",
        "selection",
    ]
    merge_cols = [c for c in extra_cols if c in meta_df.columns]
    df = df.merge(meta_df[["doc_id"] + merge_cols], on="doc_id", how="left")

    # Pre-format topics as a hover-ready string: "Topic A · Topic B · Topic C"
    def _fmt_topics(t_list):
        if not isinstance(t_list, list) or not t_list:
            return ""
        return " · ".join(t["name"] for t in t_list if isinstance(t, dict) and t.get("name"))
    df["topics_str"] = df["openalex_topics"].apply(_fmt_topics) if "openalex_topics" in df.columns else ""

    # Attach OpenAlex fields per paper via outlet_id
    outlets = _load_outlets_cached()
    df["outlet_h_index"] = df["outlet_id"].map(
        lambda oid: outlets[oid].h_index if oid and oid in outlets else None
    )
    df["outlet_openalex_id"] = df["outlet_id"].map(
        lambda oid: outlets[oid].openalex_id if oid and oid in outlets else ""
    )

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

    # Load entity sets (Task / Dataset / Method per paper)
    entity_sets_path = data_dir / "entity_sets.json"
    entity_sets: dict[str, dict[str, list]] = {}
    if entity_sets_path.exists():
        with open(entity_sets_path) as f:
            entity_sets = json.load(f)

    # Load entity similarity matrices
    entity_sim_path = data_dir / "entity_similarity.npz"
    entity_sim: dict[str, object] = {}
    if entity_sim_path.exists():
        npz = np.load(entity_sim_path, allow_pickle=False)
        entity_sim = {k: npz[k] for k in npz.files}

    # Load reference similarity matrix
    ref_sim_path = data_dir / "reference_similarity.npz"
    ref_sim: dict[str, object] = {}
    if ref_sim_path.exists():
        npz = np.load(ref_sim_path, allow_pickle=False)
        ref_sim = {k: npz[k] for k in npz.files}

    return df, embeddings_norm, edges, entity_sets, entity_sim, ref_sim


def _hover_template():
    return (
        "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
        "%{customdata[2]}–%{customdata[3]}<br>"
        "%{customdata[4]}–%{customdata[5]}: %{customdata[6]}<br>"
        "<i>%{customdata[7]}</i>"
        "<extra></extra>"
    )


def _hover_customdata(df):
    """Build customdata array: title, year, outlet_abbr, outlet_type, dataset, split, doc_id, topics_str."""
    cols = ["title", "year", "outlet_abbr", "outlet_type", "dataset", "split", "doc_id", "topics_str"]
    present = [c for c in cols if c in df.columns]
    sub = df[present].fillna("").astype(str)
    # Ensure topics_str column exists even if missing
    for c in cols:
        if c not in sub.columns:
            sub[c] = ""
    return sub[cols].values


DATASET_SYMBOLS = {
    "gsap": "circle",
    "gsap-huggingface": "circle",
    "gsap-arxiv-ml": "triangle-up",
    "scier": "square",
    "scinlp": "diamond",
}


def make_scatter(df, x_col, y_col, color_col, show_edges=False, edges=None, size_arr=None):
    """Build a plotly figure with colored scatter + hover.

    Args:
        size_arr: Optional pandas Series (same index as df) with per-point marker sizes.
                  If None, a uniform size of 7 is used.
    """
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
            _sz = size_arr[ds_mask].values if size_arr is not None else 7
            fig.add_trace(
                go.Scatter(
                    x=sub[x_col],
                    y=sub[y_col],
                    mode="markers",
                    marker=dict(
                        size=_sz,
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
                _sz = size_arr[mask].values if size_arr is not None else 7
                fig.add_trace(
                    go.Scatter(
                        x=sub[x_col],
                        y=sub[y_col],
                        mode="markers",
                        marker=dict(
                            size=_sz,
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


# ---------------------------------------------------------------------------
# Outlet Map helpers
# ---------------------------------------------------------------------------

def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


@st.cache_data
def compute_outlet_map():
    """Compute MDS layout for outlets based on OpenAlex topic overlap.

    Returns:
        outlet_map_df: DataFrame with MDS coords and outlet metadata.
        shared_matrix:  n×n int array — shared topic count between outlet i and j.
        outlet_ids:     list of outlet IDs in the same row/col order as shared_matrix.
    """
    outlets = _load_outlets_cached()
    outlet_list = list(outlets.values())

    # Always include the manual outlet_topic annotation as a synthetic topic so it
    # contributes to similarity for every outlet.  For outlets without OpenAlex
    # topics this is the sole signal; for enriched outlets it adds a shared anchor
    # that pulls topically similar outlets closer regardless of fine-grained topic overlap.
    topic_sets = [
        set(o.openalex_topics) | ({f"__manual__{o.outlet_topic}"} if o.outlet_topic else set())
        for o in outlet_list
    ]
    n = len(outlet_list)

    shared = np.zeros((n, n), dtype=int)
    dissim = np.ones((n, n))
    for i in range(n):
        for j in range(i, n):
            inter = len(topic_sets[i] & topic_sets[j])
            union = len(topic_sets[i] | topic_sets[j])
            shared[i, j] = shared[j, i] = inter
            jac = inter / union if union else (1.0 if i == j else 0.0)
            dissim[i, j] = dissim[j, i] = 1.0 - jac

    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42, n_init=4)
    coords = mds.fit_transform(dissim)

    outlet_ids = []
    rows = []
    for i, o in enumerate(outlet_list):
        outlet_ids.append(o.id)
        rows.append(
            {
                "outlet_id": o.id,
                "name": o.name,
                "abbr": o.abbr or o.name[:12],
                "outlet_type": o.outlet_type or "unknown",
                "outlet_topic": o.outlet_topic or "unknown",
                "h_index": o.h_index,
                "i10_index": o.i10_index,
                "works_count": o.works_count,
                "cited_by_count": o.cited_by_count,
                "mean_citedness_2yr": o.mean_citedness_2yr,
                "openalex_id": o.openalex_id,
                "n_topics": len(o.openalex_topics),
                "topics_preview": (
                    "<br>".join(o.openalex_topics[:3])
                    if o.openalex_topics
                    else f"(manual: {o.outlet_topic})" if o.outlet_topic else "—"
                ),
                "x": coords[i, 0],
                "y": coords[i, 1],
            }
        )
    return pd.DataFrame(rows), shared, outlet_ids


def _build_edge_traces(outlet_map_df: pd.DataFrame, shared_matrix, outlet_ids, min_shared: int):
    """Return a list of Plotly traces drawing edges between outlet pairs.

    Edges are grouped into three width tiers based on shared topic count.
    """
    id_to_row = outlet_map_df.set_index("outlet_id")[["x", "y"]]
    max_shared = int(shared_matrix.max()) if shared_matrix.max() > 0 else 1
    n = len(outlet_ids)

    # Bucket edges: thin / medium / strong
    buckets = {
        "thin":   {"ex": [], "ey": [], "width": 0.6, "alpha": 0.18},
        "medium": {"ex": [], "ey": [], "width": 1.4, "alpha": 0.30},
        "strong": {"ex": [], "ey": [], "width": 2.5, "alpha": 0.50},
    }

    for i in range(n):
        for j in range(i + 1, n):
            s = int(shared_matrix[i, j])
            if s < min_shared:
                continue
            oid_i, oid_j = outlet_ids[i], outlet_ids[j]
            if oid_i not in id_to_row.index or oid_j not in id_to_row.index:
                continue
            x0, y0 = id_to_row.loc[oid_i, "x"], id_to_row.loc[oid_i, "y"]
            x1, y1 = id_to_row.loc[oid_j, "x"], id_to_row.loc[oid_j, "y"]
            frac = s / max_shared
            if frac < 0.33:
                bucket = "thin"
            elif frac < 0.66:
                bucket = "medium"
            else:
                bucket = "strong"
            b = buckets[bucket]
            b["ex"].extend([x0, x1, None])
            b["ey"].extend([y0, y1, None])

    traces = []
    for bname, b in buckets.items():
        if not b["ex"]:
            continue
        traces.append(
            go.Scatter(
                x=b["ex"],
                y=b["ey"],
                mode="lines",
                line=dict(width=b["width"], color=f"rgba(100,100,100,{b['alpha']})"),
                hoverinfo="skip",
                showlegend=False,
                name=f"edge-{bname}",
            )
        )
    return traces


def make_outlet_map(
    outlet_map_df: pd.DataFrame,
    color_col: str,
    size_col: str | None,
    edge_traces: list | None = None,
    grey_zeros_col: str | None = None,
    color_map: dict | None = None,
) -> go.Figure:
    # Determine which rows should be greyed out (zero count in the selected dataset col)
    if grey_zeros_col and grey_zeros_col in outlet_map_df.columns:
        is_zero = pd.to_numeric(outlet_map_df[grey_zeros_col], errors="coerce").fillna(0) == 0
    else:
        is_zero = pd.Series([False] * len(outlet_map_df), index=outlet_map_df.index)

    color_series = outlet_map_df[color_col].fillna("unknown").astype(str).replace("", "unknown")
    categories = sorted(color_series.unique(), key=str)
    if color_map:
        palette = pc.qualitative.Plotly + pc.qualitative.D3 + pc.qualitative.Set3
        colors = {cat: color_map.get(cat, palette[i % len(palette)]) for i, cat in enumerate(categories)}
    else:
        palette = pc.qualitative.Plotly + pc.qualitative.D3 + pc.qualitative.Set3
        colors = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    # Normalise marker size (only over non-zero rows to avoid zero dominating the scale)
    if size_col and size_col in outlet_map_df.columns:
        raw = pd.to_numeric(outlet_map_df[size_col], errors="coerce").fillna(0)
        active = raw[~is_zero]
        vmin = active.min() if not active.empty else 0
        vmax = active.max() if not active.empty else 1
        sizes = 10 + 30 * ((raw - vmin) / (vmax - vmin + 1e-9))
        sizes[is_zero] = 8  # uniform small dot for greyed-out outlets
    else:
        sizes = pd.Series([18] * len(outlet_map_df), index=outlet_map_df.index)

    fig = go.Figure()

    # Graph edges drawn first so they sit behind the nodes
    for trace in (edge_traces or []):
        fig.add_trace(trace)

    # Grey-out trace first (drawn behind coloured nodes)
    grey_sub = outlet_map_df[is_zero]
    if not grey_sub.empty:
        fig.add_trace(
            go.Scatter(
                x=grey_sub["x"],
                y=grey_sub["y"],
                mode="markers+text",
                marker=dict(
                    size=sizes[is_zero].tolist(),
                    color="rgba(180,180,180,0.4)",
                    line=dict(width=0.5, color="rgba(150,150,150,0.3)"),
                ),
                text=grey_sub["abbr"],
                textposition="top center",
                textfont=dict(size=9, color="rgba(160,160,160,0.6)"),
                name="no papers (filtered dataset)",
                legendgroup="__grey__",
                showlegend=True,
                customdata=grey_sub[
                    ["name", "h_index", "works_count", "outlet_type", "topics_preview", "openalex_id", "# papers (total)"]
                ].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b> <i>(0 papers in selected dataset)</i><br>"
                    "Papers (total): %{customdata[6]}<br>"
                    "H-index: %{customdata[1]}<br>"
                    "Works: %{customdata[2]}<br>"
                    "Type: %{customdata[3]}<br>"
                    "Topics: %{customdata[4]}"
                    "<extra></extra>"
                ),
            )
        )

    # Coloured traces for outlets with non-zero count
    shown = set()
    for cat in categories:
        mask = (color_series == cat) & (~is_zero)
        sub = outlet_map_df[mask]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["x"],
                y=sub["y"],
                mode="markers+text",
                marker=dict(
                    size=sizes[mask].tolist(),
                    color=colors[cat],
                    line=dict(width=1, color="white"),
                    opacity=0.85,
                ),
                text=sub["abbr"],
                textposition="top center",
                textfont=dict(size=10),
                name=cat,
                legendgroup=cat,
                showlegend=(cat not in shown),
                customdata=sub[
                    ["name", "h_index", "works_count", "outlet_type", "topics_preview", "openalex_id", "# papers (total)"]
                ].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Papers (total): %{customdata[6]}<br>"
                    "H-index: %{customdata[1]}<br>"
                    "Works: %{customdata[2]}<br>"
                    "Type: %{customdata[3]}<br>"
                    "Topics: %{customdata[4]}<br>"
                    "OpenAlex: %{customdata[5]}"
                    "<extra></extra>"
                ),
            )
        )
        shown.add(cat)

    fig.update_layout(
        height=720,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

st.set_page_config(page_title="UnifiedSciERE Paper Map", layout="wide")
st.markdown(
    "<h3 style='margin-top:0; margin-bottom:0.25rem;'>UnifiedSciERE \u2014 Paper &amp; Outlet Explorer</h3>",
    unsafe_allow_html=True,
)

df, embeddings_norm, edges, entity_sets, entity_sim, ref_sim = load_data()
cfg = load_config()

PAGES = ["ERE-Datasets", "Paper Map", "Paper List", "Outlet Map", "Outlet List", "Topic Map", "Entity Map"]

# ---------------------------------------------------------------------------
# Sidebar \u2014 navigation + per-page controls
# ---------------------------------------------------------------------------
page = st.sidebar.radio("Page", PAGES, label_visibility="collapsed")


# Defaults (defined unconditionally so all code paths work)
layout = "UMAP"
color_by = COLOR_BY_OPTIONS[0]
show_edges = False
x_col, y_col = "x_umap", "y_umap"
entity_type = "combined"
entity_edge_threshold = 0.2
om_color = "outlet_type"
om_size = "# papers (total)"
show_graph = True
min_shared = 3

_ENTITY_LAYOUT_OPTIONS = [
    "Entity — Combined",
    "Entity — Task",
    "Entity — Dataset",
    "Entity — Method",
    "Entity Spring — Combined",
    "Entity Spring — Task",
    "Entity Spring — Dataset",
    "Entity Spring — Method",
    "Bibliographic Coupling",
    "Topic UMAP",
]
_ENTITY_COL_MAP = {
    "Entity — Combined":        ("x_entity_combined", "y_entity_combined"),
    "Entity — Task":            ("x_entity_task",     "y_entity_task"),
    "Entity — Dataset":         ("x_entity_dataset",  "y_entity_dataset"),
    "Entity — Method":          ("x_entity_method",   "y_entity_method"),
    "Entity Spring — Combined": ("x_spring_combined", "y_spring_combined"),
    "Entity Spring — Task":     ("x_spring_task",     "y_spring_task"),
    "Entity Spring — Dataset":  ("x_spring_dataset",  "y_spring_dataset"),
    "Entity Spring — Method":   ("x_spring_method",   "y_spring_method"),
    "Bibliographic Coupling":   ("x_spring_refs",     "y_spring_refs"),
    "Topic UMAP":               ("x_topic_umap",      "y_topic_umap"),
}

if page == "Paper Map":
    st.sidebar.header("Layout")
    layout = st.sidebar.selectbox(
        "Layout", ["UMAP", "kNN"] + _ENTITY_LAYOUT_OPTIONS, index=0
    )

    st.sidebar.header("Color")
    color_by = st.sidebar.selectbox("Color by", COLOR_BY_OPTIONS, index=0)

    st.sidebar.header("Size")
    pm_size = st.sidebar.selectbox(
        "Size by", ["(uniform)", "cited_by_count (log)"], key="pm_size"
    )

    show_edges = False

    show_ref_edges = False
    umap_ref_threshold = 0.1
    ref_power = 2.0
    ref_min_sim = 0.0
    ref_recompute = False
    _is_topic_umap = False

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

        if ref_sim:
            st.sidebar.subheader("Bibliographic coupling edges")
            show_ref_edges = st.sidebar.checkbox(
                "Show bibliographic coupling edges", value=False, key="umap_ref_edges"
            )
            if show_ref_edges:
                umap_ref_threshold = st.sidebar.slider(
                    "Min. Jaccard similarity", min_value=0.01, max_value=1.0,
                    value=0.1, step=0.01, key="umap_ref_thresh",
                )

        x_col, y_col = "x_umap", "y_umap"

    elif layout == "kNN":
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

    else:  # Entity layout (MDS or Spring), Reference Coupling, or Topic UMAP
        x_col, y_col = _ENTITY_COL_MAP[layout]
        _is_ref_coupling = layout == "Bibliographic Coupling"
        _is_topic_umap = layout == "Topic UMAP"
        _is_spring = layout.startswith("Entity Spring")
        if _is_ref_coupling:
            entity_type = "combined"
            st.sidebar.caption(
                "Spring layout (Fruchterman\u2013Reingold) based on **bibliographic coupling** "
                "(Jaccard similarity of OpenAlex reference lists). "
                "Papers citing many of the same works are pulled together. "
                "43 papers without references are excluded."
            )
            if ref_sim:
                st.sidebar.subheader("Layout parameters")
                ref_power = st.sidebar.slider(
                    "Similarity power (α)",
                    min_value=1.0, max_value=5.0, value=2.0, step=0.5,
                    key="ref_power",
                    help="Raise Jaccard weights to this power before layout. "
                         "Higher values sharpen contrast: strongly connected papers "
                         "cluster tighter, weak links nearly vanish.",
                )
                ref_min_sim = st.sidebar.slider(
                    "Min. Jaccard for edge",
                    min_value=0.0, max_value=0.3, value=0.0, step=0.01,
                    key="ref_min_sim",
                    help="Drop edges below this raw Jaccard threshold before applying the power.",
                )
                ref_recompute = st.sidebar.button("Recompute layout", key="ref_recompute")
        elif _is_topic_umap:
            entity_type = "combined"
            st.sidebar.caption(
                "UMAP layout based on **OpenAlex topic scores**. "
                "Each paper is represented as a weighted topic vector; "
                "topically similar papers cluster together. "
                "Run `compute_topic_layout.py` to update."
            )
        else:
            entity_type = " — ".join(layout.split(" — ")[1:]).lower()
            if _is_spring:
                st.sidebar.caption(
                    f"Spring layout (Fruchterman\u2013Reingold) on **{entity_type}** "
                    "entity Jaccard similarity graph. "
                    "Papers frequently sharing the same entities are pulled together."
                )
            else:
                st.sidebar.caption(
                    "Position based on Jaccard similarity of unified "
                    f"**{entity_type}** annotations (MDS). "
                    "Papers sharing more annotated entities cluster together."
                )
        show_edges = st.sidebar.checkbox("Show similarity edges", value=True, key="entity_edges")
        if show_edges:
            entity_edge_threshold = st.sidebar.slider(
                "Min. Jaccard for edge", min_value=0.05, max_value=1.0,
                value=0.2, step=0.05, key="entity_edge_thresh",
            )

elif page == "Outlet Map":
    st.sidebar.header("Outlet Map")
    om_color = st.sidebar.selectbox(
        "Color by", ["outlet_type", "outlet_topic", "dominant dataset"], key="om_color"
    )
    om_size = st.sidebar.selectbox(
        "Size by",
        [
            "# papers (total)",
            "h_index",
            "works_count",
            "cited_by_count",
            "mean_citedness_2yr",
            "# GSAP papers",
            "# SciER papers",
            "# SciNLP papers",
            "(uniform)",
        ],
        key="om_size",
    )
    show_graph = st.sidebar.checkbox("Show topic-overlap graph", value=True, key="om_graph")
    if show_graph:
        min_shared = st.sidebar.slider(
            "Min. shared topics for edge", min_value=1, max_value=15, value=3,
            key="om_min_shared",
        )
    else:
        min_shared = 1

# Entity Map sidebar defaults
em_etype = "Task"
em_layout = "MDS"
em_show_edges = True
em_edge_threshold = 0.85
em_min_cocit = 2

if page == "Topic Map":
    st.sidebar.header("Topic Map")

if page == "Entity Map":
    st.sidebar.header("Entity Map")
    em_layout = st.sidebar.radio("Layout", ["MDS", "Spring"], key="em_layout")
    em_show_edges = st.sidebar.checkbox("Show co-citation edges", value=True, key="em_edges")
    if em_show_edges:
        if em_layout == "MDS":
            em_edge_threshold = st.sidebar.slider(
                "Min. proximity for edge", min_value=0.05, max_value=1.0,
                value=0.85, step=0.05, key="em_edge_thresh",
            )
        else:
            em_min_cocit = st.sidebar.slider(
                "Min. co-citation count for edge", min_value=1, max_value=20,
                value=2, step=1, key="em_min_cocit",
            )

# ---------------------------------------------------------------------------
# Paper Map page
# ---------------------------------------------------------------------------
if page == "Paper Map":
    _is_entity_layout = layout in _ENTITY_LAYOUT_OPTIONS

    # For entity layouts: exclude papers with no annotations / no references
    _plot_df = df
    _excluded_df = pd.DataFrame()
    if _is_entity_layout:
        if _is_ref_coupling:
            # Exclude papers without reference coupling coordinates
            _has_ent_mask = df["x_spring_refs"].notna()
        elif _is_topic_umap:
            # Exclude papers without topic UMAP coordinates (no topic data)
            _has_ent_mask = df["x_topic_umap"].notna() if "x_topic_umap" in df.columns else pd.Series(False, index=df.index)
        elif entity_sets:
            _etype_keys_check = (
                ["Task", "Dataset", "Method"] if entity_type == "combined"
                else [entity_type.capitalize()]
            )
            def _has_entities(doc_id):
                sets = entity_sets.get(doc_id, {})
                return any(sets.get(k) for k in _etype_keys_check)
            _has_ent_mask = df["doc_id"].map(_has_entities)
        else:
            _has_ent_mask = pd.Series(True, index=df.index)
        _plot_df = df[_has_ent_mask].copy()
        _excluded_df = df[~_has_ent_mask].copy()

    # Live-recompute Reference Coupling layout with power-transformed weights
    if _is_entity_layout and _is_ref_coupling and ref_recompute and ref_sim:
        with st.spinner("Recomputing spring layout…"):
            _rids = list(ref_sim["doc_ids"].astype(str))
            _rmat = ref_sim["sim"]
            _rn = len(_rids)
            _G = nx.Graph()
            _G.add_nodes_from(range(_rn))
            _ri, _rj = np.where(np.triu(_rmat > ref_min_sim, 1))
            for _ii, _jj in zip(_ri, _rj):
                _G.add_edge(int(_ii), int(_jj), weight=float(_rmat[_ii, _jj] ** ref_power))
            _rpos = nx.spring_layout(_G, weight="weight", seed=42, iterations=200)
            _rcoords = {_rids[i]: (float(_rpos[i][0]), float(_rpos[i][1])) for i in range(_rn)}
        _plot_df = _plot_df.copy()
        _plot_df["x_spring_refs"] = _plot_df["doc_id"].map(
            lambda d: _rcoords[d][0] if d in _rcoords else float("nan")
        )
        _plot_df["y_spring_refs"] = _plot_df["doc_id"].map(
            lambda d: _rcoords[d][1] if d in _rcoords else float("nan")
        )

    # Build reference coupling edges for UMAP view
    _active_edges = edges  # default: kNN edges
    if layout == "UMAP" and show_ref_edges and ref_sim:
        _ref_doc_ids = list(ref_sim["doc_ids"].astype(str))
        _ref_mat = ref_sim["sim"]
        _upper = np.triu(_ref_mat, 1)
        _ii, _jj = np.where(_upper >= umap_ref_threshold)
        _active_edges = [
            {"source": _ref_doc_ids[i], "target": _ref_doc_ids[j],
             "weight": float(_ref_mat[i, j])}
            for i, j in zip(_ii, _jj)
        ]
        show_edges = True  # tell make_scatter to draw them

    # Build entity similarity edges when in entity layout mode
    if _is_entity_layout and not _is_ref_coupling and show_edges and entity_sim:
        _sim_key = f"sim_{entity_type}"
        _sim_mat = entity_sim.get(_sim_key)
        _sim_doc_ids = list(entity_sim.get("doc_ids", np.array([])).astype(str))
        if _sim_mat is not None and len(_sim_doc_ids):
            _thresh = entity_edge_threshold
            _plot_ids = set(_plot_df["doc_id"].tolist())
            # Vectorised: find upper-triangle indices above threshold
            _upper = np.triu(_sim_mat, 1)
            _ii, _jj = np.where(_upper >= _thresh)
            _active_edges = [
                {"source": _sim_doc_ids[i], "target": _sim_doc_ids[j],
                 "weight": float(_sim_mat[i, j])}
                for i, j in zip(_ii, _jj)
                if _sim_doc_ids[i] in _plot_ids and _sim_doc_ids[j] in _plot_ids
            ]

    # Compute per-paper marker sizes (log-scaled citation count)
    _size_arr = None
    if pm_size == "cited_by_count (log)" and "cited_by_count" in _plot_df.columns:
        _raw = pd.to_numeric(_plot_df["cited_by_count"], errors="coerce").fillna(0)
        _log = np.log1p(_raw)
        _lo, _hi = _log.min(), _log.max()
        _size_arr = (4 + 14 * (_log - _lo) / (_hi - _lo)) if _hi > _lo else pd.Series(7.0, index=_plot_df.index)

    fig = make_scatter(_plot_df, x_col, y_col, color_by, show_edges=show_edges, edges=_active_edges, size_arr=_size_arr)
    st.plotly_chart(fig)
    _edge_info = (
        f" | {len(_active_edges)} ref-coupling edges"
        if layout == "UMAP" and show_ref_edges
        else f" | {len(_active_edges)} edges" if _is_entity_layout and show_edges
        else ""
    )
    st.caption(
        f"{len(_plot_df)} papers shown | {len(_excluded_df)} excluded (no annotations) "
        f"| Layout: {layout} | Color: {color_by}{_edge_info}"
        if _is_entity_layout
        else f"{len(_plot_df)} papers | Layout: {layout} | Color: {color_by}{_edge_info}"
    )

    # Entity annotation summary + excluded papers list
    if _is_entity_layout and entity_sets:
        _etype_keys = (
            ["Task", "Dataset", "Method"] if entity_type == "combined"
            else [entity_type.capitalize()]
        )

        with st.expander("Top annotated entities"):
            _freq: Counter = Counter()
            for doc_id, sets in entity_sets.items():
                for ek in _etype_keys:
                    for txt in sets.get(ek, []):
                        _freq[(ek, txt)] += 1
            _freq_df = pd.DataFrame(
                [{"Type": k, "Entity": v, "# Papers": cnt}
                 for (k, v), cnt in _freq.most_common(50)],
            )
            st.dataframe(_freq_df, hide_index=True, height=300)

        if not _excluded_df.empty:
            _etype_display = " / ".join(_etype_keys)
            with st.expander(
                f"Excluded papers — no {_etype_display} annotations ({len(_excluded_df)})"
            ):
                _excl_cols = ["doc_id", "title", "year", "dataset_detail", "outlet_abbr"]
                _excl_present = [c for c in _excl_cols if c in _excluded_df.columns]

                # Show per-type entity counts for excluded papers
                for ek in ["Task", "Dataset", "Method"]:
                    _col = f"n_{ek.lower()}_ann"
                    _excluded_df[_col] = _excluded_df["doc_id"].map(
                        lambda did, k=ek: len(entity_sets.get(did, {}).get(k, []))
                    )
                _excl_present += [f"n_{ek.lower()}_ann" for ek in ["Task", "Dataset", "Method"]]

                st.dataframe(
                    _excluded_df[_excl_present].reset_index(drop=True),
                    hide_index=True,
                )

# ---------------------------------------------------------------------------
# Papers page
# ---------------------------------------------------------------------------
TABLE_COLUMNS = [
    "title",
    "year",
    "cited_by_count",
    "dataset_detail",
    "split",
    "outlet_abbr",
    "outlet_type",
    "outlet_topic",
    "doc_id",
]

FILTER_COLUMNS = ["dataset_detail", "year", "outlet_type", "outlet_topic", "split"]
GROUP_BY_OPTIONS = ["dataset_detail", "year", "outlet_type", "outlet_topic"]

if page == "Paper List":
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
                    f"\u2014 {outlet} \u00b7 `{row['doc_id']}`"
                )

# ---------------------------------------------------------------------------
# Outlet Map page
# ---------------------------------------------------------------------------
if page == "Outlet Map":
    st.markdown("### Outlet Similarity Map")

    # -- Data --
    outlet_map_df, shared_matrix, outlet_ids = compute_outlet_map()

    # Attach per-dataset paper counts from the main df
    ds_counts = (
        df.dropna(subset=["outlet_id"])
        .groupby(["outlet_id", "dataset"])["doc_id"]
        .count()
        .unstack(fill_value=0)
        .reset_index()
    )
    ds_col_map = {"gsap": "# GSAP papers", "scier": "# SciER papers", "scinlp": "# SciNLP papers"}
    for ds_key, col_label in ds_col_map.items():
        if ds_key in ds_counts.columns:
            outlet_map_df = outlet_map_df.merge(
                ds_counts[["outlet_id", ds_key]].rename(columns={ds_key: col_label}),
                on="outlet_id", how="left",
            )
            outlet_map_df[col_label] = outlet_map_df[col_label].fillna(0).astype(int)
        else:
            outlet_map_df[col_label] = 0

    outlet_map_df["# papers (total)"] = (
        outlet_map_df.get("# GSAP papers", 0)
        + outlet_map_df.get("# SciER papers", 0)
        + outlet_map_df.get("# SciNLP papers", 0)
    )

    _dataset_size_cols = {"# GSAP papers", "# SciER papers", "# SciNLP papers", "# papers (total)"}
    size_col = None if om_size == "(uniform)" else om_size
    grey_zeros_col = om_size if om_size in _dataset_size_cols else None

    # -- Dominant dataset coloring (normalized by total dataset size) --
    _om_color_map = None
    if om_color == "dominant dataset":
        _tot_gsap   = max((df["dataset"] == "gsap").sum(), 1)
        _tot_scier  = max((df["dataset"] == "scier").sum(), 1)
        _tot_scinlp = max((df["dataset"] == "scinlp").sum(), 1)
        _norm_df = pd.DataFrame({
            "GSAP":   outlet_map_df["# GSAP papers"]  / _tot_gsap,
            "SciER":  outlet_map_df["# SciER papers"] / _tot_scier,
            "SciNLP": outlet_map_df["# SciNLP papers"] / _tot_scinlp,
        }, index=outlet_map_df.index)
        outlet_map_df["dominant dataset"] = _norm_df.idxmax(axis=1).where(
            outlet_map_df["# papers (total)"] > 0, other="none"
        )
        _om_color_map = {
            "GSAP":   _DS_COLORS["gsap"],
            "SciER":  _DS_COLORS["scier"],
            "SciNLP": _DS_COLORS["scinlp"],
            "none":   "rgba(180,180,180,0.4)",
        }

    # -- Graph edges --
    edge_traces = (
        _build_edge_traces(outlet_map_df, shared_matrix, outlet_ids, min_shared)
        if show_graph
        else []
    )

    # -- Figure --
    fig_om = make_outlet_map(
        outlet_map_df,
        color_col=om_color,
        size_col=size_col,
        edge_traces=edge_traces,
        grey_zeros_col=grey_zeros_col,
        color_map=_om_color_map,
    )
    st.plotly_chart(fig_om)

    n_with_topics = int((outlet_map_df["n_topics"] > 0).sum())
    n_edges = sum(
        1
        for i in range(len(outlet_ids))
        for j in range(i + 1, len(outlet_ids))
        if shared_matrix[i, j] >= (min_shared if show_graph else 999)
    )
    st.caption(
        f"{len(outlet_map_df)} outlets \u00b7 {n_with_topics} with OpenAlex topic data"
        + (f" \u00b7 {n_edges} edges (\u2265 {min_shared} shared topics)" if show_graph else "")
    )

    with st.expander("Method"):
        st.markdown(
            "**Similarity measure** Jaccard overlap of OpenAlex topics. "
            "Each outlet is described by its OpenAlex research topics; "
            "Jaccard similarity J(i,j) = |topics(i) \u2229 topics(j)| / |topics(i) \u222a topics(j)|.\n\n"
            "**2-D layout** Classical metric MDS on the pairwise dissimilarity matrix D = 1 - J.\n\n"
            "**Graph overlay** An edge is drawn between two outlets if they share at least k common "
            "OpenAlex topics. Edge thickness encodes connection strength."
        )

    with st.expander("Outlet details table"):
        detail_cols = [
            "abbr", "name", "outlet_type", "outlet_topic",
            "h_index", "i10_index", "works_count", "cited_by_count",
            "mean_citedness_2yr", "n_topics",
            "# papers (total)", "# GSAP papers", "# SciER papers", "# SciNLP papers",
        ]
        present = [c for c in detail_cols if c in outlet_map_df.columns]
        st.dataframe(
            outlet_map_df[present]
            .sort_values("h_index", ascending=False, na_position="last")
            .reset_index(drop=True),
        )

# ---------------------------------------------------------------------------
# Outlets page
# ---------------------------------------------------------------------------
if page == "Outlet List":
    outlets_meta = _load_outlets_cached()

    st.markdown(
        "Outlet metadata (H-index, citation counts, topic assignments) is retrieved from "
        "[OpenAlex](https://openalex.org) \u2014 a fully open index of the world's research. "
        "See: Priem, Piwowar & Orr (2022). *OpenAlex: A fully-open index of the world's "
        "research.* [arXiv:2205.01833](https://arxiv.org/abs/2205.01833)"
    )

    st.markdown("### Outlet H-Index Overview")

    paper_counts = (
        df.groupby("outlet_id")["doc_id"]
        .count()
        .reset_index()
        .rename(columns={"doc_id": "papers_in_corpus"})
    )
    paper_counts_by_ds = (
        df.groupby(["outlet_id", "dataset"])["doc_id"]
        .count()
        .unstack(fill_value=0)
        .reset_index()
    )

    rows = []
    for oid, outlet in outlets_meta.items():
        oa_url = (
            f"https://openalex.org/sources/{outlet.openalex_id}"
            if outlet.openalex_id
            else ""
        )
        rows.append(
            {
                "Outlet": outlet.abbr or outlet.name,
                "Name": outlet.name,
                "Type": outlet.outlet_type,
                "Topic": outlet.outlet_topic or "\u2014",
                "H-Index": outlet.h_index,
                "i10-Index": outlet.i10_index,
                "Works (OA)": outlet.works_count,
                "Citations (OA)": outlet.cited_by_count,
                "2yr Citedness": (
                    round(outlet.mean_citedness_2yr, 2)
                    if outlet.mean_citedness_2yr is not None
                    else None
                ),
                "OpenAlex": oa_url,
                "outlet_id": oid,
            }
        )

    hindex_df = pd.DataFrame(rows)
    hindex_df = hindex_df.merge(paper_counts, on="outlet_id", how="left")
    for ds in ["gsap", "scier", "scinlp"]:
        if ds in paper_counts_by_ds.columns:
            hindex_df = hindex_df.merge(
                paper_counts_by_ds[["outlet_id", ds]].rename(columns={ds: f"#{ds}"}),
                on="outlet_id",
                how="left",
            )

    hindex_df = hindex_df.drop(columns=["outlet_id"])
    hindex_df = hindex_df.rename(columns={"papers_in_corpus": "#papers"})
    hindex_df = hindex_df.sort_values("H-Index", ascending=False, na_position="last")

    st.dataframe(
        hindex_df,
        height=500,
        column_config={
            "OpenAlex": st.column_config.LinkColumn("OpenAlex", display_text="\u2197 View"),
            "H-Index": st.column_config.NumberColumn(format="%d"),
            "i10-Index": st.column_config.NumberColumn(format="%d"),
            "Works (OA)": st.column_config.NumberColumn(format="%d"),
            "Citations (OA)": st.column_config.NumberColumn(format="%d"),
            "#papers": st.column_config.NumberColumn(format="%d"),
        },
    )

    n_enriched = sum(1 for o in outlets_meta.values() if o.openalex_id)
    st.caption(
        f"{n_enriched} of {len(outlets_meta)} outlets matched in OpenAlex \u00b7 "
        "H-index and citation metrics as indexed by OpenAlex (snapshot at retrieval date)."
    )

    st.markdown("### Publications per Outlet and Dataset")

    outlets_df = df.copy()
    outlets_df["outlet_label"] = outlets_df.apply(
        lambda r: (
            f"{r['outlet_name']} ({r['outlet_abbr']})"
            if pd.notna(r.get("outlet_name")) and r.get("outlet_name")
            else (r.get("outlet_abbr") or "Unknown")
        ),
        axis=1,
    )
    outlets_df["outlet_label"] = (
        outlets_df["outlet_label"].fillna("Unknown").replace("", "Unknown")
    )

    counts = (
        outlets_df.groupby(["outlet_label", "dataset"])
        .size()
        .reset_index(name="count")
    )
    pivot = (
        counts.pivot(index="outlet_label", columns="dataset", values="count")
        .fillna(0)
        .astype(int)
    )
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
    st.plotly_chart(fig_outlets)

# ---------------------------------------------------------------------------
# ERE-Datasets page
# ---------------------------------------------------------------------------
if page == "ERE-Datasets":
    st.markdown("## ERE-Dataset Overview")

    # Use full metadata df (includes SciER-OOD which has no embeddings/parquet entry)
    _meta_df = _load_full_meta_df()

    # Sub-dataset definitions: (key, display label, row mask in _meta_df)
    _sel = _meta_df.get("selection", pd.Series("", index=_meta_df.index)).fillna("")
    _sub_datasets = [
        ("gsap_hf",    "GSAP (HF)",    (_meta_df["dataset"] == "gsap") & (_sel == "huggingface_selection")),
        ("gsap_arxiv", "GSAP (arXiv)", (_meta_df["dataset"] == "gsap") & (_sel == "arxiv_random_selection")),
        ("scier",      "SciER",        _meta_df["dataset"] == "scier"),
        ("scier_ood",  "SciER-OOD",    _meta_df["dataset"] == "scier_ood"),
        ("scinlp",     "SciNLP",       _meta_df["dataset"] == "scinlp"),
    ]

    # ── Topics (OpenAlex) ─────────────────────────────────────────────────
    st.markdown("### Topics (OpenAlex)")
    st.markdown(
        "Top paper topics per dataset, based on OpenAlex topic assignments. "
        "Each paper has up to 3 topics. Topics are ranked by total paper assignments; "
        "the union of the top 10 per dataset is shown."
    )
    _tm_df_ds = _load_topic_map()
    if _tm_df_ds is None or not all(f"n_{ds}" in _tm_df_ds.columns for ds in ["gsap", "scier", "scinlp"]):
        st.info("Topic data not available. Run `compute_topic_layout.py` first.")
    else:
        _has_topic_split = all(c in _tm_df_ds.columns for c in ["n_gsap_hf", "n_gsap_arxiv"])
        _topic_sub_ds = (
            [("gsap_hf", "GSAP (HF)"), ("gsap_arxiv", "GSAP (arXiv)"), ("scier", "SciER"), ("scinlp", "SciNLP")]
            if _has_topic_split
            else [("gsap", "GSAP"), ("scier", "SciER"), ("scinlp", "SciNLP")]
        )
        _top_per_ds: set[str] = set()
        for _ds, _ in _topic_sub_ds:
            if f"n_{_ds}" in _tm_df_ds.columns:
                _top_per_ds.update(_tm_df_ds.nlargest(5, f"n_{_ds}")["topic"].tolist())
        _topics_plot = _tm_df_ds[_tm_df_ds["topic"].isin(_top_per_ds)].copy()
        _topics_plot = _topics_plot.sort_values("n_papers", ascending=False)
        _topic_fig = go.Figure()
        for _ds, _ds_label in _topic_sub_ds:
            _topic_fig.add_trace(go.Bar(
                name=_ds_label,
                x=_topics_plot["topic"],
                y=_topics_plot[f"n_{_ds}"],
                marker_color=_DS_COLORS.get(_ds, "#888"),
                hovertemplate=f"<b>%{{x}}</b><br>{_ds_label}: %{{y}} papers<extra></extra>",
            ))
        _topic_fig.update_layout(
            barmode="group",
            height=460,
            xaxis=dict(tickangle=-35, tickfont=dict(size=11)),
            yaxis_title="# Papers",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=20, b=160),
        )
        st.plotly_chart(_topic_fig, use_container_width=True)

    # ── Publication Years ─────────────────────────────────────────────────
    st.markdown("### Publication Years")
    _year_df = _meta_df[_meta_df["year"].notna()].copy()
    _year_df["year"] = _year_df["year"].astype(int)
    _all_years = sorted(_year_df["year"].unique())
    _year_fig = go.Figure()
    for _ds_key, _ds_label, _mask in _sub_datasets:
        _sub = _year_df[_mask[_year_df.index]]
        _counts = _sub.groupby("year")["doc_id"].count().reindex(_all_years, fill_value=0)
        _year_fig.add_trace(go.Bar(
            name=_ds_label,
            x=_all_years,
            y=_counts.values,
            marker_color=_DS_COLORS.get(_ds_key, "#888"),
        ))
    _year_fig.update_layout(
        barmode="group",
        height=360,
        xaxis_title="Year",
        yaxis_title="# Papers",
        xaxis=dict(tickmode="linear", dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(_year_fig)

    # ── Citation Counts ───────────────────────────────────────────────────
    st.markdown("### Citation Counts (OpenAlex)")
    _cit_df = _meta_df[_meta_df["cited_by_count"].notna()].copy()
    _cit_df["cited_by_count"] = pd.to_numeric(_cit_df["cited_by_count"], errors="coerce")
    _cit_bins = [0, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, float("inf")]
    _cit_labels = ["0", "1–2", "3–9", "10–29", "30–99", "100–299", "300–999", "1k–3k", "3k–10k", "10k+"]
    _cit_df["_bin"] = pd.cut(_cit_df["cited_by_count"], bins=_cit_bins, labels=_cit_labels, right=False)
    _cit_fig = go.Figure()
    for _ds_key, _ds_label, _mask in _sub_datasets:
        _sub = _cit_df[_mask[_cit_df.index]]
        _counts = _sub["_bin"].value_counts().reindex(_cit_labels, fill_value=0)
        _cit_fig.add_trace(go.Bar(
            name=_ds_label,
            x=_cit_labels,
            y=_counts.values,
            marker_color=_DS_COLORS.get(_ds_key, "#888"),
        ))
    _cit_fig.update_layout(
        barmode="group",
        height=360,
        xaxis_title="Citations (log bins)",
        yaxis_title="# Papers",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(_cit_fig)
    st.caption(
        f"{len(_cit_df)} of {len(_meta_df)} papers have citation data. "
        f"Median: {int(_cit_df['cited_by_count'].median())} · "
        f"Max: {int(_cit_df['cited_by_count'].max()):,}"
    )

    # ── Outlet Types ──────────────────────────────────────────────────────
    st.markdown("### Outlet Types")
    _otype_col = "outlet_type"
    _otype_vals = (
        _meta_df[_otype_col].fillna("Unknown").replace("", "Unknown")
        if _otype_col in _meta_df.columns
        else pd.Series(["Unknown"] * len(_meta_df), index=_meta_df.index)
    )
    _otype_vals = _otype_vals.replace("preprint", "preprint\n(unmatched)")
    _all_otypes = sorted(_otype_vals.unique(), key=lambda v: (1 if v == "book" else 0, v))
    _otype_fig = go.Figure()
    for _ds_key, _ds_label, _mask in _sub_datasets:
        _counts = _otype_vals[_mask].value_counts().reindex(_all_otypes, fill_value=0)
        _otype_fig.add_trace(go.Bar(
            name=_ds_label,
            x=_all_otypes,
            y=_counts.values,
            marker_color=_DS_COLORS.get(_ds_key, "#888"),
            hovertemplate=f"<b>%{{x}}</b><br>{_ds_label}: %{{y}} papers<extra></extra>",
        ))
    _otype_fig.update_layout(
        barmode="group",
        height=360,
        xaxis_title="Outlet type",
        yaxis_title="# Papers",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(_otype_fig, use_container_width=True)

    # ── Outlets ───────────────────────────────────────────────────────────
    st.markdown("### Outlets")
    st.markdown(
        "Top 5 outlets per sub-dataset (by paper count), plus all remaining papers grouped as "
        "\"Other outlets\"."
    )
    _outlet_col = "outlet_abbr" if "outlet_abbr" in _meta_df.columns else "outlet_id"
    _outlet_base = (
        _meta_df[_outlet_col].fillna("").replace("", "Other outlets")
        .replace("arXiv", "arXiv (not matchable)")
    )
    _top_outlets: set[str] = set()
    for _ds_key, _ds_label, _mask in _sub_datasets:
        _sub_labels = _outlet_base[_mask]
        _top5 = (
            _sub_labels[_sub_labels != "Other outlets"]
            .value_counts()
            .head(5)
            .index.tolist()
        )
        _top_outlets.update(_top5)
    _plot_labels = _outlet_base.where(_outlet_base.isin(_top_outlets), "Other outlets")
    _outlet_order = (
        _plot_labels[_plot_labels != "Other outlets"]
        .value_counts()
        .index.tolist()
    ) + ["Other outlets"]
    _outlet_fig = go.Figure()
    for _ds_key, _ds_label, _mask in _sub_datasets:
        _counts = _plot_labels[_mask].value_counts()
        _y = [int(_counts.get(lbl, 0)) for lbl in _outlet_order]
        _outlet_fig.add_trace(go.Bar(
            name=_ds_label,
            x=_outlet_order,
            y=_y,
            marker_color=_DS_COLORS.get(_ds_key, "#888"),
            hovertemplate=f"<b>%{{x}}</b><br>{_ds_label}: %{{y}} papers<extra></extra>",
        ))
    _outlet_fig.update_layout(
        barmode="group",
        height=420,
        xaxis=dict(tickangle=-35, tickfont=dict(size=11)),
        yaxis_title="# Papers",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=20, b=140),
    )
    st.plotly_chart(_outlet_fig, use_container_width=True)

    # ── Identifier Availability ───────────────────────────────────────────
    st.markdown("### Identifier Availability")
    st.markdown(
        "How many papers in each dataset have a known identifier. "
        "DOI and DBLP show published venue only; preprint variants are shown separately."
    )
    _id_fields = {
        "arxiv_id":         "arXiv ID",
        "doi":              "DOI (published)",
        "doi_preprint":     "DOI (preprint)",
        "dblp_published":   "DBLP (published)",
        "dblp_preprint_id": "DBLP (corr)",
        "semantic_scholar": "Semantic Scholar",
        "openalex_id":      "OpenAlex ID",
        "cited_by_count":   "Citation count",
    }
    _avail_rows = []
    _avail_iter = [(k, l, m) for k, l, m in _sub_datasets] + [("total", "Total", pd.Series(True, index=_meta_df.index))]
    for _ds_key, _ds_label, _mask in _avail_iter:
        _sub = _meta_df[_mask]
        _n = len(_sub)
        _row = {"Dataset": _ds_label, "# Papers": _n}
        for _key, _label in _id_fields.items():
            if _key == "dblp_published":
                _count = _sub["dblp_id"].fillna("").astype(str).str.len().gt(0).sum() if "dblp_id" in _sub.columns else 0
            elif _key == "semantic_scholar":
                _count = (
                    (_sub["s2_paper_id"].fillna("").astype(str).str.len() > 0) |
                    (_sub["s2_corpus_id"].fillna("").astype(str).str.len() > 0)
                ).sum()
            elif _key == "cited_by_count":
                _count = _sub["cited_by_count"].notna().sum() if "cited_by_count" in _sub.columns else 0
            else:
                _col = _key if _key in _sub.columns else None
                _count = _sub[_col].fillna("").astype(str).str.len().gt(0).sum() if _col else 0
            _pct = f"{100 * _count // _n}%" if _n else "—"
            _row[_label] = f"{int(_count)} ({_pct})"
        _avail_rows.append(_row)
    _avail_df = pd.DataFrame(_avail_rows)
    st.dataframe(_avail_df, hide_index=True)

    # ── Top Annotated Tasks / Datasets / Methods ─────────────────────────
    _ec_data_ds = _load_entity_cocitation()
    _ere_ds_keys = [("gsap", "GSAP"), ("scier", "SciER"), ("scinlp", "SciNLP")]
    _ere_top_n = 15

    def _ere_entity_chart(etype: str, title: str, desc: str) -> None:
        st.markdown(f"### {title}")
        st.markdown(desc)
        if not _ec_data_ds:
            st.info("Entity co-citation data not available. Run `compute_entity_cocitation.py` first.")
            return
        _ec_ents_local = _ec_data_ds.get("entities", _ec_data_ds)
        _entries = _ec_ents_local.get(etype, [])
        if not _entries:
            st.info(f"No {etype} entities found in co-citation data.")
            return
        _selected: set[str] = set()
        for _raw_ds, _ in _ere_ds_keys:
            _srt = sorted(
                _entries,
                key=lambda e, d=_raw_ds: e.get("papers_by_ds_counts", {}).get(d, 0),
                reverse=True,
            )
            _selected.update(e["term"] for e in _srt[:_ere_top_n])
        _subset = sorted(
            [e for e in _entries if e["term"] in _selected],
            key=lambda e: e["n_papers"], reverse=True,
        )
        _labels = [e["term"] for e in _subset]
        _fig = go.Figure()
        for _raw_ds, _ds_label in _ere_ds_keys:
            _fig.add_trace(go.Bar(
                name=_ds_label,
                x=_labels,
                y=[e.get("papers_by_ds_counts", {}).get(_raw_ds, 0) for e in _subset],
                marker_color=_DS_COLORS.get(_raw_ds, "#888"),
                hovertemplate=f"<b>%{{x}}</b><br>{_ds_label}: %{{y}} papers<extra></extra>",
            ))
        _fig.update_layout(
            barmode="group",
            height=460,
            xaxis=dict(tickangle=-35, tickfont=dict(size=11)),
            yaxis_title="# Papers",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=20, b=200),
        )
        st.plotly_chart(_fig, use_container_width=True)

    _ere_note = (
        "Labels are mapped to the unified schema and abbreviations are expanded. "
        f"The union of the top {_ere_top_n} per dataset is shown."
    )
    _ere_entity_chart("Task",    "Top Annotated Tasks",    "Top Task entities from unified gold annotations, ranked by paper count. " + _ere_note)
    _ere_entity_chart("Dataset", "Top Annotated Datasets", "Top Dataset entities from unified gold annotations, ranked by paper count. " + _ere_note)
    _ere_entity_chart("Method",  "Top Annotated Methods",  "Top Method entities from unified gold annotations, ranked by paper count. " + _ere_note)

    # ── arXiv papers without venue assignment ─────────────────────────────
    st.markdown("### arXiv Papers without Venue Assignment")
    _arxiv_only = _meta_df[
        _meta_df["outlet_id"].fillna("").str.startswith("outlet_000") |
        _meta_df["outlet_id"].fillna("").eq("")
    ].copy()
    st.markdown(f"**{len(_arxiv_only)} papers** with no matched publication outlet.")
    _ao_cols = ["doc_id", "dataset", "split", "title", "year", "arxiv_id", "doi", "dblp_id", "openalex_id"]
    _ao_present = [c for c in _ao_cols if c in _arxiv_only.columns]
    st.dataframe(_arxiv_only[_ao_present].reset_index(drop=True))


# ---------------------------------------------------------------------------
# Entity Map page
# ---------------------------------------------------------------------------
if page == "Entity Map":
    st.markdown("### Entity Co-citation Map")

    # Entity type selector — three inline buttons above the figure
    em_etype = st.radio(
        "Entity type",
        ["Task", "Dataset", "Method"],
        horizontal=True,
        key="em_etype",
        label_visibility="collapsed",
    )

    _ec_data = _load_entity_cocitation()

    if not _ec_data:
        st.warning(
            "Entity co-citation data not found. "
            "Run `scripts/paper_map/compute_entity_cocitation.py` first."
        )
    else:
        # Support both old format (direct dict) and new format ({"entities":…, "edges":…})
        _ec_entities = _ec_data.get("entities", _ec_data)
        _ec_edges_all = _ec_data.get("edges", {})

        _em_entries_all = _ec_entities.get(em_etype, [])
        if not _em_entries_all:
            st.warning(f"No data for entity type '{em_etype}'.")
        else:
            # Select union of top 50 per dataset to reduce dataset-size bias
            _em_ds_keys = ["gsap", "scier", "scinlp"]
            _em_selected_terms: set[str] = set()
            for _ds_key in _em_ds_keys:
                _ds_sorted = sorted(
                    _em_entries_all,
                    key=lambda e: e.get("papers_by_ds_counts", {}).get(_ds_key, 0),
                    reverse=True,
                )
                _em_selected_terms.update(e["term"] for e in _ds_sorted[:50])
            _em_entries = [e for e in _em_entries_all if e["term"] in _em_selected_terms]

            # Build DataFrame
            _em_rows = []
            for _e in _em_entries:
                _ds = _e.get("papers_by_ds_counts", {})
                _term = _e["term"]
                # Strip spurious prepended lowercase "s" before an uppercase letter
                import re as _re
                _term = _re.sub(r"^s([A-Z])", r"\1", _term)
                _em_rows.append({
                    "term":     _term,
                    "n_papers": _e["n_papers"],
                    "corpus":   _e["corpus"],
                    "x":        _e["x"],
                    "y":        _e["y"],
                    "x_spring": _e.get("x_spring", _e["x"]),
                    "y_spring": _e.get("y_spring", _e["y"]),
                    "n_gsap":   _ds.get("gsap", 0),
                    "n_scier":  _ds.get("scier", 0),
                    "n_scinlp": _ds.get("scinlp", 0),
                })
            _em_df = pd.DataFrame(_em_rows)

            st.caption(
                f"Showing the union of the top 50 {em_etype} entities per dataset "
                f"({len(_em_df)} entities total), selected by co-citation frequency. "
                "Using a per-dataset top-50 reduces bias from dataset size differences."
            )

            # Coordinate columns for selected layout
            _xcol = "x" if em_layout == "MDS" else "x_spring"
            _ycol = "y" if em_layout == "MDS" else "y_spring"

            # Normalise marker size
            _np_vals = _em_df["n_papers"]
            _vmin, _vmax = _np_vals.min(), _np_vals.max()
            _em_sizes = 6 + 28 * ((_np_vals - _vmin) / (_vmax - _vmin + 1e-9))

            _CORPUS_COLORS = {
                "GSAP":              "#636EFA",  # blue
                "GSAP+SciER":        "#AB63FA",  # violet
                "SciER":             "#EF553B",  # red
                "SciER+SciNLP":      "#FFA15A",  # orange
                "SciNLP":            "#FECB52",  # yellow
                "GSAP+SciNLP":       "#00CC96",  # green
                "GSAP+SciER+SciNLP": "#8B4513",  # brown
            }
            _CORPUS_ORDER = [
                "GSAP", "GSAP+SciER", "SciER", "SciER+SciNLP",
                "SciNLP", "GSAP+SciNLP", "GSAP+SciER+SciNLP",
            ]

            fig_em = go.Figure()

            # Edges
            _em_n_edges = 0
            if em_show_edges:
                _xy = _em_df[[_xcol, _ycol]].values
                _ex, _ey = [], []

                if em_layout == "Spring":
                    # Use stored co-citation edge list, filter by min cocit count
                    # Build mapping: original index in _em_entries_all -> filtered index in _em_df
                    _orig_to_filtered = {
                        orig_i: filt_i
                        for filt_i, orig_i in enumerate(
                            i for i, e in enumerate(_em_entries_all)
                            if e["term"] in _em_selected_terms
                        )
                    }
                    _raw_edges = _ec_edges_all.get(em_etype, [])
                    for _edge in _raw_edges:
                        if _edge["cocit"] >= em_min_cocit:
                            _i = _orig_to_filtered.get(_edge["i"])
                            _j = _orig_to_filtered.get(_edge["j"])
                            if _i is None or _j is None:
                                continue
                            _ex += [_xy[_i, 0], _xy[_j, 0], None]
                            _ey += [_xy[_i, 1], _xy[_j, 1], None]
                            _em_n_edges += 1
                else:
                    # MDS: proximity threshold on normalised Euclidean distance
                    _dx = _xy[:, 0:1] - _xy[:, 0]
                    _dy = _xy[:, 1:2] - _xy[:, 1]
                    _dists = np.sqrt(_dx ** 2 + _dy ** 2)
                    _max_d = _dists.max() if _dists.max() > 0 else 1.0
                    _sim_proxy = 1.0 - _dists / _max_d
                    _ii, _jj = np.where(np.triu(_sim_proxy >= em_edge_threshold, 1))
                    for _i, _j in zip(_ii, _jj):
                        _ex += [_xy[_i, 0], _xy[_j, 0], None]
                        _ey += [_xy[_i, 1], _xy[_j, 1], None]
                    _em_n_edges = len(_ii)

                if _ex:
                    fig_em.add_trace(go.Scatter(
                        x=_ex, y=_ey,
                        mode="lines",
                        line=dict(width=0.5, color="rgba(150,150,150,0.25)"),
                        hoverinfo="skip",
                        showlegend=False,
                        name="edges",
                    ))

            # One trace per corpus combination
            for _corpus_label in _CORPUS_ORDER:
                _mask = _em_df["corpus"] == _corpus_label
                _sub = _em_df[_mask]
                if _sub.empty:
                    continue
                fig_em.add_trace(go.Scatter(
                    x=_sub[_xcol],
                    y=_sub[_ycol],
                    mode="markers",
                    marker=dict(
                        size=_em_sizes[_mask].tolist(),
                        color=_CORPUS_COLORS.get(_corpus_label, "#888888"),
                        line=dict(width=0.8, color="white"),
                        opacity=0.85,
                    ),
                    name=_corpus_label,
                    customdata=_sub[
                        ["term", "n_papers", "corpus", "n_gsap", "n_scier", "n_scinlp"]
                    ].values,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Publications: %{customdata[1]}<br>"
                        "Corpus: %{customdata[2]}<br>"
                        "GSAP: %{customdata[3]} \u00b7 SciER: %{customdata[4]}"
                        " \u00b7 SciNLP: %{customdata[5]}"
                        "<extra></extra>"
                    ),
                ))

            fig_em.update_layout(
                height=720,
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            )
            st.plotly_chart(fig_em)

            _em_caption = f"{len(_em_df)} {em_etype} entities \u00b7 {em_layout} layout"
            if em_show_edges and em_layout == "Spring":
                _em_caption += f" \u00b7 {_em_n_edges} edges (\u2265 {em_min_cocit} co-citations)"
            elif em_show_edges:
                _em_caption += f" \u00b7 {_em_n_edges} edges (proximity \u2265 {em_edge_threshold:.2f})"
            st.caption(_em_caption)

            with st.expander("Method"):
                st.markdown(
                    f"**Entity nodes** Top 300 {em_etype} terms from unified gold annotations "
                    "across all datasets and splits, ranked by total number of publications "
                    "in which they are annotated.\n\n"
                    "**Color** Each entity is assigned to one of 7 corpus combinations based "
                    "on which datasets (GSAP, SciER, SciNLP) annotate it.\n\n"
                    "**MDS layout** Classical metric MDS on 1 \u2212 Jaccard dissimilarity, where "
                    "Jaccard is computed on the sets of publications annotating each entity pair. "
                    "Proximity in MDS space is used for edge thresholding.\n\n"
                    "**Spring layout** Fruchterman\u2013Reingold force-directed layout. "
                    "Edge weights = raw co-citation count |papers(i) \u2229 papers(j)|. "
                    "Entities that frequently co-occur in the same papers are pulled together.\n\n"
                    "**Size** Proportional to total number of annotating publications."
                )

            with st.expander(f"{em_etype} entity details"):
                _detail_df = _em_df[
                    ["term", "corpus", "n_papers", "n_gsap", "n_scier", "n_scinlp"]
                ].copy()
                _detail_df.columns = [
                    "Term", "Corpus", "# Papers", "# GSAP", "# SciER", "# SciNLP"
                ]
                st.dataframe(
                    _detail_df.sort_values("# Papers", ascending=False).reset_index(drop=True),
                )


# ---------------------------------------------------------------------------
# Topic Map page
# ---------------------------------------------------------------------------
if page == "Topic Map":
    st.markdown("### Topic Map")
    st.markdown(
        "Each point is an OpenAlex **research topic** assigned to ≥2 papers in the corpus. "
        "Position is a UMAP layout of the topic×paper score matrix: "
        "topics that co-occur on the same papers cluster together. "
        "Run `compute_topic_layout.py` to update."
    )

    _tm_df = _load_topic_map()

    if _tm_df is None:
        st.warning(
            "Topic map data not found. "
            "Run `uv run python scripts/paper_map/compute_topic_layout.py` first."
        )
    else:
        # Sidebar controls
        _tm_has_split = all(
            c in _tm_df.columns
            for c in ["n_gsap_hf", "n_gsap_arxiv", "total_gsap_hf", "total_gsap_arxiv", "total_scier", "total_scinlp"]
        )
        _tm_color_options = ["# papers (total)", "dominant dataset", "GSAP", "SciER", "SciNLP"]
        if _tm_has_split:
            _tm_color_options = ["# papers (total)", "dominant dataset", "GSAP-HF", "GSAP-arXiv", "GSAP", "SciER", "SciNLP"]
        _tm_color_by = st.sidebar.selectbox(
            "Color by",
            _tm_color_options,
            index=1,
            key="tm_color_by",
        )
        _tm_color_scale = "Plasma"
        _tm_min_papers = st.sidebar.slider(
            "Min. papers per topic", min_value=2, max_value=20, value=2,
            key="tm_min_papers",
            help="Hide topics with fewer than this many paper assignments.",
        )
        _tm_exclude_top = st.sidebar.slider(
            "Exclude top-N topics", min_value=0, max_value=20, value=0,
            key="tm_exclude_top",
            help="Exclude the N most-assigned topics (e.g. broad umbrella categories).",
        )

        # Filter
        _tm_sorted = _tm_df.sort_values("n_papers", ascending=False).reset_index(drop=True)
        _tm_top_names = set(_tm_sorted.head(_tm_exclude_top)["topic"].tolist()) if _tm_exclude_top else set()
        _tm_plot = _tm_sorted[
            (_tm_sorted["n_papers"] >= _tm_min_papers) &
            (~_tm_sorted["topic"].isin(_tm_top_names))
        ].copy()

        if _tm_exclude_top:
            st.sidebar.caption(
                f"Excluded (top {_tm_exclude_top}): "
                + ", ".join(_tm_sorted.head(_tm_exclude_top)["topic"].tolist())
            )

        st.caption(f"Showing {len(_tm_plot)} / {len(_tm_df)} topics")

        _tm_max = int(_tm_plot["n_papers"].max()) if not _tm_plot.empty else 1
        _tm_sizes = 6 + 14 * (_tm_plot["n_papers"] - 2) / max(_tm_max - 2, 1)

        # Per-dataset columns (may be absent if parquet was built without them)
        _has_ds_cols = all(f"n_{ds}" in _tm_plot.columns for ds in ["gsap", "scier", "scinlp"])
        _has_split_cols = _has_ds_cols and all(
            c in _tm_plot.columns
            for c in ["n_gsap_hf", "n_gsap_arxiv", "total_gsap_hf", "total_gsap_arxiv", "total_scier", "total_scinlp"]
        )

        # customdata: [topic, n_total, n_gsap, n_scier, n_scinlp, n_gsap_hf, n_gsap_arxiv]
        if _has_split_cols:
            _tm_cd = _tm_plot[["topic", "n_papers", "n_gsap", "n_scier", "n_scinlp", "n_gsap_hf", "n_gsap_arxiv"]].values
        elif _has_ds_cols:
            _zero = np.zeros(len(_tm_plot), dtype=int)
            _tm_cd = np.column_stack([
                _tm_plot[["topic", "n_papers", "n_gsap", "n_scier", "n_scinlp"]].values,
                _zero, _zero,
            ])
        else:
            _zero = np.zeros(len(_tm_plot), dtype=int)
            _tm_cd = np.column_stack([
                _tm_plot[["topic", "n_papers"]].assign(n_gsap=0, n_scier=0, n_scinlp=0)[
                    ["topic", "n_papers", "n_gsap", "n_scier", "n_scinlp"]
                ].values,
                _zero, _zero,
            ])

        if _has_split_cols:
            _hover_tmpl = (
                "<b>%{customdata[0]}</b><br>"
                "Total: %{customdata[1]} papers<br>"
                "GSAP-HF: %{customdata[5]} · GSAP-arXiv: %{customdata[6]}<br>"
                "SciER: %{customdata[3]} · SciNLP: %{customdata[4]}"
                "<extra></extra>"
            )
        else:
            _hover_tmpl = (
                "<b>%{customdata[0]}</b><br>"
                "Total: %{customdata[1]} papers<br>"
                "GSAP: %{customdata[2]} · SciER: %{customdata[3]} · SciNLP: %{customdata[4]}"
                "<extra></extra>"
            )

        # Determine which topics are "active" under the current color selection
        # (i.e. have at least 1 paper in the selected dataset / total)
        if _tm_color_by == "GSAP-HF" and _has_split_cols:
            _active_mask = _tm_plot["n_gsap_hf"] > 0
        elif _tm_color_by == "GSAP-arXiv" and _has_split_cols:
            _active_mask = _tm_plot["n_gsap_arxiv"] > 0
        elif _tm_color_by in ("GSAP", "SciER", "SciNLP") and _has_ds_cols:
            _active_col = "n_" + _tm_color_by.lower()
            _active_mask = _tm_plot[_active_col] > 0
        elif _tm_color_by == "dominant dataset" and _has_ds_cols:
            _active_mask = _tm_plot[["n_gsap", "n_scier", "n_scinlp"]].sum(axis=1) > 0
        else:
            _active_mask = _tm_plot["n_papers"] > 0

        _active_plot = _tm_plot[_active_mask]
        _active_cd = _tm_cd[_active_mask.values]
        _active_sizes = _tm_sizes[_active_mask.values] if hasattr(_tm_sizes, "__getitem__") else _tm_sizes

        _tm_fig = go.Figure()

        if _tm_color_by == "dominant dataset" and _has_ds_cols:
            # Determine dominant dataset per topic using normalised counts
            if _has_split_cols and not _active_plot.empty:
                _tot = {
                    "gsap_hf":    max(int(_active_plot["total_gsap_hf"].iloc[0]), 1),
                    "gsap_arxiv": max(int(_active_plot["total_gsap_arxiv"].iloc[0]), 1),
                    "scier":      max(int(_active_plot["total_scier"].iloc[0]), 1),
                    "scinlp":     max(int(_active_plot["total_scinlp"].iloc[0]), 1),
                }
                _norm = pd.DataFrame({
                    "gsap_hf":    _active_plot["n_gsap_hf"].values / _tot["gsap_hf"],
                    "gsap_arxiv": _active_plot["n_gsap_arxiv"].values / _tot["gsap_arxiv"],
                    "scier":      _active_plot["n_scier"].values / _tot["scier"],
                    "scinlp":     _active_plot["n_scinlp"].values / _tot["scinlp"],
                })
                _dom = _norm.idxmax(axis=1).values
                _dom_groups = [
                    ("gsap_hf",    "GSAP-HF"),
                    ("gsap_arxiv", "GSAP-arXiv"),
                    ("scier",      "SciER"),
                    ("scinlp",     "SciNLP"),
                ]
            else:
                # Fallback: raw counts, original three datasets
                _dom = _active_plot[["n_gsap", "n_scier", "n_scinlp"]].idxmax(axis=1).str.replace("n_", "").values
                _dom_groups = [("gsap", "GSAP"), ("scier", "SciER"), ("scinlp", "SciNLP")]

            for _ds, _ds_label in _dom_groups:
                _mask = _dom == _ds
                _sub = _active_plot[_mask]
                if _sub.empty:
                    continue
                _tm_fig.add_trace(go.Scatter(
                    x=_sub["x_topic_umap"], y=_sub["y_topic_umap"],
                    mode="markers+text",
                    name=_ds_label,
                    text=_sub["topic"], textposition="top center", textfont=dict(size=9),
                    marker=dict(
                        size=(6 + 14 * (_sub["n_papers"] - 2) / max(_tm_max - 2, 1)),
                        color=_DS_COLORS[_ds],
                        line=dict(width=0.5, color="white"),
                    ),
                    customdata=_active_cd[_mask],
                    hovertemplate=_hover_tmpl,
                ))
        elif _tm_color_by in ("GSAP-HF", "GSAP-arXiv") and _has_split_cols:
            _ds_col = "n_gsap_hf" if _tm_color_by == "GSAP-HF" else "n_gsap_arxiv"
            _tm_fig.add_trace(go.Scatter(
                x=_active_plot["x_topic_umap"], y=_active_plot["y_topic_umap"],
                mode="markers+text",
                name=_tm_color_by,
                text=_active_plot["topic"], textposition="top center", textfont=dict(size=9),
                marker=dict(
                    size=_active_sizes,
                    color=_active_plot[_ds_col],
                    colorscale=_tm_color_scale,
                    showscale=True,
                    colorbar=dict(title=f"# {_tm_color_by} papers"),
                    line=dict(width=0.5, color="white"),
                ),
                customdata=_active_cd,
                hovertemplate=_hover_tmpl,
            ))
        elif _tm_color_by in ("GSAP", "SciER", "SciNLP") and _has_ds_cols:
            _ds_col = "n_" + _tm_color_by.lower()
            _tm_fig.add_trace(go.Scatter(
                x=_active_plot["x_topic_umap"], y=_active_plot["y_topic_umap"],
                mode="markers+text",
                name=_tm_color_by,
                text=_active_plot["topic"], textposition="top center", textfont=dict(size=9),
                marker=dict(
                    size=_active_sizes,
                    color=_active_plot[_ds_col],
                    colorscale=_tm_color_scale,
                    showscale=True,
                    colorbar=dict(title=f"# {_tm_color_by} papers"),
                    line=dict(width=0.5, color="white"),
                ),
                customdata=_active_cd,
                hovertemplate=_hover_tmpl,
            ))
        else:  # # papers (total)
            _tm_fig.add_trace(go.Scatter(
                x=_active_plot["x_topic_umap"], y=_active_plot["y_topic_umap"],
                mode="markers+text",
                text=_active_plot["topic"], textposition="top center", textfont=dict(size=9),
                marker=dict(
                    size=_active_sizes,
                    color=_active_plot["n_papers"],
                    colorscale=_tm_color_scale,
                    showscale=True,
                    colorbar=dict(title="# papers"),
                    line=dict(width=0.5, color="white"),
                ),
                customdata=_active_cd,
                hovertemplate=_hover_tmpl,
            ))

        _tm_fig.update_layout(
            height=750,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        st.plotly_chart(_tm_fig, use_container_width=True)

        with st.expander("Topic table"):
            _tm_display_cols = ["topic", "n_papers"]
            if _has_ds_cols:
                _tm_display_cols += ["n_gsap", "n_scier", "n_scinlp"]
            st.dataframe(
                _tm_plot[_tm_display_cols].rename(columns={
                    "topic": "Topic", "n_papers": "Total",
                    "n_gsap": "GSAP", "n_scier": "SciER", "n_scinlp": "SciNLP",
                }),
                hide_index=True,
                height=400,
            )


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
    "[PDF](https://emr.reingold.co/force-directed.pdf)\n"
    "- **Bibliographic Coupling:** Kessler (1963). "
    "*Bibliographic coupling between scientific papers.* "
    "American Documentation, 14(1), 10–25. "
    "[doi:10.1002/asi.5090140103](https://doi.org/10.1002/asi.5090140103)\n"
    "- **MDS (Outlet Map):** Cox & Cox (2000). "
    "*Multidimensional Scaling.* Chapman & Hall/CRC."
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

st.markdown(
    "**Outlet Metadata**\n\n"
    "- **OpenAlex:** Priem, Piwowar & Orr (2022). "
    "*OpenAlex: A fully-open index of the world's research.* "
    "[arXiv:2205.01833](https://arxiv.org/abs/2205.01833) · "
    "[openalex.org](https://openalex.org)"
)
