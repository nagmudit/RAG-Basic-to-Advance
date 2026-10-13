"""Frozen versioned evidence, event-order comparison and dual-generation drill."""
import argparse
import json
import math
import platform
import random
from pathlib import Path
from time import perf_counter_ns
from datetime import datetime, timezone
import numpy as np
from experiment_ch21 import (HERE, ROOT, load_corpus, load_labels as load_ch21_labels,
    verify_snapshot, ingest, make_chunks, pack_context, digest, sha, locate_span,
    load_encoder, embed, MODEL_REVISION, Principal, authorized, TraceCollector, versions)
from lifecycle_ch22 import (VersionStore, Generation, Migration, ResultCache, contract,
    encoding_input, current_allowed, atomic_checkpoint, load_checkpoint)
from metadata_ch21 import validate_metadata

WORKLOAD = 'ch22-versioned-evidence-v1'
CORPUS = 'ch22-reviewed-version-capsules-v1'
QUERIES = 'ch22-ten-checkpoint-questions-v1'
QRELS = 'ch22-source-policy-time-bound-spans-v1'
EVENT_WORKLOAD = 'ch22-controlled-event-delivery-v1'
MIGRATION_WORKLOAD = 'ch22-compatible-generation-cutover-v1'


def capsule_key(source, revision):
    return source+'@'+str(revision)


def load_capsules(directory=None):
    docs, units, _ = load_corpus()
    load_ch21_labels(docs, units)
    original = json.loads((HERE/'index_ch21/index.json').read_text('utf-8'))
    checked = json.loads((HERE/'chapter-21-experiment.json').read_text('utf-8'))
    verify_snapshot(original, docs, units, checked['index_manifest_digest'])
    docmap = {d['source_id']: d for d in docs}
    capsules = {capsule_key(u['source_id'], 1): {'document': docmap[u['source_id']], 'unit': u} for u in units}
    directory = directory or HERE/'fixtures_ch22'
    descriptors = json.loads((directory/'updates.json').read_text('utf-8'))
    for source in descriptors:
        # Existing approval/scope gate precedes path/body reads.
        validate_metadata(source['metadata'])
        if source['metadata']['record_id'] != source['source_id'] or str(source['metadata']['version']) != source['source_version'] or set(source['allowed_scopes']) != {source['metadata']['tenant']+'-'+r for r in source['metadata']['acl_roles']}:
            raise ValueError('Update descriptor/policy contradiction')
        scope = source['allowed_scopes'][0]
        doc = ingest(directory, source, scope)
        if doc['status'] != 'accepted':
            raise ValueError('Changed update source quality')
        chunks = make_chunks(doc, 'structure48', scope)
        if len(chunks) != 1 or source['metadata']['record_id'] != source['source_id'] or str(source['metadata']['version']) != source['source_version']:
            raise ValueError('Changed update identity')
        unit = {**chunks[0], 'metadata': source['metadata'], 'metadata_digest': digest(source['metadata']),
                'license': doc['license'], 'indexing_allowed': doc['indexing_allowed']}
        key = capsule_key(source['source_id'], source['metadata']['version'])
        if key in capsules:
            raise ValueError('Duplicate version capsule')
        capsules[key] = {'document': doc, 'unit': unit}
    return capsules, original


def manifest(capsules):
    return [{'capsule_key': key, 'capsule_digest': digest(value), 'raw_sha256': value['document']['source_sha256'],
             'record_digest': value['document']['record_digest'], 'metadata_digest': value['unit']['metadata_digest']}
            for key, value in sorted(capsules.items())]


def upsert(capsules, source, revision, effective_ms, event_id):
    key = capsule_key(source, revision)
    return {'event_id': event_id, 'source_id': source, 'revision': revision, 'effective_ms': effective_ms,
            'op': 'upsert', 'capsule_key': key, 'payload_digest': digest(capsules[key])}


