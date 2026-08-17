"""
Case Explorer View Module for NetSage AI (Phase 7 UI/UX Redesign).
Renders 7-stage visual troubleshooting timeline with Glassmorphism Bento cards & status badges.
"""

import streamlit as st
from typing import Dict, Any
from ui.components import get_status_badge_html


def render_case_explorer(case: Dict[str, Any]):
    """
    Renders 7-stage visual diagnosis timeline card walkthrough.
    """
    case_id = case.get("case_id", "CASE-UNKNOWN")
    concept = case.get("concept", "Unknown")
    severity = case.get("severity", "Medium")
    osi_layer = case.get("osi_layer", "Layer 3 - Network")

    st.title(f"🔍 Case Explorer: `{case_id}`")

    # Header Summary Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Case Identifier", case_id)
    with c2:
        st.metric("Concept Category", concept)
    with c3:
        st.metric("Severity Level", severity)
    with c4:
        st.metric("Target OSI Layer", osi_layer)

    st.divider()

    # Responsible AI Warnings Banner
    fusion = case.get("fusion") or {}
    review = case.get("review_record") or {}
    ai_diag = case.get("ai_diagnosis") or {}
    conf = ai_diag.get("confidence", 0.0) if isinstance(ai_diag, dict) else 0.0
    dec = review.get("reviewer_decision", "").upper() if isinstance(review, dict) else ""

    if fusion.get("conflict_detected"):
        st.error("🚨 **RESPONSIBLE AI WARNING**: Deterministic rule results conflict with the AI diagnosis. Human review is required!")

    if conf >= 0.80 and dec in ["EDIT", "REJECT"]:
        st.warning("⚠️ **HIGH-CONFIDENCE CORRECTION**: The AI was highly confident (≥ 80%), but the human reviewer edited or rejected the diagnosis.")

    if fusion.get("agreement_status") == "INSUFFICIENT_EVIDENCE":
        st.info("ℹ️ **INSUFFICIENT EVIDENCE**: Neither deterministic rules nor AI model has sufficient evidence for a reliable diagnosis.")

    st.subheader("🌐 7-Stage Visual Troubleshooting Journey")

    # STAGE 01: SYMPTOM
    with st.container():
        st.markdown(
            f"""
            <div class="bento-card accent-cyan">
                <div class="bento-card-title">01 | REPORTED NETWORK SYMPTOM</div>
                <div style="font-size:1.05rem; font-weight:600; color:#f0f6fc;">
                    {case.get('symptom', 'No symptom statement provided.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # STAGE 02: NETWORK EVIDENCE
    with st.container():
        st.markdown(
            f"""
            <div class="bento-card accent-blue">
                <div class="bento-card-title">02 | NETWORK EVIDENCE & TOPOLOGY</div>
                <div style="font-size:0.9rem; color:#8b949e; margin-bottom:8px;">
                    Topology Note: <code style="color:#58a6ff;">{case.get('topology_note', 'N/A')}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        show_outputs = case.get("show_outputs", "")
        if show_outputs:
            st.caption("Cisco IOS CLI Show Command Output Evidence:")
            st.code(show_outputs, language="text")
        else:
            st.info("No Cisco show command evidence provided.")

    # STAGE 03: RULE CHECKER
    with st.container():
        st.markdown(
            """
            <div class="bento-card accent-blue">
                <div class="bento-card-title">03 | DETERMINISTIC RULE CHECKER ENGINE</div>
            """,
            unsafe_allow_html=True
        )
        rule_results = case.get("rule_results", [])
        if rule_results:
            for r in rule_results:
                status = r.get("status", "UNKNOWN")
                rule_id = r.get("rule_id", "RULE")
                msg = r.get("message", "")
                rec = r.get("recommendation", "")

                badge = get_status_badge_html(status)
                if status == "FAIL":
                    st.markdown(f"{badge} **[{rule_id}] FAIL** — {msg}", unsafe_allow_html=True)
                    st.caption(f"💡 Recommendation: {rec}")
                elif status == "PASS":
                    st.markdown(f"{badge} **[{rule_id}] PASS** — {msg}", unsafe_allow_html=True)
                else:
                    st.markdown(f"{badge} **[{rule_id}] UNKNOWN** — {msg}", unsafe_allow_html=True)
        else:
            st.info("No deterministic rule results available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # STAGE 04: AI DIAGNOSIS
    with st.container():
        st.markdown(
            """
            <div class="bento-card accent-purple">
                <div class="bento-card-title">04 | GROQ AI DIAGNOSIS ENGINE (RECOMMENDATION ONLY)</div>
            """,
            unsafe_allow_html=True
        )
        if ai_diag and isinstance(ai_diag, dict):
            st.markdown(f"### Root Cause: **{ai_diag.get('root_cause', 'N/A')}**")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Model Confidence Score", f"{ai_diag.get('confidence', 0.0):.2f}")
            with c2:
                st.metric("Diagnosed OSI Layer", ai_diag.get('osi_layer', 'Unknown'))

            st.markdown("**Cited Evidence Snippets**:")
            for ev in ai_diag.get("evidence", []):
                st.write(f"- `{ev}`")

            st.markdown("**Recommended Diagnostic Next Commands**:")
            for cmd in ai_diag.get("next_command", []):
                st.code(cmd, language="bash")

            st.markdown("**Remediation Steps (Presented for Human Authorization)**:")
            for step in ai_diag.get("fix_steps", []):
                st.write(f"1. {step}")
        else:
            st.warning("AI Diagnosis Not Available")
        st.markdown("</div>", unsafe_allow_html=True)

    # STAGE 05: EVIDENCE FUSION
    with st.container():
        st.markdown(
            """
            <div class="bento-card accent-amber">
                <div class="bento-card-title">05 | PHASE 5 EVIDENCE FUSION</div>
            """,
            unsafe_allow_html=True
        )
        if fusion and isinstance(fusion, dict):
            status_val = fusion.get("agreement_status", "UNKNOWN")
            badge = get_status_badge_html(status_val)

            st.markdown(f"Agreement Classification: {badge}", unsafe_allow_html=True)

            if fusion.get("supporting_rules"):
                st.write(f"**Supporting Rules**: {', '.join(fusion.get('supporting_rules'))}")
            if fusion.get("conflicting_rules"):
                st.write(f"**Conflicting Rules**: {', '.join(fusion.get('conflicting_rules'))}")
            for warn in fusion.get("warnings", []):
                st.caption(f"⚠️ Warning: {warn}")
        else:
            st.info("Fusion Analysis Not Available")
        st.markdown("</div>", unsafe_allow_html=True)

    # STAGE 06: HUMAN REVIEW
    with st.container():
        st.markdown(
            """
            <div class="bento-card accent-green">
                <div class="bento-card-title">06 | HUMAN REVIEW & GOVERNANCE OVERSIGHT</div>
            """,
            unsafe_allow_html=True
        )
        if review and isinstance(review, dict):
            decision_val = review.get("reviewer_decision", "PENDING").upper()
            badge = get_status_badge_html(decision_val)

            st.markdown(f"Reviewer Decision: {badge}", unsafe_allow_html=True)

            if review.get("correction_reason"):
                st.markdown(f"**Reviewer Rationale**: {review.get('correction_reason')}")
        else:
            st.info("Human Review Status: **PENDING**")
        st.markdown("</div>", unsafe_allow_html=True)

    # STAGE 07: FINAL DIAGNOSIS
    with st.container():
        st.markdown(
            """
            <div class="bento-card accent-green">
                <div class="bento-card-title">07 | FINAL APPROVED DIAGNOSIS (HUMAN AUTHORITY)</div>
            """,
            unsafe_allow_html=True
        )
        if review and isinstance(review, dict):
            final_diag = review.get("final_diagnosis", {})
            if final_diag and isinstance(final_diag, dict):
                st.markdown(f"### 🎯 Approved Root Cause: {final_diag.get('root_cause', 'N/A')}")
                st.caption("🛡️ Human-reviewed and approved recommendation. (Network fixes require human authorization before application).")
        else:
            st.info("Awaiting human review approval before final diagnosis release.")
        st.markdown("</div>", unsafe_allow_html=True)
