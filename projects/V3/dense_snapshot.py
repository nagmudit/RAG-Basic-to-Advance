"""Chapter 13: versioned, materialized exact dense index for the V0 corpus.

The binary file contains little-endian float32 normalized vectors in manifest
record order. Loading validates the full model/input/source contract before an
ExactIndex can score any eligible item. Scope is a static teaching fixture.
"""

import hashlib
import json
import math
import struct
from pathlib import Path

from exact_vectors import ExactIndex
from experiment_ch11 import MODEL_ID, MODEL_REVISION, embed

DIMENSION = 384
MAX_WORDPIECES = 256
FORMAT = "little-endian-float32-row-major-v1"
TEXT_POLICY = "title + newline + indexed segment body; no ID/status/date in searchable text"
POOLING_POLICY = "attention-mask-aware mean pooling from pinned checkpoint"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def searchable_text(segment):
    return segment["title"] + "\n" + segment["text"]


def encode_batches(model, texts, batch_size):
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError("Batch size must be positive")
    # The pinned Chapter 11 model has no query/document prompt. Preserve its
    # shared encode path exactly; another model needs a new input contract.
    return embed(model, texts, batch_size=batch_size)


def write_snapshot(base, model, directory, *, batch_size=16):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if getattr(model, "max_seq_length", MAX_WORDPIECES) != MAX_WORDPIECES:
        raise ValueError("Encoder token limit differs from pinned index contract")
    segments = list(base.segments)
    vectors = encode_batches(model, [searchable_text(s) for s in segments], batch_size)
    if len(vectors) != len(segments):
        raise ValueError("Vector count mismatch")
    payload = b"".join(struct.pack("<384f", *vector) for vector in vectors)
    records = [{"segment_id": s["segment_id"],
                "allowed_scopes": sorted(s["allowed_scopes"]),
                "searchable_text_sha256": digest(searchable_text(s).encode("utf-8"))}
               for s in segments]
    manifest = {
        "format": FORMAT, "dimension": DIMENSION, "count": len(records),
        "corpus_snapshot": base.snapshot, "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION, "encoder_roles": "shared encode for query and passage",
        "text_policy": TEXT_POLICY, "max_sequence_length_wordpieces": MAX_WORDPIECES,
        "pooling_policy": POOLING_POLICY,
        "normalization": "L2 unit vectors before float32 storage",
        "metric": "cosine", "tie_rule": "score descending, segment ID ascending",
        "vector_file": "vectors.f32", "vector_sha256": digest(payload),
        "records": records,
    }
    version_material = json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
    manifest["index_version"] = "ch13-exact-" + digest(version_material)[:16]
    (directory / "vectors.f32").write_bytes(payload)
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def load_snapshot(base, directory, *, expected_model_revision=MODEL_REVISION):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    segments = list(base.segments)
    expected = [{"segment_id": s["segment_id"],
                 "allowed_scopes": sorted(s["allowed_scopes"]),
                 "searchable_text_sha256": digest(searchable_text(s).encode("utf-8"))}
                for s in segments]
    if (manifest["format"] != FORMAT or manifest["dimension"] != DIMENSION or
            manifest["count"] != len(expected) or manifest["records"] != expected or
            manifest["corpus_snapshot"] != base.snapshot or
            manifest["model_id"] != MODEL_ID or
            manifest["model_revision"] != expected_model_revision or
            manifest["encoder_roles"] != "shared encode for query and passage" or
            manifest["text_policy"] != TEXT_POLICY or
            manifest["max_sequence_length_wordpieces"] != MAX_WORDPIECES or
            manifest["pooling_policy"] != POOLING_POLICY or
            manifest["normalization"] != "L2 unit vectors before float32 storage" or
            manifest["metric"] != "cosine" or
            manifest["tie_rule"] != "score descending, segment ID ascending" or
            manifest["vector_file"] != "vectors.f32"):
        raise ValueError("Dense index manifest is incompatible with query/source contract")
    without_version = {k: v for k, v in manifest.items() if k != "index_version"}
    expected_version = "ch13-exact-" + digest(
        json.dumps(without_version, sort_keys=True, ensure_ascii=False).encode("utf-8"))[:16]
    if manifest["index_version"] != expected_version:
        raise ValueError("Dense index version does not match manifest")
    payload = (directory / "vectors.f32").read_bytes()
    if len(payload) != len(expected) * DIMENSION * 4 or digest(payload) != manifest["vector_sha256"]:
        raise ValueError("Dense vector payload length or checksum mismatch")
    flat = struct.unpack(f"<{len(expected) * DIMENSION}f", payload)
    records = []
    for i, source in enumerate(expected):
        vector = flat[i * DIMENSION:(i + 1) * DIMENSION]
        magnitude = math.sqrt(math.fsum(v * v for v in vector))
        if not all(math.isfinite(v) for v in vector) or abs(magnitude - 1) > 1e-4:
            raise ValueError("Nonfinite or nonunit stored vector")
        records.append({"item_id": source["segment_id"], "vector": vector,
                        "allowed_scopes": source["allowed_scopes"]})
    return manifest, ExactIndex(records, version=manifest["index_version"])
