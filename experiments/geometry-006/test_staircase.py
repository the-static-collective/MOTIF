import unittest
from staircase import Atlas, Place, Relation, Model, Probe, hex_projection, select_question
from demo import example, run


class StaircaseTests(unittest.TestCase):
    def setUp(self):
        self.atlas = example()

    def test_13_centers(self):
        self.assertEqual(len(self.atlas.places), 13)
        self.assertEqual(len(hex_projection(self.atlas.places)), 13)
        self.assertEqual(len(set(tuple(x) for x in hex_projection(self.atlas.places).values())), 13)

    def test_later_discovery_does_not_rewrite_old_view(self):
        self.assertNotIn('late', [e['id'] for e in self.atlas.view(4, 4, 'ada')['relations']])
        h = {e['id']: e for e in self.atlas.view(4, 10, 'ada')['relations']}
        self.assertEqual((h['late']['effective_from'],h['late']['discovered_at'],h['late']['state']), (1, 8, 'DECLARED_ADMITTED'))

    def test_observer_access_changes_view_not_world(self):
        self.assertIn('late', [e['id'] for e in self.atlas.view(4, 10, 'ada')['relations']])
        self.assertNotIn('late', [e['id'] for e in self.atlas.view(4, 10, 'bo')['relations']])
        self.assertIn('late', [e['id'] for e in self.atlas.view(4, 12, 'bo')['relations']])

    def test_pencil_never_becomes_accepted_by_appearance(self):
        h = {e['id']: e for e in self.atlas.view(4, 10, 'ada', geometry=True)['relations']}
        self.assertEqual(h['pretty']['state'], 'PENCIL')
        self.assertEqual(h['temptation']['state'], 'PENCIL')
        self.assertEqual(self.atlas.earliest_route('i3','o3',0,4,10,'ada')['status'], 'HOLD')

    def test_admission_requires_knowledge_time(self):
        h = {e['id']: e for e in self.atlas.view(4, 2, 'ada')['relations']}
        self.assertEqual(h['e2']['state'], 'PENCIL')
        self.assertEqual(self.atlas.earliest_route('c','o0',0,4,2,'ada')['status'], 'HOLD')
        self.assertEqual(self.atlas.earliest_route('c','o0',0,4,3,'ada')['status'], 'PATH')

    def test_directed_temporal_route(self):
        p = self.atlas.earliest_route('c','o0',0,4,10,'ada')
        self.assertEqual(p['arrival'], 3)
        self.assertEqual([h['edge'] for h in p['hops']], ['e1','e2'])
        self.assertEqual(self.atlas.earliest_route('o0','c',0,4,10,'ada')['status'], 'HOLD')

    def test_static_aggregation_false_positive(self):
        # c->i1 and i1->o1 exist in the aggregate, but cannot be traversed in time.
        self.assertEqual(self.atlas.earliest_route('c','o1',0,8,10,'ada')['status'], 'HOLD')

    def test_withdrawn_is_retained_but_not_traversed(self):
        before = {e['id']:e for e in self.atlas.view(4,7,'ada')['relations']}
        after = {e['id']:e for e in self.atlas.view(4,9,'ada')['relations']}
        self.assertEqual(before['withdrawn']['state'], 'DECLARED_ADMITTED')
        self.assertEqual(after['withdrawn']['state'], 'WITHDRAWN')
        self.assertEqual(self.atlas.earliest_route('i4','o4',0,4,9,'ada')['status'],'HOLD')

    def test_no_geometry_same_semantics(self):
        a = self.atlas.view(4,10,'ada',geometry=False)
        b = self.atlas.view(4,10,'ada',geometry=True)
        for key in ('world_cut','knowledge_cut','observer','nodes','relations','authority'):
            self.assertEqual(a[key],b[key])
        self.assertEqual(a['coordinates'],{})
        self.assertTrue(b['coordinates'])

    def test_unknown_observer_not_implicitly_visible(self):
        self.assertEqual(self.atlas.view(4,10,'stranger')['nodes'],[])
        self.assertEqual(self.atlas.earliest_route('c','o0',0,4,10,'stranger')['status'],'HOLD')

    def test_outside_action_never_authorized(self):
        self.assertEqual(run()['authority'],'NONE')
        self.assertEqual(self.atlas.earliest_route('c','o0',0,4,10,'ada')['authority'],'NONE')

    def test_invalid_edge_grammar_refuses(self):
        with self.assertRaises(ValueError):
            Relation('x','c','i0','route',1,2,3,1,None,{'ada':1},'root')
        with self.assertRaises(ValueError):
            Relation('x','c','i0','route',1,2,1,1,None,{'ada':1},'root',0)
        with self.assertRaises(ValueError):
            Atlas([Place('a',5,{'ada':0}),Place('b',5,{'ada':0})],
                  [Relation('early','a','b','route',1,None,1,2,None,{'ada':1},'root')])

    def test_question_selection_respects_cost(self):
        ms=[Model('A',.5,{'same':'x','small':'a','huge':'a'}),
            Model('B',.5,{'same':'x','small':'b','huge':'b'})]
        q=select_question(ms,[Probe('same',1,True),Probe('huge',100,True),Probe('small',2,True)])
        self.assertEqual(q['selected']['probe'],'small')
        self.assertEqual(q['selected']['information_gain_bits'],1.0)
        self.assertIsNone(q['identified_world'])

    def test_protected_probe_cannot_win(self):
        ms=[Model('A',.5,{'private':'x','public':'x'}),Model('B',.5,{'private':'y','public':'y'})]
        q=select_question(ms,[Probe('private',.01,False),Probe('public',2,True)])
        self.assertEqual(q['selected']['probe'],'public')

    def test_same_observations_cannot_identify_world(self):
        ms=[Model('A',.5,{'same':'x'}),Model('B',.5,{'same':'x'})]
        self.assertEqual(select_question(ms,[Probe('same',1,True)])['status'],'HOLD')

    def test_missing_prediction_does_not_guess(self):
        ms=[Model('A',.5,{'test':'x'}),Model('B',.5,{})]
        self.assertEqual(select_question(ms,[Probe('test',1,True)])['status'],'HOLD')

    def test_unequal_priors_entropy_exact(self):
        ms=[Model('A',.25,{'test':'x'}),Model('B',.75,{'test':'y'})]
        self.assertAlmostEqual(select_question(ms,[Probe('test',1,True)])['selected']['information_gain_bits'],.811278124, places=7)


    def test_time_expanded_classical_control_50_seeded_graphs(self):
        # Independent exhaustive state expansion over (node, tick), no Dijkstra.
        import random
        rng = random.Random(6006)
        for _ in range(50):
            nodes = [Place(x, 0, {'ada': 0}) for x in 'abcd']
            edges = []
            for a in 'abcd':
                for b in 'abcd':
                    if a == b or rng.randrange(3) == 0:
                        continue
                    opened = rng.randrange(0, 7)
                    end = rng.choice([None, opened + rng.randint(1, 3)])
                    admitted = rng.choice([True, True, False])
                    edges.append(Relation('e'+a+b,a,b,'route',opened,end,opened,
                                          opened if admitted else None,None,
                                          {'ada': opened},'synthetic:'+a+b))
            atlas = Atlas(nodes, edges)
            frontier = {'a'}
            expected = 0 if 'a' == 'd' else None
            for tick in range(0, 9):
                next_nodes = set(frontier)  # waiting one tick is allowed
                for r in edges:
                    if r.admitted_at is None or r.source not in frontier:
                        continue
                    if tick >= r.effective_from and (r.effective_until is None or tick + 1 < r.effective_until):
                        next_nodes.add(r.target)
                frontier = next_nodes
                if 'd' in frontier:
                    expected = tick + 1
                    break
            actual = atlas.earliest_route('a','d',0,9,10,'ada')
            self.assertEqual(actual.get('arrival'), expected)

    def test_entropy_matches_direct_outcome_partition_control(self):
        from math import log2
        ms=[Model('a',.1,{'p':'red'}), Model('b',.2,{'p':'red'}),
            Model('c',.3,{'p':'blue'}), Model('d',.4,{'p':'green'})]
        response=select_question(ms,[Probe('p',1,True)])['selected']
        masses=[.1+.2,.3,.4]
        expected=-sum(x*log2(x) for x in masses)
        self.assertAlmostEqual(response['information_gain_bits'],expected,places=8)

    def test_demo_reproducible(self):
        self.assertEqual(run(),run())
        self.assertTrue(run()['no_geometry_invariant'])


if __name__=='__main__':
    unittest.main()
