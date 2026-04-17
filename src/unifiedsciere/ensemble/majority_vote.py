"""Majority vote ensemble for combining unified entity predictions.

Algorithm overview:
1. Collect predicted mentions from all models (already unified to shared schema).
2. Group mentions by overlapping spans within the same document, using gsaphub
   partial span matching — the same matching used in unification confusion analysis.
3. Within each overlap group, further split by predicted label. Groups that contain
   predictions from only one model are discarded (no majority). Groups with
   predictions from at least two models form a consensus candidate.
4. From each consensus group, select one representative mention. By default the
   longest span is preferred (broadest coverage); ties are broken by score.
5. Relations whose subject or object referred to a discarded or non-selected mention
   are re-wired to point to the selected representative where possible, or dropped
   if no mapping exists.
6. The result is a new Corpus whose `mentions_predicted` and `relations_predicted`
   contain only the consensus predictions.
"""

from collections import defaultdict
from dataclasses import replace
from typing import Literal

from gsaphub.match.spans import partial as partial_match

from ..types import Corpus, Mention, Relation


def majority_vote_ensemble(
    corpora: list[Corpus],
    prefer_longest_span: bool = True,
) -> Corpus:
    """Combine predictions from multiple unified corpora via majority vote.

    Each corpus in *corpora* must already have its predictions unified to the
    shared label schema (apply_unification_pipeline with apply_to_predicted=True
    before calling this function).

    The gold annotations are taken from the first corpus in the list (they are
    identical across corpora for the same test dataset).

    Args:
        corpora: Two or more corpora with unified predicted mentions/relations.
        prefer_longest_span: When True, the representative for each consensus
            group is the mention with the largest span (end - begin). When False,
            the mention with the highest score is selected.

    Returns:
        A new Corpus with:
        - `sentences` and `mentions` / `relation` from the first corpus (gold).
        - `mentions_predicted` containing the consensus entity set.
        - `relations_predicted` containing re-wired consensus relations.
    """
    if len(corpora) < 2:
        raise ValueError("majority_vote_ensemble requires at least two corpora.")

    # Collect all predicted mentions from all models, keeping track of origin
    all_pred_mentions: list[Mention] = []
    for corpus in corpora:
        all_pred_mentions.extend(corpus.mentions_predicted)

    # Convert to gsaphub dicts for span matching
    def _to_gh(m: Mention) -> dict:
        return {
            "id": m.id,
            "doc_id": m.document_id,
            "begin": m.begin,
            "end": m.end,
            "label": m.label,
            "annotator": m.annotator,
        }

    gh_mentions = [_to_gh(m) for m in all_pred_mentions]
    mention_by_id = {m.id: m for m in all_pred_mentions}

    # Run partial span matching: for each mention, find all overlapping mentions
    partial_match(gh_mentions, gh_mentions, target_key="overlapping_ids", only_same_annotator=False)

    # Union-Find to group overlapping mentions with the same label
    parent: dict[str, str] = {m["id"]: m["id"] for m in gh_mentions}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: str, y: str) -> None:
        parent[find(x)] = find(y)

    for gh_m in gh_mentions:
        m_label = gh_m["label"]
        for overlapping_id in gh_m.get("overlapping_ids", []):
            if overlapping_id == gh_m["id"]:
                continue
            other = mention_by_id.get(overlapping_id)
            if other is not None and other.label == m_label:
                union(gh_m["id"], overlapping_id)

    # Group mentions by their root in the union-find structure
    groups: dict[str, list[str]] = defaultdict(list)
    for m in all_pred_mentions:
        root = find(m.id)
        groups[root].append(m.id)

    # For each group, check if it spans at least two distinct annotators (models)
    # If so, select one representative; otherwise discard.
    selected_id_by_group: dict[str, str] = {}  # root -> chosen mention id
    remapping: dict[str, str] = {}  # any mention id -> chosen mention id

    for root, member_ids in groups.items():
        mentions_in_group = [mention_by_id[mid] for mid in member_ids]
        annotators = {m.annotator for m in mentions_in_group}

        if len(annotators) < 2:
            # Single-model prediction — discard; no remapping entry
            continue

        # Select representative
        if prefer_longest_span:
            representative = max(
                mentions_in_group,
                key=lambda m: (m.end - m.begin, m.score),
            )
        else:
            representative = max(
                mentions_in_group,
                key=lambda m: (m.score, m.end - m.begin),
            )

        selected_id_by_group[root] = representative.id
        for mid in member_ids:
            remapping[mid] = representative.id

    # Build the consensus mention list (unique selected mentions)
    seen_selected: set[str] = set()
    consensus_mentions: list[Mention] = []
    for chosen_id in selected_id_by_group.values():
        if chosen_id not in seen_selected:
            seen_selected.add(chosen_id)
            consensus_mentions.append(mention_by_id[chosen_id])

    # Re-wire relations: collect all predicted relations from all corpora,
    # map subject/object ids through remapping, keep if both endpoints survive.
    all_pred_relations: list[Relation] = []
    for corpus in corpora:
        all_pred_relations.extend(corpus.relations_predicted)

    seen_relation_keys: set[tuple] = set()
    consensus_relations: list[Relation] = []
    for rel in all_pred_relations:
        new_subj_id = remapping.get(rel.subject.id)
        new_obj_id = remapping.get(rel.object.id)
        if new_subj_id is None or new_obj_id is None:
            continue
        new_subj = mention_by_id[new_subj_id]
        new_obj = mention_by_id[new_obj_id]
        # Deduplicate relations by (subj_id, label, obj_id)
        rel_key = (new_subj_id, rel.label, new_obj_id)
        if rel_key in seen_relation_keys:
            continue
        seen_relation_keys.add(rel_key)
        consensus_relations.append(
            Relation(
                subject=new_subj,
                label=rel.label,
                object=new_obj,
                score=rel.score,
                annotator="ensemble",
                dataset=rel.dataset,
            )
        )

    # Use gold from the first corpus
    gold_corpus = corpora[0]
    return Corpus(
        sentences=gold_corpus.sentences,
        mentions=gold_corpus.mentions,
        relation=gold_corpus.relation,
        mentions_predicted=consensus_mentions,
        relations_predicted=consensus_relations,
    )
