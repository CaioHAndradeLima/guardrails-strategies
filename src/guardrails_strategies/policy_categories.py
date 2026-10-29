from __future__ import annotations

"""Maps guard-rails-category.md taxonomy to enforcement layers in code."""

CATEGORY_LAYER_MAP: dict[str, dict] = {
    "authentication": {"layer": "identity", "module": "policy_pipeline.check_identity"},
    "authorization_tenant": {"layer": "application", "module": "policy_pipeline.check_app_acl"},
    "retrieval_filter": {"layer": "retrieval", "module": "tenant_scoped_retrieval.filter_retrieved_docs"},
    "tool_scope": {"layer": "tools", "module": "policy_pipeline.check_tools"},
    "output_policy": {"layer": "output", "module": "policy_pipeline.check_output_gate"},
    "cache_isolation": {"layer": "application", "module": "policy_pipeline.check_cache_isolation"},
    "observability_redaction": {"layer": "observability", "module": "policy_pipeline.check_observability"},
    "ai_safety_cloud": {"layer": "ai_safety_service", "module": "cloud_adapters"},
    "data_isolation_storage": {"layer": "storage", "module": "data_isolation"},
}


def summarize_categories() -> dict:
    return {
        "reference_doc": "guard-rails-category.md",
        "categories": CATEGORY_LAYER_MAP,
        "layer_order": [
            "identity",
            "application",
            "retrieval",
            "tools",
            "output",
            "observability",
        ],
    }
