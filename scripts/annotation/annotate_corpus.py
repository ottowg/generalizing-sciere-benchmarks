"""Generate ERE annotations for a corpus using an LLM.

Reads gold JSONL from $DATA_DATASETS_FOLDER/{dataset}/{split}.jsonl,
annotates each sentence, and writes a gold-format JSONL to
$DATA_DATASETS_FOLDER/{dataset}_LLM_{model}_{version}/{split}.jsonl.

The output dataset can be loaded directly with load_corpus() as gold data.

NER format:  per-sentence list of [doc_level_begin, doc_level_end, label]
Relations:   per-sentence list of [sub_begin, sub_end, obj_begin, obj_end, label]
Both use document-level token indices (same as the original gold files).

Usage:
    uv run python scripts/annotation/annotate_corpus.py \\
        --dataset gsap-ere --split dev \\
        --model llama3.2 --backend ollama \\
        --base-url http://localhost:11434 \\
        --context-window 3 --version v1

    # Or use a YAML config file:
    uv run python scripts/annotation/annotate_corpus.py \\
        --dataset gsap-ere --split dev --config configs/annotation/llm_ere.yaml
"""

import argparse
import json
import logging
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from unifiedsciere.generate_annotations import (
    AnnotationConfig,
    annotate_document,
    load_version,
    process_sentence_output,
    render_prompt,
)
from unifiedsciere.generate_annotations.annotator import _clean_tokens

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_BATCH_BYTES = 190 * 1024 * 1024  # 190 MB, safely under the 200 MB API limit
POLL_INTERVAL   = 60                  # seconds between batch status polls
TERMINAL_STATES = {"completed", "failed", "expired", "cancelled"}


def _model_slug(model: str) -> str:
    """Sanitize a model name for use in a directory name."""
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


def _sent_offsets(sentences: list[list[str]]) -> list[int]:
    """Return the cumulative doc-level token offset for each sentence."""
    offsets = []
    total = 0
    for sent in sentences:
        offsets.append(total)
        total += len(sent)
    return offsets


def _build_output_doc(doc: dict, sent_results: list[dict]) -> dict:
    """Build a gold-format output JSONL document.

    NER entries:      [doc_level_begin, doc_level_end, label]
    Relation entries: [sub_begin, sub_end, obj_begin, obj_end, label]
    Both use document-level token indices.
    """
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


def _fmt_bytes(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def _render_all_requests(
    docs: list[dict],
    config: AnnotationConfig,
    prompt_template: str,
    *,
    try_batch: bool = False,
) -> list[dict]:
    """Render prompts for all sentences, returning batch request dicts.

    custom_id format: "{doc_id} {sent_idx}" (0-based, rsplit on last space to parse back)
    In try_batch mode: only the first 10 sentences of the first document.
    """
    cw = config.context_window
    requests = []
    for doc_idx, doc in enumerate(docs):
        if try_batch and doc_idx > 0:
            break
        doc_id = doc.get("doc_key", f"doc_{doc_idx}")
        sentences = [list(s) for s in doc["sentences"]]
        sent_range = range(min(10, len(sentences))) if try_batch else range(len(sentences))
        for i in sent_range:
            sent_tokens = sentences[i]
            before = sentences[max(0, i - cw) : i]
            after  = sentences[i : i + 1 + cw]
            context = before + after
            system_msg, user_msg = render_prompt(
                prompt_template,
                context_sentences=[_clean_tokens(s) for s in context],
                sentence_tokens=_clean_tokens(sent_tokens),
                sentence_index_in_context=len(before),
            )
            messages = []
            if system_msg:
                messages.append({"role": "system", "content": system_msg})
            messages.append({"role": "user", "content": user_msg})
            requests.append({
                "custom_id": f"{doc_id} {i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": config.model,
                    "messages": messages,
                    "temperature": config.temperature,
                },
            })
    return requests


def _count_request_tokens(requests: list[dict], enc: object) -> tuple[int, int]:
    """Return (system_tokens, user_tokens) for a list of batch requests."""
    system_total = user_total = 0
    for req in requests:
        for msg in req["body"]["messages"]:
            toks = len(enc.encode(msg["content"]))
            if msg["role"] == "system":
                system_total += toks
            else:
                user_total += toks
    return system_total, user_total


