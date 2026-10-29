from __future__ import annotations

"""Logical layer checklist for guardrails-cloud-architecture.md (no cloud SDK)."""

LAYERS = (
    "edge_protection",
    "identity_authentication",
    "application_authorization",
    "ai_safety_service",
    "retrieval_data_scope",
    "agent_workflow",
    "output_controls",
    "observability_governance",
)


def evaluate_architecture_checklist(repo_modules: set[str]) -> dict:
    """Mark layers covered by in-repo reference modules."""
    mapping = {
        "edge_protection": False,  # documented only
        "identity_authentication": "policy_pipeline" in repo_modules,
        "application_authorization": "policy_pipeline" in repo_modules,
        "ai_safety_service": "cloud_adapters" in repo_modules,
        "retrieval_data_scope": "tenant_scoped_retrieval" in repo_modules,
        "agent_workflow": "policy_pipeline" in repo_modules,
        "output_controls": "policy_pipeline" in repo_modules,
        "observability_governance": "policy_pipeline" in repo_modules,
    }
    covered = sum(1 for v in mapping.values() if v)
    return {
        "reference_doc": "guardrails-cloud-architecture.md",
        "layers": LAYERS,
        "covered_in_reference_repo": mapping,
        "coverage_fraction": round(covered / len(LAYERS), 3),
        "out_of_repo": ["edge_protection", "live_vpc_deploy"],
    }
