"""COLLECTIVE-004 independent-origin Graph Atlas heldout question-grammar controls."""
import copy
import os
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from question_inventor import HOLD, digest
from external_atlas import (
    run, source_module, carrier, external_queries, select_question,
    AtlasOwner, native_nx_eval, ATLAS_DATA_SHA256
)


class ExternalAtlasPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ["ATLAS_ROOT"]).resolve()
        cls.source=source_module(cls.root)
        cls.train,cls.test,cls.protocol=cls.source.cohort()
        cls.report=run(cls.root)

    def test_exact_external_source_and_original_split(self):
        self.assertEqual(self.protocol["atlas_data_sha256"],ATLAS_DATA_SHA256)
        self.assertEqual(len(self.train),14)
        self.assertEqual(len(self.test),28)
        self.assertTrue(self.protocol["original_carrier_authorship_independent_of_MOTIF"])
        self.assertTrue(self.protocol["benchmark_is_public_and_not_externally_blind"])
        self.assertEqual(len(set(tuple(t.atlas_ids) for t in self.train+self.test)),42)

    def test_all_predeclared_pairs_accounted_for_even_failed(self):
        t=self.report["train"]
        h=self.report["heldout"]
        self.assertEqual((t["total"],h["total"]),(14,28))
        self.assertEqual(h["old_menu_resolved"]+h["old_menu_unresolved"],28)
        self.assertEqual(h["new_grammar_additionally_resolved"]+
                         h["honest_new_grammar_holds"],h["old_menu_unresolved"])
        self.assertEqual(sum(1 for r in self.report["heldout_trials"]
                             if r["result"]=="HOLD_NEW_GRAMMAR_STILL_INSUFFICIENT"),
                         h["honest_new_grammar_holds"])

    def test_expected_atlas_performance_not_oversold(self):
        t=self.report["train"]
        h=self.report["heldout"]
        self.assertEqual(t["old_menu_unresolved"],3)
        self.assertEqual(t["new_grammar_additionally_resolved"],2)
        self.assertEqual(t["honest_new_grammar_holds"],1)
        self.assertEqual(h["old_menu_unresolved"],12)
        self.assertEqual(h["new_grammar_additionally_resolved"],10)
        self.assertEqual(h["honest_new_grammar_holds"],2)
        self.assertEqual(h["matched_classical_successes"],10)
        self.assertEqual(h["owner_questions_for_two_realizations"],20)
        self.assertTrue(self.report["equal_information_classical_best_same_grammar"])

    def test_independent_atlas_heldout_question_execution(self):
        source_proof={tuple(x["pair_ids"]):x for x in self.report["heldout_trials"]}
        for task in self.test:
            k=tuple(task.atlas_ids)
            g=tuple(carrier(x) for x in task.graphs)
            got=select_question(g)
            self.assertEqual(source_proof[k]["result"],got["status"])
            if got["status"]=="NEW_GRAMMAR_SEPARATES_ATLAS_PAIR":
                for idx,reply in enumerate(source_proof[k]["source_observations"]):
                    self.assertEqual(reply["actual_index_evaluator_only"],idx)
                    self.assertEqual(reply["identified_world_index"],idx)
                    self.assertEqual(reply["new_source_queries"],1)
                    self.assertEqual(reply["reentry_new_source_queries"],0)
                    self.assertEqual(reply["evidence_receipt"]["value"],
                                     native_nx_eval(got["selected_program"],g[idx]))
            elif got["status"]=="HOLD_NEW_GRAMMAR_STILL_INSUFFICIENT":
                self.assertEqual(source_proof[k]["fresh_source_calls"],0)
                self.assertTrue(source_proof[k]["no_outcome_claimed"])

    def test_cannot_forge_public_atlas_owner_receipt_even_by_rehashing(self):
        task=next(t for t in self.test if select_question(
            tuple(carrier(x) for x in t.graphs)
        )["status"]=="NEW_GRAMMAR_SEPARATES_ATLAS_PAIR")
        a,b=(carrier(x) for x in task.graphs)
        program=select_question((a,b))["selected_program"]
        owner=AtlasOwner(task.atlas_ids,a)
        receipt=owner.ask(program)
        owner.recheck(receipt)
        bad=copy.deepcopy(receipt)
        bad["value"]=not bad["value"]
        bad["integrity_digest"]=digest({
            k:v for k,v in bad.items() if k!="integrity_digest"
        })
        with self.assertRaises(HOLD):
            owner.recheck(bad)
        newer=AtlasOwner(task.atlas_ids,a,revision=2)
        with self.assertRaises(HOLD):
            newer.recheck(receipt)

    def test_public_data_not_mislabeled_as_blind_real_world_or_authorship(self):
        self.assertFalse(self.report["heldout_is_public_not_cryptographically_blind"] is False)
        self.assertTrue(self.report["question_oracle_is_synthetic_public_dataset_not_actual_external_agent"])
        self.assertTrue(self.report["no_new_scientific_law_or_historical_truth_proven"])
        self.assertFalse(self.report["automatic_admission"])
        self.assertFalse(self.report["installed"])


if __name__=="__main__":
    unittest.main()
