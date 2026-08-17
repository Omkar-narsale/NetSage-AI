"""
Integration Diagnosis Pipeline for NetSage AI (Phase 5).
Orchestrates end-to-end troubleshooting flow:
Evidence -> Rule Checker -> Groq AI Engine -> Evidence Fusion -> Integrated Output.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from rules.checker import RuleChecker
from ai.diagnosis import DiagnosisEngine
from ai.schemas import DiagnosisResult
from .evidence_fusion import EvidenceFusion, FusionAnalysis, AgreementStatus


@dataclass
class IntegratedDiagnosisResult:
    case_id: Optional[str]
    symptom: str
    rule_results: List[Dict[str, Any]]
    ai_diagnosis: Dict[str, Any]
    fusion: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "symptom": self.symptom,
            "rule_results": self.rule_results,
            "ai_diagnosis": self.ai_diagnosis,
            "fusion": self.fusion
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class DiagnosisPipeline:
    """
    End-to-end NetSage AI Diagnosis Pipeline.
    Combines Phase 3 Deterministic Rule Checker and Phase 4 Groq AI Diagnosis Engine.
    """

    def __init__(self, ai_engine: Optional[DiagnosisEngine] = None, rule_checker: Optional[RuleChecker] = None):
        self.ai_engine = ai_engine or DiagnosisEngine()
        self.rule_checker = rule_checker or RuleChecker()

    def diagnose(
        self,
        symptom: str,
        topology_note: Optional[str] = None,
        show_outputs: Optional[str] = None,
        case_id: Optional[str] = None,
        mock_ai_response: Optional[Dict[str, Any]] = None
    ) -> IntegratedDiagnosisResult:
        """
        Executes full Phase 5 diagnosis pipeline:
        1. Parse evidence & execute Phase 3 deterministic rule checks.
        2. Format rule results + CLI outputs for Phase 4 Groq AI engine (without expected_fault!).
        3. Execute AI diagnosis.
        4. Execute evidence fusion to compute agreement status and detect conflicts.
        5. Return final integrated diagnosis object.
        """
        if not symptom or not symptom.strip():
            raise ValueError("Symptom is required for diagnosis pipeline execution.")

        # STEP 1 & 2: Prepare evidence structure for RuleChecker
        rule_evidence = {
            "show_ip_interface_brief": show_outputs or "",
            "show_vlan_brief": show_outputs or "",
            "show_ip_route": show_outputs or "",
            "show_access_lists": show_outputs or ""
        }

        # STEP 3 & 4: Run Phase 3 Deterministic Rules
        raw_rule_results = self.rule_checker.run_all(rule_evidence)
        rule_results_dict = [r.to_dict() for r in raw_rule_results]

        # STEP 5 & 6: Run Phase 4 AI Diagnosis Engine
        ai_diagnosis = self.ai_engine.diagnose(
            symptom=symptom,
            topology_note=topology_note,
            show_outputs=show_outputs,
            rule_results=rule_results_dict,
            mock_response=mock_ai_response
        )

        # STEP 7: Run Evidence Fusion
        fusion_analysis = EvidenceFusion.fuse(
            rule_results=rule_results_dict,
            ai_diagnosis=ai_diagnosis
        )

        # STEP 8: Produce final structured result
        return IntegratedDiagnosisResult(
            case_id=case_id,
            symptom=symptom,
            rule_results=rule_results_dict,
            ai_diagnosis=ai_diagnosis.to_dict(),
            fusion=fusion_analysis.to_dict()
        )
