import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for version in ("V1", "V2", "V3"):
    sys.path.insert(0, str(ROOT / "projects" / version))
from lexical_index import build_index, load_corpus
from eval_ch09 import load_judgments as load09
from experiment_ch11 import load_judgments as load11
from experiment_ch12 import load_split
from experiment_ch13 import load_stress_qrels


class EvidenceIdentityTests(unittest.TestCase):
    def loaders(self, base):
        for loader in (load09, load11, load_split, load_stress_qrels):
            loader(base)

    def test_unchanged_and_whitespace_load(self):
        corpus = load_corpus()
        self.loaders(build_index(corpus))
        for doc in corpus["documents"]:
            doc["title"] = "  " + doc["title"].replace(" ", "\t ") + "\r\n"
            for section in doc["sections"]:
                section["text"] = section["text"].replace(" ", " \r\n\t") + "  "
        self.loaders(build_index(corpus))

    def test_same_id_snapshot_changed_fact_rejected(self):
        corpus = load_corpus()
        before = (corpus["snapshot"], corpus["documents"][0]["id"])
        corpus["documents"][0]["sections"][0]["text"] = corpus["documents"][0]["sections"][0]["text"].replace("four hours", "nine hours")
        self.assertEqual(before, (corpus["snapshot"], corpus["documents"][0]["id"]))
        base = build_index(corpus)
        for loader in (load09, load11, load_split, load_stress_qrels):
            with self.subTest(loader=loader.__module__), self.assertRaisesRegex(ValueError, "Stale/incompatible"):
                loader(base)

    def test_locator_permission_authority_changes_rejected(self):
        for change in (lambda d: d["sections"][0].update(span="new-locator"),
                       lambda d: d["allowed_scopes"].append("legal-team"),
                       lambda d: d.update(status="unsigned draft"),
                       lambda d: d.update(effective_on="2099-01-01")):
            corpus = load_corpus(); change(corpus["documents"][0])
            with self.assertRaises(ValueError):
                load09(build_index(corpus))


if __name__ == "__main__":
    unittest.main()
