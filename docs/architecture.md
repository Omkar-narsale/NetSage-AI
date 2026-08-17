# 🏗️ NetSage AI — System Architecture & Data Flow

NetSage AI is an AI-assisted network troubleshooting architecture combining **deterministic rule checking**, **Groq LLaMA 3.3 LLM reasoning**, and **human-in-the-loop governance**.

---

## 1. End-to-End Pipeline Architecture

```
                       [ Network Case / Evidence ]
                                    │
                                    ▼
                      [ Stage 1: Evidence Preparation ]
                     (Symptom, Topology, Show Outputs)
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
[ Stage 2: Rule Checker ]                       [ Stage 3: Groq AI Engine ]
 (IF-001, IP-001, IP-002,                       (LLaMA 3.3 70B JSON Schema)
 GW-001, VLAN-001, ROUTE-001)                                │
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    ▼
                       [ Stage 4: Evidence Fusion ]
               (AGREE, PARTIAL_AGREE, CONFLICT, INSUFFICIENT)
                                    │
                                    ▼
                       [ Stage 5: Human Reviewer ]
                      (ACCEPT  |  EDIT  |  REJECT)
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
[ Stage 6: Final Diagnosis ]                       [ Stage 7: Responsible AI ]
 (Human Approved Root Cause)                       (data/responsible_ai_log.csv)
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    ▼
                      [ Streamlit Operations NOC ]
                        (app.py - Zero API Calls)
```

---

## 2. Component Descriptions

### Stage 1: Evidence Preparation
Extracts structured network symptom descriptions, topology notes, and raw Cisco IOS CLI `show` command outputs (e.g. `show vlan brief`, `show ip route`, `show access-lists`, `show ip interface`).

### Stage 2: Deterministic Rule Checker (`rules/`)
Python rule engine evaluating empirical network configuration rules without LLMs:
* `IF-001`: Interface Down Check
* `IP-001`: Duplicate IP Address Detection
* `IP-002`: Subnet Mask Alignment
* `GW-001`: Default Gateway Reachability Mismatch
* `VLAN-001`: Missing VLAN Database Entry
* `ROUTE-001`: Missing Routing Table Entry

### Stage 3: Groq AI Diagnosis Engine (`ai/`)
LLM diagnosis engine powered by Groq API (`llama-3.3-70b-versatile`). Generates strict JSON payloads containing:
* `root_cause`: Concise diagnosis
* `confidence`: Score between 0.00 and 1.00
* `osi_layer`: Target OSI layer (Layer 1 through Layer 7)
* `evidence`: Cited CLI output snippets
* `next_command`: Recommended diagnostic CLI commands
* `fix_steps`: Step-by-step Cisco IOS remediation steps

### Stage 4: Evidence Fusion (`integration/`)
Compares rule checker outputs (`PASS`, `FAIL`, `UNKNOWN`) against LLM diagnoses:
* `AGREE`: Deterministic findings align with AI diagnosis.
* `PARTIAL_AGREE`: Rule checker and AI point to same domain but details differ.
* `CONFLICT`: Rule checker directly contradicts AI diagnosis (e.g. interface down vs DNS error). Flags `conflict_detected=True`.
* `INSUFFICIENT_EVIDENCE`: Neither rules nor AI have sufficient data.

### Stage 5 & 6: Human Review & Final Diagnosis (`review/`)
Enforces the **Human Authority Principle**:
* `ACCEPT`: Human approves AI diagnosis.
* `EDIT`: Human modifies root cause or fix steps (requires `correction_reason`).
* `REJECT`: Human rejects AI diagnosis and provides ground-truth diagnosis (requires `correction_reason`).
* *Original `ai_diagnosis` is NEVER overwritten or mutated.*

### Stage 7: Responsible AI & Streamlit NOC (`dashboard/`, `app.py`)
* Logs all human edits and rejections to `data/responsible_ai_log.csv`.
* Displays case explorer, KPI cards, agreement analytics, and evaluation reports in a dark-themed NOC interface without executing network commands or making API calls on load.
