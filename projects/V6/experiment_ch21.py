"""Metadata placement comparison with frozen content/policy-bound judgments."""
import argparse
import json
import math
import platform
import random
import sys
from pathlib import Path
from time import perf_counter_ns
from datetime import datetime, timezone
import numpy as np
from metadata_ch21 import Principal, MetadataIndex, authorized, validate_metadata, search, graph_walk, POLICY, SCHEMA, MODES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'projects/V5'))
from ingestion_ch19 import ingest, digest, sha, locate_span
from chunking_ch20 import make_chunks, pack_context
sys.path.insert(0, str(ROOT/'projects/common'))
from experiment_trace import TraceCollector, versions, validate
sys.path.insert(0, str(ROOT/'projects/V3'))
from experiment_ch11 import load_encoder, embed, MODEL_REVISION

WORKLOAD = 'ch21-metadata-predicates-v1'
CORPUS = 'ch21-two-tenant-policy-fixtures-v1'
QUERIES = 'ch21-twelve-filter-probes-v1'
QRELS = 'ch21-source-policy-bound-qrels-v1'
K = 2


def load_corpus():
    descriptors = json.loads((HERE/'sources_ch21.json').read_text('utf-8'))
    docs, rows, dispositions = [], [], []
    for source in descriptors:
        # Indexing job's fixture privileges are explicit; invalid/unlicensed
        # descriptors stop BEFORE path resolution/read. No unknown-open default.
        try:
            validate_metadata(source['metadata'])
        except ValueError:
            dispositions.append({'status': 'blocked', 'reason': 'invalid_policy_metadata'})
            continue
        if source['indexing_allowed'] is not True or not source['license']:
            dispositions.append({'status': 'blocked', 'reason': 'indexing_use_unapproved'})
            continue
        meta = source['metadata']
        if meta['record_id'] != source['source_id'] or str(meta['version']) != source['source_version'] or set(source['allowed_scopes']) != {meta['tenant']+'-'+r for r in meta['acl_roles']}:
            raise ValueError('Descriptor/metadata identity contradiction')
        scope = source['allowed_scopes'][0]
        doc = ingest(HERE/'fixtures_ch21', source, scope)
        if doc['status'] != 'accepted':
            raise ValueError('Fixture extraction changed')
        chunks = make_chunks(doc, 'structure48', scope)
        if len(chunks) != 1:
            raise ValueError('Reviewed single-unit fixture changed')
        docs.append(doc)
        rows.append({**chunks[0], 'metadata': meta, 'metadata_digest': digest(meta),
                     'license': doc['license'], 'indexing_allowed': doc['indexing_allowed']})
        dispositions.append({'status': 'accepted'})
    return docs, rows, dispositions


def source_manifest(docs, rows):
    metadata = {r['source_id']: r['metadata_digest'] for r in rows}
    return [{**{k: d[k] for k in ('source_id', 'source_version', 'source_sha256', 'body_sha256', 'record_digest', 'allowed_scopes', 'license', 'indexing_allowed', 'retention_policy')},
             'metadata_digest': metadata[d['source_id']]} for d in sorted(docs, key=lambda d: d['source_id'])]


def load_labels(docs, rows):
    for doc in docs:
        if digest({k: v for k, v in doc.items() if k != 'record_digest'}) != doc['record_digest'] or sha(doc['body'].encode('utf-8')) != doc['body_sha256']:
            raise ValueError('Changed canonical content or locator map')
    for row in rows:
        if digest(row['metadata']) != row['metadata_digest']:
            raise ValueError('Changed metadata sidecar')
    labels = json.loads((HERE/'qrels_ch21.json').read_text('utf-8'))
    manifest = source_manifest(docs, rows)
    if labels['version'] != QRELS or labels['query_set_version'] != QUERIES or labels['source_manifest'] != manifest or labels['source_manifest_sha256'] != digest(manifest):
        raise ValueError('Review changed evidence/metadata/policy identity')
    if labels['descriptor_sha256'] != sha((HERE/'sources_ch21.json').read_bytes()):
        raise ValueError('Changed descriptor roster')
    docmap = {d['source_id']: d for d in docs}
    for q in labels['queries']:
        view = MetadataIndex(rows, Principal(q['principal']['tenant'], frozenset(q['principal']['roles'])))
        actual = {view.rows[i]['source_id'] for i in view.select(q['predicate'])}
        # All fixture units satisfying the signed query constraints directly
        # answer this bounded waiting-period task. Not a general relevance rule.
        if actual != set(q['relevant_sources']):
            raise ValueError('Reviewed relevance/eligibility changed')
        if set(q['requirements']) != set(q['relevant_sources']):
            raise ValueError('Incomplete reviewed requirements')
        for source, req in q['requirements'].items():
            doc = docmap[source]
            a, z = req['canonical_span']
            if doc['body'][a:z] != req['text'] or sha(req['text'].encode('utf-8')) != req['text_sha256'] or locate_span(doc['blocks'], a, z) != req['anchors']:
                raise ValueError('Changed judged content or locator')
    return labels


