import unittest
from pathlib import Path

from guardrails_strategies.data import load_documents
from guardrails_strategies.scenario_evaluation import evaluate_test_use_cases, load_test_use_cases

ROOT = Path(__file__).resolve().parents[1]


class TestScenarios(unittest.TestCase):
    def test_all_use_cases_pass(self):
        documents = load_documents(ROOT / "data/documents.json")
        scenarios = load_test_use_cases(ROOT / "data/test_use_cases.json")
        report = evaluate_test_use_cases(scenarios, documents)
        self.assertEqual(report["summary"]["pass_rate"], 1.0)
        self.assertEqual(report["summary"]["total"], 10)


if __name__ == "__main__":
    unittest.main()
