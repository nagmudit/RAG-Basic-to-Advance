"""Check immutable audited results without pretending they used today's code."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def verify_historical_result(path):
    path = Path(path).resolve()
    manifest = json.loads((Path(__file__).with_name("HISTORICAL_RESULTS.json")).read_text(encoding="utf-8"))
    identity = path.relative_to(ROOT).as_posix()
    actual = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    return actual == manifest["records"][identity]["sha256_lf"]
