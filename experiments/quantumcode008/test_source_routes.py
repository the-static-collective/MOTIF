"""QC-008: transparent source-to-route discovery without phantom availability."""
from dataclasses import replace
import unittest

from recover import (
    Source,YES,NO,UNKNOWN,ROUTING,public_source_registry,synthetic_case,
    routing_cards,recover,registry_receipts,
)
from source_routes import (
    MechanismSpec,catalogued_public_mechanisms,compile_public_routes,
)


class SourceCompilationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=public_source_registry()
        cls.specs=catalogued_public_mechanisms()

    def test_compiler_can_recreate_entire_public_route_inventory(self):
        ours=compile_public_routes(self.sources,self.specs)
        used=routing_cards()
        self.assertEqual(ours,used)
        self.assertEqual(len(ours),5)

    def test_all_route_effects_are_information_not_food_delivery(self):
        for route in routing_cards():
            self.assertFalse(route.directly_provides_food)
            self.assertFalse(route.local_service_verified)
            self.assertTrue(route.may_require_user_consent)

    def test_new_documented_option_enters_planner_without_source_edit(self):
        new_source=Source(
            "additional_usagov_interpretation",
            "https://www.usa.gov/emergency-food-assistance",
            "Community and religious organizations may be contacted for "
            "emergency food referral, conditional on actual access",
            "GENERAL_NAVIGATION_ONLY","2026-11-07",
        )
        new_mechanism=MechanismSpec(
            "ask_a_person_for_community_referral",
            (new_source.id,),"PERSON",(("someone_nearby",YES),
                      ("safe_person_to_approach",YES)),ROUTING,
            "Ask a safely approachable person whether a community resource "
            "can be identified; not a food availability guarantee.",
        )
        sources=self.sources+(new_source,)
        specs=self.specs+(new_mechanism,)
        candidates=compile_public_routes(sources,specs)
        self.assertEqual(len(candidates),6)
        absent=recover(synthetic_case("no_phone_no_car_no_food"),
                       sources, specs)
        added=next(x for x in absent.routes if x.route_id==new_mechanism.id)
        self.assertEqual(added.verdict,"CONDITIONAL")
        actual=recover(
            synthetic_case("no_phone_no_car_no_food").append(
                "someone_nearby",YES,"user:someone_safe_to_ask").append(
                "safe_person_to_approach",YES,"user:approach_ok"),
            sources,specs)
        enabled=next(x for x in actual.routes if x.route_id==new_mechanism.id)
        self.assertEqual(enabled.verdict,"POSSIBLE_REFERRAL")
        self.assertFalse(actual.actual_services_verified)
        self.assertFalse(actual.food_confirmed)

    def test_new_source_without_reviewed_mechanism_does_not_create_route(self):
        extra=Source("floating","https://www.usa.gov/emergency-food-assistance",
                     "A vague association","GENERAL_NAVIGATION_ONLY",
                     "2026-11-07")
        routes=compile_public_routes(self.sources+(extra,),self.specs)
        self.assertEqual(len(routes),5)

    def test_route_with_unbacked_source_is_rejected(self):
        candidate=MechanismSpec(
            "unbacked",("no_such_source",),"PERSON",
            (("someone_nearby",YES),),ROUTING,"Someone might help")
        with self.assertRaises(ValueError):
            compile_public_routes(self.sources,self.specs+(candidate,))

    def test_new_person_route_without_safety_guard_is_refused(self):
        candidate=MechanismSpec(
            "unsafe_channel",("usagov_emergency_food",),"PERSON",
            (("someone_nearby",YES),),ROUTING,
            "Do not auto-approach somebody merely because nearby")
        with self.assertRaises(ValueError):
            compile_public_routes(self.sources,self.specs+(candidate,))

    def test_duplicate_invented_route_identity_is_refused(self):
        with self.assertRaises(ValueError):
            compile_public_routes(self.sources,self.specs+(self.specs[0],))

    def test_duplicate_source_identity_is_refused(self):
        with self.assertRaises(ValueError):
            compile_public_routes(self.sources+(self.sources[0],),self.specs)

    def test_claimed_local_service_scope_is_not_allowed(self):
        bad=replace(self.sources[0],scope="LOCAL_CONFIRMED")
        with self.assertRaises(ValueError):
            compile_public_routes((bad,)+self.sources[1:],self.specs)

    def test_live_availability_is_never_inferred_from_official_page(self):
        x=recover(synthetic_case("phone_available"))
        assert "call_211" in x.next_field
        self.assertFalse(x.actual_services_verified)
        self.assertFalse(x.food_confirmed)
        self.assertEqual(x.external_actions,0)

    def test_source_content_revision_changes_receipt_and_future_provenance(self):
        before=recover(synthetic_case("phone_available"))
        new=replace(self.sources[0],claim=self.sources[0].claim+" Updated.")
        later=recover(synthetic_case("phone_available"),
                      (new,)+self.sources[1:],self.specs)
        self.assertNotEqual(before.source_pins,later.source_pins)
        self.assertEqual(before.situation_pin,later.situation_pin)
        self.assertIn("call_211",later.next_field)
        self.assertFalse(later.actual_services_verified)

    def test_absent_source_id_does_not_silently_discard_card(self):
        with self.assertRaises(ValueError):
            recover(synthetic_case("no_phone_no_car_no_food"),
                    self.sources[1:],self.specs)

    def test_linguistically_plausible_still_requires_typed_provenance(self):
        bogus=MechanismSpec("wild","()", "WEB_SEARCH",(),
                            ROUTING,"Try an invented future device")
        with self.assertRaises(ValueError):
            compile_public_routes(self.sources,(bogus,))

    def test_unreviewed_html_is_not_executed_as_an_action(self):
        new=Source("example","https://example.org/unsafe",
                   "<script>sendMoney()</script>",
                   "GENERAL_NAVIGATION_ONLY","2026-11-07")
        candidates=compile_public_routes(self.sources+(new,),self.specs)
        self.assertEqual(len(candidates),5)
        self.assertTrue(all("script" not in r.description for r in candidates))


if __name__=="__main__":
    unittest.main()
