"""
Diagnosis Schema Models and Validation for NetSage AI Engine.
Enforces strict output validation:
- confidence float bounded strictly between 0.0 and 1.0
- non-empty root_cause, osi_layer, evidence, next_command, and fix_steps
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Union


class DiagnosisSchemaError(ValueError):
    """Raised when an AI diagnosis response fails validation against the output schema."""
    pass


@dataclass
class DiagnosisResult:
    root_cause: str
    confidence: float
    osi_layer: str
    evidence: List[str] = field(default_factory=list)
    next_command: List[str] = field(default_factory=list)
    fix_steps: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Strict validation method for fields and constraints."""
        if not isinstance(self.root_cause, str) or not self.root_cause.strip():
            raise DiagnosisSchemaError("Field 'root_cause' must be a non-empty string.")

        if not isinstance(self.osi_layer, str) or not self.osi_layer.strip():
            raise DiagnosisSchemaError("Field 'osi_layer' must be a non-empty string.")

        # Confidence validation: Must be float/int strictly between 0.0 and 1.0
        if not isinstance(self.confidence, (float, int)) or isinstance(self.confidence, bool):
            raise DiagnosisSchemaError("Field 'confidence' must be a numeric float between 0.0 and 1.0.")

        self.confidence = float(self.confidence)
        if not (0.0 <= self.confidence <= 1.0):
            raise DiagnosisSchemaError(
                f"Field 'confidence' value {self.confidence} is out of bounds. Must be between 0.0 and 1.0."
            )

        # Validate lists
        if not isinstance(self.evidence, list) or not all(isinstance(item, str) for item in self.evidence):
            raise DiagnosisSchemaError("Field 'evidence' must be a list of strings.")

        if not isinstance(self.next_command, list) or not all(isinstance(item, str) for item in self.next_command):
            raise DiagnosisSchemaError("Field 'next_command' must be a list of strings.")

        if not isinstance(self.fix_steps, list) or not all(isinstance(item, str) for item in self.fix_steps):
            raise DiagnosisSchemaError("Field 'fix_steps' must be a list of strings.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert DiagnosisResult to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize DiagnosisResult to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosisResult":
        """Construct and validate DiagnosisResult from dictionary."""
        if not isinstance(data, dict):
            raise DiagnosisSchemaError(f"Input payload must be a dictionary, got {type(data).__name__}.")

        required_keys = ["root_cause", "confidence", "osi_layer", "evidence", "next_command", "fix_steps"]
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise DiagnosisSchemaError(f"Missing required fields in AI response: {missing_keys}")

        try:
            return cls(
                root_cause=data["root_cause"],
                confidence=data["confidence"],
                osi_layer=data["osi_layer"],
                evidence=data.get("evidence", []),
                next_command=data.get("next_command", []),
                fix_steps=data.get("fix_steps", [])
            )
        except (TypeError, ValueError) as err:
            raise DiagnosisSchemaError(f"Schema instantiation failed: {err}")

    @classmethod
    def from_json(cls, json_str: str) -> "DiagnosisResult":
        """Parse raw JSON string and return validated DiagnosisResult instance."""
        try:
            cleaned = json_str.strip()
            # Handle markdown code block wrappers ```json ... ```
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            parsed = json.loads(cleaned)
            return cls.from_dict(parsed)
        except json.JSONDecodeError as err:
            raise DiagnosisSchemaError(f"AI response is not valid JSON: {err}")
