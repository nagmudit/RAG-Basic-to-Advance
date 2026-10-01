import unittest
from experiment_trace import TraceCollector, REQUIRED_FIELDS


class TraceTests(unittest.TestCase):
    def collector(self):
        return TraceCollector("toy", {key: "v1" for key in
            ("corpus_version", "query_set_version", "qrels_version", "index_version", "model_version")}, {"a", "b"})

    def test_required_and_actual_candidates(self):
        c = self.collector()
        result, rec = c.execute("q", "exact", 0, lambda: ([("b", .7)], {}),
                                context_selector=lambda result: ["b"])
        self.assertTrue(set(REQUIRED_FIELDS) <= rec.keys())
        self.assertEqual(rec["final_candidate_ids"], [result[0][0][0]])
        self.assertEqual(rec["context_ids"], ["b"])

    def test_invalid_and_failed_redacted(self):
        for error, status in ((ValueError, "invalid"), (RuntimeError, "failed")):
            c = self.collector()
            def broken():
                raise error("D10 raw confidential source text")
            with self.assertRaises(error):
                c.execute("invalid-q", "ann", 0, broken)
            self.assertEqual(c.records[0]["status"], status)
            self.assertNotIn("confidential", str(c.records))
            self.assertNotIn("D10", str(c.records))

    def test_protected_ids_are_rejected_and_not_logged(self):
        c = self.collector()
        with self.assertRaises(ValueError):
            c.execute("q", "bad", 0, lambda: ([("D10:private", 9)], {}))
        self.assertEqual(c.records[0]["status"], "failed")
        self.assertNotIn("D10", str(c.records))

    def test_eligibility_precedes_context_callback(self):
        c = self.collector()
        called = []
        with self.assertRaises(ValueError):
            c.execute("q", "bad", 0, lambda: ([("D10:private", 9)], {}),
                      context_selector=lambda r: called.append(r))
        self.assertEqual(called, [])
        self.assertNotIn("D10", str(c.records))

    def test_multistage_guard_redacts_failure(self):
        c = self.collector()
        with self.assertRaises(ValueError):
            with c.guard("invalid-q", "dense", 3):
                raise ValueError("protected D10 query/source")
        self.assertEqual(c.records[0]["status"], "invalid")
        self.assertNotIn("D10", str(c.records))


if __name__ == "__main__":
    unittest.main()