def schedule(capsules):
    seeds = [upsert(capsules, key.split('@')[0], 1, 0, 'seed-'+key) for key in sorted(capsules) if key.endswith('@1')]
    change2 = upsert(capsules, 'A06', 2, 1000, 'change-A06-2')
    delete = {'event_id': 'delete-A03-2', 'source_id': 'A03', 'revision': 2, 'effective_ms': 2000,
              'op': 'delete', 'capsule_key': None, 'payload_digest': digest({'delete': 'A03', 'revision': 2})}
    revoke = upsert(capsules, 'A08', 2, 3000, 'revoke-A08-2')
    change3 = upsert(capsules, 'A06', 3, 4000, 'change-A06-3')
    commits = [(1000, change2), (2000, delete), (3000, revoke), (4000, change3)]
    deliveries = [(1200, change2), (2600, delete), (3900, revoke), (4500, change3),
                  (5000, change2), (5100, upsert(capsules, 'A03', 1, 0, 'late-A03-1')),
                  (5200, upsert(capsules, 'A06', 1, 0, 'late-A06-1'))]
    return seeds, commits, deliveries


def load_labels(capsules, path=None, registry=None, updates=None):
    labels = json.loads((path or HERE/'qrels_ch22.json').read_text('utf-8'))
    actual = manifest(capsules)
    if labels['capsule_manifest'] != actual or labels['capsule_manifest_sha256'] != digest(actual) or labels['schedule_digest'] != digest(schedule(capsules)):
        raise ValueError('Review changed content/metadata/event-time judgments')
    if labels['updates_descriptor_sha256'] != sha(((updates or HERE/'fixtures_ch22')/'updates.json').read_bytes()):
        raise ValueError('Changed source origins or descriptor policy')
    for capsule in capsules.values():
        doc, unit = capsule['document'], capsule['unit']
        if digest({k: v for k, v in doc.items() if k != 'record_digest'}) != doc['record_digest'] or sha(doc['body'].encode('utf-8')) != doc['body_sha256'] or digest(unit['metadata']) != unit['metadata_digest']:
            raise ValueError('Changed canonical map or metadata')
    for q in labels['queries']:
        truth = VersionStore(); seeds, commits, _ = schedule(capsules)
        for event in seeds: truth.apply(event, 0)
        for clock,event in commits:
            if clock<=q['checkpoint_ms']:truth.apply(event,clock)
        principal = Principal(q['principal']['tenant'],frozenset(q['principal']['roles']))
        selected = truth.selected(q['source_id'],q['as_of_ms'])
        expected_key = (selected['capsule_key'] if selected and selected['op']=='upsert' and current_allowed(truth,q['source_id'],principal,capsules) and authorized(capsules[selected['capsule_key']]['unit'],principal) else None)
        req = q['requirement']
        if (req['capsule_key'] if req else None)!=expected_key:
            raise ValueError('Reviewed temporal/permission target changed')
        if req is None:
            continue
        capsule = capsules[req['capsule_key']]
        doc = capsule['document']; a, z = req['canonical_span']
        if doc['body'][a:z] != req['text'] or sha(req['text'].encode('utf-8')) != req['text_sha256'] or locate_span(doc['blocks'], a, z) != req['anchors']:
            raise ValueError('Changed required evidence or locator')
    registry = json.loads((registry or ROOT/'evaluation/WORKLOAD_REGISTRY.json').read_text('utf-8'))
    item = next((w for w in registry['workloads'] if w['workload_id'] == labels['workload_id']), None)
    if item is None or item['source_manifest_sha256'] != digest(actual):
        raise ValueError('Register the reviewed workload first')
    for key,field in (('corpus_version','corpus_version'),('query_set_version','query_set_version'),('qrels_version','qrels_version')):
        if labels[key]!=item[field]:raise ValueError('Registry identity mismatch')
    for key in ('event_workload_id','migration_workload_id'):
        sibling=next((w for w in registry['workloads'] if w['workload_id']==labels[key]),None)
        if sibling is None or sibling['source_manifest_sha256']!=digest(actual):raise ValueError('Register related state workloads')
    return labels


