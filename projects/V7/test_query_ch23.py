import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from query_ch23 import normalize,interpret,route_features
from retrieval_ch23 import (ROOT,load_state,authorized_view,Principal,digest,sha,execute,versions,MODEL_REVISION)
from experiment_ch23 import load_labels,metrics,HERE,WORKLOAD
from experiment_trace import validate


class InterpretationTests(unittest.TestCase):
    def test_normalized_surface_preserves_original_identifiers(self):
        value='  A06\t Cafe\u0301? '

        self.assertEqual(normalize(value),'A06 Caf\u00e9?')
        plan=interpret(value);self.assertEqual(plan['original'],value)
        self.assertEqual(plan['predicate'],{'record_id':'A06'})

    def test_invalid_control_empty_length(self):
        for text in ('','  ','x\x00y','x\u200by','x'*2049,3):
            with self.assertRaises(ValueError):normalize(text)

    def test_lowercase_fullwidth_id_not_repaired(self):
        for value in ('a06 waiting period','\uff21\uff10\uff16 waiting period'):
            p=interpret(value);self.assertEqual(p['outcome'],'clarify');self.assertIsNone(p['selected'])

    def test_multiple_ids_and_entities_clarify(self):
        for text in ('A01 or A06?','Orion versus Green?'):
            self.assertEqual(interpret(text)['outcome'],'clarify')

    def test_publication_day_half_open(self):
        p=interpret('Orion published on 2026-10-06')
        self.assertEqual(p['predicate'],{'entity':'Orion','published_gte':'2026-10-06T00:00:00Z','published_lt':'2026-10-07T00:00:00Z'})
        self.assertIsNone(p['as_of_ms'])

    def test_invalid_and_reversed_dates(self):
        for text in ('published on 2026-02-30','published from 2026-10-03 to 2026-10-01'):
            self.assertEqual(interpret(text)['reason'],'invalid_date')

    def test_distinct_time_axes_and_relative_clarification(self):
        self.assertEqual(interpret('A06 as of source 1500')['as_of_ms'],1500)
        self.assertEqual(interpret('A06 yesterday')['reason'],'unresolved_time')
        self.assertEqual(interpret('A06 published on 2026-10-06 as of source 1500')['reason'],'multiple_time_axes')

    def test_single_prior_slot_and_provenance(self):
        ctx={'record_ids':['A06'],'entity':'Orion','principal_key':'p','session_id':'s','expires_at_ms':6000,'origin_query_id':'q-old'}
        p=interpret('its wait?',context=ctx,principal_key='p',session_id='s')
        self.assertEqual(p['predicate'],{'record_id':'A06'});self.assertEqual(p['slot_provenance']['record_id'],'prior_turn:q-old')
        self.assertEqual(ctx['record_ids'],['A06'])

    def test_future_source_time_and_invalid_clock(self):
        self.assertEqual(interpret('A06 as of source 6000')['reason'],'future_source_time')
        for clock in (-1,True,1.5):
            with self.assertRaises(ValueError):interpret('A06 wait?',clock_ms=clock)

    def test_context_scope_expiry_and_ambiguity(self):
        ctx={'record_ids':['A06'],'entity':'Orion','principal_key':'p','session_id':'s','expires_at_ms':6000}
        for change,reason in (({'principal_key':'other'},'context_scope_mismatch'),({'session_id':'other'},'context_scope_mismatch'),
                ({'expires_at_ms':5300},'context_expired'),({'record_ids':['A01','A06']},'ambiguous_reference')):
            p=interpret('its wait?',context={**ctx,**change},principal_key='p',session_id='s');self.assertEqual(p['reason'],reason)

    def test_context_entity_conflict(self):
        ctx={'record_ids':['A06'],'entity':'Orion','principal_key':'p','session_id':'s','expires_at_ms':6000}
        self.assertEqual(interpret('Green its wait?',context=ctx,principal_key='p',session_id='s')['reason'],'context_entity_conflict')

    def test_count_graph_web_capabilities(self):
        self.assertEqual(interpret('How many Orion records?')['outcome'],'unsupported')
        p=interpret('Orion depends on approval');self.assertEqual((p['selected'],p['outcome']),('lexical','partial'))
        self.assertEqual(interpret('latest public Orion announcement today')['selected'],None)

    def test_quantity_false_trigger_preserved(self):
        p=interpret('How many minutes does Green wait?')
        self.assertEqual((p['kind'],p['outcome']),('count','unsupported'));self.assertIsNone(p['route_confidence'])

    def test_language_and_invalid_capabilities(self):
        self.assertEqual(interpret('Orion wait?',language='es')['reason'],'unsupported_language')
        for args in (('bogus',frozenset()),('date',{'dense'}),('date',frozenset({'magic'})),('date',frozenset(),1)):
            with self.assertRaises(ValueError):route_features(*args)


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caps,cls.auth,cls.gen=load_state();cls.labels=load_labels(cls.caps,cls.auth)
        cls.record=json.loads((HERE/'chapter-23-experiment.json').read_text('utf-8'))
        cls.snapshot=json.loads((HERE/'index_ch23/queries.json').read_text('utf-8'))
        cls.ids=versions(cls.labels['corpus_version'],cls.labels['query_set_version'],cls.labels['qrels_version'],cls.gen.identity,MODEL_REVISION)

    def request(self,key):return copy.deepcopy(next(q for q in self.labels['queries'] if q['query_id']==key))
    def run_case(self,key='r01',mode='rule_route',**kwargs):
        q=self.request(key)
        kwargs.setdefault('query_contract',self.gen.contract)
        return execute(q,mode,0,self.gen,self.auth,self.snapshot['query_vectors'][key],self.snapshot['token_counts'],self.ids,WORKLOAD,**kwargs)

    def test_source_policy_and_query_bindings(self):
        caps=copy.deepcopy(self.caps);caps['A06@3']['document']['body']+=' changed'
        with self.assertRaises(ValueError):load_labels(caps,self.auth)
        changed=copy.deepcopy(self.labels);changed['queries'][0]['text']='A07 wait?'
        with patch('experiment_ch23.json.loads',return_value=changed):
            with self.assertRaises(ValueError):load_labels(self.caps,self.auth)

    def test_frozen_counts_and_plan_accuracy(self):
        self.assertEqual(len(self.labels['queries']),21)
        self.assertEqual(sum(bool(q['requirements']) for q in self.labels['queries']),10)
        self.assertEqual(sum(len(q['requirements']) for q in self.labels['queries']),11)
        self.assertEqual(self.record['rule_plan_accuracy_21_queries'],20/21)

    def test_exact_and_followup_target_actual_version(self):
        for key in ('r01','r07'):
            ranked,packed,_,_,_=self.run_case(key)
            self.assertEqual(ranked[0][0],self.caps['A06@3']['unit']['item_id'])
            self.assertEqual(packed[0]['source_version'],'3')

    def test_historical_context_is_nine_minute_version(self):
        ranked,packed,_,parent,_=self.run_case('r08')
        self.assertEqual(packed[0]['source_version'],'2');self.assertIn('9 minutes',packed[0]['text'])
        self.assertNotEqual(parent['context_ids'][0],self.caps['A06@3']['unit']['item_id'])

    def test_deleted_revoked_wrong_tenant_unknown_no_score(self):
        for key in ('r09','r10','r11','r12'):
            ranked,_,_,parent,frames=self.run_case(key)
            self.assertEqual(ranked,[]);self.assertEqual(parent['branch_request_ids'],[])
            self.assertEqual(parent['raw_candidate_ids'],[]);self.assertEqual(len(frames),1)

    def test_private_vector_never_accessed(self):
        class Protected:
            def __iter__(self):raise AssertionError('Private vector read')
            def __len__(self):raise AssertionError('Private vector read')
        gen=copy.deepcopy(self.gen)
        for row in gen.rows.values():
            if row['metadata']['tenant']=='B' or 'admin' in row['metadata']['acl_roles']:row['vector']=Protected()
        q=self.request('r03')
        execute(q,'dense_all',0,gen,self.auth,self.snapshot['query_vectors']['r03'],self.snapshot['token_counts'],self.ids,WORKLOAD,query_contract=self.gen.contract)

    def test_current_delete_also_blocks_requested_history(self):
        q=self.request('r09');q['text']='A03 waiting period as of source 500'
        ranked,_,_,p,_=execute(q,'rule_route',0,self.gen,self.auth,self.snapshot['query_vectors']['r09'],self.snapshot['token_counts'],self.ids,WORKLOAD,query_contract=self.gen.contract)
        self.assertEqual(ranked,[]);self.assertEqual(p['raw_candidate_ids'],[])

    def test_private_body_not_read_by_lexical_statistics(self):
        class Protected:
            def __str__(self):raise AssertionError('Private body read')
            def __add__(self,other):raise AssertionError('Private body read')
            def __radd__(self,other):raise AssertionError('Private body read')
        gen=copy.deepcopy(self.gen)
        for row in gen.rows.values():
            if row['metadata']['tenant']=='B' or 'admin' in row['metadata']['acl_roles']:row['text']=Protected()
        q=self.request('r01')
        execute(q,'rule_route',0,gen,self.auth,self.snapshot['query_vectors']['r01'],self.snapshot['token_counts'],self.ids,WORKLOAD,query_contract=gen.contract)

    def test_multiple_roles_choose_actual_unit_scope(self):
        q=self.request('r01');q['principal']['roles']=['admin','reader']
        ranked,packed,_,_,_=execute(q,'rule_route',0,self.gen,self.auth,self.snapshot['query_vectors']['r01'],self.snapshot['token_counts'],self.ids,WORKLOAD,query_contract=self.gen.contract)
        self.assertTrue(ranked);self.assertEqual(packed[0]['source_id'],'A06')

    def test_both_publications_fit_actual_budget(self):
        ranked,packed,_,parent,_=self.run_case('r06')
        self.assertEqual(len(ranked),2);self.assertEqual(len(packed),2)
        self.assertEqual(parent['packing']['used_encoder_wordpieces'],68)

    def test_same_constraints_across_actual_fallback(self):
        _,_,_,parent,frames=self.run_case('r01',faults={'lexical':TimeoutError})
        self.assertEqual(len(parent['branch_request_ids']),2)
        self.assertEqual([f['route'] for f in frames[:-1]],['lexical','dense'])
        self.assertEqual(frames[0]['status'],'failed')
        self.assertTrue(all(f['plan']['constraint_digest']==parent['plan']['constraint_digest'] for f in frames))

    def test_two_failures_stop_budget(self):
        ranked,_,_,p,frames=self.run_case('r03',faults={'lexical':TimeoutError,'dense':TimeoutError})
        self.assertEqual(ranked,[]);self.assertEqual(p['reason'],'retry_budget_exhausted')
        self.assertEqual(len(frames),3);self.assertIsNone(p['final_route'])

    def test_integrity_failure_redacted_and_not_retried(self):
        sink=[]
        with self.assertRaises(ValueError):self.run_case('r03',faults={'dense':ValueError},trace_sink=sink)
        self.assertEqual(len(sink),2);self.assertEqual(sink[0]['route'],'dense')
        self.assertEqual(sink[-1]['status'],'failed');self.assertNotIn('Injected route fault',json.dumps(sink))

    def test_invalid_known_request_has_correlated_envelope(self):
        q=self.request('r01');q['text']='bad\x00query';sink=[]
        with self.assertRaises(ValueError):execute(q,'rule_route',0,self.gen,self.auth,self.snapshot['query_vectors']['r01'],self.snapshot['token_counts'],self.ids,WORKLOAD,trace_sink=sink,query_contract=self.gen.contract)
        self.assertEqual(sink[0]['query_id'],'r01');self.assertEqual(sink[0]['status'],'invalid')

    def test_partial_graph_guard_has_actual_lexical_only(self):
        ranked,_,plan,p,frames=self.run_case('r15')
        self.assertEqual(plan['primary'],'graph');self.assertEqual(p['status'],'partial')
        self.assertTrue(ranked);self.assertEqual([f['route'] for f in frames[:-1]],['lexical'])

    def test_unrun_context_is_null_not_empty_success(self):
        for key in ('r13','r14','r16','r21'):
            _,_,_,parent,_=self.run_case(key)
            self.assertIsNone(parent['context_ids']);self.assertIsNone(parent['packing'])
            self.assertNotIn('context',parent['stage_timings_ms']);self.assertIn('context',parent['stages_not_run'])

    def test_snapshot_scores_and_historical_replay(self):
        self.assertEqual(digest(self.snapshot),self.record['query_snapshot_digest'])
        self.assertEqual(self.record['query_snapshot_replay_checks'],63)
        for p,h in self.record['code_sha256'].items():self.assertEqual(sha((HERE/p).read_bytes()),h)
        self.assertEqual(sha((HERE/'qrels_ch23.json').read_bytes()),self.record['qrels_sha256'])

    def test_actual_samples_per_principal_and_branch_correlations(self):
        parents={f['request_id']:f for f in self.record['samples'] if f['mode'] in ('dense_all','constraint_dense','rule_route')}
        self.assertEqual(len(parents),189)
        for f in self.record['samples']:
            q=self.request(f['query_id']);principal=Principal(q['principal']['tenant'],frozenset(q['principal']['roles']))
            expected_plan=interpret(q['text'],context=q['context'],principal_key=digest(q['principal']),session_id=q['session_id'],language=q['language'])
            asof=None if f['mode'].startswith('dense_all') else expected_plan['as_of_ms']
            view=authorized_view(self.gen,self.auth,principal,asof);validate(f,view.rows)
            if 'parent_request_id' in f:self.assertIn(f['parent_request_id'],parents)
            for field in ('text','surface','predicate','context','principal'):
                self.assertNotIn(field,f);self.assertNotIn(field,f.get('plan',{}))

    def test_negative_quantity_and_route_tie_retained(self):
        for mode in ('constraint_dense','rule_route'):
            self.assertEqual(self.record['aggregates'][mode]['positive_recall_at_2'],.9)
        rows=[o for o in self.record['per_query_trials'] if o['query_id']=='r21' and o['mode']=='rule_route']
        self.assertTrue(all(o['positive_recall_at_2']==0 for o in rows))
        self.assertEqual(self.record['aggregates']['dense_all']['positive_recall_at_2'],.4)

    def test_unimplemented_sql_cannot_execute_as_lexical(self):
        sink=[]
        with self.assertRaises(ValueError):self.run_case('r14',capabilities=frozenset({'sql'}),trace_sink=sink)
        self.assertEqual(sink[0]['status'],'invalid');self.assertEqual(sink[0]['raw_candidate_ids'],[])

    def test_same_dimension_wrong_input_contract_rejected(self):
        bad={**self.gen.contract,'input_policy':'entity-body'};sink=[]
        with self.assertRaises(ValueError):self.run_case('r01',query_contract=bad,trace_sink=sink)
        self.assertEqual(sink[0]['raw_candidate_ids'],[])

    def test_missing_dense_is_not_called_by_dense_control(self):
        ranked,_,plan,parent,frames=self.run_case('r03',mode='constraint_dense',capabilities=frozenset({'lexical'}))
        self.assertEqual(ranked,[]);self.assertEqual(parent['status'],'unsupported');self.assertEqual(len(frames),1)

    def test_stale_source_state_rejects_before_scoring(self):
        gen=copy.deepcopy(self.gen);gen.store.heads.pop('A06');sink=[]
        q=self.request('r01')
        with self.assertRaises(ValueError):execute(q,'rule_route',0,gen,self.auth,self.snapshot['query_vectors']['r01'],self.snapshot['token_counts'],self.ids,WORKLOAD,trace_sink=sink,query_contract=gen.contract)
        self.assertEqual(sink[0]['raw_candidate_ids'],[])

    def test_independent_answer_and_unsolved_starter(self):
        spec=importlib.util.spec_from_file_location('checker23',ROOT/'labs/chapter-23/check_implementation.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.check(ROOT/'solutions/code/chapter_23_mechanisms.py')
        with self.assertRaises(NotImplementedError):module.check(ROOT/'labs/chapter-23/implement.py')


if __name__=='__main__':unittest.main()
