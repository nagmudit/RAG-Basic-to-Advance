"""One selected route, bounded fallback, current permission and version gates."""
import math
import re
import uuid
from collections import Counter
from pathlib import Path
import sys
from time import perf_counter_ns

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'projects/V6'))
from experiment_ch22 import (load_capsules, load_labels as load_ch22_labels, manifest,
    VersionStore, Generation, load_checkpoint, current_allowed, version_documents,
    pack_context, digest, sha, Principal, authorized, TraceCollector, versions, MODEL_REVISION)
from metadata_ch21 import MetadataIndex, score_rows
from query_ch23 import interpret, ROUTER_VERSION

MODES=('dense_all','constraint_dense','rule_route')


def load_state():
    capsules,_=load_capsules();load_ch22_labels(capsules)
    reference=__import__('json').loads((ROOT/'projects/V6/chapter-22-experiment.json').read_text('utf-8'))
    state=load_checkpoint(ROOT/'projects/V6/index_ch22/checkpoint.json',reference['checkpoint_digest'])
    if state['capsule_manifest']!=manifest(capsules):raise ValueError('Source snapshot mismatch')
    authority=VersionStore.restore(state['authority'])
    generation=Generation('ch23-current-body',VersionStore.restore(state['final_stores']['ordered']),
                          'body',state['bank'],capsules)
    if generation.store.state_digest()!=authority.state_digest():raise ValueError('Unreconciled source state')
    return capsules,authority,generation


def authorized_view(generation,authority,principal,as_of):
    if generation.store.state_digest()!=authority.state_digest():raise ValueError('Unreconciled source state')
    rows=[]
    for source in sorted(authority.heads):
        if not current_allowed(authority,source,principal,generation.capsules):continue
        event=generation.store.selected(source,as_of)
        if not event or event['op']=='delete':continue
        unit=generation.capsules[event['capsule_key']]['unit']
        if not authorized(unit,principal):continue
        row=generation.rows[unit['item_id']]
        if row['record_digest']!=unit['record_digest']:raise ValueError('Forward identity mismatch')
        rows.append(row)
    return MetadataIndex(rows,principal)


def terms(text):
    return re.findall(r'[^\W_]+',text.casefold())


def lexical_score(view,ids,text):
    # Fixture rebuilds authorized statistics per request. No shared private DF.
    counts={}
    for item,row in view.rows.items():
        if not authorized(row,view.principal):raise ValueError('Eligibility changed')
        counts[item]=Counter(terms(row['metadata']['record_id']+' '+row['text']))
    n=len(counts);lengths={i:sum(c.values()) for i,c in counts.items()}
    average=sum(lengths.values())/n if n else 0
    query=set(terms(text));df={t:sum(t in c for c in counts.values()) for t in query}
    scored=[]
    for item in sorted(ids):
        value=0.0
        for term in query:
            tf=counts[item][term]
            if tf:
                idf=math.log(1+(n-df[term]+.5)/(df[term]+.5))
                value+=idf*tf*2.2/(tf+1.2*(.25+.75*lengths[item]/average))
        scored.append((item,value))
    return sorted(scored,key=lambda p:(-p[1],p[0]))


def public_plan(plan):
    return {k:plan[k] for k in ('kind','primary','selected','outcome','fallback','reason','router_version','route_confidence')} | {
        'original_sha256':sha(plan['original'].encode('utf-8')),
        'surface_sha256':sha(plan['surface'].encode('utf-8')),
        'constraint_digest':digest({'predicate':plan['predicate'],'as_of':plan['as_of_ms']}),
        'slot_origin_classes':sorted({v.split(':')[0] for v in plan['slot_provenance'].values()})}


