"""Local controls, resource cutoffs, resumption, and independent oracles."""
import itertools
import random
import tempfile
import unittest
from pathlib import Path

from living_graph import LivingGraph, RewriteGrammar, RewriteRule, grammar_from_document, run_document
from display import render_dot
from repair import Atom, World, discover_composition, inspect_composition_on_graph, reaches, preserve_as_pencil


def binary_grammar(scope='lab'):
    return RewriteGrammar(scope, (
        RewriteRule('append-zero', ('#',), ('0', '#')),
        RewriteRule('append-one', ('#',), ('1', '#')),
    ))


def training_worlds(tag='training', scope='lab'):
    worlds = []
    for i in range(4):
        x, p, q = f'{tag}-x{i}', f'{tag}-p{i}', f'{tag}-q{i}'
        pos = (('start', 'carry', x), (x, 'serve', 'goal'),
               ('start', 'serve', p), (p, 'carry', q))
        neg = (('start', 'serve', x), (x, 'carry', 'goal'),
               ('start', 'carry', p), (p, 'serve', q))
        worlds.append(World(f'{tag}-yes{i}', scope, pos, True, 'fixture:root-one'))
        worlds.append(World(f'{tag}-no{i}', scope, neg, False, 'fixture:root-two'))
    return tuple(worlds)


