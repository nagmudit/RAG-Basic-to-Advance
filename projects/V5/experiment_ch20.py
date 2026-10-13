"""Matched exact-dense chunk boundary experiment; generation remains unrun."""
import argparse
import json
import math
import platform
import random
import sys
from datetime import datetime,timezone
from pathlib import Path
from time import perf_counter_ns
import numpy as np
from ingestion_ch19 import ingest,digest,sha,locate_span
from experiment_ch19 import load_requirements
from chunking_ch20 import MODES,make_chunks,evidence_metrics,pack_context,CHUNKER_VERSION

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'projects/common'))
from experiment_trace import TraceCollector,versions,validate
sys.path.insert(0,str(ROOT/'projects/V3'))
from experiment_ch11 import load_encoder,embed,MODEL_REVISION

WORKLOAD='ch20-chunked-evidence-v1'
CORPUS='ch20-canonical-five-source-v1'
QUERIES='ch20-twelve-evidence-probes-v1'
QRELS='ch20-independent-source-spans-v1'
SCOPE='support-team'
K=3
BUDGET=80


def load_documents():
    descriptors=json.loads((HERE/'fixtures/sources.json').read_text(encoding='utf-8'))
    load_requirements(HERE/'fixtures',descriptors)
    documents=json.loads((HERE/'canonical_ch19/structured.json').read_text(encoding='utf-8'))
    originals={s['source_id']:s for s in descriptors}
    for doc in documents:
        if digest({k:v for k,v in doc.items() if k!='record_digest'})!=doc['record_digest']:
            raise ValueError('Canonical record changed')
        fresh=ingest(HERE/'fixtures',originals[doc['source_id']],SCOPE)
        if fresh.get('record_digest')!=doc['record_digest']:
            raise ValueError('Pinned source/parser/canonical mismatch')
    desc=json.loads((HERE/'source_descriptor_ch20.json').read_text(encoding='utf-8'))
    new=ingest(HERE/'fixtures_ch20',desc,SCOPE)
    if new['status']!='accepted':raise ValueError('New source quality gate failed')
    return documents+[new]


def manifest(documents):
    return [{k:doc[k] for k in ('source_id','source_version','source_sha256','record_digest',
             'body_sha256','allowed_scopes','license','indexing_allowed','retention_policy')}
             for doc in sorted(documents,key=lambda r:r['source_id'])]


def load_labels(documents):
    for doc in documents:
        if digest({k:v for k,v in doc.items() if k!='record_digest'})!=doc['record_digest'] or sha(doc['body'].encode('utf-8'))!=doc['body_sha256']:
            raise ValueError('Changed canonical content/identity')
    labels=json.loads((HERE/'evidence_spans_ch20.json').read_text(encoding='utf-8'))
    if labels['version']!=QRELS or labels['query_set_version']!=QUERIES or labels['source_manifest']!=manifest(documents):
        raise ValueError('Review changed source or label version')
    docs={d['source_id']:d for d in documents}
    if labels['source_manifest_sha256']!=digest(manifest(documents)):
        raise ValueError('Manifest digest mismatch')
    # Alias equality includes policy; it is not a cross-tenant text merge.
    for alias,representative in labels['aliases'].items():
        a,b=docs[alias],docs[representative]
        if any(a[k]!=b[k] for k in ('body_sha256','allowed_scopes','license','retention_policy')):
            raise ValueError('Changed alias equality/policy')
    for q in labels['queries']:
        for req in q['requirements']:
            doc=docs[req['source_id']];a,z=req['canonical_span']
            if not 0<=a<z<=len(doc['body']) or doc['body'][a:z]!=req['text'] or sha(req['text'].encode('utf-8'))!=req['text_sha256']:
                raise ValueError('Changed required evidence span')
            if req['anchors']!=locate_span(doc['blocks'],a,z):
                raise ValueError('Changed required source locator')
    return labels


