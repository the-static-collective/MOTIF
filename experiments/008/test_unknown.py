"""MOTIF-008: independent synthetic oracle and learner boundary tests."""
import inspect
import unittest
from dataclasses import replace

import oracle
import learner
import benchmark


class UnknownWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.domain = oracle.trial("forward_join", 23)

    def test_all_six_world_families_are_explicitly_predeclared(self):
        self.assertEqual(len(oracle.FAMILIES), 6)
        self.assertEqual(len(oracle.SUPPORTED), 5)
        self.assertIn("xor", oracle.FAMILIES)

    def test_seed_reproducibility(self):
        a = oracle.trial("reverse_join", 11)
        b = oracle.trial("reverse_join", 11)
        self.assertEqual(a, b)
        self.assertNotEqual(a.train, oracle.trial("reverse_join", 23).train)

    def test_split_entity_names_are_distinct(self):
        t = self.domain
        train_names = {x.roles for x in t.train}
        valid_names = {x.roles for x in t.validation}
        test_names = {x.roles for x in t.test}
        self.assertFalse(train_names & valid_names)
        self.assertFalse(test_names & valid_names)
        self.assertFalse(train_names & test_names)

    def test_new_vocabulary_for_every_synthetic_world(self):
        a = oracle.spec_for("direct", 23)
        b = oracle.spec_for("conjunction", 23)
        c = oracle.spec_for("direct", 41)
        self.assertFalse(set(a.vocabulary) & set(b.vocabulary))
        self.assertFalse(set(a.vocabulary) & set(c.vocabulary))

    def test_all_world_vocabulary_names_are_unique_in_frozen_benchmark(self):
        tokens = [name for family in oracle.FAMILIES
                  for seed in benchmark.SEEDS
                  for name in oracle.spec_for(family, seed).vocabulary]
        self.assertEqual(len(tokens), len(set(tokens)))

    def test_learner_never_imports_hidden_oracle(self):
        text = inspect.getsource(learner)
        self.assertNotIn("from oracle import", text)
        self.assertNotIn("import oracle\n", text)
        self.assertNotIn("hidden_rule(", text)

    def test_episode_exposes_no_hidden_rule_or_flag(self):
        item = self.domain.train[0]
        self.assertEqual(set(vars(item)),
                         {"before", "observed_after", "roles", "provenance"})
        self.assertEqual(item.provenance, "SYNTHETIC_ORACLE")

    def test_observed_outcome_derived_only_from_graph_difference(self):
        plus = next(x for x in self.domain.train if x.before != x.observed_after)
        minus = next(x for x in self.domain.train if x.before == x.observed_after)
        self.assertTrue(learner.observed_outcome(plus))
        self.assertFalse(learner.observed_outcome(minus))
        with self.assertRaises(ValueError):
            learner.observed_outcome(replace(plus, provenance="UNVERIFIED_REAL"))

    def test_rewired_intervention_changes_one_edge_not_its_predicate(self):
        for family in ("forward_join", "reverse_join"):
            yes, no = oracle.paired_intervention(family, 23)
            delta = yes.before ^ no.before
            self.assertEqual(len(delta), 2)
            self.assertEqual({f[0] for f in yes.before},
                             {f[0] for f in no.before})
            self.assertTrue(learner.observed_outcome(yes))
            self.assertFalse(learner.observed_outcome(no))

    def test_join_feature_disappears_after_only_rewiring(self):
        a, b = oracle.paired_intervention("forward_join", 23)
        left = learner.features(a.before, a.roles)
        right = learner.features(b.before, b.roles)
        self.assertTrue(any(len(feature) == 2 for feature in left))
        self.assertNotEqual(left, right)
        lost = left - right
        self.assertTrue(any(len(feature) == 2 for feature in lost))
        self.assertFalse(learner.features(a.before, a.roles, use_joins=False)
                         ^ learner.features(b.before, b.roles, use_joins=False))

    def test_role_identity_invariance_of_features(self):
        t1 = oracle.make_episode(oracle.spec_for("direct", 23), 123)
        t2 = oracle.make_episode(oracle.spec_for("direct", 23), 123)
        self.assertEqual(learner.features(t1.before, t1.roles),
                         learner.features(t2.before, t2.roles))
        self.assertFalse(any("d23_" in str(feature) for feature in
                             learner.features(t1.before, t1.roles)))

    def test_training_and_validation_only(self):
        task = self.domain
        model = learner.fit_relational(task.train, task.validation)
        replacement_test = tuple(reversed(task.test))
        self.assertEqual(model, learner.fit_relational(task.train, task.validation))
        self.assertEqual(len(replacement_test), len(task.test))
        self.assertFalse(any(e in task.train for e in replacement_test))

    def test_sparsity_forces_abstention(self):
        sample = next(x for x in self.domain.train
                      if x.observed_after == x.before)
        model = learner.fit_relational([sample] * 10, self.domain.validation)
        self.assertEqual(model.status, "ABSTAIN_CLASS_SPARSE")
        self.assertIsNone(model.predict(learner.features(
            sample.before, sample.roles)))

    def test_incomplete_or_duplicate_roles_rejected(self):
        before = self.domain.train[0].before
        with self.assertRaises(ValueError):
            learner.features(before, ("A", "A"))
        with self.assertRaises(ValueError):
            learner.features(before, ("A",))

    def test_single_edge_baseline_cannot_see_join(self):
        yes, no = oracle.paired_intervention("reverse_join", 41)
        self.assertEqual(learner.features(yes.before, yes.roles, False),
                         learner.features(no.before, no.roles, False))
        self.assertNotEqual(learner.features(yes.before, yes.roles),
                            learner.features(no.before, no.roles))

    def test_tree_baseline_receives_same_training_evidence(self):
        t = self.domain
        model = learner.fit_tree(t.train, t.validation)
        rel = learner.fit_relational(t.train, t.validation)
        self.assertGreater(model.considered, 0)
        self.assertGreater(rel.considered, 0)
        self.assertGreaterEqual(model.validation_balanced, 0.5)

    def test_accuracy_requires_both_classes(self):
        self.assertAlmostEqual(
            learner.balanced_accuracy((True, True, False, False),
                                      (True, True, True, False)), 0.75)
        with self.assertRaises(ValueError):
            learner.balanced_accuracy((True, True), (True, False))

    def test_benchmark_reports_all_families_and_out_of_grammar_xor(self):
        report = benchmark.run_benchmark(include_detail=False)
        summary = report["summary"]
        self.assertEqual(summary["worlds"],
                         len(oracle.FAMILIES) * len(benchmark.SEEDS))
        self.assertEqual(summary["supported_worlds"], 25)
        self.assertEqual(summary["unsupported_worlds"], 5)
        self.assertFalse(summary["zero_shot_cross_world_transfer_demonstrated"])
        self.assertTrue(summary["vocabulary_disjoint_per_world"])
        self.assertEqual(summary["version"], "unknown-world-v2")
        self.assertFalse(summary["test_used_for_model_selection"])
        self.assertEqual(set(summary["per_family"]), set(oracle.FAMILIES))

    def test_benchmark_has_full_transparency_on_one_unfamiliar_world(self):
        result = benchmark.evaluate_world("hybrid", 37)
        self.assertEqual(result["observed_train"], oracle.COUNTS["train"])
        self.assertEqual(result["untouched_test"], oracle.COUNTS["test"])
        self.assertGreaterEqual(result["candidate_rules_checked"], 1)
        self.assertIn(result["relational_status"],
                      {"PROPOSED", "ABSTAIN_VALIDATION", "ABSTAIN_CLASS_SPARSE"})

    def test_no_external_action_is_exposed_by_learner(self):
        self.assertFalse(hasattr(learner, "execute"))
        self.assertFalse(hasattr(learner, "dispatch"))
        self.assertFalse(hasattr(learner, "authenticate"))


if __name__ == "__main__":
    unittest.main()
