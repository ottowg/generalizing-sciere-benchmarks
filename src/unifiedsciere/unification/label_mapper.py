"""Label mapping functions for unifying entity labels across datasets.

This module provides functions to map entity labels from different annotation
schemes to a unified label set, and to drop mentions that don't map to the
unified schema.
"""

from pathlib import Path
from typing import Literal

import yaml

from ..types import Corpus, Mention, Relation


def load_label_mappings(mapping_file: Path | None = None) -> dict:
    """Load label mappings from YAML file.

    Args:
        mapping_file: Path to YAML file with label mappings.
                     If None, uses default label_mappings.yaml in this directory.

    Returns:
        Dictionary with label mappings
    """
    if mapping_file is None:
        mapping_file = Path(__file__).parent / "label_mappings.yaml"

    with open(mapping_file, "r") as f:
        return yaml.safe_load(f)


def drop_unmapped_mentions(
    corpus: Corpus,
    dataset: Literal["scier", "scinlp", "gsap"],
    drop_gold: bool = True,
    drop_predicted: bool = True,
    mapping_file: Path | None = None,
) -> tuple[Corpus, dict]:
    """Drop mentions that map to null in the unified schema.

    This function removes mentions whose labels don't map to the unified label set,
    along with any relations that reference those mentions.

    Args:
        corpus: Input corpus
        dataset: Source dataset name to determine which mapping to use
        drop_gold: If True, drop unmapped gold mentions
        drop_predicted: If True, drop unmapped predicted mentions
        mapping_file: Optional path to custom mapping file

    Returns:
        Tuple of:
        - New Corpus with unmapped mentions and their relations removed
        - Dictionary with statistics about dropped mentions/relations
    """
    mappings = load_label_mappings(mapping_file)
    label_map = mappings["mappings"][dataset]

    # Find labels that map to null
    null_labels = {label for label, unified in label_map.items() if unified is None}

    stats = {
        "gold_mentions_original": len(corpus.mentions),
        "gold_mentions_dropped": 0,
        "gold_mentions_kept": len(corpus.mentions),
        "gold_relations_original": len(corpus.relation),
        "gold_relations_dropped": 0,
        "gold_relations_kept": len(corpus.relation),
        "predicted_mentions_original": len(corpus.mentions_predicted),
        "predicted_mentions_dropped": 0,
        "predicted_mentions_kept": len(corpus.mentions_predicted),
        "predicted_relations_original": len(corpus.relations_predicted),
        "predicted_relations_dropped": 0,
        "predicted_relations_kept": len(corpus.relations_predicted),
        "dropped_labels": list(null_labels),
    }

    # Process gold mentions
    if drop_gold:
        # Filter out mentions with null labels
        kept_mentions = [m for m in corpus.mentions if m.label not in null_labels]
        kept_mention_ids = {m.id for m in kept_mentions}

        # Filter relations that reference dropped mentions
        kept_relations = [
            r
            for r in corpus.relation
            if r.subject.id in kept_mention_ids and r.object.id in kept_mention_ids
        ]

        stats["gold_mentions_dropped"] = len(corpus.mentions) - len(kept_mentions)
        stats["gold_mentions_kept"] = len(kept_mentions)
        stats["gold_relations_dropped"] = len(corpus.relation) - len(kept_relations)
        stats["gold_relations_kept"] = len(kept_relations)
    else:
        kept_mentions = corpus.mentions
        kept_relations = corpus.relation

    # Process predicted mentions
    if drop_predicted:
        # Filter out mentions with null labels
        kept_mentions_pred = [
            m for m in corpus.mentions_predicted if m.label not in null_labels
        ]
        kept_mention_ids_pred = {m.id for m in kept_mentions_pred}

        # Filter relations that reference dropped mentions
        kept_relations_pred = [
            r
            for r in corpus.relations_predicted
            if r.subject.id in kept_mention_ids_pred
            and r.object.id in kept_mention_ids_pred
        ]

        stats["predicted_mentions_dropped"] = len(corpus.mentions_predicted) - len(
            kept_mentions_pred
        )
        stats["predicted_mentions_kept"] = len(kept_mentions_pred)
        stats["predicted_relations_dropped"] = len(corpus.relations_predicted) - len(
            kept_relations_pred
        )
        stats["predicted_relations_kept"] = len(kept_relations_pred)
    else:
        kept_mentions_pred = corpus.mentions_predicted
        kept_relations_pred = corpus.relations_predicted

    # Create new corpus with filtered mentions and relations
    filtered_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=kept_mentions,
        relation=kept_relations,
        mentions_predicted=kept_mentions_pred,
        relations_predicted=kept_relations_pred,
    )

    return filtered_corpus, stats


