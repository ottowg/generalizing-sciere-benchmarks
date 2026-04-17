"""Generate unification retention statistics report.

For each dataset (GSAP, SciER, SciNLP), reports:
- % of entities kept after unification
- % of relations kept after unification
- % dropped due to no shared counterpart in the unified schema
- % affected by span normalization
"""

from dataclasses import dataclass, field
from pathlib import Path

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import ensure_output
from unifiedsciere.reporting import MarkdownReport
from unifiedsciere.unification.pipeline import apply_unification_pipeline


DATASETS = ["gsap-ere", "scier", "scinlp"]
SPLITS = ["train", "dev", "test"]


@dataclass
class RetentionStats:
    dataset: str

    # Entity counts
    ent_original: int = 0
    ent_merge_eliminated: int = 0
    ent_label_dropped: int = 0           # no shared counterpart
    ent_gsap_corrections: int = 0        # GSAP-specific systematic error filtering
    ent_post_norm_dropped: int = 0       # post-normalisation blacklist (GSAP)
    ent_span_normalized: int = 0         # text changed (entity kept)
    ent_final: int = 0

    # Relation counts
    rel_original: int = 0
    rel_merge_eliminated: int = 0        # self-loops + duplicates created by merge
    rel_entity_dropped: int = 0          # dropped because entity had no counterpart
    rel_label_dropped: int = 0           # dropped because relation type has no counterpart
    rel_gsap_corrections: int = 0        # GSAP-specific corrections cascade
    rel_post_norm_dropped: int = 0       # post-normalisation blacklist cascade
    rel_final: int = 0

    # Dropped label names (for explanation)
    dropped_entity_labels: list = field(default_factory=list)

    def add(self, other: "RetentionStats") -> None:
        for attr in [
            "ent_original", "ent_merge_eliminated", "ent_label_dropped",
            "ent_gsap_corrections", "ent_post_norm_dropped", "ent_span_normalized",
            "ent_final",
            "rel_original", "rel_merge_eliminated", "rel_entity_dropped",
            "rel_label_dropped", "rel_gsap_corrections", "rel_post_norm_dropped",
            "rel_final",
        ]:
            setattr(self, attr, getattr(self, attr) + getattr(other, attr))
        # Merge dropped label sets
        for lbl in other.dropped_entity_labels:
            if lbl not in self.dropped_entity_labels:
                self.dropped_entity_labels.append(lbl)

    def pct(self, n: int) -> str:
        if self.ent_original == 0:
            return "—"
        return f"{100 * n / self.ent_original:.1f}%"

    def pct_rel(self, n: int) -> str:
        if self.rel_original == 0:
            return "—"
        return f"{100 * n / self.rel_original:.1f}%"


