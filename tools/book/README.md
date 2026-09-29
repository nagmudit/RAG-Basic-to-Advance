# Book build

Builds the book in several editions from the one canonical workspace. No chapter text is copied or maintained twice; editions differ only in which sections `book/book.toml` asks for.

```powershell
python -X utf8 tools/book/build_book.py                      # reader edition -> dist/rag-book-reader.pdf
python -X utf8 tools/book/build_book.py -p complete          # one edition
python -X utf8 tools/book/build_book.py -p reader,solutions  # several
python -X utf8 tools/book/build_book.py -p all               # every edition
python -X utf8 tools/book/build_book.py --check              # preflight only (seconds, no PDF)
python -X utf8 tools/book/build_book.py --diff               # compare page snapshots with the last build
python -X utf8 tools/book/build_book.py --release            # release cover/footers, provenance on the colophon
python -X utf8 tools/book/build_book.py --refresh-visuals    # re-render stale .mmd / plot-*.py figures first
python -X utf8 tools/book/build_book.py --list-profiles
python -X utf8 -m unittest discover -s tools/book -p "test_*.py"   # builder tests
```

The exit status is 1 whenever an error-level finding exists. The PDF is still written so you can inspect it.

## Editions

| Profile | Contents | Output |
|---|---|---|
| `reader` | Cover, colophon, Contents (Parts → chapters → labs), lists of figures/tables, preface, learner roadmap, Parts, chapters with their labs, running-project guide, glossary, bibliography, source notes | `dist/rag-book-reader.pdf` |
| `complete` | Everything: reader content plus solutions, all project records, reference architecture, case studies, reading path and frontier register, figure gallery with sources, full code/data listings, contracts, full syllabus, authoring reviews | `dist/rag-book-complete.pdf` |
| `author` | `complete` plus a build-information appendix (figure layout decisions, render-time findings) | `dist/rag-book-author.pdf` |
| `workbook` | For each chapter, its practice prompts, the lab and a ruled answer page; project guide; glossary | `dist/rag-book-workbook.pdf` |
| `solutions` | Worked solutions, expected observations and rubrics, grouped by Part | `dist/rag-book-solutions.pdf` |

Profiles can inherit from one another (`extends`). The independent knobs are:
- `toc_depth` / `toc_labs`: the printed Contents;
- `bookmark_depth`: the PDF outline, which stays detailed;
- `labs`: `inline` or `none`;
- `solutions`: `appendix`, `companion` or `none`;
- `figure_metadata`: print or hide the *Alt text / Editable source* notes;
- `local_toc`: the "In this chapter" box;
- `page_numbers`: `roman-front` or `arabic`;
- `xref_pages`: page numbers on cross-references;
- `answer_space` and `practice_sections`.

Draft or release mode is set by `book.mode` or `--release`. Draft editions show *Working draft · version · commit* on the cover and in a small footer stamp. Release editions keep that provenance on the colophon only.

Every PDF records its build date, version, git commit, dirty flag, profile and builder version: on the colophon, in the PDF metadata and XMP (`rb:` namespace), and in the `dist/rag-book-<profile>.build.json` record. That record also holds the full figure register, with numbers, titles, assets and layout decisions.

## What the build does

1. **Preflight (whole workspace).** Checks relative links and images in every tracked Markdown file. For figures and tables it checks: duplicate numbers; numbering that doesn't follow document order (the Chapter 4 regression); numbers that belong to another chapter; caption/file number mismatches; and references to figures or tables that don't exist. It also flags stale or missing renders of `.mmd` and `plot-*.py` sources, and visuals with no caption.
2. **Markdown → HTML.** Uses `markdown-it-py` and Pygments; KaTeX handles `\[…\]` / `\(…\)`. Inline Mermaid is rendered once with `mmdc` and cached in `build/.cache/mermaid`.
   - Links between printed documents become internal links. Links to anything not printed in the edition open the repository.
   - Plain-text *Chapter N*, *Figure N.NN*, *Table N.N* and *Appendix X* become links. References across documents get the page number, e.g. "Figure 7.01 (p. 88)".
