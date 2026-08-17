# 🎯 Primary Demo Scenario: CASE-033 — ACL Sequence Order Conflict

## 1. Scenario Overview
* **Case ID**: `CASE-033`
* **Networking Concept**: Access Control List (ACL)
* **Severity**: `High`
* **Target OSI Layer**: `Layer 3 - Network` / `Layer 4 - Transport`
* **Problem Statement**: Finance workstation `PC-3` (`192.168.30.15/24`) cannot access the internal HTTP web server `Server-1` (`10.0.0.5:80`). Ping to gateway succeeds, but TCP port 80 connections time out.

---

## 2. Topology
```
[ Finance PC-3 ] (192.168.30.15/24)
        │
        ▼ (Access Port Fa0/10 - VLAN 30)
[ Switch-1 ]
        │ (Trunk Link Gi0/1)
        ▼ (Sub-interface Gi0/0.30 - 192.168.30.1)
[ Core Router R1 ] (ACL 105 applied inbound on Gi0/0.30)
        │ (Interface Gi0/1 - 10.0.0.1)
        ▼
[ Web Server-1 ] (10.0.0.5:80)
```

---

## 3. Reported Symptom
```text
C:\Users\Finance> curl http://10.0.0.5
curl: (7) Failed to connect to 10.0.0.5 port 80: Timed out

C:\Users\Finance> ping 10.0.0.5
Pinging 10.0.0.5 with 32 bytes of data:
Reply from 10.0.0.5: bytes=32 time=2ms TTL=127
```

---

## 4. Cisco IOS CLI Evidence
```text
R1# show access-lists 105
Extended IP access list 105
    10 deny ip 192.168.30.0 0.0.0.255 any (245 matches)
    20 permit tcp 192.168.30.0 0.0.0.255 host 10.0.0.5 eq www (0 matches)
    30 permit ip any any

R1# show ip interface GigabitEthernet0/0.30
GigabitEthernet0/0.30 is up, line protocol is up
  Internet address is 192.168.30.1/24
  Inbound access list is 105
```

---

## 5. Phase 3 Deterministic Rule Checker Finding
* **Rule Checked**: `IF-001` (Interface Status), `IP-001` (Duplicate IP), `IP-002` (Subnet Alignment), `GW-001` (Gateway Reachability).
* **Deterministic Output**:
  - `IF-001`: `PASS` (Interface Gi0/0.30 is UP/UP)
  - `GW-001`: `PASS` (Default gateway 192.168.30.1 is reachable)
  - Rule Checker identifies that physical and IP layers are operational, narrowing scope to ACL line ordering.

---

## 6. Phase 4 Groq AI Engine Diagnosis
```json
{
  "root_cause": "Extended ACL 105 line 10 contains a broad 'deny ip' statement that evaluates before line 20 'permit tcp', causing all HTTP traffic from 192.168.30.0/24 to be dropped on line 10.",
  "confidence": 0.97,
  "osi_layer": "Layer 3 - Network / Layer 4 - Transport",
  "evidence": [
    "line 10 deny ip 192.168.30.0 0.0.0.255 any (245 matches)",
    "line 20 permit tcp 192.168.30.0 0.0.0.255 host 10.0.0.5 eq www (0 matches)"
  ],
  "next_command": [
    "show access-lists 105"
  ],
  "fix_steps": [
    "Enter access list configuration mode on Router R1: ip access-list extended 105",
    "Delete broad deny statement: no 10 deny ip 192.168.30.0 0.0.0.255 any",
    "Insert specific permit rule at top: 10 permit tcp 192.168.30.0 0.0.0.255 host 10.0.0.5 eq www",
    "Add default deny at line 20 if required: 20 deny ip 192.168.30.0 0.0.0.255 any"
  ]
}
```

---

## 7. Phase 5 Evidence Fusion & Phase 6 Human Review
* **Phase 5 Fusion Status**: `AGREE` (No rule conflicts detected).
* **Phase 6 Reviewer Decision**: `EDIT`
* **Human Correction Summary**: Specified exact top-to-bottom ACL sequence re-ordering requirements under `ip access-list extended 105`.
* **Correction Reason**: AI identified ACL rule drop; human reviewer refined root cause to highlight Cisco IOS top-to-bottom first-match rule processing logic.
* **Final Approved Root Cause**: Extended ACL 105 sequence error: Line 10 contains a broad deny ip rule preceding the specific permit tcp rule at line 20, causing all Finance traffic to match line 10 first.

---

## 8. Human Remediation (Cisco IOS Commands)
```text
R1# configure terminal
R1(config)# ip access-list extended 105
R1(config-ext-nacl)# no 10
R1(config-ext-nacl)# 10 permit tcp 192.168.30.0 0.0.0.255 host 10.0.0.5 eq www
R1(config-ext-nacl)# 20 deny ip 192.168.30.0 0.0.0.255 any
R1(config-ext-nacl)# end
```

---

## 9. Verification
```text
R1# show access-lists 105
Extended IP access list 105
    10 permit tcp 192.168.30.0 0.0.0.255 host 10.0.0.5 eq www (12 matches)
    20 deny ip 192.168.30.0 0.0.0.255 any (245 matches)
    30 permit ip any any

C:\Users\Finance> curl http://10.0.0.5
<!DOCTYPE html><html><head><title>Datacenter Web Server 1</title></head><body>HTTP 200 OK</body></html>
```

*Safety Note: NetSage AI generates diagnostic recommendations strictly for human authorization and does not execute CLI commands on hardware.*
