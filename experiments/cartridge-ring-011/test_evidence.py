"""Auditable graph receipts cannot conceal unsafe root readings or user provenance."""
from __future__ import annotations
from copy import deepcopy
import unittest

import corpus,search,benchmark,evidence_graph


class EvidenceGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=search.run()
        cls.observed=benchmark.evaluate_frozen(cls.frozen)

    def test_success_and_false_clearance_travel_in_same_conditional_hyperedge(self):
        output=evidence_graph.build(self.frozen,self.observed)
        self.assertEqual(output["schema"],evidence_graph.SCHEMA)
        self.assertEqual(len(output["hyperedges"]),2)
        self.assertGreater(output["hyperedges"][1]["source_derived_binder_metrics"][
            "exact_graphs"],0)
        self.assertGreater(output["hyperedges"][1]["false_root_action_readings"],0)
        self.assertEqual(output["hyperedges"][1]["unbound_cryptic_holds"],6)
        self.assertLess(output["hyperedges"][1]["difference_in_exact_graphs_vs_bigram"],0)
        self.assertTrue(output["hard_carrier_evidence_classes_preserved"])
        self.assertFalse(output["real_world_semantic_ontology_independently_invented"])
        self.assertEqual(output["new_executable_methods_installed"],0)

    def test_rehashed_underreported_false_root_count_is_not_accepted(self):
        changed=deepcopy(self.observed)
        changed["test_packets"][2]["comparisons"]["source_induced_scope_binder"][
            "metrics"]["false_root_action_promotion"]=0
        changed["combined"]["source_induced_scope_binder"][
            "false_root_action_promotion"]=0
        changed["receipt_sha256"]=corpus.digest({
            k:v for k,v in changed.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"case|Individual|disagree"):
            evidence_graph.build(self.frozen,changed)

    def test_duplicate_trial_is_not_independent_evidence(self):
        changed=deepcopy(self.observed)
        changed["test_packets"][2]["author_created_source_sha256"]=changed[
            "test_packets"][1]["author_created_source_sha256"]
        changed["receipt_sha256"]=corpus.digest({
            k:v for k,v in changed.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Duplicate"):
            evidence_graph.build(self.frozen,changed)

    def test_forged_carrier_truth_is_rejected_even_with_rehashed_packet(self):
        changed=deepcopy(self.observed)
        row=changed["test_packets"][0]["comparisons"][
            "source_induced_scope_binder"]["per_case"][0]
        row["target"]["EVIDENCE_STATUS"]="AUTHENTICATED_LYRIC_IS_PROOF"
        changed["receipt_sha256"]=corpus.digest({
            k:v for k,v in changed.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"carrier|Source-carrier"):
            evidence_graph.build(self.frozen,changed)


if __name__=="__main__":
    unittest.main()
