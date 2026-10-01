import unittest
from unittest.mock import patch
from types import SimpleNamespace
from experiment_ch13 import timed_queries, build_index, load_corpus, build_bm25_index
from experiment_trace import TraceCollector, versions, eligible


class PipelineErrorTraceTests(unittest.TestCase):
    def test_invalid_dense_scan_leaves_correlated_redacted_status(self):
        base = build_index(load_corpus())
        trace = TraceCollector("ch13-stress-probes-v1", versions(base.snapshot, "q", "g", "i", "m"), eligible(base))
        def bad_scan(*args, **kwargs):
            raise ValueError("D10 raw confidential source")
        dense = SimpleNamespace(search=bad_scan)
        queries = {"invalid-scan": {"query_id": "invalid-scan", "question": "support", "slice": "test"}}
        with patch("experiment_ch13.embed", return_value=[[0.0]*384]):
            with self.assertRaises(ValueError):
                timed_queries(queries, base, build_bm25_index(base), dense, None, trials=1, trace=trace)
        failed = [r for r in trace.records if r["status"] == "invalid"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["query_id"], "invalid-scan")
        self.assertEqual(failed[0]["mode"], "dense")
        self.assertEqual(failed[0]["raw_candidate_ids"], [])
        self.assertNotIn("confidential", str(trace.records))
        self.assertNotIn("D10", str(trace.records))


if __name__ == "__main__":
    unittest.main()
