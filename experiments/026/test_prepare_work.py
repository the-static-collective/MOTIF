import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location("goalwork",
 Path(__file__).with_name("prepare_work.py"))
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
COFFEE="Can we get free coffee donated for our fellowship event?"
def req(text=COFFEE,choice="a",own_example=None):
 card=g.composer.compose(text,choice,own_example)
 return {"text":text,"choice":choice,
         **({"own_example":own_example} if own_example is not None else {}),
         "expected_contract_id":card["contract_id"],
         "consent":True,"action":g.ACTION}
class GoalToWork(unittest.TestCase):
 def test_zero_action_when_no_separate_local_permission(self):
  r=req();r["consent"]=False
  x=g.prepare(r)
  self.assertEqual(x["status"],"HOLD_NO_SEPARATE_LOCAL_WORK_PERMISSION")
  self.assertFalse(x["generated"])
  self.assertIsNone(x["work_spec"])
 def test_real_source_owned_coffee_spec_after_exact_recomputed_confirmation(self):
  r=g.prepare(req())
  self.assertEqual(r["status"],"LOCAL_WORK_SPEC_PREPARED_NOT_EXECUTED")
  s=r["work_spec"]
  self.assertEqual(s["domain"],"coffee_donation")
  self.assertEqual(s["allowed_outputs"],
    ["checklist","csv_tracker","unsent_message","html_workpage"])
  self.assertIn("pickup",s["message_draft"])
  self.assertIn("evidence_of_commitment",s["tracking_fields"])
  self.assertFalse(s["external_delivery_permitted"])
  self.assertFalse(r["external_effect"])
  self.assertFalse(r["source_code_modified"])
  self.assertIsNone(r["actual_energy_joules"])
 def test_changed_goal_digest_cannot_produce_packet(self):
  old=req()
  later=dict(old,choice="b")
  self.assertEqual(g.prepare(later)["status"],"HOLD_UNCONFIRMED_OR_CHANGED_GOAL")
  changed=req(choice="b")
  self.assertNotEqual(changed["expected_contract_id"],old["expected_contract_id"])
  self.assertEqual(g.prepare(changed)["status"],"LOCAL_WORK_SPEC_PREPARED_NOT_EXECUTED")
 def test_arbitrary_human_criterion_is_not_declared_machine_verified(self):
  t="Can we get coffee donated?"
  own="I would consider it done when 80 cups are promised for Friday."
  x=g.prepare(req(text=t,choice="custom",own_example=own))
  self.assertEqual(x["work_spec"]["goal_contract"]["completion_statement"],own)
  self.assertEqual(x["work_spec"]["goal_contract"]["criterion_origin"],
                   "HUMAN_TYPED_UNINTERPRETED")
  self.assertTrue(x["work_spec"]["user_content_is_unverified"])
 def test_other_domains_are_specific_and_does_not_execute(self):
  cases={"Find volunteers for our event":"volunteer_shift",
         "Build a working website page":"website",
         "Research the evidence of this claim":"research",
         "Help me untangle an odd puzzle":"generic"}
  for text,domain in cases.items():
   x=g.prepare(req(text=text))
   self.assertEqual(x["work_spec"]["domain"],domain,text)
   self.assertGreater(len(x["work_spec"]["checklist_items"]),3)
   self.assertEqual(x["work_spec"]["goal_contract"]["requested_outcome_observed"],False)
   self.assertFalse(x["external_effect"])
 def test_hazard_and_nonconfirmed_goals_cannot_prepare(self):
  x=g.prepare({"text":"Should I evacuate because of flood risk?",
   "choice":"a","action":g.ACTION,"consent":True,
   "expected_contract_id":"0"*64})
  self.assertEqual(x["status"],"HOLD_UNCONFIRMED_OR_CHANGED_GOAL")
 def test_unlisted_privilege_fields_are_rejected(self):
  x=req();x["send_email"]=True
  with self.assertRaises(ValueError):g.prepare(x)
  x=req();x["action"]="CONTACT_DONOR_NOW"
  self.assertEqual(g.prepare(x)["status"],"HOLD_NO_SEPARATE_LOCAL_WORK_PERMISSION")
if __name__=="__main__":unittest.main()
