"""Inspectable source-preserving boundaries and evidence-span diagnostics."""
import re
from ingestion_ch19 import digest, sha, locate_span

CHUNKER_VERSION='ch20-boundaries-1'
MODES=('char128','word24','word24-o8','word48','word96','structure48','word24-parent')


def word_windows(text,size,overlap=0):
    """Whitespace-word windows mapped to original code-point intervals."""
    if type(size) is not int or type(overlap) is not int or size<1 or not 0<=overlap<size:
        raise ValueError('Invalid size/overlap')
    words=list(re.finditer(r'\S+',text))
    result=[]
    for i in range(0,len(words),size-overlap):
        end=min(i+size,len(words))
        result.append((words[i].start(),words[end-1].end()))
        if end==len(words):break
    return result


def char_windows(text,size,overlap=0):
    if type(size) is not int or type(overlap) is not int or size<1 or not 0<=overlap<size:
        raise ValueError('Invalid size/overlap')
    out=[]
    for start in range(0,len(text),size-overlap):
        end=min(start+size,len(text))
        out.append((start,end))
        if end==len(text):break
    return out


def structure_ranges(doc,size=48):
    """Greedy parser units; heading starts a section, long prose falls back."""
    out=[];pending=None
    def flush():
        nonlocal pending
        if pending is not None:out.append(tuple(pending));pending=None
    for b in doc['blocks']:
        if b['kind']=='heading':
            flush();pending=[b['start'],b['end']]
            continue
        if b['kind'] in {'code','table_row'}:
            flush();out.append((b['start'],b['end']))
            continue
        if len(b['text'].split())>size:
            flush()
            out.extend((b['start']+a,b['start']+z) for a,z in word_windows(b['text'],size))
            continue
        if pending is not None and len(doc['body'][pending[0]:b['end']].split())>size:flush()
        if pending is None:pending=[b['start'],b['end']]
        else:pending[1]=b['end']
    flush()
    return out


def make_chunks(doc,mode,scope='support-team'):
    if scope not in doc['allowed_scopes'] or not doc['indexing_allowed']:
        return []
    if mode not in MODES:raise ValueError('Unknown chunker')
    base='word24' if mode=='word24-parent' else mode
    body=doc['body']
    ranges=(char_windows(body,128) if base=='char128' else
            structure_ranges(doc) if base=='structure48' else
            word_windows(body,96 if base=='word96' else 48 if base=='word48' else 24,8 if base=='word24-o8' else 0))
    result=[]
    for a,z in ranges:
        if not body[a:z].strip():continue
        identity={'source_id':doc['source_id'],'record_digest':doc['record_digest'],
            'chunker_version':CHUNKER_VERSION,'mode':base,'canonical_span':[a,z]}
        result.append({**identity,'item_id':doc['source_id']+':'+digest(identity)[:20],
            'text':body[a:z],'text_sha256':sha(body[a:z].encode('utf-8')),
            'source_version':doc['source_version'],'source_sha256':doc['source_sha256'],
            'allowed_scopes':doc['allowed_scopes'],'anchors':locate_span(doc['blocks'],a,z),
            'parent_id':doc['source_id']+':parent:'+doc['record_digest'][:16]})
    return result


def merge_intervals(intervals):
    out=[]
    for a,z in sorted(intervals):
        if type(a) is not int or type(z) is not int or a<0 or a>=z:
            raise ValueError('Invalid interval')
        if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
        else:out.append([a,z])
    return out


def source_positions(units,docs,aliases):
    union=set();total=0
    for unit in units:
        source=unit['source_id'];a,z=unit['canonical_span']
        doc=docs[source]
        if not 0<=a<z<=len(doc['body']):raise ValueError('Invalid unit map')
        positions={(aliases.get(source,source),i) for i in range(a,z) if not doc['body'][i].isspace()}
        total+=len(positions);union.update(positions)
    return union,total


def evidence_metrics(units,requirements,docs,aliases):
    covered,total=source_positions(units,docs,aliases)
    required=set();complete=[];details=[]
    for req in requirements:
        a,z=req['canonical_span'];source=req['source_id']
        positions={(aliases.get(source,source),i) for i in range(a,z) if not docs[source]['body'][i].isspace()}
        if not positions:raise ValueError('Empty evidence requirement')
        required.update(positions)
        is_complete=positions<=covered;complete.append(is_complete)
        details.append({'requirement_id':req['requirement_id'],'complete':is_complete,
            'covered_codepoints':len(positions&covered),'required_codepoints':len(positions),
            'contributing_item_ids':[u['item_id'] for u in units
                if aliases.get(u['source_id'],u['source_id'])==aliases.get(source,source)
                and max(u['canonical_span'][0],a)<min(u['canonical_span'][1],z)]})
    return {'evidence_recall':sum(complete)/len(complete) if complete else None,
        'complete_answer_evidence':all(complete) if complete else None,
        'required_span_coverage':len(required&covered)/len(required) if required else None,
        'context_evidence_precision':len(required&covered)/len(covered) if required and covered else None,
        'duplicate_source_fraction':1-len(covered)/total if total else 0,
        'emitted_source_codepoints':total,'unique_source_codepoints':len(covered),
        'requirement_details':details}


def pack_context(ranked,lookup,docs,budget,token_counts,parent=False,scope='support-team'):
    if type(budget) is not int or budget<0:raise ValueError('Invalid budget')
    selected=[];attempts=[];seen=set();used=0
    for child_id,score in ranked:
        child=lookup[child_id]
        if scope not in child['allowed_scopes']:raise ValueError('Ineligible child before expansion')
        doc=docs[child['source_id']]
        if scope not in doc['allowed_scopes'] or not doc['indexing_allowed']:
            raise ValueError('Ineligible parent before fetch')
        id=child['parent_id'] if parent else child_id
        unit=({'item_id':id,'source_id':doc['source_id'],'canonical_span':[0,len(doc['body'])],
               'anchors':doc['blocks'],'allowed_scopes':doc['allowed_scopes']} if parent else child)
        reason='duplicate_parent' if id in seen else 'budget' if used+token_counts[id]>budget else 'selected'
        attempts.append({'child_id':child_id,'context_unit_id':id,'score':score,
            'token_count':token_counts[id],'reason':reason,'canonical_span':unit['canonical_span']})
        seen.add(id)
        if reason=='selected':selected.append(unit);used+=token_counts[id]
    return selected,{'packing_attempts':attempts,'used_encoder_wordpieces':used,
                     'context_unit_ids':[u['item_id'] for u in selected]}
