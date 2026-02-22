#!/usr/bin/env python3
"""Test vLLM setup with Qwen2.5-32B-Instruct-GPTQ-Int4.

Starts a vLLM server, runs 4 test requests (2 with guided_json, 2 without),
prints per-request timing, checks vLLM logs for grammar compilation, and shuts down.

Usage:
    uv run python scripts/test_setup/vllm.py --gpus "0"
    uv run python scripts/test_setup/vllm.py --gpus "0,1" --port 8100
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time

import httpx

MODEL = "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4"
TEST_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "paper_id",
        "area",
        "task_topic",
        "contributions",
        "confidence",
        "rationale",
    ],
    "properties": {
        "paper_id": {"type": "string"},
        "area": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "NLP",
                    "CV",
                    "Multimodal",
                    "Speech",
                    "RL",
                    "Theory",
                    "Systems",
                    "Other",
                ],
            },
            "minItems": 1,
            "uniqueItems": True,
        },
        "task_topic": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "QuestionAnswering",
                    "Compression",
                    "Retrieval",
                    "InformationExtraction",
                    "Summarization",
                    "MachineTranslation",
                    "Reasoning",
                    "Evaluation",
                    "AlignmentSafety",
                    "Optimization",
                    "Robustness",
                    "Efficiency",
                    "DataCuration",
                    "Other",
                ],
            },
            "minItems": 1,
            "uniqueItems": True,
        },
        "contributions": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "NewDatasetBenchmark",
                    "NewModelArchitecture",
                    "NewTrainingInferenceMethod",
                    "AnalysisMethodologyCritique",
                    "SurveyTutorial",
                    "ToolLibrarySystem",
                    "Other",
                ],
            },
            "minItems": 1,
        },
        "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "rationale": {"type": "string"},
    },
}

TEST_PROMPTS = [
    (
        "title: Attention Is All You Need\n"
        "abstract: We propose a new simple network architecture, the Transformer, "
        "based solely on attention mechanisms."
    ),
    (
        "title: BERT: Pre-training of Deep Bidirectional Transformers\n"
        "abstract: We introduce BERT, a language representation model designed to "
        "pre-train deep bidirectional representations from unlabeled text."
    ),
]

LOG_FILE = None  # set during start_vllm


def log(msg: str) -> None:
    print(f"[test-vllm] {time.strftime('%H:%M:%S')} {msg}", flush=True)


def start_vllm(gpus: str, port: int) -> tuple[subprocess.Popen, str]:
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = gpus

    log_path = f"/tmp/vllm_test_{port}.log"

    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        MODEL,
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
    log("Starting vLLM server...")
    log(f"  Command: {' '.join(cmd)}")
    log(f"  CUDA_VISIBLE_DEVICES={gpus}")
    log(f"  Log file: {log_path}")
    log("")

    log_fh = open(log_path, "w")
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )
    return proc, log_path


def wait_for_health(base_url: str, max_wait: int = 300, interval: int = 5) -> bool:
    url = f"{base_url}/health"
    deadline = time.time() + max_wait
    log(f"Waiting for vLLM health endpoint at {url} (max {max_wait}s) ...")

    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    log(f"  Health check passed on attempt {attempt}.")
                    return True
                log(f"  Attempt {attempt}: status {resp.status_code}")
        except httpx.HTTPError as e:
            log(f"  Attempt {attempt}: {e}")
        time.sleep(interval)

    log(f"  FAILED: vLLM did not become ready within {max_wait}s")
    return False


def send_request(
    base_url: str, prompt: str, use_guided_json: bool
) -> tuple[float, bool, str]:
    """Send a request and return (elapsed_seconds, success, response_content)."""
    url = f"{base_url}/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You classify papers. Return only valid JSON.",
            },
            {"role": "user", "content": f"Classify this paper:\n\n{prompt}"},
        ],
        "temperature": 0.0,
    }
    if use_guided_json:
        payload["guided_json"] = TEST_SCHEMA

    t0 = time.time()
    with httpx.Client(timeout=300) as client:
        resp = client.post(url, json=payload)
    elapsed = time.time() - t0

    if resp.status_code != 200:
        return elapsed, False, resp.text

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return elapsed, True, content


def check_logs_for_grammar(log_path: str) -> list[str]:
    """Search vLLM log file for grammar/compilation related messages."""
    keywords = ["compil", "grammar", "guided", "outlines", "xgrammar", "fsm", "regex"]
    matches = []
    try:
        with open(log_path) as f:
            for line in f:
                lower = line.lower()
                if any(kw in lower for kw in keywords):
                    matches.append(line.strip())
    except FileNotFoundError:
        pass
    return matches


def stop_vllm(proc: subprocess.Popen) -> None:
    log(f"Stopping vLLM (pid={proc.pid}) ...")
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=30)
        log("  vLLM stopped gracefully.")
    except subprocess.TimeoutExpired:
        log("  Graceful stop timed out, sending SIGKILL ...")
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.wait(timeout=10)
        log("  vLLM killed.")
    except ProcessLookupError:
        log("  vLLM process already exited.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test vLLM setup")
    parser.add_argument("--gpus", required=True, help='GPU IDs, e.g. "0" or "0,1"')
    parser.add_argument("--port", type=int, default=8100)
    args = parser.parse_args()

    base_url = f"http://localhost:{args.port}"

    log("=" * 60)
    log("vLLM Setup Test — guided_json vs no guided_json")
    log("=" * 60)
    log("")

    proc, log_path = start_vllm(args.gpus, args.port)
    try:
        if not wait_for_health(base_url):
            log("RESULT: FAIL — server did not start")
            # Print captured logs for debugging
            log("--- vLLM logs ---")
            try:
                with open(log_path) as f:
                    print(f.read(), flush=True)
            except FileNotFoundError:
                pass
            sys.exit(1)

        log("")
        log("-" * 60)
        log("Running 4 requests: 2x guided_json, then 2x without")
        log("-" * 60)
        log("")

        results = []

        # 2 requests WITH guided_json
        for i, prompt in enumerate(TEST_PROMPTS):
            label = f"guided_json #{i+1}"
            log(f"[{label}] Sending request ...")
            elapsed, ok, content = send_request(base_url, prompt, use_guided_json=True)
            results.append((label, elapsed, ok, content))
            log(f"[{label}] Elapsed: {elapsed:.2f}s | OK: {ok}")
            if ok:
                log(f"[{label}] Response: {content}")
            else:
                log(f"[{label}] ERROR: {content[:200]}")
            log("")

        # 2 requests WITHOUT guided_json
        for i, prompt in enumerate(TEST_PROMPTS):
            label = f"no_schema  #{i+1}"
            log(f"[{label}] Sending request ...")
            elapsed, ok, content = send_request(base_url, prompt, use_guided_json=False)
            results.append((label, elapsed, ok, content))
            log(f"[{label}] Elapsed: {elapsed:.2f}s | OK: {ok}")
            if ok:
                log(f"[{label}] Response: {content[:200]}")
            else:
                log(f"[{label}] ERROR: {content[:200]}")
            log("")

        # Summary
        log("=" * 60)
        log("TIMING SUMMARY")
        log("=" * 60)
        log(f"  {'Request':<20} {'Time (s)':>10} {'Status':>8}")
        log(f"  {'-'*20} {'-'*10} {'-'*8}")
        for label, elapsed, ok, _ in results:
            status = "OK" if ok else "FAIL"
            log(f"  {label:<20} {elapsed:>10.2f} {status:>8}")
        log("")

        # Check logs for grammar compilation
        log("=" * 60)
        log("LOG CHECK: grammar/compilation messages")
        log("=" * 60)
        grammar_lines = check_logs_for_grammar(log_path)
        if grammar_lines:
            for line in grammar_lines:
                log(f"  {line}")
        else:
            log("  No grammar/compilation messages found in vLLM logs.")
        log("")

        all_ok = all(ok for _, _, ok, _ in results)
        if all_ok:
            log("RESULT: PASS")
        else:
            log("RESULT: FAIL — some requests failed")
            sys.exit(1)

    finally:
        stop_vllm(proc)


if __name__ == "__main__":
    main()
