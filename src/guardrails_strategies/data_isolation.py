from __future__ import annotations

from .models import IsolationMode, PolicyRequest
from .policy_pipeline import enforce_policy
from .tenant_scoped_retrieval import filter_retrieved_docs


def evaluate_isolation_modes(
    cases: list[PolicyRequest],
    documents: dict,
) -> dict:
    modes: list[IsolationMode] = ["per_tenant_index", "shared_with_filter", "shared_no_filter"]
    by_mode: dict[str, dict] = {}
    for mode in modes:
        cross_leaks = 0
        cross_total = 0
        for case in cases:
            if "isolation" not in case.tags:
                continue
            cross_total += 1
            spoof = _with_mode(case, mode)
            decision = enforce_policy(spoof, documents, strategy="layered_guardrails")
            if decision.allow and not case.expected_allow:
                cross_leaks += 1
        by_mode[mode] = {
            "false_allow_rate": round(cross_leaks / max(1, cross_total), 4),
            "cases": cross_total,
        }
    return {
        "reference_doc": "guardrails-data-isolation.md",
        "by_mode": by_mode,
        "recommended_default": "per_tenant_index",
    }


def _with_mode(case: PolicyRequest, mode: IsolationMode) -> PolicyRequest:
    from dataclasses import replace

    return replace(case, isolation_mode=mode)
