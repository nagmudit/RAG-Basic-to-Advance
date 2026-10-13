"""Source-bound paired query-policy experiment and bounded fault controls."""
import argparse
import json
import math
import platform
import random
import sys
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
from time import perf_counter_ns

from retrieval_ch23 import (ROOT,load_state,manifest,digest,sha,MODES,execute,
    versions,MODEL_REVISION,TraceCollector,authorized_view,Principal)
from query_ch23 import normalize,ROUTER_VERSION
from experiment_ch21 import load_encoder,embed,locate_span

HERE=Path(__file__).resolve().parent
WORKLOAD='ch23-query-plans-v1'
CONTROL='ch23-bounded-route-fallback-v1'


def load_labels(capsules,authority,path=None):
    labels=json.loads((path or HERE/'qrels_ch23.json').read_text('utf-8'))
    if labels['capsule_manifest']!=manifest(capsules) or labels['capsule_manifest_sha256']!=digest(manifest(capsules)) or labels['authority_digest']!=authority.state_digest():
        raise ValueError('Review changed source/version/policy state')
    if labels['query_manifest_sha256']!=digest(labels['queries']):raise ValueError('Review changed original query/context/plan labels')
    for q in labels['queries']:
        normalize(q['text'])
        for req in q['requirements']:
            c=capsules[req['capsule_key']];doc=c['document'];a,z=req['canonical_span']
            if c['unit']['item_id']!=req['item_id'] or doc['body'][a:z]!=req['text'] or sha(req['text'].encode('utf-8'))!=req['text_sha256'] or locate_span(doc['blocks'],a,z)!=req['anchors']:
                raise ValueError('Changed required evidence or locator')
    registry=json.loads((ROOT/'evaluation/WORKLOAD_REGISTRY.json').read_text('utf-8'))
    entry=next((w for w in registry['workloads'] if w['workload_id']==labels['workload_id']),None)
    if not entry or any(entry[k]!=labels[k] for k in ('corpus_version','query_set_version','qrels_version','query_manifest_sha256')) or entry['source_manifest_sha256']!=digest(manifest(capsules)):
        raise ValueError('Register reviewed query workload')
    control=next((w for w in registry['workloads'] if w['workload_id']==CONTROL),None)
    if not control or control['source_manifest_sha256']!=digest(manifest(capsules)) or control['qrels_version'] is not None:
        raise ValueError('Register controlled-fault workload')
    return labels


def metrics(q,ranked,packed,plan,parent):
    required={r['item_id'] for r in q['requirements']};found={i for i,_ in ranked};context={u['item_id'] for u in packed}
    expected=q['expected_plan']
    slots=plan['predicate']==expected['predicate'] and plan['as_of_ms']==expected['as_of_ms'] and plan['kind']==expected['kind']
    decision=plan['outcome']==expected['outcome']
    return {'query_id':q['query_id'],'slice':q['slice'],'request_id':parent['request_id'],
            'positive_recall_at_2':len(required&found)/len(required) if required else None,
            'context_evidence_recall':len(required&context)/len(required) if required else None,
            'required_empty_correct':not found if q['required_empty'] else None,
            'guard_decision_correct':decision if q['guard'] else None,
            'intent_slot_correct':slots,'rule_plan_correct':slots and decision and plan['selected']==expected['selected'],
            'original_preserved':plan['original']==q['text'],
            'final_ids':list(i for i,_ in ranked),'context_ids':parent['context_ids'],
            'outcome':parent['status'],'reason':parent['reason'],
            'branch_count':len(parent['branch_request_ids']),'context':parent['stage_timings_ms'].get('context'),**parent['stage_timings_ms']}


def average(rows,key):
    values=[r[key] for r in rows if r[key] is not None]
    return sum(values)/len(values) if values else None


def percentile(values,p):return sorted(values)[math.ceil(p*len(values))-1]


