"""Frozen-intent fan-out over an exact, authorized dense index. No score fusion."""
import json
import uuid
from pathlib import Path
from time import perf_counter_ns

from retrieval_ch23 import (ROOT, load_state, manifest, VersionStore, Generation,
    current_allowed, authorized, authorized_view, score_rows, version_documents,
    pack_context, Principal, TraceCollector, versions, digest, sha, public_plan)
from query_ch23 import interpret
from reformulate_ch24 import admit, interleave, lock_for
from experiment_ch22 import upsert
from experiment_ch21 import ingest, make_chunks, locate_span
from metadata_ch21 import validate_metadata

HERE = Path(__file__).resolve().parent
WORKLOAD = 'ch24-frozen-reformulations-v1'
CONTROL = 'ch24-decomposition-budget-v1'
MODES = ('original', 'multi', 'hypothetical')


def load_sources(directory=None):
    capsules, authority, old = load_state()
    capsules = dict(capsules)  # Keep the Chapter23 generation's capsule roster immutable.
    directory = directory or HERE/'fixtures_ch24'
    for source in json.loads((directory/'sources.json').read_text('utf-8')):
        validate_metadata(source['metadata'])
        m = source['metadata']
        if m['record_id'] != source['source_id'] or str(m['version']) != source['source_version'] or set(source['allowed_scopes']) != {m['tenant']+'-'+r for r in m['acl_roles']}:
            raise ValueError('Descriptor/policy contradiction')
        scope = source['allowed_scopes'][0]
        doc = ingest(directory, source, scope)
        if doc['status'] != 'accepted':
            raise ValueError('Unapproved or changed source')
        chunks = make_chunks(doc, 'structure48', scope)
        if len(chunks) != 1:
            raise ValueError('Reviewed unit boundary changed')
        unit = {**chunks[0], 'metadata': m, 'metadata_digest': digest(m),
                'license': doc['license'], 'indexing_allowed': doc['indexing_allowed']}
        key = source['source_id']+'@'+source['source_version']
        if key in capsules:
            raise ValueError('Duplicate capsule')
        capsules[key] = {'document': doc, 'unit': unit}
        authority.apply(upsert(capsules, source['source_id'], m['version'], 5300, 'ch24-seed-'+key), 5300)
    return capsules, authority, old


def load_labels(capsules, authority, path=None, drafts_path=None):
    labels = json.loads((path or HERE/'qrels_ch24.json').read_text('utf-8'))
    drafts = json.loads((drafts_path or HERE/'reformulations_ch24.json').read_text('utf-8'))
    if labels['capsule_manifest'] != manifest(capsules) or labels['source_manifest_sha256'] != digest(manifest(capsules)) or labels['authority_digest'] != authority.state_digest():
        raise ValueError('Review changed evidence/policy/version state')
    if labels['query_manifest_sha256'] != digest(labels['queries']) or labels['drafts_digest'] != digest(drafts) or labels['descriptor_sha256'] != sha((HERE/'fixtures_ch24/sources.json').read_bytes()):
        raise ValueError('Review changed original questions/drafts/origins')
    for q in labels['queries']:
        for req in q['requirements']:
            c = capsules[req['capsule_key']]; doc = c['document']; a, z = req['canonical_span']
            if req['item_id'] != c['unit']['item_id'] or doc['body'][a:z] != req['text'] or sha(req['text'].encode()) != req['text_sha256'] or locate_span(doc['blocks'], a, z) != req['anchors']:
                raise ValueError('Changed evidence locator')
        # Independent targets include the known duration/count interpretation error.
        if q['required_empty'] and q['requirements'] or q['guard'] and q['requirements']:
            raise ValueError('Invalid judgment class')
    registry = json.loads((ROOT/'evaluation/WORKLOAD_REGISTRY.json').read_text('utf-8'))['workloads']
    for name in (WORKLOAD, CONTROL):
        entry = next((w for w in registry if w['workload_id'] == name), None)
        if not entry or entry['source_manifest_sha256'] != labels['source_manifest_sha256']:
            raise ValueError('Register workload')
    entry = next(w for w in registry if w['workload_id'] == WORKLOAD)
    if any(entry[k] != labels[k] for k in ('corpus_version', 'query_set_version', 'qrels_version', 'query_manifest_sha256')):
        raise ValueError('Workload identity mismatch')
    return labels, drafts


