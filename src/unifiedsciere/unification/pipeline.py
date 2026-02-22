"""Unified pipeline for applying all unification steps.

This module provides a complete pipeline that applies merging, mapping, and
dataset-specific corrections based on a YAML configuration file.
"""

from pathlib import Path
from typing import Literal

import yaml

from ..types import Corpus
from .gsap_specific_corrections import filter_gsap_mentions
from .label_mapper import drop_unmapped_mentions, map_labels_to_unified
from .merge_stacked import merge_stacked_mentions
from .relation_label_mapper import drop_unmapped_relations, map_relations_to_unified
from .span_corrections import normalize_spans


def load_unification_config(config_path: Path | None = None) -> dict:
    """Load unification configuration from YAML file.

    Args:
        config_path: Path to config file. If None, uses default config in
                    configs/unification_config.yaml

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default to configs/unification_config.yaml in project root
        config_path = Path(__file__).parents[3] / "configs" / "unification_config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create configs/unification_config.yaml"
        )

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config


def apply_unification_pipeline(
    corpus: Corpus,
    dataset: Literal["scier", "scinlp", "gsap"],
    config: dict | None = None,
    config_path: Path | None = None,
    apply_to_gold: bool = False,
    apply_to_predicted: bool = True,
) -> tuple[Corpus, dict]:
    """Apply complete unification pipeline to a corpus.

    This function applies the following steps based on configuration:
    1. Merge stacked/overlapping mentions
    2. Drop unmapped labels
    3. Map labels to unified schema
    4. Apply dataset-specific corrections (e.g., GSAP MLModelGeneric filtering)
    5. Normalize spans (strip systematic prefixes/suffixes)

    Args:
        corpus: Input corpus
        dataset: Source dataset name ("scier", "scinlp", "gsap")
        config: Configuration dictionary. If None, loads from config_path
        config_path: Path to config file. If None, uses default
        apply_to_gold: If True, apply pipeline to gold annotations
        apply_to_predicted: If True, apply pipeline to predictions

    Returns:
        Tuple of:
        - Unified corpus after all pipeline steps
        - Dictionary with statistics from each step

    Example:
        >>> corpus = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")
        >>> unified_corpus, stats = apply_unification_pipeline(corpus, "gsap")
        >>> print(f"Filtered {stats['gsap_corrections']['predicted_mentions_filtered']} mentions")
    """
    # Load config if not provided
    if config is None:
        config = load_unification_config(config_path)

    # Initialize stats
    stats = {
        "merge": {},
        "drop": {},
        "map": {},
        "drop_relations": {},
        "map_relations": {},
        "dataset_corrections": {},
        "span_normalization": {},
    }

    # Step 1: Merge stacked mentions
    merge_config = config.get("merge_stacked", {})
    if merge_config.get("enabled", True):
        corpus, merge_stats = merge_stacked_mentions(
            corpus,
            prefer_larger=merge_config.get("prefer_larger", True),
            merge_gold=apply_to_gold,
            merge_predicted=apply_to_predicted,
        )
        stats["merge"] = merge_stats

    # Step 2: Drop unmapped labels
    drop_config = config.get("drop_unmapped", {})
    if drop_config.get("enabled", True):
        corpus, drop_stats = drop_unmapped_mentions(
            corpus,
            dataset,
            drop_gold=apply_to_gold,
            drop_predicted=apply_to_predicted,
        )
        stats["drop"] = drop_stats

    # Step 3: Map labels to unified schema
    map_config = config.get("map_labels", {})
    if map_config.get("enabled", True):
        corpus, map_stats = map_labels_to_unified(
            corpus,
            dataset,
            map_gold=apply_to_gold,
            map_predicted=apply_to_predicted,
        )
        stats["map"] = map_stats

    # Step 4: Drop unmapped relations
    drop_rel_config = config.get("drop_unmapped_relations", {})
    if drop_rel_config.get("enabled", True):
        corpus, drop_rel_stats = drop_unmapped_relations(
            corpus,
            dataset,
            drop_gold=apply_to_gold,
            drop_predicted=apply_to_predicted,
        )
        stats["drop_relations"] = drop_rel_stats

    # Step 5: Map relations to unified schema
    map_rel_config = config.get("map_relations", {})
    if map_rel_config.get("enabled", True):
        corpus, map_rel_stats = map_relations_to_unified(
            corpus,
            dataset,
            map_gold=apply_to_gold,
            map_predicted=apply_to_predicted,
        )
        stats["map_relations"] = map_rel_stats

    # Step 6: Apply dataset-specific corrections
    corrections_config = config.get("dataset_corrections", {})

    # GSAP-specific corrections
    if dataset == "gsap":
        gsap_config = corrections_config.get("gsap", {})
        if gsap_config.get("enabled", False):
            # Get the analysis file path
            analysis_file = gsap_config.get("mlmodelgeneric_analysis_file")
            if analysis_file:
                analysis_path = Path(analysis_file)
                if not analysis_path.is_absolute():
                    # Resolve relative to project root
                    analysis_path = Path(__file__).parents[3] / analysis_path

                if analysis_path.exists():
                    min_count = gsap_config.get("min_count", 2)
                    corpus, gsap_stats = filter_gsap_mentions(
                        corpus,
                        analysis_path,
                        min_count=min_count,
                        filter_predicted=apply_to_predicted,
                        filter_gold=apply_to_gold,
                    )
                    stats["dataset_corrections"]["gsap"] = gsap_stats
                else:
                    print(f"Warning: GSAP analysis file not found: {analysis_path}")
                    print("Skipping GSAP-specific corrections")
            else:
                print(
                    "Warning: GSAP corrections enabled but no analysis file specified"
                )
                print("Skipping GSAP-specific corrections")

    # SciER-specific corrections (if any in future)
    if dataset == "scier":
        scier_config = corrections_config.get("scier", {})
        if scier_config.get("enabled", False):
            # Placeholder for future SciER corrections
            pass

    # SciNLP-specific corrections (if any in future)
    if dataset == "scinlp":
        scinlp_config = corrections_config.get("scinlp", {})
        if scinlp_config.get("enabled", False):
            # Placeholder for future SciNLP corrections
            pass

    # Step 7: Normalize spans (strip systematic prefixes/suffixes)
    span_config = config.get("span_normalization", {})
    if span_config.get("enabled", True):
        corpus, span_stats = normalize_spans(
            corpus,
            dataset=dataset,
            normalize_gold=apply_to_gold,
            normalize_predicted=apply_to_predicted,
        )
        stats["span_normalization"] = span_stats

    return corpus, stats


def generate_pipeline_report(stats: dict, output_path: Path) -> None:
    """Generate a report about the unification pipeline results.

    Args:
        stats: Statistics dictionary from apply_unification_pipeline
        output_path: Path to save the markdown report
    """
    from datetime import datetime

    md_content = f"""# Unification Pipeline Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Pipeline Steps Applied

