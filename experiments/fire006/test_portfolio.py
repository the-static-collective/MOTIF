"""FIRE-006 deterministic, temporal, cost, and rollback tests."""
import unittest

from portfolio import (
    POLICIES, Portfolio, RevisionReceipt, UNIFORM, LOOKBACK,
    fit_candidate, project_simplex, tv, evaluate, N_STEPS
)
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fire004"))
from flame import PublicEpisode, VerifiedLabel, make_world


class PriceTests(unittest.TestCase):
    def test_simplex_projection_and_cost(self):
        for values in ((-4., 0., 2.), (.1, .1, .1), (2., 1., -1.)):
            w = project_simplex(values)
            self.assertAlmostEqual(sum(w), 1.)
            self.assertTrue(all(v >= 0 for v in w))
        self.assertAlmostEqual(tv((1.,0.,0.), (0.,1.,0.)), 1.)
        self.assertEqual(tv(UNIFORM, UNIFORM), 0)

    def test_optimizer_uses_only_past_verified_labels(self):
        poor = (1., 0., 0.)
        examples = [((.9,.1,.5), 0)] * LOOKBACK
        candidate = fit_candidate(examples, poor)
        self.assertLess(candidate[0], poor[0])
        self.assertAlmostEqual(sum(candidate), 1.)
        self.assertEqual(candidate, fit_candidate(examples, poor))

    def test_cannot_update_before_forecast(self):
        w = make_world(95000, "steady")
        policy = Portfolio("fire006")
        case = w.view(0)
        with self.assertRaises(ValueError):
            policy.update(case, w.verify(0))
        self.assertEqual(policy.weights, UNIFORM)
        self.assertEqual(len(policy.history), 0)

    def test_provenance_absent_from_portfolio_interface(self):
        w = make_world(95001, "compromised")
        policy = Portfolio("fire006")
        case = w.view(0)
        self.assertNotIn("hidden_rates", vars(case))
        self.assertNotIn("truth", vars(case))
        self.assertNotIn("regime", vars(case))
        policy.forecast(case.step, (.2, .4, .8))
        with self.assertRaises(ValueError):
            policy.update(case, VerifiedLabel(0, True, "rumor"))
        self.assertEqual(policy.paid_price, 0)

    def test_gating_preserves_hypotheses_without_evidence(self):
        p = Portfolio("fire006")
        w = make_world(95002, "steady")
        for step in range(15):
            c = w.view(step)
            p.forecast(step, (.5, .5, .5))
            p.update(c, w.verify(step))
        self.assertEqual(p.weights, UNIFORM)
        self.assertEqual(p.revisions, 0)
        self.assertEqual(p.rollbacks, 0)

    def test_rapid_hedge_must_pay_price(self):
        w = make_world(95003, "steady")
        policy = Portfolio("exp3")
        case = w.view(0)
        policy.forecast(0, (.9,.1,.5))
        policy.update(case, VerifiedLabel(0, False))
        self.assertGreater(policy.paid_price, 0)
        self.assertNotEqual(policy.weights, UNIFORM)
        self.assertEqual(policy.receipts[0].status, "PENCIL_METHOD_REVISION")

    def test_rollback_is_independently_verified(self):
        p = Portfolio("fire006")
        w = make_world(95004, "steady")
        # Force a paid candidate trial; both forecasts use the same 3
        # underlying experts and future verification is still independent.
        old = UNIFORM
        new = (1., 0., 0.)
        p._change(15, new, "TRIAL_REVISION", .4, 16)
        p._trial = {"old": old, "new": new, "loss_deltas": []}
        for step in range(16, 24):
            case = w.view(step)
            p.forecast(step, (.99, .01, .01))
            p.update(case, VerifiedLabel(step, False))
        self.assertGreaterEqual(p.rollbacks, 1)
        self.assertAlmostEqual(sum(p.weights), 1.)
        self.assertEqual(p.receipts[-1].operation, "ROLLBACK")
        self.assertEqual(p.receipts[-1].verification_count, 8)
        self.assertGreater(p.receipts[-1].subsequent_verified_regret, .005)

    def test_no_rollback_ablation_never_reverses(self):
        policy = Portfolio("fire006_no_rollback")
        w = make_world(95005, "steady")
        for step in range(25):
            c = w.view(step)
            policy.forecast(step, (.8,.2,.1))
            policy.update(c, w.verify(step))
        self.assertEqual(policy.rollbacks, 0)

    def test_current_outcome_never_changes_current_prediction(self):
        w = make_world(95006, "steady")
        case = w.view(0)
        left = Portfolio("exp3")
        right = Portfolio("exp3")
        self.assertEqual(left.forecast(0, (.9,.4,.2)),
                         right.forecast(0, (.9,.4,.2)))
        left.update(case, VerifiedLabel(0, False))
        right.update(case, VerifiedLabel(0, True))
        self.assertNotEqual(left.weights, right.weights)

    def test_replay_and_budget(self):
        for regime in ("steady", "abrupt", "copied", "compromised"):
            a = evaluate(95007, regime)
            self.assertEqual(a, evaluate(95007, regime))
            self.assertEqual(set(a), set(POLICIES))
            for strategy in a.values():
                self.assertGreaterEqual(strategy["brier"], 0)
                self.assertLessEqual(strategy["brier"], 1)
                self.assertGreaterEqual(strategy["revision_price"], 0)
                self.assertGreaterEqual(strategy["total_loss_with_price"],
                                        strategy["brier"] - 1e-7)
                self.assertLess(strategy["revision_count"] if "revision_count" in strategy
                                else strategy["revisions"], N_STEPS)

    def test_fixed_equal_never_pays_to_change(self):
        r = evaluate(95008, "steady")
        self.assertEqual(r["equal3"]["revision_price"], 0)
        self.assertEqual(r["equal3"]["revisions"], 0)
        self.assertEqual(r["equal3"]["rollback_count"], 0)

    def test_bad_policy_rejected(self):
        with self.assertRaises(ValueError):
            Portfolio("oracle_tomorrow")


if __name__ == "__main__":
    unittest.main()
