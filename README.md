# NetSage AI

**NetSage AI** is an AI-assisted troubleshooting helper for Cisco-style Packet Tracer and lab networks. It is designed to assist network engineers, particularly junior engineers, by analyzing network symptoms, topology notes, and `show`-command outputs to rapidly identify root causes and recommend actionable remediation steps with evidence.

---

## 🎯 The Problem NetSage AI Solves

Junior network engineers and students often know individual Cisco IOS commands but struggle to connect a high-level symptom (e.g., "PC cannot reach server") to the exact underlying root cause across different OSI layers. 

When a host loses connectivity, the issue could stem from misconfigured VLANs, wrong gateway settings, missing DHCP relay, DNS misconfiguration, broken routing adjacencies, restrictive ACLs, or NAT interface mapping errors.

NetSage AI bridges this gap by:
1. Parsing network symptoms and command outputs.
2. Formulating structured, evidence-backed diagnostic recommendations.
3. Enforcing mandatory human-in-the-loop review before applying any network fix.

---

## 🏷️ Supported Networking Fault Categories

NetSage AI focuses on eight core networking categories:

1. **VLAN** (Layer 2 Data Link — Port assignments, 802.1Q trunking, missing VLANs)
2. **Default Gateway** (Layer 3 Network — IP mismatch, subnet misalignment, interface shutdown)
3. **DHCP** (Layer 7 Application — Scope exhaustion, missing `ip helper-address` relay)
4. **DNS** (Layer 7 Application — Unreachable name servers, domain lookup failures)
5. **Routing** (Layer 3 Network — Missing static routes, unreachable next-hops, OSPF neighbor down)
6. **ACL** (Layer 3/4 Network & Transport — Outbound/inbound explicit deny rules, port filtering)
7. **NAT** (Layer 3/4 Network & Transport — Missing `ip nat inside`/`outside` directives, pool exhaustion)
8. **Wireless** (Layer 1/2 Physical & Data Link — WLAN-to-VLAN mapping, AP/WLC trunking)

---

## 🚀 Project Status

### Phase 1 — Networking Foundation & Initial Dataset (Completed)
* **Comprehensive Troubleshooting Guide** (`docs/networking-fault-guide.md`): Detailed reference guide for all eight fault categories, explaining symptoms, root causes, relevant `show` commands, OSI layer mappings, and step-by-step example scenarios.
* **Initial Case Dataset** (`data/initial_cases.csv`): Initial 10 validated Cisco-style troubleshooting scenarios.

### Phase 2 — Troubleshooting Dataset Expansion (Completed)
* **Expanded Dataset** (`data/cases.csv`): 40 total validated Cisco-style troubleshooting cases.
* **8 Networking Concepts**: Complete coverage across VLAN, Default Gateway, DHCP, DNS, Routing, ACL, NAT, and Wireless.
* **Cisco-style Evidence**: Detailed `show` command outputs supporting expected faults.
* **Metadata Tagging**: Explicit OSI layer, concept tag, topology notes, and severity labels (High, Medium, Low).
* **Dataset Quality Report** (`docs/dataset-quality-report.md`): Statistical summary, coverage mapping, evidence quality standards, and duplicate checks.

---

## 🔮 Project Roadmap

* **Phase 1** — Networking foundation and initial cases (Completed)
* **Phase 2** — Expand troubleshooting dataset (Completed)
* **Phase 3** — Deterministic Python rule checker
* **Phase 4** — AI diagnosis engine
* **Phase 5** — AI + rule checker integration
* **Phase 6** — Human review
* **Phase 7** — Dashboard and evaluation
* **Phase 8** — Final Packet Tracer demo
