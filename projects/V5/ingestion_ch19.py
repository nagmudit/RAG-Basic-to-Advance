"""Bounded format adapters and source-bound canonical records, not a crawler."""
import hashlib
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
import fitz

PARSER_VERSION = 'ch19-bounded-adapters-1'
NORMALIZATION_VERSION = 'nfc-prose-space-code-preserve-1'


class QualityError(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':')).encode('utf-8'))


def normalize(text, kind='prose'):
    text = unicodedata.normalize('NFC', text.replace('\r\n','\n').replace('\r','\n'))
    return text.strip('\n') if kind == 'code' else ' '.join(text.split())


def locate_span(blocks, start, end):
    """Return whole source anchors for canonical-code-point intersections."""
    previous = 0
    for block in blocks:
        a, b = block['start'], block['end']
        if type(a) is not int or type(b) is not int or a < previous or b <= a:
            raise ValueError('Invalid ordered block map')
        previous = b
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= previous:
        raise ValueError('Invalid canonical span')
    return [{'block_id': b['block_id'], 'canonical_overlap': [max(start,b['start']), min(end,b['end'])],
             'locator': b['locator']} for b in blocks if max(start,b['start']) < min(end,b['end'])]


def markdown_blocks(text):
    """Line-anchored miniature dialect: headings, paragraphs and fenced code."""
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        first = i
        if lines[i].startswith('```'):
            i += 1
            first_code = i
            while i < len(lines) and not lines[i].startswith('```'):
                i += 1
            if i == len(lines):
                raise ValueError('Unclosed code fence')
            raw, kind = '\n'.join(lines[first_code:i]), 'code'
            i += 1
        elif re.match(r'^#{1,6} ', lines[i]):
            raw, kind = re.sub(r'^#{1,6} ', '', lines[i]), 'heading'
            i += 1
        else:
            kind = 'prose'
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6} |```)',lines[i]):
                i += 1
            raw = '\n'.join(lines[first:i])
        out.append((raw,kind,{'format':'markdown','line_start':first+1,'line_end':i}))
    return out, []


class HTMLBlocks(HTMLParser):
    """Explicit fixture dialect; no JS/CSS layout, networking or browser DOM."""
    VOID = {'br','img','hr','meta','link','input','wbr','source','area','base','embed','param','track','col'}
    BLOCK = {'p','h1','h2','h3','li','pre','tr'}
    SKIP = {'head','nav','footer','script','style'}

    def __init__(self, flat=False):
        super().__init__(convert_charrefs=True)
        self.flat, self.stack, self.out, self.dropped = flat, [], [], []
        self.active, self.parts, self.cell, self.cells, self.headers = None, [], None, [], None
        self.all_data = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = tag in self.SKIP or 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
        skip = hidden or any(s[1] for s in self.stack)
        if tag not in self.VOID:
            self.stack.append((tag,skip))
        if self.flat:
            return
        if hidden and not any(s[1] for s in self.stack[:-1]):
            self.dropped.append({'reason':'excluded_html_region','locator':{'tag':tag,'line':self.getpos()[0]}})
        if skip:
            return
        if tag == 'table':
            self.headers = None
        if tag in self.BLOCK:
            if self.active is not None:
                raise ValueError('Nested unsupported content block')
            self.active = (tag, {'format':'html','tag':tag,'id':attrs.get('id'), 'line':self.getpos()[0]})
            self.parts, self.cells = [], []
        if tag in {'td','th'}:
            if attrs.get('rowspan','1') != '1' or attrs.get('colspan','1') != '1' or self.cell is not None:
                raise QualityError('ambiguous_table_geometry')
            self.cell = (tag,[])
        if tag == 'br' and self.active:
            self.parts.append('\n')

    def handle_data(self, data):
        if self.flat:
            self.all_data.append(data)
        elif not any(s[1] for s in self.stack):
            if self.cell is not None:
                self.cell[1].append(data)
            elif self.active is not None:
                self.parts.append(data)
            elif data.strip():
                raise ValueError('Unanchored unsupported HTML text')

    def handle_endtag(self, tag):
        if self.flat:
            return
        if not self.stack or self.stack[-1][0] != tag:
            raise ValueError('Mismatched HTML structure')
        skip = self.stack.pop()[1]
        if skip:
            return
        if tag in {'td','th'}:
            if self.cell is None:
                raise ValueError('Missing table cell')
            self.cells.append((self.cell[0], normalize(''.join(self.cell[1]))))
            self.cell = None
        if self.active and tag == self.active[0]:
            kind = 'code' if tag == 'pre' else 'heading' if tag.startswith('h') else 'prose'
            locator = self.active[1]
            if tag == 'tr':
                if not self.cells:
                    raise ValueError('Empty table row')
                if all(t == 'th' for t,_ in self.cells):
                    self.headers = [v for _,v in self.cells]
                    raw,kind = ' | '.join(self.headers),'table_header'
                else:
                    if self.headers is None or len(self.headers) != len(self.cells) or not all(t=='td' for t,_ in self.cells):
                        raise ValueError('Unsupported table header association')
                    raw,kind = '; '.join(f'{h}={v}' for h,(_,v) in zip(self.headers,self.cells)), 'table_row'
                    locator['headers'] = self.headers
            else:
                raw = ''.join(self.parts)
            self.out.append((raw,kind,locator))
            self.active = None

    def finish(self, text):
        self.feed(text)
        self.close()
        if self.flat:
            return [(' '.join(self.all_data),'prose',{'format':'html','file_only':True})], []
        if self.stack or self.active:
            raise ValueError('Unclosed HTML structure')
        return self.out, self.dropped


def pdf_blocks(data, flat=False):
    out,dropped = [],[]
    with fitz.open(stream=data,filetype='pdf') as pdf:
        if pdf.is_encrypted:
            raise ValueError('Encrypted PDF')
        for page in pdf:
            rows = [r for r in page.get_text('blocks',sort=True) if r[6] == 0 and r[4].strip()]
            if not rows:
                raise QualityError('native_text_absent_requires_ocr_review')
            for x0,y0,x1,y1,text,number,_ in rows:
                loc={'format':'pdf','page':page.number+1,'bbox':[x0,y0,x1,y1],
                     'coordinate_system':'unrotated-pymupdf-top-left-points','block_number':number}
                # Fixture-only reviewed margins; not a generic header detector.
                if not flat and (y1 < 50 or y0 > page.rect.height-50):
                    dropped.append({'reason':'reviewed_fixture_margin','locator':loc})
                else:
                    out.append((text,'prose',loc))
    if flat:
        return [(' '.join(x[0] for x in out),'prose',{'format':'pdf','file_only':True})],[]
    return out,dropped


def ingest(root, source, scope, mode='structured'):
    """Check policy BEFORE path resolution/read; failures have redacted reasons."""
    if scope not in source['allowed_scopes']:
        return {'status':'blocked','reason':'ineligible','source_id':None}
    if not source['indexing_allowed'] or not source['license']:
        return {'status':'blocked','reason':'indexing_use_unapproved','source_id':None}
    root = Path(root).resolve()
    path = (root/source['path']).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Source outside fixture root')
    data = path.read_bytes()
    raw_sha = sha(data)
    try:
        if mode not in {'flat','structured'}:
            raise ValueError('Invalid adapter mode')
        if path.suffix == '.pdf':
            extracted,dropped = pdf_blocks(data,mode=='flat')
        else:
            text = data.decode('utf-8',errors='strict')
            if path.suffix == '.html':
                extracted,dropped = HTMLBlocks(mode=='flat').finish(text)
            elif path.suffix == '.md':
                extracted,dropped = ([(text,'prose',{'format':'markdown','file_only':True})],[]) if mode=='flat' else markdown_blocks(text)
            else:
                raise ValueError('Unsupported format')
    except (ValueError,UnicodeError,fitz.FileDataError,RuntimeError) as exc:
        reason = exc.reason if isinstance(exc,QualityError) else 'invalid_utf8' if isinstance(exc,UnicodeError) else 'parse_or_quality_review_required'
        return {'status':'quarantined','reason':reason,
                'source_id':source['source_id'],'source_sha256':raw_sha}
    blocks, offset = [],0
    for raw,kind,locator in extracted:
        text = normalize(raw,kind) if mode=='structured' else ' '.join(raw.split())
        if not text:
            continue
        block_id = f"{source['source_id']}:b{len(blocks)}"
        blocks.append({'block_id':block_id,'text':text,'kind':kind,'start':offset,
            'end':offset+len(text),'locator':locator,'raw_extracted_text':raw,
            'raw_extracted_sha256':sha(raw.encode('utf-8'))})
        offset += len(text)+2
    if not blocks:
        return {'status':'quarantined','reason':'empty_extraction','source_id':source['source_id'],'source_sha256':raw_sha}
    body = '\n\n'.join(b['text'] for b in blocks)
    record = {'source_id':source['source_id'],'source_version':source['source_version'],
        'source_sha256':raw_sha,'allowed_scopes':sorted(source['allowed_scopes']),
        'license':source['license'],'indexing_allowed':True,'retention_policy':source['retention_policy'],
        'parser_version':PARSER_VERSION,'normalization_version':NORMALIZATION_VERSION if mode=='structured' else 'flat-space-1',
        'mode':mode,'body':body,'body_sha256':sha(body.encode('utf-8')),
        'blocks':blocks,'dropped_regions':dropped,'status':'accepted','reason':None}
    record['record_digest'] = digest(record)
    return record


def duplicate_groups(records):
    groups = {}
    for r in records:
        if r['status'] == 'accepted':
            key=digest([r['body_sha256'],r['allowed_scopes'],r['license'],r['retention_policy']])
            groups.setdefault(key,[]).append(r['source_id'])
    return [sorted(ids) for ids in groups.values() if len(ids)>1]
