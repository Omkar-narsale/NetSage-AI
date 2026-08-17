"""
End-to-End Integration Test Suite for NetSage AI (Phase 8).
Validates the complete 7-stage troubleshooting pipeline across all 8 core networking concepts:
VLAN, Default Gateway, DHCP, DNS, Routing, ACL, NAT, and Wireless.
"""

import os
import unittest
from ai.schemas import DiagnosisResult
from rules.checker import RuleChecker
from integration.evidence_fusion import EvidenceFusion, AgreementStatus
from integration.diagnosis_pipeline import DiagnosisPipeline
from review.review_models import ReviewDecision, ReviewState
from review.review_manager import ReviewManager
from review.review_store import ReviewStore
from evaluation.metrics import load_all_data, calculate_review_metrics


class TestEndToEndPipeline(unittest.TestCase):
    """
    End-to-End validation testing complete pipeline execution from raw evidence to dashboard join.
    """

    def setUp(self):
        self.pipeline = DiagnosisPipeline()
        self.review_manager = ReviewManager(store=ReviewStore(
            jsonl_path="data/test_e2e_reviews.jsonl",
            csv_log_path="data/test_e2e_responsible_ai_log.csv"
        ))

    def tearDown(self):
        if os.path.exists("data/test_e2e_reviews.jsonl"):
            os.remove("data/test_e2e_reviews.jsonl")
        if os.path.exists("data/test_e2e_responsible_ai_log.csv"):
            os.remove("data/test_e2e_responsible_ai_log.csv")

    def _run_e2e_case_test(
        self,
        case_id: str,
        concept: str,
        symptom: str,
        show_outputs: str,
        mock_ai_diagnosis: dict,
        review_decision: ReviewDecision,
        final_diagnosis: dict = None,
        correction_reason: str = None
    ):
        # Stage 1 & 2: Evidence Preparation & Deterministic Rule Checker
        integrated_res = self.pipeline.diagnose(
            symptom=symptom,
            show_outputs=show_outputs,
            case_id=case_id,
            mock_ai_response=mock_ai_diagnosis
        )

        self.assertEqual(integrated_res.case_id, case_id)
        self.assertGreater(len(integrated_res.rule_results), 0)
        self.assertIsNotNone(integrated_res.ai_diagnosis)
        self.assertIn("agreement_status", integrated_res.fusion)

        # Stage 6 & 7: Human Review & Final Diagnosis
        rec = self.review_manager.process_integrated_result(
            integrated_result=integrated_res,
            decision=review_decision,
            final_diagnosis=final_diagnosis or integrated_res.ai_diagnosis,
            correction_reason=correction_reason or "End-to-end verification passed."
        )

        self.assertEqual(rec.case_id, case_id)
        self.assertEqual(rec.reviewer_decision, review_decision)
        # Original AI output must remain unchanged
        self.assertEqual(rec.ai_diagnosis["root_cause"], mock_ai_diagnosis["root_cause"])

    def test_e2e_vlan_case(self):
        self._run_e2e_case_test(
            case_id="E2E-VLAN",
            concept="VLAN",
            symptom="PC-1 in VLAN 10 cannot communicate with PC-2 on Switch-2",
            show_outputs="Switch-1# show vlan brief\n1 default active Fa0/5",
            mock_ai_diagnosis={
                "root_cause": "VLAN 10 missing on Switch-1 database",
                "confidence": 0.95,
                "osi_layer": "Layer 2 - Data Link",
                "evidence": ["Fa0/5 listed under default VLAN 1"],
                "next_command": ["show vlan brief"],
                "fix_steps": ["vlan 10", "name Sales"]
            },
            review_decision=ReviewDecision.ACCEPT
        )

    def test_e2e_gateway_case(self):
        self._run_e2e_case_test(
            case_id="E2E-GW",
            concept="Default Gateway",
            symptom="Host PC-1 cannot ping remote gateway 192.168.1.1",
            show_outputs="C:\\> ipconfig /all\nDefault Gateway . . . . : 192.168.1.254",
            mock_ai_diagnosis={
                "root_cause": "Host gateway IP set to 192.168.1.254 instead of router interface 192.168.1.1",
                "confidence": 0.96,
                "osi_layer": "Layer 3 - Network",
                "evidence": ["Default Gateway: 192.168.1.254"],
                "next_command": ["ipconfig /all"],
                "fix_steps": ["Update Default Gateway to 192.168.1.1"]
            },
            review_decision=ReviewDecision.ACCEPT
        )

    def test_e2e_dhcp_case(self):
        self._run_e2e_case_test(
            case_id="E2E-DHCP",
            concept="DHCP",
            symptom="PC-3 receives APIPA address 169.254.x.x",
            show_outputs="R1# show ip dhcp pool\nPool LAN_POOL : 0 leases",
            mock_ai_diagnosis={
                "root_cause": "Router R1 interface Gi0/0 missing ip helper-address pointing to DHCP server",
                "confidence": 0.92,
                "osi_layer": "Layer 7 - Application",
                "evidence": ["0 leases assigned"],
                "next_command": ["show running-config interface Gi0/0"],
                "fix_steps": ["interface Gi0/0", "ip helper-address 10.0.0.10"]
            },
            review_decision=ReviewDecision.ACCEPT
        )

    def test_e2e_dns_case(self):
        self._run_e2e_case_test(
            case_id="E2E-DNS",
            concept="DNS",
            symptom="Client can ping 8.8.8.8 but web browser fails to resolve www.cisco.com",
            show_outputs="C:\\> nslookup www.cisco.com\nDNS request timed out.",
            mock_ai_diagnosis={
                "root_cause": "Client host DNS server address configured with unreachable IP 10.0.0.99",
                "confidence": 0.94,
                "osi_layer": "Layer 7 - Application",
                "evidence": ["DNS request timed out"],
                "next_command": ["nslookup"],
                "fix_steps": ["ip name-server 10.0.0.2"]
            },
            review_decision=ReviewDecision.ACCEPT
        )

    def test_e2e_routing_case(self):
        self._run_e2e_case_test(
            case_id="E2E-ROUTE",
            concept="Routing",
            symptom="Branch router R1 cannot reach datacenter subnet 10.10.20.0/24",
            show_outputs="R1# show ip route\nGateway of last resort is not set",
            mock_ai_diagnosis={
                "root_cause": "Missing static default route on Branch router R1",
                "confidence": 0.95,
                "osi_layer": "Layer 3 - Network",
                "evidence": ["Gateway of last resort is not set"],
                "next_command": ["show ip route"],
                "fix_steps": ["ip route 0.0.0.0 0.0.0.0 10.0.0.2"]
            },
            review_decision=ReviewDecision.ACCEPT
        )

    def test_e2e_acl_case(self):
        self._run_e2e_case_test(
            case_id="E2E-ACL",
            concept="ACL",
            symptom="Finance PC cannot reach HTTP web server at 10.0.0.5",
            show_outputs="R1# show access-lists 105\n10 deny ip 192.168.30.0 0.0.0.255 any (100 matches)\n20 permit tcp any host 10.0.0.5 eq www",
            mock_ai_diagnosis={
                "root_cause": "ACL 105 line 10 deny rule precedes permit rule line 20",
                "confidence": 0.97,
                "osi_layer": "Layer 3 - Network",
                "evidence": ["line 10 deny ip match count 100"],
                "next_command": ["show access-lists 105"],
                "fix_steps": ["ip access-list extended 105", "no 10 deny ip 192.168.30.0 0.0.0.255 any"]
            },
            review_decision=ReviewDecision.EDIT,
            final_diagnosis={
                "root_cause": "Extended ACL 105 line sequence order error: line 10 deny rule blocks HTTP before line 20 permit rule",
                "confidence": 1.0,
                "osi_layer": "Layer 3 - Network"
            },
            correction_reason="Specified exact top-to-bottom ACL line sequence matching error."
        )

    def test_e2e_nat_case(self):
        self._run_e2e_case_test(
            case_id="E2E-NAT",
            concept="NAT",
            symptom="Internal hosts 192.168.1.0/24 cannot access Internet web servers",
            show_outputs="R1# show ip nat statistics\nTotal active translations: 0",
            mock_ai_diagnosis={
                "root_cause": "Router WAN interface GigabitEthernet0/1 missing ip nat outside statement",
                "confidence": 0.93,
                "osi_layer": "Layer 3 - Network",
                "evidence": ["Total active translations: 0"],
                "next_command": ["show ip nat statistics"],
                "fix_steps": ["interface GigabitEthernet0/1", "ip nat outside"]
            },
            review_decision=ReviewDecision.ACCEPT
        )

    def test_e2e_wireless_case(self):
        self._run_e2e_case_test(
            case_id="E2E-WLAN",
            concept="Wireless",
            symptom="Wireless laptops disconnect repeatedly from SSID Corp-Wifi",
            show_outputs="WLC-1# show wlan summary\n1 Corp-Wifi Disabled",
            mock_ai_diagnosis={
                "root_cause": "WLAN profile Corp-Wifi is administratively disabled on Wireless LAN Controller WLC-1",
                "confidence": 0.98,
                "osi_layer": "Layer 2 - Data Link",
                "evidence": ["Corp-Wifi Disabled"],
                "next_command": ["show wlan summary"],
                "fix_steps": ["wlan enable 1"]
            },
            review_decision=ReviewDecision.ACCEPT
        )


if __name__ == "__main__":
    unittest.main()
