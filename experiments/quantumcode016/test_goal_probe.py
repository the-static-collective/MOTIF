"""QC-016 goal-relative probe alternatives and epistemic safeguards."""
import unittest
from dataclasses import replace
from goal_probe import (
    Goal,Probe,evaluate,select,dominates,reenter,
    example,report,YES,NO,UNKNOWN,
)


class Dividends(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.goal,cls.probes=example()

    def test_visible_water_is_relevant_where_random_new_tile_isnt(self):
        r=select(self.goal,self.probes)
        verdicts={v.probe_id:v.verdict for v in r["verdicts"]}
        self.assertEqual(verdicts["inspect_known_water"],
                         "CANDIDATE_GOAL_PROBE")
        self.assertEqual(verdicts["wander_to_novel_tile"],
                         "NOT_RELEVANT_TO_MISSING_GOAL")
        self.assertIn("wander_to_novel_tile",r["rejected"])

    def test_unverified_hazard_even_with_high_goal_relevance_blocks(self):
        r=evaluate(self.goal,self.probes[-1])
        self.assertEqual(r.verdict,"BLOCKED_PERMISSION_OR_HAZARD")
        self.assertGreater(r.predicted_dividend,0)

    def test_permission_denied_stays_blocked(self):
        p=replace(self.probes[0],permission=NO)
        self.assertEqual(evaluate(self.goal,p).verdict,
                         "BLOCKED_PERMISSION_OR_HAZARD")

    def test_untested_reachability_causes_hold(self):
        p=replace(self.probes[0],reachable=UNKNOWN)
        self.assertEqual(evaluate(self.goal,p).verdict,
                         "HOLD_UNVERIFIED_ACCESS")

    def test_unassessed_safety_causes_hold(self):
        p=replace(self.probes[0],hazard_assessed=UNKNOWN)
        self.assertEqual(evaluate(self.goal,p).verdict,
                         "HOLD_UNVERIFIED_ACCESS")

    def test_source_not_validated_refuses_to_predict(self):
        p=replace(self.probes[0],source_kind="MADE_UP")
        with self.assertRaises(ValueError):
            evaluate(self.goal,p)

    def test_high_exposure_requires_more_than_permission(self):
        p=replace(self.probes[0],exposure="HIGH")
        self.assertEqual(evaluate(self.goal,p).verdict,
                         "BLOCKED_PERMISSION_OR_HAZARD")

    def test_ordinal_score_is_not_probability_of_success(self):
        r=evaluate(self.goal,self.probes[0])
        self.assertEqual(r.predicted_dividend,3)
        self.assertTrue(r.predicted_not_verified)
        self.assertFalse(r.automatically_executed)

    def test_known_requirement_does_not_incentivize_rechecking(self):
        result=select(self.goal,self.probes,known_facts=("water_access",))
        by={v.probe_id:v.verdict for v in result["verdicts"]}
        self.assertEqual(by["inspect_known_water"],
                         "NOT_RELEVANT_TO_MISSING_GOAL")
        self.assertEqual(by["investigate_quality"],"CANDIDATE_GOAL_PROBE")

    def test_fully_attained_goal_doesnt_keep_searching(self):
        result=select(self.goal,self.probes,known_facts=(
            "water_access","water_source_quality"))
        self.assertFalse(result["pareto_candidate_ids"])
        self.assertTrue(all(x.verdict=="GOAL_ALREADY_OBSERVED"
                            for x in result["verdicts"]))

    def test_equal_pareto_routes_remain_tied_fiber(self):
        a,b=self.probes[0],replace(self.probes[0],id="inspect_known_water_b",
                                   source_ref="fixture:other_verified_access")
        result=select(self.goal,(a,b))
        self.assertEqual(result["pareto_candidate_ids"],
                         ("inspect_known_water","inspect_known_water_b"))

    def test_cheaper_equivalent_probes_dominate(self):
        a=self.probes[0]
        b=replace(a,id="expensive_water_probe",step_cost=3,
                  source_ref="fixture:slower")
        result=select(self.goal,(a,b))
        self.assertEqual(result["pareto_candidate_ids"],(a.id,))

    def test_more_relevance_but_more_cost_preserves_alternatives(self):
        g=Goal("two_requirements",("water_access","water_source_quality"),(),
               2,"fictional:goal")
        a=self.probes[0]
        b=replace(a,id="slow_both",predicted_answers=(
            "water_access","water_source_quality"),step_cost=4)
        result=select(g,(a,b))
        self.assertEqual(len(result["pareto_candidate_ids"]),2)

    def test_mismatched_world_scope_refuses_human_policy_transfer(self):
        p=replace(self.probes[0],domain="HUMAN_CONTEXT_UNVERIFIED")
        with self.assertRaises(ValueError):
            evaluate(self.goal,p)

    def test_future_state_prediction_not_reported_as_observed(self):
        x=evaluate(self.goal,self.probes[0])
        r=reenter(x,(),"test:didnt_find_water")
        self.assertFalse(r.success_proven_in_source_world)
        self.assertEqual(r.actual_external_effects,0)

    def test_source_pinned_feedback_reenters_only_if_witnessed(self):
        x=evaluate(self.goal,self.probes[0])
        r=reenter(x,("water_access",),"game_engine:water_observed")
        self.assertTrue(r.success_proven_in_source_world)
        self.assertEqual(r.world_scope,"GAME_ONLY")

    def test_unrelated_feedback_cannot_masquerade_as_success(self):
        x=evaluate(self.goal,self.probes[0])
        r=reenter(x,("unrelated_terrain",),"test:novel")
        self.assertFalse(r.success_proven_in_source_world)

    def test_blocked_candidate_cannot_receive_success_receipt(self):
        x=evaluate(self.goal,self.probes[-1])
        with self.assertRaises(ValueError):
            reenter(x,("water_access",),"fictional")

    def test_source_ref_mandatory_for_feedback(self):
        x=evaluate(self.goal,self.probes[0])
        with self.assertRaises(ValueError):
            reenter(x,("water_access",),"")

    def test_report_is_non_effectful(self):
        r=report()
        self.assertEqual(r["real_world_actions"],0)
        self.assertEqual(r["gameplay_actions"],0)

if __name__=="__main__":
    unittest.main()
