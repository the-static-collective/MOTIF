"""COLLECTIVE-001: scoped evidence output, independent re-entry and refusal tests."""
import copy
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
for family in ("thought-025", "thought-026", "thought-027", "thought-028"):
    path = str(HERE.parent / family)
    if path not in sys.path:
        sys.path.insert(0, path)
sys.path.insert(0, str(HERE))

from specimens import BY_KEY
from proof_memory import ProofError, digest
from memory_benchmark import seeds, new_cases
from weave import investigate
from answer_weave import (first_answer, verify_answer, reenter,
                         investigate_new_task, SCHEMA)


def reseal(packet):
    packet["integrity_digest"] = digest({
        k: v for k, v in packet.items() if k != "integrity_digest"
    })
    return packet


class ProofCarryingReentryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task = BY_KEY["cancel_or_add"]
        cls.store = seeds()
        cls.inquiry = investigate(cls.task, cls.store, mode="compose")
        cls.inputs = {key: v for (key, _), v in zip(cls.task.fields, (3, 5))}
        cls.answer = first_answer(cls.task, cls.store, cls.inquiry, cls.inputs)
        cls.registry = cls.store.registry

    def test_actual_answer_node_contains_relevant_evidence_and_context(self):
        p = self.answer
        self.assertEqual(p["schema"], SCHEMA)
        self.assertEqual(p["answer"]["kind"], "SCOPED_SYNTHETIC_3BIT_RESULT")
        self.assertEqual(p["answer"]["output_mask"], 6)
        self.assertEqual(p["answer"]["owner_oracle_output_mask"], 6)
        self.assertEqual(p["answer"]["finite_oracle_cases_verified"], 64)
        self.assertEqual(p["answer"]["independent_template_cases_verified"], 64)
        self.assertEqual(len(p["relevant_evidence_nodes"]), 3)
        self.assertEqual([x["type"] for x in p["relevant_evidence_nodes"]],
                         ["SCOPED_SOURCE_PROOF", "SCOPED_SOURCE_PROOF",
                          "COMPOSED_SCOPED_PROOF"])
        self.assertEqual(len(p["proof_memory"]["source_cards"]), 2)
        self.assertEqual(len(p["proof_memory"]["derived_cards"]), 1)
        self.assertTrue(p["inquiry_receipt"]["development_observations"])
        self.assertFalse(p["automatic_admission"])
        self.assertTrue(verify_answer(p, self.registry)[0].verify_all())

    def test_round_trip_json_and_no_fresh_question_for_same_question(self):
        saved = json.loads(json.dumps(self.answer))
        r = reenter(saved, self.registry)
        self.assertEqual(r["new_development_queries"], 0)
        self.assertEqual(r["new_inference_or_model_calls"], 0)
        self.assertTrue(r["full_owner_proof_recheck_still_required"])
        self.assertEqual(r["answer_node"], self.answer)
        self.assertGreater(self.inquiry["development_queries"], 0)

    def test_related_inputs_reuse_same_verified_64_case_rule(self):
        a, b = [name for name, _ in self.task.fields]
        r = reenter(self.answer, self.registry, inputs={a: 7, b: 7})
        self.assertEqual(r["new_development_queries"], 0)
        self.assertEqual(r["answer_node"]["answer"]["output_mask"], 0)
        self.assertEqual(r["answer_node"]["answer"]["proof_digest"],
                         self.answer["answer"]["proof_digest"])
        self.assertTrue(verify_answer(r["answer_node"], self.registry))

    def test_new_domain_is_not_auto_certified_by_prior_memory(self):
        future = new_cases()["toggle_equipment"]
        r = investigate_new_task(self.answer, self.registry, future)
        self.assertEqual(r["task"], future.key)
        self.assertEqual(r["status"], "REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED")
        self.assertGreater(r["development_queries"], 0)
        self.assertEqual(r["frozen"]["correct"], 64)

    def test_relevant_lineage_only_not_unrelated_proof_cards(self):
        p = copy.deepcopy(self.answer)
        self.assertEqual(set(x["task_key"] for x in p["relevant_evidence_nodes"]),
                         {"food_safe", "food_donations", "cancel_or_add"})

    def test_answer_tamper_even_with_resealed_packet_fails(self):
        p = copy.deepcopy(self.answer)
        p["answer"]["output_mask"] ^= 1
        reseal(p)
        with self.assertRaises(ProofError):
            verify_answer(p, self.registry)

    def test_fabricated_development_evidence_resealed_but_rejected(self):
        p = copy.deepcopy(self.answer)
        p["inquiry_receipt"]["development_observations"][0][
            "source_owner_oracle_observed"] ^= 1
        p["inquiry_receipt"]["receipt_digest"] = digest({
            k: v for k, v in p["inquiry_receipt"].items()
            if k != "receipt_digest"
        })
        reseal(p)
        with self.assertRaises(ProofError):
            verify_answer(p, self.registry)

    def test_wrong_source_scope_refuses_reentry(self):
        altered = replace(self.task, description=self.task.description + " Revised.")
        reg = dict(self.registry)
        reg[self.task.key] = altered
        with self.assertRaises(ProofError):
            verify_answer(self.answer, reg)

    def test_forged_parent_attribution_rehashed_does_not_pass(self):
        p = copy.deepcopy(self.answer)
        card = p["proof_memory"]["derived_cards"][0]
        card["parent_proof_digests"] = [card["parent_proof_digests"][0]]
        card["proof_digest"] = digest({
            k: v for k, v in card.items() if k != "proof_digest"
        })
        p["proof_memory"]["integrity_digest"] = digest({
            k: v for k, v in p["proof_memory"].items() if k != "integrity_digest"
        })
        reseal(p)
        with self.assertRaises(ProofError):
            verify_answer(p, self.registry)

    def test_unsupported_task_refused_without_boolean_coercion(self):
        bad = new_cases()["ternary_unknown"]
        self.assertTrue(investigate(bad, self.store)["status"].startswith("HOLD_"))
        with self.assertRaises(ProofError):
            first_answer(bad, self.store, {"status": "HOLD"}, {"beliefs": 2, "update": 5})

    def test_bad_input_and_authority_escalation_rejected(self):
        a, b = [name for name, _ in self.task.fields]
        with self.assertRaises(ProofError):
            reenter(self.answer, self.registry, inputs={a: True, b: 5})
        with self.assertRaises(ProofError):
            reenter(self.answer, self.registry, inputs={"unrelated": 3})
        p = copy.deepcopy(self.answer)
        p["installed"] = True
        reseal(p)
        with self.assertRaises(ProofError):
            verify_answer(p, self.registry)

    def test_missing_source_proof_refused(self):
        p = copy.deepcopy(self.answer)
        p["proof_memory"]["source_cards"].pop()
        p["proof_memory"]["integrity_digest"] = digest({
            k: v for k, v in p["proof_memory"].items() if k != "integrity_digest"
        })
        reseal(p)
        with self.assertRaises(ProofError):
            verify_answer(p, self.registry)


if __name__ == "__main__":
    unittest.main()
