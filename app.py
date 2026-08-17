"""
NetSage AI Streamlit Dashboard Application (Phase 7 UI/UX Upgrade).
Modern AI Network Operations Center (NOC) Dashboard.

CRITICAL PERFORMANCE RULE: Reads pre-computed stored data only.
Does NOT make Groq API calls on dashboard load or refresh!
"""

import streamlit as st
import os
import sys
import pandas as pd

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from evaluation.metrics import (
    load_all_data,
    calculate_ai_accuracy,
    calculate_average_confidence,
    calculate_review_metrics,
    calculate_fusion_metrics,
    calculate_concept_distribution,
    calculate_severity_distribution,
    calculate_high_confidence_errors
)
from dashboard.styles import (
    inject_custom_css,
    render_header,
    render_kpi_card,
    render_sidebar_status
)
from dashboard.metrics import get_dashboard_kpis
from dashboard.charts import (
    render_concept_chart,
    render_severity_chart,
    render_review_decision_chart,
    render_fusion_status_chart,
    render_confidence_distribution_chart
)
from dashboard.case_view import render_case_explorer
from ai.diagnosis import DiagnosisEngine

# Page Configuration
st.set_page_config(
    page_title="NetSage AI - Network Operations Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Dark NOC Theme CSS
inject_custom_css()


# Load All Project Datasets (Pre-computed; Zero API calls on refresh)
@st.cache_data(ttl=60)
def get_dataset():
    return load_all_data()


raw_dataset = get_dataset()
ai_engine = DiagnosisEngine()

# === SIDEBAR NAVIGATION & FILTERS ===
st.sidebar.markdown("<h2 style='margin-bottom:0; color:#58a6ff;'>⚡ NetSage AI</h2>", unsafe_allow_html=True)
st.sidebar.caption("AI-Assisted Cisco Network Operations")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Case Explorer", "AI vs Human", "Responsible AI", "Evaluation"]
)

st.sidebar.divider()
st.sidebar.markdown("<div style='font-weight:700; font-size:0.8rem; color:#8b949e; text-transform:uppercase; letter-spacing:0.8px;'>FILTERS</div>", unsafe_allow_html=True)

# Extract filter options
all_concepts = ["All"] + sorted(list(set(c.get("concept", "Unknown") for c in raw_dataset.values() if c.get("concept"))))
all_severities = ["All", "High", "Medium", "Low"]
all_osi_layers = ["All"] + sorted(list(set(c.get("osi_layer", "Unknown") for c in raw_dataset.values() if c.get("osi_layer"))))
all_decisions = ["All", "ACCEPT", "EDIT", "REJECT", "PENDING"]
all_fusion_statuses = ["All", "AGREE", "PARTIAL_AGREE", "CONFLICT", "INSUFFICIENT_EVIDENCE"]

selected_concept = st.sidebar.selectbox("Concept", all_concepts)
selected_severity = st.sidebar.selectbox("Severity", all_severities)
selected_osi = st.sidebar.selectbox("OSI Layer", all_osi_layers)
selected_decision = st.sidebar.selectbox("Review Decision", all_decisions)
selected_fusion = st.sidebar.selectbox("Agreement Status", all_fusion_statuses)

# Sidebar System Status Panel
render_sidebar_status(
    rule_engine_ok=True,
    ai_engine_ok=ai_engine.is_api_key_configured(),
    review_sys_ok=True
)

# Apply Filters
filtered_dataset = {}
for cid, case in raw_dataset.items():
    if selected_concept != "All" and case.get("concept") != selected_concept:
        continue
    if selected_severity != "All" and case.get("severity") != selected_severity:
        continue
    if selected_osi != "All" and case.get("osi_layer") != selected_osi:
        continue

    rev = case.get("review_record") or {}
    dec = rev.get("reviewer_decision", "PENDING").upper() if isinstance(rev, dict) else "PENDING"
    if selected_decision != "All" and dec != selected_decision:
        continue

    fusion = case.get("fusion") or {}
    f_status = fusion.get("agreement_status", "").upper() if isinstance(fusion, dict) else ""
    if selected_fusion != "All" and f_status != selected_fusion:
        continue

    filtered_dataset[cid] = case


# === MAIN PAGE ROUTING ===

