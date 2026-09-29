"""Chapter 7 behavior and numerical regression tests."""

import json
import math
import unittest
from pathlib import Path

from bm25 import BM25Engine, build_bm25_index, explain, saturation, search
from lexical_index import build_index, load_corpus
from tfidf import build_weighted_index, search as tfidf_search


HERE = Path(__file__).resolve().parent


class BM25Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toy = json.loads((HERE / "toy_length_corpus.json").read_text(encoding="utf-8"))
        cls.base = build_index(cls.toy)
        cls.index = build_bm25_index(cls.base)

    def test_hand_calculation_and_length_effect(self):
        stats = self.index.by_scope["support-team"]
        self.assertEqual(stats.n_segments, 4)
        self.assertEqual(stats.df["amber"], 2)
        self.assertEqual(stats.avgdl, 4.0)
        candidates, _ = search(self.index, "amber")
        self.assertEqual([x["segment_id"] for x in candidates],
                         ["S1:body:0", "S2:body:0"])
        self.assertAlmostEqual(candidates[0]["score"], math.log(2) * 4.4 / 2.75)
        self.assertAlmostEqual(candidates[1]["score"], math.log(2) * 4.4 / 4.55)
        tfidf, _ = tfidf_search(build_weighted_index(self.base), "amber")
        self.assertAlmostEqual(tfidf[0]["score"], tfidf[1]["score"])

    def test_b_zero_removes_length_effect(self):
        index = build_bm25_index(self.base, b=0)
        candidates, _ = search(index, "amber")
        self.assertAlmostEqual(candidates[0]["score"], candidates[1]["score"])
        self.assertEqual(candidates[0]["segment_id"], "S1:body:0")

    def test_saturation_and_b_control(self):
        self.assertGreater(saturation(2, 4, 4), saturation(1, 4, 4))
        self.assertLess(saturation(2, 4, 4) - saturation(1, 4, 4),
                        saturation(1, 4, 4))
        self.assertGreater(saturation(2, 2, 4), saturation(2, 10, 4))
        self.assertEqual(saturation(0, 2, 4), 0)

    def test_explainer_sums_and_scope_gate(self):
        rows = explain(self.index, "amber filler", "S2:body:0")
        candidates, _ = search(self.index, "amber filler")
        score = next(x["score"] for x in candidates if x["segment_id"] == "S2:body:0")
        self.assertAlmostEqual(sum(row["contribution"] for row in rows), score)
        self.assertEqual(rows[0]["length"], 10)
        with self.assertRaises(PermissionError):
            explain(self.index, "amber", "S5:body:0")
        self.assertNotIn("S5:body:0", [x["segment_id"] for x in candidates])

    def test_no_result_empty_scope_and_common_term(self):
        self.assertEqual(search(self.index, "unseen")[0], [])
        self.assertEqual(search(self.index, "amber", scope="missing")[0], [])
        two = {
            "snapshot": "all-common", "documents": [
                {"id": f"S{i}", "title": "", "version": "v1",
                 "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "blue"}]}
                for i in (1, 2)
            ],
        }
        index = build_bm25_index(two)
        rows, work = search(index, "blue")
        self.assertEqual(len(rows), 2)
        self.assertGreater(rows[0]["score"], 0)
        self.assertEqual(work["scored_segments"], 2)

    def test_distinct_query_terms_and_small_title_boost(self):
        once, _ = search(self.index, "amber filler")
        twice, _ = search(self.index, "amber amber filler")
        self.assertEqual([(x["segment_id"], x["score"]) for x in once],
                         [(x["segment_id"], x["score"]) for x in twice])
        title_only = {
            "snapshot": "title-boost-probe", "documents": [
                {"id": "S1", "title": "amber", "version": "v1",
                 "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "neutral"}]},
                {"id": "S2", "title": "blue", "version": "v1",
                 "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "neutral"}]},
            ],
        }
        index = build_bm25_index(title_only, title_boost=.1)
        result, _ = search(index, "amber")
        self.assertEqual(result[0]["segment_id"], "S1:body:0")
        self.assertGreater(result[0]["score"], 0)
        self.assertEqual(index.by_scope["support-team"].lengths[0], 2)

    def test_invalid_config_and_top_k(self):
        for k1, b, boost in ((0, .75, 1), (float("nan"), .75, 1),
                             (1.2, -0.1, 1), (1.2, 1.1, 1), (1.2, .75, 0)):
            with self.assertRaises(ValueError):
                build_bm25_index(self.base, k1=k1, b=b, title_boost=boost)
        with self.assertRaises(ValueError):
            search(self.index, "amber", top_k=0)

    def test_frozen_v0_path_and_trace(self):
        engine = BM25Engine(load_corpus())
        _, trace, prompt = engine.run("q-contract-change", top_k=2)
        self.assertEqual(trace["query_id"], "q-contract-change")
        self.assertEqual(len(trace["candidate_scores"]), 2)
        self.assertIn("scoring_version", trace)
        self.assertNotIn("question", trace)
        self.assertNotIn("D10", prompt)


if __name__ == "__main__":
    unittest.main()