def _print_all_cost_estimates(plans: list[dict], config: AnnotationConfig) -> None:
    """Print per-split cost breakdown and grand total for all batch plans."""
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model("gpt-4o")
        except Exception:
            enc = tiktoken.get_encoding("o200k_base")
    except ImportError:
        logger.info("tiktoken not available — skipping cost estimate")
        return

    rows = []
    for plan in plans:
        n = len(plan["requests"])
        sys_tok, usr_tok = _count_request_tokens(plan["requests"], enc)
        est_out     = n * 100
        cached_cost = sys_tok  / 1_000_000 * config.price_cached
        input_cost  = usr_tok  / 1_000_000 * config.price_input
        output_cost = est_out  / 1_000_000 * config.price_output
        rows.append({
            "split":      plan["split"],
            "n":          n,
            "sys_tok":    sys_tok,
            "usr_tok":    usr_tok,
            "est_out":    est_out,
            "cost_cached": cached_cost,
            "cost_input":  input_cost,
            "cost_output": output_cost,
            "cost_total":  cached_cost + input_cost + output_cost,
        })

    total_n       = sum(r["n"]          for r in rows)
    total_sys     = sum(r["sys_tok"]    for r in rows)
    total_usr     = sum(r["usr_tok"]    for r in rows)
    total_out     = sum(r["est_out"]    for r in rows)
    total_cached  = sum(r["cost_cached"] for r in rows)
    total_input   = sum(r["cost_input"]  for r in rows)
    total_output  = sum(r["cost_output"] for r in rows)
    grand_total   = total_cached + total_input + total_output

    logger.info("─" * 72)
    logger.info(
        "Cost estimate — %d split(s), %d total requests, model=%s",
        len(plans), total_n, config.model,
    )
    logger.info(
        "  %-8s  %6s  %11s cached  %11s input  %9s out  %9s",
        "split", "reqs", "sys tok", "usr tok", "est out", "total $",
    )
    for r in rows:
        logger.info(
            "  %-8s  %6d  %11d        %11d       %9d      $%7.4f",
            r["split"], r["n"], r["sys_tok"], r["usr_tok"], r["est_out"], r["cost_total"],
        )
    logger.info("  %s", "─" * 68)
    logger.info(
        "  %-8s  %6d  %11d        %11d       %9d      $%7.4f",
        "TOTAL", total_n, total_sys, total_usr, total_out, grand_total,
    )
    logger.info("  Pricing:  cached $%.2f/1M  input $%.2f/1M  output $%.2f/1M",
                config.price_cached, config.price_input, config.price_output)
    logger.info("─" * 72)


def _split_chunks(lines: list[str]) -> list[list[str]]:
    """Split JSONL lines into chunks each safely under MAX_BATCH_BYTES."""
    chunks: list[list[str]] = []
    current: list[str] = []
    size = 0
    for line in lines:
        lb = len(line.encode()) + 1  # +1 for newline
        if current and size + lb > MAX_BATCH_BYTES:
            chunks.append(current)
            current = []
            size = 0
        current.append(line)
        size += lb
    if current:
        chunks.append(current)
    return chunks


def _prepare_batch_plan(
    dataset: str,
    split: str,
    config: AnnotationConfig,
    limit_docs: int | None = None,
    try_batch: bool = False,
) -> dict:
    """Load docs and render all prompts. Returns a plan dict for the other batch phases."""
    datasets_folder = os.getenv("DATA_DATASETS_FOLDER")
    if not datasets_folder:
        raise ValueError("DATA_DATASETS_FOLDER is not set. Add it to your .env file.")
    input_path = Path(datasets_folder) / dataset / f"{split}.jsonl"
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    output_dir = Path(datasets_folder) / f"{dataset}_LLM_{_model_slug(config.model)}_{config.version}"
    output_dir.mkdir(parents=True, exist_ok=True)

    docs = _load_docs(input_path)
    if limit_docs:
        docs = docs[:limit_docs]

    version_data = load_version(config.version)
    mode_label = " (try-batch: first doc, first 10 sentences)" if try_batch else ""
    logger.info("[%s] Rendering prompts%s...", split, mode_label)
    requests = _render_all_requests(docs, config, version_data["prompt"], try_batch=try_batch)
    logger.info("[%s] Rendered %d requests", split, len(requests))

    return {
        "dataset":    dataset,
        "split":      split,
        "try_batch":  try_batch,
        "docs":       docs,
        "requests":   requests,
        "output_dir": output_dir,
        "output_path": output_dir / f"{split}.jsonl",
    }