def dense_search(rows,query,k=K,scope=SCOPE):
    if type(k) is not int or k<1 or len(query)!=384 or not all(math.isfinite(float(x)) for x in query):
        raise ValueError('Invalid query/cutoff')
    scored=[]
    for row in rows:
        if scope not in row['allowed_scopes']:continue
        vector=row['vector']
        if len(vector)!=384 or not all(math.isfinite(float(x)) for x in vector):
            raise ValueError('Invalid stored vector')
        score=sum(float(x)*float(y) for x,y in zip(vector,query))
        scored.append((row['item_id'],score))
    scored.sort(key=lambda p:(-p[1],p[0]))
    return scored[:k],{'candidate_stages':{'scored':scored}}


def token_length(model,text,special=False):
    return len(model.tokenizer(text,add_special_tokens=special,truncation=False)['input_ids'])


def verify_snapshot(snapshot,documents,expected_digest):
    if snapshot['index_manifest_digest']!=expected_digest or digest({k:v for k,v in snapshot.items() if k!='index_manifest_digest'})!=expected_digest:
        raise ValueError('Untrusted or changed chunk index')
    if snapshot['model_revision']!=MODEL_REVISION or snapshot['source_manifest']!=manifest(documents):
        raise ValueError('Changed model/source/eligibility contract')
    docs={d['source_id']:d for d in documents}
    for mode,index in snapshot['indexes'].items():
        base='word24' if mode=='word24-parent' else mode
        expected=make_chunks_for_mode(documents,base)
        if len(expected)!=len(index['rows']):raise ValueError('Changed chunk roster')
        for unit,row in zip(expected,index['rows']):
            if any(row.get(k)!=v for k,v in unit.items()):raise ValueError('Changed chunk content/map')
            if len(row['vector'])!=384 or not all(math.isfinite(x) for x in row['vector']) or abs(sum(x*x for x in row['vector'])-1)>.0001:
                raise ValueError('Invalid normalized stored vector')
        if index['index_version']!=digest({'model':MODEL_REVISION,'chunker':CHUNKER_VERSION,'mode':base,'rows':index['rows']}):
            raise ValueError('Changed index identity')
    return snapshot


def make_chunks_for_mode(documents,mode):
    return [c for d in documents for c in make_chunks(d,mode,SCOPE)]


def percentile(values,p):
    return sorted(values)[max(0,math.ceil(len(values)*p)-1)]


