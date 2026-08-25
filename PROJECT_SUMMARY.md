# ⚡ NetSage AI — Comprehensive Project Summary Document

> **Document Type:** Project Architectural & Executive Summary  
> **Target Audience:** Technical Leads, Network Engineers, Responsible AI Reviewers, Project Stakeholders  
> **System Version:** 1.0.0 (Production Ready)  
> **Test Status:** 62 / 62 Tests Passed (100.0% Pass Rate)  

---

## 1. 📌 Executive Overview

**NetSage AI** is an enterprise-grade, evidence-driven Cisco network troubleshooting system. It bridges the gap between deterministic rule-based network diagnostic verification and advanced LLM natural language reasoning, while enforcing strict **Human-in-the-Loop (HITL) Governance**.

Traditional network troubleshooting relying purely on manual CLI analysis is slow and error-prone. On the other hand, relying unguided on LLMs introduces severe operational risks such as hallucinations, invalid Cisco IOS syntax, or unauthorized network modifications. NetSage AI resolves this by placing a deterministic verification engine alongside **Groq LLaMA 3.3 70B**, synthesizing their outputs through an **Evidence Fusion Engine**, and requiring **Human Authority** approval before any recommendation is finalized.

---

## 2. 📊 Core Metrics & Project Specifications

| Metric / Specification | Value / Description |
| :--- | :--- |
| **Troubleshooting Dataset** | **40 Lab Cases** spanning 8 fundamental Cisco networking domains |
| **Deterministic Rules Engine** | **6 Python Rules** (`IF-001`, `IP-001`, `IP-002`, `GW-001`, `VLAN-001`, `ROUTE-001`) |
| **AI Diagnosis Engine** | **Groq LLaMA 3.3 70B** (`llama-3.3-70b-versatile`) with structured JSON schema |
| **Evidence Fusion Engine** | **4 Agreement Categories** (`AGREE`, `PARTIAL_AGREE`, `CONFLICT`, `INSUFFICIENT_EVIDENCE`) |
| **Governance Principles** | **Human Authority Principle** with actions (`ACCEPT`, `EDIT`, `REJECT`) |
| **Responsible AI Audit Log** | **6 Genuine Human Corrections** (`CASE-006`, `CASE-010`, `CASE-016`, `CASE-020`, `CASE-027`, `CASE-033`) |
| **NOC Operations Dashboard** | **5 Interactive Pages** (Overview, Case Explorer, AI vs Human, Responsible AI, Evaluation) |
| **Automated Test Coverage** | **62 Unit & Integration Tests** (100.0% pass rate in < 0.8s) |

---

## 3. 🏗️ System Architecture & Workflow Pipeline

NetSage AI processes diagnostic requests through a sequential, non-bypassable 5-stage pipeline:

```
[ 1. CLI Diagnostic Input ]
           │
           ├───────────────────────────────┐
           ▼                               ▼
[ Phase 3: Python Rule Engine ]   [ Phase 4: Groq AI Engine ]
(Deterministic Verification)      (LLaMA 3.3 70B Reasoning)
           │                               │
           └───────────────┬───────────────┘
                           ▼
             [ Phase 5: Evidence Fusion ]
             (Cross-Evaluate AI vs Rules)
                           │
                           ▼
             [ Phase 6: Human Governance ]
             (ACCEPT / EDIT / REJECT)
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
[ Responsible AI Audit Log ]      [ Streamlit NOC Dashboard ]
(`responsible_ai_log.csv`)        (Visual Operations & Analytics)
```

### Pipeline Stage Details

1. **CLI Case Evidence Input (Phase 2 Dataset)**
   - Accepts raw CLI outputs (`show interface`, `show ip interface brief`, `show running-config`, `show ip route`, `show access-lists`, `ping`, `traceroute`).
   - Covered domains: VLAN, Default Gateway, DHCP, DNS, Routing (OSPF/Static), ACL, NAT, Wireless.

2. **Deterministic Rule Engine (Phase 3)**
   - Executes 6 zero-dependency Python rules to detect ground-truth network state without LLM hallucination risk.
   - Evaluates physical status, IP duplication, subnet mismatches, gateway reachability, VLAN tags, and routing table presence.

3. **Groq AI Diagnosis Engine (Phase 4)**
   - Sends structured prompt payloads to Groq (`llama-3.3-70b-versatile`).
   - Enforces strict Pydantic JSON outputs detailing `root_cause`, `confidence`, `osi_layer`, `evidence`, `next_command`, and `fix_steps`.

