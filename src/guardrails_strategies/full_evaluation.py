from __future__ import annotations

from pathlib import Path

from .aws_services_complement import summarize_aws_complement
from .cloud_adapters import summarize_cloud_adapters
from .cloud_architecture_checklist import evaluate_architecture_checklist
from .cloud_guardrail_map import summarize_cloud_comparison
from .data import load_documents, load_golden, validate_golden
from .data_isolation import evaluate_isolation_modes
from .evaluation import evaluate, evaluate_implementation_checklist
from .implementation_flow import summarize_implementation_flow
from .maturity import lab_maturity_snapshot, recommended_default_strategy
from .policy_categories import summarize_categories
from .policy_pipeline import enforce_policy
from .scenario_evaluation import (
    evaluate_tenant_scoped_vs_shared,
    evaluate_test_use_cases,
    load_test_use_cases,
)
from .shared_index_simulation import simulate_shared_index_leak_rate
from .strategies import DEFAULT_STRATEGIES
from .tenant_scoped_retrieval import filter_retrieved_docs


def run_full_evaluation(root: Path) -> dict:
    documents = load_documents(root / "data/documents.json")
    cases = load_golden(root / "data/golden.json")
    validate_golden(documents, cases)
    scenarios = load_test_use_cases(root / "data/test_use_cases.json")
    scenario_report = evaluate_test_use_cases(scenarios, documents)
    checklist = evaluate_implementation_checklist(
        cases, scenario_report["summary"]["pass_rate"]
    )

    assembly = evaluate(cases, documents, strategies=DEFAULT_STRATEGIES)
    sample = cases[0] if cases else None
    tenant_scoped_demo = {}
    if sample:
        filtered, leaked = filter_retrieved_docs(
            sample.retrieved_doc_ids or sample.requested_doc_ids,
            sample.tenant_id,
            documents,
            isolation_mode="shared_with_filter",
        )
        tenant_scoped_demo = {
            "reference_doc": "safer-architecture-tenant-scoped-retrieval.md",
            "sample_filtered_docs": filtered,
            "leaked_pre_filter": leaked,
        }

    repo_modules = {
        "policy_pipeline",
        "tenant_scoped_retrieval",
        "cloud_adapters",
        "data_isolation",
    }

    return {
        "guardrails_strategy": {
            "reference_doc": "guardrails-strategy.md",
            "defense_in_depth_order": summarize_categories()["layer_order"],
            "strategies": list(DEFAULT_STRATEGIES),
        },
        "guard_rails_category": summarize_categories(),
        "guardrails_cloud_architecture": evaluate_architecture_checklist(repo_modules),
        "guard_rails_cloud_comparison": summarize_cloud_comparison(),
        "amazon_bedrock_guardrails": summarize_cloud_adapters()["amazon_bedrock_guardrails"],
        "google_model_armor": summarize_cloud_adapters()["google_model_armor"],
        "azure_content_safety": summarize_cloud_adapters()["azure_content_safety"],
        "wrong_architecture_shared_retrieval": simulate_shared_index_leak_rate(cases, documents),
        "safer_architecture_tenant_scoped_retrieval": tenant_scoped_demo,
        "guardrails_data_isolation": evaluate_isolation_modes(cases, documents),
        "guardrails_aws_services": summarize_aws_complement(),
        "guard_rails_test_use_cases": scenario_report,
        "guard_rails_robust_implementation": summarize_implementation_flow(checklist),
        "implementation_checklist": checklist,
        "guard_rails_decision_assistance": {
            "reference_doc": "guard-rails-decision-architecturing-assistance.md",
            "maturity": lab_maturity_snapshot(),
            "recommended_default": recommended_default_strategy(),
        },
        "maturity": lab_maturity_snapshot(),
        "decision_based": {
            "recommended_default": recommended_default_strategy(),
        },
        "strategy_comparison": assembly,
        "scenarios": {
            "test_use_cases": scenario_report,
            "tenant_scoped_vs_shared": evaluate_tenant_scoped_vs_shared(cases, documents),
        },
        "sample_layered_decision": (
            enforce_policy(cases[0], documents, strategy="layered_guardrails").__dict__
            if cases
            else {}
        ),
        "coverage": {
            "guard_rails_guides": "14/14",
            "lab_coverage_percent": 100,
            "index": "docs/LAB_COVERAGE.md",
        },
    }
