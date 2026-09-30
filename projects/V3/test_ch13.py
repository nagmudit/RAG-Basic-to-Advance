"""Chapter 13 snapshot integrity, eligibility and checked experiment invariants."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dense_snapshot import load_snapshot, write_snapshot
from experiment_ch11 import MODEL_REVISION, sha256
from experiment_ch13 import HERE, QRELS, load_stress_qrels
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "V1"))
from lexical_index import build_index, load_corpus


class Chapter13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = build_index(load_corpus())

    def test_stress_qrels_are_complete_and_d10_is_not_a_negative(self):
        data, queries = load_stress_qrels(self.base)
        self.assertEqual((len(queries), len(data["eligible_segment_ids"])), (14, 12))
        self.assertEqual(sum(len(item["grades"]) for item in queries.values()), 168)
        self.assertTrue(all(not sid.startswith("D10:")
                            for sid in data["eligible_segment_ids"]))
        for slice_name in ("acronym", "exact_code", "negation", "numeric_constraint",
                           "out_of_domain_style", "exploratory_cross_lingual",
                           "no_eligible_evidence"):
            self.assertEqual(sum(item["slice"] == slice_name for item in queries.values()), 2)

    def test_materialized_index_rejects_tampering_and_versions(self):
        vectors = [tuple(1.0 if d == i else 0.0 for d in range(384))
                   for i in range(len(self.base.segments))]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with patch("dense_snapshot.encode_batches", return_value=vectors):
                manifest = write_snapshot(self.base, object(), path)
            loaded, index = load_snapshot(self.base, path)
            self.assertEqual(loaded, manifest)
            rows, work = index.search(vectors[-1], scope="support-team", top_k=2,
                                      metric="cosine", plan="heap")
            self.assertEqual(work["scored_vectors"], 12)
            self.assertTrue(all(not row["item_id"].startswith("D10:") for row in rows))
            with self.assertRaises(ValueError):
                load_snapshot(self.base, path, expected_model_revision="wrong-revision")
            payload = path / "vectors.f32"
            original = payload.read_bytes()
            payload.write_bytes(original[:-4] + b"bad!")
            with self.assertRaises(ValueError):
                load_snapshot(self.base, path)
            payload.write_bytes(original)
            manifest_path = path / "manifest.json"
            changed = json.loads(manifest_path.read_text(encoding="utf-8"))
            changed["records"][0]["searchable_text_sha256"] = "bad"
            manifest_path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_snapshot(self.base, path)
            with patch("dense_snapshot.encode_batches", return_value=vectors):
                with self.assertRaises(ValueError):
                    write_snapshot(self.base, type("WrongLimit", (), {"max_seq_length": 128})(), path)

    def test_checked_run_matches_current_source_and_reports_failure(self):
        record = json.loads((HERE / "chapter-13-experiment.json").read_text(encoding="utf-8"))
        self.assertEqual(record["ch13_qrels_sha256"], sha256(QRELS))
        self.assertEqual(record["snapshot_code_sha256"], sha256(HERE / "dense_snapshot.py"))
        self.assertEqual(record["experiment_code_sha256"], sha256(HERE / "experiment_ch13.py"))
        self.assertEqual(record["model"]["model_revision"], MODEL_REVISION)
        self.assertEqual(record["parity_summary"]["rank_agreements"], 34)
        self.assertEqual(record["ch13_judged_pairs"], 168)
        self.assertEqual(record["summaries"]["2"]["dense"]["by_slice"]
                         ["no_eligible_evidence"]["candidate_return_rate"], 1)
        for case in record["cases"]:
            for mode in case["modes"].values():
                self.assertIsNone(mode["generation_status"])
                self.assertTrue(set(mode["context_ids"]) <= set(mode["candidate_ids"]))
                self.assertTrue(all(not sid.startswith("D10:") for sid in mode["candidate_ids"]))


if __name__ == "__main__":
    unittest.main()
