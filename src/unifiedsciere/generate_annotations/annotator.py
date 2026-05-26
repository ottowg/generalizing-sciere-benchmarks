"""LLM-based sentence-level entity and relation extraction.

Supports Ollama, vLLM, and OpenAI backends. Prompts and version metadata are stored
in versions/vN/ directories alongside this module.

Entity type integers (as used in the LLM prompt and returned data):
  0 = concept
  1 = artifact

Relation type integers:
  0 = direct
  1 = indirect
  2 = coreference
"""

from __future__ import annotations

import ast
import csv
import io
import json
import logging
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from tqdm import tqdm

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

VERSIONS_DIR = Path(__file__).parent / "versions"


class ContentFilterError(RuntimeError):
    """Raised when the API rejects the prompt due to a content/safety filter.

    Retrying with the same prompt is pointless — the sentence is skipped and
    the error is recorded so it can be inspected later.
    """

ENTITY_LABEL: dict[int, str] = {0: "concept", 1: "artifact"}
RELATION_LABEL: dict[int, str] = {0: "direct", 1: "indirect", 2: "coreference"}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class AnnotationConfig:
    """Configuration for the annotation pipeline."""

    model: str = "llama4"
    base_url: str = "https://ai-openwebui.gesis.org/"
    api_key: str = "sk-4f8fb3e41fe14d3db50a224936e9e3aa"
    backend: str = "ollama"  # "ollama", "vllm", or "openai"
    version: str = "v1"
    context_window: int = 3
    temperature: float = 0.0
    timeout: float = 120.0
    max_retries: int = 2
    # Pricing for cost estimation ($ per 1M tokens); defaults match gpt-5.4
    price_input: float = 1.25
    price_cached: float = 0.13
    price_output: float = 7.50


def load_config(path: str | Path) -> AnnotationConfig:
    import yaml

    with open(path) as f:
        raw = yaml.safe_load(f)
    return AnnotationConfig(**raw)


# ---------------------------------------------------------------------------
# Version loader
# ---------------------------------------------------------------------------


def load_version(version: str) -> dict[str, Any]:
    """Load prompt text and manifest for a given version.

    Returns a dict with keys: prompt, manifest.
    """
    import yaml

    version_dir = VERSIONS_DIR / version
    if not version_dir.is_dir():
        available = [p.name for p in VERSIONS_DIR.iterdir() if p.is_dir()]
        raise FileNotFoundError(
            f"Version '{version}' not found in {VERSIONS_DIR}. Available: {available}"
        )

    manifest_path = version_dir / "version.yaml"
    manifest = (
        yaml.safe_load(manifest_path.read_text()) if manifest_path.exists() else {}
    )

    prompt_path = version_dir / "prompt.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"prompt.txt not found in {version_dir}")
    prompt = prompt_path.read_text()

    return {"prompt": prompt, "manifest": manifest}


# ---------------------------------------------------------------------------
# Token cleaning (prompt-only — never changes token count)
# ---------------------------------------------------------------------------

# Unicode categories to remove: control (Cc) and format (Cf) characters.
# These include zero-width spaces, BOM, soft hyphens, etc.
# Regular letters, digits, punctuation and symbols (including bullets, accented
# chars, CJK, etc.) are preserved so the LLM sees meaningful text.
_STRIP_CATEGORIES = frozenset({"Cc", "Cf"})


def _clean_token(tok: str) -> str:
    """Clean a token for use in the LLM prompt.

    Applies NFKC normalisation (resolves ligatures, fullwidth chars, etc.) and
    removes Unicode control/format characters.  The token identity and position
    within the sentence are unchanged — only the character content may differ.
    Never returns an empty string: falls back to the original if all characters
    would be stripped.
    """
    normalised = unicodedata.normalize("NFKC", tok)
    cleaned = "".join(
        ch for ch in normalised if unicodedata.category(ch) not in _STRIP_CATEGORIES
    )
    return cleaned if cleaned else tok


def _clean_tokens(tokens: list[str]) -> list[str]:
    return [_clean_token(t) for t in tokens]


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------


