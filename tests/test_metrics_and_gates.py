import json
import unittest
from pathlib import Path

from guardrails_strategies.data import load_documents, load_golden, validate_golden
from guardrails_strategies.measure_profiles import evaluate_gates, load_measure_profiles
from guardrails_strategies.pipeline_evaluation import run_guardrails_pipeline_eval

ROOT = Path(__file__).resolve().parents[1]


class TestMetricsAndGates(unittest.TestCase):
    def test_ci_guardrails_eval_passes(self):
        profile = load_measure_profiles(ROOT / "config/measure_profiles.json")["ci-guardrails-eval"]
        report = run_guardrails_pipeline_eval(ROOT, profile)
        gate = evaluate_gates(report, profile)
        self.assertTrue(gate["passed"], gate.get("failures"))

    def test_measure_profiles_load(self):
        profiles = load_measure_profiles(ROOT / "config/measure_profiles.json")
        self.assertIn("ci-guardrails-eval", profiles)
        self.assertIn("ci-all-strategies", profiles)

    def test_gate_failure_detected(self):
        profile = load_measure_profiles(ROOT / "config/measure_profiles.json")["ci-pipeline-only"]
        bad_report = {"summary": {"layered_guardrails": {"classification_accuracy": 0.1}}}
        gate = evaluate_gates(bad_report, profile)
        self.assertFalse(gate["passed"])


if __name__ == "__main__":
    unittest.main()