def process_split(dataset: str, split: str) -> RetentionStats | None:
    """Process one dataset/split and return retention stats."""
    try:
        corpus = load_corpus(dataset, split, data_type="gold")
    except FileNotFoundError:
        return None

    n_orig_ent = len(corpus.mentions)
    n_orig_rel = len(corpus.relation)

    if n_orig_ent == 0:
        return None

    unified, stats = apply_unification_pipeline(
        corpus,
        dataset,
        apply_to_gold=True,
        apply_to_predicted=False,
    )

    s = RetentionStats(dataset=dataset)

    # --- Entity counts ---
    merge = stats.get("merge", {})
    drop = stats.get("drop", {})
    dc = stats.get("dataset_corrections", {}).get("gsap-ere", {})
    span = stats.get("span_normalization", {})

    s.ent_original = merge.get("gold_original_count", n_orig_ent)
    n_after_merge = merge.get("gold_merged_count", s.ent_original)
    s.ent_merge_eliminated = s.ent_original - n_after_merge

    s.ent_label_dropped = drop.get("gold_mentions_dropped", 0)
    n_after_label_drop = drop.get("gold_mentions_kept", n_after_merge - s.ent_label_dropped)

    s.ent_gsap_corrections = dc.get("gold_mentions_filtered", 0)
    n_after_corrections = n_after_label_drop - s.ent_gsap_corrections

    s.ent_span_normalized = span.get("gold_corrections", 0)

    s.ent_final = len(unified.mentions)
    s.ent_post_norm_dropped = n_after_corrections - s.ent_final

    # --- Relation counts ---
    s.rel_original = merge.get("gold_relations_original", n_orig_rel)
    n_rels_after_merge = merge.get("gold_relations_merged", s.rel_original)
    s.rel_merge_eliminated = s.rel_original - n_rels_after_merge

    s.rel_entity_dropped = drop.get("gold_relations_dropped", 0)
    n_rels_after_entity_drop = drop.get("gold_relations_kept", n_rels_after_merge - s.rel_entity_dropped)

    drop_rel = stats.get("drop_relations", {})
    s.rel_label_dropped = drop_rel.get("gold_relations_dropped", 0)
    n_rels_after_rel_drop = drop_rel.get("gold_relations_kept", n_rels_after_entity_drop - s.rel_label_dropped)

    s.rel_gsap_corrections = dc.get("gold_relations_filtered", 0)
    n_rels_after_corrections = n_rels_after_rel_drop - s.rel_gsap_corrections

    s.rel_final = len(unified.relation)
    s.rel_post_norm_dropped = n_rels_after_corrections - s.rel_final

    s.dropped_entity_labels = sorted(drop.get("dropped_labels", []))

    return s


