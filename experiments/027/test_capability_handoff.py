import importlib.util
from pathlib import Path
from urllib.parse import urlparse,parse_qs,unquote
import unittest
p=Path(__file__).with_name("capability_handoff.py")
spec=importlib.util.spec_from_file_location("handoff",p)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
TEXT="Can we get free coffee donated for our fellowship event?"
def goal(text=TEXT,choice="a"):
 c=h.owner.composer.compose(text,choice)
 return {"text":text,"choice":choice,"expected_contract_id":c["contract_id"]}
def mail(stage=h.PREVIEW,**kw):
 return {**goal(),"stage":stage,
   "recipient":"donor@example.org","subject":"Coffee inquiry",
   "message":"Hello, would you consider donating coffee? No obligation.",
   **kw}
class LastInch(unittest.TestCase):
 def test_actual_source_verified_goal_routes_to_real_local_capabilities(self):
  x=h.route({**goal(),"stage":h.DISCOVER})
  self.assertEqual(x["status"],"LOCAL_CAPABILITIES_AVAILABLE_NOT_EXECUTED")
  self.assertEqual({a["id"] for a in x["capabilities"]},
    {"local_workkit","local_workshop","local_email_composer"})
  self.assertEqual(x["message_template_subject"],"Coffee for a community gathering")
  self.assertFalse(x["actual_message_sent"])
  self.assertFalse(x["external_delivery"])
  self.assertEqual(x["public_network_gets"],0)
 def test_two_step_exact_recipient_message_review_before_mailto(self):
  request=mail()
  prev=h.route(request)
  self.assertEqual(prev["status"],"LOCAL_MAIL_COMPOSER_PREVIEW_NOT_SENT")
  self.assertIsNone(prev["mailto_uri"])
  self.assertEqual(len(prev["preview_id"]),64)
  approved=h.route({**mail(h.OPEN),"preview_id":prev["preview_id"],
                    "open_consent":True,"open_permission":h.PERMISSION})
  self.assertEqual(approved["status"],"LOCAL_MAIL_APP_HANDOFF_READY_NOT_SENT")
  self.assertTrue(approved["mailto_uri"].startswith("mailto:donor@example.org?"))
  url=urlparse(approved["mailto_uri"])
  self.assertEqual(url.scheme,"mailto")
  self.assertEqual(parse_qs(url.query)["subject"],["Coffee inquiry"])
  self.assertEqual(parse_qs(url.query)["body"],[request["message"]])
  self.assertFalse(approved["actual_message_sent"])
  self.assertTrue(approved["no_delivery_receipt"])
 def test_missing_consent_rejected(self):
  p=h.route(mail())
  with self.assertRaises(ValueError):
   h.route({**mail(h.OPEN),"preview_id":p["preview_id"],
            "open_consent":False,"open_permission":h.PERMISSION})
 def test_changed_recipient_or_message_invalidates_review(self):
  p=h.route(mail())
  for changes in [{"recipient":"other@example.org"},{"subject":"new header"},
                  {"message":"Changed terms"}]:
   with self.assertRaises(ValueError):
    h.route({**mail(h.OPEN),"preview_id":p["preview_id"],
             "open_consent":True,"open_permission":h.PERMISSION,
             **changes})
 def test_outdated_goal_hash_fails(self):
  original=goal()
  changed={**mail(),"choice":"b"}
  with self.assertRaises(ValueError):h.route(changed)
  self.assertNotEqual(h.owner.composer.compose(TEXT,"b")["contract_id"],
                      original["expected_contract_id"])
 def test_no_recipient_inference_and_header_injection(self):
  for bad in ["a@example.org,b@example.org","a@example.org\nBcc:bad@evil.com",
              "javascript:evil@x.com", "Donor Unknown","noname@localhost"]:
   with self.assertRaises(ValueError):h.route(mail(recipient=bad))
  with self.assertRaises(ValueError):h.route(mail(subject="hi\r\nBcc: bad@evil.org"))
 def test_route_scopes_are_domain_specific(self):
  site="Build a working website page"
  x=h.route({**goal(site),"stage":h.DISCOVER})
  self.assertNotIn("local_email_composer",{a["id"] for a in x["capabilities"]})
  self.assertIn("local_workshop",{a["id"] for a in x["capabilities"]})
  with self.assertRaises(ValueError):h.route({**goal("Should I evacuate because of flood risk?"),"stage":h.DISCOVER})
 def test_river_goal_never_auto_contacts_gauge_or_email(self):
  text="Could you check the rivers?"
  x=h.route({**goal(text),"stage":h.DISCOVER})
  self.assertFalse(x["mail_app_supported"])
  self.assertEqual([a["id"] for a in x["capabilities"]],["local_workkit"])
  self.assertEqual(x["public_network_gets"],0)
 def test_arbitrary_privilege_and_personal_data_leak_are_refused(self):
  with self.assertRaises(ValueError):h.route({**goal(),"stage":h.DISCOVER,"send":True})
  with self.assertRaises(ValueError):h.route({**goal(),"stage":h.DISCOVER,
                                               "recipient":"sensitive@example.org"})
 def test_third_party_is_never_claimed_as_confirmed_donor(self):
  x=h.route(mail())
  self.assertTrue(x["contact_is_human_supplied_unverified"])
  self.assertFalse(x["actual_message_sent"])
  self.assertEqual(x["journal_events_created"],0)
if __name__=="__main__":unittest.main()
