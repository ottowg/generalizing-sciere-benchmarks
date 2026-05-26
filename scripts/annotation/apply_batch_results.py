"""Convert OpenAI Batch API results to document-format JSONL.

Reads:
  - original dataset JSONL (document-based) for document/sentence structure
  - batch results JSONL (sentence-based) from the OpenAI Batch API

Writes:
  - $DATA_DATASETS_FOLDER/{dataset}_LLM_{model}_{version}/{split}.jsonl
  - appends a run summary to {split}_runs.yaml in the same directory

custom_id format in the batch request file: "{doc_id} {sent_idx}"
Parsed with rsplit(" ", 1) so doc_ids containing spaces are handled correctly.

Usage:
    uv run python scripts/annotation/apply_batch_results.py \\
        --dataset gsap-ere --split train \\
        --batch-results /path/to/train_answer.jsonl \\
        --model gpt-4o-mini --version v3
"""

import argparse
import json
import logging
import os
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from unifiedsciere.generate_annotations import process_sentence_output

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _model_slug(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "-", model).strip("-")


def _load_docs(path: Path) -> list[dict]:
    docs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                doc = json.loads(line)
                if "doc_key" not in doc and "doc_id" in doc:
                    doc["doc_key"] = doc["doc_id"]
                docs.append(doc)
    return docs


def _load_batch_results(path: Path) -> dict[tuple[str, int], dict]:
    """Index batch results by (doc_id, sent_idx)."""
    index: dict[tuple[str, int], dict] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            custom_id = entry.get("custom_id", "")
            try:
                doc_id, sent_idx_str = custom_id.rsplit(" ", 1)
                sent_idx = int(sent_idx_str)
            except (ValueError, AttributeError):
                logger.warning("Skipping unparseable custom_id: %r", custom_id)
                continue
            index[(doc_id, sent_idx)] = entry
    return index


def _extract_response(entry: dict) -> tuple[str, dict, str | None]:
    """Extract (raw_content, usage_meta, model_resolved) from a batch result entry."""
    error = entry.get("error")
    if error:
        return "", {}, None

    response = entry.get("response", {})
    if response.get("status_code") != 200:
        return "", {}, None

    body = response.get("body", {})
    choices = body.get("choices", [])
    if not choices:
        return "", {}, None

    raw = choices[0].get("message", {}).get("content", "")
    usage = body.get("usage", {})
    meta = {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
    }
    model_resolved = body.get("model")
    return raw, meta, model_resolved


def _sent_offsets(sentences: list[list[str]]) -> list[int]:
    offsets = []
    total = 0
    for sent in sentences:
        offsets.append(total)
        total += len(sent)
    return offsets


def _build_output_doc(doc: dict, sent_results: list[dict]) -> dict:
    sentences = [list(s) for s in doc["sentences"]]
    offsets = _sent_offsets(sentences)

    ner_per_sent = []
    rels_per_sent = []

    for sent_idx, result in enumerate(sent_results):
        off = offsets[sent_idx]
        ner = [[off + b, off + e, lbl] for b, e, lbl in result["ner_indices"]]
        ner_per_sent.append(ner)
        rels = [
            [off + sb, off + se, off + ob, off + oe, rl]
            for sb, se, _sl, ob, oe, _ol, rl in result["rel_indices"]
        ]
        rels_per_sent.append(rels)

    out = {
        "doc_key": doc.get("doc_key", ""),
        "split": doc.get("split", ""),
        "sentences": doc["sentences"],
        "ner": ner_per_sent,
        "relations": rels_per_sent,
    }
    errors_per_sent = [r["errors"] for r in sent_results]
    if any(errors_per_sent):
        out["sentence_errors"] = errors_per_sent
    return out