def _execute(request,mode,trial,generation,authority,query_vector,token_counts,version_ids,
            workload,*,faults=None,capabilities=frozenset({'lexical','dense'}),samples_out=None,query_contract=None):
    if mode not in MODES:raise ValueError('Unknown policy')
    if not isinstance(capabilities,frozenset) or capabilities-{'lexical','dense'}:
        raise ValueError('Unimplemented executor capability')
    if query_contract!=generation.contract:raise ValueError('Embedding contract mismatch')
    principal=Principal(request['principal']['tenant'],frozenset(request['principal']['roles']))
    root_id=str(uuid.uuid4());samples=samples_out if samples_out is not None else [];tick=perf_counter_ns()
    plan=interpret(request['text'],available=capabilities,language=request['language'],
        context=request.get('context'),principal_key=digest(request['principal']),
        session_id=request['session_id'],clock_ms=5300)
    if mode=='dense_all':
        present='dense' in capabilities
        plan.update(predicate={},as_of_ms=None,selected='dense' if present else None,
                    outcome='ready' if present else 'unsupported',reason=None if present else 'route_unavailable',fallback=False)
    elif mode=='constraint_dense' and plan['outcome']=='ready':
        if 'dense' in capabilities:plan['selected']='dense'
        else:plan.update(selected=None,outcome='unsupported',reason='route_unavailable')
    process_ms=(perf_counter_ns()-tick)/1e6
    tick=perf_counter_ns();view=authorized_view(generation,authority,principal,plan['as_of_ms'])
    ids=view.select(plan['predicate']);eligibility_ms=(perf_counter_ns()-tick)/1e6
    collector=TraceCollector(workload,version_ids,view.rows)
    ranked=[];work={'candidate_stages':{'scored':[],'route_shortlist':[]}};attempts=[]
    outcome=plan['outcome'];reason=plan['reason'];search_ms=0.0;route=plan['selected']
    if route and not ids:
        outcome,reason='empty','no_authorized_task_candidates'
    elif route:
        routes=[route]
        if mode=='rule_route' and plan['kind'] not in ('count','fresh','relationship'):
            alternate='lexical' if route=='dense' else 'dense'
            if alternate in capabilities:routes.append(alternate)
        for step,branch in enumerate(routes[:2]):
            tick=perf_counter_ns();failure=None
            try:
                if faults and branch in faults:raise faults[branch]('Injected route fault')
                lexical_input=plan['surface']+' '+plan['predicate'].get('record_id','')
                scored=score_rows(view,ids,query_vector) if branch=='dense' else lexical_score(view,ids,lexical_input)
                positive=scored if branch=='dense' else [(i,s) for i,s in scored if s>0]
                ranked=positive[:2]
                branch_work={'candidate_stages':{'scored':scored,'positive_score':positive,'route_shortlist':ranked}}
            except TimeoutError:
                failure='route_timeout';ranked=[];branch_work={'candidate_stages':{'scored':[],'route_shortlist':[]}}
            except Exception:
                elapsed=(perf_counter_ns()-tick)/1e6
                record=collector.record(request['query_id'],mode+':'+branch,trial,([],{}),{'route_search':elapsed},status='failed',reason='operation_failed')
                record.update(parent_request_id=root_id,route=branch,plan=public_plan(plan))
                samples.append(record)
                # Authorization/integrity/program errors are not retryable timeouts.
                parent=collector.record(request['query_id'],mode,trial,([],{}),{'query_process':process_ms,'eligibility':eligibility_ms,'failed_route':elapsed},status='failed',reason='operation_failed')
                parent.update(request_id=root_id,plan=public_plan(plan),branch_request_ids=[record['request_id']])
                samples.append(parent)
                raise
            elapsed=(perf_counter_ns()-tick)/1e6;search_ms+=elapsed
            child=collector.record(request['query_id'],mode+':'+branch,trial,(ranked,branch_work),{'route_search':elapsed},
                status='failed' if failure else ('ok' if ranked else 'empty'),reason=failure or (None if ranked else 'no_positive_score'))
            child.update(parent_request_id=root_id,route=branch,route_index_identity=digest({'generation':generation.identity,'route':branch,
                'authorized_ids':sorted(view.rows),'as_of':plan['as_of_ms'],'lexical_parameters':[1.2,.75,'unicode_words_record_plus_body']}),
                score_semantics='normalized_dot' if branch=='dense' else 'BM25_body_plus_exact_record_id',
                attempt=step+1,plan=public_plan(plan))
            samples.append(child);attempts.append(child['request_id']);work=branch_work
            if failure:
                outcome,reason='failed','retry_budget_exhausted'
                continue
            outcome=plan['outcome'] if ranked else 'empty';reason=plan['reason'] if ranked else 'no_positive_score'
            break  # Successful empty is not an unbounded semantic retry trigger.
    tick=perf_counter_ns()
    def lookup(item):
        row=generation.rows[item]
        if not current_allowed(authority,row['source_id'],principal,generation.capsules) or not authorized(row,principal):
            raise ValueError('Eligibility changed before context')
        return row
    for item,_ in ranked:lookup(item)  # Gate before original-version forward map.
    docs=version_documents(ranked,generation,generation.capsules)
    class Forward:
        def __getitem__(self,item):return lookup(item)
    packed=[];packing={'packing_attempts':[],'used_encoder_wordpieces':0,'context_unit_ids':[]}
    for item,score in ranked:
        row=lookup(item)
        scopes=set(row['allowed_scopes']) & {principal.tenant+'-'+role for role in principal.roles}
        if not scopes:raise ValueError('Scope/metadata contradiction before context')
        selected,step=pack_context([(item,score)],Forward(),docs,80-packing['used_encoder_wordpieces'],
                                   token_counts,False,sorted(scopes)[0])
        packed.extend(selected);packing['packing_attempts'].extend(step['packing_attempts'])
        packing['used_encoder_wordpieces']+=step['used_encoder_wordpieces']
        packing['context_unit_ids'].extend(step['context_unit_ids'])
    context_ms=(perf_counter_ns()-tick)/1e6
    context_ran=plan['outcome'] not in ('clarify','unsupported') and outcome!='failed'
    timings={'query_process':process_ms,'eligibility':eligibility_ms,'route_search_total':search_ms}
    if context_ran:timings['context']=context_ms
    status=('ok' if outcome=='ready' and ranked else outcome)
    parent=collector.record(request['query_id'],mode,trial,(ranked,work),
        timings,context=[u['item_id'] for u in packed] if context_ran else None,status=status,reason=reason)
    parent.update(request_id=root_id,plan=public_plan(plan),branch_request_ids=attempts,
        task_match_ids=sorted(ids),source_truth_digest=authority.state_digest(),packing=packing if context_ran else None,
        stages_not_run=['generation','claim_verification']+([] if context_ran else ['context']),
        final_route=samples[-1]['route'] if attempts and ranked else None,
        last_attempted_route=samples[-1]['route'] if attempts else None,
        fallback_attempted=len(attempts)>1 or plan['fallback'],answer=None,evidence_ids=None)
    samples.append(parent)
    return ranked,packed,plan,parent,samples


def execute(*args,trace_sink=None,**kwargs):
    """Retain redacted failed attempts even when interpretation/integrity raises."""
    records=[];tick=perf_counter_ns()
    try:
        result=_execute(*args,**kwargs,samples_out=records)
    except Exception as exc:
        if not records or 'parent_request_id' in records[-1]:
            request,mode,trial=args[:3];version_ids,workload=args[7:9]
            collector=TraceCollector(workload,version_ids,[])
            records.append(collector.record(request['query_id'],mode,trial,([],{}),
                {'failed_attempt':(perf_counter_ns()-tick)/1e6},status='invalid' if isinstance(exc,ValueError) else 'failed',
                reason='invalid_input' if isinstance(exc,ValueError) else 'operation_failed'))
        if trace_sink is not None:trace_sink.extend(records)
        raise
    if trace_sink is not None:trace_sink.extend(records)
    return result
