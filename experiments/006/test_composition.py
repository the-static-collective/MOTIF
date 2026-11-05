"""MOTIF-006: proving macro induction does not bypass primitive checks."""
import unittest
from dataclasses import replace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
from motif002 import F, induce, lessons, scene, explore, Verb, utility
from composition import (Call, Trace, Macro, Inapplicable, checked_apply,
    replay, compile_trace, induce_macros, available_macros, rename_trace,
    bind_prefix, training_traces, two_level_training, root_trace, run_demo)


class CompositeVerbTests(unittest.TestCase):
    def setUp(self):
        self.verbs = induce(lessons())
        self.traces, self.inner, self.outer = two_level_training(self.verbs)
        self.catalog = dict(self.verbs)
        self.catalog[self.inner.id] = self.inner
        self.catalog[self.outer.id] = self.outer
        self.holdout = rename_trace(root_trace(self.verbs),
                          {"Jo": "FreshOwner", "Mira": "FreshTeacher",
                           "bike1": "fresh_Bike1", "bike2": "fresh_Bike2"})
        self.roles = bind_prefix(self.holdout.calls)

    def test_macro_is_inferred_from_several_traces(self):
        self.assertTrue(self.inner.id.startswith("macro-"))
        self.assertTrue(self.outer.id.startswith("macro-"))
        self.assertNotEqual(self.inner.id, self.outer.id)
        self.assertEqual(self.inner.demonstrations, 3)
        self.assertEqual(self.outer.demonstrations, 3)
        self.assertEqual((self.inner.depth, self.outer.depth), (2, 3))
        self.assertIn(self.inner.id, {x.operator for x in self.outer.calls})
        self.assertEqual(len(self.outer.calls), 2)

    def test_holdout_replay_identical_to_primitives(self):
        expanded = replay(self.holdout.before, self.holdout.calls, self.verbs)
        compact = checked_apply(self.holdout.before, self.outer.id,
                                self.roles, self.catalog)
        self.assertEqual(expanded, compact)
        self.assertEqual(utility(compact, self.holdout.before), 24)

    def test_intermediate_synthetic_permission_rechecked(self):
        bike, owner, teacher = "fresh_Bike2", "FreshOwner", "FreshTeacher"
        blocked = self.holdout.before - {F("permits", owner, owner, bike)}
        with self.assertRaises(Inapplicable):
            checked_apply(blocked, self.outer.id, self.roles, self.catalog)
        self.assertEqual(self.holdout.before, self.holdout.before)
        self.assertNotIn(F("usable", bike), blocked)

    def test_all_permissions_removed_never_find_a_macro(self):
        without = frozenset(f for f in self.holdout.before if f[0] != "permits")
        self.assertEqual(list(available_macros(without, self.catalog,
                                              (self.inner.id, self.outer.id))), [])

    def test_missing_tool_blocks_underlying_rewrite(self):
        without = self.holdout.before - {F("tool", "FreshTeacher", "wrench")}
        with self.assertRaises(Inapplicable):
            checked_apply(without, self.outer.id, self.roles, self.catalog)

    def test_source_pinning_rejects_mutated_primitive(self):
        repair = next(v for v in self.verbs.values() if F("usable", "?0") in v.adds)
        tampered = dict(self.catalog)
        tampered[repair.id] = replace(repair, adds=frozenset({F("magical", "?0")}))
        with self.assertRaisesRegex(Inapplicable, "Source operator changed"):
            checked_apply(self.holdout.before, self.outer.id, self.roles, tampered)

    def test_source_pinning_rejects_mutated_macro_body(self):
        forged = dict(self.catalog)
        forged[self.inner.id] = replace(self.inner,
            adds=self.inner.adds | {F("unearned", "?2")})
        with self.assertRaisesRegex(Inapplicable, "Source operator changed"):
            checked_apply(self.holdout.before, self.outer.id, self.roles, forged)

    def test_forged_macro_net_effect_fails(self):
        forged = dict(self.catalog)
        forged[self.outer.id] = replace(self.outer,
            adds=self.outer.adds | {F("unearned", "?3")})
        with self.assertRaisesRegex(Inapplicable, "not reproduced"):
            checked_apply(self.holdout.before, self.outer.id, self.roles, forged)

    def test_type_checks_block_wrong_role_order(self):
        swapped = ("fresh_Bike1", "FreshTeacher", "FreshOwner", "fresh_Bike2")
        with self.assertRaisesRegex(Inapplicable, "mismatched"):
            checked_apply(self.holdout.before, self.outer.id, swapped, self.catalog)

    def test_unchanged_input_world(self):
        prior = self.holdout.before
        checked_apply(prior, self.outer.id, self.roles, self.catalog)
        self.assertEqual(prior, self.holdout.before)
        self.assertNotIn(F("usable", "fresh_Bike1"), prior)

    def test_outcome_disagreement_prevents_learning(self):
        fixture = self.traces[0]
        contradictory = replace(fixture, observed_after=fixture.before)
        with self.assertRaisesRegex(ValueError, "disagrees"):
            compile_trace(contradictory, self.verbs)

    def test_wrong_provenance_prevents_learning(self):
        fixture = self.traces[0]
        with self.assertRaises(ValueError):
            compile_trace(replace(fixture, provenance="REAL_VERIFIED"), self.verbs)

    def test_insufficient_support_does_not_induce(self):
        prefix = self.traces[0]
        training = [Trace(prefix.before, prefix.calls[:2],
                          replay(prefix.before, prefix.calls[:2], self.verbs))]
        self.assertEqual(induce_macros(training, self.verbs), {})
        with self.assertRaises(ValueError):
            induce_macros(training, self.verbs, min_support=1)

    def test_budget_blocks_unbounded_operator_expansion(self):
        with self.assertRaisesRegex(ValueError, "budget"):
            compile_trace(self.traces[0], self.verbs, max_expanded_steps=2)

    def test_self_recursion_fails_closed(self):
        cyclic = dict(self.catalog)
        cyclic[self.inner.id] = replace(self.inner,
            calls=(Call(self.inner.id, ("?0", "?1", "?2")),))
        with self.assertRaisesRegex(Inapplicable, "cycle"):
            checked_apply(self.holdout.before, self.inner.id,
                          self.roles[:3], cyclic)

    def test_grounded_macro_matches_original_three_steps(self):
        candidates = list(available_macros(self.holdout.before, self.catalog,
                                           (self.outer.id,)))
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0][0].roles, self.roles)
        self.assertEqual(candidates[0][1],
                         replay(self.holdout.before, self.holdout.calls, self.verbs))

    def test_grounding_budget_reported_as_error(self):
        with self.assertRaisesRegex(ValueError, "grounding cap"):
            list(available_macros(self.holdout.before, self.catalog,
                                  (self.outer.id,), max_groundings=1))

    def test_compression_not_primitive_step_reduction(self):
        self.assertEqual(len(self.outer.calls), 2)
        self.assertEqual(self.outer.depth, 3)
        self.assertEqual(len(self.holdout.calls), 3)
        self.assertEqual(run_demo()["underlying_primitive_transitions"], 3)
        self.assertEqual(run_demo()["single_macro_invocation"], 1)

    def test_repeatable_signature_across_entity_renaming(self):
        renamed = training_traces(self.verbs, count=3)
        partial = [Trace(t.before, t.calls[:2],
                         replay(t.before, t.calls[:2], self.verbs)) for t in renamed]
        inferred = induce_macros(partial, self.verbs)
        self.assertEqual(next(iter(inferred)), self.inner.id)

    def test_full_report(self):
        result = run_demo()
        self.assertEqual(result["training_traces"], 3)
        self.assertEqual(result["two_level_macros"], 2)
        self.assertTrue(result["macro_equals_primitive_replay"])
        self.assertTrue(result["missing_permission_fixture_blocks"])
        self.assertTrue(result["original_world_unchanged"])
        self.assertEqual(result["simulated_goal_utility"], 24)


if __name__ == "__main__":
    unittest.main()
