import unittest
from pathlib import Path

from guardrails_strategies.data import load_documents
from guardrails_strategies.shared_index_simulation import simulate_shared_index_leak_rate
from guardrails_strategies.tenant_scoped_retrieval import filter_retrieved_docs

ROOT = Path(__file__).resolve().parents[1]


class TestTenantRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = load_documents(ROOT / "data/documents.json")

    def test_filter_removes_cross_tenant(self):
        filtered, leaked = filter_retrieved_docs(
            ["doc-billing-refund", "doc-comms-playbook"],
            "billing",
            self.documents,
            isolation_mode="shared_with_filter",
        )
        self.assertEqual(filtered, ["doc-billing-refund"])
        self.assertEqual(leaked, ["doc-comms-playbook"])

    def test_shared_no_filter_leaks(self):
        filtered, leaked = filter_retrieved_docs(
            ["doc-comms-playbook"],
            "billing",
            self.documents,
            isolation_mode="shared_no_filter",
        )
        self.assertEqual(filtered, ["doc-comms-playbook"])
        self.assertEqual(leaked, [])

    def test_per_tenant_index(self):
        filtered, leaked = filter_retrieved_docs(
            ["doc-comms-playbook"],
            "billing",
            self.documents,
            isolation_mode="per_tenant_index",
        )
        self.assertEqual(filtered, [])
        self.assertEqual(leaked, ["doc-comms-playbook"])


class TestSharedIndexSimulation(unittest.TestCase):
    def test_simulation_runs(self):
        from guardrails_strategies.data import load_golden

        documents = load_documents(ROOT / "data/documents.json")
        cases = load_golden(ROOT / "data/golden.json")
        report = simulate_shared_index_leak_rate(cases, documents)
        self.assertIn("false_allow_rate_shared_index", report)


if __name__ == "__main__":
    unittest.main()
