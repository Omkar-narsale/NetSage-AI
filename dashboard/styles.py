"""
NetSage AI Custom Design System & CSS Styling (Phase 7 UI/UX).
Provides modern dark-mode NOC/SaaS styles, metric cards, timeline stages,
status badges, and custom HTML/CSS component builders.
"""

import streamlit as st
from typing import Any


def inject_custom_css():
    """Injects custom CSS styling into Streamlit application."""
    css = """
    <style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0b0e14;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide Streamlit Header & Footer elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background-color: rgba(11, 14, 20, 0.85); backdrop-filter: blur(10px);}

    /* Custom Header Banner */
    .netsage-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .netsage-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff 0%, #79c0ff 50%, #d2a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
        padding: 0;
    }
    .netsage-subtitle {
        color: #8b949e;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
    }
    
    /* Live Status Badge */
    .system-status-pill {
        display: inline-flex;
        align-items: center;
        background-color: rgba(46, 160, 67, 0.15);
        border: 1px solid #2ea043;
        color: #3fb950;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #3fb950;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        box-shadow: 0 0 8px #3fb950;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f0f6fc;
        margin-bottom: 4px;
    }
    .kpi-subtext {
        font-size: 0.75rem;
        color: #7d8590;
    }

    /* Status Badges */
    .badge-pass {
        background-color: rgba(46, 160, 67, 0.2);
        color: #3fb950;
        border: 1px solid #2ea043;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-fail {
        background-color: rgba(248, 81, 73, 0.2);
        color: #f85149;
        border: 1px solid #f85149;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-unknown {
        background-color: rgba(210, 153, 34, 0.2);
        color: #d29922;
        border: 1px solid #d29922;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    /* Timeline Step Card */
    .timeline-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #58a6ff;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 18px;
    }
    .timeline-card-fail {
        border-left-color: #f85149;
    }
    .timeline-card-pass {
        border-left-color: #3fb950;
    }
    .timeline-card-warn {
        border-left-color: #d29922;
    }
    .timeline-step-num {
        font-size: 0.75rem;
        font-weight: 800;
        color: #58a6ff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Code / Terminal Styling */
    .stCodeBlock {
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    /* System Status Panel in Sidebar */
    .sidebar-status-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 15px;
    }
    .sidebar-status-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-bottom: 6px;
        color: #8b949e;
    }
    .sidebar-status-online {
        color: #3fb950;
        font-weight: 700;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    """Renders custom dark-themed application header."""
    html = """
    <div class="netsage-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 class="netsage-title">NetSage AI</h1>
                <p class="netsage-subtitle">AI-ASSISTED NETWORK TROUBLESHOOTING • EVIDENCE-DRIVEN DIAGNOSIS WITH HUMAN OVERSIGHT</p>
            </div>
            <div>
                <span class="system-status-pill"><span class="status-dot"></span>SYSTEM READY</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(label: str, value: Any, subtext: str = "", border_color: str = "#58a6ff"):
    """Renders a custom formatted KPI card."""
    html = f"""
    <div class="kpi-card" style="border-left: 3px solid {border_color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_sidebar_status(rule_engine_ok: bool, ai_engine_ok: bool, review_sys_ok: bool):
    """Renders system status panel in the sidebar."""
    ai_text = "Operational (Groq)" if ai_engine_ok else "Mock / Standby"
    ai_color = "#3fb950" if ai_engine_ok else "#d29922"

    html = f"""
    <div class="sidebar-status-box">
        <div style="font-weight:700; font-size:0.75rem; color:#8b949e; text-transform:uppercase; margin-bottom:8px; letter-spacing:0.5px;">SYSTEM STATUS</div>
        <div class="sidebar-status-item">
            <span>Rule Engine</span>
            <span class="sidebar-status-online">● Operational</span>
        </div>
        <div class="sidebar-status-item">
            <span>Groq AI Engine</span>
            <span style="color: {ai_color}; font-weight:700;">● {ai_text}</span>
        </div>
        <div class="sidebar-status-item">
            <span>Human Review</span>
            <span class="sidebar-status-online">● Active</span>
        </div>
        <div class="sidebar-status-item">
            <span>Data Pipeline</span>
            <span class="sidebar-status-online">● 40 Cases</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
