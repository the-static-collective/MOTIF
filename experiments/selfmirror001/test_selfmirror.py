"""Independent checks of MOTIF SELF-MIRROR-001 bounded policy revision."""
import sys
from dataclasses import replace
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'mathal001'))
sys.path.insert(0, str(ROOT / 'fir001'))
from selfmirror import (Audit, Case, Move, Policy, dataset_digest, failures,
    generate_cases, measure, propose_revisions, choose_on_validation,
    grid_control, preview_motif003, audit_frozen, demonstration)


class SelfMirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = generate_cases('train', 60)
        cls.validation = generate_cases('validation', 40)
        cls.test = generate_cases('test', 80)
        cls.ood = generate_cases('ood', 80, 'shift')
        cls.base = Policy()
        cls.proposals = propose_revisions(cls.base, cls.train)
        cls.selection = choose_on_validation(cls.base, cls.proposals, cls.validation)

    def test_nonempty_training_failures_are_reconstructible(self):
        data = failures(self.base, self.train)
        self.assertGreater(len(data), 0)
        by_key = {x.key:x for x in self.train}
        for r in data:
            case = by_key[r['case']]
            rewards = dict(zip((x.name for x in case.moves),case.rewards))
            self.assertEqual(r['regret'],rewards[r['better']]-rewards[r['chosen']])

    def test_proposals_from_training_exclusively_remain_ideas(self):
        self.assertTrue(self.proposals)
        for revision in self.proposals:
            self.assertEqual(revision.fir_status,'I')
            self.assertNotEqual(revision.before,revision.after)
            self.assertNotEqual(revision.source_signature,revision.target_signature)
            self.assertTrue(any(r.get('operation')=='propose' for r in revision.source_receipt))
            self.assertFalse(any(r.get('operation')=='admit' for r in revision.source_receipt))
            self.assertTrue(any(r.get('op')=='diagnose' for r in revision.source_receipt))

    def test_independent_splits_have_distinct_digests(self):
        self.assertEqual(len({dataset_digest(x) for x in (
            self.train,self.validation,self.test,self.ood)}),4)
        self.assertEqual(self.train,generate_cases('train',60))

    def test_policy_does_not_depend_on_row_order_for_ties(self):
        a,b = Move('A',3,1,3),Move('B',3,1,3)
        p = Policy(2,1)
        self.assertEqual((a,b)[p.choose((a,b))].name,'A')
        self.assertEqual((b,a)[p.choose((b,a))].name,'A')

    def test_classical_immediate_policy_matches_argmax(self):
        for c in self.test:
            choice = self.base.choose(c.moves)
            self.assertEqual(c.moves[choice].immediate,
                             max(x.immediate for x in c.moves))

    def test_validated_change_beats_incumbent_on_validation(self):
        self.assertEqual(self.selection.status,'PROPOSED_VALIDATION_WIN')
        self.assertLess(self.selection.validation_after.mean_regret,
                        self.selection.validation_before.mean_regret)
        self.assertNotEqual(self.selection.policy,self.base)

    def test_candidate_is_a_bounded_policy_and_no_code_execution(self):
        p = self.selection.policy
        self.assertLessEqual(p.frontier_weight,6)
        self.assertLessEqual(p.reach_weight,2)
        with self.assertRaises(ValueError): Policy(-1,0)
        with self.assertRaises(ValueError): Policy(0,3)

    def test_no_failure_means_no_proposed_change(self):
        c=Case('a',(Move('A',20,0,1),Move('B',1,0,1)),(20,1),'iid')
        self.assertEqual(propose_revisions(self.base,(c,)),())

    def test_truncated_preview_refuses_selection(self):
        with self.assertRaises(ValueError):
            self.base.choose((Move('A',4,0,1,True),))
        row={'operator':'a','roles':('x',),'immediate_delta':4,
             'new_affordances':(), 'reachable_after_first_move':1,'truncated':True}
        preview=preview_motif003([row],self.base)
        self.assertEqual(preview['status'],'HOLD_INCOMPLETE_FRONTIER')
        self.assertFalse(preview['admitted_fact'])

    def test_motif003_shape_is_only_counterfactual(self):
        rows=[{'operator':'fix','roles':('b',),'immediate_delta':3,
               'new_affordances':(('teach',('a',)),),
               'reachable_after_first_move':2,'truncated':False},
              {'operator':'teach','roles':('a',),'immediate_delta':1,
               'new_affordances':(), 'reachable_after_first_move':1, 'truncated':False}]
        before=repr(rows)
        r=preview_motif003(rows,self.base)
        self.assertEqual(r['status'],'I')
        self.assertFalse(r['admitted_fact'])
        self.assertIn('fix',r['selection'])
        self.assertEqual(before,repr(rows))
        self.assertIsNone(preview_motif003([],self.base)['selection'])

    def test_invalid_nonunique_case_and_incomplete_outcome(self):
        with self.assertRaises(ValueError):
            Case('dups',(Move('A',1,1,1),Move('A',2,2,2)),(4,5),'iid')
        with self.assertRaises(ValueError):
            Case('incomplete',(Move('A',1,1,1),),(),'iid')

    def test_test_labels_cannot_influence_revisions_or_selection(self):
        changed_test=tuple(replace(c, rewards=tuple(-r for r in c.rewards)) for c in self.test)
        changed_ood=tuple(replace(c, rewards=tuple(-r for r in c.rewards)) for c in self.ood)
        self.assertNotEqual(dataset_digest(self.test),dataset_digest(changed_test))
        # The only two callable learning surfaces accept training and validation.
        self.assertEqual(self.proposals,propose_revisions(self.base,self.train))
        self.assertEqual(self.selection,choose_on_validation(self.base,self.proposals,self.validation))
        self.assertNotEqual(measure(self.selection.policy,self.test),
                            measure(self.selection.policy,changed_test))
        self.assertNotEqual(measure(self.selection.policy,self.ood),
                            measure(self.selection.policy,changed_ood))

    def test_negative_control_detects_harm_under_shift(self):
        audit=audit_frozen(self.base,self.selection,self.test,self.ood)
        self.assertLess(audit.test_after.mean_regret,audit.test_before.mean_regret)
        self.assertGreater(audit.ood_after.mean_regret,audit.ood_before.mean_regret)
        self.assertEqual(audit.generalization_status,'HOLD_OOD_REGRESSION')
        self.assertTrue(any(x.get('operation')=='refuse' for x in audit.receipts))

    def test_warrant_is_bounded_to_exact_finite_fixture(self):
        audit=audit_frozen(self.base,self.selection,self.test,self.ood)
        self.assertEqual(audit.narrow_test_role,'F_LOCAL')
        admits=[r for r in audit.receipts if r.get('operation')=='admit']
        self.assertEqual(len(admits),1)
        self.assertEqual(admits[0]['kind'],'finite_computation')
        self.assertEqual(admits[0]['scope'],'test:'+dataset_digest(self.test))
        self.assertTrue('finite test fixture' in audit.narrow_test_claim)
        self.assertNotIn('universal',audit.narrow_test_claim)

    def test_no_validation_gain_does_not_promote_a_policy(self):
        from selfmirror import Selection
        original=measure(self.base,self.validation)
        no_change=Selection(self.base,'HOLD_NO_VALIDATION_GAIN',original,original,0)
        audit=audit_frozen(self.base,no_change,self.test,self.ood)
        self.assertEqual(audit.narrow_test_role,'I')
        self.assertEqual(audit.generalization_status,'HOLD_UNPROVEN_GENERALIZATION')

    def test_strong_classical_search_is_reported_not_hidden(self):
        grid=grid_control(self.base,self.validation)
        matched=grid_control(self.base,self.validation,budget=len(self.proposals))
        self.assertEqual(grid.inspected_proposals,20)
        self.assertEqual(matched.inspected_proposals,len(self.proposals))
        self.assertLessEqual(grid.validation_after.mean_regret,
                             self.selection.validation_after.mean_regret+1e-12)

    def test_budgets_and_inputs_are_strict(self):
        with self.assertRaises(ValueError): propose_revisions(self.base,self.train,0)
        with self.assertRaises(ValueError):generate_cases('user',10)
        with self.assertRaises(ValueError):generate_cases('train',-2)
        with self.assertRaises(ValueError):generate_cases('train',10,'shift')
        with self.assertRaises(ValueError):measure(self.base,())

    def test_candidate_validation_rejects_foreign_F_claim(self):
        fake=replace(self.proposals[0],fir_status='F')
        with self.assertRaises(ValueError):
            choose_on_validation(self.base,(fake,),self.validation)

    def test_real_motif003_integration_when_checked_out(self):
        if not (ROOT/'003'/'affordance.py').exists():
            self.skipTest('MOTIF-003 actual implementation only in GitHub checkout')
        sys.path.insert(0,str(ROOT/'003'))
        sys.path.insert(0,str(ROOT/'002'))
        from affordance import analyze_first_moves
        from motif002 import induce, lessons, scene, possibilities, utility
        world=scene()
        rows=analyze_first_moves(world,induce(lessons()),possibilities,utility)
        preview=preview_motif003(rows,self.selection.policy)
        self.assertEqual(preview['status'],'I')
        self.assertFalse(preview['admitted_fact'])
        self.assertEqual(world,scene())

    def test_replay_output_is_deterministic(self):
        self.assertEqual(demonstration(),demonstration())
        output=demonstration()
        self.assertEqual(output['external_actions'],0)
        self.assertFalse(output['runtime_policy_changed'])
        self.assertEqual(output['finite_test_claim'],'F_LOCAL')
        self.assertEqual(output['generalization_status'],'HOLD_OOD_REGRESSION')

if __name__=='__main__': unittest.main()
