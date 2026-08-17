"""
Case Explorer View Module for NetSage AI (Phase 7 UI/UX Upgrade).
Renders the complete 7-stage visual troubleshooting timeline:
01 SYMPTOM -> 02 NETWORK EVIDENCE -> 03 RULE CHECK -> 04 AI DIAGNOSIS -> 05 EVIDENCE FUSION -> 06 HUMAN REVIEW -> 07 FINAL DIAGNOSIS.
"""

import streamlit as st
from typing import Dict, Any


def render_case_explorer(case: Dict[str, Any]):
    """
    Renders 7-stage visual diagnosis timeline card walkthrough.
    """
    case_id = case.get("case_id", "CASE-UNKNOWN")
    concept = case.get("concept", "Unknown")
    severity = case.get("severity", "Medium")
    osi_layer = case.get("osi_layer", "Layer 3 - Network")

    st.title(f"🔍 Case Explorer: `{case_id}`")

    # Header Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Case Identifier", case_id)
    with col2:
        st.metric("Concept Category", concept)
    with col3:
        st.metric("Severity Level", severity)
    with col4:
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

    st.subheader("🌐 7-Stage Visual Troubleshooting Timeline")

    # STAGE 01: SYMPTOM
    with st.container():
        st.markdown('<div class="timeline-step-num">01 | SYMPTOM</div>', unsafe_allow_html=True)
        st.markdown(f"**Reported Problem**: {case.get('symptom', 'No symptom statement provided.')}")
        st.divider()

    # STAGE 02: NETWORK EVIDENCE
    with st.container():
        st.markdown('<div class="timeline-step-num">02 | NETWORK EVIDENCE & TOPOLOGY</div>', unsafe_allow_html=True)
        st.markdown(f"**Topology Note**: `{case.get('topology_note', 'No topology note provided.')}`")
        show_outputs = case.get("show_outputs", "")
        if show_outputs:
            st.caption("Cisco IOS CLI Output Evidence:")
            st.code(show_outputs, language="text")
        else:
            st.info("No Cisco show command evidence provided.")
        st.divider()

    # STAGE 03: RULE CHECKER
    with st.container():
        st.markdown('<div class="timeline-step-num">03 | DETERMINISTIC RULE CHECKER</div>', unsafe_allow_html=True)
        rule_results = case.get("rule_results", [])
        if rule_results:
            for r in rule_results:
                status = r.get("status", "UNKNOWN")
                rule_id = r.get("rule_id", "RULE")
                msg = r.get("message", "")
                rec = r.get("recommendation", "")

                if status == "FAIL":
                    st.error(f"❌ **[{rule_id}] FAIL** — {msg}")
                    st.caption(f"💡 Recommendation: {rec}")
                elif status == "PASS":
                    st.success(f"✓ **[{rule_id}] PASS** — {msg}")
                else:
                    st.info(f"! **[{rule_id}] UNKNOWN** — {msg}")
        else:
            st.info("No deterministic rule results available.")
        st.divider()

    # STAGE 04: AI DIAGNOSIS
    with st.container():
        st.markdown('<div class="timeline-step-num">04 | GROQ AI DIAGNOSIS ENGINE</div>', unsafe_allow_html=True)
        if ai_diag and isinstance(ai_diag, dict):
            st.markdown(f"### Root Cause: **{ai_diag.get('root_cause', 'N/A')}**")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Model Confidence Score", f"{ai_diag.get('confidence', 0.0):.2f}")
            with c2:
                st.metric("Diagnosed OSI Layer", ai_diag.get('osi_layer', 'Unknown'))

            st.markdown("**Cited Evidence**:")
            for ev in ai_diag.get("evidence", []):
                st.write(f"- `{ev}`")

            st.markdown("**Recommended Next Commands**:")
            for cmd in ai_diag.get("next_command", []):
                st.code(cmd, language="bash")

            st.markdown("**Remediation Steps (Presented for Human Review Only)**:")
            for step in ai_diag.get("fix_steps", []):
                st.write(f"1. {step}")
        else:
            st.warning("AI Diagnosis Not Available")
        st.divider()

    # STAGE 05: EVIDENCE FUSION
    with st.container():
        st.markdown('<div class="timeline-step-num">05 | EVIDENCE FUSION</div>', unsafe_allow_html=True)
        if fusion and isinstance(fusion, dict):
            status_val = fusion.get("agreement_status", "UNKNOWN")
            conflict_val = fusion.get("conflict_detected", False)

            if status_val == "AGREE":
                st.success(f"Agreement Status: **{status_val}** (No Conflicts Detected)")
            elif status_val == "CONFLICT":
                st.error(f"Agreement Status: **{status_val}** (Conflict Detected: {conflict_val})")
            else:
                st.warning(f"Agreement Status: **{status_val}**")

            if fusion.get("supporting_rules"):
                st.write(f"**Supporting Rules**: {', '.join(fusion.get('supporting_rules'))}")
            if fusion.get("conflicting_rules"):
                st.write(f"**Conflicting Rules**: {', '.join(fusion.get('conflicting_rules'))}")
            for warn in fusion.get("warnings", []):
                st.caption(f"⚠️ Warning: {warn}")
        else:
            st.info("Fusion Analysis Not Available")
        st.divider()

    # STAGE 06: HUMAN REVIEW
    with st.container():
        st.markdown('<div class="timeline-step-num">06 | HUMAN REVIEW & GOVERNANCE</div>', unsafe_allow_html=True)
        if review and isinstance(review, dict):
            decision_val = review.get("reviewer_decision", "PENDING").upper()
            
            if decision_val == "ACCEPT":
                st.success(f"Reviewer Decision: **ACCEPTED**")
            elif decision_val == "EDIT":
                st.warning(f"Reviewer Decision: **EDITED**")
            elif decision_val == "REJECT":
                st.error(f"Reviewer Decision: **REJECTED**")
            else:
                st.info("Reviewer Decision: **PENDING**")

            if review.get("correction_reason"):
                st.markdown(f"**Reviewer Reason / Rationale**: {review.get('correction_reason')}")
        else:
            st.info("Human Review Status: **PENDING**")
        st.divider()

    # STAGE 07: FINAL DIAGNOSIS
    with st.container():
        st.markdown('<div class="timeline-step-num">07 | FINAL APPROVED DIAGNOSIS (HUMAN AUTHORITY)</div>', unsafe_allow_html=True)
        if review and isinstance(review, dict):
            final_diag = review.get("final_diagnosis", {})
            if final_diag and isinstance(final_diag, dict):
                st.subheader(f"🎯 Approved Root Cause: {final_diag.get('root_cause', 'N/A')}")
                st.caption("🛡️ Human-reviewed and approved recommendation. (Network fixes require human authorization before application).")
        else:
            st.info("Awaiting human review approval before final diagnosis release.")
