"""Load book.toml and resolve build profiles (with `extends` inheritance)."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .common import PT_PER_MM

PROFILE_DEFAULTS = {
    "edition": "",
    "description": "",
    "front": [],
    "body": "chapters",
    "labs": "inline",
    "solutions": "companion",
    "practice_sections": [],
    "answer_space": False,
    "appendices": [],
    "back": [],
    "toc_depth": 2,
    "toc_labs": True,
    "bookmark_depth": 4,
    "local_toc": False,
    "figure_metadata": True,
    "page_numbers": "roman-front",
    "xref_pages": "cross-document",
}
CHOICES = {
    "body": {"chapters", "labs", "solutions"},
    "labs": {"inline", "none"},
    "solutions": {"appendix", "companion", "none"},
    "page_numbers": {"roman-front", "arabic"},
    "xref_pages": {"none", "cross-document", "all"},
}
PAPERS_MM = {"a4": (210, 297), "letter": (215.9, 279.4), "b5": (176, 250), "a5": (148, 210),
             "legal": (215.9, 355.6)}


@dataclass
class Paper:
    css: str
    width_pt: float
    height_pt: float


def parse_paper(spec: str) -> Paper:
    key = spec.strip().lower()
    if key in PAPERS_MM:
        w, h = PAPERS_MM[key]
        return Paper(spec, w * PT_PER_MM, h * PT_PER_MM)
    m = re.fullmatch(r"([\d.]+)\s*(mm|in|cm)\s+([\d.]+)\s*(mm|in|cm)", key)
    if not m:
        raise SystemExit(f"book.toml: unsupported paper size {spec!r}")
    unit = {"mm": PT_PER_MM, "cm": 10 * PT_PER_MM, "in": 72.0}
    return Paper(spec, float(m[1]) * unit[m[2]], float(m[3]) * unit[m[4]])


def load(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def resolve_profile(cfg: dict, name: str) -> dict:
    profiles = cfg.get("profiles", {})
    if name not in profiles:
        raise SystemExit(f"unknown profile {name!r}; available: {', '.join(profiles)}")
    chain, cur = [], name
    while cur:
        if cur in chain:
            raise SystemExit(f"profile inheritance loop: {' -> '.join(chain + [cur])}")
        chain.append(cur)
        cur = profiles[cur].get("extends")
        if cur and cur not in profiles:
            raise SystemExit(f"profile {chain[-1]!r} extends unknown profile {cur!r}")
    prof = dict(PROFILE_DEFAULTS)
    for p in reversed(chain):
        prof.update({k: v for k, v in profiles[p].items() if k != "extends"})
    prof["name"] = name
    for key, allowed in CHOICES.items():
        if prof[key] not in allowed:
            raise SystemExit(f"profile {name!r}: {key} must be one of {sorted(allowed)}")
    sections = cfg.get("sections", {})
    for key in ("front", "appendices", "back"):
        for sid in prof[key]:
            if sid not in sections:
                raise SystemExit(f"profile {name!r}: unknown section {sid!r} in {key}")
    return prof
