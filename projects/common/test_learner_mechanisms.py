import unittest
from pathlib import Path
from learner_checks import check, load

ROOT = Path(__file__).resolve().parents[2]


class LearnerMechanismTests(unittest.TestCase):
    def test_separate_answers_on_unseen_fixtures(self):
        for ch in (5, 6, 7, 8, 14, 15, 16):
            with self.subTest(chapter=ch):
                path = ROOT / f"solutions/code/chapter_{ch:02d}_mechanisms.py"
                self.assertTrue(check(ch, load(path)))
                self.assertNotIn("from projects", path.read_text())
                self.assertNotIn("import implement", path.read_text())

    def test_scaffolds_are_unsolved(self):
        for ch in (5, 6, 7, 8, 14, 15, 16):
            with self.subTest(chapter=ch), self.assertRaises(NotImplementedError):
                check(ch, load(ROOT / f"labs/chapter-{ch:02d}/implement.py"))


if __name__ == "__main__":
    unittest.main()
