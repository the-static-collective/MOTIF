"""MOTIF-016 fixtures are synthetic, never misrepresented as river observations."""
import importlib.util
from datetime import datetime, timezone, timedelta
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("living_watershed",
    Path(__file__).with_name("watershed.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture(n=240, include_rain=True, effects=True):
    start=datetime(2026,10,1,tzinfo=timezone.utc)
    entries={}
    for key,site in m.SITES.items():
        samples=[]
        for i in range(n):
            when=start+timedelta(hours=i)
            if key=="blue":
                q=600 + (i%40)*10 + (i//40)*7
            elif key=="sueur":
                q=260 + (i%30)*4 + (i//30)*4
            else:
                # A deterministic synthetic downstream response to earlier
                # tributary changes; it is NOT a physical hydrologic equation.
                q=2800 + (i%40)*9 + (i%30)*3 + (i//40)*5
                if effects:
                    q+=((i-7)%16)*11
            samples.append({"type":"Feature","properties":{
                "monitoring_location_id":site,"parameter_code":"00060",
                "unit_of_measure":"ft3/s","time":when.isoformat().replace("+00:00","Z"),
                "value":str(q)}})
        entries[key]={"type":"FeatureCollection","features":samples,"links":[]}
    rain={"timezone":"GMT","hourly_units":{"precipitation":"mm"},
          "hourly":{"time":[(start+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M")
                             for i in range(n)],
                    "precipitation":[float(i%7)/10 for i in range(n)]}}
    entries["rain"]=rain if include_rain else None
    return entries


class TestWatershed(unittest.TestCase):
    def test_observations_not_predictions_and_no_authority(self):
        r=m.evaluate(fixture(),now=datetime(2026,11,1,tzinfo=timezone.utc))
        self.assertGreaterEqual(r["matched_complete_hours"],m.MIN_ROWS)
        self.assertEqual(sum(r["partitions"].values()),r["matched_complete_hours"])
        self.assertFalse(r["automatic_promotion"])
        self.assertFalse(r["authority"])
        self.assertEqual(r["provenance"]["USGS_public_site_ids"],m.SITES)
        self.assertIn(r["selected_on_validation"],m.CANDIDATES)
        self.assertIn("persistence",r["holdout_mae_cfs"])
        self.assertGreater(r["partitions"]["test"],18)

    def test_missing_rain_not_zero_and_preserves_gauge_comparison(self):
        result=m.evaluate(fixture(include_rain=False))
        self.assertNotIn("rain_context",result["holdout_mae_cfs"])
        self.assertEqual(result["provenance"]["rain_type"],"UNAVAILABLE")
        self.assertFalse(result["real_world_effect"])

    def test_input_wrong_site_parameter_and_unit_holds(self):
        for key,value in (("monitoring_location_id","USGS-INVALID"),
                          ("parameter_code","00065"),
                          ("unit_of_measure","degC")):
            source=fixture()
            source["blue"]["features"][0]["properties"][key]=value
            with self.assertRaises(m.HOLD):
                m.evaluate(source)

    def test_future_leakage_guard_and_missingness(self):
        source=fixture(n=20)
        with self.assertRaises(m.HOLD):
            m.evaluate(source)
        source=fixture()
        future=datetime(2026,10,1,tzinfo=timezone.utc)
        with self.assertRaisesRegex(m.HOLD,"INSUFFICIENT"):
            m.evaluate(source,now=future)

    def test_duplicate_conflicting_water_and_rain_report_hold(self):
        source=fixture()
        row=source["blue"]["features"][0].copy()
        row["properties"]=dict(row["properties"],value="99999")
        source["blue"]["features"].append(row)
        with self.assertRaisesRegex(m.HOLD,"CONFLICTING"):
            m.evaluate(source)

        source=fixture()
        source["rain"]["hourly"]["time"][1]=source["rain"]["hourly"]["time"][0]
        with self.assertRaisesRegex(m.HOLD,"DUPLICATE_RAIN"):
            m.evaluate(source)

    def test_incomplete_gauges_cannot_be_called_usable(self):
        source=fixture()
        source["blue"]["features"]=source["blue"]["features"][:45]
        with self.assertRaisesRegex(m.HOLD,"INSUFFICIENT"):
            m.evaluate(source)

    def test_retrospective_estimate_never_recast_as_live_rain_sensor(self):
        source=fixture()
        result=m.evaluate(source)
        self.assertIn("NOT_RAIN_GAUGE",result["provenance"]["rain_type"])
        self.assertIn("telemetry",str(result["limitations"]))
        self.assertFalse(result["independent_outcome_verified"])

    def test_015_card_is_parallel_and_not_model_truth(self):
        witness={"schema":"motif.reality-iron-weather/v1",
            "status":"RETROSPECTIVE_OBSERVATIONAL_COMPARISON",
            "station":"KMKT","real_world_effect":False,
            "provenance":{"source_snapshots_sha256":{"forecast":"a"*64,"observations":"b"*64}},
            "improvement_disposition":"HOLD_NO_MEASURED_IMPROVEMENT"}
        result=m.evaluate(fixture(),weather_witness=witness)
        self.assertEqual(result["prior_weather_015"]["weather_015_disposition"],
                         "HOLD_NO_MEASURED_IMPROVEMENT")
        self.assertEqual(result["prior_weather_015"]["relation"],
                         "PARALLEL_EVIDENCE_NOT_A_PREDICTOR_OR_GROUND_TRUTH")
        witness["real_world_effect"]=True
        with self.assertRaisesRegex(m.HOLD,"INVALID_PRIOR"):
            m.evaluate(fixture(),weather_witness=witness)

    def test_pinned_http_hosts(self):
        with self.assertRaisesRegex(m.HOLD,"OUTSIDE"):
            m.request_json("http://example.org/evil")

    def test_no_test_leakage_training_rows_only(self):
        xs=[{"known":10,"y":13,"local_delta":i} for i in range(1,20)]
        fit=m.fit_ridge(xs[:10],("local_delta",))
        change=xs[10:].copy()
        change=[dict(x,y=1e6) for x in change]
        self.assertEqual(fit,m.fit_ridge(xs[:10],("local_delta",)))
        self.assertAlmostEqual(m.predict(change[0],fit),m.predict(xs[10],fit))


if __name__=="__main__":
    unittest.main()
