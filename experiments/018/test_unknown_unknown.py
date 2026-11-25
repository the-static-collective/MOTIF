"""Falsifiers for MOTIF-018's deliberately small unknown-unknown world."""
from dataclasses import replace
import json
import unittest

from unknown_unknown import (
    Episode, RelationProgram, assess, build_episode, classical_exhaustive_selector,
    discover, fit, intervention_audit, propose_concepts, run, surface_collisions,
    world,
)


class UnknownUnknownTests(unittest.TestCase):
    def setUp(self):
        self.train = world("path", "train")
        self.validation = world("path", "validation")
        self.holdout = world("path", "holdout")

    def test_a_surface_contradiction_is_detected(self):
        self.assertEqual(surface_collisions(self.train), 2)
        self.assertEqual(assess(fit(self.train), self.holdout)["accuracy"], 0.5)

    def test_concept_is_constructed_from_raw_edges_not_labels(self):
        found = propose_concepts(self.train)
        self.assertIn(RelationProgram("path2", ("carries", "reaches")), found)
        self.assertIn(RelationProgram("direct", ("marked",)), found)
        flipped_labels = tuple(replace(e, outcome=1 - e.outcome)
                               for e in self.train)
        self.assertEqual(propose_concepts(flipped_labels), found)

    def test_induced_relation_separates_heldout_worlds(self):
        r = discover(self.train, self.validation)
        self.assertEqual(r["status"], "HOLD_FOR_HUMAN_REVIEW")
        self.assertEqual(r["model"].concept.name(), "path2(carries,reaches)")
        self.assertEqual(assess(r["model"], self.holdout)["accuracy"], 1.0)

    def test_spurious_direct_relation_fails_frozen_validation(self):
        r = discover(self.train, self.validation)
        decoy = next(x for x in r["candidates"]
                     if x["concept"] == "direct(marked)")
        self.assertEqual(decoy["train"]["accuracy"], 1.0)
        self.assertEqual(decoy["validation"]["accuracy"], 0.0)
        self.assertFalse(decoy["passes"])

    def test_conventional_exhaustive_feature_search_ties(self):
        expanded = discover(self.train, self.validation)["model"]
        classical = classical_exhaustive_selector(self.train, self.validation)
        self.assertIsNotNone(classical)
        self.assertEqual(assess(expanded, self.holdout),
                         assess(classical, self.holdout))

    def test_diagnostic_requests_revision_but_cannot_install_it(self):
        r = discover(self.train, self.validation)
        self.assertEqual(r["diagnostics"]["v0"],
                         "HOLD_CONTRADICTORY_SURFACE")
        self.assertEqual(r["diagnostics"]["proposed_revision"],
                         "search_composed_graph_relations")
        self.assertFalse(r["diagnostics"]["revision_installed"])
        self.assertEqual(r["cartridge"]["authority"], "NONE")
        self.assertTrue(r["cartridge"]["human_review_required"])

    def test_receipt_digest_is_reproducible_and_not_authentication(self):
        from hashlib import sha256
        r = discover(self.train, self.validation)["cartridge"]
        body = {k: v for k, v in r.items() if k != "checksum_sha256"}
        self.assertEqual(sha256(json.dumps(body, sort_keys=True).encode()
                               ).hexdigest(), r["checksum_sha256"])
        self.assertEqual(r["scope"], "SYNTHETIC_PREDICTION_ONLY")

    def test_structural_intervention_evaluated_separately(self):
        model = discover(self.train, self.validation)["model"]
        audit = intervention_audit(model)
        self.assertTrue(audit["all_interventions_predicted"])
        self.assertEqual(len(audit["pairs"]), 4)
        self.assertFalse(audit["interventions_executed_in_real_world"])

    def test_unrepresented_hidden_cause_stays_unexplained(self):
        r = discover(world("latent", "train"),
                     world("latent", "validation"))
        self.assertEqual(r["status"], "HOLD_UNEXPLAINED_SURPRISE")
        self.assertIsNone(r["model"])

    def test_rival_concepts_stay_unidentified_if_validation_confounded(self):
        r = discover(self.train, self.train)
        self.assertEqual(r["status"], "HOLD_RIVAL_MODELS")
        self.assertIsNone(r["model"])

    def test_independent_label_corruption_forces_hold(self):
        bad = (replace(self.validation[0],
                       outcome=1 - self.validation[0].outcome),) + self.validation[1:]
        r = discover(self.train, bad)
        self.assertEqual(r["status"], "HOLD_UNEXPLAINED_SURPRISE")

    def test_negative_transfer_is_preserved(self):
        model = discover(self.train, self.validation)["model"]
        transferred = assess(model, world("badge", "holdout"))
        self.assertEqual(transferred["accuracy"], 0.5)

    def test_no_new_grammar_when_surface_is_consistent(self):
        episodes = tuple(build_episode(f"stable-{x}{i}", x, i, 1 - i,
                                       x) for x in (0, 1) for i in (0, 1))
        r = discover(episodes, episodes)
        self.assertEqual(r["status"], "HOLD_NO_OBSERVED_GAP")

    def test_unknown_feature_combination_abstains(self):
        model = fit(self.train, RelationProgram("direct", ("marked",)))
        unknown = Episode("unseen", 2, (), 0, False)
        self.assertIsNone(model.predict(unknown))

    def test_wrong_or_unpermitted_proposals_are_counted(self):
        bad = fit(self.train)
        grade = assess(bad, self.holdout)
        self.assertIn("wrong_or_unpermitted_positive_proposals", grade)
        better = discover(self.train, self.validation)["model"]
        self.assertEqual(assess(better, self.holdout)[
                         "wrong_or_unpermitted_positive_proposals"], 0)

    def test_benchmark_is_deterministic_and_never_externally_acts(self):
        a, b = run(), run()
        self.assertEqual(a, b)
        self.assertEqual(a["heldout_surface_only"]["accuracy"], 0.5)
        self.assertEqual(a["heldout_expanded"]["accuracy"], 1.0)
        self.assertEqual(a["heldout_classical_exhaustive_feature_search"][
                         "accuracy"], 1.0)
        self.assertEqual(a["negative_transfer_to_badge_cause"]["accuracy"],
                         0.5)
        self.assertEqual(a["external_actions"], 0)
        self.assertFalse(a["automatically_deployed"])
        self.assertFalse(a["consciousness_claim"])


if __name__ == "__main__":
    unittest.main()
