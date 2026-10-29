import unittest

from guardrails_strategies.models import PolicyRequest
from guardrails_strategies.policy_pipeline import (
    check_app_acl,
    check_cache_isolation,
    check_identity,
    check_observability,
    check_output_gate,
    check_tools,
    check_worker_context,
)
from guardrails_strategies.data import load_documents
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = load_documents(ROOT / "data/documents.json")


def _req(**kwargs) -> PolicyRequest:
    base = dict(
        id="x",
        tenant_id="billing",
        user_id="u1",
        user_tenants=["billing"],
        expected_allow=True,
    )
    base.update(kwargs)
    return PolicyRequest(**base)


class TestPolicyLayersExtended(unittest.TestCase):
    def test_identity_ok(self):
        self.assertIsNone(check_identity(_req()))

    def test_identity_fail(self):
        self.assertIsNotNone(check_identity(_req(user_id="")))

    def test_app_acl_ok(self):
        self.assertIsNone(check_app_acl(_req()))

    def test_app_acl_fail_membership(self):
        self.assertIsNotNone(check_app_acl(_req(user_tenants=["communications"])))

    def test_cache_ok(self):
        self.assertIsNone(check_cache_isolation(_req(cache_key="k", cache_owner_tenant="billing")))

    def test_cache_fail(self):
        self.assertIsNotNone(
            check_cache_isolation(_req(cache_key="k", cache_owner_tenant="communications"))
        )

    def test_worker_ok(self):
        self.assertIsNone(check_worker_context(_req(worker_job_tenant="billing")))

    def test_worker_fail(self):
        self.assertIsNotNone(check_worker_context(_req(worker_job_tenant="communications")))

    def test_tools_ok(self):
        self.assertIsNone(
            check_tools(_req(tool_name="billing_lookup", tool_args={"tenant_id": "billing"}))
        )

    def test_tools_unknown(self):
        self.assertIsNotNone(check_tools(_req(tool_name="unknown_tool")))

    def test_output_citation_ok(self):
        self.assertIsNone(check_output_gate(_req(output_citations=["doc-billing-refund"]), DOCUMENTS))

    def test_output_citation_fail(self):
        self.assertIsNotNone(
            check_output_gate(_req(output_citations=["doc-comms-playbook"]), DOCUMENTS)
        )

    def test_observability_fail(self):
        self.assertIsNotNone(
            check_observability(
                _req(retrieved_doc_ids=["doc-billing-refund"], log_export_requested=True)
            )
        )

    def test_observability_ok(self):
        self.assertIsNone(check_observability(_req()))


if __name__ == "__main__":
    unittest.main()
