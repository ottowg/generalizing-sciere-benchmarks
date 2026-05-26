"""Merge stacked/overlapping mentions in predictions and gold annotations.

This module provides functionality to merge mentions that have overlapping spans,
which is a common preprocessing step for annotation unification. Relations are
automatically remapped to the merged mention spans.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from ..data_loader import load_corpus
from ..types import Corpus, Mention, Relation


def _mentions_overlap(m1: Mention, m2: Mention) -> bool:
    """Check if two mentions overlap (share at least one character position).

    Args:
        m1: First mention
        m2: Second mention

    Returns:
        True if mentions overlap, False otherwise
    """
    # Must be in the same document and sentence
    if m1.document_id != m2.document_id or m1.sent_idx != m2.sent_idx:
        return False

    # Check for character overlap
    return not (m1.end <= m2.begin or m2.end <= m1.begin)


def _merge_mentions(
    mentions: list[Mention], prefer_larger: bool = True
) -> tuple[list[Mention], dict[str, Mention], list[tuple[str, str, str, str]]]:
    """Merge overlapping mentions within each document.

    Args:
        mentions: List of mentions to merge
        prefer_larger: If True, prefer larger spans; if False, prefer smaller spans

    Returns:
        Tuple of:
        - List of merged mentions
        - Dictionary mapping old mention IDs to new merged Mention objects
        - List of merge statistics: (merged_label, kept_label, doc_id, merged_count)
    """
    if not mentions:
        return [], {}, []

    # Group mentions by document and sentence
    by_doc_sent = defaultdict(list)
    for m in mentions:
        by_doc_sent[(m.document_id, m.sent_idx)].append(m)

    merged_mentions = []
    id_mapping = {}  # old_id -> new_mention
    merge_stats = []  # (merged_label, kept_label, doc_id, count)

    for (doc_id, sent_idx), doc_mentions in by_doc_sent.items():
        # Sort by begin position
        doc_mentions.sort(key=lambda m: (m.begin, -m.end if prefer_larger else m.end))

        processed = set()

        for i, mention in enumerate(doc_mentions):
            if mention.id in processed:
                continue

            # Find all overlapping mentions
            overlapping = [mention]
            for j, other in enumerate(doc_mentions):
                if (
                    i != j
                    and other.id not in processed
                    and _mentions_overlap(mention, other)
                ):
                    overlapping.append(other)

            if len(overlapping) == 1:
                # No overlap, keep as is
                merged_mentions.append(mention)
                id_mapping[mention.id] = mention
            else:
                # Merge overlapping mentions
                # Choose the span to keep based on preference
                if prefer_larger:
                    # Keep the largest span
                    keeper = max(overlapping, key=lambda m: m.end - m.begin)
                else:
                    # Keep the smallest span
                    keeper = min(overlapping, key=lambda m: m.end - m.begin)

                merged_mentions.append(keeper)

                # Map all overlapping IDs to the keeper
                for m in overlapping:
                    id_mapping[m.id] = keeper
                    processed.add(m.id)

                    # Record merge statistics
                    if m.id != keeper.id:
                        merge_stats.append((m.label, keeper.label, doc_id, 1))

    return merged_mentions, id_mapping, merge_stats


def _remap_relations(
    relations: list[Relation], id_mapping: dict[str, Mention]
) -> tuple[list[Relation], int, int, list[str]]:
    """Remap relations to use merged mention objects.

    Args:
        relations: Original relations
        id_mapping: Mapping from old mention IDs to new merged Mention objects

    Returns:
        Tuple of:
        - List of relations with remapped mentions
        - Number of self-loops removed
        - Number of duplicates removed
        - List of relation labels for self-loops
    """
    remapped = []
    seen_pairs = set()
    self_loops = 0
    duplicates = 0
    self_loop_labels = []

    for rel in relations:
        # Map subject and object to merged mentions
        new_subject = id_mapping.get(rel.subject.id, rel.subject)
        new_object = id_mapping.get(rel.object.id, rel.object)

        # Skip self-loops (relations where subject and object got merged)
        if new_subject.id == new_object.id:
            self_loops += 1
            self_loop_labels.append(rel.label)
            continue

        # Skip duplicate relations (same subject-object-label combination)
        pair_key = (new_subject.id, new_object.id, rel.label)
        if pair_key in seen_pairs:
            duplicates += 1
            continue
        seen_pairs.add(pair_key)

        remapped.append(
            Relation(
                subject=new_subject,
                label=rel.label,
                object=new_object,
                score=rel.score,
                annotator=rel.annotator,
                dataset=rel.dataset,
            )
        )

    return remapped, self_loops, duplicates, self_loop_labels


def merge_stacked_mentions(
    corpus: Corpus,
    prefer_larger: bool = True,
    merge_gold: bool = True,
    merge_predicted: bool = True,
) -> tuple[Corpus, dict]:
    """Merge stacked/overlapping mentions in a corpus.

    Args:
        corpus: Input corpus with potentially overlapping mentions
        prefer_larger: If True, prefer larger spans; if False, prefer smaller spans
        merge_gold: If True, merge gold mentions
        merge_predicted: If True, merge predicted mentions

    Returns:
        Tuple of:
        - New Corpus with merged mentions and remapped relations
        - Dictionary with merge statistics
    """
    stats = {
        "gold_merges": [],
        "predicted_merges": [],
        "gold_original_count": len(corpus.mentions),
        "gold_merged_count": len(corpus.mentions),
        "predicted_original_count": len(corpus.mentions_predicted),
        "predicted_merged_count": len(corpus.mentions_predicted),
        "gold_relations_original": len(corpus.relation),
        "gold_relations_merged": len(corpus.relation),
        "gold_relations_self_loops": 0,
        "gold_relations_duplicates": 0,
        "gold_self_loop_labels": [],
        "predicted_relations_original": len(corpus.relations_predicted),
        "predicted_relations_merged": len(corpus.relations_predicted),
        "predicted_relations_self_loops": 0,
        "predicted_relations_duplicates": 0,
        "predicted_self_loop_labels": [],
    }

    # Merge gold mentions
    if merge_gold and corpus.mentions:
        merged_mentions, id_mapping, merge_stats = _merge_mentions(
            corpus.mentions, prefer_larger
        )
        merged_relations, self_loops, duplicates, self_loop_labels = _remap_relations(
            corpus.relation, id_mapping
        )

        stats["gold_merges"] = merge_stats
        stats["gold_merged_count"] = len(merged_mentions)
        stats["gold_relations_merged"] = len(merged_relations)
        stats["gold_relations_self_loops"] = self_loops
        stats["gold_relations_duplicates"] = duplicates
        stats["gold_self_loop_labels"] = self_loop_labels
    else:
        merged_mentions = corpus.mentions
        merged_relations = corpus.relation
        stats["gold_relations_self_loops"] = 0
        stats["gold_relations_duplicates"] = 0

    # Merge predicted mentions
    if merge_predicted and corpus.mentions_predicted:
        merged_mentions_pred, id_mapping_pred, merge_stats_pred = _merge_mentions(
            corpus.mentions_predicted, prefer_larger
        )
        (
            merged_relations_pred,
            self_loops_pred,
            duplicates_pred,
            self_loop_labels_pred,
        ) = _remap_relations(corpus.relations_predicted, id_mapping_pred)

        stats["predicted_merges"] = merge_stats_pred
        stats["predicted_merged_count"] = len(merged_mentions_pred)
        stats["predicted_relations_merged"] = len(merged_relations_pred)
        stats["predicted_relations_self_loops"] = self_loops_pred
        stats["predicted_relations_duplicates"] = duplicates_pred
        stats["predicted_self_loop_labels"] = self_loop_labels_pred
    else:
        merged_mentions_pred = corpus.mentions_predicted
        merged_relations_pred = corpus.relations_predicted
        stats["predicted_relations_self_loops"] = 0
        stats["predicted_relations_duplicates"] = 0

    # Create new corpus with merged mentions
    merged_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=merged_mentions,
        relation=merged_relations,
        mentions_predicted=merged_mentions_pred,
        relations_predicted=merged_relations_pred,
    )

    return merged_corpus, stats


def generate_merge_report(
    datasets: list[Literal["scier", "scinlp", "gsap-ere"]],
    split: Literal["train", "dev", "test"],
    models: list[Literal["scier", "scinlp", "gsap-ere"]],
    prefer_larger: bool = True,
    output_dir: Path | None = None,
) -> Path:
    """Generate a report on mention merging statistics.

    Args:
        datasets: List of datasets to analyze
        split: Data split to use
        models: List of models to analyze predictions from
        prefer_larger: If True, prefer larger spans; if False, prefer smaller spans
        output_dir: Output directory (default: reports/ere_confusion_analysis/unification/)

    Returns:
        Path to generated markdown file
    """
    if output_dir is None:
        output_dir = Path("reports/ere_confusion_analysis/unification")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    span_preference = "larger" if prefer_larger else "smaller"

    md_content = f"""# Mention Merging Report

**Generated:** {timestamp}

**Split:** {split}

**Span Preference:** Prefer {span_preference} spans when merging

## Overview

This report shows statistics on merging stacked/overlapping mentions in gold annotations
and model predictions. When mentions overlap, we keep the {span_preference} span and merge
the others into it. Relations are automatically remapped to merged mention IDs.

"""

    for dataset in datasets:
        md_content += f"\n## {dataset.upper()} Dataset\n\n"

        # Process gold annotations
        # Note: Load from any prediction file and use .mentions (not .mentions_predicted) for gold
        try:
            # Try to load from any available prediction file
            gold_corpus = None
            for model in models:
                try:
                    temp_corpus = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    # Create a corpus with just the gold annotations
                    gold_corpus = Corpus(
                        sentences=temp_corpus.sentences,
                        mentions=temp_corpus.mentions,
                        relation=temp_corpus.relation,
                        mentions_predicted=[],
                        relations_predicted=[],
                    )
                    break
                except Exception:
                    continue

            if gold_corpus is None:
                raise FileNotFoundError(
                    f"Could not load gold annotations for {dataset}"
                )

            merged_corpus, gold_stats = merge_stacked_mentions(
                gold_corpus,
                prefer_larger=prefer_larger,
                merge_gold=True,
                merge_predicted=False,
            )

            md_content += f"""### Gold Annotations

