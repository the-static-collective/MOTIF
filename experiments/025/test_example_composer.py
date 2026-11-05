import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("composer",
 Path(__file__).with_name("example_composer.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ComposableExamples(unittest.TestCase):
 def test_coffee_donation_gets_two_relevant_nonfactual_examples_and_custom(self):
  x=m.compose("Can we get free coffee donated for our fellowship event?")
  self.assertEqual(x["status"],"SHOW_TWO_EXAMPLES")
  self.assertEqual(x["domain"],"coffee_donation")
  self.assertEqual(len(x["examples"]),2)
  self.assertIn("pickup",x["examples"][0]["would_this_be_enough"])
  self.assertIn("two successive",x["examples"][1]["would_this_be_enough"])
  self.assertEqual(x["write_your_own_option"]["id"],"custom")
  self.assertTrue(all(e["is_illustrative_not_an_achieved_outcome"]
                      for e in x["examples"]))
  self.assertEqual(x["network_requests_sent"],0)
  self.assertFalse(x["human_confirmed"])

 def test_one_donor_and_recurring_donor_are_distinct_completed_condition_not_facts(self):
  text="Can we get coffee donated for a fellowship?"
  a=m.compose(text,"a")
  b=m.compose(text,"b")
  self.assertEqual(a["status"],"CONFIRM_REQUIRED")
  self.assertEqual(b["status"],"CONFIRM_REQUIRED")
  self.assertNotEqual(a["contract_id"],b["contract_id"])
  self.assertIn("quantity",a["draft_contract"]["completion_statement"])
  self.assertIn("at least two",b["draft_contract"]["completion_statement"])
  self.assertFalse(a["draft_contract"]["requested_outcome_observed"])
  self.assertFalse(b["draft_contract"]["semantics_machine_verified"])
  self.assertIsNone(a["actual_energy_joules"])

 def test_person_can_define_an_entirely_different_success_criterion(self):
  text="Can we get coffee donated for the gathering?"
  custom="A local donor confirms 80 cups for Friday and sends pickup instructions."
  x=m.compose(text,"custom",custom)
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["draft_contract"]["completion_statement"],custom)
  self.assertEqual(x["draft_contract"]["criterion_origin"],"HUMAN_TYPED_UNINTERPRETED")
  self.assertFalse(x["completion_criterion_understood_by_machine"])
  self.assertEqual(x["network_requests_sent"],0)
  self.assertFalse(x["human_text_persisted"])

 def test_changed_human_definition_requires_new_consent_not_old_authority(self):
  text="Find coffee donated for an event"
  first=m.compose(text,"a")
  changed=m.compose(text,"b",correction_of_id=first["contract_id"])
  self.assertTrue(changed["correction_replaces_prior_id"])
  old=m.compose(text,"b",confirmed=True,expected_contract_id=first["contract_id"])
  self.assertEqual(old["status"],"HOLD_CONFLICTING_HUMAN_INTENT")
  yes=m.compose(text,"b",confirmed=True,expected_contract_id=changed["contract_id"])
  self.assertEqual(yes["status"],"READY_HELD_NO_EXECUTION")
  self.assertTrue(yes["human_confirmed"])
  self.assertEqual(yes["network_requests_sent"],0)
  self.assertFalse(yes["authority"])

 def test_explicit_recurring_request_refuses_one_time_shortcut(self):
  a=m.compose("Find recurring coffee donations for every fellowship","a")
  self.assertEqual(a["status"],"HOLD_CONFLICTING_HUMAN_INTENT")
  b=m.compose("Find coffee donated only once for the next event","b")
  self.assertEqual(b["status"],"HOLD_CONFLICTING_HUMAN_INTENT")

 def test_volunteer_grocery_site_research_and_event_differ(self):
  cases={
   "Find volunteers for a church event":"volunteer_shift",
   "Match a grocery food exchange offer":"grocery_network",
   "Build our website landing page":"website",
   "Research whether this claim is true":"research",
   "Plan a community fellowship gathering":"community_event",
  }
  for txt,domain in cases.items():
   r=m.compose(txt)
   self.assertEqual(r["domain"],domain,txt)
   self.assertEqual(r["status"],"SHOW_TWO_EXAMPLES")
   self.assertNotEqual(r["examples"][0]["would_this_be_enough"],
                       r["examples"][1]["would_this_be_enough"])

 def test_multi_domain_request_uses_conservative_fallback(self):
  x=m.compose("Can you help recruit volunteers for the grocery exchange?")
  self.assertEqual(x["domain"],"generic")
  self.assertEqual(x["selection_basis"],"multiple-domains-ambiguous")
  self.assertEqual(x["unresolved_domains"],["volunteer_shift","grocery_network"])
  self.assertEqual(len(x["examples"]),2)

 def test_unknown_request_returns_useful_generic_options_without_fake_recognition(self):
  x=m.compose("Help me understand why my toaster is haunted")
  self.assertEqual(x["domain"],"generic")
  self.assertEqual(x["selection_basis"],"unknown-domain-fallback")
  self.assertEqual(len(x["examples"]),2)
  self.assertFalse(x["general_language_understanding_proven"])
  y=m.compose("Help me understand why my toaster is haunted","custom",
              "I'd consider it understood if the toaster passes three repeatable tests.")
  self.assertEqual(y["draft_contract"]["criterion_origin"],"HUMAN_TYPED_UNINTERPRETED")

 def test_river_delegates_to_source_pinned_prior_024_without_source_calls(self):
  x=m.compose("Could you check the rivers?")
  self.assertEqual(x["domain"],"river_reports")
  self.assertEqual(x["status"],"SHOW_TWO_EXAMPLES")
  self.assertEqual(len(x["examples"]),2)
  self.assertEqual(x["network_requests_sent"],0)
  a=m.compose("Could you check the rivers?","a")
  b=m.compose("Could you check the rivers?","b")
  self.assertEqual(a["status"],"CONFIRM_REQUIRED")
  self.assertEqual(a["draft_contract"]["goal"],"any_fresh")
  self.assertEqual(b["draft_contract"]["goal"],"two_named_fresh")

 def test_river_custom_missing_age_can_request_clarification_and_confirm(self):
  x=m.compose("Could you check the rivers?","custom",
    "Both Blue Earth and Le Sueur reports are enough")
  self.assertEqual(x["status"],"ASK_ONE_DECISIVE_QUESTION")
  self.assertEqual(x["next_question"]["id"],"freshness_hours")
  y=m.compose("Could you check the rivers?","custom",
    "Both Blue Earth and Le Sueur reports are enough",freshness_hours=24)
  self.assertEqual(y["status"],"CONFIRM_REQUIRED")
  self.assertEqual(y["draft_contract"]["freshness_hours"],24)
  self.assertEqual(y["draft_contract"]["goal"],"two_named_fresh")

 def test_river_custom_6hour_still_needs_human_confirmation(self):
  x=m.compose("Could you check the rivers?","custom",
     "One report from within the last 6 hours would be enough")
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["draft_contract"]["freshness_hours"],6)
  self.assertIsNone(x["actual_energy_joules"])

 def test_unsafe_original_goal_holds_no_plan(self):
  for text in ["Should I evacuate because of flood risk?",
               "Is this bridge safe to cross?",
               "I need emergency medical instructions"]:
   x=m.compose(text)
   self.assertEqual(x["status"],"HOLD_HIGH_STAKES")
   self.assertIsNone(x["examples"])
   self.assertEqual(x["network_requests_sent"],0)

 def test_arbitrary_custom_text_is_reprinted_for_local_review_not_claimed_understood(self):
  x=m.compose("Get coffee donations","custom",
      "I want 20 volunteer roasters committed by Thanksgiving.")
  self.assertEqual(x["draft_contract"]["criterion_origin"],"HUMAN_TYPED_UNINTERPRETED")
  self.assertEqual(x["draft_contract"]["verification_required"],
                   "HUMAN_MUST_REVIEW_AND_DEFINE_ACCEPTANCE_EVIDENCE")
  self.assertFalse(x["human_confirmed"])

 def test_invalid_inputs_refused(self):
  with self.assertRaises(ValueError):m.compose("a"*321)
  with self.assertRaises(ValueError):m.compose("Coffee donations",choice="HACK")
  with self.assertRaises(ValueError):m.compose("Coffee donations",choice="a",
                                               own_example="override")
  with self.assertRaises(ValueError):m.compose("Coffee donations","a",confirmed=True)
  self.assertEqual(m.compose("Coffee donations","custom")["status"],
                   "HOLD_CUSTOM_EXAMPLE_REQUIRED")

if __name__=="__main__":unittest.main()
