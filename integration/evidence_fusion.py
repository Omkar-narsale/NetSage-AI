"""
Evidence Fusion Module for NetSage AI (Phase 5).
Compares Phase 3 deterministic rule results against Phase 4 AI diagnoses
to compute agreement status, flag conflicts, and generate warnings.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from ai.schemas import DiagnosisResult


class AgreementStatus(str, Enum):
    AGREE = "AGREE"
    PARTIAL_AGREE = "PARTIAL_AGREE"
    CONFLICT = "CONFLICT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class FusionAnalysis:
    agreement_status: AgreementStatus
    conflict_detected: bool
    supporting_rules: List[str] = field(default_factory=list)
    conflicting_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agreement_status": self.agreement_status.value if isinstance(self.agreement_status, AgreementStatus) else str(self.agreement_status),
            "conflict_detected": self.conflict_detected,
            "supporting_rules": self.supporting_rules,
            "conflicting_rules": self.conflicting_rules,
            "warnings": self.warnings
        }


class EvidenceFusion:
    """
    Analyzes alignment between deterministic rules and AI diagnosis.
    Does NOT automatically override AI or rule findings; flags conflicts for Phase 6 Human Review.
    """

    # Keyword mappings between Rule IDs / Concepts and Root Cause keywords
    CONCEPT_KEYWORDS = {
        "IF-001": ["interface", "down", "administratively down", "shutdown", "line protocol"],
        "IP-001": ["duplicate", "conflict", "ip address"],
        "IP-002": ["subnet", "mask", "alignment"],
        "GW-001": ["gateway", "default gateway", "default-router"],
        "VLAN-001": ["vlan", "trunk", "access port", "native vlan", "802.1q"],
        "ROUTE-001": ["route", "routing", "ospf", "next-hop", "static route", "gateway of last resort"]
    }

    @classmethod
    def fuse(
        cls,
        rule_results: List[Dict[str, Any]],
        ai_diagnosis: DiagnosisResult
    ) -> FusionAnalysis:
        """
        Fuses deterministic rule results with AI diagnosis output.
        """
        ai_cause = ai_diagnosis.root_cause.lower().strip()
        ai_confidence = ai_diagnosis.confidence

        failing_rules = [r for r in rule_results if r.get("status") == "FAIL"]
        supporting_rules = []
        conflicting_rules = []
        warnings = []

        # Case 1: Incomplete / low evidence state
        if ai_confidence < 0.50 and not failing_rules:
            return FusionAnalysis(
                agreement_status=AgreementStatus.INSUFFICIENT_EVIDENCE,
                conflict_detected=False,
                supporting_rules=[],
                conflicting_rules=[],
                warnings=["Insufficient evidence available for both deterministic rules and AI model."]
            )

        # Case 2: Evaluate failing rules against AI diagnosis
        if failing_rules:
            for rule in failing_rules:
                rule_id = rule.get("rule_id", "")
                rule_msg = rule.get("message", "").lower()
                keywords = cls.CONCEPT_KEYWORDS.get(rule_id, [])

                # Check keyword or rule message match with AI root cause
                has_keyword_match = any(kw in ai_cause for kw in keywords)
                has_message_match = any(word in ai_cause for word in rule_msg.split() if len(word) > 4)

                if has_keyword_match or has_message_match:
                    supporting_rules.append(rule_id)
                else:
                    conflicting_rules.append(rule_id)

            if conflicting_rules:
                # Strong conflict detected
                conflict_rule_str = ", ".join(conflicting_rules)
                warnings.append(
                    f"AI diagnosis conflicts with deterministic rule {conflict_rule_str}. Human review is required."
                )
                return FusionAnalysis(
                    agreement_status=AgreementStatus.CONFLICT,
                    conflict_detected=True,
                    supporting_rules=supporting_rules,
                    conflicting_rules=conflicting_rules,
                    warnings=warnings
                )

            if supporting_rules:
                # Check for exact vs partial agreement
                if len(supporting_rules) == len(failing_rules):
                    if ai_confidence >= 0.75:
                        return FusionAnalysis(
                            agreement_status=AgreementStatus.AGREE,
                            conflict_detected=False,
                            supporting_rules=supporting_rules,
                            conflicting_rules=[],
                            warnings=[]
                        )
                    else:
                        return FusionAnalysis(
                            agreement_status=AgreementStatus.PARTIAL_AGREE,
                            conflict_detected=False,
                            supporting_rules=supporting_rules,
                            conflicting_rules=[],
                            warnings=["AI diagnosis agrees with failing rules but has moderate confidence."]
                        )

        # Case 3: No failing rules, but AI provided a high-confidence diagnosis based on CLI evidence
        if not failing_rules:
            if ai_confidence >= 0.75:
                return FusionAnalysis(
                    agreement_status=AgreementStatus.AGREE,
                    conflict_detected=False,
                    supporting_rules=[],
                    conflicting_rules=[],
                    warnings=["No failing deterministic rules triggered; AI diagnosis relies directly on CLI evidence."]
                )
            else:
                return FusionAnalysis(
                    agreement_status=AgreementStatus.PARTIAL_AGREE,
                    conflict_detected=False,
                    supporting_rules=[],
                    conflicting_rules=[],
                    warnings=["No failing deterministic rules triggered and AI confidence is moderate."]
                )

        return FusionAnalysis(
            agreement_status=AgreementStatus.PARTIAL_AGREE,
            conflict_detected=False,
            supporting_rules=supporting_rules,
            conflicting_rules=conflicting_rules,
            warnings=warnings
        )
