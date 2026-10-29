import unittest
from pathlib import Path

from guardrails_strategies.data import load_documents, load_golden, validate_golden
from guardrails_strategies.measurement_pipeline import run_measurement_pipeline
from guardrails_strategies.strategies import DEFAULT_STRATEGIES

ROOT = Path(__file__).resolve().parents[1]


class TestMeasurementPipeline(unittest.TestCase):
    def test_pipeline_report_shape(self):
        documents = load_documents(ROOT / "data/documents.json")
        cases = load_golden(ROOT / "data/golden.json")
        validate_golden(documents, cases)
        report = run_measurement_pipeline(cases, documents, strategies=DEFAULT_STRATEGIES)
        self.assertEqual(report["eval_type"], "guardrails_measure")
        self.assertIn("layered_guardrails", report["summary"])


if __name__ == "__main__":
    unittest.main()
