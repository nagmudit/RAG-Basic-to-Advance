"""Print spacing must preserve content, anchors, headings and figure decisions."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookkit.builder import BookBuilder
from bookkit.common import DEFAULT_CONFIG, ROOT, Issues
from bookkit.config import load, resolve_profile


class DocumentSpacingTests(unittest.TestCase):
    def make_builder(self, compact):
        cfg = copy.deepcopy(load(DEFAULT_CONFIG))
        if not compact:
            cfg['layout']['compact_documents'] = []
        return BookBuilder(cfg, resolve_profile(cfg, 'reader'), Issues())

    def test_opt_in_preserves_complete_document_content_and_destinations(self):
        cfg = load(DEFAULT_CONFIG)
        for name in cfg['layout']['compact_documents']:
            with self.subTest(document=name):
                path = ROOT/name
                self.assertTrue(path.is_file())
                compact, normal = self.make_builder(True), self.make_builder(False)
                a, b = compact.render_doc(path), normal.render_doc(path)
                self.assertIn('class="doc layout-compact"', a.html)
                self.assertEqual(a.html.replace('class="doc layout-compact"', 'class="doc"'), b.html)
                self.assertEqual(a.headings, b.headings)
                self.assertEqual(compact.figures, normal.figures)

    def test_other_documents_do_not_inherit_compact_spacing(self):
        path = ROOT/'chapters/chapter-24-rewrite-expand-and-decompose-queries.md'
        compact, normal = self.make_builder(True), self.make_builder(False)
        a, b = compact.render_doc(path), normal.render_doc(path)
        self.assertNotIn('class="doc layout-compact"', a.html)
        self.assertEqual(a.html, b.html)
        self.assertEqual(a.headings, b.headings)


if __name__ == '__main__':
    unittest.main()
