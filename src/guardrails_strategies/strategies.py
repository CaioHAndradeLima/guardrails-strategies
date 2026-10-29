from __future__ import annotations

from typing import Iterable

from .models import DocumentRecord, PolicyDecision, PolicyRequest, StrategyName
from .policy_pipeline import enforce_policy

DEFAULT_STRATEGIES: tuple[StrategyName, ...] = (
    "prompt_only",
    "app_acl_only",
    "layered_guardrails",
)


def run_strategy(
    cases: Iterable[PolicyRequest],
    documents: dict[str, DocumentRecord],
    strategy: StrategyName,
) -> list[PolicyDecision]:
    return [enforce_policy(case, documents, strategy=strategy) for case in cases]


def select_strategies(names: list[str] | None) -> tuple[StrategyName, ...]:
    if not names:
        return DEFAULT_STRATEGIES
    allowed = set(DEFAULT_STRATEGIES)
    out: list[StrategyName] = []
    for name in names:
        if name not in allowed:
            raise ValueError(f"Unknown strategy '{name}'")
        out.append(name)  # type: ignore[arg-type]
    return tuple(out)
