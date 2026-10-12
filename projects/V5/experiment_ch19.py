"""Frozen extraction-quality comparison and lexical source diagnostic."""
import argparse
import json
import math
import platform
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns
import fitz
from ingestion_ch19 import ingest, digest, sha, duplicate_groups, locate_span, PARSER_VERSION

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(ROOT/'projects/common'))
from experiment_trace import TraceCollector, versions

WORKLOAD = 'ch19-source-quality-v1'
CORPUS = 'ch19-authored-three-format-v1'
QUESTIONS = 'ch19-eight-source-span-probes-v1'
QRELS = 'ch19-source-span-requirements-v1'
SCOPE = 'support-team'


def binding(directory, sources):
    # Excluded policies/contents are not copied into the judged/ordinary manifest.
    return [{'source_id':s['source_id'],'source_version':s['source_version'],'path':s['path'],
             'sha256':sha((directory/s['path']).read_bytes()),
             'allowed_scopes':sorted(s['allowed_scopes']),'license':s['license'],
             'indexing_allowed':s['indexing_allowed'],'retention_policy':s['retention_policy']}
            for s in sources if SCOPE in s['allowed_scopes'] and s['indexing_allowed'] and s['license']]


def load_requirements(directory, sources):
    labels=json.loads((HERE/'span_requirements.json').read_text(encoding='utf-8'))
    if labels['source_manifest'] != binding(directory,sources) or labels['manifest_sha256'] != digest(labels['source_manifest']):
        raise ValueError('Source/content/policy changed: review span requirements')
    if labels['version'] != QRELS or labels['query_set_version'] != QUESTIONS:
        raise ValueError('Question/label version mismatch')
    return labels


def rank(records, query, k=1):
    terms=set(re.findall(r'[\w-]+',query.lower()))
    pairs=[]
    for r in records:
        if r['status']=='accepted' and SCOPE in r['allowed_scopes']:
            score=len(terms & set(re.findall(r'[\w-]+',r['body'].lower())))
            pairs.append((r['source_id'],float(score)))
    pairs.sort(key=lambda p:(-p[1],p[0]))
    positive=[pair for pair in pairs if pair[1]>0]
    return positive[:k],{'candidate_stages':{'scored':pairs,'positive_score':positive}}


def percentile(values,p):
    ordered=sorted(values)
    return ordered[max(0,math.ceil(p*len(ordered))-1)]


