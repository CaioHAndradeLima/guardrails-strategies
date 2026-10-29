from __future__ import annotations

import json
from pathlib import Path

from .models import DocumentRecord, PolicyRequest


def load_documents(path: Path) -> dict[str, DocumentRecord]:
    payload = json.loads(path.read_text())
    docs: dict[str, DocumentRecord] = {}
    for row in payload.get("documents", []):
        doc = DocumentRecord(
            doc_id=row["doc_id"],
            tenant=row["tenant"],
            title=row.get("title", ""),
            text=row.get("text", ""),
            unique_phrase=row.get("unique_phrase", ""),
        )
        docs[doc.doc_id] = doc
    return docs


def _row_to_case(row: dict) -> PolicyRequest:
    return PolicyRequest(
        id=row["id"],
        tenant_id=row["tenant_id"],
        user_id=row["user_id"],
        user_tenants=row.get("user_tenants", [row["tenant_id"]]),
        expected_allow=row["expected_allow"],
        claimed_tenant_id=row.get("claimed_tenant_id"),
        requested_doc_ids=row.get("requested_doc_ids", []),
        search_query=row.get("search_query", ""),
        retrieved_doc_ids=row.get("retrieved_doc_ids", []),
        tool_name=row.get("tool_name"),
        tool_args=row.get("tool_args", {}),
        output_text=row.get("output_text", ""),
        output_citations=row.get("output_citations", []),
        cache_key=row.get("cache_key", ""),
        cache_owner_tenant=row.get("cache_owner_tenant", ""),
        worker_job_tenant=row.get("worker_job_tenant"),
        isolation_mode=row.get("isolation_mode", "shared_with_filter"),
        retrieved_contains_injection=row.get("retrieved_contains_injection", False),
        log_export_requested=row.get("log_export_requested", False),
        tags=row.get("tags", []),
        scenario_id=row.get("scenario_id", ""),
    )


def load_golden(path: Path) -> list[PolicyRequest]:
    payload = json.loads(path.read_text())
    return [_row_to_case(row) for row in payload.get("cases", [])]


def validate_golden(documents: dict[str, DocumentRecord], cases: list[PolicyRequest]) -> None:
    for case in cases:
        for doc_id in case.requested_doc_ids + case.retrieved_doc_ids + case.output_citations:
            if doc_id and doc_id not in documents:
                raise ValueError(f"case {case.id} references unknown document {doc_id}")
