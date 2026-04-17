#!/usr/bin/env python
"""Generate combined confusion reports for all model comparisons."""

from unifiedsciere.analysis.label_confusion import (
    generate_simplified_confusion_report,
)

if __name__ == "__main__":
    # All three datasets to combine
    datasets = ["scier", "scinlp", "gsap-ere"]
    split = "dev"

    # Generate three comparison reports
    comparisons = [
        ("gsap-ere", "scinlp", "GSAP-ERE vs SCINLP"),
        ("gsap-ere", "scier", "GSAP-ERE vs SCIER"),
        ("scinlp", "scier", "SCINLP vs SCIER"),
    ]

    for model1, model2, description in comparisons:
        print(f"\nGenerating {description}...")
        try:
            report_path = generate_simplified_confusion_report(
                datasets=datasets,
                split=split,
                model1=model1,
                model2=model2,
                top_n=15,
                combine_datasets=True,
            )
            print(f"✓ Generated: {report_path}")
        except Exception as e:
            print(f"✗ Error generating {description}: {e}")
            import traceback

            print(f"✗ Error generating {description}: {e}")
            import traceback
            traceback.print_exc()

    print("\nAll reports generated!")
