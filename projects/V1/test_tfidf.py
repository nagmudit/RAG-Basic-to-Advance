"""Chapter 6 formula, ranking-change and access-boundary checks."""

import math
import unittest
from pathlib import Path

from tfidf import (
    RankedEngine, build_weighted_index, explain, load_corpus, search,
)


TOY = Path(__file__).with_name("toy_ranking_corpus.json")


class TfIdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = load_corpus(TOY)
        cls.before = {
            **cls.full,
            "snapshot": cls.full["snapshot"] + "-before-T4",
            "documents": cls.full["documents"][:3],
        }
        cls.before_index = build_weighted_index(cls.before)
        cls.after_index = build_weighted_index(cls.full)

    def test_df_idf_and_zero_missing_term(self):
        prior = self.before_index.by_scope["support-team"]
        later = self.after_index.by_scope["support-team"]
        self.assertEqual((prior.n_segments, prior.df["amber"], prior.df["blue"]), (3, 2, 2))
        self.assertAlmostEqual(prior.idf("amber"), math.log(3 / 2))
        self.assertEqual((later.n_segments, later.df["amber"], later.df["blue"]), (4, 2, 3))
        self.assertAlmostEqual(later.idf("amber"), math.log(2))
        self.assertAlmostEqual(later.idf("blue"), math.log(4 / 3))
        self.assertEqual(later.idf("missing"), 0.0)
        self.assertEqual(search(self.after_index, "missing")[0], [])

    def test_hand_calculated_raw_scores_reverse_after_one_document(self):
        before, _ = search(self.before_index, "amber blue", mode="raw")
        after, _ = search(self.after_index, "amber blue", mode="raw")
        self.assertEqual([row["document_id"] for row in before], ["T2", "T1", "T3"])
        self.assertEqual([row["document_id"] for row in after], ["T1", "T2", "T3", "T4"])
        self.assertAlmostEqual(before[0]["score"], 3 * math.log(3 / 2))
        self.assertAlmostEqual(after[0]["score"], 2 * math.log(4 / 2))
        self.assertAlmostEqual(after[1]["score"], math.log(4 / 2) + 2 * math.log(4 / 3))

    def test_sublinear_and_cosine_are_distinct_declared_variants(self):
        sublinear, _ = search(self.after_index, "amber blue", mode="sublinear")
        cosine, _ = search(self.after_index, "amber blue", mode="cosine")
        self.assertEqual(sublinear[0]["document_id"], "T2")
        self.assertEqual(cosine[0]["document_id"], "T2")
        self.assertAlmostEqual(sublinear[0]["score"], 1.1802347, places=5)
        self.assertAlmostEqual(cosine[0]["score"], 0.9555108, places=5)
        self.assertTrue(all(0 <= row["score"] <= 1 for row in cosine))
        for mode in ("raw", "sublinear", "cosine"):
            detail = explain(self.after_index, "amber blue", "T2:body:0", mode=mode)
            ranked = search(self.after_index, "amber blue", mode=mode)[0]
            score = next(row["score"] for row in ranked if row["document_id"] == "T2")
            self.assertAlmostEqual(sum(item["contribution"] for item in detail), score)

    def test_common_term_zero_idf_is_not_no_result(self):
        corpus = {
            "snapshot": "all-blue-v1",
            "documents": [
                {"id": f"T{i}", "title": "", "version": "v1", "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "blue"}]}
                for i in (1, 2)
            ],
        }
        index = build_weighted_index(corpus)
        for mode in ("raw", "sublinear", "cosine"):
            with self.subTest(mode=mode):
                rows, work = search(index, "blue", mode=mode)
                self.assertEqual([row["score"] for row in rows], [0.0, 0.0])
                self.assertEqual(work["zero_score_candidates"], 2)

    def test_scope_local_statistics_and_trace_exclude_restricted_source(self):
        corpus = load_corpus()
        index = build_weighted_index(corpus)
        support = index.by_scope["support-team"]
        legal = index.by_scope["legal-team"]
        self.assertEqual((support.n_segments, legal.n_segments), (12, 1))
        self.assertEqual(support.df.get("thirty-minute", 0), 0)
        self.assertEqual(legal.df["thirty-minute"], 1)
        rows, _ = search(index, "thirty-minute", scope="support-team")
        self.assertEqual(rows, [])
        with self.assertRaises(PermissionError):
            explain(index, "thirty-minute", "D10:§1:0", scope="support-team")
        answer, trace, prompt = RankedEngine(corpus).run("q-contract-change")
        self.assertEqual(trace["status"], "answered")
        self.assertIn("D2", answer)
        self.assertNotIn("D10:", repr(trace))
        self.assertNotIn("[D10", prompt)

    def test_rank_depth_can_lose_required_evidence_and_stub_abstains(self):
        engine = RankedEngine(load_corpus())
        _, trace, _ = engine.run("q-contract-change", mode="raw", top_k=2)
        self.assertEqual(trace["status"], "abstained")
        self.assertEqual(trace["reason"], "missing_required_evidence")
        self.assertNotIn("D1:§3:0", trace["context_ids"])
        _, deeper, _ = engine.run("q-contract-change", mode="raw", top_k=8)
        self.assertEqual(deeper["status"], "answered")
        self.assertEqual(set(deeper["evidence_ids"]), {"D1:§3:0", "D2:§2:0"})

    def test_invalid_mode_boost_and_depth(self):
        with self.assertRaises(ValueError):
            build_weighted_index(self.full, title_boost=0)
        with self.assertRaises(ValueError):
            build_weighted_index(self.full, title_boost=float("nan"))
        with self.assertRaises(ValueError):
            search(self.after_index, "amber", mode="unknown")
        with self.assertRaises(ValueError):
            search(self.after_index, "amber", top_k=0)

    def test_small_title_boost_keeps_sublinear_contribution_nonnegative(self):
        corpus = {
            "snapshot": "field-boost-test-v1",
            "documents": [
                {"id": "T1", "title": "amber", "version": "v1", "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "plain"}]},
                {"id": "T2", "title": "other", "version": "v1", "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "plain"}]},
            ],
        }
        index = build_weighted_index(corpus, title_boost=.1)
        rows, _ = search(index, "amber", mode="sublinear")
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["score"], .1 * math.log(2))
        first = build_weighted_index(corpus, title_boost=1.0000001)
        second = build_weighted_index(corpus, title_boost=1.0000002)
        self.assertNotEqual(first.version, second.version)


if __name__ == "__main__":
    unittest.main()