def apply_batch_results(
    dataset: str,
    split: str,
    batch_results_path: Path,
    model: str,
    version: str,
    backend: str = "openai",
) -> None:
    datasets_folder = os.getenv("DATA_DATASETS_FOLDER")
    if not datasets_folder:
        raise ValueError("DATA_DATASETS_FOLDER is not set. Add it to your .env file.")

    input_path = Path(datasets_folder) / dataset / f"{split}.jsonl"
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = Path(datasets_folder) / f"{dataset}_LLM_{_model_slug(model)}_{version}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{split}.jsonl"

    docs = _load_docs(input_path)
    batch_index = _load_batch_results(batch_results_path)

    logger.info(
        "Applying batch results: %d docs, %d batch entries → %s",
        len(docs), len(batch_index), output_path,
    )

    total_sents = 0
    total_errors = 0
    total_missing = 0
    total_tokens_in = 0
    total_tokens_out = 0
    spans_per_sent: list[int] = []
    rels_per_sent:  list[int] = []
    spans_per_doc:  list[int] = []
    rels_per_doc:   list[int] = []
    span_label_counts: dict[str, int] = {}
    rel_label_counts:  dict[str, int] = {}
    model_resolved: str | None = None

    with open(output_path, "w") as out_f:
        for doc_idx, doc in enumerate(docs):
            doc_id = doc.get("doc_key", f"doc_{doc_idx}")
            sentences = [list(s) for s in doc["sentences"]]
            sent_results = []

            doc_spans = 0
            doc_rels = 0

            for sent_idx, sent_tokens in enumerate(sentences):
                entry = batch_index.get((doc_id, sent_idx))
                if entry is None:
                    logger.warning("Missing batch result: doc=%r sent=%d", doc_id, sent_idx)
                    total_missing += 1
                    sent_results.append({
                        "entities": [], "relations": [],
                        "ner_indices": [], "rel_indices": [],
                        "raw": "", "errors": ["missing batch result"],
                    })
                    spans_per_sent.append(0)
                    rels_per_sent.append(0)
                    continue

                raw, usage_meta, resolved = _extract_response(entry)
                if model_resolved is None and resolved:
                    model_resolved = resolved

                result = process_sentence_output(raw, sent_tokens, version)

                if entry.get("error"):
                    result["errors"].append(f"batch error: {entry['error']}")
                elif entry.get("response", {}).get("status_code") != 200:
                    result["errors"].append(
                        f"batch status {entry.get('response', {}).get('status_code')}"
                    )

                total_tokens_in  += usage_meta.get("prompt_tokens") or 0
                total_tokens_out += usage_meta.get("completion_tokens") or 0

                n_spans = len(result["ner_indices"])
                n_rels  = len(result["rel_indices"])
                spans_per_sent.append(n_spans)
                rels_per_sent.append(n_rels)
                doc_spans += n_spans
                doc_rels  += n_rels

                for _, _, lbl in result["ner_indices"]:
                    span_label_counts[lbl] = span_label_counts.get(lbl, 0) + 1
                for *_, rel_lbl in result["rel_indices"]:
                    rel_label_counts[rel_lbl] = rel_label_counts.get(rel_lbl, 0) + 1

                if result["errors"]:
                    total_errors += 1

                sent_results.append(result)

            total_sents += len(sentences)
            spans_per_doc.append(doc_spans)
            rels_per_doc.append(doc_rels)

            out_doc = _build_output_doc(doc, sent_results)
            out_f.write(json.dumps(out_doc, ensure_ascii=False) + "\n")

            logger.info(
                "  [%d/%d] %s — %d sents, %d spans, %d rels",
                doc_idx + 1, len(docs), doc_id,
                len(sentences), doc_spans, doc_rels,
            )

    def _mean(values: list[int]) -> float:
        return round(statistics.mean(values), 2) if values else 0.0

    def _median(values: list[int]) -> float:
        return statistics.median(values) if values else 0.0

    mean_tok_in  = total_tokens_in  / total_sents if total_sents else 0.0
    mean_tok_out = total_tokens_out / total_sents if total_sents else 0.0

    summary = {
        "timestamp":             datetime.now(timezone.utc).isoformat(),
        "dataset":               dataset,
        "split":                 split,
        "model":                 model,
        **({"model_resolved": model_resolved} if model_resolved else {}),
        "backend":               backend,
        "version":               version,
        "batch_results_file":    str(batch_results_path),
        "sentences":             total_sents,
        "sentences_with_errors": total_errors,
        "sentences_missing":     total_missing,
        "sentences_unannotated": sum(1 for n in spans_per_sent if n == 0),
        "spans": {
            "total":        sum(spans_per_sent),
            "per_sentence": {"mean": _mean(spans_per_sent), "median": _median(spans_per_sent)},
            "per_document": {"mean": _mean(spans_per_doc),  "median": _median(spans_per_doc)},
            "by_label":     dict(sorted(span_label_counts.items())),
        },
        "relations": {
            "total":        sum(rels_per_sent),
            "per_sentence": {"mean": _mean(rels_per_sent), "median": _median(rels_per_sent)},
            "per_document": {"mean": _mean(rels_per_doc),  "median": _median(rels_per_doc)},
            "by_label":     dict(sorted(rel_label_counts.items())),
        },
        "tokens_in":  {"total": total_tokens_in,  "mean": round(mean_tok_in,  1)},
        "tokens_out": {"total": total_tokens_out, "mean": round(mean_tok_out, 1)},
    }

    summary_path = output_dir / f"{split}_runs.yaml"
    runs: list = []
    if summary_path.exists():
        runs = yaml.safe_load(summary_path.read_text()) or []
    runs.append(summary)
    summary_path.write_text(yaml.dump(runs, allow_unicode=True, sort_keys=False))

    logger.info("─" * 56)
    logger.info(
        "Done: %d sents, %d with errors, %d missing, %d unannotated",
        total_sents, total_errors, total_missing, summary["sentences_unannotated"],
    )
    logger.info(
        "  Spans   total=%d  mean=%.1f/sent", sum(spans_per_sent), _mean(spans_per_sent)
    )
    logger.info(
        "  Rels    total=%d  mean=%.1f/sent", sum(rels_per_sent), _mean(rels_per_sent)
    )
    logger.info("  Tok in  total=%d  mean=%.0f/sent", total_tokens_in,  mean_tok_in)
    logger.info("  Tok out total=%d  mean=%.0f/sent", total_tokens_out, mean_tok_out)
    logger.info("  Output:  %s", output_path)
    logger.info("  Summary: %s", summary_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Apply OpenAI Batch API results to produce document-format JSONL. "
            "Output: $DATA_DATASETS_FOLDER/{dataset}_LLM_{model}_{version}/{split}.jsonl"
        )
    )
    parser.add_argument(
        "--dataset", required=True, help="Dataset name (e.g. gsap-ere, scier, scinlp)"
    )
    parser.add_argument("--split", required=True, help="Split name (e.g. train, dev, test)")
    parser.add_argument(
        "--batch-results", required=True,
        help="Path to the OpenAI Batch API results JSONL file",
    )
    parser.add_argument("--model", required=True, help="Model name used to generate the batch (e.g. gpt-4o-mini)")
    parser.add_argument("--version", required=True, help="Prompt version used to generate the batch (e.g. v3)")
    parser.add_argument("--backend", default="openai", help="Backend label for the summary YAML (default: openai)")
    args = parser.parse_args()

    apply_batch_results(
        dataset=args.dataset,
        split=args.split,
        batch_results_path=Path(args.batch_results),
        model=args.model,
        version=args.version,
        backend=args.backend,
    )


if __name__ == "__main__":
    main()
