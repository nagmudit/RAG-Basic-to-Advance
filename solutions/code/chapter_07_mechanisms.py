"""Separate worked answer: attempt the learner task first. Standard library only."""

import math
from collections import Counter


def bm25_score(query_terms, documents, doc_id, k1=1.2, b=.75):
    if not math.isfinite(k1) or k1 <= 0 or not math.isfinite(b) or not 0 <= b <= 1:
        raise ValueError("Invalid BM25 controls")
    n = len(documents)
    avgdl = sum(map(len, documents.values()))/n
    dl = len(documents[doc_id])
    counts = Counter(documents[doc_id])
    total = 0.0
    for term in sorted(set(query_terms)):
        tf = counts[term]
        if not tf:
            continue
        df = sum(term in tokens for tokens in documents.values())
        idf = math.log1p((n-df+.5)/(df+.5))
        total += idf * tf*(k1+1)/(tf+k1*(1-b+b*dl/avgdl))
    return total
