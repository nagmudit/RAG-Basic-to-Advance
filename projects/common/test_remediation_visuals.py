"""Targeted asset/reference and label-bound checks; render into a temporary folder."""
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RemediationVisualTests(unittest.TestCase):
    def test_target_figure_references_exist_and_match_numbers(self):
        for chapter, number in ((12, "12.02"), (16, "16.01")):
            text = next((ROOT / "chapters").glob(f"chapter-{chapter:02d}-*.md")).read_text(encoding="utf-8")
            self.assertIn(f"**Figure {number}", text)
            links = re.findall(r"\]\(([^)]+)\)", text)
            assets = [link for link in links if f"figure-{chapter:02d}-" in link]
            self.assertTrue(assets)
            for target in assets:
                self.assertTrue((ROOT / "chapters" / target).resolve().exists(), target)

    def test_query_label_within_plot_and_geometric_example_unchanged(self):
        import matplotlib
        matplotlib.use("Agg")
        script = ROOT / "visuals/chapter-16/plot-16-01-cells-and-codes.py"
        source = script.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            source = source.replace('HERE = Path(__file__).resolve().parent', f'HERE = Path({directory!r})')
            namespace = {"__file__": str(script), "__name__": "targeted_figure_test"}
            exec(compile(source, str(script), "exec"), namespace)
            fig, ax = namespace["fig"], namespace["ax"]
            fig.canvas.draw()
            ann = next(t for t in ax.texts if t.get_text().startswith("q ("))
            box = ann.get_bbox_patch().get_window_extent(fig.canvas.get_renderer())
            bounds = ax.get_window_extent()
            self.assertLessEqual(box.x1, bounds.x1)
            self.assertGreaterEqual(box.x0, bounds.x0)
            self.assertLessEqual(box.y1, bounds.y1)
            self.assertGreaterEqual(box.y0, bounds.y0)
            self.assertEqual(namespace["angle"], 38)
            self.assertEqual([i for i,_ in namespace["exact"]], ["01", "02"])
            self.assertEqual([i for i,_ in namespace["one"]], ["01", "00"])
            self.assertTrue((Path(directory)/"figure-16-01-cells-and-codes.svg").exists())
            self.assertTrue((Path(directory)/"figure-16-01-cells-and-codes.png").exists())


if __name__ == "__main__":
    unittest.main()
