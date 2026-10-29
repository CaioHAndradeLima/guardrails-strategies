from __future__ import annotations

"""guard-rails-decision-architecturing-assistance.md maturity snapshot."""


def lab_maturity_snapshot() -> dict:
    return {
        "mvp": {
            "recommended_strategy": "app_acl_only",
            "in_repo": True,
            "notes": "Tenant membership checks on golden requests; no retrieval filter yet.",
        },
        "production_rag": {
            "recommended_strategy": "layered_guardrails",
            "in_repo": True,
            "notes": "Retrieval filter, tool scope, output gate, test-use-case regression.",
        },
        "multi_agent_platform": {
            "recommended_strategy": "layered_guardrails",
            "in_repo": True,
            "notes": "Per-tool tenant args, cache isolation, worker job tenant context.",
        },
        "production_deployment_only": [
            "Live Bedrock Guardrails / Model Armor / Azure Content Safety API wiring",
            "Org-wide IAM, WAF/Shield, and VPC perimeter deploy",
            "Central IdP integration and vector DB row-level security",
            "Production log redaction pipelines and SIEM export",
        ],
    }


def recommended_default_strategy() -> str:
    return "layered_guardrails"