def _upload_batch_plan(client: object, plan: dict, config: AnnotationConfig) -> list[str]:
    """Serialize, chunk, upload, and create OpenAI batches. Returns list of batch IDs."""
    dataset, split, try_batch = plan["dataset"], plan["split"], plan["try_batch"]
    jsonl_lines = [json.dumps(req, ensure_ascii=False) for req in plan["requests"]]
    chunks = _split_chunks(jsonl_lines)
    if len(chunks) > 1:
        logger.info("[%s] Split into %d file chunks", split, len(chunks))
    batch_ids: list[str] = []
    for ci, chunk in enumerate(chunks):
        chunk_bytes = ("\n".join(chunk)).encode()
        prefix = f"[chunk {ci + 1}/{len(chunks)}] " if len(chunks) > 1 else ""
        logger.info("[%s] %sUploading %s...", split, prefix, _fmt_bytes(len(chunk_bytes)))
        file_obj = client.files.create(
            file=(f"{dataset}_{split}_{ci}.jsonl", chunk_bytes),
            purpose="batch",
        )
        batch = client.batches.create(
            input_file_id=file_obj.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "dataset": dataset,
                "split":   split,
                "model":   config.model,
                "version": config.version,
                **({"chunk": str(ci)} if len(chunks) > 1 else {}),
                **({"try_batch": "true"} if try_batch else {}),
            },
        )
        batch_ids.append(batch.id)
        logger.info("[%s] %sCreated batch %s (file %s)", split, prefix, batch.id, file_obj.id)
    return batch_ids


def _extract_response(entry: dict) -> tuple[str, dict]:
    if entry.get("error"):
        return "", {}
    resp = entry.get("response", {})
    if resp.get("status_code") != 200:
        return "", {}
    body = resp.get("body", {})
    choices = body.get("choices", [])
    if not choices:
        return "", {}
    raw = choices[0].get("message", {}).get("content", "")
    usage = body.get("usage", {})
    details = usage.get("prompt_tokens_details", {}) or {}
    return raw, {
        "prompt_tokens":     usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "cached_tokens":     details.get("cached_tokens", 0),
    }


