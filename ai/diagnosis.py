"""
NetSage AI Diagnosis Engine Implementation.
Modular provider abstraction for executing AI network diagnoses via LLM APIs or mock providers.
Enforces strict output validation against DiagnosisResult schema.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from .schemas import DiagnosisResult, DiagnosisSchemaError
from .prompts import build_diagnosis_prompt


class LLMAPIError(RuntimeError):
    """Raised when the LLM provider API call fails or fails authentication."""
    pass


def _load_env_file():
    """Helper to parse local .env file variables without external dependencies."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line_clean = line.strip()
                if line_clean and not line_clean.startswith("#") and "=" in line_clean:
                    k, v = line_clean.split("=", 1)
                    k_str = k.strip()
                    v_str = v.strip().strip("'\"")
                    if k_str and k_str not in os.environ:
                        os.environ[k_str] = v_str


class DiagnosisEngine:
    """
    Central AI Diagnosis Engine.
    Interfaces with configured LLM API provider (Groq, OpenAI, Gemini, etc.)
    or mock test harness to generate evidence-grounded network troubleshooting diagnoses.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        _load_env_file()
        # Support GROQ_API_KEY or LLM_API_KEY environment variables
        self.api_key = api_key or os.environ.get("GROQ_API_KEY") or os.environ.get("LLM_API_KEY", "").strip()
        
        # Default model: LLaMA 3.3 70B Versatile for Groq, or specified model
        default_model = "llama-3.3-70b-versatile" if (os.environ.get("GROQ_API_KEY") or self.api_key.startswith("gsk_")) else "gemini-1.5-pro"
        self.model = model or os.environ.get("LLM_MODEL", default_model).strip()
        
        # Determine base URL (defaults to Groq OpenAI-compatible endpoint if Groq key or model used)
        custom_base = os.environ.get("LLM_BASE_URL", "").strip()
        if custom_base:
            self.base_url = custom_base.rstrip("/")
        elif self.api_key.startswith("gsk_") or "llama" in self.model.lower() or "mixtral" in self.model.lower() or os.environ.get("GROQ_API_KEY"):
            self.base_url = "https://api.groq.com/openai/v1"
        else:
            self.base_url = "https://api.openai.com/v1"

    def is_api_key_configured(self) -> bool:
        """Checks whether a valid API key is available in environment or configuration."""
        return bool(self.api_key and self.api_key not in ["your_api_key_here", "your_groq_api_key_here"])

    def diagnose(
        self,
        symptom: str,
        topology_note: Optional[str] = None,
        show_outputs: Optional[str] = None,
        rule_results: Optional[List[Dict[str, Any]]] = None,
        mock_response: Optional[Dict[str, Any]] = None
    ) -> DiagnosisResult:
        """
        Executes AI network diagnosis.

        Parameters:
        - symptom: Problem statement (required)
        - topology_note: Device path / network layout (optional)
        - show_outputs: Cisco CLI output evidence (optional)
        - rule_results: Structured output from Phase 3 RuleChecker (optional)
        - mock_response: Pre-defined mock payload for offline testing without API key (optional)

        Returns:
        - Validated DiagnosisResult instance.
        """
        if not symptom or not symptom.strip():
            raise ValueError("Symptom is required for diagnosis.")

        # Build formatted prompt payload (expected_fault is intentionally excluded)
        prompt_text = build_diagnosis_prompt(
            symptom=symptom,
            topology_note=topology_note,
            show_outputs=show_outputs,
            rule_results=rule_results
        )

        # 1. Handle Mock Testing Mode (if mock_response is provided)
        if mock_response is not None:
            if isinstance(mock_response, dict):
                return DiagnosisResult.from_dict(mock_response)
            elif isinstance(mock_response, str):
                return DiagnosisResult.from_json(mock_response)
            else:
                raise DiagnosisSchemaError("Invalid mock_response format provided.")

        # 2. Check for missing API Key before making network call
        if not self.is_api_key_configured():
            raise LLMAPIError(
                "LLM API Key is missing or unconfigured. Please set GROQ_API_KEY or LLM_API_KEY in your environment or .env file."
            )

        # 3. Call LLM Provider API
        raw_response_text = self._call_llm_provider(prompt_text)

        # 4. Parse & Validate Response against DiagnosisResult schema
        try:
            return DiagnosisResult.from_json(raw_response_text)
        except DiagnosisSchemaError as schema_err:
            # Fallback for malformed LLM response to prevent unhandled crashing
            return DiagnosisResult(
                root_cause=f"AI Response Validation Error: {str(schema_err)}",
                confidence=0.0,
                osi_layer="Unknown",
                evidence=["Raw response failed output schema validation."],
                next_command=["Inspect raw LLM output and prompt template."],
                fix_steps=["Re-evaluate case manually or re-run diagnosis with clean evidence."]
            )

    def _call_llm_provider(self, prompt: str) -> str:
        """
        Internal HTTP provider integration to call LLM endpoint using standard library urllib.
        Supports Groq API, OpenAI-compatible REST endpoints, or Google Gemini REST API.
        """
        if "gemini" in self.model.lower() and "groq" not in self.base_url:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    text = res_body["candidates"][0]["content"]["parts"][0]["text"]
                    return text
            except urllib.error.HTTPError as http_err:
                raise LLMAPIError(f"Gemini API returned HTTP Error {http_err.code}: {http_err.reason}")
            except Exception as err:
                raise LLMAPIError(f"LLM API request failed: {str(err)}")
        else:
            # Standard OpenAI-compatible chat completions endpoint (Works for Groq, OpenAI, Ollama, etc.)
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    text = res_body["choices"][0]["message"]["content"]
                    return text
            except urllib.error.HTTPError as http_err:
                err_content = http_err.read().decode("utf-8") if hasattr(http_err, "read") else ""
                raise LLMAPIError(f"LLM Provider API ({self.base_url}) returned HTTP {http_err.code}: {http_err.reason}. Details: {err_content}")
            except Exception as err:
                raise LLMAPIError(f"LLM API request to {self.base_url} failed: {str(err)}")

