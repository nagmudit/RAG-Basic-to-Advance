"""Frozen representation ablation; prepare real vectors, preserve all branch pools."""
import argparse
import json
import math
import platform
import random
import unicodedata
from pathlib import Path
from time import perf_counter_ns

from retrieval_ch24 import (HERE, ROOT, WORKLOAD, CONTROL, MODES, load_sources,
    load_labels, proposals_for, execute, Generation, VersionStore, Principal,
    authorized_view, versions, TraceCollector, manifest, digest, sha)
from query_ch23 import interpret
from reformulate_ch24 import ready_tasks
from experiment_ch21 import load_encoder, embed, MODEL_REVISION


def average(rows, key):
    values = [r[key] for r in rows if r[key] is not None]
    return sum(values)/len(values) if values else None


def percentile(values, p):
    return sorted(values)[math.ceil(p*len(values))-1]


def scheduler_controls(corpus):
    collector = TraceCollector(CONTROL, versions(corpus, 'ch24-four-task-scheduler-controls-v1', None, None, None), [])
    cases = [
        ('budget', {'retry': [], 'trust': [], 'combine': ['retry', 'trust']}, set(), 2),
        ('failed-dependency', {'retry': [], 'trust': [], 'combine': ['retry', 'trust']}, {'retry'}, 2),
        ('cycle', {'retry': ['trust'], 'trust': ['retry']}, set(), 2),
        ('missing-dependency', {'retry': ['absent']}, set(), 2)]
    for i, (name, deps, failed, budget) in enumerate(cases):
        tick = perf_counter_ns(); done = set(); events = []; status = 'ok'; reason = None
        try:
            for step in range(budget):
                ready, blocked = ready_tasks(deps, done, failed)
                events.append({'step': step, 'ready': ready, 'blocked': blocked, 'completed': sorted(done)})
                if not ready: break
                # This marks abstract control tasks complete, not retrieved evidence.
                done.add(ready[0])
            ready, blocked = ready_tasks(deps, done, failed)
            status = 'partial' if len(done) != len(deps) else 'ok'
            reason = 'dependency_failed' if blocked else 'step_budget' if ready else None
        except ValueError:
            ready = []; blocked = []; status = 'invalid'; reason = 'invalid_dependency_graph'
        frame = collector.record('scheduler-'+str(i+1), name, 0, ([], {}),
            {'schedule': (perf_counter_ns()-tick)/1e6}, status=status, reason=reason)
        frame.update(task_events=events, ready_task_ids=ready, blocked_task_ids=blocked,
            completed_task_ids=sorted(done), step_budget=budget, abstract_control_only=True,
            stages_not_run=['retrieval', 'encoding', 'context', 'generation'])
    return collector.records


def restore_snapshot(path, expected_digest, capsules, authority, labels):
    payload = json.loads(path.read_text('utf-8'))
    if digest(payload) != expected_digest:
        raise ValueError('Untrusted Chapter24 snapshot')
    if payload['source_manifest_sha256'] != digest(manifest(capsules)) or payload['authority'] != authority.payload() or payload['query_manifest_sha256'] != labels['query_manifest_sha256'] or payload['drafts_digest'] != labels['drafts_digest']:
        raise ValueError('Changed evidence/query/draft snapshot')
    generation = Generation('ch24-current-body', authority, 'body', {'body': payload['body_vectors']}, capsules)
    if generation.identity != payload['generation_identity'] or generation.contract != payload['model_contract']:
        raise ValueError('Snapshot index/model mismatch')
    return payload, generation


