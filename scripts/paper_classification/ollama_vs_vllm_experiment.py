#!/usr/bin/env python3
"""Speed comparison: Ollama vs vLLM for structured paper classification.

Starts a vLLM server on specified GPUs, runs both backends on the same
abstracts with structured JSON output, then stops vLLM.

Usage:
    uv run python scripts/ollama_vs_vllm_experiment.py --gpus "0"
    uv run python scripts/ollama_vs_vllm_experiment.py --gpus "0,1" --limit 20
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import subprocess
import time
from pathlib import Path

import httpx
import matplotlib.pyplot as plt
import pandas as pd

from unifiedsciere.paper_classifier.classifier import (
    classify_batch_vllm,
    classify_paper,
    classify_paper_vllm,
    ensure_model,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "metadata" / "unified" / "all_papers.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "data" / "classifications" / "exp05_ollama_vs_vllm"
REPORT_DIR = PROJECT_ROOT / "reports" / "classification" / "speed"

OLLAMA_MODEL = "qwen2.5:32b-instruct-q4_K_M"
VLLM_MODEL = "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4"
VERSION = "v3"
METHOD = "with_schema"
TIMEOUT = 600.0
TEMPERATURE = 0.0


def load_papers(path: Path, limit: int) -> list[dict]:
    papers = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            paper = json.loads(line)
            if not paper.get("abstract"):
                continue
            papers.append(paper)
            if len(papers) >= limit:
                break
    return papers


def start_vllm(gpus: str, port: int) -> subprocess.Popen:
    """Start a vLLM server as a subprocess."""
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = gpus

    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        VLLM_MODEL,
        "--quantization",
        "gptq",
        "--enable-prefix-caching",
        "--max-model-len",
        "4096",
        "--gpu-memory-utilization",
        "0.5",
        "--port",
        str(port),
    ]
    logger.info("Starting vLLM: %s", " ".join(cmd))
    logger.info("CUDA_VISIBLE_DEVICES=%s", gpus)

    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )
    return proc


def wait_for_vllm(base_url: str, max_wait: int = 300, interval: int = 5) -> None:
    """Wait until the vLLM health endpoint responds."""
    url = f"{base_url.rstrip('/')}/health"
    deadline = time.time() + max_wait
    logger.info("Waiting for vLLM at %s ...", url)

    while time.time() < deadline:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    logger.info("vLLM is ready.")
                    return
        except httpx.HTTPError:
            pass
        time.sleep(interval)

    raise RuntimeError(f"vLLM did not become ready within {max_wait}s")


def stop_vllm(proc: subprocess.Popen) -> None:
    """Stop the vLLM subprocess."""
    logger.info("Stopping vLLM (pid=%d) ...", proc.pid)
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        logger.warning("vLLM did not stop gracefully, sending SIGKILL.")
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.wait(timeout=10)
    logger.info("vLLM stopped.")


def run_ollama(papers: list[dict], base_url: str) -> list[dict]:
    """Run classification via Ollama."""
    logger.info("=== Condition: OLLAMA (%s) ===", OLLAMA_MODEL)
    results = []
    total = len(papers)
    for i, paper in enumerate(papers, 1):
        pid = paper["doc_id"]
        logger.info("[%d/%d] Classifying %s ...", i, total, pid)
        result = classify_paper(
            title=paper["title"],
            abstract=paper.get("abstract", ""),
            paper_id=pid,
            method=METHOD,
            version=VERSION,
            model=OLLAMA_MODEL,
            base_url=base_url,
            timeout=TIMEOUT,
            temperature=TEMPERATURE,
        )
        results.append(result)
    return results


def run_vllm(papers: list[dict], base_url: str) -> list[dict]:
    """Run classification via vLLM."""
    logger.info("=== Condition: VLLM (%s) ===", VLLM_MODEL)
    results = []
    total = len(papers)
    for i, paper in enumerate(papers, 1):
        pid = paper["doc_id"]
        logger.info("[%d/%d] Classifying %s ...", i, total, pid)
        result = classify_paper_vllm(
            title=paper["title"],
            abstract=paper.get("abstract", ""),
            paper_id=pid,
            method=METHOD,
            version=VERSION,
            model=VLLM_MODEL,
            base_url=base_url,
            timeout=TIMEOUT,
            temperature=TEMPERATURE,
        )
        results.append(result)
    return results


def run_vllm_concurrent(
    papers: list[dict], base_url: str, concurrency: int = 8
) -> list[dict]:
    """Run classification via vLLM with concurrent requests."""
    logger.info(
        "=== Condition: VLLM CONCURRENT (%s, concurrency=%d) ===",
        VLLM_MODEL,
        concurrency,
    )
    return classify_batch_vllm(
        papers,
        method=METHOD,
        version=VERSION,
        model=VLLM_MODEL,
        base_url=base_url,
        timeout=TIMEOUT,
        temperature=TEMPERATURE,
        concurrency=concurrency,
    )


def extract_metrics(results: list[dict]) -> pd.DataFrame:
    rows = []
    for i, r in enumerate(results):
        meta = r.get("_meta", {})
        rows.append(
            {
                "index": i + 1,
                "elapsed_seconds": meta.get("elapsed_seconds"),
                "prompt_tokens": meta.get("prompt_tokens"),
                "completion_tokens": meta.get("completion_tokens"),
            }
        )
    return pd.DataFrame(rows)


def save_jsonl(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info("Saved %d results to %s", len(results), path)


def generate_figure(
    df_ollama: pd.DataFrame,
    df_vllm: pd.DataFrame,
    out_path: Path,
    df_vllm_conc: pd.DataFrame | None = None,
) -> None:
    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        df_ollama["index"],
        df_ollama["elapsed_seconds"],
        marker="o",
        label=f"Ollama ({OLLAMA_MODEL})",
    )
    ax.plot(
        df_vllm["index"],
        df_vllm["elapsed_seconds"],
        marker="s",
        label=f"vLLM sequential ({VLLM_MODEL})",
    )
    if df_vllm_conc is not None:
        ax.plot(
            df_vllm_conc["index"],
            df_vllm_conc["elapsed_seconds"],
            marker="^",
            label=f"vLLM concurrent ({VLLM_MODEL})",
        )
    ax.set_xlabel("Abstract index")
    ax.set_ylabel("Runtime (seconds)")
    ax.set_title("Per-query runtime: Ollama vs vLLM")
    ax.legend()
    ax.set_xticks(df_ollama["index"])
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure saved to %s", out_path)


def build_summary_table(
    df_ollama: pd.DataFrame,
    df_vllm: pd.DataFrame,
    df_vllm_conc: pd.DataFrame | None = None,
    vllm_conc_wall_time: float | None = None,
) -> str:
    def _stats(df: pd.DataFrame, col: str) -> dict:
        return {
            "mean": df[col].mean(),
            "median": df[col].median(),
            "total": df[col].sum(),
        }

    datasets = [
        (f"Ollama ({OLLAMA_MODEL})", df_ollama),
        (f"vLLM seq. ({VLLM_MODEL})", df_vllm),
    ]
    if df_vllm_conc is not None:
        datasets.append((f"vLLM conc. ({VLLM_MODEL})", df_vllm_conc))

    rows = []
    for label, df in datasets:
        t = _stats(df, "elapsed_seconds")
        pt = _stats(df, "prompt_tokens")
        ct = _stats(df, "completion_tokens")
        rows.append(
            {
                "Backend": label,
                "Mean time (s)": f"{t['mean']:.2f}",
                "Median time (s)": f"{t['median']:.2f}",
                "Total time (s)": f"{t['total']:.2f}",
                "Mean prompt tok.": f"{pt['mean']:.0f}",
                "Mean compl. tok.": f"{ct['mean']:.0f}",
                "Total prompt tok.": f"{pt['total']:.0f}",
                "Total compl. tok.": f"{ct['total']:.0f}",
            }
        )
    return pd.DataFrame(rows).to_markdown(index=False)


def build_report(
    df_ollama: pd.DataFrame,
    df_vllm: pd.DataFrame,
    fig_name: str,
    gpus: str,
    limit: int,
    ollama_setup_time: float = 0.0,
    vllm_setup_time: float = 0.0,
) -> str:
    summary = build_summary_table(df_ollama, df_vllm)
    speedup = df_ollama["elapsed_seconds"].mean() / df_vllm["elapsed_seconds"].mean()

    return f"""\