**Mentions:**
- Original: {gold_stats["gold_original_count"]}
- After merging: {gold_stats["gold_merged_count"]}
- Merged: {gold_stats["gold_original_count"] - gold_stats["gold_merged_count"]}

**Relations:**
- Original: {gold_stats["gold_relations_original"]}
- After merging: {gold_stats["gold_relations_merged"]}
- Self-loops removed: {gold_stats["gold_relations_self_loops"]}
- Duplicates removed: {gold_stats["gold_relations_duplicates"]}

"""

            # Report self-loop relation labels
            if gold_stats["gold_self_loop_labels"]:
                from collections import Counter

                label_counts = Counter(gold_stats["gold_self_loop_labels"])
                md_content += "**Self-loop Relation Labels:**\n\n"
                md_content += "| Relation Label | Count |\n"
                md_content += "|----------------|-------|\n"
                for label, count in label_counts.most_common():
                    md_content += f"| {label} | {count} |\n"
                md_content += "\n"

            # Aggregate merge statistics by label pairs
            if gold_stats["gold_merges"]:
                merge_counts = defaultdict(lambda: defaultdict(int))
                for merged_label, kept_label, doc_id, count in gold_stats[
                    "gold_merges"
                ]:
                    merge_counts[(merged_label, kept_label)]["count"] += count

                md_content += "**Label Merge Patterns:**\n\n"
                md_content += "| Merged Label | Kept Label | Count |\n"
                md_content += "|--------------|------------|-------|\n"

                # Sort by count descending
                sorted_merges = sorted(
                    merge_counts.items(), key=lambda x: x[1]["count"], reverse=True
                )

                for (merged_label, kept_label), stats in sorted_merges:
                    md_content += (
                        f"| {merged_label} | {kept_label} | {stats['count']} |\n"
                    )

                md_content += "\n"
            else:
                md_content += (
                    "**No overlapping mentions found in gold annotations.**\n\n"
                )

        except Exception as e:
            md_content += f"**Error processing gold annotations:** {str(e)}\n\n"

        # Process predictions from each model
        for model in models:
            try:
                pred_corpus = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model
                )
                merged_corpus, pred_stats = merge_stacked_mentions(
                    pred_corpus,
                    prefer_larger=prefer_larger,
                    merge_gold=False,
                    merge_predicted=True,
                )

                md_content += f"""### {model.upper()} Predictions

