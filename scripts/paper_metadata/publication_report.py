"""Publication metadata report.

Loads all paper metadata from data/metadata/unified/all_papers.jsonl
(the single source of truth), then generates bar charts comparing
publication years across datasets and writes a markdown report.
"""

import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ALL_PAPERS = Path(__file__).parent.parent.parent / "data" / "metadata" / "unified" / "all_papers.jsonl"
OUT_DIR = Path(__file__).parent.parent.parent / "reports" / "paper_metadata"


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------


def load_all_papers() -> pd.DataFrame:
    """Load all papers from the unified all_papers.jsonl."""
    rows = []
    with open(ALL_PAPERS) as f:
        for line in f:
            p = json.loads(line)
            rows.append({
                "doc_id": p.get("doc_id", ""),
                "year": p.get("year"),
                "split": p.get("split", ""),
                "dataset": p.get("dataset", ""),
                "selection": p.get("selection", ""),
                "has_abstract": bool((p.get("abstract") or "").strip()),
                "has_openalex": bool((p.get("openalex_id") or "").strip()),
                "has_arxiv": bool((p.get("arxiv_id") or "").strip()),
                "has_s2": bool((p.get("s2_paper_id") or "").strip()),
                "has_doi": bool((p.get("doi") or "").strip()),
            })
    return pd.DataFrame(rows)


def load_gsap(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["dataset"] == "gsap-ere"].copy()


def load_scier(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["dataset"] == "scier"].copy()


def load_scier_ood(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["dataset"] == "scier_ood"].copy()


def load_scinlp(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["dataset"] == "scinlp"].copy()


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

DATASET_COLORS = {
    "gsap-ere": "#4C72B0",
    "scier": "#DD8452",
    "scier_ood": "#55A868",
    "scinlp": "#C44E52",
}

DATASET_LABELS = {
    "gsap-ere": "GSAP",
    "scier": "SciER",
    "scier_ood": "SciER-OOD",
    "scinlp": "SciNLP",
}


def plot_publications_by_year(dfs: dict[str, pd.DataFrame], out_path: Path) -> None:
    """Bar chart: number of publications per year, one bar per dataset (not stacked)."""
    plt.style.use("ggplot")

    # Build year counts per dataset
    year_counts: dict[str, Counter] = {}
    for name, df in dfs.items():
        counts = df["year"].dropna().astype(int).value_counts()
        year_counts[name] = Counter(counts.to_dict())

    # Determine full year range
    all_years: set[int] = set()
    for c in year_counts.values():
        all_years.update(c.keys())

    if not all_years:
        print("No year data available — skipping plot.")
        return

    years = sorted(all_years)

    # Filter to datasets that actually have data
    active_datasets = [name for name in dfs if year_counts[name]]

    n_datasets = len(active_datasets)
    bar_width = 0.8 / max(n_datasets, 1)

    fig, ax = plt.subplots(figsize=(12, 5))

    for i, name in enumerate(active_datasets):
        counts = year_counts[name]
        values = [counts.get(y, 0) for y in years]
        offsets = [y + (i - n_datasets / 2 + 0.5) * bar_width for y in years]
        ax.bar(
            offsets,
            values,
            width=bar_width,
            label=DATASET_LABELS.get(name, name),
            color=DATASET_COLORS.get(name, None),
        )

    ax.set_xlabel("Publication Year")
    ax.set_ylabel("Number of Publications")
    ax.set_title("Publications by Year across Datasets")
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right")
    ax.legend()
    ax.yaxis.get_major_locator().set_params(integer=True)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------