# Speed comparison: Ollama vs vLLM

## Research Question

Is vLLM faster than Ollama for sequential structured paper classification
using comparable 4-bit quantized models?

## Method

We compare two serving backends for the same classification task:

- **Ollama**: Uses the native `/api/chat` endpoint with the `format` parameter
  for JSON Schema enforcement via GBNF grammar constraints. Model weights are
  in GGUF format with Q4_K_M quantization.
- **vLLM**: Uses the OpenAI-compatible `/v1/chat/completions` endpoint with
  `guided_json` for constrained decoding. Model weights are in GPTQ-Int4
  format. Prefix caching is enabled (`--enable-prefix-caching`).

Both backends receive the identical system prompt, user message, and JSON
schema. The only differences are the serving engine and quantization format
(GGUF Q4_K_M vs GPTQ-Int4 — both 4-bit).

## Experimental Setting

| Parameter            | Ollama                        | vLLM                                  |
|----------------------|-------------------------------|---------------------------------------|
| Model                | `{OLLAMA_MODEL}` | `{VLLM_MODEL}` |
| Quantization         | GGUF Q4_K_M                   | GPTQ-Int4                             |
| Structured output    | `format` (GBNF grammar)       | `guided_json` (outlines/xgrammar)     |
| Prefix caching       | implicit                      | `--enable-prefix-caching`             |
| GPU(s)               | {gpus}                        | {gpus}                                |
| Prompt version       | `{VERSION}`                   | `{VERSION}`                           |
| Method               | `{METHOD}`                    | `{METHOD}`                            |
| Temperature          | {TEMPERATURE}                 | {TEMPERATURE}                         |
| Number of abstracts  | {limit}                       | {limit}                               |
| Execution order      | vLLM first, then Ollama       | —                                     |

