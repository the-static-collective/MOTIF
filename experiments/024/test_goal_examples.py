"""MOTIF-024: concrete alternatives, custom restatements, correction rights."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("goal_examples",
 Path(__file__).with_name("goal_examples.py"))
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

class CorrectTheMachine(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.witness=g.human.physical_witness()
 def ask(self,text="Could you check the rivers?",choice=None,own_example=None,**kw):
  return g.evaluate(text,choice,own_example,prior=self.witness,**kw)

 def test_show_exactly_two_readable_would_this_be_enough_examples_and_custom(self):
  x=self.ask()
  self.assertEqual(x["status"],"SHOW_TWO_EXAMPLES")
  self.assertEqual(len(x["examples"]),2)
  self.assertEqual([x["id"] for x in x["examples"]],["one","both"])
  self.assertIn("would be enough",x["examples"][0]["would_this_be_enough"])
  self.assertIn("Blue Earth",x["examples"][1]["would_this_be_enough"])
  self.assertEqual(x["write_your_own_option"]["id"],"custom")
  self.assertEqual(x["source_requests_sent"],0)
  self.assertEqual(x["llm_calls"],0)
  self.assertFalse(x["human_confirmed"])

 def test_example_one_composes_actual_contract_not_fake_source_data(self):
  x=self.ask(choice="one")
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["draft_contract"]["goal"],"any_fresh")
  self.assertEqual(x["draft_contract"]["freshness_hours"],12)
  self.assertEqual(x["prior_physical_example"]["historical_actual_request_count"],1)
  self.assertEqual(x["source_requests_sent"],0)
  self.assertFalse(x["authority"])

 def test_example_both_requires_two_named_sources(self):
  x=self.ask(choice="both")
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["draft_contract"]["goal"],"two_named_fresh")
  self.assertEqual(x["prior_physical_example"]["historical_actual_request_count"],2)

 def test_specific_original_two_cannot_be_edited_to_one_silently(self):
  x=self.ask("Need both Blue Earth and Le Sueur river reports within 12 hours",choice="one")
  self.assertEqual(x["status"],"HOLD_CONFLICTING_HUMAN_INTENT")

 def test_original_freshness_not_overridden_by_convenient_example(self):
  x=self.ask("One river report from the last 6 hours",choice="one")
  self.assertEqual(x["status"],"HOLD_CONFLICTING_HUMAN_INTENT")

 def test_custom_example_expresses_different_acceptable_freshness(self):
  c="One report from within the last 6 hours would be enough"
  x=self.ask(choice="custom",own_example=c)
  self.assertEqual(x["status"],"CONFIRM_REQUIRED")
  self.assertEqual(x["draft_contract"]["goal"],"any_fresh")
  self.assertEqual(x["draft_contract"]["freshness_hours"],6)
  self.assertIsNone(x["prior_physical_example"])
  self.assertNotIn(c,str(x))
  self.assertFalse(x["personal_question_stored"])

 def test_custom_without_cutoff_asks_age_and_preserves_example_choice(self):
  x=self.ask(choice="custom",own_example="Both Blue Earth and Le Sueur reports are enough")
  self.assertEqual(x["status"],"ASK_ONE_DECISIVE_QUESTION")
  self.assertEqual(x["next_question"]["id"],"freshness_hours")
  y=self.ask(choice="custom",
     own_example="Both Blue Earth and Le Sueur reports are enough",
     freshness_hours=24)
  self.assertEqual(y["status"],"CONFIRM_REQUIRED")
  self.assertEqual(y["draft_contract"]["freshness_hours"],24)
  self.assertEqual(y["draft_contract"]["goal"],"two_named_fresh")

 def test_custom_specific_mankato_is_not_substituted(self):
  x=self.ask(choice="custom",own_example="One reading at Mankato from the last 12 hours")
  self.assertEqual(x["status"],"HOLD_CUSTOM_EXAMPLE_NEEDS_REVIEW")

 def test_custom_informal_unsafe_or_negative_text_is_not_guessed(self):
  for custom in ("I don't need both river readings",
                 "Anything to determine whether the bridge is safe",
                 "Something that answers my question"):
   x=self.ask(choice="custom",own_example=custom)
   self.assertEqual(x["status"],"HOLD_CUSTOM_EXAMPLE_NEEDS_REVIEW")

 def test_custom_example_is_optional_but_cannot_be_blank(self):
  x=self.ask(choice="custom")
  self.assertEqual(x["status"],"HOLD_CUSTOM_EXAMPLE_REQUIRED")
  with self.assertRaises(g.HOLD):
   self.ask(choice="one",own_example="please override")

 def test_right_to_correct_changes_contract_and_revokes_old_digest(self):
  first=self.ask(choice="one")
  revised=self.ask(choice="both",correction_of_id=first["contract_id"])
  self.assertTrue(revised["correction_reviewed_only_in_this_request"])
  self.assertTrue(revised["prior_contract_replaced"])
  self.assertTrue(revised["needs_fresh_confirmation_after_correction"])
  self.assertNotEqual(first["contract_id"],revised["contract_id"])
  rejected=self.ask(choice="both",confirmed=True,
    expected_contract_id=first["contract_id"],
    correction_of_id=first["contract_id"])
  self.assertEqual(rejected["status"],"HOLD_CONFLICTING_HUMAN_INTENT")
  approved=self.ask(choice="both",confirmed=True,
    expected_contract_id=revised["contract_id"],
    correction_of_id=first["contract_id"])
  self.assertEqual(approved["status"],"READY_HELD_NO_EXECUTION")
  self.assertTrue(approved["human_confirmed"])
  self.assertEqual(approved["source_requests_sent"],0)

 def test_outside_work_including_community_fellowship_does_not_get_fake_scope(self):
  x=self.ask("Can we get free coffee for our fellowship?",choice=None)
  self.assertEqual(x["status"],"HOLD_OUTSIDE_RESEARCH_SCOPE")
  self.assertIsNone(x["examples"])

 def test_hazard_request_does_not_get_false_safe_answer(self):
  x=self.ask("Should I evacuate because of flood risk?",choice=None)
  self.assertEqual(x["status"],"HOLD_HIGH_STAKES")

 def test_invented_cost_and_energy_remain_unknown(self):
  x=self.ask(choice="one")
  self.assertIsNone(x["actual_energy_joules"])
  self.assertEqual(x["credits_used"],0)
  self.assertFalse(x["automatic_model_promotion"])
  self.assertEqual(x["source_requests_sent"],0)

 def test_input_and_confirmation_are_bounded(self):
  with self.assertRaises(g.HOLD):self.ask("river",choice="invented")
  with self.assertRaises(g.HOLD):self.ask("river",choice="custom",own_example="a"*321)
  self.assertEqual(self.ask("river",choice="one",freshness_hours=6)["status"],
                   "HOLD_CONFLICTING_HUMAN_INTENT")
  with self.assertRaises(g.HOLD):self.ask("river",choice="both",confirmed=True,expected_contract_id="a")
  with self.assertRaises(g.HOLD):self.ask("river",choice="one",own_example="secret")

if __name__=="__main__":unittest.main()
