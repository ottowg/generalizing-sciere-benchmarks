"""Paper classifier using an external LLM API (Ollama).

Supports two methods:
  - with_schema: provides the JSON Schema to the LLM and uses Ollama's
    structured output (format parameter) to enforce it.
  - without_schema: inlines enum descriptions in the prompt and lets the
    LLM produce free-form JSON.

Both methods validate the response against the schema using jsonschema.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import httpx
import jsonschema

logger = logging.getLogger(__name__)

VERSIONS_DIR = Path(__file__).parent / "versions"


# ---------------------------------------------------------------------------
# Experiment config
# ---------------------------------------------------------------------------


@dataclass
class ExperimentConfig:
    """Configuration for a classification experiment."""

    name: str
    model: str = "llama4"
    base_url: str = "http://localhost:11434"
    version: str = "v1"
    methods: list[str] = field(
        default_factory=lambda: ["with_schema", "without_schema"]
    )
    input: str = "data/metadata/unified/all_papers.jsonl"
    output_dir: str = "data/classifications"
    limit: int | None = None
    timeout: float = 300.0
    temperature: float = 0.0
    description: str = ""

    def output_path(self, method: str) -> Path:
        return Path(self.output_dir) / self.name / f"{method}.jsonl"


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    """Load an experiment config from a YAML file."""
    import yaml

    path = Path(path)
    with open(path) as f:
        raw = yaml.safe_load(f)

    return ExperimentConfig(**raw)


def load_all_experiment_configs(path: str | Path) -> list[ExperimentConfig]:
    """Load multiple experiment configs from a YAML file.

    The file can contain a single experiment (top-level mapping) or
    multiple experiments under an ``experiments`` key (list of mappings).
    """
    import yaml

    path = Path(path)
    with open(path) as f:
        raw = yaml.safe_load(f)

    if isinstance(raw, dict) and "experiments" in raw:
        return [ExperimentConfig(**exp) for exp in raw["experiments"]]
    return [ExperimentConfig(**raw)]


# ---------------------------------------------------------------------------
# Version loader
# ---------------------------------------------------------------------------


def load_version(version: str) -> dict[str, Any]:
    """Load schema, prompts, examples, and version manifest for a given version.

    Returns a dict with keys: schema, prompt_with_schema, prompt_without_schema,
    examples, manifest.
    """
    import yaml

    version_dir = VERSIONS_DIR / version
    if not version_dir.is_dir():
        available = [p.name for p in VERSIONS_DIR.iterdir() if p.is_dir()]
        raise FileNotFoundError(
            f"Version '{version}' not found in {VERSIONS_DIR}. Available: {available}"
        )

    # Load version manifest
    manifest_path = version_dir / "version.yaml"
    manifest = None
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

    schema_path = version_dir / "schema.json"
    schema = json.loads(schema_path.read_text()) if schema_path.exists() else None

    # Load prompts — v3+ uses a single prompt.txt, v1/v2 use with/without variants
    prompt_path = version_dir / "prompt.txt"
    if prompt_path.exists():
        prompt = prompt_path.read_text()
        prompt_with_schema = prompt
        prompt_without_schema = prompt
    else:
        prompt_with_schema = None
        prompt_without_schema = None
        for name in ("prompt_with_schema", "prompt_without_schema"):
            path = version_dir / f"{name}.txt"
            if path.exists():
                if name == "prompt_with_schema":
                    prompt_with_schema = path.read_text()
                else:
                    prompt_without_schema = path.read_text()

    examples_dir = version_dir / "examples"
    examples = []
    if examples_dir.is_dir():
        for p in sorted(examples_dir.glob("*.json")):
            examples.append(json.loads(p.read_text()))

    return {
        "schema": schema,
        "prompt_with_schema": prompt_with_schema,
        "prompt_without_schema": prompt_without_schema,
        "examples": examples,
        "manifest": manifest,
    }


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------


def _parse_prompt_sections(raw: str) -> tuple[str, str]:
    """Split a prompt template into (system, user) parts.

    The template uses [SYSTEM] and [USER] markers.
    """
    system = ""
    user = ""
    current = None
    for line in raw.splitlines(keepends=True):
        stripped = line.strip()
        if stripped == "[SYSTEM]":
            current = "system"
            continue
        elif stripped == "[USER]":
            current = "user"
            continue
        if current == "system":
            system += line
        elif current == "user":
            user += line
    return system.strip(), user.strip()


def render_prompt(
    template: str,
    *,
    paper_id: str,
    title: str,
    abstract: str,
    schema_json: str | None = None,
) -> tuple[str, str]:
    """Render a prompt template, returning (system_message, user_message)."""
    filled = template.replace("{{paper_id}}", paper_id)
    filled = filled.replace("{{title}}", title)
    filled = filled.replace("{{abstract}}", abstract)
    if schema_json is not None:
        filled = filled.replace("{{SCHEMA_JSON_HERE}}", schema_json)
    return _parse_prompt_sections(filled)


def split_prompt_static_dynamic(
    template: str,
    *,
    schema_json: str | None = None,
) -> tuple[str, str]:
    """Split a prompt template into a static system prompt and a dynamic user template.

    The static part contains the [SYSTEM] content and the [USER] instructions
    (everything before the per-paper placeholders). The dynamic part contains
    only the per-paper template with ``{{paper_id}}``, ``{{title}}``, and
    ``{{abstract}}`` placeholders.

    Returns:
        (static_system_prompt, dynamic_user_template)
    """
    if schema_json is not None:
        template = template.replace("{{SCHEMA_JSON_HERE}}", schema_json)

    system_msg, user_msg = _parse_prompt_sections(template)

    # Split user message at the first template variable
    split_idx = user_msg.find("{{paper_id}}")
    if split_idx == -1:
        # No split point found — treat entire user section as static
        return f"{system_msg}\n\n{user_msg}".strip(), ""

    static_user_part = user_msg[:split_idx].rstrip()
    dynamic_template = user_msg[split_idx:]

    static_prompt = f"{system_msg}\n\n{static_user_part}".strip()
    return static_prompt, dynamic_template


# ---------------------------------------------------------------------------
# Response parsing helpers
# ---------------------------------------------------------------------------

_CODE_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n(.*?)\n\s*```",
    re.DOTALL,
)


def _extract_json(raw: str) -> str:
    """Extract JSON from an LLM response that may contain code fences or trailing text."""
    # Try to find JSON inside code fences first
    m = _CODE_FENCE_RE.search(raw)
    if m:
        return m.group(1).strip()

    # Otherwise try to find the outermost { ... } block
    start = raw.find("{")
    if start == -1:
        return raw

    depth = 0
    end = start
    for i, ch in enumerate(raw[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    return raw[start : end + 1]


# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------


def ensure_model(model: str, base_url: str, timeout: float = 600.0) -> None:
    """Check if the model is available on Ollama, pull it if not.

    Raises RuntimeError if the model cannot be made available.
    """
    url = base_url.rstrip("/")
    # Check if model is already available
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{url}/api/show", json={"name": model})
            if resp.status_code == 200:
                logger.info("Model '%s' is available.", model)
                return
    except httpx.HTTPError:
        pass

    # Try to pull the model
    logger.info("Model '%s' not found locally. Pulling...", model)
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                f"{url}/api/pull",
                json={"name": model, "stream": False},
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Model '{model}' is not available and pulling failed: {exc}"
        ) from exc

    # Verify it's now available
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{url}/api/show", json={"name": model})
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Model '{model}' was pulled but is still not available: {exc}"
        ) from exc

    logger.info("Model '%s' pulled successfully.", model)


def _derived_model_name(base_model: str, version: str, method: str) -> str:
    """Build a deterministic derived-model name for Ollama."""
    sanitized = base_model.replace("/", "-").replace(":", "-")
    return f"{sanitized}-classifier-{version}-{method}"


def create_ollama_model(
    base_model: str,
    derived_name: str,
    system_prompt: str,
    base_url: str,
    timeout: float = 120.0,
) -> None:
    """Create a derived Ollama model with a baked-in system prompt.

    Uses the ``/api/create`` endpoint so the system prompt is only processed
    once instead of being sent with every request.

    Raises RuntimeError if creation fails.
    """
    url = f"{base_url.rstrip('/')}/api/create"
    payload = {
        "from": base_model,
        "model": derived_name,
        "system": system_prompt,
    }
    logger.info("Creating derived model '%s' from '%s' ...", derived_name, base_model)
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Failed to create derived model '{derived_name}': {exc}"
        ) from exc
    logger.info("Derived model '%s' ready.", derived_name)


def _call_ollama(
    system_msg: str,
    user_msg: str,
    *,
    model: str,
    base_url: str,
    format_schema: dict | None = None,
    timeout: float = 300.0,
    temperature: float = 0.0,
) -> str:
    """Call Ollama's native /api/chat endpoint.

    Uses the native API (not /v1/chat/completions) because only the native
    endpoint supports the ``format`` parameter for JSON Schema enforcement
    via GBNF grammar constraints.

    Args:
        format_schema: If provided, passed as the ``format`` parameter to
            enforce structured JSON output at the token-sampling level.
    """
    url = f"{base_url.rstrip('/')}/api/chat"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if format_schema is not None:
        payload["format"] = format_schema

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()

    data = resp.json()
    content = data["message"]["content"]
    usage = {
        "prompt_tokens": data.get("prompt_eval_count"),
        "completion_tokens": data.get("eval_count"),
    }
    logger.info(
        "Tokens — prompt: %s, completion: %s",
        usage["prompt_tokens"],
        usage["completion_tokens"],
    )
    return content, usage


def _call_vllm(
    system_msg: str,
    user_msg: str,
    *,
    model: str,
    base_url: str,
    format_schema: dict | None = None,
    timeout: float = 300.0,
    temperature: float = 0.0,
) -> tuple[str, dict]:
    """Call a vLLM OpenAI-compatible /v1/chat/completions endpoint.

    Args:
        format_schema: If provided, passed as ``guided_json`` to enforce
            structured JSON output via constrained decoding.
    """
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": temperature,
    }
    if format_schema is not None:
        payload["guided_json"] = format_schema

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage_data = data.get("usage", {})
    usage = {
        "prompt_tokens": usage_data.get("prompt_tokens"),
        "completion_tokens": usage_data.get("completion_tokens"),
    }
    logger.info(
        "Tokens — prompt: %s, completion: %s",
        usage["prompt_tokens"],
        usage["completion_tokens"],
    )
    return content, usage


async def _call_vllm_async(
    system_msg: str,
    user_msg: str,
    *,
    model: str,
    base_url: str,
    client: httpx.AsyncClient,
    format_schema: dict | None = None,
    temperature: float = 0.0,
) -> tuple[str, dict]:
    """Async version of _call_vllm for concurrent batch requests."""
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": temperature,
    }
    if format_schema is not None:
        payload["guided_json"] = format_schema

    resp = await client.post(url, json=payload)
    resp.raise_for_status()

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage_data = data.get("usage", {})
    usage = {
        "prompt_tokens": usage_data.get("prompt_tokens"),
        "completion_tokens": usage_data.get("completion_tokens"),
    }
    return content, usage


def classify_batch_vllm(
    papers: list[dict[str, str]],
    *,
    method: str = "with_schema",
    version: str = "v3",
    model: str = "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4",
    base_url: str = "http://localhost:8100",
    timeout: float = 600.0,
    temperature: float = 0.0,
    concurrency: int = 8,
) -> list[dict[str, Any]]:
    """Classify papers via vLLM with concurrent requests.

    Sends up to ``concurrency`` requests in parallel to leverage vLLM's
    continuous batching. Returns results in the same order as ``papers``.
    """
    ver = load_version(version)
    schema = ver["schema"]
    template = ver[f"prompt_{method}"]
    if template is None:
        raise ValueError(
            f"No prompt template for method '{method}' in version '{version}'"
        )
    format_schema = schema if method == "with_schema" else None
    manifest = ver.get("manifest")

    async def _classify_one(
        paper: dict, idx: int, sem: asyncio.Semaphore, client: httpx.AsyncClient
    ) -> dict[str, Any]:
        pid = paper["doc_id"]
        title = paper["title"]
        abstract = paper.get("abstract", "")

        system_msg, user_msg = render_prompt(
            template,
            paper_id=pid,
            title=title,
            abstract=abstract,
        )

        async with sem:
            logger.info("[%d/%d] Classifying %s ...", idx + 1, len(papers), pid)
            t0 = time.time()
            try:
                raw, usage = await _call_vllm_async(
                    system_msg,
                    user_msg,
                    model=model,
                    base_url=base_url,
                    client=client,
                    format_schema=format_schema,
                    temperature=temperature,
                )
                elapsed = time.time() - t0

                raw_cleaned = _extract_json(raw)
                try:
                    result = json.loads(raw_cleaned)
                except json.JSONDecodeError as exc:
                    logger.warning("Failed to parse JSON for %s: %s", pid, exc)
                    result = {"_raw": raw, "_parse_error": str(exc)}

                validation_errors: list[str] = []
                if schema and "_parse_error" not in result:
                    validator = jsonschema.Draft202012Validator(schema)
                    for error in validator.iter_errors(result):
                        validation_errors.append(f"{error.json_path}: {error.message}")

                if "_parse_error" not in result:
                    result.setdefault("input", {"title": title, "abstract": abstract})

                result["_meta"] = {
                    "method": method,
                    "version": version,
                    "version_date": manifest.get("date") if manifest else None,
                    "schema_id": manifest.get("schema", {}).get("id")
                    if manifest
                    else None,
                    "model": model,
                    "backend": "vllm",
                    "batch_mode": "concurrent",
                    "concurrency": concurrency,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "elapsed_seconds": round(elapsed, 2),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "valid": len(validation_errors) == 0
                    and "_parse_error" not in result,
                    "validation_errors": validation_errors,
                }
            except Exception:
                logger.exception("Error classifying %s", pid)
                result = {
                    "paper_id": pid,
                    "_meta": {
                        "method": method,
                        "version": version,
                        "model": model,
                        "backend": "vllm",
                        "batch_mode": "concurrent",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "valid": False,
                        "error": "request_failed",
                    },
                }
            return result

    async def _run_all() -> list[dict[str, Any]]:
        sem = asyncio.Semaphore(concurrency)
        async with httpx.AsyncClient(timeout=timeout) as client:
            tasks = [
                _classify_one(paper, i, sem, client) for i, paper in enumerate(papers)
            ]
            return await asyncio.gather(*tasks)

    return asyncio.run(_run_all())


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify_paper(
    title: str,
    abstract: str,
    paper_id: str,
    *,
    method: str = "with_schema",
    version: str = "v1",
    model: str = "llama4",
    base_url: str = "http://localhost:11434",
    timeout: float = 300.0,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Classify a single paper.

    Args:
        method: ``"with_schema"`` or ``"without_schema"``.
        version: Version folder name (e.g. ``"v1"``).
        model: Ollama model name.
        base_url: Ollama server URL.
        timeout: Request timeout in seconds.
        temperature: Sampling temperature.

    Returns:
        dict with the classification result plus a ``_meta`` key containing
        method, version, model, timestamp, and validation info.
    """
    ver = load_version(version)
    schema = ver["schema"]

    if method == "with_schema":
        template = ver["prompt_with_schema"]
        system_msg, user_msg = render_prompt(
            template,
            paper_id=paper_id,
            title=title,
            abstract=abstract,
        )
        format_schema = schema
    elif method == "without_schema":
        template = ver["prompt_without_schema"]
        system_msg, user_msg = render_prompt(
            template,
            paper_id=paper_id,
            title=title,
            abstract=abstract,
        )
        format_schema = None
    else:
        raise ValueError(
            f"Unknown method: {method!r}. Use 'with_schema' or 'without_schema'."
        )

    t0 = time.time()
    raw, usage = _call_ollama(
        system_msg,
        user_msg,
        model=model,
        base_url=base_url,
        format_schema=format_schema,
        timeout=timeout,
        temperature=temperature,
    )
    elapsed = time.time() - t0

    # Parse JSON from response — strip markdown code fences and trailing text
    raw_cleaned = _extract_json(raw)

    try:
        result = json.loads(raw_cleaned)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse JSON for paper %s: %s", paper_id, exc)
        result = {"_raw": raw, "_parse_error": str(exc)}

    # Validate against schema
    validation_errors: list[str] = []
    if schema and "_parse_error" not in result:
        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(result):
            validation_errors.append(f"{error.json_path}: {error.message}")
            logger.warning("Validation error for %s: %s", paper_id, error.message)

    # Inject input fields (removed from schema to save output tokens)
    if "_parse_error" not in result:
        result.setdefault("input", {"title": title, "abstract": abstract})

    manifest = ver.get("manifest")
    result["_meta"] = {
        "method": method,
        "version": version,
        "version_date": manifest.get("date") if manifest else None,
        "schema_id": manifest.get("schema", {}).get("id") if manifest else None,
        "model": model,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(elapsed, 2),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "valid": len(validation_errors) == 0 and "_parse_error" not in result,
        "validation_errors": validation_errors,
    }

    return result


