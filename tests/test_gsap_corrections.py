"""Tests for unifiedsciere.unification.gsap_specific_corrections."""

import json

import pytest
from conftest import make_corpus, make_mention, make_relation

from unifiedsciere.unification.gsap_specific_corrections import (
    filter_gsap_mentions,
    generate_correction_report,
)


@pytest.fixture
def analysis_file(tmp_path):
    """Create a JSON analysis file with unmatched text counts."""
    data = {
        "unmatched_by_text": {
            "the model": {"count": 5, "labels": ["MLModelGeneric"]},
            "models": {"count": 3, "labels": ["MLModelGeneric"]},
            "fine-tuning": {"count": 1, "labels": ["Method"]},  # below threshold
        }
    }
    p = tmp_path / "analysis.json"
    p.write_text(json.dumps(data))
    return p


@pytest.fixture
def gsap_corpus():
    """Corpus with some mentions that match the analysis texts."""
    p1 = make_mention(
        id="p1", text="the model", label="MLModelGeneric", annotator="gsap"
    )
    p2 = make_mention(
        id="p2", text="BERT", label="Method", annotator="gsap", begin=10, end=14
    )
    p3 = make_mention(
        id="p3",
        text="models",
        label="MLModelGeneric",
        annotator="gsap",
        begin=20,
        end=26,
    )
    p4 = make_mention(
        id="p4", text="fine-tuning", label="Method", annotator="gsap", begin=30, end=41
    )

    pr1 = make_relation(p1, p2, label="Used-for", annotator="gsap")
    pr2 = make_relation(p2, p3, label="Used-for", annotator="gsap")

    g1 = make_mention(id="g1", text="BERT", label="Method", begin=10, end=14)
    gr1 = make_relation(g1, g1, label="Same")  # dummy

    return make_corpus(
        mentions=[g1],
        relations=[gr1],
        mentions_predicted=[p1, p2, p3, p4],
        relations_predicted=[pr1, pr2],
    )


# ---------- filter_gsap_mentions ----------


def test_filter_predicted_mentions(gsap_corpus, analysis_file):
    filtered, stats = filter_gsap_mentions(gsap_corpus, analysis_file, min_count=2)
    # p1 ("the model", count=5) and p3 ("models", count=3) should be filtered
    # p4 ("fine-tuning", count=1) below threshold, kept
    remaining_ids = {m.id for m in filtered.mentions_predicted}
    assert "p1" not in remaining_ids
    assert "p3" not in remaining_ids
    assert "p2" in remaining_ids
    assert "p4" in remaining_ids
    assert stats["predicted_mentions_filtered"] == 2


def test_filter_respects_min_count(gsap_corpus, analysis_file):
    """With min_count=4, only 'the model' (count=5) should be filtered."""
    filtered, stats = filter_gsap_mentions(gsap_corpus, analysis_file, min_count=4)
    remaining_ids = {m.id for m in filtered.mentions_predicted}
    assert "p1" not in remaining_ids  # "the model" count=5 >= 4
    assert "p3" in remaining_ids  # "models" count=3 < 4
    assert stats["predicted_mentions_filtered"] == 1


def test_filter_relations_referencing_filtered_mentions(gsap_corpus, analysis_file):
    filtered, stats = filter_gsap_mentions(gsap_corpus, analysis_file, min_count=2)
    # pr1 (p1->p2): p1 filtered, so relation dropped
    # pr2 (p2->p3): p3 filtered, so relation dropped
    assert len(filtered.relations_predicted) == 0
    assert stats["predicted_relations_filtered"] == 2


def test_filter_predicted_false(gsap_corpus, analysis_file):
    filtered, stats = filter_gsap_mentions(
        gsap_corpus, analysis_file, filter_predicted=False
    )
    assert len(filtered.mentions_predicted) == len(gsap_corpus.mentions_predicted)
    assert stats["predicted_mentions_filtered"] == 0


def test_filter_gold(gsap_corpus, analysis_file):
    filtered, stats = filter_gsap_mentions(
        gsap_corpus, analysis_file, filter_gold=True, filter_predicted=False
    )
    # g1 is "BERT" which is NOT in the analysis texts, so gold unchanged
    assert len(filtered.mentions) == 1
    assert stats["gold_mentions_filtered"] == 0


def test_filter_stats_keys(gsap_corpus, analysis_file):
    _, stats = filter_gsap_mentions(gsap_corpus, analysis_file)
    assert "total_texts_to_filter" in stats
    assert "min_count_threshold" in stats
    assert "filtered_texts" in stats
    assert stats["min_count_threshold"] == 2
    assert stats["total_texts_to_filter"] == 2  # "the model" and "models"


# ---------- generate_correction_report ----------


def test_generate_correction_report_writes_file(gsap_corpus, analysis_file, tmp_path):
    filtered, stats = filter_gsap_mentions(gsap_corpus, analysis_file)
    output_path = tmp_path / "report.md"
    generate_correction_report(gsap_corpus, filtered, stats, output_path)
    assert output_path.exists()
    content = output_path.read_text()
    assert "GSAP Correction Report" in content
    assert "Filtered" in content
