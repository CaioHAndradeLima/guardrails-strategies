import unittest
from pathlib import Path

from guardrails_strategies.data import load_documents, load_golden, validate_golden
from guardrails_strategies.metrics import compare_strategies
from guardrails_strategies.strategies import DEFAULT_STRATEGIES, select_strategies

ROOT = Path(__file__).resolve().parents[1]


class TestStrategies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = load_documents(ROOT / "data/documents.json")
        cls.cases = load_golden(ROOT / "data/golden.json")
        validate_golden(cls.documents, cls.cases)

    def test_default_strategies(self):
        self.assertEqual(len(DEFAULT_STRATEGIES), 3)

    def test_layered_beats_prompt_on_attacks(self):
        report = compare_strategies(self.cases, self.documents, DEFAULT_STRATEGIES)
        layered = report["summary"]["layered_guardrails"]["attack_block_rate"]
        prompt = report["summary"]["prompt_only"]["attack_block_rate"]
        self.assertGreater(layered, prompt)

    def test_select_strategies_invalid(self):
        with self.assertRaises(ValueError):
            select_strategies(["not_a_strategy"])


if __name__ == "__main__":
    unittest.main()