def run(output,artifacts):
    documents=load_documents();docs={d['source_id']:d for d in documents}
    labels=load_labels(documents)
    model,model_info=load_encoder(allow_download=False)
    model_info['encode_policy']='canonical chunk body only; shared frozen encoder; normalized float32; no added heading/summary'
    if model.max_seq_length!=256:raise ValueError('Changed encoder limit')
    if model.tokenizer.num_special_tokens_to_add(pair=False)!=2:
        raise ValueError('Changed special-token contract')
    indexes={};builds={};vectors={};all_chunks=[];token_counts={}
    for mode in MODES:
        if mode=='word24-parent':
            indexes[mode]=indexes['word24'];builds[mode]={'reuse_of':'word24','new_vectors':0}
            continue
        tick=perf_counter_ns()
        chunks=[c for d in documents for c in make_chunks(d,mode,SCOPE)]
        split_ms=(perf_counter_ns()-tick)/1e6
        lengths=[token_length(model,c['text'],True) for c in chunks]
        if any(n>model.max_seq_length for n in lengths):
            raise ValueError('Refuse silent embedding truncation')
        tick=perf_counter_ns();matrix=embed(model,[c['text'] for c in chunks],batch_size=16)
        embed_ms=(perf_counter_ns()-tick)/1e6
        rows=[]
        for c,v,n in zip(chunks,matrix,lengths):
            row={**c,'vector':v,'encoder_wordpieces_with_special':n}
            rows.append(row);all_chunks.append(c);token_counts[c['item_id']]=n-2
        version=digest({'model':MODEL_REVISION,'chunker':CHUNKER_VERSION,'mode':mode,'rows':rows})
        indexes[mode]={'rows':rows,'index_version':version}
        builds[mode]={'chunk_count':len(rows),'split_ms':split_ms,'embed_ms':embed_ms,
            'max_encoder_input_with_special':max(lengths),'encoder_input_wordpieces_with_special':sum(lengths),
            'float32_vector_payload_bytes':len(rows)*384*4,'index_version':version}
    for d in documents:token_counts[d['source_id']+':parent:'+d['record_digest'][:16]]=token_length(model,d['body'])
    eligible={c['item_id'] for c in all_chunks}|set(token_counts)
    trace=TraceCollector(WORKLOAD,versions(CORPUS,QUERIES,QRELS,None,MODEL_REVISION),eligible)
    query_vectors={}
    for q in labels['queries']:
        with trace.guard(q['query_id'],'query_encode',0):
            if token_length(model,q['question'],True)>model.max_seq_length:
                raise ValueError('Refuse query truncation')
            tick=perf_counter_ns();query_vectors[q['query_id']]=embed(model,[q['question']],batch_size=1)[0]
        trace.record(q['query_id'],'query_encode',0,([],{}),{'query_encode':(perf_counter_ns()-tick)/1e6},
            status='ok',reason='candidate_search_not_run')
    lookup={c['item_id']:c for c in all_chunks}
    jobs=[(mode,q,trial) for mode in MODES for q in labels['queries'] for trial in range(3)]
    random.Random(20013026).shuffle(jobs)
    cases={};times={mode:[] for mode in MODES}
    for mode,q,trial in jobs:
        with trace.guard(q['query_id'],mode,trial):
            tick=perf_counter_ns();ranked,work=dense_search(indexes[mode]['rows'],query_vectors[q['query_id']])
            search_ms=(perf_counter_ns()-tick)/1e6
            tick=perf_counter_ns();context,packing=pack_context(ranked,lookup,docs,BUDGET,token_counts,parent=mode=='word24-parent')
            pack_ms=(perf_counter_ns()-tick)/1e6
            rec=trace.record(q['query_id'],mode,trial,(ranked,work),{'exact_dense':search_ms,'whole_unit_pack':pack_ms},context=packing['context_unit_ids'])
            rec['index_version']=indexes[mode]['index_version']
            rec.update({'chunker_version':CHUNKER_VERSION,'context_budget_encoder_wordpieces':BUDGET,
                **packing,'timing_boundary':'precomputed query; search and whole-unit packing separate; quality/trace serialization excluded'})
            validate(rec,eligible)
        times[mode].append([search_ms,pack_ms])
        if trial==0:
            candidate=evidence_metrics([lookup[id] for id,_ in ranked],q['requirements'],docs,labels['aliases'])
            selected=evidence_metrics(context,q['requirements'],docs,labels['aliases'])
            cases[(mode,q['query_id'])]={'query_id':q['query_id'],'slice':q['slice'],
                'request_id':rec['request_id'],'candidate':candidate,'context':selected,
                'candidate_ids':[id for id,_ in ranked],'context_ids':rec['context_ids'],
                'packing_attempts':packing['packing_attempts'],'context_encoder_wordpieces':packing['used_encoder_wordpieces'],
                'answer_correctness':None,'faithfulness':None,'citation_support':None,'abstention':None}
    summaries={}
    for mode in MODES:
        rows=[cases[(mode,q['query_id'])] for q in labels['queries']]
        positive=[r for r in rows if r['candidate']['evidence_recall'] is not None]
        negative=[r for r in rows if r['candidate']['evidence_recall'] is None]
        summaries[mode]={'workload_id':WORKLOAD,'positive_queries':len(positive),'no_evidence_queries':len(negative),
            'candidate_evidence_recall_at_3':sum(r['candidate']['evidence_recall'] for r in positive)/len(positive),
            'context_evidence_recall':sum(r['context']['evidence_recall'] for r in positive)/len(positive),
            'complete_context_evidence_rate':sum(r['context']['complete_answer_evidence'] for r in positive)/len(positive),
            'mean_context_duplicate_source_fraction':sum(r['context']['duplicate_source_fraction'] for r in rows)/len(rows),
            'no_evidence_candidate_return_rate':sum(bool(r['candidate_ids']) for r in negative)/len(negative),
            'search_samples':len(times[mode]),'exact_search_p95_ms':percentile([t[0] for t in times[mode]],.95),
            'pack_p95_ms':percentile([t[1] for t in times[mode]],.95),'cases':rows}
    artifacts=Path(artifacts);artifacts.mkdir(parents=True,exist_ok=True)
    index_record={'schema':'ch20-exact-chunks-1','model_revision':MODEL_REVISION,'source_manifest':manifest(documents),
        'chunker_version':CHUNKER_VERSION,'indexes':indexes,'token_counts':token_counts,'query_vectors':query_vectors}
    index_record['index_manifest_digest']=digest(index_record)
    (artifacts/'index.json').write_bytes((json.dumps(index_record,ensure_ascii=False)+'\n').encode('utf-8'))
    (artifacts/'documents.json').write_bytes((json.dumps(documents,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    reloaded=verify_snapshot(json.loads((artifacts/'index.json').read_text(encoding='utf-8')),documents,index_record['index_manifest_digest'])
    replay_checks=0
    for mode in MODES:
        for q in labels['queries']:
            rows,_=dense_search(reloaded['indexes'][mode]['rows'],reloaded['query_vectors'][q['query_id']])
            if [id for id,_ in rows]!=cases[(mode,q['query_id'])]['candidate_ids']:
                raise ValueError('Reloaded candidate mismatch')
            replay_checks+=1
    record={'experiment_id':'ch20-chunking-comparison-1','date':'2026-10-13','timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'workload_id':WORKLOAD,'versions':versions(CORPUS,QUERIES,QRELS,None,MODEL_REVISION),
        'question':'Which boundaries preserve required source evidence at fixed candidate depth and context budget?',
        'hypothesis':'Overlap may improve boundary coverage while adding duplicate context; larger chunks and whole-parent expansion may lose context under the same budget.',
        'baseline':'word24, no overlap, exact frozen dense search, top3, whole-unit budget80 encoder WordPieces',
        'independent_variable':'boundary policy/size/overlap; word24-parent changes expansion only with shared child index',
        'controls':['same five accepted source records and twelve inspected questions','same independent source-span requirements and alias policy','same model/input normalization and exact scorer','k3 and budget80; no reranker or generator','no OCR repair of Chapter19 quarantines'],
        'procedure':'build each base once; query-encode once; three shuffled requests/query/mode seed20013026; no tuning/held-out split',
        'acceptance_gate':'source/record/requirement identity validates; chunk text/maps agree; no silent truncation or authorization regression. Selection is provisional on inspected probes, not universal gain.',
        'model':model_info,'environment':{'python':platform.python_version(),'numpy':np.__version__},
        'source_manifest_sha256':digest(manifest(documents)),
        'qrels_file_sha256':sha((HERE/'evidence_spans_ch20.json').read_bytes().replace(b'\r\n',b'\n')),
        'code_sha256':{p.name:sha(p.read_bytes().replace(b'\r\n',b'\n')) for p in [HERE/'chunking_ch20.py',Path(__file__)]},
        'builds':builds,'summaries':summaries,'request_samples':trace.records,
        'uncertainty':'Twelve single-author inspected questions; ten positives/two no-evidence. Three tiny timing repeats, one corpus/model; no CI/generalization/production claim.',
        'index_manifest_digest':index_record['index_manifest_digest'],
        'reload_candidate_parity_checks':replay_checks,
        'decision':'Provisionally retain structure48 for V5 development on this inspected workload, while keeping all exact snapshots and failures. No generator, OCR, learned semantic splitter, RAPTOR, contextual rewriting or late-chunking model is run.'}
    Path(output).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    for mode,s in summaries.items():print(mode,{k:s[k] for k in ['candidate_evidence_recall_at_3','context_evidence_recall','complete_context_evidence_rate','mean_context_duplicate_source_fraction']})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(HERE/'chapter-20-experiment-local.json'))
    p.add_argument('--artifacts',default=str(ROOT/'build/ch20-local-index'))
    args=p.parse_args();run(args.output,args.artifacts)
