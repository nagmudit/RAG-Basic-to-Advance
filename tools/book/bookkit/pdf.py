"""Chromium printing and PyMuPDF post-processing."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from . import BUILDER_VERSION
from .common import CSS, Heading, Issues, PX_PER_PT, roman

FONT_CANDIDATES = (r"C:\Windows\Fonts\segoeui.ttf", "/System/Library/Fonts/Helvetica.ttc",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def launch_browser(pw):
    last = None
    for opts in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
        try:
            return pw.chromium.launch(**opts)
        except Exception as e:  # this browser flavour is not installed
            last = e
    sys.exit(f"Could not start Chromium/Edge/Chrome via Playwright: {last}\n"
             f"Try: python -m playwright install chromium")


def print_pdf(browser, html_path: Path, pdf_path: Path, content_width_pt: float, issues: Issues):
    """Print with a viewport as wide as the text block, so in-page measurements match print."""
    page = browser.new_page(viewport={"width": round(content_width_pt * PX_PER_PT), "height": 1100})
    page.on("console", lambda m: m.type == "error" and issues.warn(f"browser: {m.text}"))
    page.goto(html_path.as_uri(), wait_until="load", timeout=180_000)
    page.wait_for_function("window.__BOOK_READY === true", timeout=180_000)
    for e in page.evaluate("window.__BOOK_ERRORS || []"):
        issues.error(e)
    for r in page.evaluate("window.__BOOK_REPORT || []"):
        issues.warn(r)
    page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True, tagged=True)
    page.close()


def top_margin_pt() -> float:
    """The @page top margin from book.css; Chromium's destinations are relative to it."""
    m = re.search(r"@page\s*\{\s*margin:\s*([\d.]+)mm", CSS.read_text(encoding="utf-8"))
    return float(m[1]) * 72 / 25.4 if m else 0.0


def named_destinations(doc, offset: int = 0) -> dict[str, tuple[int, float]]:
    """id -> (1-based page in the final book, y from page top) for each linked anchor."""
    out = {}
    margin = top_margin_pt()
    for name, d in doc.resolve_names().items():
        if isinstance(d, dict) and d.get("page", -1) >= 0:
            page = doc[d["page"]]
            to = d.get("to") or (0, page.rect.height)
            out[name] = (d["page"] + 1 + offset, max(0.0, page.rect.height - to[1]) + margin)
    return out


def label_for(page: int, body_start: int | None, style: str) -> str:
    if style == "roman-front" and body_start:
        return roman(page) if page < body_start else str(page - body_start + 1)
    return str(page)


def finish_pdf(src: Path, cover: Path, dst: Path, headings: list[Heading], dests, builder,
               body_start: int | None) -> dict:
    import fitz
    prof, book = builder.p, builder.book
    doc = fitz.open(src)
    with fitz.open(cover) as c:
        doc.insert_pdf(c, start_at=0)
    n_cover = 1
    style = prof["page_numbers"]
    # Page labels: roman front matter, arabic from the first Part/unit.
    if style == "roman-front" and body_start and body_start > 1:
        doc.set_page_labels([{"startpage": 0, "prefix": "", "style": "r", "firstpagenum": 1},
                             {"startpage": body_start - 1, "prefix": "", "style": "D", "firstpagenum": 1}])
    else:
        doc.set_page_labels([{"startpage": 0, "prefix": "", "style": "D", "firstpagenum": 1}])
    # Bookmarks at the configured depth, pointing at the exact heading position.
    toc, last = [], 0
    for h in headings:
        if not h.page or h.level > prof["bookmark_depth"]:
            continue
        lvl = min(h.level, last + 1) if toc else 1
        y = dests.get(h.id, (h.page, 0.0))[1]
        toc.append([lvl, h.text, h.page, {"kind": fitz.LINK_GOTO, "page": h.page - 1,
                                          "to": fitz.Point(0, max(0.0, y - 12)), "zoom": 0}])
        last = lvl
    doc.set_toc(toc)
    # Running heads (verso: Part or book title; recto: chapter/section) and outer folios.
    font_file = next((f for f in FONT_CANDIDATES if Path(f).exists()), None)
    font = fitz.Font(fontfile=font_file) if font_file else fitz.Font("helv")
    fname = "bookfont" if font_file else "helv"
    openers = {h.page for h in headings if h.opener and h.page}
    events = sorted(((h.page, i, h) for i, h in enumerate(headings) if h.page), key=lambda e: e[:2])
    draft = builder.mode == "draft"
    stamp = (f"Working draft · v{book.get('version', '')} · {builder.commit}{'+' if builder.dirty else ''}"
             if draft else "")
    grey, dark = (0.42, 0.42, 0.42), (0.2, 0.2, 0.2)
    verso = recto = None
    ei = 0
    first_folio = n_cover + 2          # cover and colophon carry no folio
    for pno in range(1, doc.page_count + 1):
        while ei < len(events) and events[ei][0] <= pno:
            h = events[ei][2]
            if h.verso is not None:
                verso = h.verso
            if h.running is not None:
                recto = h.running or None
            ei += 1
        if pno < first_folio:
            continue
        page = doc[pno - 1]
        before = len(page.get_contents())
        w, hgt = page.rect.width, page.rect.height
        mx = 42.5 if w > hgt else 56.7     # landscape pages use 15mm side margins
        label = label_for(pno, body_start, style)
        num = int(label) if label.isdigit() else _roman_value(label)
        is_verso = num % 2 == 0
        if pno not in openers:
            text = (verso or book["title"]) if is_verso else (recto or verso or book["title"])
            while font.text_length(text, 8.5) > w - 2 * mx and len(text) > 10:
                text = text[:-2].rstrip() + "…"
            x = mx if is_verso else w - mx - font.text_length(text, 8.5)
            page.insert_text((x, 34), text, fontsize=8.5, fontname=fname, fontfile=font_file, color=grey)
            page.draw_line((mx, 40), (w - mx, 40), color=(0.82, 0.82, 0.82), width=0.5)
        fx = mx if is_verso else w - mx - font.text_length(label, 9)
        page.insert_text((fx, hgt - 28), label, fontsize=9, fontname=fname, fontfile=font_file, color=dark)
        if stamp:
            sx = w - mx - font.text_length(stamp, 6.5) if is_verso else mx
            page.insert_text((sx, hgt - 28), stamp, fontsize=6.5, fontname=fname, fontfile=font_file,
                             color=(0.62, 0.62, 0.62))
        _mark_artifacts(doc, page, before)
    _metadata(doc, builder)
    tmp = dst.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=1, deflate=True, use_objstms=1)
    doc.close()
    tmp.replace(dst)
    return {"bookmarks": len(toc)}


