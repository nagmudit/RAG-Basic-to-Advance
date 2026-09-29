"""Chapter 8's exact-top-k, skip, tie, scope and codec checks."""

import json
import random
import unittest
from pathlib import Path

from bm25 import build_bm25_index, search as exhaustive_search
from lexical_index import load_corpus
from postings_codec import decode_docids, encode_docids, encode_positive
from wand import build_wand_index, exhaustive_cached_search, search as wand_search


HERE = Path(__file__).resolve().parent


def signature(rows):
    return [(row["segment_id"], row["score"]) for row in rows]


class WANDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toy = json.loads((HERE / "toy_pruning_corpus.json").read_text(encoding="utf-8"))
        cls.bm25 = build_bm25_index(cls.toy)
        cls.wand = build_wand_index(cls.bm25)

    def assert_same(self, bm25, wand, question, *, scope="support-team", top_k=1):
        reference, _ = exhaustive_search(bm25, question, scope=scope, top_k=top_k)
        cached, _ = exhaustive_cached_search(wand, question, scope=scope, top_k=top_k)
        pruned, work, _ = wand_search(wand, question, scope=scope, top_k=top_k)
        self.assertEqual(signature(cached), signature(reference))
        self.assertEqual(signature(pruned), signature(reference))
        return work

    def test_toy_skips_four_postings_and_preserves_top_one(self):
        exhaustive, exhaustive_work = exhaustive_search(self.bm25, "rare common", top_k=1)
        result, work, steps = wand_search(
            self.wand, "rare common", top_k=1, capture_steps=True
        )
        self.assertEqual(signature(result), signature(exhaustive))
        self.assertEqual(exhaustive_work["scored_segments"], 6)
        self.assertEqual(work["fully_scored_segments"], 2)
        self.assertEqual(work["postings_advanced_by_seek"], 4)
        self.assertEqual([step["action"] for step in steps],
                         ["score", "seek", "score"])
        self.assertIsNone(steps[0]["threshold_before"])
        self.assertEqual(steps[1]["from"], 1)
        self.assertEqual(steps[1]["to"], 5)

    def test_depth_and_scope_parity(self):
        for scope in ("support-team", "legal-team", "missing"):
            for top_k in (1, 2, 5, 10):
                with self.subTest(scope=scope, top_k=top_k):
                    self.assert_same(self.bm25, self.wand, "rare common",
                                     scope=scope, top_k=top_k)
        support, _, _ = wand_search(self.wand, "rare common")
        self.assertNotIn("P7:body:0", [row["segment_id"] for row in support])

    def test_ties_are_not_pruned_on_equal_score(self):
        corpus = {
            "snapshot": "tie-probe", "documents": [
                {"id": f"P{i}", "title": "", "version": "v1",
                 "allowed_scopes": ["support-team"],
                 "sections": [{"span": "body", "text": "same"}]}
                for i in (3, 1, 2)
            ],
        }
        bm25 = build_bm25_index(corpus)
        wand = build_wand_index(bm25)
        rows, work, _ = wand_search(wand, "same", top_k=1)
        self.assertEqual(rows[0]["segment_id"], "P1:body:0")
        self.assertEqual(work["fully_scored_segments"], 3)
        self.assert_same(bm25, wand, "same", top_k=2)

    def test_no_result_and_invalid_k(self):
        rows, work, _ = wand_search(self.wand, "absent")
        self.assertEqual(rows, [])
        self.assertEqual(work["fully_scored_segments"], 0)
        with self.assertRaises(ValueError):
            wand_search(self.wand, "rare", top_k=0)

    def test_frozen_v0_queries_and_parameter_versions(self):
        corpus = load_corpus()
        for b, boost in ((.75, 1.0), (0, 1.0), (.75, .1)):
            bm25 = build_bm25_index(corpus, b=b, title_boost=boost)
            wand = build_wand_index(bm25)
            for query in ("the support", "initial response target",
                          "12000 credits", "zzzx-missing", "termination support"):
                for k in (1, 2, 8):
                    with self.subTest(b=b, boost=boost, query=query, k=k):
                        self.assert_same(bm25, wand, query, top_k=k)

    def test_seeded_small_corpora_preserve_order_and_float_scores(self):
        rng = random.Random(8082026)
        vocabulary = ("amber", "blue", "green", "rare")
        for case in range(6):
            documents = []
            for i in range(1, 13):
                body = " ".join(rng.choice(vocabulary) for _ in range(rng.randint(1, 8)))
                documents.append({
                    "id": f"P{i}", "title": "", "version": "v1",
                    "allowed_scopes": ["support-team"],
                    "sections": [{"span": "body", "text": body}],
                })
            bm25 = build_bm25_index({"snapshot": f"seeded-{case}",
                                     "documents": documents})
            wand = build_wand_index(bm25)
            for query in ("amber blue", "rare green", "blue", "absent"):
                for k in (1, 3, 8):
                    with self.subTest(case=case, query=query, k=k):
                        self.assert_same(bm25, wand, query, top_k=k)


class CodecTests(unittest.TestCase):
    def test_hand_bytes_and_roundtrip(self):
        encoded = encode_docids([3, 8, 138])
        self.assertEqual(encoded, bytes([0x83, 0x85, 0x01, 0x82]))
        self.assertEqual(decode_docids(encoded), [3, 8, 138])
        self.assertEqual(decode_docids(b""), [])
        self.assertEqual(decode_docids(encode_docids([1, 128, 129, 100000])),
                         [1, 128, 129, 100000])

    def test_codec_rejects_nonmonotone_and_truncated_data(self):
        for docids in ([3, 3], [3, 2], [0]):
            with self.assertRaises(ValueError):
                encode_docids(docids)
        with self.assertRaises(ValueError):
            encode_positive(0)
        for data in (b"\x00", b"\x01", b"\x80"):
            with self.assertRaises(ValueError):
                decode_docids(data)


if __name__ == "__main__":
    unittest.main()
