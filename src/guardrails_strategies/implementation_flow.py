from __future__ import annotations

CHECKLIST_ITEMS = (
    "identity_before_data_access",
    "tenant_acl_in_application",
    "retrieval_metadata_filter",
    "tool_allowlist_and_tenant_args",
    "output_citation_authorization",
    "cache_tenant_isolation",
    "async_worker_tenant_context",
    "observability_redaction",
    "adversarial_regression_ci",
    "cloud_ai_safety_complement",
)


def summarize_implementation_flow(checklist_eval: dict) -> dict:
    by_tag = checklist_eval.get("by_tag", {})
    covered = [item for item in CHECKLIST_ITEMS if _item_covered(item, by_tag, checklist_eval)]
    return {
        "checklist_items": list(CHECKLIST_ITEMS),
        "covered_in_repo": covered,
        "coverage_fraction": round(len(covered) / len(CHECKLIST_ITEMS), 3),
        "reference_doc": "guard-rails-robust-cloud-rules-implementation.md",
    }


def _item_covered(item: str, by_tag: dict, checklist_eval: dict) -> bool:
    mapping = {
        "identity_before_data_access": "identity" in by_tag or "acl" in by_tag,
        "tenant_acl_in_application": "acl" in by_tag or "cross_tenant" in by_tag,
        "retrieval_metadata_filter": "retrieval" in by_tag or "isolation" in by_tag,
        "tool_allowlist_and_tenant_args": "tool" in by_tag,
        "output_citation_authorization": "output" in by_tag,
        "cache_tenant_isolation": "cache" in by_tag,
        "async_worker_tenant_context": "worker" in by_tag,
        "observability_redaction": "observability" in by_tag,
        "adversarial_regression_ci": "attack" in by_tag or "cross_tenant" in by_tag,
        "cloud_ai_safety_complement": True,
    }
    return mapping.get(item, False)
