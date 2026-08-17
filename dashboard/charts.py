"""
Dashboard Charts Module for NetSage AI (Phase 7 UI/UX Upgrade).
Renders dark-themed Plotly charts with automatic fallback to Streamlit native charts.
"""

import streamlit as st
from typing import Dict, Any, List

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def render_concept_chart(dist: Dict[str, int]):
    """Renders Bar chart showing cases per networking concept."""
    st.subheader("📊 Issue Distribution by Concept")
    if not dist:
        st.info("No concept data available.")
        return

    if HAS_PLOTLY:
        categories = list(dist.keys())
        counts = list(dist.values())
        fig = px.bar(
            x=categories,
            y=counts,
            labels={"x": "Networking Concept", "y": "Number of Cases"},
            color_discrete_sequence=["#58a6ff"]
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(dist)


def render_severity_chart(dist: Dict[str, int]):
    """Renders Donut / Bar chart showing cases per severity level."""
    st.subheader("⚠️ Severity Distribution")
    if not dist or sum(dist.values()) == 0:
        st.info("No severity data available.")
        return

    if HAS_PLOTLY:
        labels = list(dist.keys())
        values = list(dist.values())
        colors = ["#f85149", "#d29922", "#3fb950"]  # High: Red, Med: Yellow, Low: Green
        fig = px.pie(
            names=labels,
            values=values,
            hole=0.5,
            color=labels,
            color_discrete_map={"High": "#f85149", "Medium": "#d29922", "Low": "#3fb950"}
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(dist)


def render_review_decision_chart(review_metrics: Dict[str, Any]):
    """Renders Donut / Bar chart showing AI vs Human Review decisions."""
    st.subheader("👤 AI vs Human Agreement Decisions")
    data = {
        "Accepted": review_metrics.get("accepted_count", 0),
        "Edited": review_metrics.get("edited_count", 0),
        "Rejected": review_metrics.get("rejected_count", 0)
    }
    if sum(data.values()) == 0:
        st.info("No human review data available.")
        return

    if HAS_PLOTLY:
        labels = list(data.keys())
        values = list(data.values())
        fig = px.pie(
            names=labels,
            values=values,
            hole=0.5,
            color=labels,
            color_discrete_map={"Accepted": "#3fb950", "Edited": "#d29922", "Rejected": "#f85149"}
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(data)


def render_fusion_status_chart(fusion_metrics: Dict[str, Any]):
    """Renders Bar chart showing Phase 5 Evidence Fusion agreement status."""
    st.subheader("⚡ Evidence Fusion Agreement Status")
    counts = fusion_metrics.get("counts", {})
    if not counts or sum(counts.values()) == 0:
        st.info("No fusion status data available.")
        return

    if HAS_PLOTLY:
        statuses = list(counts.keys())
        vals = list(counts.values())
        fig = px.bar(
            x=statuses,
            y=vals,
            labels={"x": "Agreement Status", "y": "Case Count"},
            color=statuses,
            color_discrete_map={
                "AGREE": "#3fb950",
                "PARTIAL_AGREE": "#58a6ff",
                "CONFLICT": "#f85149",
                "INSUFFICIENT_EVIDENCE": "#d29922"
            }
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
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

    if HAS_PLOTLY:
        labels = list(buckets.keys())
        vals = list(buckets.values())
        fig = px.bar(
            x=labels,
            y=vals,
            labels={"x": "Confidence Level", "y": "Case Count"},
            color=labels,
            color_discrete_map={
                "High (>= 0.80)": "#3fb950",
                "Medium (0.50 - 0.79)": "#58a6ff",
                "Low (< 0.50)": "#d29922"
            }
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(buckets)
