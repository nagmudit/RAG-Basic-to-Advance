#!/usr/bin/env python3
"""Build the RAG book in one or more editions from the canonical workspace.

    python -X utf8 tools/book/build_book.py                       # reader edition
    python -X utf8 tools/book/build_book.py --profile complete
    python -X utf8 tools/book/build_book.py --profile all         # every edition
    python -X utf8 tools/book/build_book.py --check               # preflight only, no PDF
    python -X utf8 tools/book/build_book.py --list-profiles
    python -X utf8 tools/book/build_book.py --diff                # compare page snapshots with last build
    python -X utf8 tools/book/build_book.py --release             # release cover/footers (no build metadata)

Editions are declared in book/book.toml (sections + profiles). Output goes to
dist/rag-book-<profile>.pdf with a .build.json report beside it; working
files and page snapshots go to build/<profile>/ and build/snapshots/<profile>/.

Pipeline: preflight manuscript checks -> Markdown to HTML (markdown-it-py,
Pygments, KaTeX, Mermaid via mmdc) -> headless Chromium prints a tagged PDF,
repeated until page numbers in the Contents, lists and cross-references are
stable -> PyMuPDF adds the cover, page labels, running heads, bookmarks and
metadata -> PDF validation, text-extraction smoke test, snapshots, report.

Exit status is 1 when any error-level finding exists (the PDF is still written).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bookkit import BUILDER_VERSION  # noqa: E402
from bookkit.builder import BookBuilder  # noqa: E402
from bookkit.checks import preflight, snapshots, validate_pdf, visual_diff  # noqa: E402
from bookkit.common import DEFAULT_CONFIG, ROOT, Issues, glob_files, rel  # noqa: E402
from bookkit.config import load, resolve_profile  # noqa: E402
from bookkit.pdf import finish_pdf, launch_browser, named_destinations, print_pdf  # noqa: E402


def find_vendor() -> dict[str, str]:
    """Prefer local KaTeX/mermaid (e.g. from a global mermaid-cli install), else the CDN."""
    cdn = {"katex_js": "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js",
           "katex_css": "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css",
           "mermaid_js": "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"}
    roots = []
    if npm := shutil.which("npm"):
        try:
            r = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                roots.append(Path(r.stdout.strip()))
        except (OSError, subprocess.TimeoutExpired):
            pass
    if appdata := os.environ.get("APPDATA"):
        roots.append(Path(appdata) / "npm" / "node_modules")
    roots += [ROOT / "node_modules"]
    out = dict(cdn)
    for base in [b for r in roots for b in (r, r / "@mermaid-js" / "mermaid-cli" / "node_modules")]:
        k = base / "katex" / "dist"
        if "katex_local" not in out and (k / "katex.min.js").exists():
            out.update(katex_js=(k / "katex.min.js").as_uri(), katex_css=(k / "katex.min.css").as_uri(),
                       katex_local="1")
        m = base / "mermaid" / "dist" / "mermaid.min.js"
        if "mermaid_local" not in out and m.exists():
            out.update(mermaid_js=m.as_uri(), mermaid_local="1")
    return out


def refresh_visuals(issues: Issues):
    """Re-render Mermaid figures and plot programs whose outputs are missing or older."""
    mmdc = shutil.which("mmdc")
    for mmd in glob_files(["visuals/**/*.mmd"]):
        outs = [mmd.with_suffix(".svg"), mmd.with_suffix(".png")]
        if all(o.exists() and o.stat().st_mtime >= mmd.stat().st_mtime for o in outs):
            continue
        if not mmdc:
            issues.warn(f"mmdc not found; cannot refresh {rel(mmd)}")
            continue
        for o in outs:
            print(f"mmdc  {rel(mmd)} -> {o.name}")
            extra = ["-s", "2"] if o.suffix == ".png" else []
            subprocess.run([mmdc, "-i", str(mmd), "-o", str(o), "-b", "white", *extra], cwd=ROOT, check=False)
    for py in glob_files(["visuals/**/plot-*.py"]):
        m = re.search(r"-(\d{2}-\d{2})-", py.name)
        outs = [p for p in py.parent.glob(f"*-{m[1]}-*") if p.suffix in (".svg", ".png")] if m else []
        if outs and all(o.stat().st_mtime >= py.stat().st_mtime for o in outs):
            continue
        print(f"plot  {rel(py)}")
        subprocess.run([sys.executable, "-X", "utf8", str(py)], cwd=ROOT, check=False)


def body_start_page(headings) -> int | None:
    pages = [h.page for h in headings if h.page and h.kind == "part"]
    pages = pages or [h.page for h in headings if h.page and h.kind == "chapter"]
    return min(pages) if pages else None


def build_profile(cfg: dict, name: str, args, vendor, pw) -> tuple[dict, Issues]:
    import fitz
    issues = Issues()
    prof = resolve_profile(cfg, name)
    b = BookBuilder(cfg, prof, issues, mode=args.mode)
    work = ROOT / "build" / name
    work.mkdir(parents=True, exist_ok=True)
    out_dir = ROOT / cfg["book"].get("output_dir", "dist")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pdf = out_dir / cfg["book"].get("output_name", "rag-book-{profile}.pdf").format(profile=name)
    html_path = work / "book.html"
    page_html, headings = b.compose(None, vendor)
    html_path.write_text(page_html, encoding="utf-8")
    stats = {"profile": name, "edition": prof["edition"], "mode": b.mode, "html": rel(html_path)}
    if args.html_only:
        return stats, issues
    cover_html, cover_pdf, tmp = work / "cover.html", work / "cover.pdf", work / "pass.pdf"
    cover_html.write_text(b.cover_document(vendor), encoding="utf-8")
    browser = pw["browser"]
    print_pdf(browser, cover_html, cover_pdf, b.js_layout()["viewportWidthPt"], issues)
    with fitz.open(cover_pdf) as d:
        offset = d.page_count
    state: dict = {}
    dests = {}
    for attempt in range(1, 5):
        print_pdf(browser, html_path, tmp, b.js_layout()["viewportWidthPt"], issues)
        with fitz.open(tmp) as d:
            dests = named_destinations(d, offset)
            pages = {k: v[0] for k, v in dests.items()}
            n_pages = d.page_count + offset
        for h in headings:
            h.page = pages.get(h.id)
        found = {"pages": pages, "body_start": body_start_page(headings)}
        print(f"  pass {attempt}: {n_pages} pages, {len(pages)} destinations")
        if found == state:
            break
        if attempt == 4:
            issues.warn("page numbers did not stabilise after 4 passes")
            break
        state = found
        page_html, headings = b.compose(state, vendor)
        html_path.write_text(page_html, encoding="utf-8")
    for h in headings:
        h.page = state["pages"].get(h.id)
        if h.page is None and h.toc:
            issues.error(f"could not locate the page of heading: {h.text}")
    body_start = state.get("body_start")
    fin = finish_pdf(tmp, cover_pdf, out_pdf, headings, dests, b, body_start)
    stats.update(validate_pdf(out_pdf, page_html, headings, b, issues))
    stats.update(fin)
    # Layout findings gathered while rendering.
    long_code = [c for c in b.code_blocks if c["long"] and not c["listing"]]
    for c in long_code:
        issues.warn(f"{c['doc']}: code block has {c['long']} line(s) longer than the widest code measure "
                    f"({b.code_columns('wide')} columns; longest {c['max']}); they wrap with a continuation marker")
    listing_long = sum(c["long"] for c in b.code_blocks if c["listing"])
    if listing_long:
        issues.note(f"{listing_long} long lines in full code listings wrap with continuation markers")
    used = b.bib.used()
    cats = {k: sum(1 for w in used if b.bib.category(w) == k) for k in ("reference", "further", "frontier")}
    layouts: dict[str, int] = {}
    for f in b.figures:
        layouts[f["layout"]] = layouts.get(f["layout"], 0) + 1
    stats.update({
        "output": rel(out_pdf), "version": str(cfg["book"].get("version", "")), "commit": b.commit,
        "dirty": b.dirty, "build_date": b.built, "builder": f"bookkit {BUILDER_VERSION}",
        "chapters": [c.number for c in b.chapters], "planned_chapters": len(b.planned),
        "body_start_page": body_start,
        "figures": sum(1 for c in b.captions if c.kind != "Table"),
        "tables": sum(1 for c in b.captions if c.kind == "Table"),
        "figure_layouts": layouts, "citations": b.citations, "bibliography": cats,
        "index_entries": len(b.index_marks),
        "figure_register": [{"number": c.number, "kind": c.kind, "title": c.title, "asset": c.asset,
                             "source_doc": c.src} for c in b.captions],
        "figure_decisions": b.figures,
    })
    if not args.no_snapshots:
        snap_dir = ROOT / "build" / "snapshots" / name
        stats["snapshots"] = snapshots(out_pdf, snap_dir, headings, b, dests)
        stats["snapshot_dir"] = rel(snap_dir)
        if args.diff:
            stats["visual_diff"] = visual_diff(snap_dir)
    for f in (tmp, cover_pdf):
        f.unlink(missing_ok=True)
    return stats, issues


def report(stats: dict, issues: Issues, preflight_issues: Issues) -> str:
    ch = stats.get("chapters", [])
    span = f"{ch[0]}–{ch[-1]}" if len(ch) > 1 else (str(ch[0]) if ch else "none")
    errors = issues.of("error")
    warnings = issues.of("warning")
    lines = [f"RAG Book build complete — {stats['edition']}", "",
             f"Profile:        {stats['profile']} ({stats['mode']})"]
    if "pages" in stats:
        bs = stats.get("body_start_page")
        front = f" (front matter i–{_roman(bs - 1)}, body 1–{stats['pages'] - bs + 1})" if bs else ""
        cats = stats["bibliography"]
        lay = ", ".join(f"{k} {v}" for k, v in sorted(stats["figure_layouts"].items()))
        lines += [
            f"Chapters:       {span} ({len(ch)} of {stats['planned_chapters']} planned)",
            f"Pages:          {stats['pages']}{front}",
            f"Figures:        {stats['figures']}" + (f" (placed: {lay})" if lay else ""),
            f"Tables:         {stats['tables']}",
            f"Citations:      {stats['citations']} in text -> {sum(cats.values())} works "
            f"(references {cats['reference']}, further reading {cats['further']}, frontier {cats['frontier']})",
            f"Bookmarks:      {stats['bookmarks']}",
            f"Internal links: {stats['internal_links']}",
            f"External links: {stats['external_links']}",
            f"Text checks:    {stats['text_samples_checked'] - stats['text_samples_failed']}"
            f"/{stats['text_samples_checked']} sample phrases found in the text layer",
        ]
    lines += [f"Errors:         {len(errors)}", f"Warnings:       {len(warnings)}"]
    for lv, items in (("error", errors), ("warning", warnings)):
        for m in items:
            lines.append(f"  {lv}: {m}")
    for m in issues.of("note"):
        lines.append(f"  note: {m}")
    lines += ["", f"Output:         {stats.get('output', stats['html'])}"]
    if stats.get("snapshot_dir"):
        lines.append(f"Snapshots:      {stats['snapshot_dir']}/")
    for d in stats.get("visual_diff", []):
        lines.append(f"  diff  {d}")
    return "\n".join(lines)


def _roman(n: int) -> str:
    from bookkit.common import roman
    return roman(max(n, 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("-p", "--profile", action="append",
                    help="edition(s) to build: a profile name, a comma list, or 'all' (default: reader)")
    ap.add_argument("--list-profiles", action="store_true")
    ap.add_argument("--check", action="store_true", help="run preflight checks only")
    ap.add_argument("--html-only", action="store_true", help="write HTML and stop (fast preview)")
    ap.add_argument("--refresh-visuals", action="store_true",
                    help="re-render stale Mermaid (.mmd) and plot-*.py figures first")
    ap.add_argument("--release", dest="mode", action="store_const", const="release",
                    help="release mode: no build metadata on the cover or in footers")
    ap.add_argument("--draft", dest="mode", action="store_const", const="draft")
    ap.add_argument("--no-snapshots", action="store_true", help="skip rendering snapshot pages")
    ap.add_argument("--diff", action="store_true", help="compare snapshots with the previous build")
    ap.add_argument("--open", action="store_true", help="open the (last) PDF when finished")
    args = ap.parse_args()
    cfg = load(args.config)
    profiles = cfg.get("profiles", {})
    if args.list_profiles:
        for name, p in profiles.items():
            full = resolve_profile(cfg, name)
            print(f"{name:10} {full['edition']:22} {full['description']}")
        return 0
    wanted = [n for spec in (args.profile or ["reader"]) for n in spec.split(",") if n]
    if "all" in wanted:
        wanted = list(profiles)
    for n in wanted:
        resolve_profile(cfg, n)

    pre = Issues()
    if args.refresh_visuals:
        refresh_visuals(pre)
    pf = preflight(cfg, pre)
    print(f"Preflight: {pf['chapters']} chapters, {pf['captions']} numbered captions, "
          f"{len(pre.of('error'))} error(s), {len(pre.of('warning'))} warning(s)")
    for lv in ("error", "warning"):
        for m in pre.of(lv):
            print(f"  {lv}: {m}")
    if args.check:
        return 1 if pre.of("error") else 0

    vendor = find_vendor()
    if "katex_local" not in vendor:
        print("note: KaTeX not found locally; loading it from the CDN (network required)")
    failed = bool(pre.of("error"))
    last_pdf = None
    ctx: dict = {}
    t0 = dt.datetime.now()
    try:
        if not args.html_only:
            from playwright.sync_api import sync_playwright
            ctx["pw"] = sync_playwright().start()
            ctx["browser"] = launch_browser(ctx["pw"])
        for name in wanted:
            t1 = dt.datetime.now()
            print(f"\n[{name}]")
            stats, issues = build_profile(cfg, name, args, vendor, ctx)
            stats["preflight"] = {"errors": pre.of("error"), "warnings": pre.of("warning")}
            stats["issues"] = {lv: issues.of(lv) for lv in ("error", "warning", "note")}
            stats["seconds"] = round((dt.datetime.now() - t1).total_seconds(), 1)
            print(report(stats, issues, pre))
            if "output" in stats:
                last_pdf = ROOT / stats["output"]
                last_pdf.with_suffix(".build.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False),
                                                               encoding="utf-8")
                print(f"Build record:   {rel(last_pdf.with_suffix('.build.json'))}  ({stats['seconds']}s)")
            failed |= bool(issues.of("error"))
    finally:
        if "browser" in ctx:
            ctx["browser"].close()
            ctx["pw"].stop()
    print(f"\nDone in {(dt.datetime.now() - t0).total_seconds():.0f}s"
          + (" — with errors" if failed else ""))
    if args.open and last_pdf:
        if sys.platform == "win32":
            os.startfile(last_pdf)  # noqa: S606
        else:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(last_pdf)], check=False)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
