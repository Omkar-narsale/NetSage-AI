# ⚡ NetSage AI — AI-Assisted Cisco Network Troubleshooting

NetSage AI is an AI-assisted Cisco/Packet Tracer network troubleshooting system combining **deterministic Python rule checking**, **Groq LLaMA 3.3 LLM reasoning**, **evidence fusion**, and **human-in-the-loop governance** into an interactive dark-themed Network Operations Center (NOC) dashboard.

---

## 📌 Problem Statement
Modern enterprise networks generate massive volumes of CLI diagnostic data when faults occur—such as VLAN mismatches, ACL sequence blocks, default gateway misconfigurations, or routing drops. Traditional troubleshooting relies on manual inspection, which is slow and error-prone. Pure LLM approaches risk hallucinating CLI syntax or recommending dangerous configuration changes.

---

## 💡 Solution
NetSage AI addresses these challenges with a **7-Stage Governed Troubleshooting Pipeline**:
1. **Deterministic First Pass**: Executes Python rule checks (`IF-001`, `IP-001`, `IP-002`, `GW-001`, `VLAN-001`, `ROUTE-001`) to verify physical and IP layers without LLM hallucinations.
2. **Groq LLaMA 3.3 LLM Reasoning**: Analyzes CLI evidence to produce structured JSON diagnoses containing cited evidence, next CLI commands, and remediation steps.
3. **Evidence Fusion**: Cross-evaluates rule checker findings against LLM root cause analysis (`AGREE`, `PARTIAL_AGREE`, `CONFLICT`, `INSUFFICIENT_EVIDENCE`).
4. **Human-in-the-Loop Oversight**: Enforces that the human reviewer is the ultimate decision-maker (`ACCEPT`, `EDIT`, `REJECT`).
5. **Responsible AI Audit Logging**: Records all human edits and rejections in `data/responsible_ai_log.csv`.

---

## 🏗️ Architecture & Pipeline Flow

```
[ Case Evidence ] ➔ [ Rule Checker ] ──┐
                                     ├──➔ [ Evidence Fusion ] ➔ [ Human Review ] ➔ [ Final Diagnosis ] ➔ [ NOC Dashboard ]
[ CLI Output ]    ➔ [ Groq AI Engine ] ──┘
```

---

## ✨ Features
* **40 Troubleshooting Cases**: Spanning VLAN, Default Gateway, DHCP, DNS, Routing, ACL, NAT, and Wireless.
* **Deterministic Rule Checker**: 6 core rules executing without external dependencies.
* **Groq AI Diagnosis Engine**: Powered by `llama-3.3-70b-versatile` with native Groq API support.
* **Evidence Fusion Module**: Automated agreement classification and conflict flagging.
* **Human Authority Principle**: Original AI diagnosis is NEVER overwritten; human reviewer decisions control final output.
* **Responsible AI Audit Log**: Tracks high-confidence AI mistakes and human corrections.
* **Dark NOC Streamlit Dashboard**: 5 interactive pages (Overview, Case Explorer, AI vs Human, Responsible AI, Evaluation) with zero API call overhead on page refreshes.

---

## 🛠️ Tech Stack
* **Language**: Python 3.8+
* **LLM Engine**: Groq API (`llama-3.3-70b-versatile`)
* **Dashboard**: Streamlit (`streamlit>=1.25.0`), Plotly
* **Testing**: Python `unittest` framework (54 unit tests)

---

## 📂 Project Structure

