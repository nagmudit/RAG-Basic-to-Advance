"""Paths, small helpers, shared data classes and the issue collector."""

from __future__ import annotations

import hashlib
import html
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent          # tools/book/bookkit
TOOLS = HERE.parent                             # tools/book
ROOT = TOOLS.parents[1]                         # repository root
CSS = TOOLS / "book.css"
DEFAULT_CONFIG = ROOT / "book" / "book.toml"
PYGMENTS_STYLE = "friendly"
PT_PER_MM = 72 / 25.4
PX_PER_PT = 96 / 72


# ------------------------------------------------------------------ issues

class Issues:
    """Collects build findings. Errors are high-confidence defects; warnings are
    heuristics or layout concerns; notes are informational."""

    def __init__(self):
        self.items: dict[tuple[str, str], None] = {}

    def add(self, level: str, msg: str) -> None:
        self.items.setdefault((level, msg), None)

    def error(self, msg: str) -> None:
        self.add("error", msg)

    def warn(self, msg: str) -> None:
        self.add("warning", msg)

    def note(self, msg: str) -> None:
        self.add("note", msg)

    def of(self, level: str) -> list[str]:
        return [m for (lv, m) in self.items if lv == level]

    def clear(self) -> None:
        self.items.clear()


# ----------------------------------------------------------------- helpers

def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def gh_slug(text: str) -> str:
    """GitHub-style heading anchor, so existing `file.md#frag` links resolve."""
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def id_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def short_id(text: str, limit: int) -> str:
    """Cap an anchor's length (PDF named destinations are dropped beyond ~127 bytes)."""
    if len(text) <= limit:
        return text
    return f"{text[:limit - 9].rstrip('-')}-{hashlib.sha1(text.encode()).hexdigest()[:8]}"


def doc_anchor(path: str) -> str:
    return short_id("d-" + id_slug(path.removesuffix(".md")), 40)


def heading_anchor(doc_id: str, slug: str) -> str:
    return short_id(f"{doc_id}--{slug}", 100)


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def glob_files(patterns: list[str]) -> list[Path]:
    seen, out = set(), []
    for pat in patterns:
        for p in sorted(ROOT.glob(pat), key=lambda p: natural_key(rel(p))):
            r = rel(p)
            if p.is_file() and r not in seen and not r.startswith((".", "build/", "dist/")):
                seen.add(r)
                out.append(p)
    return out


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def first_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("_", " ").title()


def roman(n: int) -> str:
    out = ""
    for v, s in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
                 (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= v:
            out, n = out + s, n - v
    return out


# ------------------------------------------------------------ data classes

@dataclass
class Heading:
    id: str
    text: str
    level: int                   # outline level (1 = top)
    kind: str = "section"        # front | part | chapter | lab | appendix | doc | section | back | unit
    toc: bool = False            # listed in the printed Contents
    running: str | None = None   # recto running head from this page on
    verso: str | None = None     # verso running head from this page on (Part title)
    opener: bool = False         # suppress running head on its page
    page: int | None = None


@dataclass
class Block:
    html: str
    headings: list[Heading] = field(default_factory=list)


@dataclass
class Caption:
    kind: str            # Figure / Table / Plot / Illustration / Listing
    number: str          # "7.01" as written
    title: str
    anchor: str
    chapter: int | None
    doc_id: str
    src: str             # repo path of the Markdown file
    order: int           # occurrence order within the build
    attached: bool = False   # followed by the figure/table it describes
    asset: str | None = None  # repo path of the image, if any

    @property
    def key(self) -> tuple[int, int]:
        a, _, b = self.number.partition(".")
        return int(a), int(b or 0)


@dataclass
class Chapter:
    nn: str
    path: Path
    number: int
    title: str

    @property
    def short_title(self) -> str:
        return self.title.split(" — ", 1)[-1]