def verify_snapshot(snapshot, docs, rows, expected_digest):
    if snapshot['index_manifest_digest'] != expected_digest or digest({k: v for k, v in snapshot.items() if k != 'index_manifest_digest'}) != expected_digest:
        raise ValueError('Untrusted vector/metadata snapshot')
    if snapshot['source_manifest'] != source_manifest(docs, rows) or snapshot['model_revision'] != MODEL_REVISION or snapshot['metadata_schema'] != SCHEMA or snapshot['policy_version'] != POLICY:
        raise ValueError('Changed source/model/schema/policy')
    if len(rows) != len(snapshot['rows']):
        raise ValueError('Changed roster')
    for expected, row in zip(rows, snapshot['rows']):
        if any(row.get(k) != v for k, v in expected.items()):
            raise ValueError('Changed chunk/map/metadata')
        vector = row['vector']
        if len(vector) != 384 or not all(math.isfinite(v) for v in vector) or abs(sum(v*v for v in vector)-1) > .0001:
            raise ValueError('Invalid normalized vector')
    return snapshot


def quality(ranked, view, predicate, relevant, oracle, context_ids=()):
    ids = {i for i, _ in ranked}
    task_ids = view.select(predicate)
    relevant_ids = {i for i, r in view.rows.items() if r['source_id'] in relevant}
    oracle_ids = {i for i, _ in oracle}
    return {'recall_at_2': len(ids & relevant_ids)/len(relevant_ids) if relevant_ids else None,
            'context_source_recall': len(set(context_ids) & relevant_ids)/len(relevant_ids) if relevant_ids else None,
            'precision_at_2': len(ids & relevant_ids)/K,
            'predicate_violations': len(ids-task_ids),
            'oracle_recall': len(ids & oracle_ids)/len(oracle_ids) if oracle_ids else None,
            'empty_correct': not ranked if not relevant else None,
            'task_count': len(task_ids), 'authorized_count': len(view.rows)}


def percentile(values, p):
    return sorted(values)[math.ceil(p*len(values))-1]


