"""GENIUS-003: no-leakage, prospective correction and hidden-profile controls."""
import json
import unittest

from perspective_learning import (
    TOPICS, ARMS, FrequencyModel, Report, SyntheticWorld,
    public_only, choose_question, brier, run,
)
from hidden_profile import Evidence, Member, evidence_pool, demo


class TestCorrectablePerspectives(unittest.TestCase):
    def test_self_report_updates_only_after_explicit_share(self):
        m = FrequencyModel()
        kept = Report("id1", "A", "safety", True, True, "synthetic:1")
        withheld = Report("id2", "A", "safety", False, False,
                          "PRIVATE_REF", "SECRET_NOT_PUBLIC")
        m.fit((kept, withheld))
        self.assertEqual(m.count("A", "safety"), 1)
        self.assertAlmostEqual(m.predict("A", "safety", "target_topic"), 2/3)
        self.assertFalse(m.update(withheld))
        self.assertEqual(m.count("A", "safety"), 1)
        with self.assertRaises(ValueError):
            m.update(kept)

    def test_unknown_person_or_topic_is_hold_not_mindreading(self):
        model = FrequencyModel().fit((Report("a1", "A", "safety", True,
                                             True, "synthetic:source"),))
        for arm in ARMS:
            self.assertIsNone(model.predict("B", "safety", arm))
            self.assertIsNone(model.predict("A", "unknown", arm))
        self.assertEqual(choose_question(model, "A", TOPICS,
                                         target_opted_in=False)["status"], "HOLD")
        self.assertEqual(choose_question(model, "A", TOPICS,
                                         target_opted_in=True)["status"], "SUGGESTION_ONLY")
        self.assertTrue(choose_question(model, "A", TOPICS,
                                        target_opted_in=True)
                        ["requires_separate_disclosure_authorization"])

    def test_train_only_freeze_and_counterfactual_shift(self):
        first = run(30301)
        repeated = run(30301)
        self.assertEqual(first["frozen_training_digest"], repeated["frozen_training_digest"])
        self.assertEqual(first["training_cv_scores"], repeated["training_cv_scores"])
        self.assertEqual(first["stable"]["fixed_comparators"],
                         repeated["stable"]["fixed_comparators"])
        self.assertIn(first["selected_train_only_policy"], ARMS)
        self.assertEqual(first["status"], "SYNTHETIC_RESEARCH_HOLD")
        self.assertTrue(first["no_live_people_contacted"])
        self.assertTrue(first["no_external_action_taken"])
        self.assertEqual(set(first["stable"]["fixed_comparators"]["arms"]), set(ARMS))
        self.assertEqual(set(first["shift"]["fixed_comparators"]["arms"]), set(ARMS))
        self.assertGreater(first["stable"]["fixed_comparators"]["withheld_excluded"], 0)
        self.assertGreater(first["shift"]["fixed_comparators"]
                           ["unknown_target_or_topic_abstentions"], 0)
        output = json.dumps(first)
        self.assertNotIn("PRIVATE_SIMULATOR_STATE_DO_NOT_EXPORT", output)
        # Shift deliberately reverses individual patterns; a learner's
        # confidence can become misleading. Do not assume guaranteed gain.
        self.assertNotEqual(first["stable"]["fixed_comparators"]["arms"]
                            ["target_topic"]["brier"],
                            first["shift"]["fixed_comparators"]["arms"]
                            ["target_topic"]["brier"])

    def test_brier_is_proper_binary_quadratic_error(self):
        self.assertEqual(brier(0.9, True), (0.9 - 1) ** 2)
        self.assertEqual(brier(0.9, False), 0.9 ** 2)
        self.assertLess(brier(0.9, True), brier(0.5, True))

    def test_future_outcomes_do_not_change_frozen_training_hash(self):
        # Different simulation futures must not be used to select a policy.
        a = SyntheticWorld.create(30301)
        b = SyntheticWorld.create(30301)
        self.assertEqual(a.episodes(30304, 3), b.episodes(30304, 3))
        self.assertNotEqual(a.episodes(30304, 3), b.episodes(30304, 3, shift=True))
        self.assertEqual(run(30301)["frozen_training_digest"],
                         run(30301)["frozen_training_digest"])

    def test_same_agent_two_distinct_case_ids_are_two_reports_not_two_authors(self):
        m = FrequencyModel().fit((
            Report("a1", "A", "speed", True, True, "ref1"),
            Report("a2", "A", "speed", False, True, "ref2")))
        self.assertEqual(m.count("A", "speed"), 2)
        self.assertEqual(m.known_targets, {"A"})


class TestHiddenProfile(unittest.TestCase):
    def test_unshared_unique_facts_change_majority_model_conclusion(self):
        r = demo()
        self.assertEqual(r["simple_majority_local_preference"], "A")
        self.assertEqual(r["conditional_candidate"], "B")
        self.assertEqual(r["pooled_weight_sum"], -4)
        self.assertEqual(len(r["unique_public_evidence"]), 3)
        self.assertEqual(r["status"], "MODEL_CHOICE_CONDITIONAL_ON_DECLARED_WEIGHTS")
        self.assertTrue(r["no_real_world_ground_truth_established"])
        self.assertTrue(r["no_external_action_taken"])
        self.assertNotIn("PRIVATE_SENSITIVE_001", json.dumps(r))
        self.assertNotIn("private:do-not-leak", json.dumps(r))

    def test_conflicting_weights_same_id_force_hold_not_average(self):
        r = evidence_pool((
            Member("A", (Evidence("same", "A", 2, True, "ref:A"),)),
            Member("B", (Evidence("same", "B", -3, True, "ref:B"),)),
        ))
        self.assertEqual(r["status"], "HOLD_INCONSISTENT_EVIDENCE")
        self.assertIsNone(r["conditional_candidate"])
        self.assertEqual(r["conflicts"][0]["evidence_id"], "same")

    def test_echoes_deduplicated_and_private_never_changes_answer(self):
        a = evidence_pool((
            Member("A", (Evidence("same", "A", 3, True, "ref:A"),)),
            Member("B", (Evidence("same", "B", 3, True, "ref:A"),)),
            Member("C", (Evidence("same", "C", 3, True, "ref:A"),
                         Evidence("private", "C", -300, False, "secret"),)),
        ))
        self.assertEqual(a["pooled_weight_sum"], 3)
        self.assertEqual(a["unique_public_evidence"][0]["reporting_nodes"],
                         ["A", "B", "C"])
        self.assertEqual(a["withheld_records_count"], 1)

    def test_false_owner_fails(self):
        with self.assertRaises(ValueError):
            evidence_pool((Member("A", (Evidence("x", "B", 1, True, "ref"),)),))


if __name__ == "__main__":
    unittest.main()
