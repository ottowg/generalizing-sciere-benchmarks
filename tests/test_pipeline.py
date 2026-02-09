"""Tests for unifiedsciere.unification.pipeline."""

from pathlib import Path

import pytest
import yaml
from conftest import make_corpus, make_mention, make_relation

from unifiedsciere.unification.pipeline import (
    apply_unification_pipeline,
    generate_pipeline_report,
    load_unification_config,
)

# ---------- Fixtures ----------


@pytest.fixture
def config_file(tmp_path):
    """Minimal unification config YAML."""
    config = {
        "merge_stacked": {"enabled": True, "prefer_larger": True},
        "drop_unmapped": {"enabled": False},
        "map_labels": {"enabled": False},
        "dataset_corrections": {
            "gsap": {"enabled": False},
            "scier": {"enabled": False},
            "scinlp": {"enabled": False},
        },
        "span_normalization": {"enabled": False},
    }
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump(config))
    return p


@pytest.fixture
def all_enabled_config(tmp_path):
    """Config with merge + drop + map + span enabled (no GSAP corrections)."""
    config = {
        "merge_stacked": {"enabled": True, "prefer_larger": True},
        "drop_unmapped": {"enabled": True},
        "map_labels": {"enabled": True},
        "dataset_corrections": {
            "gsap": {"enabled": False},
            "scier": {"enabled": False},
            "scinlp": {"enabled": False},
        },
        "span_normalization": {"enabled": True},
    }
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump(config))
    return p


@pytest.fixture
def scier_corpus():
    """Corpus with SciERC-style labels (Dataset, Method, Task)."""
    g1 = make_mention(
        id="g1", text="BERT", label="Method", begin=0, end=4, begin_token=0, end_token=1
    )
    g2 = make_mention(
        id="g2",
        text="SQuAD",
        label="Dataset",
        begin=10,
        end=15,
        begin_token=2,
        end_token=3,
    )
    r1 = make_relation(g1, g2, label="Used-for")

    p1 = make_mention(
        id="p1",
        text="BERT",
        label="Method",
        begin=0,
        end=4,
        begin_token=0,
        end_token=1,
        annotator="scier",
    )
    p2 = make_mention(
        id="p2",
        text="SQuAD",
        label="Dataset",
        begin=10,
        end=15,
        begin_token=2,
        end_token=3,
        annotator="scier",
    )
    pr1 = make_relation(p1, p2, label="Used-for", annotator="scier")

    return make_corpus(
        mentions=[g1, g2],
        relations=[r1],
        mentions_predicted=[p1, p2],
        relations_predicted=[pr1],
    )


# ---------- load_unification_config ----------


def test_load_config_from_path(config_file):
    config = load_unification_config(config_file)
    assert config["merge_stacked"]["enabled"] is True
    assert config["drop_unmapped"]["enabled"] is False


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_unification_config(Path("/nonexistent/config.yaml"))


# ---------- apply_unification_pipeline ----------


def test_pipeline_merge_only(config_file, sample_corpus):
    """With only merge enabled, other steps are skipped."""
    config = load_unification_config(config_file)
    result, stats = apply_unification_pipeline(sample_corpus, "scier", config=config)
    # Merge should have run
    assert stats["merge"] != {}
    # Drop/map/span should be empty
    assert stats["drop"] == {}
    assert stats["map"] == {}
    assert stats["span_normalization"] == {}


def test_pipeline_all_steps(all_enabled_config, scier_corpus):
    """With merge + drop + map + span enabled for scier."""
    config = load_unification_config(all_enabled_config)
    result, stats = apply_unification_pipeline(scier_corpus, "scier", config=config)
    assert stats["merge"] != {}
    assert stats["drop"] != {}
    assert stats["map"] != {}
    # scier has span rules for Dataset suffix
    assert "span_normalization" in stats


def test_pipeline_stats_has_all_keys(config_file, sample_corpus):
    config = load_unification_config(config_file)
    _, stats = apply_unification_pipeline(sample_corpus, "scier", config=config)
    expected = ["merge", "drop", "map", "dataset_corrections", "span_normalization"]
    for key in expected:
        assert key in stats


def test_pipeline_gsap_corrections_skipped_no_file(tmp_path, sample_corpus):
    """GSAP corrections enabled but analysis file doesn't exist → skipped gracefully."""
    config = {
        "merge_stacked": {"enabled": False},
        "drop_unmapped": {"enabled": False},
        "map_labels": {"enabled": False},
        "dataset_corrections": {
            "gsap": {
                "enabled": True,
                "mlmodelgeneric_analysis_file": str(tmp_path / "nonexistent.json"),
                "min_count": 2,
            },
        },
        "span_normalization": {"enabled": False},
    }
    # Should not raise, just print a warning and skip
    result, stats = apply_unification_pipeline(sample_corpus, "gsap", config=config)
    assert "gsap" not in stats["dataset_corrections"]


# ---------- generate_pipeline_report ----------


def test_generate_report_writes_file(tmp_path):
    stats = {
        "merge": {"predicted_merged": 5, "gold_merged": 2},
        "drop": {
            "predicted_mentions_dropped": 3,
            "gold_mentions_dropped": 1,
            "dropped_labels": ["Junk"],
        },
        "map": {"predicted_mentions_mapped": 10, "gold_mentions_mapped": 5},
        "dataset_corrections": {},
        "span_normalization": {
            "predicted_corrections": 2,
            "gold_corrections": 0,
            "corrections_by_rule": {},
            "examples": [],
        },
    }
    output = tmp_path / "report.md"
    generate_pipeline_report(stats, output)
    assert output.exists()
    content = output.read_text()
    assert "Unification Pipeline Report" in content


def test_generate_report_empty_stats(tmp_path):
    stats = {
        "merge": {},
        "drop": {},
        "map": {},
        "dataset_corrections": {},
        "span_normalization": {},
    }
    output = tmp_path / "report.md"
    generate_pipeline_report(stats, output)
    assert output.exists()
