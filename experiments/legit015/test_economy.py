"""MOTIF LEGIT-015 falsifiers for compounding improvement economics.

The point is NOT to assert that improvements compound in reality. We test
when finite resource reinvestment really does produce synergy in a declared
model, when it fails, and whether the planner agrees EXACTLY with a
separately written conventional Bellman and exhaustive policy-tree oracle.

No real-world probability or future speedup is inferred from prior CI.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from itertools import product
import json
import unittest

HERE=Path(__file__).resolve().parent
from economy import (
    HOLD,Economy,Improvement,State,validate,initial,_legal,transition,
    planner,action_values,evaluate,interaction,independent_only,sensitivity,
)
from classical_reference import (
    classical_optimal,tree_optimal,one_step_action_values,no_reinvestment,
)
from evidence_bridge import evidence
_spec=spec_from_file_location("legit015_local_benchmark",HERE/"benchmark.py")
_benchmark=module_from_spec(_spec)
_spec.loader.exec_module(_benchmark)
scenario_cases=_benchmark.scenario_cases
execute=_benchmark.execute


class CompoundingEconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=scenario_cases()

    def test_each_assumption_scenario_is_well_typed(self):
        self.assertEqual(len(self.cases),7)
        for scenario in self.cases.values():
            self.assertEqual(validate(scenario),scenario)

    def test_actual_014_performance_rejection_cannot_be_made_into_return(self):
        prior=evidence()
        self.assertEqual(prior["observed_status"],
                         "HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT")
        self.assertFalse(prior["actual_retention_gate_passed"])
        self.assertFalse(prior["permitted_to_count_as_real_compounding_return"])
        self.assertFalse(prior["future_gain_probability_calibrated_from_this_result"])
        self.assertLess(prior["measured_fraction_vs_earlier_012"],0)
        self.assertGreater(prior["observed_profile_cost_ms"],0)
        self.assertGreater(prior["observed_total_candidate_proof_compile_cost_ms"],0)

    def test_work_generates_useful_output_and_investment_capital(self):
        model=self.cases["CASHFLOW_COMPOUND_AND_UNLOCK"]
        start=initial(model)
        result=transition(model,start,"WORK")
        self.assertEqual(result[0][0],Fraction(1))
        self.assertEqual(result[0][2],Fraction(4))
        self.assertEqual(result[0][1].capital,9)
        self.assertEqual(result[0][1].power,4)

    def test_investing_consumes_a_period_and_real_credit_budget(self):
        model=self.cases["CASHFLOW_COMPOUND_AND_UNLOCK"]
        start=initial(model)
        self.assertNotIn("NEXT_GENERATOR",_legal(model,start))
        next_state=transition(model,start,"FASTER_ENGINE")[0][1]
        self.assertEqual(next_state.period,1)
        self.assertEqual(next_state.capital,0)
        self.assertEqual(next_state.power,8)
        self.assertIn("WORK",_legal(model,next_state))
        self.assertNotIn("NEXT_GENERATOR",_legal(model,next_state))

    def test_compounding_requires_reinvestment_of_produced_capacity(self):
        result=evaluate(self.cases["CASHFLOW_COMPOUND_AND_UNLOCK"])
        self.assertEqual(result["first_action"],"FASTER_ENGINE")
        self.assertEqual(result["best_expected_useful_work"],Fraction(88))
        self.assertEqual(result["baseline_work_only"],Fraction(32))
        path=[s["action"] for s in result["success_path_only_not_expected_trajectory"]]
        self.assertEqual(path[:3],["FASTER_ENGINE","WORK","NEXT_GENERATOR"])
        self.assertEqual(path[3:],["WORK"]*5)

    def test_opportunity_cost_of_waiting_is_explicit(self):
        result=evaluate(self.cases["CASHFLOW_COMPOUND_AND_UNLOCK"])
        values=action_values(self.cases["CASHFLOW_COMPOUND_AND_UNLOCK"])
        self.assertEqual(result["cost_of_forcing_work_before_improvement"],
                         result["best_expected_useful_work"]-values["WORK"])
        self.assertGreater(result["cost_of_forcing_work_before_improvement"],0)

    def test_synergy_is_not_automatically_additive(self):
        sc=self.cases["MULTIPLICATIVE_INTERACTION"]
        effects=interaction(sc,"INDEX_LIBRARY","PROOF_REUSE")
        self.assertEqual(effects["base"],Fraction(32))
        self.assertEqual(effects["A_only"],Fraction(56))
        self.assertEqual(effects["B_only"],Fraction(56))
        self.assertEqual(effects["both"],Fraction(96))
        self.assertEqual(effects["net_synergy"],Fraction(16))

    def test_the_same_resource_model_can_refuse_too_late_improvements(self):
        r=evaluate(self.cases["TOO_LATE_TO_PAY_OFF"])
        self.assertEqual(r["first_action"],"WORK")
        self.assertEqual(r["best_expected_useful_work"],Fraction(4))
        self.assertEqual(r["gain_vs_never_invest"],0)

    def test_certain_failure_is_not_exponential_growth(self):
        r=evaluate(self.cases["CERTAIN_FAILURE_SHOULD_BE_REFUSED"])
        self.assertEqual(r["first_action"],"WORK")
        self.assertEqual(r["best_expected_useful_work"],r["baseline_work_only"])
        self.assertEqual(r["cost_of_forcing_work_before_improvement"],0)

    def test_cap_saturation_refutes_runaway_compound_claim(self):
        model=self.cases["SATURATION_ENDS_COMPOUNDING"]
        r=evaluate(model)
        self.assertLessEqual(max(s["success_branch_power_after"]
                                 for s in r["success_path_only_not_expected_trajectory"]),12)
        self.assertLess(r["best_expected_useful_work"],
                        evaluate(self.cases["MULTIPLICATIVE_INTERACTION"])
                        ["best_expected_useful_work"])

    def test_infrastructure_can_create_option_value_without_direct_speed_gain(self):
        sc=self.cases["CAPABILITY_GATE_UNLOCKS_NEW_ACTION"]
        value=evaluate(sc)
        self.assertEqual(value["first_action"],"BUILD_VERIFIER")
        self.assertGreater(value["best_expected_useful_work"],value["baseline_work_only"])
        first=transition(sc,initial(sc),"BUILD_VERIFIER")[0][1]
        self.assertEqual(first.power,4)
        self.assertIn("COMPOSE_NEW_SOLVER",_legal(sc,first))

    def test_probability_change_can_reverse_the_recommendation(self):
        sc=self.cases["UNCERTAIN_SUCCESS"]
        cases=sensitivity(sc,"RISKY_REWRITE")
        self.assertEqual(len(cases),5)
        self.assertEqual(cases[0]["probability"],"0")
        self.assertEqual(cases[-1]["probability"],"1")
        self.assertEqual(cases[0]["first_action"],"WORK")
        self.assertGreater(Fraction(cases[-1]["best_expected_work"]),
                           Fraction(cases[0]["best_expected_work"]))

    def test_probability_is_exact_and_outcomes_conserve_mass(self):
        sc=self.cases["UNCERTAIN_SUCCESS"]
        branches=transition(sc,initial(sc),"RISKY_REWRITE")
        self.assertEqual(len(branches),2)
        self.assertEqual(sum(p for p,_,_ in branches),Fraction(1))
        self.assertEqual(branches[0][1].power,12)
        self.assertEqual(branches[1][1].power,4)
        self.assertEqual(branches[0][1].capital,0)
        self.assertEqual(branches[1][1].capital,0)

    def test_failed_improvement_cannot_be_repeated_forever(self):
        sc=self.cases["UNCERTAIN_SUCCESS"]
        first=transition(sc,initial(sc),"RISKY_REWRITE")[1][1]
        self.assertNotIn("RISKY_REWRITE",_legal(sc,first))
        self.assertNotIn("DOWNSTREAM",_legal(sc,first))

    def test_independently_written_classical_dp_ties_for_every_scenario(self):
        for name,sc in self.cases.items():
            self.assertEqual(evaluate(sc)["best_expected_useful_work"],
                             classical_optimal(sc),name)

    def test_exhaustive_unguided_policy_tree_ties_in_small_scenarios(self):
        for name in ("UNCERTAIN_SUCCESS","TOO_LATE_TO_PAY_OFF",
                     "CERTAIN_FAILURE_SHOULD_BE_REFUSED"):
            sc=self.cases[name]
            reference,first=tree_optimal(sc)
            result=evaluate(sc)
            self.assertEqual(reference,result["best_expected_useful_work"],name)
            self.assertEqual(first,result["first_action"],name)

    def test_policy_oracle_agrees_on_independent_first_action_values(self):
        for name,sc in self.cases.items():
            got=action_values(sc)
            ref=one_step_action_values(sc)
            self.assertEqual(got,ref,name)
            self.assertEqual(max(got.values()),evaluate(sc)
                             ["best_expected_useful_work"])

    def test_exhaustive_grid_of_small_problem_variants(self):
        for horizon,capital,odds in product((2,3,4),(0,2,4),(0,1,2)):
            scenario=Economy(horizon,capital,2,(
                Improvement("TEST",2,2,odds,2),),8,16)
            ours=evaluate(scenario)
            exhaustive,first=tree_optimal(scenario)
            self.assertEqual(ours["best_expected_useful_work"],exhaustive)
            self.assertEqual(ours["first_action"],first)

    def test_invalid_risk_priors_and_nonfinite_resources_hold(self):
        broken=[
            Economy(11,5,4,(),64,64),
            Economy(2,-1,4,(),64,64),
            Economy(2,0,0,(),64,64),
            Economy(2,5,4,(Improvement("BAD",1,2,2,1),),64,64),
            Economy(2,5,4,(Improvement("BAD",1,2,1,0),),64,64),
            Economy(2,5,4,(Improvement("BAD",1,5),),64,64),
        ]
        for sc in broken:
            with self.assertRaises(HOLD):
                evaluate(sc)

    def test_duplicate_improvements_and_circular_dependencies_hold(self):
        cases=[
            Economy(2,5,4,(Improvement("A",1,2),Improvement("A",1,3))),
            Economy(2,5,4,(Improvement("A",1,2,requires=("B",)),
                           Improvement("B",1,2,requires=("A",)))),
            Economy(2,5,4,(Improvement("A",1,2,requires=("UNKNOWN",)),)),
        ]
        for sc in cases:
            with self.assertRaises(HOLD):
                evaluate(sc)

    def test_disallowed_action_never_consumes_capital(self):
        sc=self.cases["CASHFLOW_COMPOUND_AND_UNLOCK"]
        initial_state=initial(sc)
        for action in ("NEXT_GENERATOR","REJECTED_LEGIT014","PYTHON_EXEC"):
            with self.assertRaises(HOLD):
                transition(sc,initial_state,action)

    def test_no_infinite_reinvestment_and_terminal_work_is_finite(self):
        for sc in self.cases.values():
            r=evaluate(sc)
            self.assertGreaterEqual(r["best_expected_useful_work"],0)
            self.assertLessEqual(r["best_expected_useful_work"],Fraction(
                sc.power_cap*sc.horizon))
            self.assertLessEqual(len(r["success_path_only_not_expected_trajectory"]),
                                 sc.horizon)
            self.assertLessEqual(r["bellman_states_evaluated"],50000)

    def test_benchmark_admits_negative_results_and_never_auto_installs(self):
        out=execute()
        self.assertEqual(out["experiment"],"MOTIF-LEGIT-015")
        self.assertFalse(out["general_superiority_over_classical"])
        self.assertFalse(out["discovery_probabilities_real_world_validated"])
        self.assertEqual(out["state"],"RESEARCH_HOLD")
        self.assertFalse(out["production_improvement_promotion"])
        self.assertEqual(out["automated_external_actions"],0)
        self.assertEqual(out["examples"]["TOO_LATE_TO_PAY_OFF"]["first_action"],"WORK")
        self.assertEqual(out["demonstrations"]["non_additive_synergy"]["net_synergy"],"16")

if __name__=="__main__":
    unittest.main()