def run(output, canonical):
    directory=HERE/'fixtures'
    sources=json.loads((directory/'sources.json').read_text(encoding='utf-8'))
    labels=load_requirements(directory,sources)
    eligible={s['source_id'] for s in sources if SCOPE in s['allowed_scopes'] and s['indexing_allowed'] and s['license']}
    identity=versions(CORPUS,QUESTIONS,QRELS,None,None)
    trace=TraceCollector(WORKLOAD,identity,eligible)
    quality, ingest_samples, snapshots={},[],{}
    jobs=[(mode,trial,slot,s) for mode in ['flat','structured'] for trial in range(3) for slot,s in enumerate(sources)]
    random.Random(19013026).shuffle(jobs)
    for mode,trial,slot,s in jobs:
        tick=perf_counter_ns()
        with trace.guard(f'ingest-slot-{slot}',mode,trial):
            r=ingest(directory,s,SCOPE,mode)
        elapsed=(perf_counter_ns()-tick)/1e6
        event=trace.record(f'ingest-slot-{slot}',mode,trial,([],{}),{'ingest_adapter':elapsed},
            status=r['status'],reason=r['reason'])
        event.update({'operation':'ingestion','source_id':r.get('source_id'),
            'source_version':s['source_version'] if r.get('source_id') else None,
            'source_sha256':r.get('source_sha256'),'parser_version':PARSER_VERSION,
            'normalization_version':r.get('normalization_version'),
            'normalized_block_ids':[b['block_id'] for b in r.get('blocks',[])],
            'normalization_inputs_retained_in':'access-controlled canonical artifact' if r.get('blocks') else None,
            'published_block_ids':[b['block_id'] for b in r.get('blocks',[])],
            'dropped_regions':r.get('dropped_regions',[]),
            'record_digest':r.get('record_digest'),
            'not_run':['queue','OCR','chunk_design','embedding','index_write','visibility'],
            'timing_boundary':'file read, parsing and canonicalization; trace/output serialization excluded'})
        ingest_samples.append(event)
        snapshots.setdefault(mode,{})[slot]=r
    for mode in ['flat','structured']:
        records=[snapshots[mode][i] for i in range(len(sources))]
        cases=[]
        for q in labels['probes']:
            found=[]
            for r in records:
                if r['status']!='accepted' or r['source_id'] not in q['source_ids']:
                    continue
                for b in r['blocks']:
                    if q['required_text'] in b['text']:
                        start=b['start']+b['text'].index(q['required_text'])
                        anchors=locate_span(r['blocks'],start,start+len(q['required_text']))
                        found.append({'source_id':r['source_id'],'record_digest':r['record_digest'],
                            'canonical_span':[start,start+len(q['required_text'])],
                            'anchors':anchors,'traceable':not b['locator'].get('file_only',False)})
            ranked,rec=trace.execute(q['query_id'],mode,0,lambda r=records,q=q:rank(r,q['query']),stage='lexical_source_diagnostic')
            rec['index_version']=f'{mode}-canonical-documents-'+digest([r.get('record_digest') for r in records])
            cases.append({'query_id':q['query_id'],'slice':q['slice'],'preserved':bool(found),
                'traceable':any(f['traceable'] for f in found),'matches':found,
                'source_hit_at_1':bool(ranked[0] and ranked[0][0][0] in q['source_ids']),
                'final_candidate_ids':rec['final_candidate_ids'],'context_ids':None,
                'answer_correctness':None,'faithfulness':None,'citation_support':None,'abstention':None})
        times=[s['stage_timings_ms']['ingest_adapter'] for s in ingest_samples if s['mode']==mode]
        searches=[s['stage_timings_ms']['lexical_source_diagnostic'] for s in trace.records if s['mode']==mode and 'lexical_source_diagnostic' in s['stage_timings_ms']]
        quality[mode]={'workload_id':WORKLOAD,'cases':cases,'probe_count':len(cases),
            'preservation_rate':sum(c['preserved'] for c in cases)/len(cases),
            'traceable_preservation_rate':sum(c['traceable'] for c in cases)/len(cases),
            'source_hit_at_1':sum(c['source_hit_at_1'] for c in cases)/len(cases),
            'source_dispositions':{state:sum(r['status']==state for r in records) for state in ['accepted','quarantined','blocked']},
            'duplicate_groups':duplicate_groups(records),
            'ingest_samples':len(times),'ingest_adapter_p50_ms':percentile(times,.5),'ingest_adapter_p95_ms':percentile(times,.95),
            'diagnostic_search_samples':len(searches),'diagnostic_search_p95_ms':percentile(searches,.95)}
    canonical=Path(canonical)
    canonical.mkdir(parents=True,exist_ok=True)
    for mode in ['flat','structured']:
        accepted=[r for _,r in sorted(snapshots[mode].items()) if r['status']=='accepted']
        (canonical/f'{mode}.json').write_bytes((json.dumps(accepted,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    record={'experiment_id':'ch19-ingestion-quality-1','date':'2026-10-13',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),'workload_id':WORKLOAD,
        'question':'Does preserving format structure retain source-bound evidence and actionable provenance?',
        'hypothesis':'Structured adapters preserve table relations and NFC spans, with some deliberate quarantines; no complete recall claim.',
        'baseline':'flat extracted text, whitespace collapse, file-only anchors; same scope/rights gate',
        'independent_variable':'adapter/normalization bundle (not an isolated parser-only ablation)',
        'controls':['same nine source descriptors and bytes','same eight authored inspected probes','same scope/rights rules','same lexical diagnostic','no OCR/encoder/ANN/generation'],
        'versions':identity,'source_manifest_sha256':labels['manifest_sha256'],
        'span_requirements_sha256':sha((HERE/'span_requirements.json').read_bytes().replace(b'\r\n',b'\n')),
        'code_sha256':{p.name:sha(p.read_bytes().replace(b'\r\n',b'\n')) for p in [HERE/'ingestion_ch19.py',Path(__file__)]},
        'environment':{'python':platform.python_version(),'pymupdf':fitz.VersionBind,'unicode_database':__import__('unicodedata').unidata_version},
        'procedure':'quality on frozen authored probes; three randomized adapter trials per descriptor, seed19013026; one diagnostic search/query/mode; no tuning/test split',
        'acceptance_gate':'Trace every retained required span to a source-bound region; no unauthorized/unapproved read; quarantine detected ambiguity. Gate does not demand 100% extraction coverage.',
        'summaries':quality,'request_samples':trace.records,
        'uncertainty':'No confidence intervals; three tiny local ingestion repeats, one warm lexical diagnostic per query; no service/load/generalization claim.',
        'decision':'Use structured canonical corpus for V5 development, retain flat comparison, quarantine scan/invalid bytes/merged table and preserve duplicate aliases. No replacement of historical V0/V3/V4 corpus.',
        'limitations':['seven licensed eligible inputs; two policy blocks','authored inspected corpus/probes, not production or held-out evaluation','strict limited dialect; fixture-specific PDF margins','no OCR or layout model; fully scanned file quarantined','no generation/context/abstention assessment','canonical IDs differ by extraction mode; source-span requirements are not complete graded block qrels']}
    Path(output).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    for mode,summary in quality.items():
        print(mode,{k:summary[k] for k in ['workload_id','preservation_rate','traceable_preservation_rate','source_hit_at_1','source_dispositions','ingest_adapter_p95_ms']})


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(HERE/'chapter-19-experiment-local.json'))
    parser.add_argument('--canonical',default=str(ROOT/'build/ch19-local-canonical'))
    args=parser.parse_args()
    run(args.output,args.canonical)
