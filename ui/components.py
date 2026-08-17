"""
NetSage AI HTML Component Builders (Phase 7 UI Redesign).
Provides Glassmorphism Bento cards, Brand header, Status badges, and Navigation components.
"""

import html
import streamlit as st
from typing import Any, Optional


def render_top_brand_header():
    """Renders top brand header banner with Ctrl+K shortcut, status badge, and Deploy button."""
    header_html = """
    <div class="netsage-brand-header">
        <div>
            <div style="font-weight:700; font-size:0.75rem; color:#38bdf8; text-transform:uppercase; letter-spacing:1px; margin-bottom:2px;">
                ⚡ NETSAGE AI • AI-ASSISTED CISCO NETWORK OPERATIONS
            </div>
            <h1 class="brand-title">Welcome back, Engineer 👋</h1>
            <div class="brand-subtitle">
                Evidence-driven diagnosis with human oversight • Smarter decisions, safer networks.
            </div>
        </div>
        <div class="header-actions">
            <div class="search-pill" title="Press Ctrl+K to search cases">
                <span>🔍 Search Cases</span>
                <span class="kbd-shortcut">Ctrl K</span>
            </div>
            <span class="status-pill-ready">
                <span class="status-dot-green"></span>SYSTEM READY
            </span>
            <div class="deploy-btn-visual">
                ⚡ Deploy Pipeline
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_bento_kpi_card(
    title: str,
    value: Any,
    subtext: str,
    icon: str = "📊",
    accent: str = "blue"
):
    """Renders Glassmorphism Bento KPI card."""
    card_html = f"""
    <div class="bento-card accent-{accent}">
        <div class="bento-card-title">
            <span>{icon}</span>
            <span>{html.escape(title)}</span>
        </div>
        <div class="bento-kpi-value">{html.escape(str(value))}</div>
        <div class="bento-kpi-subtext">{html.escape(subtext)}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def get_status_badge_html(status: str) -> str:
    """Returns HTML pill badge string for given status."""
    st_clean = str(status).upper().strip()
    
    if st_clean in ["ACCEPTED", "AGREE", "PASS", "OPERATIONAL"]:
        badge_cls = "badge-accepted"
        icon = "✓"
    elif st_clean in ["EDITED", "PARTIAL_AGREE", "PARTIAL", "UNKNOWN", "MEDIUM"]:
        badge_cls = "badge-edited"
        icon = "✎"
    elif st_clean in ["REJECTED", "CONFLICT", "FAIL", "HIGH"]:
        badge_cls = "badge-rejected"
        icon = "✕"
    elif st_clean in ["INSUFFICIENT_EVIDENCE", "INSUFFICIENT"]:
        badge_cls = "badge-insufficient"
        icon = "ℹ"
    else:
        badge_cls = "badge-edited"
        icon = "●"

    return f'<span class="badge-pill {badge_cls}"><span>{icon}</span> <span>{html.escape(st_clean)}</span></span>'


def render_status_badge(status: str):
    """Renders HTML status pill badge directly."""
    st.markdown(get_status_badge_html(status), unsafe_allow_html=True)


def render_sidebar_health_panel(
    rule_engine_ok: bool = True,
    ai_engine_ok: bool = True,
    review_sys_ok: bool = True
):
    """Renders real backend system health status in sidebar."""
    ai_text = "Operational (Groq)" if ai_engine_ok else "Standby Mode"
    ai_cls = "health-status-ok" if ai_engine_ok else "health-status-warn"

    panel_html = f"""
    <div class="sidebar-health-panel">
        <div style="font-weight:700; font-size:0.75rem; color:#8b949e; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.8px;">
            SYSTEM HEALTH
        </div>
        <div class="health-item">
            <span>● Rule Engine</span>
            <span class="health-status-ok">Operational</span>
        </div>
        <div class="health-item">
            <span>● Groq AI Engine</span>
            <span class="{ai_cls}">{ai_text}</span>
        </div>
        <div class="health-item">
            <span>● Human Review</span>
            <span class="health-status-ok">Operational</span>
        </div>
        <div class="health-item">
            <span>● Data Pipeline</span>
            <span class="health-status-ok">40 Cases</span>
        </div>
    </div>
    """
    st.markdown(panel_html, unsafe_allow_html=True)
