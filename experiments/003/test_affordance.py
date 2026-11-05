"""MOTIF-003 exercises the existing 002 model in a separate, bounded decision layer."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '002'))
from motif002 import F, induce, lessons, scene, possibilities, utility
from affordance import (actions, frontier_after, analyze_first_moves,
                        select_first_move, witness_gap, run_demo)


class CapabilityHorizonTests(unittest.TestCase):
    def setUp(self):
        self.verbs = induce(lessons())
        self.world = scene()

    def test_initial_actions_include_repair_and_teach(self):
        self.assertEqual(len(actions(self.world, self.verbs, possibilities)), 2)

    def test_different_immediate_and_frontier_choices(self):
        rows = analyze_first_moves(self.world, self.verbs, possibilities, utility)
        greedy = select_first_move(rows, 'immediate')
        opening = select_first_move(rows, 'new-choices')
        self.assertEqual(greedy['immediate_delta'], 10)
        self.assertEqual(opening['immediate_delta'], 4)
        self.assertGreater(len(opening['new_affordances']), 0)
        self.assertEqual(len(greedy['new_affordances']), 0)
        self.assertNotEqual((greedy['operator'], greedy['roles']),
                            (opening['operator'], opening['roles']))

    def test_world_and_observations_not_mutated(self):
        snapshot = self.world
        analyze_first_moves(self.world, self.verbs, possibilities, utility)
        self.assertEqual(snapshot, self.world)
        self.assertNotIn(F('usable', 'bike1'), self.world)

    def test_no_permission_means_no_recommended_action(self):
        denied = scene(permissions=False)
        self.assertEqual(actions(denied, self.verbs, possibilities), [])
        self.assertIsNone(select_first_move(analyze_first_moves(
            denied, self.verbs, possibilities, utility)))

    def test_frontier_budget_exhaustion_is_visible(self):
        reached, truncated = frontier_after(self.world, self.verbs, possibilities,
                                            horizon=3, max_worlds=1)
        self.assertEqual(reached, 1)
        self.assertTrue(truncated)

    def test_witness_mismatch_kept_distinct(self):
        observed = frozenset({F('thing', 'test')})
        predicted = frozenset({F('other', 'test')})
        gap = witness_gap(predicted, observed)
        self.assertFalse(gap['agrees'])
        self.assertEqual(gap['missing'], (F('other', 'test'),))
        self.assertEqual(gap['unexpected'], (F('thing', 'test'),))

    def test_002_integration_demo(self):
        self.assertTrue(run_demo()['different_first_moves'])


if __name__ == '__main__':
    unittest.main()
