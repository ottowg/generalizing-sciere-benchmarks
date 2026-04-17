"""Persistent storage for human annotations on abbreviation candidates.

Format
------
``data/abbreviation/annotations.jsonl`` — one JSON object per line:

    {"id": "A_abc123", "label": 1, "annotator": "alice", "timestamp": "2026-04-11T12:00:00"}

The *label* field is 1 (abbreviation), 0 (not an abbreviation), or 2 (inverse
correct — it is an abbreviation but the relation direction is swapped).

If the same candidate is annotated multiple times the **last** entry wins,
so corrections are always possible by simply appending a new line.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# Candidate ID helpers (stable, content-addressed)
# ---------------------------------------------------------------------------

def candidate_id_a(dataset: str, split: str, relation) -> str:
    """Stable ID for a Subtask A relation candidate.

    Keyed on (dataset, split, doc_id, subj_begin, subj_end, subj_label,
    relation_label, obj_begin, obj_end, obj_label, annotator) so that the
    same annotation triple always receives the same ID across detection runs.
    """
    s, o = relation.subject, relation.object
    key = (
        f"A|{dataset}|{split}|{relation.document_id}"
        f"|{s.begin}|{s.end}|{s.label}"
        f"|{relation.label}"
        f"|{o.begin}|{o.end}|{o.label}"
        f"|{relation.annotator}"
    )
    return "A_" + hashlib.sha1(key.encode()).hexdigest()[:16]


def candidate_id_b(dataset: str, split: str, mention) -> str:
    """Stable ID for a Subtask B single-span candidate.

    Keyed on (dataset, split, doc_id, begin, end, label, annotator).
    """
    key = (
        f"B|{dataset}|{split}|{mention.document_id}"
        f"|{mention.begin}|{mention.end}|{mention.label}"
        f"|{mention.annotator}"
    )
    return "B_" + hashlib.sha1(key.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def load_annotations(path: Path | str) -> dict[str, int]:
    """Return ``{candidate_id: label}`` from *path* (last write wins).

    Returns an empty dict if the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        return {}
    result: dict[str, int] = {}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                lbl = int(record["label"])
                result[record["id"]] = 1 if lbl == 2 else lbl  # 2=inverse → positive
            except (json.JSONDecodeError, KeyError):
                continue
    return result


def iter_annotations(path: Path | str) -> Iterator[dict]:
    """Yield every annotation record in order (raw dicts, no deduplication)."""
    path = Path(path)
    if not path.exists():
        return
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def save_annotation(
    path: Path | str,
    candidate_id: str,
    label: int,
    annotator: str = "unknown",
) -> None:
    """Append one annotation to *path*, creating the file if needed.

    Parameters
    ----------
    path:
        Path to the ``annotations.jsonl`` file.
    candidate_id:
        Stable ID produced by :func:`candidate_id_a` or :func:`candidate_id_b`.
    label:
        1 = abbreviation, 0 = not an abbreviation.
    annotator:
        Free-form name of the person (or script) making the annotation.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": candidate_id,
        "label": int(label),
        "annotator": annotator,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with path.open("a") as fh:
        fh.write(json.dumps(record) + "\n")
