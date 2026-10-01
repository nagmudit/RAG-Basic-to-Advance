"""Separate worked answer: attempt the learner task first. Standard library only."""

import math
from collections import Counter


def tfidf_score(query_terms, documents, doc_id):
    # Same raw TF and ln(N/DF) convention as Chapter 6, no smoothing.
    vocabulary = sorted({term for tokens in documents.values() for term in tokens} | set(query_terms))
    df = {term: sum(term in tokens for tokens in documents.values()) for term in vocabulary}
    idf = {term: math.log(len(documents)/df[term]) if df[term] else 0.0 for term in vocabulary}
    query_tf, document_tf = Counter(query_terms), Counter(documents[doc_id])
    query_weights = {term: int(term in query_tf)*idf[term] for term in vocabulary}
    document_weights = {term: document_tf[term]*idf[term] for term in vocabulary}
    query_norm = math.sqrt(sum(v*v for v in query_weights.values()))
    document_norm = math.sqrt(sum(v*v for v in document_weights.values()))
    score = (sum(query_weights[t]*document_weights[t] for t in vocabulary)/(query_norm*document_norm)
             if query_norm and document_norm else 0.0)
    return dict(df=df, idf=idf, query_tf=dict(query_tf), document_tf=dict(document_tf),
                query_weights=query_weights, document_weights=document_weights,
                query_norm=query_norm, document_norm=document_norm, score=score)
