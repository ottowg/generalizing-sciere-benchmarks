"""Fix entities and relations based on the abbreviates relation fixes from
get_best_abbr_relations.py.

The ``changes.json`` produced by that script has the following structure::

    {
        "ents_to_split": {
            "<doc_id>": [[begin_token, end_token, label], ...],
            ...
        },
        "rels_to_replace": {
            "<doc_id>": [[[s_b, s_e, o_b, o_e, label], [new_s_b, ...]], ...],
            ...
        }
    }

Entities in ``ents_to_split`` match the pattern ``"Long Form ( Short )"``;
the script splits them into two separate entities and inserts an *abbreviates*
relation between them.  Relations in ``rels_to_replace`` are rewritten (label
and/or direction) to use the canonical *abbreviates* label with the longer
span as the subject.

After processing, a JSON summary is written to *summary_path* (default:
``<changed_path>/changes_summary.json``) reporting per-file counts of changed
relations, added relations, deleted entities, and added entities.
"""

import json
from glob import glob
from itertools import chain
from pathlib import Path

# Type aliases for token-index-based span/relation tuples used internally.
# Each entity span is (begin_token, end_token, label).
# Each relation is (subj_begin, subj_end, obj_begin, obj_end, label).
SpanTuple = tuple[int, int, str]
RelTuple = tuple[int, int, int, int, str]

# Per-file statistics dict returned by process_file.
FileStats = dict[str, int]


def _empty_stats() -> FileStats:
    return {
        "relations_changed_to_abbr": 0,
        "relations_changed_subj_or_obj": 0,
        "relations_added": 0,
        "entities_deleted": 0,
        "entities_added": 0,
    }


def main(
    gold_path: str,
    changed_path: str,
    changes_fn: str,
    summary_path: str | None = None,
) -> None:
    """Apply abbreviation fixes to all JSONL files in *gold_path*.

    Reads the change specification from *changes_fn*, rewrites every
    ``*.jsonl`` file found in *gold_path* into *changed_path* with entities
    and relations corrected, then writes a markdown summary of the changes
    made to *summary_path*.

    Args:
        gold_path: Directory containing the original gold ``.jsonl`` files.
        changed_path: Directory to write the fixed ``.jsonl`` files into
            (created if it does not exist).
        changes_fn: Path to the ``changes.json`` file produced by
            ``get_best_abbr_relations.py``.
        summary_path: Where to write the JSON summary.  Defaults to
            ``<changed_path>/changes_summary.json``.
    """
    with open(changes_fn) as f:
        changes = json.load(f)
    files = sorted(glob(f"{gold_path}/*.jsonl"))
    changed_path = Path(changed_path)
    changed_path.mkdir(parents=True, exist_ok=True)

    all_stats: dict[str, FileStats] = {}
    for file in files:
        old_name = Path(file).name
        ds_name, split_fn = old_name.split("_", 1)
        target_path = changed_path / ds_name
        target_path.mkdir(parents=True, exist_ok=True)
        target_file = target_path / split_fn

        file_stats = process_file(file, target_file, changes)
        all_stats[Path(file).name] = file_stats

    _write_summary(
        all_stats,
        summary_path or str(changed_path / "changes_summary.json"),
    )


