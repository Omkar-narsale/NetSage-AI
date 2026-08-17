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
### Phase 3 — Deterministic Rule Checker (Completed)
* **Deterministic Rule Engine** (`rules/checker.py`): Central rule orchestration engine (`RuleChecker`) executing non-probabilistic Python rule checks against structured evidence payloads.
* **Six Core Rules**:
  1. `IF-001` — **Interface Down Check**: Detects `administratively down` and down line protocol interface states.
  2. `IP-001` — **Duplicate IP Check**: Detects duplicate IP address allocations across network devices.
  3. `IP-002` — **Subnet Alignment Check**: Validates host IP address and mask against expected subnet boundaries.
  4. `GW-001` — **Default Gateway Mismatch Check**: Validates default gateway IP alignment with host subnet and router IP.
  5. `VLAN-001` — **Missing VLAN Check**: Verifies required VLAN presence in switch VLAN database.
  6. `ROUTE-001` — **Missing Route Check**: Verifies active routing table entries for target destination subnets.
* **Deterministic Status Output**: Every rule produces a structured `PASS`, `FAIL`, or `UNKNOWN` result with severity, evidence, and actionable recommendation. If evidence is incomplete or missing, rules return `UNKNOWN` without guessing or throwing exceptions.
* **Non-AI Layer**: This layer operates 100% deterministically without LLM calls to provide fast, zero-cost, verifiable validation. In later phases, this rule checker works alongside the AI diagnosis engine to pre-filter basic configuration errors before AI inference.
* **Unit Test Suite** (`tests/test_rules.py`): Comprehensive 22-test suite verifying `PASS`, `FAIL`, and `UNKNOWN` states across all rules.
### Phase 4 — AI Diagnosis Engine (Completed)
* **Structured AI Diagnosis Engine** (`ai/diagnosis.py`): Modular LLM provider integration (`DiagnosisEngine`) executing evidence-grounded troubleshooting analysis against network symptoms, topology notes, Cisco CLI outputs, and Phase 3 rule checker results.
* **Strict Output Schema Validation** (`ai/schemas.py`): Enforces validated JSON response format containing `root_cause`, bounded `confidence` (float between 0.0 and 1.0), `osi_layer`, grounded `evidence` quotes, `next_command` recommendations, and `fix_steps`.
* **Evidence Grounding & Safety**: Models are strictly instructed to cite only supplied evidence without inventing command outputs, IP addresses, VLAN IDs, or topology details.
* **Next-Command Recommendations**: When evidence is incomplete or ambiguous, the AI lowers its confidence score and recommends specific diagnostic CLI commands.
* **Deterministic Rule Checker Integration**: Combines Phase 3 Python rule checker results (`PASS`, `FAIL`, `UNKNOWN`) into the AI prompt payload while preserving independent LLM analysis.
* **Evaluation Framework** (`evaluation/evaluate_ai.py` & `data/ai_diagnoses.jsonl`): Evaluation harness measuring AI accuracy, average confidence, high-confidence error rates, and insufficient evidence flags against the 40 lab cases in `data/cases.csv`. Data leakage is strictly prevented by withholding `expected_fault` from prompt payloads during evaluation.
* **Prompt Specification & Worked Examples**: Formatted prompt templates in `prompts/diagnose_prompt.md` and worked examples across VLAN, Routing, and ACL categories in `prompts/worked_examples.md`.
* *Note: Human review is intentionally implemented in a later phase. The AI diagnosis engine generates remediation recommendations strictly for human review and does not automatically modify network configurations.*

---

## 🔮 Project Roadmap

* **Phase 1** — Networking foundation and initial cases (Completed)
* **Phase 2** — Expand troubleshooting dataset (Completed)
* **Phase 3** — Deterministic Python rule checker (Completed)
* **Phase 4** — AI diagnosis engine (Completed)
* **Phase 5** — AI + rule checker integration
* **Phase 6** — Human review
* **Phase 7** — Dashboard and evaluation
* **Phase 8** — Final Packet Tracer demo
