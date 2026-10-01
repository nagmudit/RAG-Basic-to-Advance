import copy
import json
import unittest
from pathlib import Path
from split_semantics import validate_generalization


class SplitSemanticsTests(unittest.TestCase):
    def data(self):
        return json.loads((Path(__file__).resolve().parents[1] / "V3/judgments_ch12.json").read_text(encoding="utf-8"))

    def test_current_document_holdout_reports_family_overlap(self):
        report = validate_generalization(self.data())
        self.assertEqual(report["family_overlap"]["train/validation"], ["helios-support"])
        self.assertEqual(report["family_overlap"]["train/test"], ["helios-support"])
        self.assertFalse(report["unseen_family_transfer_established"])

    def test_same_data_cannot_claim_family_holdout(self):
        data = self.data(); data["generalization_unit"] = "source-family-holdout"
        with self.assertRaises(ValueError):
            validate_generalization(data)

    def test_family_holdout_validator_and_incomplete_map(self):
        data = self.data(); data["generalization_unit"] = "source-family-holdout"
        data["source_family"] = {d: name for name, docs in data["document_split"].items() for d in docs}
        self.assertTrue(all(not overlap for overlap in validate_generalization(data)["family_overlap"].values()))
        del data["source_family"]["D1"]
        with self.assertRaises(ValueError):
            validate_generalization(data)


if __name__ == "__main__":
    unittest.main()
