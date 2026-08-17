"""
Unit Test Suite for NetSage AI Diagnosis Engine (Phase 4).
Tests schema validation, confidence bounds, prompt formatting, missing API key handling,
and evaluation functionality.
"""

import unittest
from ai.schemas import DiagnosisResult, DiagnosisSchemaError
from ai.prompts import build_diagnosis_prompt
from ai.diagnosis import DiagnosisEngine, LLMAPIError
from evaluation.evaluate_ai import evaluate_dataset


class TestDiagnosisSchema(unittest.TestCase):
    """Test suite for DiagnosisResult schema and validation."""

    def test_valid_schema(self):
        data = {
            "root_cause": "VLAN 30 is missing on switch",
            "confidence": 0.88,
            "osi_layer": "Layer 2 - Data Link",
            "evidence": ["show vlan brief lacks VLAN 30"],
            "next_command": ["show interfaces trunk"],
            "fix_steps": ["vlan 30"]
        }
        res = DiagnosisResult.from_dict(data)
        self.assertEqual(res.confidence, 0.88)
        self.assertEqual(res.root_cause, "VLAN 30 is missing on switch")

    def test_invalid_confidence_above_one(self):
        data = {
            "root_cause": "VLAN 30 missing",
            "confidence": 1.5,
            "osi_layer": "Layer 2",
            "evidence": [],
            "next_command": [],
            "fix_steps": []
        }
        with self.assertRaises(DiagnosisSchemaError):
            DiagnosisResult.from_dict(data)

    def test_invalid_confidence_negative(self):
        data = {
            "root_cause": "VLAN 30 missing",
            "confidence": -0.2,
            "osi_layer": "Layer 2",
            "evidence": [],
            "next_command": [],
            "fix_steps": []
        }
        with self.assertRaises(DiagnosisSchemaError):
            DiagnosisResult.from_dict(data)

    def test_invalid_confidence_type(self):
        data = {
            "root_cause": "VLAN 30 missing",
            "confidence": "very high",
            "osi_layer": "Layer 2",
            "evidence": [],
            "next_command": [],
            "fix_steps": []
        }
        with self.assertRaises(DiagnosisSchemaError):
            DiagnosisResult.from_dict(data)

    def test_missing_required_field(self):
        data = {
            "confidence": 0.9,
            "osi_layer": "Layer 2",
            "evidence": [],
            "next_command": [],
            "fix_steps": []
        }
        with self.assertRaises(DiagnosisSchemaError):
            DiagnosisResult.from_dict(data)


class TestPromptBuilder(unittest.TestCase):
    """Test suite for prompt generation."""

    def test_prompt_includes_inputs_and_excludes_expected_fault(self):
        symptom = "PC-1 cannot ping Server-1"
        topology = "PC-1 -> SW1 -> Router R1"
        show_outputs = "show vlan brief output here"
        rule_results = [{"rule_id": "VLAN-001", "status": "FAIL", "message": "VLAN 30 missing"}]

        prompt = build_diagnosis_prompt(
            symptom=symptom,
            topology_note=topology,
            show_outputs=show_outputs,
            rule_results=rule_results
        )

        self.assertIn("PC-1 cannot ping Server-1", prompt)
        self.assertIn("PC-1 -> SW1 -> Router R1", prompt)
        self.assertIn("show vlan brief output here", prompt)
        self.assertIn("VLAN-001", prompt)
        self.assertNotIn("expected_fault", prompt.lower())
        self.assertNotIn("expected fault", prompt.lower())


class TestDiagnosisEngine(unittest.TestCase):
    """Test suite for DiagnosisEngine API handling."""

    def test_missing_api_key_raises_error(self):
        engine = DiagnosisEngine(api_key="")
        with self.assertRaises(LLMAPIError):
            engine.diagnose(symptom="PC cannot reach router")

    def test_mock_diagnosis_response(self):
        engine = DiagnosisEngine(api_key="")
        mock = {
            "root_cause": "Interface Gig0/1 is shut down",
            "confidence": 0.95,
            "osi_layer": "Layer 1 - Physical",
            "evidence": ["Gi0/1 is administratively down"],
            "next_command": ["show ip interface brief"],
            "fix_steps": ["no shutdown"]
        }
        res = engine.diagnose(symptom="Port down", mock_response=mock)
        self.assertEqual(res.status if hasattr(res, 'status') else res.confidence, 0.95)
        self.assertEqual(res.root_cause, "Interface Gig0/1 is shut down")


class TestAIEvaluation(unittest.TestCase):
    """Test suite for dataset evaluation harness."""

    def test_evaluate_dataset_mock(self):
        report = evaluate_dataset(
            cases_path="data/cases.csv",
            diagnoses_path="data/ai_diagnoses.jsonl",
            use_mock=True
        )
        self.assertEqual(report["total_cases_evaluated"], 40)
        self.assertEqual(report["correct_diagnoses"], 40)
        self.assertEqual(report["diagnosis_accuracy_pct"], 100.0)
        self.assertTrue(report["is_mock_evaluation"])


if __name__ == "__main__":
    unittest.main()
