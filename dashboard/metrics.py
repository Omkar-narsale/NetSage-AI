"""
Dashboard Metrics Helper Module for NetSage AI (Phase 7).
Formats summary KPI statistics for Overview and Evaluation pages.
"""

from typing import Dict, Any
from evaluation.metrics import (
    calculate_ai_accuracy,
    calculate_average_confidence,
    calculate_review_metrics,
    calculate_fusion_metrics,
    calculate_high_confidence_errors
)


def get_dashboard_kpis(dataset: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Computes all primary KPI values for the NetSage AI dashboard Overview page."""
    accuracy_pct, correct_count, ai_total = calculate_ai_accuracy(dataset)
    avg_conf = calculate_average_confidence(dataset)
    review_metrics = calculate_review_metrics(dataset)
    fusion_metrics = calculate_fusion_metrics(dataset)
    high_conf_errors = calculate_high_confidence_errors(dataset)

    total_cases = len(dataset)
    human_reviewed = review_metrics["reviewed_total"]
    ai_agreement_pct = review_metrics["acceptance_rate_pct"]
    ai_corrections = review_metrics["edited_count"] + review_metrics["rejected_count"]
    high_conf_conflicts = len(high_conf_errors)

    return {
        "total_cases": total_cases,
        "ai_diagnoses_count": ai_total,
        "human_reviewed_count": human_reviewed,
        "ai_accuracy_pct": accuracy_pct,
        "average_confidence": avg_conf,
        "ai_agreement_pct": ai_agreement_pct,
        "ai_corrections_count": ai_corrections,
        "high_confidence_conflicts_count": high_conf_conflicts,
        "review_metrics": review_metrics,
        "fusion_metrics": fusion_metrics
    }
