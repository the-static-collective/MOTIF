"""QC-010 falsification of risk catalogue worship and survival romanticism."""
from dataclasses import replace
import unittest

from traction import (
    YES, NO, UNKNOWN, Witness, Situation, Hazard, Action, Feedback,
    oven_scene, oven_hazards, oven_candidates, repair_candidates,
    assess, reenter, benchmark,
)


class PracticalTractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene=oven_scene()
        cls.options=oven_candidates()
        cls.hazards=oven_hazards()
        cls.states={x.id:assess(x,cls.scene,cls.hazards) for x in cls.options}

    def test_no_reliable_old_oven_is_not_a_no_action_state(self):
        self.assertEqual(self.scene.at("conventional_oven_usable"),NO)
        self.assertIn("CANDIDATE_SAFE_TO_INSPECT_ONLY",
                      {s.verdict for s in self.states.values()})

    def test_cold_probes_remain_possible_without_certified_hot_masonry(self):
        self.assertEqual(self.states["cold_fit_masonry"].verdict,
                         "CANDIDATE_SAFE_TO_INSPECT_ONLY")
        self.assertEqual(self.states["draw_new_layout"].verdict,
                         "CANDIDATE_SAFE_TO_INSPECT_ONLY")

    def test_hot_operation_is_not_cleared_by_successful_cold_fit(self):
        hot=self.states["operate_proposed_oven"]
        self.assertEqual(hot.verdict,"REFUSE_UNMITIGATED_SEVERE_HAZARD")
        self.assertIn("unknown_hot_masonry",hot.hazards)
        self.assertIn("unverified_metal_surface",hot.hazards)

    def test_manual_memory_of_cooking_does_not_prove_thermal_safety(self):
        prior=self.states["cold_fit_masonry"]
        trail=reenter(prior,Feedback(
            prior.action,"WORKED",("cold_fit_assembled",),
            "fixture:person_says_it_fit","USER_REPORT"),self.options)
        self.assertEqual(trail.next_status,
                         "FUNCTION_OBSERVED_SAFETY_UNVERIFIED")
        self.assertTrue(trail.unverified_safety)
        self.assertEqual(self.states["operate_proposed_oven"].verdict,
                         "REFUSE_UNMITIGATED_SEVERE_HAZARD")

    def test_a_successful_functional_trial_creates_next_questions(self):
        trail=reenter(self.states["cold_fit_masonry"],Feedback(
            "cold_fit_masonry","WORKED",("pieces_assembled",),
            "fixture:observation","SIMULATED"),self.options)
        self.assertIn("identify_new_reusable_capability",trail.hypotheses)
        self.assertIn("check_material_health_and_exposure",trail.hypotheses)

    def test_cold_fit_failure_reopens_alternatives_not_terminal_hold(self):
        trail=reenter(self.states["cold_fit_masonry"],Feedback(
            "cold_fit_masonry","FAILED",(),
            "fixture:fit_didnt_hold","SIMULATED"),self.options)
        self.assertEqual(trail.next_status,"REOPEN_ALTERNATIVE_ACTION_FIELD")
        self.assertIn("draw_new_layout",trail.hypotheses)
        self.assertIn("inspect_thermal_compatibility",trail.hypotheses)
        self.assertNotIn("cold_fit_masonry",trail.hypotheses)

    def test_uncertain_result_proposes_smaller_observation(self):
        trail=reenter(self.states["cold_fit_masonry"],Feedback(
            "cold_fit_masonry","INCONCLUSIVE",(),
            "fixture:insufficient_measure","SIMULATED"),self.options)
        self.assertEqual(trail.next_status,
                         "REQUIRE_SMALLER_OR_BETTER_MEASURED_PROBE")
        self.assertIn("change_observation_method",trail.hypotheses)

    def test_precondition_absence_does_not_make_up_external_equipment(self):
        x=self.states["find_alternative_cooker"]
        self.assertEqual(x.verdict,"ASK_FOR_FACTS")
        self.assertIn("safe_alternative_exists",x.unknown)

    def test_unsatisfied_precondition_is_blocked_not_inferred(self):
        s=self.scene.observe("safe_alternative_exists",NO,"fixture:no")
        x=assess(self.options[-1],s,self.hazards)
        self.assertEqual(x.verdict,"BLOCKED_PRECONDITION")

    def test_rated_material_evidence_clears_only_named_hazards(self):
        s=(self.scene
           .observe("masonry_materials_verified",YES,"fixture:reviewed_source")
           .observe("food_contact_material_verified",YES,"fixture:reviewed_source")
           .observe("clearance_verified",YES,"fixture:reviewed_source")
           .observe("fire_location_unsafe",NO,"fixture:clear_site"))
        result=assess(next(x for x in self.options if
                           x.id=="operate_proposed_oven"),s,self.hazards)
        self.assertEqual(result.verdict,"CONDITIONAL_REVIEW_NOT_EXECUTION")
        self.assertFalse(result.executed)
        self.assertFalse(result.hazards)

    def test_unresolved_fire_location_is_not_fictional_clearance(self):
        s=(self.scene
           .observe("masonry_materials_verified",YES,"fixture:reviewed_source")
           .observe("food_contact_material_verified",YES,"fixture:reviewed_source")
           .observe("clearance_verified",YES,"fixture:reviewed_source"))
        x=assess(next(y for y in self.options if
                      y.id=="operate_proposed_oven"),s,self.hazards)
        self.assertEqual(x.verdict,"HOLD_UNKNOWN_SEVERE_SAFETY")
        self.assertIn("unsafe_flame_location",x.hazards)

    def test_known_unsafe_fire_location_is_hard_stop(self):
        s=(self.scene
           .observe("fire_location_unsafe",YES,"fixture:hazard"))
        x=assess(next(y for y in self.options if
                      y.id=="operate_proposed_oven"),s,self.hazards)
        self.assertEqual(x.verdict,"REFUSE_UNMITIGATED_SEVERE_HAZARD")
        self.assertIn("unsafe_flame_location",x.hazards)

    def test_valid_hazard_controls_do_not_block_low_exposure_inspection(self):
        self.assertFalse(self.states["inspect_thermal_compatibility"].hazards)
        self.assertEqual(self.states["inspect_thermal_compatibility"].verdict,
                         "CANDIDATE_SAFE_TO_INSPECT_ONLY")

    def test_no_broad_institutional_ban_on_all_reuse(self):
        self.assertGreaterEqual(sum(
            x.verdict=="CANDIDATE_SAFE_TO_INSPECT_ONLY"
            for x in self.states.values()),3)

    def test_report_does_not_confuse_success_with_verified_safe_heat(self):
        r=benchmark()
        self.assertFalse(r["verified_safe_hot_use"])
        self.assertEqual(r["real_world_actions"],0)
        self.assertEqual(r["observed_fit"],
                         "FUNCTION_OBSERVED_SAFETY_UNVERIFIED")

    def test_knowledge_is_not_promoted_to_cause_of_observed_success(self):
        f=Feedback("cold_fit_masonry","WORKED",("fitted",),
                   "fixture:user_report","HISTORICAL_ANALOGY")
        t=reenter(self.states["cold_fit_masonry"],f,self.options)
        self.assertTrue(t.unverified_safety)

    def test_unsupported_success_does_not_rewrite_scene(self):
        pre=self.scene.pin
        reenter(self.states["cold_fit_masonry"],Feedback(
            "cold_fit_masonry","WORKED",("fitted",),
            "fixture:test","SIMULATED"),self.options)
        self.assertEqual(pre,self.scene.pin)

    def test_invalid_observation_cannot_enter_history(self):
        with self.assertRaises(ValueError):
            self.scene.observe("masonry_materials_verified",UNKNOWN,
                               "fixture:guessed")
        with self.assertRaises(ValueError):
            self.scene.observe("masonry_materials_verified",YES,"")

    def test_evidence_receipts_keep_reversals_replayable(self):
        first=self.scene.observe("metal_coating_unverified",NO,
                                 "fixture:identified")
        later=first.observe("metal_coating_unverified",YES,
                            "fixture:coating_discovered")
        self.assertEqual(first.at("metal_coating_unverified"),NO)
        self.assertEqual(later.at("metal_coating_unverified"),YES)
        self.assertEqual(len(later.trail("metal_coating_unverified")),3)
        self.assertEqual(first.history,later.history[:-1])

    def test_earlier_scene_receipt_is_immutable(self):
        earlier=self.scene.pin
        later=self.scene.observe("site_use_permitted",NO,
                                 "fixture:permission_withdrawn")
        self.assertNotEqual(earlier,later.pin)
        self.assertEqual(self.scene.pin,earlier)

    def test_new_lack_of_permission_blocks_fitting(self):
        s=self.scene.observe("site_use_permitted",NO,"fixture:withdrawn")
        result=assess(next(x for x in self.options if
                           x.id=="cold_fit_masonry"),s,self.hazards)
        self.assertEqual(result.verdict,"BLOCKED_PRECONDITION")

    def test_mismatched_feedback_is_rejected(self):
        with self.assertRaises(ValueError):
            reenter(self.states["cold_fit_masonry"],Feedback(
                "draw_new_layout","WORKED",(),
                "fixture:wrong","SIMULATED"),self.options)

    def test_no_external_actions_ever_supposed(self):
        self.assertTrue(all(not state.executed
                            for state in self.states.values()))

    def test_dry_fitting_is_reversible_but_open_fire_is_not(self):
        fit=next(x for x in self.options if x.id=="cold_fit_masonry")
        burn=next(x for x in self.options if
                  x.id=="operate_proposed_oven")
        self.assertTrue(fit.reversible)
        self.assertFalse(burn.reversible)
        self.assertEqual(fit.exposure,"REVERSIBLE")
        self.assertEqual(burn.exposure,"HIGH_EXPOSURE")

    def test_unreviewed_hazard_definition_refuses(self):
        h=replace(self.hazards[0],severity="MADE_UP")
        with self.assertRaises(ValueError):
            assess(self.options[3],self.scene,(h,))

    def test_invalid_high_exposure_action_reversibility_refuses(self):
        wrong=replace(self.options[3],reversible=True)
        with self.assertRaises(ValueError):
            assess(wrong,self.scene,self.hazards)

    def test_repair_is_same_kernel_not_a_fire_specific_planner(self):
        state=Situation().observe(
            "broken_equipment_present",YES,"fixture:broken_part").observe(
            "safe_to_handle",YES,"fixture:disconnected")
        results=[assess(a,state) for a in repair_candidates()]
        self.assertEqual(len(results),3)
        self.assertEqual(results[0].verdict,
                         "CANDIDATE_SAFE_TO_INSPECT_ONLY")
        self.assertEqual(results[1].verdict,
                         "CANDIDATE_SAFE_TO_INSPECT_ONLY")
        self.assertEqual(results[2].verdict,"ASK_FOR_FACTS")

    def test_repair_failure_reopens_peer_actions(self):
        state=Situation().observe("broken_equipment_present",YES,
                                  "fixture:broken")
        first=assess(repair_candidates()[0],state)
        x=reenter(first,Feedback(first.action,"FAILED",(),
                                  "fixture:no_failure_found","SIMULATED"),
                  repair_candidates())
        self.assertEqual(x.next_status,"REOPEN_ALTERNATIVE_ACTION_FIELD")
        self.assertIn("seek_other_part",x.hypotheses)

    def test_observational_sources_are_not_equivalent_to_expertise(self):
        source_classes={"FIELD_WITNESS","TECHNICAL_GUIDANCE",
                        "HISTORICAL_ANALOGY","BENCH_OBSERVATION"}
        self.assertEqual(len(source_classes),4)
        # Their statuses remain separately addressable in Witness.kind.
        x=Witness("fit",YES,"fixture:old_analogy",
                  "HISTORICAL_ANALOGY",1)
        self.assertEqual(x.kind,"HISTORICAL_ANALOGY")
        self.assertNotEqual(x.pin,Witness("fit",YES,"fixture:old_analogy",
                                         "FIELD_WITNESS",1).pin)

    def test_only_defined_feedback_types_accepted(self):
        with self.assertRaises(ValueError):
            Feedback("fit","SAFE_FOR_LIFE",(),"fixture:claim",
                     "SIMULATED").check()

    def test_no_implicit_safety_from_antiquity_or_survival(self):
        x=assess(next(y for y in self.options if
                      y.id=="operate_proposed_oven"),self.scene,self.hazards)
        self.assertNotEqual(x.verdict,"CANDIDATE_SAFE_TO_INSPECT_ONLY")
        self.assertNotEqual(x.verdict,"CONDITIONAL_REVIEW_NOT_EXECUTION")

    def test_usable_future_capability_is_predicted_not_guaranteed(self):
        x=assess(next(y for y in self.options if
                      y.id=="operate_proposed_oven"),self.scene,self.hazards)
        self.assertIn("reusable_cooking_capacity",x.predicted_effects)
        self.assertFalse(x.observed_effects)


if __name__=="__main__":
    unittest.main()
