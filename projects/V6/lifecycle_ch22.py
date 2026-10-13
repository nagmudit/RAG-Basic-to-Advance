"""Revision-aware local projection and compatible index generations.

Single-process, trusted fixture events. No broker/CDC/authentication service.
Historical access intersects current grants; deletion blocks every read route.
"""
import copy
import json
import math
import os
from pathlib import Path
from metadata_ch21 import MetadataIndex, authorized, score_rows
from experiment_ch21 import digest, MODEL_REVISION


def event_identity(event):
    required = ('source_id', 'revision', 'effective_ms', 'op', 'capsule_key', 'payload_digest')
    if not isinstance(event.get('event_id'), str) or not event['event_id']:
        raise ValueError('Invalid event identity')
    if not isinstance(event.get('source_id'), str) or not event['source_id']:
        raise ValueError('Invalid source identity')
    if type(event.get('revision')) is not int or event['revision'] < 1 or type(event.get('effective_ms')) is not int or event['effective_ms'] < 0:
        raise ValueError('Invalid monotonic revision or effective time')
    if event.get('op') not in ('upsert', 'delete') or not isinstance(event.get('payload_digest'), str):
        raise ValueError('Invalid event payload')
    if (event['op'] == 'delete') != (event.get('capsule_key') is None):
        raise ValueError('Delete must have no live content pointer')
    return digest({key: event[key] for key in required})


class VersionStore:
    """Copy-on-commit heads/history/receipts; arrival baseline shares dedup rules."""
    def __init__(self, policy='ordered'):
        if policy not in ('ordered', 'arrival'):
            raise ValueError('Unknown ordering policy')
        self.policy = policy
        self.heads, self.history, self.receipts = {}, {}, {}
        self.transitions = []

    def apply(self, event, received_ms):
        identity = event_identity(event)
        if type(received_ms) is not int or received_ms < event['effective_ms']:
            raise ValueError('Invalid controlled receive clock')
        before = self.heads.get(event['source_id'])
        reason = 'accepted'
        if event['event_id'] in self.receipts:
            if self.receipts[event['event_id']] != identity:
                raise ValueError('Event-ID payload conflict')
            reason = 'duplicate_event'
        elif before and event['revision'] == before['revision']:
            if event_identity(before) != identity:
                raise ValueError('Same-revision payload conflict')
            reason = 'duplicate_revision'
        elif before and self.policy == 'ordered' and event['revision'] < before['revision']:
            reason = 'stale_revision'
        newest = max(self.history.get(event['source_id'], {}).values(), key=lambda e:e['revision'], default=None)
        if reason == 'accepted' and newest and event['revision'] > newest['revision'] and event['effective_ms'] < newest['effective_ms']:
            raise ValueError('Backdated correction needs a different temporal policy')
        # Stage all state before publishing it; exceptions leave old state.
        heads, history, receipts = copy.deepcopy(self.heads), copy.deepcopy(self.history), dict(self.receipts)
        receipts[event['event_id']] = identity
        if reason == 'accepted':
            prior_versions = history.get(event['source_id'], {})
            previous_same = prior_versions.get(str(event['revision']))
            if previous_same and event_identity(previous_same) != identity:
                raise ValueError('Historical revision conflict')
            history.setdefault(event['source_id'], {})[str(event['revision'])] = copy.deepcopy(event)
            heads[event['source_id']] = copy.deepcopy(event)
        transition = {'event_id': event['event_id'], 'source_id': event['source_id'],
                      'incoming_revision': event['revision'], 'before_revision': before['revision'] if before else None,
                      'after_revision': heads[event['source_id']]['revision'], 'reason': reason,
                      'received_ms': received_ms, 'source_effective_ms': event['effective_ms']}
        self.heads, self.history, self.receipts = heads, history, receipts
        self.transitions.append(transition)
        return transition

    def selected(self, source_id, as_of=None):
        if as_of is None:
            return self.heads.get(source_id)
        if type(as_of) is not int or as_of < 0:
            raise ValueError('Invalid as-of clock')
        candidates = [event for event in self.history.get(source_id, {}).values() if event['effective_ms'] <= as_of]
        return max(candidates, key=lambda e: (e['effective_ms'], e['revision'])) if candidates else None

    def payload(self):
        return {'policy': self.policy, 'heads': self.heads, 'history': self.history,
                'receipts': self.receipts, 'transitions': self.transitions}

    def state_digest(self):
        return digest({'heads': self.heads, 'history': self.history})

    @classmethod
    def restore(cls, payload):
        obj = cls(payload['policy'])
        for key in ('heads', 'history', 'receipts', 'transitions'):
            setattr(obj, key, copy.deepcopy(payload[key]))
        for event in obj.heads.values():
            event_identity(event)
            if obj.history[event['source_id']][str(event['revision'])] != event:
                raise ValueError('Head/history contradiction')
        return obj


def contract(policy):
    if policy not in ('body', 'entity-body'):
        raise ValueError('Unknown encoding policy')
    return {'model_revision': MODEL_REVISION, 'dimension': 384, 'metric': 'cosine-normalized-dot',
            'normalization': 'unit-l2-float32', 'input_policy': policy}


def encoding_input(text, entity, policy):
    return text if policy == 'body' else 'Entity: '+entity+'\n'+text


def current_allowed(authority, source, principal, capsules):
    head = authority.heads.get(source)
    if not head or head['op'] == 'delete':
        return False
    return authorized(capsules[head['capsule_key']]['unit'], principal)


