"""Executable guardrails for FIRE-002, including actual online update."""
import unittest
from productive import (
    EpistemicLedger, probability_of_majority_correct, productive_select,
    run, world, REGIMES,
)
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fire001'))
from combustion import Furnace


class ProductiveCombustionTests(unittest.TestCase):
    def test_posterior_uses_only_revealed_reports(self):
        self.assertAlmostEqual(probability_of_majority_correct((), 1, .8), .8)
        self.assertGreater(probability_of_majority_correct((True, True), 3, .8),
                           probability_of_majority_correct((), 3, .8))
        self.assertAlmostEqual(
            probability_of_majority_correct((True, False), 3, .8), .8)
        with self.assertRaises(ValueError):
            probability_of_majority_correct((True,), 2, .8)

    def test_no_unverified_updates(self):
        ledger = EpistemicLedger()
        before = vars(ledger).copy()
        with self.assertRaises(ValueError):
            ledger.learn({'action': 'observe', 'answer': True}, (True,), 10, False)
        self.assertEqual(vars(ledger), before)

    def test_verified_feedback_changes_source_model(self):
        ledger = EpistemicLedger()
        initial = ledger.source_accuracy
        ledger.learn({'action': 'verify', 'certified': False, 'guess': True},
                     (True, True, False), 7, True)
        self.assertLess(ledger.source_accuracy, initial)
        self.assertLess(ledger.child_yield, .75)
        self.assertEqual(ledger.realized_value, 0)
        ledger.learn({'action': 'verify', 'certified': True, 'guess': False},
                     (False, False, True), 7, True)
        self.assertEqual(ledger.realized_value, 7)
        self.assertEqual(ledger.verified_count, 2)

    def test_no_hidden_oracle_in_selection_view(self):
        q, owner = world(42000, 'steady')
        f = Furnace(q, owner)
        public = f.public_view()
        self.assertNotIn('owner', vars(public))
        self.assertNotIn('truth', vars(public))
        initial = productive_select(public, EpistemicLedger())
        self.assertIn(initial, public.eligible)
        flipped = type(owner)({k: not v for k, v in owner.truth.items()},
                              {k: tuple(not x for x in y)
                               for k, y in owner.reports.items()})
        other = Furnace(q, flipped)
        self.assertEqual(initial,
                         productive_select(other.public_view(), EpistemicLedger()))

    def test_question_unlock_requires_certification(self):
        q, owner = world(42003, 'steady')
        f = Furnace(q, owner)
        # Nothing can unlock solely from a speculative scheduler selection.
        selected = productive_select(f.public_view(), EpistemicLedger(), 4.)
        self.assertIn(selected, f.unlocked)
        unlocked_before = set(f.unlocked)
        if f.next_action(selected) == 'observe':
            f.apply(selected)
        self.assertEqual(f.unlocked, unlocked_before)

    def test_no_free_oxygen_or_budget_overrun(self):
        for policy in ('ratio', 'fire001', 'productive_frozen',
                       'productive_online', 'value', 'information'):
            result = run(42020, 'correlated', policy, 2., budget=24)
            self.assertLessEqual(result['steps'], 24)
            self.assertEqual(sum(a['action'] == 'verify' for a in result['actions']),
                             result['certified_questions'] +
                             result['failed_verifications'])
            if policy != 'productive_online':
                self.assertEqual(result['learning_events'], 0)
            else:
                self.assertEqual(result['learning_events'],
                                 result['certified_questions'] +
                                 result['failed_verifications'])

    def test_reproducibility_and_regime_difference(self):
        for regime in REGIMES:
            a = run(42024, regime, 'productive_online', 1.)
            b = run(42024, regime, 'productive_online', 1.)
            self.assertEqual(a, b)
        self.assertNotEqual(world(42024, 'steady')[1].reports,
                            world(42024, 'correlated')[1].reports)

    def test_reject_unknown_regime(self):
        with self.assertRaises(ValueError):
            world(99, 'magic')


if __name__ == '__main__':
    unittest.main()
