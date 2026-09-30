"""Behavioral checks for exactness, geometry and eligibility."""

import math
import unittest

from exact_vectors import ExactIndex, dot, measure, norm
from experiment_ch10 import build_binary_index, query_vector, run, vector_search
from lexical_index import build_index, load_corpus


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.index = ExactIndex([
            {"item_id": "A", "vector": [1, 0], "allowed_scopes": ["public"]},
            {"item_id": "B", "vector": [2, 0], "allowed_scopes": ["public"]},
            {"item_id": "C", "vector": [.8, .6], "allowed_scopes": ["public"]},
            {"item_id": "P", "vector": [100, 0], "allowed_scopes": ["private"]},
        ], version="toy-v1")

    def test_hand_geometry(self):
        self.assertEqual(dot((1, 0), (2, 0)), 2)
        self.assertEqual(norm((.8, .6)), 1)
        self.assertAlmostEqual(measure((1, 0), (.8, .6), "l2"), math.sqrt(.4))
        self.assertAlmostEqual(measure((1, 0), (.8, .6), "l1"), .8)
        self.assertEqual([r["item_id"] for r in self.index.search([1, 0], scope="public", metric="dot", top_k=3)[0]], ["B", "A", "C"])
        self.assertEqual([r["item_id"] for r in self.index.search([1, 0], scope="public", metric="l2", top_k=3)[0]], ["A", "C", "B"])
        self.assertEqual([r["item_id"] for r in self.index.search([1, 0], scope="public", metric="cosine", top_k=3)[0]], ["A", "B", "C"])

    def test_heap_matches_sort_and_scores_every_eligible_vector(self):
        for metric in ("dot", "cosine", "l2", "l1"):
            for k in (1, 2, 3, 10):
                sorted_rows, work = self.index.search([1, 0], scope="public", metric=metric, top_k=k, plan="sort")
                heap_rows, heap_work = self.index.search([1, 0], scope="public", metric=metric, top_k=k, plan="heap")
                self.assertEqual(sorted_rows, heap_rows)
                self.assertEqual((work["eligible_vectors"], work["scored_vectors"], work["coordinate_comparisons"]), (3, 3, 6))
                self.assertEqual(heap_work["scored_vectors"], 3)
                self.assertNotIn("P", [row["item_id"] for row in heap_rows])

    def test_zero_invalid_mismatch_and_empty_scope(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            self.index.search([0, 0], scope="public", metric="cosine")
        with self.assertRaisesRegex(ValueError, "dimension"):
            self.index.search([1, 0, 0], scope="public")
        with self.assertRaises(ValueError):
            self.index.search([float("nan"), 0], scope="public")
        with self.assertRaises(ValueError):
            self.index.search([1, 0], scope="public", top_k=0)
        self.assertEqual(self.index.search([1, 0], scope="nobody")[0], [])
        zero_index = ExactIndex([{"item_id": "Z", "vector": [0, 0],
                                  "allowed_scopes": ["public"]}], version="zero-v1")
        self.assertEqual(zero_index.search([1, 0], scope="public", metric="dot")[0][0]["value"], 0)
        with self.assertRaisesRegex(ValueError, "zero"):
            zero_index.search([1, 0], scope="public", metric="cosine")

    def test_duplicate_and_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            ExactIndex([{"item_id": "A", "vector": [1], "allowed_scopes": ["s"]},
                        {"item_id": "A", "vector": [2], "allowed_scopes": ["s"]}], version="x")
        with self.assertRaises(ValueError):
            ExactIndex([{"item_id": "A", "vector": [math.inf],
                         "allowed_scopes": ["s"]}], version="x")

    def test_frozen_v2_scope_and_zero_query_policy(self):
        base = build_index(load_corpus())
        index, vocab = build_binary_index(base)
        self.assertEqual(index.dimension, len(vocab))
        self.assertEqual(query_vector(base, vocab, "never-seen-made-up-token"), tuple(0.0 for _ in vocab))
        rows, work = vector_search(index, base, vocab, "never-seen-made-up-token", 2)
        self.assertEqual(rows, [])
        self.assertEqual(work["reason"], "zero_in_vocabulary_query")
        rows, work = vector_search(index, base, vocab, "Helios Pro", 8)
        self.assertEqual(work["scored_vectors"], 12)
        self.assertTrue(all(not r["segment_id"].startswith("D10:") for r in rows))

    def test_judged_experiment_preserves_stage_boundaries(self):
        record = run(trials=1)
        self.assertEqual((record["query_count"], record["eligible_segments"],
                          record["judged_pairs"], record["vocabulary_dimension"]),
                         (14, 12, 168, 119))
        case = next(row for row in record["cases"]
                    if row["query_id"] == "q-termination" and row["top_k"] == 2)
        self.assertIn("D1:§8:0", case["modes"]["bm25"]["context_ids"])
        self.assertNotIn("D1:§8:0", case["modes"]["binary_cosine"]["candidate_ids"])
        self.assertEqual(case["modes"]["bm25"]["stub_status"], "answered")
        self.assertEqual(case["modes"]["binary_cosine"]["stub_status"], "abstained")
        for row in record["cases"]:
            for mode in ("bm25", "binary_cosine"):
                self.assertTrue(all(not id_.startswith("D10:")
                                    for id_ in row["modes"][mode]["candidate_ids"]
                                    + row["modes"][mode]["context_ids"]))
        self.assertLess(record["summaries"]["2"]["binary_cosine"]
                        ["macro_positive_query_mean"]["ndcg_at_k"],
                        record["summaries"]["2"]["bm25"]
                        ["macro_positive_query_mean"]["ndcg_at_k"])


if __name__ == "__main__":
    unittest.main()
