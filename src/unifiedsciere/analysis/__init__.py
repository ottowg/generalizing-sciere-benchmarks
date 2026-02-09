"""Analysis module for UnifiedSciERE."""

from .model_performance import (
    analyze_cross_dataset_performance,
    compare_models,
    create_performance_table,
    evaluate_model_performance,
    generate_all_reports,
    generate_comprehensive_report,
    generate_markdown_report,
    print_performance_summary,
    save_performance_table,
)
from .unification_performance import (
    evaluate_unified_performance,
    generate_unification_report,
)

__all__ = [
    "evaluate_model_performance",
    "compare_models",
    "print_performance_summary",
    "analyze_cross_dataset_performance",
    "create_performance_table",
    "save_performance_table",
    "generate_markdown_report",
    "generate_all_reports",
    "generate_comprehensive_report",
    "generate_unification_report",
    "evaluate_unified_performance",
]
