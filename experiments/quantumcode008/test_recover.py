"""QC-008: source provenance, epistemic holds, recovery before nourishment."""
from dataclasses import replace
import unittest

from recover import (
    AS_OF, Source, Observation, Situation, Route, RouteStatus,
    Bridge, Question, Recovery, YES, NO, UNKNOWN,
    CAPABILITIES, SOURCE_STATES, public_source_registry,
    registry_receipts, routing_cards, route_status, bridge_library,
    bridges_for, questions_from_routes, recover, synthetic_case, report,
)


class AffordanceRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=public_source_registry()
        cls.base=synthetic_case("no_phone_no_car_no_food")
        cls.recovery=recover(cls.base)

    def test_authoritative_public_guidance_sources_are_pinned(self):
        self.assertEqual(len(self.sources),3)
        self.assertEqual({x.id for x in self.sources},
                         {"united_way_211","feeding_america_locator",
                          "usagov_emergency_food"})
        self.assertTrue(all(s.scope=="GENERAL_NAVIGATION_ONLY"
                            for s in self.sources))
        self.assertTrue(all(s.captured==AS_OF for s in self.sources))
        self.assertTrue(all(len(s.pin)==64 for s in self.sources))

    def test_source_receipt_changes_when_claim_changes(self):
        one=self.sources[0]
        changed=replace(one,claim="A different and unverified claim")
        self.assertNotEqual(one.pin,changed.pin)
        self.assertNotEqual(registry_receipts((one,)),
                            registry_receipts((changed,)))

    def test_invalid_source_does_not_enter_ledger(self):
        with self.assertRaises(ValueError):
            replace(self.sources[0],url="example.com/unsupported").check()
        with self.assertRaises(ValueError):
            registry_receipts(self.sources+(self.sources[0],))
        with self.assertRaises(ValueError):
            replace(self.sources[0],scope="LOCAL_FOOD_CONFIRMED").check()

    def test_source_reference_is_not_availability_proof(self):
        for route in routing_cards():
            route.check()
            self.assertFalse(route.local_service_verified)
            self.assertFalse(route.directly_provides_food)
            self.assertTrue(route.may_require_user_consent)

    def test_unattributed_route_is_refused(self):
        created=Route("fake","ASSISTANCE_ROUTING",(),
                      ("missing_source",),"PUBLIC","unknown")
        with self.assertRaises(ValueError):
            route_status(created,self.base,self.sources)

    def test_no_phone_is_not_no_ability_to_walk(self):
        self.assertEqual(self.base.at("has_phone"),NO)
        self.assertEqual(self.base.at("motor_transport"),NO)
        self.assertEqual(self.base.at("can_walk"),UNKNOWN)
        self.assertEqual(self.base.at("safe_to_walk"),UNKNOWN)

    def test_no_food_route_does_not_mean_no_next_action(self):
        x=self.recovery
        self.assertEqual(x.status,"NO_FOOD_ROUTE_YET__NEXT_CAPABILITY")
        self.assertFalse(x.food_confirmed)
        self.assertFalse(x.actual_services_verified)
        self.assertEqual(x.external_actions,0)
        self.assertGreater(len(x.next_field),0)
        self.assertIn("brief_grounding",x.next_field)
        self.assertIn("check_walking_safety",x.next_field)
        self.assertIn("notice_nearby_people",x.next_field)

    def test_211_is_blocked_without_phone(self):
        x=next(z for z in self.recovery.routes if z.route_id=="call_211")
        self.assertEqual(x.verdict,"BLOCKED")
        self.assertIn("has_phone",x.blocked)

    def test_phone_is_not_borrowed_without_observation(self):
        self.assertEqual(self.base.at("has_phone"),NO)
        assert "seek_safe_shared_contact" in {
            b.id for b in self.recovery.bridges
        }
        self.assertEqual(self.base.at("has_phone"),NO)

    def test_walking_path_is_conditionally_unavailable_until_observed(self):
        x=next(z for z in self.recovery.routes if
               z.route_id=="ask_in_person_for_food_referral")
        self.assertEqual(x.verdict,"CONDITIONAL")
        self.assertEqual(set(x.unknown),
                         {"can_walk","safe_to_walk",
                          "safe_public_destination_known"})

    def test_safe_walking_if_known_changes_route_to_referral_not_food(self):
        case=synthetic_case("known_safe_walk")
        result=recover(case)
        self.assertEqual(result.status,"REFERRAL_PATH_POSSIBLE_NOT_FOOD")
        available={x.route_id for x in result.routes
                   if x.verdict=="POSSIBLE_REFERRAL"}
        self.assertIn("ask_in_person_for_food_referral",available)
        self.assertFalse(result.food_confirmed)
        self.assertFalse(result.actual_services_verified)

    def test_no_unsafe_walking_suggestion(self):
        situation=synthetic_case("not_safe_to_walk")
        result=recover(situation)
        walk=next(x for x in result.routes
                  if x.route_id=="ask_in_person_for_food_referral")
        self.assertEqual(walk.verdict,"BLOCKED")
        self.assertIn("safe_to_walk",walk.blocked)
        self.assertNotIn("check_walking_safety",
                         {b.id for b in result.bridges})
        self.assertNotIn("ask_in_person_for_food_referral",
                         result.next_field)

    def test_medical_red_flags_preempt_walking(self):
        case=synthetic_case("symptomatic")
        result=recover(case)
        self.assertEqual(result.status,
                         "PRIORITIZE_URGENT_HUMAN_ASSISTANCE")
        self.assertEqual(result.next_field,
                         ("seek_urgent_human_assistance",))
        self.assertNotIn("look_for_safe_public_destination",
                         result.next_field)

    def test_a_nearby_person_is_not_automatically_safe_to_approach(self):
        state=self.base.append("someone_nearby",YES,"user:someone_there")
        out=recover(state)
        nearby=next(x for x in out.routes if
                    x.route_id=="ask_nearby_person_for_help")
        self.assertEqual(nearby.verdict,"CONDITIONAL")
        self.assertIn("safe_person_to_approach",nearby.unknown)
        self.assertNotIn(nearby.route_id,out.next_field)

    def test_an_unsafe_nearby_person_is_not_a_referral_route(self):
        state=(self.base.append("someone_nearby",YES,"user:present")
               .append("safe_person_to_approach",NO,"user:unsafe"))
        out=recover(state)
        nearby=next(x for x in out.routes if
                    x.route_id=="ask_nearby_person_for_help")
        self.assertEqual(nearby.verdict,"BLOCKED")
        self.assertIn("safe_person_to_approach",nearby.blocked)

    def test_severe_symptoms_override_formerly_safe_walking_evidence(self):
        state=synthetic_case("known_safe_walk").append(
            "medical_red_flags",YES,"fixture:new_sudden_symptoms")
        out=recover(state)
        self.assertEqual(out.status,"PRIORITIZE_URGENT_HUMAN_ASSISTANCE")
        walking=next(x for x in out.routes if
                     x.route_id=="ask_in_person_for_food_referral")
        self.assertEqual(walking.verdict,"BLOCKED")
        self.assertIn("medical_red_flags",walking.blocked)

    def test_phone_opening_is_referral_not_nutrition(self):
        x=recover(synthetic_case("phone_available"))
        self.assertEqual(x.status,"REFERRAL_PATH_POSSIBLE_NOT_FOOD")
        self.assertIn("call_211",x.next_field)
        self.assertFalse(x.food_confirmed)
        self.assertFalse(x.actual_services_verified)

    def test_food_presence_reports_safety_not_external_confirmation(self):
        x=recover(self.base.append("has_food",YES,"fixture:new_food"))
        self.assertEqual(x.status,
                         "FOOD_PRESENT_VERIFY_SAFE_NOURISHMENT")
        self.assertTrue(x.food_confirmed)
        self.assertFalse(x.actual_services_verified)
        self.assertEqual(x.external_actions,0)

    def test_unknown_values_are_not_guessed(self):
        self.assertEqual(self.base.at("someone_nearby"),UNKNOWN)
        self.assertIn("someone_nearby",
                      {q.predicate for q in self.recovery.questions})
        self.assertEqual(self.base.at("someone_nearby"),UNKNOWN)
        self.assertTrue(all(q.status=="NEEDS_OBSERVATION_NOT_ASSUMPTION"
                            for q in self.recovery.questions))

    def test_safety_first_questions_rank_above_convenience(self):
        result=self.recovery
        names=[q.predicate for q in result.questions]
        self.assertIn("medical_red_flags",names)
        self.assertIn("safe_to_walk",names)
        first=names.index("medical_red_flags")
        self.assertLess(first,names.index("can_walk"))
        self.assertLess(first,names.index("someone_nearby"))

    def test_questions_preserve_equal_urgency_fiber(self):
        result=self.recovery
        same=[q for q in result.questions if q.safety_priority==0]
        self.assertGreaterEqual(len(same),2)
        self.assertTrue(all(q.status=="NEEDS_OBSERVATION_NOT_ASSUMPTION"
                            for q in same))

    def test_user_answer_reopens_care_route_without_user_phoning(self):
        state=(self.base.append("someone_nearby",YES,"user:explicit")
                .append("safe_person_to_approach",YES,"user:safety_confirmed"))
        x=recover(state)
        self.assertIn("ask_nearby_person_for_help",
                      {y.route_id for y in x.routes
                       if y.verdict=="POSSIBLE_REFERRAL"})
        self.assertEqual(state.at("has_phone"),NO)
        self.assertFalse(x.food_confirmed)

    def test_observation_receipt_is_append_only(self):
        first=self.base
        after=first.append("can_walk",YES,"user:self-report")
        self.assertEqual(first.at("can_walk"),UNKNOWN)
        self.assertEqual(after.at("can_walk"),YES)
        self.assertEqual(len(after.history),len(first.history)+1)
        self.assertEqual(after.history[:len(first.history)],first.history)
        self.assertNotEqual(first.pin,after.pin)

    def test_later_reversal_preserves_historical_fact_cut(self):
        first=self.base.append("safe_to_walk",YES,"user:at_t0")
        second=first.append("safe_to_walk",NO,"user:storm_at_t1")
        self.assertEqual(first.at("safe_to_walk"),YES)
        self.assertEqual(second.at("safe_to_walk"),NO)
        self.assertEqual(len(second.trace("safe_to_walk")),2)
        self.assertEqual(second.trace("safe_to_walk")[0].value,YES)

    def test_unreferenced_observation_is_refused(self):
        with self.assertRaises(ValueError):
            self.base.append("can_walk",YES,"")
        with self.assertRaises(ValueError):
            self.base.append("can_walk","MAYBE","user")
        with self.assertRaises(ValueError):
            self.base.append("imaginary_power",YES,"user")

    def test_false_or_backdated_receipt_cannot_be_inserted(self):
        forged=Observation("has_phone",YES,"fake","PERSON_REPORT",1)
        with self.assertRaises(ValueError):
            Situation(self.base.history+(forged,),
                      "IMMEDIATE","ORDINARY")
        with self.assertRaises(ValueError):
            Observation("has_phone",YES,"fixture","ALIEN",55).check()

    def test_persistent_need_is_not_downgraded_to_single_food_source(self):
        x=recover(synthetic_case("persistent_no_phone"))
        self.assertEqual(x.goal,"FIND_REPEATABLE_FOOD_ACCESS")
        self.assertTrue(any(r.route_id=="research_ongoing_access" for r in x.routes))
        self.assertFalse(x.food_confirmed)
        self.assertGreater(len(x.next_field),0)

    def test_breathing_may_support_focus_but_never_claims_a_meal(self):
        calm=next(b for b in bridge_library() if b.id=="brief_grounding")
        self.assertEqual(calm.target,"decision_readiness")
        self.assertEqual(calm.claimed_nutrition,0)
        self.assertFalse(calm.automatically_changes_world)
        self.assertIn("NOT nourishment",calm.guard)
        self.assertEqual(self.base.at("has_food"),NO)

    def test_no_risky_fasting_as_an_emergency_food_route(self):
        specs=bridge_library()
        self.assertTrue(all("fasting" not in x.id for x in specs))
        self.assertTrue(all("fast" not in x.id for x in routing_cards()))
        self.assertTrue(all(x.claimed_nutrition==0 for x in specs))
        self.assertIn("FASTING_NOT_A_FOOD_ROUTE",
                      report()["health_guard"])

    def test_no_walk_if_serious_symptoms_or_unsafe(self):
        for name in ("symptomatic","not_safe_to_walk"):
            x=recover(synthetic_case(name))
            self.assertNotIn("ask_in_person_for_food_referral",x.next_field)

    def test_unknown_real_world_provider_claim_never_nominated_as_verified(self):
        cards=routing_cards()
        self.assertFalse(any(x.local_service_verified for x in cards))
        self.assertFalse(any(x.directly_provides_food for x in cards))
        out=report()
        self.assertFalse(out["verified_real_world_impact"])
        self.assertEqual(out["real_meals_provided"],0)

    def test_no_real_outgoing_calls_or_contact_creation(self):
        out=report()
        self.assertEqual(out["external_actions"],0)
        self.assertEqual(out["source_scope"],
                         "GENERAL_NAVIGATION_NOT_LOCAL_AVAILABILITY")

    def test_sources_stay_separate_from_person_report(self):
        self.assertEqual({s.scope for s in self.sources},
                         {"GENERAL_NAVIGATION_ONLY"})
        self.assertTrue(all(e.kind=="PERSON_REPORT"
                            for e in self.base.history))
        self.assertTrue(all(e.ref=="fixture:user"
                            for e in self.base.history))

    def test_bounded_route_inventory_and_no_arbitrary_shell(self):
        routes=routing_cards()
        self.assertLess(len(routes),100)
        self.assertEqual(len({r.id for r in routes}),len(routes))
        self.assertTrue(all(r.channel in {"TELEPHONE","WEB_SEARCH",
                                            "ON_FOOT","PERSON"}
                            for r in routes))
        self.assertFalse(any(x.channel=="EVAL_PYTHON" for x in routes))

    def test_synthetic_report_contains_blocked_and_opened_states(self):
        cases=report()["cases"]
        self.assertEqual(len(cases),6)
        self.assertEqual(cases["no_phone_no_car_no_food"]["possible_referrals"],())
        self.assertIn("ask_in_person_for_food_referral",
                      cases["known_safe_walk"]["possible_referrals"])
        self.assertIn("call_211",
                      cases["phone_available"]["possible_referrals"])
        self.assertEqual(cases["symptomatic"]["status"],
                         "PRIORITIZE_URGENT_HUMAN_ASSISTANCE")

    def test_unknown_scenario_is_not_hallucinated(self):
        with self.assertRaises(ValueError):
            synthetic_case("unknown_realworld_address")

    def test_question_fiber_carries_provenance_and_discriminator(self):
        questions=self.recovery.questions
        self.assertGreater(len(questions),4)
        self.assertTrue(all(q.predicate in CAPABILITIES for q in questions))
        self.assertTrue(all(len(q.text)>15 for q in questions))
        self.assertTrue(any(q.unlocks for q in questions))

    def test_source_pin_stale_or_missing_refuses_route(self):
        route=routing_cards()[0]
        with self.assertRaises(ValueError):
            route_status(route,self.base,())

    def test_no_forced_unique_solution_when_multiple_safe_actions(self):
        x=recover(self.base)
        self.assertGreaterEqual(len(x.next_field),4)
        self.assertEqual(len(x.next_field),len(set(x.next_field)))

    def test_short_list_of_questions_not_infinite_auto_self_improvement(self):
        x=recover(self.base)
        self.assertLessEqual(len(x.questions),len(CAPABILITIES))
        self.assertEqual(x.boundedness,"FINITE_TYPED_CANDIDATES")
        self.assertEqual(x.external_actions,0)

    def test_borrow_phone_is_not_automatic(self):
        b=next(x for x in self.recovery.bridges
               if x.id=="seek_safe_shared_contact")
        self.assertEqual(b.target,"has_phone")
        self.assertFalse(b.automatically_changes_world)
        self.assertEqual(self.base.at("has_phone"),NO)

    def test_hunger_is_not_reframed_as_a_moral_failure(self):
        x=recover(self.base)
        self.assertNotIn("fast",str(x.next_field).lower())
        self.assertEqual(x.food_confirmed,False)
        self.assertTrue(x.status.startswith("NO_FOOD_ROUTE_YET"))

    def test_future_food_available_requires_new_source_observation(self):
        first=recover(self.base)
        second=recover(self.base.append("has_food",YES,
                                        "fixture:actual_source_claim"))
        self.assertFalse(first.food_confirmed)
        self.assertTrue(second.food_confirmed)
        self.assertNotEqual(first.situation_pin,second.situation_pin)


if __name__=="__main__":
    unittest.main()
