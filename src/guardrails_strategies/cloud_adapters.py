from __future__ import annotations

"""Optional offline stubs for cloud AI safety controls (Bedrock, Model Armor, Azure)."""

import os
from typing import Literal

Provider = Literal["aws_bedrock", "gcp_model_armor", "azure_content_safety"]


def live_provider_configured(provider: Provider) -> bool:
    env_keys = {
        "aws_bedrock": "AWS_BEDROCK_GUARDRAIL_ID",
        "gcp_model_armor": "GCP_MODEL_ARMOR_TEMPLATE",
        "azure_content_safety": "AZURE_CONTENT_SAFETY_ENDPOINT",
    }
    return bool(os.environ.get(env_keys[provider], "").strip())


def offline_screen(text: str, *, provider: Provider) -> dict:
    """Deterministic lexical stub used in CI; swap for live API when keys are set."""
    blocked = "ignore previous instructions" in text.lower()
    return {
        "provider": provider,
        "mode": "live" if live_provider_configured(provider) else "offline_stub",
        "blocked": blocked,
        "reason": "injection_pattern" if blocked else None,
    }


def summarize_cloud_adapters() -> dict:
    return {
        "amazon_bedrock_guardrails": {
            "reference_doc": "ai-specific-controls-amazon-bedrock-guardrails.md",
            "offline_stub": offline_screen("test", provider="aws_bedrock"),
            "live_configured": live_provider_configured("aws_bedrock"),
        },
        "google_model_armor": {
            "reference_doc": "ai-specific-controls-google-model-armor.md",
            "offline_stub": offline_screen("test", provider="gcp_model_armor"),
            "live_configured": live_provider_configured("gcp_model_armor"),
        },
        "azure_content_safety": {
            "reference_doc": "ai-specific-controls-azure-content-safety-prompt-shields.md",
            "offline_stub": offline_screen("test", provider="azure_content_safety"),
            "live_configured": live_provider_configured("azure_content_safety"),
        },
    }
