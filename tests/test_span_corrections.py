"""Tests for unifiedsciere.unification.span_corrections."""

from conftest import make_corpus, make_mention, make_relation

from unifiedsciere.unification.span_corrections import (
    _apply_rules_to_mention,
    normalize_spans,
)

# ---------- _apply_rules_to_mention ----------


def test_apply_prefix_strip():
    m = make_mention(text="the BERT", begin=0, end=8, begin_token=0, end_token=2)
    rules = [("prefix", r"^(?:the|The)$")]
    new_m, applied = _apply_rules_to_mention(m, rules)
    assert new_m.text == "BERT"
    assert new_m.begin == 4  # 0 + len("the") + 1
    assert new_m.begin_token == 1
    assert applied == ["prefix:the"]


def test_apply_suffix_strip():
    m = make_mention(text="BERT model", begin=0, end=10, begin_token=0, end_token=2)
    rules = [("suffix", r"^(?:models?|layers?)$")]
    new_m, applied = _apply_rules_to_mention(m, rules)
    assert new_m.text == "BERT"
    assert new_m.end == 4  # 10 - len("model") - 1
    assert new_m.end_token == 1
    assert applied == ["suffix:model"]


def test_apply_suffix_multi_strip():
    m = make_mention(text="SQuAD test set", begin=0, end=14, begin_token=0, end_token=3)
    rules = [("suffix_multi", r"^(?:test set|data set)$")]
    new_m, applied = _apply_rules_to_mention(m, rules)
    assert new_m.text == "SQuAD"
    assert new_m.end_token == 1
    assert applied == ["suffix_multi:test set"]


def test_apply_no_match():
    m = make_mention(text="BERT", begin=0, end=4, begin_token=0, end_token=1)
    rules = [("prefix", r"^(?:the|The)$")]
    new_m, applied = _apply_rules_to_mention(m, rules)
    assert new_m.text == "BERT"
    assert applied == []
    # Should return the original mention object
    assert new_m is m


def test_apply_wont_strip_single_token():
    """Should not strip if it would leave the mention empty."""
    m = make_mention(text="the", begin=0, end=3, begin_token=0, end_token=1)
    rules = [("prefix", r"^(?:the|The)$")]
    new_m, applied = _apply_rules_to_mention(m, rules)
    assert new_m.text == "the"
    assert applied == []


def test_apply_multiple_rules_sequential():
    m = make_mention(text="the BERT model", begin=0, end=14, begin_token=0, end_token=3)
    rules = [
        ("prefix", r"^(?:the|The)$"),
        ("suffix", r"^(?:models?)$"),
    ]
    new_m, applied = _apply_rules_to_mention(m, rules)
    assert new_m.text == "BERT"
    assert len(applied) == 2
    assert "prefix:the" in applied
    assert "suffix:model" in applied


def test_apply_offsets_correct():
    """Verify character and token offsets after prefix + suffix strip."""
    m = make_mention(
        text="the BERT model", begin=10, end=24, begin_token=3, end_token=6
    )
    rules = [
        ("prefix", r"^(?:the)$"),
        ("suffix", r"^(?:model)$"),
    ]
    new_m, _ = _apply_rules_to_mention(m, rules)
    assert new_m.text == "BERT"
    assert new_m.begin == 14  # 10 + len("the") + 1
    assert new_m.end == 18  # 24 - len("model") - 1
    assert new_m.begin_token == 4
    assert new_m.end_token == 5


# ---------- normalize_spans ----------


def test_normalize_predicted_by_default():
    """With normalize_predicted=True (default), predicted mentions should be normalized."""
    p1 = make_mention(
        id="p1",
        text="the BERT model",
        label="Method",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
        annotator="gsap",
    )
    corpus = make_corpus(mentions_predicted=[p1])

    result, stats = normalize_spans(corpus, dataset="gsap", normalize_predicted=True)
    # GSAP Method rules strip "the" prefix and "model" suffix
    assert result.mentions_predicted[0].text == "BERT"
    assert stats["predicted_corrections"] == 1


def test_normalize_skips_gold_by_default():
    g1 = make_mention(
        id="g1",
        text="the BERT model",
        label="Method",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
    )
    corpus = make_corpus(mentions=[g1])

    result, stats = normalize_spans(corpus, dataset="gsap", normalize_gold=False)
    assert result.mentions[0].text == "the BERT model"
    assert stats["gold_corrections"] == 0


def test_normalize_unknown_dataset():
    """Unknown dataset should produce no corrections."""
    p1 = make_mention(
        id="p1",
        text="the BERT model",
        label="Method",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
    )
    corpus = make_corpus(mentions_predicted=[p1])

    result, stats = normalize_spans(corpus, dataset="unknown")
    assert result.mentions_predicted[0].text == "the BERT model"
    assert stats["predicted_corrections"] == 0


def test_normalize_stats_populated():
    p1 = make_mention(
        id="p1",
        text="the BERT model",
        label="Method",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
        annotator="gsap",
    )
    corpus = make_corpus(mentions_predicted=[p1])

    _, stats = normalize_spans(corpus, dataset="gsap")
    assert "corrections_by_rule" in stats
    assert "corrections_by_label" in stats
    assert "examples" in stats
    assert stats["corrections_by_label"].get("Method", 0) > 0


def test_normalize_relations_remapped():
    """Relations should reference the new normalized mention objects."""
    p1 = make_mention(
        id="p1",
        text="the BERT model",
        label="Method",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
    )
    p2 = make_mention(
        id="p2",
        text="GLUE",
        label="Dataset",
        begin=20,
        end=24,
        begin_token=5,
        end_token=6,
    )
    pr = make_relation(p1, p2)
    corpus = make_corpus(mentions_predicted=[p1, p2], relations_predicted=[pr])

    result, _ = normalize_spans(corpus, dataset="gsap")
    # p1 should have been normalized; relation's subject should point to the normalized mention
    assert result.relations_predicted[0].subject.text == "BERT"


def test_normalize_possessive_suffix():
    """GSAP _all rule strips 's suffix when it's a separate token."""
    p1 = make_mention(
        id="p1",
        text="BERT 's",
        label="Method",
        begin=0,
        end=7,
        begin_token=0,
        end_token=2,
    )
    corpus = make_corpus(mentions_predicted=[p1])

    result, stats = normalize_spans(corpus, dataset="gsap")
    assert result.mentions_predicted[0].text == "BERT"
    assert stats["predicted_corrections"] == 1
