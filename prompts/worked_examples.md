# NetSage AI - Diagnosis Prompt Worked Examples

This document provides 3 complete worked examples demonstrating input cases and expected structured AI JSON outputs across different networking categories (**VLAN**, **Routing**, and **ACL**).

---

## Example 1: VLAN Misconfiguration (Layer 2)

### Input
```markdown
SYMPTOM:
PC-1 in Finance Dept cannot ping Server-1 on Switch-2. Local link is UP.

TOPOLOGY NOTE:
PC-1 (Fa0/5) -> Switch-1 (Fa0/24) -> Switch-2 (Fa0/10) -> Server-1. Target VLAN is 10.

SHOW COMMAND OUTPUTS:
Switch-1# show vlan brief
1 default active Fa0/3, Fa0/4, Fa0/5, Fa0/6
10 Finance active Fa0/1, Fa0/2

Switch-1# show interfaces fa0/5 switchport
Access Mode VLAN: 1 (default)

DETERMINISTIC RULE CHECKER RESULTS:
- [IF-001] Status: PASS | Message: All inspected interfaces are up and operational.
- [VLAN-001] Status: PASS | Message: Required VLAN 10 exists in database.
```

### Expected Structured Output
```json
{
  "root_cause": "Access port Fa0/5 on Switch-1 is assigned to VLAN 1 default instead of target VLAN 10 Finance.",
  "confidence": 0.95,
  "osi_layer": "Layer 2 - Data Link",
  "evidence": [
    "Switch-1# show vlan brief shows 1 default active Fa0/3, Fa0/4, Fa0/5, Fa0/6",
    "Switch-1# show interfaces fa0/5 switchport shows Access Mode VLAN: 1 (default)"
  ],
  "next_command": [
    "show interfaces fa0/5 status"
  ],
  "fix_steps": [
    "Enter configuration mode on Switch-1: configure terminal",
    "Select interface: interface FastEthernet0/5",
    "Assign port to VLAN 10: switchport access vlan 10",
    "Verify assignment with show vlan brief"
  ]
}
```

---

## Example 2: Missing Subnet Route (Layer 3)

### Input
```markdown
SYMPTOM:
Branch office router R2 cannot reach HQ subnet 10.10.0.0/16. Traceroute drops at R2.

TOPOLOGY NOTE:
Branch R2 (192.168.20.0/24) connected to HQ R1 via Serial 0/1/0 (10.0.0.0/30). OSPF routing enabled.

SHOW COMMAND OUTPUTS:
R2# show ip route
Codes: C - connected, S - static, O - OSPF
Gateway of last resort is not set
C 192.168.20.0/24 is directly connected, GigabitEthernet0/0
C 10.0.0.0/30 is directly connected, Serial0/1/0

R2# show ip ospf neighbor
(blank output)

DETERMINISTIC RULE CHECKER RESULTS:
- [IF-001] Status: PASS | Message: Interfaces up.
- [ROUTE-001] Status: FAIL | Message: Routing table is missing a route for destination 10.10.0.0/16.
```

### Expected Structured Output
```json
{
  "root_cause": "OSPF neighbor adjacency between R1 and R2 is down, causing missing route entry for HQ subnet 10.10.0.0/16 on R2.",
  "confidence": 0.90,
  "osi_layer": "Layer 3 - Network",
  "evidence": [
    "R2# show ip route contains no route for 10.10.0.0/16",
    "R2# show ip ospf neighbor output is blank",
    "Rule ROUTE-001 reported FAIL for destination 10.10.0.0/16"
  ],
  "next_command": [
    "show ip ospf interface Serial0/1/0",
    "show running-config | section router ospf"
  ],
  "fix_steps": [
    "Verify OSPF process configuration on R2 under router ospf 1",
    "Ensure network 10.0.0.0 0.0.0.3 area 0 statement is active on R2",
    "Verify hello/dead timers and subnet masks match R1 Serial0/1/0"
  ]
}
```

---

## Example 3: Access Control List Deny (Layer 4)

### Input
```markdown
SYMPTOM:
HR users in subnet 192.168.10.0/24 can ping Payroll Server 10.0.5.20, but HTTP web access (port 80) is denied.

TOPOLOGY NOTE:
HR Subnet (192.168.10.0/24) -> Router R1 (Gig0/0/1 outbound) -> Payroll Subnet (10.0.5.0/24).

SHOW COMMAND OUTPUTS:
R1# show access-lists 101
Extended IP access list 101
 10 deny tcp 192.168.10.0 0.0.0.255 host 10.0.5.20 eq www (156 matches)
 20 permit ip any any (450 matches)

R1# show ip interface GigabitEthernet0/0/1
 Outbound access list is 101

DETERMINISTIC RULE CHECKER RESULTS:
- [IF-001] Status: PASS | Message: Interface up.
```

### Expected Structured Output
```json
{
  "root_cause": "Outbound ACL 101 line 10 on interface GigabitEthernet0/0/1 explicitly denies TCP port 80 (www) traffic from 192.168.10.0/24 to Payroll Server 10.0.5.20.",
  "confidence": 0.95,
  "osi_layer": "Layer 4 - Transport",
  "evidence": [
    "R1# show access-lists 101 line 10: deny tcp 192.168.10.0 0.0.0.255 host 10.0.5.20 eq www (156 matches)",
    "R1# show ip interface GigabitEthernet0/0/1 shows Outbound access list is 101"
  ],
  "next_command": [
    "show access-lists 101"
  ],
  "fix_steps": [
    "Enter router global config mode: configure terminal",
    "Edit access-list 101 to replace line 10: no access-list 101 deny tcp 192.168.10.0 0.0.0.255 host 10.0.5.20 eq www",
    "Add permit rule: access-list 101 permit tcp 192.168.10.0 0.0.0.255 host 10.0.5.20 eq www",
    "Verify match counters reset or increment under permit rule"
  ]
}
```
