from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

IsolationMode = Literal["per_tenant_index", "shared_with_filter", "shared_no_filter"]
StrategyName = Literal["prompt_only", "app_acl_only", "layered_guardrails"]


@dataclass
class DocumentRecord:
    doc_id: str
    tenant: str
    title: str
    text: str
    unique_phrase: str = ""


@dataclass
class PolicyRequest:
    id: str
    tenant_id: str
    user_id: str
    user_tenants: list[str]
    expected_allow: bool
    claimed_tenant_id: str | None = None
    requested_doc_ids: list[str] = field(default_factory=list)
    search_query: str = ""
    retrieved_doc_ids: list[str] = field(default_factory=list)
    tool_name: str | None = None
    tool_args: dict[str, Any] = field(default_factory=dict)
    output_text: str = ""
    output_citations: list[str] = field(default_factory=list)
    cache_key: str = ""
    cache_owner_tenant: str = ""
    worker_job_tenant: str | None = None
    isolation_mode: IsolationMode = "shared_with_filter"
    retrieved_contains_injection: bool = False
    log_export_requested: bool = False
    tags: list[str] = field(default_factory=list)
    scenario_id: str = ""


@dataclass
class PolicyDecision:
    allow: bool
    layer_blocked: str | None = None
    reason: str = ""
    audit: list[str] = field(default_factory=list)
    policy_ms: float = 0.0
