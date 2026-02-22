"""UnifiedSciERE: Unified Scientific Entity and Relation Extraction corpus.

This package provides tools for working with the unified SciERE corpus, which
combines annotations from GSAP, SciER, and SciNLP datasets.
"""

__version__ = "0.1.0"

# Import key types for convenience
from unifiedsciere.types import (
    Corpus,
    Mention,
    Outlet,
    PaperMetadata,
    Relation,
    RepositoryLink,
    Sentence,
)

__all__ = [
    "Corpus",
    "Mention",
    "Outlet",
    "PaperMetadata",
    "Relation",
    "RepositoryLink",
    "Sentence",
]
