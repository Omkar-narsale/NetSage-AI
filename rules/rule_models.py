"""
Rule Models for NetSage AI Deterministic Rule Engine.
Defines RuleStatus enum and RuleResult dataclass.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional


class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    status: RuleStatus
    severity: str
    message: str
    evidence: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": self.status.value if isinstance(self.status, RuleStatus) else str(self.status),
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }
