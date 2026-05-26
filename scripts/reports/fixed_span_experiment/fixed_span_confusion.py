"""Fixed-span NER + RE confusion matrix analysis.

In the fixed-span experiment, gold entity spans are given to the model — it only
predicts the *label* for each span (NER) and the relations between them (RE).
This script compares gold vs predicted labels for both tasks.

One report file is produced per (model, dataset, split) combination.

Usage:
    uv run python scripts/reports/fixed_span_experiment/fixed_span_confusion.py
"""

from collections import Counter, defaultdict

import numpy as np
import pandas as pd

from unifiedsciere.data_loader import _load_docs
from unifiedsciere.paths import project_root, reports_dir
from unifiedsciere.reporting import MarkdownReport

FIXED_SPANS_DIR = project_root() / "data" / "predictions_fixed_spans"
OUTPUT_DIR = reports_dir("fixed_span_analysis")
N_EXAMPLES = 5


# ---------------------------------------------------------------------------
# NER
# ---------------------------------------------------------------------------

def _build_ner_confusion(docs: list[dict]) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    dict[tuple[str, str], list[str]],
]:
    """Build NER confusion matrices and collect mention text examples.

    Returns:
        count_cm  – count confusion matrix (rows=gold, cols=predicted)
        prob_cm   – mean prob1/prob2 confusion matrix (strings)
        examples  – (gold_label, pred_label) → list of mention texts
    """
    counts: dict[tuple[str, str], int] = defaultdict(int)
    probs: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)

    for doc in docs:
        gold_sents = doc.get("ner", [])
        pred_sents = doc.get("predicted_ner", [])
        proba_sents = doc.get("predicted_ner_proba", [])
        tokens = [tok for sent in doc.get("sentences", []) for tok in sent]

        for sent_idx, (gold_spans, pred_spans) in enumerate(zip(gold_sents, pred_sents)):
            pred_by_span = {(b, e): label for b, e, label in pred_spans}

            proba_by_span: dict[tuple[int, int], tuple[float, float]] = {}
            if sent_idx < len(proba_sents):
                for entry in proba_sents[sent_idx]:
                    b, e = entry[0], entry[1]
                    p1 = float(entry[3]) if len(entry) > 3 else float("nan")
                    p2 = float(entry[4]) if len(entry) > 4 else float("nan")
                    proba_by_span[(b, e)] = (p1, p2)

            for begin, end, gold_label in gold_spans:
                pred_label = pred_by_span.get((begin, end), "MISSING")
                counts[(gold_label, pred_label)] += 1
                examples[(gold_label, pred_label)].append(
                    " ".join(tokens[begin : end + 1])
                )
                if (begin, end) in proba_by_span:
                    probs[(gold_label, pred_label)].append(proba_by_span[(begin, end)])

    gold_labels = sorted({k[0] for k in counts})
    pred_labels = sorted({k[1] for k in counts})

    count_df = pd.DataFrame(0, index=gold_labels, columns=pred_labels)
    for (g, p), n in counts.items():
        count_df.at[g, p] = n

    prob_df = pd.DataFrame("—", index=gold_labels, columns=pred_labels)
    for (g, p), vals in probs.items():
        if not vals:
            continue
        arr = np.array(vals)
        m1 = np.nanmean(arr[:, 0])
        m2 = np.nanmean(arr[:, 1])
        prob_df.at[g, p] = f"{m1:.3f} / {m2:.3f}"

    return count_df, prob_df, dict(examples)


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------

SYMMETRIC_RELATIONS = {"coreference", "Synonym-Of", "isComparedTo", "Compare-With"}


def _normalize_rel(
    sb: int, se: int, ob: int, oe: int, lbl: str
) -> tuple[int, int, int, int]:
    """For symmetric relations swap subject/object so the left-most span comes first."""
    if lbl in SYMMETRIC_RELATIONS and sb > ob:
        return ob, oe, sb, se
    return sb, se, ob, oe


