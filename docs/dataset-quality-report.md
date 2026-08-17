# NetSage AI - Dataset Quality Report (Phase 2)

This document provides a comprehensive quality audit and statistical breakdown of the **40 troubleshooting cases** in the NetSage AI dataset (`data/cases.csv`). 

---

## 📊 Dataset Summary

* **Total Troubleshooting Cases**: 40 (`CASE-001` through `CASE-040`)
* **Target Environment**: Cisco IOS / Packet Tracer network topologies
* **Primary Objective**: Provide deterministic, evidence-backed network fault scenarios for AI evaluation and rule verification.

---

### Cases per Concept

| Concept | Number of Cases | Case Identifiers |
| :--- | :---: | :--- |
| **VLAN** | 5 | `CASE-001`, `CASE-002`, `CASE-011`, `CASE-012`, `CASE-013` |
| **Default Gateway** | 5 | `CASE-003`, `CASE-014`, `CASE-015`, `CASE-016`, `CASE-017` |
| **DHCP** | 5 | `CASE-004`, `CASE-018`, `CASE-019`, `CASE-020`, `CASE-021` |
| **DNS** | 5 | `CASE-005`, `CASE-022`, `CASE-023`, `CASE-024`, `CASE-025` |
| **Routing** | 7 | `CASE-006`, `CASE-010`, `CASE-026`, `CASE-027`, `CASE-028`, `CASE-029`, `CASE-030` |
| **ACL** | 5 | `CASE-007`, `CASE-031`, `CASE-032`, `CASE-033`, `CASE-034` |
| **NAT** | 4 | `CASE-008`, `CASE-035`, `CASE-036`, `CASE-037` |
| **Wireless** | 4 | `CASE-009`, `CASE-038`, `CASE-039`, `CASE-040` |
| **Total** | **40** | |

---

### Cases per Severity

| Severity Level | Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **High** | 24 | 60.0% | Complete outage, missing subnets, broken gateways, security bypass, total DHCP/NAT failure |
| **Medium** | 14 | 35.0% | Single host/VLAN isolation, specific port ACL blocks, stale DNS records, disabled WLANs |
| **Low** | 2 | 5.0% | Non-critical CLI convenience settings, mistyped router domain lookup delays |
| **Total** | **40** | **100%** | |

---

### Cases per OSI Layer

| OSI Layer | Count | Primary Categories Included |
| :--- | :---: | :--- |
| **Layer 2 — Data Link** | 11 | VLAN, Switchport Access/Trunk, Native VLAN, Wireless 802.11/WPA2 |
| **Layer 3 — Network** | 18 | Default Gateway, Static & OSPF Routing, IP Subnetting, NAT, Layer 3 ACL |
| **Layer 4 — Transport** | 2 | TCP/UDP Port ACL filtering (SSH, HTTP/HTTPS) |
| **Layer 7 — Application** | 9 | DHCP (Scopes, Relay, Excluded IPs), DNS (Nameservers, Lookups, Host records) |
| **Total** | **40** | |

---

## 🌐 Coverage & Concept Diversity

All **eight foundational networking concepts** required by NetSage AI are fully represented. Each category includes multiple distinct failure vectors to avoid repetitive patterns:

1. **VLAN**: Wrong access VLAN assignment, trunk allowed-list pruning, missing VLAN database creation, native VLAN mismatch, switchport access vs trunk mode misconfiguration.
2. **Default Gateway**: Incorrect gateway IP configuration, missing gateway IP, gateway sub-interface administratively down, gateway IP subnet mismatch, down/down SVI interface.
3. **DHCP**: Missing `ip helper-address` relay, pool exhaustion (100% leased), globally disabled DHCP service, default-router option misconfiguration, missing excluded IP static address conflict.
4. **DNS**: Invalid DNS server IP on client, missing `ip name-server` on router, ACL blocking UDP port 53, stale DNS A-record mapping, missing `no ip domain-lookup`.
5. **Routing**: Missing static routes, unreachable static next-hop IP, unestablished OSPF neighbor adjacency, asymmetric missing return route, OSPF hello/dead timer mismatch, missing default route of last resort, unadvertised LAN network.
6. **ACL**: Outbound HTTP deny rule, standard ACL VTY line access-class restriction, unapplied global ACL on interface, sequence order mismatch (broad deny preceding permit), missing HTTPS permit line hitting implicit deny.
7. **NAT**: Missing `ip nat inside` directive on LAN interface, missing static NAT web server mapping, NAT ACL scope excluding client VLANs, dynamic NAT pool address exhaustion without `overload`.
8. **Wireless**: Missing VLAN database entry for WLAN SSID, RADIUS shared secret key mismatch, missing DHCP Option 43 for CAPWAP WLC discovery, administratively disabled WLAN status on WLC.

---

## 🔍 Evidence Quality & Logical Consistency

Every case in `data/cases.csv` follows strict evidence-based diagnostic rules:
* **Direct Proof**: The provided Cisco command output (`show vlan brief`, `show ip route`, `show access-lists`, `show ip interface brief`, `ipconfig`, `nslookup`, etc.) explicitly exposes the root cause.
* **Zero Contradictions**: Symptom statements align 100% with the provided topology notes and CLI output. For example:
  - If a route is missing, `show ip route` explicitly shows the route is missing.
  - If an interface is down, `show ip interface brief` explicitly reads `administratively down`.
  - If a VLAN is missing, it is excluded from `show vlan brief`.
* **Single Primary Fault**: Every scenario isolates exactly one primary fault so that deterministic rule checkers and LLM diagnosis engines can reach an unambiguous ground-truth classification.

---

## 🔄 Duplicate Prevention

Scenarios were carefully designed with unique topologies, IP schemes, device names, and failure modes to ensure no two cases are identical. Even within the same category (e.g. 7 Routing cases), each case tests a distinct networking principle (static routing, next-hop validation, asymmetric return routes, OSPF timers, default routes, passive interfaces, and area adjacencies).

---

## ✅ Validation Confirmation

All **40 troubleshooting cases** have been manually reviewed for:
1. Valid CSV syntax and escaped double quotes around multiline `show` command outputs.
2. Unique case identifiers (`CASE-001` through `CASE-040`).
3. 100% alignment between symptom, topology, show-command evidence, expected fault, OSI layer, concept, and severity rating.
