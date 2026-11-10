"""CONFLUENCE-002 source-pinned native composition and epistemic adversaries."""
from __future__ import annotations
import copy
import json
import unittest

from native import (coherent_trial, native_modules, source_pins,
                    native_lineage, native_macro, native_proof, FieldOwnerView)
from confluence import Confluence, SyntheticOwner, WORLDS


class NativeConfluenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = native_modules()

    def test_both_foreign_git_sources_exactly_pinned(self):
        self.assertEqual(set(source_pins()), {"field008", "collective001"})
        self.assertEqual(len(source_pins()["field008"]), 40)

    def test_single_hinge_composes_four_real_modules(self):
        owner = SyntheticOwner(2, False)
        result = coherent_trial(owner)
        self.assertEqual(result["status"], "REVIEW_ONLY_SYNTHETIC_PROOF")
        self.assertEqual(result["base"]["plan"], "PANEL_AND_CHAIR")
        self.assertEqual(result["base"]["ink_count"], 2)
        self.assertEqual(result["field"]["source_observation_nodes"], 2)
        self.assertEqual(result["field"]["proposed_branch_predictions"], 4)
        self.assertEqual(result["field"]["independent_source_origins"], 1)
        self.assertEqual(result["field"]["refuted_predictions"], 2)
        self.assertEqual(result["macro"]["demonstrations"], 2)
        self.assertTrue(result["macro"]["missing_permission_rejected"])
        self.assertEqual(result["macro"]["recorded_coverage_mask"], 7)
        self.assertEqual(result["proof"]["verified_coverage_mask"], 7)
        self.assertEqual(result["proof"]["reentry_new_development_queries"], 0)
        self.assertEqual(result["proof"]["owner_truth_table_cases"], 64)
        self.assertTrue(result["no_physical_actions"])
        self.assertEqual(result["authority"], "NONE")
        self.assertIn("motif003", result["base"]["proof_chain"][-1]["payload"])

    def test_two_hinges_and_native_selective_retraction(self):
        owner = SyntheticOwner(1, True)
        output = coherent_trial(owner)
        self.assertEqual(output["base"]["plan"], "MESH_AND_CHAIR")
        self.assertEqual(output["field"]["source_observation_nodes"], 3)
        self.assertEqual(output["field"]["proposed_branch_predictions"], 6)
        self.assertEqual(output["field"]["refuted_predictions"], 3)
        self.assertEqual(output["macro"]["expanded_primitive_steps"], 3)
        self.assertEqual(output["proof"]["verified_coverage_mask"], 7)
        self.assertTrue(all(v["grounding"]["state"] in
                            ("HOLD_CONTRADICTED", "PENCIL_CONDITIONAL")
                            for v in output["field"]["retractions"]))

    def test_no_plan_holds_and_does_not_invent_proof(self):
        owner = SyntheticOwner(1, False)
        x = coherent_trial(owner)
        self.assertEqual(x["status"], "HOLD")
        self.assertIsNone(x["macro"])
        self.assertIsNone(x["proof"])
        self.assertEqual(x["field"]["source_observation_nodes"], 3)

    def test_absent_permission_halts_before_macro(self):
        owner = SyntheticOwner(2, True, permission=False)
        x = coherent_trial(owner)
        self.assertEqual(x["status"], "HOLD")
        self.assertEqual(x["base"]["reason"], "PERMISSION_UNVERIFIED_OR_DENIED")
        self.assertEqual(x["field"]["proposed_branch_predictions"], 0)
        self.assertIsNone(x["macro"])

    def test_incomplete_budget_holds_with_original_pencil(self):
        x = coherent_trial(SyntheticOwner(2, True), budget=0)
        self.assertEqual(x["status"], "HOLD")
        self.assertEqual(x["base"]["ink_count"], 1)
        self.assertIsNone(x["proof"])

    def test_real_macro_cannot_be_given_unsupported_plan(self):
        with self.assertRaises(ValueError):
            native_macro("UNREVIEWED_MATERIAL", self.modules)

    def test_full_proof_payload_is_a_native_reverifiable_node(self):
        x = coherent_trial(SyntheticOwner(2, True), include_full_proof=True)
        full = x["proof"]["full_proof_node"]
        self.assertFalse(full["automatic_admission"])
        self.assertEqual(full["external_authority"], "NONE")
        self.assertEqual(len(full["relevant_evidence_nodes"]), 3)
        self.assertEqual(full["answer"]["output_mask"], 7)
        self.assertTrue(x["proof"]["reentry_runs_full_verification"])

    def test_rehashed_wrong_answer_is_still_refused(self):
        from proof_memory import ProofError
        with self.assertRaises(ProofError):
            native_proof(7, self.modules, corrupted_packet=True)

    def test_native_proof_never_proves_wrong_fence_mask(self):
        with self.assertRaises(RuntimeError):
            native_proof(6, self.modules)

    def test_field_source_forgery_rejected_even_rehashed(self):
        owner = SyntheticOwner(2, False)
        base = Confluence(owner).run()
        target = next(e for e in base["proof_chain"] if e["kind"] == "INK_OBSERVATION")
        changed = copy.deepcopy(base)
        target2 = next(e for e in changed["proof_chain"] if e["kind"] == "INK_OBSERVATION")
        target2["payload"]["value"] = False
        # Even if a caller has rewritten the envelope digest, source membership fails.
        target2["payload"]["sha256"] = "forged"
        with self.assertRaises(ValueError):
            native_lineage(changed, owner, self.modules)
        self.assertTrue(owner.verify(target["payload"]))

    def test_field_owner_normalization_does_not_forge_an_origin(self):
        owner = SyntheticOwner(2, False)
        receipt = owner.read("permission")
        adapter = FieldOwnerView(owner)
        normalized = adapter.normalize(receipt)
        self.assertTrue(adapter.verify(normalized))
        normalized["provenance_origin"] = "SECOND_FAKE_SOURCE"
        self.assertFalse(adapter.verify(normalized))

    def test_native_methods_do_not_upgrade_hypotheses(self):
        for condition in ((2, False), (1, True)):
            owner = SyntheticOwner(*condition)
            x = coherent_trial(owner)
            self.assertEqual(x["field"]["independent_source_origins"], 1)
            self.assertNotIn("INK", {p["grounding"]["state"]
                                     for p in x["field"]["retractions"]})
            self.assertTrue(all(e["payload"].get("status") == "PENCIL"
                                for e in x["base"]["proof_chain"]
                                if e["kind"] == "PENCIL_PROPOSAL"))


if __name__ == "__main__":
    unittest.main()
