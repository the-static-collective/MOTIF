import importlib.util
from copy import deepcopy
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("m22",Path(__file__).with_name("cost_of_knowing.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PhysicalCostOfKnowing(unittest.TestCase):
 def setUp(self):
  self.source=m.load()
  self.result=m.inspect(self.source)

 def test_real_live_source_reports_two_goal_satisfactions_no_credits(self):
  r=self.result
  self.assertEqual(r["schema"],"motif.cost-of-knowing/v1")
  self.assertEqual(r["total_actual_public_gets"],9)
  self.assertEqual(r["total_actual_http_body_bytes"],2463224)
  self.assertTrue(r["resource_units_are_not_fictional_credit_prices"])
  self.assertIsNone(r["measured_electrical_energy_joules"])
  self.assertFalse(r["automatic_promotion"])
  self.assertFalse(r["dispatch"])
  self.assertEqual(r["hypothesis_disposition"],
    "HELD_REAL_NARROW_GOAL_COMPLETION_WITH_LESS_OBSERVED_RESOURCE_WORK")
  self.assertEqual(r["goal_aware_vs_exhaustive_actual_resources"]["any_fresh"]["optimized_real_requests"],1)
  self.assertEqual(r["goal_aware_vs_exhaustive_actual_resources"]["two_named_fresh"]["optimized_real_requests"],2)

 def test_goal_contract_necessary_second_question_is_preserved(self):
  trace=self.result["inquiry_steps_composed_from_source_receipts"]
  first=trace["two_named_fresh/goal_aware"][0]
  second=trace["two_named_fresh/goal_aware"][1]
  self.assertFalse(first["goal_was_satisfied"])
  self.assertTrue(first["is_another_question_capable_of_completing_original_goal"])
  self.assertEqual(first["next_decision"],"ASK_NEXT_POSSIBLY_USEFUL_SOURCE")
  self.assertEqual(second["next_decision"],"STOP_GOAL_MET")

 def test_question_url_full_utc_and_checksum_verified(self):
  for trial in self.source["actually_executed_trials"]:
   for step in trial["actual_steps"]:
    self.assertIn("T",m.validate_source_url(step["public_request_url"],step["actual_site_requested"]))
  self.assertEqual(m.gitblob(m.FIXED_SOURCE.read_bytes()),m.GHOT_GIT_BLOB)

 def test_false_goals_and_energy_promotion_do_not_pass(self):
  cases=[
    lambda x:x.update(actual_energy_joules=0),
    lambda x:x.update(automatic_model_promotion=True),
    lambda x:x["actually_executed_trials"][0].update(task_contract_completed=False),
    lambda x:x["actually_executed_trials"][3]["actual_steps"][0].update(
       original_goal_satisfied_after_this_step=True),
    lambda x:x["actually_executed_trials"][1]["per_request_receipts"][0].update(
       body_bytes_received=0),
    lambda x:x["actually_executed_trials"][1]["actual_steps"][0].update(
       public_request_url="http://127.0.0.1/token"),
  ]
  for change in cases:
   x=deepcopy(self.source);change(x)
   with self.assertRaises(m.HOLD):m.inspect(x)

 def test_observed_comparison_does_not_overclaim_causality(self):
  comp=self.result["goal_aware_vs_exhaustive_actual_resources"]
  self.assertTrue(all(v["contract_completed_in_both_actual_trials"] for v in comp.values()))
  self.assertTrue(all(v["goal_aware_observed_non_worse_on_all_measured_dimensions"] for v in comp.values()))
  self.assertTrue(all(v["matched_contemporaneous_randomized_trial"] is False for v in comp.values()))
  self.assertTrue(all(v["causal_performance_gain_demonstrated"] is False for v in comp.values()))
  self.assertEqual(self.result["no_autonomous_code_revision"],True)

if __name__=="__main__":unittest.main()
