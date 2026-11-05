"""Adversarial offline fixtures. Real source queries happen in separate CI job."""
import importlib.util
from pathlib import Path
from datetime import datetime,timezone,timedelta
from copy import deepcopy
import unittest

spec=importlib.util.spec_from_file_location("q019",Path(__file__).with_name("availability_question.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture(window,blue_drop=None,sueur_drop=None,scale=1):
    beginning=datetime.fromisoformat(m.WINDOWS[window][0]).replace(tzinfo=timezone.utc)
    source={}
    for station,site in m.SITES.items():
        features=[]
        for i in range(210):
            if station=="blue" and blue_drop and i in blue_drop:continue
            if station=="sueur" and sueur_drop and i in sueur_drop:continue
            dt=beginning+timedelta(hours=i)
            q=((1200+(i%25)*18+(i//25)*13+(i%11)*8)*scale)
            if station=="blue":q*=0.40
            elif station=="sueur":q*=0.21
            features.append({"type":"Feature","properties":{
              "monitoring_location_id":site,"parameter_code":"00060",
              "unit_of_measure":"ft3/s",
              "time":dt.isoformat().replace("+00:00","Z"),"value":str(q)
            }})
        source[station]={"type":"FeatureCollection","features":features,"links":[]}
    return source

class TestedQuestionKinds(unittest.TestCase):
    def setUp(self):
        self.train=fixture("train")
        self.dev=fixture("develop",blue_drop=set(range(70,110)))
        self.test=fixture("holdout",scale=1.3,blue_drop=set(range(30,120)))
        self.plan=m.develop(self.train,self.dev)

    def test_source_window_and_six_question_type_revisions(self):
        self.assertEqual(len(self.plan["stages"]),6)
        self.assertEqual(self.plan["stages"][4]["new_question_kind_introduced"],"source_health")
        self.assertEqual(self.plan["stages"][5]["new_question_kind_introduced"],"false_health_cost")
        self.assertEqual(self.plan["windows"]["holdout"],m.WINDOWS["holdout"])
        self.assertTrue(self.plan["holdout_was_not_read"])
        self.assertFalse(self.plan["auto_modify_source"])
        m.verify(self.plan)

    def test_complete_downstream_denominator_survives_every_upstream_outage(self):
        raw=fixture("holdout",blue_drop=set(range(210)),sueur_drop=set(range(210)))
        rows,coverage=m.make_rows(raw,"holdout")
        baseline=m.make_rows(fixture("holdout"),"holdout")[0]
        self.assertEqual(len(rows),len(baseline))
        self.assertEqual(coverage["complete_both_hours"],0)
        self.assertTrue(all(x["sueur_delta"] is None and x["blue_delta"] is None for x in rows))

    def test_health_uses_only_past_not_target_or_origin_future(self):
        rows,_=m.make_rows(self.test,"holdout")
        row=deepcopy(rows[0])
        for kind in m.HEALTH_LENGTH:
            before=m.step_action(row,kind)
            row["y"]=1e8
            self.assertEqual(before,m.step_action(row,kind))

    def test_realistic_health_can_be_wrong_and_is_not_an_oracle(self):
        rows,_=m.make_rows(self.test,"holdout")
        n=sum(m.step_action(r,"health_last3")[-1] for r in rows)
        self.assertTrue(isinstance(n,int))
        self.assertEqual(m.HEALTH_LENGTH["health_last3"],(3,2))
        self.assertTrue(all("blue_historic_present_last3" in r for r in rows))

    def test_graceful_both_falls_back_to_sueur_not_default_persistence(self):
        rows,_=m.make_rows(self.test,"holdout")
        damaged=next(r for r in rows if r["sueur_delta"] is not None and r["blue_delta"] is None)
        prediction=m.simulate_one(damaged,"both_graceful",self.plan["bank"])
        self.assertEqual(prediction["uses_model"],"sueur")
        self.assertEqual(prediction["requests"],2)
        self.assertEqual(prediction["silent"],1)

    def test_probe_credits_paid_even_when_health_false(self):
        rows,_=m.make_rows(self.test,"holdout")
        damaged=next(r for r in rows if r["blue_delta"] is None)
        result=m.simulate_one(damaged,"health_last3",self.plan["bank"])
        self.assertAlmostEqual(result["probe_credit"],.2)
        self.assertIn(result["requests"],(1,2))

    def test_rewriting_selected_policy_and_resigning_does_not_defeat_contract(self):
        adulterated=deepcopy(self.plan)
        adulterated["stages"][5]["predeclared_utility_weights"]["missing"]=0
        del adulterated["plan_sha256"]
        adulterated["plan_sha256"]=m.digest(adulterated)
        with self.assertRaisesRegex(m.HOLD,"FROZEN_REVISION_CONTRACT"):
            m.test_frozen(adulterated,self.test)

    def test_holdout_truth_cannot_change_frozen_policy(self):
        before=m.digest(self.plan)
        report=m.test_frozen(self.plan,self.test)
        altered=fixture("holdout",scale=2.7)
        different=m.test_frozen(self.plan,altered)
        self.assertEqual(m.digest(self.plan),before)
        self.assertEqual(report["frozen_selection"],different["frozen_selection"])
        self.assertNotEqual(report["holdout_source_response_sha256"],
                            different["holdout_source_response_sha256"])
        self.assertFalse(report["observed_future_labels_used_to_modify_policy"])
        self.assertFalse(report["automatic_admission"])

    def test_rejects_wrong_source_units_and_identity(self):
        bad=deepcopy(self.dev)
        bad["blue"]["features"][0]["properties"]["unit_of_measure"]="degC"
        with self.assertRaises(m.water.HOLD):
            m.develop(self.train,bad)

    def test_failed_sensor_is_never_imputed_as_no_rain_or_no_flow(self):
        data=fixture("holdout",blue_drop=set(range(210)))
        cases,_=m.make_rows(data,"holdout")
        self.assertTrue(all(row["blue_delta"] is None for row in cases))

    def test_all_candidates_share_denominator_and_query_costs(self):
        report=m.test_frozen(self.plan,self.test)
        self.assertEqual(len(report["all_declared_policy_results_POSTHOC_DO_NOT_SELECT"]),7)
        total=report["downstream_complete_case_population"]["complete_downstream_hours"]
        self.assertTrue(all(v["count"]==total for v in
                            report["all_declared_policy_results_POSTHOC_DO_NOT_SELECT"].values()))
        self.assertFalse(report["sensor_health_really_queried_at_issue_time"])

if __name__=="__main__":
    unittest.main()
