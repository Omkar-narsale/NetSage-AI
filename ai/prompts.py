"""
Prompt Builder for NetSage AI Diagnosis Engine.
Formats network symptoms, topology, show outputs, and deterministic rule results
into a structured prompt payload for LLM inference.

CRITICAL: Never includes expected_fault in the prompt payload to prevent data leakage!
"""

from typing import Dict, Any, Optional, List


SYSTEM_INSTRUCTION = """You are an expert Cisco-style network troubleshooting assistant helping junior network engineers.
Your task is to analyze network symptoms, topology descriptions, Cisco show command outputs, and deterministic rule checker results to determine the most likely primary root cause.

STRICT REQUIREMENTS:
1. Grounding: Cite ONLY evidence explicitly present in the provided input. NEVER invent command outputs, IP addresses, VLAN IDs, routes, or topology details.
2. Unclear Evidence: If evidence is incomplete or ambiguous, lower your confidence score (0.0 to 1.0) and recommend specific diagnostic next commands.
3. Rule Engine Results: Consider deterministic rule engine results alongside CLI outputs. If you disagree with a rule checker result, explain why based on evidence.
4. Output Format: You MUST return ONLY a valid raw JSON object matching this exact schema:
{
  "root_cause": "Concise primary root cause description",
  "confidence": 0.85,
  "osi_layer": "Layer X - Layer Name",
  "evidence": ["Verbatim or direct quote snippet from show outputs or topology"],
  "next_command": ["Recommended Cisco show command(s) for further investigation"],
  "fix_steps": ["Step-by-step remediation commands/instructions for human review"]
}
5. Safety: Recommend remediation steps ONLY for human review. Do NOT assume fixes are automatically applied.
"""


def build_diagnosis_prompt(
    symptom: str,
    topology_note: Optional[str] = None,
    show_outputs: Optional[str] = None,
    rule_results: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Constructs the formatted prompt string for LLM diagnosis.
    Ensures symptom, topology, show_outputs, and rule_results are properly formatted.
    """
    if not symptom or not symptom.strip():
        raise ValueError("Symptom is required to build a diagnosis prompt.")

    prompt_parts = []
    prompt_parts.append(SYSTEM_INSTRUCTION)
    prompt_parts.append("\n=== INPUT TROUBLESHOOTING CASE ===")
    prompt_parts.append(f"SYMPTOM:\n{symptom.strip()}\n")

    if topology_note and topology_note.strip():
        prompt_parts.append(f"TOPOLOGY NOTE:\n{topology_note.strip()}\n")
    else:
        prompt_parts.append("TOPOLOGY NOTE:\nNot provided.\n")

    if show_outputs and show_outputs.strip():
        prompt_parts.append(f"SHOW COMMAND OUTPUTS:\n{show_outputs.strip()}\n")
    else:
        prompt_parts.append("SHOW COMMAND OUTPUTS:\nNo show command evidence provided.\n")

    if rule_results:
        prompt_parts.append("DETERMINISTIC RULE CHECKER RESULTS:")
        for res in rule_results:
            rule_id = res.get("rule_id", "UNKNOWN")
            status = res.get("status", "UNKNOWN")
            msg = res.get("message", "")
            prompt_parts.append(f"- [{rule_id}] Status: {status} | Message: {msg}")
        prompt_parts.append("")
    else:
        prompt_parts.append("DETERMINISTIC RULE CHECKER RESULTS:\nNone available.\n")

    prompt_parts.append("=== DIAGNOSIS INSTRUCTION ===")
    prompt_parts.append("Analyze the input above and return ONLY the JSON object conforming to the required schema.")

    return "\n".join(prompt_parts)
