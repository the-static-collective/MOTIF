"""QC-007 reusable typed action network tests beyond food-only scenario."""
from dataclasses import replace
import unittest

from domain_kernel import (
    STATUS, MetricWorld, Objective, Option, Route, nondominated, sample,
    search, meaning_aperture, report, value,
)
from living_field import fixture_field


class DomainNeutralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event=sample("community_gathering")
        cls.equipment=sample("equipment_function")
        cls.event_run=search(*cls.event)
        cls.equipment_run=search(*cls.equipment)

    def test_two_declared_problem_domains_not_one_food_specific_schema(self):
        self.assertEqual({self.event[1].id,self.equipment[1].id},
                         {"community_gathering","equipment_function"})
        self.assertNotEqual({k for k,_ in self.event[0].metrics},
                            {k for k,_ in self.equipment[0].metrics})

    def test_action_plan_finds_two_forms_of_event_meal_provision(self):
        r=self.event_run
        self.assertEqual(r.status,"MODELLED_PATHS")
        self.assertGreater(len(r.paths_meeting_goal),2)
        rows={p.options for p in r.paths_meeting_goal}
        self.assertTrue(any("prepare_meal" in xs for xs in rows))
        self.assertTrue(any("ask_shared_pantry" in xs for xs in rows))
        self.assertTrue(all(p.world.get("meals_prepared")>=8 and
                            p.world.get("invitations")>=8
                            for p in r.paths_meeting_goal))

    def test_event_followup_is_distinct_from_event_occurrence(self):
        r=self.event_run
        self.assertTrue(any(p.world.get("return_contacts")>=5
                            for p in r.paths_meeting_goal))
        self.assertTrue(any(p.world.get("return_contacts")==0
                            for p in r.paths_meeting_goal))
        self.assertTrue(all(p.world.get("meals_prepared")>=8
                            for p in r.paths_meeting_goal))

    def test_equipment_works_via_different_routes(self):
        r=self.equipment_run
        self.assertEqual(r.status,"MODELLED_PATHS")
        options={p.options for p in r.paths_meeting_goal}
        self.assertIn(("borrow_backup_route",),options)
        self.assertTrue(any("test_local_signal" in x for x in options))
        self.assertTrue(any("repair_port" in x for x in options))

    def test_domain_local_definitions_do_not_change_planner(self):
        # One exact function (search) is used for both domains.
        self.assertGreater(self.event_run.expanded_nodes,4)
        self.assertGreater(self.equipment_run.expanded_nodes,4)
        self.assertTrue(all(p.status==STATUS for p in
                            self.event_run.paths_meeting_goal +
                            self.equipment_run.paths_meeting_goal))

    def test_full_pareto_set_is_not_one_forced_strategy(self):
        self.assertGreater(len(self.event_run.frontier),1)
        self.assertGreater(len(self.equipment_run.frontier),1)
        _,goal,_=self.event
        for i,a in enumerate(self.event_run.frontier):
            for b in self.event_run.frontier[i+1:]:
                x,y=value(a,goal),value(b,goal)
                self.assertFalse(all(m>=n for m,n in zip(x,y)) and x!=y)

    def test_nonterminal_actions_are_available_after_goal(self):
        for run in (self.event_run,self.equipment_run):
            self.assertEqual(len(run.continuations),len(run.frontier))
            self.assertTrue(any(options for _,options in run.continuations))

    def test_tie_routes_preserve_different_action_histories(self):
        goal=self.equipment[1]
        w=MetricWorld((("available_route",1),))
        a=Route(("a",),w,20,0,0,"r1")
        b=Route(("b",),w,20,0,0,"r2")
        keep=nondominated((a,b),goal)
        self.assertEqual(len(keep),2)
        self.assertNotEqual(keep[0].receipt(),keep[1].receipt())

    def test_action_requirements_generate_future_affordances(self):
        w,goal,actions=self.equipment
        repair=next(x for x in actions if x.id=="repair_port")
        self.assertIsNone(repair.next(w))
        inspect=next(x for x in actions if x.id=="inspect_connector")
        part=next(x for x in actions if x.id=="obtain_compatible_part")
        w2=part.next(inspect.next(w))
        self.assertIsNotNone(repair.next(w2))
        self.assertGreater(repair.next(w2).get("available_route"),0)

    def test_negative_resource_inventory_is_refused(self):
        with self.assertRaises(ValueError):
            MetricWorld((("coin",2),("coin",3)))
        with self.assertRaises(ValueError):
            MetricWorld((("hours",-1),))
        w=MetricWorld((("coin",1),))
        self.assertIsNone(w.change((("coin",-2),)))

    def test_no_fake_user_data_or_new_service_instantiation(self):
        result=report()
        self.assertTrue(result["model_starts_from_researcher_authored_actions"])
        self.assertEqual(result["external_actions"],0)
        self.assertFalse(result["domains"]["community_gathering"]["reported_as_reality"])
        self.assertFalse(result["domains"]["equipment_function"]["reported_as_reality"])

    def test_predeclared_resource_and_time_budget_cannot_be_spent_twice(self):
        for initial,goal,options in (self.event,self.equipment):
            for p in search(initial,goal,options).paths_meeting_goal:
                self.assertLessEqual(p.minutes,goal.max_minutes)
                self.assertLessEqual(p.dollars,goal.max_dollars)
                self.assertLessEqual(len(p.options),goal.max_depth)
                self.assertEqual(len(p.options),len(set(p.options)))

    def test_illegal_option_schema_holds(self):
        initial,goal,actions=self.event
        forbidden=Option("generate_infinite_meals",(),
                         (("meals_prepared",999999),),0)
        with self.assertRaises(ValueError):
            search(initial,goal,actions+(forbidden,))
        with self.assertRaises(ValueError):
            search(initial,goal,actions+(actions[0],))

    def test_limited_exploration_does_not_pretend_to_complete_search(self):
        initial,goal,actions=self.event
        r=search(initial,goal,actions,node_limit=2)
        self.assertEqual(r.status,"HOLD_BUDGET")
        self.assertLessEqual(r.expanded_nodes,2)

    def test_hypothesis_based_meaning_relevance_preserves_ledger(self):
        field=fixture_field()
        before=field.receipt()
        _,context,inventory=self.event
        v=meaning_aperture(field,context,inventory)
        self.assertEqual(v["source"],before)
        self.assertEqual(v["unchanged_history"],6)
        self.assertGreater(len(v["relevant"]),1)
        self.assertEqual(field.receipt(),before)

    def test_unknown_problem_never_autogenerates_services(self):
        with self.assertRaises(ValueError):
            sample("molecular_quantum_economy")

    def test_action_contract_holds_no_real_execution_claim(self):
        for _,_,inventory in (self.event,self.equipment):
            self.assertTrue(all(op.claim=="TOY_ASSUMPTION_UNVERIFIED"
                                for op in inventory))

    def test_generic_applicability_rejects_mismatched_goal_type(self):
        initial,goal,inventory=self.event
        bad=replace(goal,max_depth=20)
        with self.assertRaises(ValueError):
            search(initial,bad,inventory)


if __name__=="__main__":
    unittest.main()
