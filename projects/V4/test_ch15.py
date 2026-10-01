"""Chapter 15 correctness, approximation and frozen-record safeguards."""

import json
import math
import random
import unittest
from pathlib import Path

from ann_ch15 import KDTree, HyperplaneLSH, exact_cosine, unit, vector
from experiment_ch15 import HERE, rank_recall, source_hash


class Chapter15Tests(unittest.TestCase):
    def test_kd_backtracks_and_matches_exhaustive_low_and_high_dimension(self):
        for dimension in (2, 8, 32):
            rng = random.Random(15+dimension)
            rows = [{"item_id": f"p{i:03d}",
                     "vector": unit([rng.gauss(0, 1) for _ in range(dimension)]),
                     "allowed_scopes": ["public"]} for i in range(73)]
            kd = KDTree(rows, leaf_size=3)
            for _ in range(12):
                query = unit([rng.gauss(0, 1) for _ in range(dimension)])
                oracle, _ = exact_cosine(rows, query, scope="public", k=5)
                result, work = kd.search(query, k=5)
                self.assertEqual([item_id for item_id, _ in oracle],
                                 [item_id for item_id, _ in result])
                self.assertLessEqual(work["scored_vectors"], len(rows))
        tie = [{"item_id": "b", "vector": (1.0, 0.0)},
               {"item_id": "a", "vector": (-1.0, 0.0)}]
        ranked, _ = KDTree(tie, leaf_size=1).search((0.0, 0.0), k=1)
        self.assertEqual(ranked[0][0], "a")

    def test_lsh_deterministic_scope_and_empty_bucket_without_fallback(self):
        rows = [{"item_id": "public", "vector": (1.0, 0.0),
                 "allowed_scopes": ["public"]},
                {"item_id": "private", "vector": (0.0, 1.0),
                 "allowed_scopes": ["private"]}]
        a = HyperplaneLSH(rows, tables=2, bits=3, seed=15, source_version="v1")
        b = HyperplaneLSH(rows, tables=2, bits=3, seed=15, source_version="v1")
        self.assertEqual(a.buckets, b.buckets)
        result, work = a.search((0, 1), scope="public", k=2)
        self.assertNotIn("private", [item_id for item_id, _ in result])
        self.assertEqual(work["eligible"], 1)
        empty, work = a.search((1, 0), scope="absent", k=2)
        self.assertEqual(empty, [])
        self.assertTrue(work["no_bucket_match"])
        self.assertEqual(rank_recall([], ["public"], 1), 0)

    def test_invalid_coordinates_and_parameters(self):
        with self.assertRaises(ValueError):
            unit((0, 0))
        with self.assertRaises(ValueError):
            vector((1, float("nan")))
        with self.assertRaises(ValueError):
            KDTree([{"item_id": "x", "vector": (1, 0)}], leaf_size=0)
        with self.assertRaises(ValueError):
            HyperplaneLSH([{"item_id": "x", "vector": (1, 0),
                            "allowed_scopes": ["public"]}],
                           tables=1, bits=0, seed=1, source_version="v")

    def test_checked_record_preserves_kd_parity_and_ann_loss(self):
        record = json.loads((HERE / "chapter-15-experiment.json").read_text(encoding="utf-8"))
        # Preserve the audited run and its historical hashes.
        from historical_results import verify_historical_result
        self.assertTrue(verify_historical_result(Path(__file__).with_name("chapter-15-experiment.json")))

        self.assertEqual(len(record["synthetic"]), 6)
        self.assertTrue(all(row["quality"]["kd_rank_agreement"] == 20
                            for row in record["synthetic"]))
        v0 = record["v0_diagnostic"]
        self.assertEqual((v0["question_count"], v0["judged_pairs"], v0["eligible_vectors"]),
                         (14, 168, 12))
        self.assertEqual(len(v0["lsh_configurations"]), 9)
        self.assertEqual(v0["summaries"]["kd"]["mean_exact_neighbor_recall_at_2"], 1)
        self.assertLess(v0["summaries"]["lsh_t2_b4"]["mean_exact_neighbor_recall_at_2"], 1)
        for case in v0["cases"]:
            self.assertTrue(case["request_id"].startswith("ch15-"))
            self.assertGreaterEqual(case["query_encode_ms"], 0)
            for mode in case["modes"].values():
                self.assertFalse(any(sid.startswith("D10:") for sid in mode["candidate_ids"] + mode["context_ids"]))
                self.assertTrue(set(mode["context_ids"]) <= set(mode["candidate_ids"]))
                self.assertIsNone(mode["generation_status"])


if __name__ == "__main__":
    unittest.main()
