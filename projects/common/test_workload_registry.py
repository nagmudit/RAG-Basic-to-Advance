import json
import sys
import unittest
from pathlib import Path
from qrel_identity import digest
from historical_results import verify_historical_result

ROOT = Path(__file__).resolve().parents[2]


class RegistryTests(unittest.TestCase):
    def test_identity_counts_slices_and_markdown_register(self):
        registry = json.loads((ROOT / "evaluation/WORKLOAD_REGISTRY.json").read_text(encoding="utf-8"))
        rows = registry["workloads"]
        self.assertEqual(len({r["workload_id"] for r in rows}), len(rows))
        md = (ROOT / "evaluation/WORKLOAD_REGISTRY.md").read_text(encoding="utf-8")
        for r in rows:
            with self.subTest(workload=r["workload_id"]):
                self.assertIn(r["workload_id"], md)
                for key in ("chapters_using_it", "corpus_version", "query_set_version", "qrels_version",
                            "number_of_queries", "judgment_count", "query_slices", "purpose",
                            "valid_comparisons", "invalid_cross_workload_inferences"):
                    self.assertIn(key, r)
                self.assertTrue((ROOT / r["source"]).exists())
                if "judgments" not in r["source"]:
                    if r["source"].endswith("experiment_ch14.py"):
                        sys.path.insert(0, str(ROOT / "projects/V3"))
                        from experiment_ch14 import SPARSE_QRELS, TOKEN_QRELS
                        grades = SPARSE_QRELS if "sparse" in r["workload_id"] else TOKEN_QRELS
                        self.assertEqual(r["number_of_queries"], 1)
                        self.assertEqual(r["judgment_count"], len(grades))
                    if "synthetic" in r["workload_id"]:
                        chapter = r["chapters_using_it"][0]
                        reference = json.loads((ROOT / f"projects/V4/chapter-{chapter}-experiment.json").read_text(encoding="utf-8"))
                        matching = [case for case in reference["synthetic"]
                            if f"ch{chapter}-synthetic-n{case['n']}-d{case['dimension']}-v1" == r["workload_id"]]
                        self.assertEqual(len(matching), 1)
                        case = matching[0]
                        self.assertEqual(r["number_of_queries"], case["query_count"])
                        self.assertEqual(r["number_of_queries"], len(case["cases"]))
                        self.assertEqual(r["judgment_count"], 0)
                        self.assertEqual(r["oracle_neighbor_memberships"], 2*case["query_count"])
                        expected_corpus = (f"synthetic-{case['n']}-{case['dimension']}-{case['seed']}"
                                           if chapter == 15 else f"synth-{case['seed']}")
                        self.assertEqual(r["corpus_version"], expected_corpus)
                    continue
                data = json.loads((ROOT / r["source"]).read_text(encoding="utf-8"))
                self.assertEqual(r["qrels_version"], data["version"])
                self.assertEqual(r["evidence_manifest_sha256"], data["evidence_identity"]["manifest_sha256"])
                if "queries" in data:
                    self.assertEqual(r["number_of_queries"], len(data["queries"]))
                    self.assertEqual(r["judgment_count"], len(data["queries"])*len(data["eligible_segment_ids"]))
                    self.assertEqual(r["query_slices"], {s: sum(q["slice"] == s for q in data["queries"])
                        for s in {q["slice"] for q in data["queries"]}})
                elif "document_split" in data:
                    self.assertEqual(r["number_of_queries"], sum(len(data[k]) for k in ("training_pairs", "validation_queries", "test_queries")))
                    self.assertEqual(r["judgment_count"], (len(data["validation_queries"])+len(data["test_queries"]))*12)
                else:
                    self.assertEqual(r["number_of_queries"], len(data["development"])+len(data["test"]))
                    self.assertEqual(r["judgment_count"], r["number_of_queries"]*12)

    def test_historical_results_are_byte_preserved(self):
        sealed = json.loads((ROOT / "projects/common/HISTORICAL_RESULTS.json").read_text(encoding="utf-8"))
        for path in sealed["records"]:
            with self.subTest(path=path):
                self.assertTrue(verify_historical_result(ROOT / path))


if __name__ == "__main__":
    unittest.main()
