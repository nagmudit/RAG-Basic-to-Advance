import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ingestion_ch19 import ingest, normalize, locate_span, markdown_blocks, HTMLBlocks, duplicate_groups, sha, digest
from experiment_ch19 import load_requirements, binding, HERE, ROOT, SCOPE, WORKLOAD


class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.directory=HERE/'fixtures'
        self.sources=json.loads((self.directory/'sources.json').read_text(encoding='utf-8'))
        self.by_id={r['source_id']:r for r in self.sources}

    def get(self,id,mode='structured'):
        return ingest(self.directory,self.by_id[id],SCOPE,mode)

    def test_scope_and_rights_before_read_or_path(self):
        for id in ['S-private','S-unknown']:
            with patch.object(Path,'resolve',side_effect=AssertionError('Read boundary')):
                result=self.get(id)
            self.assertEqual(result['status'],'blocked')
            self.assertIsNone(result['source_id'])

    def test_path_escape_is_rejected(self):
        source={**self.by_id['S-md'],'path':'../../README.md'}
        with self.assertRaises(ValueError):ingest(self.directory,source,SCOPE)

    def test_three_formats_publish_with_anchors(self):
        for id in ['S-md','S-html','S-pdf']:
            r=self.get(id)
            self.assertEqual(r['status'],'accepted')
            self.assertEqual(r['body'],'\n\n'.join(b['text'] for b in r['blocks']))
            for b in r['blocks']:
                self.assertEqual(r['body'][b['start']:b['end']],b['text'])
                self.assertEqual(sha(b['raw_extracted_text'].encode('utf-8')),b['raw_extracted_sha256'])
                self.assertNotIn('file_only',b['locator'])

    def test_unicode_normalization_is_not_raw_offset_identity(self):
        self.assertEqual(normalize('cafe\u0301'), 'caf\u00e9')
        self.assertNotEqual(len('cafe\u0301'),len(normalize('cafe\u0301')))
        self.assertEqual(normalize('TK-042 NOT 403'), 'TK-042 NOT 403')
        self.assertEqual(normalize('x\n    y','code'),'x\n    y')
        self.assertEqual(normalize('\u2163'), '\u2163')

    def test_table_relationship_and_boilerplate(self):
        r=self.get('S-html')
        self.assertIn('Region=East; Retry limit=2',r['body'])
        self.assertIn('No retry on HTTP 403.',r['body'])
        self.assertNotIn('Home',r['body'])
        self.assertNotIn('999',r['body'])
        self.assertGreaterEqual(len(r['dropped_regions']),4)
        self.assertIn('999',self.get('S-html','flat')['body'])

    def test_scanned_invalid_bytes_merged_cells_quarantine(self):
        for id in ['S-scan','S-bad','S-merged']:
            r=self.get(id)
            self.assertEqual(r['status'],'quarantined')
            self.assertNotIn('body',r)
        self.assertEqual(self.get('S-merged','flat')['status'],'accepted')

    def test_pdf_page_bbox_and_margin_report(self):
        r=self.get('S-pdf')
        self.assertEqual({b['locator']['page'] for b in r['blocks']},{1,2})
        self.assertEqual(len(r['dropped_regions']),4)
        self.assertNotIn('ACME SUPPORT',r['body'])
        for b in r['blocks']:
            self.assertEqual(len(b['locator']['bbox']),4)
            x0,y0,x1,y1=b['locator']['bbox']
            self.assertTrue(0<=x0<x1<=612 and 0<=y0<y1<=792)

    def test_markdown_code_and_rejection(self):
        r=self.get('S-md')
        self.assertIn('if approved:\n    restart()',r['body'])
        with self.assertRaises(ValueError):markdown_blocks('```python\nnever closed')

    def test_html_inline_entities_and_malformed_reject(self):
        rows,_=HTMLBlocks().finish('<main><p id="a">A &amp; <em>B</em>.</p></main>')
        self.assertEqual(rows[0][0],'A & B.')
        for text in ['<main><p>x</main>','<main><p>x','<main>unanchored</main>']:
            with self.assertRaises(ValueError):HTMLBlocks().finish(text)

    def test_dedup_keeps_policy_and_alias_identity(self):
        a,b=self.get('S-md'),self.get('S-copy')
        self.assertEqual(duplicate_groups([a,b]),[['S-copy','S-md']])
        self.assertNotEqual(a['record_digest'],b['record_digest'])
        for key,value in [('allowed_scopes',['different']),('license','different'),('retention_policy','different')]:
            changed={**b,key:value}
            self.assertEqual(duplicate_groups([a,changed]),[])

    def test_span_crosses_blocks_but_not_separator(self):
        blocks=[{'block_id':'a','start':0,'end':3,'locator':{'page':1}},
                {'block_id':'b','start':5,'end':9,'locator':{'page':2}}]
        self.assertEqual([x['canonical_overlap'] for x in locate_span(blocks,2,7)],[[2,3],[5,7]])
        self.assertEqual(locate_span(blocks,3,5),[])
        for start,end in [(-1,2),(2,2),(0,10),(False,2)]:
            with self.assertRaises(ValueError):locate_span(blocks,start,end)

    def test_source_labels_reject_same_id_changed_content(self):
        load_requirements(self.directory,self.sources)
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            for s in self.sources:
                (Path(temp)/s['path']).write_bytes((self.directory/s['path']).read_bytes())
            target=Path(temp)/'runbook.md'
            target.write_bytes(target.read_bytes().replace(b'TK-042',b'TK-043'))
            with self.assertRaisesRegex(ValueError,'Source/content/policy'):
                load_requirements(Path(temp),self.sources)

    def test_policy_and_locator_binding(self):
        for key,value in [('source_version','2'),('retention_policy','changed'),('allowed_scopes',['support-team','new'])]:
            sources=copy.deepcopy(self.sources)
            sources[0][key]=value
            with self.assertRaises(ValueError):load_requirements(self.directory,sources)

    def test_record_hashes_identity_samples_and_negative_result(self):
        sys.path.insert(0,str(ROOT/'projects/common'))
        from experiment_trace import validate
        record=json.loads((HERE/'chapter-19-experiment.json').read_text(encoding='utf-8'))
        eligible={r['source_id'] for r in binding(self.directory,self.sources)}
        self.assertEqual(len(record['request_samples']),70)
        for sample in record['request_samples']:
            self.assertEqual(sample['workload_id'],WORKLOAD)
            validate(sample,eligible)
        encoded=json.dumps(record['request_samples'])
        for forbidden in ['Protected marker','S-private','S-unknown','Do not restart','retry=999']:
            self.assertNotIn(forbidden,encoded)
        for name,expected in record['code_sha256'].items():
            self.assertEqual(sha((HERE/name).read_bytes().replace(b'\r\n',b'\n')),expected)
        self.assertEqual(record['span_requirements_sha256'],sha((HERE/'span_requirements.json').read_bytes().replace(b'\r\n',b'\n')))
        a,b=record['summaries']['flat'],record['summaries']['structured']
        self.assertEqual(a['preservation_rate'],5/8)
        self.assertEqual(b['preservation_rate'],7/8)
        self.assertEqual(a['source_hit_at_1'],b['source_hit_at_1'])
        self.assertFalse(b['cases'][-1]['preserved'])

    def test_canonical_record_digests_and_saved_reload(self):
        for mode in ['flat','structured']:
            rows=json.loads((HERE/'canonical_ch19'/f'{mode}.json').read_text(encoding='utf-8'))
            for row in rows:
                stored=row['record_digest']
                self.assertEqual(stored,digest({k:v for k,v in row.items() if k!='record_digest'}))
                fresh=self.get(row['source_id'],mode)
                self.assertEqual(fresh['record_digest'],stored)

    def test_separate_answer_and_intentionally_unsolved_starter(self):
        lab=ROOT/'labs/chapter-19'
        spec=importlib.util.spec_from_file_location('ch19_checker',lab/'check_implementation.py')
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        checker.check(ROOT/'solutions/code/chapter_19_mechanisms.py')
        with self.assertRaises(NotImplementedError):checker.check(lab/'implement.py')

    def test_registered_new_workload(self):
        registry=json.loads((ROOT/'evaluation/WORKLOAD_REGISTRY.json').read_text(encoding='utf-8'))
        r=next(r for r in registry['workloads'] if r['workload_id']==WORKLOAD)
        self.assertEqual(r['number_of_queries'],8)
        self.assertEqual(r['source_manifest_sha256'],load_requirements(self.directory,self.sources)['manifest_sha256'])


if __name__=='__main__':unittest.main()
