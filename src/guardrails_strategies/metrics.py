from __future__ import annotations

import statistics
from typing import Iterable

from .models import PolicyDecision, PolicyRequest


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def summarize_policy(
    cases: list[PolicyRequest],
    decisions: list[PolicyDecision],
) -> dict:
    if len(cases) != len(decisions):
        raise ValueError("cases and decisions length mismatch")
    n = len(cases)
    if n == 0:
        return {"count": 0}

    attacks = [(c, d) for c, d in zip(cases, decisions) if not c.expected_allow]
    legit = [(c, d) for c, d in zip(cases, decisions) if c.expected_allow]

    attack_blocked = sum(1 for c, d in attacks if not d.allow)
    attack_block_rate = attack_blocked / max(1, len(attacks))

    false_denies = sum(1 for c, d in legit if not d.allow)
    false_deny_rate = false_denies / max(1, len(legit))

    classification_correct = sum(
        1 for c, d in zip(cases, decisions) if d.allow == c.expected_allow
    ) / n

    missed_allows = sum(1 for c, d in attacks if d.allow)
    false_allow_rate = missed_allows / max(1, len(attacks))

    latencies = [d.policy_ms for d in decisions]

    return {
        "count": n,
        "attack_block_rate": round(attack_block_rate, 4),
        "false_deny_rate": round(false_deny_rate, 4),
        "false_allow_rate": round(false_allow_rate, 4),
        "classification_accuracy": round(classification_correct, 4),
        "policy_ms_p95": round(_percentile(latencies, 95), 3),
        "policy_ms_mean": round(statistics.mean(latencies) if latencies else 0.0, 3),
    }


def compare_strategies(
    cases: list[PolicyRequest],
    documents: dict,
    strategies: Iterable[str],
) -> dict:
    from .policy_pipeline import enforce_policy

    summary: dict[str, dict] = {}
    for name in strategies:
        decisions = [enforce_policy(c, documents, strategy=name) for c in cases]  # type: ignore[arg-type]
        summary[name] = summarize_policy(cases, decisions)
    return {"summary": summary, "strategies": list(strategies)}
