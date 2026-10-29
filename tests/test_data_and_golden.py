import unittest
from pathlib import Path

from guardrails_strategies.data import load_documents, load_golden, validate_golden

ROOT = Path(__file__).resolve().parents[1]


class TestGoldenData(unittest.TestCase):
    def test_documents_load(self):
        docs = load_documents(ROOT / "data/documents.json")
        self.assertGreaterEqual(len(docs), 5)

    def test_golden_validates(self):
        docs = load_documents(ROOT / "data/documents.json")
        cases = load_golden(ROOT / "data/golden.json")
        validate_golden(docs, cases)
        self.assertGreaterEqual(len(cases), 10)

    def test_unknown_doc_raises(self):
        docs = load_documents(ROOT / "data/documents.json")
        cases = load_golden(ROOT / "data/golden.json")
        cases[0].requested_doc_ids = ["doc-nonexistent"]
        with self.assertRaises(ValueError):
            validate_golden(docs, cases)

    def test_tenant_alignment_billing(self):
        docs = load_documents(ROOT / "data/documents.json")
        self.assertEqual(docs["doc-billing-refund"].tenant, "billing")


if __name__ == "__main__":
    unittest.main()