def run(output, artifacts):
    docs, rows, dispositions = load_corpus()
    labels = load_labels(docs, rows)
    model, model_info = load_encoder(allow_download=False)
    model_info['encode_policy'] = 'canonical chunk body only; shared frozen encoder for questions/passages; normalized float32; metadata excluded; no prefixes'
    lengths = [len(model.tokenizer(r['text'], truncation=False)['input_ids']) for r in rows]
    if model.max_seq_length != 256 or model.tokenizer.num_special_tokens_to_add(pair=False) != 2 or max(lengths) > 256:
        raise ValueError('Refuse truncation/model input change')
    tick = perf_counter_ns()
    matrix = embed(model, [r['text'] for r in rows], batch_size=16)
    passage_ms = (perf_counter_ns()-tick)/1e6
    indexed = [{**row, 'vector': list(vec)} for row, vec in zip(rows, matrix)]
    tokens = {row['item_id']: length-2 for row, length in zip(indexed, lengths)}
    queries, collectors, query_encoding_ms = {}, {}, {}
    index_version = digest({'model': MODEL_REVISION, 'rows': indexed, 'schema': SCHEMA, 'policy': POLICY})
    identity = versions(CORPUS, QUERIES, QRELS, index_version, MODEL_REVISION)
    for q in labels['queries']:
        principal = Principal(q['principal']['tenant'], frozenset(q['principal']['roles']))
        view = MetadataIndex(indexed, principal)
        collector = TraceCollector(WORKLOAD, identity, view.rows)
        collectors[q['query_id']] = collector
        with collector.guard(q['query_id'], 'query-encoding', 0):
            length = len(model.tokenizer(q['question'], truncation=False)['input_ids'])
            if length > 256:
                raise ValueError('Refuse query truncation')
            tick = perf_counter_ns()
            queries[q['query_id']] = list(embed(model, [q['question']], batch_size=1)[0])
            query_encoding_ms[q['query_id']] = (perf_counter_ns()-tick)/1e6
            collector.record(q['query_id'], 'query-encoding', 0, ([], {}), {'query_encoding': query_encoding_ms[q['query_id']]}, status='ok', reason='query_encoded')
    snapshot = {'model_revision': MODEL_REVISION, 'metadata_schema': SCHEMA, 'policy_version': POLICY,
                'source_manifest': source_manifest(docs, rows), 'index_version': index_version,
                'rows': indexed, 'queries': queries, 'input_lengths_with_specials': lengths}
    snapshot['index_manifest_digest'] = digest(snapshot)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts/'index.json').write_bytes((json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    (artifacts/'documents.json').write_bytes((json.dumps(docs, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    reloaded = verify_snapshot(json.loads((artifacts/'index.json').read_text('utf-8')), docs, rows, snapshot['index_manifest_digest'])
    outcomes, reload_checks = [], 0
    schedule = [(q, mode, trial) for q in labels['queries'] for mode in MODES for trial in range(3)]
    random.Random(21013).shuffle(schedule)
    for q, mode, trial in schedule:
        principal = Principal(q['principal']['tenant'], frozenset(q['principal']['roles']))
        collector = collectors[q['query_id']]
        with collector.guard(q['query_id'], mode, trial):
            tick = perf_counter_ns()
            view = MetadataIndex(indexed, principal)
            authorized_view_ms = (perf_counter_ns()-tick)/1e6
            tick = perf_counter_ns()
            result = search(view, q['predicate'], queries[q['query_id']], mode, K)
            search_ms = (perf_counter_ns()-tick)/1e6
            ranked, work = result
            # Carry V5's real context selector forward. Recheck policy before
            # forward text access; task-correctness remains a separate constraint.
            for item, _ in ranked:
                if not authorized(view.rows[item], principal):
                    raise ValueError('Unauthorized before context fetch')
            tick = perf_counter_ns()
            packed, packing = pack_context(ranked, view.rows, {d['source_id']: d for d in docs}, 80, tokens,
                                  scope=principal.tenant+'-reader')
            packing_ms = (perf_counter_ns()-tick)/1e6
            selected = [r['item_id'] for r in packed]
            rec = collector.record(q['query_id'], mode, trial, result, {'authorized_view': authorized_view_ms, 'filter_and_search': search_ms, 'context_packing': packing_ms}, context=selected)
            rec['context_packing'] = packing
            rec['filter_plan'] = {k: work[k] for k in ('authorized_count', 'task_count', 'scored_count', 'requested_k', 'shortlist_depth', 'underfilled')}
            rec['predicate_digest'] = digest(q['predicate'])
            rec['task_match_ids'] = sorted(view.select(q['predicate']))
            rec['metadata_schema_version'], rec['authorization_policy_version'] = SCHEMA, POLICY
            # Ordinary sample retains only already-authorized identities. No
            # query, predicates, tenant/principal strings, text or exclusions.
            validate(rec, view.rows)
            oracle, _ = search(view, q['predicate'], queries[q['query_id']], 'prefilter', K)
            metrics = quality(ranked, view, q['predicate'], q['relevant_sources'], oracle, selected)
            outcomes.append({'query_id': q['query_id'], 'mode': mode, 'trial_id': trial,
                             'request_id': rec['request_id'], 'metrics': metrics,
                             'final_ids': [i for i, _ in ranked], 'oracle_ids': [i for i, _ in oracle],
                             'filter_and_search_ms': search_ms, 'authorized_view_ms': authorized_view_ms,
                             'context_packing_ms': packing_ms, 'context_ids': selected,
                             'scored_count': work['scored_count']})
            replay = search(MetadataIndex(reloaded['rows'], principal), q['predicate'], reloaded['queries'][q['query_id']], mode, K)[0]
            if replay != ranked:
                raise ValueError('Changed reloaded ranking')
            reload_checks += 1
    aggregates = {}
    for mode in MODES:
        subset = [r for r in outcomes if r['mode'] == mode]
        positive = [r for r in subset if r['metrics']['recall_at_2'] is not None]
        empty = [r for r in subset if r['metrics']['empty_correct'] is not None]
        times = [r['filter_and_search_ms'] for r in subset]
        aggregates[mode] = {'macro_recall_at_2_positive': sum(r['metrics']['recall_at_2'] for r in positive)/len(positive),
                            'macro_context_source_recall_positive': sum(r['metrics']['context_source_recall'] for r in positive)/len(positive),
                            'macro_oracle_recall_positive': sum(r['metrics']['oracle_recall'] for r in positive)/len(positive),
                            'mean_precision_at_2_all': sum(r['metrics']['precision_at_2'] for r in subset)/len(subset),
                            'predicate_violations_per_pass': sum(r['metrics']['predicate_violations'] for r in subset)/3,
                            'empty_correct_fraction': sum(r['metrics']['empty_correct'] for r in empty)/len(empty),
                            'mean_scored_count_all': sum(r['scored_count'] for r in subset)/len(subset),
                            'filter_search_p50_ms': percentile(times, .5), 'filter_search_p95_ms': percentile(times, .95),
                            'authorized_view_p50_ms': percentile([r['authorized_view_ms'] for r in subset], .5),
                            'context_packing_p50_ms': percentile([r['context_packing_ms'] for r in subset], .5),
                            'sample_count': len(subset)}
    bridge = {'u': ['x'], 'x': ['y'], 'y': ['v'], 'v': []}
    bridge_scores = {'u': .2, 'x': .3, 'y': .4, 'v': .9}
    graph = {name: dict(zip(('ranked', 'events'), graph_walk(bridge, bridge_scores, {'v'}, prune)))
             for name, prune in (('task-transit', False), ('task-pruned', True))}
    # This separate deterministic demonstration has its own registered workload.
    bridge_fixture = {'adjacency': bridge, 'scores': bridge_scores, 'task_ids': ['v'], 'entry': 'u'}
    graph_collector = TraceCollector('ch21-authorized-task-bridge-v1', versions('ch21-four-public-nodes-v1', 'ch21-bridge-query-v1', 'preassigned-score-task-top1-v1', digest(bridge_fixture), None), bridge)
    for name, result in graph.items():
        scored = [(e['node'], e['score']) for e in result['events'] if e['action'] == 'expanded']
        rec = graph_collector.record('bridge', name, 0, (result['ranked'], {'candidate_stages': {'scored': scored}}), {}, reason=None if result['ranked'] else 'task_bridge_pruned')
        rec['frontier_events'] = result['events']
    record = {'workload_id': WORKLOAD, 'date_utc': datetime.now(timezone.utc).isoformat(),
              'question': 'Do exact constraints survive similarity ranking and bounded task postfilters?',
              'hypothesis': 'Authorization-first exact prefilter obeys constraints and matches the eligible oracle; shallow task postfilter can underfill despite an exact global authorized ranking.',
              'baseline': 'semantic top2 within authorized roster; task predicates omitted',
              'independent_variable': 'task filter placement and explicit shortlist depth',
              'controls': 'same principal/query/predicate/source/qrels/384 normalized body-only model/exact dot scores/stable ID ties/k2/whole-unit80 encoder-WordPiece context proxy',
              'versions': identity, 'schema_version': SCHEMA, 'policy_version': POLICY,
              'procedure': '12 single-author inspected queries, 9 positive/3 empty, four plans, three warm repetitions, randomized seed21013; no train/dev/test split',
              'denominators': {'positive_queries': 9, 'empty_queries': 3, 'all_queries': 12, 'trials': 3, 'relevant_memberships': 11, 'reviewed_authorized_pairs': 108},
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'platform': platform.platform()},
              'model': model_info, 'passage_encoding_ms': passage_ms, 'query_encoding_ms': query_encoding_ms,
              'source_dispositions': dispositions, 'source_manifest': source_manifest(docs, rows),
              'index_manifest_digest': snapshot['index_manifest_digest'], 'qrels_sha256': sha((HERE/'qrels_ch21.json').read_bytes()),
              'code_sha256': {p: sha((HERE/p).read_bytes()) for p in ('metadata_ch21.py', 'experiment_ch21.py', '../V5/chunking_ch20.py', '../V5/ingestion_ch19.py')},
              'aggregates': aggregates, 'per_query_trials': outcomes,
              'samples': [rec for collector in collectors.values() for rec in collector.records],
              'bridge_workload_id': 'ch21-authorized-task-bridge-v1', 'bridge_fixture': bridge_fixture, 'bridge': graph, 'bridge_samples': graph_collector.records,
              'ordered_reload_checks': reload_checks,
              'decision': 'Use exact prefilter for the small frozen V6 fixture; preserve bounded postfilter failures. No authorization relaxation or production/ANN speed conclusion.',
              'limitations': 'Fictional templates; one author; inspected questions; three warm repeats; no generation/authentication/live revocation; metadata assumed curated correct; whole-unit80 encoder-WordPiece proxy is not a generator budget; bridge is exhaustive traversal, not HNSW.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((json.dumps(record, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'workload': WORKLOAD, 'aggregates': aggregates, 'samples': len(record['samples']), 'reload_checks': reload_checks}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE/'chapter-21-experiment.json')
    parser.add_argument('--artifacts', type=Path, default=HERE/'index_ch21')
    args = parser.parse_args()
    run(args.output, args.artifacts)
