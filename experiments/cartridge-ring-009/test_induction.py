"""Counterexample-driven semantic relation invention contracts and source gates."""
from __future__ import annotations
import ast
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

import contrasts,induce,search


class InductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=contrasts.generate("train",seed=2026110901,repeats=4)
        cls.ast=induce.construct(
            cls.train,min_support=4,max_cue_tokens=3,max_gap=9,min_purity=1.0)

    def test_pair_common_action_is_discovered_not_supplied(self):
        a="please send the ledger to neighbors"
        b="what if someone were to send the ledger to neighbors"
        shared=induce.common_span(a,b)
        self.assertEqual(shared["common_tokens"],
                         ["send","the","ledger","to","neighbors"])
        self.assertEqual(shared["arm_a_before"],["please"])
        self.assertEqual(shared["arm_b_before"],[
            "what","if","someone","were","to"])

    def test_actual_learning_invents_new_typed_relational_instances(self):
        doc=self.ast
        self.assertGreater(doc["operator_instances_induced_from_examples"],5)
        self.assertGreater(doc["comparable_pairs"],20)
        self.assertIn("send",doc["semantic_anchors_inferred_from_overlapping_utterances"])
        self.assertTrue(all(x["derived_from"]==
                            "ANTI_UNIFICATION_OF_OPPOSITE_LABELS"
                            for x in doc["discovered_relational_operators"]))
        self.assertTrue(any(x["cue"]==["please"] and
                            x["inferred_speech_act"]=="ACT"
                            for x in doc["discovered_relational_operators"]))
        self.assertTrue(any(x["inferred_speech_act"]=="META"
                            for x in doc["discovered_relational_operators"]))
        self.assertEqual(doc["execution_authority"],"NONE")
        self.assertTrue(doc["no_new_python_opcodes_generated"])

    def test_same_verb_different_utterance_scope_produces_distinct_frames(self):
        act=induce.parse(self.ast,"please send the ledger to neighbors")
        meta=induce.parse(
            self.ast,"what if someone were to send the ledger to neighbors")
        self.assertEqual(act["frame"],{
            "mode":"ACT","topic":"RECORD","operator":"TRANSFER"})
        self.assertEqual(meta["frame"],{
            "mode":"META","topic":"RECORD","operator":"TRANSFER"})
        self.assertFalse("send" in [x["cue"] for x in
                                   self.ast["discovered_relational_operators"]])

    def test_unknown_predicate_and_ungrounded_language_abstains(self):
        for sentence in (
            "please transmogrify the ledger to neighbors",
            "what if a comet needs a new moon",
            "please run custom shell code",
        ):
            with self.subTest(sentence=sentence):
                self.assertIsNone(induce.parse(self.ast,sentence)["frame"])

    def test_changed_operator_name_or_arbitrary_code_denied(self):
        bad=deepcopy(self.ast)
        bad["discovered_relational_operators"][0]["opcode"]="$(__import__('os'))"
        bad["receipt_sha256"]=induce.digest({
            k:v for k,v in bad.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(induce.HOLD,"Forbidden"):
            induce.validate(bad)

    def test_case_unlabeled_difference_verified(self):
        contrasts.check(self.train,split="train")
        self.assertTrue(all(
            pair["a"]["frame"]["topic"]==pair["b"]["frame"]["topic"] and
            pair["a"]["frame"]["operator"]==pair["b"]["frame"]["operator"] and
            pair["a"]["frame"]["mode"]=="ACT" and
            pair["b"]["frame"]["mode"]=="META"
            for pair in self.train["pairs"]))
        self.assertTrue(all(
            set(pair["a"])=={"text","frame"} and
            set(pair["b"])=={"text","frame"}
            for pair in self.train["pairs"]))

    def test_missing_real_source_evidence_is_hold(self):
        corrupted=deepcopy(self.train)
        corrupted["pairs"][0]["a"]["frame"]["mode"]="META"
        corrupted["receipt_sha256"]=contrasts.digest({
            k:v for k,v in corrupted.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(ValueError,"Contrasts"):
            contrasts.check(corrupted,split="train")

    def test_unseen_challenge_is_not_imported_in_synthesis(self):
        sources=(Path(search.__file__).read_text(),
                 Path(induce.__file__).read_text())
        imports=[]
        for source in sources:
            for node in ast.walk(ast.parse(source)):
                if isinstance(node,ast.Import):
                    imports.extend(x.name for x in node.names)
                elif isinstance(node,ast.ImportFrom):
                    imports.append(node.module)
        self.assertNotIn("novel_pairs",imports)
        self.assertNotIn("benchmark",imports)

    def test_typed_operators_provide_hypotheses_never_actions(self):
        r=induce.parse(self.ast,"please edit the journal before noon")
        self.assertIn(r["status"],("HOLD","NONAUTHORITATIVE_FRAME_HYPOTHESIS"))
        if r["frame"] is not None:
            self.assertEqual(r["execution_authority"],"NONE")

    def test_original_source_commit_does_not_change(self):
        self.assertFalse(self.ast["full_natural_language_understanding_claimed"])
        self.assertEqual(self.ast["source_training_sha256"],
                         self.train["receipt_sha256"])


if __name__=="__main__":
    unittest.main()
