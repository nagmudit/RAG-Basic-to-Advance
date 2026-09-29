"""Chapter 1: audit a manually selected evidence path, without doing retrieval.

Run from the repository root: python labs/chapter-01/source_trace.py
The fictional source text is embedded to make the example reproducible.
"""

import json
from time import perf_counter


DOCUMENTS = {
    "D1": {
        "allowed_scopes": {"support-team"},
        "spans": {
            "§3": "For Sev-1 incidents, the initial response target is four hours.",
            "§8": "Either party may terminate this agreement with 30 days' written notice.",
        },
    },
    "D2": {
        "allowed_scopes": {"support-team"},
        "spans": {
            "§2": (
                "Section 3’s Sev-1 initial response target is replaced "
                "with one hour, effective 15 May 2026."
            )
        },
    },
    "D3": {
        "allowed_scopes": {"support-team"},
        "spans": {"FAQ-7": "The Sev-1 initial response target is four hours."},
    },
}

REQUEST = {
    "request_id": "r-01",
    "query_id": "q-contract-change",
    "corpus_snapshot": "support-corpus-2026-05-20",
    "scope": "support-team",
    # Search has not been implemented. This list is supplied by the learner.
    "candidate_ids": ["D3", "D1", "D2"],
    "selected_evidence": [
        {
            "document_id": "D1",
            "span": "§3",
            "quote": "For Sev-1 incidents, the initial response target is four hours.",
        },
        {
            "document_id": "D2",
            "span": "§2",
            "quote": (
                "Section 3’s Sev-1 initial response target is replaced "
                "with one hour, effective 15 May 2026."
            ),
        },
    ],
}


def audit_locators(request, documents):
    """Check scope, candidate membership and exact source locators only."""
    candidate_ids = set(request["candidate_ids"])
    for document_id in candidate_ids:
        document = documents.get(document_id)
        if document is None:
            raise ValueError(f"Candidate document is missing: {document_id}")
        if request["scope"] not in document["allowed_scopes"]:
            raise PermissionError("Candidate is not eligible for this scope")
    evidence_refs = []
    for item in request["selected_evidence"]:
        document_id = item["document_id"]
        if document_id not in candidate_ids:
            raise ValueError(f"Selected evidence was not a candidate: {document_id}")
        document = documents[document_id]
        source_text = document["spans"].get(item["span"])
        if source_text is None or not item["quote"] or item["quote"] not in source_text:
            raise ValueError(f"Quote or span does not match source: {document_id}")
        evidence_refs.append({"document_id": document_id, "span": item["span"]})
    return evidence_refs


if __name__ == "__main__":
    started = perf_counter()
    refs = audit_locators(REQUEST, DOCUMENTS)
    # This measures the small audit step, not end-to-end RAG request latency.
    audit_latency_ms = round((perf_counter() - started) * 1000, 3)
    trace = {
        "request_id": REQUEST["request_id"],
        "query_id": REQUEST["query_id"],
        "corpus_snapshot": REQUEST["corpus_snapshot"],
        "candidate_ids": REQUEST["candidate_ids"],
        "selected_evidence": refs,
        "status": "locators_verified",
        "claim_support": "requires_separate_review",
        "audit_latency_ms": audit_latency_ms,
    }
    # No raw source text or requester identity appears in this record.
    print(json.dumps(trace, ensure_ascii=True, indent=2))
