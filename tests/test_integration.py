"""
Unit Test Suite for NetSage AI Phase 5 Integration & Evidence Fusion.
Tests agreement categories: AGREE, PARTIAL_AGREE, CONFLICT, and INSUFFICIENT_EVIDENCE.
"""

import unittest
from ai.schemas import DiagnosisResult
from integration.evidence_fusion import EvidenceFusion, AgreementStatus, FusionAnalysis
from integration.diagnosis_pipeline import DiagnosisPipeline, IntegratedDiagnosisResult


class TestEvidenceFusion(unittest.TestCase):
    """Test suite for EvidenceFusion module logic."""

    def test_fusion_agree(self):
        rule_results = [
            {"rule_id": "VLAN-001", "status": "FAIL", "message": "Required VLAN 30 is missing."}
        ]
        ai_diag = DiagnosisResult(
            root_cause="Missing VLAN 30 on switch",
            confidence=0.92,
            osi_layer="Layer 2 - Data Link",
            evidence=["VLAN 30 absent in show vlan brief"],
            next_command=["show interfaces trunk"],
            fix_steps=["vlan 30"]
        )

        fusion = EvidenceFusion.fuse(rule_results, ai_diag)
        self.assertEqual(fusion.agreement_status, AgreementStatus.AGREE)
        self.assertFalse(fusion.conflict_detected)
        self.assertIn("VLAN-001", fusion.supporting_rules)
        self.assertEqual(len(fusion.conflicting_rules), 0)

    def test_fusion_conflict(self):
        rule_results = [
            {"rule_id": "IF-001", "status": "FAIL", "message": "Interface GigabitEthernet0/1 is administratively down."}
        ]
        ai_diag = DiagnosisResult(
            root_cause="DNS server configuration problem on client",
            confidence=0.88,
            osi_layer="Layer 7 - Application",
            evidence=["DNS request timed out"],
            next_command=["nslookup"],
            fix_steps=["ip name-server"]
        )

        fusion = EvidenceFusion.fuse(rule_results, ai_diag)
        self.assertEqual(fusion.agreement_status, AgreementStatus.CONFLICT)
        self.assertTrue(fusion.conflict_detected)
        self.assertIn("IF-001", fusion.conflicting_rules)
        self.assertTrue(any("Human review is required" in w for w in fusion.warnings))

    def test_fusion_partial_agree(self):
        rule_results = [
            {"rule_id": "ROUTE-001", "status": "FAIL", "message": "Missing route to 10.10.20.0/24."}
        ]
        ai_diag = DiagnosisResult(
            root_cause="General routing configuration issue on remote router",
            confidence=0.70,
            osi_layer="Layer 3 - Network",
            evidence=["Route absent"],
            next_command=["show ip route"],
            fix_steps=["ip route 10.10.20.0 255.255.255.0"]
        )

        fusion = EvidenceFusion.fuse(rule_results, ai_diag)
        self.assertEqual(fusion.agreement_status, AgreementStatus.PARTIAL_AGREE)
        self.assertFalse(fusion.conflict_detected)
        self.assertIn("ROUTE-001", fusion.supporting_rules)

    def test_fusion_insufficient_evidence(self):
        rule_results = [
            {"rule_id": "VLAN-001", "status": "UNKNOWN", "message": "No VLAN evidence"}
        ]
        ai_diag = DiagnosisResult(
            root_cause="Unclear network connectivity issue",
            confidence=0.35,
            osi_layer="Unknown",
            evidence=["Insufficient evidence"],
            next_command=["show ip route", "show access-lists"],
            fix_steps=["Gather diagnostic outputs"]
        )

        fusion = EvidenceFusion.fuse(rule_results, ai_diag)
        self.assertEqual(fusion.agreement_status, AgreementStatus.INSUFFICIENT_EVIDENCE)
        self.assertFalse(fusion.conflict_detected)

    def test_fusion_no_failing_rules_ai_preserves_diagnosis(self):
        rule_results = [
            {"rule_id": "IF-001", "status": "PASS", "message": "All interfaces up"}
        ]
        ai_diag = DiagnosisResult(
            root_cause="Outbound ACL line 10 explicitly denies port 80",
            confidence=0.90,
            osi_layer="Layer 4 - Transport",
            evidence=["deny tcp any host 10.0.5.20 eq www"],
            next_command=["show access-lists"],
            fix_steps=["permit tcp any host 10.0.5.20 eq www"]
        )

        fusion = EvidenceFusion.fuse(rule_results, ai_diag)
        self.assertEqual(fusion.agreement_status, AgreementStatus.AGREE)
        self.assertFalse(fusion.conflict_detected)
        self.assertIn("No failing deterministic rules triggered", fusion.warnings[0])


class TestDiagnosisPipeline(unittest.TestCase):
    """Test suite for DiagnosisPipeline end-to-end execution."""

    def test_pipeline_execution(self):
        pipeline = DiagnosisPipeline()
        mock_response = {
            "root_cause": "Access port Fa0/5 on Switch-1 assigned to VLAN 1 instead of 10",
            "confidence": 0.95,
            "osi_layer": "Layer 2 - Data Link",
            "evidence": ["Fa0/5 listed under VLAN 1"],
            "next_command": ["show vlan brief"],
            "fix_steps": ["switchport access vlan 10"]
        }

        symptom = "PC-1 cannot ping Server-1 on Switch-2"
        show_outputs = "Switch-1# show vlan brief\n1 default active Fa0/5"

        result = pipeline.diagnose(
            symptom=symptom,
            show_outputs=show_outputs,
            case_id="CASE-001",
            mock_ai_response=mock_response
        )

        self.assertIsInstance(result, IntegratedDiagnosisResult)
        self.assertEqual(result.case_id, "CASE-001")
        self.assertEqual(len(result.rule_results), 6)
        self.assertEqual(result.ai_diagnosis["confidence"], 0.95)
        self.assertIn("fusion", result.to_dict())
        self.assertIn("agreement_status", result.fusion)


if __name__ == "__main__":
    unittest.main()
