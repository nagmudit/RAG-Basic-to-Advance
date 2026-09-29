"""Preflight (manuscript) checks, PDF validation, text-extraction smoke test,
visual snapshots and the build report."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .common import ROOT, Issues, git, glob_files, rel

CAPTION_RE = re.compile(r"^\*\*(Figure|Table|Plot|Illustration|Trace|Listing) (\d+)\.(\d+) — ", re.M)
LINK_RE = re.compile(r"(?<!!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)\s]+)\)|!\[[^\]]*\]\(([^)\s]+)\)")
REF_RE = re.compile(r"(?<![\w.])(Figure|Table) (\d+)\.(\d+)\b")


# ------------------------------------------------------------------ preflight

def scan_captions(text: str, chapter: int | None, src: str, issues: Issues) -> list[tuple]:
    """Check one document's numbered captions; return [(kind, chapter, seq)]."""
    found, last = [], {}
    for m in CAPTION_RE.finditer(text):
        kind, a, b = m[1], int(m[2]), int(m[3])
        family = "Table" if kind == "Table" else "Figure"
        if chapter is not None and a != chapter:
            issues.error(f"{src}: {kind} {m[2]}.{m[3]} is numbered for Chapter {a} but appears in Chapter {chapter}")
        if (family, a, b) in {(f, x, y) for f, x, y in found}:
            issues.error(f"{src}: duplicate {family} number {m[2]}.{m[3]}")
        prev = last.get((family, a))
        if prev is not None and b <= prev:
            issues.error(f"{src}: {family} {m[2]}.{m[3]} appears after {family} {a}.{prev:02d} "
                         f"(numbering must follow document order)")
        elif prev is not None and b != prev + 1:
            issues.warn(f"{src}: {family} numbering jumps from {a}.{prev} to {a}.{b}")
        elif prev is None and b != 1:
            issues.warn(f"{src}: first {family.lower()} of Chapter {a} is numbered {m[2]}.{m[3]}")
        last[(family, a)] = b
        found.append((family, a, b))
    # A numbered figure's image file must carry the same number (figure-NN-SS-...).
    for m in re.finditer(r"^\*\*(Figure|Plot|Illustration) (\d+)\.(\d+) — .*?\n+!\[[^\]]*\]\(([^)]+)\)",
                         text, re.M):
        fm = re.search(r"-(\d{2})-(\d{2})-", Path(m[4]).name)
        if fm and (int(fm[1]), int(fm[2])) != (int(m[2]), int(m[3])):
            issues.error(f"{src}: {m[1]} {m[2]}.{m[3]} shows {Path(m[4]).name}, whose file number is "
                         f"{fm[1]}.{fm[2]}")
    return found


