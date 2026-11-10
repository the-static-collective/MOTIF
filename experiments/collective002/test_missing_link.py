"""COLLECTIVE-002 adversarial and matched-information proof/question checks."""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
for name in ("thought-025", "thought-026", "thought-027",
             "thought-028", "collective001"):
    p = str(HERE.parent / name)
    if p not in sys.path:
        sys.path.insert(0, p)
sys.path.insert(0, str(HERE))

from specimens import BY_KEY
from memory_benchmark import seeds, new_cases
from weave import investigate as old_investigate
from answer_weave import first_answer
from proof_memory import ProofError, digest
from missing_link import (BridgeOwner, derive_questions, policy_order,
                          expected_cost, exhaustive_classical_reference,
                          investigate, verify_packet, reenter, synthetic_owner,
                          reference_evaluator_only, evaluate_fixed_order)


def reseal(packet):
    packet["integrity_digest"] = digest({
        k: v for k, v in packet.items() if k != "integrity_digest"
    })
    return packet


def source_nodes():
    """Two genuinely separately scoped prior *finite proofs*, not two oracles."""
    store = seeds()
    first = BY_KEY["cancel_or_add"]
    proof_a = old_investigate(first, store, mode="compose")
    self_a = {n: x for (n, _), x in zip(first.fields, (3, 5))}
    left = first_answer(first, store, proof_a, self_a)
    second = new_cases()["toggle_equipment"]
    store.add_task(second)
    proof_b = old_investigate(second, store, mode="retrieved")
    self_b = {n: x for (n, _), x in zip(second.fields, (4, 1))}
    right = first_answer(second, store, proof_b, self_b)
    return left, right, store.registry


class MissingLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.left, cls.right, cls.registry = source_nodes()

    def test_two_distinct_scoped_proofs_but_no_real_author_claim(self):
        self.assertEqual(self.left["answer"]["output_mask"], 6)
        self.assertEqual(self.right["answer"]["output_mask"], 5)
        self.assertNotEqual(self.left["task_key"], self.right["task_key"])
        self.assertFalse(self.left["assertion_origin_authenticated"])
        self.assertFalse(self.right["assertion_origin_authenticated"])

    def test_generated_question_is_derived_not_prespecified_single_pair(self):
        owner = synthetic_owner(202602)
        candidates = derive_questions(self.left, self.right,
                                      self.registry, owner.contract())
        self.assertEqual({tuple(x["pair"]) for x in candidates},
                         {(1, 0), (1, 2), (2, 0), (2, 2)})
        self.assertTrue(all(
            x["left_proof_digest"] == self.left["answer"]["proof_digest"]
            and x["right_proof_digest"] == self.right["answer"]["proof_digest"]
            and x["not_yet_observed"] for x in candidates
        ))
        self.assertEqual(owner.query_count, 0)
        self.assertNotIn((0, 0), {tuple(x["pair"]) for x in candidates})

    def test_actual_new_source_question_creates_proof_carrying_link(self):
        owner = synthetic_owner(101, true_pairs={(2, 2)})
        node = investigate(self.left, self.right, self.registry, owner)
        self.assertEqual(node["status"], "FOUND_VERIFIED_FINITE_LINK")
        self.assertEqual(node["positive_witness_pair"], [2, 2])
        self.assertGreaterEqual(owner.query_count, 1)
        self.assertLessEqual(owner.query_count, 4)
        self.assertEqual(len(node["observations"]), owner.query_count)
        self.assertTrue(verify_packet(node, self.registry, owner))
        self.assertEqual(len(node["candidate_questions"]), 4)
        self.assertEqual(len(node["answer_dependencies"]), 2)
        self.assertFalse(node["source_identity_authenticated"])
        self.assertFalse(node["automatic_admission"])

    def test_reentry_needs_zero_new_questions_but_rechecks_owner(self):
        owner = synthetic_owner(102, true_pairs={(1, 0)})
        node = investigate(self.left, self.right, self.registry, owner)
        count = owner.query_count
        before = owner.recheck_count
        saved = json.loads(json.dumps(node))
        receipt = reenter(saved, self.registry, owner)
        self.assertEqual(receipt["status"], "SCOPED_COLLECTIVE_RESULT_RECHECKED")
        self.assertEqual(receipt["new_source_queries"], 0)
        self.assertEqual(owner.query_count, count)
        self.assertGreater(owner.recheck_count, before)
        self.assertEqual(receipt["answer_node"], node)

    def test_negative_certified_only_under_closed_finite_domain(self):
        owner = synthetic_owner(103, true_pairs={(0, 0)})
        node = investigate(self.left, self.right, self.registry, owner)
        self.assertEqual(node["status"], "PROVED_NO_LINK_WITHIN_DECLARED_FINITE_SCOPE")
        self.assertIsNone(node["positive_witness_pair"])
        self.assertEqual(owner.query_count, 4)
        self.assertTrue(verify_packet(node, self.registry, owner))
        self.assertTrue(node["negative_result_is_only_finite"])

    def test_open_world_negative_is_not_global_negative(self):
        owner = synthetic_owner(103, true_pairs={(0, 0)}, closed=False)
        node = investigate(self.left, self.right, self.registry, owner)
        self.assertEqual(node["status"], "HOLD_UNRESOLVED_BRIDGE_RELATION")
        self.assertTrue(verify_packet(node, self.registry, owner))

    def test_budget_exhaustion_is_hold(self):
        owner = synthetic_owner(105, true_pairs={(1, 0)})
        node = investigate(self.left, self.right, self.registry, owner, budget=1)
        # First probe is (2,2), so a different positive remains unobserved.
        self.assertEqual(node["status"], "HOLD_UNRESOLVED_BRIDGE_RELATION")
        self.assertEqual(len(node["observations"]), 1)
        self.assertTrue(verify_packet(node, self.registry, owner))

    def test_resign_source_record_cannot_turn_false_into_true(self):
        owner = synthetic_owner(106, true_pairs={(2, 2)})
        node = investigate(self.left, self.right, self.registry, owner)
        bad = copy.deepcopy(node)
        bad["observations"][0]["observation"] = False
        bad["observations"][0]["integrity_digest"] = digest({
            k: v for k, v in bad["observations"][0].items()
            if k != "integrity_digest"
        })
        bad["status"] = "HOLD_UNRESOLVED_BRIDGE_RELATION"
        bad["positive_witness_pair"] = None
        reseal(bad)
        with self.assertRaises(ProofError):
            verify_packet(bad, self.registry, owner)

    def test_modified_proof_source_can_not_inherit_earlier_claim(self):
        owner = synthetic_owner(107, true_pairs={(2, 2)})
        node = investigate(self.left, self.right, self.registry, owner)
        bad = copy.deepcopy(node)
        bad["right_proof_node"]["answer"]["output_mask"] ^= 1
        bad["right_proof_node"]["integrity_digest"] = digest({
            k: v for k, v in bad["right_proof_node"].items()
            if k != "integrity_digest"
        })
        reseal(bad)
        with self.assertRaises(ProofError):
            verify_packet(bad, self.registry, owner)

    def test_revoked_owner_revision_invalidates_cached_link(self):
        original = synthetic_owner(108, true_pairs={(2, 2)})
        node = investigate(self.left, self.right, self.registry, original)
        revised = synthetic_owner(108, true_pairs=set(), revision=2)
        with self.assertRaises(ProofError):
            reenter(node, self.registry, revised)

    def test_false_relation_outside_relevant_masks_does_not_count(self):
        owner = synthetic_owner(109, true_pairs={(0, 0), (0, 1)})
        node = investigate(self.left, self.right, self.registry, owner)
        self.assertEqual(node["status"], "PROVED_NO_LINK_WITHIN_DECLARED_FINITE_SCOPE")
        self.assertFalse(reference_evaluator_only(owner, node["candidate_questions"]))
        self.assertTrue(verify_packet(node, self.registry, owner))

    def test_missing_parent_proof_rejected(self):
        owner = synthetic_owner(110, true_pairs={(2, 2)})
        node = investigate(self.left, self.right, self.registry, owner)
        bad = copy.deepcopy(node)
        bad["left_proof_node"]["proof_memory"]["source_cards"].pop()
        bad["left_proof_node"]["proof_memory"]["integrity_digest"] = digest({
            k: v for k, v in bad["left_proof_node"]["proof_memory"].items()
            if k != "integrity_digest"
        })
        bad["left_proof_node"]["integrity_digest"] = digest({
            k: v for k, v in bad["left_proof_node"].items()
            if k != "integrity_digest"
        })
        reseal(bad)
        with self.assertRaises(ProofError):
            verify_packet(bad, self.registry, owner)

    def test_unsupported_budget_and_authority_escalation(self):
        owner = synthetic_owner(111, true_pairs={(2, 2)})
        for bad in (-1, 5, True):
            with self.assertRaises(ProofError):
                investigate(self.left, self.right, self.registry, owner, budget=bad)
        node = investigate(self.left, self.right, self.registry, owner)
        node["installed"] = True
        reseal(node)
        with self.assertRaises(ProofError):
            verify_packet(node, self.registry, owner)

    def test_missing_input_evidence_is_no_question_not_imagined_link(self):
        owner = synthetic_owner(112, true_pairs={(2, 2)})
        empty = copy.deepcopy(self.left)
        # A forged 0 mask, even if checksum recomputed, cannot eliminate proof.
        empty["answer"]["output_mask"] = 0
        empty["integrity_digest"] = digest({
            k: v for k, v in empty.items() if k != "integrity_digest"
        })
        with self.assertRaises(ProofError):
            derive_questions(empty, self.right, self.registry, owner.contract())

    def test_policy_ties_strong_classical_exact_expected_cost(self):
        owner = synthetic_owner(113)
        candidate = derive_questions(self.left, self.right,
                                     self.registry, owner.contract())
        picked = policy_order(candidate)
        classical, optimum = exhaustive_classical_reference(candidate)
        self.assertEqual(expected_cost(picked), optimum)
        self.assertEqual(expected_cost(classical), optimum)

    def test_valid_conclusions_match_hidden_evaluator_on_32_worlds(self):
        successful = 0
        all_no = 0
        for seed in range(300, 332):
            owner = synthetic_owner(seed)
            node = investigate(self.left, self.right, self.registry, owner)
            truth = reference_evaluator_only(owner, node["candidate_questions"])
            self.assertEqual(node["status"] == "FOUND_VERIFIED_FINITE_LINK", truth)
            self.assertTrue(verify_packet(node, self.registry, owner))
            successful += int(truth)
            all_no += int(not truth)
        self.assertGreater(successful, 0)
        self.assertGreater(all_no, 0)


if __name__ == "__main__":
    unittest.main()
