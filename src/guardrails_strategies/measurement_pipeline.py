from __future__ import annotations

from .metrics import compare_strategies
from .models import PolicyRequest, StrategyName


def run_measurement_pipeline(
    cases: list[PolicyRequest],
    documents: dict,
    *,
    strategies: tuple[StrategyName, ...],
) -> dict:
    report = compare_strategies(cases, documents, strategies)
    report["eval_type"] = "guardrails_measure"
    return report
