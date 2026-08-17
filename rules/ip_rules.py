"""
IP and Gateway Rules for NetSage AI Deterministic Rule Checker.
Includes:
- IP-001: Duplicate IP Address Check
- IP-002: Subnet Mask / Subnet Alignment Check
- GW-001: Default Gateway Mismatch Check
"""

import ipaddress
from typing import Dict, Any, List
from collections import defaultdict
from .rule_models import RuleResult, RuleStatus


def check_duplicate_ip(evidence: Dict[str, Any]) -> RuleResult:
    """
    Rule IP-001: Duplicate IP Address Check.
    Detects if the same IPv4 address is assigned to multiple devices/interfaces.

    Expected evidence format:
    {
        "hosts": [
            {"device": "PC-1", "ip": "192.168.1.10"},
            {"device": "PC-2", "ip": "192.168.1.10"}
        ]
    }
    """
    hosts = evidence.get("hosts") or evidence.get("ip_mappings")

    if not hosts:
        return RuleResult(
            rule_id="IP-001",
            rule_name="Duplicate IP Address Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No host or device IP configuration evidence available.",
            evidence="Missing host IP mappings list in evidence.",
            recommendation="Provide device IP assignment data for validation."
        )

    ip_to_devices = defaultdict(list)
    for host in hosts:
        device = host.get("device", "Unknown Device")
        ip = host.get("ip", "").strip()
        if ip:
            ip_to_devices[ip].append(device)

    if not ip_to_devices:
        return RuleResult(
            rule_id="IP-001",
            rule_name="Duplicate IP Address Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="No valid IP addresses extracted from provided evidence.",
            evidence="Empty IP fields in host configuration list.",
            recommendation="Ensure IP addresses are properly formatted in device mappings."
        )

    duplicates = {ip: devs for ip, devs in ip_to_devices.items() if len(devs) > 1}

    if duplicates:
        details = [f"{ip} on ({', '.join(devs)})" for ip, devs in duplicates.items()]
        dup_summary = "; ".join(details)
        return RuleResult(
            rule_id="IP-001",
            rule_name="Duplicate IP Address Check",
            status=RuleStatus.FAIL,
            severity="High",
            message=f"Duplicate IP address detected: {dup_summary}.",
            evidence=f"IP conflicts found: {dup_summary}",
            recommendation="Reassign unique IP addresses to conflicting hosts or add static IPs to DHCP excluded ranges."
        )

    return RuleResult(
        rule_id="IP-001",
        rule_name="Duplicate IP Address Check",
        status=RuleStatus.PASS,
        severity="Low",
        message="All inspected device IP addresses are unique across the network.",
        evidence=f"Validated {len(ip_to_devices)} unique IP assignment(s).",
        recommendation="No action required. IP address allocation is unique."
    )


def check_subnet_mask(evidence: Dict[str, Any]) -> RuleResult:
    """
    Rule IP-002: Wrong Subnet Mask / Subnet Alignment Check.
    Validates whether host IP belongs to the expected subnet.

    Expected evidence format:
    {
        "host_ip": "192.168.10.25",
        "subnet_mask": "255.255.255.0",
        "expected_subnet": "192.168.20.0/24"
    }
    """
    host_ip_str = evidence.get("host_ip")
    subnet_mask_str = evidence.get("subnet_mask", "255.255.255.0")
    expected_subnet_str = evidence.get("expected_subnet")

    if not host_ip_str or not expected_subnet_str:
        return RuleResult(
            rule_id="IP-002",
            rule_name="Subnet Alignment Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="Insufficient evidence to validate host subnet alignment.",
            evidence="Missing host_ip or expected_subnet in evidence.",
            recommendation="Provide host_ip, subnet_mask, and expected_subnet for rule evaluation."
        )

    try:
        host_addr = ipaddress.ip_address(host_ip_str)
        expected_net = ipaddress.ip_network(expected_subnet_str, strict=False)

        if host_addr in expected_net:
            return RuleResult(
                rule_id="IP-002",
                rule_name="Subnet Alignment Check",
                status=RuleStatus.PASS,
                severity="Low",
                message=f"Host IP {host_ip_str} belongs to expected subnet {expected_subnet_str}.",
                evidence=f"Host IP: {host_ip_str}, Expected Subnet: {expected_subnet_str}",
                recommendation="No action required. Host subnet assignment is correct."
            )
        else:
            # Determine actual network for host
            host_interface = ipaddress.ip_interface(f"{host_ip_str}/{subnet_mask_str}")
            actual_net = host_interface.network
            return RuleResult(
                rule_id="IP-002",
                rule_name="Subnet Alignment Check",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Host IP {host_ip_str} (in {actual_net}) is outside expected subnet {expected_subnet_str}.",
                evidence=f"Host IP: {host_ip_str}/{subnet_mask_str} (Subnet: {actual_net}), Expected: {expected_subnet_str}",
                recommendation=f"Reconfigure host IP address or subnet mask to align with subnet {expected_subnet_str}."
            )
    except ValueError as err:
        return RuleResult(
            rule_id="IP-002",
            rule_name="Subnet Alignment Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message=f"Invalid IP or subnet format: {err}",
            evidence=f"Raw inputs: host_ip={host_ip_str}, mask={subnet_mask_str}, expected={expected_subnet_str}",
            recommendation="Verify string formatting of IPv4 addresses and CIDR notation."
        )