4. **Evidence Fusion Engine (Phase 5)**
   - Cross-references LLM diagnosis against deterministic rule results.
   - Computes agreement category (`AGREE`, `PARTIAL_AGREE`, `CONFLICT`, `INSUFFICIENT_EVIDENCE`) and flags contradictions (`conflict_detected`).

5. **Human Governance & Audit Logging (Phase 6)**
   - Presents synthesized findings to a human network engineer.
   - Enforces Human Authority: reviewer can `ACCEPT` (85.0%), `EDIT` (12.5%), or `REJECT` (2.5%) the AI diagnosis.
   - Preserves original raw AI output untouched for auditability and logs all human overrides to `responsible_ai_log.csv`.

---

## 4. 📂 Repository Sitemap & Directory Structure

```
NetSage-AI/
├── app.py                      # Streamlit Operations Dashboard main launcher
├── requirements.txt            # Project dependencies (streamlit, groq, plotly, pydantic)
├── .env.example                # Template for environment configuration
├── README.md                   # Primary project readme documentation
│
├── ai/                         # Phase 4: Groq AI Diagnosis Module
│   ├── diagnosis.py            # AI Engine handler (Groq API client & fallback logic)
│   ├── prompts.py              # System & user prompt templates for network diagnosis
│   └── schemas.py              # Pydantic JSON schemas for diagnosis responses
│
├── rules/                      # Phase 3: Deterministic Rule Checker Engine
│   ├── checker.py              # Rule suite runner & result aggregator
│   ├── interface_rules.py      # IF-001: Physical interface status check
│   ├── ip_rules.py             # IP-001 (Duplicate IP) & IP-002 (Subnet Mismatch)
│   ├── routing_rules.py        # GW-001 (Gateway Reachability) & ROUTE-001 (Route Table)
│   └── vlan_rules.py           # VLAN-001: Missing VLAN database entry check
│
├── integration/                # Phase 5: Evidence Fusion Engine
│   ├── diagnosis_pipeline.py   # End-to-end processing pipeline orchestrator
│   └── evidence_fusion.py      # Rule vs AI cross-evaluation & conflict detector
│
├── review/                     # Phase 6: Human Review & Governance
│   ├── review_manager.py       # Decision processor (ACCEPT, EDIT, REJECT)
│   ├── review_models.py        # Dataclass models for review records
│   ├── review_store.py         # JSONL persistence store for human review logs
│   └── run_review_session.py   # CLI session launcher for human reviewer batch processing
│
├── dashboard/                  # Streamlit UI Components & Pages
│   ├── case_view.py            # Interactive case timeline renderer
│   ├── charts.py               # Plotly visual charts generator
│   └── metrics.py              # Dashboard KPI metric calculators
│
├── evaluation/                 # Metrics & Evaluation Harness
│   ├── evaluate_ai.py          # AI accuracy and JSON schema validator harness
│   ├── evaluate_integration.py # Evidence fusion performance evaluator
│   └── metrics.py              # Overall precision, recall, & agreement score metrics
│
├── ui/                         # Visual Design & Styling System
│   ├── styles.css              # Custom Dark NOC CSS stylesheet with Glassmorphism
│   ├── theme.py                # CSS theme loader
│   ├── components.py           # Custom HTML components (Bento cards, badges)
│   └── sidebar.py              # Dashboard sidebar navigation menu
│
├── data/                       # Operational Datasets & Audit Records
│   ├── cases.csv               # 40 core troubleshooting cases dataset
│   ├── ai_diagnoses.jsonl      # Pre-computed AI diagnoses outputs
│   ├── integrated_results.jsonl# Pre-computed Evidence Fusion records
│   ├── review_records.jsonl    # Pre-computed Human Review records
│   └── responsible_ai_log.csv  # Responsible AI audit log (6 human corrections)
│
├── docs/                       # Project Documentation & Architectural Artifacts
│   ├── architecture.md         # Full architectural specification & diagrams
│   ├── dataset-quality-report.md# Quality analysis of 40 cases dataset
│   ├── demo-scenario.md        # Deep-dive into primary demo (CASE-033)
│   ├── demo-script.md          # 10-minute presentation guide
│   ├── final-test-report.md    # Automated test suite execution summary
│   ├── networking-fault-guide.md# Field reference for Cisco network troubleshooting
│   └── requirements-traceability.md# Requirement mapping matrix
│
└── tests/                      # Automated Unit & Integration Test Suite
    ├── test_rules.py           # 22 tests for Phase 3 Deterministic Rules
    ├── test_ai_engine.py       # 9 tests for Phase 4 Groq AI Engine
    ├── test_integration.py     # 6 tests for Phase 5 Evidence Fusion
    ├── test_review.py          # 8 tests for Phase 6 Human Review & Governance
    ├── test_dashboard_metrics.py# 9 tests for Dashboard Analytics & Safety
    └── test_end_to_end.py      # 8 tests for End-to-End Pipeline
```

