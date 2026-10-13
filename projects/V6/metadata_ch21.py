"""Typed metadata, authorization-first set algebra, and exact filter plans.

Task postfilters operate ONLY inside an already authorized roster. This module
is a local fixture mechanism, not authentication or a production ACL service.
"""
import bisect
import copy
import math
from dataclasses import dataclass
from datetime import datetime, timezone

SCHEMA = 'ch21-metadata-1'
POLICY = 'ch21-role-intersection-1'
EXACT_FIELDS = ('record_id', 'tenant', 'owner', 'entity', 'language', 'version')
MODES = ('semantic', 'prefilter', 'post3', 'post9')


def instant(value):
    if not isinstance(value, str):
        raise ValueError('Timestamp must be an aware ISO string')
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('Invalid timestamp') from None
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError('Ambiguous naive timestamp')
    return stamp.astimezone(timezone.utc)


def validate_metadata(meta):
    if not isinstance(meta, dict):
        raise ValueError('Invalid metadata object')
    if meta.get('schema_version') != SCHEMA or meta.get('policy_version') != POLICY:
        raise ValueError('Unknown schema or policy')
    for key in ('record_id', 'tenant', 'owner', 'entity', 'parent_id'):
        if not isinstance(meta.get(key), str) or not meta[key]:
            raise ValueError('Missing typed identity')
    if type(meta.get('version')) is not int or meta['version'] < 1:
        raise ValueError('Invalid source version')
    if not isinstance(meta.get('acl_roles'), list) or not meta['acl_roles'] or any(
            not isinstance(r, str) or not r for r in meta['acl_roles']):
        raise ValueError('Missing explicit ACL')
    if len(set(meta['acl_roles'])) != len(meta['acl_roles']):
        raise ValueError('Duplicate role')
    if meta.get('language') is not None and (
            not isinstance(meta['language'], str) or not meta['language']):
        raise ValueError('Invalid optional language')
    confidence = meta.get('extraction_confidence')
    if type(confidence) not in (int, float) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError('Invalid extraction confidence')
    instant(meta.get('published_at'))
    instant(meta.get('updated_at'))
    return meta


@dataclass(frozen=True)
class Principal:
    tenant: str
    roles: frozenset
    policy_version: str = POLICY

    def __post_init__(self):
        if not isinstance(self.tenant, str) or not self.tenant or not isinstance(self.roles, frozenset) or not self.roles or any(
                not isinstance(r, str) or not r for r in self.roles) or self.policy_version != POLICY:
            raise ValueError('Invalid trusted principal')


def authorized(row, principal):
    # All accessed fields are policy metadata, never body/vector/locator.
    meta = row.get('metadata', {})
    try:
        validate_metadata(meta)
    except ValueError:
        return False
    return (row.get('indexing_allowed') is True and bool(row.get('license')) and
            meta['tenant'] == principal.tenant and
            bool(principal.roles.intersection(meta['acl_roles'])))


def validate_predicate(predicate):
    if not isinstance(predicate, dict) or set(predicate) - set(EXACT_FIELDS) - {'published_gte', 'published_lt'}:
        raise ValueError('Unknown predicate field')
    for key, value in predicate.items():
        if key == 'version':
            if type(value) is not int or value < 1:
                raise ValueError('Invalid exact version')
        elif key in EXACT_FIELDS:
            if not isinstance(value, str) or not value:
                raise ValueError('Invalid exact value; null is not a wildcard')
        else:
            instant(value)
    if 'published_gte' in predicate and 'published_lt' in predicate and instant(predicate['published_gte']) >= instant(predicate['published_lt']):
        raise ValueError('Invalid half-open interval')
    return predicate


def matches(meta, predicate):
    validate_predicate(predicate)
    for key, value in predicate.items():
        if key in EXACT_FIELDS and (meta.get(key) is None or meta.get(key) != value):
            return False
        if key == 'published_gte' and instant(meta['published_at']) < instant(value):
            return False
        if key == 'published_lt' and instant(meta['published_at']) >= instant(value):
            return False
    return True


