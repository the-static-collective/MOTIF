"""Adversarial tests: cross-view inquiry is useful question transfer, NOT evidence creation."""
import copy
import tempfile
import unittest
from pathlib import Path
from cross_lens import CrossLensInquiry,render_svg,ViewError,LENSES
from fixtures import make_engine
from benchmark import run as benchmark
from demo import run as demo

class CrossLensTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.field,self.engine,self.rels=make_engine(Path(self.temp.name)/'fixture.jsonl')
        self.solver=CrossLensInquiry(self.engine)

    def test_initial_question_from_two_neighbors_not_geometric_proximity(self):
        first=self.solver.start(max_steps=0)
        self.assertEqual(len(first['initial_inquiries']),1)
        inquiry=first['initial_inquiries'][0]
        self.assertEqual(set(inquiry['topic']),{'m:food','m:meal'})
        self.assertEqual(len(inquiry['witness_relation_ids']),4)
        self.assertEqual(inquiry['status'],'QUESTION_ONLY')
        self.assertFalse(first['steps'])

    def test_carried_questions_across_three_distinct_lenses(self):
        report=self.solver.start(max_steps=3,policy='sequential')
        self.assertEqual(report['visited_lenses'],['dependency','tension','affordance'])
        self.assertEqual([s['sequence'] for s in report['steps']],[1,2,3])
        kinds={q['kind'] for q in report['carried_questions']}
        self.assertEqual(kinds,{'association_bridge','verify_prerequisite','resolve_tension','test_conditional_enablement'})
        for step in report['steps']:
            self.assertFalse(step['geometry_used_for_evidence'])
            self.assertEqual(step['survival'],'QUESTION_ONLY')
            self.assertFalse(step['pen_promotion'])

    def test_local_tension_not_unrelated_decoy(self):
        report=self.solver.start(policy='sequential')
        tensions=[q for q in report['carried_questions'] if q['kind']=='resolve_tension']
        self.assertEqual(len(tensions),1)
        self.assertEqual(tensions[0]['topic'],['m:venue-open','m:venue-closed'])
        self.assertIn('r:disputed-venue',tensions[0]['witness_relation_ids'])
        self.assertTrue(all('home' not in str(q['topic']) for q in tensions))

    def test_no_hypothesis_can_become_witness(self):
        report=self.solver.start(policy='sequential')
        self.assertTrue(all('r:hypothetical-direct' not in q['witness_relation_ids'] for q in report['carried_questions']))
        self.assertEqual(report['assertion_promotion'],'NONE')
        self.assertEqual(report['pen_status'],'UNCHANGED')
        self.assertEqual(report['effective_external_authority'],'NONE')

    def test_same_snapshot_no_mutation_or_new_assertions(self):
        before=copy.deepcopy(self.field.snapshot())
        links=copy.deepcopy(self.rels)
        self.solver.start(max_steps=3)
        self.assertEqual(self.field.snapshot(),before)
        self.assertEqual(self.rels,links)

    def test_full_none_geometry_same_questions(self):
        visual=self.solver.start(max_steps=3,policy='sequential',allow_geometry=True)
        no_map=self.solver.evidence_only_full_control()
        self.assertEqual(visual['carried_questions'],no_map['carried_questions'])
        self.assertEqual(no_map['view_cost_units'],0)
        self.assertEqual(no_map['lens_inspection_count'],3)

    def test_reordering_and_geometry_toggle_cannot_alter_questions(self):
        a=self.solver.start(max_steps=3,policy='source_first')
        b=self.solver.start(max_steps=3,policy='sequential',allow_geometry=False)
        self.assertEqual({q['id'] for q in a['carried_questions']}, {q['id'] for q in b['carried_questions']})
        self.assertEqual(a['source_digest'],b['source_digest'])

    def test_source_first_ranks_local_question_pressure(self):
        report=self.solver.start(max_steps=2,policy='source_first')
        self.assertEqual(report['visited_lenses'][:1],['dependency'])
        self.assertLessEqual(report['lens_inspection_count'],2)
        self.assertEqual(report['view_cost_units'],2)

    def test_operator_feedback_defer_lens_without_changing_source(self):
        report=self.solver.start(max_steps=2,feedback=('dependency',),policy='sequential')
        self.assertEqual(report['visited_lenses'],['tension','affordance'])
        self.assertIn('dependency',report['operator_deferred_lenses'])
        self.assertNotIn('verify_prerequisite',{q['kind'] for q in report['carried_questions']})

    def test_resume_recomputes_and_confirms_original(self):
        first=self.solver.start(max_steps=3)
        again=self.solver.resume(first,max_steps=3)
        self.assertEqual(first,again)

    def test_invalid_prior_receipt_cannot_inject_question(self):
        old=self.solver.start()
        bad=copy.deepcopy(old)
        bad['carried_questions'][0]['status']='CERTIFIED'
        with self.assertRaisesRegex(ViewError,'integrity'):
            self.solver.resume(bad)
        bad=copy.deepcopy(old);bad['initial_inquiries'][0]['id']='unknown'
        with self.assertRaisesRegex(ViewError,'integrity'):
            self.solver.resume(bad)

    def test_source_change_stales_prior_inquiry(self):
        old=self.solver.start()
        revised=copy.deepcopy(self.rels)
        revised.append({'id':'r:new','source':'m:meal','target':'m:food',
                'predicate':'contradicts','origin':'fixture:later','status':'AUTHORED'})
        from multiview import ThoughtViews
        changed=CrossLensInquiry(ThoughtViews(self.field.snapshot(),revised))
        with self.assertRaisesRegex(ViewError,'STALE_SOURCE'):
            changed.resume(old)

    def test_identity_change_stales_prior_even_if_relationships_same(self):
        old=self.solver.start()
        self.field.revise_concept('c:food','Food revised','different local meaning','fixture:revision')
        from multiview import ThoughtViews
        changed=CrossLensInquiry(ThoughtViews(self.field.snapshot(),self.rels))
        with self.assertRaisesRegex(ViewError,'STALE_SOURCE'):
            changed.resume(old)

    def test_moving_placement_does_not_change_questions_or_source_semantics(self):
        old=self.solver.start()
        self.field.move('p:one',-100000,90000,'sketch drift',expected_revision=1)
        from multiview import ThoughtViews
        moved=CrossLensInquiry(ThoughtViews(self.field.snapshot(),self.rels))
        new=moved.start()
        self.assertEqual(old['carried_questions'],new['carried_questions'])
        self.assertEqual(old['source_digest'],new['source_digest'])
        self.assertNotEqual(old['source_snapshot_digest'],new['source_snapshot_digest'])

    def test_unknown_input_max_steps_feedback_rejected(self):
        for kwargs in ({'max_steps':True},{'max_steps':99},{'allow_geometry':'yes'},
                       {'policy':'trust_flower'},{'feedback':['dependency','dependency']},
                       {'feedback':['mind_reading']}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ViewError):
                self.solver.start(**kwargs)
        with self.assertRaisesRegex(ViewError,'not in current'):
            self.solver.start(initial_question='q:unknown')

    def test_no_bridge_or_only_hypothetical_refuses_to_advance(self):
        for variant in ('no_bridge','hypothesis_only'):
            with tempfile.TemporaryDirectory() as temp:
                _,engine,_=make_engine(Path(temp)/'other.jsonl',variant)
                result=CrossLensInquiry(engine).start()
                self.assertEqual(result['status'],'HOLD_NO_WITNESSED_BRIDGE')
                self.assertEqual(result['carried_questions'],[])
                self.assertEqual(result['steps'],[])

    def test_no_tension_shows_no_tension_question(self):
        with tempfile.TemporaryDirectory() as temp:
            _,engine,_=make_engine(Path(temp)/'other.jsonl','no_tension')
            result=CrossLensInquiry(engine).start()
            self.assertNotIn('resolve_tension',{q['kind'] for q in result['carried_questions']})

    def test_svg_escapes_dynamic_labels_and_shows_hold(self):
        report=self.solver.start(max_steps=3)
        svg=render_svg(report)
        self.assertIn('MOTIF / Cross-Lens Inquiry',svg)
        self.assertIn('HOLD:',svg)
        # actual content controlled by constant prompts but renderer still escapes
        self.assertNotIn('<script>',svg)

    def test_reproducibility_on_same_source(self):
        self.assertEqual(self.solver.start(policy='sequential'),self.solver.start(policy='sequential'))

    def test_benchmark_and_demo(self):
        b=benchmark()
        self.assertEqual(b['status'],'PASS')
        self.assertEqual(b['passed'],6)
        d=demo()
        self.assertTrue(d['deterministic_replay'])
        self.assertTrue(d['source_only_full_control_parity'])
        self.assertEqual(d['authority'],'NONE')

if __name__=='__main__': unittest.main()
