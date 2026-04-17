"""Build allowed-signature sets from gold annotations.

Produces:
  data/allowed_signatures.yaml

Structure (one block per label set):
  <dataset>:
    allowed:
      <subject_type>:
        <relation_type>:
          <object_type>:
    wrong_direction:
      <subject_type>:       # reversed triples that are NOT in the allowed set
        <relation_type>:
          <object_type>:
    not_allowed:            # null — fill in manually to mark impossible combinations
      <subject_type>:
        <relation_type>:
          <object_type>:

Label sets:
  gsap-ere  — raw GSAP-ERE label space
  scier     — raw SciER label space
  scinlp    — raw SciNLP label space
  unified   — unified label space (all datasets merged)

Usage:
    uv run python scripts/ere_quality/allowed_signatures.py

Derived from data/relation_signatures.json (gold rows only).
Run scripts/ere_quality/relation_signatures.py first if that file is missing.
"""

import json
from collections import defaultdict
from pathlib import Path

import yaml

from unifiedsciere.paths import project_root

DATASETS   = ["gsap-ere", "scier", "scinlp"]
SIG_FILE   = "data/relation_signatures.json"
OUT_FILE   = "data/allowed_signatures.yaml"
OLD_JSON   = "data/allowed_signatures.json"


# ── YAML helpers ──────────────────────────────────────────────────────────────

class _NullRepr(yaml.Dumper):
    """Render None as bare empty value (key:) instead of 'null'."""
    pass


def _represent_none(dumper, _):
    return dumper.represent_scalar("tag:yaml.org,2002:null", "")


_NullRepr.add_representer(type(None), _represent_none)


# ── Signature helpers ─────────────────────────────────────────────────────────

def _to_nested(triples: set[tuple[str, str, str]]) -> dict | None:
    """(s, r, o) set → {s: {r: {o: None}}} nested mapping, or None if empty."""
    if not triples:
        return None
    d: dict = {}
    for s, r, o in sorted(triples):
        d.setdefault(s, {}).setdefault(r, {})[o] = None
    return d


def _wrong_direction(allowed: set[tuple[str, str, str]]) -> set[tuple[str, str, str]]:
    """Reverse triples (B, rel, A) for each (A, rel, B) in allowed that are
    not themselves in allowed and are not self-relations (A != B)."""
    return {
        (o, rel, s)
        for (s, rel, o) in allowed
        if s != o and (o, rel, s) not in allowed
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    root     = project_root()
    sig_path = root / SIG_FILE

    if not sig_path.exists():
        raise FileNotFoundError(
            f"{SIG_FILE} not found. "
            "Run scripts/ere_quality/relation_signatures.py first."
        )

    rows = json.loads(sig_path.read_text())

    # Collect raw allowed sets per key
    raw_allowed: dict[str, set[tuple[str, str, str]]] = defaultdict(set)

    for r in rows:
        if r["model"] != "gold":
            continue
        triple = (r["subject_type"], r["relation_type"], r["object_type"])
        if r["label_set"] == "original":
            raw_allowed[r["dataset"]].add(triple)
        elif r["label_set"] == "unified":
            raw_allowed["unified"].add(triple)

    # Build output document
    doc: dict = {}
    keys = DATASETS + ["unified"]
    for key in keys:
        allowed = raw_allowed.get(key, set())
        doc[key] = {
            "allowed":         _to_nested(allowed),
            "wrong_direction": _to_nested(_wrong_direction(allowed)),
            "not_allowed":     None,
        }

    out_path = root / OUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Allowed relation signatures derived from gold annotations.\n"
        "# allowed:         confirmed valid (subj, rel, obj) triples from gold\n"
        "# wrong_direction: reversed triples whose direction is flipped vs gold\n"
        "# not_allowed:     explicitly forbidden triples (fill in manually)\n\n"
    )
    out_path.write_text(
        header + yaml.dump(doc, Dumper=_NullRepr, allow_unicode=True,
                           default_flow_style=False, sort_keys=False)
    )
    print(f"Wrote {out_path}")

    # Remove stale JSON if present
    old_json = root / OLD_JSON
    if old_json.exists():
        old_json.unlink()
        print(f"Removed stale {OLD_JSON}")

    print()
    for key in keys:
        allowed   = raw_allowed.get(key, set())
        wrong_dir = _wrong_direction(allowed)
        print(f"  {key:12s}  {len(allowed):4d} allowed  {len(wrong_dir):4d} wrong_direction")


if __name__ == "__main__":
    main()
