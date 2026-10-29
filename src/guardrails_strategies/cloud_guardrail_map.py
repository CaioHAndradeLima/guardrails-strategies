from __future__ import annotations

"""Responsibility → vendor capability table (guard-rails-cloud-comparison.md)."""

VENDOR_MAP = {
    "edge_waf": {"aws": "AWS WAF / Shield", "gcp": "Cloud Armor", "azure": "Azure WAF / Front Door"},
    "identity": {"aws": "Cognito / IAM", "gcp": "Identity Platform / IAM", "azure": "Entra ID"},
    "tenant_acl_app": {"aws": "App-level + IAM policies", "gcp": "App + IAM", "azure": "App + RBAC"},
    "vector_filter": {"aws": "App-enforced metadata filter", "gcp": "App-enforced metadata filter", "azure": "App-enforced metadata filter"},
    "ai_safety_prompt": {
        "aws": "Bedrock Guardrails",
        "gcp": "Model Armor",
        "azure": "Content Safety + Prompt Shields",
    },
    "secrets_kms": {"aws": "Secrets Manager + KMS", "gcp": "Secret Manager + Cloud KMS", "azure": "Key Vault"},
    "audit_logs": {"aws": "CloudTrail", "gcp": "Cloud Audit Logs", "azure": "Activity Log"},
}


def summarize_cloud_comparison() -> dict:
    return {
        "reference_doc": "guard-rails-cloud-comparison.md",
        "responsibilities": VENDOR_MAP,
        "note": "Application tenant filters remain your code; cloud AI safety APIs complement—not replace—ACL and retrieval boundaries.",
    }
