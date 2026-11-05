"""Adversarial synthetic person-goal examples; NOT a human-participant study."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("human_goal",Path(__file__).with_name("human_goal.py"))
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

class HumanGoalHandshake(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.physical=g.physical_witness()

 def assess(self,text,answers=None,**kw):
  return g.evaluate(text,answers,prior=self.physical,**kw)

 def test_ambiguous_request_asks_one_decisive_question(self):
  x=self.assess("Can you check the rivers?")
  self.assertEqual(x["status"],"ASK_ONE_DECISIVE_QUESTION")
  self.assertEqual(x["next_question"]["id"],"evidence_scope")
  self.assertEqual(x["historical_resource_examples"]["any_fresh"]["historical_actual_request_count"],1)
  self.assertEqual(x["historical_resource_examples"]["two_named_fresh"]["historical_actual_request_count"],2)
  self.assertEqual(x["source_requests_sent"],0)
  self.assertEqual(x["llm_calls"],0)

 def test_both_named_requires_both_and_no_early_one_source_stop(self):
  x=self.assess("Get both Blue Earth and Le Sueur river readings within 12 hours.")
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["selected_goal"],"two_named_fresh")
  self.assertEqual(x["draft_contract"]["completion_rule"],"BOTH_NAMED_REPORTED_SOURCES")
  self.assertEqual(len(x["draft_contract"]["read_only_public_gauge_ids"]),2)
  self.assertEqual(x["earlier_matching_12h_example"]["historical_actual_request_count"],2)

 def test_explicit_single_report_is_not_overqueried(self):
  x=self.assess("One river discharge report from the last 12 hours is enough.")
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["selected_goal"],"any_fresh")
  self.assertEqual(x["draft_contract"]["completion_rule"],"ANY_ONE_REPORTED_SOURCE")

 def test_missing_freshness_is_not_filled_by_fabricated_default(self):
  x=self.assess("One recent river flow report")
  self.assertEqual(x["next_question"]["id"],"freshness_hours")
  y=self.assess("One recent river flow report",{"freshness_hours":6})
  self.assertEqual(y["status"],"CONFIRM_REQUIRED")
  self.assertIsNone(y["earlier_matching_12h_example"])

 def test_two_clarifications_go_in_order_without_repeating_earlier_answer(self):
  text="Please check the river data."
  a=self.assess(text)
  self.assertEqual(a["next_question"]["id"],"evidence_scope")
  b=self.assess(text,{"evidence_scope":"two_named_fresh"})
  self.assertEqual(b["next_question"]["id"],"freshness_hours")
  c=self.assess(text,{"evidence_scope":"two_named_fresh","freshness_hours":12})
  self.assertEqual(c["status"],"CONFIRM_REQUIRED")

 def test_exact_confirm_digest_allows_only_held_plan_not_network(self):
  text="Need both Blue Earth and Le Sueur river reports within 12 hours."
  draft=self.assess(text)
  x=self.assess(text,confirmed=True,expected_contract_id=draft["contract_id"])
  self.assertEqual(x["status"],"READY_HELD_NO_EXECUTION")
  self.assertTrue(x["human_confirmed"])
  self.assertEqual(x["source_requests_sent"],0)
  self.assertFalse(x["physical_action"])
  self.assertFalse(x["authority"])

 def test_false_or_stale_confirmation_fails_closed(self):
  text="One recent river report"
  a=self.assess(text,{"freshness_hours":12})
  b=self.assess(text,{"freshness_hours":6},confirmed=True,
                expected_contract_id=a["contract_id"])
  self.assertEqual(b["status"],"HOLD_CONFLICTING_HUMAN_INTENT")
  c=self.assess(text,{"freshness_hours":12},confirmed=True,
                expected_contract_id="f"*64)
  self.assertEqual(c["status"],"HOLD_CONFLICTING_HUMAN_INTENT")

 def test_safety_request_never_gets_hydrologic_safety_answer(self):
  for text in ("Is this bridge safe to cross?",
               "Should I evacuate because of flood risk?",
               "Is the river safe to drive across?"):
   x=self.assess(text)
   self.assertEqual(x["status"],"HOLD_HIGH_STAKES")
   self.assertEqual(x["source_requests_sent"],0)

 def test_nonriver_human_need_does_not_get_river_plan(self):
  for text in ("Can we get free coffee donated for the fellowship event?",
               "Help someone volunteer for our grocery project"):
   x=self.assess(text)
   self.assertEqual(x["status"],"HOLD_OUTSIDE_RESEARCH_SCOPE")

 def test_named_specific_source_not_silently_substituted(self):
  x=self.assess("Please read the Mankato river gauge")
  self.assertEqual(x["status"],"HOLD_UNSUPPORTED_SOURCE_SPECIFICATION")

 def test_specific_explicit_goal_cannot_be_overridden(self):
  text="I need both Blue Earth and Le Sueur river observations"
  x=self.assess(text,{"evidence_scope":"any_fresh","freshness_hours":12})
  self.assertEqual(x["status"],"HOLD_CONFLICTING_HUMAN_INTENT")

 def test_specific_original_freshness_cannot_be_overridden(self):
  text="I need one river reading from the last 12 hours"
  x=self.assess(text,{"freshness_hours":24})
  self.assertEqual(x["status"],"HOLD_CONFLICTING_HUMAN_INTENT")

 def test_unsupported_recency_fails_closed(self):
  x=self.assess("Need one river reading within 3 hours")
  self.assertEqual(x["status"],"HOLD_UNSUPPORTED_FRESHNESS")

 def test_unknown_clarification_field_rejected(self):
  with self.assertRaises(g.HOLD):
   self.assess("River data",{"execute":"right now"})
  with self.assertRaises(g.HOLD):
   self.assess("River data",{"evidence_scope":"safety_decision"})

 def test_nontext_cannot_trigger_personal_query_persistence(self):
  with self.assertRaises(g.HOLD):self.assess(None)
  t="PRIVATE_USER_MARKER_4594"
  x=self.assess("Help me with "+t)
  self.assertNotIn(t,str(x))
  self.assertFalse(x["personal_question_stored"])

 def test_physical_evidence_is_source_pinned_and_not_a_predictive_cost(self):
  self.assertTrue(self.physical["any_fresh"]["not_a_future_cost_prediction"])
  self.assertGreater(self.physical["two_named_fresh"]["historical_actual_http_body_bytes"],
                     self.physical["any_fresh"]["historical_actual_http_body_bytes"])

 def test_no_cost_conversion_in_held_card(self):
  x=self.assess("One river reading from last 12 hours")
  self.assertIsNone(x["estimated_actual_future_requests"])
  self.assertIsNone(x["actual_energy_joules"])
  self.assertEqual(x["credits_used"],0)
  self.assertFalse(x["automatic_promotion"])

if __name__=="__main__":unittest.main()
