"""COLLECTIVE-003: source-owned strange questions + original native Question Box."""
from __future__ import annotations
import copy
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from national_treasure_frontier import (
    CASES, HOLD, NT_BOX_COMMIT, NT_ENGINE_BLOB, NT_CASES_COMMIT,
    SPEC_BY_ID, build_node, verify_node, graph_identifiability_certificate,
    cicada_contrast_certificate, proof_of_source, source_checkout,
    native_question_box, run, digest,
)


class SourceNativeFrontier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_root = Path(os.environ["NT_CASE_ROOT"]).resolve()
        cls.box_root = Path(os.environ["NT_BOX_ROOT"]).resolve()
        cls.packet = run(cls.case_root, cls.box_root)
        cls.nodes = {n["case_id"]: n for n in cls.packet["question_nodes"]}

    def test_original_sources_are_pinned_and_independent_of_box_branch(self):
        self.assertEqual(source_checkout(self.case_root, NT_CASES_COMMIT), self.case_root)
        self.assertEqual(source_checkout(self.box_root, NT_BOX_COMMIT), self.box_root)
        self.assertNotEqual(NT_CASES_COMMIT, NT_BOX_COMMIT)
        q = proof_of_source(self.box_root, "tools/question-box/engine.mjs",
                            NT_ENGINE_BLOB, "export function buildQuestionFrontier")
        self.assertEqual(q["git_blob"], NT_ENGINE_BLOB)
        for case in CASES:
            p = proof_of_source(self.case_root, case["path"], case["blob"],
                                case["anchor"])
            self.assertEqual(p["git_blob"], case["blob"])
            self.assertTrue(p["exact_source_excerpt"])
            self.assertFalse(p["historical_primary_source_authenticated"])

    def test_six_strange_questions_are_truly_native_receipts(self):
        self.assertEqual(self.packet["native_question_count"], 6)
        for n in self.nodes.values():
            self.assertTrue(verify_node(n, self.case_root, self.box_root))
            native = n["original_question_receipt"]
            self.assertEqual(native["schema"], "national-treasure.question-receipt/v0")
            self.assertNotIn("answer", native)
            self.assertNotIn("conclusion", native)
            self.assertTrue(native["non_claims"])
            self.assertEqual(n["knowledge_status"],
                             "SOURCE_TEXT_VERIFIED_QUESTION_UNRESOLVED")
            self.assertFalse(n["world_claim_verified"])
            self.assertFalse(n["action_authorized_or_executed"])

    def test_fictional_artifact_remains_unlocated_and_failed(self):
        n = self.nodes["time-artifact-that-wasnt-there"]
        q = n["original_question_receipt"]
        self.assertEqual(q["evidence"]["provenance_class"], "failed")
        self.assertEqual(q["evidence"]["support_confidence"], "unsupported")
        self.assertEqual(q["evidence"]["source_locator"], "")
        self.assertEqual(q["aperture"]["id"], "source-object")
        self.assertTrue(n["source_object_missing_in_reality"])
        self.assertEqual(n["motif_recommended_action"],
                         "RECOVER_ORIGINAL_SOURCE_BEFORE_EXPLANATION")

    def test_particular_source_forces_counterevidence_after_chronology(self):
        n = self.nodes["particular-treasure"]
        q = n["original_question_receipt"]
        self.assertTrue(q["evidence"]["chronology"])
        self.assertEqual(q["aperture"]["id"], "counterevidence")
        self.assertIn("RETROJECTION IS NOT ANCESTRY",
                      n["source_witness"]["exact_source_excerpt"])

    def test_source_names_are_not_independent_witnesses(self):
        for n in self.nodes.values():
            self.assertEqual(n["original_question_receipt"]["evidence"]["source_families"], [])
            self.assertTrue(n["source_document_is_not_historical_proof"])
            self.assertIn("External original sources", n["unresolved"][0])

    def test_exact_identifiability_case_finds_minimal_discriminator(self):
        card = graph_identifiability_certificate(
            self.nodes["same-state-different-world"])
        self.assertEqual(card["selected_total_cost"], 2)
        self.assertEqual(set(card["selected_question_operations"]),
                         {"max_degree", "component_count"})
        self.assertEqual(card["all_subsets_exhausted"], 15)
        self.assertEqual(len({str(x) for x in card["inherited_observation"].values()}), 1)
        self.assertEqual(len({str(x) for x in card["candidate_feature_values"]["max_degree"].values()}), 2)
        self.assertTrue(card["independent_direct_adjacency_check"])
        self.assertFalse(card["new_general_mathematics_discovered"])
        self.assertTrue(card["synthetic_only"])

    def test_cicada_explicit_contrast_retains_real_and_refused_fixture_edges(self):
        card = cicada_contrast_certificate(self.nodes["cicada-overfit"],
                                            self.case_root)
        a = [x["fixture_expected"] for x in
             card["source_fixture_pair"]["co-013"]["author_declared_edges"]]
        b = [x["fixture_expected"] for x in
             card["source_fixture_pair"]["co-014"]["author_declared_edges"]]
        self.assertEqual(a.count("DEMONSTRATED_ANCESTRY"), 2)
        self.assertIn("FORMAL_RESEMBLANCE", b)
        self.assertIn("REFUSED_ANCESTRY", b)
        self.assertTrue(card["no_actual_cicada_authorship_conclusion"])

    def test_adversarial_rehashed_question_node_is_not_accepted(self):
        n = copy.deepcopy(self.nodes["time-artifact-that-wasnt-there"])
        n["original_question_receipt"]["evidence"]["source_locator"] = (
            "a fabricated nineteenth-century museum inventory"
        )
        n["original_question_receipt"]["aperture"]["id"] = "chronology"
        n["integrity_digest"] = digest({
            k: v for k, v in n.items() if k != "integrity_digest"
        })
        with self.assertRaises(HOLD):
            verify_node(n, self.case_root, self.box_root)

    def test_source_blob_mismatch_refused_even_with_real_file(self):
        case = SPEC_BY_ID["numatherology"]
        with self.assertRaises(HOLD):
            proof_of_source(self.case_root, case["path"], "0" * 40, case["anchor"])

    def test_invalid_checkout_revision_fails_closed(self):
        with self.assertRaises(HOLD):
            source_checkout(self.case_root, "0" * 40)

    def test_native_question_box_receipt_cannot_be_mislabeled_as_answer(self):
        output = native_question_box(self.box_root, {
            "clue": "An unidentifiable thing has a mysterious history",
            "provenance_class": "failed",
            "support_confidence": "unsupported",
        })
        self.assertEqual(output["aperture"]["id"], "source-object")
        self.assertNotIn("answer", output)
        self.assertNotIn("conclusion", output)

    def test_no_action_or_authority_exported(self):
        self.assertFalse(self.packet["automatic_admission"])
        self.assertFalse(self.packet["installed"])
        self.assertEqual(self.packet["external_authority"], "NONE")
        self.assertEqual(self.packet["new_model_calls"], 0)
        self.assertEqual(self.packet["new_external_research_queries"], 0)
        self.assertIn("RESEARCH_HOLD", self.packet["status"])


if __name__ == "__main__":
    unittest.main()
