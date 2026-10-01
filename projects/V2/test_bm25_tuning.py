import copy
import json
import tempfile
import unittest
from pathlib import Path
from tune_bm25_ch09 import load_workload, select_parameters, run, K1, B
from lexical_index import build_index, load_corpus


class TuningTests(unittest.TestCase):
    def test_test_labels_cannot_choose_parameters(self):
        base = build_index(load_corpus()); data = load_workload(base)
        chosen, grid = select_parameters(base, data["development"])
        self.assertEqual(len(grid), len(K1)*len(B))
        for q in data["test"]:
            q["grades"] = {i: 2 for i in q["grades"]}
            q["question"] = "different unseen test text"
        self.assertEqual(chosen, select_parameters(base, data["development"])[0])
        self.assertFalse({q["query_id"] for q in data["development"]} & {q["query_id"] for q in data["test"]})

    def test_freeze_and_trace_and_test_slice_reporting(self):
        result = run(trials=1)
        self.assertFalse(result["selection"]["test_used_for_selection"])
        self.assertEqual(len(result["request_samples"]), 12)
        for mode in ("default", "selected"):
            self.assertEqual(len(result["test"][mode]["cases"]), 6)
            self.assertIn("no_eligible_evidence", result["test"][mode]["slices"])
        self.assertTrue(all(r["query_id"].startswith("test-") for r in result["request_samples"]))

    def test_cross_split_query_id_rejected(self):
        data = load_workload(build_index(load_corpus()))
        data["test"][0]["query_id"] = data["development"][0]["query_id"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bad.json";path.write_text(json.dumps(data, ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(ValueError):
                load_workload(build_index(load_corpus()), path)


if __name__ == "__main__":
    unittest.main()
