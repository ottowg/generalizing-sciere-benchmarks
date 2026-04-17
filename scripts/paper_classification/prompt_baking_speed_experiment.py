#!/usr/bin/env python3
"""Speed comparison: derived model (hardcoded prompt) vs standard prompting.

Runs 20 abstracts through Qwen 2.5 32B 4-bit in two conditions:
  1. "not hardcoded" — full system+user prompt sent every request (classify_paper)
  2. "hardcoded"     — system prompt baked into derived Ollama model (classify_batch)

Produces:
  - Raw JSONL results under data/classifications/exp04_prompt_baking_speed/
  - Markdown report with figure at reports/paper_classification/speed/prompt_baking_speed.md

Usage:
    uv run python scripts/prompt_baking_speed_experiment.py
    uv run python scripts/prompt_baking_speed_experiment.py --base-url http://localhost:11555
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from unifiedsciere.paper_classifier.classifier import (
    classify_batch,
    classify_paper,
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
OUTPUT_DIR = PROJECT_ROOT / "data" / "classifications" / "exp04_prompt_baking_speed"
REPORT_DIR = PROJECT_ROOT / "reports" / "classification" / "speed"

MODEL = "qwen2.5:32b-instruct-q4_K_M"
VERSION = "v1"
METHOD = "with_schema"
LIMIT = 20
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


def run_not_hardcoded(papers: list[dict], base_url: str) -> list[dict]:
    """Condition A: send full prompt every request via classify_paper()."""
    logger.info("=== Condition: NOT HARDCODED (standard prompting) ===")
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
            model=MODEL,
            base_url=base_url,
            timeout=TIMEOUT,
            temperature=TEMPERATURE,
        )
        results.append(result)
    return results


def run_hardcoded(papers: list[dict], base_url: str) -> list[dict]:
    """Condition B: baked-in system prompt via classify_batch()."""
    logger.info("=== Condition: HARDCODED (derived model) ===")
    return list(
        classify_batch(
            papers,
            method=METHOD,
            version=VERSION,
            model=MODEL,
            base_url=base_url,
            timeout=TIMEOUT,
            temperature=TEMPERATURE,
        )
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


def generate_figure(df_std: pd.DataFrame, df_hc: pd.DataFrame, out_path: Path) -> None:
    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        df_std["index"],
        df_std["elapsed_seconds"],
        marker="o",
        label="not hardcoded",
    )
    ax.plot(
        df_hc["index"],
        df_hc["elapsed_seconds"],
        marker="s",
        label="hardcoded",
    )
    ax.set_xlabel("Abstract index")
    ax.set_ylabel("Runtime (seconds)")
    ax.set_title("Per-query runtime: hardcoded vs not hardcoded system prompt")
    ax.legend()
    ax.set_xticks(df_std["index"])
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure saved to %s", out_path)


def build_summary_table(df_std: pd.DataFrame, df_hc: pd.DataFrame) -> str:
    def _stats(df: pd.DataFrame, col: str) -> dict:
        return {
            "mean": df[col].mean(),
            "median": df[col].median(),
            "total": df[col].sum(),
        }

    rows = []
    for label, df in [("not hardcoded", df_std), ("hardcoded", df_hc)]:
        t = _stats(df, "elapsed_seconds")
        pt = _stats(df, "prompt_tokens")
        ct = _stats(df, "completion_tokens")
        rows.append(
            {
                "Condition": label,
                "Mean time (s)": f"{t['mean']:.2f}",
                "Median time (s)": f"{t['median']:.2f}",
                "Total time (s)": f"{t['total']:.2f}",
                "Mean prompt tokens": f"{pt['mean']:.0f}",
                "Mean completion tokens": f"{ct['mean']:.0f}",
                "Total prompt tokens": f"{pt['total']:.0f}",
                "Total completion tokens": f"{ct['total']:.0f}",
            }
        )
    return pd.DataFrame(rows).to_markdown(index=False)


def build_report(df_std: pd.DataFrame, df_hc: pd.DataFrame, fig_name: str) -> str:
    summary = build_summary_table(df_std, df_hc)

    speedup = df_std["elapsed_seconds"].mean() / df_hc["elapsed_seconds"].mean()
    token_saving = 1 - df_hc["prompt_tokens"].mean() / df_std["prompt_tokens"].mean()

    return f"""\