---

## 5. 🖥️ Streamlit NOC Operations Dashboard

The interactive Streamlit dashboard (`app.py`) provides full operational visibility and governance tools across 5 pages:

1. **Overview Page**: High-level KPIs (Total Cases, Rule Pass Rate, AI Confidence, Human Agreement Rate, Override Count), issue distribution by network category, severity breakdown, and agreement fusion pie chart.
2. **Case Explorer Page**: 7-stage visual troubleshooting timeline per case (`01 SYMPTOM` ➔ `02 EVIDENCE` ➔ `03 RULE RESULTS` ➔ `04 AI DIAGNOSIS` ➔ `05 FUSION RESULT` ➔ `06 HUMAN REVIEW` ➔ `07 FINAL APPROVED DIAGNOSIS`).
3. **AI vs Human Page**: Side-by-side decision breakdown (`ACCEPT`, `EDIT`, `REJECT`), error breakdown by domain, and interactive filtering matrix.
4. **Responsible AI Page**: Dedicated audit table displaying human overrides from `responsible_ai_log.csv` and expandable cards for high-confidence AI misdiagnoses.
5. **Evaluation Page**: Comprehensive evaluation metrics report detailing precision, recall, schema validity, rule coverage, and pipeline execution latencies.

---

## 6. 🧪 Test Suite & Quality Verification

NetSage AI includes **62 automated tests** with **100.0% pass rate** executed via Python's standard `unittest` framework:

| Test Module | Coverage Area | Test Count | Status |
| :--- | :--- | :---: | :---: |
| `tests/test_rules.py` | Individual rule functions (`IF-001` to `ROUTE-001`) and edge cases | **22** | **PASS** |
| `tests/test_ai_engine.py` | Groq API responses, JSON schema validation, and offline fallback | **9** | **PASS** |
| `tests/test_integration.py` | Evidence fusion, agreement scoring, and conflict detection | **6** | **PASS** |
| `tests/test_review.py` | Human decision enforcement (`ACCEPT`/`EDIT`/`REJECT`) & audit CSV logging | **8** | **PASS** |
| `tests/test_dashboard_metrics.py` | Metrics calculation, edge cases, zero-division protection | **9** | **PASS** |
| `tests/test_end_to_end.py` | Full pipeline execution across 8 Cisco networking concepts | **8** | **PASS** |

---

## 7. 🎬 Primary Demo Walkthrough (`CASE-033`)

* **Scenario**: Extended Access Control List (ACL) Sequence Order Conflict.
* **Symptom**: Workstation `PC-3` (`192.168.30.15/24`) cannot reach Web Server (`10.0.0.5:80`). Ping to default gateway works.
* **Phase 3 Verification**: `IF-001` PASS, `GW-001` PASS (Physical and IP connectivity operational).
* **Phase 4 Groq AI Diagnosis**: AI detects line 10 broad `deny ip` rule matching traffic before line 20 `permit tcp 192.168.30.0/24 host 10.0.0.5 eq 80`.
* **Phase 5 Fusion**: Categorized as `AGREE` with rules.
* **Phase 6 Human Governance**: Human reviewer executes `EDIT` action to clarify Cisco IOS top-to-bottom first-match rule processing mechanics.
* **Audit Trail**: Recorded in `responsible_ai_log.csv` with original AI diagnosis preserved.

---

## 8. 🚀 Quick Start & Environment Execution

### Prerequisites
- Python 3.8+
- Groq API Key (Optional; system defaults to offline mock mode if absent)

### Installation & Setup

1. **Clone repository and create virtual environment:**
   ```bash
   git clone https://github.com/Omkar-narsale/NetSage-AI.git
   cd NetSage-AI
   python -m venv venv
   # Activate environment:
   # Windows: venv\Scripts\activate
   # Linux/macOS: source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and insert your GROQ_API_KEY if available
   ```

4. **Run Unit & Integration Tests:**
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

5. **Launch Operations Dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## 🛡️ Safety Boundary & Disclaimer

NetSage AI operates strictly as an **advisory diagnostic system**. It generates verified recommendations and CLI remediation commands, but **does NOT automatically execute CLI commands** or push configuration changes to live network hardware. Final execution authority rests entirely with the human network administrator.