def map_labels_to_unified(
    corpus: Corpus,
    dataset: Literal["scier", "scinlp", "gsap"],
    map_gold: bool = True,
    map_predicted: bool = True,
    mapping_file: Path | None = None,
) -> tuple[Corpus, dict]:
    """Map entity labels to the unified label set.

    This function transforms entity labels from dataset-specific schemas
    to a unified label set (Dataset, Method, Metric, Task).

    Args:
        corpus: Input corpus
        dataset: Source dataset name to determine which mapping to use
        map_gold: If True, map gold mention labels
        map_predicted: If True, map predicted mention labels
        mapping_file: Optional path to custom mapping file

    Returns:
        Tuple of:
        - New Corpus with labels mapped to unified schema
        - Dictionary with statistics about label mappings
    """
    mappings = load_label_mappings(mapping_file)
    label_map = mappings["mappings"][dataset]

    # Track mapping statistics
    from collections import defaultdict

    stats = {
        "gold_label_changes": defaultdict(lambda: defaultdict(int)),
        "predicted_label_changes": defaultdict(lambda: defaultdict(int)),
        "gold_mentions_mapped": 0,
        "predicted_mentions_mapped": 0,
    }

    # Process gold mentions
    if map_gold:
        mapped_mentions = []
        for mention in corpus.mentions:
            unified_label = label_map.get(mention.label)

            if unified_label is None:
                # Skip mentions that map to null (should have been dropped already)
                continue

            # Create new mention with mapped label, preserve original label
            mapped_mention = Mention(
                id=mention.id,
                document_id=mention.document_id,
                sent_idx=mention.sent_idx,
                text=mention.text,
                label=unified_label,
                begin=mention.begin,
                end=mention.end,
                begin_token=mention.begin_token,
                end_token=mention.end_token,
                split=mention.split,
                score=mention.score,
                annotator=mention.annotator,
                dataset=mention.dataset,
                label_original=mention.label,  # Preserve original label before mapping
            )
            mapped_mentions.append(mapped_mention)

            # Track label changes
            if mention.label != unified_label:
                stats["gold_label_changes"][mention.label][unified_label] += 1
                stats["gold_mentions_mapped"] += 1
    else:
        mapped_mentions = corpus.mentions

    # Process predicted mentions
    if map_predicted:
        mapped_mentions_pred = []
        for mention in corpus.mentions_predicted:
            unified_label = label_map.get(mention.label)

            if unified_label is None:
                # Skip mentions that map to null (should have been dropped already)
                continue

            # Create new mention with mapped label, preserve original label
            mapped_mention = Mention(
                id=mention.id,
                document_id=mention.document_id,
                sent_idx=mention.sent_idx,
                text=mention.text,
                label=unified_label,
                begin=mention.begin,
                end=mention.end,
                begin_token=mention.begin_token,
                end_token=mention.end_token,
                split=mention.split,
                score=mention.score,
                annotator=mention.annotator,
                dataset=mention.dataset,
                label_original=mention.label,  # Preserve original label before mapping
            )
            mapped_mentions_pred.append(mapped_mention)

            # Track label changes
            if mention.label != unified_label:
                stats["predicted_label_changes"][mention.label][unified_label] += 1
                stats["predicted_mentions_mapped"] += 1
    else:
        mapped_mentions_pred = corpus.mentions_predicted

    # Relations remain unchanged (they reference mentions by ID, not label)
    # But we need to update the mention objects in the relations to point to mapped mentions
    mapped_mention_dict = {m.id: m for m in mapped_mentions}
    mapped_mention_pred_dict = {m.id: m for m in mapped_mentions_pred}

    # Update gold relations
    updated_relations = []
    for rel in corpus.relation:
        updated_subject = mapped_mention_dict.get(rel.subject.id, rel.subject)
        updated_object = mapped_mention_dict.get(rel.object.id, rel.object)

        updated_relation = Relation(
            subject=updated_subject,
            label=rel.label,
            object=updated_object,
            score=rel.score,
            annotator=rel.annotator,
            dataset=rel.dataset,
        )
        updated_relations.append(updated_relation)

    # Update predicted relations
    updated_relations_pred = []
    for rel in corpus.relations_predicted:
        updated_subject = mapped_mention_pred_dict.get(rel.subject.id, rel.subject)
        updated_object = mapped_mention_pred_dict.get(rel.object.id, rel.object)

        updated_relation = Relation(
            subject=updated_subject,
            label=rel.label,
            object=updated_object,
            score=rel.score,
            annotator=rel.annotator,
            dataset=rel.dataset,
        )
        updated_relations_pred.append(updated_relation)

    # Create new corpus with mapped labels
    mapped_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=mapped_mentions,
        relation=updated_relations,
        mentions_predicted=mapped_mentions_pred,
        relations_predicted=updated_relations_pred,
    )

    # Convert defaultdicts to regular dicts for cleaner output
    stats["gold_label_changes"] = dict(stats["gold_label_changes"])
    stats["predicted_label_changes"] = dict(stats["predicted_label_changes"])

    return mapped_corpus, stats
