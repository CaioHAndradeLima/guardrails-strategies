from __future__ import annotations

import time
from typing import Literal

from .models import DocumentRecord, PolicyDecision, PolicyRequest, StrategyName
from .tenant_scoped_retrieval import filter_retrieved_docs

INJECTION_MARKERS = (
    "ignore previous instructions",
    "system prompt",
    "disregard all policies",
    "you are now in developer mode",
)

ALLOWED_TOOLS = {
    "billing_lookup": {"billing", "payments"},
    "support_search": {"billing", "communications", "catalog"},
    "platform_metrics": {"platform"},
}


def check_identity(req: PolicyRequest) -> PolicyDecision | None:
    if not req.user_id or not req.user_id.strip():
        return PolicyDecision(allow=False, layer_blocked="identity", reason="missing_user_id")
    return None


def check_app_acl(req: PolicyRequest) -> PolicyDecision | None:
    effective_tenant = req.claimed_tenant_id or req.tenant_id
    if effective_tenant not in req.user_tenants:
        return PolicyDecision(
            allow=False,
            layer_blocked="application",
            reason="tenant_not_authorized",
        )
    if req.claimed_tenant_id and req.claimed_tenant_id != req.tenant_id:
        if req.claimed_tenant_id not in req.user_tenants:
            return PolicyDecision(
                allow=False,
                layer_blocked="application",
                reason="tenant_spoof_denied",
            )
    return None


def check_retrieval(
    req: PolicyRequest,
    documents: dict[str, DocumentRecord],
) -> PolicyDecision | None:
    tenant = req.tenant_id
    for doc_id in req.requested_doc_ids:
        doc = documents.get(doc_id)
        if doc is None:
            return PolicyDecision(
                allow=False,
                layer_blocked="retrieval",
                reason="unknown_document",
            )
        if doc.tenant != tenant:
            return PolicyDecision(
                allow=False,
                layer_blocked="retrieval",
                reason="cross_tenant_document_access",
            )

    filtered, leak_ids = filter_retrieved_docs(
        req.retrieved_doc_ids,
        tenant,
        documents,
        isolation_mode=req.isolation_mode,
    )
    if leak_ids:
        return PolicyDecision(
            allow=False,
            layer_blocked="retrieval",
            reason="cross_tenant_retrieval_leak",
            audit=[f"leaked_docs:{','.join(leak_ids)}"],
        )

    if req.search_query and leak_ids:
        return PolicyDecision(
            allow=False,
            layer_blocked="retrieval",
            reason="cross_tenant_search_leaked_chunks",
        )
    return None


def check_tools(req: PolicyRequest) -> PolicyDecision | None:
    if not req.tool_name:
        return None
    allowed_tenants = ALLOWED_TOOLS.get(req.tool_name)
    if allowed_tenants is None:
        return PolicyDecision(allow=False, layer_blocked="tools", reason="tool_not_allowed")
    arg_tenant = str(req.tool_args.get("tenant_id", req.tenant_id))
    if arg_tenant != req.tenant_id:
        return PolicyDecision(
            allow=False,
            layer_blocked="tools",
            reason="tool_tenant_mismatch",
        )
    if req.tenant_id not in allowed_tenants:
        return PolicyDecision(
            allow=False,
            layer_blocked="tools",
            reason="tool_scope_denied",
        )
    return None


def check_output_gate(
    req: PolicyRequest,
    documents: dict[str, DocumentRecord],
) -> PolicyDecision | None:
    tenant = req.tenant_id
    for cid in req.output_citations:
        doc = documents.get(cid)
        if doc and doc.tenant != tenant:
            return PolicyDecision(
                allow=False,
                layer_blocked="output",
                reason="unauthorized_citation",
            )
    lower = req.output_text.lower()
    for marker in INJECTION_MARKERS:
        if marker in lower:
            return PolicyDecision(
                allow=False,
                layer_blocked="output",
                reason="injection_in_output",
            )
    return None


def check_cache_isolation(req: PolicyRequest) -> PolicyDecision | None:
    if not req.cache_key:
        return None
    if req.cache_owner_tenant and req.cache_owner_tenant != req.tenant_id:
        return PolicyDecision(
            allow=False,
            layer_blocked="application",
            reason="cross_tenant_cache_access",
        )
    return None


def check_worker_context(req: PolicyRequest) -> PolicyDecision | None:
    if req.worker_job_tenant is None:
        return None
    if req.worker_job_tenant != req.tenant_id:
        return PolicyDecision(
            allow=False,
            layer_blocked="application",
            reason="worker_tenant_mismatch",
        )
    return None


def check_observability(req: PolicyRequest) -> PolicyDecision | None:
    if req.log_export_requested and req.retrieved_doc_ids:
        return PolicyDecision(
            allow=False,
            layer_blocked="observability",
            reason="retrieved_content_log_export_denied",
        )
    return None


def check_prompt_only(req: PolicyRequest) -> PolicyDecision | None:
    text = (req.search_query or "") + " " + req.output_text
    lower = text.lower()
    for marker in INJECTION_MARKERS:
        if marker in lower:
            return PolicyDecision(
                allow=False,
                layer_blocked="prompt_scan",
                reason="injection_pattern",
            )
    if req.retrieved_contains_injection:
        return None  # prompt-only ignores retrieved injection
    return None


def enforce_policy(
    req: PolicyRequest,
    documents: dict[str, DocumentRecord],
    *,
    strategy: StrategyName = "layered_guardrails",
) -> PolicyDecision:
    start = time.perf_counter()
    audit: list[str] = []

    if strategy == "prompt_only":
        block = check_prompt_only(req)
        if block:
            block.policy_ms = (time.perf_counter() - start) * 1000
            return block
        decision = PolicyDecision(allow=True, audit=["prompt_only_pass"])
        decision.policy_ms = (time.perf_counter() - start) * 1000
        return decision

    checks: list[tuple[str, PolicyDecision | None]] = []

    if strategy in ("app_acl_only", "layered_guardrails"):
        for fn, label in (
            (lambda: check_identity(req), "identity"),
            (lambda: check_app_acl(req), "application"),
            (lambda: check_cache_isolation(req), "application"),
            (lambda: check_worker_context(req), "application"),
        ):
            block = fn()
            checks.append((label, block))
            if block:
                block.policy_ms = (time.perf_counter() - start) * 1000
                block.audit = audit + [label]
                return block
            audit.append(f"{label}:ok")

    if strategy == "layered_guardrails":
        for fn, label in (
            (lambda: check_retrieval(req, documents), "retrieval"),
            (lambda: check_tools(req), "tools"),
            (lambda: check_output_gate(req, documents), "output"),
            (lambda: check_observability(req), "observability"),
        ):
            block = fn()
            checks.append((label, block))
            if block:
                block.policy_ms = (time.perf_counter() - start) * 1000
                block.audit = audit + [label]
                return block
            audit.append(f"{label}:ok")

        if req.retrieved_contains_injection:
            audit.append("retrieved_injection:treat_as_untrusted_content")

    decision = PolicyDecision(allow=True, audit=audit)
    decision.policy_ms = (time.perf_counter() - start) * 1000
    return decision


LayerName = Literal[
    "identity",
    "application",
    "retrieval",
    "tools",
    "output",
    "observability",
    "prompt_scan",
]