def run(output, artifacts):
    capsules, authority, old = load_sources(); labels, drafts = load_labels(capsules, authority)
    model, info = load_encoder(allow_download=False)
    if model.max_seq_length != 256 or model.tokenizer.num_special_tokens_to_add(pair=False) != 2:
        raise ValueError('Encoder contract changed')
    def count(text):
        length = len(model.tokenizer(text, truncation=False)['input_ids'])
        if length > 256: raise ValueError('Refuse input truncation')
        return length
    new_keys = sorted(set(capsules) - set(old.capsules))
    body_bank = dict(old.bank['body'])
    build_texts = [capsules[k]['unit']['text'] for k in new_keys]
    for text in build_texts: count(text)
    tick = perf_counter_ns(); vectors = embed(model, build_texts, batch_size=10)
    build_ms = (perf_counter_ns()-tick)/1e6
    body_bank.update({k: list(v) for k, v in zip(new_keys, vectors)})
    generation = Generation('ch24-current-body', authority, 'body', {'body': body_bank}, capsules)
    ids = versions(labels['corpus_version'], labels['query_set_version'], labels['qrels_version'], generation.identity, MODEL_REVISION)
    build_sample = TraceCollector(WORKLOAD, ids, []).record('index-build', 'encode_new_bodies', 0, ([], {}), {'document_encode': build_ms}, status='ok')
    build_sample.update(new_capsule_keys=new_keys, input_wordpieces_with_specials=[count(t) for t in build_texts], privileged_indexing=True)
    inputs = {}; encoding_samples = []
    for q in labels['queries']:
        plan = interpret(q['text'], clock_ms=5300)
        principal = Principal(q['principal']['tenant'], frozenset(q['principal']['roles']))
        view = authorized_view(generation, authority, principal, plan['as_of_ms'])
        needed = {}
        if plan['outcome'] in ('ready', 'partial') and view.select(plan['predicate']):
            for mode in MODES:
                branches, _ = proposals_for(q, plan, drafts['queries'][q['query_id']], mode, authority, generation.contract)
                for b in branches: needed[b['branch_id']] = b
        inputs[q['query_id']] = {}
        for branch_id, branch in needed.items():
            wp = count(branch['text']); tick = perf_counter_ns()
            vector = list(embed(model, [branch['text']], batch_size=1)[0])
            elapsed = (perf_counter_ns()-tick)/1e6
            frame = TraceCollector(WORKLOAD, ids, []).record(q['query_id'], 'prepare_input', 0, ([], {}), {'query_encode': elapsed}, status='ok')
            frame.update(branch_id=branch_id, input_sha256=sha(branch['text'].encode()), input_wordpieces_with_specials=wp)
            encoding_samples.append(frame)
            inputs[q['query_id']][branch_id] = {'text_sha256': frame['input_sha256'], 'vector': vector,
                'wordpieces_with_specials': wp, 'encoding_request_id': frame['request_id']}
    tokens = {item: len(model.tokenizer(row['text'], add_special_tokens=False)['input_ids']) for item, row in generation.rows.items()}
    observations = []; samples = []; rng = random.Random(24014)
    for trial in range(3):
        cases = [(q, mode) for q in labels['queries'] for mode in MODES]; rng.shuffle(cases)
        for q, mode in cases:
            ranked, packed, plan, parent, frames = execute(q, drafts['queries'][q['query_id']], mode, trial, generation, authority,
                inputs[q['query_id']], tokens, ids, query_contract=generation.contract)
            required = {r['item_id'] for r in q['requirements']}
            union = {i for b in parent['branch_shortlists'] for i in b['ids']}
            final = {i for i,_ in ranked}; context = {p['item_id'] for p in packed}
            branch_hits = {b['branch_id']: sorted(required & set(b['ids'])) for b in parent['branch_shortlists']}
            observations.append({'query_id': q['query_id'], 'mode': mode, 'trial_id': trial, 'slice': q['slice'],
                'request_id': parent['request_id'], 'union_recall': len(required & union)/len(required) if required else None,
                'positive_recall_at_2': len(required & final)/len(required) if required else None,
                'context_evidence_recall': len(required & context)/len(required) if required else None,
                'required_empty_correct': not final if q['required_empty'] else None,
                'guard_decision_correct': plan['outcome'] == q['expected_outcome'] if q['guard'] else None,
                'expected_intent_outcome_correct': plan['outcome'] == q['expected_outcome'],
                'branch_hits': branch_hits, 'branch_count': len(parent['branch_request_ids']),
                'input_wordpieces_charged': parent['input_wordpieces_charged'],
                'scored_pairs': len(parent['raw_candidate_ids']), 'final_ids': [i for i,_ in ranked],
                'context_ids': parent['context_ids'], 'status': parent['status'], 'reason': parent['reason'], **parent['stage_timings_ms']})
            samples.extend(frames)
    aggregates = {}
    for mode in MODES:
        rows = [o for o in observations if o['mode'] == mode]
        aggregates[mode] = {key: average(rows, key) for key in ('union_recall', 'positive_recall_at_2', 'context_evidence_recall', 'required_empty_correct', 'guard_decision_correct', 'expected_intent_outcome_correct', 'branch_count', 'input_wordpieces_charged', 'scored_pairs')}
        aggregates[mode].update(requests=len(rows), dense_search_p50_ms=percentile([o['dense_search_total'] for o in rows], .5),
            dense_search_p95_ms=percentile([o['dense_search_total'] for o in rows], .95),
            context_timed_requests=sum('context' in o for o in rows),
            per_positive_query={o['query_id']: {'union': o['union_recall'], 'final': o['positive_recall_at_2'], 'context': o['context_evidence_recall']} for o in rows if o['positive_recall_at_2'] is not None})
    payload = {'source_manifest_sha256': labels['source_manifest_sha256'], 'authority': authority.payload(),
        'generation_identity': generation.identity, 'model_contract': generation.contract, 'query_manifest_sha256': labels['query_manifest_sha256'],
        'drafts_digest': labels['drafts_digest'], 'body_vectors': body_bank, 'inputs': inputs, 'token_counts': tokens}
    artifacts.mkdir(parents=True, exist_ok=True); path = artifacts/'snapshot.json'
    path.write_bytes((json.dumps(payload, indent=2, sort_keys=True)+'\n').encode())
    snapshot_digest = digest(payload); restored, replay_gen = restore_snapshot(path, snapshot_digest, capsules, authority, labels)
    replays = 0
    for q in labels['queries']:
        for mode in MODES:
            _, _, _, parent, _ = execute(q, drafts['queries'][q['query_id']], mode, -1, replay_gen, authority,
                restored['inputs'][q['query_id']], restored['token_counts'], ids, query_contract=restored['model_contract'])
            first = next(o for o in observations if o['query_id'] == q['query_id'] and o['mode'] == mode)
            original = next(s for s in samples if s['request_id'] == first['request_id'])
            for field in ('raw_candidate_ids', 'raw_candidate_scores', 'intermediate_candidate_ids', 'intermediate_candidate_scores', 'final_candidate_ids', 'final_candidate_scores', 'context_ids', 'raw_branch_ids', 'admission_branch_ids', 'final_origin_branch_ids'):
                if parent[field] != original[field]: raise ValueError('Replay stage/score/provenance mismatch')
            replays += 1
    record = {'workload_id': WORKLOAD, 'authoring_date': '2026-10-14',
        'question': 'Can bounded alternative representations find required source evidence without losing original constraints or hiding work?',
        'hypothesis': 'Some paraphrases may recover candidates; more branches can still tie, crowd out evidence or increase cost. A wrong hypothetical passage can lose to the original.',
        'baseline': 'Interpreted original surface, exact authorized dense retrieval; dense held fixed even for exact IDs to isolate representation. This is not a full Chapter23 route-policy comparison.',
        'independent_variable': 'Original versus original plus at most two paraphrases versus one author-written hypothetical passage (original fallback on admission rejection).',
        'controls': 'Same 28 source/version capsules, authority, interpreted constraints, frozen backbone/body input, branch depth2, stable round-robin admission, globalcap2, context80 encoder-WordPiece proxy, original questions and judgments.',
        'procedure': 'Drafts frozen before encoding/ranking. One author knows authored sources; no language model or query rewriting training. Three warm repeats in shuffled seed24014 order with prepared vectors; no train/dev/test/generalization/zero-shot claim.',
        'versions': ids, 'model': info, 'source_manifest_sha256': labels['source_manifest_sha256'], 'query_manifest_sha256': labels['query_manifest_sha256'],
        'drafts_digest': labels['drafts_digest'], 'qrels_sha256': sha((HERE/'qrels_ch24.json').read_bytes()), 'snapshot_digest': snapshot_digest,
        'code_sha256': {p: sha((HERE/p).read_bytes()) for p in ('reformulate_ch24.py', 'retrieval_ch24.py', 'experiment_ch24.py')},
        'environment': {'python': platform.python_version(), 'unicode_database': unicodedata.unidata_version, 'platform': platform.platform()},
        'aggregates': aggregates, 'per_query_trials': observations, 'samples': samples,
        'encoding_samples': encoding_samples, 'index_build_samples': [build_sample],
        'scheduler_controls': {'workload_id': CONTROL, 'samples': scheduler_controls(labels['corpus_version'])}, 'replay_checks': replays,
        'decision': 'Preserve all paired results, especially failed hypotheses and cap/packing losses. Alternative representations remain experimental; no claim of automatic improvement.',
        'limitations': 'Small author-written fictional workload, source-aware drafts, non-exhaustive span targets, closed English parser, exact small corpus, prepared query vectors, three warm repeats. No generator, calibrated score fusion, reranker, real dependency-driven retrieval, service latency or generated answer evaluation. Same-topic semantic drift can pass atom checks; original duration false trigger persists.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((json.dumps(record, ensure_ascii=False, indent=2)+'\n').encode())
    print(json.dumps({'workload': WORKLOAD, 'aggregates': aggregates, 'samples': len(samples), 'encodes': len(encoding_samples), 'replays': replays}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE/'chapter-24-experiment.json')
    parser.add_argument('--artifacts', type=Path, default=HERE/'index_ch24')
    args = parser.parse_args(); run(args.output, args.artifacts)