def _parse_prompt_sections(raw: str) -> tuple[str, str]:
    """Split a prompt template into (system, user) parts via [SYSTEM]/[USER] markers."""
    system, user = "", ""
    current = None
    for line in raw.splitlines(keepends=True):
        stripped = line.strip()
        if stripped == "[SYSTEM]":
            current = "system"
        elif stripped == "[USER]":
            current = "user"
        elif current == "system":
            system += line
        elif current == "user":
            user += line
    return system.strip(), user.strip()


def _format_tokens(tokens: list[str]) -> str:
    return json.dumps(tokens, ensure_ascii=False)


def render_prompt(
    prompt_template: str,
    *,
    context_sentences: list[list[str]],
    sentence_tokens: list[str],
    sentence_index_in_context: int = 0,
) -> tuple[str, str]:
    """Render the prompt template, returning (system_msg, user_msg).

    Context lines are labeled with relative indices: the target sentence is 0,
    preceding sentences are negative (-1, -2, …), following sentences are
    positive (1, 2, …).  sentence_index_in_context is the position of the
    target sentence within context_sentences.
    """
    context_str = "\n".join(
        f"  {j - sentence_index_in_context:2d}: {_format_tokens(s)}"
        for j, s in enumerate(context_sentences)
    )
    sentence_str = _format_tokens(sentence_tokens)

    filled = prompt_template.replace("{{context}}", context_str)
    filled = filled.replace("{{sentence}}", sentence_str)
    return _parse_prompt_sections(filled)


# ---------------------------------------------------------------------------
# LLM backends
# ---------------------------------------------------------------------------


def _call_ollama(
    system_msg: str,
    user_msg: str,
    config: AnnotationConfig,
) -> tuple[str, dict]:
    """Call the Ollama native API and return (content, meta)."""
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        # "x-api-key": config.api_key,
        "Content-Type": "application/json",
    }
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": config.model,
        "messages": messages,
        "stream": False,
        "temperature": config.temperature,
    }

    url = config.base_url.rstrip("/") + "/api/chat/completions"
    with httpx.Client(timeout=config.timeout) as client:
        resp = client.post(url, json=payload, headers=headers)
    if not resp.is_success:
        logger.error("HTTP %s error: %s", resp.status_code, resp.text[:1000])
        try:
            err_code = resp.json().get("error", {}).get("code", "")
        except Exception:
            err_code = ""
        exc_cls = ContentFilterError if err_code == "content_filter" else RuntimeError
        raise exc_cls(f"HTTP {resp.status_code}: {resp.text[:1000]}")
    data = resp.json()

    content = data.get("choices", [])
    if not content:
        return None, None
    content = content[0].get("message", {}).get("content", "")
    if not content:
        return None, None
    meta = {
        "usage": data.get("usage", {}),
    }
    return content, meta


def _call_vllm(
    system_msg: str,
    user_msg: str,
    config: AnnotationConfig,
) -> tuple[str, dict]:
    """Call a vLLM (OpenAI-compatible) endpoint and return (content, meta)."""
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": config.model,
        "messages": messages,
        "temperature": config.temperature,
    }

    url = config.base_url.rstrip("/") + "/v1/chat/completions"
    with httpx.Client(timeout=config.timeout) as client:
        resp = client.post(url, json=payload)
    if not resp.is_success:
        logger.error("HTTP %s error: %s", resp.status_code, resp.text[:1000])
        try:
            err_code = resp.json().get("error", {}).get("code", "")
        except Exception:
            err_code = ""
        exc_cls = ContentFilterError if err_code == "content_filter" else RuntimeError
        raise exc_cls(f"HTTP {resp.status_code}: {resp.text[:1000]}")
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    meta = {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
    }
    return content, meta


