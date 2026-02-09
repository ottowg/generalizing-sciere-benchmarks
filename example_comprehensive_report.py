"""Example script demonstrating how to generate a comprehensive performance report."""

from src.unifiedsciere.analysis.model_performance import generate_comprehensive_report

# Generate a comprehensive report across all datasets, splits, and models
print("Generating comprehensive performance report...")
report_path = generate_comprehensive_report()

print(f"\nReport generated: {report_path}")
print("\nThe report includes:")
print("  - Entity (Mention) Extraction Performance table")
print("  - Relation Extraction Performance table")
print("  - All datasets (SCIER, SCINLP, GSAP)")
print("  - All splits (train, dev, test)")
print("  - All models (SCIER, SCINLP, GSAP)")
