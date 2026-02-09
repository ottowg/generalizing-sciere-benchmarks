"""Test script to verify evaluation functions work with real data."""

from src.unifiedsciere.analysis.model_performance import (
    generate_all_reports,
    print_performance_summary,
)

# Test with a single model evaluation
print("Testing evaluation function with SciNLP test set...")
print_performance_summary("scinlp", "test", "gsap")

# Generate comprehensive reports
print("\nGenerating comprehensive reports...")
report_paths = generate_all_reports("scinlp", "test")

print("\nGenerated reports:")
for report_type, path in report_paths.items():
    print(f"  {report_type}: {path}")

print("\nEvaluation test completed successfully!")