def run(output,artifacts):
    capsules,authority,generation=load_state();labels=load_labels(capsules,authority)
    model,info=load_encoder(allow_download=False)
    info['encode_policy']='NFC/whitespace-normalized preserved query surface; document body-only vectors reused from trusted V6; lexical exact record slot carried separately'
    texts=[normalize(q['text']) for q in labels['queries']]
    lengths=[len(model.tokenizer(t,truncation=False)['input_ids']) for t in texts]
    if model.max_seq_length!=256 or model.tokenizer.num_special_tokens_to_add(pair=False)!=2 or max(lengths)>256:
        raise ValueError('Refuse model/input truncation')
    vector_map={};samples=[]
    encode_versions=versions(labels['corpus_version'],labels['query_set_version'],labels['qrels_version'],None,MODEL_REVISION)
    for q,text in zip(labels['queries'],texts):
        tick=perf_counter_ns();vec=list(embed(model,[text],batch_size=1)[0]);elapsed=(perf_counter_ns()-tick)/1e6
        vector_map[q['query_id']]=vec
        collector=TraceCollector(WORKLOAD,encode_versions,[])
        frame=collector.record(q['query_id'],'encode_surface',0,([],{}),{'query_encode':elapsed},status='ok')
        frame.update(surface_sha256=sha(text.encode('utf-8')),input_wordpieces_with_specials=len(model.tokenizer(text)['input_ids']))
        samples.append(frame)
    tokens={row['item_id']:len(model.tokenizer(row['text'],add_special_tokens=False)['input_ids']) for row in generation.rows.values()}
    ids=versions(labels['corpus_version'],labels['query_set_version'],labels['qrels_version'],generation.identity,MODEL_REVISION)
    observations=[];rng=random.Random(23014)
    for trial in range(3):
        cases=[(q,mode) for q in labels['queries'] for mode in MODES];rng.shuffle(cases)
        for q,mode in cases:
            result=execute(q,mode,trial,generation,authority,vector_map[q['query_id']],tokens,ids,WORKLOAD,query_contract=generation.contract)
            ranked,packed,plan,parent,frames=result
            observations.append({'mode':mode,'trial_id':trial,**metrics(q,ranked,packed,plan,parent)})
            samples.extend(frames)
    aggregates={}
    for mode in MODES:
        rows=[o for o in observations if o['mode']==mode]
        aggregates[mode]={k:average(rows,k) for k in ('positive_recall_at_2','context_evidence_recall','required_empty_correct','guard_decision_correct','intent_slot_correct','original_preserved')}
        aggregates[mode].update(requests=len(rows),route_search_p50_ms=percentile([o['route_search_total'] for o in rows],.5),
            route_search_p95_ms=percentile([o['route_search_total'] for o in rows],.95),
            query_process_p50_ms=percentile([o['query_process'] for o in rows],.5),
            query_process_p95_ms=percentile([o['query_process'] for o in rows],.95),
            eligibility_p50_ms=percentile([o['eligibility'] for o in rows],.5),packing_p50_ms=percentile([o['context'] for o in rows if o['context'] is not None],.5),
            packing_timed_requests=sum(o['context'] is not None for o in rows),
            actual_branch_attempts=sum(o['branch_count'] for o in rows),
            slices={s:{k:average([o for o in rows if o['slice']==s],k) for k in ('positive_recall_at_2','context_evidence_recall','required_empty_correct','guard_decision_correct')} for s in sorted({o['slice'] for o in rows})})
    control_samples=[];control_observations=[]
    control_ids=versions(labels['corpus_version'],'ch23-four-controlled-failure-cases-v1',None,generation.identity,MODEL_REVISION)
    scenarios=[('dense-timeout','r03',{'dense':TimeoutError}),('lexical-timeout','r01',{'lexical':TimeoutError}),
               ('both-timeout','r03',{'dense':TimeoutError,'lexical':TimeoutError}),('empty-hard-id','r12',{})]
    for name,key,faults in scenarios:
        request=next(q for q in labels['queries'] if q['query_id']==key)
        ranked,packed,plan,parent,frames=execute(request,'rule_route',0,generation,authority,vector_map[key],tokens,control_ids,CONTROL,faults=faults,query_contract=generation.contract)
        control_samples.extend(frames)
        control_observations.append({'scenario':name,'query_id':key,'request_id':parent['request_id'],
            'status':parent['status'],'reason':parent['reason'],'branch_count':len(parent['branch_request_ids']),
            'predicate_digest':parent['plan']['constraint_digest'],'final_ids':parent['final_candidate_ids']})
    payload={'source_manifest_sha256':digest(manifest(capsules)),'authority_digest':authority.state_digest(),
             'generation_identity':generation.identity,'model_contract':generation.contract,
             'query_manifest_sha256':labels['query_manifest_sha256'],'query_vectors':vector_map,'token_counts':tokens}
    artifacts.mkdir(parents=True,exist_ok=True);(artifacts/'queries.json').write_bytes((json.dumps(payload,indent=2,sort_keys=True)+'\n').encode())
    restored=json.loads((artifacts/'queries.json').read_text('utf-8'));expected=digest(payload)
    if digest(restored)!=expected:raise ValueError('Untrusted query snapshot')
    replays=0
    for q in labels['queries']:
        for mode in MODES:
            ranked,packed,plan,parent,_=execute(q,mode,-1,generation,authority,restored['query_vectors'][q['query_id']],restored['token_counts'],ids,WORKLOAD,query_contract=restored['model_contract'])
            baseline=next(o for o in observations if o['query_id']==q['query_id'] and o['mode']==mode)
            if [i for i,_ in ranked]!=baseline['final_ids'] or parent['context_ids']!=baseline['context_ids']:raise ValueError('Reload output mismatch')
            original_parent=next(s for s in samples if s['request_id']==baseline['request_id'])
            if parent['raw_candidate_ids']!=original_parent['raw_candidate_ids'] or parent['raw_candidate_scores']!=original_parent['raw_candidate_scores'] or parent['final_candidate_scores']!=original_parent['final_candidate_scores']:
                raise ValueError('Reload score sequence mismatch')
            replays+=1
    record={'workload_id':WORKLOAD,'date_utc':datetime.now(timezone.utc).isoformat(),'authoring_date':'2026-10-14',
        'question':'Do explicit query constraints and route semantics prevent wrong-evidence dispatch on the frozen V6 state?',
        'hypothesis':'Typed IDs/time/follow-up slots repair all-dense mistakes; route selection may tie constraint-dense. A coarse count trigger can reject an answerable duration query.',
        'baseline':'dense_all within current authorization, normalized original query surface, current source heads; no interpretation constraints',
        'independent_variable':'interpretation/dispatch policy bundle; constraint_dense ablation shares interpreted constraints and guards but selects dense for ready searches',
        'controls':'same authoritative final V6 source/permission state, frozen body-only backbone, normalized surface vectors, k2, context80 encoder-WordPiece proxy and frozen original queries/labels',
        'procedure':'three warm repeats, shuffled query/policy order with seed23014; 10 positives/11 spans, four required-empty and seven guard tasks; no train/dev/test or generalization claim',
        'versions':ids,'model':info,'max_query_wordpieces_with_specials':max(lengths),
        'code_sha256':{p:sha((HERE/p).read_bytes()) for p in ('query_ch23.py','retrieval_ch23.py','experiment_ch23.py')},
        'qrels_sha256':sha((HERE/'qrels_ch23.json').read_bytes()),'query_snapshot_digest':expected,
        'source_manifest_sha256':payload['source_manifest_sha256'],'query_manifest_sha256':labels['query_manifest_sha256'],
        'environment':{'python':platform.python_version(),'unicode_database':unicodedata.unidata_version,'platform':platform.platform()},
        'aggregates':aggregates,'per_query_trials':observations,'samples':samples,
        'rule_plan_accuracy_21_queries':average([o for o in observations if o['mode']=='rule_route'],'rule_plan_correct'),
        'controlled_fallback':{'workload_id':CONTROL,'cases':control_observations,'samples':control_samples},
        'query_snapshot_replay_checks':replays,
        'decision':'Keep explicit constraints and bounded capability/retry policy provisionally; preserve quantity false trigger and dense misses. Both required publication units fit the actual budget. No superiority claim for lexical route selection when constraint-dense ties it.',
        'limitations':'Fictional narrow grammar and inspected source spans/route rubric, one author, 21 questions, singleton/two-source targets, three warm repeats and prepared query vectors. Controlled immediate exception injection is not deadline behavior. No learned router, real SQL/graph/web, query generation/fusion, authentication/distributed service or answer generation.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'workload':WORKLOAD,'aggregates':{m:{k:v for k,v in a.items() if k!='slices'} for m,a in aggregates.items()},
        'rule_plan_accuracy':record['rule_plan_accuracy_21_queries'],'samples':len(samples),'controls':control_observations,'replays':replays},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'chapter-23-experiment.json')
    parser.add_argument('--artifacts',type=Path,default=HERE/'index_ch23');args=parser.parse_args();run(args.output,args.artifacts)
