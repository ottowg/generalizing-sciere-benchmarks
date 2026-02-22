"""Centralized path resolution for the UnifiedSciERE project.

All paths are resolved relative to the project root (the directory
containing pyproject.toml / .env).  This avoids hard-coded strings
and keeps scripts independent of their own location on disk.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def project_root() -> Path:
    """Return the project root directory.

    Walks up from this file until it finds a directory containing
    ``pyproject.toml``.  The result is cached for the process lifetime.
    """
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError(
        "Could not locate project root (no pyproject.toml found above "
        f"{Path(__file__).resolve()})"
    )


# ── convenience accessors ────────────────────────────────────────────


def reports_dir(subfolder: str = "") -> Path:
    """Return the reports directory, optionally with a *subfolder*.

    Creates the directory (and parents) if it does not exist.

    >>> reports_dir("ere_performance")
    PosixPath('/…/UnifiedSciERE/reports/ere_performance')
    """
    path = project_root() / "reports"
    if subfolder:
        path = path / subfolder
    path.mkdir(parents=True, exist_ok=True)
    return path


def scripts_dir(subfolder: str = "") -> Path:
    """Return the scripts directory, optionally with a *subfolder*."""
    path = project_root() / "scripts"
    if subfolder:
        path = path / subfolder
    return path


def data_dir(subfolder: str = "") -> Path:
    """Return the data directory, optionally with a *subfolder*."""
    path = project_root() / "data"
    if subfolder:
        path = path / subfolder
    return path


def configs_dir(subfolder: str = "") -> Path:
    """Return the configs directory, optionally with a *subfolder*."""
    path = project_root() / "configs"
    if subfolder:
        path = path / subfolder
    return path


# ── output helpers ───────────────────────────────────────────────────


def ensure_output(relative_path: str | Path) -> Path:
    """Resolve *relative_path* against the project root, create parent dirs.

    Returns the absolute path so callers can immediately write to it.

    >>> p = ensure_output("reports/ere_performance/my_report.md")
    >>> p.write_text(content)
    """
    path = project_root() / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
