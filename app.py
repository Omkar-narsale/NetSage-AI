"""
NetSage AI Streamlit Dashboard Application (Phase 7).
Interactive dark-themed network troubleshooting & evaluation dashboard.

CRITICAL: Performance rule - Reads pre-computed stored data only. Does NOT make Groq API calls on load/refresh!
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
from dashboard.metrics import get_dashboard_kpis
from dashboard.charts import (
    render_concept_chart,
    render_severity_chart,
    render_review_decision_chart,
    render_fusion_status_chart,
    render_confidence_distribution_chart
)
from dashboard.case_view import render_case_explorer

# Page Configuration
st.set_page_config(
    page_title="NetSage AI - Cisco Troubleshooting",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load All Project Datasets (Pre-computed; Zero API calls on refresh)
@st.cache_data(ttl=60)
def get_dataset():
    return load_all_data()


raw_dataset = get_dataset()

# === SIDEBAR NAVIGATION & FILTERS ===
st.sidebar.title("⚡ NetSage AI")
st.sidebar.caption("AI-Assisted Cisco Network Troubleshooting")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Case Explorer", "AI vs Human", "Responsible AI", "Evaluation"]
)

st.sidebar.divider()
st.sidebar.subheader("🔍 Dataset Filters")

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
    st.title("⚡ NetSage AI Dashboard")
    st.markdown("### AI-Assisted Cisco Network Troubleshooting & Human-in-the-Loop Governance")
    st.caption(f"Showing **{len(filtered_dataset)}** of **{len(raw_dataset)}** troubleshooting cases.")

    st.divider()

    # KPI Summary Cards (6 KPIs)
    kpis = get_dashboard_kpis(filtered_dataset)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.metric("Total Cases", kpis["total_cases"])
    with k2:
        st.metric("AI Diagnoses", kpis["ai_diagnoses_count"])
    with k3:
        st.metric("Human Reviewed", kpis["human_reviewed_count"])
    with k4:
        st.metric("AI Agreement", f"{kpis['ai_agreement_pct']:.1f}%")
    with k5:
        st.metric("AI Corrections", kpis["ai_corrections_count"])
    with k6:
        st.metric("High-Conf Conflicts", kpis["high_confidence_conflicts_count"])

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
    if not filtered_dataset:
        st.warning("No cases match the selected sidebar filters.")
    else:
        case_ids = sorted(list(filtered_dataset.keys()))
        selected_cid = st.sidebar.selectbox("Select Case ID to Inspect", case_ids)
        if selected_cid in filtered_dataset:
            render_case_explorer(filtered_dataset[selected_cid])

# 3. AI VS HUMAN PAGE
elif page == "AI vs Human":
    st.title("👤 AI vs Human Review Oversight")
    st.markdown("Human-in-the-loop review metrics evaluating AI acceptance, corrections, and rejections.")

    review_metrics = calculate_review_metrics(filtered_dataset)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Acceptance Rate", f"{review_metrics['acceptance_rate_pct']:.1f}%")
    with m2:
        st.metric("Correction Rate", f"{review_metrics['correction_rate_pct']:.1f}%")
    with m3:
        st.metric("Rejection Rate", f"{review_metrics['rejection_rate_pct']:.1f}%")
    with m4:
        st.metric("Pending Review", review_metrics['pending_count'])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        render_review_decision_chart(review_metrics)
    with col2:
        render_confidence_distribution_chart(filtered_dataset)

# 4. RESPONSIBLE AI PAGE
elif page == "Responsible AI":
    st.title("🛡️ Responsible AI Audit & Corrections Log")
    st.markdown("Audit record of cases where human reviewers edited or rejected AI diagnoses to ensure safety and transparency.")

    high_conf_errors = calculate_high_confidence_errors(filtered_dataset)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("High-Conf Errors", len(high_conf_errors))
    with m2:
        review_metrics = calculate_review_metrics(filtered_dataset)
        st.metric("Total Corrections", review_metrics["edited_count"] + review_metrics["rejected_count"])
    with m3:
        st.metric("Acceptances", review_metrics["accepted_count"])
    with m4:
        st.metric("Correction Rate", f"{review_metrics['correction_rate_pct']:.1f}%")

    st.divider()

    st.subheader("📋 Responsible AI Correction Log (`data/responsible_ai_log.csv`)")
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

    st.subheader("🚨 High-Confidence AI Error Breakdown (Confidence >= 0.80 + Human Edit/Reject)")
    if high_conf_errors:
        for err in high_conf_errors:
            with st.expander(f"Case {err['case_id']} — {err['reviewer_decision']} (Confidence: {err['confidence']:.2f})"):
                st.write(f"**AI Diagnosis**: {err['ai_root_cause']}")
                st.write(f"**Human Correction**: {err['human_correction']}")
                st.write(f"**Correction Reason**: {err['correction_reason']}")
                st.write(f"**Final Diagnosis**: {err['final_diagnosis']}")
    else:
        st.success("No high-confidence AI errors found in selected dataset view.")

# 5. EVALUATION PAGE
elif page == "Evaluation":
    st.title("📈 Comprehensive Evaluation Report")
    st.markdown("End-to-end evaluation metrics across dataset coverage, Phase 3 rules, Phase 4 AI engine, Phase 5 fusion, and Phase 6 human review.")

    acc_pct, correct_cnt, ai_tot = calculate_ai_accuracy(filtered_dataset)
    avg_conf = calculate_average_confidence(filtered_dataset)
    review_metrics = calculate_review_metrics(filtered_dataset)
    fusion_metrics = calculate_fusion_metrics(filtered_dataset)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("AI Diagnosis Accuracy", f"{acc_pct:.1f}%")
    with c2:
        st.metric("Average Confidence", f"{avg_conf:.2f}")
    with c3:
        st.metric("AI Diagnoses Evaluated", f"{ai_tot} / {len(filtered_dataset)}")
    with c4:
        st.metric("Reviewed Cases", f"{review_metrics['reviewed_total']} / {len(filtered_dataset)}")

    st.divider()

    st.subheader("⚡ Phase 5 Evidence Fusion Breakdown")
    f_counts = fusion_metrics.get("counts", {})
    f_pcts = fusion_metrics.get("percentages", {})

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        st.metric("AGREE", f"{f_counts.get('AGREE', 0)} ({f_pcts.get('AGREE', 0.0):.1f}%)")
    with fc2:
        st.metric("PARTIAL_AGREE", f"{f_counts.get('PARTIAL_AGREE', 0)} ({f_pcts.get('PARTIAL_AGREE', 0.0):.1f}%)")
    with fc3:
        st.metric("CONFLICT", f"{f_counts.get('CONFLICT', 0)} ({f_pcts.get('CONFLICT', 0.0):.1f}%)")
    with fc4:
        st.metric("INSUFFICIENT_EVIDENCE", f"{f_counts.get('INSUFFICIENT_EVIDENCE', 0)} ({f_pcts.get('INSUFFICIENT_EVIDENCE', 0.0):.1f}%)")
