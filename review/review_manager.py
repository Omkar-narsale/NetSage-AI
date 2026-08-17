"""
Review Manager Module for NetSage AI (Phase 6).
Orchestrates the Human Review workflow and validates reviewer decisions.
Ensures Human is Final Authority and original AI output is NEVER mutated.
"""

from typing import Dict, Any, Optional, List, Union
from .review_models import ReviewRecord, ReviewDecision, ReviewState, ReviewValidationError
from .review_store import ReviewStore
from integration.diagnosis_pipeline import IntegratedDiagnosisResult


class ReviewManager:
    """
    Manages human review workflow for NetSage AI diagnoses.
    """

    def __init__(self, store: Optional[ReviewStore] = None):
        self.store = store or ReviewStore()

    def process_review(
        self,
        case_id: str,
        ai_diagnosis: Dict[str, Any],
        rule_results: List[Dict[str, Any]],
        fusion_result: Dict[str, Any],
        decision: Union[str, ReviewDecision],
        final_diagnosis: Optional[Dict[str, Any]] = None,
        correction_reason: Optional[str] = None,
        reviewer_correction: Optional[str] = None
    ) -> ReviewRecord:
        """
        Processes a human reviewer's decision for a specific case.

        Parameters:
        - case_id: Unique case identifier
        - ai_diagnosis: Original AI diagnosis dict (preserved as-is)
        - rule_results: Phase 3 rule checker output
        - fusion_result: Phase 5 evidence fusion output
        - decision: ACCEPT, EDIT, or REJECT
        - final_diagnosis: Human accepted or human edited diagnosis dict
        - correction_reason: Required for EDIT and REJECT
        - reviewer_correction: Short summary of correction

        Returns:
        - Saved ReviewRecord instance.
        """
        if isinstance(decision, str):
            try:
                decision = ReviewDecision(decision.upper())
            except ValueError:
                raise ReviewValidationError(f"Invalid decision '{decision}'. Allowed: ACCEPT, EDIT, REJECT.")

        # Preserve original AI output by making deep/shallow copy if needed
        preserved_ai_diagnosis = dict(ai_diagnosis)

        if decision == ReviewDecision.ACCEPT:
            # For ACCEPT, if final_diagnosis not provided, default to preserved_ai_diagnosis
            resolved_final_diagnosis = dict(final_diagnosis) if final_diagnosis else dict(preserved_ai_diagnosis)
            resolved_reason = correction_reason or "AI diagnosis accepted without modification."
            resolved_correction = reviewer_correction or None
        elif decision == ReviewDecision.EDIT:
            if not final_diagnosis or not isinstance(final_diagnosis, dict):
                raise ReviewValidationError("EDIT decision requires a valid final_diagnosis dictionary.")
            if not correction_reason or not str(correction_reason).strip():
                raise ReviewValidationError("EDIT decision requires a non-empty correction_reason.")
            resolved_final_diagnosis = dict(final_diagnosis)
            resolved_reason = str(correction_reason).strip()
            resolved_correction = reviewer_correction or resolved_final_diagnosis.get("root_cause", "")
        elif decision == ReviewDecision.REJECT:
            if not final_diagnosis or not isinstance(final_diagnosis, dict):
                raise ReviewValidationError("REJECT decision requires a valid final_diagnosis dictionary.")
            if not correction_reason or not str(correction_reason).strip():
                raise ReviewValidationError("REJECT decision requires a non-empty correction_reason (rejection reason).")
            resolved_final_diagnosis = dict(final_diagnosis)
            resolved_reason = str(correction_reason).strip()
            resolved_correction = reviewer_correction or f"REJECTED: {resolved_reason}"

        record = ReviewRecord(
            case_id=case_id,
            ai_diagnosis=preserved_ai_diagnosis,
            rule_results=rule_results,
            fusion_result=fusion_result,
            reviewer_decision=decision,
            final_diagnosis=resolved_final_diagnosis,
            reviewer_correction=resolved_correction,
            correction_reason=resolved_reason
        )

        self.store.save_review(record)
        return record

    def process_integrated_result(
        self,
        integrated_result: IntegratedDiagnosisResult,
        decision: Union[str, ReviewDecision],
        final_diagnosis: Optional[Dict[str, Any]] = None,
        correction_reason: Optional[str] = None,
        reviewer_correction: Optional[str] = None
    ) -> ReviewRecord:
        """Helper to process review directly from an IntegratedDiagnosisResult instance."""
        res_dict = integrated_result.to_dict()
        return self.process_review(
            case_id=res_dict.get("case_id") or "CASE-UNKNOWN",
            ai_diagnosis=res_dict.get("ai_diagnosis", {}),
            rule_results=res_dict.get("rule_results", []),
            fusion_result=res_dict.get("fusion", {}),
            decision=decision,
            final_diagnosis=final_diagnosis,
            correction_reason=correction_reason,
            reviewer_correction=reviewer_correction
        )