def write_markdown_report(
    dfs: dict[str, pd.DataFrame],
    gsap_df: pd.DataFrame,
    out_path: Path,
) -> None:
    """Write a markdown report summarising the publication metadata."""
    lines: list[str] = []
    lines.append("# Publication Metadata Report")
    lines.append("")
    lines.append("Overview of publication years across the four datasets used in")
    lines.append("the UnifiedSciERE project. Metadata was collected from arXiv")
    lines.append("(GSAP), Semantic Scholar (SciER, SciER-OOD), and the ACL")
    lines.append("Anthology (SciNLP).")
    lines.append("")

    # Summary table
    lines.append("## Dataset Summary")
    lines.append("")
    lines.append("| Dataset | Papers | Year Range | Source |")
    lines.append("|---------|-------:|------------|--------|")
    sources = {
        "gsap-ere": "arXiv",
        "scier": "Semantic Scholar",
        "scier_ood": "Semantic Scholar",
        "scinlp": "ACL Anthology",
    }
    for key, df in dfs.items():
        label = DATASET_LABELS[key]
        n = len(df)
        years = df["year"].dropna().astype(int)
        yr_range = f"{years.min()}--{years.max()}" if len(years) > 0 else "n/a"
        lines.append(f"| {label} | {n} | {yr_range} | {sources.get(key, '')} |")
    lines.append("")

    # Abstract availability
    lines.append("### Abstract Availability")
    lines.append("")
    lines.append("| Dataset | Papers | With Abstract | Without Abstract | Coverage |")
    lines.append("|---------|-------:|--------------:|-----------------:|---------:|")
    for key, df in dfs.items():
        label = DATASET_LABELS[key]
        n = len(df)
        if "has_abstract" in df.columns:
            with_abs = df["has_abstract"].sum()
        else:
            with_abs = 0
        without_abs = n - with_abs
        pct = f"{100 * with_abs / n:.0f}%" if n > 0 else "n/a"
        lines.append(f"| {label} | {n} | {with_abs} | {without_abs} | {pct} |")
    lines.append("")

    # Identifier coverage
    lines.append("### Identifier Coverage")
    lines.append("")
    lines.append("| Dataset | Papers | OpenAlex | arXiv | Semantic Scholar | DOI |")
    lines.append("|---------|-------:|---------:|------:|----------------:|----:|")
    for key, df in dfs.items():
        label = DATASET_LABELS[key]
        n = len(df)
        def pct(col):
            c = int(df[col].sum()) if col in df.columns else 0
            return f"{c} ({100 * c // n}%)" if n > 0 else "n/a"
        lines.append(f"| {label} | {n} | {pct('has_openalex')} | {pct('has_arxiv')} | {pct('has_s2')} | {pct('has_doi')} |")
    lines.append("")

    # GSAP selection breakdown
    if not gsap_df.empty and "selection" in gsap_df.columns:
        lines.append("### GSAP Selection Breakdown")
        lines.append("")
        lines.append("GSAP documents are drawn from two sources, identified by the")
        lines.append("`doc_id` prefix:")
        lines.append("")
        lines.append("| Selection | Papers |")
        lines.append("|-----------|-------:|")
        for sel, cnt in gsap_df["selection"].value_counts().items():
            lines.append(f"| {sel} | {cnt} |")
        lines.append("")

    # Figure
    lines.append("## Publications by Year")
    lines.append("")
    lines.append("![Publications by Year](publications_by_year.png)")
    lines.append("")
    lines.append("The chart shows the number of publications per year for each")
    lines.append("dataset. Bars are grouped (not stacked) to allow direct")
    lines.append("comparison.")
    lines.append("")
    lines.append("Key observations:")
    lines.append("")

    # Auto-generate a few observations
    for key, df in dfs.items():
        label = DATASET_LABELS[key]
        years = df["year"].dropna().astype(int)
        if len(years) == 0:
            continue
        mode = years.mode().iloc[0]
        mode_count = (years == mode).sum()
        lines.append(
            f"- **{label}**: {len(df)} papers, most frequent year {mode}"
            f" ({mode_count} papers)."
        )
    lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_df = load_all_papers()
    gsap_df = load_gsap(all_df)
    scier_df = load_scier(all_df)
    scier_ood_df = load_scier_ood(all_df)
    scinlp_df = load_scinlp(all_df)

    # Summary
    for name, df in [
        ("GSAP", gsap_df),
        ("SciER", scier_df),
        ("SciER-OOD", scier_ood_df),
        ("SciNLP", scinlp_df),
    ]:
        print(f"{name}: {len(df)} publications")

    if not gsap_df.empty:
        for sel, cnt in gsap_df["selection"].value_counts().items():
            print(f"  GSAP {sel}: {cnt}")

    # Collect datasets with data
    dfs: dict[str, pd.DataFrame] = {}
    for key, df in [
        ("gsap-ere", gsap_df),
        ("scier", scier_df),
        ("scier_ood", scier_ood_df),
        ("scinlp", scinlp_df),
    ]:
        if not df.empty:
            dfs[key] = df

    plot_publications_by_year(dfs, OUT_DIR / "publications_by_year.png")
    write_markdown_report(dfs, gsap_df, OUT_DIR / "publications_report.md")


if __name__ == "__main__":
    main()
