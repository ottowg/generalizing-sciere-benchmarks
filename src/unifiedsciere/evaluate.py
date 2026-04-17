"""Shared helpers for converting Corpus objects to gsaphub evaluation format."""

from .types import Mention, Relation


def mention_to_gsaphub(m: Mention) -> dict[str, object]:
    """Convert a Mention to the dict format expected by gsaphub.evaluate."""
    return {
        "id": m.id,
        "doc_id": m.document_id,
        "sent_id": m.sent_idx,
        "text": m.text,
        "label": m.label,
        "begin": m.begin,
        "end": m.end,
    }


def relation_to_gsaphub(r: Relation, idx: int, annotator: str) -> dict[str, object]:
    """Convert a Relation to the dict format expected by gsaphub.evaluate."""
    return {
        "id": idx,
        "doc_id": r.subject.document_id,
        "sent_id": r.subject.sent_idx,
        "subject_id": r.subject.id,
        "object_id": r.object.id,
        "relation_label": r.label,
        "annotator": annotator,
    }


def filter_relations_with_valid_entities(
    rels: list[dict],
    ent_ids: set[str],
) -> list[dict]:
    """Keep only relations whose subject and object exist in the entity set."""
    return [r for r in rels if r["subject_id"] in ent_ids and r["object_id"] in ent_ids]
