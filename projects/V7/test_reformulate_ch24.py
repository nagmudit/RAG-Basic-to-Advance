"""Mechanism, evidence identity, eligibility, budget and correlated-stage gates."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import retrieval_ch24 as r
from reformulate_ch24 import admit, interleave, ready_tasks, rocchio, lock_for
from query_ch23 import interpret
from experiment_ch24 import restore_snapshot, scheduler_controls
from experiment_trace import validate


class AdmissionTests(unittest.TestCase):
    def p(self, text, lock='ok', branch='b'):
        return {'text': text, 'lock': lock, 'branch_id': branch}

    def test_original_reserved(self):
        chosen, _ = admit(' A11  retry ', [], 'ok')
        self.assertEqual(chosen[0]['text'], 'A11 retry')

    def test_duplicate_normalization(self):
        chosen, d = admit('A11 retry', [self.p(' A11 RETRY ')], 'ok')
        self.assertEqual(len(chosen), 1); self.assertEqual(d[0]['reason'], 'duplicate')

    def test_anchor_mismatch_precedes_other_reasons(self):
        _, d = admit('A11 retry', [self.p('A12 retry', 'other')], 'ok')
        self.assertEqual(d[0]['reason'], 'anchor_mismatch')

    def test_changed_id_rejects(self):
        _, d = admit('A11 retry', [self.p('A12 retry')], 'ok')
        self.assertEqual(d[0]['reason'], 'protected_atom_change')

    def test_lowercase_id_rejects(self):
        _, d = admit('A11 retry', [self.p('a11 retry')], 'ok')
        self.assertEqual(d[0]['reason'], 'protected_atom_change')

    def test_changed_number_rejects(self):
        _, d = admit('Orion HTTP 503', [self.p('Orion HTTP 429')], 'ok')
        self.assertEqual(d[0]['reason'], 'protected_atom_change')

    def test_changed_entity_rejects(self):
        _, d = admit('Orion retry', [self.p('Green retry')], 'ok')
        self.assertEqual(d[0]['reason'], 'protected_atom_change')

    def test_omitted_entity_does_not_mutate_typed_lock(self):
        selected, _ = admit('Orion retry', [self.p('try again')], 'ok')
        self.assertEqual(len(selected), 2)

    def test_same_entity_semantic_drift_can_pass(self):
        _, d = admit('Orion TLS', [self.p('Orion billing')], 'ok')
        self.assertTrue(d[0]['accepted'])  # Deliberate limitation, not a guarantee.

    def test_branch_budget(self):
        _, d = admit('Orion retry', [self.p('Orion backoff')], 'ok', max_branches=1)
        self.assertEqual(d[0]['reason'], 'branch_budget')

    def test_word_budget_counts_original(self):
        _, d = admit('Orion retry', [self.p('Orion backoff')], 'ok', max_words=3)
        self.assertEqual(d[0]['reason'], 'word_budget')

    def test_budget_inputs(self):
        for kw in ({'max_branches': True}, {'max_words': 0}, {'max_words': 1}):
            with self.assertRaises(ValueError): admit('Orion retry', [], 'ok', **kw)

    def test_reserved_branch(self):
        with self.assertRaises(ValueError): admit('Orion retry', [self.p('Orion backoff', branch='original')], 'ok')

    def test_duplicate_branch_id(self):
        with self.assertRaises(ValueError): admit('Orion retry', [self.p('Orion backoff'), self.p('Orion wait')], 'ok')

    def test_interleave_does_not_sort_scores(self):
        final, admission, owners, _ = interleave([('o', [('x', .2), ('z', .9)]), ('r', [('y', .99), ('x', .8)])])
        self.assertEqual(final, [('x', .2), ('y', .99)])
        self.assertEqual(owners, ['o', 'r']); self.assertEqual(admission[-1], ('z', .9))

    def test_interleave_retains_origin_of_duplicate(self):
        final, _, owners, _ = interleave([('o', [('x', .1)]), ('r', [('x', .9), ('y', .8)])])
        self.assertEqual(final[0], ('x', .1)); self.assertEqual(owners, ['o', 'r'])

    def test_empty_interleave(self):
        self.assertEqual(interleave([]), ([], [], [], []))

    def test_interleave_invalid_cap(self):
        with self.assertRaises(ValueError): interleave([], True)

    def test_dag_readiness(self):
        deps = {'a': [], 'b': [], 'c': ['a', 'b']}
        self.assertEqual(ready_tasks(deps, set(), set()), (['a', 'b'], []))
        self.assertEqual(ready_tasks(deps, {'a', 'b'}, set()), (['c'], []))

    def test_failed_dependency_propagates(self):
        self.assertEqual(ready_tasks({'a': [], 'b': ['a'], 'c': ['b']}, set(), {'a'}), ([], ['a', 'b', 'c']))

    def test_disconnected_cycle_rejects(self):
        with self.assertRaises(ValueError): ready_tasks({'free': [], 'a': ['b'], 'b': ['a']}, set(), set())

    def test_missing_dependency_rejects(self):
        with self.assertRaises(ValueError): ready_tasks({'a': ['absent']}, set(), set())

    def test_invalid_completion_rejects(self):
        with self.assertRaises(ValueError): ready_tasks({'a': []}, {'unknown'}, set())

    def test_rocchio_worked_example(self):
        v = rocchio([1, 0], [[0, 1]])
        self.assertAlmostEqual(v[0], 1/math.sqrt(1.25)); self.assertAlmostEqual(v[1], .5/math.sqrt(1.25))

    def test_rocchio_empty_feedback(self):
        self.assertEqual(rocchio([1, 0], []), [1, 0])

    def test_rocchio_zero_and_bad_shape(self):
        for q, positives in (([0, 0], []), ([1, 0], [[1]]), ([1, math.nan], [])):
            with self.assertRaises(ValueError): rocchio(q, positives)


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capsules, cls.authority, cls.old = r.load_sources()
        cls.labels, cls.drafts = r.load_labels(cls.capsules, cls.authority)
        cls.record = json.loads((r.HERE/'chapter-24-experiment.json').read_text('utf-8'))
        cls.payload, cls.gen = restore_snapshot(r.HERE/'index_ch24/snapshot.json', cls.record['snapshot_digest'], cls.capsules, cls.authority, cls.labels)

    def run_query(self, qid='q01', mode='multi', **kwargs):
        q = next(q for q in self.labels['queries'] if q['query_id'] == qid)
        contract = kwargs.pop('query_contract', self.gen.contract)
        return r.execute(q, self.drafts['queries'][qid], mode, 0, self.gen, self.authority,
            self.payload['inputs'][qid], self.payload['token_counts'], self.record['versions'], query_contract=contract, **kwargs)

    def test_historical_roster_immutable(self):
        self.assertEqual(len(self.old.capsules), 18); self.assertEqual(len(self.capsules), 28)

    def test_snapshot_digest(self):
        with self.assertRaises(ValueError): restore_snapshot(r.HERE/'index_ch24/snapshot.json', 'wrong', self.capsules, self.authority, self.labels)

    def test_stale_labels_fail(self):
        changed = copy.deepcopy(self.capsules); changed['A11@1']['document']['body'] += 'changed'
        with self.assertRaises(ValueError): r.load_labels(changed, self.authority)

    def test_stale_draft_fails(self):
        changed = copy.deepcopy(self.drafts); changed['queries']['q01']['multi'][0]['text'] += ' changed'
        scratch = r.ROOT/'build/test-temp'; scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            p = Path(directory)/'drafts.json'; p.write_text(json.dumps(changed), encoding='utf-8')
            with self.assertRaises(ValueError): r.load_labels(self.capsules, self.authority, drafts_path=p)

    def test_compatible_model_required_before_scoring(self):
        frames = []
        with patch.object(r, 'score_rows') as scorer:
            with self.assertRaises(ValueError): self.run_query(query_contract={}, trace_sink=frames)
            scorer.assert_not_called()
        self.assertEqual(frames[-1]['reason'], 'invalid_input')

    def test_shared_typed_publication_scope(self):
        _, _, _, parent, frames = self.run_query('q10')
        self.assertEqual({self.gen.rows[i]['source_id'] for i in parent['task_match_ids']}, {'A01', 'A02'})
        self.assertEqual(len({f['plan']['constraint_digest'] for f in frames}), 1)

    def test_other_tenant_hard_id_has_no_branch(self):
        _, packed, _, parent, _ = self.run_query('q12')
        self.assertEqual(parent['branch_request_ids'], []); self.assertEqual(packed, [])
        self.assertEqual(parent['context_ids'], [])

    def test_admin_hard_id_has_no_branch(self):
        _, _, _, parent, _ = self.run_query('q11')
        self.assertEqual(parent['raw_candidate_ids'], []); self.assertEqual(parent['task_match_ids'], [])

    def test_deleted_source_not_recovered_by_rewrite(self):
        _, _, _, parent, _ = self.run_query('q15')
        self.assertEqual(parent['branch_request_ids'], []); self.assertEqual(parent['status'], 'empty')

    def test_scoring_only_current_authorized_ids(self):
        original = r.score_rows; seen = []
        def check(view, ids, vector):
            sources = {view.rows[i]['source_id'] for i in ids}; seen.append(sources)
            self.assertFalse(sources & {'A03', 'A08', 'A19', 'B05'})
            return original(view, ids, vector)
        with patch.object(r, 'score_rows', side_effect=check): self.run_query()
        self.assertEqual(len(seen), 3)

    def test_guard_null_context_and_no_backend(self):
        for qid in ('q13', 'q14', 'q16'):
            with patch.object(r, 'score_rows') as scorer:
                _, _, _, parent, _ = self.run_query(qid)
                scorer.assert_not_called()
            self.assertIsNone(parent['context_ids']); self.assertNotIn('context', parent['stage_timings_ms'])

    def test_known_quantity_false_trigger_retained(self):
        q = next(q for q in self.labels['queries'] if q['query_id'] == 'q16')
        self.assertTrue(q['requirements']); self.assertFalse(q['guard'])
        _, _, plan, _, _ = self.run_query('q16'); self.assertEqual(plan['outcome'], 'unsupported')

    def test_hypothesis_number_change_falls_back_original(self):
        _, _, _, parent, _ = self.run_query('q09', 'hypothetical')
        self.assertEqual(parent['branch_shortlists'][0]['branch_id'], 'original')

    def test_encoder_budget_skips_variants(self):
        _, _, _, parent, _ = self.run_query(wordpiece_budget=16)
        self.assertEqual(len(parent['branch_request_ids']), 1)
        self.assertTrue(any(d['reason'] == 'encoder_budget' for d in parent['proposal_decisions']))

    def test_original_encoder_budget_rejects(self):
        with self.assertRaises(ValueError): self.run_query(wordpiece_budget=2)

    def test_wrong_prepared_text_rejects(self):
        q = self.labels['queries'][0]; inputs = copy.deepcopy(self.payload['inputs']['q01'])
        inputs['original']['text_sha256'] = 'wrong'
        with self.assertRaises(ValueError): r.execute(q, self.drafts['queries']['q01'], 'original', 0, self.gen, self.authority, inputs, self.payload['token_counts'], self.record['versions'], query_contract=self.gen.contract)

    def test_partial_timeout_retains_other_branches(self):
        _, _, _, parent, frames = self.run_query(faults={'rewrite-1': TimeoutError})
        self.assertEqual(parent['status'], 'partial'); self.assertTrue(parent['final_candidate_ids'])
        self.assertEqual(sum(f['status'] == 'failed' for f in frames[:-1]), 1)

    def test_all_timeouts_null_context(self):
        _, _, _, parent, _ = self.run_query(faults={b: TimeoutError for b in ('original', 'rewrite-1', 'rewrite-2')})
        self.assertEqual(parent['status'], 'failed'); self.assertIsNone(parent['context_ids'])

    def test_nonretryable_failure_preserves_correlated_error(self):
        frames = []
        with self.assertRaises(RuntimeError): self.run_query(faults={'rewrite-1': RuntimeError}, trace_sink=frames)
        self.assertEqual(frames[-1]['request_id'], frames[0]['parent_request_id'])
        self.assertEqual(frames[-1]['status'], 'failed')

    def test_envelopes_and_real_origin_scores(self):
        _, _, _, parent, frames = self.run_query()
        eligible = r.authorized_view(self.gen, self.authority, r.Principal('A', frozenset({'reader'})), None).rows
        for f in frames: validate(f, eligible)
        self.assertEqual(len(parent['raw_branch_ids']), len(parent['raw_candidate_ids']))
        children = {f['branch_id']: f for f in frames[:-1]}
        for item, score, owner in zip(parent['final_candidate_ids'], parent['final_candidate_scores'], parent['final_origin_branch_ids']):
            child = children[owner]; self.assertEqual(score, dict(zip(child['final_candidate_ids'], child['final_candidate_scores']))[item])

    def test_prepared_encodes_are_linked_and_not_claimed_as_request_time(self):
        _, _, _, parent, frames = self.run_query()
        encoding_ids = {f['request_id'] for f in self.record['encoding_samples']}
        self.assertTrue(all(f['prepared_encoding_request_id'] in encoding_ids for f in frames[:-1]))
        self.assertIn('request_time_encoding', parent['stages_not_run'])
        self.assertIsNone(parent['generator_cost'])

    def test_no_hypothesis_can_enter_context(self):
        _, _, _, parent, _ = self.run_query('q07', 'hypothetical')
        self.assertTrue(set(parent['context_ids']) <= set(self.gen.rows))
        self.assertNotIn('hypothesis', parent['context_ids'])

    def test_negative_results_are_retained(self):
        a = self.record['aggregates']
        self.assertEqual(a['original']['positive_recall_at_2'], a['multi']['positive_recall_at_2'])
        self.assertLess(a['hypothetical']['positive_recall_at_2'], a['original']['positive_recall_at_2'])
        self.assertGreater(a['multi']['scored_pairs'], a['original']['scored_pairs'])

    def test_control_workload_is_scheduler_only(self):
        frames = scheduler_controls(self.labels['corpus_version'])
        self.assertEqual(frames[0]['ready_task_ids'], ['combine'])
        self.assertEqual(frames[1]['blocked_task_ids'], ['combine', 'retry'])
        self.assertEqual([f['status'] for f in frames], ['partial', 'partial', 'invalid', 'invalid'])
        self.assertTrue(all(f['model_version'] is None and f['context_ids'] is None for f in frames))

    def test_record_core_hashes(self):
        for name, value in self.record['code_sha256'].items(): self.assertEqual(r.sha((r.HERE/name).read_bytes()), value)


if __name__ == '__main__': unittest.main()
