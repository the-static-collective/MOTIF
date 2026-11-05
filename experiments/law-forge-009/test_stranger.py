"""Adversarial LAW-FORGE-009 tests for portable entropy reason cartridge."""
from itertools import product
import inspect
import math
import unittest

import entropy_cartridge
from desk import dispatch, SCHEMA as DESK_SCHEMA
from entropy_cartridge import (
    EntropyCartridge, Proposal, SCHEMA, hypothesis_digest, shannon
)
from gap import diagnose, independent_core_check
from learner import (
    DOMAIN, MAX_QUERIES, Observation, Question, SourceContract,
    rule_library, fitted_indices
)
from stranger_owner import FAMILIES, Stranger, partitions
from trial import METHODS, benchmark, inquire, trial


class StrangerEntropyTests(unittest.TestCase):
    def test_the_cartridge_uses_real_shannon_not_unlabeled_gini(self):
        self.assertEqual(shannon(0), 0)
        self.assertEqual(shannon(1), 0)
        self.assertEqual(shannon(.5), 1)
        self.assertAlmostEqual(shannon(.25), .8112781244591328, places=12)
        with self.assertRaises(ValueError):
            shannon(1.1)
        self.assertEqual(len(rule_library()), 650)

    def test_entropy_cartridge_reuses_native_classical_008(self):
        code = inspect.getsource(entropy_cartridge)
        self.assertIn("from learner import", code)
        self.assertIn("fitted_indices", code)
        self.assertIn("make_desk", code)
        self.assertNotIn("import stranger_owner", code)

    def test_portable_cartridge_roundtrip_and_source_pin(self):
        world = Stranger("two_bit_xor", 1)
        model = EntropyCartridge(world.contract, world.initial())
        restored = EntropyCartridge.from_packet(model.packet())
        self.assertEqual(restored, model)
        self.assertEqual(model.id, restored.id)
        self.assertEqual(model.packet()["policy"],
                         "SHANNON_ENTROPY_PER_DECLARED_COST")
        self.assertEqual(model.packet()["hypothesis_language_digest"],
                         hypothesis_digest())
        self.assertFalse(model.packet()["real_world_authority"])

    def test_entropy_proposes_a_real_score_from_frozen_version_space(self):
        world = Stranger("two_bit_xor", 3)
        model = EntropyCartridge(world.contract, world.initial())
        proposal = model.propose(world.catalog())
        self.assertIsInstance(proposal, Proposal)
        self.assertGreater(proposal.entropy_bits, 0)
        self.assertLessEqual(proposal.entropy_bits, 1)
        self.assertAlmostEqual(
            proposal.information_per_cost,
            proposal.entropy_bits / proposal.card.unit_cost
        )
        self.assertEqual(proposal.supporting_evidence, model.source_digest)
        self.assertTrue(proposal.packet()["owner_must_execute"])

    def test_owner_must_execute_question_and_return_same_controls(self):
        world = Stranger("three_bit_or", 3)
        model = EntropyCartridge(world.contract, world.initial())
        proposal = model.propose(world.catalog())
        returned = world.execute(proposal.card)
        updated = model.ingest(proposal, returned, world.catalog())
        self.assertEqual(len(updated.observations), len(model.observations)+1)
        self.assertEqual(updated.budget_spent, proposal.card.unit_cost)
        self.assertNotEqual(updated.source_digest, model.source_digest)
        self.assertEqual(len(model.observations), 4)
        self.assertEqual(EntropyCartridge.from_packet(updated.packet()), updated)

    def test_stale_query_cannot_be_replayed_after_new_evidence(self):
        world = Stranger("three_bit_or", 0)
        old = EntropyCartridge(world.contract, world.initial())
        proposal = old.propose(world.catalog())
        result = world.execute(proposal.card)
        updated = old.ingest(proposal, result, world.catalog())
        with self.assertRaises(ValueError):
            updated.ingest(proposal, result, world.catalog())
        with self.assertRaises(ValueError):
            old.ingest(proposal, world.initial()[0], world.catalog())
        with self.assertRaises(ValueError):
            old.ingest(proposal, result, ())
        with self.assertRaises(ValueError):
            old.ingest(proposal, result,
                       tuple(q for q in world.catalog() if q != proposal.card))

    def test_model_lookup_overrides_conditional_hypothesis(self):
        world = Stranger("two_bit_xor", 2)
        model = EntropyCartridge(world.contract, world.initial())
        for row in world.initial():
            result = model.predict(row.x, world.contract)
            self.assertEqual(result["status"], "LOOKUP_WITNESSED")
            self.assertEqual(result["value"], row.y)

    def test_changed_revision_is_not_inferred_as_a_known_world(self):
        world = Stranger("two_bit_xor", 2)
        model = EntropyCartridge(world.contract, world.initial())
        changed = world.matching_new_epoch()
        self.assertEqual(model.predict(world.initial()[0].x, changed.contract)
                         ["status"], "HOLD_CHANGED_SOURCE_CONTRACT")

    def test_foreign_truth_evidence_and_modified_packets_refused(self):
        world = Stranger("two_bit_xor", 0)
        model = EntropyCartridge(world.contract, world.initial())
        p = model.packet()
        changed = (
            {"policy": "DO_ANYTHING"},
            {"real_world_authority": True},
            {"owner_must_execute": False},
            {"callback_url": "https://invalid.example"},
            {"hypothesis_language_digest": "0"*64},
            {"id": "entropy-" + "0"*24},
            {"evidence_digest": "0"*64},
            {"budget_spent": True},
            {"budget_spent": 25},
            {"max_budget": 128},
            {"observations": []}
        )
        for mutation in changed:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                EntropyCartridge.from_packet({**p, **mutation})
        with self.assertRaises(ValueError):
            EntropyCartridge(world.contract,
                             world.initial() + (
                                 Observation(world.initial()[0].x,
                                             1-world.initial()[0].y,
                                             world.contract.id),
                             ))

    def test_query_catalog_must_be_unique_and_source_owned(self):
        world = Stranger("two_bit_xor", 0)
        model = EntropyCartridge(world.contract, world.initial())
        card = world.catalog()[0]
        with self.assertRaises(ValueError):
            model.propose((card,card))
        with self.assertRaises(ValueError):
            model.propose(tuple(world.catalog()) + (card,))
        with self.assertRaises(ValueError):
            model.propose(world.catalog(), remaining_budget=25)
        with self.assertRaises(ValueError):
            model.propose(world.catalog(), remaining_budget=True)
        with self.assertRaises(ValueError):
            Question.from_packet({**card.packet(), "authority": "LIVE_WEB"})

    def test_challenge_source_disjoint_and_label_blind(self):
        for seed in range(7):
            with self.subTest(seed=seed):
                groups = partitions(seed)
                self.assertEqual([len(groups[k]) for k in (
                    "initial","catalog","review","test")],
                    [4,128,192,256])
                all_rows = [set(groups[k]) for k in groups]
                for i, a in enumerate(all_rows):
                    for b in all_rows[i+1:]:
                        self.assertTrue(a.isdisjoint(b))
        self.assertNotIn("conditional_mux",
                         str(Stranger("conditional_mux", 2).contract.packet()))

    def test_budget_limits_real_owner_queries(self):
        world = Stranger("two_bit_xor", 3)
        for budget in (0, 1, 12, 24):
            with self.subTest(budget=budget):
                desk, cartridge, questions, spent = inquire(
                    world, "shannon_entropy_cartridge", budget=budget
                )
                self.assertLessEqual(spent, budget)
                self.assertEqual(cartridge.budget_spent, spent)
                self.assertEqual(len(set(q.x for q in questions)), len(questions))
                self.assertLessEqual(len(desk.snapshot), 4+budget)
        with self.assertRaises(ValueError):
            inquire(world, budget=25)
        with self.assertRaises(ValueError):
            inquire(world, budget=True)

    def test_separate_native_stranger_source_refuses_unlisted_questions(self):
        world = Stranger("conditional_mux", 2)
        from learner import question_cost, consequence_weight
        not_in_catalog = next(x for x in partitions(2)["review"])
        forbidden = Question(not_in_catalog,
                             question_cost(not_in_catalog),
                             consequence_weight(not_in_catalog))
        with self.assertRaises(ValueError):
            world.execute(forbidden)

    def test_out_of_grammar_core_proves_relative_inadequacy(self):
        source = Stranger("four_bit_parity", 2)
        channels = source.important_channels
        observations = []
        for configuration in product((0, 1), repeat=4):
            x = [0]*12
            for idx, bit in zip(channels, configuration):
                x[idx] = bit
            observations.append(source.observe(tuple(x)))
        cartridge = EntropyCartridge(source.contract, tuple(observations))
        self.assertEqual(cartridge.survivor_indices, ())
        gap = diagnose(cartridge)
        self.assertIsNotNone(gap)
        self.assertLessEqual(len(gap.witness_core), len(observations))
        self.assertTrue(independent_core_check(cartridge, gap))
        self.assertEqual(gap.packet()["status"],
                         "HOLD_NO_RULE_IN_DECLARED_GRAMMAR")
        self.assertFalse(gap.packet()["real_world_authority"])

    def test_compatible_explanation_never_claims_a_grammar_gap(self):
        source = Stranger("single_bit", 2)
        model = EntropyCartridge(source.contract, source.initial())
        self.assertIsNone(diagnose(model))

    def test_grammar_inadequacy_cannot_be_used_as_authorization(self):
        source = Stranger("four_bit_parity", 2)
        from learner import controls
        rows = tuple(source.observe(x) for x in partitions(2)["initial"])
        skill = EntropyCartridge(source.contract, rows)
        result = dispatch({"schema": DESK_SCHEMA, "action": "diagnose",
                           "cartridge": skill.packet()})
        self.assertIn(result["status"], (
            "COMPATIBLE_WITH_DECLARED_GRAMMAR",
            "HOLD_NO_RULE_IN_DECLARED_GRAMMAR"
        ))
        self.assertFalse(result["real_world_authority"])

    def test_local_desk_create_propose_ingest_predict_roundtrip(self):
        world = Stranger("two_bit_xor", 0)
        rows = [{"x":list(row.x),"y":row.y,
                 "contract_id":row.contract_id,
                 "provenance":row.provenance} for row in world.initial()]
        created = dispatch({"schema": DESK_SCHEMA, "action": "create",
                            "source": world.contract.packet(),
                            "observations": rows})
        self.assertEqual(created["status"], "PROPOSE_ONLY")
        initial = created["cartridge"]
        requested = {
            "schema": DESK_SCHEMA, "action": "propose",
            "cartridge": initial,
            "catalog": [q.packet() for q in world.catalog()],
            "remaining_budget": 24
        }
        proposal = dispatch(requested)
        self.assertEqual(proposal["status"], "PROPOSE_ONLY")
        self.assertTrue(proposal["proposal"]["owner_must_execute"])
        choice = Question.from_packet(proposal["proposal"]["question"])
        response = world.execute(choice)
        receipt = {
            "x": list(response.x), "y": response.y,
            "contract_id": response.contract_id,
            "provenance": response.provenance
        }
        applied = dispatch({**requested,"action":"ingest",
                            "owner_observation": receipt,
                            "proposed_question": proposal["proposal"]})
        self.assertEqual(applied["status"], "PROPOSE_ONLY")
        self.assertEqual(applied["owner_receipt_authentication"], "NOT_PROVIDED")
        predicted = dispatch({"schema": DESK_SCHEMA, "action": "predict",
                              "cartridge": applied["cartridge"],
                              "source": world.contract.packet(),
                              "x": list(choice.x)})
        self.assertEqual(predicted["status"], "LOOKUP_WITNESSED")
        self.assertEqual(predicted["value"], response.y)

    def test_desk_denies_unapproved_executable_fields(self):
        world = Stranger("two_bit_xor", 2)
        packet = EntropyCartridge(world.contract, world.initial()).packet()
        base = {"schema": DESK_SCHEMA,"action":"predict",
                "cartridge":packet,"source":world.contract.packet(),
                "x":list(world.initial()[0].x)}
        self.assertEqual(dispatch({**base, "live_write":True})["status"],"REFUSE")
        self.assertEqual(dispatch({**base, "action":"exec"})["status"],"REFUSE")
        self.assertEqual(dispatch({**base, "cartridge":{
            **packet, "real_world_authority":True}})["status"],"REFUSE")

    def test_gini_and_shannon_are_different_explicit_classical_methods(self):
        source = Stranger("two_bit_xor",3)
        for method in ("shannon_entropy_cartridge","classical_gini_008",
                       "fixed_catalog","classical_tree","lookup_only"):
            with self.subTest(method=method):
                result=trial(source,method)
                self.assertEqual(result["initial_observations"],4)
                self.assertLessEqual(result["membership_cost"],24)
                self.assertEqual(result["stale_contract_status"],
                                 "HOLD_CHANGED_SOURCE_CONTRACT")
                self.assertEqual(result["heldout_total"],256)

    def test_frozen_comparison_is_honest_and_no_auto_promotion(self):
        receipt = benchmark()
        self.assertEqual(receipt["domain_size"],4096)
        self.assertEqual(receipt["source_owned_query_budget"],24)
        for method in METHODS:
            self.assertEqual(receipt["development"][method]["worlds"],
                             len(FAMILIES)*2)
            self.assertEqual(receipt["evaluation"][method]["worlds"],
                             len(FAMILIES)*5)
        self.assertEqual(receipt["external_actions"],0)
        self.assertFalse(receipt["automatic_promotion"])
        self.assertFalse(receipt["real_world_authority"])
        self.assertIn(receipt["frozen_selection"],
                      ("NO_METHOD_PROMOTION","PROPOSE_FOR_HUMAN_REVIEW"))


if __name__ == "__main__":
    unittest.main()
