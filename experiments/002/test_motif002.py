"""MOTIF-002 test suite: python -m unittest -v test_motif002.py"""
import unittest
from motif002 import F, Transition, induce, lessons, scene, possibilities, explore, report


class UnnamedVerbTests(unittest.TestCase):
    def setUp(self):
        self.verbs = induce(lessons())

    def test_no_action_labels_or_role_hints(self):
        self.assertEqual(len(self.verbs), 2)
        self.assertTrue(all(x.id.startswith('verb-') for x in self.verbs.values()))
        self.assertTrue(all(x.demonstrations == 3 for x in self.verbs.values()))

    def test_holdout_names_and_composition(self):
        plan = explore(scene(), self.verbs)
        self.assertEqual(len(plan['path']), 3)
        self.assertIn(F('skill', 'Jo', 'repair'), plan['final'])
        self.assertIn(F('usable', 'bike1'), plan['final'])
        self.assertIn(F('usable', 'bike2'), plan['final'])

    def test_no_permission_is_no_plan(self):
        plan = explore(scene(permissions=False), self.verbs)
        self.assertEqual(plan['path'], ())
        self.assertEqual(plan['reachable'], 1)

    def test_missing_wrenches_disallows_repairs(self):
        plan = explore(scene(tools=False), self.verbs)
        self.assertNotIn(F('usable', 'bike1'), plan['final'])
        self.assertNotIn(F('usable', 'bike2'), plan['final'])

    def test_no_fixture_can_imply_real_authority(self):
        self.assertTrue(all(any(f[0] == 'permits' for f in v.requires)
                            for v in self.verbs.values()))
        self.assertRaises(ValueError, induce, [Transition(frozenset(),
                            frozenset({F('usable','b')}), 'REAL')])

    def test_noop_does_not_invent_rule(self):
        self.assertEqual(induce([Transition(scene(), scene())]), {})

    def test_one_off_noise_is_not_required(self):
        self.assertTrue(all(all(f[0] != 'likes' for f in v.requires)
                            for v in self.verbs.values()))

    def test_training_order_does_not_change_model(self):
        backward = induce(list(reversed(lessons())))
        self.assertEqual(self.verbs, backward)

    def test_new_world_is_not_mutated(self):
        before = scene()
        list(possibilities(before, self.verbs))
        self.assertEqual(before, scene())

    def test_report_is_consistent(self):
        self.assertEqual(report()['training_pairs'], 6)


if __name__ == '__main__':
    unittest.main()
