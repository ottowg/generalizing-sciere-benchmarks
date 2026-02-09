#!/usr/bin/env python
"""Generate mention merging report for all datasets."""

from src.unifiedsciere.unification import generate_merge_report

if __name__ == "__main__":
    print("Generating mention merge report...")

    report_path = generate_merge_report(
        datasets=["scier", "scinlp", "gsap"],
        split="dev",
        models=["scier", "scinlp", "gsap"],
        prefer_larger=True,
    )

    print(f"✓ Generated: {report_path}")
