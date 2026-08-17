"""
Review Store Module for NetSage AI (Phase 6).
Manages persistence of human review records in data/review_records.jsonl
and logs human corrections (EDIT/REJECT) to data/responsible_ai_log.csv.
"""

import os
import csv
import json
from typing import Dict, Any, List, Optional
from .review_models import ReviewRecord, ReviewDecision, ReviewState, ReviewValidationError


class ReviewStore:
    """
    Persistent store for human review records and Responsible AI audit logging.
    """

    def __init__(
        self,
        jsonl_path: str = "data/review_records.jsonl",
        csv_log_path: str = "data/responsible_ai_log.csv"
    ):
        self.jsonl_path = jsonl_path
        self.csv_log_path = csv_log_path

    def save_review(self, record: ReviewRecord) -> None:
        """
        Saves a validated ReviewRecord to data/review_records.jsonl.
        If reviewer decision is EDIT or REJECT, appends entry to data/responsible_ai_log.csv.
        """
        record.validate()
        os.makedirs(os.path.dirname(self.jsonl_path), exist_ok=True)

        # Read existing records to update or append by case_id
        records_map = {}
        if os.path.exists(self.jsonl_path):
            with open(self.jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        records_map[data["case_id"]] = data

        records_map[record.case_id] = record.to_dict()

        # Write all records back to JSONL file
        with open(self.jsonl_path, "w", encoding="utf-8") as f:
            for rec in records_map.values():
                f.write(json.dumps(rec) + "\n")

        # If EDIT or REJECT, append to responsible_ai_log.csv
        if record.reviewer_decision in [ReviewDecision.EDIT, ReviewDecision.REJECT]:
            self.log_responsible_ai_correction(record)

    def get_review(self, case_id: str) -> Optional[ReviewRecord]:
        """Retrieves a ReviewRecord by case_id if present."""
        if not os.path.exists(self.jsonl_path):
            return None

        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data.get("case_id") == case_id:
                        return ReviewRecord.from_dict(data)
        return None

    def list_reviews(self) -> List[ReviewRecord]:
        """Returns list of all saved ReviewRecord instances."""
        if not os.path.exists(self.jsonl_path):
            return []

        results = []
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    results.append(ReviewRecord.from_dict(json.loads(line)))
        return results

    def count_decisions(self) -> Dict[str, int]:
        """Returns dictionary of decision counts (ACCEPT, EDIT, REJECT, PENDING)."""
        counts = {"ACCEPT": 0, "EDIT": 0, "REJECT": 0, "PENDING": 0}
        for rec in self.list_reviews():
            dec = rec.reviewer_decision.value if isinstance(rec.reviewer_decision, ReviewDecision) else str(rec.reviewer_decision)
            if dec in counts:
                counts[dec] += 1
            else:
                counts[dec] = 1
        return counts

    def log_responsible_ai_correction(self, record: ReviewRecord) -> None:
        """
        Appends human correction record to data/responsible_ai_log.csv.
        CSV Columns:
        case_id, ai_diagnosis, ai_confidence, rule_result, agreement_status, reviewer_decision, human_correction, correction_reason, final_diagnosis
        """
        os.makedirs(os.path.dirname(self.csv_log_path), exist_ok=True)
        file_exists = os.path.exists(self.csv_log_path)

        # Check existing entries to avoid duplicate logging of the same case_id
        existing_cases = set()
        if file_exists:
            with open(self.csv_log_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "case_id" in row:
                        existing_cases.add(row["case_id"])

        if record.case_id in existing_cases:
            return  # Prevent duplicate entry for same case_id

        fieldnames = [
            "case_id",
            "ai_diagnosis",
            "ai_confidence",
            "rule_result",
            "agreement_status",
            "reviewer_decision",
            "human_correction",
            "correction_reason",
            "final_diagnosis"
        ]

        ai_diag = record.ai_diagnosis.get("root_cause", "") if isinstance(record.ai_diagnosis, dict) else str(record.ai_diagnosis)
        ai_conf = record.ai_diagnosis.get("confidence", 0.0) if isinstance(record.ai_diagnosis, dict) else 0.0
        
        # Rule result summary
        failing_rules = [r.get("rule_id", "") for r in record.rule_results if r.get("status") == "FAIL"]
        rule_summary = ", ".join(failing_rules) if failing_rules else "PASS/UNKNOWN"
        
        agreement_status = record.fusion_result.get("agreement_status", "UNKNOWN") if isinstance(record.fusion_result, dict) else "UNKNOWN"
        final_diag = record.final_diagnosis.get("root_cause", "") if isinstance(record.final_diagnosis, dict) else str(record.final_diagnosis)

        row = {
            "case_id": record.case_id,
            "ai_diagnosis": ai_diag,
            "ai_confidence": ai_conf,
            "rule_result": rule_summary,
            "agreement_status": agreement_status,
            "reviewer_decision": record.reviewer_decision.value,
            "human_correction": record.reviewer_correction or final_diag,
            "correction_reason": record.correction_reason or "",
            "final_diagnosis": final_diag
        }

        with open(self.csv_log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def get_responsible_ai_log_entries(self) -> List[Dict[str, str]]:
        """Reads and returns all rows from data/responsible_ai_log.csv."""
        if not os.path.exists(self.csv_log_path):
            return []

        entries = []
        with open(self.csv_log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
        return entries
