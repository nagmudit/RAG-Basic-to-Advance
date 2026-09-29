"""Independent arithmetic and integrity checks for Chapter 9 evaluation."""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from eval_ch09 import (JUDGMENTS_PATH, evaluate_ranking, load_judgments,
                       nearest_rank, summarize)
from lexical_index import build_index, load_corpus


class RankingMetricTests(unittest.TestCase):
    def test_hand_worked_graded_ranking_and_cutoff(self):
        grades = {"A": 2, "B": 1, "C": 0, "D": 0}
        at_three = evaluate_ranking(["C", "B", "A"], grades, 3)
        self.assertEqual(at_three["precision_at_k"], 2 / 3)
        self.assertEqual(at_three["recall_at_k"], 1)
        self.assertEqual(at_three["hit_at_k"], 1)
        self.assertEqual(at_three["f1_at_k"], .8)
        self.assertEqual(at_three["rr_at_k"], .5)
        self.assertAlmostEqual(at_three["ap_at_k"], 7 / 12)
        self.assertAlmostEqual(at_three["dcg_at_k"], 1 / math.log2(3) + 3 / 2)
        self.assertAlmostEqual(at_three["idcg_at_k"], 3 + 1 / math.log2(3))
        self.assertAlmostEqual(at_three["ndcg_at_k"],
                               (1 / math.log2(3) + 1.5) / (3 + 1 / math.log2(3)))
        self.assertTrue(at_three["all_direct_at_k"])
        at_two = evaluate_ranking(["C", "B", "A"], grades, 2)
        self.assertEqual(at_two["ap_at_k"], .25)  # denominator: both positives
        self.assertEqual(at_two["direct_recall_at_k"], 0)

    def test_missing_slots_zero_positive_and_invalid_run(self):
        grades = {"A": 2, "B": 0}
        row = evaluate_ranking(["A"], grades, 3)
        self.assertEqual(row["precision_at_k"], 1 / 3)
        self.assertEqual(row["recall_at_k"], 1)
        empty = evaluate_ranking([], {"A": 0, "B": 0}, 2)
        self.assertEqual(empty["precision_at_k"], 0)
        self.assertIsNone(empty["recall_at_k"])
        self.assertIsNone(empty["ap_at_k"])
        self.assertFalse(empty["no_positive_candidate_returned"])
        self.assertTrue(evaluate_ranking(["B"], {"A": 0, "B": 0}, 2)
                        ["no_positive_candidate_returned"])
        with self.assertRaises(ValueError):
            evaluate_ranking(["A", "A"], grades, 2)
        with self.assertRaises(ValueError):
            evaluate_ranking(["X"], grades, 2)
        with self.assertRaises(ValueError):
            evaluate_ranking(["A"], grades, 0)

    def test_macro_differs_from_micro_and_nearest_rank(self):
        first = evaluate_ranking(["A"], {"A": 2, "B": 1}, 1)
        second = evaluate_ranking(["D"], {"C": 2, "D": 0}, 1)
        zero = evaluate_ranking(["E"], {"E": 0}, 1)
        result = summarize([first, second, zero])
        self.assertEqual(result["macro_positive_query_mean"]["recall_at_k"], .25)
        self.assertEqual(result["micro_recall_at_k"], 1 / 3)
        self.assertEqual(result["zero_positive_candidate_rate"], 1)
        self.assertEqual(nearest_rank([2, 1, 4, 3, 5], .95), 5)


class JudgmentIntegrityTests(unittest.TestCase):
    def test_frozen_roster_and_eligibility(self):
        dataset, queries = load_judgments()
        self.assertEqual(len(dataset["eligible_segment_ids"]), 12)
        self.assertEqual(len(queries), 14)
        self.assertEqual(sum(bool(q["grade_1"] or q["grade_2"])
                             for q in queries.values()), 11)
        self.assertTrue(all(len(q["grades"]) == 12 for q in queries.values()))
        self.assertTrue(all("D10" not in segment_id
                            for q in queries.values() for segment_id in q["grades"]))
        self.assertEqual(queries["q-contract-change"]["grades"]["D3:FAQ-7:0"], 0)

    def test_roster_or_frozen_question_change_fails_closed(self):
        source = json.loads(JUDGMENTS_PATH.read_text(encoding="utf-8"))
        index = build_index(load_corpus())
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "qrels.json"
            changed = copy.deepcopy(source)
            changed["eligible_segment_ids"].remove("D9:proposal-2:0")
            target.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_judgments(index, target)
            changed = copy.deepcopy(source)
            changed["queries"][0]["question"] = "Altered old question"
            target.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_judgments(index, target)


if __name__ == "__main__":
    unittest.main()
