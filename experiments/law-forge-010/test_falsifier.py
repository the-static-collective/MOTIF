"""Adversarial LAW-FORGE-010 falsification and matched classical audit tests."""
import inspect
import unittest
from itertools import product

import falsifier
from desk import SCHEMA as DESK_SCHEMA, dispatch
from entropy_cartridge import EntropyCartridge
from falsifier import (
    LEARN_BUDGET, AUDIT_BUDGET, POLICIES,
    AuditLedger, Challenge, Mutant,
    candidate_critics, choose_challenge, counterfactual_library, hamming,
)
from learner import Question, Observation, SourceContract, fitted_indices
from stranger_owner import Stranger, partitions, FAMILIES
from trial import identification, inquiry, trial, benchmark


class BlindFalsifierTests(unittest.TestCase):
    def test_critic_cannot_import_hidden_owner(self):
        program = inspect.getsource(falsifier)
        self.assertNotIn("import stranger_owner", program)
        self.assertNotIn("from stranger_owner import", program)
        self.assertIn("from entropy_cartridge import", program)
        self.assertEqual((LEARN_BUDGET, AUDIT_BUDGET), (12, 12))
        self.assertEqual(set(POLICIES), {
            "mutant_challenge", "classical_diversity", "classical_fixed",
            "classical_random", "no_audit"
        })

    def test_mutant_grammar_is_explicit_classical_counterfactual_library(self):
        corpus = counterfactual_library()
        self.assertEqual(len(corpus), 12+66+220)
        self.assertEqual(Mutant((1,)).changes(
            (0,1) + (0,)*10), 1)
        self.assertEqual(Mutant((1,2)).changes(
            (0,1) + (0,)*10), 0)
        with self.assertRaises(ValueError):
            Mutant((2,1))
        with self.assertRaises(ValueError):
            Mutant((1,1))
        with self.assertRaises(ValueError):
            Mutant((0,1,2,3))

    def test_hamming_distance_is_classical_not_entropy(self):
        self.assertEqual(hamming((0,)*12, (1,)*12), 12)
        self.assertEqual(hamming((0,)*12, (0,)*12), 0)
        with self.assertRaises(ValueError):
            hamming((0,)*11, (1,)*12)

    def test_learning_equal_for_every_audit_method(self):
        world = Stranger("two_bit_xor", 3)
        original, queries = identification(world)
        self.assertLessEqual(original.budget_spent, LEARN_BUDGET)
        self.assertEqual(original.source.id, world.contract.id)
        for policy in POLICIES:
            with self.subTest(policy=policy):
                ledger, recorded, audited, _ = inquiry(world, policy)
                self.assertEqual(ledger.learning, original)
                self.assertEqual(recorded, queries)
                self.assertLessEqual(ledger.audit_spent, AUDIT_BUDGET)
                self.assertLessEqual(ledger.learning.budget_spent +
                                     ledger.audit_spent, 24)
                self.assertLess(len(ledger.evidence.snapshot), 4096)

    def test_post_identification_cannot_start_with_many_candidates(self):
        world = Stranger("two_bit_xor", 3)
        initial = EntropyCartridge(world.contract, world.initial())
        # Four initial observations cannot justify treating the surviving
        # hypothesis space as a unique discovered explanation.
        self.assertGreater(len(initial.survivor_indices), 1)
        ledger = AuditLedger(initial)
        self.assertIsNone(ledger.propose(world.catalog()))
        self.assertIsNone(choose_challenge(
            initial, world.catalog(), "mutant_challenge", 12))

    def test_bounded_owner_challenges_only_after_one_candidate(self):
        world = Stranger("two_bit_xor", 2)
        learned, _ = identification(world)
        self.assertLessEqual(len(learned.survivor_indices), 1)
        if len(learned.survivor_indices) == 1:
            ledger = AuditLedger(learned)
            challenge = ledger.propose(world.catalog())
            self.assertIsNotNone(challenge)
            self.assertEqual(challenge.source_evidence_digest,
                             ledger.evidence.source_digest)
            self.assertTrue(challenge.packet()["owner_must_execute"])
            self.assertFalse(challenge.packet()["real_world_authority"])

    def test_challenge_cannot_use_unowned_or_forged_query(self):
        world = Stranger("two_bit_xor", 2)
        learned, _ = identification(world)
        if len(learned.survivor_indices) != 1:
            self.skipTest("Source did not identify a single candidate")
        ledger = AuditLedger(learned)
        proposal = ledger.propose(world.catalog())
        if proposal is None:
            self.skipTest("No admissible post-identification query")
        observed = world.execute(proposal.card)
        different = next(q for q in world.catalog()
                         if q.x != proposal.card.x)
        with self.assertRaises(ValueError):
            ledger.ingest(proposal, world.execute(different), world.catalog())
        with self.assertRaises(ValueError):
            ledger.ingest(proposal, observed, ())
        with self.assertRaises(ValueError):
            ledger.ingest(Challenge(
                proposal.card, proposal.policy, "a"*64,
                proposal.champion_rule, proposal.surviving_mutants,
                proposal.declared_score
            ), observed, world.catalog())
        with self.assertRaises(ValueError):
            ledger.ingest(proposal, observed,
                          tuple(q for q in world.catalog()
                                if q != proposal.card))

    def test_unmodified_actual_source_response_updates_new_immutable_ledger(self):
        world = Stranger("two_bit_xor", 2)
        learned, _ = identification(world)
        if len(learned.survivor_indices) != 1:
            self.skipTest("No single candidate in bounded source sample")
        ledger = AuditLedger(learned)
        proposal = ledger.propose(world.catalog())
        if proposal is None:
            self.skipTest("No available source query")
        observed = world.execute(proposal.card)
        changed = ledger.ingest(proposal, observed, world.catalog())
        self.assertNotEqual(changed.id, ledger.id)
        self.assertEqual(len(ledger.audit), 0)
        self.assertEqual(len(changed.audit), 1)
        self.assertEqual(changed.audit_spent, proposal.card.unit_cost)
        self.assertEqual(AuditLedger.from_packet(changed.packet()), changed)
        with self.assertRaises(ValueError):
            changed.ingest(proposal, observed, world.catalog())

    def test_in_grammar_source_cannot_yield_fabricated_gap(self):
        for family in ("single_bit", "two_bit_xor", "three_bit_or"):
            with self.subTest(family=family):
                result = trial(Stranger(family, 3))
                self.assertFalse(result["audit_discovered_new_gap"])
                self.assertFalse(result["learning_grammar_gap"])
                self.assertIsNone(result["audit_gap"])

    def test_source_rule_shift_remains_independent_review_problem(self):
        for family in ("drifting_pair_xor", "hidden_exception"):
            with self.subTest(family=family):
                result = trial(Stranger(family, 3))
                self.assertEqual(result["test_covered"], 0)
                self.assertFalse(result["decision"].startswith("ELIGIBLE"))

    def test_training_gap_certificate_is_relative_to_650_grammar(self):
        source = Stranger("four_bit_parity", 1)
        rows = []
        for assigned in product((0,1), repeat=4):
            x = [0]*12
            for idx, bit in zip(source.important_channels, assigned):
                x[idx] = bit
            rows.append(source.observe(tuple(x)))
        original = EntropyCartridge(source.contract, tuple(rows))
        self.assertEqual(original.survivor_indices, ())
        ledger = AuditLedger(original)
        gap = ledger.diagnosis()
        self.assertIsNotNone(gap)
        self.assertEqual(gap.packet()["proposal"],
                         "REQUEST_SOURCE_OWNED_GRAMMAR_REVIEW_ONLY")
        self.assertTrue(ledger.packet()["status"] == "HOLD_GRAMMAR_GAP")

    def test_audit_cartridge_packet_roundtrip_and_tamper_rejection(self):
        source = Stranger("two_bit_xor", 2)
        learning, _ = identification(source)
        ledger = AuditLedger(learning)
        packet = ledger.packet()
        self.assertEqual(AuditLedger.from_packet(packet), ledger)
        for change in (
            {"status":"APPROVED"},
            {"real_world_authority": True},
            {"endpoint":"https://invalid.example"},
            {"id":"blind-falsifier-"+"0"*24},
            {"source_evidence_digest":"0"*64},
            {"audit_budget_units":99},
            {"audit_cost_units":1},
            {"audit_policy":"UNAUTHORIZED"},
            {"owner_must_execute":False}
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                AuditLedger.from_packet({**packet, **change})

    def test_ledger_never_accepts_overbudget_derived_evidence(self):
        source = Stranger("three_bit_or", 2)
        original = EntropyCartridge(source.contract, source.initial())
        with self.assertRaises(ValueError):
            AuditLedger(original, audit_spent=13)
        with self.assertRaises(ValueError):
            AuditLedger(EntropyCartridge(source.contract,
                                         source.initial(),
                                         budget_spent=13))
        with self.assertRaises(ValueError):
            choose_challenge(original, source.catalog(),
                             "mutant_challenge", True)
        with self.assertRaises(ValueError):
            choose_challenge(original, source.catalog(),
                             "mutant_challenge", 13)

    def test_owner_catalog_review_and_test_are_truly_disjoint(self):
        for seed in range(7):
            with self.subTest(seed=seed):
                p = partitions(seed)
                for x in ("initial","catalog"):
                    self.assertTrue(set(p[x]).isdisjoint(p["review"]))
                    self.assertTrue(set(p[x]).isdisjoint(p["test"]))
                self.assertTrue(set(p["review"]).isdisjoint(p["test"]))
                self.assertEqual(len(p["catalog"]), 128)

    def test_policy_comparison_uses_same_identification_budget(self):
        source = Stranger("conditional_mux", 3)
        training = {}
        for policy in POLICIES:
            out = trial(source, policy)
            training[policy] = (out["learning_questions"],
                                out["learning_cost"],
                                out["hypotheses_after_learning"])
            self.assertLessEqual(out["audit_cost"], AUDIT_BUDGET)
            self.assertLessEqual(out["total_question_cost"], 24)
            self.assertEqual(out["test_total"], 256)
        self.assertEqual(len(set(training.values())), 1)

    def test_no_audit_has_zero_additional_source_cost(self):
        source = Stranger("conditional_mux", 3)
        ledger, _, audit, _ = inquiry(source, "no_audit")
        self.assertEqual(len(audit), 0)
        self.assertEqual(ledger.audit_spent, 0)
        self.assertEqual(trial(source, "no_audit")["audit_cost"], 0)

    def test_desk_open_propose_ingest_diagnose_no_external_execution(self):
        source = Stranger("two_bit_xor", 3)
        learned, _ = identification(source)
        opened = dispatch({
            "schema":DESK_SCHEMA,
            "action":"open",
            "learning_cartridge":learned.packet(),
            "policy":"mutant_challenge"
        })
        self.assertEqual(opened["status"],"PROPOSE_ONLY")
        packed = opened["audit_cartridge"]
        proposed = dispatch({
            "schema":DESK_SCHEMA,
            "action":"propose",
            "audit_cartridge":packed,
            "catalog":[q.packet() for q in source.catalog()]
        })
        self.assertIn(proposed["status"], (
            "PROPOSE_ONLY_SOURCE_QUESTION", "HOLD_NO_SUPPORTED_CHALLENGE"
        ))
        if proposed["question"] is not None:
            chosen = Question.from_packet(proposed["question"]["question"])
            witness = source.execute(chosen)
            ingested = dispatch({
                "schema":DESK_SCHEMA,
                "action":"ingest",
                "audit_cartridge":packed,
                "catalog":[q.packet() for q in source.catalog()],
                "proposed_challenge":proposed["question"],
                "owner_observation":{
                    "x":list(witness.x), "y":witness.y,
                    "contract_id":witness.contract_id,
                    "provenance":witness.provenance
                }
            })
            self.assertEqual(ingested["status"],"PROPOSE_ONLY")
            self.assertFalse(ingested["receipt_signature_verified"])
            self.assertEqual(AuditLedger.from_packet(
                ingested["audit_cartridge"]).audit[-1], witness)
        diagnosed = dispatch({
            "schema":DESK_SCHEMA,
            "action":"diagnose", "audit_cartridge":packed
        })
        self.assertIn(diagnosed["status"], (
            "NO_WITNESSED_GRAMMAR_GAP","HOLD_GRAMMAR_GAP"
        ))

    def test_desk_declines_privilege_escalation(self):
        source = Stranger("two_bit_xor", 2)
        learning, _ = identification(source)
        packet = AuditLedger(learning).packet()
        base = {"schema":DESK_SCHEMA,
                "action":"diagnose", "audit_cartridge":packet}
        self.assertEqual(dispatch({**base,"url":"https://invalid.example"})
                         ["status"],"REFUSE")
        self.assertEqual(dispatch({**base,"action":"eval"})["status"],"REFUSE")
        self.assertEqual(dispatch({
            **base,"audit_cartridge":{
                **packet,"real_world_authority":True
            }
        })["status"],"REFUSE")

    def test_desk_source_revision_change_holds_every_prediction(self):
        source = Stranger("two_bit_xor", 2)
        learning, _ = identification(source)
        packet = AuditLedger(learning).packet()
        reply = dispatch({
            "schema":DESK_SCHEMA,
            "action":"predict",
            "audit_cartridge":packet,
            "source":source.matching_new_epoch().contract.packet(),
            "x":list(source.initial()[0].x)
        })
        self.assertEqual(reply["status"],"HOLD_SOURCE_REVISION_CHANGED")

    def test_benchmark_records_falsification_and_compares_strong_controls(self):
        summary = benchmark()
        self.assertEqual(summary["learning_budget"],12)
        self.assertEqual(summary["post_identification_audit_budget"],12)
        self.assertEqual(summary["total_budget"],24)
        for policy in POLICIES:
            self.assertEqual(summary["development"][policy]["worlds"],
                             2*len(FAMILIES))
            self.assertEqual(summary["evaluation"][policy]["worlds"],
                             5*len(FAMILIES))
            self.assertEqual(summary["evaluation"][policy]["test_wrong"],0)
        self.assertEqual(summary["evaluation"]["no_audit"]["audit_cost"],0)
        self.assertFalse(summary["automatic_admission"])
        self.assertFalse(summary["real_world_authority"])
        self.assertIn(summary["frozen_method_decision"],
                      ("NO_METHOD_PROMOTION","PROPOSE_FOR_HUMAN_REVIEW_ONLY"))


if __name__ == "__main__":
    unittest.main()