# 1. OVERVIEW PAGE
if page == "Overview":
    render_header()
    
    st.markdown("## Network Troubleshooting Overview")
    st.caption(f"Monitor diagnosis quality, network fault patterns and human-AI agreement across **{len(filtered_dataset)}** active cases.")

    st.divider()

    # System Health Section
    st.markdown("### 🟢 System Health & Operations Status")
    sh1, sh2, sh3, sh4 = st.columns(4)
    with sh1:
        st.success("Rule Engine: **Operational**")
    with sh2:
        if ai_engine.is_api_key_configured():
            st.success("AI Diagnosis: **Operational (Groq)**")
        else:
            st.warning("AI Diagnosis: **Mock / Standby Mode**")
    with sh3:
        st.success("Human Review: **Operational**")
    with sh4:
        st.success("Data Pipeline: **Operational (40 Cases)**")

    st.divider()

    # KPI Summary Cards (6 Custom Cards)
    kpis = get_dashboard_kpis(filtered_dataset)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        render_kpi_card("TOTAL CASES", kpis["total_cases"], "Dataset cases", border_color="#58a6ff")
    with k2:
        render_kpi_card("AI DIAGNOSES", kpis["ai_diagnoses_count"], "Engine outputs", border_color="#58a6ff")
    with k3:
        render_kpi_card("HUMAN REVIEWED", kpis["human_reviewed_count"], "Reviewed cases", border_color="#3fb950")
    with k4:
        render_kpi_card("AI AGREEMENT", f"{kpis['ai_agreement_pct']:.1f}%", "Human accepted", border_color="#3fb950")
    with k5:
        render_kpi_card("AI CORRECTIONS", kpis["ai_corrections_count"], "EDIT + REJECT", border_color="#d29922")
    with k6:
        render_kpi_card("HIGH-CONF ERRORS", kpis["high_confidence_conflicts_count"], "Confidence ≥ 80%", border_color="#f85149")

    st.divider()

    # Charts Grid
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        concept_dist = calculate_concept_distribution(filtered_dataset)
        render_concept_chart(concept_dist)
    with row1_col2:
        severity_dist = calculate_severity_distribution(filtered_dataset)
        render_severity_chart(severity_dist)

    st.divider()

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        render_review_decision_chart(kpis["review_metrics"])
    with row2_col2:
        render_fusion_status_chart(kpis["fusion_metrics"])

# 2. CASE EXPLORER PAGE
elif page == "Case Explorer":
    render_header()
    if not filtered_dataset:
        st.warning("No cases match the selected sidebar filters.")
    else:
        case_ids = sorted(list(filtered_dataset.keys()))
        selected_cid = st.sidebar.selectbox("Select Case ID to Inspect", case_ids)
        if selected_cid in filtered_dataset:
            render_case_explorer(filtered_dataset[selected_cid])

# 3. AI VS HUMAN PAGE
elif page == "AI vs Human":
    render_header()
    st.markdown("## 👤 AI vs Human Review Oversight")
    st.caption("Human-in-the-loop oversight evaluating AI acceptance, corrections, and rejections.")

    review_metrics = calculate_review_metrics(filtered_dataset)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("ACCEPTANCE RATE", f"{review_metrics['acceptance_rate_pct']:.1f}%", "Accepted without change", border_color="#3fb950")
    with m2:
        render_kpi_card("CORRECTION RATE", f"{review_metrics['correction_rate_pct']:.1f}%", "Human edits & rejects", border_color="#d29922")
    with m3:
        render_kpi_card("REJECTION RATE", f"{review_metrics['rejection_rate_pct']:.1f}%", "Fundamentally wrong", border_color="#f85149")
    with m4:
        render_kpi_card("PENDING REVIEWS", review_metrics['pending_count'], "Awaiting decision", border_color="#8b949e")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        render_review_decision_chart(review_metrics)
    with col2:
        render_confidence_distribution_chart(filtered_dataset)

    st.divider()

    st.subheader("📋 Case Comparison Table (AI Root Cause vs Human Final Diagnosis)")
    comparison_rows = []
    for cid, case in filtered_dataset.items():
        ai_d = case.get("ai_diagnosis") or {}
        rev_r = case.get("review_record") or {}
        fin_d = rev_r.get("final_diagnosis") or {}
        
        comparison_rows.append({
            "Case ID": cid,
            "Concept": case.get("concept", "Unknown"),
            "AI Root Cause": ai_d.get("root_cause", "N/A"),
            "Confidence": f"{ai_d.get('confidence', 0.0):.2f}",
            "Human Decision": rev_r.get("reviewer_decision", "PENDING"),
            "Final Approved Root Cause": fin_d.get("root_cause", "Pending Review")
        })
    if comparison_rows:
        st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True)

