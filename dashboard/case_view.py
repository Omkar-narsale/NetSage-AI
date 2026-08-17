"""
Case Explorer View Module for NetSage AI (Phase 7).
Renders the complete 9-stage end-to-end troubleshooting walkthrough for any selected case.
"""

import streamlit as st
from typing import Dict, Any


def render_case_explorer(case: Dict[str, Any]):
    """
    Renders detailed case view displaying Case Info, Symptom, Topology, Show Output,
    Deterministic Rules, Groq AI Diagnosis, Evidence Fusion, and Human Review status.
    """
    case_id = case.get("case_id", "CASE-UNKNOWN")
    concept = case.get("concept", "Unknown")
    severity = case.get("severity", "Medium")
    osi_layer = case.get("osi_layer", "Layer 3 - Network")

    st.title(f"🔍 Case Explorer: `{case_id}`")

    # Metadata Banner
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Case ID", case_id)
    with col2:
        st.metric("Concept", concept)
    with col3:
        st.metric("Severity", severity)
    with col4:
        st.metric("OSI Layer", osi_layer)

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
        st.warning("⚠️ **HIGH-CONFIDENCE CORRECTION**: The AI was highly confident, but the human reviewer corrected or rejected the diagnosis.")

    if fusion.get("agreement_status") == "INSUFFICIENT_EVIDENCE":
        st.info("ℹ️ **INSUFFICIENT EVIDENCE**: Neither deterministic rules nor AI model has sufficient evidence for a reliable diagnosis.")

    # 1. Symptom & Topology
    st.header("1. Symptom & Topology")
    st.markdown(f"**Symptom**: {case.get('symptom', 'No symptom reported.')}")
    st.markdown(f"**Topology Note**: `{case.get('topology_note', 'No topology provided.')}`")

    # 2. Show Command Evidence
    st.header("2. Cisco CLI Evidence")
    show_outputs = case.get("show_outputs", "")
    if show_outputs:
        st.code(show_outputs, language="text")
    else:
        st.info("No show command evidence provided.")

    st.divider()

    # 3. Deterministic Rule Results (Phase 3)
    st.header("3. Phase 3 Deterministic Rule Checker Results")
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
                st.success(f"✅ **[{rule_id}] PASS** — {msg}")
            else:
                st.info(f"⚪ **[{rule_id}] UNKNOWN** — {msg}")
    else:
        st.info("No deterministic rule results available.")

    st.divider()

    # 4. AI Diagnosis (Phase 4 Groq Engine)
    st.header("4. Phase 4 Groq AI Diagnosis Engine")
    if ai_diag and isinstance(ai_diag, dict):
        st.subheader(f"Root Cause: {ai_diag.get('root_cause', 'N/A')}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("AI Confidence", f"{ai_diag.get('confidence', 0.0):.2f}")
        with c2:
            st.metric("Diagnosed OSI Layer", ai_diag.get('osi_layer', 'Unknown'))

        st.markdown("**Cited Evidence**:")
        for ev in ai_diag.get("evidence", []):
            st.write(f"- `{ev}`")

        st.markdown("**Recommended Next Commands**:")
        for cmd in ai_diag.get("next_command", []):
            st.code(cmd, language="bash")

        st.markdown("**Recommended Remediation Steps (For Human Review)**:")
        for step in ai_diag.get("fix_steps", []):
            st.write(f"1. {step}")
    else:
        st.warning("AI Diagnosis Not Available")

    st.divider()

    # 5. Evidence Fusion (Phase 5)
    st.header("5. Phase 5 Evidence Fusion")
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

    # 6. Human Review & Final Diagnosis (Phase 6)
    st.header("6. Phase 6 Human Review & Responsible AI Logging")
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
            st.markdown(f"**Correction / Review Reason**: {review.get('correction_reason')}")

        final_diag = review.get("final_diagnosis", {})
        if final_diag and isinstance(final_diag, dict):
            st.subheader("🎯 Final Approved Diagnosis (Human Authority)")
            st.markdown(f"**Approved Root Cause**: {final_diag.get('root_cause', 'N/A')}")
            if decision_val in ["EDIT", "REJECT"]:
                st.caption("Note: The final approved diagnosis above reflects the human reviewer's correction.")
    else:
        st.info("Human Review Status: **PENDING**")
