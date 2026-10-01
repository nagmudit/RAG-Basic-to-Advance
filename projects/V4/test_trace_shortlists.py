import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from experiment_trace import TraceCollector, versions
from ann_ch15 import HyperplaneLSH
from ivf_pq_ch16 import IVFPQ


class IntermediateTraceTests(unittest.TestCase):
    def rows(self):
        return [{"item_id": f"p{i}", "vector": v, "allowed_scopes": ["public"]}
                for i, v in enumerate(((1,.1,0,0), (1,-.1,0,0), (0,0,1,.1), (0,0,1,-.1), (.6,.8,0,0), (0,0,.6,.8)))]

    def test_ivf_actual_top_r_then_refinement_then_context(self):
        rows = self.rows(); index = IVFPQ(rows, nlist=2, subspaces=2, bits=1, seed=16)
        trace = TraceCollector("toy", versions("c", "q", "g", "i", None), [r["item_id"] for r in rows])
        returned, rec = trace.execute("q", "refine", 0,
            lambda: index.search(rows[0]["vector"], scope="public", k=2, nprobe=2, mode="adc", rerank_depth=4),
            context_selector=lambda r: [r[0][0][0]])
        stages = returned[1]["candidate_stages"]
        self.assertEqual(rec["intermediate_candidate_ids"]["approximate_top_r"], [i for i,_ in stages["approximate_top_r"]])
        self.assertEqual(len(rec["intermediate_candidate_ids"]["approximate_top_r"]), 4)
        self.assertEqual(set(rec["intermediate_candidate_ids"]["approximate_top_r"]),
                         set(rec["intermediate_candidate_ids"]["exact_refinement_candidates"]))
        self.assertEqual(rec["final_candidate_ids"], [i for i,_ in returned[0]])
        self.assertEqual(len(rec["final_candidate_ids"]), 2)
        self.assertEqual(len(rec["context_ids"]), 1)
        self.assertEqual(rec["ivf_probed_lists"], returned[1]["probed_lists"])

    def test_invalid_ann_query_emits_status(self):
        index = IVFPQ(self.rows(), nlist=2, subspaces=2, bits=1)
        trace = TraceCollector("toy", versions("c", "q", "g", "i", None), index.rows)
        with self.assertRaises(ValueError):
            trace.execute("invalid", "ivf", 0, lambda: index.search([0,0], scope="public", k=2, nprobe=1))
        self.assertEqual(trace.records[0]["status"], "invalid")
        self.assertEqual(trace.records[0]["raw_candidate_ids"], [])

    def test_lsh_retains_eligible_union(self):
        rows = self.rows() + [{"item_id": "D10-private", "vector": (1,.1,0,0), "allowed_scopes": ["legal"]}]
        index = HyperplaneLSH(rows, tables=2, bits=1, seed=15, source_version="v")
        trace = TraceCollector("toy", versions("c", "q", "g", "i", None), [r["item_id"] for r in self.rows()])
        returned, rec = trace.execute("q", "lsh", 0, lambda: index.search(rows[0]["vector"], scope="public", k=1))
        self.assertEqual(rec["intermediate_candidate_ids"]["eligible_bucket_union"],
                         [i for i,_ in returned[1]["candidate_stages"]["eligible_bucket_union"]])
        self.assertNotIn("D10", str(rec))


if __name__ == "__main__":
    unittest.main()
