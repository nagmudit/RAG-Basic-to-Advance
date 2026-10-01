"""Content identity for evidence judgments, independent of ranking algorithms."""
import hashlib
import json

POLICY = "evidence-identity-v1-whitespace-collapse-case-and-punctuation-preserved"


def normalize(text):
    # CRLF/LF, tabs and runs of Unicode whitespace are formatting here.
    # Do not lowercase, stem, strip punctuation, or apply Unicode compatibility folding.
    return " ".join(text.split())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def document_identity(document):
    return {"document_id": document["id"], "source_version": document["version"],
            "allowed_scopes": sorted(set(document["allowed_scopes"])),
            "status": document.get("status"), "effective_on": document.get("effective_on"),
            "source_content_sha256": digest({"title": normalize(document["title"]),
                "sections": [{"span": section["span"], "text": normalize(section["text"])}
                             for section in document["sections"]]})}


def evidence_manifest(index, scope):
    documents = index.source_identities
    records = []
    for ordinal in sorted(index.scope_ordinals.get(scope, ())):
        row = index.segments[ordinal]
        records.append({"segment_id": row["segment_id"],
            "document": documents[row["document_id"]],
            "locator": {key: row[key] for key in ("source_span", "section_order", "segment_number",
                                                 "word_start", "word_end_exclusive")},
            "allowed_scopes": sorted(set(row["allowed_scopes"])),
            "segment_content_sha256": digest({"title": normalize(row["title"]), "text": normalize(row["text"])})})
    payload = {"normalization_policy": POLICY, "corpus_snapshot": index.snapshot,
               "scope_fixture": scope, "retrieval_unit": "indexed_segment", "items": records}
    return {**payload, "manifest_sha256": digest(payload)}


def validate_judgments(data, index):
    saved = data.get("evidence_identity")
    expected = evidence_manifest(index, data["scope_fixture"])
    if saved != expected:
        raise ValueError("Stale/incompatible qrels: evidence content, locator, scope or source manifest changed")
