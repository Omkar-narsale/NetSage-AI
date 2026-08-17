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
### Phase 5 — Deterministic Rule Checker + Groq AI Integration (Completed)
* **Integration Pipeline** (`integration/diagnosis_pipeline.py`): End-to-end diagnosis pipeline (`DiagnosisPipeline`) combining Phase 3 deterministic rule results with Phase 4 Groq AI diagnosis.
* **Evidence Fusion Module** (`integration/evidence_fusion.py`): `EvidenceFusion` module evaluating agreement between rule checker findings and LLM root cause analysis.
* **Four Deterministic Agreement Categories**:
  1. `AGREE`: AI diagnosis aligns with failing deterministic rules without contradiction.
  2. `PARTIAL_AGREE`: AI and rule checker point to same fault category, or rules pass while AI diagnoses CLI evidence with high confidence.
  3. `CONFLICT`: Deterministic rules strongly indicate one fault (e.g. `IF-001` interface down) while AI identifies a different root cause (e.g. DNS failure). Flags `conflict_detected=True` and generates mandatory review warning.
  4. `INSUFFICIENT_EVIDENCE`: Neither deterministic rules nor AI model has sufficient evidence to establish a reliable diagnosis.
* **End-to-End Pipeline Architecture**:
  ```
  Evidence ➔ Rule Checker ➔ Rule Results ➔ Groq AI ➔ AI Diagnosis ➔ Evidence Fusion ➔ Agreement / Conflict ➔ Human Review
  ```
* **Evaluation Framework** (`evaluation/evaluate_integration.py` & `data/integrated_results.jsonl`): Evaluates full integrated pipeline against 40 lab cases, tracking agreement counts, accuracy %, and high-confidence conflicts (AI confidence >= 0.80 with status `CONFLICT`). Data leakage is strictly prevented by withholding `expected_fault` from AI prompt payloads.
### Phase 6 — Human Review & Responsible AI Logging (Completed)
* **Human Review Workflow Engine** (`review/review_manager.py` & `review/review_models.py`): Workflow manager enforcing that the human reviewer is the final authority. Every AI diagnosis must pass through human review (`PENDING` ➔ `ACCEPTED`, `EDITED`, or `REJECTED`).
* **Three Reviewer Decisions**:
  1. `ACCEPT`: Preserves AI diagnosis as final approved diagnosis.
  2. `EDIT`: Allows human reviewer to edit root cause, OSI layer, evidence, next commands, or fix steps. Requires mandatory `correction_reason`.
  3. `REJECT`: Rejects fundamentally incorrect AI output and records human ground-truth diagnosis. Requires mandatory `correction_reason`.
* **Original Output Preservation**: `ai_diagnosis` is NEVER overwritten or mutated. Both `ai_diagnosis` and `final_diagnosis` are stored in `data/review_records.jsonl` to measure model accuracy and human correction rates.
* **Responsible AI Audit Log** (`data/responsible_ai_log.csv`): Audit logger recording genuine cases where AI diagnosis was edited or rejected by a human reviewer. Logs 6 genuine human corrections (`CASE-006`, `CASE-010`, `CASE-016`, `CASE-020`, `CASE-027`, `CASE-033`).
* **End-to-End Governance Architecture**:
  ```
  AI ➔ Rule Checker + Evidence Fusion ➔ Human Review (Accept / Edit / Reject) ➔ Final Diagnosis ➔ Responsible AI Log
  ```
* **Unit Test Suite** (`tests/test_review.py`): 8 unit tests verifying decision validation, original AI output preservation, correction reason enforcement, and audit log isolation.
* *Note: The system does not automatically apply network fixes. Remediation steps are strictly presented for human review and approval.*

---

## 🔮 Project Roadmap

* **Phase 1** — Networking foundation and initial cases (Completed)
* **Phase 2** — Expand troubleshooting dataset (Completed)
* **Phase 3** — Deterministic Python rule checker (Completed)
* **Phase 4** — AI diagnosis engine (Completed)
* **Phase 5** — AI + rule checker integration (Completed)
* **Phase 6** — Human review & responsible AI logging (Completed)
* **Phase 7** — Dashboard and evaluation
* **Phase 8** — Final Packet Tracer demo
