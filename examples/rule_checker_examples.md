# NetSage AI - Deterministic Rule Checker Examples

This document demonstrates execution examples for all **six core deterministic rules** implemented in Phase 3 of NetSage AI.

For each rule, an example shows:
`Input Payload` ➔ `Rule Evaluated` ➔ `Structured Result` ➔ `Technical Explanation`.

---

## 1. Rule IF-001: Interface Down Check

### Example A: Interface Administratively Down (FAIL)

**Input Evidence**:
```json
{
  "interfaces": [
    {"name": "GigabitEthernet0/0", "status": "up", "protocol": "up"},
    {"name": "GigabitEthernet0/1", "status": "administratively down", "protocol": "down"}
  ]
}
```

**Rule Evaluated**: `IF-001`

**Structured Result**:
```json
{
  "rule_id": "IF-001",
  "rule_name": "Interface Down Check",
  "status": "FAIL",
  "severity": "High",
  "message": "Interface GigabitEthernet0/1 is administratively down.",
  "evidence": "Administratively down interfaces: GigabitEthernet0/1",
  "recommendation": "Execute 'no shutdown' under interface configuration mode for GigabitEthernet0/1."
}
```

**Explanation**: Interface `GigabitEthernet0/1` is explicitly marked as `administratively down`, indicating a software `shutdown` directive exists in configuration.

---

### Example B: All Interfaces Up (PASS)

**Input Evidence**:
```json
{
  "interfaces": [
    {"name": "GigabitEthernet0/0", "status": "up", "protocol": "up"},
    {"name": "GigabitEthernet0/1", "status": "up", "protocol": "up"}
  ]
}
```

**Rule Evaluated**: `IF-001`

**Structured Result**:
```json
{
  "rule_id": "IF-001",
  "rule_name": "Interface Down Check",
  "status": "PASS",
  "severity": "Low",
  "message": "All inspected interfaces are up and operational.",
  "evidence": "Evaluated 2 interface(s); all reported up/up status.",
  "recommendation": "No action required. Interface layer status is healthy."
}
```

**Explanation**: All listed interfaces report `up` status and line protocol `up`.

---

### Example C: Missing Interface Evidence (UNKNOWN)

**Input Evidence**:
```json
{}
```

**Rule Evaluated**: `IF-001`

**Structured Result**:
```json
{
  "rule_id": "IF-001",
  "rule_name": "Interface Down Check",
  "status": "UNKNOWN",
  "severity": "Medium",
  "message": "No interface status evidence available to evaluate.",
  "evidence": "Missing interface list or show ip interface brief output.",
  "recommendation": "Execute 'show ip interface brief' on target device and provide output."
}
```

**Explanation**: Evidence dictionary contains no interface information; the rule safely returns `UNKNOWN` rather than guessing or raising an exception.

---

## 2. Rule IP-001: Duplicate IP Address Check

### Example A: Duplicate IP Detected (FAIL)

**Input Evidence**:
```json
{
  "hosts": [
    {"device": "PC-1", "ip": "192.168.1.10"},
    {"device": "PC-2", "ip": "192.168.1.10"}
  ]
}
```

**Rule Evaluated**: `IP-001`

**Structured Result**:
```json
{
  "rule_id": "IP-001",
  "rule_name": "Duplicate IP Address Check",
  "status": "FAIL",
  "severity": "High",
  "message": "Duplicate IP address detected: 192.168.1.10 on (PC-1, PC-2).",
  "evidence": "IP conflicts found: 192.168.1.10 on (PC-1, PC-2)",
  "recommendation": "Reassign unique IP addresses to conflicting hosts or add static IPs to DHCP excluded ranges."
}
```

**Explanation**: The IP address `192.168.1.10` is assigned to both `PC-1` and `PC-2`, causing Layer 3 addressing conflict and ARP flapping.

---

## 3. Rule IP-002: Subnet Mask Alignment Check

### Example A: Host Outside Expected Subnet (FAIL)

