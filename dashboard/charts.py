"""
Dashboard Charts Module for NetSage AI (Phase 7).
Renders professional, dark-themed visualizations for Streamlit.
"""

import streamlit as st
from typing import Dict, Any, List


def render_concept_chart(dist: Dict[str, int]):
    """Renders Bar chart showing cases per networking concept."""
    st.subheader("📊 Issue Distribution by Concept")
    if not dist:
        st.info("No concept data available.")
        return
    st.bar_chart(dist)


def render_severity_chart(dist: Dict[str, int]):
    """Renders Bar chart showing cases per severity level."""
    st.subheader("⚠️ Severity Distribution")
    if not dist:
        st.info("No severity data available.")
        return
    st.bar_chart(dist)


def render_review_decision_chart(review_metrics: Dict[str, Any]):
    """Renders Bar chart showing AI vs Human Review decisions."""
    st.subheader("👤 AI vs Human Agreement Decisions")
    data = {
        "Accepted": review_metrics.get("accepted_count", 0),
        "Edited": review_metrics.get("edited_count", 0),
        "Rejected": review_metrics.get("rejected_count", 0)
    }
    if sum(data.values()) == 0:
        st.info("No human review data available.")
        return
    st.bar_chart(data)


def render_fusion_status_chart(fusion_metrics: Dict[str, Any]):
    """Renders Bar chart showing Phase 5 Evidence Fusion agreement status."""
    st.subheader("⚡ Evidence Fusion Agreement Status")
    counts = fusion_metrics.get("counts", {})
    if not counts or sum(counts.values()) == 0:
        st.info("No fusion status data available.")
        return
    st.bar_chart(counts)


def render_confidence_distribution_chart(dataset: Dict[str, Dict[str, Any]]):
    """Renders confidence distribution buckets chart."""
    st.subheader("🎯 AI Confidence Distribution")
    high = 0
    med = 0
    low = 0
    for case in dataset.values():
        ai_diag = case.get("ai_diagnosis")
        if ai_diag and isinstance(ai_diag, dict):
            conf = ai_diag.get("confidence", 0.0)
            if conf >= 0.80:
                high += 1
            elif conf >= 0.50:
                med += 1
            else:
                low += 1

    buckets = {
        "High (>= 0.80)": high,
        "Medium (0.50 - 0.79)": med,
        "Low (< 0.50)": low
    }
    st.bar_chart(buckets)
