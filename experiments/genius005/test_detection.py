"""GENIUS-005 falsifiers: exactness, false alarms, future-only feedback."""
import json
import math
import unittest

from detectors import (
    ALPHA, CHECK_TIMES, Detectors, fisher_two_sided,
    detection_summary,
)
from benchmark import (
    CUSUM_OPTIONS, FORECASTS, FUTURE_SEEDS, REGIMES, STREAMS,
    VALIDATION_SEEDS, PublicReport, StandardForecasts,
    project, source_world, run_stream, run,
)


class TestExactMonitoring(unittest.TestCase):
    def test_exact_fisher_extremes_symmetry_and_no_early_warnings(self):
        self.assertEqual(fisher_two_sided(12, 24, 20, 40), 1.0)
        p = fisher_two_sided(0, 40, 24, 24)
        self.assertLess(p, 1e-8)
        self.assertAlmostEqual(p, fisher_two_sided(24, 24, 0, 40))
        with self.assertRaises(ValueError):
            fisher_two_sided(3, 2, 1, 2)
        monitor = Detectors(tuple([True] * 20 + [False] * 20))
        for i in range(23):
            response = monitor.update(bool(i % 2), f"public:{i}")
            self.assertNotIn("EXACT", response["new_alarms"])
        self.assertNotIn("EXACT", monitor.alarms)

    def test_finite_familywise_accounting_and_long_shift_detection(self):
        # Controlled finite scope: K predetermined tests, each alpha/K.
        self.assertEqual(len(CHECK_TIMES), 12)
        self.assertEqual(CHECK_TIMES[0], 24)
        self.assertEqual(CHECK_TIMES[-1], 112)
        monitor = Detectors(tuple([False]*40))
        for i in range(112):
            report = monitor.update(True, f"public:{i}")
            if "fisher_p_value" in report:
                self.assertEqual(report["per_test_threshold"], ALPHA / len(CHECK_TIMES))
        self.assertIn("EXACT", monitor.alarms)
        observed = detection_summary(monitor, 40, tuple(range(112)))
        self.assertTrue(observed["EXACT"]["alarm_exists"])
        # This artificial change occurred at round 0: its first alarm is
        # before the declared 40, so correctly labeled as early/false.
        self.assertTrue(observed["EXACT"]["false_alarm"])

    def test_repeated_evidence_ref_does_not_amplify_statistical_support(self):
        monitor = Detectors(tuple([True] * 40))
        monitor.update(False, "same-receipt")
        with self.assertRaises(ValueError):
            monitor.update(False, "same-receipt")
        self.assertEqual(len(monitor.history), 1)
        self.assertNotIn("EXACT", monitor.alarms)

    def test_stable_stream_is_not_guaranteed_zero_alarms(self):
        # A false-alarm budget is a probabilistic statement, not a promise
        # that any particular finite IID sequence cannot trigger.
        stable = run_stream(50541, "STABLE", 0, 6.0)
        self.assertIsNone(stable["ground_truth_change_round_for_evaluator_only"])
        self.assertGreater(stable["shared_samples"], 90)
        self.assertGreater(stable["withheld_samples"], 0)
        self.assertEqual(set(stable["mean_prequential_brier"]), set(FORECASTS))

    def test_withheld_and_public_note_is_stripped_at_projection(self):
        r = PublicReport("id", True, True, "synthetic:ref", "DO_NOT_SHARE")
        p = project(r)
        self.assertIsNotNone(p)
        self.assertEqual(p.private_text, "")
        self.assertEqual(project(PublicReport("w", False, False, "s", "SECRET")), None)
        self.assertNotIn("DO_NOT_SHARE", json.dumps(p.__dict__))

    def test_online_predict_then_update_prevents_future_label_leakage(self):
        initial = tuple([True]*24+[False]*16)
        model = StandardForecasts(initial)
        forecast = model.forecasts(False, False)
        copy = StandardForecasts(initial)
        self.assertEqual(copy.forecasts(False, False), forecast)
        model.update(False, forecast)
        copy.update(True, forecast)
        self.assertNotEqual(model.forecasts(False, False),
                            copy.forecasts(False, False))
        self.assertAlmostEqual(forecast["FROZEN"],
                               model.forecasts(False, False)["FROZEN"])

    def test_reporting_uses_scoring_truth_after_the_fact_only(self):
        d = Detectors(tuple([True]*40))
        indices = tuple(range(112))
        for i in indices:
            d.update(False, f"s:{i}")
        r0 = detection_summary(d, None, indices)
        r1 = detection_summary(d, 10, indices)
        self.assertEqual(d.alarms, d.alarms)
        self.assertNotEqual(r0["EXACT"]["true_detection"],
                            r1["EXACT"]["true_detection"])
        self.assertTrue(r1["EXACT"]["true_detection"])

    def test_internal_seeded_worlds_different_and_independent_of_prediction(self):
        a_train, a_future, a_change = source_world(50541, "LOCAL", 0)
        b_train, b_future, b_change = source_world(50541, "LOCAL", 1)
        self.assertEqual(len(a_train), 40)
        self.assertEqual(len(a_future), 120)
        self.assertNotEqual(a_future, b_future)
        self.assertEqual(a_change, 40)
        self.assertIsNone(b_change)
        self.assertTrue(all(r.private_text for r in a_future))
        with self.assertRaises(ValueError):
            source_world(50541, "MADE_UP", 0)


class TestProspectiveEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run()

    def test_all_future_worlds_and_classical_arms_preserved(self):
        r = self.report
        self.assertEqual(r["status"], "RESEARCH_HOLD_ENGINEER_AUTHORED_SYNTHETIC")
        self.assertEqual(len(r["config_frozen_sha256_before_holdout"]), 64)
        self.assertIn(r["precommitted_settings"]["selected_classical_cusum_threshold"],
                      CUSUM_OPTIONS)
        self.assertEqual(set(r["future_scenarios"]), set(REGIMES))
        self.assertEqual(r["precommitted_settings"]["validation_seeds"], VALIDATION_SEEDS)
        self.assertEqual(r["precommitted_settings"]["future_seeds"], FUTURE_SEEDS)
        self.assertTrue(r["no_live_people_contacted"])
        self.assertTrue(r["no_external_actions_taken"])
        for name, vals in r["future_scenarios"].items():
            self.assertEqual(vals["streams"], len(FUTURE_SEEDS)*STREAMS)
            self.assertEqual(set(vals["forecast_brier"]), set(FORECASTS))
            self.assertGreater(vals["withheld_excluded"], 0)
            self.assertEqual(set(vals["detection"]), {"NAIVE", "EXACT", "CUSUM"})

    def test_stable_and_noisy_no_positive_change_and_shift_has_positive(self):
        r=self.report["future_scenarios"]
        for name in ("STABLE", "NOISY_STABLE"):
            for det in r[name]["detection"].values():
                self.assertEqual(det["changed_streams"], 0)
                self.assertEqual(det["true_positive_streams"], 0)
        for name in ("ABRUPT", "LOCAL", "GRADUAL"):
            self.assertGreater(r[name]["detection"]["EXACT"]["changed_streams"], 0)
        self.assertLess(r["LOCAL"]["detection"]["EXACT"]["changed_streams"],
                        r["ABRUPT"]["detection"]["EXACT"]["changed_streams"])

    def test_receipts_no_private_simulator_notes(self):
        r=self.report
        txt=json.dumps(r)
        self.assertNotIn("PRIVATE_SIMULATOR_FIELD_MUST_NOT_EXPORT", txt)
        for rec in r["audit_traces"]:
            self.assertIn(rec["regime"], REGIMES)
            for e in rec["public_prediction_receipts"]:
                self.assertTrue(all(0 <= p <= 1 for p in
                                    e["forecast_before_feedback"].values()))
                self.assertIsNone(e["private_text"])
                self.assertIn("public_self_report", e)
                self.assertIn("alarms_before_current_report", e)


if __name__ == "__main__":
    unittest.main()