def _roman_value(s: str) -> int:
    vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = vals.get(a, 0)
        total += -v if vals.get(b, 0) > v else v
    return total


def _mark_artifacts(doc, page, before: int):
    """Wrap stamped header/footer content as /Artifact so assistive technology skips it."""
    for xref in page.get_contents()[before:]:
        data = doc.xref_stream(xref)
        if data and not data.startswith(b"/Artifact"):
            doc.update_stream(xref, b"/Artifact BMC\n" + data + b"\nEMC\n")


def _metadata(doc, builder):
    book, prof = builder.book, builder.p
    keywords = "retrieval-augmented generation; RAG; information retrieval; BM25; search"
    doc.set_metadata({
        "title": book["title"],
        "author": book.get("author", ""),
        "subject": f'{book.get("subtitle", "")} — {prof["edition"]}',
        "keywords": f"{keywords}; edition={prof['name']}; version={book.get('version', '')}; mode={builder.mode}",
        "creator": f"bookkit {BUILDER_VERSION} (profile {prof['name']})",
        "producer": "Chromium + PyMuPDF",
    })
    e = html.escape
    xmp = f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:rb="urn:rag-book:build:1.0#">
   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">{e(book["title"])}</rdf:li></rdf:Alt></dc:title>
   <dc:creator><rdf:Seq><rdf:li>{e(book.get("author", ""))}</rdf:li></rdf:Seq></dc:creator>
   <dc:description><rdf:Alt><rdf:li xml:lang="x-default">{e(book.get("subtitle", ""))}</rdf:li></rdf:Alt></dc:description>
   <dc:language><rdf:Bag><rdf:li>en</rdf:li></rdf:Bag></dc:language>
   <pdf:Keywords>{e(prof["edition"])}</pdf:Keywords>
   <xmp:CreatorTool>bookkit {BUILDER_VERSION}</xmp:CreatorTool>
   <rb:profile>{e(prof["name"])}</rb:profile>
   <rb:edition>{e(prof["edition"])}</rb:edition>
   <rb:version>{e(str(book.get("version", "")))}</rb:version>
   <rb:mode>{e(builder.mode)}</rb:mode>
   <rb:buildDate>{builder.built}</rb:buildDate>
   <rb:commit>{e(builder.commit)}</rb:commit>
   <rb:dirty>{str(builder.dirty).lower()}</rb:dirty>
   <rb:builder>bookkit {BUILDER_VERSION}</rb:builder>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""
    doc.set_xml_metadata(xmp)
    cat = doc.pdf_catalog()
    doc.xref_set_key(cat, "ViewerPreferences", "<</DisplayDocTitle true>>")
    doc.xref_set_key(cat, "Lang", "(en)")
    doc.xref_set_key(cat, "PageMode", "/UseOutlines")
