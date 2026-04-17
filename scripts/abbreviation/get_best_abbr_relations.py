import json
from collections import defaultdict
from dataclasses import dataclass

from numpy.lib import scimath
from pandas.core.arrays.sparse.array import doc

from unifiedsciere.abbreviates_relation.annotations import (
    load_annotations,
)
from unifiedsciere.abbreviates_relation.queue import get_entries, get_pool_entries
from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import project_root
from unifiedsciere.types import Corpus


@dataclass
class CorpusEntry:
    """One corpus with its origin metadata."""

    corpus: Corpus
    dataset: str
    split: str


ALL_DATASETS = ["gsap-ere", "scier", "scinlp"]
ALL_SPLITS = ["train", "dev", "test", "test_ood"]

ANNOTATIONS_PATH = project_root() / "data" / "abbreviation" / "annotations.jsonl"
QUEUE_PATH = project_root() / "data" / "abbreviation" / "al_queue.json"
TEST_SET_PATH = project_root() / "data" / "abbreviation" / "test_set.json"
HISTORY_PATH = project_root() / "data" / "abbreviation" / "eval_history.json"

ABBR_LABEL = ["no abbreviation", "abbreviates", "inverted"]


def load_subtask_a():
    human_labels = load_annotations(ANNOTATIONS_PATH)

    corpora: list[CorpusEntry] = []
    for dataset in ALL_DATASETS:
        for split in ALL_SPLITS:
            print(f"  Loading {dataset}/{split} … ", end="", flush=True)
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
                corpora.append(CorpusEntry(corpus=corpus, dataset=dataset, split=split))
                print("ok")
            except Exception as e:
                print(f"skip ({e})")
    # Recalculate the predictions in 3 fold setup
    #  => Dictionary of
    # for each corpus get the relations and look into manual annotations
    # = to_predict are the relation left to predict

    log = lambda x: print(f"log: {x}")
    entries_a, entries_b = get_entries(corpora, log)

    if log:
        log("— Subtask A —")
    pool_entries_a, pool_prob_a, summary_a, clf_a = get_pool_entries(
        entries_a, "A", human_labels, set(), extra_entries=entries_b, log=log
    )
    pool_entries_b, pool_prob_b, summary_b, clf_b = get_pool_entries(
        entries_b, "B", human_labels, set(), extra_entries=entries_a, log=log
    )
    # get pool predictions
    pool_preds_a = {}
    for p_entry, p_prob in zip(pool_entries_a, pool_prob_a):
        pool_preds_a[p_entry["cid"]] = int(p_prob > 0.5), p_prob
    pool_preds_b = {}
    for p_entry, p_prob in zip(pool_entries_b, pool_prob_b):
        pool_preds_b[p_entry["cid"]] = int(p_prob > 0.5), p_prob
    assert len(set(human_labels) & set(pool_preds_a)) == 0
    assert len(set(human_labels) & set(pool_preds_b)) == 0

    human_labels = {k: (h, 1.0) for k, h in human_labels.items()}
    all_preds_a = human_labels | pool_preds_a
    all_preds_b = human_labels | pool_preds_b
    rels_a = [
        dict(
            # cand=e,
            rel=e["cand"].relation,
            split=e["cand"].relation.split,
            text=f"{e['cand'].relation.subject.text} -->  {e['cand'].relation.object.text}",
            pred=all_preds_a[e["cid"]][0],
            score=all_preds_a[e["cid"]][1],
            is_manual=e["cid"] in human_labels,
        )
        for e in entries_a
    ]

    rels_b = [
        dict(
            rel=e["cand"].mention,
            split=f"{e['cand'].mention.split}",
            pred=all_preds_b[e["cid"]][0],
            score=all_preds_b[e["cid"]][1],
            text=e["cand"].mention.text,
            is_manual=e["cid"] in human_labels,
        )
        for e in entries_b
    ]
    # save new test_set
    import pandas as pd

    rels_df = pd.DataFrame(rels_a)
    f = rels_df.split.str.startswith("gsap-ere")
    f &= rels_df.pred == 1
    print(rels_df[f].sample(min(len(rels_df[f]), 50)))
    print(
        rels_df.groupby("split")
        .pred.value_counts()  # [["manual", "pred"]]
        .unstack()
        # .unstack()
    )
    rels_to_replace = persist_changes_a([r["rel"] for r in rels_a if r["pred"] == 1])
    ents_to_split = [e["rel"] for e in rels_b if e["pred"] == 1]
    print(len(ents_to_split))
    ents_to_split = persist_changes_b(ents_to_split)
    with open("data/abbreviation/changes.json", "w") as f:
        json.dump(
            dict(
                rels_to_replace=rels_to_replace,
                ents_to_split=ents_to_split,
            ),
            f,
            indent=2,
        )


def persist_changes_a(rels):
    to_replace = defaultdict(list)
    for rel in rels:
        docs = rel.dataset
        # new relation
        short, long = rel.subject, rel.object
        if short.text > long.text:
            short, long = long, short
        doc_id = short.id.split(" ")[0]
        new_rel_key = [
            short.begin_token,
            short.end_token,
            long.begin_token,
            long.end_token,
            "abbreviates",
        ]
        old_rel_key = [
            rel.subject.begin_token,
            rel.subject.end_token,
            rel.object.begin_token,
            rel.object.end_token,
            rel.label,
        ]
        to_replace[doc_id].append([old_rel_key, new_rel_key])
    return to_replace


def persist_changes_b(ents):
    entities_to_split = defaultdict(list)
    for ent in ents:
        doc_id = ent.id.split(" ")[0]
        new_ent_key = [ent.begin_token, ent.end_token, ent.label]
        entities_to_split[doc_id].append(new_ent_key)
    return entities_to_split


if __name__ == "__main__":
    load_subtask_a()