**Mentions:**
- Original: {pred_stats["predicted_original_count"]}
- After merging: {pred_stats["predicted_merged_count"]}
- Merged: {pred_stats["predicted_original_count"] - pred_stats["predicted_merged_count"]}

**Relations:**
- Original: {pred_stats["predicted_relations_original"]}
- After merging: {pred_stats["predicted_relations_merged"]}
- Self-loops removed: {pred_stats["predicted_relations_self_loops"]}
- Duplicates removed: {pred_stats["predicted_relations_duplicates"]}

"""

                # Report self-loop relation labels
                if pred_stats["predicted_self_loop_labels"]:
                    from collections import Counter

                    label_counts = Counter(pred_stats["predicted_self_loop_labels"])
                    md_content += "**Self-loop Relation Labels:**\n\n"
                    md_content += "| Relation Label | Count |\n"
                    md_content += "|----------------|-------|\n"
                    for label, count in label_counts.most_common():
                        md_content += f"| {label} | {count} |\n"
                    md_content += "\n"

                # Aggregate merge statistics by label pairs
                if pred_stats["predicted_merges"]:
                    merge_counts = defaultdict(lambda: defaultdict(int))
                    for merged_label, kept_label, doc_id, count in pred_stats[
                        "predicted_merges"
                    ]:
                        merge_counts[(merged_label, kept_label)]["count"] += count

                    md_content += "**Label Merge Patterns:**\n\n"
                    md_content += "| Merged Label | Kept Label | Count |\n"
                    md_content += "|--------------|------------|-------|\n"

                    # Sort by count descending
                    sorted_merges = sorted(
                        merge_counts.items(), key=lambda x: x[1]["count"], reverse=True
                    )

                    for (merged_label, kept_label), stats in sorted_merges:
                        md_content += (
                            f"| {merged_label} | {kept_label} | {stats['count']} |\n"
                        )

                    md_content += "\n"
                else:
                    md_content += (
                        "**No overlapping mentions found in predictions.**\n\n"
                    )

            except Exception as e:
                md_content += (
                    f"**Error processing {model.upper()} predictions:** {str(e)}\n\n"
                )

    md_content += """
## Notes

- **Overlapping mentions**: Two mentions overlap if they share at least one character position in the same sentence
- **Span preference**: When merging, we keep the preferred span size and discard others
- **Relation remapping**: Relations are automatically updated to reference merged mention objects
- **Self-loop removal**: Relations where subject and object were merged are removed
- **Duplicate removal**: Duplicate relations (same subject-object-label) are removed

---
*Generated by UnifiedSciERE Mention Merging*
"""

    # Save markdown file
    preference_suffix = "larger" if prefer_larger else "smaller"
    md_path = output_dir / f"merge_report_{split}_{preference_suffix}.md"
    md_path.write_text(md_content)

    return md_path


if __name__ == "__main__":
    # Example: Generate merge report for all datasets
    report_path = generate_merge_report(
        datasets=["scier", "scinlp", "gsap-ere"],
        split="dev",
        models=["scier", "scinlp", "gsap-ere"],
        prefer_larger=True,
    )
    print(f"Generated merge report: {report_path}")
