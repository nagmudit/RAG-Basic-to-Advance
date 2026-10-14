"""Bounded representation admission, score-free interleaving and task readiness."""
import math
import re
from query_ch23 import normalize, ID
from retrieval_ch23 import digest, sha

POLICY = 'ch24-anchor-admission-1'


def lock_for(request, plan, authority, contract):
    return digest({'original': request['text'], 'predicate': plan['predicate'],
                   'as_of': plan['as_of_ms'], 'principal': request['principal'],
                   'authority': authority.state_digest(), 'model_contract': contract,
                   'policy': POLICY})


def atoms(text):
    return {'ids': set(re.findall(ID.pattern, text, re.I)),
            'entities': set(re.findall(r'\b(?:Orion|Green)\b', text, re.I)),
            'numbers': set(re.findall(r'(?<!\w)\d+(?!\w)', text))}


def admit(original, proposals, lock, *, max_branches=3, max_words=128):
    """Original reserves branch zero. No qrels, vectors or answer model is read."""
    if type(max_branches) is not int or max_branches < 1 or type(max_words) is not int or max_words < 1:
        raise ValueError('Invalid admission budget')
    surface = normalize(original)
    if len(surface.split()) > max_words:
        raise ValueError('Original exceeds admission budget')
    selected = [{'branch_id': 'original', 'text': surface, 'kind': 'original'}]
    seen = {surface.casefold()}; used = len(surface.split()); decisions = []
    protected = atoms(surface)
    protected['entities'] = {e.casefold() for e in protected['entities']}
    proposal_ids = [p['branch_id'] for p in proposals]
    if len(set(proposal_ids)) != len(proposal_ids) or 'original' in proposal_ids:
        raise ValueError('Duplicate/reserved branch identity')
    for p in proposals:
        text = normalize(p['text']); key = text.casefold(); a = atoms(text)
        a['entities'] = {e.casefold() for e in a['entities']}
        reason = ('anchor_mismatch' if p['lock'] != lock else
                  'protected_atom_change' if any(a[k] - protected[k] for k in a) else
                  'duplicate' if key in seen else
                  'branch_budget' if len(selected) >= max_branches else
                  'word_budget' if used + len(text.split()) > max_words else None)
        decisions.append({'branch_id': p['branch_id'], 'text_sha256': sha(text.encode()),
                          'accepted': reason is None, 'reason': reason})
        if reason is None:
            selected.append({**p, 'text': text}); seen.add(key); used += len(text.split())
    return selected, decisions


def interleave(branches, cap=2):
    """First occurrence owns the score; scores are never compared across branches."""
    if type(cap) is not int or cap < 1:
        raise ValueError('Invalid candidate cap')
    if len({b for b, _ in branches}) != len(branches):
        raise ValueError('Duplicate branch identity')
    admitted = []; owners = []; seen = set()
    for rank in range(max((len(rows) for _, rows in branches), default=0)):
        for branch, rows in branches:
            if rank >= len(rows):
                continue
            item, score = rows[rank]
            if item not in seen:
                seen.add(item); admitted.append((item, score)); owners.append(branch)
    return admitted[:cap], admitted, owners[:cap], owners


def ready_tasks(dependencies, completed, failed):
    """Validate a DAG, then expose ready and permanently blocked task IDs."""
    ids = set(dependencies)
    if set(completed) & set(failed) or not (set(completed) | set(failed)) <= ids:
        raise ValueError('Invalid task state')
    if any(not set(deps) <= ids for deps in dependencies.values()):
        raise ValueError('Missing dependency')
    remaining = {n: set(ds) for n, ds in dependencies.items()}; visited = set()
    while remaining:
        layer = {n for n, ds in remaining.items() if ds <= visited}
        if not layer:
            raise ValueError('Dependency cycle')
        visited |= layer
        remaining = {n: ds for n, ds in remaining.items() if n not in layer}
    blocked = set(failed)
    while True:
        expanded = blocked | {n for n, ds in dependencies.items() if set(ds) & blocked}
        if expanded == blocked:
            break
        blocked = expanded
    pending = ids - set(completed) - blocked
    return sorted(n for n in pending if set(dependencies[n]) <= set(completed)), sorted(blocked)


def rocchio(query, positives, negatives=(), alpha=1., beta=.5, gamma=.25):
    """An explicit normalized centroid update; no feedback is fetched here."""
    if not query or any(len(v) != len(query) for v in (*positives, *negatives)):
        raise ValueError('Vector shape mismatch')
    if any(not math.isfinite(float(x)) for v in (query, *positives, *negatives) for x in v):
        raise ValueError('Nonfinite feedback')
    if any(not math.isfinite(x) or x < 0 for x in (alpha, beta, gamma)):
        raise ValueError('Invalid coefficient')
    p = [sum(v[j] for v in positives)/len(positives) if positives else 0 for j in range(len(query))]
    n = [sum(v[j] for v in negatives)/len(negatives) if negatives else 0 for j in range(len(query))]
    result = [alpha*q + beta*a - gamma*b for q, a, b in zip(query, p, n)]
    norm = math.sqrt(sum(x*x for x in result))
    if norm == 0:
        raise ValueError('Zero feedback vector')
    return [x/norm for x in result]