def classify_paper_vllm(
    title: str,
    abstract: str,
    paper_id: str,
    *,
    method: str = "with_schema",
    version: str = "v1",
    model: str = "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4",
    base_url: str = "http://localhost:8100",
    timeout: float = 300.0,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Classify a single paper using a vLLM backend.

    Same as ``classify_paper`` but calls the OpenAI-compatible vLLM endpoint
    with ``guided_json`` for structured output.
    """
    ver = load_version(version)
    schema = ver["schema"]

    if method == "with_schema":
        template = ver["prompt_with_schema"]
        format_schema = schema
    elif method == "without_schema":
        template = ver["prompt_without_schema"]
        format_schema = None
    else:
        raise ValueError(
            f"Unknown method: {method!r}. Use 'with_schema' or 'without_schema'."
        )

    system_msg, user_msg = render_prompt(
        template,
        paper_id=paper_id,
        title=title,
        abstract=abstract,
    )

    t0 = time.time()
    raw, usage = _call_vllm(
        system_msg,
        user_msg,
        model=model,
        base_url=base_url,
        format_schema=format_schema,
        timeout=timeout,
        temperature=temperature,
    )
    elapsed = time.time() - t0

    raw_cleaned = _extract_json(raw)

    try:
        result = json.loads(raw_cleaned)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse JSON for paper %s: %s", paper_id, exc)
        result = {"_raw": raw, "_parse_error": str(exc)}

    validation_errors: list[str] = []
    if schema and "_parse_error" not in result:
        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(result):
            validation_errors.append(f"{error.json_path}: {error.message}")
            logger.warning("Validation error for %s: %s", paper_id, error.message)

    if "_parse_error" not in result:
        result.setdefault("input", {"title": title, "abstract": abstract})

    manifest = ver.get("manifest")
    result["_meta"] = {
        "method": method,
        "version": version,
        "version_date": manifest.get("date") if manifest else None,
        "schema_id": manifest.get("schema", {}).get("id") if manifest else None,
        "model": model,
        "backend": "vllm",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(elapsed, 2),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "valid": len(validation_errors) == 0 and "_parse_error" not in result,
        "validation_errors": validation_errors,
    }

    return result


def classify_batch(
    papers: list[dict[str, str]],
    *,
    method: str = "with_schema",
    version: str = "v1",
    model: str = "llama4",
    base_url: str = "http://localhost:11434",
    timeout: float = 300.0,
    temperature: float = 0.0,
) -> Iterator[dict[str, Any]]:
    """Classify a list of papers sequentially, yielding results one at a time.

    Creates a derived Ollama model with the static system prompt baked in,
    then sends only the per-paper data for each request.

    Each item in ``papers`` must have keys: ``doc_id``, ``title``, ``abstract``.
    """
    ensure_model(model, base_url)

    # Load version data and build the derived model with baked-in system prompt
    ver = load_version(version)
    schema = ver["schema"]
    template_key = f"prompt_{method}"
    template = ver[template_key]
    if template is None:
        raise ValueError(
            f"No prompt template for method '{method}' in version '{version}'"
        )

    static_prompt, dynamic_template = split_prompt_static_dynamic(template)
    derived_name = _derived_model_name(model, version, method)
    create_ollama_model(model, derived_name, static_prompt, base_url)

    format_schema = schema if method == "with_schema" else None
    manifest = ver.get("manifest")

    total = len(papers)
    for i, paper in enumerate(papers, 1):
        pid = paper["doc_id"]
        title = paper["title"]
        abstract = paper.get("abstract", "")
        logger.info("[%d/%d] Classifying %s ...", i, total, pid)

        # Render only the dynamic per-paper content
        user_msg = dynamic_template.replace("{{paper_id}}", pid)
        user_msg = user_msg.replace("{{title}}", title)
        user_msg = user_msg.replace("{{abstract}}", abstract)

        try:
            t0 = time.time()
            raw, usage = _call_ollama(
                "",  # system prompt is baked into derived model
                user_msg,
                model=derived_name,
                base_url=base_url,
                format_schema=format_schema,
                timeout=timeout,
                temperature=temperature,
            )
            elapsed = time.time() - t0

            raw_cleaned = _extract_json(raw)
            try:
                result = json.loads(raw_cleaned)
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse JSON for paper %s: %s", pid, exc)
                result = {"_raw": raw, "_parse_error": str(exc)}

            validation_errors: list[str] = []
            if schema and "_parse_error" not in result:
                validator = jsonschema.Draft202012Validator(schema)
                for error in validator.iter_errors(result):
                    validation_errors.append(f"{error.json_path}: {error.message}")
                    logger.warning("Validation error for %s: %s", pid, error.message)

            if "_parse_error" not in result:
                result.setdefault("input", {"title": title, "abstract": abstract})

            result["_meta"] = {
                "method": method,
                "version": version,
                "version_date": manifest.get("date") if manifest else None,
                "schema_id": manifest.get("schema", {}).get("id") if manifest else None,
                "model": model,
                "derived_model": derived_name,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_seconds": round(elapsed, 2),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "valid": len(validation_errors) == 0 and "_parse_error" not in result,
                "validation_errors": validation_errors,
            }
        except Exception:
            logger.exception("Error classifying %s", pid)
            result = {
                "paper_id": pid,
                "_meta": {
                    "method": method,
                    "version": version,
                    "model": model,
                    "derived_model": derived_name,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "valid": False,
                    "error": "request_failed",
                },
            }
        yield result
