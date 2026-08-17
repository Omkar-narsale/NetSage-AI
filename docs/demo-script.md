# 🎙️ NetSage AI — 10-Minute Demonstration Presentation Script

---

## ⏱️ Timeline & Presentation Agenda

| Timestamp | Presentation Phase | Visual Target / Screen | Key Talking Points |
| :--- | :--- | :--- | :--- |
| **00:00–01:00** | **Problem Statement** | Title Slide / `README.md` | Network troubleshooting complexity, manual show-command analysis errors, need for deterministic safety + AI intelligence. |
| **01:00–02:00** | **Architecture Overview** | `docs/architecture.md` Diagram | 7-Stage Pipeline: Evidence ➔ Rule Checker ➔ Groq AI ➔ Fusion ➔ Human Review ➔ Final Diagnosis ➔ Dashboard. |
| **02:00–03:00** | **Broken Case Setup** | Dashboard ➔ Case Explorer (`CASE-033`) | Symptom: PC-3 HTTP port 80 timeout to Datacenter Server. Topology & Cisco show-command evidence. |
| **03:00–04:00** | **Rule Checker Findings** | Case Explorer ➔ Stage 3 | Deterministic Phase 3 Rule Checker (`IF-001`, `GW-001` PASS) verifying Layer 1-3 connectivity. |
| **04:00–05:00** | **Groq AI Diagnosis** | Case Explorer ➔ Stage 4 | Groq LLaMA 3.3 70B structured JSON diagnosis identifying ACL 105 line 10 sequence drop. |
| **05:00–06:00** | **Evidence Fusion & Human Review** | Case Explorer ➔ Stage 5 & 6 | Agreement status `AGREE`. Human-in-the-loop review decision (`EDIT`), human authority rule. |
| **06:00–07:00** | **Final Diagnosis & Fix** | Case Explorer ➔ Stage 7 | Final approved root cause. Recommended Cisco IOS CLI remediation & verification commands. |
| **07:00–09:00** | **Dashboard & Responsible AI** | Dashboard ➔ Overview & Responsible AI | 6 KPI cards, dark NOC theme, Responsible AI Audit Log (`responsible_ai_log.csv`), high-confidence error tracking. |
| **09:00–10:00** | **Conclusion & Safety Summary** | Dashboard ➔ Evaluation | Summary of 40 cases, 100% test pass rate, human safety boundary (zero automatic hardware execution). |

---

## 🗣️ Minute-by-Minute Verbal Script

### 00:00–01:00 — Problem Statement & Motivation
> "Hello everyone! Welcome to the presentation of **NetSage AI**, an AI-assisted Cisco network troubleshooting system.
> Modern enterprise networks generate massive volumes of CLI diagnostic data when faults occur—such as VLAN mismatches, ACL blocking, or routing drops. Traditional troubleshooting relies on manual inspection, which is slow and error-prone.
> NetSage AI bridges this gap by combining **deterministic Python rule checking** with **Groq LLaMA 3.3 AI diagnosis**—governed by strict **human-in-the-loop oversight**."

### 01:00–02:00 — System Architecture
> "Let's examine our architecture. NetSage AI processes evidence through a strict 7-stage pipeline:
> 1. Raw CLI Evidence Preparation
> 2. Deterministic Rule Checker (verifying interface down, duplicate IPs, gateway mismatches)
> 3. Groq AI Diagnosis Engine (generating structured JSON diagnoses)
> 4. Evidence Fusion Module (categorizing agreement and flagging conflicts)
> 5. Human Review Workflow (ACCEPT, EDIT, REJECT)
> 6. Final Approved Diagnosis
> 7. Responsible AI Audit Logging and Visual Operations Dashboard."

### 02:00–03:00 — Live Demonstration: Broken Case (`CASE-033`)
> "Let's navigate to our **Case Explorer** page on the Streamlit dashboard and inspect **`CASE-033`**.
> Here, Finance workstation `PC-3` is trying to access web server `10.0.0.5` on port 80. Ping to gateway succeeds, but HTTP curl requests time out.
> Under Stage 02, we view the actual Cisco IOS show-command output: `show access-lists 105` and `show ip interface Gi0/0.30`."

### 03:00–04:00 — Deterministic Rule Checker Execution
> "In Stage 03, our Phase 3 Python Rule Checker executes.
> Rule `IF-001` checks interface status: PASS. Rule `GW-001` checks default gateway reachability: PASS.
> The rule checker proves that physical interfaces and IP addressing are operational, isolating the problem to access control policies."

### 04:00–05:00 — Groq AI Engine Diagnosis
> "In Stage 04, the Groq LLaMA 3.3 70B AI engine analyzes the evidence and produces a structured diagnosis with 97% confidence.
> It identifies that Extended ACL 105 line 10 contains a broad `deny ip` rule matching 245 packets before line 20's `permit tcp` rule can evaluate. It cites exact evidence lines and provides recommended next CLI commands."

### 05:00–06:00 — Evidence Fusion & Human Review
> "In Stage 05, Evidence Fusion evaluates agreement: Status `AGREE`.
> In Stage 06, our **Human Reviewer** inspects the AI diagnosis. The human reviewer selects **EDIT** and refines the root cause description to explicitly specify top-to-bottom first-match rule processing.
> This demonstrates our core safety principle: **The AI is never the final diagnosis—the human reviewer remains the ultimate decision-maker.**"

### 06:00–07:00 — Final Approved Diagnosis & Remediation
> "In Stage 07, the final human-approved diagnosis is stored.
> The recommended Cisco IOS remediation commands are displayed: entering `ip access-list extended 105`, re-ordering line 10 permit tcp before line 20 deny ip. Verification with `show access-lists 105` confirms 12 matches on line 10 and successful HTTP connection."

### 07:00–09:00 — Operations Dashboard & Responsible AI Audit Log
> "Now let's switch to our **Overview** dashboard page.
> You can see our custom dark NOC design with 6 KPI cards tracking 40 total cases across 8 core networking categories.
> Under **Responsible AI**, we view `responsible_ai_log.csv`. This audit log records every case where a human reviewer edited or rejected an AI diagnosis—such as `CASE-006`, `CASE-010`, `CASE-016`, `CASE-020`, `CASE-027`, and `CASE-033`."

### 09:00–10:00 — Conclusion & Q&A
> "In summary: NetSage AI combines deterministic validation, high-speed Groq AI reasoning, and mandatory human review into a transparent, production-ready system.
> All 54 unit tests pass cleanly, and the system strictly enforces zero automatic hardware execution.
> Thank you! We are now open for questions."