3. **Figures.** Each SVG is measured, and the layout (normal → wide → full-page or landscape) is chosen so that labels render at no less than `layout.min_label_pt` (6.5pt). A figure is never shrunk just to stay beside its prose. You can force a layout with an HTML comment before the caption or image: `<!-- layout: landscape -->`, and the same works before a table or code block. The caption and figure are kept together.
   - In the reader edition the *Alt text* paragraph becomes the image's alt text in the tagged PDF, and the source/metadata notes are hidden. They stay in the Markdown and print in `complete` and `author`.
4. **Citations.** A link to a known source gets an author–year citation, e.g. "(Lewis et al., 2020)", linking to the bibliography. The bibliography is parsed from the registers (`REFERENCES.md`, `PAPER_READING_PATH.md`, `FRONTIER_RESEARCH.md`) and deduplicated by DOI, then arXiv ID, then canonical URL. `book/bibliography.toml` only groups URLs into one work and supplies fuller metadata.
   - The bibliography separates **References** (cited in chapter text or in the reference register), **Further reading** (only in "Further reading" sections or the reading path) and **Frontier sources**.
   - `REFERENCES.md` still prints in full as *Source notes and provenance register*: what each source supports, its scope and caution notes, and the verification date.
5. **Print.** Headless Chromium prints a tagged PDF, repeating until every page number in the Contents, lists, local contents and cross-references is stable. Wide tables that would overflow move to a landscape page. Code that fits within the wide measure extends into the margin; longer lines wrap with a ↪ marker, drawn as a background so copied code is unchanged.
6. **Post-process (PyMuPDF).** Adds the full-bleed cover, roman front-matter and arabic body page labels, and verso/recto running heads (Part / chapter). Outer folios and the draft stamp are marked as PDF artifacts so screen readers skip them. It also adds bookmarks at `bookmark_depth` and metadata.
7. **Validate.** Checks fonts are embedded, TOC entries are clickable, bookmarks exist, every internal link resolves, and no `file:` links leak local paths. It flags nearly empty pages, overflowing tables, very tall table rows and code too wide for any measure. A text-extraction smoke test checks for ligatures, lost glyphs and punctuation, and looks up sample chapter sentences and code lines in the PDF text layer.
8. **Snapshots.** Renders the cover, contents, part opener, chapter opener, diagram, plot, table, code, lab, landscape and references pages to `build/snapshots/<profile>/`, keeping the previous set in `previous/`. `--diff` reports the percentage of changed pixels and writes red-highlighted diffs to `diff/`.

## Conventions for authors

- **Captions:** `**Figure N.NN — Title.** Caption…` directly before the image or Mermaid block, and `**Table N.N — Title.**` directly before the table. Numbers follow the order they appear in the chapter. File names use the same number: `figure-NN-SS-slug.*`.
- **Figure metadata:** put it in a paragraph starting `*Alt text:*` right after the figure.
- **Index:** mark index terms with `@index{term}` or `@index{term|subterm}`. The markers are removed from the text, and an Index section is built once any exist.
- **Reader front matter** lives in `book/front/`. `{{written_span}}`, `{{planned_total}}`, `{{planned_parts}}`, `{{solutions_note}}`, `{{edition}}` and `{{version}}` are filled in at build time.

## Requirements

`markdown-it-py`, `Pygments`, `PyMuPDF`, `playwright` with Chromium (`python -m playwright install chromium`; an installed Edge or Chrome also works), and `mmdc` (`@mermaid-js/mermaid-cli`) for inline Mermaid. KaTeX is taken from a local npm install when available, otherwise from jsDelivr. `numpy` and `Pillow` are needed for `--diff`; `matplotlib` for `--refresh-visuals` plots.

Code: `build_book.py` (CLI) and `bookkit/`: `config.py` (profiles), `builder.py` (Markdown → HTML), `figures.py` (layout decisions), `biblio.py` (citations), `pdf.py` (print and post-process), `checks.py` (preflight, validation, snapshots).
