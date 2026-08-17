"""
Evaluation Metrics Module for NetSage AI (Phase 7).
Provides reusable calculations for AI accuracy, human review metrics,
evidence fusion statistics, distribution metrics, and high-confidence error detection.

CRITICAL: All functions handle missing files, empty datasets, and zero denominators safely.
"""

import os
import csv
import json
from typing import Dict, Any, List, Optional, Tuple


def load_all_data(
    cases_path: str = "data/cases.csv",
    ai_path: str = "data/ai_diagnoses.jsonl",
    integrated_path: str = "data/integrated_results.jsonl",
    review_path: str = "data/review_records.jsonl",
    log_path: str = "data/responsible_ai_log.csv"
) -> Dict[str, Dict[str, Any]]:
    """
    Loads and joins all project datasets using case_id as the primary key.
    Handles missing or partially completed files gracefully without throwing errors.
    """
    dataset: Dict[str, Dict[str, Any]] = {}

    # 1. Load cases.csv (Ground Truth)
    if os.path.exists(cases_path):
        with open(cases_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("case_id", "").strip()
                if cid:
                    dataset[cid] = {
                        "case_id": cid,
                        "symptom": row.get("symptom", ""),
                        "topology_note": row.get("topology_note", ""),
                        "show_outputs": row.get("show_outputs", ""),
                        "expected_fault": row.get("expected_fault", ""),
                        "osi_layer": row.get("osi_layer", "Unknown"),
                        "concept": row.get("concept", "Unknown"),
                        "severity": row.get("severity", "Medium"),
                        "ai_diagnosis": None,
                        "rule_results": [],
                        "fusion": None,
                        "review_record": None,
                        "responsible_ai_log": None
                    }

    # 2. Load ai_diagnoses.jsonl
    if os.path.exists(ai_path):
        with open(ai_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        cid = rec.get("case_id")
                        if cid and cid in dataset:
                            dataset[cid]["ai_diagnosis"] = rec.get("diagnosis")
                        elif cid:
                            dataset[cid] = {
                                "case_id": cid,
                                "ai_diagnosis": rec.get("diagnosis"),
                                "symptom": "", "topology_note": "", "show_outputs": "", "expected_fault": "",
                                "osi_layer": "Unknown", "concept": "Unknown", "severity": "Medium",
                                "rule_results": [], "fusion": None, "review_record": None, "responsible_ai_log": None
                            }
                    except json.JSONDecodeError:
                        continue

    # 3. Load integrated_results.jsonl (Phase 5 Pipeline Output)
    if os.path.exists(integrated_path):
        with open(integrated_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        cid = rec.get("case_id")
                        if cid and cid in dataset:
                            dataset[cid]["rule_results"] = rec.get("rule_results", [])
                            dataset[cid]["fusion"] = rec.get("fusion")
                            if not dataset[cid]["ai_diagnosis"]:
                                dataset[cid]["ai_diagnosis"] = rec.get("ai_diagnosis")
                    except json.JSONDecodeError:
                        continue

    # 4. Load review_records.jsonl (Phase 6 Human Review Records)
    if os.path.exists(review_path):
        with open(review_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        cid = rec.get("case_id")
                        if cid and cid in dataset:
                            dataset[cid]["review_record"] = rec
                    except json.JSONDecodeError:
                        continue

    # 5. Load responsible_ai_log.csv
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("case_id", "").strip()
                if cid and cid in dataset:
                    dataset[cid]["responsible_ai_log"] = row

    return dataset


def calculate_ai_accuracy(dataset: Dict[str, Dict[str, Any]]) -> Tuple[float, int, int]:
    """
    Calculates AI diagnosis accuracy against ground truth expected_fault.
    Returns: (accuracy_pct, correct_count, total_ai_cases)
    """
    total = 0
    correct = 0
    for case in dataset.values():
        ai_diag = case.get("ai_diagnosis")
        exp_fault = case.get("expected_fault")
        if ai_diag and exp_fault and isinstance(ai_diag, dict):
            total += 1
            root_cause = ai_diag.get("root_cause", "")
            if _is_cause_matching(root_cause, exp_fault):
                correct += 1
    accuracy = (correct / total * 100.0) if total > 0 else 0.0
    return round(accuracy, 2), correct, total


def calculate_average_confidence(dataset: Dict[str, Dict[str, Any]]) -> float:
    """Calculates average confidence score across cases with AI diagnoses."""
    total = 0
    sum_conf = 0.0
    for case in dataset.values():
        ai_diag = case.get("ai_diagnosis")
        if ai_diag and isinstance(ai_diag, dict):
            conf = ai_diag.get("confidence")
            if isinstance(conf, (int, float)):
                total += 1
                sum_conf += conf
    return round(sum_conf / total, 2) if total > 0 else 0.0


def calculate_review_metrics(dataset: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates human review decision metrics and percentages.
    Zero-divide safe!
    """
    accepted = 0
    edited = 0
    rejected = 0
    pending = 0

    for case in dataset.values():
        rev = case.get("review_record")
        if rev and isinstance(rev, dict):
            dec = rev.get("reviewer_decision", "").upper()
            if dec == "ACCEPT":
                accepted += 1
            elif dec == "EDIT":
                edited += 1
            elif dec == "REJECT":
                rejected += 1
            else:
                pending += 1
        else:
            pending += 1

    reviewed_total = accepted + edited + rejected
    acceptance_rate = (accepted / reviewed_total * 100.0) if reviewed_total > 0 else 0.0
    correction_rate = ((edited + rejected) / reviewed_total * 100.0) if reviewed_total > 0 else 0.0
    rejection_rate = (rejected / reviewed_total * 100.0) if reviewed_total > 0 else 0.0

    return {
        "reviewed_total": reviewed_total,
        "pending_count": pending,
        "accepted_count": accepted,
        "edited_count": edited,
        "rejected_count": rejected,
        "acceptance_rate_pct": round(acceptance_rate, 2),
        "correction_rate_pct": round(correction_rate, 2),
        "rejection_rate_pct": round(rejection_rate, 2)
    }


def calculate_fusion_metrics(dataset: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates Phase 5 Evidence Fusion agreement status distribution."""
    counts = {"AGREE": 0, "PARTIAL_AGREE": 0, "CONFLICT": 0, "INSUFFICIENT_EVIDENCE": 0}
    total = 0

    for case in dataset.values():
        fusion = case.get("fusion")
        if fusion and isinstance(fusion, dict):
            status = fusion.get("agreement_status", "").upper()
            if status in counts:
                counts[status] += 1
                total += 1

    pcts = {}
    for status, count in counts.items():
        pcts[status] = round((count / total * 100.0), 2) if total > 0 else 0.0

    return {
        "total_fusion_cases": total,
        "counts": counts,
        "percentages": pcts
    }


def calculate_concept_distribution(dataset: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    """Calculates breakdown of cases per networking concept."""
    dist: Dict[str, int] = {}
    for case in dataset.values():
        c = case.get("concept", "Unknown")
        dist[c] = dist.get(c, 0) + 1
    return dist


def calculate_severity_distribution(dataset: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    """Calculates breakdown of cases per severity level."""
    dist = {"High": 0, "Medium": 0, "Low": 0}
    for case in dataset.values():
        sev = case.get("severity", "Medium")
        dist[sev] = dist.get(sev, 0) + 1
    return dist


def calculate_high_confidence_errors(dataset: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifies high-confidence AI errors:
    AI Confidence >= 0.80 AND Human Reviewer decision is EDIT or REJECT.
    """
    errors = []
    for cid, case in dataset.items():
        ai_diag = case.get("ai_diagnosis")
        rev = case.get("review_record")

        if ai_diag and rev and isinstance(ai_diag, dict) and isinstance(rev, dict):
            conf = ai_diag.get("confidence", 0.0)
            dec = rev.get("reviewer_decision", "").upper()

            if conf >= 0.80 and dec in ["EDIT", "REJECT"]:
                errors.append({
                    "case_id": cid,
                    "concept": case.get("concept", "Unknown"),
                    "ai_root_cause": ai_diag.get("root_cause", ""),
                    "confidence": conf,
                    "reviewer_decision": dec,
                    "human_correction": rev.get("reviewer_correction") or rev.get("final_diagnosis", {}).get("root_cause", ""),
                    "correction_reason": rev.get("correction_reason", ""),
                    "final_diagnosis": rev.get("final_diagnosis", {}).get("root_cause", "")
                })
    return errors


def _is_cause_matching(ai_cause: str, expected_fault: str) -> bool:
    """Helper token matching function."""
    ai_clean = ai_cause.lower().strip()
    exp_clean = expected_fault.lower().strip()
    words = [w for w in exp_clean.replace(".", "").replace(",", "").split() if len(w) > 3]
    if not words:
        return True
    matches = sum(1 for w in words if w in ai_clean)
    return (matches / len(words)) >= 0.40
