"""MOTIF-015 offline regression tests; no PostHog credentials or network."""
import unittest

from observer import UnsafeObservation, evaluate, wilson_interval

NOW = "2026-11-06T09:00:00+00:00"


def packet():
    return {
        "schema": "motif.observation.015.v1",
        "source": {
            "provider": "posthog", "query_ref": "fixture:synthetic-funnel-001",
            "window_start": "2026-11-05T00:00:00Z", "window_end": "2026-11-05T22:00:00Z",
            "exported_at": "2026-11-06T08:00:00Z", "method": "same_cohort_funnel",
            "unique_actors": True, "same_cohort": True,
            "collection_consent": "explicit_opt_in", "personal_data_in_packet": False,
            "source_reviewed": True,
        },
        "prediction": {"metric": "artifact_completion_rate", "expected_rate": 0.7, "minimum_n": 30},
        "observation": {"entry_count": 100, "completed_count": 40},
    }


class ObservationTests(unittest.TestCase):
    def test_real_discrepancy_is_review_not_autonomous_action(self):
        receipt = evaluate(packet(), now=NOW)
        self.assertEqual(receipt["status"], "REVIEW_DEPARTURE")
        self.assertEqual(receipt["observed_rate"], 0.4)
        self.assertFalse(receipt["boundary"]["permission_to_act"])
        self.assertFalse(receipt["boundary"]["field_outcome_verified"])
        self.assertFalse(receipt["boundary"]["causation_established"])

    def test_match_is_not_claim_of_field_success(self):
        p = packet()
        p["prediction"]["expected_rate"] = 0.4
        receipt = evaluate(p, now=NOW)
        self.assertEqual(receipt["status"], "REVIEW_NO_DEPARTURE")
        self.assertFalse(receipt["boundary"]["field_outcome_verified"])

    def test_small_sample_holds(self):
        p = packet()
        p["observation"] = {"entry_count": 5, "completed_count": 1}
        self.assertIn("insufficient_sample", evaluate(p, now=NOW)["holds"])

    def test_zero_sample_holds_without_dividing(self):
        p = packet()
        p["observation"] = {"entry_count": 0, "completed_count": 0}
        r = evaluate(p, now=NOW)
        self.assertEqual(r["status"], "HOLD")
        self.assertIsNone(r["observed_rate"])

    def test_stale_export_holds(self):
        self.assertIn("stale_export", evaluate(packet(), now="2026-11-18T09:00:00Z")["holds"])

    def test_unreviewed_source_holds(self):
        p = packet()
        p["source"]["source_reviewed"] = False
        self.assertEqual(evaluate(p, now=NOW)["status"], "HOLD")

    def test_rejects_not_a_funnel(self):
        for key in ("unique_actors", "same_cohort"):
            p = packet()
            p["source"][key] = False
            with self.subTest(key=key), self.assertRaises(UnsafeObservation):
                evaluate(p, now=NOW)

    def test_rejects_person_level_data_and_extra_fields(self):
        p = packet()
        p["source"]["personal_data_in_packet"] = True
        with self.assertRaises(UnsafeObservation):
            evaluate(p, now=NOW)
        p = packet()
        p["observation"]["person_ids"] = ["secret"]
        with self.assertRaises(UnsafeObservation):
            evaluate(p, now=NOW)

    def test_requires_explicit_opt_in(self):
        p = packet()
        p["source"]["collection_consent"] = "implicit"
        with self.assertRaises(UnsafeObservation):
            evaluate(p, now=NOW)

    def test_rejects_bad_counts_and_bool(self):
        for invalid in (101, True, -1, "40"):
            p = packet()
            p["observation"]["completed_count"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(UnsafeObservation):
                evaluate(p, now=NOW)

    def test_rejects_invalid_prediction(self):
        for invalid in (True, float("nan"), -0.3, 1.2):
            p = packet()
            p["prediction"]["expected_rate"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(UnsafeObservation):
                evaluate(p, now=NOW)

    def test_rejects_time_travel_and_unzoned_clocks(self):
        p = packet()
        p["source"]["exported_at"] = "2026-11-09T20:00:00Z"
        with self.assertRaises(UnsafeObservation):
            evaluate(p, now=NOW)
        p = packet()
        p["source"]["window_start"] = "2026-11-05T09:00:00"
        with self.assertRaises(UnsafeObservation):
            evaluate(p, now=NOW)

    def test_wilson_bounds(self):
        lo, hi = wilson_interval(40, 100)
        self.assertTrue(0.3 < lo < 0.4 < hi < 0.5)
        self.assertEqual(wilson_interval(0, 10)[0], 0.0)
        self.assertEqual(wilson_interval(10, 10)[1], 1.0)


if __name__ == "__main__":
    unittest.main()