"""

    # Merge step
    if stats.get("merge"):
        merge = stats["merge"]
        md_content += f"""### 1. Merge Stacked Mentions

- **Predicted mentions merged**: {merge.get("predicted_merged", 0)}
- **Gold mentions merged**: {merge.get("gold_merged", 0)}
- **Self-loop relations removed**: {merge.get("predicted_self_loops_removed", 0) + merge.get("gold_self_loops_removed", 0)}
- **Duplicate relations removed**: {merge.get("predicted_duplicates_removed", 0) + merge.get("gold_duplicates_removed", 0)}

"""

    # Drop step
    if stats.get("drop"):
        drop = stats["drop"]
        md_content += f"""### 2. Drop Unmapped Labels

- **Predicted mentions dropped**: {drop.get("predicted_mentions_dropped", 0)}
- **Gold mentions dropped**: {drop.get("gold_mentions_dropped", 0)}
- **Dropped labels**: {", ".join(drop.get("dropped_labels", []))}

"""

    # Map step
    if stats.get("map"):
        map_stats = stats["map"]
        md_content += f"""### 3. Map to Unified Schema

- **Predicted mentions mapped**: {map_stats.get("predicted_mentions_mapped", 0)}
- **Gold mentions mapped**: {map_stats.get("gold_mentions_mapped", 0)}

"""

    # Dataset corrections
    if stats.get("dataset_corrections"):
        md_content += "### 4. Dataset-Specific Corrections\n\n"

        if "gsap" in stats["dataset_corrections"]:
            gsap = stats["dataset_corrections"]["gsap"]
            md_content += f"""#### GSAP MLModelGeneric Filtering

- **Predicted mentions filtered**: {gsap.get("predicted_mentions_filtered", 0)}
- **Gold mentions filtered**: {gsap.get("gold_mentions_filtered", 0)}
- **Min count threshold**: {gsap.get("min_count_threshold", "N/A")}
- **Total texts filtered**: {gsap.get("total_texts_to_filter", 0)}

"""

    # Span normalization step
    if stats.get("span_normalization"):
        span = stats["span_normalization"]
        md_content += f"""### 5. Span Normalization

- **Predicted mentions corrected**: {span.get("predicted_corrections", 0)}
- **Gold mentions corrected**: {span.get("gold_corrections", 0)}

"""
        if span.get("corrections_by_rule"):
            md_content += "**Corrections by rule:**\n\n"
            md_content += "| Rule | Count |\n"
            md_content += "|------|-------|\n"
            for rule, count in sorted(
                span["corrections_by_rule"].items(), key=lambda x: -x[1]
            ):
                md_content += f"| {rule} | {count} |\n"
            md_content += "\n"

        if span.get("examples"):
            md_content += "**Examples:**\n\n"
            md_content += "| Original | Corrected | Label |\n"
            md_content += "|----------|-----------|-------|\n"
            for ex in span["examples"][:10]:
                orig = ex["original"].replace("|", "\\|")
                corr = ex["corrected"].replace("|", "\\|")
                md_content += f"| {orig} | {corr} | {ex['label']} |\n"
            md_content += "\n"

    md_content += """
## Summary

The unification pipeline successfully applied all configured steps to standardize
the corpus annotations. This ensures consistent entity labels and removes
systematic errors across different annotation schemes.

---
*Generated by UnifiedSciERE Unification Pipeline*
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(md_content)


if __name__ == "__main__":
    # Example usage
    from ..data_loader import load_corpus

    # Load corpus
    corpus = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")

    print(f"Original: {len(corpus.mentions_predicted)} predicted mentions")

    # Apply pipeline
    unified_corpus, stats = apply_unification_pipeline(
        corpus, "gsap", apply_to_predicted=True, apply_to_gold=False
    )

    print(f"Unified: {len(unified_corpus.mentions_predicted)} predicted mentions")
    print(f"Filtered: {stats['merge'].get('predicted_merged', 0)} merged")

    # Generate report
    report_path = Path(
        "reports/ere_confusion_analysis/unification/pipeline/pipeline_report_gsap_dev.md"
    )
    generate_pipeline_report(stats, report_path)
    print(f"Report saved to: {report_path}")
