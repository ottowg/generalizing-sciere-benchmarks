#!/usr/bin/env python
"""Generate simplified confusion report for GSAP vs SCIER."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import directly from the module to avoid __init__.py
import importlib.util

spec = importlib.util.spec_from_file_location(
    "label_confusion",
    Path(__file__).parent.parent
    / "src"
    / "unifiedsciere"
    / "analysis"
    / "label_confusion.py",
)
label_confusion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(label_confusion)

generate_simplified_confusion_report = (
    label_confusion.generate_simplified_confusion_report
)

if __name__ == "__main__":
    report_path = generate_simplified_confusion_report(
        datasets=["gsap"],
        split="dev",
        model1="gsap",
        model2="scier",
        top_n=15,
    )
    print(f"Generated report: {report_path}")
