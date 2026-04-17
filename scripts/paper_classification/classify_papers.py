#!/usr/bin/env python3
"""Classify papers from a JSONL file using an LLM via Ollama.

Usage examples:
    # Run from experiment config
    python scripts/classify_papers.py --config configs/experiments/exp01_llama4.yaml

    # Override limit from config
    python scripts/classify_papers.py --config configs/experiments/exp01_llama4.yaml --limit 5

    # Direct CLI usage (no config)
    python scripts/classify_papers.py --method with_schema --model llama4 --limit 5
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from unifiedsciere.paper_classifier.classifier import (
    classify_batch,
    load_all_experiment_configs,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_INPUT = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "metadata"
    / "unified"
    / "all_papers.jsonl"
)


def load_papers(path: Path, limit: int | None = None) -> list[dict]:
    papers = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            paper = json.loads(line)
            if not paper.get("abstract"):
                logger.warning("Skipping %s (no abstract)", paper.get("doc_id", "?"))
                continue
            papers.append(paper)
            if limit and len(papers) >= limit:
                break
    return papers


def run_experiment(cfg, cli_limit: int | None = None) -> None:
    """Run a single experiment from an ExperimentConfig."""
    limit = cli_limit if cli_limit is not None else cfg.limit
    input_path = Path(cfg.input)
    if not input_path.is_absolute():
        input_path = Path(__file__).resolve().parent.parent / input_path

    papers = load_papers(input_path, limit=limit)
    logger.info(
        "Experiment '%s': %d papers, model=%s, version=%s, methods=%s",
        cfg.name,
        len(papers),
        cfg.model,
        cfg.version,
        cfg.methods,
    )

    for method in cfg.methods:
        logger.info("--- Running method: %s ---", method)
        output_path = cfg.output_path(method)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        total = 0
        valid = 0
        with open(output_path, "w") as f:
            for result in classify_batch(
                papers,
                method=method,
                version=cfg.version,
                model=cfg.model,
                base_url=cfg.base_url,
                timeout=cfg.timeout,
                temperature=cfg.temperature,
            ):
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()
                total += 1
                if result.get("_meta", {}).get("valid", False):
                    valid += 1

        logger.info("  %d/%d valid. Output: %s", valid, total, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify papers using an LLM via Ollama."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Experiment config YAML file. Overrides other CLI args.",
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--method", choices=["with_schema", "without_schema"], default="with_schema"
    )
    parser.add_argument("--version", default="v1")
    parser.add_argument("--model", default="llama4")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()

    if args.config:
        experiments = load_all_experiment_configs(args.config)
        for cfg in experiments:
            run_experiment(cfg, cli_limit=args.limit)
        return

    # Direct CLI mode (no config)
    if args.output is None:
        args.output = Path(f"data/classifications/{args.version}_{args.method}.jsonl")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    papers = load_papers(args.input, limit=args.limit)
    logger.info("Loaded %d papers from %s", len(papers), args.input)

    total = 0
    valid = 0
    with open(args.output, "w") as f:
        for r in classify_batch(
            papers,
            method=args.method,
            version=args.version,
            model=args.model,
            base_url=args.base_url,
            timeout=args.timeout,
        ):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            total += 1
            if r.get("_meta", {}).get("valid", False):
                valid += 1

    logger.info("Done. %d/%d valid. Output: %s", valid, total, args.output)


if __name__ == "__main__":
    main()
