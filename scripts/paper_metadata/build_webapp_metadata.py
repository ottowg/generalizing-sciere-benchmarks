"""Build paper-metadata JSON for the webapp.

Reads all_papers.jsonl, outlet_info.json, topic_map.parquet, and
entity_cocitation.json, then computes all aggregations needed by
the PaperMetadata Vue component and writes them to
data/webapp_metadata.json.

Usage:
    uv run python scripts/paper_metadata/build_webapp_metadata.py
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.metadata.read_metadata import load_outlets, read_as_dataframe
from unifiedsciere.paths import ensure_output, project_root
from unifiedsciere.unification.pipeline import apply_unification_pipeline

ROOT = project_root()

DS_COLORS = {
    "gsap_hf":    "#636EFA",
    "gsap_arxiv": "#19D3F3",
    "scier":      "#EF553B",
    "scier_ood":  "#FF9F1C",
    "scinlp":     "#00CC96",
}

# ── helpers ────────────────────────────────────────────────────────────────────

def _mask_to_bool(mask: pd.Series) -> list[bool]:
    return mask.tolist()


def _counts_to_dict(series: pd.Series, index: list) -> dict:
    reindexed = series.reindex(index, fill_value=0)
    return {str(k): int(v) for k, v in reindexed.items()}


# ── entity frequency helper ────────────────────────────────────────────────────

_ERE_DATASETS = ["gsap-ere", "scier", "scinlp"]
_ERE_SPLITS   = ["train", "dev", "test"]
_ENTITY_TYPES = ["Task", "Dataset", "Method"]


def _build_entity_freq() -> dict[str, dict[str, dict[str, int]]]:
    """Return {doc_id: {etype: {normalised_term: count}}} from all unified gold data."""
    freq: dict = defaultdict(lambda: {t: Counter() for t in _ENTITY_TYPES})
    for dataset in _ERE_DATASETS:
        for split in _ERE_SPLITS:
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
            except FileNotFoundError:
                continue
            corpus, _ = apply_unification_pipeline(
                corpus, dataset, apply_to_gold=True, apply_to_predicted=False
            )
            for m in corpus.mentions:
                if m.label in _ENTITY_TYPES:
                    term = " ".join(m.text.lower().split())
                    freq[m.document_id][m.label][term] += 1
    return {
        doc_id: {etype: dict(counts) for etype, counts in etypes.items()}
        for doc_id, etypes in freq.items()
    }


# ── main ───────────────────────────────────────────────────────────────────────

def build() -> dict:
    print("Loading metadata …")
    meta_df   = read_as_dataframe()
    outlets_m = load_outlets()

    sel = meta_df.get("selection", pd.Series("", index=meta_df.index)).fillna("")

    sub_datasets = [
        ("gsap_hf",    "GSAP (HF)",    (meta_df["dataset"] == "gsap") & (sel == "huggingface_selection")),
        ("gsap_arxiv", "GSAP (arXiv)", (meta_df["dataset"] == "gsap") & (sel == "arxiv_random_selection")),
        ("scier",      "SciER",         meta_df["dataset"] == "scier"),
        ("scier_ood",  "SciER-OOD",     meta_df["dataset"] == "scier_ood"),
        ("scinlp",     "SciNLP",        meta_df["dataset"] == "scinlp"),
    ]

    result: dict = {}

    # ── Sub-dataset labels & colors ───────────────────────────────────────────
    result["sub_datasets"] = [
        {"key": k, "label": lbl, "color": DS_COLORS[k]}
        for k, lbl, _ in sub_datasets
    ]

    # ── Publication Years ─────────────────────────────────────────────────────
    print("  Publication years …")
    year_df = meta_df[meta_df["year"].notna()].copy()
    year_df["year"] = year_df["year"].astype(int)
    all_years = sorted(year_df["year"].unique().tolist())
    by_year = {}
    for k, _, mask in sub_datasets:
        sub = year_df[mask[year_df.index]]
        counts = sub.groupby("year")["doc_id"].count().reindex(all_years, fill_value=0)
        by_year[k] = [int(v) for v in counts.values]
    result["years"]   = all_years
    result["by_year"] = by_year

    # ── Citation Bins ─────────────────────────────────────────────────────────
    print("  Citation bins …")
    cit_df = meta_df[meta_df["cited_by_count"].notna()].copy()
    cit_df["cited_by_count"] = pd.to_numeric(cit_df["cited_by_count"], errors="coerce")
    cit_df = cit_df[cit_df["cited_by_count"].notna()]
    cit_bins   = [0, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, float("inf")]
    cit_labels = ["0", "1–2", "3–9", "10–29", "30–99", "100–299", "300–999", "1k–3k", "3k–10k", "10k+"]
    cit_df["_bin"] = pd.cut(cit_df["cited_by_count"], bins=cit_bins, labels=cit_labels, right=False)
    by_cit = {}
    for k, _, mask in sub_datasets:
        sub = cit_df[mask[cit_df.index]]
        counts = sub["_bin"].value_counts().reindex(cit_labels, fill_value=0)
        by_cit[k] = [int(v) for v in counts.values]
    result["citation_labels"] = cit_labels
    result["by_citation"]     = by_cit
    result["citation_stats"]  = {
        "n":      int(len(cit_df)),
        "total":  int(len(meta_df)),
        "median": int(cit_df["cited_by_count"].median()),
        "max":    int(cit_df["cited_by_count"].max()),
    }

    # ── Citations vs Year (scatter) ───────────────────────────────────────────
    print("  Citation scatter …")
    scatter_df = meta_df[meta_df["cited_by_count"].notna() & meta_df["year"].notna()].copy()
    scatter_df["cited_by_count"] = pd.to_numeric(scatter_df["cited_by_count"], errors="coerce")
    scatter_df["year"]           = scatter_df["year"].astype(int)
    scatter_df = scatter_df[scatter_df["cited_by_count"].notna()]
    import numpy as np
    from sklearn.manifold import MDS
    rng = np.random.default_rng(42)
    scatter_by_ds = {}
    for k, _, mask in sub_datasets:
        sub = scatter_df[mask[scatter_df.index]]
        if sub.empty:
            scatter_by_ds[k] = []
            continue
        jitter = rng.uniform(-0.3, 0.3, size=len(sub))
        scatter_by_ds[k] = [
            {
                "x": float(year + j),
                "y": float(cit),
                "title": str(title)[:80] if pd.notna(title) else "",
            }
            for year, cit, j, title in zip(
                sub["year"], sub["cited_by_count"], jitter,
                sub.get("title", pd.Series("", index=sub.index)).fillna("")
            )
        ]
    result["scatter"] = scatter_by_ds

    # ── Outlet Types ──────────────────────────────────────────────────────────
    print("  Outlet types …")
    otype_vals = meta_df["outlet_type"].fillna("Unknown").replace("", "Unknown") \
        if "outlet_type" in meta_df.columns \
        else pd.Series(["Unknown"] * len(meta_df), index=meta_df.index)
    all_otypes = sorted(otype_vals.unique().tolist(), key=lambda v: (1 if v == "book" else 0, v))
    by_otype = {}
    for k, _, mask in sub_datasets:
        counts = otype_vals[mask].value_counts().reindex(all_otypes, fill_value=0)
        by_otype[k] = [int(v) for v in counts.values]
    result["outlet_types"]    = all_otypes
    result["by_outlet_type"]  = by_otype

    # ── Top Outlets ───────────────────────────────────────────────────────────
    print("  Top outlets …")
    outlet_col  = "outlet_abbr" if "outlet_abbr" in meta_df.columns else "outlet_id"
    outlet_base = meta_df[outlet_col].fillna("").replace("", "Other").replace("arXiv", "arXiv (unmatched)")
    top_outlets: set[str] = set()
    for _, _, mask in sub_datasets:
        sub_lbl = outlet_base[mask]
        top5 = sub_lbl[sub_lbl != "Other"].value_counts().head(5).index.tolist()
        top_outlets.update(top5)
    plot_labels = outlet_base.where(outlet_base.isin(top_outlets), "Other")
    outlet_order = plot_labels[plot_labels != "Other"].value_counts().index.tolist() + ["Other"]
    by_outlet = {}
    for k, _, mask in sub_datasets:
        counts = plot_labels[mask].value_counts()
        by_outlet[k] = [int(counts.get(lbl, 0)) for lbl in outlet_order]
    result["top_outlet_labels"] = outlet_order
    result["by_top_outlet"]     = by_outlet

    # ── Identifier Availability ───────────────────────────────────────────────
    print("  Identifier availability …")
    id_fields = [
        ("arxiv_id",       "arXiv ID"),
        ("doi",            "DOI (published)"),
        ("doi_preprint",   "DOI (preprint)"),
        ("dblp_published", "DBLP (published)"),
        ("dblp_preprint_id", "DBLP (corr)"),
        ("semantic_scholar","Semantic Scholar"),
        ("openalex_id",    "OpenAlex ID"),
        ("cited_by_count", "Citation count"),
    ]
    avail_rows = []
    for ds_key, ds_label, mask in [*sub_datasets, ("total", "Total", pd.Series(True, index=meta_df.index))]:
        sub  = meta_df[mask]
        n    = len(sub)
        row  = {"dataset": ds_label, "n_papers": n}
        for key, label in id_fields:
            if key == "dblp_published":
                cnt = sub["dblp_id"].fillna("").astype(str).str.len().gt(0).sum() \
                    if "dblp_id" in sub.columns else 0
            elif key == "semantic_scholar":
                cnt = ((sub["s2_paper_id"].fillna("").astype(str).str.len() > 0) |
                       (sub["s2_corpus_id"].fillna("").astype(str).str.len() > 0)).sum() \
                    if "s2_paper_id" in sub.columns else 0
            elif key == "cited_by_count":
                cnt = sub["cited_by_count"].notna().sum() if "cited_by_count" in sub.columns else 0
            else:
                col = key if key in sub.columns else None
                cnt = sub[col].fillna("").astype(str).str.len().gt(0).sum() if col else 0
            pct = f"{int(100 * cnt // n)}%" if n else "—"
            row[label] = {"count": int(cnt), "pct": pct}
        avail_rows.append(row)
    result["identifier_cols"] = [lbl for _, lbl in id_fields]
    result["identifier_avail"] = avail_rows

    # ── arXiv without venue ───────────────────────────────────────────────────
    arxiv_only = meta_df[
        meta_df["outlet_id"].fillna("").str.startswith("outlet_000") |
        meta_df["outlet_id"].fillna("").eq("")
    ].copy()
    keep_cols = ["doc_id", "dataset", "split", "title", "year", "arxiv_id", "doi", "dblp_id"]
    arxiv_rows = arxiv_only[[c for c in keep_cols if c in arxiv_only.columns]].fillna("").to_dict("records")
    result["arxiv_without_venue"] = arxiv_rows

    # ── Topics (OpenAlex) ─────────────────────────────────────────────────────
    print("  Topics …")
    topic_path = ROOT / "data" / "doc_embeddings" / "topic_map.parquet"
    if topic_path.exists():
        tm = pd.read_parquet(topic_path)
        has_split = all(c in tm.columns for c in ["n_gsap_hf", "n_gsap_arxiv"])
        topic_sub_ds = (
            [("gsap_hf", "GSAP (HF)"), ("gsap_arxiv", "GSAP (arXiv)"), ("scier", "SciER"), ("scinlp", "SciNLP")]
            if has_split
            else [("gsap", "GSAP"), ("scier", "SciER"), ("scinlp", "SciNLP")]
        )
        top_topics: set[str] = set()
        for ds, _ in topic_sub_ds:
            col = f"n_{ds}"
            if col in tm.columns:
                top_topics.update(tm.nlargest(5, col)["topic"].tolist())
        subset = tm[tm["topic"].isin(top_topics)].sort_values("n_papers", ascending=False)
        result["topics"] = {
            "sub_datasets": [{"key": k, "label": l, "color": DS_COLORS.get(k, "#888")} for k, l in topic_sub_ds],
            "labels":       subset["topic"].tolist(),
            "by_ds":        {k: [int(v) for v in subset[f"n_{k}"].tolist()] if f"n_{k}" in subset.columns
                             else [0] * len(subset)
                             for k, _ in topic_sub_ds},
        }
    else:
        result["topics"] = None

    # ── Entity co-citation (Tasks / Datasets / Methods) ───────────────────────
    print("  Entity co-citation …")
    ec_path = ROOT / "data" / "doc_embeddings" / "entity_cocitation.json"
    if ec_path.exists():
        with open(ec_path) as f:
            ec_data = json.load(f)
        ec_ents = ec_data.get("entities", ec_data)
        top_n   = 15
        ere_ds  = [("gsap", "GSAP"), ("scier", "SciER"), ("scinlp", "SciNLP")]
        entities_out = {}
        for etype in ["Task", "Dataset", "Method"]:
            entries = ec_ents.get(etype, [])
            selected: set[str] = set()
            for raw_ds, _ in ere_ds:
                srt = sorted(entries, key=lambda e, d=raw_ds: e.get("papers_by_ds_counts", {}).get(d, 0), reverse=True)
                selected.update(e["term"] for e in srt[:top_n])
            subset_e = sorted([e for e in entries if e["term"] in selected], key=lambda e: e["n_papers"], reverse=True)
            entities_out[etype] = {
                "labels": [e["term"] for e in subset_e],
                "by_ds":  {raw_ds: [int(e.get("papers_by_ds_counts", {}).get(raw_ds, 0)) for e in subset_e]
                           for raw_ds, _ in ere_ds},
            }
        result["entities"] = {
            "sub_datasets": [{"key": k, "label": l, "color": DS_COLORS.get(k, "#888")} for k, l in ere_ds],
            "types":        entities_out,
        }
    else:
        result["entities"] = None

    # ── Outlet list ───────────────────────────────────────────────────────────
    print("  Outlet list …")
    paper_counts = meta_df.groupby("outlet_id")["doc_id"].count().to_dict()
    counts_by_ds = meta_df.groupby(["outlet_id", "dataset"])["doc_id"].count().unstack(fill_value=0).to_dict("index")
    outlet_rows = []
    for oid, o in outlets_m.items():
        oa_url = f"https://openalex.org/sources/{o.openalex_id}" if o.openalex_id else ""
        row = {
            "outlet_id":        oid,
            "abbr":             o.abbr or o.name,
            "name":             o.name,
            "type":             o.outlet_type,
            "topic":            o.outlet_topic or "—",
            "h_index":          o.h_index,
            "i10_index":        o.i10_index,
            "works_oa":         o.works_count,
            "citations_oa":     o.cited_by_count,
            "citedness_2yr":    round(o.mean_citedness_2yr, 2) if o.mean_citedness_2yr else None,
            "openalex_url":     oa_url,
            "papers_total":     int(paper_counts.get(oid, 0)),
            "papers_gsap_ere":  int(counts_by_ds.get(oid, {}).get("gsap", 0)),
            "papers_scier":     int(counts_by_ds.get(oid, {}).get("scier", 0)),
            "papers_scinlp":    int(counts_by_ds.get(oid, {}).get("scinlp", 0)),
        }
        outlet_rows.append(row)
    outlet_rows.sort(key=lambda r: (r["h_index"] or 0), reverse=True)
    result["outlet_list"] = outlet_rows
    result["outlet_list_meta"] = {
        "n_enriched": sum(1 for o in outlets_m.values() if o.openalex_id),
        "n_total":    len(outlets_m),
    }

    # ── Outlet publications bar (horizontal stacked) ──────────────────────────
    meta_df["outlet_label"] = meta_df.apply(
        lambda r: (f"{r['outlet_name']} ({r['outlet_abbr']})"
                   if pd.notna(r.get("outlet_name")) and r.get("outlet_name")
                   else (r.get("outlet_abbr") or "Unknown")),
        axis=1,
    )
    meta_df["outlet_label"] = meta_df["outlet_label"].fillna("Unknown").replace("", "Unknown")
    pub_pivot = (
        meta_df.groupby(["outlet_label", "dataset"])
        .size().reset_index(name="count")
        .pivot(index="outlet_label", columns="dataset", values="count")
        .fillna(0).astype(int)
    )
    pub_pivot["_total"] = pub_pivot.sum(axis=1)
    pub_pivot = pub_pivot.sort_values("_total", ascending=True).drop(columns="_total")
    ds_order = ["gsap", "scier", "scinlp"]
    result["outlet_pubs"] = {
        "labels":  pub_pivot.index.tolist(),
        "datasets": ds_order,
        "by_ds": {ds: [int(v) for v in pub_pivot[ds].tolist()] if ds in pub_pivot.columns else [0]*len(pub_pivot)
                  for ds in ds_order},
        "colors": {"gsap": "#636EFA", "scier": "#EF553B", "scinlp": "#00CC96"},
    }

    # ── Publication map ───────────────────────────────────────────────────────
    print("  Publication map …")
    pm_path = ROOT / "data" / "doc_embeddings" / "paper_map.parquet"
    if pm_path.exists():
        pm = pd.read_parquet(pm_path)
        extra_cols = ["dataset", "split", "year", "outlet_abbr", "outlet_type", "outlet_topic", "selection", "cited_by_count"]
        merge_cols = [c for c in extra_cols if c in meta_df.columns]
        pm = pm.merge(meta_df[["doc_id"] + merge_cols], on="doc_id", how="left")

        sel_map = {"huggingface_selection": "gsap_hf", "arxiv_random_selection": "gsap_arxiv"}
        pm["dataset_detail"] = pm.apply(
            lambda r: sel_map.get(r.get("selection", ""), r["label"])
            if r["label"] == "gsap" else r["label"],
            axis=1,
        )

        def _clean(v):
            if isinstance(v, float) and math.isnan(v):
                return None
            if hasattr(v, "item"):
                return v.item()
            return v

        pm_records = []
        for _, row in pm.iterrows():
            pm_records.append({k: _clean(v) for k, v in row.items()})

        knn_edges_path = ROOT / "data" / "doc_embeddings" / "knn_edges.json"
        knn_edges = []
        if knn_edges_path.exists():
            with open(knn_edges_path) as f:
                knn_edges = json.load(f)

        entity_sets_path = ROOT / "data" / "doc_embeddings" / "entity_sets.json"
        entity_sets_data: dict = {}
        if entity_sets_path.exists():
            with open(entity_sets_path) as f:
                entity_sets_data = json.load(f)

        print("  Entity frequencies …")
        entity_freq_data = _build_entity_freq()

        result["paper_map"] = {
            "points":      pm_records,
            "knn_edges":   knn_edges,
            "entity_sets": entity_sets_data,
            "entity_freq": entity_freq_data,
        }
    else:
        result["paper_map"] = None

    # ── Outlet map ────────────────────────────────────────────────────────────
    print("  Outlet map …")
    outlet_list_vals = list(outlets_m.values())
    topic_sets = [
        set(o.openalex_topics) | ({f"__manual__{o.outlet_topic}"} if o.outlet_topic else set())
        for o in outlet_list_vals
    ]
    n_out = len(outlet_list_vals)

    shared_mat = np.zeros((n_out, n_out), dtype=int)
    dissim_mat = np.ones((n_out, n_out))
    for i in range(n_out):
        for j in range(i, n_out):
            inter = len(topic_sets[i] & topic_sets[j])
            union = len(topic_sets[i] | topic_sets[j])
            shared_mat[i, j] = shared_mat[j, i] = inter
            jac = inter / union if union else (1.0 if i == j else 0.0)
            dissim_mat[i, j] = dissim_mat[j, i] = 1.0 - jac
    np.fill_diagonal(dissim_mat, 0.0)

    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42, n_init=4)
    coords = mds.fit_transform(dissim_mat)

    outlet_paper_counts = meta_df.groupby("outlet_id")["doc_id"].count().to_dict()
    outlet_points = []
    for i, o in enumerate(outlet_list_vals):
        outlet_points.append({
            "outlet_id":     o.id,
            "name":          o.name,
            "abbr":          o.abbr or o.name[:15],
            "outlet_type":   o.outlet_type or "unknown",
            "outlet_topic":  o.outlet_topic or "unknown",
            "h_index":       o.h_index,
            "papers_total":  int(outlet_paper_counts.get(o.id, 0)),
            "topics_preview": ", ".join(o.openalex_topics[:4]) if o.openalex_topics else "",
            "x": float(coords[i, 0]),
            "y": float(coords[i, 1]),
        })

    outlet_edges = [
        {"i": int(i), "j": int(j), "shared": int(shared_mat[i, j])}
        for i in range(n_out) for j in range(i + 1, n_out)
        if shared_mat[i, j] > 0
    ]

    result["outlet_map"] = {"points": outlet_points, "edges": outlet_edges}

    return result


def main():
    data = build()
    out = ensure_output("data/webapp_metadata.json")
    out.write_text(json.dumps(data, ensure_ascii=False))
    print(f"\nWritten → {out}")


if __name__ == "__main__":
    main()
