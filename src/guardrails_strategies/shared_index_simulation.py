from __future__ import annotations

from dataclasses import replace

from .models import DocumentRecord, PolicyRequest
from .policy_pipeline import enforce_policy


def simulate_shared_index_leak_rate(
    cases: list[PolicyRequest],
    documents: dict[str, DocumentRecord],
) -> dict:
    """Anti-pattern: shared index without retrieval filter — measures false-allow on cross-tenant retrieval."""
    allows_on_attack = 0
    attack_n = 0
    for case in cases:
        if "cross_tenant" not in case.tags and "shared_index" not in case.tags:
            continue
        attack_n += 1
        spoof = replace(case, isolation_mode="shared_no_filter")
        decision = enforce_policy(spoof, documents, strategy="layered_guardrails")
        if decision.allow:
            allows_on_attack += 1
    leak_rate = allows_on_attack / max(1, attack_n)
    return {
        "reference_doc": "wrong-architecture-shared-retrieval.md",
        "attack_cases": attack_n,
        "false_allow_rate_shared_index": round(leak_rate, 4),
        "recommended_mitigation": "tenant_scoped_retrieval + shared_with_filter or per_tenant_index",
    }
