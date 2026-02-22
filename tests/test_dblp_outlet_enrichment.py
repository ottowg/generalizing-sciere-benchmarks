from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "metadata"
    / "unified"
    / "all_papers.jsonl"
)
OUTLETS_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "metadata" / "outlet_info.json"
)
DBLP_PREFIXES = {
    "conf/aaai",
    "conf/acl",
    "conf/cvpr",
    "conf/dicta",
    "conf/emnlp",
    "conf/fgr",
    "conf/iccv",
    "conf/iclr",
    "conf/icra",
    "conf/vehits",
    "conf/wacv",
    "journals/ijcv",
    "journals/mta",
    "journals/pami",
    "journals/pr",
    "journals/tgrs",
    "journals/tip",
}


def _dblp_prefix(dblp_id: str) -> str | None:
    parts = dblp_id.split("/")
    if len(parts) < 2:
        return None
    return "/".join(parts[:2])


def test_dblp_prefixes_are_enriched():
    assert DATA_PATH.exists(), f"Missing unified metadata file: {DATA_PATH}"

    totals = defaultdict(int)
    missing = defaultdict(int)

    with DATA_PATH.open() as f:
        for line in f:
            d = json.loads(line)
            dblp_id = d.get("dblp_id", "")
            if not dblp_id:
                continue
            prefix = _dblp_prefix(dblp_id)
            if prefix not in DBLP_PREFIXES:
                continue
            totals[prefix] += 1
            if not d.get("outlet_id", ""):
                missing[prefix] += 1

    # Ensure the prefixes exist in the data and all are enriched.
    not_found = sorted(p for p in DBLP_PREFIXES if totals[p] == 0)
    assert not_found == [], f"No papers found for prefixes: {not_found}"

    not_enriched = sorted(p for p in DBLP_PREFIXES if missing[p] > 0)
    assert not_enriched == [], (
        "Some papers with these dblp_id prefixes are missing outlet_id: "
        f"{not_enriched}"
    )


def test_additional_dblp_prefixes_are_enriched():
    prefixes = {
        "conf/aaai",
        "conf/acl",
        "conf/cvpr",
        "conf/dagm",
        "conf/dicta",
        "conf/emnlp",
        "conf/fgr",
        "conf/iccv",
        "conf/iclr",
        "conf/icra",
        "conf/vehits",
        "conf/wacv",
        "journals/access",
        "journals/cogcom",
        "journals/eswa",
        "journals/ijcv",
        "journals/mta",
        "journals/pami",
        "journals/pr",
        "journals/tgrs",
        "journals/tip",
    }

    assert DATA_PATH.exists(), f"Missing unified metadata file: {DATA_PATH}"

    totals = defaultdict(int)
    missing = defaultdict(int)

    with DATA_PATH.open() as f:
        for line in f:
            d = json.loads(line)
            dblp_id = d.get("dblp_id", "")
            if not dblp_id:
                continue
            prefix = _dblp_prefix(dblp_id)
            if prefix not in prefixes:
                continue
            totals[prefix] += 1
            if not d.get("outlet_id", ""):
                missing[prefix] += 1

    not_found = sorted(p for p in prefixes if totals[p] == 0)
    assert not_found == [], f"No papers found for prefixes: {not_found}"

    not_enriched = sorted(p for p in prefixes if missing[p] > 0)
    assert not_enriched == [], (
        "Some papers with these dblp_id prefixes are missing outlet_id: "
        f"{not_enriched}"
    )


def test_scier_aaai_examples_are_not_arxiv():
    target_ids = {"209862890", "202565512"}
    assert DATA_PATH.exists(), f"Missing unified metadata file: {DATA_PATH}"
    assert OUTLETS_PATH.exists(), f"Missing outlet info file: {OUTLETS_PATH}"

    outlet_aaai_id = None
    with OUTLETS_PATH.open() as f:
        outlets = json.loads(f.read())
    for item in outlets:
        if item.get("dblp_outlet_id") == "conf/aaai":
            outlet_aaai_id = item.get("id")
            break

    assert outlet_aaai_id, "AAAI outlet not found in outlet_info.json"

    found = {}
    with DATA_PATH.open() as f:
        for line in f:
            d = json.loads(line)
            if d.get("dataset") != "scier":
                continue
            if str(d.get("s2_corpus_id")) in target_ids:
                found[str(d.get("s2_corpus_id"))] = d

    missing = sorted(t for t in target_ids if t not in found)
    assert missing == [], f"Missing scier papers: {missing}"

    for paper_id, d in found.items():
        assert d.get("outlet_id") == outlet_aaai_id, (
            f"Paper {paper_id} expected AAAI outlet ({outlet_aaai_id}), "
            f"got {d.get('outlet_id')}"
        )