def preflight(cfg: dict, issues: Issues) -> dict:
    """Manuscript integrity across the whole workspace (independent of edition)."""
    src = cfg["sources"]
    chapters = {}
    for p in glob_files([src["chapters"]]):
        if m := re.search(r"chapter-(\d+)", p.name):
            chapters[int(m[1])] = p
    captions: set[tuple] = set()
    for n, p in sorted(chapters.items()):
        captions |= set(scan_captions(p.read_text(encoding="utf-8"), n, rel(p), issues))
    # Every tracked Markdown file: relative links and images must resolve.
    tracked = [ROOT / f for f in git("ls-files", "*.md").splitlines()] or glob_files(["**/*.md"])
    tracked += glob_files(["book/**/*.md"])
    for p in dict.fromkeys(tracked):
        if not p.exists() or rel(p).startswith((".", "build/", "dist/")):
            continue
        text = p.read_text(encoding="utf-8")
        text_nocode = re.sub(r"```.*?```", "", text, flags=re.S)
        text_nocode = re.sub(r"`[^`\n]*`", "", text_nocode)
        for m in LINK_RE.finditer(text_nocode):
            href = m[1] or m[2]
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:|^#|^//", href):
                continue
            target = (p.parent / href.split("#")[0]).resolve()
            if href.split("#")[0] and not target.exists():
                kind = "missing image" if m[2] else "broken relative link"
                issues.error(f"{rel(p)}: {kind} -> {href}")
        # References to figures/tables of written chapters must exist.
        for m in REF_RE.finditer(text_nocode):
            fam, a, b = m[1], int(m[2]), int(m[3])
            if a in chapters and (fam, a, b) not in captions:
                issues.error(f"{rel(p)}: reference to {fam} {m[2]}.{m[3]}, which does not exist")
    # Visual assets: stale renders and figures no chapter uses.
    for mmd in glob_files(["visuals/**/*.mmd"]):
        for out in (mmd.with_suffix(".svg"), mmd.with_suffix(".png")):
            if not out.exists():
                issues.error(f"{rel(mmd)}: rendered {out.suffix} is missing (run with --refresh-visuals)")
            elif out.stat().st_mtime + 1 < mmd.stat().st_mtime:
                issues.warn(f"{rel(out)} is older than its Mermaid source (run with --refresh-visuals)")
    for py in glob_files(["visuals/**/plot-*.py"]):
        m = re.search(r"-(\d{2}-\d{2})-", py.name)
        outs = [o for o in py.parent.glob(f"*-{m[1]}-*") if o.suffix in (".svg", ".png")] if m else []
        if not outs:
            issues.error(f"{rel(py)}: no rendered output found")
        elif any(o.stat().st_mtime + 1 < py.stat().st_mtime for o in outs):
            issues.warn(f"{rel(py)} is newer than its rendered figure (run with --refresh-visuals)")
    for f in glob_files(["visuals/chapter-*/*.svg"]):
        m = re.search(r"-(\d{2})-(\d{2})-", f.name)
        if m and int(m[1]) in chapters and not any(c[1:] == (int(m[1]), int(m[2])) for c in captions):
            issues.warn(f"{rel(f)} has no matching numbered caption in Chapter {int(m[1])}")
    return {"chapters": len(chapters), "captions": len(captions)}


# ------------------------------------------------------------ PDF validation

def validate_pdf(pdf: Path, html_text: str, headings, builder, issues: Issues) -> dict:
    import fitz
    stats = {}
    with fitz.open(pdf) as doc:
        stats["pages"] = doc.page_count
        if doc.page_count == 0:
            issues.error("PDF has no pages")
            return stats
        names = doc.resolve_names()
        internal = external = broken = 0
        fonts, not_embedded = set(), set()
        for page in doc:
            for f in page.get_fonts():
                fonts.add(f[3])
                if f[1] == "n/a" and f[2] != "Type3":
                    not_embedded.add(f[3])
            for l in page.get_links():
                k = l.get("kind")
                if k == fitz.LINK_GOTO:
                    internal += 1
                    if not 0 <= l.get("page", -1) < doc.page_count:
                        broken += 1
                elif k == fitz.LINK_NAMED:
                    internal += 1
                    if l.get("nameddest") not in names and l.get("name") not in names:
                        broken += 1
                elif k == fitz.LINK_URI:
                    external += 1
                    uri = l.get("uri", "")
                    if uri.startswith("file:"):
                        issues.error(f"page {page.number + 1}: link exposes a local file path")
                    elif not re.match(r"(https?|mailto):", uri):
                        issues.warn(f"page {page.number + 1}: unusual link target {uri[:60]}")
        if broken:
            issues.error(f"{broken} internal PDF link(s) point to missing destinations")
        if not_embedded:
            issues.warn(f"fonts not embedded: {', '.join(sorted(not_embedded))}")
        wanted = set(re.findall(r'href="#([^"]+)"', html_text))
        missing = sorted(t for t in wanted if t not in names)
        if missing:
            issues.error(f"{len(missing)} link target(s) produced no PDF destination, e.g. #{missing[0]}")
        toc = doc.get_toc()
        if not toc:
            issues.error("PDF has no bookmarks")
        toc_entries = sum(1 for h in headings if h.toc)
        contents = [h for h in headings if h.id == "contents"]
        if contents and contents[0].page:
            nxt = min((h.page for h in headings if h.page and h.page > contents[0].page and h.opener),
                      default=contents[0].page + 1)
            toc_links = sum(1 for p in range(contents[0].page - 1, nxt - 1)
                            for l in doc[p].get_links() if l.get("kind") in (fitz.LINK_GOTO, fitz.LINK_NAMED))
            if toc_links < toc_entries:
                issues.error(f"Contents has {toc_entries} entries but only {toc_links} clickable links")
        stats.update(internal_links=internal, external_links=external, bookmarks=len(toc),
                     fonts=len(fonts))
        stats.update(nearly_empty_pages(doc, headings, issues,
                                        intentional=("Notes and answers",) if builder.p["answer_space"] else ()))
        stats.update(text_smoke(doc, builder, issues))
    return stats


