"""Behavioral checks for the V0 evidence and eligibility contract.

Run: python -m unittest discover -s projects/V0 -p 'test_*.py' -v
"""

import copy
import json
import unittest
from datetime import datetime

from engine import Engine, FROZEN_QUESTIONS, load_corpus, search


class V0ContractTests(unittest.TestCase):
    def setUp(self):
        self.corpus = load_corpus()
        self.engine = Engine(self.corpus)

    def test_contract_change_requires_both_source_spans(self):
        answer, trace, _ = self.engine.run("q-contract-change")
        self.assertEqual(trace["status"], "answered")
        self.assertEqual(set(trace["evidence_ids"]), {"D1:§3:0", "D2:§2:0"})
        self.assertIn("75%", answer)

        incomplete = copy.deepcopy(self.corpus)
        incomplete["documents"] = [
            doc for doc in incomplete["documents"] if doc["id"] != "D2"
        ]
        incomplete["snapshot"] += "-without-D2"
        answer, trace, _ = Engine(incomplete).run("q-contract-change")
        self.assertEqual(trace["status"], "abstained")
        self.assertEqual(trace["evidence_ids"], [])
        self.assertNotIn("one hour", answer)

    def test_restricted_source_never_enters_candidates_or_prompt(self):
        _, trace, prompt = self.engine.run("q-contract-change", scope="support-team")
        self.assertFalse(
            any(row["segment_id"].startswith("D10:") for row in trace["candidate_scores"])
        )
        self.assertFalse(any(ref.startswith("D10:") for ref in trace["context_ids"]))
        self.assertNotIn("thirty-minute", prompt)
        self.assertEqual(trace["eligible_segments_scanned"], 12)

    def test_inaccessible_amendment_is_excluded_before_scoring(self):
        restricted = copy.deepcopy(self.corpus)
        for document in restricted["documents"]:
            if document["id"] == "D2":
                document["allowed_scopes"] = ["legal-team"]
        restricted["snapshot"] += "-D2-restricted"
        answer, trace, prompt = Engine(restricted).run("q-contract-change")
        self.assertEqual(trace["status"], "abstained")
        self.assertFalse(
            any(row["segment_id"].startswith("D2:") for row in trace["candidate_scores"])
        )
        self.assertFalse(any(ref.startswith("D2:") for ref in trace["context_ids"]))
        self.assertNotIn("one hour", prompt)
        self.assertNotIn("one hour", answer)

    def test_source_only_request_returns_the_clause(self):
        answer, trace, _ = self.engine.run("q-termination")
        self.assertEqual(trace["status"], "answered")
        self.assertEqual(trace["evidence_ids"], ["D1:§8:0"])
        self.assertIn("30 days' written notice", answer)

    def test_candidate_depth_changes_answerability(self):
        _, narrow, _ = self.engine.run("q-contract-change", top_k=1)
        _, wider, _ = self.engine.run("q-contract-change", top_k=2)
        self.assertEqual(narrow["status"], "abstained")
        self.assertEqual(wider["status"], "answered")
        self.assertEqual(narrow["candidate_scores"][0]["segment_id"], "D2:§2:0")
        self.assertEqual(len(wider["evidence_ids"]), 2)

    def test_no_shared_terms_returns_no_candidates(self):
        matches, scanned = search(self.engine.segments, "zymurgy", "support-team", 8)
        self.assertEqual(matches, [])
        self.assertEqual(scanned, 12)
        _, trace, _ = self.engine.run("q-contract-change", question="zymurgy")
        self.assertEqual(trace["status"], "abstained")
        self.assertEqual(trace["reason"], "no_result")

    def test_trace_omits_raw_question_and_source_text(self):
        _, trace, _ = self.engine.run("q-contract-change")
        self.assertEqual(datetime.fromisoformat(trace["timestamp_utc"]).utcoffset().total_seconds(), 0)
        logged = json.dumps(trace)
        self.assertNotIn(FROZEN_QUESTIONS["q-contract-change"], logged)
        self.assertNotIn("Section 3’s", logged)
        self.assertNotIn("thirty-minute", logged)

    def test_context_budget_can_remove_required_evidence(self):
        _, trace, _ = self.engine.run("q-contract-change", context_budget_words=5)
        self.assertEqual(trace["status"], "abstained")
        self.assertEqual(trace["context_ids"], [])
        self.assertEqual(trace["reason"], "context_empty")

    def test_small_windows_split_the_required_quote(self):
        fragmented = Engine(self.corpus, window_words=8)
        _, trace, _ = fragmented.run("q-contract-change", top_k=20)
        self.assertEqual(trace["status"], "abstained")
        self.assertTrue(
            any(row["segment_id"].startswith("D2:") for row in trace["candidate_scores"])
        )

    def test_long_section_has_ordered_nonoverlapping_windows(self):
        pieces = [
            part for part in self.engine.segments if part["document_id"] == "D4"
        ]
        self.assertGreaterEqual(len(pieces), 3)
        self.assertEqual(pieces[0]["word_start"], 0)
        for earlier, later in zip(pieces, pieces[1:]):
            self.assertEqual(earlier["word_end_exclusive"], later["word_start"])


if __name__ == "__main__":
    unittest.main()
