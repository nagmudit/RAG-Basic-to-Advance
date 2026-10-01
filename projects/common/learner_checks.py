"""Executable assessment fixtures, independent of supplied project engines.

These are public feedback tests, not a secret grading service. The lab asks the
learner to make a first attempt before inspecting these new input fixtures.
"""
import argparse
import importlib.util
import math
import random
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location("learner_attempt", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(chapter, m):
    def near(actual, expected):
        assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10), (actual, expected)
    if chapter == 5:
        docs = {"Z": ["go", "go", "home"], "A": ["home", "go", "now"], "M": ["go", "home", "go"]}
        p = m.build_postings(docs)
        assert p["go"] == {"A": [1], "M": [0, 2], "Z": [0, 1]}
        assert m.phrase_match(p, ["go", "go"]) == ["Z"]
        assert m.phrase_match(p, ["go", "home"]) == ["M", "Z"]
        assert m.phrase_match(p, ["home", "go"]) == ["A", "M"]
        assert m.phrase_match(p, ["go", "go", "go"]) == []
        assert m.phrase_match(p, ["absent"]) == []
        assert m.phrase_match(p, []) == []
        assert m.build_postings(dict(reversed(list(docs.items())))) == p
        return {"phrase_cases": 6, "exact_parity": True}
    if chapter == 6:
        docs = {"a": ["red", "red", "blue"], "b": ["red", "green"], "c": ["green"]}
        r = m.tfidf_score(["red", "blue", "blue"], docs, "a")
        x, y = math.log(3/2), math.log(3)
        assert r["df"] == {"blue": 1, "green": 2, "red": 2}
        assert r["document_tf"]["red"] == 2 and r["query_tf"]["blue"] == 2
        near(r["idf"]["red"], x); near(r["document_weights"]["red"], 2*x)
        near(r["query_weights"]["blue"], y)
        near(r["document_norm"], math.sqrt(4*x*x+y*y))
        near(r["query_norm"], math.sqrt(x*x+y*y))
        near(r["score"], (2*x*x+y*y)/(math.sqrt(x*x+y*y)*math.sqrt(4*x*x+y*y)))
        near(m.tfidf_score(["unseen"], docs, "a")["score"], 0)
        near(m.tfidf_score(["common"], {"a": ["common"], "b": ["common"]}, "a")["score"], 0)
        return {"tf_df_idf_norm_score_checked": True, "zero_norm_policy_checked": True}
    if chapter == 7:
        docs = {"a": ["red", "red", "blue"], "b": ["red", "green"], "c": ["green"]}
        for k1, b in ((.8, 0), (1.2, .75), (2, 1)):
            # Hand fixture N=3, avgdl=2, dl=3; query repeats count once.
            expected = math.log(1.6)*2*(k1+1)/(2+k1*(1-b+b*1.5))
            expected += math.log(8/3)*(k1+1)/(1+k1*(1-b+b*1.5))
            near(m.bm25_score(["red", "red", "blue", "absent"], docs, "a", k1, b), expected)
        near(m.bm25_score(["absent"], docs, "a"), 0)
        try:
            m.bm25_score(["red"], docs, "a", b=1.1)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid b accepted")
        return {"complete_score_cases": 4, "query_tf_policy": "distinct terms"}
    if chapter == 8:
        rng = random.Random(810)
        for trial in range(24):
            values = {f"d{i:02d}": rng.randrange(10)/2 for i in range(12)}
            bounds = [(i, value + rng.randrange(3)/2) for i, value in values.items()]
            observed = []
            def score(i):
                observed.append(i)
                return values[i]
            for k in (1, 3, 12):
                observed.clear()
                r = m.safe_top_k(bounds, k, score)
                oracle = sorted(values.items(), key=lambda p: (-p[1], p[0]))[:k]
                assert r["ranking"] == oracle
                assert observed == r["scored_ids"]
                assert set(r["scored_ids"]) | set(r["skipped_ids"]) == set(values)
        r = m.safe_top_k([("z", 8), ("a", 4), ("b", 1)], 1, {"z": 4, "a": 4, "b": 1}.__getitem__)
        assert r["ranking"] == [("a", 4)] and r["skipped_ids"] == ["b"]
        return {"exact_parity_cases": 73, "safe_skip_and_tie_checked": True}
    if chapter == 14:
        postings = {"x": [("a", 3), ("private", 999)], "y": [("b", 2), ("a", 1)]}
        assert m.weighted_sparse_score({"x": 2, "y": .5}, postings, {"a", "b"}) == [("a", 6.5), ("b", 1)]
        score, grid, winners = m.maxsim([(1., 0.), (0., 1.)], [(0., -1.), (1., 0.), (0., 1.)])
        near(score, 2); assert grid == [[0., 1., 0.], [-1., 0., 1.]] and winners == [1, 2]
        score, _, winners = m.maxsim([(1., 0.)], [(1., 0.), (1., 0.)])
        near(score, 1); assert winners == [0]
        return {"eligible_weighted_accumulation": True, "maxsim_matrix_and_ties": True}
    if chapter == 15:
        docs = {"a": (1., .05), "b": (0., 1.), "c": (-1., 0.)}
        seeded = m.build_lsh(docs, seed=21, bits=4)
        assert seeded == m.build_lsh(docs, seed=21, bits=4)
        assert len(seeded["planes"]) == 4 and all(len(p) == 2 for p in seeded["planes"])
        index = m.build_lsh(docs, planes=[(0., 1.)])
        assert m.signature((1., -.01), index["planes"]) == (0,)
        hits = []
        for q in ((1., -.01), (1., .04)):
            oracle = sorted(docs, key=lambda i: (-sum(a*b for a,b in zip(q, docs[i]))/math.sqrt(sum(x*x for x in docs[i])), i))[0]
            r = m.lsh_search(index, docs, q, k=1)
            assert set(i for i, _ in r["ranking"]) <= set(r["candidate_ids"])
            hits.append(int(bool(r["ranking"]) and r["ranking"][0][0] == oracle))
        assert hits == [0, 1]
        return {"exact_neighbor_recall_at_1": sum(hits)/2, "empty_bucket_miss": True}
    if chapter == 16:
        centers = [(0., 0.), (2., 0.)]
        assert m.nearest_centroid([1., 0.], centers) == 0
        books = [[(0., 0.), (1., 0.)], [(0., 0.), (1., -1.)]]
        x, q = [.9, .2, 1.1, -.1], [.8, .3, .9, -.9]
        code = m.encode_subvectors(x, books)
        assert tuple(code) == (1, 1)
        near(m.adc_distance(q, code, books), .15)
        reconstructed = [1., 0., 1., -1.]
        near(m.adc_distance(q, code, books), sum((a-b)**2 for a,b in zip(q, reconstructed)))
        # Exact-neighbor miss caused by code compression, not coarse probing.
        book = [[(0., 0.), (1., 0.)]]
        a, b, q2 = [.49, 0.], [.99, 0.], [.55, 0.]
        exact = [sum((x-y)**2 for x,y in zip(q2,v)) for v in (a,b)]
        adc = [m.adc_distance(q2, m.encode_subvectors(v, book), book) for v in (a,b)]
        assert exact[0] < exact[1] and adc[0] > adc[1]
        return {"adc_matches_decoded_distance": True, "compression_miss_recall_at_1": 0,
                "absolute_distance_error": [abs(x-y) for x,y in zip(exact,adc)]}
    raise ValueError("Unsupported chapter")


def main(chapter, default):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--implementation", type=Path, default=default)
    args = parser.parse_args()
    print(check(chapter, load(args.implementation)))