# 4. RESPONSIBLE AI PAGE
elif page == "Responsible AI":
    render_header()
    st.markdown("## 🛡️ Responsible AI Audit & Quality Control")
    st.caption("Audit record of cases where human reviewers edited or rejected AI diagnoses to ensure safety, governance, and model transparency.")

    high_conf_errors = calculate_high_confidence_errors(filtered_dataset)
    review_metrics = calculate_review_metrics(filtered_dataset)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("HUMAN REVIEWED", review_metrics["reviewed_total"], "Total reviewed cases", border_color="#58a6ff")
    with m2:
        render_kpi_card("AI ACCEPTANCES", review_metrics["accepted_count"], "Accepted without change", border_color="#3fb950")
    with m3:
        render_kpi_card("AI CORRECTIONS", review_metrics["edited_count"] + review_metrics["rejected_count"], "Human edits & rejects", border_color="#d29922")
    with m4:
        render_kpi_card("HIGH-CONF ERRORS", len(high_conf_errors), "Confidence ≥ 80%", border_color="#f85149")

    st.divider()

    st.info("💡 **Why Human Review Matters**: NetSage AI provides diagnostic recommendations. A human network engineer remains the final authority responsible for inspecting evidence and authorizing configuration changes.")

    st.divider()

    st.subheader("📋 Responsible AI Audit Log (`data/responsible_ai_log.csv`)")
    log_file = "data/responsible_ai_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Responsible AI log is currently empty.")
    else:
        st.warning("Responsible AI log CSV not found.")

    st.divider()

    st.subheader("🚨 High-Confidence AI Error Breakdown (Confidence ≥ 0.80 + Human Edit/Reject)")
    if high_conf_errors:
        for err in high_conf_errors:
            with st.expander(f"Case {err['case_id']} — Decision: {err['reviewer_decision']} (Confidence: {err['confidence']:.2f})"):
                st.write(f"**AI Diagnosis**: {err['ai_root_cause']}")
                st.write(f"**Human Correction**: {err['human_correction']}")
                st.write(f"**Correction Reason**: {err['correction_reason']}")
                st.write(f"**Final Approved Diagnosis**: {err['final_diagnosis']}")
    else:
        st.success("No high-confidence AI errors found in selected dataset view.")

# 5. EVALUATION PAGE
elif page == "Evaluation":
    render_header()
    st.markdown("## 📈 Comprehensive System Evaluation Report")
    st.caption("Detailed statistical evaluation across dataset coverage, Phase 3 rules, Phase 4 AI engine, Phase 5 fusion, and Phase 6 human governance.")

    acc_pct, correct_cnt, ai_tot = calculate_ai_accuracy(filtered_dataset)
    avg_conf = calculate_average_confidence(filtered_dataset)
    review_metrics = calculate_review_metrics(filtered_dataset)
    fusion_metrics = calculate_fusion_metrics(filtered_dataset)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("MODEL ACCURACY", f"{acc_pct:.1f}%", f"{correct_cnt}/{ai_tot} correct", border_color="#3fb950")
    with c2:
        render_kpi_card("AVG CONFIDENCE", f"{avg_conf:.2f}", "Model score average", border_color="#58a6ff")
    with c3:
        render_kpi_card("AI EVALUATED", f"{ai_tot} / {len(filtered_dataset)}", "Diagnosed cases", border_color="#58a6ff")
    with c4:
        render_kpi_card("HUMAN REVIEWED", f"{review_metrics['reviewed_total']} / {len(filtered_dataset)}", "Reviewed cases", border_color="#3fb950")

    st.divider()

    st.subheader("⚡ Phase 5 Evidence Fusion Breakdown")
    f_counts = fusion_metrics.get("counts", {})
    f_pcts = fusion_metrics.get("percentages", {})

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        render_kpi_card("AGREE", f"{f_counts.get('AGREE', 0)} ({f_pcts.get('AGREE', 0.0):.1f}%)", "Rule & AI match", border_color="#3fb950")
    with fc2:
        render_kpi_card("PARTIAL AGREE", f"{f_counts.get('PARTIAL_AGREE', 0)} ({f_pcts.get('PARTIAL_AGREE', 0.0):.1f}%)", "Same domain", border_color="#58a6ff")
    with fc3:
        render_kpi_card("CONFLICT", f"{f_counts.get('CONFLICT', 0)} ({f_pcts.get('CONFLICT', 0.0):.1f}%)", "Rule/AI mismatch", border_color="#f85149")
    with fc4:
        render_kpi_card("INSUFFICIENT EV", f"{f_counts.get('INSUFFICIENT_EVIDENCE', 0)} ({f_pcts.get('INSUFFICIENT_EVIDENCE', 0.0):.1f}%)", "Low confidence", border_color="#d29922")
