"""QC-009: disconnected field atlas, consent, expiration, safe approach."""
from dataclasses import replace
import unittest

from field_atlas import (
    Atlas,LocalLead,YES,NO,UNKNOWN,fixture,evaluate,atlas_options,report,
)


class FieldAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas=fixture()

    def test_fixture_is_four_consent_pinned_synthetic_reports(self):
        self.assertEqual(len(self.atlas.leads),4)
        self.assertTrue(all(lead.consent_to_retain for lead in self.atlas.leads))
        self.assertTrue(all(len(x.pin)==64 for x in self.atlas.leads))

    def test_first_hand_safe_contact_survives_network_cut(self):
        out=atlas_options(self.atlas,2,{"PHONE":NO,"WEB":NO})
        self.assertIn("local_walkable_contact",out["candidate_leads"])

    def test_phone_based_referral_fails_with_phone_outage(self):
        out=atlas_options(self.atlas,2,{"PHONE":NO,"WEB":NO})
        self.assertIn("outdated_food_referral",out["blocked"])
        self.assertIn("CHANNEL_DOWN",dict((k,reason)
            for k,_,reason in out["detail"])["outdated_food_referral"])

    def test_web_rumor_has_no_automatic_approval_even_when_connected(self):
        out=atlas_options(self.atlas,2,{"PHONE":YES,"WEB":YES})
        self.assertIn("unconfirmed_rumor",out["to_revalidate"])
        self.assertNotIn("unconfirmed_rumor",out["candidate_leads"])

    def test_recent_but_unverified_water_is_only_a_candidate(self):
        out=atlas_options(self.atlas,2,{"PHONE":NO,"WEB":NO})
        self.assertIn("locally_seen_water",out["candidate_leads"])
        self.assertEqual(out["actual_supplies_confirmed_now"],0)

    def test_time_decay_does_not_erase_history(self):
        before=self.atlas.pin
        old=atlas_options(self.atlas,5,{"PHONE":NO,"WEB":NO})
        self.assertIn("locally_seen_water",old["to_revalidate"])
        self.assertEqual(before,self.atlas.pin)

    def test_no_permission_blocks_lead_storage(self):
        new=replace(self.atlas.leads[0],id="unsafe_copy",
                    consent_to_retain=False)
        with self.assertRaises(ValueError):
            self.atlas.append(new)

    def test_cannot_identify_local_person_by_unconsented_name(self):
        lead=LocalLead("nothing","CONNECTION","IN_PERSON",
                       "FIRST_HAND_REPORT","",1,2,YES,"SAFE",
                       True,"missing source")
        with self.assertRaises(ValueError):
            lead.check()

    def test_unsafe_place_can_never_be_fresh_action_lead(self):
        bad=replace(self.atlas.leads[0],access_safety="UNSAFE")
        out=evaluate(bad,2,{"PHONE":YES,"WEB":YES})
        self.assertEqual(out.state,"BLOCKED")
        self.assertIn("ACCESS_UNSAFE",out.why)

    def test_unassessed_safety_remains_explicit_unknown(self):
        bad=replace(self.atlas.leads[0],access_safety="UNASSESSED")
        x=evaluate(bad,2,{})
        self.assertEqual(x.state,"REVALIDATE")

    def test_historical_cut_only_contains_available_at_date(self):
        old=self.atlas.as_of(1)
        self.assertEqual(len(old.leads),3)
        self.assertNotIn("locally_seen_water",{x.id for x in old.leads})
        self.assertEqual(len(self.atlas.leads),4)

    def test_duplicate_lead_refused_without_destroying_origins(self):
        with self.assertRaises(ValueError):
            self.atlas.append(self.atlas.leads[0])

    def test_future_dated_observation_not_available_now(self):
        with self.assertRaises(ValueError):
            evaluate(self.atlas.leads[1],1,{})

    def test_missing_or_stale_infrastructure_changes_only_relevance(self):
        pre=atlas_options(self.atlas,2,{"PHONE":YES,"WEB":YES})
        cut=atlas_options(self.atlas,2,{"PHONE":NO,"WEB":NO})
        self.assertEqual(pre["atlas_pin"],cut["atlas_pin"])
        self.assertGreaterEqual(len(cut["candidate_leads"]),1)
        self.assertIn("outdated_food_referral",cut["blocked"])

    def test_source_type_cannot_impersonate_first_hand(self):
        now=replace(self.atlas.leads[0],source_type="PUBLIC_GUIDANCE")
        r=evaluate(now,2,{})
        self.assertEqual(r.state,"REVALIDATE")
        self.assertIn("NOT_A_LOCAL_FIRST_HAND_OBSERVATION",r.why)

    def test_report_does_not_create_resource_or_collect_address(self):
        r=report()
        self.assertEqual(r["external_actions"],0)
        self.assertFalse(r["real_resource_availability_verified"])
        self.assertFalse(r["user_real_locations_collected"])

    def test_offline_retains_more_than_institutional_directory(self):
        r=report()
        self.assertIn("local_walkable_contact",
                      r["network_failure"]["candidate_leads"])
        self.assertNotIn("outdated_food_referral",
                         r["network_failure"]["candidate_leads"])

    def test_all_remaining_safety_flags_are_explicit(self):
        for l in self.atlas.leads:
            l.check()
        self.assertTrue(all(x.access_safety in
                            {"SAFE","UNSAFE","UNASSESSED"}
                            for x in self.atlas.leads))


if __name__=="__main__":
    unittest.main()
