"""
Routing Rules for NetSage AI Deterministic Rule Checker.
Includes ROUTE-001: Missing Route Check.
"""

import ipaddress
import re
from typing import Dict, Any, List, Optional
from .rule_models import RuleResult, RuleStatus


def check_missing_route(evidence: Dict[str, Any]) -> RuleResult:
    """
    Rule ROUTE-001: Missing Route Check.
    Determines whether a route covering the required destination subnet exists in the routing table.

    Expected evidence format:
    {
        "required_destination": "10.10.20.0/24",
        "routes": ["10.10.10.0/24", "192.168.1.0/24"],
        "show_ip_route": raw text output (optional)
    }
    """
    dest_str = evidence.get("required_destination") or evidence.get("required_route")

    if not dest_str:
        return RuleResult(
            rule_id="ROUTE-001",
            rule_name="Missing Route Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No required destination subnet specified for routing check.",
            evidence="Missing required_destination or required_route in evidence.",
            recommendation="Specify target destination network (e.g. 10.10.20.0/24) in evidence."
        )

    routes = evidence.get("routes", [])
    raw_output = evidence.get("show_ip_route", "")

    if not routes and raw_output:
        routes = _parse_routes_from_show_ip_route(raw_output)

    if not routes and not raw_output:
        return RuleResult(
            rule_id="ROUTE-001",
            rule_name="Missing Route Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No routing table evidence available to inspect.",
            evidence="Missing routes list or show ip route output.",
            recommendation="Execute 'show ip route' on router and provide output evidence."
        )

    # Validate destination target
    try:
        if "/" in dest_str:
            target_net = ipaddress.ip_network(dest_str, strict=False)
            target_ip = target_net.network_address
        else:
            target_ip = ipaddress.ip_address(dest_str)
            target_net = ipaddress.ip_network(f"{dest_str}/32", strict=False)
    except ValueError:
        return RuleResult(
            rule_id="ROUTE-001",
            rule_name="Missing Route Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message=f"Invalid destination format: {dest_str}",
            evidence=f"Target: {dest_str}",
            recommendation="Ensure target destination is a valid IPv4 network or host address."
        )

    route_matched = False
    matching_route = None

    for r in routes:
        try:
            # Handle default route notation
            if r == "0.0.0.0/0" or "Gateway of last resort is set" in r:
                route_matched = True
                matching_route = "0.0.0.0/0 (Default Route)"
                break
            
            # Clean string route
            r_clean = r.split()[0] if " " in r else r
            if "/" not in r_clean and not r_clean.count(".") == 3:
                continue

            r_net = ipaddress.ip_network(r_clean, strict=False)
            if target_ip in r_net or r_net.subnet_of(target_net) or target_net.subnet_of(r_net):
                route_matched = True
                matching_route = str(r_net)
                break
        except Exception:
            continue

    if not route_matched:
        return RuleResult(
            rule_id="ROUTE-001",
            rule_name="Missing Route Check",
            status=RuleStatus.FAIL,
            severity="High",
            message=f"Routing table is missing a route for destination {dest_str}.",
            evidence=f"Target: {dest_str}, Active Routing Table Entries: {routes[:5]}...",
            recommendation=f"Add static route ('ip route {dest_str} <next-hop>') or check OSPF/EIGRP network advertisement."
        )

    return RuleResult(
        rule_id="ROUTE-001",
        rule_name="Missing Route Check",
        status=RuleStatus.PASS,
        severity="Low",
        message=f"Valid route to destination {dest_str} exists via {matching_route}.",
        evidence=f"Target: {dest_str}, Matched Route Entry: {matching_route}",
        recommendation="No action required. Destination route is active in routing table."
    )


def _parse_routes_from_show_ip_route(text: str) -> List[str]:
    """Helper parser to extract network prefixes from Cisco 'show ip route' output."""
    routes = []
    # Match standard prefixes like 10.10.10.0/24 or 192.168.1.0/24 or 0.0.0.0/0
    pattern = r'(?:[O|C|S|R|B|D|i]\s+)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})'
    matches = re.findall(pattern, text)
    if matches:
        routes.extend(matches)

    if "Gateway of last resort is" in text and "not set" not in text:
        routes.append("0.0.0.0/0")

    return routes
