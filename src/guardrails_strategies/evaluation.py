from __future__ import annotations

from .metrics import compare_strategies
from .models import PolicyRequest, StrategyName


def evaluate(
    cases: list[PolicyRequest],
    documents: dict,
    *,
    strategies: tuple[StrategyName, ...],
) -> dict:
    return compare_strategies(cases, documents, strategies)


def evaluate_implementation_checklist(cases: list[PolicyRequest], scenario_pass_rate: float) -> dict:
    tags: dict[str, int] = {}
    for case in cases:
        for tag in case.tags:
            tags[tag] = tags.get(tag, 0) + 1
    return {
        "by_tag": tags,
        "overall": {
            "scenario_pass_rate": scenario_pass_rate,
            "layers_exercised": tags.get("layered", 0) > 0,
        },
    }
