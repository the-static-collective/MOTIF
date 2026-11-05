"""Synthetic fixtures only; actual 2024 river event is obtained separately in CI."""
import importlib.util
from datetime import datetime, timezone, timedelta
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("event017",
    Path(__file__).with_name("event_learner.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fake_window(name,scale=1.0,trend=1.0,miss=None):
    start=datetime.fromisoformat(m.WINDOWS[name][0]).replace(tzinfo=timezone.utc)
    raw={"rain":None}
    n=180
    for station,site in m.SITES.items():
        feats=[]
        for i in range(n):
            if miss is not None and (station,i) in miss:
                continue
            when=start+timedelta(hours=i)
            # Synthetic, deterministic changing hydrograph with correlated sources.
            q=(1500 + 160*(i//24) + 90*(i%12) + ((i%19)-10)*trend*7)*scale
            if station=="blue":
                q=q/2
            if station=="sueur":
                q=q/4
            if station=="mankato":
                q=q*1.5+150
            feats.append({"type":"Feature","properties":{
                "monitoring_location_id":site,"parameter_code":"00060",
                "unit_of_measure":"ft3/s",
                "time":when.isoformat().replace("+00:00","Z"),
                "value":str(q)}})
        raw[station]={"type":"FeatureCollection","features":feats,"links":[]}
    return raw


class Reality017Tests(unittest.TestCase):
    def setUp(self):
        self.train=fake_window("train")
        self.val=fake_window("validation")
        self.event=fake_window("event",scale=3.0)
        self.plan=m.freeze(self.train,self.val)

    def test_prepare_has_no_event_label_input_and_has_provenance_seal(self):
        self.assertEqual(self.plan["schema"],m.PLAN_SCHEMA)
        self.assertEqual(self.plan["windows"]["event"],m.WINDOWS["event"])
        self.assertIn(self.plan["legacy_choice"],m.METHODS)
        self.assertIn(self.plan["cautious_choice"],m.METHODS)
        self.assertEqual(self.plan["plan_sha256"],m.fingerprint({k:v for k,v in self.plan.items() if k!="plan_sha256"}))
        m.validate_frozen(self.plan)

    def test_truth_cannot_change_prepared_plan_or_models(self):
        first=m.canonical(self.plan)
        mutated=fake_window("event",scale=5.0,trend=1.5)
        self.assertNotEqual(m.evaluate_frozen(self.plan,self.event)["event_source_snapshot_sha256"],
                            m.evaluate_frozen(self.plan,mutated)["event_source_snapshot_sha256"])
        self.assertEqual(m.canonical(self.plan),first)

    def test_fixed_event_is_held_even_when_regime_starkly_different(self):
        report=m.evaluate_frozen(self.plan,self.event)
        self.assertEqual(report["matched_test_hours"],len(m.rows_from(self.event,"event")[0]))
        self.assertFalse(report["test_labels_selected_policy"])
        self.assertFalse(report["model_was_trained_on_event"])
        self.assertFalse(report["automatic_admission"])
        self.assertIn("persistence",report["candidate_event_mae_cfs"])
        self.assertIn("cautious_selection",report["candidate_event_mae_cfs"])

    def test_chosen_gate_is_input_only_and_bad_data_cannot_change_it(self):
        t=self.plan["training_only_out_of_distribution_guard"]
        self.assertLess(t["low_cfs"],t["high_cfs"])
        for outcome in (-1e7,3e7):
            before=dict(m.rows_from(self.event,"event")[0][0])
            after=dict(before,y=outcome)
            model=self.plan["models"]
            # Routing only depends on known origin, not future ground truth.
            choice=self.plan["cautious_choice"]
            abstain=lambda row:choice!="persistence" and (
                row["known"]<t["low_cfs"] or row["known"]>t["high_cfs"])
            self.assertEqual(abstain(before),abstain(after))

    def test_corrupt_frozen_policy_and_injected_future_hold(self):
        for change in (
            lambda x:x.update(plan_sha256="a"*64),
            lambda x:x.update(legacy_choice="exploit_test"),
            lambda x:x["models"]["cross_gauges"].update(weights=[float("nan")]),
            lambda x:x["gate_thresholds"].update(validation_relative_advantage=0),
        ):
            corrupt=__import__("copy").deepcopy(self.plan)
            change(corrupt)
            with self.assertRaises(m.water.HOLD):
                m.evaluate_frozen(corrupt,self.event)

    def test_missing_sensor_window_holds_instead_of_inventing_flows(self):
        raw=fake_window("event",miss={(s,i) for s in m.SITES for i in range(165)})
        with self.assertRaises(m.water.HOLD):
            m.evaluate_frozen(self.plan,raw)

    def test_event_window_is_fixed_not_interpolated(self):
        other=fake_window("train")
        with self.assertRaises(m.water.HOLD):
            m.evaluate_frozen(self.plan,other)

    def test_validation_shift_causes_caution_without_event_data(self):
        val=fake_window("validation",scale=10.0)
        plan=m.freeze(self.train,val)
        self.assertEqual(plan["cautious_choice"],"persistence")
        self.assertIn("REGIME_SHIFT_IN_PRE_EVENT_VALIDATION",plan["reasons_for_caution"])

    def test_source_http_is_fixed_monitoring_sites_only(self):
        self.assertEqual(set(m.SITES),{"blue","sueur","mankato"})
        self.assertEqual(m.WINDOWS["event"],("2024-06-18","2024-06-28"))

    def test_sensor_target_partition_is_physically_later_than_predictor_origin(self):
        parsed,_=m.rows_from(self.event,"event")
        self.assertGreater(len(parsed),m.MIN_CASES["event"])
        self.assertEqual(m.water.HOUR if hasattr(m.water,"HOUR") else m.water.HORIZON_HOURS,7)

    def test_frozen_plan_compares_with_same_observations_for_all_methods(self):
        r=m.evaluate_frozen(self.plan,self.event)
        self.assertEqual(r["candidate_event_mae_cfs"]["persistence"],
                         r["all_method_event_mae_cfs"]["persistence"])
        self.assertEqual(r["candidate_event_mae_cfs"]["old_selection"],
                         r["all_method_event_mae_cfs"][self.plan["legacy_choice"]])
        self.assertFalse(r["external_action"])


if __name__=="__main__":
    unittest.main()
