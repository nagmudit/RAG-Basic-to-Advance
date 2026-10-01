"""Chapter 14 arithmetic, sparse execution, eligibility and record invariants."""

import json
import math
import unittest
from pathlib import Path

from experiment_ch14 import DOCUMENTS, HERE, Q, build_record, source_sha256, sparse_fixture
from sparse_late_ch14 import SparseIndex, SparseRow, maxsim, pooled_cosine, sparse_pool


class Chapter14Tests(unittest.TestCase):
    def test_sparse_pool_and_expansion(self):
        weights = sparse_pool([{"a": 2, "b": -10}, {"a": 1, "c": 3}])
        self.assertAlmostEqual(weights["a"], math.log(3))
        self.assertAlmostEqual(weights["c"], math.log(4))
        self.assertNotIn("b", weights)
        q, lexical_q, index = sparse_fixture()
        self.assertEqual(index.search(lexical_q, "support-team", 3)[0][0][0], "reply_template")
        ranked, work = index.search(q, "support-team", 3)
        self.assertEqual(ranked[0][0], "incident")
        self.assertEqual(work["eligible_rows"], 3)
        self.assertNotIn("private", [item_id for item_id, _ in ranked])
        with self.assertRaises(ValueError):
            sparse_pool([{"x": float("nan")}])
        with self.assertRaises(ValueError):
            SparseIndex([SparseRow("x", "public", {"x": -1})])

    def test_maxsim_grid_and_pooling_reversal(self):
        score, grid, winners = maxsim(Q, DOCUMENTS["A_both_with_noise"])
        self.assertAlmostEqual(score, 2)
        self.assertEqual(winners, [0, 1])
        self.assertEqual(grid[0][:2], [1, 0])
        self.assertEqual(grid[1][:2], [0, 1])
        self.assertGreater(score, maxsim(Q, DOCUMENTS["B_generic"])[0])
        self.assertLess(pooled_cosine(Q, DOCUMENTS["A_both_with_noise"]),
                        pooled_cosine(Q, DOCUMENTS["B_generic"]))
        with self.assertRaises(ValueError):
            maxsim(Q, [])
        with self.assertRaises(ValueError):
            maxsim(Q, [(2.0, 0.0)])

    def test_record_keeps_mechanism_and_model_claims_separate(self):
        record = json.loads((HERE / "chapter-14-experiment.json").read_text(encoding="utf-8"))
        self.assertEqual(record["source"]["code_sha256"],
                         build_record()["source"]["code_sha256"])
        # Preserve the audited run and its historical hashes.
        from historical_results import verify_historical_result
        self.assertTrue(verify_historical_result(Path(__file__).with_name("chapter-14-experiment.json")))
        self.assertIsNone(record["source"]["model_version"])
        self.assertEqual(record["sparse"]["surface_only"]["recall_at_1"], 0)
        self.assertEqual(record["sparse"]["expanded"]["recall_at_1"], 1)
        self.assertEqual(record["token_rankings"]["exact_maxsim"][0], "A_both_with_noise")
        self.assertEqual(record["token_rankings"]["pooled_cosine"][0], "B_generic")
        self.assertTrue(all(item["work"]["eligible_rows"] == 3
                            for item in record["sparse"].values()))
        self.assertEqual(len(record["request_trace_examples"]), 4)
        self.assertTrue(all(trace["selected_context_ids"] is None and
                            trace["answer_status"] == "not_run" and trace["status"] == "scored" and
                            trace["elapsed_ms"] >= 0
                            for trace in record["request_trace_examples"]))


if __name__ == "__main__":
    unittest.main()
