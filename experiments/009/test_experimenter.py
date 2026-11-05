"""MOTIF-009: tree cartridges, bounded inquiry, and matched label budgets."""
import inspect
import json
import unittest
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import oracle
import learner
import cartridge
import experimenter
import benchmark


class TreeCartridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = oracle.spec_for("forward_join", 11)
        cls.train = oracle.split(cls.spec, "train", 80)
        cls.local = oracle.split(cls.spec, "validation", 32)
        cls.model = cartridge.fit_cartridge(cls.train)
        cls.raw = cartridge.export_cartridge(cls.model)

    def test_cartridge_roundtrip_is_semantically_identical(self):
        recovered = cartridge.validate_cartridge(self.raw)
        self.assertEqual(self.model, recovered)
        self.assertEqual(recovered.id, self.model.id)
        self.assertTrue(recovered.id.startswith("tree-"))
        self.assertEqual(len(recovered.counts), 4)
        self.assertEqual(sum(sum(x) for x in recovered.counts), 80)

    def test_predict_and_explain_are_readonly(self):
        case = self.local[0]
        prior = case.before
        row = learner.features(case.before, case.roles)
        exp = self.model.explain(row)
        self.assertEqual(exp["hypothesis"], self.model.predict(row))
        self.assertFalse(exp["real_world_authority"])
        self.assertEqual(prior, case.before)
        self.assertEqual(self.model.probability(row) >= 0, True)
        self.assertTrue(self.model.probability(row) <= 1)

    def test_source_package_has_no_world_objects_or_actions(self):
        data = json.loads(self.raw)
        self.assertNotIn("d11_", self.raw)
        self.assertNotIn("observed_after", self.raw)
        self.assertNotIn("execute", self.raw)
        self.assertEqual(data["status"], "PROPOSAL_ONLY")
        self.assertFalse(hasattr(cartridge.Cartridge, "dispatch"))

    def test_mismatched_checksum_is_held(self):
        tampered = self.raw.replace("PROPOSAL_ONLY", "ADMIT_PLAN_ONLY")
        with self.assertRaises(cartridge.HOLD):
            cartridge.validate_cartridge(tampered)

    def test_unknown_payload_field_is_rejected_even_if_rehashed(self):
        obj = json.loads(self.raw)
        obj["external_command"] = "fire"
        body = {k: v for k, v in obj.items() if k != "checksum_sha256"}
        obj["checksum_sha256"] = cartridge.checksum(body)
        with self.assertRaisesRegex(cartridge.HOLD, "fields"):
            cartridge.validate_cartridge(json.dumps(obj))

    def test_rehashed_impersonation_is_not_authentication(self):
        obj = json.loads(self.raw)
        obj["fit_balanced"] = 0.1234
        body = {k: v for k, v in obj.items() if k not in ("checksum_sha256", "id")}
        obj["id"] = "tree-" + cartridge.checksum(body)[:16]
        obj["checksum_sha256"] = cartridge.checksum({
            k: v for k, v in obj.items() if k != "checksum_sha256"})
        copied = cartridge.validate_cartridge(json.dumps(obj))
        self.assertNotEqual(copied.fit_balanced, self.model.fit_balanced)
        # Rehashing can mint a new well-formed packet; NOT proof of provenance.
        self.assertNotEqual(copied.id, self.model.id)

    def test_default_hold_and_preview_independent_of_admission(self):
        bay = cartridge.CartridgeBay()
        ticket = bay.offer(self.raw)
        self.assertNotIn(ticket, bay.admitted)
        with self.assertRaises(cartridge.HOLD):
            bay.predict_admitted(ticket, self.local[0].before, self.local[0].roles)

    def test_local_review_admits_readonly_prediction(self):
        bay = cartridge.CartridgeBay()
        ticket = bay.offer(self.raw)
        receipt = bay.review(ticket, "ADMIT_PREDICT_ONLY", "LOCAL_TEST",
                             self.local, min_balanced=0.65)
        self.assertEqual(receipt["decision"], "ADMIT_PREDICT_ONLY")
        self.assertFalse(receipt["real_world_authority"])
        result = bay.predict_admitted(ticket, self.local[0].before,
                                     self.local[0].roles)
        self.assertIsInstance(result["leaf_index"], int)

    def test_refuse_and_revoke_block_cartridge_use(self):
        bay = cartridge.CartridgeBay()
        ticket = bay.offer(self.raw)
        bay.review(ticket, "ADMIT_PREDICT_ONLY", "LOCAL_TEST", self.local)
        bay.revoke(ticket, "LOCAL_TEST")
        with self.assertRaises(cartridge.HOLD):
            bay.predict_admitted(ticket, self.local[0].before,
                                 self.local[0].roles)

    def test_other_world_vocabulary_requires_new_local_review(self):
        foreign = oracle.split(oracle.spec_for("forward_join", 23),
                               "validation", 32)
        bay = cartridge.CartridgeBay()
        ticket = bay.offer(self.raw)
        with self.assertRaisesRegex(cartridge.HOLD, "incompatible"):
            bay.review(ticket, "ADMIT_PREDICT_ONLY", "LOCAL_TEST",
                       foreign)

    def test_bad_local_accuracy_blocks_admission(self):
        bay = cartridge.CartridgeBay()
        ticket = bay.offer(self.raw)
        # Asking for impossible >1 threshold is a controlled rejection.
        with self.assertRaises(cartridge.HOLD):
            bay.review(ticket, "ADMIT_PREDICT_ONLY", "LOCAL_TEST",
                       self.local, min_balanced=1.01)

    def test_selector_cannot_import_hidden_rules(self):
        self.assertNotIn("from oracle import", inspect.getsource(experimenter))
        self.assertNotIn("import oracle\n", inspect.getsource(experimenter))
        self.assertNotIn("from oracle import", inspect.getsource(cartridge))
        self.assertNotIn("hidden_rule(", inspect.getsource(experimenter))

    def test_public_question_has_no_outcome_or_generator_flags(self):
        e = self.train[0]
        q = experimenter.public_question(2, e.before, e.roles)
        self.assertEqual(set(vars(q)), {"ticket", "before", "roles"})
        self.assertFalse(hasattr(q, "observed_after"))
        self.assertFalse(hasattr(q, "family"))
        self.assertFalse(hasattr(q, "hidden_rule"))

    def test_question_selection_is_deterministic_and_label_free(self):
        known = self.train[:16]
        committee = experimenter.train_committee(known, seed=12)
        unlabeled = [experimenter.public_question(i, e.before, e.roles)
                     for i,e in enumerate(self.train[16:])]
        a = experimenter.propose_question(unlabeled, known, committee)
        b = experimenter.propose_question(unlabeled, known, committee)
        self.assertEqual(a, b)
        self.assertIn(a.ticket, {q.ticket for q in unlabeled})
        self.assertFalse(a.answer_known)
        self.assertEqual(len(a.votes), 3)

    def test_duplicate_and_exhausted_queries_blocked(self):
        budget = experimenter.QueryBudget(1)
        budget.consume("Q00001")
        with self.assertRaises(ValueError):
            budget.consume("Q00001")
        with self.assertRaises(ValueError):
            budget.consume("Q00002")

    def test_oracle_resolution_requires_a_consumed_ticket(self):
        known = self.train[:16]
        committee = experimenter.train_committee(known)
        q = experimenter.public_question(19, self.train[19].before,
                                         self.train[19].roles)
        offer = experimenter.propose_question((q,), known, committee)
        with self.assertRaises(ValueError):
            experimenter.independent_oracle_answer(offer, {})

    def test_small_world_equal_label_budgets(self):
        one = benchmark.experiment("reverse_join", 11)
        self.assertEqual(one["oracle_answers_revealed_active"], benchmark.REQUESTS)
        self.assertEqual(one["oracle_answers_revealed_random"], benchmark.REQUESTS)
        self.assertEqual(one["checkpoints"]["0"]["active_balanced"],
                         one["checkpoints"]["0"]["random_balanced"])
        self.assertEqual(one["checkpoints"]["12"]["active_seen"], 28)
        self.assertEqual(one["checkpoints"]["12"]["random_seen"], 28)
        self.assertEqual(len({q["selected_ticket"] for q in one["questions"]}), 12)
        self.assertTrue(all(q["question_exposed_outcome_before_query"] is False
                            for q in one["questions"]))

    def test_full_benchmark_is_complete_and_reports_losses(self):
        result = benchmark.report()
        s = result["summary"]
        self.assertEqual(s["worlds"], 30)
        self.assertEqual(len(result["worlds"]), 30)
        self.assertEqual(s["active_wins"] + s["ties"] + s["active_losses"], 30)
        self.assertTrue(s["both_strategies_same_label_budget"])
        self.assertFalse(s["test_labels_available_to_selector"])
        self.assertFalse(s["oracle_rules_available_to_selector"])
        self.assertEqual(set(s["mean_learning_curve"]), {"0", "6", "12"})
        self.assertEqual(result["cartridge_local_review"]["admission"],
                         "ADMIT_PREDICT_ONLY")
        self.assertFalse(result["cartridge_local_review"]["real_authority"])


if __name__ == "__main__":
    unittest.main()
