"""Markdown report builder for UnifiedSciERE scripts.

Provides a lightweight :class:`MarkdownReport` that accumulates sections
and writes them to disk with consistent formatting.

Typical usage::

    from unifiedsciere.reporting import MarkdownReport

    report = MarkdownReport("Entity Performance Overview")
    report.text("Split: test")
    report.heading("Results", level=2)
    report.table(df)
    report.write("reports/ere_performance/entity_overview.md")
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .paths import ensure_output


class MarkdownReport:
    """Accumulates markdown content and writes it to a file.

    Parameters
    ----------
    title : str
        Top-level ``# Title`` for the report.
    timestamp : bool
        If *True* (default), a **Generated:** line is added after the title.
    """

    def __init__(self, title: str, *, timestamp: bool = True) -> None:
        self._parts: list[str] = []
        self._parts.append(f"# {title}")
        self._parts.append("")
        if timestamp:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._parts.append(f"**Generated:** {ts}")
            self._parts.append("")

    # ── content helpers ──────────────────────────────────────────────

    def heading(self, text: str, level: int = 2) -> "MarkdownReport":
        """Append a heading (``## …`` by default)."""
        prefix = "#" * level
        self._parts.append(f"{prefix} {text}")
        self._parts.append("")
        return self

    def text(self, content: str) -> "MarkdownReport":
        """Append a block of text (or any raw markdown)."""
        self._parts.append(content)
        self._parts.append("")
        return self

    def table(self, df: pd.DataFrame, *, index: bool = False) -> "MarkdownReport":
        """Append a pandas DataFrame as a markdown table."""
        self._parts.append(df.to_markdown(index=index))
        self._parts.append("")
        return self

    def bullet_list(self, items: list[str]) -> "MarkdownReport":
        """Append a bullet list."""
        for item in items:
            self._parts.append(f"- {item}")
        self._parts.append("")
        return self

    def separator(self) -> "MarkdownReport":
        """Append a horizontal rule."""
        self._parts.append("---")
        self._parts.append("")
        return self

    # ── output ───────────────────────────────────────────────────────

    def build(self) -> str:
        """Return the accumulated markdown as a single string."""
        return "\n".join(self._parts)

    def write(self, relative_path: str | Path) -> Path:
        """Write the report to *relative_path* (resolved via project root).

        Creates parent directories if needed and prints a status line.

        Returns
        -------
        Path
            Absolute path of the written file.
        """
        output = ensure_output(relative_path)
        output.write_text(self.build())
        print(f"Report written to: {output}")
        return output
