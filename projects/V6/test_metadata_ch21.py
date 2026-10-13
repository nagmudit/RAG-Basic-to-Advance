import copy
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from metadata_ch21 import *
from experiment_ch21 import load_corpus, load_labels, verify_snapshot, HERE, ROOT, digest, sha, WORKLOAD


def meta(item='r', tenant='A', role='reader', language='en', date='2026-10-06T00:00:00Z'):
    return {'schema_version': SCHEMA, 'policy_version': POLICY, 'record_id': item,
            'tenant': tenant, 'acl_roles': [role], 'owner': 'ops', 'entity': 'Orion',
            'parent_id': 'manual', 'version': 1, 'language': language,
            'published_at': date, 'updated_at': date, 'extraction_confidence': .9}


def row(item='r', tenant='A', role='reader', language='en', score=.8):
    return {'item_id': item, 'metadata': meta(item, tenant, role, language),
            'indexing_allowed': True, 'license': 'fixture',
            'vector': [score, math.sqrt(1-score*score)]+[0.]*382}


class Protected(dict):
    def __getitem__(self, key):
        if key in ('body', 'text', 'vector', 'anchors'):
            raise AssertionError('Protected content access')
        return super().__getitem__(key)


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.principal = Principal('A', frozenset({'reader'}))

    def test_offset_equivalence(self):
        self.assertEqual(instant('2026-10-06T05:30:00+05:30'), instant('2026-10-06T00:00:00Z'))

    def test_naive_invalid_dates(self):
        for value in ('2026-10-06', 'bad', None, 6):
            with self.assertRaises(ValueError): instant(value)

    def test_security_schema_missing_deny(self):
        for key in ('tenant', 'acl_roles', 'policy_version', 'schema_version'):
            r = row(); del r['metadata'][key]
            self.assertFalse(authorized(r, self.principal))

    def test_empty_acl_deny(self):
        r = row(); r['metadata']['acl_roles'] = []
        self.assertFalse(authorized(r, self.principal))

    def test_malformed_types_deny(self):
        for key, value in (('version', True), ('extraction_confidence', float('nan')), ('acl_roles', 'reader'), ('tenant', 1)):
            r = row(); r['metadata'][key] = value
            self.assertFalse(authorized(r, self.principal))
        self.assertFalse(authorized({'metadata': []}, self.principal))

    def test_role_overlap_does_not_override_tenant(self):
        self.assertFalse(authorized(row(tenant='B'), self.principal))
        self.assertFalse(authorized(row(role='admin'), self.principal))
        self.assertTrue(authorized(row(), Principal('A', frozenset({'reader', 'admin'}))))

    def test_license_is_hard(self):
        r = row(); r['license'] = None
        self.assertFalse(authorized(r, self.principal))
        r = row(); r['indexing_allowed'] = False
        self.assertFalse(authorized(r, self.principal))

    def test_invalid_principal(self):
        for tenant, roles in (('', frozenset({'reader'})), ('A', frozenset()), ('A', {'reader'})):
            with self.assertRaises(ValueError): Principal(tenant, roles)

    def test_null_is_not_wildcard(self):
        view = MetadataIndex([row(language=None)], self.principal)
        self.assertEqual(view.select({}), {'r'})
        self.assertEqual(view.select({'language': 'en'}), set())
        with self.assertRaises(ValueError): view.select({'language': None})

    def test_half_open_endpoint(self):
        r1, r2 = row('r1'), row('r2')
        r2['metadata']['published_at'] = '2026-10-07T00:00:00Z'
        view = MetadataIndex([r1, r2], self.principal)
        self.assertEqual(view.select({'published_gte': '2026-10-06T00:00:00Z', 'published_lt': '2026-10-07T00:00:00Z'}), {'r1'})

    def test_predicate_rejection(self):
        for p in ({'sql': 'DROP'}, {'version': True}, {'language': ['en']}, {'published_gte': '2026-10-07T00:00:00Z', 'published_lt': '2026-10-06T00:00:00Z'}):
            with self.assertRaises(ValueError): validate_predicate(p)

    def test_protected_content_never_accessed(self):
        view = MetadataIndex([row(), Protected(row('private', tenant='B')), Protected(row('admin', role='admin'))], self.principal)
        final, work = search(view, {}, [1.]+[0.]*383, 'semantic')
        self.assertEqual([i for i, _ in final], ['r'])
        self.assertEqual(work['scored_count'], 1)

    def test_recheck_before_vector_access(self):
        r = row(); view = MetadataIndex([r], self.principal)
        r['metadata']['acl_roles'] = ['admin']
        with self.assertRaises(ValueError): search(view, {}, [1.]+[0.]*383, 'semantic')

    def test_task_metadata_mutation_invalidates_view(self):
        r = row(); view = MetadataIndex([r], self.principal)
        r['metadata']['language'] = 'fr'
        with self.assertRaises(ValueError): view.select({'language': 'en'})

    def test_postfilter_retains_loss(self):
        rows = [row('r'+str(i), language='es' if i == 4 else 'en', score=.99-i*.1) for i in range(5)]
        view = MetadataIndex(rows, self.principal)
        q = [1.]+[0.]*383
        final, work = search(view, {'language': 'es'}, q, 'post3')
        self.assertEqual(final, [])
        self.assertEqual(work['reason'], 'shortlist_underfill')
        self.assertEqual(len(work['candidate_stages']['scored']), 5)
        self.assertEqual(len(work['candidate_stages']['shortlist']), 3)
        self.assertEqual(search(view, {'language': 'es'}, q, 'prefilter')[0][0][0], 'r4')

    def test_post9_has_no_universal_guarantee(self):
        rows = [row('r'+str(i).zfill(2), language='es' if i == 9 else 'en', score=.99-i*.08) for i in range(10)]
        view = MetadataIndex(rows, self.principal)
        self.assertEqual(search(view, {'language': 'es'}, [1.]+[0.]*383, 'post9')[0], [])

    def test_requested_tenant_cannot_switch_authority(self):
        view = MetadataIndex([row(), Protected(row('b', tenant='B'))], self.principal)
        self.assertEqual(search(view, {'tenant': 'B'}, [1.]+[0.]*383, 'prefilter')[0], [])

    def test_invalid_vector_and_depth(self):
        view = MetadataIndex([row()], self.principal)
        for q in ([1.], [float('nan')]+[0.]*383):
            with self.assertRaises(ValueError): search(view, {}, q, 'prefilter')
        with self.assertRaises(ValueError): search(view, {}, [1.]+[0.]*383, 'prefilter', True)

    def test_duplicate_identity(self):
        with self.assertRaises(ValueError): MetadataIndex([row(), row()], self.principal)

    def test_graph_bridge(self):
        adjacency = {'u': ['x'], 'x': ['y'], 'y': ['v'], 'v': []}
        scores = {'u': .2, 'x': .3, 'y': .4, 'v': .9}
        good, events = graph_walk(adjacency, scores, {'v'})
        bad, pruned = graph_walk(adjacency, scores, {'v'}, True)
        self.assertEqual(good, [('v', .9)]); self.assertEqual(bad, [])
        self.assertEqual([e['node'] for e in events], ['u', 'x', 'y', 'v'])
        self.assertEqual([e['score'] for e in events], [.2, .3, .4, .9])
        self.assertEqual(pruned[-1]['action'], 'task_pruned')
        self.assertNotIn('score', pruned[-1])


class BoundArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs, cls.rows, cls.dispositions = load_corpus()
        cls.labels = load_labels(cls.docs, cls.rows)
        cls.record = json.loads((HERE/'chapter-21-experiment.json').read_text('utf-8'))
        cls.snapshot = json.loads((HERE/'index_ch21/index.json').read_text('utf-8'))

    def test_postings_equal_independent_predicate_scan(self):
        for q in self.labels['queries']:
            view = MetadataIndex(self.rows, Principal(q['principal']['tenant'], frozenset(q['principal']['roles'])))
            self.assertEqual(view.select(q['predicate']), {i for i, r in view.rows.items() if matches(r['metadata'], q['predicate'])})

    def test_metadata_change_rejects_qrels(self):
        rows = copy.deepcopy(self.rows); rows[0]['metadata']['language'] = 'fr'; rows[0]['metadata_digest'] = digest(rows[0]['metadata'])
        with self.assertRaises(ValueError): load_labels(self.docs, rows)

    def test_locator_change_rejects_qrels(self):
        docs = copy.deepcopy(self.docs); docs[0]['blocks'][0]['locator']['line_start'] = 999
        with self.assertRaises(ValueError): load_labels(docs, self.rows)

    def test_source_bytes_change_rejects_qrels(self):
        docs = copy.deepcopy(self.docs); docs[0]['source_sha256'] = '0'*64
        with self.assertRaises(ValueError): load_labels(docs, self.rows)

    def test_snapshot_trust_and_mutation(self):
        verify_snapshot(self.snapshot, self.docs, self.rows, self.record['index_manifest_digest'])
        tampered = copy.deepcopy(self.snapshot); tampered['rows'][0]['vector'][0] += .01
        with self.assertRaises(ValueError): verify_snapshot(tampered, self.docs, self.rows, self.record['index_manifest_digest'])

    def test_all_samples_per_principal_and_negative_losses(self):
        from experiment_trace import validate
        queries = {q['query_id']: q for q in self.labels['queries']}
        self.assertEqual(len(self.record['samples']), 156)
        for rec in self.record['samples']:
            q = queries[rec['query_id']]
            view = MetadataIndex(self.snapshot['rows'], Principal(q['principal']['tenant'], frozenset(q['principal']['roles'])))
            validate(rec, view.rows)
            for forbidden in ('question', 'text', 'principal', 'tenant', 'excluded_ids'):
                self.assertNotIn(forbidden, rec)
            if rec['mode'] != 'query-encoding':
                self.assertTrue(set(rec['task_match_ids']) <= set(view.rows))
                self.assertIn('shortlist', rec['intermediate_candidate_ids'])
        self.assertLess(self.record['aggregates']['post3']['macro_oracle_recall_positive'], 1)
        self.assertEqual(self.record['aggregates']['semantic']['empty_correct_fraction'], 0)

    def test_roster_and_review_denominators(self):
        self.assertEqual(len(self.docs), 15)
        self.assertEqual(sum(d['status'] == 'blocked' for d in self.dispositions), 2)
        self.assertEqual(sum(len(q['relevant_sources']) for q in self.labels['queries']), 11)
        self.assertEqual(self.record['ordered_reload_checks'], 144)

    def test_code_and_qrel_hashes(self):
        for p, expected in self.record['code_sha256'].items():
            self.assertEqual(sha((HERE/p).read_bytes()), expected)
        self.assertEqual(sha((HERE/'qrels_ch21.json').read_bytes()), self.record['qrels_sha256'])

    def test_actual_model_input_contract(self):
        self.assertIn('canonical chunk body only', self.record['model']['encode_policy'])
        self.assertNotIn('title newline', self.record['model']['encode_policy'])
        self.assertEqual(max(self.snapshot['input_lengths_with_specials']), 64)

    def test_registry_and_historical_boundary(self):
        registry = json.loads((ROOT/'evaluation/WORKLOAD_REGISTRY.json').read_text('utf-8'))
        item = next(w for w in registry['workloads'] if w['workload_id'] == WORKLOAD)
        self.assertEqual(item['source_manifest_sha256'], self.labels['source_manifest_sha256'])
        self.assertEqual(item['judgment_count'], 108)
        # V5 is not imported as a new comparison workload or silently relabeled.
        historical = json.loads((ROOT/'projects/V5/chapter-20-experiment.json').read_text('utf-8'))
        self.assertEqual(historical['workload_id'], 'ch20-chunked-evidence-v1')

    def test_independent_answer_and_unsolved_starter(self):
        checker = ROOT/'labs/chapter-21/check_implementation.py'
        answer = ROOT/'solutions/code/chapter_21_mechanisms.py'
        good = subprocess.run([sys.executable, '-X', 'utf8', str(checker), str(answer)], capture_output=True)
        bad = subprocess.run([sys.executable, '-X', 'utf8', str(checker)], capture_output=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn(b'NotImplementedError', bad.stderr)


if __name__ == '__main__':
    unittest.main()
