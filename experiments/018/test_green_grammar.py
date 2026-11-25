"""Adversarial tests, including expected *failures* of MOTIF-018's model.

No past claim is silently promoted; adapter tests are not native integration.
"""
from dataclasses import replace
import unittest

from green_grammar_crucible import (
    Claim, Crossing, LanguageWitness, Witness,
    admit_claim, adjudicate, compare_projections, doorway, ground_alias,
    n_step_world, numeric_delta, parse_bank, projections_for_022100,
    reading_available, rebase_reading_on_past, run_crucible, stripped_of_graph,
    two_relation_xor,
)
from unknown_unknown import assess, discover, world


class GreenGrammarCrucibleTests(unittest.TestCase):

    def setUp(self):
        self.train = world("path", "train")
        self.validation = world("path", "validation")
        self.holdout = world("path", "holdout")

    def test_existing_motif_expands_a_supplied_grammar(self):
        r = discover(self.train, self.validation)
        self.assertEqual(r["status"], "HOLD_FOR_HUMAN_REVIEW")
        self.assertEqual(assess(r["model"], self.holdout)["accuracy"], 1)

    def test_irreversibly_erased_graph_cannot_be_reconstructed(self):
        r = discover(stripped_of_graph(self.train),
                     stripped_of_graph(self.validation))
        self.assertEqual(r["status"], "HOLD_UNEXPLAINED_SURPRISE")

    def test_new_three_edge_primitive_is_outside_original_grammar(self):
        cases = n_step_world(3)
        r = discover(cases, cases)
        self.assertEqual(r["status"], "HOLD_UNEXPLAINED_SURPRISE")
        self.assertIsNone(r["model"])

    def test_two_feature_xor_cannot_be_handled_by_one_added_bit(self):
        r = discover(two_relation_xor(), two_relation_xor())
        self.assertEqual(r["status"], "HOLD_UNEXPLAINED_SURPRISE")

    def test_retains_graph_spoof_as_real_failure_of_native_018(self):
        model = discover(self.train, self.validation)["model"]
        false_world = tuple(replace(e, outcome=1 - e.outcome)
                            for e in self.holdout)
        self.assertEqual(assess(model, false_world)["accuracy"], 0.0)
        # Critical: the predictor itself has NO mechanism to verify raw edges.

    def test_drift_in_causal_relation_is_negative_transfer(self):
        model = discover(self.train, self.validation)["model"]
        self.assertEqual(assess(model, world("badge", "holdout"))[
                         "accuracy"], 0.5)

    def test_ambiguity_is_preserved_at_earlier_cut(self):
        earlier = parse_bank("The bank moved.", "", 1, "raw-1")
        later = parse_bank("The bank moved.", "After the flood", 2, "raw-1+2")
        self.assertEqual(len(earlier.candidate_senses), 2)
        self.assertEqual(later.candidate_senses, ("riverbank",))
        self.assertEqual(len(earlier.candidate_senses), 2)
        self.assertEqual(earlier.status, "PROPOSED_NOT_INTENTION")
        self.assertEqual(rebase_reading_on_past(later, earlier),
                         "HOLD_RETROSPECTIVE_KNOWLEDGE")
        self.assertFalse(reading_available(later, 1))
        self.assertTrue(reading_available(earlier, 1))

    def test_typed_carrier_decoders_do_not_claim_one_identity(self):
        a, b = projections_for_022100()
        self.assertEqual(a["value"], 225)
        self.assertEqual(b["value"], "E_major")
        self.assertEqual(compare_projections(a, b),
                         "HOLD_CROSS_DECODER_IDENTITY")
        self.assertEqual(compare_projections(a, a),
                         "SAME_DECODER_COMPARABLE")

    def test_composition_order_is_measured_not_mythologized(self):
        self.assertEqual(numeric_delta(5, "add1", "double")["delta"], 1)
        self.assertEqual(numeric_delta(5, "add1", "add3")["delta"], 0)
        self.assertFalse(numeric_delta(5, "add1", "double")[
                         "causal_or_usefulness_proven"])
        with self.assertRaises(ValueError):
            numeric_delta(5, "new-magical-operator", "double")

    def test_math_identity_is_checked_without_promoting_metaphysics(self):
        T = lambda n: n * (n + 1) // 2
        for n in range(1, 51):
            self.assertEqual(T(n * n) - T(n) ** 2, T(n - 1) ** 2)

    def test_semantic_fact_is_not_proof(self):
        named_fact = Claim("The bank moved.", "FACT_CANDIDATE",
                           "generated-output", False, True)
        self.assertEqual(admit_claim(named_fact), "HOLD_EVIDENCE")
        self.assertEqual(admit_claim(replace(named_fact,
                                            external_evidence=True)),
                         "PROPOSE_LOCAL_REVIEW_ONLY")

    def test_idea_and_relation_labels_also_require_evidence(self):
        for role in ("IDEA", "RELATION"):
            self.assertEqual(admit_claim(Claim("x", role, "model", False, True)),
                             "HOLD_EVIDENCE")
        self.assertEqual(admit_claim(Claim("x", "FACT", "model", True, True)),
                         "HOLD_UNTYPED_CLAIM")

    def test_source_and_destination_stay_distinct(self):
        x = Crossing("A", "B", True, True, True)
        self.assertEqual(doorway(replace(x, source_receipt=False)),
                         "HOLD_MISSING_SOURCE_HAND")
        self.assertEqual(doorway(replace(x, destination_consent=False)),
                         "HOLD_MISSING_DESTINATION_HAND")
        self.assertEqual(doorway(replace(x, independent_authority=False)),
                         "HOLD_MISSING_AUTHORITY")
        self.assertEqual(doorway(x),
                         "REVIEWABLE_SYNTHETIC_CROSSING_NOT_EXECUTED")
        self.assertEqual(doorway(replace(x, scope="EXTERNAL")),
                         "HOLD_EXTERNAL_CROSSING")

    def test_correct_name_cannot_grant_authority(self):
        self.assertEqual(doorway(Crossing("correct-name", "target",
                                         True, True, False)),
                         "HOLD_MISSING_AUTHORITY")

    def test_forwarded_hearsay_does_not_multiply_evidence(self):
        copies = (Witness(False, "upstream-A", True),) * 100
        self.assertEqual(adjudicate(copies), "HOLD_ONLY_ONE_UPSTREAM_FAMILY")
        self.assertEqual(adjudicate(copies + (
                         Witness(True, "upstream-B", True),)),
                         "HOLD_INDEPENDENT_CONFLICT")

    def test_declared_sources_do_not_authenticate_themselves(self):
        self.assertEqual(adjudicate((
            Witness(True, "A", False),
            Witness(True, "B", False))),
            "HOLD_UNAUTHENTICATED_SOURCE_METADATA")
        self.assertEqual(adjudicate((
            Witness(True, "A", True),
            Witness(True, "B", True))),
            "PROPOSE_INDEPENDENT_AGREEMENT_NOT_AUTHORITY")

    def test_same_source_conflicts_stay_visible(self):
        self.assertEqual(adjudicate((
            Witness(True, "A", True),
            Witness(False, "A", True),
            Witness(True, "B", True))),
            "HOLD_SAME_ORIGIN_CONTRADICTION")

    def test_local_name_requires_multiple_distinct_corrections(self):
        single = (LanguageWitness("blue spoons", "path2", "A", True),)
        self.assertEqual(ground_alias(single, "blue spoons")["status"],
                         "HOLD_INSUFFICIENT_INDEPENDENT_CORRECTION")
        repeated = single * 5
        self.assertEqual(ground_alias(repeated, "blue spoons")["status"],
                         "HOLD_INSUFFICIENT_INDEPENDENT_CORRECTION")
        both = single + (LanguageWitness("blue spoons", "path2", "B", True),)
        self.assertEqual(ground_alias(both, "blue spoons")["status"],
                         "PROPOSE_LOCAL_REFERENT_NOT_AUTHORITY")
        self.assertEqual(ground_alias(both, "blue spoons")["referent"],
                         "path2")

    def test_local_homonym_reopens_gap_instead_of_forcing_a_victor(self):
        records = (
            LanguageWitness("green", "riverbank", "A", True),
            LanguageWitness("green", "riverbank", "B", True),
            LanguageWitness("green", "financial_institution", "C", True))
        self.assertEqual(ground_alias(records, "green")["status"],
                         "HOLD_CONFLICTING_LOCAL_MEANINGS")

    def test_unverified_feedback_cannot_ground_a_local_word(self):
        records = (
            LanguageWitness("green", "path", "A", False),
            LanguageWitness("green", "path", "B", False))
        self.assertEqual(ground_alias(records, "green")["status"],
                         "HOLD_INSUFFICIENT_INDEPENDENT_CORRECTION")

    def test_report_has_explicit_exposed_failure_and_no_promotion(self):
        r = run_crucible()
        cases = {x["id"]: x for x in r["test_cases"]}
        self.assertEqual(len(cases), 20)
        self.assertEqual(cases["false_graph_world"]["observed"], 0)
        self.assertEqual(cases["false_graph_world"]["verdict"],
                         "EXPOSED_PREDICTION_FAILURE")
        self.assertEqual(cases["three_hop_unavailable"]["verdict"], "HELD")
        self.assertEqual(cases["aperture_ambiguity"]["layer"],
                         "bounded_green_adapter")
        self.assertEqual(r["external_actions"], 0)
        self.assertEqual(r["promotions"], 0)
        self.assertTrue(r["sources_are_noncanonical_research_witnesses"])


if __name__ == "__main__":
    unittest.main()
