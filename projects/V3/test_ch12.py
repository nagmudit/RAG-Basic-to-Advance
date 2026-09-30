"""Tests for split integrity, false-negative policy, and query adaptation."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from experiment_ch12 import JUDGMENTS, HERE, adapt_query, load_split, rank_dense
from experiment_ch11 import sha256
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "V1"))
from lexical_index import build_index, load_corpus


class Chapter12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = build_index(load_corpus())

    def test_frozen_split_and_complete_roster(self):
        data = load_split(self.base)
        self.assertEqual(len(data["training_pairs"]), 10)
        self.assertEqual(len(data["validation_queries"]), 4)
        self.assertEqual(len(data["test_queries"]), 11)
        self.assertEqual(len(data["eligible_segment_ids"]), 12)
        self.assertEqual(sum(len(q["grades"]) for q in data["validation_queries"] +
                             data["test_queries"]), 180)
        self.assertTrue(all(not sid.startswith("D10:")
                            for sid in data["eligible_segment_ids"]))

    def test_rejects_source_leak_and_masked_positive(self):
        original = json.loads(JUDGMENTS.read_text(encoding="utf-8"))
        for mutate in (
            lambda d: d["document_split"]["test"].append("D1"),
            lambda d: d["training_pairs"][0].update(positive_id="D5:§3:0"),
            lambda d: d["training_pairs"][0]["unsafe_negative_ids"].append("D5:§3:0"),
            lambda d: d["training_pairs"][0]["unsafe_negative_ids"].append("D1:§8:0"),
            lambda d: d["test_queries"][0].update(grade_2=["D1:§8:0"]),
        ):
            data = copy.deepcopy(original)
            mutate(data)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_split(self.base, path)

    def test_zero_adapter_is_identity_and_exact_rank(self):
        import torch
        q = torch.tensor([1.0, 0.0, 0.0])
        a = torch.ones((1, 3)) * .01
        b = torch.zeros((3, 1))
        self.assertTrue(torch.allclose(adapt_query(q, a, b), q))
        p = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        self.assertEqual([sid for sid, _ in rank_dense(q, p, ["p1", "p2"], a, b)],
                         ["p1", "p2"])

    def test_checked_in_record_keeps_negative_result_and_versions(self):
        record = json.loads((HERE / "chapter-12-experiment.json").read_text(encoding="utf-8"))
        self.assertEqual(record["qrels_sha256"], sha256(JUDGMENTS))
        self.assertEqual(record["experiment_code_sha256"], sha256(HERE / "experiment_ch12.py"))
        self.assertEqual(record["test_judged_pairs"], 132)
        self.assertEqual(record["training"]["selected_epoch"], 1)
        self.assertEqual(record["training"]["history"][1]["validation_recall_at_2"], 0)
        frozen = record["test"]["frozen"]["summary"]["macro_positive_query_mean"]
        adapted = record["test"]["adapted"]["summary"]["macro_positive_query_mean"]
        self.assertEqual(frozen["recall_at_k"], adapted["recall_at_k"])
        for mode in record["test"].values():
            self.assertEqual(mode["summary"]["zero_positive_candidate_rate"], 1)
            self.assertTrue(all(not sid.startswith("D10:") for case in mode["cases"]
                                for sid in case["candidate_ids"]))


if __name__ == "__main__":
    unittest.main()
