"""QC-009: falsify simplistic 'use infrastructure or stop' survival reasoning."""
from dataclasses import replace
import unittest

from street_sense import (
    YES,NO,UNKNOWN,STATUS,FACTS, Fact, Scene, StreetOption, SkillWitness,
    SOURCES, catalogue, assess, reason, counterfactual_disconnect, case, run,
)


class StreetSenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.options=catalogue()
        cls.cases={k:reason(case(k)) for k in (
            "offline_unknown","hot_and_offline","wet_cold_and_unprepared",
            "with_safe_contact","danger_signs","network_connected",
            "unverified_water","repeated_needs")}

    def test_eight_distinct_test_scenes(self):
        self.assertEqual(len(self.cases),8)
        self.assertEqual(len({x.scene_pin for x in self.cases.values()}),8)

    def test_no_internet_no_phone_no_food_is_still_an_action_field(self):
        r=self.cases["offline_unknown"]
        self.assertEqual(r.status,"SAFE_WATER_GAP_PRIORITY")
        self.assertTrue(r.offline_ready)
        self.assertIn("pause_and_orient",r.offline_ready)
        self.assertIn("check_urgent_signs",r.offline_ready)
        self.assertIn("check_water_condition",r.offline_ready)
        self.assertFalse(r.online_ready)

    def test_not_survival_romanticism_or_phantom_resource(self):
        for r in self.cases.values():
            self.assertFalse(r.food_supplied)
            self.assertFalse(r.shelter_delivered)
            self.assertEqual(r.external_effects,0)
            self.assertFalse(r.field_expertise_automatically_verified)

    def test_water_priority_outranks_food_without_safe_water(self):
        r=self.cases["offline_unknown"]
        self.assertEqual(r.preferred_urgencies[0],"FIND_SAFE_WATER")
        self.assertNotIn("ingest_safe_water",r.offline_ready)
        self.assertNotIn("eat_verified_food",r.offline_ready)

    def test_contaminated_water_cannot_be_drunk_even_if_claimed_available(self):
        r=self.cases["unverified_water"]
        contaminated=next(x for x in r.blocked
                          if x.option.id=="ingest_safe_water")
        self.assertIn("suspected_water_contamination",contaminated.blocked)
        self.assertNotIn("ingest_safe_water",r.offline_ready)

    def test_a_safe_water_drinking_route_requires_two_explicit_facts(self):
        initial=case("offline_unknown")
        state=(initial.add("has_safe_water",YES,"user:bottled_supply")
               .add("suspected_water_contamination",NO,"user:known_safe"))
        result=reason(state)
        self.assertIn("ingest_safe_water",result.offline_ready)
        self.assertFalse(result.food_supplied)

    def test_cold_priority_correctly_overrides_food_options(self):
        r=self.cases["wet_cold_and_unprepared"]
        self.assertEqual(r.status,"COLD_EXPOSURE_PRIORITY")
        self.assertEqual(r.preferred_urgencies[0],"SAFE_DRY_WARMTH")
        self.assertNotIn("use_known_dry_layers",r.offline_ready)
        self.assertNotIn("move_into_known_shelter",r.offline_ready)

    def test_dry_layers_requires_actual_supply(self):
        r=self.cases["wet_cold_and_unprepared"]
        dry=next(x for x in r.blocked if x.option.id=="use_known_dry_layers")
        self.assertIn("dry_layers_available",dry.blocked)

    def test_cold_after_actual_dry_layers_report_opens_candidate(self):
        state=case("wet_cold_and_unprepared").add(
            "dry_layers_available",YES,"user:found_dry_jacket")
        self.assertIn("use_known_dry_layers",reason(state).offline_ready)

    def test_heat_support_if_safe_shade_verified(self):
        r=self.cases["hot_and_offline"]
        self.assertEqual(r.status,"HEAT_EXPOSURE_PRIORITY")
        self.assertEqual(r.preferred_urgencies[0],"SHADE_COOLING")
        self.assertIn("move_into_known_shade",r.offline_ready)

    def test_heat_shade_is_not_treated_as_food_or_a_cure(self):
        r=self.cases["hot_and_offline"]
        shade=next(x.option for x in r.ready
                   if x.option.id=="move_into_known_shade")
        self.assertEqual(shade.purpose,"STABILIZE")
        self.assertFalse(shade.verified_benefit)
        self.assertFalse(r.food_supplied)

    def test_cannot_walk_from_absence_of_a_vehicle(self):
        s=case("offline_unknown")
        self.assertEqual(s.get("can_walk"),UNKNOWN)
        self.assertEqual(s.get("walking_safe"),UNKNOWN)
        self.assertFalse(any(x.option.channel=="FOOT"
                             for x in self.cases["offline_unknown"].ready))

    def test_walking_route_requires_confirmed_ability_and_destination(self):
        state=(case("offline_unknown")
               .add("can_walk",YES,"user:mobility")
               .add("walking_safe",YES,"user:conditions")
               .add("safe_public_place_known",YES,"user:confirmed_place"))
        self.assertIn("walk_to_verified_public_place",
                      reason(state).offline_ready)

    def test_severe_symptoms_block_every_foot_route(self):
        r=self.cases["danger_signs"]
        self.assertEqual(r.status,"URGENT_HUMAN_ASSISTANCE_REQUIRED")
        self.assertEqual(r.preferred_urgencies[0],"URGENT_HUMAN_HELP")
        self.assertFalse(any(x.option.channel=="FOOT" for x in r.ready))

    def test_later_urgent_signs_override_previous_mobility(self):
        s=(case("hot_and_offline")
           .add("safe_public_place_known",YES,"fixture:place")
           .add("urgent_symptoms",YES,"fixture:new_symptoms"))
        r=reason(s)
        walk=next(x for x in r.blocked
                  if x.option.id=="walk_to_verified_public_place")
        self.assertIn("urgent_symptoms",walk.blocked)

    def test_safe_human_network_can_offer_offline_bridge(self):
        r=self.cases["with_safe_contact"]
        self.assertIn("request_help_from_safe_person",r.offline_ready)
        self.assertIn("ask_for_borrowed_call",r.offline_ready)
        self.assertFalse(r.online_ready)

    def test_stranger_not_assumed_safe_or_willing(self):
        s=case("offline_unknown")
        self.assertEqual(s.get("safe_person_present"),UNKNOWN)
        r=reason(s)
        self.assertNotIn("request_help_from_safe_person",r.offline_ready)
        helper=next(x for x in r.conditional
                    if x.option.id=="request_help_from_safe_person")
        self.assertIn("safe_person_present",helper.unresolved)

    def test_asking_for_borrowed_phone_does_not_create_phone(self):
        s=case("with_safe_contact")
        result=reason(s)
        self.assertIn("ask_for_borrowed_call",result.offline_ready)
        self.assertEqual(s.get("has_phone"),NO)

    def test_infrastructure_returns_network_options(self):
        r=self.cases["network_connected"]
        self.assertIn("online_food_referral",r.online_ready)
        self.assertIn("call_for_support",r.online_ready)
        self.assertIn("pause_and_orient",r.offline_ready)

    def test_infrastructure_outage_does_not_erase_offline_action_paths(self):
        before=case("network_connected")
        after=counterfactual_disconnect(before)
        self.assertTrue(after["before_online_candidates"])
        self.assertFalse(after["after_online_candidates"])
        self.assertIn("pause_and_orient",after["retained_offline_candidates"])
        self.assertIn("check_urgent_signs",after["retained_offline_candidates"])
        self.assertEqual(after["new_real_world_supplies"],0)

    def test_unplugging_network_is_not_a_loss_of_all_knowledge(self):
        r=reason(case("network_connected"))
        s=reason(case("offline_unknown"))
        self.assertGreaterEqual(len(s.offline_ready),3)
        self.assertTrue({x.option.id for x in r.ready} &
                        {x.option.id for x in s.ready})

    def test_persistent_horizon_does_not_downgrade_to_one_meal(self):
        r=self.cases["repeated_needs"]
        self.assertIn("ESTABLISH_RECURRING_ACCESS",r.preferred_urgencies)
        self.assertIn("build_recurring_food_route",r.offline_ready)
        self.assertFalse(r.food_supplied)

    def test_no_shelter_found_still_calls_for_new_observation(self):
        r=self.cases["wet_cold_and_unprepared"]
        self.assertIn("check_urgent_signs",r.offline_ready)
        self.assertIn("identify_human_connections",r.offline_ready)
        self.assertEqual(r.status,"COLD_EXPOSURE_PRIORITY")

    def test_option_fiber_retains_multiple_nonconflicting_immediate_modes(self):
        r=self.cases["offline_unknown"]
        self.assertGreaterEqual(len(r.offline_ready),4)
        self.assertEqual(len(r.offline_ready),len(set(r.offline_ready)))
        self.assertIn("check_mobility",r.offline_ready)

    def test_unknown_prereqs_are_conditional_not_blocked(self):
        r=self.cases["offline_unknown"]
        walk=next(x for x in r.conditional if
                  x.option.id=="walk_to_verified_public_place")
        self.assertIn("can_walk",walk.unresolved)
        self.assertIn("safe_public_place_known",walk.unresolved)

    def test_cannot_use_unverified_weather_gear_or_drinking_water(self):
        r=self.cases["offline_unknown"]
        self.assertNotIn("use_known_dry_layers",r.offline_ready)
        self.assertNotIn("ingest_safe_water",r.offline_ready)

    def test_known_cold_weather_not_only_digital_resources(self):
        r=self.cases["wet_cold_and_unprepared"]
        self.assertIn("SAFE_DRY_WARMTH",r.preferred_urgencies)
        self.assertFalse(r.online_ready)

    def test_sources_are_navigation_and_safety_evidence_not_live_service(self):
        r=self.cases["offline_unknown"]
        self.assertTrue(all(src.startswith("https://") for src in r.source_urls))
        self.assertIn(SOURCES["cdc_cold"],r.source_urls)
        self.assertFalse(r.shelter_delivered)

    def test_no_unreviewed_source_category_promotes_action(self):
        a=replace(self.options[0],evidence_ids=("fictional_survival_manual",))
        with self.assertRaises(ValueError):
            assess(a,case("offline_unknown"))

    def test_unsafe_walking_card_needs_explicit_guard(self):
        a=replace(self.options[0],id="unsafe_foot",channel="FOOT")
        with self.assertRaises(ValueError):
            assess(a,case("offline_unknown"))

    def test_unsafe_human_card_needs_explicit_guard(self):
        a=replace(self.options[0],id="unsafe_person",channel="HUMAN")
        with self.assertRaises(ValueError):
            assess(a,case("offline_unknown"))

    def test_unsafe_network_card_needs_explicit_guard(self):
        a=replace(self.options[0],id="unsafe_phone",channel="NETWORK")
        with self.assertRaises(ValueError):
            assess(a,case("offline_unknown"))

    def test_water_card_cannot_skip_safety_gate(self):
        a=next(x for x in self.options if x.id=="ingest_safe_water")
        a=replace(a,requires=(("has_safe_water",YES),))
        with self.assertRaises(ValueError):
            assess(a,case("offline_unknown"))

    def test_personal_survival_skills_are_not_mined_without_permission(self):
        no=SkillWitness("person1","experience","someone",False,"general")
        with self.assertRaises(ValueError):
            no.admit()
        allowed=replace(no,consent_to_store=True)
        self.assertEqual(allowed.admit(),allowed)
        self.assertEqual(allowed.verification,"UNVERIFIED_EXPERIENCE")

    def test_experience_is_not_independent_verified_truth(self):
        a=SkillWitness("share01","dry-clothing tip","voluntary interview",
                       True,"cold weather")
        self.assertEqual(a.admit().verification,"UNVERIFIED_EXPERIENCE")

    def test_historical_observations_append_without_backdating(self):
        now=case("offline_unknown")
        later=now.add("has_food",YES,"person:food_arrived")
        self.assertEqual(now.get("has_food"),NO)
        self.assertEqual(later.get("has_food"),YES)
        self.assertNotEqual(now.pin,later.pin)
        self.assertEqual(later.observations[:-1],now.observations)

    def test_unattributed_or_backdated_observations_refuse(self):
        with self.assertRaises(ValueError):
            case("offline_unknown").add("has_food",YES,"")
        base=case("offline_unknown")
        with self.assertRaises(ValueError):
            Scene(base.observations+(Fact("has_food",YES,"fake",1),))

    def test_actions_cannot_claim_verified_nutrition_from_guess(self):
        a=replace(self.options[0],verified_benefit=True)
        with self.assertRaises(ValueError):
            assess(a,case("offline_unknown"))

    def test_research_run_no_real_world_provisions(self):
        o=run()
        self.assertEqual(o["external_effects"],0)
        self.assertEqual(o["measured_real_world_outcomes"],0)
        self.assertEqual(o["real_world_expertise_claims"],0)

    def test_report_all_predetermined_scenes_and_hazards(self):
        o=run()
        self.assertEqual(len(o["scenes"]),8)
        self.assertEqual(o["scenes"]["danger_signs"]["status"],
                         "URGENT_HUMAN_ASSISTANCE_REQUIRED")
        self.assertEqual(o["scenes"]["wet_cold_and_unprepared"]["status"],
                         "COLD_EXPOSURE_PRIORITY")

    def test_unknown_scenario_not_made_up(self):
        with self.assertRaises(ValueError):
            case("nearby_real_911_station")

    def test_no_live_database_of_unhoused_people_collected(self):
        o=run()
        self.assertFalse("people" in o)
        self.assertFalse("names" in o)
        self.assertFalse("addresses" in o)


if __name__=="__main__":
    unittest.main()
