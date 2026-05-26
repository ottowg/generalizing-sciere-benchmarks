"""Load paper data and compute SPECTER2 embeddings."""

import json
import logging
from pathlib import Path

import numpy as np
import torch
from adapters import AutoAdapterModel
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


def load_papers(data_path: str | Path) -> list[dict]:
    """Load papers from JSONL file. Expects fields: doc_id, title, abstract, dataset."""
    papers = []
    with open(data_path) as f:
        for line in f:
            rec = json.loads(line)
            papers.append(
                {
                    "doc_id": rec["doc_id"],
                    "title": rec.get("title", ""),
                    "abstract": rec.get("abstract", ""),
                    "label": rec.get("dataset", "unknown"),
                }
            )
            if rec.get("abstract") is None:
                logger.warning(f'Paper {rec["doc_id"]} %s has no abstract')
    logger.info("Loaded %d papers from %s", len(papers), data_path)
    empty_abs = sum(1 for p in papers if not p["abstract"])
    if empty_abs:
        logger.warning(
            "%d papers have empty abstracts (will embed title only)", empty_abs
        )
    return papers


def compute_embeddings(
    papers: list[dict],
    model_name: str = "allenai/specter2_base",
    adapter_name: str = "allenai/specter2",
    batch_size: int = 32,
) -> np.ndarray:
    """Compute SPECTER2 CLS embeddings for papers.

    Returns array of shape (N, D) in the same order as papers.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoAdapterModel.from_pretrained(model_name)
    model.load_adapter(adapter_name, source="hf", set_active=True)
    model.eval()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    logger.info("Using device: %s", device)

    sep = tokenizer.sep_token or "[SEP]"
    texts = []
    for p in papers:
        if p["abstract"]:
            texts.append(f"{p['title']}{sep}{p['abstract']}")
        else:
            texts.append(p["title"])

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        cls_emb = outputs.last_hidden_state[:, 0, :]
        all_embeddings.append(cls_emb.cpu().numpy())
        logger.info(
            "Embedded batch %d/%d",
            i // batch_size + 1,
            (len(texts) + batch_size - 1) // batch_size,
        )

    embeddings = np.concatenate(all_embeddings, axis=0)
    logger.info("Embedding matrix shape: %s", embeddings.shape)
    return embeddings


def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """L2-normalize each embedding vector."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-10, None)
    normalized = embeddings / norms
    logger.info(
        "Norms after normalization: min=%.6f, max=%.6f",
        np.linalg.norm(normalized, axis=1).min(),
        np.linalg.norm(normalized, axis=1).max(),
    )
    return normalized


def save_embeddings(
    embeddings: np.ndarray,
    doc_ids: list[str],
    out_dir: Path,
) -> None:
    """Save embeddings as doc_id-keyed JSON (each doc_id -> embedding vector)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    emb_dict = {doc_id: emb.tolist() for doc_id, emb in zip(doc_ids, embeddings)}
    path = out_dir / "embeddings.json"
    with open(path, "w") as f:
        json.dump(emb_dict, f)
    logger.info("Saved %d embeddings to %s", len(emb_dict), path)


def load_cached_embeddings(
    out_dir: Path,
    doc_ids: list[str],
) -> np.ndarray | None:
    """Load cached embeddings, embedding only missing papers incrementally.

    If the cache covers all doc_ids, returns the full array immediately.
    If the cache is missing some doc_ids, computes embeddings only for those,
    merges them into the cache, saves the updated cache, and returns the full array.
    Returns None only if the cache file does not exist.
    """
    path = out_dir / "embeddings.json"
    if not path.exists():
        return None
    with open(path) as f:
        emb_dict: dict[str, list[float]] = json.load(f)

    missing = [did for did in doc_ids if did not in emb_dict]
    extra = [did for did in emb_dict if did not in set(doc_ids)]

    if extra:
        logger.info("Cache has %d stale doc_ids (will be dropped)", len(extra))

    if missing:
        logger.info(
            "%d new doc_ids not in cache — embedding only those: %s",
            len(missing),
            missing,
        )
        return None  # signal to caller to embed missing papers and merge

    # Full cache hit
    embeddings = np.array([emb_dict[did] for did in doc_ids])
    logger.info("Loaded cached embeddings: shape=%s", embeddings.shape)
    return embeddings


def load_cached_embedding_dict(out_dir: Path) -> dict[str, list[float]]:
    """Return the raw cache dict (doc_id -> vector), or {} if not found."""
    path = out_dir / "embeddings.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)