# Speed comparison: hardcoded vs not hardcoded system prompt

## Research Question

Does baking the static system prompt into a derived Ollama model (via `/api/create`)
reduce per-query inference latency and prompt token usage compared to sending the
full prompt with every request?

## Method

We compare two prompting strategies for paper classification:

- **not hardcoded** (baseline): The full system prompt and task instructions are sent
  as part of every API request alongside the per-paper data. This is the standard
  approach using `classify_paper()`.
- **hardcoded** (derived model): The static portion of the prompt (system instructions,
  task description, enum definitions, rules) is baked into a derived Ollama model via
  the `/api/create` endpoint. At inference time, only the per-paper data (paper_id,
  title, abstract) is sent as the user message.

Both conditions use identical classification logic, JSON Schema enforcement
(`with_schema` via Ollama's `format` parameter), and the same prompt content.
The only difference is whether the static prompt is transmitted per-request or
pre-loaded into the model.

## Experimental Setting

| Parameter       | Value                            |
|-----------------|----------------------------------|
| Model           | `{MODEL}` |
| Prompt version  | `{VERSION}`                          |
| Method          | `{METHOD}`                |
| Temperature     | {TEMPERATURE}                          |
| Timeout         | {TIMEOUT}s                        |
| Number of abstracts | {LIMIT}                       |
| Execution order | not hardcoded first, then hardcoded |

## Results

### Per-query runtime

![Runtime comparison]({fig_name})

### Summary statistics

{summary}

### Key observations

- Mean speedup (hardcoded / not hardcoded): **{speedup:.2f}x**
- Mean prompt token reduction: **{token_saving:.1%}**

## Conclusion

{"The hardcoded (derived model) approach reduces prompt token count by baking the static system prompt into the model, which avoids re-processing the same instructions for every query. " if token_saving > 0.01 else ""}{"The runtime improvement is modest" if speedup < 1.2 else "The runtime improvement is substantial"}, with a speedup factor of {speedup:.2f}x across {LIMIT} abstracts. {"This suggests that for batch workloads the derived model approach is beneficial, especially as batch size grows." if speedup > 1.05 else "The difference is small, suggesting prompt processing overhead is not the dominant cost for this model and batch size."}
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Speed comparison: hardcoded vs not hardcoded system prompt"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-url", default="http://localhost:11555")
    args = parser.parse_args()

    papers = load_papers(args.input, LIMIT)
    logger.info("Loaded %d papers from %s", len(papers), args.input)

    # Ensure model is available before timing anything
    ensure_model(MODEL, args.base_url)

    # Condition A: not hardcoded (standard)
    results_std = run_not_hardcoded(papers, args.base_url)
    save_jsonl(results_std, OUTPUT_DIR / "not_hardcoded.jsonl")

    # Condition B: hardcoded (derived model)
    results_hc = run_hardcoded(papers, args.base_url)
    save_jsonl(results_hc, OUTPUT_DIR / "hardcoded.jsonl")

    # Extract metrics
    df_std = extract_metrics(results_std)
    df_hc = extract_metrics(results_hc)

    # Generate figure
    fig_path = REPORT_DIR / "runtime_comparison.png"
    generate_figure(df_std, df_hc, fig_path)

    # Generate report
    report = build_report(df_std, df_hc, "runtime_comparison.png")
    report_path = REPORT_DIR / "prompt_baking_speed.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    logger.info("Report written to %s", report_path)

    print(f"\n=== Done ===")
    print(f"Results:  {OUTPUT_DIR}")
    print(f"Report:   {report_path}")
    print(f"Figure:   {fig_path}")


if __name__ == "__main__":
    main()