def _transform_batch_plan(
    plan: dict,
    all_results: dict[str, dict],
    config: AnnotationConfig,
    batch_ids: list[str],
    model_resolved: str | None = None,
) -> None:
    """Transform batch results into document-format JSONL and write summary YAML."""
    split      = plan["split"]
    try_batch  = plan["try_batch"]
    docs       = plan["docs"]
    output_path = plan["output_path"]
    output_dir  = plan["output_dir"]

    docs_to_transform = docs[:1] if try_batch else docs
    total_sents = 0
    total_errors = 0
    total_missing = 0
    total_tokens_in = 0
    total_tokens_out = 0
    total_tokens_cached = 0
    spans_per_sent: list[int] = []
    rels_per_sent:  list[int] = []
    spans_per_doc:  list[int] = []
    rels_per_doc:   list[int] = []
    span_label_counts: dict[str, int] = {}
    rel_label_counts:  dict[str, int] = {}

    with open(output_path, "w") as out_f:
        for doc_idx, doc in enumerate(docs_to_transform):
            doc_id = doc.get("doc_key", f"doc_{doc_idx}")
            sentences = [list(s) for s in doc["sentences"]]
            sents = sentences[:10] if try_batch else sentences
            sent_results, doc_spans, doc_rels = [], 0, 0

            for sent_idx, sent_tokens in enumerate(sents):
                cid   = f"{doc_id} {sent_idx}"
                entry = all_results.get(cid)
                if entry is None:
                    logger.warning("[%s] Missing result: %s", split, cid)
                    total_missing += 1
                    result = {
                        "entities": [], "relations": [],
                        "ner_indices": [], "rel_indices": [],
                        "raw": "", "errors": ["missing batch result"],
                    }
                else:
                    raw, usage_meta = _extract_response(entry)
                    result = process_sentence_output(raw, sent_tokens, config.version)
                    if entry.get("error"):
                        result["errors"].append(f"batch error: {entry['error']}")
                    elif entry.get("response", {}).get("status_code") != 200:
                        result["errors"].append(
                            f"batch status {entry.get('response', {}).get('status_code')}"
                        )
                    total_tokens_in     += usage_meta.get("prompt_tokens")     or 0
                    total_tokens_out    += usage_meta.get("completion_tokens") or 0
                    total_tokens_cached += usage_meta.get("cached_tokens")     or 0

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

            total_sents += len(sents)
            spans_per_doc.append(doc_spans)
            rels_per_doc.append(doc_rels)
            doc_out = {**doc, "sentences": doc["sentences"][:10]} if try_batch else doc
            out_f.write(json.dumps(_build_output_doc(doc_out, sent_results), ensure_ascii=False) + "\n")
            logger.info(
                "  [%s %d/%d] %s — %d sents, %d spans, %d rels",
                split, doc_idx + 1, len(docs_to_transform), doc_id,
                len(sents), doc_spans, doc_rels,
            )

    def _mean(vs: list[int]) -> float:
        return round(statistics.mean(vs), 2) if vs else 0.0

    def _median(vs: list[int]) -> float:
        return statistics.median(vs) if vs else 0.0

    mean_tok_in  = total_tokens_in  / total_sents if total_sents else 0.0
    mean_tok_out = total_tokens_out / total_sents if total_sents else 0.0

    actual_cached_cost = total_tokens_cached                     / 1_000_000 * config.price_cached
    actual_input_cost  = (total_tokens_in - total_tokens_cached) / 1_000_000 * config.price_input
    actual_output_cost = total_tokens_out                        / 1_000_000 * config.price_output
    actual_total_cost  = actual_cached_cost + actual_input_cost + actual_output_cost

    summary = {
        "timestamp":             datetime.now(timezone.utc).isoformat(),
        "dataset":               plan["dataset"],
        "split":                 split,
        "model":                 config.model,
        **({"model_resolved": model_resolved} if model_resolved else {}),
        "backend":               "openai_batch",
        "version":               config.version,
        "try_batch":             try_batch,
        "batch_ids":             batch_ids,
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
        "tokens_in":     {"total": total_tokens_in,     "mean": round(mean_tok_in,  1)},
        "tokens_cached": {"total": total_tokens_cached},
        "tokens_out":    {"total": total_tokens_out,    "mean": round(mean_tok_out, 1)},
        "cost_usd": {
            "cached_input":  round(actual_cached_cost, 6),
            "regular_input": round(actual_input_cost,  6),
            "output":        round(actual_output_cost, 6),
            "total":         round(actual_total_cost,  6),
        },
    }

    summary_path = output_dir / f"{split}_runs.yaml"
    runs: list = []
    if summary_path.exists():
        runs = yaml.safe_load(summary_path.read_text()) or []
    runs.append(summary)
    summary_path.write_text(yaml.dump(runs, allow_unicode=True, sort_keys=False))

    logger.info("─" * 62)
    logger.info(
        "[%s] Done: %d sents, %d with errors, %d missing, %d unannotated",
        split, total_sents, total_errors, total_missing, summary["sentences_unannotated"],
    )
    logger.info("[%s] Actual cost:", split)
    logger.info("  Cached input  : %9d tok  $%8.4f  @ $%.2f/1M",
                total_tokens_cached, actual_cached_cost, config.price_cached)
    logger.info("  Regular input : %9d tok  $%8.4f  @ $%.2f/1M",
                total_tokens_in - total_tokens_cached, actual_input_cost, config.price_input)
    logger.info("  Output        : %9d tok  $%8.4f  @ $%.2f/1M",
                total_tokens_out, actual_output_cost, config.price_output)
    logger.info("  Total actual  :               $%8.4f", actual_total_cost)
    logger.info("─" * 62)
    logger.info("  Output:  %s", output_path)
    logger.info("  Summary: %s", summary_path)


