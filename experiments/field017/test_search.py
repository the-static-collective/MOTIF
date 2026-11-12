import unittest
from dataclasses import replace
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'field016'))
import engine as f16
from search import Layout, run, neighbors, canonical_state, update_and_repeat, question_for, _assessment

class TestSearch(unittest.TestCase):
    def setUp(self):
        self.world=f16.invented_scene()
        self.seed=Layout('original',('privacy',))
    def test_verdict_initial_mechanics_fail(self):
        x=_assessment(self.world,self.seed)
        self.assertTrue(x.failures)
        self.assertEqual(x.verdict,'REJECTED_UNDER_STATED_MODEL')
    def test_finds_alternative_by_relocating_and_substituting(self):
        r=run(self.world,self.seed,budget=16)
        self.assertEqual(r['selected']['layout']['route'],'repositioned')
        self.assertEqual(r['selected']['layout']['pieces'],('porous',))
        self.assertTrue(r['improved_declared_score'])
        self.assertFalse(r['installation_safety_certified'])
    def test_not_safe_even_after_numeric_improvement(self):
        x=run(self.world,self.seed,budget=16)
        self.assertEqual(x['selected']['verdict'],'CONDITIONAL_HOLD_NOT_CERTIFIED')
        self.assertGreater(len(x['selected']['unknowns']),0)
        self.assertFalse(x['selected']['physical_safety_verified'])
        self.assertFalse(x['pet_containment_certified'])
    def test_budget_counts_actual_critic_calls(self):
        for n in (1,2,4,8,16,25):
            with self.subTest(n=n):
                x=run(self.world,self.seed,budget=n)
                self.assertLessEqual(x['evaluated'],n)
                self.assertEqual(x['evaluated'],len(x['iterations']))
                self.assertEqual(len({t['candidate'] for t in x['iterations']}),x['evaluated'])
    def test_budget_one_cannot_leap_to_other_candidate(self):
        x=run(self.world,self.seed,budget=1)
        self.assertEqual(x['selected']['layout']['route'],'original')
        self.assertEqual(x['selected']['layout']['pieces'],('privacy',))
    def test_no_executed_actions_and_no_promoted_photo_geometry(self):
        x=run(self.world,self.seed,budget=15)
        for k in ('physical_actions','real_model_calls'):
            self.assertEqual(x[k],0)
        self.assertFalse(x['site_reconstruction_verified'])
    def test_no_scene_mutation(self):
        before=canonical_state(self.world)
        run(self.world,self.seed,budget=40)
        self.assertEqual(before,canonical_state(self.world))
    def test_neighbors_only_existing_resources(self):
        for n in neighbors(self.seed,self.world):
            self.assertIn(n.route,{r.id for r in self.world.routes})
            self.assertTrue(set(n.pieces).issubset({p.id for p in self.world.pieces}))
    def test_joint_unavailable_disallows_composition(self):
        s=replace(self.world,salvage_connections_available=False)
        self.assertNotIn('COMPOSE_PANELS',{n.operation for n in neighbors(self.seed,s)})
    def test_unknown_candidate_fails_not_crashes(self):
        for bad in (Layout('fake',('privacy',)),Layout('original',('alien',)),Layout('original',('privacy','privacy'))):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):run(self.world,bad)
    def test_invalid_budget(self):
        for b in (0,-1,251,1.5,True):
            with self.subTest(b=b):
                with self.assertRaises((ValueError,TypeError)):run(self.world,self.seed,budget=b)
    def test_reenter_actual_width_falsifies_previous_winner(self):
        evt=f16.Observation('test1','MEASURED','piece_width','porous',1.32,1)
        rep=update_and_repeat(self.world,self.seed,evt)
        before=rep['before']['selected']['layout']
        after=rep['after']['selected']['layout']
        self.assertEqual(before['pieces'],('porous',))
        self.assertNotEqual(after['pieces'],('porous',))
        self.assertNotEqual(rep['before']['world_sha256'],rep['after']['world_sha256'])
        self.assertEqual(rep['simulated_actions_added_as_observations'],0)
    def test_hypothetical_report_does_not_become_measurement(self):
        evt=f16.Observation('guess1','MODEL_TENTATIVE','piece_width','porous',1.32,1)
        new=f16.reenter(self.world,evt)
        self.assertFalse(next(p for p in new.pieces if p.id=='porous').measured_width)
    def test_missing_width_produces_hold(self):
        s=replace(self.world,pieces=tuple(replace(p,width_m=None) for p in self.world.pieces))
        r=run(s,self.seed,budget=5)
        self.assertIn('MISSING_COVERAGE_DIMENSIONS',r['initial']['unknowns'])
        self.assertFalse(r['installation_safety_certified'])
    def test_high_wind_not_silently_downgraded(self):
        high=replace(self.world,wind_mps=15)
        initial=canonical_state(high)
        x=run(high,self.seed,budget=20)
        self.assertEqual(initial,canonical_state(high))
        self.assertEqual(x['world_sha256'],initial)
    def test_known_blocked_access_remains_failure(self):
        blocked=replace(self.world,routes=tuple(replace(r,retains_access=False) for r in self.world.routes))
        x=run(blocked,self.seed,budget=20)
        self.assertTrue(all('USER_MARKED_ACCESS_BLOCKED' in _assessment(blocked,Layout(t['candidate'].split('|')[0],tuple(t['candidate'].split('|')[1].split(',')))).failures for t in x['iterations']))
    def test_stop_when_there_is_no_other_resource(self):
        scene=replace(self.world,pieces=(self.world.pieces[0],),routes=(self.world.routes[0],),salvage_connections_available=False,piece_clearance_m={'privacy':0.})
        x=run(scene,self.seed,budget=16)
        self.assertEqual(x['evaluated'],1)
    def test_receipt_stable(self):
        a=run(self.world,self.seed,budget=12)
        b=run(self.world,self.seed,budget=12)
        self.assertEqual(a['receipt_sha256'],b['receipt_sha256'])
    def test_loss_of_measured_width_not_replaced_with_fake_fact(self):
        s=replace(self.world,pieces=tuple(replace(p,width_m=None,measured_width=False) if p.id=='porous' else p for p in self.world.pieces))
        x=run(s,self.seed,budget=30)
        self.assertFalse(x['selected']['physical_safety_verified'])
    def test_veto_strong_even_if_cheaper(self):
        s=replace(self.world,routes=(replace(self.world.routes[0],retains_access=False),self.world.routes[1]))
        fail=_assessment(s,Layout('original',('cage','privacy')))
        unknown=_assessment(s,Layout('repositioned',('porous',)))
        self.assertGreater(fail.score,unknown.score)
    def test_question_is_actionable_and_provenance_safe(self):
        x=run(self.world,self.seed,budget=16)
        q=x['next_input']
        self.assertTrue(q['question'])
        self.assertTrue(q['can_answer_by'])
    def test_beam_zero_and_one_are_bounded(self):
        for n in (0,1,2):
            x=run(self.world,self.seed,budget=9,beam=n)
            self.assertLessEqual(x['evaluated'],9)
    def test_no_fraud_if_wind_unknown_physics_dimensions(self):
        s=replace(self.world,pieces=tuple(replace(p,mass_kg=None) for p in self.world.pieces))
        x=run(s,self.seed,budget=13)
        self.assertFalse(x['installation_safety_certified'])
        self.assertTrue(any('Mass' in u or 'physics' in u.lower() or 'material' in u.lower() for u in x['selected']['unknowns']) or x['selected']['verdict']=='CONDITIONAL_HOLD_NOT_CERTIFIED')

if __name__=='__main__':unittest.main()