class GrowingHypergraph(unittest.TestCase):
    def test_graph_free_of_legacy_thirteen_or_4096_global_ceiling(self):
        with LivingGraph(scope='lab') as graph:
            graph.seed(['#'])
            a = graph.grow(binary_grammar(), work_budget=2200)
            self.assertEqual(a['totals']['nodes'], 4401)
            self.assertEqual(a['totals']['relations'], 6600)
            self.assertEqual(a['totals']['unexpanded'], 2201)
            self.assertEqual(a['status'], 'WORK_SLICE_COMPLETE')
            self.assertEqual(graph.verify(), {'foreign_key_errors': 0, 'integrity': 'ok'})

    def test_append_only_resume_on_disk_keeps_exact_frontier(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'graph.db'
            with LivingGraph(db, scope='lab') as graph:
                seed = graph.seed(['#'])
                result = graph.grow(binary_grammar(), work_budget=2)
                self.assertEqual(result['totals']['nodes'], 5)
            with LivingGraph(db, scope='lab') as graph:
                self.assertEqual(graph.seed(['#']), seed)
                later = graph.grow(binary_grammar(), work_budget=3)
                self.assertEqual(later['totals']['nodes'], 11)
                self.assertEqual(later['totals']['expanded'], 5)
                self.assertEqual(later['totals']['unexpanded'], 6)
                self.assertEqual(graph.verify()['integrity'], 'ok')

    def test_saturated_finite_grammar_and_cycle_are_safe(self):
        gram = RewriteGrammar('lab', (RewriteRule('a-to-b', ('a',), ('b',)),
                                      RewriteRule('b-to-a', ('b',), ('a',))))
        with LivingGraph(scope='lab') as graph:
            graph.seed(['a'])
            outcome = graph.grow(gram, work_budget=100)
            self.assertEqual(outcome['status'], 'SATURATED_FOR_CURRENT_GRAMMAR')
            self.assertEqual(outcome['totals']['nodes'], 2)
            self.assertEqual(outcome['totals']['relations'], 2)
            self.assertEqual(outcome['totals']['unexpanded'], 0)

    def test_n_ary_hyperrelation_more_than_thirteen_endpoints(self):
        with LivingGraph(scope='lab') as graph:
            endpoints = []
            for i in range(31):
                n = f'n-{i}'
                graph.add_node(n, kind='idea', label=f'Node {i}',
                               payload={'i': i}, source_root='fixture')
                endpoints.append(('participant', n))
            self.assertTrue(graph.add_relation('debate-hyperedge', endpoints,
                         source_root='declared-person', note={'proposed': True}))
            self.assertFalse(graph.add_relation('debate-hyperedge', endpoints,
                          source_root='declared-person', note={'proposed': True}))
            self.assertEqual(graph.counts()['relations'], 1)
            view = graph.neighborhood('n-0', node_budget=40, relation_budget=10)
            self.assertEqual(len(view['nodes']), 31)
            self.assertEqual(len(view['relations'][0]['participants']), 31)
            self.assertTrue(all(n['status'] == 'PENCIL' for n in view['nodes']))

    def test_outside_scope_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'graph.db'
            with LivingGraph(db, scope='observer-1') as graph:
                graph.seed(['#'])
            with self.assertRaisesRegex(ValueError, 'scope mismatch'):
                LivingGraph(db, scope='observer-2')

    def test_grammar_change_cannot_silently_reinterpret_existing_frontier(self):
        with LivingGraph(scope='lab') as graph:
            graph.seed(['#'])
            graph.grow(binary_grammar(), work_budget=1)
            with self.assertRaisesRegex(ValueError, 'cannot silently replace'):
                graph.grow(RewriteGrammar('lab', (RewriteRule('new', ('#',), ('9', '#')),)),
                           work_budget=1)

    def test_variable_arity_rewrite_and_empty_expression(self):
        with LivingGraph(scope='lab') as graph:
            graph.seed(['red', 'blue', 'red'])
            grammar = RewriteGrammar('lab', (RewriteRule('delete-red', ('red',), ()),
                                             RewriteRule('pair-red', ('red',), ('red', 'red'))))
            outcome = graph.grow(grammar, work_budget=1)
            self.assertEqual(outcome['totals']['nodes'], 5)
            self.assertEqual(outcome['totals']['relations'], 5)
            self.assertEqual(graph.verify()['integrity'], 'ok')

    def test_zero_length_pattern_insertions_are_finite_per_node(self):
        with LivingGraph(scope='lab') as graph:
            graph.seed([])
            g = RewriteGrammar('lab', (RewriteRule('invent-A', (), ('A',)),
                                       RewriteRule('invent-B', (), ('B',))))
            outcome = graph.grow(g, work_budget=3)
            self.assertGreaterEqual(outcome['totals']['nodes'], 5)
            self.assertEqual(graph.verify()['integrity'], 'ok')

    def test_paging_no_full_graph_materialization(self):
        with LivingGraph(scope='lab') as graph:
            graph.seed(['#'])
            graph.grow(binary_grammar(), work_budget=50)
            found = []
            cursor = ''
            while True:
                page = graph.node_page(after=cursor, page_size=7)
                found += [n['id'] for n in page['nodes']]
                if page['next_cursor'] is None:
                    break
                cursor = page['next_cursor']
            self.assertEqual(len(found), 101)
            self.assertEqual(len(set(found)), 101)

    def test_local_view_marks_truncation_no_fabricated_distance(self):
        with LivingGraph(scope='lab') as graph:
            seed = graph.seed(['#'])
            graph.grow(binary_grammar(), work_budget=50)
            view = graph.neighborhood(seed, hops=2, node_budget=2, relation_budget=2)
            self.assertTrue(view['partial_view'])
            self.assertLessEqual(len(view['nodes']), 2)
            self.assertEqual(view['authority'], 'NONE')

    def test_read_only_query_reports_incomplete_instead_of_false_negative(self):
        with LivingGraph(scope='lab') as graph:
            root = graph.seed(['#'])
            graph.grow(binary_grammar(), work_budget=5)
            partial = inspect_composition_on_graph(graph, root, (Atom('rewrite'),),
                                                   transition_budget=1)
            self.assertEqual(partial['status'], 'INCOMPLETE_RESOURCE_SLICE')
            complete = inspect_composition_on_graph(graph, root, (Atom('rewrite'),),
                                                    transition_budget=10)
            self.assertEqual(complete['status'], 'COMPLETE_WITHIN_OPERATOR_AND_GRAPH')
            self.assertEqual(len(complete['endpoints']), 2)
            self.assertTrue(all(x['relation_witnesses'] for x in complete['endpoints']))

    def test_dot_is_optional_partial_and_escapes_arbitrary_labels(self):
        with LivingGraph(scope='lab') as graph:
            graph.add_node('one', kind='wild', label='</script>"\\evil',
                           payload={'hi': 1}, source_root='declared')
            graph.add_node('two', kind='wild', label='destination',
                           payload={'hi': 2}, source_root='declared')
            graph.add_relation('invented\nrelationship', [('from', 'one'), ('to', 'two')],
                               source_root='declared')
            dot = render_dot(graph.neighborhood('one', hops=1))
            self.assertIn('digraph LivingAtlas', dot)
            self.assertIn('shape=diamond', dot)
            self.assertIn('PENCIL-only', dot)
            self.assertIn('invented\\nrelationship', dot)
            self.assertNotIn('[label="</script>"', dot)

    def test_hostile_payloads_cannot_add_actions(self):
        doc = {'grammar': {'scope': 'lab', 'rules': [
                   {'name': 'right', 'find': ['#'], 'replace': ['X', '#']}]},
               'seed': ['#'], 'work_budget': 3, 'run_shell': 'rm -rf /'}
        with self.assertRaisesRegex(ValueError, 'unknown graph request field'):
            run_document(doc)
        with self.assertRaises(ValueError):
            grammar_from_document({'scope': 'lab', 'rules': [{'name': 'a', 'find': ['x'],
                                  'replace': ['y'], 'exec': 'sh'}]})

    def test_requires_explicit_work_budget(self):
        with LivingGraph(scope='lab') as graph:
            graph.seed(['#'])
            with self.assertRaises(ValueError):
                graph.grow(binary_grammar(), work_budget=0)
            with self.assertRaises(ValueError):
                graph.grow(binary_grammar(), work_budget=True)


class CompositionRepair(unittest.TestCase):
    def test_no_atomic_edge_rule_but_two_step_composition_succeeds(self):
        data = discover_composition(training_worlds(), training_worlds('heldout'),
                                    start='start', goal='goal', work_budget=30)
        self.assertEqual(data['status'], 'COMPOSITION_PROPOSED')
        self.assertTrue(data['representation_gap'])
        self.assertEqual(data['length'], 2)
        self.assertEqual([d['relation'] for d in data['program']], ['carry', 'serve'])
        self.assertEqual(data['train']['accuracy'], 1.0)
        self.assertEqual(data['heldout']['accuracy'], 1.0)
        self.assertLess(data['baseline_single_relation']['train']['accuracy'], 1.0)
        self.assertEqual(data['status_of_assertion'], 'PENCIL')

    def test_search_resumes_across_work_slices_without_replaying_offset(self):
        cursor = None
        for _ in range(30):
            data = discover_composition(training_worlds(), training_worlds('heldout'),
                                        start='start', goal='goal', work_budget=1, cursor=cursor)
            if data['status'] != 'CONTINUE_SEARCH':
                self.assertEqual(data['status'], 'COMPOSITION_PROPOSED')
                break
            cursor = data['next_cursor']
        else:
            self.fail('composition not discovered under 30 discrete work slices')

    def test_cursor_rejects_changed_worlds(self):
        data = discover_composition(training_worlds(), training_worlds('heldout'),
                                    start='start', goal='goal', work_budget=1)
        bad = training_worlds('alternate')
        with self.assertRaisesRegex(ValueError, 'cursor'):
            discover_composition(bad, training_worlds('heldout'),
                                 start='start', goal='goal', work_budget=1,
                                 cursor=data['next_cursor'])

    def test_heldout_failure_is_reported_without_retraining(self):
        heldout = list(training_worlds('heldout'))
        first = heldout[0]
        heldout[0] = World(first.identity, first.scope, first.edges, False, first.source_root)
        data = discover_composition(training_worlds(), heldout,
                                    start='start', goal='goal', work_budget=30)
        self.assertEqual(data['train']['accuracy'], 1.0)
        self.assertLess(data['heldout']['accuracy'], 1.0)
        self.assertEqual(data['program'][0]['relation'], 'carry')

    def test_requires_identical_scope(self):
        heldout = list(training_worlds('test'))
        first = heldout[0]
        heldout[0] = World(first.identity, 'different', first.edges, first.expected)
        with self.assertRaisesRegex(ValueError, 'scope'):
            discover_composition(training_worlds(), heldout, start='start', goal='goal',
                                 work_budget=20)

    def test_composition_only_claims_grammar_synthesis(self):
        data = discover_composition(training_worlds(), training_worlds('heldout'),
                                    start='start', goal='goal', work_budget=30)
        self.assertIn('existing relation atoms', data['limitations'])
        self.assertEqual(data['authority'], 'NONE')

    def test_requested_length_limit_refuses_without_false_conclusion(self):
        data = discover_composition(training_worlds(), training_worlds('heldout'),
                                    start='start', goal='goal', work_budget=100, max_length=1)
        self.assertEqual(data['status'], 'NO_OPERATOR_WITHIN_REQUESTED_GRAMMAR')

    def test_reverse_operator_can_be_composed(self):
        a = (World('yes', 'lab', (('x', 'hop', 's'), ('x', 'walk', 'g')), True),
             World('no', 'lab', (('x', 'hop', 's'), ('y', 'walk', 'g')), False))
        b = (World('holdout-yes', 'lab', a[0].edges, True),
             World('holdout-no', 'lab', a[1].edges, False))
        data = discover_composition(a, b, start='s', goal='g',
                                    work_budget=50, allow_reverse=True)
        self.assertEqual(data['status'], 'COMPOSITION_PROPOSED')
        self.assertEqual(data['heldout']['accuracy'], 1.0)
        self.assertTrue(data['program'][0]['direction'] == 'reverse')

    def test_proposed_macro_is_preserved_as_n_ary_pencil_hyperedge(self):
        train, hold = training_worlds(), training_worlds('hold')
        result = discover_composition(train, hold, start='start', goal='goal', work_budget=20)
        with LivingGraph(scope='lab') as graph:
            saved = preserve_as_pencil(graph, result, train, hold, start='start', goal='goal')
            self.assertEqual(saved['status'], 'PENCIL_CARTRIDGE_STORED')
            self.assertEqual(saved['witness_count'], 16)
            view = graph.neighborhood(saved['candidate_node'], node_budget=25, relation_budget=5)
            self.assertEqual(len(view['relations'][0]['participants']), 17)
            self.assertEqual(graph.counts()['nodes'], 17)
            self.assertEqual(graph.verify()['integrity'], 'ok')
            forged = dict(result)
            forged['heldout'] = dict(result['heldout'], accuracy=0.0)
            with self.assertRaisesRegex(ValueError, 'reported scores'):
                preserve_as_pencil(graph, forged, train, hold, start='start', goal='goal')

    def test_no_hidden_total_size_threshold_even_after_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'g.db'
            gram = binary_grammar()
            with LivingGraph(path, scope='lab') as graph:
                graph.seed(['#'])
                graph.grow(gram, work_budget=1200)
            with LivingGraph(path, scope='lab') as graph:
                again = graph.grow(gram, work_budget=1200)
                self.assertEqual(again['totals']['nodes'], 4801)
                self.assertEqual(again['totals']['relations'], 7200)
                self.assertEqual(again['totals']['unexpanded'], 2401)

    def test_absent_atoms_stops_safely(self):
        yes = World('y', 'lab', (), True)
        no = World('n', 'lab', (), False)
        data = discover_composition((yes, no), (World('yy', 'lab', (), True),
                                                World('nn', 'lab', (), False)),
                                    start='a', goal='z', work_budget=10)
        self.assertEqual(data['status'], 'HOLD')

    def test_independent_exhaustive_walk_oracle_randomized(self):
        rng = random.Random(20261106)
        for index in range(70):
            verts = ['n0', 'n1', 'n2', 'n3']
            kinds = ['a', 'b', 'c']
            es = tuple((rng.choice(verts), rng.choice(kinds), rng.choice(verts))
                       for _ in range(rng.randrange(1, 10)))
            world = World(str(index), 'oracle', es, True)
            steps = tuple(Atom(rng.choice(kinds), bool(rng.randrange(2)))
                          for _ in range(rng.randrange(1, 5)))
            # Exhaustive witness enumeration; independent of frontier-set code.
            oracle = False
            for states in itertools.product(verts, repeat=len(steps) + 1):
                if states[0] != 'n0' or states[-1] != 'n3':
                    continue
                valid = True
                for j, atom in enumerate(steps):
                    src, dst = states[j], states[j + 1]
                    if atom.reverse:
                        src, dst = dst, src
                    if (src, atom.relation, dst) not in es:
                        valid = False
                        break
                if valid:
                    oracle = True
                    break
            self.assertEqual(reaches(world, 'n0', 'n3', steps), oracle)


if __name__ == '__main__':
    unittest.main(verbosity=2)