class Generation:
    def __init__(self, name, store, policy, bank, capsules):
        self.name, self.contract = name, contract(policy)
        self.store = VersionStore.restore(store.payload())
        self.bank, self.capsules = bank, capsules  # privileged immutable artifacts
        self.rows = {}
        self.sync(store)

    def sync(self, store):
        candidate = VersionStore.restore(store.payload())
        rows = {}
        for versions in candidate.history.values():
            for event in versions.values():
                if event['op'] == 'delete':
                    continue
                key = event['capsule_key']
                capsule = self.capsules[key]
                if digest(capsule) != event['payload_digest']:
                    raise ValueError('Changed source capsule')
                if capsule['unit']['source_id'] != event['source_id'] or capsule['unit']['source_version'] != str(event['revision']) or capsule['unit']['metadata']['version'] != event['revision']:
                    raise ValueError('Source/revision/capsule contradiction')
                vector = self.bank[self.contract['input_policy']][key]
                if len(vector) != 384 or any(not math.isfinite(x) for x in vector) or abs(sum(x*x for x in vector)-1) > .0001:
                    raise ValueError('Invalid normalized vector')
                row = {**capsule['unit'], 'vector': vector, 'effective_ms': event['effective_ms']}
                rows[row['item_id']] = row
        identity = digest({'name': self.name, 'state': candidate.state_digest(), 'contract': self.contract, 'rows': rows})
        self.store, self.rows, self.identity = candidate, rows, identity

    def query(self, query, query_contract, principal, authority, source, as_of=None):
        # Contract rejection and current policy occur before vector/body access.
        if query_contract != self.contract:
            raise ValueError('Embedding contract mismatch')
        if not current_allowed(authority, source, principal, self.capsules):
            return [], {'candidate_stages': {'scored': [], 'shortlist': [], 'freshness_barrier': []},
                        'reason': 'no_authorized_candidates', 'known_pending': False}
        selected = self.store.selected(source, as_of)
        truth = authority.selected(source, as_of)
        if not selected or selected['op'] == 'delete':
            return [], {'candidate_stages': {'scored': [], 'shortlist': [], 'freshness_barrier': []},
                        'reason': 'not_materialized', 'known_pending': True}
        key = selected['capsule_key']
        unit = self.capsules[key]['unit']
        view = MetadataIndex([self.rows[unit['item_id']]], principal)
        scored = score_rows(view, view.select({'record_id': source}), query)
        # Known source revision barrier: stale candidates are observable but
        # never fetched into evidence/context for a requested current/as-of task.
        matches_truth = truth and truth['op'] != 'delete' and truth['payload_digest'] == selected['payload_digest']
        final = scored[:1] if matches_truth else []
        return final, {'candidate_stages': {'scored': scored, 'shortlist': scored[:1], 'freshness_barrier': final},
                       'reason': None if final else 'known_revision_pending', 'known_pending': not bool(matches_truth)}

    def publish(self, store, event, received_ms):
        transition = store.apply(event, received_ms)
        before = self.identity
        # A receipt can commit before index publication fails. Retry must
        # reconcile that pending index even when the event is a duplicate.
        if self.store.state_digest() != store.state_digest():
            self.sync(store)
        return transition, self.identity != before


class Migration:
    """One-process compare-and-swap alias; gate data, not just index names."""
    def __init__(self, active):
        self.active, self.generations, self.events = active.name, {active.name: active}, []

    def add(self, generation):
        if generation.name in self.generations:
            raise ValueError('Generation name collision')
        self.generations[generation.name] = generation

    def cutover(self, expected_active, target, authoritative_store):
        if self.active != expected_active:
            raise ValueError('Alias compare-and-swap failed')
        proposed = self.generations[target]
        if proposed.store.state_digest() != authoritative_store.state_digest():
            self.events.append({'from': self.active, 'to': target, 'status': 'rejected', 'reason': 'head_or_history_mismatch'})
            return False
        # sync validates all source, metadata, vector and contract coverage.
        proposed.sync(proposed.store)
        self.events.append({'from': self.active, 'to': target, 'status': 'accepted', 'reason': 'validated_cutover'})
        self.active = target
        return True


class ResultCache:
    def __init__(self):
        self.entries = {}

    def key(self, principal, authority, generation, query_id, as_of):
        return (principal.tenant, tuple(sorted(principal.roles)), principal.policy_version,
                authority.state_digest(), generation.identity, digest(generation.contract), query_id, as_of)

    def get(self, key, generation, principal, authority):
        current = (principal.tenant, tuple(sorted(principal.roles)), principal.policy_version,
                   authority.state_digest(), generation.identity, digest(generation.contract))
        if key[:6] != current:
            return None
        cached = self.entries.get(key)
        if cached is None:
            return None
        for item, _ in cached:
            row = generation.rows.get(item)
            if row is None or not current_allowed(authority, row['source_id'], principal, generation.capsules) or not authorized(row, principal):
                raise ValueError('Cached eligibility violation')
        return copy.deepcopy(cached)

    def put(self, key, ranked):
        self.entries[key] = copy.deepcopy(ranked)


def atomic_checkpoint(path, payload):
    """Replace one local file; no distributed or universal crash-durability claim."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')
    temporary = path.with_suffix(path.suffix+'.new')
    with temporary.open('wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return digest(payload)


def load_checkpoint(path, expected_digest):
    payload = json.loads(Path(path).read_text('utf-8'))
    if digest(payload) != expected_digest:
        raise ValueError('Untrusted checkpoint')
    return payload
