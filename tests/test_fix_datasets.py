"""Tests for scripts/abbreviation/fix_datasets.py.

The module operates on raw JSONL dicts (the on-disk format used by the gold
data), so tests work directly with those dicts rather than with the
``Mention`` / ``Relation`` domain objects.

Token layout used in most tests
--------------------------------
Index:  0     1      2               3          4                  5    6      7
Token: "We"  "use"  "Bidirectional" "Encoder"  "Representations"  "("  "BERT"  ")"

The entity ``Bidirectional Encoder Representations ( BERT )`` spans tokens
[2, 7] and should be split into:
  long form:  tokens [2, 4]  → "Bidirectional Encoder Representations"
  short form: tokens [6, 6]  → "BERT"
"""

import json
import sys
from pathlib import Path

import pytest

# The script lives outside the package; add its directory to sys.path so we
# can import it directly without hacks in the script itself.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "abbreviation"))

from fix_datasets import (
    _check_direction,
    _span_len,
    change_abbreviation_entities_sentence,
    change_abbreviation_relations_sentence,
    get_ents_to_replace,
    process_doc,
    process_file,
    _empty_stats,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TOKENS = ["We", "use", "Bidirectional", "Encoder", "Representations", "(", "BERT", ")"]
#          0      1      2               3          4                  5    6       7


# ---------------------------------------------------------------------------
# _span_len
# ---------------------------------------------------------------------------


def test_span_len_single_token():
    assert _span_len(6, 6, TOKENS) == 1


def test_span_len_multi_token():
    assert _span_len(2, 4, TOKENS) == 3


# ---------------------------------------------------------------------------
# get_ents_to_replace
# ---------------------------------------------------------------------------


def test_get_ents_to_replace_basic():
    """Standard 'Long Form ( Short )' pattern is split correctly."""
    ents_to_split = [[2, 7, "Method"]]
    result = get_ents_to_replace(TOKENS, ents_to_split)
    assert (2, 7, "Method") in result
    long_span, short_span = result[(2, 7, "Method")]
    assert long_span == (2, 4, "Method")
    assert short_span == (6, 6, "Method")


def test_get_ents_to_replace_skips_span_starting_with_paren():
    """Spans that begin with '(' are skipped (only the short form is annotated)."""
    tokens = ["(", "BERT", ")"]
    ents_to_split = [[0, 2, "Method"]]
    result = get_ents_to_replace(tokens, ents_to_split)
    assert result == {}


def test_get_ents_to_replace_skips_trailing_tokens():
    """Spans with tokens after the closing ')' are skipped."""
    # "Long Form ( Short ) extra"
    tokens = ["Long", "Form", "(", "Short", ")", "extra"]
    ents_to_split = [[0, 5, "Method"]]
    result = get_ents_to_replace(tokens, ents_to_split)
    assert result == {}


def test_get_ents_to_replace_empty_input():
    result = get_ents_to_replace(TOKENS, [])
    assert result == {}


def test_get_ents_to_replace_multiple_entities():
    """Two independent abbreviation spans in the same document."""
    tokens = [
        "Natural", "Language", "Processing", "(", "NLP", ")",  # 0-5
        "and",                                                   # 6
        "Convolutional", "Neural", "Network", "(", "CNN", ")",  # 7-12
    ]
    ents_to_split = [[0, 5, "Task"], [7, 12, "Method"]]
    result = get_ents_to_replace(tokens, ents_to_split)
    assert (0, 5, "Task") in result
    assert (7, 12, "Method") in result
    assert result[(0, 5, "Task")] == ((0, 2, "Task"), (4, 4, "Task"))
    assert result[(7, 12, "Method")] == ((7, 9, "Method"), (11, 11, "Method"))


# ---------------------------------------------------------------------------
# _check_direction
# ---------------------------------------------------------------------------


def test_check_direction_no_swap_needed():
    """Subject is already the short span — no swap (short abbreviates long)."""
    # short form (1 token, index 6-6) → long form (3 tokens, index 2-4): correct
    change = [([0, 0, 5, 5, "Used-for"], [6, 6, 2, 4, "abbreviates"])]
    result = _check_direction(change, TOKENS)
    assert len(result) == 1
    orig, new = result[0]
    assert tuple(new) == (6, 6, 2, 4, "abbreviates")


def test_check_direction_swaps_when_subject_is_longer():
    """Subject is the longer form — subject and object are swapped to put short first."""
    # long form (3 tokens, index 2-4) as subject: wrong direction → swap
    change = [([0, 0, 5, 5, "Used-for"], [2, 4, 6, 6, "abbreviates"])]
    result = _check_direction(change, TOKENS)
    orig, new = result[0]
    # after swap: short form (6-6) becomes subject, long form (2-4) becomes object
    assert tuple(new) == (6, 6, 2, 4, "abbreviates")


def test_check_direction_preserves_original_rel():
    """The original relation in the pair is not modified by direction check."""
    original = [5, 5, 0, 0, "some-label"]
    change = [(original, [6, 6, 2, 4, "abbreviates"])]
    result = _check_direction(change, TOKENS)
    assert result[0][0] is original


# ---------------------------------------------------------------------------
# change_abbreviation_relations_sentence
# ---------------------------------------------------------------------------


def test_change_abbr_rels_replaces_relation():
    """A relation in the change list is replaced and n_changed_to_abbr is 1.

    _check_direction normalises to short-first, so the long form (2-4, 3
    tokens) becomes the object and the short form (6-6, 1 token) the subject.
    """
    rels = {(0, 0, 5, 5, "Used-for")}
    # Proposed new relation has long form as subject — _check_direction will swap it.
    change = [([0, 0, 5, 5, "Used-for"], [2, 4, 6, 6, "abbreviates"])]
    result, n_to_abbr, n_subj_obj = change_abbreviation_relations_sentence(rels, change, TOKENS)
    assert (6, 6, 2, 4, "abbreviates") in result
    assert (0, 0, 5, 5, "Used-for") not in result
    assert n_to_abbr == 1
    assert n_subj_obj == 0


def test_change_abbr_rels_empty_change_returns_all_rels():
    """With no changes, all original relations are returned unchanged."""
    rels = {(0, 0, 5, 5, "Used-for"), (1, 1, 6, 6, "Part-of")}
    result, n_to_abbr, n_subj_obj = change_abbreviation_relations_sentence(rels, [], TOKENS)
    assert set(result) == rels
    assert n_to_abbr == 0
    assert n_subj_obj == 0


def test_change_abbr_rels_direction_not_changed_when_already_correct():
    """When short form is already the subject no swap occurs."""
    rels = {(0, 0, 5, 5, "Used-for")}
    # short form (6-6, 1 token) already as subject — no swap needed
    change = [([0, 0, 5, 5, "Used-for"], [6, 6, 2, 4, "abbreviates"])]
    result, n_to_abbr, _ = change_abbreviation_relations_sentence(rels, change, TOKENS)
    assert (6, 6, 2, 4, "abbreviates") in result
    assert n_to_abbr == 1


def test_change_abbr_rels_indirect_subj_obj_counted():
    """A relation whose subject coincides with a replaced relation's new subject
    is redirected and counted in n_changed_subj_or_obj."""
    # rels_to_replace: (6,6)→(2,4) gets fixed to short→long abbreviates.
    # Another relation (6,6) → (0,0) should have its subject redirected to (2,4).
    #
    # After _check_direction the new abbr rel is (6,6,2,4,"abbreviates"),
    # so ent_changes = {(6,6): (2,4)}.
    # The extra rel (6,6,0,0,"Part-of") will have its subject changed to (2,4).
    rels = {(0, 0, 5, 5, "Used-for"), (6, 6, 0, 0, "Part-of")}
    change = [([0, 0, 5, 5, "Used-for"], [6, 6, 2, 4, "abbreviates"])]
    result, n_to_abbr, n_subj_obj = change_abbreviation_relations_sentence(rels, change, TOKENS)
    assert n_to_abbr == 1
    assert n_subj_obj == 1
    # the Part-of relation should have its subject redirected to (2,4)
    part_of = [r for r in result if r[4] == "Part-of"]
    assert len(part_of) == 1
    assert tuple(part_of[0])[:2] == (2, 4)


def test_change_abbr_rels_unrelated_rel_kept():
    """Relations not mentioned in the change list are passed through."""
    rels = {(0, 0, 5, 5, "Used-for"), (1, 1, 3, 4, "Part-of")}
    change = [([0, 0, 5, 5, "Used-for"], [2, 4, 6, 6, "abbreviates"])]
    result, _, _ = change_abbreviation_relations_sentence(rels, change, TOKENS)
    assert any(r[4] == "Part-of" for r in result)


# ---------------------------------------------------------------------------
# change_abbreviation_entities_sentence
# ---------------------------------------------------------------------------


def test_change_abbr_ents_splits_entity():
    """Combined span is replaced by long and short sub-spans."""
    sent_ents = {(2, 7, "Method")}
    sent_rels = []
    ents_to_replace = {
        (2, 7, "Method"): ((2, 4, "Method"), (6, 6, "Method")),
    }
    new_ents, new_rels, n_subj_obj = change_abbreviation_entities_sentence(
        sent_ents, sent_rels, ents_to_replace
    )
    assert (2, 7, "Method") not in new_ents
    assert (2, 4, "Method") in new_ents
    assert (6, 6, "Method") in new_ents
    assert n_subj_obj == 0  # no existing relations to redirect


def test_change_abbr_ents_adds_abbreviates_relation():
    """An *abbreviates* relation is added for each split entity."""
    sent_ents = {(2, 7, "Method")}
    sent_rels = []
    ents_to_replace = {
        (2, 7, "Method"): ((2, 4, "Method"), (6, 6, "Method")),
    }
    _, new_rels, _ = change_abbreviation_entities_sentence(
        sent_ents, sent_rels, ents_to_replace
    )
    abbr_rels = [r for r in new_rels if r[4] == "abbreviates"]
    assert len(abbr_rels) == 1
    assert abbr_rels[0][:4] == (2, 4, 6, 6) or abbr_rels[0][:4] == [2, 4, 6, 6]


def test_change_abbr_ents_redirects_existing_relation():
    """A relation pointing to the combined span is redirected and counted."""
    # Existing: some_ent (0-0) --Used-for--> combined (2-7)
    sent_ents = {(0, 0, "Task"), (2, 7, "Method")}
    sent_rels = [(0, 0, 2, 7, "Used-for")]
    ents_to_replace = {
        (2, 7, "Method"): ((2, 4, "Method"), (6, 6, "Method")),
    }
    _, new_rels, n_subj_obj = change_abbreviation_entities_sentence(
        sent_ents, sent_rels, ents_to_replace
    )
    # The "Used-for" relation should now point to the long sub-span (2-4)
    used_for_rels = [r for r in new_rels if r[4] == "Used-for"]
    assert len(used_for_rels) == 1
    assert tuple(used_for_rels[0])[:4] == (0, 0, 2, 4)
    assert n_subj_obj == 1


def test_change_abbr_ents_no_change_when_no_match():
    """Entities not in ents_to_replace are left untouched."""
    sent_ents = {(0, 0, "Task")}
    sent_rels = [(0, 0, 1, 1, "Used-for")]
    new_ents, new_rels, n_subj_obj = change_abbreviation_entities_sentence(
        sent_ents, sent_rels, {}
    )
    assert (0, 0, "Task") in new_ents
    assert len(new_rels) == 1
    assert n_subj_obj == 0


# ---------------------------------------------------------------------------
# process_doc
# ---------------------------------------------------------------------------


def _make_doc(sentences, ner, relations, doc_id="doc1"):
    return {
        "doc_id": doc_id,
        "sentences": sentences,
        "ner": ner,
        "relations": relations,
    }


def test_process_doc_returns_tuple():
    """process_doc must return (dict, stats) — it was returning None before the fix."""
    doc = _make_doc(
        sentences=[["We", "use", "BERT", "."]],
        ner=[[]],
        relations=[[]],
    )
    changes = {"ents_to_split": {}, "rels_to_replace": {}}
    result, stats = process_doc(doc, changes)
    assert isinstance(result, dict)
    assert set(stats.keys()) == {
        "relations_changed_to_abbr", "relations_changed_subj_or_obj",
        "relations_added", "entities_deleted", "entities_added",
    }


def test_process_doc_no_changes_preserves_ner_and_rels():
    """With an empty changes dict, ner and relations are passed through unchanged."""
    doc = _make_doc(
        sentences=[["We", "use", "BERT", "."]],
        ner=[[[2, 2, "Method"]]],
        relations=[[[0, 0, 2, 2, "Used-for"]]],
    )
    changes = {"ents_to_split": {}, "rels_to_replace": {}}
    result, stats = process_doc(doc, changes)
    assert result["ner"] == [[[2, 2, "Method"]]]
    assert result["relations"] == [[[0, 0, 2, 2, "Used-for"]]]
    assert stats == _empty_stats()


def test_process_doc_splits_entity():
    """An entity in ents_to_split is split into two and an abbreviates rel is added."""
    # Sentence tokens: "Bidirectional Encoder Representations ( BERT ) ."
    sentences = [["Bidirectional", "Encoder", "Representations", "(", "BERT", ")", "."]]
    doc = _make_doc(
        sentences=sentences,
        ner=[[[0, 5, "Method"]]],
        relations=[[]],
    )
    changes = {
        "ents_to_split": {"doc1": [[0, 5, "Method"]]},
        "rels_to_replace": {},
    }
    result, stats = process_doc(doc, changes)
    flat_ner = result["ner"][0]
    spans = [tuple(e) for e in flat_ner]
    assert (0, 2, "Method") in spans  # long form
    assert (4, 4, "Method") in spans  # short form
    assert (0, 5, "Method") not in spans  # combined span gone

    flat_rels = result["relations"][0]
    abbr_rels = [r for r in flat_rels if r[4] == "abbreviates"]
    assert len(abbr_rels) == 1

    assert stats["entities_deleted"] == 1
    assert stats["entities_added"] == 2
    assert stats["relations_added"] == 1
    assert stats["relations_changed_to_abbr"] == 0
    assert stats["relations_changed_subj_or_obj"] == 0


def test_process_doc_replaces_relation():
    """A relation in rels_to_replace is updated to the new label/direction."""
    sentences = [["Bidirectional", "Encoder", "(", "BE", ")", "is", "great", "."]]
    #              0                1          2    3    4    5    6       7
    doc = _make_doc(
        sentences=sentences,
        ner=[[[0, 1, "Method"], [3, 3, "Method"]]],
        relations=[[[0, 1, 5, 7, "Used-for"]]],
    )
    changes = {
        "ents_to_split": {},
        "rels_to_replace": {
            "doc1": [
                [[0, 1, 5, 7, "Used-for"], [0, 1, 3, 3, "abbreviates"]],
            ]
        },
    }
    result, stats = process_doc(doc, changes)
    flat_rels = result["relations"][0]
    labels = [r[4] for r in flat_rels]
    assert "abbreviates" in labels
    assert "Used-for" not in labels
    assert stats["relations_changed_to_abbr"] == 1
    assert stats["relations_changed_subj_or_obj"] == 0
    assert stats["relations_added"] == 0


def test_process_doc_uses_doc_key_fallback():
    """Documents that use 'doc_key' instead of 'doc_id' are handled correctly."""
    doc = {
        "doc_key": "doc42",
        "sentences": [["token"]],
        "ner": [[]],
        "relations": [[]],
    }
    changes = {"ents_to_split": {}, "rels_to_replace": {}}
    result, stats = process_doc(doc, changes)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# process_file (integration)
# ---------------------------------------------------------------------------


def test_process_file_writes_valid_jsonl(tmp_path):
    """process_file reads a JSONL file and writes a valid JSONL file."""
    doc = {
        "doc_id": "d1",
        "sentences": [["BERT", "is", "a", "model", "."]],
        "ner": [[[0, 0, "Method"]]],
        "relations": [[]],
    }
    src = tmp_path / "test.jsonl"
    src.write_text(json.dumps(doc) + "\n")
    dst = tmp_path / "fixed.jsonl"
    changes = {"ents_to_split": {}, "rels_to_replace": {}}
    stats = process_file(src, dst, changes)

    lines = dst.read_text().strip().splitlines()
    assert len(lines) == 1
    out = json.loads(lines[0])
    assert out["doc_id"] == "d1"
    assert out["ner"] == [[[0, 0, "Method"]]]
    assert stats == _empty_stats()


def test_process_file_returns_aggregated_stats(tmp_path):
    """Stats are aggregated across all documents in the file."""
    # Two docs: one with an entity split, one clean.
    doc1 = {
        "doc_id": "d1",
        "sentences": [["Long", "Form", "(", "LF", ")", "."]],
        "ner": [[[0, 4, "Method"]]],
        "relations": [[]],
    }
    doc2 = {
        "doc_id": "d2",
        "sentences": [["plain", "sentence", "."]],
        "ner": [[[0, 0, "Task"]]],
        "relations": [[]],
    }
    src = tmp_path / "multi.jsonl"
    src.write_text(json.dumps(doc1) + "\n" + json.dumps(doc2) + "\n")
    dst = tmp_path / "fixed_multi.jsonl"
    changes = {
        "ents_to_split": {"d1": [[0, 4, "Method"]]},
        "rels_to_replace": {},
    }
    stats = process_file(src, dst, changes)

    assert stats["entities_deleted"] == 1
    assert stats["entities_added"] == 2
    assert stats["relations_added"] == 1
    assert stats["relations_changed_to_abbr"] == 0
    assert stats["relations_changed_subj_or_obj"] == 0


def test_main_writes_summary_file(tmp_path):
    """main writes a markdown summary file listing per-file change counts."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "abbreviation"))
    from fix_datasets import main

    doc = {
        "doc_id": "d1",
        "sentences": [["Long", "Form", "(", "LF", ")", "."]],
        "ner": [[[0, 4, "Method"]]],
        "relations": [[]],
    }
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    (gold_dir / "gsap_dev.jsonl").write_text(json.dumps(doc) + "\n")

    changed_dir = tmp_path / "gold_fixed"
    changes = {
        "ents_to_split": {"d1": [[0, 4, "Method"]]},
        "rels_to_replace": {},
    }
    changes_file = tmp_path / "changes.json"
    changes_file.write_text(json.dumps(changes))

    summary_file = tmp_path / "summary.json"
    main(str(gold_dir), str(changed_dir), str(changes_file), str(summary_file))

    assert summary_file.exists()
    data = json.loads(summary_file.read_text())
    assert "gsap_dev.jsonl" in data["files"]
    assert set(data["files"]["gsap_dev.jsonl"].keys()) == {
        "relations_changed_to_abbr", "relations_changed_subj_or_obj",
        "relations_added", "entities_deleted", "entities_added",
    }
    assert "total" in data
    assert data["total"]["entities_deleted"] == data["files"]["gsap_dev.jsonl"]["entities_deleted"]
