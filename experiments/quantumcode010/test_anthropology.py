"""QC-010: historical precedents inform possibilities, never prove safety."""
from dataclasses import replace
import unittest
from anthropology import (
    SOURCE_INDEX,HistoricalPattern,ContemporaryProblem,compare,samples,report,
)


class AnthropologyTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pat,cls.cases=samples()

    def test_four_sources_include_critical_view(self):
        self.assertEqual(len(SOURCE_INDEX),4)
        self.assertIn("safety_II_critique",SOURCE_INDEX)
        self.assertIn("bricolage_2024",SOURCE_INDEX)

    def test_bricolage_principles_transfer_at_process_level(self):
        x=compare(self.pat,self.cases[0])
        self.assertIn("assemble_parts",x.shared)
        self.assertIn("reassign_existing_materials",x.shared)
        self.assertEqual(x.disposition,
                         "ANALOGICAL_FEASIBILITY_HYPOTHESIS__INSPECT_FIRST")

    def test_historical_pavement_analogy_doesnt_certify_hot_material(self):
        x=compare(self.pat,self.cases[0])
        self.assertIn("actual_heat_rating",x.unverified)
        self.assertIn("unknown_coatings",x.unverified)
        self.assertFalse(x.inferred_safe_to_operate)

    def test_successful_past_cooking_does_not_prove_future_safety(self):
        x=compare(self.pat,self.cases[0])
        self.assertFalse(x.verified_outcome)
        self.assertTrue(any("successful meal" in y for y in x.cautions))

    def test_different_material_context_doesnt_transfer_chemical_safety(self):
        x=compare(self.pat,self.cases[0])
        self.assertIn("food_contact_suitability",x.unverified)

    def test_repair_is_a_new_problem_same_bricolage_mechanisms(self):
        x=compare(self.pat,self.cases[1])
        self.assertIn("assemble_parts",x.shared)
        self.assertIn("electrical_state",x.unverified)
        self.assertEqual(x.disposition,
                         "ANALOGICAL_FEASIBILITY_HYPOTHESIS__INSPECT_FIRST")

    def test_unrelated_pattern_does_not_invent_relevance(self):
        x=compare(self.pat,self.cases[2])
        self.assertEqual(x.disposition,"NO_USEFUL_SHARED_MECHANISM")
        self.assertEqual(x.shared,())

    def test_historical_sources_have_stable_content_pins(self):
        first=compare(self.pat,self.cases[0])
        second=compare(self.pat,self.cases[0])
        self.assertEqual(first.source_pins,second.source_pins)
        self.assertTrue(all(len(x)==64 for x in first.source_pins))

    def test_anonymous_historical_claim_still_requires_source(self):
        broken=replace(self.pat,supporting_sources=("unbacked",))
        with self.assertRaises(ValueError):
            compare(broken,self.cases[0])

    def test_unresolved_safety_does_not_disappear_if_reformulated(self):
        x=compare(self.pat,self.cases[0])
        self.assertGreater(len(x.unverified),0)
        self.assertFalse(x.inferred_safe_to_operate)

    def test_even_close_analogy_without_known_unknowns_needs_new_test(self):
        case=ContemporaryProblem(
            "near_pattern",("test_geometry",),(),())
        x=compare(self.pat,case)
        self.assertEqual(x.disposition,
                         "ANALOGICAL_IDEA_ONLY__INDEPENDENT_TEST_REQUIRED")
        self.assertFalse(x.verified_outcome)

    def test_expert_adaptation_source_not_elevated_to_blanket_authority(self):
        x=compare(self.pat,self.cases[0])
        self.assertNotEqual(x.disposition,"APPROVED_BY_AUTHORITY")
        self.assertNotEqual(x.disposition,"FORBIDDEN_BY_AUTHORITY")

    def test_no_live_human_subject_data_is_assumed(self):
        d=report()
        self.assertFalse(d["safety_assumed_from_historical_precedent"])
        self.assertFalse(d["historical_analogy_automatically_executed"])
        self.assertEqual(d["real_world_interventions"],0)


if __name__=="__main__":
    unittest.main()
