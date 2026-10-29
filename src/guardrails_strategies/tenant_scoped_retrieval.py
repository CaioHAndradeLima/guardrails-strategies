from __future__ import annotations

from .models import DocumentRecord, IsolationMode


def filter_retrieved_docs(
    doc_ids: list[str],
    tenant: str,
    documents: dict[str, DocumentRecord],
    *,
    isolation_mode: IsolationMode,
) -> tuple[list[str], list[str]]:
    """Return (authorized_doc_ids, leaked_doc_ids)."""
    if isolation_mode == "shared_no_filter":
        return list(doc_ids), []

    authorized: list[str] = []
    leaked: list[str] = []
    for doc_id in doc_ids:
        doc = documents.get(doc_id)
        if doc is None:
            continue
        if doc.tenant == tenant:
            authorized.append(doc_id)
        else:
            leaked.append(doc_id)
            if isolation_mode == "per_tenant_index":
                continue
    if isolation_mode == "shared_with_filter":
        return authorized, leaked
    return authorized, leaked
