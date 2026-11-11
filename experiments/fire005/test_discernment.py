"""Proof-gated FIRE-005 test suite: Bayesian filter, reversible edits, leakage."""
import unittest

from discernment import (
    RootRunLength, BayesianChangePredictor, ReversibleGovernor,
    ClassicalTwoExpertHedge, PolicyReceipt, BOCPD_MAX_STATES,
    evaluate, REGIMES, MODEL_NAMES
)
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fire004'))
from flame import make_world, VerifiedLabel


class DiscernmentTests(unittest.TestCase):
    def test_bocpd_bayes_mass_normalizes_and_adapts(self):
        state = RootRunLength()
        initial = state.predict_correctness()
        for _ in range(36):
            state.learn(True)
        high = state.predict_correctness()
        self.assertGreater(high, initial)
        for _ in range(25):
            state.learn(False)
        self.assertLess(state.predict_correctness(), high)
        self.assertAlmostEqual(sum(s.mass for s in state.states), 1.)
        self.assertLessEqual(len(state.states), BOCPD_MAX_STATES)
        self.assertGreater(state.last_changepoint_posterior, 0)

    def test_separate_root_counts_are_not_claim_counts(self):
        w = make_world(91000, 'copied')
        model = BayesianChangePredictor()
        c = w.view(0)
        model.predict(c)
        model.update(c, w.verify(0))
        self.assertEqual(len(model.roots), 3)
        self.assertEqual(model.forecast_history[0]['attested_distinct_roots'], 3)

    def test_compromised_auditor_can_still_deceive(self):
        w = make_world(91000, 'compromised')
        c = w.view(0)
        m = BayesianChangePredictor()
        m.predict(c)
        m.update(c, w.verify(0))
        self.assertEqual(len(m.roots), 5)
        self.assertEqual(len(set(w.hidden_origins[0])), 3)

    def test_no_label_or_hidden_rate_in_public_view(self):
        w = make_world(91001, 'abrupt')
        case = w.view(47)
        self.assertNotIn('hidden_labels', vars(case))
        self.assertNotIn('hidden_origins', vars(case))
        self.assertNotIn('hidden_rates', vars(case))
        self.assertNotIn('regime', vars(case))

    def test_bocpd_requires_public_forecast_before_feedback(self):
        w = make_world(91002, 'steady')
        model = BayesianChangePredictor()
        with self.assertRaises(ValueError):
            model.update(w.view(0), w.verify(0))
        model.predict(w.view(0))
        with self.assertRaises(ValueError):
            model.update(w.view(0), VerifiedLabel(0, True, 'forged'))
        self.assertFalse(model.roots)
        model.update(w.view(0), w.verify(0))
        with self.assertRaises(ValueError):
            model.update(w.view(0), w.verify(0))
        with self.assertRaises(ValueError):
            model.predict(w.view(0))

    def test_signed_regret_and_changepoint_support_required(self):
        gov = ReversibleGovernor(True)
        simple = ReversibleGovernor(False)
        w = make_world(91003, 'steady')
        for step in range(12):
            case = w.view(step)
            receipt = VerifiedLabel(step, False)
            # HEDGE very wrong, BOCPD correct, but *no* CP support.
            gov.predict(step, .9, .1)
            simple.predict(step, .9, .1)
            gov.update(case, receipt, .9, .1, .01)
            simple.update(case, receipt, .9, .1, .01)
        self.assertEqual(gov.mode, 'hedge')
        self.assertEqual(simple.mode, 'bocpd')
        self.assertEqual(len(gov.receipts), 0)
        self.assertEqual(simple.receipts[0].status,
                         'PENCIL_REVERSIBLE_METHOD_EDIT')

    def test_continued_evidence_triggers_edit_and_rollback(self):
        gov = ReversibleGovernor(True)
        w = make_world(91004, 'steady')
        for step in range(12):
            case = w.view(step)
            r = VerifiedLabel(step, False)
            gov.predict(step, .9, .1)
            gov.update(case, r, .9, .1, .2)
        self.assertEqual(gov.mode, 'bocpd')
        self.assertEqual(gov.receipts[0].step, 11)
        for step in range(12, 20):
            case = w.view(step)
            r = VerifiedLabel(step, False)
            self.assertEqual(gov.mode, 'bocpd')
            gov.predict(step, .1, .9)
            gov.update(case, r, .1, .9, .01)
        self.assertEqual(gov.mode, 'hedge')
        self.assertEqual(gov.receipts[-1].reason, 'REVOKED_BY_VERIFIED_REGRET')
        self.assertEqual(gov.receipts[-1].step, 19)
        self.assertEqual([rec.from_method for rec in gov.receipts],
                         ['hedge', 'bocpd'])

    def test_cannot_update_from_wrong_label_receipt(self):
        w = make_world(91005, 'steady')
        governor = ReversibleGovernor()
        mixing = ClassicalTwoExpertHedge()
        with self.assertRaises(ValueError):
            governor.update(w.view(0), VerifiedLabel(1, True), .5, .5, .1)
        with self.assertRaises(ValueError):
            mixing.update(w.view(0), VerifiedLabel(0, True, 'fake'), .5, .5)

    def test_hedge2_weights_are_normalized_after_online_updates(self):
        w = make_world(91006, 'steady')
        classical = ClassicalTwoExpertHedge()
        for step in range(20):
            case, r = w.view(step), w.verify(step)
            p = classical.predict(.8, .3)
            self.assertTrue(0 < p < 1)
            classical.update(case, r, .8, .3)
            self.assertAlmostEqual(sum(classical.weights), 1.)

    def test_fixed_seed_replay_and_valid_ranges(self):
        for regime in REGIMES:
            first = evaluate(91007, regime)
            second = evaluate(91007, regime)
            self.assertEqual(first, second)
            for name in MODEL_NAMES:
                self.assertGreaterEqual(first[name]['brier'], 0)
                self.assertLessEqual(first[name]['brier'], 1)
                self.assertGreaterEqual(first[name]['coverage'], 0)
                self.assertLessEqual(first[name]['coverage'], 1)
            self.assertEqual(len(first['bocpd']['cp_scores']), 96)

    def test_unknown_regime_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(91001, 'fairy-fire')


if __name__ == '__main__':
    unittest.main()