def build_report() -> str:
    """Build the full markdown report."""
    report = MarkdownReport("Unification Retention Statistics")

    report.text(
        "This report quantifies how the unification pipeline transforms each dataset's "
        "gold annotations. Numbers are aggregated across all available splits (train, dev, test)."
    )

    # ── Collect stats ──────────────────────────────────────────────────────────
    totals: dict[str, RetentionStats] = {}

    for dataset in DATASETS:
        agg = RetentionStats(dataset=dataset)
        for split in SPLITS:
            s = process_split(dataset, split)
            if s is not None:
                agg.add(s)
        totals[dataset] = agg

    # ── High-level summary table ───────────────────────────────────────────────
    report.heading("Summary", level=2)
    report.text(
        "The table below shows the key retention rates after running the full unification "
        "pipeline on gold annotations. *Entities kept* and *Relations kept* are the "
        "fractions that survive all pipeline steps and end up in the unified corpus."
    )

    import pandas as pd

    rows = []
    for ds, s in totals.items():
        rows.append({
            "Dataset": ds.upper(),
            "Entities (orig)": s.ent_original,
            "Entities kept": f"{s.ent_final:,} ({s.pct(s.ent_final)})",
            "Relations (orig)": s.rel_original,
            "Relations kept": f"{s.rel_final:,} ({s.pct_rel(s.rel_final)})",
        })
    report.table(pd.DataFrame(rows))

    # ── Entity retention breakdown ─────────────────────────────────────────────
    report.heading("Entity Retention Breakdown", level=2)
    report.text(
        "Each row shows how many entities were removed at each pipeline stage, as a "
        "percentage of the original entity count. *Span-normalised* entities are kept "
        "but have their surface text adjusted (e.g. a determiner or trailing word stripped); "
        "they do not count as removed."
    )

    ent_rows = []
    for ds, s in totals.items():
        row = {
            "Dataset": ds.upper(),
            "Original": f"{s.ent_original:,}",
            "Removed: overlap merge": f"{s.ent_merge_eliminated:,} ({s.pct(s.ent_merge_eliminated)})",
            "Removed: no counterpart": f"{s.ent_label_dropped:,} ({s.pct(s.ent_label_dropped)})",
        }
        if ds == "gsap-ere":
            row["Removed: GSAP corrections"] = f"{s.ent_gsap_corrections:,} ({s.pct(s.ent_gsap_corrections)})"
            row["Removed: post-norm blacklist"] = f"{s.ent_post_norm_dropped:,} ({s.pct(s.ent_post_norm_dropped)})"
        row["Span-normalised (kept)"] = f"{s.ent_span_normalized:,} ({s.pct(s.ent_span_normalized)})"
        row["Kept"] = f"{s.ent_final:,} ({s.pct(s.ent_final)})"
        ent_rows.append(row)

    report.table(pd.DataFrame(ent_rows).fillna("—"))

    # Dropped label details
    report.heading("Dropped entity labels by dataset", level=3)
    for ds, s in totals.items():
        if s.dropped_entity_labels:
            report.text(f"**{ds.upper()}:** {', '.join(s.dropped_entity_labels)}")
        else:
            report.text(f"**{ds.upper()}:** _(none)_")

    # ── Relation retention breakdown ───────────────────────────────────────────
    report.heading("Relation Retention Breakdown", level=2)
    report.text(
        "Relations can be dropped for several reasons: (a) their endpoint entity was "
        "dropped, (b) the relation type itself has no equivalent in the unified schema, "
        "or (c) the merge step created self-loops or duplicates. "
        "Columns (a) and (b) together constitute *no shared counterpart* for relations."
    )

    rel_rows = []
    for ds, s in totals.items():
        n_no_counterpart = s.rel_entity_dropped + s.rel_label_dropped
        row = {
            "Dataset": ds.upper(),
            "Original": f"{s.rel_original:,}",
            "Removed: merge (self-loop/dup)": f"{s.rel_merge_eliminated:,} ({s.pct_rel(s.rel_merge_eliminated)})",
            "Removed: entity no counterpart": f"{s.rel_entity_dropped:,} ({s.pct_rel(s.rel_entity_dropped)})",
            "Removed: relation no counterpart": f"{s.rel_label_dropped:,} ({s.pct_rel(s.rel_label_dropped)})",
            "Total removed: no counterpart": f"{n_no_counterpart:,} ({s.pct_rel(n_no_counterpart)})",
        }
        if ds == "gsap-ere":
            row["Removed: GSAP corrections"] = f"{s.rel_gsap_corrections:,} ({s.pct_rel(s.rel_gsap_corrections)})"
            row["Removed: post-norm blacklist"] = f"{s.rel_post_norm_dropped:,} ({s.pct_rel(s.rel_post_norm_dropped)})"
        row["Kept"] = f"{s.rel_final:,} ({s.pct_rel(s.rel_final)})"
        rel_rows.append(row)

    report.table(pd.DataFrame(rel_rows).fillna("—"))

    # ── Methodology description ────────────────────────────────────────────────
    report.heading("Methodology", level=2)

    report.heading("Overview", level=3)
    report.text(
        "All three datasets (GSAP, SciER, SciNLP) use overlapping but non-identical "
        "annotation guidelines, label sets, and annotation conventions. "
        "To make their annotations mutually comparable, we apply a sequential "
        "unification pipeline to the gold annotations of each dataset. "
        "The pipeline steps are described below; they are applied in order, and each "
        "step operates on the output of the previous one."
    )

    report.heading("Pipeline Steps", level=3)

    report.text(
        "**Step 1 — Merge overlapping mentions.** "
        "Each dataset may contain mentions whose character spans overlap within the same "
        "sentence (e.g. a model name nested inside a longer span). "
        "Overlapping mentions are collapsed into a single mention; "
        "by default the larger span is preferred. "
        "Relations between two mentions that collapse into the same span become "
        "self-loops and are discarded; duplicate relations created by the merge are "
        "also removed. "
        "This step is necessary because the unified evaluation metric cannot handle "
        "overlapping spans."
    )

    report.text(
        "**Step 2 — Drop unmapped entity labels.** "
        "Each dataset has its own label vocabulary. "
        "GSAP, for example, includes labels such as `DatasetGeneric`, `ReferenceLink`, "
        "and `URL` that have no equivalent in the three-way unified schema "
        "(`Dataset`, `Method`, `Task`). "
        "SciNLP uses a lowercase `metric` label that is likewise out of scope. "
        "Mentions bearing any of these unmapped labels are removed, along with every "
        "relation that references one of those mentions. "
        "This is what the statistics above call *no shared counterpart* for entities."
    )

    report.text(
        "**Step 3 — Map entity labels to the unified schema.** "
        "Dataset-specific labels that do have a shared counterpart are renamed. "
        "For example, GSAP's `MLModel`, `ModelArchitecture`, and `MLModelGeneric` all "
        "map to the unified `Method` label; SciNLP's lowercase `dataset` maps to "
        "`Dataset`. The original label is preserved in the `label_original` field for "
        "traceability."
    )

    report.text(
        "**Step 4 — Drop unmapped relation types.** "
        "Relations whose type has no mapping in the unified relation schema are removed. "
        "This step is analogous to Step 2 but for relation labels."
    )

    report.text(
        "**Step 5 — Map relation labels to the unified schema.** "
        "Remaining relations are relabelled to their canonical counterparts "
        "(e.g. SciER's `Used-For` → `appliedTo`, `Benchmark-For` → `benchmarkFor`). "
        "Where the direction of the relation changes (e.g. GSAP's `architecture` "
        "maps to an *inverted* `usedFor`), the subject and object are swapped. "
        "Undirected relations (such as `coreference` and `isComparedTo`) are "
        "normalised to a canonical direction by entity span position."
    )

    report.text(
        "**Step 6 — GSAP-specific corrections (GSAP only).** "
        "GSAP's `MLModelGeneric` label is used for generic anaphoric references "
        "('the model', 'our system', 'the baseline') that are semantically "
        "uninformative and appear frequently as unmatched predictions in cross-dataset "
        "evaluation. "
        "A data-driven analysis identifies such surface forms by their frequency among "
        "unmatched predictions; those appearing at least twice are added to a filter "
        "list together with a hand-curated static blacklist. "
        "Mentions whose normalised text appears in this list are removed, along with "
        "their relations."
    )

    report.text(
        "**Step 7 — Span normalisation.** "
        "Systematic prefix and suffix tokens are stripped from entity spans to reduce "
        "spurious span mismatches across datasets. "
        "Rules are dataset-specific: "
        "GSAP `Method` spans lose leading determiners ('the', 'a', 'our', …) and "
        "trailing generic nouns ('models', 'layers', 'classifiers', …); "
        "all GSAP labels lose a trailing possessive `'s`. "
        "SciNLP `Dataset` spans lose a leading 'the' and trailing words like 'dataset', "
        "'benchmark', or 'corpus'; SciNLP `Method` spans similarly lose 'the' and "
        "'models'. "
        "SciER `Dataset` spans lose trailing 'corpus', 'papers', or 'submissions'. "
        "Normalisation changes the surface text of the mention but does not remove it; "
        "mentions reduced to a single token are not stripped further."
    )

    report.text(
        "**Step 8 — Post-normalisation blacklist (GSAP only).** "
        "After span normalisation, some mentions that previously had informative text "
        "are reduced to generic tokens (e.g. 'their model' → 'model'). "
        "A second pass of the GSAP blacklist is applied to catch these newly generic "
        "forms. Mentions that now match a blacklisted token are removed together with "
        "their relations."
    )

    report.heading("Interpreting the Statistics", level=3)
    report.text(
        "**% of entities kept** — the fraction of original gold entity mentions that "
        "survive all pipeline steps unchanged (or with only surface-text adjustments "
        "from span normalisation) and appear in the final unified corpus."
    )
    report.text(
        "**% of relations kept** — analogously for relation instances."
    )
    report.text(
        "**% dropped due to no shared counterpart** — the fraction removed specifically "
        "because the label (entity type or relation type) has no equivalent in the "
        "unified schema. For relations this also includes those dropped as a cascade "
        "when one of their endpoint entities was unmapped."
    )
    report.text(
        "**% affected by span normalisation** — the fraction of entities whose surface "
        "text was modified by the prefix/suffix stripping rules. These entities are "
        "retained in the unified corpus, just with a shorter, more canonical span."
    )

    return report


def main():
    report = build_report()
    out_path = ensure_output("reports/ere_performance/unification_retention_stats.md")
    report.write(str(out_path))


if __name__ == "__main__":
    main()
