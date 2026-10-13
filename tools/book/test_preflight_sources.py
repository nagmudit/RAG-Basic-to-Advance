"""Preflight checks new manuscripts while preserving declared binary fixtures."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bookkit.checks import preflight
from bookkit.common import ROOT,Issues,DEFAULT_CONFIG
from bookkit.config import load


class SourcePreflightTests(unittest.TestCase):
    def test_new_untracked_markdown_links_are_checked(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='preflight-test-') as name:
            path=Path(name)/'new.md'
            path.write_bytes(b'# New draft\n\n[bad](missing-target.txt)\n')
            issues=Issues();preflight(load(DEFAULT_CONFIG),issues)
            self.assertTrue(any('new.md: broken relative link' in e for e in issues.of('error')))

    def test_invalid_unmarked_manuscript_is_an_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='preflight-test-') as name:
            (Path(name)/'new.md').write_bytes(b'# Bad\n\xff')
            issues=Issues();preflight(load(DEFAULT_CONFIG),issues)
            self.assertTrue(any('new.md: Markdown is not UTF-8' in e for e in issues.of('error')))

    def test_explicit_binary_fixture_is_not_decoded_as_manuscript(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='preflight-test-') as name:
            (Path(name)/'.gitattributes').write_bytes(b'raw.md binary\n')
            (Path(name)/'raw.md').write_bytes(b'# Raw fixture\n\xff')
            issues=Issues();preflight(load(DEFAULT_CONFIG),issues)
            self.assertFalse(any('raw.md' in e for e in issues.of('error')))


if __name__=='__main__':unittest.main()