def _build_rel_confusion(docs: list[dict]) -> tuple[
    pd.DataFrame,
    dict[tuple[str, str], list[str]],
] | None:
    """Build relation confusion matrix and collect relation text examples.

    Matches gold and predicted relations by (sub_begin, sub_end, obj_begin, obj_end).
    Unmatched gold → NIL predicted; unmatched predicted → NIL gold.

    Returns None if no predicted relations exist in the docs.
    """
    counts: dict[tuple[str, str], int] = defaultdict(int)
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)

    any_pred = False

    for doc in docs:
        gold_sents = doc.get("relations", [])
        pred_sents = doc.get("predicted_rel_proba", [])
        tokens = [tok for sent in doc.get("sentences", []) for tok in sent]

        def span_text(b: int, e: int) -> str:
            return " ".join(tokens[b : e + 1])

        # Flatten across sentences — indices are doc-level.
        # Normalize symmetric gold relations to left-to-right (lower begin first).
        # For matching, we also check the reversed span for symmetric gold (see below).
        gold_rels: list[tuple[int, int, int, int, str]] = [
            (*_normalize_rel(sb, se, ob, oe, lbl), lbl)
            for sent in gold_sents
            for sb, se, ob, oe, lbl in sent
        ]
        pred_rels: list[tuple[int, int, int, int, str]] = [
            (sb, se, ob, oe, lbl)
            for sent in pred_sents
            for sb, se, ob, oe, lbl, *_ in sent
        ]

        if pred_rels:
            any_pred = True

        pred_by_span: dict[tuple[int, int, int, int], str] = {
            (sb, se, ob, oe): lbl for sb, se, ob, oe, lbl in pred_rels
        }
        matched_pred_spans: set[tuple[int, int, int, int]] = set()

        for sb, se, ob, oe, gold_lbl in gold_rels:
            key = (sb, se, ob, oe)
            rev_key = (ob, oe, sb, se)
            # For symmetric gold relations also check the reversed span direction
            # in case the model predicted the same pair in the opposite order.
            if key in pred_by_span:
                matched_key = key
            elif gold_lbl in SYMMETRIC_RELATIONS and rev_key in pred_by_span:
                matched_key = rev_key
            else:
                matched_key = None

            if matched_key is not None:
                pred_lbl = pred_by_span[matched_key]
                matched_pred_spans.add(matched_key)
            else:
                pred_lbl = "NIL"

            counts[(gold_lbl, pred_lbl)] += 1
            ex = f"{span_text(sb, se)} → {span_text(ob, oe)}"
            examples[(gold_lbl, pred_lbl)].append(ex)

        # Unmatched predicted → NIL gold
        for sb, se, ob, oe, pred_lbl in pred_rels:
            if (sb, se, ob, oe) not in matched_pred_spans:
                counts[("NIL", pred_lbl)] += 1
                ex = f"{span_text(sb, se)} → {span_text(ob, oe)}"
                examples[("NIL", pred_lbl)].append(ex)

    if not any_pred:
        return None

    all_gold = sorted({k[0] for k in counts})
    all_pred = sorted({k[1] for k in counts})

    # Keep NIL at end
    def sort_key(label: str) -> tuple:
        return (1, label) if label == "NIL" else (0, label)

    all_gold = sorted(all_gold, key=sort_key)
    all_pred = sorted(all_pred, key=sort_key)

    count_df = pd.DataFrame(0, index=all_gold, columns=all_pred)
    for (g, p), n in counts.items():
        count_df.at[g, p] = n

    return count_df, dict(examples)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _per_label_accuracy(cm: pd.DataFrame, skip_nil: bool = True) -> pd.DataFrame:
    rows = []
    for label in cm.index:
        if skip_nil and label == "NIL":
            continue
        total = cm.loc[label].sum()
        correct = cm.at[label, label] if label in cm.columns else 0
        rows.append(
            {
                "Gold Label": label,
                "Total": int(total),
                "Correct": int(correct),
                "Accuracy": round(correct / total, 3) if total > 0 else float("nan"),
            }
        )
    return pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)


