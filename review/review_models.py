"""
Review Models for NetSage AI (Phase 6).
Defines ReviewDecision, ReviewState, and ReviewRecord data structures.
Enforces strict validation rules:
- Human decision MUST be ACCEPT, EDIT, or REJECT.
- EDIT and REJECT decisions require final_diagnosis and correction_reason.
- Original ai_diagnosis MUST NEVER be overwritten.
"""

from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List


class ReviewValidationError(ValueError):
    """Raised when a human review decision or record fails validation."""
    pass


class ReviewDecision(str, Enum):
    ACCEPT = "ACCEPT"
    EDIT = "EDIT"
    REJECT = "REJECT"


class ReviewState(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"


@dataclass
class ReviewRecord:
    case_id: str
    ai_diagnosis: Dict[str, Any]
    rule_results: List[Dict[str, Any]]
    fusion_result: Dict[str, Any]
    reviewer_decision: ReviewDecision
    final_diagnosis: Dict[str, Any]
    reviewer_correction: Optional[str] = None
    correction_reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    review_state: ReviewState = ReviewState.PENDING

    def __post_init__(self):
        # Convert string decisions/states to Enum if passed as raw strings
        if isinstance(self.reviewer_decision, str) and not isinstance(self.reviewer_decision, ReviewDecision):
            try:
                self.reviewer_decision = ReviewDecision(self.reviewer_decision.upper())
            except ValueError:
                raise ReviewValidationError(f"Invalid reviewer_decision '{self.reviewer_decision}'. Must be ACCEPT, EDIT, or REJECT.")

        if isinstance(self.review_state, str) and not isinstance(self.review_state, ReviewState):
            try:
                self.review_state = ReviewState(self.review_state.upper())
            except ValueError:
                self.review_state = ReviewState.PENDING

        self.validate()

    def validate(self):
        """Enforces validation rules for human review decisions."""
        if not self.case_id or not str(self.case_id).strip():
            raise ReviewValidationError("Field 'case_id' is required.")

        if not isinstance(self.ai_diagnosis, dict) or not self.ai_diagnosis:
            raise ReviewValidationError("Field 'ai_diagnosis' must be a non-empty dictionary containing the original AI output.")

        # Set review_state based on reviewer_decision
        if self.reviewer_decision == ReviewDecision.ACCEPT:
            self.review_state = ReviewState.ACCEPTED
            # For ACCEPT, if final_diagnosis is empty, default to copy of ai_diagnosis
            if not self.final_diagnosis:
                self.final_diagnosis = dict(self.ai_diagnosis)

        elif self.reviewer_decision == ReviewDecision.EDIT:
            self.review_state = ReviewState.EDITED
            if not self.final_diagnosis or not isinstance(self.final_diagnosis, dict):
                raise ReviewValidationError("EDIT decision requires a valid final_diagnosis dictionary.")
            if not self.correction_reason or not str(self.correction_reason).strip():
                raise ReviewValidationError("EDIT decision requires a non-empty 'correction_reason'.")

        elif self.reviewer_decision == ReviewDecision.REJECT:
            self.review_state = ReviewState.REJECTED
            if not self.final_diagnosis or not isinstance(self.final_diagnosis, dict):
                raise ReviewValidationError("REJECT decision requires a valid final_diagnosis dictionary.")
            if not self.correction_reason or not str(self.correction_reason).strip():
                raise ReviewValidationError("REJECT decision requires a non-empty 'correction_reason' (or rejection reason).")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "ai_diagnosis": self.ai_diagnosis,
            "rule_results": self.rule_results,
            "fusion_result": self.fusion_result,
            "reviewer_decision": self.reviewer_decision.value,
            "final_diagnosis": self.final_diagnosis,
            "reviewer_correction": self.reviewer_correction,
            "correction_reason": self.correction_reason,
            "timestamp": self.timestamp,
            "review_state": self.review_state.value
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewRecord":
        if not isinstance(data, dict):
            raise ReviewValidationError("Input data must be a dictionary.")
        return cls(
            case_id=data["case_id"],
            ai_diagnosis=data["ai_diagnosis"],
            rule_results=data.get("rule_results", []),
            fusion_result=data.get("fusion_result", {}),
            reviewer_decision=data["reviewer_decision"],
            final_diagnosis=data.get("final_diagnosis", {}),
            reviewer_correction=data.get("reviewer_correction"),
            correction_reason=data.get("correction_reason"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            review_state=data.get("review_state", ReviewState.PENDING)
        )