def _write_summary(all_stats: dict[str, FileStats], summary_path: str) -> None:
    """Write a JSON summary of per-file change counts to *summary_path*.

    The output has a ``"files"`` dict keyed by filename and a ``"total"``
    entry with the column sums::

        {
          "files": {
            "gsap_dev.jsonl": {
              "relations_changed": 3,
              "relations_added": 7,
              "entities_deleted": 7,
              "entities_added": 14
            },
            ...
          },
          "total": {
            "relations_changed": 4,
            ...
          }
        }

    Args:
        all_stats: Mapping of filename to :data:`FileStats`.
        summary_path: Destination path for the JSON file.
    """
    totals = _empty_stats()
    for stats in all_stats.values():
        for key in totals:
            totals[key] += stats[key]

    payload = {
        "files": dict(sorted(all_stats.items())),
        "total": totals,
    }

    out = Path(summary_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Summary written to {out}")


def process_file(
    file: str | Path,
    target_file: str | Path,
    changes: dict,
) -> FileStats:
    """Read *file* line by line, apply changes, and write to *target_file*.

    Args:
        file: Path to the source JSONL file.
        target_file: Path where the fixed JSONL file is written.
        changes: Parsed contents of ``changes.json``.

    Returns:
        Aggregated :data:`FileStats` for all documents in the file.
    """
    lines = []
    file_stats = _empty_stats()
    with open(file) as f:
        for line in f:
            doc = json.loads(line)
            changed_doc, doc_stats = process_doc(doc, changes)
            lines.append(changed_doc)
            for key in file_stats:
                file_stats[key] += doc_stats[key]
    with open(target_file, "w") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")
    return file_stats


def process_doc(doc: dict, changes: dict) -> tuple[dict, FileStats]:
    """Apply abbreviation fixes to a single document dict.

    Modifies the ``"ner"`` and ``"relations"`` fields and returns the updated
    document together with per-document change counts.

    Args:
        doc: A document dict with at least the keys ``"sentences"``,
            ``"ner"``, ``"relations"``, and either ``"doc_id"`` or
            ``"doc_key"``.
        changes: Parsed contents of ``changes.json`` with keys
            ``"ents_to_split"`` and ``"rels_to_replace"``.

    Returns:
        A ``(updated_doc, stats)`` pair where *stats* is a :data:`FileStats`
        dict with keys ``relations_changed_to_abbr``,
        ``relations_changed_subj_or_obj``, ``relations_added``,
        ``entities_deleted``, and ``entities_added``.
    """
    doc_tokens = list(chain(*doc["sentences"]))
    doc_id = doc["doc_id"] if "doc_id" in doc else doc["doc_key"]
    ents_to_split = changes["ents_to_split"].get(doc_id, [])
    ents_to_replace = get_ents_to_replace(doc_tokens, ents_to_split)
    rel_changes = changes["rels_to_replace"].get(doc_id, [])

    new_ner: list[list[list]] = []
    new_rels: list[list] = []
    stats = _empty_stats()

    for sent_ents, sent_rels in zip(doc["ner"], doc["relations"]):
        sent_ents = set([tuple(e) for e in sent_ents])
        sent_rels = set([tuple(r) for r in sent_rels])
        # get changes for this sentence — convert JSON lists to tuples for set lookup
        rel_changes_sent = [(r, rr) for r, rr in rel_changes if tuple(r) in sent_rels]
        changed_rels, n_to_abbr, n_subj_obj_rels = (
            change_abbreviation_relations_sentence(
                sent_rels, rel_changes_sent, doc_tokens
            )
        )
        # change the entities
        ents_to_replace_sent = {
            k: v for k, v in ents_to_replace.items() if (k in sent_ents)
        }
        changed_ents, changed_rels, n_subj_obj_ents = (
            change_abbreviation_entities_sentence(
                sent_ents, changed_rels, ents_to_replace_sent
            )
        )
        changed_ents = [list(e) for e in changed_ents]
        changed_ents.sort(key=lambda e: (e[0], e[1]))
        changed_rels.sort(key=lambda r: (r[0], r[1], r[2]))
        new_ner.append(changed_ents)
        new_rels.append([list(r) for r in changed_rels])

        n_splits = len(ents_to_replace_sent)
        stats["relations_changed_to_abbr"] += n_to_abbr
        stats["relations_changed_subj_or_obj"] += n_subj_obj_rels + n_subj_obj_ents
        stats["relations_added"] += n_splits  # one abbreviates rel per split
        stats["entities_deleted"] += n_splits  # one combined span removed per split
        stats["entities_added"] += 2 * n_splits  # long + short added per split

    doc["ner"] = new_ner
    doc["relations"] = new_rels
    return doc, stats


def get_ents_to_replace(
    doc_tokens: list[str],
    ents_to_split: list[list],
) -> dict[SpanTuple, tuple[SpanTuple, SpanTuple]]:
    """Build a mapping from combined ``"Long Form ( Short )"`` spans to their parts.

    Only spans that strictly follow the pattern
    ``<long tokens> ( <short tokens> )`` (i.e. where the closing parenthesis
    is the last token of the span) are included.  Spans that start with ``(``
    are skipped, as are spans where tokens appear after the closing ``)``.

    Args:
        doc_tokens: Flat list of all tokens in the document (across sentences).
        ents_to_split: List of ``[begin_token, end_token, label]`` triples
            (document-level token indices) identifying entities to split.

    Returns:
        A dict mapping each combined span ``(begin, end, label)`` to a
        ``((long_begin, long_end, label), (short_begin, short_end, label))``
        pair.
    """
    ents_to_replace: dict[SpanTuple, tuple[SpanTuple, SpanTuple]] = {}
    for begin, end, label in ents_to_split:
        span = doc_tokens[begin : end + 1]
        long_begin = begin
        long_end = -1
        short_begin = -1
        short_end = -1
        if span[0] == "(":
            continue
        for idx, token in enumerate(span, begin):
            if token == "(":
                long_end = idx - 1
                short_begin = idx + 1
            elif token == ")":
                short_end = idx - 1
        if short_end < end - 1:
            continue  # There is something after <long> (<abbr>)
        ents_to_replace[(begin, end, label)] = (
            (long_begin, long_end, label),
            (short_begin, short_end, label),
        )
    return ents_to_replace


def change_abbreviation_entities_sentence(
    sent_ents: set[SpanTuple],
    sent_rels: list,
    ents_to_replace_sent: dict[SpanTuple, tuple[SpanTuple, SpanTuple]],
) -> tuple[set[SpanTuple], list, int]:
    """Split combined abbreviation entities and insert *abbreviates* relations.

    For every entry in *ents_to_replace_sent*:

    * The combined span (e.g. ``"Bidirectional Encoder ( BERT )"``) is removed
      from *sent_ents* and replaced by the long and short sub-spans.
    * Any existing relation that references the combined span is updated to
      point to the long sub-span instead.
    * A new ``abbreviates`` relation ``(long_begin, long_end, short_begin,
      short_end, "abbreviates")`` is appended.

    Args:
        sent_ents: Mutable set of entity span tuples for the current sentence.
            Modified in-place.
        sent_rels: List of relation tuples for the current sentence.
        ents_to_replace_sent: Subset of ``get_ents_to_replace`` output that
            applies to this sentence (i.e. whose keys are in *sent_ents*).

    Returns:
        A ``(updated_sent_ents, new_rels, n_changed_subj_or_obj)`` triple
        where *n_changed_subj_or_obj* counts existing relations whose subject
        or object was redirected to the long sub-span.
    """
    rel_ent_changes = {
        (b, e): (b_r, e_r)
        for (b, e, m_l), ((b_r, e_r, _), _) in ents_to_replace_sent.items()
        if (b, e, m_l) in sent_ents
    }
    # change existing relations: replace old long spans with the first span of the splitted version.
    new_rels = []
    n_changed_subj_or_obj = 0
    for rel in sent_rels:
        s_b, s_e, o_b, o_e, rel_l = rel
        new_s_b, new_s_e = rel_ent_changes.get((s_b, s_e), (s_b, s_e))
        new_o_b, new_o_e = rel_ent_changes.get((o_b, o_e), (o_b, o_e))
        new_rels.append((new_s_b, new_s_e, new_o_b, new_o_e, rel_l))
        if (new_s_b, new_s_e) != (s_b, s_e) or (new_o_b, new_o_e) != (o_b, o_e):
            n_changed_subj_or_obj += 1
    # add the new abbreviation relation
    for (s_b, s_e, _), (o_b, o_e, _) in ents_to_replace_sent.values():
        new_rel = [s_b, s_e, o_b, o_e, "abbreviates"]
        new_rels.append(new_rel)
    # delete old entities
    sent_ents -= set(ents_to_replace_sent.keys())
    for new_long, new_short in ents_to_replace_sent.values():
        sent_ents.add(tuple(new_long))
        sent_ents.add(tuple(new_short))
    return sent_ents, new_rels, n_changed_subj_or_obj


def change_abbreviation_relations_sentence(
    rels: set[RelTuple],
    change: list[tuple],
    doc_tokens: list[str],
) -> tuple[list, int, int]:
    """Rewrite relation labels and directions according to *change*.

    Relations listed in *change* are replaced with their corrected versions
    (canonical *abbreviates* label, subject = short form).  For all other
    relations that involve an entity appearing as the *object* of an
    *abbreviates* relation, the entity reference is redirected to the long
    form (subject side).

    The *abbreviates* relation must have the shorter span as its subject.
    ``_check_direction`` enforces this by swapping subject and object when the
    current subject is the longer span.

    Args:
        rels: Set of relation tuples for the current sentence.
        change: List of ``(old_rel, new_rel)`` pairs where both elements are
            sequences of ``[s_b, s_e, o_b, o_e, label]`` (may be lists from
            JSON or tuples).
        doc_tokens: Flat list of all tokens in the document.

    Returns:
        A ``(fixed_rels, n_changed_to_abbr, n_changed_subj_or_obj)`` triple:

        * *n_changed_to_abbr* — relations directly replaced with a new
          *abbreviates* relation (from ``rels_to_replace``).
        * *n_changed_subj_or_obj* — other relations whose subject or object
          was redirected to the long mention.
    """
    fixed_rels = []
    n_changed_to_abbr = 0
    n_changed_subj_or_obj = 0
    change = _check_direction(change, doc_tokens)
    # Convert to a dict keyed by old relation tuple for O(1) lookup.
    # JSON deserialises relation arrays as lists, so we normalise to tuples.
    change = {tuple(e): tuple(r) for e, r in change}
    # Identify the short entity which should not be connected to other entities via relations.
    # * define the mention change for the correction
    ent_changes: dict[tuple[int, int], tuple[int, int]] = {}
    for rel, new_rel in change.items():
        s_b, s_e, o_b, o_e, _ = new_rel
        ent_changes[(s_b, s_e)] = o_b, o_e
    # Change all existing relations, where the abbr. is connected to other entities with connections to the long mention
    for rel in rels:
        s_b, s_e, o_b, o_e, rel_l = rel
        # replace relation if it is in the change dictionary
        if rel in change:
            fixed_rels.append(change[rel])
            n_changed_to_abbr += 1
        else:
            # only replace entities if they are in the ent_changes dictionary
            new_s_b, new_s_e = ent_changes.get((s_b, s_e), (s_b, s_e))
            new_o_b, new_o_e = ent_changes.get((o_b, o_e), (o_b, o_e))
            fixed_rels.append((new_s_b, new_s_e, new_o_b, new_o_e, rel_l))
            if (new_s_b, new_s_e) != (s_b, s_e) or (new_o_b, new_o_e) != (o_b, o_e):
                n_changed_subj_or_obj += 1
    return fixed_rels, n_changed_to_abbr, n_changed_subj_or_obj


def _span_len(begin: int, end: int, doc_tokens: list[str]) -> int:
    """Return the number of tokens in the span ``[begin, end]`` (inclusive)."""
    span = doc_tokens[begin : end + 1]
    return len(span)


def _check_direction(
    change: list[tuple],
    doc_tokens: list[str],
) -> list[tuple]:
    """Ensure every *abbreviates* relation has the shorter span as its subject.

    If the subject of a proposed replacement relation is *longer* than the
    object, the subject and object are swapped so that the short form is always
    the subject of *abbreviates*.

    Args:
        change: List of ``(original_rel, proposed_new_rel)`` pairs.
        doc_tokens: Flat list of all tokens in the document.

    Returns:
        A new list of ``(original_rel, corrected_new_rel)`` pairs.
    """
    corrected = []
    for rel, new_rel in change:
        s_b, s_e, o_b, o_e, rel_label = new_rel
        if _span_len(s_b, s_e, doc_tokens) > _span_len(o_b, o_e, doc_tokens):
            # wrong direction of abbreviates relation
            new_rel = o_b, o_e, s_b, s_e, rel_label
        corrected.append((rel, new_rel))
    return corrected


if __name__ == "__main__":
    gold_path = "data/gold"
    target_path = "data/gold_fixed"
    changes_fn = "data/abbreviation/changes.json"
    main(gold_path, target_path, changes_fn)
