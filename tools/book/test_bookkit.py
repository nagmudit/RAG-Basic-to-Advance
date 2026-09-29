"""Tests for the book build toolkit (no browser needed).

    python -X utf8 -m unittest discover -s tools/book -p "test_*.py" -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bookkit.biblio import Bibliography, canon_url, cite_label  # noqa: E402
from bookkit.builder import BookBuilder  # noqa: E402
from bookkit.checks import preflight, scan_captions  # noqa: E402
from bookkit.common import DEFAULT_CONFIG, Caption, Issues  # noqa: E402
from bookkit.config import load, parse_paper, resolve_profile  # noqa: E402
from bookkit.figures import Measure, choose_layout, layout_boxes  # noqa: E402

CFG = load(DEFAULT_CONFIG)


def builder(profile="reader"):
    return BookBuilder(CFG, resolve_profile(CFG, profile), Issues())


class FigureOrderTests(unittest.TestCase):
    def test_manuscript_passes_preflight(self):
        issues = Issues()
        preflight(CFG, issues)
        self.assertEqual(issues.of("error"), [])

    def test_out_of_order_figures_are_errors(self):
        # The Chapter 4 regression: Figure 4.02 printed before Figure 4.01.
        text = ("**Figure 4.02 — Loop.** a\n\n![a](x/figure-04-02-loop.svg)\n\n"
                "**Figure 4.01 — Path.** b\n\n![b](x/figure-04-01-path.svg)\n")
        issues = Issues()
        scan_captions(text, 4, "ch4", issues)
        self.assertTrue(any("appears after" in e for e in issues.of("error")))

    def test_duplicate_and_foreign_numbers_are_errors(self):
        text = "**Table 3.1 — A.**\n\n**Table 3.1 — B.**\n\n**Figure 5.01 — C.**\n"
        issues = Issues()
        scan_captions(text, 3, "ch3", issues)
        errors = " ".join(issues.of("error"))
        self.assertIn("duplicate Table number 3.1", errors)
        self.assertIn("numbered for Chapter 5", errors)

    def test_caption_file_number_mismatch(self):
        text = "**Figure 4.01 — Loop.** a\n\n![a](x/figure-04-02-loop.svg)\n"
        issues = Issues()
        scan_captions(text, 4, "ch4", issues)
        self.assertTrue(any("file number" in e for e in issues.of("error")))

    def test_list_of_figures_is_numeric_not_occurrence_or_filesystem(self):
        b = builder()
        b.captions = [Caption("Figure", "4.02", "Second", "a2", 4, "d", "s", 0),
                      Caption("Figure", "4.01", "First", "a1", 4, "d", "s", 1),
                      Caption("Figure", "10.01", "Tenth", "a10", 10, "d", "s", 2)]
        html = b.list_block(("Figure",), "List of figures", "lof", None).html
        self.assertLess(html.index("First"), html.index("Second"))
        self.assertLess(html.index("Second"), html.index("Tenth"))

    def test_rendered_list_of_figures_in_order(self):
        b = builder()
        b.build_body(None)
        keys = [c.key for c in b.captions if c.kind != "Table"]
        self.assertEqual(keys, sorted(keys), "figures must occur in numeric order in the manuscript")


class ProfileTests(unittest.TestCase):
    def test_inheritance_and_sections(self):
        reader, complete = resolve_profile(CFG, "reader"), resolve_profile(CFG, "complete")
        self.assertNotIn("reviews", reader["appendices"])
        self.assertNotIn("code", reader["appendices"])
        for sid in ("reviews", "code", "contracts", "syllabus", "visuals"):
            self.assertIn(sid, complete["appendices"])
        self.assertEqual(complete["labs"], "inline")          # inherited from reader
        self.assertEqual(resolve_profile(CFG, "author")["toc_depth"], 3)

    def test_reader_contents_is_concise(self):
        b = builder("reader")
        heads = [h for blk in b.build_body(None) for h in blk.headings if h.toc]
        self.assertTrue(all(h.kind != "section" or h.level <= 2 for h in heads))
        self.assertTrue(any(h.kind == "lab" for h in heads))

    def test_reader_hides_figure_metadata_but_keeps_alt_text(self):
        html = "".join(blk.html for blk in builder("reader").build_body(None))
        self.assertNotIn("Editable source:", html)
        self.assertIn('alt="Repetition curves rise and flatten', html)
        complete = "".join(blk.html for blk in builder("complete").build_body(None))
        self.assertIn("Editable source:", complete)


class BibliographyTests(unittest.TestCase):
    def test_canonical_urls(self):
        self.assertEqual(canon_url("http://arxiv.org/pdf/2005.11401v4"), "arxiv:2005.11401")
        self.assertEqual(canon_url("https://doi.org/10.1145/ABC"), "doi:10.1145/abc")
        self.assertEqual(canon_url("https://Example.org/a/#frag"), "https://example.org/a")

    def test_textbook_sections_collapse_to_one_work(self):
        bib = Bibliography(CFG["sources"], Issues())
        a = bib.lookup("https://nlp.stanford.edu/IR-book/html/htmledition/tokenization-1.html")
        b = bib.lookup("https://nlp.stanford.edu/IR-book/pdf/12lmodel.pdf")
        self.assertIs(a, b)
        self.assertEqual(a.in_text(), "Manning, Raghavan & Schütze, 2008")

    def test_preprint_and_published_version_are_one_work(self):
        bib = Bibliography(CFG["sources"], Issues())
        self.assertIs(bib.lookup("https://arxiv.org/abs/2307.03172"),
                      bib.lookup("https://aclanthology.org/2024.tacl-1.9/"))

    def test_register_metadata(self):
        bib = Bibliography(CFG["sources"], Issues())
        self.assertEqual(bib.lookup("https://arxiv.org/abs/2004.04906").in_text(), "Karpukhin et al., 2020")
        self.assertEqual(cite_label("Manning, Raghavan and Schütze"), "Manning, Raghavan & Schütze")


class LayoutTests(unittest.TestCase):
    boxes = layout_boxes(parse_paper("A4"))

    def test_small_diagram_stays_in_text(self):
        layout, _, label = choose_layout(Measure(300, 200, 10, False), self.boxes, 6.5, 11)
        self.assertEqual(layout, "normal")
        self.assertGreaterEqual(label, 6.5)

    def test_wide_diagram_goes_landscape_not_tiny(self):
        layout, _, label = choose_layout(Measure(1100, 480, 12, True), self.boxes, 6.5, 11)
        self.assertEqual(layout, "landscape")
        self.assertGreaterEqual(label, 6.5)

    def test_tall_diagram_gets_full_page(self):
        layout, _, _ = choose_layout(Measure(700, 1200, 12, True), self.boxes, 6.5, 11)
        self.assertEqual(layout, "fullpage")


class CrossReferenceTests(unittest.TestCase):
    def test_links_plain_references_only(self):
        b = builder()
        b.build_body(None)
        html = ('<section class="doc" id="d-x"><p>See Figure 7.01 and Chapter 5.</p>'
                '<p><code>Figure 7.01</code> <a href="#z">Chapter 5</a></p></section>')
        out = b.crossref(html, None)
        self.assertIn('<a class="xref" href="#cap-figure-7-01">Figure 7.01</a>', out)
        self.assertIn('<a class="xref" href="#unit-ch05">Chapter 5</a>', out)
        self.assertIn("<code>Figure 7.01</code>", out)
        self.assertEqual(out.count('class="xref"'), 2)

    def test_page_numbers_across_documents(self):
        b = builder()
        b.build_body(None)
        pages = {"pages": {"cap-figure-7-01": 120}, "body_start": 11}
        out = b.crossref('<section class="doc" id="d-lab"><p>Open Figure 7.01.</p></section>', pages)
        self.assertIn("(p.&#8239;110)", out)


class WorkbookTests(unittest.TestCase):
    def test_practice_sections_extracted(self):
        text = BookBuilder._extract_sections(
            Path(__file__).resolve().parents[2] / "chapters/chapter-07-bm25-and-other-lexical-ranking-models.md",
            ["Practice"])
        self.assertTrue(text.startswith("### Practice and active recall"))
        self.assertNotIn("### Further reading", text)


if __name__ == "__main__":
    unittest.main()
