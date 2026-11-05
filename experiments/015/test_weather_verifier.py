"""Synthetic *test-only* fixtures; not presented as weather measurements."""
import unittest
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("verifier", Path(__file__).with_name("weather_verifier.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def fixture(count=60, bias=2.0, start=None):
    start = start or datetime(2026, 11, 1, tzinfo=timezone.utc)
    times, fc, reports = [], [], []
    for i in range(count):
        t = start + timedelta(hours=i)
        observed = float((i % 10) - 4)
        times.append(t.strftime("%Y-%m-%dT%H:%M"))
        fc.append(observed - bias)
        reports.append({"properties": {
            "timestamp": (t - timedelta(minutes=5)).isoformat().replace("+00:00","Z"),
            "temperature": {"unitCode":"wmoUnit:degC","value":observed}
        }})
    f = {"timezone":"GMT","hourly_units":{"temperature_2m_previous_day1":"°C"},
         "hourly":{"time":times,"temperature_2m_previous_day1":fc}}
    o = {"features":reports}
    return f, o


class WeatherWitnessTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 6, tzinfo=timezone.utc)

    def test_heldout_bias_correction_improves_synthetic_known_bias(self):
        result = v.evaluate(*fixture(), self.now)
        self.assertEqual(result["matched_count"],60)
        self.assertEqual(result["train_count"],40)
        self.assertEqual(result["test_count"],20)
        self.assertEqual(result["holdout_mae_c"]["raw_previous_day1"],2)
        self.assertEqual(result["holdout_mae_c"]["train_bias_adjusted"],0)
        self.assertEqual(result["improvement_disposition"],"HELD_FOR_INDEPENDENT_VALIDATION")
        self.assertFalse(result["automatic_promotion"])

    def test_no_benefit_is_not_promoted(self):
        result = v.evaluate(*fixture(bias=0), self.now)
        self.assertEqual(result["improvement_disposition"],"HOLD_NO_MEASURED_IMPROVEMENT")
        self.assertEqual(result["difference_raw_minus_adjusted_mae_c"],0)

    def test_bad_units_hold(self):
        f,o = fixture()
        f["hourly_units"]["temperature_2m_previous_day1"]="°F"
        with self.assertRaisesRegex(v.HOLD,"units"):
            v.evaluate(f,o,self.now)

    def test_missing_mismatched_data_hold(self):
        f,o = fixture()
        o["features"] = o["features"][:12]
        with self.assertRaisesRegex(v.HOLD,"insufficient"):
            v.evaluate(f,o,self.now)

    def test_no_future_verification_and_no_duplicate_sensor_witnesses(self):
        f,o=fixture()
        self.assertEqual(v.evaluate(f,o,self.now)["matched_count"],60)
        f["hourly"]["time"] = [(datetime(2026,11,8,tzinfo=timezone.utc) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(60)]
        with self.assertRaisesRegex(v.HOLD,"insufficient"):
            v.evaluate(f,o,self.now)

    def test_conflicted_measurement_hold(self):
        f,o=fixture()
        shadow={"properties":dict(o["features"][0]["properties"])}
        shadow["properties"]["temperature"]={"unitCode":"wmoUnit:degC","value":99.0}
        o["features"].append(shadow)
        with self.assertRaises(v.HOLD):
            v.evaluate(f,o,self.now)

    def test_missing_timezone_holds_and_repeated_archive_hour_holds(self):
        f,o=fixture()
        o["features"][0]["properties"]["timestamp"]="2026-11-01T00:00"
        with self.assertRaisesRegex(v.HOLD,"timezone"):
            v.evaluate(f,o,self.now)
        f,o=fixture()
        f["hourly"]["time"][1]=f["hourly"]["time"][0]
        with self.assertRaisesRegex(v.HOLD,"duplicate"):
            v.evaluate(f,o,self.now)

    def test_source_allowlist(self):
        with self.assertRaisesRegex(v.HOLD,"allowlist"):
            v.get_json("http://evil.example/")

    def test_retrospective_only_not_real_time_claim(self):
        output=v.evaluate(*fixture(),self.now)
        self.assertEqual(output["status"],"RETROSPECTIVE_OBSERVATIONAL_COMPARISON")
        self.assertFalse(output["authority"])
        self.assertTrue(any("retrospectively" in x for x in output["limitations"]))


if __name__ == "__main__":
    unittest.main()