**Input Evidence**:
```json
{
  "host_ip": "192.168.10.25",
  "subnet_mask": "255.255.255.0",
  "expected_subnet": "192.168.20.0/24"
}
```

**Rule Evaluated**: `IP-002`

**Structured Result**:
```json
{
  "rule_id": "IP-002",
  "rule_name": "Subnet Alignment Check",
  "status": "FAIL",
  "severity": "High",
  "message": "Host IP 192.168.10.25 (in 192.168.10.0/24) is outside expected subnet 192.168.20.0/24.",
  "evidence": "Host IP: 192.168.10.25/255.255.255.0 (Subnet: 192.168.10.0/24), Expected: 192.168.20.0/24",
  "recommendation": "Reconfigure host IP address or subnet mask to align with subnet 192.168.20.0/24."
}
```

**Explanation**: Using Python `ipaddress` validation, host `192.168.10.25/24` belongs to subnet `192.168.10.0/24`, which does not match expected subnet `192.168.20.0/24`.

---

## 4. Rule GW-001: Default Gateway Mismatch Check

### Example A: Gateway Outside Subnet (FAIL)

**Input Evidence**:
```json
{
  "host_ip": "192.168.1.20",
  "subnet_mask": "255.255.255.0",
  "default_gateway": "192.168.2.1"
}
```

**Rule Evaluated**: `GW-001`

**Structured Result**:
```json
{
  "rule_id": "GW-001",
  "rule_name": "Default Gateway Mismatch Check",
  "status": "FAIL",
  "severity": "High",
  "message": "Default gateway 192.168.2.1 is outside host subnet 192.168.1.0/24.",
  "evidence": "Host IP: 192.168.1.20/255.255.255.0 (Subnet: 192.168.1.0/24), Configured Gateway: 192.168.2.1",
  "recommendation": "Update host default gateway to an IP address within the local subnet 192.168.1.0/24."
}
```

**Explanation**: The host IP network is `192.168.1.0/24`, but default gateway `192.168.2.1` resides in `192.168.2.0/24`, preventing local ARP resolution for remote destination traffic.

---

## 5. Rule VLAN-001: Missing VLAN Check

### Example A: Required VLAN Missing (FAIL)

**Input Evidence**:
```json
{
  "required_vlan": 30,
  "vlans": [10, 20]
}
```

**Rule Evaluated**: `VLAN-001`

**Structured Result**:
```json
{
  "rule_id": "VLAN-001",
  "rule_name": "Missing VLAN Check",
  "status": "FAIL",
  "severity": "High",
  "message": "Required VLAN 30 is missing from the switch database.",
  "evidence": "Required: [30], Configured in database: [10, 20]",
  "recommendation": "Execute global configuration 'vlan 30' on switch to create missing VLAN."
}
```

**Explanation**: VLAN 30 is required for client access, but the switch VLAN database only contains VLANs 10 and 20.

---

## 6. Rule ROUTE-001: Missing Route Check

### Example A: Required Subnet Route Missing (FAIL)

**Input Evidence**:
```json
{
  "required_destination": "10.10.20.0/24",
  "routes": ["10.10.10.0/24", "192.168.1.0/24"]
}
```

**Rule Evaluated**: `ROUTE-001`

**Structured Result**:
```json
{
  "rule_id": "ROUTE-001",
  "rule_name": "Missing Route Check",
  "status": "FAIL",
  "severity": "High",
  "message": "Routing table is missing a route for destination 10.10.20.0/24.",
  "evidence": "Target: 10.10.20.0/24, Active Routing Table Entries: ['10.10.10.0/24', '192.168.1.0/24']...",
  "recommendation": "Add static route ('ip route 10.10.20.0 255.255.255.0 <next-hop>') or check OSPF/EIGRP network advertisement."
}
```

**Explanation**: The destination subnet `10.10.20.0/24` has no matching static, connected, or dynamic route in the routing table.
