"""Hostile, deterministic tests for recursive evidence and model symmetry."""
from dataclasses import replace
from itertools import product
from pathlib import Path
from random import Random
import sys
import unittest

from witnesschain import (ACCURACY, CHANNELS, HYPOTHESES, READINGS, State, Event,
    Witness, TruthReceipt, collapse, flip, _likelihood, expected_gain, propose,
    synthetic_cases, synthetic_event, from_probe_observation, demonstration,
    fir_receipt, investigate, challenge_reference)


class WitnessChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = synthetic_cases((1,1,1),7,100)
        state = State()
        for event,_ in cls.samples:
            state=state.add(event)
        cls.bare=state

    def test_three_channels_and_uniform_prior(self):
        self.assertEqual(len(HYPOTHESES),8)
        self.assertEqual(len(CHANNELS),3)
        self.assertEqual(len(ACCURACY),3)
        self.assertTrue(all(abs(v-.125)<1e-10 for v in State().probabilities().values()))

    def test_exact_global_flip_symmetry_for_every_observation(self):
        for bits in HYPOTHESES:
            flipped=tuple(1-x for x in bits)
            for tokens in product(READINGS,repeat=3):
                self.assertAlmostEqual(_likelihood(bits,tokens),_likelihood(flipped,tokens),places=14)

    def test_exact_symmetry_even_with_missing_channel(self):
        for bits in HYPOTHESES:
            opposite=tuple(1-x for x in bits)
            for readings in product((*READINGS,None),repeat=3):
                self.assertAlmostEqual(_likelihood(bits,readings),_likelihood(opposite,readings),places=14)

    def test_absolute_stays_held_regardless_of_repetition(self):
        result=self.bare.decision('absolute_polarity')
        self.assertEqual(result['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')
        self.assertLessEqual(result['confidence'],.50000000001)
        self.assertEqual(result['reference_count'],0)
        self.assertFalse(result['authenticity_verified'])

    def test_relative_question_can_be_answered_without_truth(self):
        result=self.bare.decision('primary_audit_alignment')
        self.assertEqual(result['status'],'I_RELATIVE_MODEL_ONLY')
        self.assertEqual(result['candidate'],'same')
        self.assertGreater(result['confidence'],.95)
        self.assertFalse(result['authenticity_verified'])

    def test_fixture_reference_changes_identifiability_conditionally(self):
        state=self.bare
        for e,t in self.samples[:10]:
            state=state.verify(TruthReceipt(e.id,t,'declared-synthetic-oracle'))
        result=state.decision('absolute_polarity')
        self.assertEqual(result['status'],'I_CONDITIONAL_ON_FIXTURE_REFERENCE')
        self.assertEqual(result['candidate'],'111')
        self.assertGreater(result['confidence'],.95)
        self.assertFalse(result['authenticity_verified'])

    def test_corrupt_truth_receipts_confidently_select_wrong_model(self):
        state=self.bare
        for e,t in self.samples[:10]:
            state=state.verify(TruthReceipt(e.id,flip(t),'compromised-reference'))
        result=state.decision('absolute_polarity')
        self.assertEqual(result['status'],'I_CONDITIONAL_ON_FIXTURE_REFERENCE')
        self.assertEqual(result['candidate'],'000')
        self.assertGreater(result['confidence'],.95)

    def test_forwarded_copies_count_as_one_observation(self):
        event=Event('e1',(
            Witness('root','primary','amber','root-A'),
            Witness('copy','primary','amber','fake-alias',('root',)),
            Witness('copy2','primary','amber','other-alias',('copy',)),
            Witness('audit','audit','amber','root-B'),
            Witness('ref','anchor','amber','root-C')))
        result=collapse(event)
        self.assertEqual(result.status,'ACCEPTED')
        self.assertEqual(result.copies_collapsed,2)
        self.assertEqual(dict(result.root_claims)['primary'],('root-A',))
        self.assertFalse(result.authenticated)
        self.assertEqual(State().add(event).accepted[0].readings,('amber',)*3)

    def test_conflicting_forwarded_source_is_held(self):
        e=Event('x',(Witness('r','primary','blue','A'),
                     Witness('forwards','primary','amber','B',('r',)),
                     Witness('a','audit','amber','C')))
        result=State().add(e)
        self.assertEqual(len(result.accepted),0)
        self.assertEqual(result.holds[0]['status'],'HOLD_CONFLICTING_COPIES')

    def test_two_independent_claimed_roots_in_same_channel_are_held(self):
        e=Event('x',(Witness('r','primary','blue','A'),
                     Witness('s','primary','blue','B'),
                     Witness('a','audit','amber','C')))
        self.assertEqual(collapse(e).status,'HOLD_MULTIPLE_ORIGINS_PER_CHANNEL')

    def test_shared_ancestry_across_channels_blocks_joint_likelihood(self):
        e=Event('x',(Witness('r','primary','blue','A'),
                     Witness('s','audit','blue','B',('r',))))
        s=State().add(e)
        self.assertEqual(len(s.accepted),0)
        self.assertEqual(s.holds[0]['status'],'HOLD_SHARED_UPSTREAM_ROOT')
        self.assertEqual(s.probabilities(),State().probabilities())

    def test_fake_disjoint_root_names_cannot_be_authenticated(self):
        e=Event('x',(Witness('p','primary','blue','CLAIM1'),
                     Witness('a','audit','blue','CLAIM2')))
        s=State().add(e)
        self.assertEqual(s.accepted[0].status,'ACCEPTED_PARTIAL')
        self.assertFalse(s.accepted[0].authenticated)
        self.assertEqual(s.decision('absolute_polarity')['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')

    def test_cycle_unknown_parent_duplicate_and_replay_are_refused(self):
        with self.assertRaisesRegex(ValueError,'cycle'):
            collapse(Event('x',(Witness('a','primary','blue','A',('b',)),
                                Witness('b','primary','blue','A',('a',)))))
        with self.assertRaisesRegex(ValueError,'unknown witness parent'):
            collapse(Event('x',(Witness('a','primary','blue','A',('missing',)),)))
        with self.assertRaisesRegex(ValueError,'duplicate witness id'):
            collapse(Event('x',(Witness('a','primary','blue','A'),Witness('a','audit','blue','B'))))
        s=State().add(self.samples[0][0])
        with self.assertRaisesRegex(ValueError,'replay'):s.add(self.samples[0][0])

    def test_partial_observations_are_allowed_without_manufacturing_information(self):
        e=Event('x',(Witness('p','primary','blue','A'),))
        s=State().add(e)
        self.assertEqual(len(s.accepted),1)
        self.assertEqual(s.accepted[0].status,'ACCEPTED_PARTIAL')
        self.assertTrue(all(abs(v-.125)<1e-12 for v in s.probabilities().values()))

    def test_unknown_questions_and_invalid_threshold_are_refused(self):
        with self.assertRaises(ValueError):self.bare.decision('knows_real_truth')
        with self.assertRaises(ValueError):self.bare.decision('absolute_polarity',confidence=1)
        with self.assertRaises(ValueError):expected_gain(self.bare,'UNKNOWN')

    def test_inquiry_query_gain_is_lost_under_symmetry_but_truth_is_informative(self):
        new=expected_gain(self.bare,'NEW_TRIPLET')
        existing=expected_gain(self.bare,'VERIFY_EXISTING',self.samples[0][0].id)
        self.assertLess(new,1e-7)
        self.assertGreater(existing,.01)
        query=propose(self.bare,frozenset({'NEW_TRIPLET','VERIFY_EXISTING'}),4)
        self.assertEqual(query.status,'I_SYNTHETIC_INQUIRY_PROPOSAL')
        self.assertEqual(query.action,'VERIFY_EXISTING')
        self.assertFalse(query.real_authority)

    def test_inquiry_budget_permission_and_no_information_hold(self):
        self.assertEqual(propose(self.bare,frozenset({'VERIFY_EXISTING'}),3).status,
                         'HOLD_NOT_ALLOWED_OR_AFFORDABLE')
        self.assertEqual(propose(self.bare,frozenset({'NEW_TRIPLET'}),1).status,
                         'HOLD_NO_INFORMATION')
        self.assertEqual(propose(self.bare,frozenset(),4).status,
                         'HOLD_NOT_ALLOWED_OR_AFFORDABLE')
        with self.assertRaises(ValueError):propose(self.bare,frozenset({'HACK'}),4)
        with self.assertRaises(ValueError):propose(self.bare,frozenset({'NEW_TRIPLET'}),-1)

    def test_repeated_reference_is_refused_and_original_state_unchanged(self):
        e,t=self.samples[0]
        updated=self.bare.verify(TruthReceipt(e.id,t,'synthetic'))
        self.assertEqual(len(self.bare.truth_receipts),0)
        with self.assertRaises(ValueError):updated.verify(TruthReceipt(e.id,t,'again'))
        with self.assertRaises(ValueError):self.bare.verify(TruthReceipt('missing','blue','fabricated'))
        with self.assertRaises(ValueError):TruthReceipt(e.id,t,'synthetic',fixture_attested=False)

    def test_adapter_downgrades_previous_trusted_anchor_to_fallible_channel(self):
        root=Path(__file__).resolve().parents[1]
        probe_path=str(root/'provenanceprobe001')
        sys.path.insert(0,probe_path)
        try:
            from provenanceprobe import Observation
        finally:
            sys.path.remove(probe_path)
        previous=Observation('prior','amber','blue','p','a','amber',True)
        converted=from_probe_observation(previous)
        state=State().add(converted)
        self.assertEqual(len(state.accepted),1)
        self.assertEqual(len(state.truth_receipts),0)
        self.assertEqual(state.decision('absolute_polarity')['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')

    def test_deterministic_fixtures_are_distinct_by_hypothesis(self):
        self.assertEqual(self.samples,synthetic_cases((1,1,1),7,100))
        other=synthetic_cases((0,0,0),7,100)
        self.assertNotEqual(self.samples,other)
        with self.assertRaises(ValueError):synthetic_cases((0,0,0),0,0)

    def test_cross_event_root_reuse_is_not_independent_sample(self):
        first=Event('first',(Witness('a','primary','amber','datum-X'),
                             Witness('b','audit','blue','datum-Y')))
        second=Event('second',(Witness('c','primary','amber','datum-X'),
                               Witness('d','audit','blue','datum-Z')))
        original=State().add(first)
        followed=original.add(second)
        self.assertEqual(len(followed.accepted),1)
        self.assertEqual(len(followed.holds),1)
        self.assertEqual(followed.holds[0]['status'],'HOLD_REUSED_UPSTREAM_DATUM')
        self.assertEqual(original.probabilities(),followed.probabilities())

    def test_query_relative_stop_can_skip_unnecessary_expensive_probe(self):
        rel=investigate(self.bare,'primary_audit_alignment',
                        frozenset({'VERIFY_EXISTING'}),100)
        self.assertEqual(rel['status'],'STOP_QUERY_SUFFICIENT_UNDER_MODEL')
        self.assertIsNone(rel['inquiry'])
        absolute=investigate(self.bare,'absolute_polarity',
                             frozenset({'VERIFY_EXISTING'}),4)
        self.assertEqual(absolute['status'],'I_SYNTHETIC_INQUIRY_PROPOSAL')
        self.assertEqual(absolute['inquiry'].action,'VERIFY_EXISTING')
        self.assertEqual(absolute['real_actions'],0)

    def test_reopening_declared_reference_restores_global_symmetry(self):
        e,t=self.samples[0]
        conditionally=self.bare.verify(TruthReceipt(e.id,t,'assumed-fixture'))
        result=challenge_reference(conditionally,e.id,'claimed reference compromised')
        self.assertEqual(len(conditionally.truth_receipts),1)
        self.assertEqual(len(result.after.truth_receipts),0)
        self.assertEqual(result.after.decision('absolute_polarity')['status'],
                         'HOLD_GLOBAL_FLIP_SYMMETRY')
        self.assertEqual(result.receipt['operation'],'reopen_synthetic_reference')
        self.assertEqual(result.receipt['reason'],'claimed reference compromised')
        with self.assertRaises(ValueError):challenge_reference(self.bare,e.id,'reason')
        with self.assertRaises(ValueError):challenge_reference(conditionally,e.id,'')

    def test_hidden_shared_noise_behind_distinct_roots_is_not_authenticated(self):
        s=State()
        for i in range(40):
            # Three channels copy a hidden common signal, yet assert fresh roots.
            # The graph cannot discover dependence that has been concealed.
            seen='amber' if i%2 else 'blue'
            e=Event(f'correlated{i}',tuple(Witness(f'{i}:{c}',c,seen,f'{i}:{c}')
                                           for c in CHANNELS))
            s=s.add(e)
        self.assertEqual(len(s.accepted),40)
        self.assertTrue(all(not x.authenticated for x in s.accepted))
        self.assertEqual(s.decision('absolute_polarity')['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')
        self.assertFalse(s.decision('primary_audit_alignment')['authenticity_verified'])

    def test_fir_count_warrant_not_posterior_admission(self):
        receipt=fir_receipt(self.bare)
        self.assertEqual(receipt['hypothesis_role'],'I')
        self.assertFalse(receipt['admitted_model'])
        self.assertEqual(receipt['ledger_count_role'],'F_LOCAL')
        self.assertEqual([r['operation'] for r in receipt['receipts']],
                         ['propose','propose','admit'])
        self.assertEqual(receipt['receipts'][-1]['kind'],'finite_computation')

    def test_equal_cost_benchmark_inference_is_reproducible(self):
        from benchmark import benchmark
        result=benchmark(seeds_per_regime=2)
        self.assertEqual(result,benchmark(seeds_per_regime=2))
        self.assertEqual(result['scenario_count'],16)
        self.assertEqual(result['without_reference_hold_rate'],1.0)
        self.assertEqual(result['equal_extra_budget'],16)
        self.assertFalse(result['reference_authentication_verified'])
        with self.assertRaises(ValueError):benchmark(0)

    def test_not_real_actuator_nor_general_proof(self):
        report=demonstration()
        self.assertEqual(report['real_queries'],0)
        self.assertEqual(report['automated_code_changes'],0)
        self.assertEqual(report['general_status'],'HOLD_REAL_WORLD_SOURCE_AUTHENTICITY_UNPROVEN')
        self.assertEqual(report['unreferenced_absolute']['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')


if __name__ == '__main__':
    unittest.main()
