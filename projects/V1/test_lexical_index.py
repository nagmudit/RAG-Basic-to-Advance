"""Behavioral checks for Chapter 5's index and preserved V0 contract."""

import unittest
from pathlib import Path

from lexical_index import (
    Analyzer, IndexedEngine, boolean_ids, build_index, load_corpus,
    phrase_ids, search, segment_corpus,
)
from engine import Engine as V0Engine, FROZEN_QUESTIONS, search as v0_search


TOY = Path(__file__).with_name("toy_corpus.json")


class LexicalIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toy = build_index(load_corpus(TOY))
        cls.v0_corpus = load_corpus()
        cls.v1 = IndexedEngine(cls.v0_corpus)

    def test_postings_positions_and_tf_keep_fields_separate(self):
        row = next(row for row in self.toy.posting("hx-7a") if row.segment_id == "S1:body:0")
        self.assertEqual(row.title_positions, ())
        self.assertEqual(row.body_positions, (2,))
        self.assertEqual(row.term_frequency, 1)
        self.assertEqual(self.toy.field_lengths[0], {"title": 1, "body": 5})
        self.assertEqual(
            [row.segment_id for row in self.toy.posting("hx-7a")],
            ["S1:body:0", "S2:body:0", "S3:body:0", "S5:body:0"],
        )

    def test_boolean_and_or_not_are_scoped_before_results(self):
        self.assertEqual(
            boolean_ids(self.toy, all_terms=["hx-7a", "guide"]),
            ["S1:body:0", "S3:body:0"],
        )
        self.assertEqual(
            boolean_ids(self.toy, any_terms=["checklist", "legacy"], not_terms=["legacy"]),
            ["S2:body:0"],
        )
        self.assertEqual(boolean_ids(self.toy, all_terms=["key"]), [])
        with self.assertRaises(ValueError):
            boolean_ids(self.toy, not_terms=["legacy"])

    def test_phrase_requires_adjacent_positions_in_one_field(self):
        self.assertEqual(phrase_ids(self.toy, "reset guide"), ["S1:body:0", "S3:body:0", "S4:body:0"])
        self.assertEqual(phrase_ids(self.toy, "guide reset"), [])
        self.assertEqual(phrase_ids(self.toy, "manual helios"), [])  # no title/body crossing
        self.assertEqual(phrase_ids(self.toy, "hx-7a reset"), ["S1:body:0", "S2:body:0", "S3:body:0"])

    def test_rare_code_and_misspelling_are_not_semantic_or_fuzzy(self):
        rows, work = search(self.toy, "HX-7A", top_k=10)
        self.assertEqual([row["segment_id"] for row in rows], ["S1:body:0", "S2:body:0", "S3:body:0"])
        self.assertEqual(work["scored_segments"], 3)
        self.assertEqual(search(self.toy, "HX-7C", top_k=10)[0], [])
        self.assertEqual(search(self.toy, "resett", top_k=10)[0], [])

    def test_or_ranking_is_distinct_term_overlap_with_v0_ties(self):
        rows, _ = search(self.toy, "HX-7A reset guide", top_k=10)
        self.assertEqual(
            [(row["segment_id"], row["score"]) for row in rows],
            [("S1:body:0", 3), ("S3:body:0", 3), ("S2:body:0", 2), ("S4:body:0", 2)],
        )
        repeated, _ = search(self.toy, "HX-7A reset reset guide", top_k=10)
        self.assertEqual(
            [(row["segment_id"], row["score"]) for row in repeated],
            [(row["segment_id"], row["score"]) for row in rows],
        )

    def test_repeated_term_phrase_needs_each_offset(self):
        corpus = {
            "snapshot": "repetition-test-v1",
            "documents": [{
                "id": "S1", "title": "Example", "version": "v1",
                "allowed_scopes": ["support-team"],
                "sections": [{"span": "body", "text": "go go now"}],
            }],
        }
        index = build_index(corpus)
        self.assertEqual(phrase_ids(index, "go go"), ["S1:body:0"])
        self.assertEqual(phrase_ids(index, "go now"), ["S1:body:0"])
        self.assertEqual(phrase_ids(index, "go go go"), [])

    def test_unicode_nfc_matches_canonical_forms_but_v0_does_not(self):
        unicode_index = build_index(load_corpus(TOY), Analyzer("unicode_nfc"))
        rows, _ = search(unicode_index, "cafe\u0301", top_k=10)
        self.assertEqual([row["segment_id"] for row in rows], ["S4:body:0"])
        self.assertEqual(search(self.toy, "cafe\u0301", top_k=10)[0], [])

    def test_indexed_v0_analyzer_matches_full_scan_order_scores_and_answers(self):
        segments = segment_corpus(self.v0_corpus)
        v0_engine = V0Engine(self.v0_corpus)
        for query_id, question in FROZEN_QUESTIONS.items():
            for top_k in (1, 2, 8):
                with self.subTest(query_id=query_id, top_k=top_k):
                    baseline, _ = v0_search(segments, question, "support-team", top_k)
                    indexed, work = search(self.v1.index, question, "support-team", top_k)
                    self.assertEqual(
                        [(row["segment_id"], row["score"]) for row in indexed],
                        [(row["segment_id"], row["score"]) for row in baseline],
                    )
                    self.assertLessEqual(work["scored_segments"], work["eligible_segments"])
                    old_answer, old_trace, _ = v0_engine.run(query_id, top_k=top_k)
                    new_answer, new_trace, _ = self.v1.run(query_id, top_k=top_k)
                    self.assertEqual((new_answer, new_trace["status"], new_trace["evidence_ids"]),
                                     (old_answer, old_trace["status"], old_trace["evidence_ids"]))

    def test_missing_amendment_and_inaccessible_source_do_not_leak(self):
        missing = load_corpus()
        missing["documents"] = [doc for doc in missing["documents"] if doc["id"] != "D2"]
        missing["snapshot"] += "-without-D2"
        _, trace, prompt = IndexedEngine(missing).run("q-contract-change")
        self.assertEqual(trace["status"], "abstained")
        self.assertNotIn("D2:", repr(trace))
        self.assertNotIn("[D2", prompt)
        rows, _ = search(self.v1.index, "thirty-minute", scope="support-team", top_k=20)
        self.assertFalse(any(row["document_id"] == "D10" for row in rows))
        _, trace, prompt = self.v1.run("q-contract-change")
        self.assertNotIn("D10:", repr(trace))
        self.assertNotIn("[D10", prompt)


if __name__ == "__main__":
    unittest.main()
