"""Synthetic deterministic tests only. Real USGS test comes from separately staged CI."""
import importlib.util
from pathlib import Path
from datetime import datetime,timezone,timedelta
import unittest
import copy

spec=importlib.util.spec_from_file_location("motif018",Path(__file__).with_name("question_loop.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture(name,scale=1.0,drop=None,shock=1.0):
 start=datetime.fromisoformat(m.WINDOWS[name][0]).replace(tzinfo=timezone.utc)
 data={}
 n=192
 for key,site in m.FIXED_SITES.items():
  features=[]
  for i in range(n):
   if drop and (key,i) in drop:continue
   when=start+timedelta(hours=i)
   base=(700+((i%24)*8)+(i//24)*13+((i%11)-5)*shock*5)*scale
   q=(base if key=="mankato" else base*(.40 if key=="blue" else .25))
   features.append({"type":"Feature","properties":{
    "monitoring_location_id":site,"parameter_code":"00060",
    "unit_of_measure":"ft3/s",
    "time":when.isoformat().replace("+00:00","Z"),"value":str(q)
   }})
  data[key]={"type":"FeatureCollection","features":features,"links":[]}
 return data

class QuestionLoopTests(unittest.TestCase):
 def setUp(self):
  self.train=fixture("training")
  self.dev=fixture("development")
  self.test=fixture("new_event",scale=1.6)
  self.frozen=m.freeze(self.train,self.dev)

 def test_five_actual_rule_revisions_precede_holdout(self):
  self.assertEqual(len(self.frozen["loop"]),m.MAX_ITERATIONS)
  self.assertEqual(self.frozen["loop"][0]["version"],"QUESTION-0")
  self.assertEqual(self.frozen["loop"][-1]["version"],"QUESTION-4")
  self.assertFalse(self.frozen["heldout_data_seen_before_freeze"])
  self.assertTrue(all(h["test_outcomes_seen"]==0 for h in self.frozen["loop"]))
  self.assertFalse(self.frozen["automatic_promotion"])
  self.assertIn(self.frozen["frozen_final_question_policy"],m.QUESTIONS)
  m.verify_plan(self.frozen)

 def test_full_downstream_denominator_even_if_all_upstream_lost(self):
  drop={(key,i) for key in ("blue","sueur") for i in range(180)}
  base=m.rows(self.test,"new_event")[0]
  missing,coverage=m.rows(fixture("new_event",scale=1.6,drop=drop),"new_event")
  self.assertEqual(len(missing),len(base))
  self.assertEqual(coverage["paired_both_available"],0)
  self.assertTrue(all(x["blue_delta"] is None for x in missing))
  self.assertTrue(all(x["sueur_delta"] is None for x in missing))

 def test_missing_ask_counts_price_and_fallback(self):
  training,_=m.rows(self.train,"training")
  bank=m.fit_bank(training)
  data,_=m.rows(self.test,"new_event")
  crippled=copy.deepcopy(data)
  for row in crippled:row["blue_delta"]=None
  score=m.metrics(crippled,"ask_blue",bank,5.0,(1.0,2.0,0.0))
  baseline=m.metrics(crippled,"use_last_mankato",bank,5.0,(1.0,2.0,0.0))
  self.assertEqual(score["observed_mae_cfs"],baseline["observed_mae_cfs"])
  self.assertEqual(score["unanswered_questions"],len(crippled))
  self.assertGreater(score["declared_development_objective_cfs_equivalent"],
                     baseline["declared_development_objective_cfs_equivalent"])

 def test_conditional_question_uses_origin_only(self):
  train,_=m.rows(self.train,"training")
  bank=m.fit_bank(train)
  row=copy.deepcopy(m.rows(self.test,"new_event")[0][0])
  a=m.predict_row(row,"conditional_blue",bank)
  row["y"]=1e7
  b=m.predict_row(row,"conditional_blue",bank)
  self.assertEqual(a,b)

 def test_holdout_truth_not_used_to_change_frozen_decision(self):
  before=m.digest(self.frozen)
  original=m.challenge(self.frozen,self.test)
  different=m.challenge(self.frozen,fixture("new_event",scale=2.0))
  self.assertNotEqual(original["heldout_source_json_sha256"],
                      different["heldout_source_json_sha256"])
  self.assertEqual(m.digest(self.frozen),before)
  self.assertFalse(original["model_retrained_on_holdout"])
  self.assertEqual(original["frozen_plan_sha256"],self.frozen["plan_sha256"])
  self.assertFalse(original["automatic_promotion"])

 def test_new_question_can_follow_holdout_but_cannot_reselect_policy(self):
  out=m.challenge(self.frozen,self.test)
  question=out["posthoc_question_generation_only"]
  self.assertTrue(question["not_a_permitted_policy_change"])
  self.assertTrue(question["needs_fresh_untouched_data"])
  self.assertIn(question["best_only_after_opening_holdout"],m.QUESTIONS)
  self.assertEqual(out["selected_policy"],self.frozen["frozen_final_question_policy"])
  self.assertFalse(out["model_retrained_on_holdout"])
  self.assertIn("?",out["next_best_question"])

 def test_validation_prices_are_fixed_from_training_only(self):
  x=self.frozen["training_only_question_cost_unit_cfs_equivalent"]
  different=m.freeze(self.train,fixture("development",shock=2.0))
  self.assertEqual(x,different["training_only_question_cost_unit_cfs_equivalent"])

 def test_no_custom_unlisted_policy_or_source_window(self):
  with self.assertRaises(m.water.HOLD):m.rows(self.train,"unseen")
  a=copy.deepcopy(self.frozen)
  a["frozen_final_question_policy"]="write_external_script"
  with self.assertRaises(m.water.HOLD):m.challenge(a,self.test)

 def test_rewrite_versions_without_resigning_holds(self):
  a=copy.deepcopy(self.frozen)
  a["loop"][-1]["bounded_rule_change"]["unanswered_query_weight"]=0
  with self.assertRaises(m.water.HOLD):m.challenge(a,self.test)

 def test_signed_abuse_attempt_still_checked_against_fixed_revision_contract(self):
  a=copy.deepcopy(self.frozen)
  a["loop"][-1]["bounded_rule_change"]["unanswered_query_weight"]=0
  del a["plan_sha256"]
  a["plan_sha256"]=m.digest(a)
  with self.assertRaisesRegex(m.water.HOLD,"REVISED_HISTORY"):m.challenge(a,self.test)

 def test_sensor_units_wrong_holds(self):
  a=copy.deepcopy(self.train)
  a["blue"]["features"][0]["properties"]["unit_of_measure"]="degC"
  with self.assertRaises(m.water.HOLD):m.freeze(a,self.dev)

 def test_no_future_target_allowed_in_origin_feature(self):
  data,_=m.rows(self.train,"training")
  self.assertTrue(all(row["local_delta"] is not None for row in data))
  self.assertTrue(all("target_utc" in row and row["y"]>=0 for row in data))

if __name__=="__main__":unittest.main()
