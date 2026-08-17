"""
Interface Rules for NetSage AI Deterministic Rule Checker.
Includes IF-001: Interface Down Check.
"""

from typing import Dict, Any, List, Optional
from .rule_models import RuleResult, RuleStatus


def check_interface_down(evidence: Dict[str, Any]) -> RuleResult:
    """
    Rule IF-001: Interface Down Check.
    Inspects interface operational state and protocol status.
    
    Expected evidence format:
    {
        "interfaces": [
            {"name": "GigabitEthernet0/0", "status": "up", "protocol": "up"},
            {"name": "GigabitEthernet0/1", "status": "administratively down", "protocol": "down"}
        ]
    }
    Or raw text string in evidence["show_ip_interface_brief"].
    """
    interfaces = evidence.get("interfaces")
    raw_output = evidence.get("show_ip_interface_brief", "")

    # Parse raw text output if structured list is not provided
    if not interfaces and raw_output:
        interfaces = _parse_show_ip_interface_brief(raw_output)

    if not interfaces:
        return RuleResult(
            rule_id="IF-001",
            rule_name="Interface Down Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No interface status evidence available to evaluate.",
            evidence="Missing interface list or show ip interface brief output.",
            recommendation="Execute 'show ip interface brief' on target device and provide output."
        )

    down_interfaces = []
    admin_down_interfaces = []

    for intf in interfaces:
        name = intf.get("name", "Unknown Interface")
        status = intf.get("status", "").lower()
        protocol = intf.get("protocol", "").lower()

        if "administratively down" in status or "admin down" in status:
            admin_down_interfaces.append(name)
        elif status == "down" or protocol == "down":
            down_interfaces.append(f"{name} ({status}/{protocol})")

    if admin_down_interfaces:
        affected = ", ".join(admin_down_interfaces)
        return RuleResult(
            rule_id="IF-001",
            rule_name="Interface Down Check",
            status=RuleStatus.FAIL,
            severity="High",
            message=f"Interface {affected} is administratively down.",
            evidence=f"Administratively down interfaces: {affected}",
            recommendation=f"Execute 'no shutdown' under interface configuration mode for {affected}."
        )
    elif down_interfaces:
        affected = ", ".join(down_interfaces)
        return RuleResult(
            rule_id="IF-001",
            rule_name="Interface Down Check",
            status=RuleStatus.FAIL,
            severity="High",
            message=f"Interface {affected} line protocol is down.",
            evidence=f"Down interfaces: {affected}",
            recommendation=f"Verify physical cable connections, SFP modules, or remote end port status for {affected}."
        )

    return RuleResult(
        rule_id="IF-001",
        rule_name="Interface Down Check",
        status=RuleStatus.PASS,
        severity="Low",
        message="All inspected interfaces are up and operational.",
        evidence=f"Evaluated {len(interfaces)} interface(s); all reported up/up status.",
        recommendation="No action required. Interface layer status is healthy."
    )


def _parse_show_ip_interface_brief(text: str) -> List[Dict[str, str]]:
    """Helper parser for Cisco 'show ip interface brief' text output."""
    parsed = []
    lines = text.strip().splitlines()
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("Interface") or line_clean.startswith("Codes"):
            continue
        parts = line_clean.split()
        if len(parts) >= 4:
            name = parts[0]
            ip = parts[1]
            # Handle status containing spaces like 'administratively down'
            if "administratively down" in line_clean.lower():
                status = "administratively down"
                protocol = parts[-1].lower()
            else:
                status = parts[-2].lower() if len(parts) >= 6 else parts[4].lower()
                protocol = parts[-1].lower()
            parsed.append({"name": name, "ip": ip, "status": status, "protocol": protocol})
    return parsed
