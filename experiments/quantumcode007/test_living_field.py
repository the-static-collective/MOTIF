"""QC-007: actual adversarial tests of living meaning + continuing action field."""
from __future__ import annotations

from dataclasses import replace
import unittest

from living_field import (
    Action, ActionField, ClaimedWitness, FieldView, Meaning, MeaningEdge,
    MeaningField, Path, STATUS, World, action_inventory, aperture, digest,
    dominates, fixture_field, frontier, meets_need, plan, possible_actions,
    reenter, report, run_case, scenario, vector, receive_feedback,
    accrue_from_feedback, diagnose_report, single_step_food_baseline,
)


class LivingFieldChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field=fixture_field()
        cls.inventory=action_inventory()
        cls.results={}
        for name in ("acute","persistent","isolated","stored"):
            w,c=scenario(name)
            cls.results[name]=plan(w,c,cls.inventory)

    def test_all_valid_inventory_specs(self):
        self.assertEqual(len(self.inventory),11)
        for item in self.inventory:
            item.validate()
        self.assertEqual(len({a.id for a in self.inventory}),len(self.inventory))

    def test_meaning_history_is_append_only_not_dictionary_override(self):
        self.assertEqual(len(self.field.meanings),6)
        self.assertEqual(len({m.id for m in self.field.meanings}),6)
        old=self.field
        born=Meaning("bread.new_meaning","bread","new seasonal reinterpretation",
                     frozenset({"ongoing_food"}),frozenset({"access"}),
                     "future-synthetic-witness","INTERPRETATION",11)
        newer=old.add(born)
        self.assertEqual(len(newer.meanings),7)
        self.assertEqual(len(old.meanings),6)
        self.assertEqual(newer.as_of(10).receipt(),old.receipt())
        self.assertNotEqual(newer.receipt(),old.receipt())

    def test_duplicate_or_backdated_meaning_is_refused(self):
        with self.assertRaises(ValueError):
            self.field.add(self.field.meanings[0])
        backdated=Meaning("extra","bread","test",
                         frozenset(),frozenset(),"receipt","HYPOTHESIS",2)
        with self.assertRaises(ValueError):
            self.field.add(backdated)

    def test_cannot_add_meaning_without_witness_or_carrier(self):
        no_provenance=Meaning("missing","bread","description",frozenset(),
                              frozenset(),"","HYPOTHESIS",12)
        with self.assertRaises(ValueError):
            self.field.add(no_provenance)
        no_carrier=replace(no_provenance,witness_id="witness",carrier="")
        with self.assertRaises(ValueError):
            self.field.add(no_carrier)

    def test_tension_is_retained_not_retyped_as_evidence(self):
        self.assertIn("TENSIONS",{edge.relationship for edge in self.field.links})
        with self.assertRaises(ValueError):
            self.field.relate(MeaningEdge("bread.fasting","bread.nutrition",
                                          "PROVES", "fiction",11))

    def test_relation_cannot_predate_meanings(self):
        bad=MeaningEdge("bread.fasting","bread.nutrition","TENSIONS",
                        "fake-timestamp",1)
        with self.assertRaises(ValueError):
            self.field.relate(bad)

    def test_old_snapshot_never_rewrites_earlier_interpretation(self):
        self.assertEqual(len(self.field.as_of(3).meanings),3)
        self.assertEqual(len(self.field.as_of(3).links),0)
        self.assertEqual(len(self.field.as_of(10).links),4)
        self.assertEqual(self.field.meanings[0].phrase,
                         "bread as sustenance")

    def test_relevance_aperture_is_a_field_not_single_decoder(self):
        w,c=scenario("acute")
        view=aperture(self.field,c,possible_actions(w,self.inventory,(),c))
        ids={m.meaning_id for m in view.meanings}
        self.assertIn("bread.nutrition",ids)
        self.assertIn("bread.table",ids)
        self.assertIn("bread.continuity",ids)
        self.assertGreater(len(ids),2)
        self.assertTrue(view.field_receipt)

    def test_persistent_context_reweighs_but_never_discards_history(self):
        wa,ca=scenario("acute")
        wp,cp=scenario("persistent")
        va=aperture(self.field,ca,possible_actions(wa,self.inventory,(),ca))
        vp=aperture(self.field,cp,possible_actions(wp,self.inventory,(),cp))
        self.assertEqual(va.field_receipt,vp.field_receipt)
        self.assertEqual(len(self.field.meanings),6)
        self.assertIn("bread.continuity",
                      {m.meaning_id for m in vp.meanings})

    def test_action_aperture_retains_full_relation_trace(self):
        w,c=scenario("acute")
        view=aperture(self.field,c,possible_actions(w,self.inventory,(),c))
        self.assertTrue(any(e.relationship=="TENSIONS" for e in view.relations))
        self.assertTrue(any(e.relationship=="POSSIBLE_ROUTE"
                            for e in view.relations))

    def test_reinterpretation_may_change_view_without_changing_past_receipt(self):
        before=self.field
        m=Meaning("bread.new_route","bread","a newly noticed food-share relation",
                  frozenset({"urgent_food"}),frozenset({"connect"}),
                  "fixture:new_link", "HYPOTHESIS",11)
        grown=before.add(m)
        grown=grown.relate(MeaningEdge("bread.new_route","bread.continuity",
                                      "REINTERPRETS","fixture:later-reading",12))
        w,c=scenario("acute")
        old=aperture(before,c,possible_actions(w,self.inventory,(),c))
        now=aperture(grown,c,possible_actions(w,self.inventory,(),c))
        self.assertNotEqual(old.field_receipt,now.field_receipt)
        self.assertNotIn("bread.new_route",{x.meaning_id for x in old.meanings})
        self.assertIn("bread.new_route",{x.meaning_id for x in now.meanings})
        self.assertEqual(grown.as_of(10).receipt(),before.receipt())

    def test_incompatible_context_has_no_singular_forced_interpretation(self):
        c=ActionField("other","ACUTE",frozenset({"galactic_navigation"}),
                      5,0,0,0)
        empty=aperture(self.field,c,())
        self.assertFalse(empty.meanings)
        self.assertEqual(len(empty.unused_meanings),6)

    def test_one_step_food_baseline_works_acute_but_cannot_create_continuity(self):
        immediate_world,immediate_context=scenario("acute")
        ongoing_world,ongoing_context=scenario("persistent")
        now=single_step_food_baseline(immediate_world,immediate_context,self.inventory)
        ongoing=single_step_food_baseline(ongoing_world,ongoing_context,self.inventory)
        self.assertEqual(now["selected"],"community_table")
        self.assertTrue(now["meets_need"])
        self.assertFalse(ongoing["meets_need"])
        self.assertEqual(ongoing["modelled_future_days"],0)
        self.assertGreater(len(self.results["persistent"].viable_paths),0)

    def test_one_step_baseline_is_labeled_not_a_strong_comparator(self):
        cases=report()["cases"]
        self.assertIn("one_step_baseline",cases["acute"])
        self.assertIn("one_step_baseline",cases["persistent"])
        self.assertFalse(cases["persistent"]["one_step_baseline"]["meets_need"])

    def test_acute_and_persistent_are_distinct_goal_conditions(self):
        _,acute=scenario("acute")
        _,chronic=scenario("persistent")
        self.assertEqual(acute.min_recurring_days,0)
        self.assertEqual(chronic.min_recurring_days,7)
        self.assertLess(acute.deadline_minutes,chronic.deadline_minutes)

    def test_acute_multiple_paths_to_nourishment(self):
        result=self.results["acute"]
        self.assertEqual(result.status,"SIMULATED_OPTIONS_FOUND")
        sequences={p.action_ids for p in result.viable_paths}
        self.assertIn(("community_table",),sequences)
        self.assertIn(("contact_neighbor","eat_available_food"),sequences)
        self.assertTrue(all(p.state.meals_today>=1 for p in result.viable_paths))

    def test_pareto_does_not_force_away_valuable_tied_alternatives(self):
        w=World(meals_today=1)
        a=Path(("a",),w,15,0,0,"old-a")
        b=Path(("b",),w,15,0,0,"old-b")
        c=Path(("c",),w,20,0,0,"old-c")
        selected=frontier((a,b,c))
        self.assertIn(a,selected)
        self.assertIn(b,selected)
        self.assertNotIn(c,selected)
        self.assertEqual(len(selected),2)

    def test_pareto_retains_incomparable_fast_vs_durable(self):
        a=Path(("a",),World(meals_today=1),15,0,0,"first")
        b=Path(("b",),World(meals_today=1,recurring_days=7),40,0,0,"second")
        self.assertFalse(dominates(a,b))
        self.assertFalse(dominates(b,a))
        self.assertEqual(len(frontier((a,b))),2)

    def test_no_unsafe_food_substitutes(self):
        for result in self.results.values():
            for p in result.viable_paths:
                self.assertNotIn("fast_instead_of_food",p.action_ids)
                self.assertNotIn("unverified_foraging",p.action_ids)
        for candidate in self.inventory:
            if candidate.id in ("fast_instead_of_food","unverified_foraging"):
                self.assertFalse(candidate.permitted(World()))

    def test_breathing_exercise_does_not_count_as_nourishment(self):
        item=next(a for a in self.inventory if a.id=="breathing_focus")
        next_state=item.transition(World())
        self.assertEqual(next_state.meals_today,0)
        self.assertEqual(next_state.recurring_days,0)
        self.assertEqual(next_state.stress_tools,1)

    def test_preconditions_create_new_options(self):
        w,c=scenario("persistent")
        enabled={a.id for a in possible_actions(w,self.inventory,(),c)}
        self.assertNotIn("enroll_recurring_pickup",enabled)
        link=next(a for a in self.inventory if a.id=="contact_neighbor")
        linked=link.transition(w)
        afterward={a.id for a in possible_actions(linked,self.inventory,
                                                    ("contact_neighbor",),c)}
        self.assertIn("enroll_recurring_pickup",afterward)
        self.assertIn("eat_available_food",afterward)
        self.assertNotEqual(w,linked)

    def test_long_run_food_access_needs_action_chain(self):
        result=self.results["persistent"]
        self.assertEqual(result.status,"SIMULATED_OPTIONS_FOUND")
        self.assertGreater(len(result.viable_paths),0)
        self.assertTrue(all(p.state.meals_today>=1 and
                            p.state.recurring_days>=7
                            for p in result.viable_paths))
        self.assertTrue(any("enroll_recurring_pickup" in p.action_ids
                            for p in result.viable_paths))

    def test_immediate_meal_alone_does_not_solve_persistent_access(self):
        community=next(a for a in self.inventory if a.id=="community_table")
        after=community.transition(World())
        self.assertEqual(after.meals_today,1)
        self.assertEqual(after.recurring_days,0)
        _,c=scenario("persistent")
        p=Path(("community_table",),after,35,0,0,"source")
        self.assertFalse(meets_need(p,c))

    def test_synthetic_success_never_declares_a_terminal_endpoint(self):
        result=self.results["persistent"]
        self.assertEqual(len(result.continuations),len(result.pareto_paths))
        self.assertTrue(all(p.status==STATUS for p in result.pareto_paths))
        self.assertTrue(any(options for _,options in result.continuations))

    def test_blocked_context_holds_without_faking_food(self):
        result=self.results["isolated"]
        self.assertEqual(result.status,"HOLD_NO_SAFE_COMPLETE_PATH")
        self.assertEqual(len(result.viable_paths),0)
        self.assertGreaterEqual(result.partial_paths,1)

    def test_action_plan_is_not_observation(self):
        root=self.results["acute"]
        example=root.pareto_paths[0]
        self.assertEqual(reenter(example,None).state_label(),
                         "COUNTERFACTUAL_ONLY")
        self.assertFalse(root.exhausted)

    def test_source_pinned_attestation_does_not_become_independent_truth(self):
        path=self.results["acute"].pareto_paths[0]
        claim=ClaimedWitness(path.parent_receipt,path.action_ids[-1],
                             path.state.receipt(),"some-human-testimony")
        converted=reenter(path,claim)
        self.assertEqual(converted.state_label(),"CLAIMED_NOT_VERIFIED")
        self.assertEqual(converted.preview,path)
        self.assertEqual(converted.claim.classification,
                         "USER_ATTESTED_NOT_INDEPENDENTLY_VERIFIED")

    def test_unlinked_claim_is_refused(self):
        path=self.results["acute"].pareto_paths[0]
        claim=ClaimedWitness("counterfeit",path.action_ids[-1],
                             path.state.receipt(),"source")
        with self.assertRaises(ValueError):
            reenter(path,claim)
        changed=replace(claim,before_receipt=path.parent_receipt,
                        after_receipt="spoof")
        with self.assertRaises(ValueError):
            reenter(path,changed)

    def test_fake_actual_event_is_not_generated_by_planner(self):
        result=self.results["acute"]
        self.assertFalse(hasattr(result,"actual_execution"))
        for p in result.viable_paths:
            self.assertEqual(p.status,STATUS)

    def test_fair_path_budget_exhaustion_is_explicit(self):
        w,c=scenario("persistent")
        result=plan(w,c,self.inventory,node_cap=3)
        self.assertTrue(result.exhausted)
        self.assertEqual(result.status,"HOLD_BUDGET_EXHAUSTED")
        self.assertLessEqual(result.nodes,3)

    def test_max_depth_is_a_horizon_not_a_global_end(self):
        for p in self.results["persistent"].viable_paths:
            self.assertLessEqual(len(p.action_ids),3)
        self.assertTrue(all(p.minutes<=180 for p in
                            self.results["persistent"].viable_paths))

    def test_budget_is_checked_cumulatively(self):
        w=World(budget=10,food_in_hand=False,kitchen=True)
        _,c=scenario("stored")
        x=plan(w,c,self.inventory)
        for p in x.viable_paths:
            self.assertLessEqual(p.spent,c.budget_limit)
            self.assertLessEqual(p.minutes,c.deadline_minutes)

    def test_action_identity_cannot_repeat_indefinitely(self):
        for result in self.results.values():
            for p in result.viable_paths:
                self.assertEqual(len(p.action_ids),len(set(p.action_ids)))

    def test_inventory_invalid_actions_are_rejected(self):
        bad=Action("free_meal","nourish",-1,0,0)
        w,c=scenario("acute")
        with self.assertRaises(ValueError):
            plan(w,c,self.inventory+(bad,))
        duplicate=self.inventory+(self.inventory[0],)
        with self.assertRaises(ValueError):
            plan(w,c,duplicate)

    def test_user_scenarios_are_predeclared_toy_not_local_services(self):
        r=report()
        self.assertEqual(r["fact_origin"],"RESEARCHER_AUTHORED_TOY_WORLD")
        self.assertFalse(r["real_world_food_provision_verified"])
        self.assertEqual(r["external_actions"],0)
        self.assertTrue(r["no_terminal_success_claim"])
        self.assertFalse(r["mathematical_superiority_demonstrated"])

    def test_field_and_path_result_each_have_replayable_hashes(self):
        first=self.field.receipt()
        second=fixture_field().receipt()
        self.assertEqual(first,second)
        self.assertEqual(self.results["acute"].source_receipt,World().receipt())
        self.assertEqual(
            tuple(p.receipt() for p in self.results["acute"].pareto_paths),
            tuple(p.receipt() for p in plan(*scenario("acute"),self.inventory).pareto_paths))

    def test_partial_scenario_output_does_not_mark_success(self):
        case=run_case("isolated")
        self.assertEqual(case["paths_meeting_synthetic_need"],0)
        self.assertEqual(case["nondominated_paths"],0)
        self.assertFalse(case["unsafe_substitute_admitted"])

    def test_report_contains_multiple_distinct_time_horizons(self):
        r=report()
        self.assertEqual(set(r["cases"]),{"acute","persistent","isolated","stored"})
        self.assertTrue(all(x["suppressed_pareto_disclosure"]>=0 for x in r["cases"].values()))
        self.assertGreaterEqual(r["cases"]["acute"]["paths_meeting_synthetic_need"],2)
        self.assertGreaterEqual(r["cases"]["persistent"]["paths_meeting_synthetic_need"],2)

    def test_feedback_records_surprise_without_overwriting_a_past_path(self):
        path=self.results["acute"].pareto_paths[0]
        failed=replace(path.state,meals_today=0)
        record=receive_feedback(path,failed,"fixture:food-did-not-arrive",
                                path.parent_receipt)
        self.assertTrue(record.disagrees)
        note=diagnose_report(path,record)
        self.assertEqual(note["status"],"HOLD_MODEL_REVIEW")
        self.assertEqual(note["prediction_preserved"],path.receipt())
        self.assertFalse(note["reported_as_fact"])

    def test_reported_agreement_is_not_external_verification(self):
        path=self.results["acute"].pareto_paths[0]
        record=receive_feedback(path,path.state,"fixture:claim",
                                path.parent_receipt)
        self.assertFalse(record.disagrees)
        note=diagnose_report(path,record)
        self.assertEqual(note["status"],"AGREEMENT_REPORTED_NOT_VERIFIED")

    def test_feedback_can_accrue_a_cautious_new_meaning_not_a_rewrite(self):
        before=self.field
        path=self.results["acute"].pareto_paths[0]
        feedback=receive_feedback(path,replace(path.state,meals_today=0),
                                  "fixture:missed-supper",path.parent_receipt)
        expanded=accrue_from_feedback(
            before,"bread.nutrition",feedback,
            "bread.failed-route","an offered meal may not arrive",11,
            frozenset({"urgent_food","ongoing_food"}),
            frozenset({"connect","access"}))
        self.assertEqual(len(expanded.meanings),len(before.meanings)+1)
        self.assertEqual(expanded.meanings[-1].kind,"HYPOTHESIS")
        self.assertEqual(expanded.meanings[-1].witness_id,feedback.seal())
        self.assertEqual(expanded.as_of(10).receipt(),before.receipt())
        self.assertEqual(len(expanded.links),len(before.links)+1)
        self.assertEqual(expanded.links[-1].relationship,"REINTERPRETS")

    def test_unsupported_feedback_cannot_create_meaning(self):
        path=self.results["acute"].pareto_paths[0]
        with self.assertRaises(ValueError):
            receive_feedback(path,path.state,"","counterfeit")
        claim=receive_feedback(path,path.state,"fixture:ok",path.parent_receipt)
        with self.assertRaises(ValueError):
            accrue_from_feedback(self.field,"nonexistent",claim,
                                 "new","fake",11,frozenset(),frozenset())
        with self.assertRaises(ValueError):
            accrue_from_feedback(self.field,"bread.nutrition",claim,
                                 "new","backdated",1,frozenset(),frozenset())

    def test_feedback_cannot_be_moved_to_another_prediction(self):
        one,two=self.results["acute"].pareto_paths[:2]
        record=receive_feedback(one,one.state,"fixture:first",one.parent_receipt)
        with self.assertRaises(ValueError):
            diagnose_report(two,record)

    def test_retrospective_meaning_does_not_claim_past_prediction(self):
        path=self.results["acute"].pareto_paths[0]
        feedback=receive_feedback(path,path.state,"fixture:later",
                                  path.parent_receipt)
        expanded=accrue_from_feedback(
            self.field,"bread.table",feedback,
            "bread.later-reading","new meaning after the event",11,
            frozenset({"community"}),frozenset({"connect"}))
        self.assertNotIn("bread.later-reading",
                         {m.id for m in expanded.as_of(10).meanings})
        self.assertIn("bread.later-reading",{m.id for m in expanded.meanings})

    def test_no_hidden_claim_that_modelled_access_is_guaranteed(self):
        for item in self.inventory:
            if item.id in ("enroll_recurring_pickup","pantry_pickup",
                           "contact_neighbor","weekly_food_sharing"):
                self.assertTrue("Hypothetical" in item.description or
                                "assum" in item.description or
                                "no availability guarantee" in item.description)

    def test_context_unknown_is_explicit_error_not_invented_need(self):
        with self.assertRaises(ValueError):
            scenario("world_peace_and_hunger")

    def test_not_an_unbounded_or_self_installing_agent(self):
        r=report()
        self.assertTrue(r["local_planner_only"])
        self.assertFalse(any(key in r for key in
                             ("deployed","tool_calls","real_outcomes","autonomy_earned")))


if __name__=="__main__":
    unittest.main()
