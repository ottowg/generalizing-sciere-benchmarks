"""Example usage of the model performance analysis module with report generation."""

from pathlib import Path

from src.unifiedsciere.analysis import (
    analyze_cross_dataset_performance,
    create_performance_table,
    generate_all_reports,
    generate_markdown_report,
    save_performance_table,
)

# Example 1: Generate all reports for SciNLP test set
print("=" * 60)
print("Example 1: Generate Complete Reports")
print("=" * 60)

output_paths = generate_all_reports(
    target_dataset="scinlp",
    split="test",
    output_dir=Path("reports"),
)

print("\nGenerated reports:")
print(f"  LaTeX table: {output_paths['latex']}")
print(f"  HTML table:  {output_paths['html']}")
print(f"  Markdown report: {output_paths['markdown']}")

# Example 2: Create and display a performance table
print("\n" + "=" * 60)
print("Example 2: Create Performance Table")
print("=" * 60)

gt_table = create_performance_table(target_dataset="gsap", split="test")
print("\nTable created successfully!")
print("You can display it in a Jupyter notebook with: gt_table")

# Example 3: Save just the LaTeX table
print("\n" + "=" * 60)
print("Example 3: Save LaTeX Table Only")
print("=" * 60)

table_paths = save_performance_table(
    target_dataset="scier",
    split="dev",
    output_dir=Path("reports"),
)

print(f"\nLaTeX table saved to: {table_paths['latex']}")
print(f"HTML table saved to: {table_paths['html']}")

# Example 4: Generate markdown report only
print("\n" + "=" * 60)
print("Example 4: Generate Markdown Report Only")
print("=" * 60)

md_path = generate_markdown_report(
    target_dataset="gsap",
    split="test",
    output_dir=Path("reports"),
)

print(f"\nMarkdown report saved to: {md_path}")

# Show a preview of the markdown content
print("\nReport preview:")
print("-" * 60)
with open(md_path) as f:
    lines = f.readlines()[:20]  # First 20 lines
    print("".join(lines))
print("...")

# Example 5: Generate reports for all datasets
print("\n" + "=" * 60)
print("Example 5: Batch Generate Reports for All Datasets")
print("=" * 60)

datasets = ["scier", "scinlp", "gsap"]

for dataset in datasets:
    print(f"\nGenerating reports for {dataset.upper()}...")
    paths = generate_all_reports(
        target_dataset=dataset,
        split="test",
        output_dir=Path("reports"),
    )
    print(f"  ✓ Reports saved to reports/ folder")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)
print("\nCheck the reports/ folder for generated files:")
print("  reports/              - HTML tables and markdown reports")
print("  reports/tables/latex/ - LaTeX tables")