def _call_openai(
    system_msg: str,
    user_msg: str,
    config: AnnotationConfig,
) -> tuple[str, dict]:
    """Call the OpenAI API and return (content, meta)."""
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": config.model,
        "messages": messages,
        "temperature": config.temperature,
    }

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    url = config.base_url.rstrip("/") + "/v1/chat/completions"
    with httpx.Client(timeout=config.timeout) as client:
        resp = client.post(url, json=payload, headers=headers)
    if not resp.is_success:
        logger.error("HTTP %s error: %s", resp.status_code, resp.text[:1000])
        try:
            err_code = resp.json().get("error", {}).get("code", "")
        except Exception:
            err_code = ""
        exc_cls = ContentFilterError if err_code == "content_filter" else RuntimeError
        raise exc_cls(f"HTTP {resp.status_code}: {resp.text[:1000]}")
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    meta = {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "model_resolved": data.get("model"),
    }
    return content, meta


def _call_llm(
    system_msg: str,
    user_msg: str,
    config: AnnotationConfig,
) -> tuple[str, dict]:
    if config.backend == "openai":
        return _call_openai(system_msg, user_msg, config)
    if config.backend == "vllm":
        return _call_vllm(system_msg, user_msg, config)
    return _call_ollama(system_msg, user_msg, config)


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

_ASSIGN_RE = re.compile(r"(entities|relations)\s*=\s*\[", re.MULTILINE)


def _extract_list_block(raw: str, start: int) -> str | None:
    """Extract a balanced [...] block starting at position start (pointing to '[')."""
    depth = 0
    i = start
    while i < len(raw):
        ch = raw[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
        elif ch in ('"', "'"):
            # Skip string literals
            quote = ch
            i += 1
            while i < len(raw):
                if raw[i] == "\\":
                    i += 1
                elif raw[i] == quote:
                    break
                i += 1
        i += 1
    return None


def _parse_result_v1(raw: str) -> tuple[list, list, list[str]]:
    """Parse Python-style entities and relations from LLM output (v1 format)."""
    entities: list = []
    relations: list = []
    errors: list[str] = []

    blocks: dict[str, str] = {}
    for m in _ASSIGN_RE.finditer(raw):
        name = m.group(1)
        block_start = m.end() - 1
        block = _extract_list_block(raw, block_start)
        if block is not None:
            blocks[name] = block

    for name, default in [("entities", "[]"), ("relations", "[]")]:
        src = blocks.get(name, default)
        try:
            parsed = ast.literal_eval(src)
            if not isinstance(parsed, list):
                errors.append(f"{name}: expected list, got {type(parsed).__name__}")
                parsed = []
        except (ValueError, SyntaxError) as exc:
            errors.append(f"{name}: parse error — {exc}")
            parsed = []
        if name == "entities":
            entities = parsed
        else:
            relations = parsed

    return entities, relations, errors


def _parse_csv_section(lines: list[str], n_fields: int, section: str, errors: list[str]) -> list[list]:
    """Parse tab-separated CSV rows from a section, returning parsed rows."""
    rows = []
    for line in lines:
        try:
            row = next(csv.reader(io.StringIO(line), delimiter="\t"))
        except StopIteration:
            continue
        if len(row) != n_fields:
            errors.append(f"{section}: expected {n_fields} fields, got {len(row)}: {line!r}")
            continue
        rows.append(row)
    return rows


def _parse_result_v2(raw: str) -> tuple[list, list, list[str]]:
    """Parse tab-separated CSV entities and relations from LLM output (v2 format).

    entities section:   <token_list_json>\\t<entity_type_int>
    relations section:  <subj_list_json>\\t<obj_list_json>\\t<relation_type_int>

    Relation subject/object types are resolved from the entities section.
    Relations referencing a span not in entities are skipped with an error.
    Standard CSV quoting (RFC 4180) handles embedded tabs or double-quotes.
    """
    entities: list = []
    relations: list = []
    errors: list[str] = []

    # Split output into named sections
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped in ("entities:", "relations:"):
            current = stripped[:-1]
            sections.setdefault(current, [])
        elif current is not None and stripped:
            sections[current].append(line)

    # Parse entities
    for row in _parse_csv_section(sections.get("entities", []), 2, "entities", errors):
        try:
            tokens = json.loads(row[0])
            type_int = int(row[1])
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"entities: parse error — {exc} in {row!r}")
            continue
        if not isinstance(tokens, list):
            errors.append(f"entities: token list expected, got {type(tokens).__name__}")
            continue
        entities.append((tokens, type_int))

    # Build token-list → type lookup for relation resolution
    entity_type_map: dict[tuple, int] = {tuple(t): typ for t, typ in entities}

    # Parse relations
    for row in _parse_csv_section(sections.get("relations", []), 3, "relations", errors):
        try:
            subj_tokens = json.loads(row[0])
            obj_tokens  = json.loads(row[1])
            rel_type    = int(row[2])
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"relations: parse error — {exc} in {row!r}")
            continue
        if not isinstance(subj_tokens, list) or not isinstance(obj_tokens, list):
            errors.append(f"relations: token lists expected in {row!r}")
            continue
        subj_type = entity_type_map.get(tuple(subj_tokens))
        obj_type  = entity_type_map.get(tuple(obj_tokens))
        if subj_type is None:
            errors.append(f"relations: subject not in entities: {subj_tokens!r}")
            continue
        if obj_type is None:
            errors.append(f"relations: object not in entities: {obj_tokens!r}")
            continue
        relations.append(((subj_tokens, subj_type), (obj_tokens, obj_type), rel_type))

    return entities, relations, errors


