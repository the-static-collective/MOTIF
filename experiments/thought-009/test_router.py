"""Metareasoning tests against classical source-only controls."""
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from router import Task, ViewRouter
from multiview import ViewError
from fixtures import make_engine
from benchmark import main as benchmark
from demo import main as demo

class RouterTests(unittest.TestCase):
    def setUp(self):
        self.t=TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.engine=make_engine(Path(self.t.name)/'field.jsonl')
        self.router=ViewRouter(self.engine)
    def task(self,*goals,**kw):return Task(tuple(goals),**kw)
    def test_multi(self):
        r=self.router.run(self.task('association','tension',max_views=2))
        self.assertEqual(r['selected_lenses'],['association','tension'])
        self.assertEqual(r['view_cost_units'],2)
    def test_zero(self):
        r=self.router.run(self.task('association','tension',max_views=0))
        self.assertEqual(r['selected_lenses'],[])
        self.assertEqual(r['view_cost_units'],0)
        self.assertTrue(r['questions'])
    def test_very_small_budget(self):
        r=self.router.run(self.task('association','tension','dependency',max_views=1))
        self.assertEqual(r['selected_lenses'],['dependency'])
        self.assertEqual(len([d for d in r['decisions'] if d['decision']=='BUDGET_DEFERRED']),2)
    def test_no_visual(self):
        r=self.router.run(self.task('tension',show_geometry=False))
        self.assertEqual(r['selected_lenses'],[])
        self.assertEqual(r['decisions'][0]['decision'],'OPERATOR_DISABLED')
    def test_non_geo_inventory(self):
        r=self.router.run(self.task('inventory'))
        self.assertEqual(r['selected_lenses'],[])
        self.assertEqual(r['decisions'][0]['decision'],'NON_GEOMETRIC_GOAL')
    def test_pen_review_never_does_mapping_or_commit(self):
        r=self.router.run(self.task('tension',phase='PEN_REVIEW'))
        self.assertEqual(r['selected_lenses'],[])
        self.assertEqual(r['pen_state'],'UNCHANGED')
        self.assertEqual(r['effective_external_authority'],'NONE')
    def test_preserve_hypotheses(self):
        r=self.router.run(self.task('association'))
        self.assertTrue(all(q['status']=='QUESTION_ONLY' for q in r['questions']))
        self.assertNotIn('r:unreviewed',[x['id'] for x in self.engine._authored('associated')])
    def test_no_map_parity(self):
        tasks=[self.task('association','dependency','tension','affordance',anchor='m:volunteers'),
               self.task('tension'),self.task('inventory')]
        for task in tasks:
            multi=self.router.run(task)
            control=self.router.run(Task(task.goals,anchor=task.anchor,max_views=0))
            self.assertEqual(multi['source_only_answers'],control['source_only_answers'])
            self.assertEqual(multi['questions'],control['questions'])
            self.assertEqual(multi['source_evidence_digest'],control['source_evidence_digest'])
    def test_change_seed_no_facts(self):
        a=self.router.run(self.task('association',seed=1))
        b=self.router.run(self.task('association',seed=2))
        self.assertEqual(a['questions'],b['questions'])
        self.assertEqual(a['source_only_answers'],b['source_only_answers'])
    def test_no_signal_abstains(self):
        engine=make_engine(Path(self.t.name)/'empty.jsonl','empty')
        r=ViewRouter(engine).run(self.task('tension','association'))
        self.assertEqual(r['selected_lenses'],[])
        self.assertTrue(all(x['decision']=='NO_WITNESSED_SIGNAL' for x in r['decisions']))
    def test_recycle_when_same_source(self):
        old=self.router.run(self.task('association'))
        new=self.router.run(self.task('association',phase='CONCRETE_PENCIL'),previous=old)
        self.assertFalse(new['prior_cycle_source_changed'])
        self.assertEqual(new['prior_cycle_digest'],old['receipt_digest'])
    def test_recycle_requires_review_on_changed_source(self):
        old=self.router.run(self.task('association'))
        links=copy.deepcopy(self.engine.relations)
        links.append(dict(id='new-link',source='m:food',target='m:van',predicate='associated',
                          origin='fixture:new',status='AUTHORED'))
        other=ViewRouter(type(self.engine)(self.engine._original,links))
        new=other.run(self.task('association'),previous=old)
        self.assertTrue(new['prior_cycle_source_changed'])
        self.assertTrue(new['prior_cycle_needs_revalidation'])
    def test_validation(self):
        for bad in [lambda:Task(('mystery',)),lambda:Task(('tension','tension')),
                    lambda:Task(('tension',),max_views=-1),
                    lambda:Task(('tension',),max_views=True),
                    lambda:Task(('tension',),phase='SUPERPEN'),
                    lambda:Task(('tension',),show_geometry='true')]:
            with self.assertRaises(ViewError):bad()
        with self.assertRaises(ViewError):self.router.run(self.task('dependency',anchor='not-existent'))
        with self.assertRaises(ViewError):self.router.run(self.task('dependency'),previous={'schema':'bad'})
    def test_review_can_switch_from_unhelpful_lens_without_evidence_change(self):
        task=self.task('association','dependency',max_views=1)
        initial=self.router.run(task)
        self.assertEqual(initial['selected_lenses'],['dependency'])
        revised=self.router.reconsider(task,initial,unhelpful_lenses=('dependency',),
                                       reason='Dependency layout did not answer operator question')
        self.assertEqual(revised['selected_lenses'],['association'])
        self.assertEqual(revised['source_only_answers'],initial['source_only_answers'])
        self.assertEqual(revised['questions'],initial['questions'])
        self.assertEqual(revised['decisions'][1]['decision'],'REVIEW_DECLARED_UNHELPFUL')
        self.assertEqual(revised['effective_external_authority'],'NONE')
        with self.assertRaises(ViewError):
            self.router.reconsider(task,initial,unhelpful_lenses=('tension',),reason='not selected')
        with self.assertRaises(ViewError):
            self.router.reconsider(task,initial,unhelpful_lenses=('dependency',),reason='')

    def test_source_never_modified(self):
        before=copy.deepcopy(self.engine._original)
        links=copy.deepcopy(self.engine.relations)
        self.router.run(self.task('association','dependency','tension','affordance',
                                  anchor='m:volunteers',max_views=4))
        self.assertEqual(before,self.engine._original)
        self.assertEqual(links,self.engine.relations)
    def test_benchmark(self):self.assertEqual(benchmark()['status'],'PASS')
    def test_demo(self):self.assertTrue(demo()['all_answers_equal'])

if __name__=='__main__':unittest.main()
