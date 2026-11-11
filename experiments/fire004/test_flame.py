"""FIRE-004: firewall, provenance, prequential and change-monitor tests."""
import unittest
from flame import (
    make_world, construct_models, Fixed003, PooledBeta, BayesianHMM, Hedge,
    roots_only, evaluate, source_rates, VerifiedLabel, REGIMES, POLICIES,
)


class FlameTests(unittest.TestCase):
    def test_private_world_state_never_in_public_episode(self):
        w = make_world(70000, 'abrupt')
        public = w.view(0)
        self.assertNotIn('truth', public.__dataclass_fields__)
        self.assertNotIn('hidden_labels', public.__dataclass_fields__)
        self.assertNotIn('hidden_rates', public.__dataclass_fields__)
        self.assertNotIn('regime', public.__dataclass_fields__)
        self.assertEqual(public.step, 0)

    def test_claims_collapse_into_three_verified_origins(self):
        w = make_world(70001, 'copied')
        case = w.view(0)
        self.assertEqual(len(case.reports), 5)
        self.assertEqual(len(roots_only(case)), 3)
        self.assertEqual(case.reports[0].answer, case.reports[2].answer)

    def test_compromised_auditor_is_invisible_to_policy(self):
        w = make_world(70001, 'compromised')
        case = w.view(0)
        self.assertEqual(len(roots_only(case)), 5)
        self.assertEqual(len(set(w.hidden_origins[0])), 3)
        # No method receiving only this public attestation may assert it
        # discovered secret common ancestry in the observed record.

    def test_all_predictions_occur_before_any_feedback(self):
        w = make_world(70002, 'steady')
        models = construct_models()
        case = w.view(0)
        predictions = {key: model.predict(case) for key, model in models.items()}
        self.assertEqual(set(predictions), set(POLICIES))
        self.assertTrue(all(0 < p < 1 for p in predictions.values()))
        self.assertEqual(models['pooled_beta'].a, 4)
        self.assertFalse(models['hmm_fast'].trust)
        receipt = w.verify(0)
        for model in models.values():
            model.update(case, receipt)
        self.assertGreater(models['pooled_beta'].a + models['pooled_beta'].b, 5)
        self.assertTrue(models['hmm_fast'].trust)

    def test_trust_estimator_responds_to_verified_contradictions(self):
        w = make_world(70003, 'steady')
        case = w.view(0)
        hmm = BayesianHMM(.08)
        hmm.predict(case)
        positive_roots = [root for root, bit in roots_only(case)]
        self.assertEqual(len(positive_roots), 5)
        first_root, report_bit = roots_only(case)[0]
        hypothetical = VerifiedLabel(case.step, report_bit)
        hmm.update(case, hypothetical)
        supported = hmm.trust[first_root]
        opposite = BayesianHMM(.08)
        opposite.predict(case)
        opposite.update(case, VerifiedLabel(case.step, not report_bit))
        contradicted = opposite.trust[first_root]
        self.assertGreater(supported, contradicted)

    def test_reject_unverified_or_stale_feedback(self):
        w = make_world(70004, 'steady')
        case = w.view(0)
        model = PooledBeta()
        with self.assertRaises(ValueError):
            model.update(case, VerifiedLabel(99, True))
        with self.assertRaises(ValueError):
            model.update(case, VerifiedLabel(0, True, authority='untrusted'))
        self.assertEqual((model.a, model.b), (4., 1.))

    def test_hedge_needs_forecast_before_label(self):
        h = Hedge(True)
        w = make_world(70005, 'steady')
        with self.assertRaises(ValueError):
            h.update(w.view(0), w.verify(0))

    def test_alarm_is_after_verified_surprise(self):
        w = make_world(70006, 'steady')
        h = Hedge(True)
        # Force a hypothetical sequence of high-confidence wrong
        # forecast *for testing the monitor*, not for testing accuracy.
        for i in range(3):
            case = w.view(i)
            h.predict(case)
            h.last_p = .999 if not w.hidden_labels[i] else .001
            h.update(case, w.verify(i))
        self.assertTrue(h.alarm_steps)
        self.assertEqual(h.alarm_steps[0], 0)
        self.assertAlmostEqual(sum(h.weights), 1.)

    def test_routine_sources_match_precise_transition_window(self):
        self.assertEqual(source_rates('abrupt', 47)['root-0'], .88)
        self.assertEqual(source_rates('abrupt', 48)['root-0'], .12)
        self.assertEqual(source_rates('transient', 47)['root-0'], .78)
        self.assertEqual(source_rates('transient', 48)['root-0'], .12)
        self.assertEqual(source_rates('transient', 50)['root-0'], .78)

    def test_replay_and_metric_ranges(self):
        for regime in REGIMES:
            a = evaluate(70008, regime)
            b = evaluate(70008, regime)
            self.assertEqual(a, b)
            for policy in (*POLICIES, 'oracle'):
                row = a[policy]
                self.assertGreaterEqual(row['brier'], 0)
                self.assertLessEqual(row['brier'], 1)
                self.assertGreaterEqual(row['coverage'], 0)
                self.assertLessEqual(row['coverage'], 1)

    def test_frozen_fire003_is_imported_actual_prior_experiment(self):
        w = make_world(70009, 'copied')
        self.assertIsInstance(construct_models()['fire003'], Fixed003)
        self.assertTrue(0 < Fixed003().predict(w.view(0)) < 1)

    def test_bad_generator_regime(self):
        with self.assertRaises(ValueError):
            make_world(1, 'unseen')


if __name__ == '__main__':
    unittest.main()
