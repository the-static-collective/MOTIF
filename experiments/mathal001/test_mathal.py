"""Executable, hostile controls for the MATHAL-001 / NUNUMATHAL-001 pair."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fir001'))
from fir import Claim, FIRRefusal, FIRWorld, Relation, Warrant
from mathal import Step, Program, execute, compose_runs, mark, receipt_projection, nominate_motif003
from nunumathal import Graph, GraphRefusal, perform, statistics, compare


class MathalTests(unittest.TestCase):
    def test_propose_without_admission(self):
        world = FIRWorld('finite graph')
        claim = Claim('graph connected')
        run = execute(world, Program('hypothesis', (Step('propose',claim),), 'finite graph'))
        self.assertTrue(run.applied)
        self.assertIn(claim, run.world.ideas)
        self.assertNotIn(claim, run.world.facts)
        self.assertEqual(len(world.ideas), 0)

    def test_warranted_local_admission_receipted(self):
        w = FIRWorld('integers 1..20')
        c = Claim('n(n+1) even','n=1..20')
        run = execute(w, Program('finite claim', (
            Step('propose',c), Step('admit',c,Warrant('finite_computation','enumerate exact','n=1..20'))
        ),'integers 1..20'))
        self.assertIn(c,run.world.facts)
        self.assertEqual(receipt_projection(run, {'warrants'})['warrants'][0][1], 'finite_computation')

    def test_refusal_is_atomic_and_keeps_receipt(self):
        w = FIRWorld('N')
        candidate = Claim('Goldbach all', 'unbounded')
        p = Program('failed proof', (Step('propose',candidate),
            Step('admit',candidate,Warrant('finite_computation','check 4..100','4..100'))), 'N')
        run = execute(w,p)
        self.assertFalse(run.applied)
        self.assertIsNone(run.world)
        self.assertEqual(run.source,run.target)
        self.assertEqual(mark(w),run.source)
        self.assertIn('refused_admission', [r['operation'] for r in run.receipts])
        self.assertIn('aborted', [r['operation'] for r in run.receipts])

    def test_source_interface_rejected(self):
        run = execute(FIRWorld('real'), Program('wrong', (Step('propose',Claim('x')),), 'complex'))
        self.assertFalse(run.applied)
        self.assertEqual(run.receipts[0]['operation'],'refused_interface')

    def test_full_mark_differs_when_counts_agree(self):
        w1,w2=FIRWorld('graph'),FIRWorld('graph')
        w1.propose(Claim('a'))
        w2.propose(Claim('b'))
        self.assertEqual(w1.snapshot()['ideas'],w2.snapshot()['ideas'])
        self.assertNotEqual(mark(w1),mark(w2))

    def test_admission_warrants_do_not_collapse(self):
        x=Claim('p')
        w1,w2=FIRWorld('U'),FIRWorld('U')
        for w,e in ((w1,'source1'),(w2,'source2')):
            w.propose(x)
            w.admit(x,Warrant('external',e))
        self.assertNotEqual(mark(w1),mark(w2))

    def test_relation_not_inherited(self):
        w=FIRWorld('graph')
        relation=Relation('supports',('a','b'))
        run=execute(w,Program('relate',(Step('propose',relation),),'graph'))
        self.assertIn(relation,run.world.ideas)
        self.assertNotIn(relation,run.world.relations)

    def test_reify_no_inherited_higher_relation(self):
        e=Relation('edge',('a','b'))
        w=FIRWorld('graph')
        w.propose(e)
        w.admit(e,Warrant('assumption','fixture edge'))
        run=execute(w,Program('reify',(Step('reify',e,address='e_ab'),),'graph'))
        self.assertIn('e_ab',run.world.addressable)
        self.assertNotIn('e_ab',run.world.facts)

    def test_compose_requires_complete_mark(self):
        w=FIRWorld('N')
        a=execute(w,Program('A',(Step('propose',Claim('x')),),'N'))
        b=execute(a.world,Program('B',(Step('propose',Claim('y')),),'N'))
        both=compose_runs(a,b)
        self.assertTrue(both.applied)
        self.assertEqual(both.target,b.target)
        unrelated=execute(w,Program('other',(Step('propose',Claim('z')),),'N'))
        with self.assertRaises(FIRRefusal):
            compose_runs(a,unrelated)

    def test_same_endpoints_different_receipts(self):
        w=FIRWorld('U')
        r1=execute(w,Program('path',(Step('propose',Claim('x')),Step('refuse',Claim('x'),reason='no warrant')),'U'))
        r2=execute(w,Program('short',(Step('propose',Claim('x')),),'U'))
        self.assertEqual(r1.target,r2.target)
        self.assertNotEqual(r1.receipts,r2.receipts)

    def test_reopen_return_endpoint_but_trace_not_empty(self):
        w=FIRWorld('U')
        x=Claim('p')
        w.propose(x)
        r=execute(w,Program('round trip',(Step('admit',x,Warrant('assumption','local axiom')),
                                      Step('reopen',x,reason='assumption discharged')),'U'))
        self.assertEqual(r.source,r.target)
        self.assertEqual([x['operation'] for x in r.receipts],['admit','reopen'])

    def test_carrier_switch_reopens_admissions(self):
        w=FIRWorld('Q^2')
        x=Claim('diag(2,2) invertible')
        w.propose(x);w.admit(x,Warrant('proof','rational inverse'))
        r=execute(w,Program('switch',(Step('change_carrier','Z^2'),),'Q^2'))
        self.assertIn(x,r.world.ideas)
        self.assertNotIn(x,r.world.facts)
        self.assertNotEqual(r.source.carrier,r.target.carrier)

    def test_step_must_be_typed_and_admission_warrant_required(self):
        for invalid in [lambda:Step('admit',Claim('p')),
                        lambda:Step('reopen',Claim('p')),
                        lambda:Step('change_carrier',Claim('p')),
                        lambda:Step('unsupported',Claim('p'))]:
            with self.assertRaises(FIRRefusal): invalid()

    def test_projection_rejects_unknown_question(self):
        run=execute(FIRWorld('U'), Program('one',(Step('propose',Claim('x')),),'U'))
        with self.assertRaises(FIRRefusal):
            receipt_projection(run, {'all_future_questions'})
        self.assertIn('path',receipt_projection(run, {'path'}))
        self.assertNotIn('path',receipt_projection(run, {'endpoints'}))

    def test_nomination_from_motif003_is_idea_only(self):
        rows=[{'operator':'operator-A','roles':('bike','student')}]
        suggestions=nominate_motif003(rows)
        self.assertEqual(len(suggestions),1)
        self.assertTrue(suggestions[0].applied)
        self.assertEqual(len(suggestions[0].world.facts),0)
        self.assertEqual(len(suggestions[0].world.ideas),1)

    def test_actual_motif003_preview_adapter(self):
        if not (Path(__file__).resolve().parents[1]/'003'/'affordance.py').exists():
            self.skipTest('MOTIF-003 is present in the GitHub repository, not this local fixture')
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'003'))
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'002'))
        from affordance import analyze_first_moves
        from motif002 import induce,lessons,scene,possibilities,utility
        initial=scene()
        rows=analyze_first_moves(initial,induce(lessons()),possibilities,utility)
        candidates=nominate_motif003(rows)
        self.assertEqual(len(candidates),len(rows))
        self.assertTrue(all(r.applied and not r.world.facts for r in candidates))
        self.assertEqual(initial,scene())


class NunumathalTests(unittest.TestCase):
    def setUp(self):
        self.g=Graph.build({'a','b','c'},[('a','b'),('b','c')])

    def test_isolated_and_subdivision_are_not_same_mechanism(self):
        iso=perform(self.g,'isolated','d')
        sub=perform(self.g,'subdivide','d',edge=('b','c'))
        self.assertEqual(iso.numerical_index,sub.numerical_index)
        self.assertNotEqual(iso.delta,sub.delta)
        cmp=compare(iso,sub)
        self.assertTrue(cmp['same_index'])
        self.assertFalse(cmp['numeral_removed_signature_match'])
        self.assertEqual(cmp['second_order_status'],'I')

    def test_same_rule_different_index_survives_numeral_removal(self):
        iso1=perform(self.g,'isolated','d')
        g2=Graph.build({'a','b','c','d','e'},[('a','b'),('b','c')])
        iso2=perform(g2,'isolated','f')
        cmp=compare(iso1,iso2)
        self.assertFalse(cmp['same_index'])
        self.assertTrue(cmp['numeral_removed_signature_match'])
        self.assertTrue(cmp['equal_rule_label'])
        self.assertEqual(cmp['second_order_status'],'I')

    def test_matching_signature_cannot_prove_matching_cause(self):
        iso=perform(self.g,'isolated','d')
        another=perform(self.g,'isolated','e')
        cmp=compare(iso,another)
        self.assertTrue(cmp['numeral_removed_signature_match'])
        self.assertTrue(cmp['needs_independent_warrant'])
        self.assertNotEqual(cmp['second_order_status'],'F')

    def test_leaf_and_subdivide_collide_under_coarse_invariants(self):
        leaf=perform(self.g,'leaf','d',anchor='a')
        sub=perform(self.g,'subdivide','d',edge=('a','b'))
        # HOSTILE CONTROL: different mechanisms can have an identical 5-vector.
        self.assertEqual(leaf.delta,sub.delta)
        self.assertNotEqual(leaf.target.edges,sub.target.edges)
        self.assertFalse(compare(leaf,sub)['equal_rule_label'])
        self.assertEqual(compare(leaf,sub)['second_order_status'],'I')

    def test_graph_components_cycle_rank(self):
        triangle=Graph.build({'a','b','c'},[('a','b'),('a','c'),('b','c')])
        self.assertEqual(statistics(triangle),(3,3,1,0,1))
        self.assertEqual(statistics(self.g),(3,2,1,0,0))

    def test_precondition_refusals(self):
        with self.assertRaises(GraphRefusal):perform(self.g,'isolated','a')
        with self.assertRaises(GraphRefusal):perform(self.g,'subdivide','d',edge=('a','c'))
        with self.assertRaises(GraphRefusal):perform(self.g,'leaf','d',anchor='z')
        with self.assertRaises(GraphRefusal):Graph.build({'a'},[('a','a')])

    def test_graphs_and_receipts_remain_immutable(self):
        before=self.g
        r=perform(self.g,'subdivide','d',edge=('a','b'))
        self.assertEqual(before,self.g)
        self.assertNotEqual(r.target,before)
        self.assertEqual(r.delta,(1,1,0,0,0))
        self.assertTrue(any(x.startswith('simulation:') for x in r.receipt))


if __name__=='__main__': unittest.main()