def _parse_result(raw: str, version: str = "v1") -> tuple[list, list, list[str]]:
    if version in ("v2", "v3"):
        return _parse_result_v2(raw)
    return _parse_result_v1(raw)


def _find_span_indices(
    sentence_tokens: list[str], span_tokens: list[str]
) -> tuple[int, int] | None:
    """Find the first occurrence of span_tokens as a contiguous subsequence.

    Returns (begin_token_idx, end_token_idx) or None.
    """
    n = len(span_tokens)
    for i in range(len(sentence_tokens) - n + 1):
        if sentence_tokens[i : i + n] == span_tokens:
            return i, i + n - 1
    return None


# ---------------------------------------------------------------------------
# Public annotation API
# ---------------------------------------------------------------------------


def process_sentence_output(
    raw: str,
    sentence_tokens: list[str],
    version: str,
) -> dict:
    """Parse LLM output and resolve entity/relation spans to token indices.

    sentence_tokens must be the original (uncleaned) tokens — cleaning is applied
    internally to match how the prompt was rendered.

    Returns a dict with: entities, relations, ner_indices, rel_indices, raw, errors.
    Does not include meta (timing/model info); add that at the call site.
    """
    prompt_sentence = _clean_tokens(sentence_tokens)
    entities, relations, errors = _parse_result(raw, version=version)

    ner_indices: list[tuple[int, int, str]] = []
    span_to_indices: dict[tuple, tuple[int, int]] = {}

    for ent in entities:
        if not (isinstance(ent, (list, tuple)) and len(ent) == 2):
            errors.append(f"malformed entity: {ent!r}")
            continue
        span_tokens, type_int = ent
        if not isinstance(span_tokens, list) or not isinstance(type_int, int):
            errors.append(f"malformed entity: {ent!r}")
            continue
        label = ENTITY_LABEL.get(type_int, f"type_{type_int}")
        indices = _find_span_indices(prompt_sentence, span_tokens)
        if indices is None:
            errors.append(f"span not found in sentence: {span_tokens!r}")
            continue
        begin, end = indices
        orig_slice = sentence_tokens[begin : end + 1]
        cleaned_orig = _clean_tokens(orig_slice)
        if cleaned_orig != span_tokens:
            errors.append(
                f"index mismatch after cleaning: span={span_tokens!r} "
                f"orig={orig_slice!r} cleaned={cleaned_orig!r} at [{begin}:{end+1}]"
            )
            continue
        ner_indices.append((begin, end, label))
        span_to_indices[tuple(span_tokens)] = (begin, end)

    rel_indices: list[tuple[int, int, str, int, int, str, str]] = []
    for rel in relations:
        if not (isinstance(rel, (list, tuple)) and len(rel) == 3):
            errors.append(f"malformed relation: {rel!r}")
            continue
        subj, obj, type_int = rel
        if not (
            isinstance(subj, (list, tuple))
            and len(subj) == 2
            and isinstance(obj, (list, tuple))
            and len(obj) == 2
        ):
            errors.append(f"malformed relation entity tuple: {rel!r}")
            continue
        subj_span, subj_type = subj
        obj_span, obj_type = obj
        if not isinstance(subj_span, list) or not isinstance(obj_span, list):
            errors.append(f"malformed relation span: {rel!r}")
            continue
        rel_label = RELATION_LABEL.get(type_int, f"rel_{type_int}")
        subj_lbl = ENTITY_LABEL.get(subj_type, f"type_{subj_type}")
        obj_lbl = ENTITY_LABEL.get(obj_type, f"type_{obj_type}")
        subj_idx = span_to_indices.get(tuple(subj_span))
        obj_idx = span_to_indices.get(tuple(obj_span))
        if subj_idx is None or obj_idx is None:
            errors.append(
                f"relation references unknown span: {subj_span!r} or {obj_span!r}"
            )
            continue
        rel_indices.append((
            subj_idx[0], subj_idx[1], subj_lbl,
            obj_idx[0], obj_idx[1], obj_lbl,
            rel_label,
        ))

    return {
        "entities": entities,
        "relations": relations,
        "ner_indices": ner_indices,
        "rel_indices": rel_indices,
        "raw": raw,
        "errors": errors,
    }