def check_default_gateway(evidence: Dict[str, Any]) -> RuleResult:
    """
    Rule GW-001: Default Gateway Mismatch Check.
    Validates whether host default gateway is within the host's subnet and matches expected router IP.

    Expected evidence format:
    {
        "host_ip": "192.168.1.20",
        "subnet_mask": "255.255.255.0",
        "default_gateway": "192.168.2.1",
        "expected_gateway_ip": "192.168.1.1" (optional)
    }
    """
    host_ip_str = evidence.get("host_ip")
    subnet_mask_str = evidence.get("subnet_mask", "255.255.255.0")
    gateway_str = evidence.get("default_gateway")
    expected_gateway_str = evidence.get("expected_gateway_ip")

    if not host_ip_str or not gateway_str:
        return RuleResult(
            rule_id="GW-001",
            rule_name="Default Gateway Mismatch Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message="Insufficient evidence to evaluate default gateway status.",
            evidence="Missing host_ip or default_gateway in evidence.",
            recommendation="Provide host_ip, subnet_mask, and default_gateway for rule evaluation."
        )

    # Check for empty gateway or 0.0.0.0
    if gateway_str in ["0.0.0.0", "", "None"]:
        return RuleResult(
            rule_id="GW-001",
            rule_name="Default Gateway Mismatch Check",
            status=RuleStatus.FAIL,
            severity="High",
            message=f"Host {host_ip_str} has no default gateway configured (0.0.0.0).",
            evidence=f"Host IP: {host_ip_str}, Default Gateway: {gateway_str}",
            recommendation="Configure a valid default gateway IP address on the client network interface."
        )

    try:
        host_iface = ipaddress.ip_interface(f"{host_ip_str}/{subnet_mask_str}")
        gateway_addr = ipaddress.ip_address(gateway_str)
        host_subnet = host_iface.network

        # 1. Verify gateway is in host's subnet
        if gateway_addr not in host_subnet:
            return RuleResult(
                rule_id="GW-001",
                rule_name="Default Gateway Mismatch Check",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Default gateway {gateway_str} is outside host subnet {host_subnet}.",
                evidence=f"Host IP: {host_ip_str}/{subnet_mask_str} (Subnet: {host_subnet}), Configured Gateway: {gateway_str}",
                recommendation=f"Update host default gateway to an IP address within the local subnet {host_subnet}."
            )

        # 2. If expected gateway IP is supplied, check exact match
        if expected_gateway_str and expected_gateway_str != gateway_str:
            return RuleResult(
                rule_id="GW-001",
                rule_name="Default Gateway Mismatch Check",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Configured gateway {gateway_str} does not match expected router gateway IP {expected_gateway_str}.",
                evidence=f"Host Gateway: {gateway_str}, Router Interface IP: {expected_gateway_str}",
                recommendation=f"Change host default gateway configuration from {gateway_str} to {expected_gateway_str}."
            )

        return RuleResult(
            rule_id="GW-001",
            rule_name="Default Gateway Mismatch Check",
            status=RuleStatus.PASS,
            severity="Low",
            message=f"Default gateway {gateway_str} is valid and correctly aligned with subnet {host_subnet}.",
            evidence=f"Host IP: {host_ip_str}/{subnet_mask_str}, Gateway: {gateway_str}",
            recommendation="No action required. Default gateway configuration is valid."
        )

    except ValueError as err:
        return RuleResult(
            rule_id="GW-001",
            rule_name="Default Gateway Mismatch Check",
            status=RuleStatus.UNKNOWN,
            severity="Medium",
            message=f"Invalid IP address format in gateway evaluation: {err}",
            evidence=f"Inputs: host_ip={host_ip_str}, gateway={gateway_str}",
            recommendation="Check formatting of host IP and gateway IP addresses."
        )
