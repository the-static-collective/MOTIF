"""Reproducible hostile tests for PROVENANCE-PROBE-001, standard library only."""
from __future__ import annotations

from dataclasses import replace
from math import isclose
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'provenanceprobe001'))
sys.path.insert(0, str(ROOT / 'fir001'))
sys.path.insert(0, str(ROOT / 'mathal001'))
from provenanceprobe import (Belief, Observation, SourceClaim, collapse_forwarded,
    naive_majority, HYPOTHESES, likelihood, synthetic_batch, evaluate_once, fir_receipt,
    query_information, propose_inquiry, demonstration, sample_case)
from random import Random


class ProvenanceProbeTests(unittest.TestCase):
    def test_unanchored_clean_and_both_are_observationally_identical(self):
        for p in ('amber','blue'):
            for a in ('amber','blue'):
                self.assertEqual(likelihood('CLEAN',p,a),likelihood('BOTH_INVERTED',p,a))
                self.assertEqual(likelihood('PRIMARY_INVERTED',p,a),
                                 likelihood('AUDIT_INVERTED',p,a))

    def test_anchoring_breaks_the_symmetry(self):
        self.assertGreater(likelihood('CLEAN','amber','amber','amber'),
                           likelihood('BOTH_INVERTED','amber','amber','amber'))
        self.assertGreater(likelihood('BOTH_INVERTED','blue','blue','amber'),
                           likelihood('CLEAN','blue','blue','amber'))

    def test_predictive_probability_sums_to_one(self):
        for h in HYPOTHESES:
            p=sum(likelihood(h,a,b) for a in ('amber','blue') for b in ('amber','blue'))
            anchored=sum(0.5*likelihood(h,a,b,t)
                         for a in ('amber','blue') for b in ('amber','blue')
                         for t in ('amber','blue'))
            self.assertAlmostEqual(p,1)
            self.assertAlmostEqual(anchored,1)

    def test_pair_only_never_resolves_unidentifiable_pair(self):
        belief=Belief()
        for record in synthetic_batch('BOTH_INVERTED','AUDIT_PAIR',160):
            belief=belief.ingest(record)
        posterior=belief.probabilities()
        self.assertAlmostEqual(posterior['CLEAN'],posterior['BOTH_INVERTED'],places=12)
        self.assertEqual(belief.anchor_count,0)
        self.assertEqual(belief.classification()['identifiability'],'NO_ANCHOR_SYMMETRY')
        self.assertNotEqual(belief.classification()['status'],'F')

    def test_conditional_posterior_recovers_all_four_simulated_flip_models(self):
        for h in HYPOTHESES:
            outcome=evaluate_once(h)
            self.assertGreater(outcome['posterior_after_anchors'][h],0.90)
            self.assertLess(outcome['posterior_without_anchors'][h],0.51)
            self.assertEqual(outcome['final_status'],'I_MODEL_CONDITIONAL')

    def test_no_future_anchor_peeking(self):
        b=Belief()
        for pair in synthetic_batch('BOTH_INVERTED','AUDIT_PAIR',48):
            b=b.ingest(pair)
        before=b.probabilities()
        proposed=propose_inquiry(b,frozenset({'AUDIT_PAIR','VERIFY_ANCHOR'}),3)
        self.assertEqual(before,b.probabilities())
        self.assertFalse(proposed.can_execute_real_action)
        self.assertEqual(proposed.status,'I_SYNTHETIC_INQUIRY_PROPOSAL')
        self.assertEqual(b.anchor_count,0)

    def test_information_gain_invariant_under_pair_only_ambiguity(self):
        belief=Belief()
        for pair in synthetic_batch('BOTH_INVERTED','AUDIT_PAIR',160):
            belief=belief.ingest(pair)
        self.assertLess(query_information(belief,'AUDIT_PAIR'),1e-8)
        self.assertGreater(query_information(belief,'VERIFY_ANCHOR'),0.5)
        self.assertEqual(propose_inquiry(belief,frozenset({'AUDIT_PAIR','VERIFY_ANCHOR'}),3).query,
                         'VERIFY_ANCHOR')

    def test_new_environment_information_gain_prior_can_prefer_cheap_pair(self):
        prior=Belief()
        self.assertGreater(query_information(prior,'AUDIT_PAIR'),0)
        self.assertGreater(query_information(prior,'VERIFY_ANCHOR'),0)
        proposal=propose_inquiry(prior,frozenset({'AUDIT_PAIR','VERIFY_ANCHOR'}),3)
        self.assertTrue(proposal.cost in (1,3))
        self.assertGreater(proposal.information_gain_bits,0)

    def test_query_permission_and_budget_are_strict(self):
        prior=Belief()
        self.assertEqual(propose_inquiry(prior,frozenset(),3).status,
                         'HOLD_NOT_ALLOWED_OR_UNAFFORDABLE')
        self.assertEqual(propose_inquiry(prior,frozenset({'VERIFY_ANCHOR'}),2).query,None)
        self.assertEqual(propose_inquiry(prior,frozenset({'VERIFY_ANCHOR'}),3).query,
                         'VERIFY_ANCHOR')
        with self.assertRaises(ValueError):propose_inquiry(prior,frozenset({'REAL_WORLD_QUERY'}),10)
        with self.assertRaises(ValueError):propose_inquiry(prior,frozenset({'AUDIT_PAIR'}),-1)
        with self.assertRaises(ValueError):propose_inquiry(prior,frozenset({'AUDIT_PAIR'}),2,{'AUDIT_PAIR':0})

    def test_forwarded_copies_not_independent_votes(self):
        reports=(SourceClaim('1','Alice','alice','blue'),
                 SourceClaim('2','Bob','alice','blue'),
                 SourceClaim('3','Carol','alice','blue'),
                 SourceClaim('4','Dan','dan','amber'))
        self.assertEqual(naive_majority(reports),'blue')
        self.assertIsNone(naive_majority(reports,deduplicate=True))
        collapsed=collapse_forwarded(reports)
        self.assertEqual(collapsed.forwarded,2)
        self.assertFalse(collapsed.verified_independence)

    def test_spoofed_root_labels_can_defeat_deduplication(self):
        reports=tuple(SourceClaim(str(i),str(i),f'fabricated-{i}','blue') for i in range(3))
        reports+=(SourceClaim('honest','witness','honest','amber'),)
        summary=collapse_forwarded(reports)
        self.assertEqual(summary.forwarded,0)
        self.assertEqual(naive_majority(reports,deduplicate=True),'blue')
        self.assertFalse(summary.verified_independence)

    def test_same_asserted_root_must_hold_observation(self):
        b=Belief()
        row=Observation('event','amber','blue','root','root')
        after=b.ingest(row)
        self.assertEqual(after.probabilities(),b.probabilities())
        self.assertEqual(after.held_count,1)
        self.assertEqual(after.pair_count,0)
        self.assertEqual(after.receipts[-1]['status'],'HOLD_SHARED_ASSERTED_ROOT')

    def test_conflicting_claims_from_same_root_are_flagged(self):
        reports=(SourceClaim('r1','a','root','amber'),
                 SourceClaim('r2','b','root','blue'))
        self.assertEqual(collapse_forwarded(reports).conflicts,('root',))
        self.assertIsNone(naive_majority(reports,deduplicate=True))

    def test_event_replay_is_refused(self):
        row=Observation('id','amber','amber')
        once=Belief().ingest(row)
        with self.assertRaises(ValueError):once.ingest(row)
        with self.assertRaises(ValueError):collapse_forwarded((SourceClaim('r','a','s','blue'),
                                                                SourceClaim('r','b','t','blue')))

    def test_real_decoder_integrity_adapter_preserves_hold_and_declarations(self):
        sys.path.insert(0,str(ROOT/'decoderintegrity001'))
        from decoderintegrity import audit_pairs
        from provenanceprobe import ingest_decoder_witness_pairs
        sample=audit_pairs('test',12,missing_every=3)
        witness_only=tuple(pair for _episode,pair in sample)
        prior=repr(witness_only)
        belief=ingest_decoder_witness_pairs(witness_only)
        self.assertEqual(belief.pair_count,8)
        self.assertEqual(belief.held_count,4)
        self.assertEqual(belief.anchor_count,0)
        self.assertEqual(repr(witness_only),prior)
        self.assertEqual(sum(r['status']=='HOLD_MISSING_AUDIT' for r in belief.receipts),4)
        self.assertEqual(belief.classification()['identifiability'],'NO_ANCHOR_SYMMETRY')
        self.assertFalse(belief.classification()['verified_independence'])

    def test_no_unattested_anchor_admission(self):
        with self.assertRaises(ValueError):Observation('id','amber','blue',anchor='amber')
        with self.assertRaises(ValueError):Observation('id','amber','blue',fixture_anchor_attested=True)
        with self.assertRaises(ValueError):Observation('id','amber','blue',anchor='red',fixture_anchor_attested=True)

    def test_tampered_anchor_makes_inference_confidently_wrong(self):
        base=Belief()
        for pair in synthetic_batch('BOTH_INVERTED','AUDIT_PAIR',160):
            base=base.ingest(pair)
        clean, tampered=base,base
        for pair in synthetic_batch('BOTH_INVERTED','VERIFY_ANCHOR',24):
            clean=clean.ingest(pair)
        for pair in synthetic_batch('BOTH_INVERTED','VERIFY_ANCHOR',24,tamper_anchor=True):
            tampered=tampered.ingest(pair)
        self.assertGreater(clean.probabilities()['BOTH_INVERTED'],0.95)
        self.assertLess(tampered.probabilities()['BOTH_INVERTED'],0.05)
        self.assertNotEqual(tampered.classification()['status'],'F')

    def test_probabilities_are_stable_under_many_reports(self):
        b=Belief()
        for row in synthetic_batch('PRIMARY_INVERTED','AUDIT_PAIR',5000):
            b=b.ingest(row)
        probs=b.probabilities()
        self.assertAlmostEqual(sum(probs.values()),1,places=10)
        self.assertTrue(all(v>=0 for v in probs.values()))

    def test_fixture_has_no_truth_field_on_witness_record(self):
        row,truth=sample_case('PRIMARY_INVERTED','x',Random(1),anchor=False)
        self.assertFalse(hasattr(row,'true'))
        self.assertFalse(hasattr(row,'hidden_regime'))
        self.assertIsNone(row.anchor)
        self.assertIn(truth,('amber','blue'))

    def test_fir_evidence_only_admits_finite_count(self):
        b=Belief()
        for row in synthetic_batch('CLEAN','VERIFY_ANCHOR',4):
            b=b.ingest(row)
        receipt=fir_receipt(b)
        self.assertEqual(receipt['proposed_role'],'I')
        self.assertFalse(receipt['proposed_is_fact'])
        self.assertEqual(receipt['count_role'],'F_LOCAL')
        self.assertEqual([x['operation'] for x in receipt['receipts']],['propose','propose','admit'])
        self.assertEqual(receipt['receipts'][-1]['scope'],receipt['scope'])

    def test_cost_matched_independent_anchor_benchmark(self):
        from benchmark import benchmark
        result=benchmark(20)
        self.assertEqual(result,benchmark(20))
        self.assertEqual(result['query_cost_budget'],6)
        self.assertGreater(result['with_informative_anchor_accuracy'],
                           result['matched_cost_pairs_only_accuracy'] + 0.2)
        self.assertEqual(result['real_queries'],0)

    def test_reproducible_demo_and_no_external_mutation(self):
        result=demonstration()
        self.assertEqual(result,demonstration())
        self.assertEqual(result['real_inquiries_dispatched'],0)
        self.assertEqual(result['autonomous_code_changes'],0)
        self.assertEqual(result['inquiry']['type'],'VERIFY_ANCHOR')


if __name__=='__main__':
    unittest.main()