def percentile(values, p):
    return sorted(values)[math.ceil(p*len(values))-1]


def version_documents(ranked, generation, capsules):
    documents={}
    for item,_ in ranked:
        row=generation.rows[item]
        doc=capsules[capsule_key(row['source_id'],row['source_version'])]['document']
        if doc['record_digest']!=row['record_digest']:raise ValueError('Candidate/forward version mismatch')
        prior=documents.get(row['source_id'])
        if prior is not None and prior['record_digest']!=doc['record_digest']:raise ValueError('Ambiguous multi-version parent map')
        documents[row['source_id']]=doc
    return documents


def run(output, artifacts, updates=None, label_path=None, registry=None):
    capsules, original = load_capsules(updates)
    labels = load_labels(capsules, label_path, registry, updates)
    corpus_id,queries_id,qrels_id = (labels[k] for k in ('corpus_version','query_set_version','qrels_version'))
    model, model_info = load_encoder(allow_download=False)
    model_info['encode_policy'] = 'body and explicit Entity prefix contracts; same cached backbone, not two trained models'
    bank, builds, tokens = {}, {}, {}
    original_rows = {capsule_key(row['source_id'], 1): row for row in original['rows']}
    for policy in ('body', 'entity-body'):
        keys = sorted(capsules)
        bank[policy] = {}
        needed = [key for key in keys if policy != 'body' or key not in original_rows]
        inputs = [encoding_input(capsules[key]['unit']['text'], capsules[key]['unit']['metadata']['entity'], policy) for key in needed]
        lengths = [len(model.tokenizer(text, truncation=False)['input_ids']) for text in inputs]
        if model.max_seq_length != 256 or model.tokenizer.num_special_tokens_to_add(pair=False) != 2 or max(lengths) > 256:
            raise ValueError('Refuse silent input/model change')
        tick = perf_counter_ns(); matrix = embed(model, inputs, batch_size=16)
        builds[policy] = {'new_vectors': len(needed), 'reused_vectors': len(keys)-len(needed),
                         'max_input_wordpieces_with_specials': max(lengths), 'encoding_ms': (perf_counter_ns()-tick)/1e6}
        bank[policy].update({key: list(vec) for key, vec in zip(needed, matrix)})
        if policy == 'body':
            bank[policy].update({key: row['vector'] for key, row in original_rows.items()})
        for key in keys:
            tokens[capsules[key]['unit']['item_id']] = len(model.tokenizer(capsules[key]['unit']['text'], add_special_tokens=False, truncation=False)['input_ids'])
    query_vectors, encoding_samples = {}, []
    encode_trace = TraceCollector(labels['workload_id'], versions(corpus_id, queries_id, qrels_id, None, MODEL_REVISION), [])
    for policy in bank:
        query_vectors[policy] = {}
        for q in labels['queries']:
            text = encoding_input(q['question'], 'Orion', policy)
            with encode_trace.guard(q['query_id'], policy+'-encoding', 0):
                if len(model.tokenizer(text, truncation=False)['input_ids']) > 256:
                    raise ValueError('Query truncation')
                tick = perf_counter_ns(); query_vectors[policy][q['query_id']] = list(embed(model, [text], batch_size=1)[0])
                encode_trace.record(q['query_id'], policy+'-encoding', 0, ([], {}), {'query_encoding': (perf_counter_ns()-tick)/1e6}, status='ok', reason='query_encoded')
    seeds, commits, deliveries = schedule(capsules)
    stores = {name: VersionStore(name) for name in ('arrival', 'ordered')}
    authority = VersionStore()
    for event in seeds:
        authority.apply(event, 0)
        for store in stores.values(): store.apply(event, 0)
    generations = {name: Generation(name+'-body', store, 'body', bank, capsules) for name, store in stores.items()}
    transition_trace = TraceCollector(labels['event_workload_id'], versions(corpus_id, labels['event_query_set_version'], None, None, MODEL_REVISION), [])
    all_samples, observations, checkpoints = list(encode_trace.records), [], {}
    backfill = None
    timeline = sorted([(t, 0, e) for t, e in commits]+[(t, 1, e) for t, e in deliveries]+[(3500, 2, None)]+
                      [(q['checkpoint_ms'], 3, q) for q in labels['queries']], key=lambda x: (x[0], x[1]))
    for clock, kind, item in timeline:
        if kind == 0:
            authority.apply(item, clock)
        elif kind == 1:
            for mode, store in stores.items():
                with transition_trace.guard('delivery-'+str(clock), mode, 0):
                    tick = perf_counter_ns(); transition, published = generations[mode].publish(store, item, clock)
                    sample = transition_trace.record('delivery-'+str(clock), mode, 0, ([], {}), {'apply_and_publish_preencoded': (perf_counter_ns()-tick)/1e6}, status='ok', reason=transition['reason'])
                    sample['ingestion_transition'] = transition
                    sample['index_version'] = generations[mode].identity
                    sample['published_unit_ids'] = ([capsules[item['capsule_key']]['unit']['item_id']] if item['op']=='upsert' and published else [])
                    sample['controlled_visible_ms'] = clock if published else None
        elif kind == 2:
            backfill = VersionStore.restore(stores['ordered'].payload())
        else:
            q = item
            checkpoints[q['query_id']] = {'authority': authority.payload(), 'stores': {m: s.payload() for m, s in stores.items()}}
            principal = Principal(q['principal']['tenant'], frozenset(q['principal']['roles']))
            for mode, generation in generations.items():
                allowed = {i for i, row in generation.rows.items() if current_allowed(authority, row['source_id'], principal, capsules) and authorized(row, principal)}
                collector = TraceCollector(labels['workload_id'], versions(corpus_id, queries_id, qrels_id, generation.identity, digest(generation.contract)), allowed)
                for trial in range(3):
                    with collector.guard(q['query_id'], mode, trial):
                        tick = perf_counter_ns()
                        ranked, work = generation.query(query_vectors['body'][q['query_id']], contract('body'), principal, authority, q['source_id'], q['as_of_ms'])
                        search_ms = (perf_counter_ns()-tick)/1e6
                        # Current permission is rechecked before actual forward fetch.
                        if any(not current_allowed(authority, generation.rows[i]['source_id'], principal, capsules) for i, _ in ranked):
                            raise ValueError('Permission changed before context')
                        tick = perf_counter_ns()
                        selected, packing = pack_context(ranked, generation.rows, version_documents(ranked,generation,capsules), 80, tokens, scope=principal.tenant+'-reader')
                        packing_ms = (perf_counter_ns()-tick)/1e6
                        context = [unit['item_id'] for unit in selected]
                        rec = collector.record(q['query_id'], mode, trial, (ranked, work), {'version_gate_search': search_ms, 'context_packing': packing_ms}, context=context)
                        rec['source_truth_digest'] = authority.state_digest()
                        rec['controlled_checkpoint_ms'], rec['as_of_ms'] = clock, q['as_of_ms']
                        rec['context_packing'] = packing
                        rec['encoding_contract'] = generation.contract
                        req = q['requirement']; expected = capsules[req['capsule_key']]['unit']['item_id'] if req else None
                        returned = [i for i, _ in ranked]
                        raw = rec['raw_candidate_ids']
                        observations.append({'query_id': q['query_id'], 'mode': mode, 'trial_id': trial, 'request_id': rec['request_id'],
                            'recall_at_1': float(expected in returned) if expected else None,
                            'context_evidence_recall': float(expected in context) if expected else None,
                            'correct_empty': not returned if expected is None else None,
                            'stale_scored_candidate': bool(raw and expected not in raw),
                            'search_ms': search_ms, 'packing_ms': packing_ms})
                all_samples.extend(collector.records)
    # Backfill-only target is stale; tail catch-up is required before cutover.
    migration = Migration(generations['ordered'])
    target = Generation('new-entity-body', backfill, 'entity-body', bank, capsules)
    migration.add(target)
    unsafe_cutover = migration.cutover(generations['ordered'].name, target.name, authority)
    if unsafe_cutover: raise ValueError('Stale backfill passed gate')
    tail_replay = VersionStore.restore(backfill.payload())
    for clock, event in deliveries:
        if clock > 3500: tail_replay.apply(event, clock)
    target.sync(tail_replay)
    valid_cutover = migration.cutover(generations['ordered'].name, target.name, authority)
    migration_samples = []
    final_queries = [q for q in labels['queries'] if q['checkpoint_ms']==5300]
    for generation in (target, generations['ordered']):
        for q in final_queries:
            principal = Principal(q['principal']['tenant'], frozenset(q['principal']['roles']))
            allowed = {i for i, r in generation.rows.items() if current_allowed(authority, r['source_id'], principal, capsules) and authorized(r, principal)}
            tc = TraceCollector(labels['migration_workload_id'], versions(corpus_id, labels['migration_query_set_version'], qrels_id, generation.identity, digest(generation.contract)), allowed)
            result, _ = tc.execute(q['query_id'], generation.name, 0, lambda: generation.query(query_vectors[generation.contract['input_policy']][q['query_id']], generation.contract, principal, authority, q['source_id'], q['as_of_ms']), stage='migration_query')
            ranked = result[0]; req = q['requirement']
            expected = capsules[req['capsule_key']]['unit']['item_id'] if req else None
            if (expected is not None and [i for i, _ in ranked]!=[expected]) or (expected is None and ranked): raise ValueError('Migration regression')
            migration_samples.extend(tc.records)
    principal = Principal('A', frozenset({'reader'}))
    allowed = {i for i,r in target.rows.items() if current_allowed(authority,r['source_id'],principal,capsules) and authorized(r,principal)}
    mismatch_trace = TraceCollector(labels['migration_workload_id'], versions(corpus_id, labels['migration_query_set_version'], None, target.identity, digest(target.contract)), allowed)
    try:
        mismatch_trace.execute('contract-rejection', 'old-query-on-new-index', 0, lambda: target.query(query_vectors['body'][labels['queries'][0]['query_id']], contract('body'), principal, authority, 'A06'), stage='contract_validation')
    except ValueError:
        incompatible_rejected = True
    else:
        raise ValueError('Same-dimension incompatible query accepted')
    mismatch_trace.records[-1]['reason']='encoding_contract_mismatch'
    migration_samples.extend(mismatch_trace.records)
    rollback = migration.cutover(target.name, generations['ordered'].name, authority)
    # Real cache probes: hits inside one generation; changed policy/generation miss.
    cache = ResultCache(); principal = Principal('A', frozenset({'reader'})); generation = generations['ordered']
    q = next(q for q in labels['queries'] if q['query_id']=='final-current')
    key = cache.key(principal, authority, generation, digest(q), None)
    allowed = {i for i,r in generation.rows.items() if current_allowed(authority,r['source_id'],principal,capsules) and authorized(r,principal)}
    cache_trace = TraceCollector(labels['migration_workload_id'], versions(corpus_id, labels['migration_query_set_version'], None, generation.identity, digest(generation.contract)), allowed)
    result,population = cache_trace.execute('cache-populate','cache-query',0,lambda: generation.query(query_vectors['body'][q['query_id']],contract('body'),principal,authority,'A06'),stage='uncached_query')
    ranked = result[0]
    cache.put(key, ranked)
    tick=perf_counter_ns();cached=cache.get(key,generation,principal,authority);cache_ms=(perf_counter_ns()-tick)/1e6
    hit_record=cache_trace.record('cache-hit','cache',0,(cached,{'candidate_stages':{'scored':[],'cached_payload':cached}}),{'cache_validation':cache_ms},status='ok',reason='validated_cache_hit')
    hit_record['cache_source_request_id']=population['request_id']
    cache_hit = cached == ranked
    changed_generation_key = cache.key(principal, authority, target, digest(q), None)
    tenant_key = cache.key(Principal('B', frozenset({'reader'})), authority, generation, digest(q), None)
    cache_probes = {'same_context_hit': cache_hit}
    initial_authority=VersionStore()
    for e in seeds:initial_authority.apply(e,0)
    policy_key=cache.key(principal,initial_authority,generation,digest(q),None)
    for name, probe_key, probe_generation, probe_principal, probe_authority in (
            ('generation_change_miss',changed_generation_key,target,principal,authority),
            ('other_tenant_miss',tenant_key,generation,Principal('B',frozenset({'reader'})),authority),
            ('source_policy_epoch_miss',policy_key,generation,principal,initial_authority)):
        probe_allowed={i for i,r in probe_generation.rows.items() if current_allowed(probe_authority,r['source_id'],probe_principal,capsules) and authorized(r,probe_principal)}
        probe_trace=TraceCollector(labels['migration_workload_id'],versions(corpus_id,labels['migration_query_set_version'],None,probe_generation.identity,digest(probe_generation.contract)),probe_allowed)
        tick=perf_counter_ns();value=cache.get(probe_key,probe_generation,probe_principal,probe_authority);elapsed=(perf_counter_ns()-tick)/1e6
        cache_probes[name]=value is None
        if value is not None:raise ValueError('Cache context boundary failed')
        rec=probe_trace.record('cache-'+name,'cache',0,([] ,{'candidate_stages':{'scored':[]}}),{'cache_validation':elapsed},status='ok',reason='cache_context_miss')
        rec['source_truth_digest']=probe_authority.state_digest()
        migration_samples.extend(probe_trace.records)
    migration_samples.extend(cache_trace.records)
    artifacts.mkdir(parents=True, exist_ok=True)
    payload = {'capsule_manifest': manifest(capsules), 'bank': bank, 'queries': query_vectors,
               'checkpoints': checkpoints, 'final_stores': {m:s.payload() for m,s in stores.items()},
               'authority': authority.payload(), 'migration_events': migration.events, 'contracts': {p:contract(p) for p in bank}}
    expected_digest = atomic_checkpoint(artifacts/'checkpoint.json', payload)
    reloaded = load_checkpoint(artifacts/'checkpoint.json', expected_digest)
    replay_checks = 0
    for q in labels['queries']:
        point = reloaded['checkpoints'][q['query_id']]
        source_authority = VersionStore.restore(point['authority'])
        for mode in stores:
            store = VersionStore.restore(point['stores'][mode])
            gen = Generation(mode+'-body', store, 'body', reloaded['bank'], capsules)
            principal = Principal(q['principal']['tenant'], frozenset(q['principal']['roles']))
            result,work = gen.query(reloaded['queries']['body'][q['query_id']], contract('body'), principal, source_authority, q['source_id'], q['as_of_ms'])
            actual=next(r for r in all_samples if r['query_id']==q['query_id'] and r['mode']==mode and r['trial_id']==0)
            if result!=list(zip(actual['final_candidate_ids'],actual['final_candidate_scores'])) or work['candidate_stages']['scored']!=list(zip(actual['raw_candidate_ids'],actual['raw_candidate_scores'])):
                raise ValueError('Ordered candidate or scored-stage replay mismatch')
            observed = next(o for o in observations if o['query_id']==q['query_id'] and o['mode']==mode)
            expected = capsules[q['requirement']['capsule_key']]['unit']['item_id'] if q['requirement'] else None
            if (float(expected in [i for i,_ in result]) if expected else None) != observed['recall_at_1']: raise ValueError('Replay quality mismatch')
            replay_checks += 1
    aggregates = {}
    for mode in stores:
        subset=[o for o in observations if o['mode']==mode]; positives=[o for o in subset if o['recall_at_1'] is not None]; empty=[o for o in subset if o['correct_empty'] is not None]
        aggregates[mode]={'macro_recall_at_1': sum(o['recall_at_1'] for o in positives)/len(positives),
            'macro_context_evidence_recall': sum(o['context_evidence_recall'] for o in positives)/len(positives),
            'empty_correct_fraction': sum(o['correct_empty'] for o in empty)/len(empty),
            'stale_candidate_fraction_all': sum(o['stale_scored_candidate'] for o in subset)/len(subset),
            'search_p50_ms':percentile([o['search_ms'] for o in subset],.5),'search_p95_ms':percentile([o['search_ms'] for o in subset],.95),
            'packing_p50_ms':percentile([o['packing_ms'] for o in subset],.5),'requests':len(subset)}
    record={'workload_id':labels['workload_id'],'date_utc':datetime.now(timezone.utc).isoformat(),
        'question':'Does monotonic revision processing prevent stale replay while preserving source/policy-bound current and historical evidence?',
        'hypothesis':'Ordered projection rejects stale resurrection, but known pending delivery still creates an evidence gap. Untailed backfill must fail cutover.',
        'baseline':'last unseen arrival wins; same dedup/current authorization/known-revision barrier/model/query/evidence rules',
        'independent_variable':'projection revision ordering; migration is a separate compatibility drill',
        'controls':'same cached body model, source events/delivery order, current authority, exact-ID task,k1,80 encoder-WordPiece proxy and ten frozen checkpoint questions',
        'procedure':'three warm repeats/checkpoint/mode; controlled logical clocks (not service time); six positive/four empty inspected questions; no train/dev/test',
        'versions':versions(corpus_id,queries_id,qrels_id,None,MODEL_REVISION),'model':model_info,'builds':builds,
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform()},
        'capsule_manifest':manifest(capsules),'checkpoint_digest':expected_digest,'qrels_sha256':sha((label_path or HERE/'qrels_ch22.json').read_bytes()),
        'code_sha256':{p:sha((HERE/p).read_bytes()) for p in ('lifecycle_ch22.py','experiment_ch22.py')},
        'aggregates':aggregates,'per_query_trials':observations,'samples':all_samples,'event_samples':transition_trace.records,
        'controlled_lags_ms':{'A06@2':200,'A03-delete@2':600,'A08-revoke@2':900,'A06@3':500},
        'migration':{'backfill_clock_ms':3500,'unsafe_cutover':unsafe_cutover,'valid_cutover':valid_cutover,'rollback':rollback,
            'same_dimension_incompatible_query_rejected':incompatible_rejected,'events':migration.events,'samples':migration_samples,'cache_probes':cache_probes},
        'checkpoint_query_replay_checks':replay_checks,
        'decision':'Keep ordered projection, current-policy/known-revision barriers and tail-validated generation changes; retain pending-delivery miss and arrival replay failures.',
        'limitations':'Single process, fictional source revisions, oracle-like trusted source authority, exact ID tasks, curated labels, prepared embedding bank and controlled clocks. No live CDC/broker/distributed commit/power-loss durability/physical erasure/authentication/generator or model superiority claim.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'workload':record['workload_id'],'aggregates':aggregates,'search_encode_samples':len(all_samples),'event_samples':len(transition_trace.records),'migration_samples':len(migration_samples),'replays':replay_checks,'migration':{k:v for k,v in record['migration'].items() if k not in ('samples','events')}},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'chapter-22-experiment.json')
    parser.add_argument('--artifacts',type=Path,default=HERE/'index_ch22')
    parser.add_argument('--updates',type=Path)
    parser.add_argument('--labels',type=Path)
    parser.add_argument('--registry',type=Path)
    args=parser.parse_args();run(args.output,args.artifacts,args.updates,args.labels,args.registry)
