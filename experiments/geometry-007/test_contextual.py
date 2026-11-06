"""Adversarial synthetic controls for GEOM-007, no external service required."""
from __future__ import annotations
import json
import random
import unittest
from itertools import product, combinations
from pathlib import Path
from math import log2
from contextual import (Context, ContextualAtlas, Lens, Question, from_geom006_models,
                        run_document)

HERE = Path(__file__).parent


def two_world_atlas():
    scope='observer:alice/world:9/knowledge:9/decoder:v1'
    contexts=[
        Context('temporal',scope,('route', 'known'),({'route':'OPEN','known':'YES'},),'doc:temporal'),
        Context('provenance',scope,('known','origin'),({'known':'YES','origin':'PRIMARY'},
                                                      {'known':'YES','origin':'ECHO'}),'doc:provenance'),
        Context('affordance',scope,('origin','reachable'),({'origin':'PRIMARY','reachable':'YES'},
                                                          {'origin':'ECHO','reachable':'NO'}),'doc:affordance')]
    lenses=[Lens('appearance',('route','known'),'HEX'), Lens('causal',('origin','reachable'),'RADIAL'),
            Lens('none',(),'NONE')]
    probes=[Question('test-origin','origin',1.0,True),
            Question('test-reach','reachable',3.0,True),
            Question('forbidden-cheap','reachable',0.01,False),
            Question('uninformative','route',0.1,True)]
    return ContextualAtlas(contexts,lenses,probes)