def annotate_sentence(
    sentence_tokens: list[str],
    context_sentences: list[list[str]],
    config: AnnotationConfig,
    prompt_template: str,
    sentence_index_in_context: int = 0,
) -> dict:
    """Annotate a single sentence.

    Returns a dict with:
      entities     — list of (span_tokens, type_int)
      relations    — list of (subj_tuple, obj_tuple, type_int)
      ner_indices  — list of (begin_token, end_token, label_str)
      rel_indices  — list of (sb, se, sl, ob, oe, ol, rel_label)
      raw          — raw LLM output string
      meta         — timing/token metadata
      errors       — list of parse/validation error strings
    """
    t0 = time.time()

    prompt_sentence = _clean_tokens(sentence_tokens)
    prompt_context  = [_clean_tokens(s) for s in context_sentences]

    system_msg, user_msg = render_prompt(
        prompt_template,
        context_sentences=prompt_context,
        sentence_tokens=prompt_sentence,
        sentence_index_in_context=sentence_index_in_context,
    )

    raw = ""
    llm_meta: dict = {}
    llm_errors: list[str] = []

    for attempt in range(1, config.max_retries + 2):
        try:
            raw, llm_meta = _call_llm(system_msg, user_msg, config)
            break
        except ContentFilterError as exc:
            llm_errors.append(f"content_filter: {exc}")
            logger.warning(
                "Content filter triggered for sentence: %s — skipping retries",
                sentence_tokens[:5],
            )
            break
        except Exception as exc:
            llm_errors.append(f"attempt {attempt}: {exc}")
            logger.warning("LLM attempt %d failed: %s", attempt, exc)
            if attempt > config.max_retries:
                logger.warning(
                    "All LLM attempts failed for sentence: %s", sentence_tokens[:5]
                )

    result = process_sentence_output(raw, sentence_tokens, config.version)
    elapsed = time.time() - t0

    return {
        **result,
        "meta": {
            **llm_meta,
            "elapsed_seconds": round(elapsed, 3),
            "backend": config.backend,
            "model": config.model,
            "version": config.version,
        },
        "errors": result["errors"] + llm_errors,
    }


def annotate_document(
    sentences: list[list[str]],
    config: AnnotationConfig,
    prompt_template: str,
) -> list[dict]:
    """Annotate all sentences in a document with context windows.

    For each sentence at index i, the context passed to the prompt is
    [i - context_window … i … i + context_window], i.e. the sentence
    itself is included in context_sentences so the model sees it both as
    the surrounding context and as the explicit annotation target.
    """
    results = []
    cw = config.context_window
    for i, sent_tokens in enumerate(tqdm(sentences)):
        before = sentences[max(0, i - cw) : i]
        after = sentences[i : i + 1 + cw]
        context = before + after
        result = annotate_sentence(
            sent_tokens, context, config, prompt_template,
            sentence_index_in_context=len(before),
        )
        results.append(result)
    return results