def proposals_for(request, plan, draft, mode, authority, contract):
    lock = lock_for(request, plan, authority, contract)
    if mode not in MODES:
        raise ValueError('Unknown method')
    if plan['outcome'] not in ('ready', 'partial'):
        return [], []
    proposals = [] if mode == 'original' else (draft['multi'] if mode == 'multi' else [draft['hypothetical']])
    chosen, decisions = admit(request['text'], proposals, lock)
    if mode == 'hypothetical' and len(chosen) > 1:
        chosen = chosen[1:2]
    return chosen, decisions


def _execute(request, draft, mode, trial, generation, authority, inputs, tokens,
             version_ids, *, query_contract, wordpiece_budget=192, faults=None, frames):
    root = str(uuid.uuid4()); tick = perf_counter_ns()
    if query_contract != generation.contract:
        raise ValueError('Embedding contract mismatch')
    if type(wordpiece_budget) is not int or wordpiece_budget < 1:
        raise ValueError('Invalid WordPiece budget')
    plan = interpret(request['text'], language=request.get('language', 'en'),
                     context=request.get('context'), principal_key=request.get('principal_key'),
                     session_id=request.get('session_id'), clock_ms=5300)
    chosen, decisions = proposals_for(request, plan, draft, mode, authority, query_contract)
    process_ms = (perf_counter_ns()-tick)/1e6
    principal = Principal(request['principal']['tenant'], frozenset(request['principal']['roles']))
    tick = perf_counter_ns()
    view = authorized_view(generation, authority, principal, plan['as_of_ms'])
    task_ids = view.select(plan['predicate']) if chosen else set()
    eligibility_ms = (perf_counter_ns()-tick)/1e6
    collector = TraceCollector(WORKLOAD, version_ids, view.rows)
    branches = []; raw = []; raw_owners = []; child_ids = []; used = 0; search_ms = 0.; failed = 0
    for branch in chosen if task_ids else []:
        branch_id = branch['branch_id']; inp = inputs[branch_id]
        if inp['text_sha256'] != sha(branch['text'].encode()):
            raise ValueError('Prepared input/text mismatch')
        wp = inp['wordpieces_with_specials']
        if type(wp) is not int or not 2 <= wp <= 256:
            raise ValueError('Invalid prepared input length')
        if used + wp > wordpiece_budget:
            if branch_id == 'original':
                raise ValueError('Original exceeds encoder budget')
            decisions.append({'branch_id': branch_id, 'accepted': False, 'reason': 'encoder_budget'})
            continue
        used += wp; tick = perf_counter_ns(); error = None
        try:
            if faults and branch_id in faults:
                raise faults[branch_id]()
            scored = score_rows(view, task_ids, inp['vector'])
        except TimeoutError:
            scored = []; failed += 1; error = 'injected_timeout'
        except Exception:
            child = collector.record(request['query_id'], mode+':branch', trial, ([], {}),
                {'dense_search': (perf_counter_ns()-tick)/1e6}, status='failed', reason='operation_failed')
            child.update(parent_request_id=root, branch_id=branch_id)
            frames.append(child)
            raise
        elapsed = (perf_counter_ns()-tick)/1e6; search_ms += elapsed
        top = scored[:2]
        child = collector.record(request['query_id'], mode+':branch', trial,
            (top, {'candidate_stages': {'scored': scored, 'shortlist': top}}),
            {'dense_search': elapsed}, status='failed' if error else ('ok' if top else 'empty'), reason=error)
        child.update(parent_request_id=root, branch_id=branch_id, plan=public_plan(plan),
            prepared_encoding_request_id=inp['encoding_request_id'],
            input_sha256=inp['text_sha256'], input_wordpieces_with_specials=wp,
            score_semantics='unit_float32_vectors_python_dot', stages_not_run=['generation'])
        frames.append(child); child_ids.append(child['request_id'])
        raw.extend(scored); raw_owners.extend([branch_id]*len(scored)); branches.append((branch_id, top))
    tick = perf_counter_ns()
    ranked, admission, owners, admission_owners = interleave(branches, cap=2)
    merge_ms = (perf_counter_ns()-tick)/1e6
    context_ran = bool(chosen) and (not failed or bool(ranked))
    packed = []; packing = None; context_ms = None
    if context_ran:
        tick = perf_counter_ns()
        def lookup(item):
            row = generation.rows[item]
            if not current_allowed(authority, row['source_id'], principal, generation.capsules) or not authorized(row, principal):
                raise ValueError('Eligibility changed before forward fetch')
            return row
        for item, _ in ranked: lookup(item)
        docs = version_documents(ranked, generation, generation.capsules)
        class Forward:
            def __getitem__(self, item): return lookup(item)
        packing = {'packing_attempts': [], 'used_encoder_wordpieces': 0, 'context_unit_ids': []}
        for item, score in ranked:
            row = lookup(item)
            scopes = set(row['allowed_scopes']) & {principal.tenant+'-'+role for role in principal.roles}
            if not scopes: raise ValueError('Scope contradiction')
            selected, step = pack_context([(item, score)], Forward(), docs,
                80-packing['used_encoder_wordpieces'], tokens, False, sorted(scopes)[0])
            packed.extend(selected)
            for key in ('packing_attempts', 'context_unit_ids'): packing[key].extend(step[key])
            packing['used_encoder_wordpieces'] += step['used_encoder_wordpieces']
        context_ms = (perf_counter_ns()-tick)/1e6
    timings = {'query_process': process_ms, 'eligibility': eligibility_ms, 'dense_search_total': search_ms, 'merge': merge_ms}
    if context_ms is not None: timings['context'] = context_ms
    status = plan['outcome'] if not chosen else ('partial' if failed and ranked else 'failed' if failed else 'ok' if ranked else 'empty')
    reason = plan['reason'] if not chosen else ('branch_failure' if failed else None if ranked else 'no_task_matches')
    parent = collector.record(request['query_id'], mode, trial,
        (ranked, {'candidate_stages': {'scored': raw, 'deduplicated_admission': admission, 'capped': ranked}}),
        timings, context=[p['item_id'] for p in packed] if context_ran else None, status=status, reason=reason)
    parent.update(request_id=root, plan=public_plan(plan), branch_request_ids=child_ids,
        proposal_decisions=decisions, raw_branch_ids=raw_owners, admission_branch_ids=admission_owners,
        final_origin_branch_ids=owners, branch_shortlists=[{'branch_id': b, 'ids': [i for i,_ in r], 'scores': [s for _,s in r]} for b,r in branches],
        score_semantics='origin_branch_dot; no merged relevance score',
        source_truth_digest=authority.state_digest(), task_match_ids=sorted(task_ids),
        input_wordpieces_charged=used, input_wordpiece_budget=wordpiece_budget,
        generator_input_tokens=None, generator_output_tokens=None, generator_cost=None,
        packing=packing, answer=None, stages_not_run=['proposal_generation', 'request_time_encoding', 'answer_generation', 'claim_verification']+([] if context_ran else ['context']))
    frames.append(parent)
    return ranked, packed, plan, parent, frames


def execute(*args, trace_sink=None, **kwargs):
    frames = []; tick = perf_counter_ns()
    try:
        result = _execute(*args, frames=frames, **kwargs)
    except Exception as exc:
        request, _, mode, trial = args[:4]; version_ids = args[8]
        parent = TraceCollector(WORKLOAD, version_ids, []).record(request['query_id'], mode, trial, ([], {}),
            {'failed_attempt': (perf_counter_ns()-tick)/1e6}, status='invalid' if isinstance(exc, ValueError) else 'failed', reason='invalid_input' if isinstance(exc, ValueError) else 'operation_failed')
        if frames:
            parent['request_id'] = frames[0]['parent_request_id']
            parent['branch_request_ids'] = [f['request_id'] for f in frames]
        frames.append(parent)
        if trace_sink is not None: trace_sink.extend(frames)
        raise
    if trace_sink is not None: trace_sink.extend(frames)
    return result
