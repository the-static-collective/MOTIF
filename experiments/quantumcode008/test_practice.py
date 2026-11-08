"""QC-008 contextual fasting boundaries and non-nutrition safety tests."""
import unittest
from practice import PracticeContext, consider_practices, practice_sources
from recover import YES, NO, UNKNOWN, synthetic_case, recover


class PracticeBoundaryTests(unittest.TestCase):
    def test_involuntary_food_shortage_is_not_therapeutic_fasting(self):
        entries=consider_practices(PracticeContext(NO,NO,UNKNOWN,UNKNOWN))
        self.assertIn("RESOURCE_GAP_REMAINS",{e.status for e in entries})
        self.assertNotIn("POSSIBLE_VOLUNTARY_PRACTICE_NOT_NUTRITION",
                         {e.status for e in entries})
        self.assertTrue(all(e.calorie_effect==0 for e in entries))

    def test_voluntary_fasting_is_not_arbitrarily_denied_as_a_practice(self):
        entries=consider_practices(PracticeContext(YES,YES,NO,NO))
        self.assertIn("POSSIBLE_VOLUNTARY_PRACTICE_NOT_NUTRITION",
                      {e.status for e in entries})
        self.assertTrue(all(e.calorie_effect==0 for e in entries))

    def test_medical_risk_prevents_fast_recommendation(self):
        entries=consider_practices(PracticeContext(YES,YES,YES,NO))
        self.assertIn("HOLD_HEALTH_CONTRAINDICATION",
                      {e.status for e in entries})

    def test_symptoms_prevent_therapeutic_fast_inference(self):
        entries=consider_practices(PracticeContext(YES,YES,NO,YES))
        self.assertIn("HOLD_HEALTH_CONTRAINDICATION",
                      {e.status for e in entries})

    def test_unobserved_willingness_and_condition_means_hold(self):
        entries=consider_practices(
            PracticeContext(UNKNOWN,UNKNOWN,UNKNOWN,UNKNOWN))
        self.assertIn("HOLD_NEED_HEALTH_AND_CHOICE_CONTEXT",
                      {e.status for e in entries})

    def test_breathing_can_support_attention_but_not_nutrition(self):
        entries=consider_practices(PracticeContext(NO,NO,UNKNOWN,UNKNOWN))
        b=next(e for e in entries if e.id=="comfortable_breathing")
        self.assertEqual(b.calorie_effect,0)
        self.assertEqual(b.status,"OPTIONAL_SUPPORT_NOT_NOURISHMENT")
        self.assertTrue("attention" in b.possible_role)

    def test_medical_sources_are_public_guidance_not_personal_diagnosis(self):
        self.assertEqual({s.id for s in practice_sources()},
                         {"cochrane_fasting_2026","mayo_fasting_safety"})
        self.assertTrue(all(s.scope=="GENERAL_NAVIGATION_ONLY"
                            for s in practice_sources()))
        self.assertTrue(all(len(s.pin)==64 for s in practice_sources()))

    def test_no_fast_substitute_in_urgent_no_phone_case(self):
        need=recover(synthetic_case("no_phone_no_car_no_food"))
        self.assertFalse(need.food_confirmed)
        self.assertTrue(need.next_field)
        self.assertFalse(any("fast" in s for s in need.next_field))

    def test_context_types_cannot_be_ambiguous_strings(self):
        with self.assertRaises(ValueError):
            consider_practices(PracticeContext("MAYBE",NO,UNKNOWN,UNKNOWN))

    def test_context_transition_requires_real_change(self):
        initial=PracticeContext(NO,NO,UNKNOWN,UNKNOWN)
        later=PracticeContext(YES,YES,NO,NO)
        first={x.status for x in consider_practices(initial)}
        second={x.status for x in consider_practices(later)}
        self.assertNotEqual(first,second)
        self.assertIn("RESOURCE_GAP_REMAINS",first)
        self.assertIn("POSSIBLE_VOLUNTARY_PRACTICE_NOT_NUTRITION",second)


if __name__=="__main__":
    unittest.main()
