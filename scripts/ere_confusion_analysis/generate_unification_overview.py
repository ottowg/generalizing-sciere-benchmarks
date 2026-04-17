"""Generate JSON overview files for the unification pipeline and retention stats.

Produces:
  reports/unification/pipeline.json   — pipeline steps, label/relation mappings
  reports/unification/retention.json  — retention stats across all datasets/splits
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import project_root, reports_dir
from unifiedsciere.unification.pipeline import apply_unification_pipeline, load_unification_config

DATASETS = ["gsap-ere", "scier", "scinlp"]
SPLITS   = ["train", "dev", "test"]


# ── Pipeline JSON ─────────────────────────────────────────────────────────────

def build_pipeline_json(timestamp: str) -> dict:
    config      = load_unification_config()
    root        = project_root()
    label_yaml  = yaml.safe_load((root / "src/unifiedsciere/unification/label_mappings.yaml").read_text())
    rel_yaml    = yaml.safe_load((root / "src/unifiedsciere/unification/relation_mappings.yaml").read_text())
    gsap_cfg    = config.get("dataset_corrections", {}).get("gsap-ere", {})

    steps = [
        {
            "number": 1,
            "name": "Merge Stacked Mentions",
            "scope": "all datasets",
            "enabled": config.get("merge_stacked", {}).get("enabled", True),
            "description": (
                "Collapses overlapping entity spans within the same sentence into a single mention. "
                "By default the larger span is kept. Relations between two mentions that collapse "
                "into the same span become self-loops and are discarded; duplicate relations are also removed."
            ),
            "config": {"prefer_larger": config.get("merge_stacked", {}).get("prefer_larger", True)},
        },
        {
            "number": 2,
            "name": "Drop Unmapped Entity Labels",
            "scope": "all datasets",
            "enabled": config.get("drop_unmapped", {}).get("enabled", True),
            "description": (
                "Removes mentions whose label has no equivalent in the unified schema "
                "(Dataset / Method / Task). All relations referencing a dropped mention are also removed. "
                "Affected labels: GSAP — DatasetGeneric, ReferenceLink, URL; SciNLP — metric."
            ),
            "config": {},
        },
        {
            "number": 3,
            "name": "Map Entity Labels to Unified Schema",
            "scope": "all datasets",
            "enabled": config.get("map_labels", {}).get("enabled", True),
            "description": (
                "Renames remaining labels to the three unified types: Dataset, Method, Task. "
                "The original label is preserved in label_original for traceability. "
                "Example: GSAP MLModel / ModelArchitecture / MLModelGeneric → Method."
            ),
            "config": {},
        },
        {
            "number": 4,
            "name": "Drop Unmapped Relation Types",
            "scope": "all datasets",
            "enabled": config.get("drop_unmapped_relations", {}).get("enabled", True),
            "description": (
                "Removes relations whose type has no equivalent in the canonical relation schema. "
                "Affected types include GSAP citation, generatedBy, size, sourcedFrom, "
                "and SciNLP MeasuredBy, evaluatedBy."
            ),
            "config": {},
        },
        {
            "number": 5,
            "name": "Map Relation Labels to Unified Schema",
            "scope": "all datasets",
            "enabled": config.get("map_relations", {}).get("enabled", True),
            "description": (
                "Renames remaining relations to canonical types (e.g. SciER Used-For → appliedTo). "
                "Where direction changes across datasets, subject and object are swapped "
                "(e.g. GSAP architecture → inverted usedFor). "
                "Undirected relations (coreference, isComparedTo) are normalised by span position."
            ),
            "config": {},
        },
        {
            "number": 6,
            "name": "GSAP-Specific Corrections",
            "scope": "GSAP only",
            "enabled": gsap_cfg.get("enabled", False),
            "description": (
                "Removes generic anaphoric MLModelGeneric mentions ('model', 'baseline', 'our system') "
                "that are semantically uninformative and appear frequently as unmatched cross-dataset predictions. "
                "Uses a data-driven dynamic filter (mentions appearing ≥ min_count times in unmatched predictions) "
                "combined with a hand-curated static blacklist and pattern blacklist (e.g. trailing -ing forms)."
            ),
            "config": {
                "min_count": gsap_cfg.get("min_count", 2),
                "static_blacklist": gsap_cfg.get("static_blacklist", []),
                "pattern_blacklist": gsap_cfg.get("pattern_blacklist", {}),
            },
        },
        {
            "number": 7,
            "name": "Span Normalisation",
            "scope": "all datasets",
            "enabled": config.get("span_normalization", {}).get("enabled", True),
            "description": (
                "Strips systematic prefix and suffix tokens that differ across annotation schemes. "
                "Rules are dataset-specific: GSAP Method loses leading determiners (the, a, our, …) "
                "and trailing generic nouns (models, layers, classifiers, …); all GSAP labels lose trailing 's. "
                "SciNLP Dataset/Method lose leading 'the' and trailing 'dataset', 'benchmark', 'models'. "
                "SciER Dataset loses trailing 'corpus', 'papers', 'submissions'. "
                "Mentions reduced to a single token are not stripped further."
            ),
            "config": {},
        },
        {
            "number": 8,
            "name": "Post-Normalisation Blacklist",
            "scope": "GSAP only",
            "enabled": gsap_cfg.get("enabled", False),
            "description": (
                "A second pass of the GSAP static and pattern blacklists applied after span normalisation. "
                "Catches mentions that became generic after stripping "
                "(e.g. 'their model' → 'model' after prefix removal)."
            ),
            "config": {},
        },
    ]

    # Label mappings: flatten to list of {original, unified} per dataset
    label_mappings = {}
    for ds, mapping in label_yaml["mappings"].items():
        label_mappings[ds] = [
            {"original": orig, "unified": unified if unified else "—  (dropped)"}
            for orig, unified in mapping.items()
        ]

    # Relation mappings: flatten per dataset
    rel_mappings = {}
    for ds, mapping in rel_yaml["mappings"].items():
        rows = []
        for orig, target in mapping.items():
            if target is None:
                rows.append({"original": orig, "unified": "—  (dropped)", "inverted": False})
            elif isinstance(target, dict):
                rows.append({"original": orig, "unified": target["canonical"], "inverted": target.get("inverted", False)})
            else:
                rows.append({"original": orig, "unified": target, "inverted": False})
        rel_mappings[ds] = rows

    return {
        "title":              "Unification Pipeline",
        "generated":          timestamp,
        "info": (
            "The unification pipeline maps dataset-specific label schemes to a shared schema "
            "(Dataset / Method / Task for entities; seven canonical relation types). "
            "It is applied per origin — predictions are unified using the trained-on dataset's scheme, "
            "gold data using the annotation dataset's scheme. "
            "Eight sequential steps handle overlapping spans, unmapped labels, relation directions, "
            "dataset-specific noise, and surface-text normalisation."
        ),
        "unified_labels":     label_yaml["unified_labels"],
        "canonical_relations": rel_yaml["canonical_relations"],
        "steps":              steps,
        "label_mappings":     label_mappings,
        "relation_mappings":  rel_mappings,
    }


# ── Retention Stats JSON ──────────────────────────────────────────────────────

def build_retention_json(timestamp: str) -> dict:
    agg = {ds: defaultdict(int) for ds in DATASETS}

    for ds in DATASETS:
        for split in SPLITS:
            print(f"  {ds} / {split}")
            try:
                corpus = load_corpus(ds, split, data_type="gold")
                orig_ents = len(corpus.mentions)
                orig_rels = len(corpus.relation)

                unified, stats = apply_unification_pipeline(
                    corpus, ds, apply_to_gold=True, apply_to_predicted=False
                )

                a = agg[ds]
                a["entities_original"] += orig_ents
                a["entities_kept"]     += len(unified.mentions)
                a["relations_original"] += orig_rels
                a["relations_kept"]     += len(unified.relation)

                merge = stats.get("merge", {})
                a["entities_removed_merge"] += merge.get("gold_merged", 0)
                a["relations_removed_merge"] += (
                    merge.get("gold_self_loops_removed", 0) +
                    merge.get("gold_duplicates_removed", 0)
                )

                drop = stats.get("drop", {})
                a["entities_removed_unmapped"] += drop.get("gold_mentions_dropped", 0)

                drop_rel = stats.get("drop_relations", {})
                a["relations_removed_unmapped"] += drop_rel.get("gold_relations_dropped", 0)

                corr = stats.get("dataset_corrections", {}).get("gsap-ere", {})
                a["entities_removed_corrections"] += corr.get("gold_mentions_filtered", 0)

                span = stats.get("span_normalization", {})
                a["entities_span_normalised"] += span.get("gold_corrections", 0)

            except Exception as e:
                print(f"    ERROR: {e}")

    def pct(n, total):
        return round(n / total * 100, 1) if total else 0.0

    summary = []
    entity_breakdown = []
    relation_breakdown = []

    for ds in DATASETS:
        a = agg[ds]
        eo, ek = a["entities_original"], a["entities_kept"]
        ro, rk = a["relations_original"], a["relations_kept"]

        summary.append({
            "dataset": ds,
            "entities_original": eo,
            "entities_kept": ek,
            "entities_pct": pct(ek, eo),
            "relations_original": ro,
            "relations_kept": rk,
            "relations_pct": pct(rk, ro),
        })

        entity_breakdown.append({
            "dataset": ds,
            "original": eo,
            "removed_merge":       {"count": a["entities_removed_merge"],       "pct": pct(a["entities_removed_merge"], eo)},
            "removed_unmapped":    {"count": a["entities_removed_unmapped"],    "pct": pct(a["entities_removed_unmapped"], eo)},
            "removed_corrections": {"count": a["entities_removed_corrections"], "pct": pct(a["entities_removed_corrections"], eo)},
            "span_normalised":     {"count": a["entities_span_normalised"],     "pct": pct(a["entities_span_normalised"], eo)},
            "kept":                {"count": ek,                                "pct": pct(ek, eo)},
        })

        relation_breakdown.append({
            "dataset": ds,
            "original": ro,
            "removed_merge":    {"count": a["relations_removed_merge"],    "pct": pct(a["relations_removed_merge"], ro)},
            "removed_unmapped": {"count": a["relations_removed_unmapped"], "pct": pct(a["relations_removed_unmapped"], ro)},
            "kept":             {"count": rk,                              "pct": pct(rk, ro)},
        })

    label_yaml = yaml.safe_load(
        (project_root() / "src/unifiedsciere/unification/label_mappings.yaml").read_text()
    )
    dropped_labels = {
        ds: [orig for orig, unified in mapping.items() if unified is None]
        for ds, mapping in label_yaml["mappings"].items()
    }

    return {
        "title":     "Unification Retention Statistics",
        "generated": timestamp,
        "info": (
            "Quantifies how the unification pipeline transforms each dataset's gold annotations, "
            "aggregated across all splits (train, dev, test). "
            "Numbers show how many entity mentions and relations survive each pipeline stage."
        ),
        "summary":            summary,
        "entity_breakdown":   entity_breakdown,
        "relation_breakdown": relation_breakdown,
        "dropped_labels":     dropped_labels,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_dir = reports_dir("unification")

    print("Building pipeline JSON …")
    pipeline_json = build_pipeline_json(timestamp)
    (output_dir / "pipeline.json").write_text(json.dumps(pipeline_json, ensure_ascii=False, indent=2))
    print(f"  Saved: {output_dir / 'pipeline.json'}")

    print("Computing retention stats …")
    retention_json = build_retention_json(timestamp)
    (output_dir / "retention.json").write_text(json.dumps(retention_json, ensure_ascii=False, indent=2))
    print(f"  Saved: {output_dir / 'retention.json'}")


if __name__ == "__main__":
    main()
