"""
NetSage AI Sidebar Module (Phase 7 Premium Sidebar Redesign).
Renders high-end dark glassmorphism navigation rail, system health status,
compact filter controls, Responsible AI callout card, and footer.
"""

import streamlit as st
from typing import Dict, Any, Tuple


def render_sidebar_branding():
    """Renders top brand header in sidebar with title and uppercase subtitle."""
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.6rem;">⚡</span>
                <span style="font-size:1.5rem; font-weight:800; background:linear-gradient(90deg, #58a6ff 0%, #38bdf8 50%, #bc8cff 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    NetSage AI
                </span>
            </div>
            <div style="font-size:0.7rem; font-weight:800; color:#8b949e; text-transform:uppercase; letter-spacing:1.2px; margin-top:4px;">
                AI-ASSISTED CISCO NETWORK OPERATIONS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sidebar_status_card(ai_configured: bool = True):
    """Renders real backend system status card in sidebar."""
    ai_status = "Operational" if ai_configured else "Standby Mode"
    ai_color = "#3fb950" if ai_configured else "#d29922"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-status-box">
            <div style="font-weight:800; font-size:0.72rem; color:#8b949e; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.8px;">
                SYSTEM STATUS
            </div>
            <div class="sidebar-status-item">
                <span>⚙ Rule Engine</span>
                <span style="color:#3fb950; font-weight:700;">● Operational</span>
            </div>
            <div class="sidebar-status-item">
                <span>◉ Groq AI Engine</span>
                <span style="color:{ai_color}; font-weight:700;">● {ai_text_val(ai_configured)}</span>
            </div>
            <div class="sidebar-status-item">
                <span>♙ Human Review</span>
                <span style="color:#3fb950; font-weight:700;">● Active</span>
            </div>
            <div class="sidebar-status-item">
                <span>▣ Data Pipeline</span>
                <span style="color:#3fb950; font-weight:700;">● 40 Cases</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def ai_text_val(configured: bool) -> str:
    return "Operational" if configured else "Standby"


def render_sidebar_navigation() -> str:
    """Renders premium navigation section without radio circles."""
    st.sidebar.markdown(
        """
        <div style="font-weight:800; font-size:0.72rem; color:#8b949e; text-transform:uppercase; letter-spacing:0.8px; margin: 18px 0 8px 0;">
            NAVIGATION
        </div>
        """,
        unsafe_allow_html=True
    )

    page_choice = st.sidebar.radio(
        "Navigation Menu",
        [
            "🏠  Overview",
            "📁  Case Explorer",
            "◫  AI vs Human",
            "🛡️  Responsible AI",
            "📊  Evaluation"
        ],
        label_visibility="collapsed"
    )

    # Clean raw page name
    clean_page = page_choice.split("  ")[-1].strip()
    return clean_page


def render_sidebar_filters(raw_dataset: Dict[str, Dict[str, Any]]) -> Tuple[str, str, str, str, str]:
    """Renders sidebar filters with glass styling."""
    st.sidebar.markdown(
        """
        <div style="display:flex; justify-between:space-between; align-items:center; margin: 20px 0 8px 0;">
            <span style="font-weight:800; font-size:0.72rem; color:#8b949e; text-transform:uppercase; letter-spacing:0.8px;">FILTERS</span>
            <span style="font-size:0.75rem; color:#58a6ff;">⚙</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    all_concepts = ["All"] + sorted(list(set(c.get("concept", "Unknown") for c in raw_dataset.values() if c.get("concept"))))
    all_severities = ["All", "High", "Medium", "Low"]
    all_osi = ["All"] + sorted(list(set(c.get("osi_layer", "Unknown") for c in raw_dataset.values() if c.get("osi_layer"))))
    all_decisions = ["All", "ACCEPT", "EDIT", "REJECT", "PENDING"]
    all_fusion = ["All", "AGREE", "PARTIAL_AGREE", "CONFLICT", "INSUFFICIENT_EVIDENCE"]

    s_concept = st.sidebar.selectbox("◇ Concept", all_concepts)
    s_severity = st.sidebar.selectbox("⚠ Severity", all_severities)
    s_osi = st.sidebar.selectbox("◈ OSI Layer", all_osi)
    s_decision = st.sidebar.selectbox("♙ Review Decision", all_decisions)
    s_fusion = st.sidebar.selectbox("♢ Agreement Status", all_fusion)

    return s_concept, s_severity, s_osi, s_decision, s_fusion


def render_sidebar_callout_and_footer():
    """Renders bottom Responsible AI callout card and system footer."""
    st.sidebar.markdown(
        """
        <div class="sidebar-callout-card">
            <div style="font-weight:800; font-size:0.82rem; color:#bc8cff; margin-bottom:4px;">
                ✦ Evidence-driven. Human-verified.
            </div>
            <div style="font-size:0.75rem; color:#8b949e; line-height:1.4;">
                AI provides diagnostic recommendations. Human engineers retain final authority.
            </div>
        </div>

        <div class="sidebar-footer-text">
            © 2026 NetSage AI &nbsp;•&nbsp; v1.0.0 &nbsp;•&nbsp; <span style="color:#3fb950;">● System Ready</span>
        </div>
        """,
        unsafe_allow_html=True
    )
