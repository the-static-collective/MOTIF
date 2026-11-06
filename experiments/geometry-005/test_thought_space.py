import unittest
from thought_space import *
from demo import synthetic_fellowship,main
from display import render_svg
from interface import process

class ThoughtSpaceTests(unittest.TestCase):
    def setUp(self):self.g=synthetic_fellowship()

    def test_validated_relationships_have_provenance(self):
        with self.assertRaises(ValueError):Edge('shelf','meal','associated','')
        with self.assertRaises(ValueError):Edge('shelf','meal','equals','x')
        with self.assertRaises(ValueError):self.g.add_edge(Edge('shelf','unknown','associated','source'))

    def test_bridge_is_hypothesis_not_an_edge(self):
        before=len(self.g.edges)
        p=self.g.bridge_candidates()
        self.assertTrue(any(x['nodes']==['meal','shelf'] and len(x['via'])>=2 for x in p))
        self.assertTrue(all(x['status']=='HYPOTHESIS_ONLY' for x in p))
        self.assertEqual(before,len(self.g.edges))

    def test_deduplicated_echo_roots_not_independent(self):
        g=ThoughtGraph([Node(x,x) for x in 'abcd'],[
            Edge('a','c','associated','same-root'), Edge('b','c','associated','same-root'),
            Edge('a','d','associated','same-root'), Edge('b','d','associated','same-root')])
        self.assertEqual(g.bridge_candidates(),[])

    def test_contradictions_are_not_positive_bridges(self):
        self.assertFalse(any(e.relation=='contradicts' for e in self.g.positive_links()))
        self.assertEqual(len(self.g.contradictions()),1)
        self.assertEqual(self.g.route('claim_yes','claim_no')['status'],'HOLD')

    def test_directions_are_not_reversed(self):
        self.assertEqual(self.g.route('fish','storage')['status'],'PATH')
        self.assertEqual(self.g.route('storage','fish')['status'],'HOLD')

    def test_free_text_is_weak_association_not_fact(self):
        g=from_text('birds meet fish; fish move and birds rest','mock-paragraph')
        self.assertTrue(all(e.relation=='co_mentioned' for e in g.edges))
        self.assertTrue(all(e.confidence==0.1 for e in g.edges))
        self.assertTrue(all(e.origin=='mock-paragraph' for e in g.edges))
        self.assertEqual(g.positive_links(),[])
        self.assertGreater(len(g.positive_links(include_co_mention=True)),0)

    def test_optional_geometry_can_hold(self):
        plan=choose_thought_space(self.g,'explore',allow_geometry=False)
        self.assertEqual(plan['projection'],'NONE')
        self.assertEqual(plan['coordinates'],{})
        self.assertEqual(plan['authority'],'HOLD')

    def test_route_mode_selected_when_anchored(self):
        p=choose_thought_space(self.g,'connect these two ideas',anchors=('shelf','meal'))
        self.assertEqual(p['thought_mode'],'trace')
        self.assertEqual(p['answer']['status'],'PATH')
        self.assertEqual(p['projection'],'radial')

    def test_contrast_mode_keeps_conflict(self):
        p=choose_thought_space(self.g,'compare contradicting claims')
        self.assertEqual(p['thought_mode'],'contrast')
        self.assertEqual(p['answer']['status'],'CONFLICTS')

    def test_all_layouts_cover_same_nodes(self):
        for p in (layout_spring(self.g),layout_radial(self.g,'shelf'),layout_hex(self.g,'shelf')):
            self.assertEqual(set(p),set(self.g.nodes))

    def test_machine_interface_accepts_prose_and_refuses_excessive_input(self):
        graph,plan,output=process({'text':'Words and ideas connect words',
            'origin':'text-fixture','geometry_preference':'flower_hex'})
        self.assertEqual(output['authority'],'HOLD')
        self.assertTrue(all(e.relation=='co_mentioned' for e in graph.edges))
        with self.assertRaises(ValueError):
            process({'text':'too much '*3000})

    def test_svg_labels_and_hypotheses(self):
        plan=choose_thought_space(self.g,'explore')
        svg=render_svg(self.g,plan)
        self.assertIn('Food shelf',svg)
        self.assertIn('HOLD:',svg)
        self.assertIn('stroke-dasharray=',svg)

    def test_no_geometry_from_naked_words(self):
        g=ThoughtGraph([Node('sole','Sole')])
        self.assertEqual(choose_thought_space(g,'explore')['projection'],'NONE')

    def test_explicit_flower_of_life_layout_preference(self):
        p=choose_thought_space(self.g,'explore',geometry_preference='flower_hex')
        self.assertEqual(p['projection'],'flower_hex')
        self.assertEqual(set(p['coordinates']),set(self.g.nodes))
        with self.assertRaises(ValueError):
            choose_thought_space(self.g,'explore',geometry_preference='quantum_fractal')

    def test_snapshot_determinism(self):
        self.assertEqual(main(False),main(False))

    def test_escape_user_label(self):
        g=ThoughtGraph([Node('bad','<script>alert(1)</script>'),Node('ok','Good')],
             [Edge('bad','ok','associated','text')])
        s=render_svg(g,choose_thought_space(g,'explore'))
        self.assertNotIn('<script>',s)
        self.assertIn('&lt;script&gt;',s)

if __name__=='__main__':unittest.main()
