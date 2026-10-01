"""Separate worked answer: attempt the learner task first. Standard library only."""

def build_postings(documents):
    postings = {}
    for doc_id, tokens in sorted(documents.items()):
        for position, term in enumerate(tokens):
            postings.setdefault(term, {}).setdefault(doc_id, []).append(position)
    return {term: postings[term] for term in sorted(postings)}


def phrase_match(postings, phrase):
    if not phrase:
        return []
    candidates = set(postings.get(phrase[0], {}))
    for term in phrase[1:]:
        candidates &= set(postings.get(term, {}))
    return sorted(doc for doc in candidates if any(
        all(start + offset in postings[term][doc] for offset, term in enumerate(phrase))
        for start in postings[phrase[0]][doc]))
