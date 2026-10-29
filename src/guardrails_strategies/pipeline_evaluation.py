"""Guard-rails pipeline scorecard: core policy metrics + scenario fixtures."""

from pathlib import Path

from .data import load_documents, load_golden, validate_golden
from .measure_profiles import MeasureProfile
from .measurement_pipeline import run_measurement_pipeline
from .scenario_evaluation import (
    evaluate_tenant_scoped_vs_shared,
    evaluate_test_use_cases,
    load_test_use_cases,
)
from .shared_index_simulation import simulate_shared_index_leak_rate


def build_scorecard(measure_report: dict, *, primary_strategy: str = "layered_guardrails") -> dict:
    core = measure_report.get("summary", {}).get(primary_strategy, {})
    return {
        "primary_strategy": primary_strategy,
        "core_quality": {
            "attack_block_rate": core.get("attack_block_rate"),
            "false_deny_rate": core.get("false_deny_rate"),
            "false_allow_rate": core.get("false_allow_rate"),
            "classification_accuracy": core.get("classification_accuracy"),
            "policy_ms_p95": core.get("policy_ms_p95"),
        },
        "reference_doc": "guard-rails-test-use-cases.md",
    }


def run_guardrails_pipeline_eval(root: Path, profile: MeasureProfile) -> dict:
    documents = load_documents(root / "data/documents.json")
    cases = load_golden(root / "data/golden.json")
    validate_golden(documents, cases)
    scenarios = load_test_use_cases(root / "data/test_use_cases.json")

    strategies = profile.strategies
    measure_report = run_measurement_pipeline(cases, documents, strategies=strategies)
    primary = strategies[0] if strategies else "layered_guardrails"
    scorecard = build_scorecard(measure_report, primary_strategy=primary)

    return {
        **measure_report,
        "eval_type": "guardrails_pipeline",
        "profile": {"name": profile.name, "description": profile.description},
        "scorecard": scorecard,
        "scenarios": {
            "test_use_cases": evaluate_test_use_cases(scenarios, documents),
            "tenant_scoped_vs_shared": evaluate_tenant_scoped_vs_shared(cases, documents),
            "shared_index_antipattern": simulate_shared_index_leak_rate(cases, documents),
        },
    }
