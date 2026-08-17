"""
VLAN Rules for NetSage AI Deterministic Rule Checker.
Includes VLAN-001: Missing VLAN Check.
"""

import re
from typing import Dict, Any, List, Set
from .rule_models import RuleResult, RuleStatus


def check_missing_vlan(evidence: Dict[str, Any]) -> RuleResult:
    """
    Rule VLAN-001: Missing VLAN Check.
    Determines whether a required VLAN exists in the switch VLAN database.

    Expected evidence format:
    {
        "required_vlan": 30 (or "required_vlans": [10, 20, 30]),
        "vlans": [10, 20] (or list of dicts [{"id": 10, "name": "Users"}]),
        "show_vlan_brief": raw text output (optional)
    }
    """
    required_vlan = evidence.get("required_vlan")
    required_vlans = evidence.get("required_vlans", [])
    
    if required_vlan is not None:
        if isinstance(required_vlans, list) and required_vlan not in required_vlans:
            required_vlans.append(required_vlan)
        elif not required_vlans:
            required_vlans = [required_vlan]

    if not required_vlans:
        return RuleResult(
            rule_id="VLAN-001",
            rule_name="Missing VLAN Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No required VLAN specified for validation.",
            evidence="Missing required_vlan or required_vlans in evidence.",
            recommendation="Specify required_vlan ID in evidence for evaluation."
        )

    # Gather configured VLAN IDs
    configured_vlan_ids: Set[int] = set()
    vlans = evidence.get("vlans")
    raw_output = evidence.get("show_vlan_brief", "")

    if vlans:
        for v in vlans:
            if isinstance(v, int):
                configured_vlan_ids.add(v)
            elif isinstance(v, str) and v.isdigit():
                configured_vlan_ids.add(int(v))
            elif isinstance(v, dict):
                v_id = v.get("id") or v.get("vlan_id")
                if v_id is not None:
                    configured_vlan_ids.add(int(v_id))

    if not configured_vlan_ids and raw_output:
        configured_vlan_ids = _parse_vlan_ids_from_show_vlan_brief(raw_output)

    if not configured_vlan_ids and not raw_output:
        return RuleResult(
            rule_id="VLAN-001",
            rule_name="Missing VLAN Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No VLAN database evidence available to inspect.",
            evidence="Missing configured vlans list or show vlan brief output.",
            recommendation="Execute 'show vlan brief' on switch and provide evidence output."
        )

    missing_vlans = [int(v) for v in required_vlans if int(v) not in configured_vlan_ids]

    if missing_vlans:
        missing_str = ", ".join(str(v) for v in missing_vlans)
        return RuleResult(
            rule_id="VLAN-001",
            rule_name="Missing VLAN Check",
            status=RuleStatus.FAIL,
            severity="High",
            message=f"Required VLAN {missing_str} is missing from the switch database.",
            evidence=f"Required: {required_vlans}, Configured in database: {sorted(list(configured_vlan_ids))}",
            recommendation=f"Execute global configuration 'vlan {missing_str}' on switch to create missing VLAN."
        )

    return RuleResult(
        rule_id="VLAN-001",
        rule_name="Missing VLAN Check",
        status=RuleStatus.PASS,
        severity="Low",
        message=f"All required VLANs ({required_vlans}) exist in the switch VLAN database.",
        evidence=f"Configured VLANs found: {sorted(list(configured_vlan_ids))}",
        recommendation="No action required. VLAN database configuration is complete."
    )


def _parse_vlan_ids_from_show_vlan_brief(text: str) -> Set[int]:
    """Helper parser to extract VLAN IDs from 'show vlan brief' text output."""
    vlan_ids = set()
    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("VLAN") or line_clean.startswith("----") or line_clean.startswith("Note"):
            continue
        parts = line_clean.split()
        if parts and parts[0].isdigit():
            vlan_ids.add(int(parts[0]))
    return vlan_ids
