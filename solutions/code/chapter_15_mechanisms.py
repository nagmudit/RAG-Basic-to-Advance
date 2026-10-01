"""Separate worked answer: attempt the learner task first. Standard library only."""

import math
import random


def signature(vector, planes):
    return tuple(int(sum(a*b for a, b in zip(vector, plane)) >= 0) for plane in planes)


def build_lsh(documents, *, seed=15, bits=3, planes=None):
    dimension = len(next(iter(documents.values())))
    if dimension < 1 or bits < 1 or any(len(v) != dimension for v in documents.values()):
        raise ValueError("Invalid dimensions or bit count")
    rng = random.Random(seed)
    if planes is None:
        planes = [tuple(rng.gauss(0, 1) for _ in range(dimension)) for _ in range(bits)]
    if not planes or any(len(p) != dimension for p in planes):
        raise ValueError("Invalid planes")
    buckets = {}
    for item_id, vector in sorted(documents.items()):
        buckets.setdefault(signature(vector, planes), []).append(item_id)
    return dict(planes=planes, buckets=buckets)


def lsh_search(index, documents, query, k=2):
    if k < 1 or not query or not all(math.isfinite(x) for x in query) or not any(query):
        raise ValueError("Invalid query or k")
    if len(query) != len(index['planes'][0]):
        raise ValueError("Query dimension mismatch")
    candidates = index['buckets'].get(signature(query, index['planes']), [])
    qnorm = math.sqrt(sum(x*x for x in query))
    scored = []
    for item_id in candidates:
        vector = documents[item_id]
        norm = math.sqrt(sum(x*x for x in vector))
        if norm == 0:
            raise ValueError("Zero indexed vector")
        scored.append((item_id, sum(a*b for a,b in zip(query, vector))/(qnorm*norm)))
    return dict(candidate_ids=list(candidates), ranking=sorted(scored, key=lambda p: (-p[1], p[0]))[:k])
