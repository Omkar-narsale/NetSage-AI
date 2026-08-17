"""
Unit Test Suite for NetSage AI Human Review & Responsible AI Logging (Phase 6).
Tests ACCEPT, EDIT, REJECT workflows, validation constraints, and audit logging.
"""

import os
import shutil
import tempfile
import unittest
from review.review_models import ReviewRecord, ReviewDecision, ReviewState, ReviewValidationError
from review.review_store import ReviewStore
from review.review_manager import ReviewManager


class TestHumanReview(unittest.TestCase):
    """Test suite for Phase 6 Human Review Workflow & Responsible AI Logging."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.jsonl_path = os.path.join(self.temp_dir, "test_reviews.jsonl")
        self.csv_path = os.path.join(self.temp_dir, "test_responsible_ai_log.csv")
        self.store = ReviewStore(jsonl_path=self.jsonl_path, csv_log_path=self.csv_path)
        self.manager = ReviewManager(store=self.store)

        self.sample_ai_diagnosis = {
            "root_cause": "VLAN 30 missing on switch",
            "confidence": 0.90,
            "osi_layer": "Layer 2 - Data Link",
            "evidence": ["show vlan brief lacks 30"],
            "next_command": ["show vlan brief"],
            "fix_steps": ["vlan 30"]
        }
        self.sample_rule_results = [{"rule_id": "VLAN-001", "status": "FAIL", "message": "VLAN 30 missing"}]
        self.sample_fusion = {"agreement_status": "AGREE", "conflict_detected": False}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_1_accept_valid_review(self):
        rec = self.manager.process_review(
            case_id="TEST-001",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.ACCEPT
        )
        self.assertEqual(rec.reviewer_decision, ReviewDecision.ACCEPT)
        self.assertEqual(rec.review_state, ReviewState.ACCEPTED)
        self.assertEqual(rec.final_diagnosis["root_cause"], "VLAN 30 missing on switch")

        saved = self.store.get_review("TEST-001")
        self.assertIsNotNone(saved)
        self.assertEqual(saved.reviewer_decision, ReviewDecision.ACCEPT)

    def test_2_edit_valid_review(self):
        edited_final = {
            "root_cause": "VLAN 30 created but not assigned to access port Fa0/5",
            "confidence": 1.0,
            "osi_layer": "Layer 2 - Data Link",
            "evidence": ["Fa0/5 listed under VLAN 1 default"],
            "next_command": ["show interfaces fa0/5 switchport"],
            "fix_steps": ["interface fa0/5", "switchport access vlan 30"]
        }
        rec = self.manager.process_review(
            case_id="TEST-002",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.EDIT,
            final_diagnosis=edited_final,
            correction_reason="AI missed port assignment detail",
            reviewer_correction="Corrected VLAN assignment to access port Fa0/5"
        )
        self.assertEqual(rec.reviewer_decision, ReviewDecision.EDIT)
        self.assertEqual(rec.review_state, ReviewState.EDITED)
        self.assertEqual(rec.final_diagnosis["root_cause"], "VLAN 30 created but not assigned to access port Fa0/5")

    def test_3_reject_valid_review(self):
        rejected_final = {
            "root_cause": "Trunk native VLAN mismatch on link Gi0/1",
            "confidence": 1.0,
            "osi_layer": "Layer 2 - Data Link",
            "evidence": ["Native VLAN mismatch warning on Gi0/1"],
            "next_command": ["show interfaces trunk"],
            "fix_steps": ["switchport trunk native vlan 99"]
        }
        rec = self.manager.process_review(
            case_id="TEST-003",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.REJECT,
            final_diagnosis=rejected_final,
            correction_reason="AI diagnosed missing VLAN, but the issue is a native VLAN mismatch",
            reviewer_correction="Rejected AI diagnosis; corrected to native VLAN mismatch"
        )
        self.assertEqual(rec.reviewer_decision, ReviewDecision.REJECT)
        self.assertEqual(rec.review_state, ReviewState.REJECTED)

    def test_4_edit_without_correction_reason_fails(self):
        edited_final = dict(self.sample_ai_diagnosis)
        with self.assertRaises(ReviewValidationError):
            self.manager.process_review(
                case_id="TEST-004",
                ai_diagnosis=self.sample_ai_diagnosis,
                rule_results=self.sample_rule_results,
                fusion_result=self.sample_fusion,
                decision=ReviewDecision.EDIT,
                final_diagnosis=edited_final,
                correction_reason=""
            )

    def test_5_reject_without_final_diagnosis_fails(self):
        with self.assertRaises(ReviewValidationError):
            self.manager.process_review(
                case_id="TEST-005",
                ai_diagnosis=self.sample_ai_diagnosis,
                rule_results=self.sample_rule_results,
                fusion_result=self.sample_fusion,
                decision=ReviewDecision.REJECT,
                final_diagnosis=None,
                correction_reason="Wrong diagnosis"
            )

    def test_6_invalid_decision_fails(self):
        with self.assertRaises(ReviewValidationError):
            self.manager.process_review(
                case_id="TEST-006",
                ai_diagnosis=self.sample_ai_diagnosis,
                rule_results=self.sample_rule_results,
                fusion_result=self.sample_fusion,
                decision="APPROVE"
            )

    def test_7_ai_diagnosis_remains_unchanged_after_edit(self):
        edited_final = {
            "root_cause": "Edited Root Cause Description",
            "confidence": 1.0,
            "osi_layer": "Layer 2",
            "evidence": [],
            "next_command": [],
            "fix_steps": []
        }
        rec = self.manager.process_review(
            case_id="TEST-007",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.EDIT,
            final_diagnosis=edited_final,
            correction_reason="Root cause modification"
        )
        self.assertNotEqual(rec.ai_diagnosis["root_cause"], rec.final_diagnosis["root_cause"])
        self.assertEqual(rec.ai_diagnosis["root_cause"], "VLAN 30 missing on switch")
        self.assertEqual(rec.final_diagnosis["root_cause"], "Edited Root Cause Description")

    def test_8_responsible_ai_log_only_includes_edits_and_rejects(self):
        # 1. ACCEPT case -> Should NOT enter responsible AI log CSV
        self.manager.process_review(
            case_id="TEST-ACC",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.ACCEPT
        )

        # 2. EDIT case -> Should enter log CSV
        edited_final = dict(self.sample_ai_diagnosis)
        edited_final["root_cause"] = "Edited cause"
        self.manager.process_review(
            case_id="TEST-EDT",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.EDIT,
            final_diagnosis=edited_final,
            correction_reason="Reason for edit"
        )

        # 3. REJECT case -> Should enter log CSV
        rejected_final = dict(self.sample_ai_diagnosis)
        rejected_final["root_cause"] = "Rejected cause"
        self.manager.process_review(
            case_id="TEST-REJ",
            ai_diagnosis=self.sample_ai_diagnosis,
            rule_results=self.sample_rule_results,
            fusion_result=self.sample_fusion,
            decision=ReviewDecision.REJECT,
            final_diagnosis=rejected_final,
            correction_reason="Reason for reject"
        )

        log_entries = self.store.get_responsible_ai_log_entries()
        logged_case_ids = [entry["case_id"] for entry in log_entries]

        self.assertNotIn("TEST-ACC", logged_case_ids)
        self.assertIn("TEST-EDT", logged_case_ids)
        self.assertIn("TEST-REJ", logged_case_ids)
        self.assertEqual(len(log_entries), 2)


if __name__ == "__main__":
    unittest.main()
