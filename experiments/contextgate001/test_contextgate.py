"""Frozen controls for CONEXT-GATE-001. No external calls or mutable agents."""
import sys
from dataclasses import replace
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'selfmirror001'))
sys.path.insert(0,str(HERE/'fir001'))
sys.path.insert(0,str(HERE/'mathal001'))
from selfmirror import Move, Policy
from contextgate import (BASE,SPECIALIST,Episode,Gate,generate,digest,regret,
    train_gate,choose_validation,evaluate,policy_score,oracle_score,audit,
    preview_motif003,demonstration)


class ContextGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=generate('train',240)
        cls.valid=generate('validation',120)
        cls.test=generate('test',200)
        cls.ood=generate('ood',200,invert_sensor=True)
        cls.selected=choose_validation(cls.train,cls.valid)

    def test_frozen_splits_and_digests(self):
        self.assertEqual(self.train,generate('train',240))
        self.assertEqual(len({digest(x) for x in (self.train,self.valid,self.test,self.ood)}),4)
        self.assertFalse(set(x.key for x in self.train)&set(x.key for x in self.valid))

    def test_observed_signal_is_noisy_not_hidden_regime(self):
        mistakes=sum((x.signal=='amber') != (x.hidden_regime=='expansion') for x in self.train)
        self.assertGreater(mistakes,0)
        self.assertLess(mistakes,len(self.train)//3)

    def test_training_route_proposes_contextual_specialist(self):
        gate=train_gate(self.train,12,0.5)
        self.assertEqual(dict(gate.route)['amber'],'SPECIALIST')
        self.assertEqual(dict(gate.route)['blue'],'BASE')
        self.assertEqual(gate.train_digest,digest(self.train))

    def test_unknown_context_abstains_not_assumes(self):
        decision=self.selected.gate.choose('green',self.test[0].moves)
        self.assertEqual(decision.status,'HOLD_UNKNOWN_CONTEXT')
        self.assertIsNone(decision.selected)

    def test_missing_or_truncated_frontier_abstains(self):
        self.assertEqual(self.selected.gate.choose('amber',()).status,'HOLD_NO_MOVES')
        row=replace(self.test[0].moves[0],truncated=True)
        self.assertEqual(self.selected.gate.choose('amber',(row,)).status,'HOLD_INCOMPLETE_FRONTIER')

    def test_duplicate_actions_abstain(self):
        m=self.test[0].moves[0]
        self.assertEqual(self.selected.gate.choose('amber',(m,m)).status,'HOLD_DUPLICATE_ACTION')

    def test_thin_training_support_produces_hold(self):
        gate=train_gate(self.train[:2],12,0.5)
        self.assertTrue(all(v=='HOLD' for _,v in gate.route))
        self.assertEqual(gate.choose('amber',self.test[0].moves).status,'HOLD_INSUFFICIENT_EVIDENCE')

    def test_training_claim_cannot_force_admission(self):
        self.assertEqual(self.selected.status,'I_VALIDATION_SELECTION')
        self.assertTrue(any(r.get('operation')=='propose' for r in self.selected.receipt))
        self.assertFalse(any(r.get('operation')=='admit' for r in self.selected.receipt))

    def test_route_choice_does_not_read_hidden_label_or_rewards(self):
        ep=self.test[0]
        first=self.selected.gate.choose(ep.signal,ep.moves)
        changed=replace(ep,hidden_regime='altered',rewards=tuple(999-i for i in range(4)))
        self.assertEqual(first,self.selected.gate.choose(changed.signal,changed.moves))
        self.assertFalse(hasattr(self.selected.gate,'hidden_regime'))

    def test_validation_is_outcome_sensitive_but_holdout_not_input(self):
        other_valid=tuple(replace(e,rewards=tuple(-x for x in e.rewards)) for e in self.valid)
        self.assertNotEqual(digest(self.valid),digest(other_valid))
        self.assertEqual(self.selected,choose_validation(self.train,self.valid))
        self.assertEqual(self.selected.gate.train_digest,digest(self.train))
        self.assertNotEqual(self.selected.validation.mean_regret_all_with_hold_penalty,
                            evaluate(self.selected.gate,other_valid).mean_regret_all_with_hold_penalty)

    def test_frozen_gate_helps_on_clean_synthetic_holdout(self):
        g=evaluate(self.selected.gate,self.test)
        self.assertEqual(g.covered,len(self.test))
        self.assertLess(g.mean_regret_all_with_hold_penalty,policy_score(BASE,self.test))
        self.assertLess(g.mean_regret_all_with_hold_penalty,policy_score(SPECIALIST,self.test))

    def test_hostile_sensor_inversion_damages_gate(self):
        g=evaluate(self.selected.gate,self.ood)
        self.assertGreater(g.mean_regret_all_with_hold_penalty,policy_score(BASE,self.ood))
        result=audit(self.selected,self.test,self.ood)
        self.assertEqual(result['status'],'HOLD_SENSOR_SHIFT_REGRESSION')
        self.assertTrue(any(r.get('operation')=='refuse' for r in result['receipts']))

    def test_warrant_is_only_local_finite(self):
        result=audit(self.selected,self.test,self.ood)
        self.assertEqual(result['finite_test_role'],'F_LOCAL')
        admitted=[r for r in result['receipts'] if r.get('operation')=='admit']
        self.assertEqual(len(admitted),1)
        self.assertEqual(admitted[0]['scope'],'test:'+digest(self.test))
        self.assertNotIn('universal',admitted[0]['scope'])

    def test_oracle_gets_privileged_information_not_route(self):
        self.assertLessEqual(oracle_score(self.test),
                             max(policy_score(BASE,self.test),policy_score(SPECIALIST,self.test)))
        self.assertNotIn('hidden_regime',self.selected.gate.__dataclass_fields__)

    def test_incomplete_evaluation_count_has_declared_penalty(self):
        empty=Gate((('amber','HOLD'),('blue','HOLD')),(('amber',0),('blue',0)),
                   'empty',12,0.5)
        result=evaluate(empty,self.test[:5],hold_penalty=17)
        self.assertEqual(result.covered,0)
        self.assertEqual(result.mean_regret_all_with_hold_penalty,17)
        self.assertIsNone(result.mean_regret_covered)

    def test_refuse_invalid_fixtures(self):
        with self.assertRaises(ValueError):generate('test',0)
        with self.assertRaises(ValueError):generate('test',10,-1)
        with self.assertRaises(ValueError):generate('train',10,invert_sensor=True)
        with self.assertRaises(ValueError):train_gate(())
        with self.assertRaises(ValueError):train_gate(self.train,0)
        with self.assertRaises(ValueError):choose_validation(self.train,self.train)
        with self.assertRaises(ValueError):Episode('x','amber',self.test[0].moves,(), 'unknown')

    def test_motif003_preview_is_only_idea(self):
        rows=[{'operator':'test','roles':('r',),'immediate_delta':3,
               'new_affordances':(('more',('a',)),),
               'reachable_after_first_move':3,'truncated':False}]
        d=preview_motif003(rows,'amber',self.selected.gate)
        self.assertEqual(d.status,'I_PROPOSAL_ONLY')
        self.assertTrue(d.selected)
        self.assertEqual(preview_motif003(rows,'unknown',self.selected.gate).status,
                         'HOLD_UNKNOWN_CONTEXT')

    def test_real_motif003_bridge_is_read_only(self):
        if not (HERE/'003'/'affordance.py').exists():
            self.skipTest('actual MOTIF-003 only in repository checkout')
        sys.path.insert(0,str(HERE/'003'))
        sys.path.insert(0,str(HERE/'002'))
        from motif002 import induce,lessons,scene,possibilities,utility
        from affordance import analyze_first_moves
        w=scene()
        rows=analyze_first_moves(w,induce(lessons()),possibilities,utility)
        d=preview_motif003(rows,'amber',self.selected.gate)
        self.assertEqual(d.status,'I_PROPOSAL_ONLY')
        self.assertEqual(w,scene())

    def test_reproducible_honest_report(self):
        x=demonstration()
        self.assertEqual(x,demonstration())
        self.assertFalse(x['autonomous_self_modification'])
        self.assertEqual(x['external_actions'],0)
        self.assertEqual(x['generalization_status'],'HOLD_SENSOR_SHIFT_REGRESSION')


if __name__=='__main__':unittest.main()
