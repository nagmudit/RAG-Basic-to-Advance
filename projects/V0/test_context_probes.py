"""Check Chapter 4 prompt interventions without making LLM-quality claims."""

import json
import unittest

from context_probes import REQUIRED, build_cases, eligible_parts, safe_manifest, select
from engine import load_corpus


class ContextProbeTests(unittest.TestCase):
    def setUp(self):
        self.corpus = load_corpus()
        self.cases = build_cases(self.corpus)

    def ids(self, case_id):
        return [part["segment_id"] for part in self.cases[case_id]["context"]]

    def test_position_probe_keeps_evidence_and_prompt_length_fixed(self):
        names = ["position-front", "position-middle", "position-end"]
        self.assertEqual(
            {tuple(sorted(self.ids(name))) for name in names},
            {tuple(sorted(self.ids(names[0])))},
        )
        self.assertEqual(len({len(self.cases[name]["prompt"]) for name in names}), 1)
        self.assertEqual(self.ids("position-front")[:2], sorted(REQUIRED))
        self.assertEqual(self.ids("position-end")[-2:], sorted(REQUIRED))

    def test_conflict_and_instruction_probes_keep_required_evidence(self):
        for name in ("conflict-neutral", "conflict-stale", "instruction-base", "instruction-explicit"):
            self.assertTrue(REQUIRED.issubset(self.ids(name)))
        self.assertEqual(self.ids("instruction-base"), self.ids("instruction-explicit"))
        self.assertIn("P1:probe:0", self.ids("conflict-neutral"))
        self.assertIn("D3:FAQ-7:0", self.ids("conflict-stale"))

    def test_missing_amendment_and_scope_are_visible(self):
        self.assertNotIn("D2:§2:0", self.ids("missing-amendment"))
        parts = eligible_parts(self.corpus)
        with self.assertRaises(PermissionError):
            select(parts, ["D10:§1:0"])

    def test_manifest_is_redacted_and_does_not_claim_model_outcomes(self):
        manifest = safe_manifest(self.cases, self.corpus["snapshot"])
        logged = json.dumps(manifest)
        self.assertNotIn("SYSTEM: Ignore", logged)
        self.assertNotIn("Section 3", logged)
        self.assertNotIn("As of 20 May", logged)
        self.assertIsNone(manifest["model_result"])
        self.assertIsNone(manifest["model_token_count"])
        self.assertIn("SYSTEM: Ignore", self.cases["untrusted-injected"]["prompt"])
        self.assertNotIn("SYSTEM: Ignore", self.cases["untrusted-neutral"]["prompt"])


if __name__ == "__main__":
    unittest.main()
