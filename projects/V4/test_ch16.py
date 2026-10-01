"""Chapter 16 checks for coarse loss, PQ loss, scope and frozen evidence."""

import json
import math
import random
import unittest
from pathlib import Path

from ann_ch15 import exact_cosine, unit
from experiment_ch15 import source_hash
from experiment_ch16 import HERE
from ivf_pq_ch16 import IVFPQ, train_kmeans


class Chapter16Tests(unittest.TestCase):
    def make_rows(self):
        rng = random.Random(1601)
        return [{"item_id": f"p{i:03d}",
                 "vector": unit([rng.gauss(0, 1) for _ in range(8)]),
                 "allowed_scopes": ["public"]} for i in range(48)]

    def test_full_probe_flat_is_exact_but_pq_can_misorder(self):
        rows = self.make_rows()
        index = IVFPQ(rows, nlist=4, subspaces=4, bits=1, seed=16)
        pq_misses = 0
        for row in rows[:16]:
            q = row["vector"]
            oracle, _ = exact_cosine(rows, q, scope="public", k=2)
            flat, work = index.search(q, scope="public", k=2, nprobe=4)
            self.assertEqual([i for i, _ in flat], [i for i, _ in oracle])
            self.assertEqual(work["eligible_scored"], 48)
            adc, _ = index.search(q, scope="public", k=2, nprobe=4, mode="adc")
            pq_misses += [i for i, _ in adc] != [i for i, _ in oracle]
            refined, work = index.search(q, scope="public", k=2, nprobe=4,
                                         mode="adc", rerank_depth=48)
            self.assertEqual([i for i, _ in refined], [i for i, _ in oracle])
            self.assertEqual(work["original_reranked"], 48)
        self.assertGreater(pq_misses, 0)

    def test_coarse_probe_scope_and_tombstone(self):
        rows = self.make_rows()
        rows.append({"item_id": "restricted", "vector": rows[0]["vector"],
                     "allowed_scopes": ["private"]})
        index = IVFPQ(rows, nlist=4, subspaces=4, bits=2, seed=16)
        exact, _ = exact_cosine(rows, rows[0]["vector"], scope="public", k=2)
        result, work = index.search(rows[0]["vector"], scope="public", k=2, nprobe=4)
        self.assertEqual([i for i, _ in result], [i for i, _ in exact])
        self.assertNotIn("restricted", [i for i, _ in result])
        self.assertEqual(len(work["probed_lists"]), 4)
        index.delete("p000")
        result, _ = index.search(rows[0]["vector"], scope="public", k=2, nprobe=4)
        self.assertNotIn("p000", [i for i, _ in result])
        index.add({"item_id": "new", "vector": rows[1]["vector"],
                   "allowed_scopes": ["public"]})
        result, _ = index.search(rows[1]["vector"], scope="public", k=3, nprobe=4)
        self.assertIn("new", [i for i, _ in result])

    def test_fixed_figure_boundary_has_one_list_miss(self):
        angles = (15, 30, 60, 75, 105, 120, 150, 165,
                  195, 210, 240, 255, 285, 300, 330, 345)
        rows = [{"item_id": f"{i:02d}",
                 "vector": (math.cos(math.radians(a)), math.sin(math.radians(a))),
                 "allowed_scopes": ["demo"]} for i, a in enumerate(angles)]
        index = IVFPQ(rows, nlist=4, subspaces=2, bits=1, seed=16)
        q = (math.cos(math.radians(38)), math.sin(math.radians(38)))
        oracle, _ = exact_cosine(rows, q, scope="demo", k=2)
        one, _ = index.search(q, scope="demo", k=2, nprobe=1)
        two, _ = index.search(q, scope="demo", k=2, nprobe=2)
        self.assertEqual([i for i, _ in oracle], ["01", "02"])
        self.assertEqual([i for i, _ in one], ["01", "00"])
        self.assertEqual([i for i, _ in two], ["01", "02"])

    def test_training_and_search_contract(self):
        self.assertEqual(train_kmeans([(0,), (2,), (4,), (6,)], 2, seed=1),
                         train_kmeans([(0,), (2,), (4,), (6,)], 2, seed=1))
        with self.assertRaises(ValueError):
            IVFPQ(self.make_rows(), nlist=4, subspaces=3, bits=2)
        with self.assertRaises(ValueError):
            IVFPQ(self.make_rows(), nlist=4, subspaces=4, bits=6)
        compressed = IVFPQ(self.make_rows(), nlist=4, subspaces=4, bits=2,
                           keep_originals=False)
        compressed.search(self.make_rows()[0]["vector"], scope="public", k=2,
                          nprobe=4, mode="adc")
        with self.assertRaises(ValueError):
            compressed.search(self.make_rows()[0]["vector"], scope="public", k=2,
                              nprobe=4, mode="flat")

    def test_checked_record_hashes_and_error_decomposition(self):
        record = json.loads((HERE / "chapter-16-experiment.json").read_text(encoding="utf-8"))
        # Preserve the audited run and its historical hashes.
        from historical_results import verify_historical_result
        self.assertTrue(verify_historical_result(Path(__file__).with_name("chapter-16-experiment.json")))

        self.assertEqual(len(record["synthetic"]), 2)
        for workload in (*record["synthetic"], record["v0_diagnostic"]):
            all_lists = workload["nlist"]
            self.assertEqual(workload["summaries"][f"flat_p{all_lists}"]
                             ["mean_exact_neighbor_recall_at_2"], 1)
            self.assertLessEqual(workload["summaries"][f"adc_p{all_lists}"]
                                 ["mean_exact_neighbor_recall_at_2"], 1)
            self.assertLess(workload["summaries"]["flat_p1"]
                            ["mean_exact_neighbor_recall_at_2"], 1)
            self.assertLess(workload["summaries"][f"adc_p{all_lists}"]
                            ["mean_exact_neighbor_recall_at_2"], 1)
            for case in workload["cases"]:
                for mode in case["modes"].values():
                    self.assertIsNone(mode["generation_status"])
                    self.assertFalse(any(i.startswith("D10:") for i in
                                         mode["candidate_ids"] + mode.get("context_ids", [])))


if __name__ == "__main__":
    unittest.main()