class ContextualTests(unittest.TestCase):
    def test_observer_blind_to_second_world(self):
        a=two_world_atlas()
        v=a.inspect(('appearance',))
        self.assertEqual(v['global_sections'],2)
        self.assertTrue(v['representation_blind'])
        self.assertEqual(v['view_signatures'],1)
        self.assertEqual(v['hidden_discriminators'],['origin','reachable'])

    def test_second_lens_distinguishes_without_new_truth(self):
        a=two_world_atlas()
        v=a.inspect(('appearance','causal'))
        self.assertEqual(v['global_sections'],2)
        self.assertEqual(v['view_signatures'],2)
        self.assertFalse(v['representation_blind'])
        self.assertEqual(v['instrument'],'PENCIL')

    def test_reframe_recommendation_is_question_not_evidence(self):
        a=two_world_atlas()
        proposal=a.next_question(('appearance',))
        self.assertEqual(proposal['status'],'QUESTION_PROPOSED')
        self.assertEqual(proposal['best']['question'],'test-origin')
        self.assertTrue(proposal['best']['requires_reframing'])
        self.assertEqual(a.inspect(('appearance',))['global_sections'],2)

    def test_cost_budget_permission(self):
        a=two_world_atlas()
        self.assertEqual(a.next_question(('appearance',),budget=.5)['status'],'HOLD')
        self.assertNotEqual(a.next_question(('appearance',))['best']['question'],'forbidden-cheap')

    def test_counterfactual_does_not_mutate(self):
        a=two_world_atlas()
        out=a.filter_on_observation('origin','PRIMARY','claimed:not-verified')
        self.assertEqual(out['matching_sections'],1)
        self.assertEqual(out['status'],'PENCIL_COUNTERFACTUAL')
        self.assertEqual(len(a.sections),2)

    def test_display_ablation_exactly_invariant(self):
        a=two_world_atlas()
        x=a.inspect(('appearance',),display=False)
        y=a.inspect(('appearance',),display=True)
        y['coordinates']={}
        self.assertEqual(x,y)

    def test_no_geometry_lens_same_semantic_conclusion(self):
        a=two_world_atlas()
        no=a.inspect(('none',))
        self.assertEqual(no['global_sections'],2)
        self.assertTrue(no['representation_blind'])
        self.assertEqual(a.next_question(('none',))['best']['question'],'test-origin')

    def test_unique_within_grammar_not_verified_reality(self):
        s='single-observer/cut'
        a=ContextualAtlas([Context('x',s,('a',),({'a':'1'},),'src')],[Lens('v',('a',))],[])
        out=a.inspect(('v',))
        self.assertEqual(out['status'],'UNIQUE_WITHIN_GRAMMAR')
        self.assertEqual(out['authority'],'NONE')
        self.assertEqual(a.next_question(('v',))['status'],'HOLD')

    def test_conflict_core_preserves_provenance(self):
        s='single-observer/cut'
        a=ContextualAtlas([Context('a',s,('x',),({'x':'1'},),'source-a'),
                           Context('b',s,('x',),({'x':'2'},),'source-b'),
                           Context('c',s,('y',),({'y':'Q'},),'source-c')],
                          [Lens('v',('x','y'))],[Question('ask','x',1,True)])
        out=a.inspect(('v',))
        self.assertEqual(out['status'],'INCOMPATIBLE_LOCAL_CONTEXTS')
        self.assertEqual([v['context'] for v in out['minimal_conflict']],['a','b'])
        self.assertEqual(a.next_question(('v',))['status'],'HOLD')

    def test_pairwise_compatible_but_globally_incompatible(self):
        # Each two-constraint subproblem is satisfiable. Together they are not.
        # a == b, b == c, a != c: classical contextual constraint obstruction.
        scope='same-observer/same-cut'
        cs=[
            Context('eq-ab',scope,('a','b'),({'a':'0','b':'0'},{'a':'1','b':'1'}),'claimed:r1'),
            Context('eq-bc',scope,('b','c'),({'b':'0','c':'0'},{'b':'1','c':'1'}),'claimed:r2'),
            Context('neq-ac',scope,('a','c'),({'a':'0','c':'1'},{'a':'1','c':'0'}),'claimed:r3'),
        ]
        for pair in combinations(cs,2):
            self.assertGreater(len(ContextualAtlas(list(pair),[Lens('v',('a','b','c'))],[]).sections),0)
        atlas=ContextualAtlas(cs,[Lens('v',('a','b','c'))],[])
        self.assertEqual(atlas.inspect(('v',))['status'],'INCOMPATIBLE_LOCAL_CONTEXTS')
        self.assertEqual(len(atlas.inspect(('v',))['minimal_conflict']),3)

    def test_repetition_cannot_mint_independent_truth(self):
        s='scope'
        a=ContextualAtlas([Context('a',s,('x',),({'x':'YES'},),'same-root'),
                           Context('b',s,('x',),({'x':'YES'},),'same-root')],
                          [Lens('v',('x',))],[])
        self.assertEqual(a.inspect(('v',))['authority'],'NONE')

    def test_scope_separation_refuses_overreach(self):
        with self.assertRaisesRegex(ValueError,'cross-observer'):
            ContextualAtlas([Context('a','alice/t1',('x',),({'x':'YES'},),'src1'),
                             Context('b','bob/t2',('x',),({'x':'NO'},),'src2')],
                            [Lens('v',('x',))],[])

    def test_bad_local_assignments_refuse(self):
        for broken in ({'x':'YES'}, {'x':'YES','y':'NO','z':'YES'}):
            with self.assertRaises(ValueError):
                Context('x','scope',('x','y'),(broken,),'root')
        with self.assertRaises(ValueError):
            Context('x','scope',('x',),({'x':'Y'},{'x':'Y'}),'root')

    def test_lens_does_not_invent_variables(self):
        with self.assertRaises(ValueError):
            ContextualAtlas([Context('a','scope',('x',),({'x':'Y'},),'r')],
                            [Lens('v',('z',))],[])

    def test_question_does_not_invent_variable(self):
        with self.assertRaises(ValueError):
            ContextualAtlas([Context('a','scope',('x',),({'x':'Y'},),'r')],
                            [Lens('v',('x',))],[Question('foo','z',1,True)])

    def test_invalid_permitted_value_fails_closed(self):
        with self.assertRaises(ValueError):Question('q','x',1,'yes')
        with self.assertRaises(ValueError):Question('q','x',float('inf'),True)
        with self.assertRaises(ValueError):Question('q','x',0,True)

    def test_combinatorial_explosion_fails_closed(self):
        s='s'
        contexts=[]
        for i in range(5):
            var=f'x{i}'
            contexts.append(Context(f'c{i}',s,(var,),tuple({var:str(j)} for j in range(9)),f's{i}'))
        with self.assertRaisesRegex(ValueError,'too many raw combinations'):
            ContextualAtlas(contexts,[Lens('all',tuple(f'x{i}' for i in range(5)))],[])

    def test_geometry_display_limit_and_determinism(self):
        a=two_world_atlas()
        self.assertEqual(a.inspect(('appearance',),display=True),a.inspect(('appearance',),display=True))
        self.assertEqual(len(a.inspect(('appearance',),display=True)['coordinates']['appearance']),2)

    def test_unknown_lens_rejected(self):
        with self.assertRaises(ValueError):two_world_atlas().inspect(('unavailable',))

    def test_mixed_geometric_lenses_keep_semantics(self):
        a=two_world_atlas()
        x=a.inspect(('appearance','causal'),display=False)
        y=a.inspect(('appearance','causal'),display=True)
        y['coordinates']={}
        self.assertEqual(x,y)

    def test_geom006_model_adapter_pencil_only(self):
        class Model:
            def __init__(self,id,predictions):self.id=id;self.predictions=predictions
        c=from_geom006_models([Model('a',{'a':'0','b':'Y'}),Model('b',{'a':'1','b':'Y'})],scope='alice@t1')
        a=ContextualAtlas([c],[Lens('v',('b',))],[Question('ask-a','a',1,True)])
        self.assertEqual(a.inspect(('v',))['global_sections'],2)
        self.assertEqual(a.next_question(('v',))['best']['variable'],'a')
        self.assertEqual(a.inspect(('v',))['authority'],'NONE')

    def test_geom006_model_adapter_no_implicit_missing_prediction(self):
        class Model:
            def __init__(self,predictions):self.predictions=predictions
        with self.assertRaises(ValueError):
            from_geom006_models([Model({'x':'Y'}),Model({'z':'N'})],scope='same')

    def test_json_cli_deterministic(self):
        doc=json.loads((HERE/'example-input.json').read_text())
        self.assertEqual(run_document(doc),run_document(doc))
        self.assertEqual(run_document(doc)['inspection']['global_sections'],2)

    def test_unknown_top_level_mutation_rejected(self):
        doc=json.loads((HERE/'example-input.json').read_text())
        doc['run_shell']='x'
        with self.assertRaises(ValueError):run_document(doc)

    def test_independent_cartesian_join_random_worlds(self):
        # An independently written exhaustive product oracle; no call into _sections.
        rng=random.Random(8307)
        for _ in range(60):
            var_pool=['a','b','c','d']
            contexts=[]
            for c in range(rng.randint(2,4)):
                vs=tuple(sorted(rng.sample(var_pool,rng.randint(1,3))))
                alts=[]
                for _j in range(rng.randint(1,4)):
                    item={v:str(rng.randrange(2)) for v in vs}
                    if item not in alts:alts.append(item)
                contexts.append(Context(f'c{c}','same-scope',vs,tuple(alts),f'root{c}'))
            a=ContextualAtlas(contexts,[Lens('v',tuple(var_pool))] if set(var_pool)==set().union(*(set(c.variables) for c in contexts)) else [Lens('v',tuple(sorted(set().union(*(set(c.variables) for c in contexts)))))],[])
            brute=set()
            for choice in product(*(c.alternatives for c in contexts)):
                merged={}
                okay=True
                for local in choice:
                    for k,v in local.items():
                        if k in merged and merged[k]!=v:
                            okay=False
                        merged[k]=v
                if okay:brute.add(tuple(sorted(merged.items())))
            self.assertEqual({tuple(sorted(s.items())) for s in a.sections},brute)

    def test_independent_entropy_controls(self):
        a=two_world_atlas()
        proposals=a.next_question(('appearance',))
        self.assertEqual(proposals['best']['question'],'test-origin')
        # Explicit partition entropy, independent of implementation.
        counts=[1,1];total=sum(counts)
        expected=-sum(n/total*log2(n/total) for n in counts)
        self.assertEqual(proposals['best']['information_gain_bits'],expected)
        self.assertEqual(proposals['best']['gain_per_cost'],expected)


if __name__=='__main__':unittest.main()
