import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch
from ingestion_ch19 import digest,sha
from chunking_ch20 import word_windows,char_windows,make_chunks,merge_intervals,evidence_metrics,pack_context,MODES
from experiment_ch20 import HERE,ROOT,load_documents,load_labels,verify_snapshot,dense_search,WORKLOAD,MODEL_REVISION


class ChunkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents=load_documents();cls.docs={d['source_id']:d for d in cls.documents}
        cls.labels=load_labels(cls.documents)
        cls.record=json.loads((HERE/'chapter-20-experiment.json').read_text(encoding='utf-8'))
        cls.index=json.loads((HERE/'index_ch20/index.json').read_text(encoding='utf-8'))

    def test_hand_windows_preserve_original_coordinates(self):
        text=' A  BB\nCCC D E '
        self.assertEqual(word_windows(text,3,1),[(1,10),(7,14)])
        self.assertEqual([text[a:z] for a,z in word_windows(text,2)],['A  BB','CCC D','E'])
        self.assertEqual(word_windows(' \n',2),[])

    def test_invalid_overlap_and_tail_termination(self):
        self.assertEqual(word_windows('a b c d e',3,1),[(0,5),(4,9)])
        for n,o in [(0,0),(3,3),(3,-1),(False,0),(2,False)]:
            with self.assertRaises(ValueError):word_windows('x',n,o)

    def test_unicode_character_unit_is_not_word_or_byte(self):
        self.assertEqual(char_windows('caf\u00e9 x',4),[(0,4),(4,6)])
        self.assertEqual(len('caf\u00e9'.encode('utf-8')),5)
        self.assertEqual(word_windows('caf\u00e9\tZ',1),[(0,4),(5,6)])

    def test_eligibility_precedes_body_access(self):
        doc={'allowed_scopes':['private'],'indexing_allowed':True}
        self.assertEqual(make_chunks(doc,'word24'),[])
        doc={'allowed_scopes':['support-team'],'indexing_allowed':False}
        self.assertEqual(make_chunks(doc,'word24'),[])

    def test_every_boundary_map_and_identity(self):
        for mode in MODES:
            for doc in self.documents:
                for c in make_chunks(doc,mode):
                    a,z=c['canonical_span']
                    self.assertEqual(c['text'],doc['body'][a:z])
                    self.assertEqual(c['record_digest'],doc['record_digest'])
                    self.assertEqual(c['text_sha256'],sha(c['text'].encode('utf-8')))
                    self.assertTrue(c['anchors'])
                    self.assertEqual(c['allowed_scopes'],doc['allowed_scopes'])

    def test_atomic_table_and_code_structure(self):
        rows=make_chunks(self.docs['S-html'],'structure48')
        self.assertTrue(any(c['text']=='Region=East; Retry limit=2' for c in rows))
        rows=make_chunks(self.docs['S-md'],'structure48')
        self.assertTrue(any(c['text']=='if approved:\n    restart()' for c in rows))

    def test_overlap_union_and_duplicate_denominator(self):
        doc={'source_id':'a','body':'ABCDEFGHIJ'}
        units=[{'item_id':'x','source_id':'a','canonical_span':[0,6]},
               {'item_id':'y','source_id':'a','canonical_span':[4,10]}]
        req=[{'requirement_id':'r','source_id':'a','canonical_span':[3,8]}]
        m=evidence_metrics(units,req,{'a':doc},{})
        self.assertEqual(m['evidence_recall'],1)
        self.assertAlmostEqual(m['duplicate_source_fraction'],2/12)
        self.assertEqual(m['emitted_source_codepoints'],12)
        self.assertEqual(m['unique_source_codepoints'],10)

    def test_adjacent_fragments_whitespace_and_incomplete_evidence(self):
        docs={'a':{'body':'ABC DE'}}
        req=[{'requirement_id':'r','source_id':'a','canonical_span':[0,6]}]
        x={'item_id':'x','source_id':'a','canonical_span':[0,3]}
        y={'item_id':'y','source_id':'a','canonical_span':[4,6]}
        self.assertEqual(evidence_metrics([x,y],req,docs,{})['evidence_recall'],1)
        m=evidence_metrics([x],req,docs,{})
        self.assertEqual(m['evidence_recall'],0)
        self.assertAlmostEqual(m['required_span_coverage'],3/5)

    def test_alias_duplicates_are_counted_once(self):
        docs={'a':{'body':'ABC'},'b':{'body':'ABC'}}
        units=[{'item_id':s,'source_id':s,'canonical_span':[0,3]} for s in docs]
        req=[{'requirement_id':'r','source_id':'a','canonical_span':[0,3]}]
        m=evidence_metrics(units,req,docs,{'b':'a'})
        self.assertEqual(m['evidence_recall'],1)
        self.assertEqual(m['duplicate_source_fraction'],.5)

    def test_interval_merge_tie_and_empty(self):
        self.assertEqual(merge_intervals([[4,8],[0,3],[3,5],[10,12]]),[[0,8],[10,12]])
        self.assertEqual(merge_intervals([]),[])
        with self.assertRaises(ValueError):merge_intervals([[1,1]])

    def test_parent_budget_rejection_and_child_selection_trace(self):
        doc=self.docs['S-ops'];children=make_chunks(doc,'word24')[:2]
        lookup={c['item_id']:c for c in children};counts={c['item_id']:10 for c in children}
        counts[children[0]['parent_id']]=517
        ranked=[(c['item_id'],1.0) for c in children]
        selected,trace=pack_context(ranked,lookup,{doc['source_id']:doc},80,counts,True)
        self.assertEqual(selected,[])
        self.assertEqual([r['reason'] for r in trace['packing_attempts']],['budget','duplicate_parent'])
        selected,trace=pack_context(ranked,lookup,{doc['source_id']:doc},10,counts)
        self.assertEqual(len(selected),1)
        self.assertEqual(trace['packing_attempts'][1]['reason'],'budget')

    def test_parent_authorization_before_expansion(self):
        doc=copy.deepcopy(self.docs['S-md']);child=make_chunks(doc,'word24')[0]
        doc['allowed_scopes']=['private']
        with self.assertRaises(ValueError):pack_context([(child['item_id'],1)],{child['item_id']:child},{doc['source_id']:doc},80,{},True)

    def test_source_mutation_and_scope_reject_stale_judgments(self):
        for key,value in [('body','same ID but changed body'),('allowed_scopes',['private']),('source_version','2')]:
            rows=copy.deepcopy(self.documents);rows[0][key]=value
            with self.assertRaises(ValueError):load_labels(rows)

    def test_original_locator_mutation_is_rejected(self):
        labels=copy.deepcopy(self.labels)
        labels['queries'][0]['requirements'][0]['anchors'][0]['locator']['line_start']=999
        real=Path.read_text
        def reader(path,*args,**kwargs):
            return json.dumps(labels) if path.name=='evidence_spans_ch20.json' else real(path,*args,**kwargs)
        with patch.object(Path,'read_text',reader):
            with self.assertRaisesRegex(ValueError,'source locator'):load_labels(self.documents)

    def test_exact_sort_ties_and_scope_before_scoring(self):
        v=[1.0]+[0.0]*383
        rows=[{'item_id':i,'vector':v,'allowed_scopes':['support-team']} for i in ['b','a']]
        rows.append({'item_id':'protected','allowed_scopes':['private'],'vector':None})
        ranked,work=dense_search(rows,v,2)
        self.assertEqual(ranked,[('a',1.0),('b',1.0)])
        self.assertEqual(work['candidate_stages']['scored'],ranked)
        with self.assertRaises(ValueError):dense_search(rows,[float('nan')]*384)

    def test_snapshot_trust_and_actual_reload_candidate_parity(self):
        verify_snapshot(self.index,self.documents,self.record['index_manifest_digest'])
        self.assertEqual(self.record['reload_candidate_parity_checks'],84)
        for mode,s in self.record['summaries'].items():
            for case in s['cases']:
                ranking,_=dense_search(self.index['indexes'][mode]['rows'],self.index['query_vectors'][case['query_id']])
                self.assertEqual([id for id,_ in ranking],case['candidate_ids'])
        changed=copy.deepcopy(self.index);changed['indexes']['word24']['rows'][0]['vector'][0]+=.1
        with self.assertRaises(ValueError):verify_snapshot(changed,self.documents,self.record['index_manifest_digest'])

    def test_labels_counts_and_new_workload_binding(self):
        self.assertEqual(len(self.labels['queries']),12)
        self.assertEqual(sum(len(q['requirements']) for q in self.labels['queries']),18)
        registry=json.loads((ROOT/'evaluation/WORKLOAD_REGISTRY.json').read_text(encoding='utf-8'))
        entry=next(r for r in registry['workloads'] if r['workload_id']==WORKLOAD)
        self.assertEqual(entry['source_manifest_sha256'],self.record['source_manifest_sha256'])

    def test_all_correlated_pools_and_private_text_absent(self):
        sys_path=ROOT/'projects/common'
        import sys;sys.path.insert(0,str(sys_path))
        from experiment_trace import validate
        eligible=set(self.index['token_counts'])
        samples=self.record['request_samples'];self.assertEqual(len(samples),264)
        self.assertEqual(len({s['request_id'] for s in samples}),264)
        for s in samples:
            validate(s,eligible)
            self.assertEqual(s['workload_id'],WORKLOAD)
            if s['mode']!='query_encode':self.assertEqual(len(s['final_candidate_ids']),3)
            self.assertIsNone(s['evidence_ids'])
        for text in ['S-private','Protected marker','password unlocks','ordinary waiting period is thirty']:
            self.assertNotIn(text,json.dumps(samples))

    def test_source_and_code_hashes_and_negative_results(self):
        for name,value in self.record['code_sha256'].items():
            self.assertEqual(sha((HERE/name).read_bytes().replace(b'\r\n',b'\n')),value)
        s=self.record['summaries']
        self.assertEqual(s['word96']['candidate_evidence_recall_at_3'],1)
        self.assertEqual(s['word96']['context_evidence_recall'],.4)
        self.assertGreater(s['word24-o8']['mean_context_duplicate_source_fraction'],s['word24']['mean_context_duplicate_source_fraction'])
        self.assertLess(s['word24-parent']['context_evidence_recall'],s['word24']['context_evidence_recall'])
        for b in self.record['builds'].values():
            if 'max_encoder_input_with_special' in b:self.assertLessEqual(b['max_encoder_input_with_special'],256)

    def test_separate_solution_and_unsolved_construction(self):
        path=ROOT/'labs/chapter-20/check_implementation.py'
        spec=importlib.util.spec_from_file_location('ch20_checker',path)
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        checker.check(ROOT/'solutions/code/chapter_20_mechanisms.py')
        with self.assertRaises(NotImplementedError):checker.check(path.with_name('implement.py'))


if __name__=='__main__':unittest.main()
