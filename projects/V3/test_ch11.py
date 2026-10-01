"""Chapter 11 arithmetic, frozen-qrel and checked-in run invariants."""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from contrastive_math import in_batch_loss, masked_mean_pool
from experiment_ch11 import (DATASET_PATH, MODEL_REVISION, load_judgments,
                             sha256)
from lexical_index import build_index, load_corpus


class ContrastiveMathTests(unittest.TestCase):
    def test_masked_mean_pool_ignores_padding(self):
        self.assertEqual(masked_mean_pool([(2, 0), (0, 4), (99, 99)],
                                          [1, 1, 0]), (1, 2))
        with self.assertRaises(ValueError):
            masked_mean_pool([(1, 2)], [0])

    def test_stable_two_pair_loss_and_temperature(self):
        loss, probabilities = in_batch_loss(((3, 1), (0, 2)))
        self.assertAlmostEqual(loss, math.log1p(math.exp(-2)))
        self.assertAlmostEqual(probabilities[0], .8807970779778823)
        self.assertAlmostEqual(probabilities[1], .8807970779778823)
        colder, _ = in_batch_loss(((3, 1), (0, 2)), temperature=.5)
        self.assertLess(colder, loss)
        huge, _ = in_batch_loss(((10000, 9999), (9999, 10000)))
        self.assertTrue(math.isfinite(huge))

    def test_false_negative_contract_is_visible(self):
        loss, probabilities = in_batch_loss(((1, 1), (1, 1)))
        self.assertAlmostEqual(loss, math.log(2))
        for probability in probabilities:
            self.assertAlmostEqual(probability, .5)
        with self.assertRaises(ValueError):
            in_batch_loss(((1, 2),))
        with self.assertRaises(ValueError):
            in_batch_loss(((1,),), temperature=0)
        with self.assertRaises(ValueError):
            in_batch_loss(((1e300,),), temperature=1e-300)


class FrozenProbeTests(unittest.TestCase):
    def setUp(self):
        self.base = build_index(load_corpus())

    def test_roster_and_query_set_are_complete(self):
        data, queries = load_judgments(self.base)
        self.assertEqual((len(queries), len(data["eligible_segment_ids"])), (17, 12))
        self.assertEqual(sum(x["slice"] == "paraphrase" for x in queries.values()), 8)
        self.assertEqual(sum(x["slice"] == "exact_identifier" for x in queries.values()), 6)
        self.assertEqual(sum(x["slice"] == "no_eligible_evidence" for x in queries.values()), 3)
        self.assertTrue(all(len(q["grades"]) == 12 for q in queries.values()))
        self.assertTrue(all(not x.startswith("D10:") for x in data["eligible_segment_ids"]))

    def test_changed_roster_or_ineligible_label_is_rejected(self):
        data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
        for mutation in ("roster", "private"):
            changed = copy.deepcopy(data)
            if mutation == "roster":
                changed["eligible_segment_ids"].pop()
            else:
                changed["queries"][0]["grade_2"].append("D10:§1:0")
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "qrels.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_judgments(self.base, path)

    def test_checked_in_run_versions_and_stage_separation(self):
        path = DATASET_PATH.parent / "chapter-11-experiment.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["model"]["model_revision"], MODEL_REVISION)
        # Preserve the audited run and its historical hashes.
        from historical_results import verify_historical_result
        self.assertTrue(verify_historical_result(Path(__file__).with_name("chapter-11-experiment.json")))
        self.assertEqual((record["query_count"], record["judged_pairs"]), (17, 204))
        self.assertEqual(record["model"]["dimension"], 384)
        for case in record["cases"]:
            for mode in ("bm25", "frozen_encoder"):
                result = case["modes"][mode]
                self.assertIsNone(result["generation_status"])
                self.assertTrue(set(result["context_ids"]) <= set(result["candidate_ids"]))
                self.assertTrue(all(not x.startswith("D10:") for x in result["candidate_ids"]))
                if mode == "frozen_encoder":
                    self.assertEqual(result["work"]["scored_vectors"], 12)
        rows = [x for x in record["cases"] if x["top_k"] == 2]
        shared = next(x for x in rows if x["query_id"] == "p-shared")
        self.assertNotIn("D4:step-4:1", shared["modes"]["bm25"]["candidate_ids"])
        self.assertEqual(shared["modes"]["frozen_encoder"]["candidate_ids"][0],
                         "D4:step-4:1")
        for qid in ("i-segment", "i-price-id"):
            case = next(x for x in rows if x["query_id"] == qid)
            self.assertEqual(case["modes"]["bm25"]["candidate_ids"], [])
            self.assertEqual(case["modes"]["frozen_encoder"]["ranking_metrics"]
                             ["binary_hits"], 0)


if __name__ == "__main__":
    unittest.main()
