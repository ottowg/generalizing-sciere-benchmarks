"""Publication metadata report.

Loads bib files for GSAP, SciER, SciER-OOD, and SciNLP datasets,
then generates bar charts comparing publication years across datasets
and writes a markdown report.
"""

from collections import Counter
from pathlib import Path

import bibtexparser
import matplotlib.pyplot as plt
import pandas as pd

BIB_DIR = Path(__file__).parent.parent / "data" / "metadata" / "bib"
OUT_DIR = Path(__file__).parent.parent / "reports" / "publications"


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------


def load_bib(path: Path) -> list[dict]:
    """Parse a .bib file and return list of entry dicts."""
    with open(path) as f:
        db = bibtexparser.load(f)
    return db.entries


def _rows_from_entries(entries: list[dict], dataset: str) -> list[dict]:
    """Convert bib entries to row dicts with year, group, dataset, has_abstract."""
    rows = []
    for e in entries:
        rows.append(
            {
                "doc_id": e.get("doc_id", ""),
                "year": int(e["year"]) if e.get("year", "").isdigit() else None,
                "group": e.get("group", ""),
                "dataset": dataset,
                "has_abstract": bool(e.get("abstract", "").strip()),
            }
        )
    return rows


def load_gsap() -> pd.DataFrame:
    """Load GSAP metadata from gsap_all.bib.

    Adds a 'selection' column based on the doc_id prefix:
      - doc_id starting with '0' -> 'huggingface_selection'
      - doc_id starting with '1' -> 'arxiv_random_selection'
    """
    entries = load_bib(BIB_DIR / "gsap_all.bib")
    rows = []
    for e in entries:
        doc_id = e.get("doc_id", "")
        if doc_id.startswith("0"):
            selection = "huggingface_selection"
        elif doc_id.startswith("1"):
            selection = "arxiv_random_selection"
        else:
            selection = "unknown"
        rows.append(
            {
                "doc_id": doc_id,
                "year": int(e["year"]) if e.get("year", "").isdigit() else None,
                "group": e.get("group", ""),
                "selection": selection,
                "dataset": "gsap",
                "has_abstract": bool(e.get("abstract", "").strip()),
            }
        )
    return pd.DataFrame(rows)


def load_scier() -> pd.DataFrame:
    """Load SciER metadata by combining train/dev/test bib files."""
    rows = []
    for name in ["scier_train", "scier_dev", "scier_test"]:
        rows.extend(_rows_from_entries(load_bib(BIB_DIR / f"{name}.bib"), "scier"))
    return pd.DataFrame(rows)


def load_scier_ood() -> pd.DataFrame:
    """Load SciER out-of-distribution metadata."""
    return pd.DataFrame(
        _rows_from_entries(load_bib(BIB_DIR / "scier_ood.bib"), "scier_ood")
    )


def load_scinlp() -> pd.DataFrame:
    """Load SciNLP metadata from scinlp.bib."""
    bib_path = BIB_DIR / "scinlp.bib"
    if not bib_path.exists() or bib_path.stat().st_size == 0:
        return pd.DataFrame(columns=["doc_id", "year", "group", "dataset"])
    return pd.DataFrame(_rows_from_entries(load_bib(bib_path), "scinlp"))


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

DATASET_COLORS = {
    "gsap": "#4C72B0",
    "scier": "#DD8452",
    "scier_ood": "#55A868",
    "scinlp": "#C44E52",
}

DATASET_LABELS = {
    "gsap": "GSAP",
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
        "gsap": "arXiv",
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

    gsap_df = load_gsap()
    scier_df = load_scier()
    scier_ood_df = load_scier_ood()
    scinlp_df = load_scinlp()

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
        ("gsap", gsap_df),
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