def nearly_empty_pages(doc, headings, issues: Issues, intentional: tuple[str, ...] = ()) -> dict:
    """Flag pages with a few stray lines before a forced break (widowed chapter endings).
    Pages whose text starts with one of `intentional` (e.g. answer space) are skipped."""
    opener_pages = {h.page for h in headings if h.page and (h.opener or h.kind in ("lab", "part"))}
    flagged = []
    for p in range(3, doc.page_count):             # skip cover and colophon
        page = doc[p]
        if (p + 1) in opener_pages or page.rect.width > page.rect.height:
            continue
        blocks = [b for b in page.get_text("blocks") if 50 < b[1] < page.rect.height - 50]
        if blocks and intentional and blocks[0][4].strip().startswith(intentional):
            continue
        if page.get_images() or page.get_drawings() and len(page.get_drawings()) > 40:
            continue
        used = max((b[3] for b in blocks), default=0) - 57
        if blocks and used < (page.rect.height - 114) * 0.12 and (p + 2) in opener_pages:
            flagged.append(p + 1)
        elif not blocks and (p + 2) not in opener_pages and (p + 1) not in opener_pages:
            flagged.append(p + 1)
    for pg in flagged:
        issues.warn(f"page {pg} is nearly empty (a few lines before a page break)")
    return {"nearly_empty_pages": len(flagged)}


def text_smoke(doc, builder, issues: Issues) -> dict:
    """Copy/paste and search sanity: ligatures, replacement characters, phrases, code, punctuation."""
    text = "\n".join(page.get_text() for page in doc)
    flat = re.sub(r"\s+", " ", text)
    ligs = sorted({c for c in text if 0xFB00 <= ord(c) <= 0xFB06})
    if ligs:
        issues.warn(f"text layer contains ligature code points {ligs}; copied text may not match searches")
    if "�" in text:
        issues.error("text layer contains U+FFFD replacement characters (lost glyph mappings)")
    pua = sum(1 for c in text if 0xE000 <= ord(c) <= 0xF8FF)
    if pua > 20:
        issues.warn(f"text layer contains {pua} private-use characters")
    checked = failed = 0
    samples = []
    for ch in builder.chapters if builder.p["body"] == "chapters" else []:
        for para in ch.path.read_text(encoding="utf-8").split("\n\n"):
            para = para.strip()
            if para and not para.startswith(("#", "*", ">", "|", "!", "`", "-", "\\")):
                plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
                plain = re.sub(r"[*_`]", "", plain)
                words = plain.split()
                if len(words) >= 8:
                    samples.append(" ".join(words[:7]))
                    break
    for code in builder.code_samples()[:5]:
        samples.append(code)
    for s in samples:
        checked += 1
        if s not in flat:
            failed += 1
            issues.warn(f"text extraction: phrase not found in PDF text layer: {s[:60]!r}")
    for mark in ("—", "“", "≈"):
        if mark in "".join(p.read_text(encoding="utf-8") for p in [c.path for c in builder.chapters]) \
                and mark not in text and builder.p["body"] == "chapters":
            issues.warn(f"text extraction: punctuation {mark!r} missing from text layer")
    hyph = len(re.findall(r"[a-z]-\n[a-z]", text))
    return {"text_samples_checked": checked, "text_samples_failed": failed, "hyphenated_breaks": hyph}