```
NetSage-AI/
│
├── app.py                          # Main Streamlit Dashboard Application
├── requirements.txt                # Python Dependencies
├── .env.example                    # Environment Variables Template
├── .gitignore                      # Git Ignore Specification
│
├── ai/                             # Groq AI Diagnosis Module
│   ├── diagnosis.py                # DiagnosisEngine & Groq API Integration
│   ├── prompts.py                  # Prompt Generation Logic
│   └── schemas.py                  # Pydantic / Dataclass Response Schemas
│
├── rules/                          # Deterministic Python Rule Checker Engine
│   ├── checker.py                  # RuleChecker Main Orchestrator
│   ├── interface_rules.py          # IF-001 Interface Down Check
│   ├── ip_rules.py                 # IP-001, IP-002, GW-001 Checks
│   ├── vlan_rules.py               # VLAN-001 Missing VLAN Check
│   └── routing_rules.py            # ROUTE-001 Missing Route Check
│
├── integration/                    # Phase 5 Evidence Fusion Module
│   ├── diagnosis_pipeline.py       # DiagnosisPipeline End-to-End Orchestrator
│   └── evidence_fusion.py          # EvidenceFusion & Agreement Status Logic
│
├── review/                         # Phase 6 Human Review & Audit Module
│   ├── review_manager.py           # ReviewManager Workflow Engine
│   ├── review_models.py            # ReviewRecord & ReviewDecision Specs
│   ├── review_store.py             # ReviewStore Persistence & CSV Logger
│   └── run_review_session.py       # Review Session Executor
│
├── dashboard/                      # Phase 7 Streamlit UI Components
│   ├── styles.py                   # Custom Dark NOC CSS & HTML Cards
│   ├── charts.py                   # Dark Plotly & Streamlit Charts
│   ├── case_view.py                # 7-Stage Visual Timeline Explorer
│   └── metrics.py                  # KPI Card Formatting Helpers
│
├── evaluation/                     # Evaluation Harnesses & Metrics
│   ├── metrics.py                  # Reusable Metric Calculations
│   ├── evaluate_ai.py              # AI Engine Evaluator
│   └── evaluate_integration.py     # Pipeline Evaluator
│
├── data/                           # Ground Truth & Pre-computed Dataset
│   ├── cases.csv                   # 40 Troubleshooting Cases
│   ├── ai_diagnoses.jsonl          # AI Engine Diagnoses
│   ├── integrated_results.jsonl    # Pipeline Fusion Results
│   ├── review_records.jsonl        # Human Review Records
│   └── responsible_ai_log.csv      # Audit Log of Human Corrections
│
├── docs/                           # Documentation Sitemap
│   ├── architecture.md             # System Architecture & Pipeline Flow
│   ├── demo-scenario.md            # Flagship Demo Case Walkthrough (CASE-033)
│   ├── demo-script.md              # 10-Minute Presentation Script
│   ├── final-test-report.md        # Comprehensive Test Execution Report
│   └── requirements-traceability.md# Requirements Traceability Matrix
│
└── tests/                          # Automated Unit Test Suites
    ├── test_rules.py               # Phase 3 Rule Checker Tests (22 tests)
    ├── test_ai_engine.py           # Phase 4 AI Engine Tests (9 tests)
    ├── test_integration.py        # Phase 5 Integration Tests (6 tests)
    ├── test_review.py             # Phase 6 Human Review Tests (8 tests)
    ├── test_dashboard_metrics.py  # Phase 7 Dashboard Tests (9 tests)
    └── test_end_to_end.py         # Phase 8 End-to-End Tests (8 tests)
```

---

## ⚡ Quick Start & Setup

### 1. Clone Repository & Environment Setup
```bash
git clone https://github.com/Omkar-narsale/NetSage-AI.git
cd NetSage-AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Groq API key:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```
*(Note: If `GROQ_API_KEY` is omitted, NetSage AI operates cleanly in offline mock mode).*

---

## 🧪 Running Automated Unit Tests
Run all 54 unit tests across Phases 3 through 8:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🖥️ Running the Streamlit Dashboard
Launch the interactive Network Operations Center dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🎯 Primary Demo Case (`CASE-033`)
* **Problem**: Finance workstation `PC-3` cannot access web server `10.0.0.5:80`.
* **Rule Finding**: `IF-001` PASS, `GW-001` PASS (Physical and IP layers operational).
* **AI Diagnosis**: Groq AI identifies Extended ACL 105 line 10 broad `deny ip` rule matching traffic before line 20 `permit tcp`.
* **Human Review**: Reviewer submits `EDIT` to specify exact top-to-bottom CLI line sequence matching logic.
* **Fix**: Re-order ACL 105 lines under `ip access-list extended 105`.

---

## 🛡️ Safety & Governance Boundary
NetSage AI is a **diagnostic recommendation assistant**. It does **NOT** automatically execute CLI commands or modify network router configurations. The human reviewer remains the sole authority responsible for reviewing, approving, and applying configuration changes.
