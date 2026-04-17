"""Count relation signatures across all datasets, models, and splits.

Produces:
  data/relation_signatures.json  — one row per (dataset, model, split, label_set, signature)
  data/semantic_groups.json      — group definitions derived from semantic_groups.yaml

Columns in relation_signatures.json:
  dataset, model, split, label_set,
  subject_type, relation_type, object_type, count,
  entity_group_subj, entity_group_obj, relation_group

- dataset  : test data source ("gsap-ere", "scier", "scinlp")
- model    : "gold" for annotated data, or the trained_on dataset for predictions
- split    : "train", "dev", "test"
- label_set: "original" (original labels) or "unified" (after unification pipeline)
- *_group  : semantic group from semantic_groups.yaml ("Other" if unmapped)

Usage:
    uv run python scripts/ere_quality/relation_signatures.py
"""

import json
from collections import Counter
from pathlib import Path

import yaml

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import project_root
from unifiedsciere.types import Relation
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[str] = ["gsap-ere", "scier", "scinlp"]
SPLITS: list[str] = ["train", "dev", "test"]

_GROUPS_YAML = (
    Path(__file__).resolve().parents[2]
    / "src" / "unifiedsciere" / "unification" / "semantic_groups.yaml"
)


# ── semantic group helpers ────────────────────────────────────────────────────

def load_groups() -> dict:
    with open(_GROUPS_YAML) as fh:
        return yaml.safe_load(fh)


def build_reverse_maps(groups: dict) -> tuple[dict, dict]:
    """Return (entity_map, relation_map): label → group name."""
    entity_map: dict[str, str] = {}
    for gname, gdata in groups.get("entity_groups", {}).items():
        for member in gdata.get("members", []):
            entity_map[member] = gname

    relation_map: dict[str, str] = {}
    for gname, gdata in groups.get("relation_groups", {}).items():
        for member in gdata.get("members", []):
            relation_map[member] = gname

    return entity_map, relation_map


# ── counting helpers ──────────────────────────────────────────────────────────

def _count_signatures(relations: list[Relation]) -> Counter:
    c: Counter = Counter()
    for rel in relations:
        c[(rel.subject.label, rel.label, rel.object.label)] += 1
    return c


def _rows_from_counter(
    counter: Counter,
    dataset: str,
    model: str,
    split: str,
    label_set: str,
    entity_map: dict,
    relation_map: dict,
) -> list[dict]:
    return [
        {
            "dataset":           dataset,
            "model":             model,
            "split":             split,
            "label_set":         label_set,
            "subject_type":      subj,
            "relation_type":     rel,
            "object_type":       obj,
            "count":             cnt,
            "entity_group_subj": entity_map.get(subj, "Other"),
            "entity_group_obj":  entity_map.get(obj,  "Other"),
            "relation_group":    relation_map.get(rel, "Other"),
        }
        for (subj, rel, obj), cnt in sorted(counter.items())
    ]


# ── data collection ───────────────────────────────────────────────────────────

def collect_gold(rows: list[dict], entity_map: dict, relation_map: dict) -> None:
    for dataset in DATASETS:
        for split in SPLITS:
            print(f"  gold  {dataset:12s} {split}")
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
            except Exception as e:
                print(f"    SKIP (gold load): {e}")
                continue

            rows.extend(_rows_from_counter(
                _count_signatures(corpus.relation),
                dataset, "gold", split, "original", entity_map, relation_map,
            ))

            try:
                unified, _ = apply_unification_pipeline(
                    corpus, dataset, apply_to_gold=True, apply_to_predicted=False
                )
                rows.extend(_rows_from_counter(
                    _count_signatures(unified.relation),
                    dataset, "gold", split, "unified", entity_map, relation_map,
                ))
            except Exception as e:
                print(f"    SKIP (gold unify): {e}")


def collect_predictions(rows: list[dict], entity_map: dict, relation_map: dict) -> None:
    for trained_on in DATASETS:
        for dataset in DATASETS:
            for split in SPLITS:
                print(f"  pred  {trained_on:12s} → {dataset:12s} {split}")
                try:
                    corpus = load_corpus(
                        dataset, split, data_type="predictions", trained_on=trained_on
                    )
                except FileNotFoundError:
                    print(f"    SKIP (file not found)")
                    continue
                except Exception as e:
                    print(f"    SKIP (pred load): {e}")
                    continue

                rows.extend(_rows_from_counter(
                    _count_signatures(corpus.relations_predicted),
                    dataset, trained_on, split, "original", entity_map, relation_map,
                ))

                try:
                    unified, _ = apply_unification_pipeline(
                        corpus, trained_on,
                        apply_to_gold=False, apply_to_predicted=True,
                    )
                    rows.extend(_rows_from_counter(
                        _count_signatures(unified.relations_predicted),
                        dataset, trained_on, split, "unified", entity_map, relation_map,
                    ))
                except Exception as e:
                    print(f"    SKIP (pred unify): {e}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    groups = load_groups()
    entity_map, relation_map = build_reverse_maps(groups)

    rows: list[dict] = []

    print("Collecting gold signatures …")
    collect_gold(rows, entity_map, relation_map)

    print("\nCollecting prediction signatures …")
    collect_predictions(rows, entity_map, relation_map)

    root = project_root()

    # Write signature rows
    sig_path = root / "data" / "relation_signatures.json"
    sig_path.parent.mkdir(parents=True, exist_ok=True)
    sig_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"\nWrote {len(rows):,} rows → {sig_path}")

    # Write semantic groups (frontend-ready, stripped of YAML comments)
    grp_path = root / "data" / "semantic_groups.json"
    grp_path.write_text(json.dumps(groups, ensure_ascii=False, indent=2))
    print(f"Wrote groups  → {grp_path}")

    from collections import Counter as C
    by_ds = C(r["dataset"] for r in rows)
    print("\nRows per dataset:")
    for ds, n in sorted(by_ds.items()):
        print(f"  {ds:14s} {n:6,}")


if __name__ == "__main__":
    main()