def annotate_corpus(
    dataset: str,
    split: str,
    config: AnnotationConfig,
    limit_docs: int | None = None,
) -> None:
    datasets_folder = os.getenv("DATA_DATASETS_FOLDER")
    if not datasets_folder:
        raise ValueError("DATA_DATASETS_FOLDER is not set. Add it to your .env file.")

    input_path = Path(datasets_folder) / dataset / f"{split}.jsonl"
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = Path(datasets_folder) / f"{dataset}_LLM_{_model_slug(config.model)}_{config.version}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{split}.jsonl"

    version_data = load_version(config.version)
    prompt_template = version_data["prompt"]

    docs = _load_docs(input_path)
    if limit_docs:
        docs = docs[:limit_docs]

    # Resume: collect already-written doc_keys
    done: set[str] = set()
    if output_path.exists():
        with open(output_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line).get("doc_key", ""))
        if done:
            logger.info("Resuming: %d docs already written, skipping.", len(done))

    logger.info(
        "Annotating %d docs from %s [%s] → %s",
        len(docs),
        dataset,
        split,
        output_path,
    )
    logger.info(
        "model=%s backend=%s version=%s context_window=%d",
        config.model,
        config.backend,
        config.version,
        config.context_window,
    )

    total_sents = 0
    total_errors = 0
    total_elapsed = 0.0
    total_tokens_in = 0
    total_tokens_out = 0
    model_resolved: str | None = None

    # per-sentence and per-doc counts for distribution stats
    spans_per_sent: list[int] = []
    rels_per_sent:  list[int] = []
    spans_per_doc:  list[int] = []
    rels_per_doc:   list[int] = []
    span_label_counts: dict[str, int] = {}
    rel_label_counts:  dict[str, int] = {}

    def _extract_tokens(meta: dict) -> tuple[int, int]:
        usage = meta.get("usage", {})
        tok_in  = usage.get("prompt_tokens")     or meta.get("prompt_tokens")     or 0
        tok_out = usage.get("completion_tokens") or meta.get("completion_tokens") or 0
        return tok_in, tok_out

    with open(output_path, "a") as out_f:
        for doc_idx, doc in enumerate(docs):
            doc_id = doc.get("doc_key", f"doc_{doc_idx}")
            if doc_id in done:
                logger.info("  [%d/%d] %s — skipped (already done)", doc_idx + 1, len(docs), doc_id)
                continue

            sentences = [list(s) for s in doc["sentences"]]
            sent_results = annotate_document(sentences, config, prompt_template)

            out_doc = _build_output_doc(doc, sent_results)
            out_f.write(json.dumps(out_doc, ensure_ascii=False) + "\n")
            out_f.flush()

            n_sent = len(sentences)
            n_err = sum(1 for r in sent_results if r["errors"])
            total_sents += n_sent
            total_errors += n_err

            doc_spans = 0
            doc_rels  = 0
            for r in sent_results:
                meta = r.get("meta", {})
                total_elapsed += meta.get("elapsed_seconds", 0.0)
                ti, to = _extract_tokens(meta)
                total_tokens_in  += ti
                total_tokens_out += to
                if model_resolved is None:
                    model_resolved = meta.get("model_resolved")

                n_spans = len(r["ner_indices"])
                n_rels  = len(r["rel_indices"])
                spans_per_sent.append(n_spans)
                rels_per_sent.append(n_rels)
                doc_spans += n_spans
                doc_rels  += n_rels

                for _, _, lbl in r["ner_indices"]:
                    span_label_counts[lbl] = span_label_counts.get(lbl, 0) + 1
                for *_, rel_lbl in r["rel_indices"]:
                    rel_label_counts[rel_lbl] = rel_label_counts.get(rel_lbl, 0) + 1

            spans_per_doc.append(doc_spans)
            rels_per_doc.append(doc_rels)

            logger.info(
                "  [%d/%d] %s — %d sents, %d with errors, %d spans, %d rels",
                doc_idx + 1,
                len(docs),
                doc_id,
                n_sent,
                n_err,
                doc_spans,
                doc_rels,
            )

    def _dist(values: list[int]) -> dict:
        if not values:
            return {"total": 0, "mean": 0.0, "median": 0.0}
        return {
            "total":  sum(values),
            "mean":   round(statistics.mean(values), 2),
            "median": statistics.median(values),
        }

    mean_elapsed = total_elapsed / total_sents if total_sents else 0.0
    mean_tok_in  = total_tokens_in  / total_sents if total_sents else 0.0
    mean_tok_out = total_tokens_out / total_sents if total_sents else 0.0

    summary = {
        "timestamp":             datetime.now(timezone.utc).isoformat(),
        "dataset":               dataset,
        "split":                 split,
        "model":                 config.model,
        **({"model_resolved": model_resolved} if model_resolved else {}),
        "backend":               config.backend,
        "version":               config.version,
        "context_window":        config.context_window,
        "sentences":             total_sents,
        "sentences_with_errors": total_errors,
        "sentences_unannotated": sum(1 for n in spans_per_sent if n == 0),
        "spans": {
            "total":        sum(spans_per_sent),
            "per_sentence": {"mean": _dist(spans_per_sent)["mean"], "median": _dist(spans_per_sent)["median"]},
            "per_document": {"mean": _dist(spans_per_doc)["mean"],  "median": _dist(spans_per_doc)["median"]},
            "by_label":     dict(sorted(span_label_counts.items())),
        },
        "relations": {
            "total":        sum(rels_per_sent),
            "per_sentence": {"mean": _dist(rels_per_sent)["mean"], "median": _dist(rels_per_sent)["median"]},
            "per_document": {"mean": _dist(rels_per_doc)["mean"],  "median": _dist(rels_per_doc)["median"]},
            "by_label":     dict(sorted(rel_label_counts.items())),
        },
        "time": {
            "total_s": round(total_elapsed, 2),
            "mean_s":  round(mean_elapsed, 3),
        },
        "tokens_in": {
            "total": total_tokens_in,
            "mean":  round(mean_tok_in, 1),
        },
        "tokens_out": {
            "total": total_tokens_out,
            "mean":  round(mean_tok_out, 1),
        },
    }

    summary_path = output_dir / f"{split}_runs.yaml"
    runs: list = []
    if summary_path.exists():
        runs = yaml.safe_load(summary_path.read_text()) or []
    runs.append(summary)
    summary_path.write_text(yaml.dump(runs, allow_unicode=True, sort_keys=False))

    logger.info("─" * 56)
    logger.info("Run summary  (%d sentences, %d with errors, %d unannotated)",
                total_sents, total_errors, summary["sentences_unannotated"])
    logger.info("  Spans   total=%d  mean=%.1f/sent  median=%s/sent",
                sum(spans_per_sent),
                statistics.mean(spans_per_sent) if spans_per_sent else 0,
                statistics.median(spans_per_sent) if spans_per_sent else 0)
    logger.info("  Rels    total=%d  mean=%.1f/sent  median=%s/sent",
                sum(rels_per_sent),
                statistics.mean(rels_per_sent) if rels_per_sent else 0,
                statistics.median(rels_per_sent) if rels_per_sent else 0)
    logger.info("  Time    total=%.1fs  mean=%.2fs/sent", total_elapsed, mean_elapsed)
    logger.info("  Tok in  total=%d  mean=%.0f/sent", total_tokens_in,  mean_tok_in)
    logger.info("  Tok out total=%d  mean=%.0f/sent", total_tokens_out, mean_tok_out)
    logger.info("  Summary: %s", summary_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "LLM-based ERE annotation. "
            "Output: $DATA_DATASETS_FOLDER/{dataset}_LLM_{model}_{version}/{split}.jsonl. "
            "Omit --split to process all JSONL files found in the dataset folder."
        )
    )
    parser.add_argument(
        "--dataset", required=True, help="Dataset name (e.g. gsap-ere, scier, scinlp)"
    )
    parser.add_argument(
        "--split", nargs="+",
        help="Split(s) to annotate (e.g. dev test). Omit to process all JSONL files.",
    )
    parser.add_argument(
        "--config", help="Path to YAML config file (overrides CLI flags)"
    )
    parser.add_argument("--model",           default="llama4:latest")
    parser.add_argument("--base-url",        default="http://localhost:11434")
    parser.add_argument("--api-key",         default="", help="API key (required for --batch / --try-batch)")
    parser.add_argument("--backend",         default="ollama", choices=["ollama", "vllm", "openai"])
    parser.add_argument("--version",         default="v1")
    parser.add_argument("--context-window",  type=int,   default=3)
    parser.add_argument("--temperature",     type=float, default=0.0)
    parser.add_argument("--timeout",         type=float, default=120.0)
    parser.add_argument("--limit",           type=int,   default=None,
                        help="Process only first N documents per split")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--batch", action="store_true",
        help="Upload to OpenAI Batch API, monitor, download, and write output JSONL end-to-end.",
    )
    mode.add_argument(
        "--try-batch", action="store_true",
        help="Like --batch but only the first 10 sentences of the first document (quick smoke test).",
    )
    args = parser.parse_args()

    if args.config:
        from unifiedsciere.generate_annotations import load_config
        config = load_config(args.config)
    else:
        config = AnnotationConfig(
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            backend=args.backend,
            version=args.version,
            context_window=args.context_window,
            temperature=args.temperature,
            timeout=args.timeout,
        )

    datasets_folder = os.getenv("DATA_DATASETS_FOLDER")
    if not datasets_folder:
        raise ValueError("DATA_DATASETS_FOLDER is not set. Add it to your .env file.")
    dataset_dir = Path(datasets_folder) / args.dataset

    if args.split:
        splits = args.split
    else:
        splits = sorted(p.stem for p in dataset_dir.glob("*.jsonl"))
        if not splits:
            raise FileNotFoundError(f"No JSONL files found in {dataset_dir}")
        logger.info("Auto-discovered splits: %s", splits)

    if args.batch or args.try_batch:
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("openai package not installed. Run: uv add openai")
        client = OpenAI(api_key=config.api_key)

        # Phase 1: render all splits, then show combined cost estimate and confirm once
        plans = []
        for split in splits:
            logger.info("Preparing split: %s", split)
            plan = _prepare_batch_plan(
                args.dataset, split, config, args.limit, args.try_batch
            )
            plans.append(plan)

        _print_all_cost_estimates(plans, config)

        try:
            answer = input("Proceed and submit to OpenAI? [y/N] ").strip().lower()
        except EOFError:
            answer = "y"
        if answer not in ("y", "yes"):
            logger.info("Aborted.")
            return

        # Phase 2: submit all splits (batches run in parallel on OpenAI's side)
        batch_ids_by_plan: list[list[str]] = []
        batch_to_plan_idx: dict[str, int]  = {}
        for pi, plan in enumerate(plans):
            bids = _upload_batch_plan(client, plan, config)
            batch_ids_by_plan.append(bids)
            for bid in bids:
                batch_to_plan_idx[bid] = pi

        # Phase 3: poll all batches together
        logger.info(
            "Monitoring %d batch(es) across %d split(s) — polling every %ds...",
            len(batch_to_plan_idx), len(plans), POLL_INTERVAL,
        )
        results_by_plan: list[dict[str, dict]]  = [{} for _ in plans]
        resolved_by_plan: list[str | None]       = [None] * len(plans)
        pending = dict(batch_to_plan_idx)

        while pending:
            time.sleep(POLL_INTERVAL)
            for bid in list(pending):
                batch = client.batches.retrieve(bid)
                pi    = pending[bid]
                c     = batch.request_counts
                logger.info(
                    "  [%s] %s  %-12s  %d/%d completed  %d failed",
                    plans[pi]["split"], bid, batch.status,
                    c.completed, c.total, c.failed,
                )
                if batch.status in TERMINAL_STATES:
                    if batch.output_file_id:
                        for line in client.files.content(batch.output_file_id).text.splitlines():
                            if not line.strip():
                                continue
                            entry = json.loads(line)
                            cid = entry.get("custom_id", "")
                            if cid:
                                results_by_plan[pi][cid] = entry
                                if resolved_by_plan[pi] is None:
                                    resolved_by_plan[pi] = (
                                        entry.get("response", {}).get("body", {}).get("model")
                                    )
                    if batch.error_file_id:
                        for line in client.files.content(batch.error_file_id).text.splitlines():
                            if not line.strip():
                                continue
                            entry = json.loads(line)
                            cid = entry.get("custom_id", "")
                            if cid and cid not in results_by_plan[pi]:
                                results_by_plan[pi][cid] = entry
                    if batch.status != "completed":
                        logger.warning("Batch %s ended with status: %s", bid, batch.status)
                    del pending[bid]

        logger.info("All batches done.")

        # Phase 4: transform each split
        for plan, results, model_resolved, batch_ids in zip(
            plans, results_by_plan, resolved_by_plan, batch_ids_by_plan
        ):
            logger.info("═" * 56)
            logger.info("Transforming split: %s (%d results)", plan["split"], len(results))
            _transform_batch_plan(plan, results, config, batch_ids, model_resolved)

    else:
        for split in splits:
            logger.info("═" * 56)
            logger.info("Processing split: %s", split)
            annotate_corpus(
                dataset=args.dataset,
                split=split,
                config=config,
                limit_docs=args.limit,
            )


if __name__ == "__main__":
    main()