def _examples_table(
    cm: pd.DataFrame,
    examples: dict[tuple[str, str], list[str]],
    n: int = N_EXAMPLES,
    text_col: str = "Text",
) -> pd.DataFrame:
    rows = []
    for gold_label in cm.index:
        for pred_label in cm.columns:
            texts = examples.get((gold_label, pred_label), [])
            if not texts:
                continue
            for text, freq in Counter(texts).most_common(n):
                rows.append(
                    {
                        "Gold Label": gold_label,
                        "Pred Label": pred_label,
                        text_col: text.replace("|", "\\|"),
                        "Freq": freq,
                    }
                )
    return pd.DataFrame(
        rows, columns=["Gold Label", "Pred Label", text_col, "Freq"]
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_report(
    model: str,
    dataset: str,
    split: str,
    filepath_name: str,
    docs: list[dict],
) -> None:
    # --- NER ---
    ner_count_cm, ner_prob_cm, ner_examples = _build_ner_confusion(docs)
    ner_accuracy = _per_label_accuracy(ner_count_cm, skip_nil=False)
    ner_ex_table = _examples_table(ner_count_cm, ner_examples, text_col="Mention Text")

    # --- Relations ---
    rel_result = _build_rel_confusion(docs)

    report = MarkdownReport(
        f"Fixed-Span NER + RE — {model.upper()} on {dataset.upper()} ({split})"
    )

    report.text(
        "## Method\n\n"
        "In the **fixed-span experiment** the model receives the gold entity spans "
        "and only predicts a label for each span (NER) and the relations between "
        "them (RE). This isolates *label classification* from *span detection*.\n\n"
        "**NER:** For every span the gold label is compared to the predicted label. "
        "The count confusion matrix (rows = gold, cols = predicted) shows occurrence "
        "counts; the probability matrix shows mean `prob1 / prob2` from "
        "`predicted_ner_proba`.\n\n"
        "**RE:** Gold and predicted relations are matched by "
        "`(sub_begin, sub_end, obj_begin, obj_end)`. "
        "Unmatched gold relations are mapped to NIL predicted; unmatched predicted "
        "relations are mapped to NIL gold. "
        f"Examples show the top {N_EXAMPLES} most-frequent `subject → object` texts "
        "per label pair."
    )

    ner_total = int(ner_count_cm.sum().sum())
    ner_acc = ner_accuracy["Correct"].sum() / ner_accuracy["Total"].sum()

    report.text(
        f"**File:** `{filepath_name}`  \n"
        f"**Gold NER spans:** {ner_total}  \n"
        f"**NER overall accuracy:** {ner_acc:.3f}"
    )

    # NER sections
    report.heading("NER — Count Confusion Matrix", level=2)
    report.text("Rows = gold labels · Columns = predicted labels")
    report.table(ner_count_cm, index=True)

    report.heading("NER — Mean Probability Confusion Matrix", level=2)
    report.text(
        "Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data."
    )
    report.table(ner_prob_cm, index=True)

    report.heading("NER — Per-Label Accuracy", level=2)
    report.table(ner_accuracy)

    report.heading(f"NER — Examples (top {N_EXAMPLES} per cell)", level=2)
    report.table(ner_ex_table)

    # Relation sections
    report.heading("RE — Relation Confusion Matrix", level=2)
    if rel_result is None:
        report.text("*No predicted relations found in this file.*")
    else:
        rel_count_cm, rel_examples = rel_result
        rel_accuracy = _per_label_accuracy(rel_count_cm, skip_nil=True)
        rel_ex_table = _examples_table(
            rel_count_cm, rel_examples, text_col="Subject → Object"
        )

        gold_rels = int(rel_count_cm.loc[
            [l for l in rel_count_cm.index if l != "NIL"]
        ].sum().sum())
        pred_rels = int(rel_count_cm[[
            c for c in rel_count_cm.columns if c != "NIL"
        ]].sum().sum())

        report.text(
            f"**Gold relations:** {gold_rels}  \n"
            f"**Predicted relations:** {pred_rels}  \n\n"
            "Rows = gold labels · Columns = predicted labels · "
            "NIL = unmatched on the respective side."
        )
        report.table(rel_count_cm, index=True)

        report.heading("RE — Per-Label Accuracy", level=2)
        report.table(rel_accuracy)

        report.heading(f"RE — Examples (top {N_EXAMPLES} per cell)", level=2)
        report.table(rel_ex_table)

    out_path = OUTPUT_DIR / f"fixed_span_{model}_{dataset}_{split}.md"
    report.write(out_path)


def main() -> None:
    files = sorted(
        [*FIXED_SPANS_DIR.glob("*.jsonl"), *FIXED_SPANS_DIR.glob("*.json")]
    )
    if not files:
        print(f"No JSONL files found in {FIXED_SPANS_DIR}")
        return

    for filepath in files:
        stem = filepath.stem
        parts = stem.split("_", 2)
        if len(parts) < 3:
            print(f"Skipping unrecognised filename: {filepath.name}")
            continue
        model, dataset, split = parts[0], parts[1], "_".join(parts[2:])

        print(f"Processing {filepath.name} ...")
        docs = _load_docs(FIXED_SPANS_DIR, [filepath.name])
        _generate_report(model, dataset, split, filepath.name, docs)


if __name__ == "__main__":
    main()
