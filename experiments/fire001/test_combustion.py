import unittest
from combustion import Furnace, Owner, Question, make_world, new_affordances, run, select


class CombustionTests(unittest.TestCase):
    def test_no_owner_truth_in_public_question(self):
        questions, owner = make_world(4101)
        self.assertNotIn('truth', QuestionsFields(questions['Q0']))
        self.assertNotIn('reports', QuestionsFields(questions['Q0']))
        self.assertEqual(set(questions), set(owner.truth))
        self.assertNotIn('owner', vars(Furnace(questions, owner).public_view()))

    def test_same_world_replay(self):
        self.assertEqual(run(9101, 'fire', .5), run(9101, 'fire', .5))

    def test_source_starvation_is_ember(self):
        q = {'Q0': Question('Q0', 99, 3, 1, 1)}
        owner = Owner({'Q0': True}, {'Q0': (True,)})
        f = Furnace(q, owner, budget=8, unlocked={'Q0'})
        self.assertEqual(f.eligible(), [])
        self.assertIsNone(select(f.public_view(), 'fire', 1.))
        self.assertEqual(f.spent, 0)

    def test_no_child_without_independent_certification(self):
        q = {'Q0': Question('Q0', 3, 1, 1, 1, ('Q1',)),
             'Q1': Question('Q1', 7, 1, 1, 1)}
        owner = Owner({'Q0': True, 'Q1': True},
                      {'Q0': (False,), 'Q1': (True,)})
        f = Furnace(q, owner, unlocked={'Q0'}, budget=8)
        self.assertEqual(new_affordances(q, f.unlocked, f.finished, 'Q0'), 1)
        for _ in range(3):
            f.apply('Q0')
        self.assertIn('Q0', f.failed)
        self.assertNotIn('Q1', f.unlocked)
        self.assertEqual(f.score, 0)
        self.assertEqual(f.false_attempts, 1)

    def test_quorum_and_heat_gate(self):
        q = {'Q0': Question('Q0', 3, 3, 2, 3)}
        owner = Owner({'Q0': True}, {'Q0': (True, True, False)})
        f = Furnace(q, owner, unlocked={'Q0'}, budget=7)
        for _ in range(3):
            self.assertEqual(f.next_action('Q0'), 'observe')
            f.apply('Q0')
        self.assertEqual(f.next_action('Q0'), 'reason')
        f.apply('Q0'); f.apply('Q0')
        self.assertEqual(f.next_action('Q0'), 'verify')
        f.apply('Q0')
        self.assertIn('Q0', f.finished)
        self.assertEqual(f.score, 3)

    def test_duplicate_origin_is_rejected(self):
        q = {'Q0': Question('Q0', 1, 3, 1, 3)}
        class DuplicateOwner(Owner):
            def observe(self, key, index):
                return super().observe(key, 0)
        f = Furnace(q, DuplicateOwner({'Q0': True}, {'Q0': (True,) * 3}),
                    unlocked={'Q0'})
        f.apply('Q0')
        with self.assertRaises(ValueError):
            f.apply('Q0')
        self.assertEqual(f.spent, 1)

    def test_budget_cannot_overshoot(self):
        q = {'Q0': Question('Q0', 1, 3, 3, 3)}
        owner = Owner({'Q0': True}, {'Q0': (True,) * 3})
        f = Furnace(q, owner, unlocked={'Q0'}, budget=2)
        self.assertIsNone(select(f.public_view(), 'fire', 1.))
        f.apply('Q0'); f.apply('Q0')
        with self.assertRaises(ValueError):
            f.apply('Q0')

    def test_equal_budgets_all_policies(self):
        for policy in ('value', 'information', 'ratio', 'fire'):
            result = run(9107, policy, .5, budget=24)
            self.assertLessEqual(result['steps'], 24)
            self.assertGreaterEqual(result['verified_value'], 0)
            self.assertEqual(sum(r['action'] == 'verify' for r in result['history']),
                             result['correct_tasks'] + result['false_attempts'])


def QuestionsFields(q):
    return tuple(q.__dataclass_fields__)


if __name__ == '__main__':
    unittest.main()
