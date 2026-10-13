import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from lifecycle_ch22 import *
from experiment_ch22 import load_capsules, load_labels, schedule, HERE, ROOT, manifest, sha, version_documents
from experiment_trace import validate
from metadata_ch21 import Principal


def event(rev=1, op='upsert', name=None, effective=None):
    return {'event_id':name or 'event-'+str(rev), 'source_id':'x','revision':rev,
            'effective_ms':rev if effective is None else effective,'op':op,
            'capsule_key':None if op=='delete' else 'x@'+str(rev),'payload_digest':digest({'rev':rev,'op':op})}


class StoreTests(unittest.TestCase):
    def test_upsert_and_no_input_mutation(self):
        s=VersionStore();e=event();before=copy.deepcopy(e)
        self.assertEqual(s.apply(e,10)['reason'],'accepted');self.assertEqual(e,before)

    def test_identical_event_duplicate(self):
        s=VersionStore();e=event();s.apply(e,10)
        original=s.state_digest();self.assertEqual(s.apply(e,20)['reason'],'duplicate_event');self.assertEqual(s.state_digest(),original)

    def test_duplicate_revision_new_id(self):
        s=VersionStore();s.apply(event(),10);self.assertEqual(s.apply(event(name='another'),20)['reason'],'duplicate_revision')

    def test_same_id_conflict_atomic(self):
        s=VersionStore();s.apply(event(),10);before=s.payload();e=event();e['payload_digest']='different'
        with self.assertRaises(ValueError):s.apply(e,20)
        self.assertEqual(s.payload(),before)

    def test_same_revision_conflict_atomic(self):
        s=VersionStore();s.apply(event(),10);before=s.payload();e=event(name='another');e['payload_digest']='changed'
        with self.assertRaises(ValueError):s.apply(e,20)
        self.assertEqual(s.payload(),before)

    def test_tombstone_blocks_stale_upsert(self):
        s=VersionStore();s.apply(event(),10);s.apply(event(2,'delete'),20)
        self.assertEqual(s.apply(event(name='late'),30)['reason'],'stale_revision')
        self.assertEqual(s.heads['x']['op'],'delete');self.assertEqual(s.heads['x']['revision'],2)

    def test_arrival_control_resurrects_projection(self):
        s=VersionStore('arrival');s.apply(event(),10);s.apply(event(2,'delete'),20);s.apply(event(name='late'),30)
        self.assertEqual(s.heads['x']['revision'],1)

    def test_explicit_newer_recreation(self):
        s=VersionStore();s.apply(event(2,'delete'),20);s.apply(event(3),30);self.assertEqual(s.heads['x']['revision'],3)

    def test_invalid_revision_clock_and_op(self):
        for key,value in (('revision',True),('revision',0),('effective_ms',True),('op','unknown')):
            e=event();e[key]=value
            with self.assertRaises(ValueError):VersionStore().apply(e,10)
        with self.assertRaises(ValueError):VersionStore().apply(event(),0)

    def test_backdated_policy_explicit(self):
        s=VersionStore();s.apply(event(1,effective=10),10)
        with self.assertRaises(ValueError):s.apply(event(2,effective=5),20)

    def test_asof_boundary_and_latest(self):
        s=VersionStore();s.apply(event(1,effective=10),10);s.apply(event(2,effective=20),20)
        self.assertIsNone(s.selected('x',9));self.assertEqual(s.selected('x',19)['revision'],1);self.assertEqual(s.selected('x',20)['revision'],2)

    def test_restart_keeps_tombstone_and_receipts(self):
        s=VersionStore();s.apply(event(),10);s.apply(event(2,'delete'),20)
        restored=VersionStore.restore(s.payload());self.assertEqual(restored.apply(event(name='late'),30)['reason'],'stale_revision')
        self.assertEqual(restored.apply(event(2,'delete'),30)['reason'],'duplicate_event')

    def test_local_atomic_checkpoint_and_digest(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as directory:
            p=Path(directory)/'state.json';payload={'x':1};expected=atomic_checkpoint(p,payload)
            self.assertEqual(load_checkpoint(p,expected),payload)
            p.write_text('{"x":2}',encoding='utf-8')
            with self.assertRaises(ValueError):load_checkpoint(p,expected)


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capsules,_=load_capsules();cls.labels=load_labels(cls.capsules)
        cls.record=json.loads((HERE/'chapter-22-experiment.json').read_text('utf-8'))
        cls.checkpoint=load_checkpoint(HERE/'index_ch22/checkpoint.json',cls.record['checkpoint_digest'])
        cls.seeds,cls.commits,cls.deliveries=schedule(cls.capsules)

    def initial(self):
        store=VersionStore()
        for e in self.seeds:store.apply(e,0)
        return store

    def final_authority(self):
        return VersionStore.restore(self.checkpoint['authority'])

    def test_content_metadata_event_bindings(self):
        c=copy.deepcopy(self.capsules);c['A06@2']['unit']['metadata']['language']='fr'
        with self.assertRaises(ValueError):load_labels(c)
        c=copy.deepcopy(self.capsules);c['A06@2']['document']['blocks'][0]['locator']['line_start']=99
        with self.assertRaises(ValueError):load_labels(c)

    def test_event_and_checkpoint_targets(self):
        self.assertEqual(len(self.capsules),18);self.assertEqual(len(self.labels['queries']),10)
        self.assertEqual(sum(q['requirement'] is not None for q in self.labels['queries']),6)
        self.assertEqual(self.record['checkpoint_query_replay_checks'],20)

    def test_monotonic_final_heads_and_arrival_failure(self):
        good=self.checkpoint['final_stores']['ordered']['heads'];bad=self.checkpoint['final_stores']['arrival']['heads']
        self.assertEqual(good['A06']['revision'],3);self.assertEqual(good['A03']['op'],'delete')
        self.assertEqual(bad['A06']['revision'],1);self.assertEqual(bad['A03']['op'],'upsert')

    def test_deleted_and_revoked_history_never_scores(self):
        gen=Generation('test',self.initial(),'body',self.checkpoint['bank'],self.capsules);authority=self.final_authority();p=Principal('A',frozenset({'reader'}))
        for source in ('A03','A08'):
            ranked,work=gen.query([1.]+[0.]*383,contract('body'),p,authority,source,500)
            self.assertEqual(ranked,[]);self.assertEqual(work['candidate_stages']['scored'],[])

    def test_authority_delete_before_index_delivery(self):
        initial=self.initial();gen=Generation('test',initial,'body',self.checkpoint['bank'],self.capsules);authority=self.initial()
        authority.apply(self.commits[1][1],2000)
        ranked,work=gen.query([1.]+[0.]*383,contract('body'),Principal('A',frozenset({'reader'})),authority,'A03')
        self.assertEqual(ranked,[]);self.assertEqual(work['candidate_stages']['scored'],[])

    def test_known_pending_loss_is_preserved(self):
        records=[r for r in self.record['samples'] if r['query_id']=='known-pending' and r['mode']=='ordered']
        self.assertEqual(len(records),3)
        for r in records:
            self.assertEqual(len(r['raw_candidate_ids']),1);self.assertEqual(r['final_candidate_ids'],[]);self.assertEqual(r['context_ids'],[])
            self.assertEqual(r['reason'],'known_revision_pending')

    def test_same_dimension_contract_rejected_before_vector(self):
        gen=Generation('test',self.initial(),'entity-body',self.checkpoint['bank'],self.capsules)
        with self.assertRaises(ValueError):gen.query([1.]+[0.]*383,contract('body'),Principal('A',frozenset({'reader'})),self.initial(),'A06')

    def test_private_vector_never_touched(self):
        class Protected(dict):
            def __getitem__(self,key):
                if key in ('vector','text','anchors'):raise AssertionError('Private access')
                return super().__getitem__(key)
        g=Generation('test',self.initial(),'body',self.checkpoint['bank'],self.capsules)
        item=self.capsules['A06@1']['unit']['item_id'];g.rows[item]=Protected(g.rows[item])
        self.assertEqual(g.query([1.]+[0.]*383,contract('body'),Principal('B',frozenset({'reader'})),self.initial(),'A06')[0],[])

    def test_raw_vector_bank_tamper_rejects_trusted_checkpoint(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as directory:
            p=Path(directory)/'state.json';changed=copy.deepcopy(self.checkpoint);changed['bank']['body']['A06@1'][0]+=.1
            atomic_checkpoint(p,changed)
            with self.assertRaises(ValueError):load_checkpoint(p,self.record['checkpoint_digest'])

    def test_generation_source_contract_identity(self):
        s=self.initial();g1=Generation('a',s,'body',self.checkpoint['bank'],self.capsules);g2=Generation('b',s,'entity-body',self.checkpoint['bank'],self.capsules)
        self.assertNotEqual(g1.identity,g2.identity);self.assertEqual(g1.contract['dimension'],g2.contract['dimension']);self.assertNotEqual(g1.contract,g2.contract)

    def test_historical_forward_parent_is_actual_version(self):
        g=Generation('old',VersionStore.restore(self.checkpoint['final_stores']['ordered']),'body',self.checkpoint['bank'],self.capsules)
        item=self.capsules['A06@1']['unit']['item_id'];docs=version_documents([(item,.5)],g,self.capsules)
        self.assertEqual(docs['A06']['source_version'],'1');self.assertEqual(docs['A06']['record_digest'],g.rows[item]['record_digest'])

    def test_authored_workload_and_source_links_are_exact(self):
        chapter=(ROOT/'chapters/chapter-22-freshness-versions-and-incremental-indexes.md').read_text('utf-8')
        lab=(ROOT/'labs/chapter-22/LAB.md').read_text('utf-8')
        self.assertIn('`ch22-versioned-evidence-v1`',chapter)
        self.assertNotIn('-v 1',chapter);self.assertIn('fixtures_ch22/A06-v2.md',lab);self.assertIn('fixtures_ch22/A06-v3.md',lab)

    def test_stale_cutover_refused_and_rollback_gated(self):
        g=Generation('old',self.initial(),'body',self.checkpoint['bank'],self.capsules);m=Migration(g)
        other=Generation('new',self.initial(),'entity-body',self.checkpoint['bank'],self.capsules);m.add(other)
        self.assertFalse(m.cutover('old','new',self.final_authority()));self.assertEqual(m.active,'old')
        with self.assertRaises(ValueError):m.cutover('wrong','new',self.initial())

    def test_live_migration_results(self):
        m=self.record['migration'];self.assertFalse(m['unsafe_cutover']);self.assertTrue(m['valid_cutover']);self.assertTrue(m['rollback']);self.assertTrue(m['same_dimension_incompatible_query_rejected'])

    def test_partial_publication_retry_reconciles_duplicate(self):
        store=self.initial();bank=copy.deepcopy(self.checkpoint['bank']);g=Generation('old',store,'body',bank,self.capsules)
        bank['body']['A06@2']=[float('nan')]*384
        with self.assertRaises(ValueError):g.publish(store,self.commits[0][1],1200)
        self.assertEqual(store.heads['A06']['revision'],2);self.assertEqual(g.store.heads['A06']['revision'],1)
        bank['body']['A06@2']=self.checkpoint['bank']['body']['A06@2']
        transition,published=g.publish(store,self.commits[0][1],1250)
        self.assertEqual(transition['reason'],'duplicate_event');self.assertTrue(published);self.assertEqual(g.store.heads['A06']['revision'],2)

    def test_source_revision_capsule_contradiction(self):
        s=self.initial();e=copy.deepcopy(self.commits[0][1]);e['revision']=4;s.apply(e,1200)
        with self.assertRaises(ValueError):Generation('bad',s,'body',self.checkpoint['bank'],self.capsules)

    def test_cache_context_and_current_policy(self):
        authority=self.initial();g=Generation('old',authority,'body',self.checkpoint['bank'],self.capsules);p=Principal('A',frozenset({'reader'}));cache=ResultCache()
        key=cache.key(p,authority,g,'fixed-query-digest',None);item=self.capsules['A03@1']['unit']['item_id'];cache.put(key,[(item,.4)])
        self.assertEqual(cache.get(key,g,p,authority),[(item,.4)])
        self.assertIsNone(cache.get(key,g,p,self.final_authority()))
        self.assertIsNone(cache.get(key,g,Principal('B',frozenset({'reader'})),authority))

    def test_forged_cache_payload_denied(self):
        authority=self.final_authority();g=Generation('old',VersionStore.restore(self.checkpoint['final_stores']['ordered']),'body',self.checkpoint['bank'],self.capsules);p=Principal('A',frozenset({'reader'}));cache=ResultCache()
        key=cache.key(p,authority,g,'fixed-query',None);cache.put(key,[(self.capsules['A03@1']['unit']['item_id'],.5)])
        with self.assertRaises(ValueError):cache.get(key,g,p,authority)

    def test_per_principal_trace_and_actual_loss(self):
        queries={q['query_id']:q for q in self.labels['queries']}
        self.assertEqual(len(self.record['samples']),80)
        for r in self.record['samples']:
            q=queries[r['query_id']]
            point=self.checkpoint['checkpoints'][q['query_id']];a=VersionStore.restore(point['authority']);p=Principal(q['principal']['tenant'],frozenset(q['principal']['roles']))
            allowed={c['unit']['item_id'] for c in self.capsules.values() if current_allowed(a,c['unit']['source_id'],p,self.capsules) and authorized(c['unit'],p)}
            validate(r,allowed)
            for key in ('question','text','principal','exception'):self.assertNotIn(key,r)

    def test_final_metrics_negative_gap_and_hashes(self):
        self.assertAlmostEqual(self.record['aggregates']['ordered']['macro_recall_at_1'],5/6)
        self.assertAlmostEqual(self.record['aggregates']['arrival']['macro_recall_at_1'],4/6)
        for file,expected in self.record['code_sha256'].items():self.assertEqual(sha((HERE/file).read_bytes()),expected)
        self.assertEqual(sha((HERE/'qrels_ch22.json').read_bytes()),self.record['qrels_sha256'])

    def test_own_reducer_and_unsolved_starter(self):
        checker=ROOT/'labs/chapter-22/check_implementation.py';answer=ROOT/'solutions/code/chapter_22_mechanisms.py'
        good=subprocess.run([sys.executable,'-X','utf8',str(checker),str(answer)],capture_output=True)
        bad=subprocess.run([sys.executable,'-X','utf8',str(checker)],capture_output=True)
        self.assertEqual(good.returncode,0,good.stderr);self.assertNotEqual(bad.returncode,0);self.assertIn(b'NotImplementedError',bad.stderr)


if __name__=='__main__':unittest.main()
