from __future__ import annotations

import json
from pathlib import Path

from .models import DocumentRecord, PolicyRequest
from .policy_pipeline import enforce_policy
from .tenant_scoped_retrieval import filter_retrieved_docs


def load_test_use_cases(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    return payload.get("scenarios", [])


def evaluate_test_use_cases(
    scenarios: list[dict],
    documents: dict[str, DocumentRecord],
) -> dict:
    results = []
    for row in scenarios:
        req = _scenario_to_request(row)
        decision = enforce_policy(req, documents, strategy="layered_guardrails")
        ok = decision.allow == row["expected_allow"]
        results.append(
            {
                "scenario_id": row["id"],
                "passed": ok,
                "expected_allow": row["expected_allow"],
                "actual_allow": decision.allow,
                "layer_blocked": decision.layer_blocked,
            }
        )
    passed = sum(1 for r in results if r["passed"])
    return {
        "reference_doc": "guard-rails-test-use-cases.md",
        "summary": {
            "pass_rate": round(passed / max(1, len(results)), 4),
            "passed": passed,
            "total": len(results),
        },
        "results": results,
    }


def evaluate_tenant_scoped_vs_shared(
    cases: list[PolicyRequest],
    documents: dict[str, DocumentRecord],
) -> dict:
    scoped_ok = 0
    shared_leak = 0
    n = 0
    for case in cases:
        if "retrieval_compare" not in case.tags:
            continue
        n += 1
        decision = enforce_policy(case, documents, strategy="layered_guardrails")
        if decision.allow == case.expected_allow:
            scoped_ok += 1
        shared = _shared_antipattern(case, documents)
        if shared and case.expected_allow is False:
            shared_leak += 1
    return {
        "tenant_scoped_match_rate": round(scoped_ok / max(1, n), 4),
        "shared_index_false_allow_signals": shared_leak,
        "cases": n,
    }


def _shared_antipattern(case: PolicyRequest, documents: dict[str, DocumentRecord]) -> bool:
    _, leaked = filter_retrieved_docs(
        case.retrieved_doc_ids,
        case.tenant_id,
        documents,
        isolation_mode="shared_no_filter",
    )
    return bool(leaked)


def _scenario_to_request(row: dict) -> PolicyRequest:
    return PolicyRequest(
        id=row["id"],
        scenario_id=row["id"],
        tenant_id=row["tenant_id"],
        user_id=row.get("user_id", "user-a"),
        user_tenants=row.get("user_tenants", [row["tenant_id"]]),
        expected_allow=row["expected_allow"],
        claimed_tenant_id=row.get("claimed_tenant_id"),
        requested_doc_ids=row.get("requested_doc_ids", []),
        search_query=row.get("search_query", ""),
        retrieved_doc_ids=row.get("retrieved_doc_ids", []),
        tool_name=row.get("tool_name"),
        tool_args=row.get("tool_args", {}),
        output_text=row.get("output_text", ""),
        output_citations=row.get("output_citations", []),
        cache_key=row.get("cache_key", ""),
        cache_owner_tenant=row.get("cache_owner_tenant", ""),
        worker_job_tenant=row.get("worker_job_tenant"),
        isolation_mode=row.get("isolation_mode", "shared_with_filter"),
        retrieved_contains_injection=row.get("retrieved_contains_injection", False),
        log_export_requested=row.get("log_export_requested", False),
        tags=row.get("tags", []),
    )
