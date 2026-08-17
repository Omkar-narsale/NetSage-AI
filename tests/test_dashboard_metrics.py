"""
Unit Test Suite for NetSage AI Phase 7 Dashboard Metrics.
Tests metric calculation functions, zero-divide safety, and missing data handling.
"""

import unittest
from evaluation.metrics import (
    calculate_ai_accuracy,
    calculate_average_confidence,
    calculate_review_metrics,
    calculate_fusion_metrics,
    calculate_concept_distribution,
    calculate_severity_distribution,
    calculate_high_confidence_errors,
    load_all_data
)


class TestDashboardMetrics(unittest.TestCase):
    """Test suite for Phase 7 Dashboard metrics calculations."""

    def setUp(self):
        self.sample_dataset = {
            "CASE-001": {
                "case_id": "CASE-001",
                "concept": "VLAN",
                "severity": "Medium",
                "expected_fault": "VLAN 30 missing",
                "ai_diagnosis": {
                    "root_cause": "VLAN 30 missing on switch",
                    "confidence": 0.90
                },
                "fusion": {"agreement_status": "AGREE"},
                "review_record": {"reviewer_decision": "ACCEPT"}
            },
            "CASE-002": {
                "case_id": "CASE-002",
                "concept": "Routing",
                "severity": "High",
                "expected_fault": "Missing default route",
                "ai_diagnosis": {
                    "root_cause": "DNS configuration error",
                    "confidence": 0.85
                },
                "fusion": {"agreement_status": "CONFLICT"},
                "review_record": {
                    "reviewer_decision": "EDIT",
                    "reviewer_correction": "Corrected to missing default route",
                    "correction_reason": "AI diagnosed DNS issue instead of route",
                    "final_diagnosis": {"root_cause": "Missing default route"}
                }
            },
            "CASE-003": {
                "case_id": "CASE-003",
                "concept": "VLAN",
                "severity": "Low",
                "expected_fault": "Trunk native VLAN mismatch",
                "ai_diagnosis": None,
                "fusion": None,
                "review_record": None
            }
        }

    def test_calculate_ai_accuracy(self):
        acc, correct, total = calculate_ai_accuracy(self.sample_dataset)
        self.assertEqual(total, 2)
        self.assertEqual(correct, 1)
        self.assertEqual(acc, 50.0)

    def test_calculate_average_confidence(self):
        avg_conf = calculate_average_confidence(self.sample_dataset)
        self.assertEqual(avg_conf, 0.88)

    def test_calculate_review_metrics(self):
        metrics = calculate_review_metrics(self.sample_dataset)
        self.assertEqual(metrics["reviewed_total"], 2)
        self.assertEqual(metrics["accepted_count"], 1)
        self.assertEqual(metrics["edited_count"], 1)
        self.assertEqual(metrics["pending_count"], 1)
        self.assertEqual(metrics["acceptance_rate_pct"], 50.0)
        self.assertEqual(metrics["correction_rate_pct"], 50.0)

    def test_calculate_fusion_metrics(self):
        fusion = calculate_fusion_metrics(self.sample_dataset)
        self.assertEqual(fusion["total_fusion_cases"], 2)
        self.assertEqual(fusion["counts"]["AGREE"], 1)
        self.assertEqual(fusion["counts"]["CONFLICT"], 1)

    def test_calculate_concept_distribution(self):
        dist = calculate_concept_distribution(self.sample_dataset)
        self.assertEqual(dist["VLAN"], 2)
        self.assertEqual(dist["Routing"], 1)

    def test_calculate_severity_distribution(self):
        dist = calculate_severity_distribution(self.sample_dataset)
        self.assertEqual(dist["Medium"], 1)
        self.assertEqual(dist["High"], 1)
        self.assertEqual(dist["Low"], 1)

    def test_calculate_high_confidence_errors(self):
        errors = calculate_high_confidence_errors(self.sample_dataset)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["case_id"], "CASE-002")
        self.assertEqual(errors[0]["confidence"], 0.85)
        self.assertEqual(errors[0]["reviewer_decision"], "EDIT")

    def test_zero_review_handling(self):
        empty_data = {}
        metrics = calculate_review_metrics(empty_data)
        self.assertEqual(metrics["reviewed_total"], 0)
        self.assertEqual(metrics["acceptance_rate_pct"], 0.0)
        self.assertEqual(metrics["correction_rate_pct"], 0.0)

    def test_missing_ai_result_handling(self):
        no_ai_data = {
            "CASE-001": {
                "case_id": "CASE-001",
                "expected_fault": "Fault",
                "ai_diagnosis": None
            }
        }
        acc, correct, total = calculate_ai_accuracy(no_ai_data)
        self.assertEqual(total, 0)
        self.assertEqual(acc, 0.0)
        avg_conf = calculate_average_confidence(no_ai_data)
        self.assertEqual(avg_conf, 0.0)


if __name__ == "__main__":
    unittest.main()
