import unittest

from guardrails_strategies.data import load_documents, load_golden, validate_golden
from guardrails_strategies.models import PolicyRequest
from guardrails_strategies.policy_pipeline import enforce_policy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPolicyPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = load_documents(ROOT / "data/documents.json")
        cls.cases = load_golden(ROOT / "data/golden.json")
        validate_golden(cls.documents, cls.cases)

    def test_legit_billing_allowed(self):
        case = next(c for c in self.cases if c.id == "legit-billing-doc")
        d = enforce_policy(case, self.documents, strategy="layered_guardrails")
        self.assertTrue(d.allow)

    def test_cross_tenant_doc_denied(self):
        case = next(c for c in self.cases if c.id == "attack-cross-tenant-doc")
        d = enforce_policy(case, self.documents, strategy="layered_guardrails")
        self.assertFalse(d.allow)
        self.assertEqual(d.layer_blocked, "retrieval")

    def test_missing_identity_denied(self):
        case = next(c for c in self.cases if c.id == "missing-identity")
        d = enforce_policy(case, self.documents, strategy="layered_guardrails")
        self.assertFalse(d.allow)

    def test_prompt_only_allows_acl_attack(self):
        case = next(c for c in self.cases if c.id == "prompt-only-misses-acl")
        d = enforce_policy(case, self.documents, strategy="prompt_only")
        self.assertTrue(d.allow)

    def test_app_acl_blocks_empty_membership(self):
        case = next(c for c in self.cases if c.id == "prompt-only-misses-acl")
        d = enforce_policy(case, self.documents, strategy="app_acl_only")
        self.assertFalse(d.allow)

    def test_tool_tenant_mismatch(self):
        req = PolicyRequest(
            id="t",
            tenant_id="billing",
            user_id="u",
            user_tenants=["billing"],
            expected_allow=False,
            tool_name="billing_lookup",
            tool_args={"tenant_id": "communications"},
        )
        d = enforce_policy(req, self.documents, strategy="layered_guardrails")
        self.assertFalse(d.allow)
        self.assertEqual(d.layer_blocked, "tools")

    def test_output_injection_blocked(self):
        case = next(c for c in self.cases if c.id == "attack-injection-output")
        d = enforce_policy(case, self.documents, strategy="layered_guardrails")
        self.assertFalse(d.allow)

    def test_cache_isolation(self):
        case = next(c for c in self.cases if c.id == "attack-cache-cross")
        d = enforce_policy(case, self.documents, strategy="layered_guardrails")
        self.assertFalse(d.allow)


if __name__ == "__main__":
    unittest.main()
