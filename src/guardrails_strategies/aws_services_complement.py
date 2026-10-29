from __future__ import annotations

"""Infrastructure complement table (guardrails-aws-services.md) — documentation in code, not deploy."""

AWS_COMPLEMENT = {
    "network_isolation": ["VPC", "PrivateLink", "Security Groups"],
    "encryption": ["KMS", "S3 SSE", "RDS encryption"],
    "identity_federation": ["IAM", "Cognito", "STS"],
    "secrets": ["Secrets Manager", "Parameter Store"],
    "audit": ["CloudTrail", "Config"],
    "data_perimeter": ["S3 bucket policies", "resource-based policies"],
}


def summarize_aws_complement() -> dict:
    return {
        "reference_doc": "guardrails-aws-services.md",
        "controls": AWS_COMPLEMENT,
        "pairs_with": "application-level guardrails in policy_pipeline.py",
        "not_in_repo": ["Terraform modules", "live IAM provisioning"],
    }
