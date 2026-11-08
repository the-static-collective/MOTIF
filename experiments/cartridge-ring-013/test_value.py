"""RING-013 contracts: positive-value smashing, negative-value STOP, open-world evidence.

The names are read-only research intents: every execution in these tests is
a local simulated reversible probe. Even a huge apparent external reward
may not turn into a tool call, authorization, file write or email.
"""
from __future__ import annotations
import ast
from copy import deepcopy
from pathlib import Path
import unittest

import scenario,value


GOOD_PARAMS={
    "information_weight":0.0,"affordance_weight":0.0,
    "risk_weight":0.0,"ambiguity_sensitivity":0.0,
}
MINI_SOURCE={
    "status":"MULTIPLE_SUPPORTED_PERSPECTIVES",
    "supported_worlds":[{"dummy":"not used by value planner"}],
    "other_unmodeled_readings_remain_possible":True,
    "conditional_invariants_within_modeled_worlds":{},
    "optional_discriminator_question_kind":"WHO_IF_ANY_REQUESTED_THIS_EVENT",
}


def synthetic():
    row=scenario.make_cases(split="dev",seed=2026111302,n=1)[0]
    return row["public"],row["hidden"]


class ValueOfActionTests(unittest.TestCase):
    def test_positive_sandbox_experiment_is_selected_and_executed(self):
        p,h=synthetic()
        for name in ("SMASH_A","SMASH_B"):
            p["actions"][name]["affordances"]={w:0 for w in scenario.WORLDS}
        p["actions"]["SMASH_A"]["rewards"]={w:80.0 for w in scenario.WORLDS}
        p["actions"]["SMASH_B"]["rewards"]={w:0.0 for w in scenario.WORLDS}
        picked=value.choose(p,p["proposed_prior"],GOOD_PARAMS)
        self.assertEqual(picked["action"],"SMASH_A")
        result=value.simulate(p,h,MINI_SOURCE,GOOD_PARAMS)
        self.assertEqual(result["steps"][0]["action"],"SMASH_A")
        self.assertGreater(result["realized_utility"],0)
        self.assertTrue(result["all_actions_safe_simulated_only"])
        self.assertTrue(result["no_real_effects"])

    def test_zero_potential_gain_does_not_trigger_curiosity_theater(self):
        p,h=synthetic()
        for name in ("SMASH_A","SMASH_B"):
            p["actions"][name]["rewards"]={w:0.0 for w in scenario.WORLDS}
            p["actions"][name]["affordances"]={w:0 for w in scenario.WORLDS}
        choice=value.choose(p,p["proposed_prior"],GOOD_PARAMS)
        self.assertEqual(choice["action"],"STOP")
        measured=value.simulate(p,h,MINI_SOURCE,GOOD_PARAMS)
        self.assertEqual(measured["internal_smash_count"],0)
        self.assertEqual(measured["action_count"],0)

    def test_information_probe_is_worth_doing_for_conditional_followup(self):
        # Without learning, the risky trial has NEGATIVE expected value.
        # A cheap diagnostic can create positive expected value of trying
        # that same reversible test ONLY if its signal is favorable.
        p,h=synthetic()
        p["proposed_prior"]={
            "USEFUL":0.49,"UNHELPFUL":0.49,"SURPRISE":0.02}
        p["actions"]["SMASH_A"]["rewards"]={
            "USEFUL":10.0,"UNHELPFUL":-11.0,"SURPRISE":0.0}
        p["actions"]["SMASH_A"]["affordances"]={
            w:0 for w in scenario.WORLDS}
        p["actions"]["SMASH_B"]["rewards"]={
            w:0.0 for w in scenario.WORLDS}
        p["actions"]["SMASH_B"]["affordances"]={
            w:0 for w in scenario.WORLDS}
        self.assertLess(
            value.immediate(p["actions"]["SMASH_A"],
                            p["proposed_prior"],GOOD_PARAMS),0)
        self.assertEqual(value.choose(
            p,p["proposed_prior"],GOOD_PARAMS,strategy="GREEDY")["action"],
            "STOP")
        thoughtful=value.choose(p,p["proposed_prior"],GOOD_PARAMS)
        self.assertEqual(thoughtful["action"],"INSPECT")
        self.assertGreater(thoughtful["expected_net"],0)
        simulated=value.simulate(p,h,MINI_SOURCE,GOOD_PARAMS)
        self.assertEqual(simulated["steps"][0]["action"],"INSPECT")
        self.assertTrue(simulated["no_real_effects"])

    def test_effectful_actions_forbidden_even_if_apparent_gain_is_enormous(self):
        p,h=synthetic()
        self.assertEqual(p["actions"]["EXTERNAL_COMMIT"]["permission"],
                         "FORBIDDEN_EXTERNAL_EFFECT")
        output=value.choose(p,p["proposed_prior"],GOOD_PARAMS)
        self.assertNotEqual(output["action"],"EXTERNAL_COMMIT")
        self.assertNotIn("EXTERNAL_COMMIT",
                         [x["action"] for x in output["ranked"]])
        r=value.simulate(p,h,MINI_SOURCE,GOOD_PARAMS)
        self.assertNotIn("EXTERNAL_COMMIT",
                         [x["action"] for x in r["steps"]])

    def test_information_gain_can_be_measured_without_claiming_truth(self):
        p,h=synthetic()
        prior=p["proposed_prior"]
        info=value.information_gain(p["actions"]["INSPECT"],prior)
        self.assertGreater(info,0)
        sig="PASS"
        posterior=value.update(prior,p["actions"]["INSPECT"],sig)
        self.assertAlmostEqual(sum(posterior.values()),1,places=9)
        self.assertGreater(posterior["SURPRISE"],0)

    def test_affordances_are_counted_as_future_options_not_real_authority(self):
        p,h=synthetic()
        b=p["proposed_prior"]
        low=dict(GOOD_PARAMS)
        high=dict(GOOD_PARAMS)
        high["affordance_weight"]=1.0
        gain=value.immediate(p["actions"]["SMASH_A"],b,high)
        no_options=value.immediate(p["actions"]["SMASH_A"],b,low)
        self.assertGreaterEqual(gain,no_options)
        result=value.public_decision(p,MINI_SOURCE,high)
        self.assertTrue(result["never_act_on_semantics_as_external_authority"])
        self.assertFalse(result["external_action_executed"])
        self.assertTrue(result["unmodeled_readings_still_possible"])

    def test_budget_is_bounded_and_no_smash_is_repeated(self):
        p,h=synthetic()
        r=value.simulate(p,h,MINI_SOURCE,{
            "information_weight":0.7,"affordance_weight":1.0,
            "risk_weight":0.0,"ambiguity_sensitivity":0.4,
        })
        actions=[x["action"] for x in r["steps"]]
        self.assertEqual(len(actions),len(set(actions)))
        self.assertLessEqual(len(actions),p["horizon"])
        self.assertGreaterEqual(r["budget_units_remaining"],0)
        self.assertEqual(r["human_interruption_count"],0)

    def test_human_question_is_simulated_only(self):
        p,h=synthetic()
        r=value.simulate(p,h,MINI_SOURCE,GOOD_PARAMS,strategy="ASK_FIRST")
        self.assertEqual(r["human_interruption_count"],0)
        self.assertFalse(any(x["external_effect_executed"] for x in r["steps"]))
        self.assertTrue(r["no_real_effects"])

    def test_source_priors_and_signal_distributions_are_checked(self):
        p,h=synthetic()
        scenario.verify_public(p)
        altered=deepcopy(p)
        altered["proposed_prior"]["USEFUL"]=9
        with self.assertRaises(ValueError):
            scenario.verify_public(altered)
        altered=deepcopy(p)
        altered["actions"]["INSPECT"]["signal_distribution"]["USEFUL"]["PASS"]=8
        with self.assertRaises(ValueError):
            scenario.verify_public(altered)

    def test_unreviewed_value_function_parameters_are_not_allowed(self):
        p,h=synthetic()
        params=dict(GOOD_PARAMS)
        params["unrestricted_tools"]=True
        with self.assertRaises(ValueError):
            value.choose(p,p["proposed_prior"],params)

    def test_prospective_source_challenge_is_not_imported_during_selection(self):
        root=Path(__file__).resolve().parent
        names=[]
        for filename in ("scenario.py","value.py","freeze.py"):
            tree=ast.parse((root/filename).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    names += [alias.name for alias in node.names]
                elif isinstance(node,ast.ImportFrom):
                    names.append(node.module)
        self.assertNotIn("novel",names)
        self.assertNotIn("trial",names)

    def test_author_created_hidden_viability_is_not_in_public_input(self):
        p,h=synthetic()
        self.assertNotIn("true_world",p)
        self.assertNotIn("measurement_seed",p)
        self.assertIn("true_world",h)
        self.assertNotIn("hidden",value.public_decision(
            p,MINI_SOURCE,GOOD_PARAMS))


if __name__=="__main__":
    unittest.main()