# ------------------------------------------------------------ snapshots

def snapshot_pages(doc, headings, builder, dests) -> dict[str, int]:
    """Choose representative pages (1-based) by content type."""
    pick: dict[str, int] = {"cover": 1}
    by_id = {h.id: h for h in headings}

    def first(pred):
        return next((h.page for h in headings if h.page and pred(h)), None)
    pick["contents"] = by_id["contents"].page if "contents" in by_id else None
    pick["part-opener"] = first(lambda h: h.kind == "part")
    pick["chapter-opener"] = first(lambda h: h.kind == "chapter")
    pick["lab"] = first(lambda h: h.kind == "lab")
    for c in builder.captions:
        page = dests.get(c.anchor, (None,))[0]
        if not page:
            continue
        asset = c.asset or ""
        if c.kind == "Table":
            pick.setdefault("table", page)
        elif asset.startswith("build/") or (asset and (ROOT / asset).with_suffix(".mmd").exists()):
            pick.setdefault("diagram", page)
        elif asset and list((ROOT / asset).parent.glob("plot-" + Path(asset).name.split("-", 1)[1][:5] + "*.py")):
            pick.setdefault("plot", page)
    for s in builder.code_samples()[:1]:
        for p in range(doc.page_count):
            if s in re.sub(r"\s+", " ", doc[p].get_text()):
                pick["code"] = p + 1
                break
    for i in range(doc.page_count):
        if doc[i].rect.width > doc[i].rect.height:
            pick["landscape"] = i + 1
            break
    pick["references"] = first(lambda h: h.id.startswith("bib-") or h.text in ("Bibliography",))
    return {k: v for k, v in pick.items() if v}


def snapshots(pdf: Path, out_dir: Path, headings, builder, dests, dpi: int = 70) -> list[str]:
    """Render representative pages; keep the previous set and report visual changes."""
    import fitz
    lines = []
    prev = out_dir / "previous"
    if out_dir.exists():
        if prev.exists():
            shutil.rmtree(prev)
        pngs = list(out_dir.glob("*.png"))
        if pngs:
            prev.mkdir(parents=True)
            for f in pngs:
                f.replace(prev / f.name)
    out_dir.mkdir(parents=True, exist_ok=True)
    with fitz.open(pdf) as doc:
        for name, page in snapshot_pages(doc, headings, builder, dests).items():
            doc[page - 1].get_pixmap(dpi=dpi).save(out_dir / f"{name}.png")
            lines.append(f"{name}: page {page}")
    return lines


def visual_diff(out_dir: Path) -> list[str]:
    """Compare snapshots with the previous build's; write red-highlighted diff images."""
    prev = out_dir / "previous"
    if not prev.exists():
        return ["no previous snapshots to compare"]
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return ["numpy and Pillow are needed for --diff"]
    diff_dir = out_dir / "diff"
    shutil.rmtree(diff_dir, ignore_errors=True)
    diff_dir.mkdir()
    lines = []
    for f in sorted(out_dir.glob("*.png")):
        old = prev / f.name
        if not old.exists():
            lines.append(f"{f.stem}: new")
            continue
        a = np.asarray(Image.open(old).convert("L"), dtype=np.int16)
        b = np.asarray(Image.open(f).convert("L"), dtype=np.int16)
        if a.shape != b.shape:
            lines.append(f"{f.stem}: page size changed")
            continue
        mask = np.abs(a - b) > 24
        pct = 100.0 * mask.mean()
        if pct > 0:
            rgb = np.stack([b, b, b], axis=-1).astype(np.uint8)
            rgb[mask] = (230, 40, 40)
            Image.fromarray(rgb).save(diff_dir / f.name)
        lines.append(f"{f.stem}: {pct:.2f}% of pixels changed")
    return lines