## Results

### Per-query runtime

![Runtime comparison]({fig_name})

### Summary statistics

{summary}

### Model setup time

| Backend | Setup time (s) |
|---------|---------------|
| Ollama  | {ollama_setup_time:.2f} |
| vLLM    | {vllm_setup_time:.2f} |

Ollama setup time measures `ensure_model()` (check if model exists, pull if needed).
vLLM setup time measures server startup until the `/health` endpoint responds
(includes model loading, KV cache allocation, and engine initialization).

### Key observations

- Mean speedup (vLLM / Ollama): **{speedup:.2f}x**

## Conclusion

{"vLLM is significantly faster than Ollama" if speedup > 1.5 else "vLLM is moderately faster than Ollama" if speedup > 1.1 else "Both backends show comparable performance"}\
 for sequential structured classification, with a speedup factor of {speedup:.2f}x \
across {limit} abstracts. \
{"This is likely due to vLLM's more efficient attention implementation, prefix caching, and optimized GPTQ kernel support." if speedup > 1.1 else "At this batch size and sequential execution pattern, the serving overhead differences are minimal."}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Speed comparison: Ollama vs vLLM")
    parser.add_argument(
        "--gpus", required=True, help='GPU IDs for vLLM, e.g. "0" or "0,1"'
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--ollama-url", default="http://localhost:11555")
    parser.add_argument("--vllm-port", type=int, default=8100)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    vllm_url = f"http://localhost:{args.vllm_port}"

    papers = load_papers(args.input, args.limit)
    logger.info("Loaded %d papers from %s", len(papers), args.input)

    # --- vLLM (first, so Ollama results aren't wasted if vLLM fails) ---
    t0 = time.time()
    vllm_proc = start_vllm(args.gpus, args.vllm_port)
    try:
        wait_for_vllm(vllm_url)
        vllm_setup_time = time.time() - t0
        logger.info("vLLM setup time: %.2fs", vllm_setup_time)

        results_vllm = run_vllm(papers, vllm_url)
        save_jsonl(results_vllm, OUTPUT_DIR / "vllm.jsonl")

        # Concurrent vLLM
        t0_conc = time.time()
        results_vllm_conc = run_vllm_concurrent(papers, vllm_url)
        vllm_conc_total_time = time.time() - t0_conc
        logger.info("vLLM concurrent total wall time: %.2fs", vllm_conc_total_time)
        save_jsonl(results_vllm_conc, OUTPUT_DIR / "vllm_concurrent.jsonl")
    finally:
        stop_vllm(vllm_proc)

    # --- Ollama ---
    t0 = time.time()
    ensure_model(OLLAMA_MODEL, args.ollama_url)
    ollama_setup_time = time.time() - t0
    logger.info("Ollama setup time: %.2fs", ollama_setup_time)

    results_ollama = run_ollama(papers, args.ollama_url)
    save_jsonl(results_ollama, OUTPUT_DIR / "ollama.jsonl")

    # --- Report ---
    df_ollama = extract_metrics(results_ollama)
    df_vllm = extract_metrics(results_vllm)

    fig_path = REPORT_DIR / "ollama_vs_vllm.png"
    generate_figure(df_ollama, df_vllm, fig_path)

    report = build_report(
        df_ollama,
        df_vllm,
        "ollama_vs_vllm.png",
        args.gpus,
        args.limit,
        ollama_setup_time=ollama_setup_time,
        vllm_setup_time=vllm_setup_time,
    )
    report_path = REPORT_DIR / "ollama_vs_vllm.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    logger.info("Report written to %s", report_path)

    print(f"\n=== Done ===")
    print(f"Results:  {OUTPUT_DIR}")
    print(f"Report:   {report_path}")
    print(f"Figure:   {fig_path}")


if __name__ == "__main__":
    main()
