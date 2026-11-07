"""Adversarial, isolated controls for DECODER-INTEGRITY-001."""
import sys
from dataclasses import replace
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'contextgate001'))
sys.path.insert(0,str(ROOT/'selfmirror001'))
sys.path.insert(0,str(ROOT/'mathal001'))
sys.path.insert(0,str(ROOT/'fir001'))
from contextgate import choose_validation, generate, BASE
from decoderintegrity import (WitnessPair, audit_pairs, calibrate, Monitor, simulate,
    classical_signal_frequency_control, swap, demonstrate, pair_digest)


class DecoderIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate=choose_validation(generate('train',240),generate('validation',120)).gate
        cls.cal_fixture=audit_pairs('train',320)
        cls.cal=calibrate(tuple(p for _,p in cls.cal_fixture))
        cls.clean=audit_pairs('test',240)
        cls.shift=audit_pairs('ood',240,primary_inverted=True)
        cls.tandem=audit_pairs('ood',240,primary_inverted=True,audit_inverted=True)

    def test_reproducible_world_and_audit_pairs(self):
        self.assertEqual(self.cal_fixture,audit_pairs('train',320))
        self.assertEqual(pair_digest(tuple(p for _,p in self.shift)),
                         pair_digest(tuple(p for _,p in audit_pairs('ood',240,primary_inverted=True))))

    def test_same_underlying_world_when_primary_inverted(self):
        reference=audit_pairs('ood',240)
        for (a,one),(b,two) in zip(reference,self.shift):
            self.assertEqual(a,b)
            self.assertEqual(one.audit,two.audit)
            self.assertEqual(swap(one.primary),two.primary)

    def test_reference_is_fallible_and_distinct(self):
        a=self.cal_fixture
        errors=sum((pair.audit=='amber') != (episode.hidden_regime=='expansion')
                   for episode,pair in a)
        self.assertGreater(errors,0)
        self.assertLess(errors,len(a)//4)
        self.assertTrue(all(p.primary_origin!=p.audit_origin for _,p in a))

    def test_calibration_has_finite_scope_and_bound(self):
        self.assertEqual(self.cal.count,320)
        self.assertLess(self.cal.lower_agreement,self.cal.estimated_agreement)
        self.assertGreater(self.cal.estimated_agreement,0.65)
        self.assertGreater(Monitor(self.cal).threshold,0.2)
        self.assertLess(Monitor(self.cal).threshold,self.cal.lower_agreement)

    def test_calibration_rejects_thin_or_dependent_data(self):
        pairs=tuple(p for _,p in self.cal_fixture)
        with self.assertRaises(ValueError):calibrate(pairs[:10])
        with self.assertRaises(ValueError):calibrate(pairs,confidence_budget=2)
        duplicate=pairs[:319]+(pairs[0],)
        with self.assertRaises(ValueError):calibrate(duplicate)
        with self.assertRaises(ValueError):calibrate((replace(pairs[0],audit=None),)+pairs[1:])
        with self.assertRaises(ValueError):calibrate((replace(pairs[0],audit_origin=pairs[0].primary_origin),)+pairs[1:])

    def test_live_decision_is_based_only_on_prior_state_and_primary(self):
        ep,pair=self.shift[0]
        mon=Monitor(self.cal)
        before=mon.decide(self.gate,pair.primary,ep.moves)
        self.assertEqual(before.status,'I_PROPOSAL_ONLY')
        # No feedback for current episode until AFTER decision.
        self.assertEqual(mon.checks,0)
        mon.observe(pair)
        self.assertEqual(before.status,'I_PROPOSAL_ONLY')
        self.assertEqual(mon.state,'WATCH')

    def test_clean_monitor_does_not_alarm(self):
        r=simulate(self.gate,self.cal,self.clean)
        self.assertEqual(r.final_state,'WATCH')
        self.assertIsNone(r.alarm_index)
        self.assertEqual(r.covered,len(self.clean))

    def test_attacked_monitor_reopens_decoder_assumption(self):
        r=simulate(self.gate,self.cal,self.shift)
        self.assertEqual(r.final_state,'DEGRADED')
        self.assertIsNotNone(r.alarm_index)
        self.assertGreaterEqual(r.alarm_index,47)
        self.assertLess(r.alarm_index,100)
        self.assertTrue(any(x.get('operation')=='reopen' for x in r.receipts))
        self.assertTrue(any(x.get('operation')=='agreement_alarm' for x in r.receipts))
        self.assertTrue(any(x.get('mechanism_claim')=='I_ONLY' for x in r.receipts))

    def test_shift_reduces_regret_vs_unprotected_gate(self):
        r=simulate(self.gate,self.cal,self.shift)
        full=0
        for episode,pair in self.shift:
            choice=self.gate.choose(pair.primary,episode.moves)
            index=[m.name for m in episode.moves].index(choice.selected)
            full+=max(episode.rewards)-episode.rewards[index]
        self.assertLess(r.mean_regret_penalized,full/len(self.shift))
        # Adaptive fallback is not guaranteed to outperform fixed BASE.
        self.assertGreater(r.mean_regret_penalized,
                           sum(max(e.rewards)-e.rewards[BASE.choose(e.moves)]
                               for e,_ in self.shift)/len(self.shift))

    def test_synchronized_sensor_inversion_undetectable_here(self):
        r=simulate(self.gate,self.cal,self.tandem)
        self.assertEqual(r.final_state,'WATCH')
        self.assertIsNone(r.alarm_index)
        shifted=simulate(self.gate,self.cal,self.shift)
        self.assertGreater(r.mean_regret_penalized,shifted.mean_regret_penalized)

    def test_audit_only_inversion_causes_false_attribution_risk(self):
        # Same observed primary, but audit channel is compromised. Monitor
        # detects disagreement, not which witness is responsible.
        audit_bad=audit_pairs('ood',240,audit_inverted=True)
        good_primary=audit_pairs('ood',240)
        self.assertTrue(all(a.primary==b.primary for (_,a),(_,b) in zip(audit_bad,good_primary)))
        bad=simulate(self.gate,self.cal,audit_bad)
        good=simulate(self.gate,self.cal,good_primary)
        self.assertEqual(bad.final_state,'DEGRADED')
        self.assertEqual(good.final_state,'WATCH')
        self.assertGreater(bad.mean_regret_penalized,good.mean_regret_penalized)

    def test_same_source_metadata_forces_hold(self):
        m=Monitor(self.cal)
        ep,p=self.clean[0]
        m.observe(replace(p,audit_origin=p.primary_origin))
        self.assertEqual(m.state,'HOLD_SHARED_ORIGIN')
        self.assertEqual(m.decide(self.gate,p.primary,ep.moves).status,'HOLD_SHARED_ORIGIN')
        self.assertIn(m.working_assumption,m.world.ideas)
        self.assertNotIn(m.working_assumption,m.world.facts)

    def test_fake_distinct_metadata_cannot_establish_true_independence(self):
        # This is a LIMITATION test: an adversary can label correlated sensors as distinct.
        fake=audit_pairs('ood',240,primary_inverted=True,audit_inverted=True)
        self.assertTrue(all(x.primary_origin!=x.audit_origin for _,x in fake))
        self.assertEqual(simulate(self.gate,self.cal,fake).final_state,'WATCH')

    def test_repeated_missing_audits_hold_instead_of_false_confidence(self):
        m=Monitor(self.cal,max_missing_run=3)
        for ep,p in self.clean[:3]:
            m.observe(replace(p,audit=None))
        self.assertEqual(m.state,'HOLD_MISSING_AUDIT')
        self.assertEqual(m.decide(self.gate,self.clean[3][1].primary,self.clean[3][0].moves).status,
                         'HOLD_MISSING_AUDIT')

    def test_duplicate_audit_event_rejected(self):
        m=Monitor(self.cal)
        p=self.clean[0][1]
        m.observe(p)
        with self.assertRaises(ValueError):m.observe(p)

    def test_exhausted_horizon_fails_closed(self):
        m=Monitor(self.cal,window=2,max_checks=1)
        for ep,p in self.clean[:3]:m.observe(p)
        self.assertEqual(m.state,'HOLD_MONITOR_HORIZON')

    def test_invalid_tokens_and_parameters(self):
        with self.assertRaises(ValueError):WitnessPair('a','green','blue')
        with self.assertRaises(ValueError):WitnessPair('a','amber','red')
        with self.assertRaises(ValueError):swap('red')
        with self.assertRaises(ValueError):audit_pairs('test',100,audit_reliability=-1)
        with self.assertRaises(ValueError):Monitor(self.cal,window=1)

    def test_only_limited_local_claim_is_admitted(self):
        m=Monitor(self.cal)
        for ep,p in self.shift[:100]:m.observe(p)
        self.assertEqual(m.state,'DEGRADED')
        admitted=[(x,w) for x,w in m.world.facts.items()]
        self.assertEqual(len(admitted),1)
        claim,warrant=admitted[0]
        self.assertIn('agreement below',claim.text)
        self.assertEqual(warrant.kind,'finite_computation')
        self.assertNotIn('inversion',claim.text.lower())
        self.assertIn(m.working_assumption,m.world.ideas)

    def test_learning_does_not_consume_test_or_ood_labels(self):
        ep,p=self.shift[0]
        with_changed_outcomes=replace(ep,rewards=tuple(x*17 for x in ep.rewards),
                                      hidden_regime='hidden-other')
        a=Monitor(self.cal)
        b=Monitor(self.cal)
        self.assertEqual(a.decide(self.gate,p.primary,ep.moves),
                         b.decide(self.gate,p.primary,with_changed_outcomes.moves))
        a.observe(p);b.observe(p)
        self.assertEqual(a.state,b.state)
        self.assertEqual(a.receipts,b.receipts)

    def test_single_sensor_ambiguous_under_inversion(self):
        clean_freq=classical_signal_frequency_control(audit_pairs('ood',240))
        flip_freq=classical_signal_frequency_control(self.shift)
        self.assertAlmostEqual(clean_freq+flip_freq,1.0)
        self.assertLess(abs(clean_freq-0.5),0.1)
        self.assertLess(abs(flip_freq-0.5),0.1)

    def test_result_is_reproducible_and_limits_explicit(self):
        r=demonstrate()
        self.assertEqual(r,demonstrate())
        self.assertEqual(r['real_actions'],0)
        self.assertEqual(r['automatic_code_changes'],0)
        self.assertIn('HOLD',r['generalization'])
        self.assertEqual(r['both_sensors_inverted']['final_state'],'WATCH')


if __name__=='__main__':unittest.main()