class MetadataIndex:
    """Private per-principal view: exact postings plus sorted UTC instants."""
    def __init__(self, rows, principal):
        self.principal = principal
        self.rows = {}
        self.metadata_snapshot = {}
        self.postings = {}
        self.dates = []
        for row in rows:
            if not authorized(row, principal):
                continue
            item = row['item_id']
            if item in self.rows:
                raise ValueError('Duplicate eligible item identity')
            self.rows[item] = row
            meta = row['metadata']
            self.metadata_snapshot[item] = copy.deepcopy(meta)
            for key in EXACT_FIELDS:
                if meta.get(key) is not None:
                    self.postings.setdefault((key, meta[key]), set()).add(item)
            self.dates.append((instant(meta['published_at']), item))
        self.dates.sort()
        self.times = [stamp for stamp, _ in self.dates]

    def select(self, predicate):
        validate_predicate(predicate)
        for item, row in self.rows.items():
            if row['metadata'] != self.metadata_snapshot[item] or not authorized(row, self.principal):
                raise ValueError('Frozen metadata/policy view changed')
        sets = [self.postings.get((key, value), set()) for key, value in predicate.items() if key in EXACT_FIELDS]
        if 'published_gte' in predicate or 'published_lt' in predicate:
            lo = bisect.bisect_left(self.times, instant(predicate['published_gte'])) if 'published_gte' in predicate else 0
            hi = bisect.bisect_left(self.times, instant(predicate['published_lt'])) if 'published_lt' in predicate else len(self.dates)
            sets.append({item for _, item in self.dates[lo:hi]})
        result = set(self.rows)
        for subset in sorted(sets, key=len):
            result.intersection_update(subset)
        return result


def score_rows(view, ids, query):
    if len(query) != 384 or not all(math.isfinite(float(v)) for v in query):
        raise ValueError('Invalid query vector')
    scored = []
    for item in sorted(ids):
        row = view.rows[item]
        # Recheck before vector access; a view is not a revocation protocol.
        if not authorized(row, view.principal):
            raise ValueError('Eligibility changed; rebuild authorized view')
        vector = row['vector']
        if len(vector) != 384 or not all(math.isfinite(float(v)) for v in vector):
            raise ValueError('Invalid stored vector')
        scored.append((item, sum(float(a)*float(b) for a, b in zip(query, vector))))
    return sorted(scored, key=lambda pair: (-pair[1], pair[0]))


def search(view, predicate, query, mode, k=2):
    if mode not in MODES or type(k) is not int or k < 1:
        raise ValueError('Invalid search plan')
    eligible = view.select(predicate)
    pool = eligible if mode == 'prefilter' else set(view.rows)
    scored = score_rows(view, pool, query)
    depth = 3 if mode == 'post3' else 9 if mode == 'post9' else k
    shortlist = scored[:depth]
    filtered = shortlist if mode == 'semantic' else [(i, s) for i, s in shortlist if i in eligible]
    final = filtered[:k]
    reason = None if final else 'no_task_matches' if not eligible else 'shortlist_underfill'
    work = {'candidate_stages': {'scored': scored, 'shortlist': shortlist, 'task_survivors': filtered},
            'reason': reason, 'authorized_count': len(view.rows), 'task_count': len(eligible),
            'scored_count': len(scored), 'requested_k': k, 'shortlist_depth': depth,
            'underfilled': len(final) < min(k, len(eligible)) if mode != 'semantic' else None,
            'predicate_digest_input': predicate}
    return final, work


def graph_walk(adjacency, scores, task_ids, prune_task=False):
    """Exhaustive four-node public-task bridge demo, NOT HNSW/ANN timing.

    The adjacency/scores are entirely inside one authorized partition.
    Filtering transit vertices differs from filtering result membership.
    """
    frontier, seen, events, found = ['u'], set(), [], []
    while frontier:
        current = frontier.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if prune_task and current not in task_ids and current != 'u':
            events.append({'node': current, 'action': 'task_pruned', 'frontier': list(frontier)})
            continue
        score = scores[current]  # Actual preassigned-score lookup, not replay.
        if current in task_ids:
            found.append((current, score))
        frontier.extend(n for n in adjacency[current] if n not in seen)
        events.append({'node': current, 'action': 'expanded', 'score': score, 'frontier': list(frontier)})
    return sorted(found, key=lambda pair: (-pair[1], pair[0])), events
