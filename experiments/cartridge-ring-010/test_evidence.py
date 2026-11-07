"""RING-010 source provenance, graph-invention and measured-risk audit tests."""
from __future__ import annotations
from copy import deepcopy
import unittest

import search,benchmark,evidence_graph,world,induce


class GraphEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=search.run()
        cls.outcome=benchmark.evaluate_frozen(cls.frozen)

    def test_graph_transitions_hypergraph_records_good_and_bad_head_outcomes(self):
        g=evidence_graph.build(self.frozen,self.outcome)
        self.assertEqual(g["schema"],evidence_graph.SCHEMA)
        self.assertEqual(len(g["hyperedges"]),2)
        graph_edge=g["hyperedges"][1]
        self.assertGreater(graph_edge["exact_semantic_graph"],0)
        self.assertGreater(graph_edge["false_directive_clearances"],0)
        self.assertGreater(graph_edge["wrong_decisive"],0)
        self.assertEqual(len(graph_edge["tails"]),5)
        self.assertEqual(len(graph_edge["heads"]),4)
        self.assertTrue(g["no_private_user_messages_copied_into_public_repo"])
        self.assertEqual(g["real_world_capability_edges_promoted"],0)

    def test_rehashed_misreported_false_directive_count_fails(self):
        b=deepcopy(self.outcome)
        row=b["test_packets"][1]["models"]["induced_graph_relations"]
        row["metrics"]["false_directive_clearance"]=0
        b["combined"]["induced_graph_relations"]["false_directive_clearance"]=0
        b["receipt_sha256"]=world.digest({
            k:v for k,v in b.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Case-level"):
            evidence_graph.build(self.frozen,b)

    def test_synthetic_hidden_source_identity_must_be_distinct(self):
        b=deepcopy(self.outcome)
        b["test_packets"][1]["packet_receipt_sha256"]=(
            b["test_packets"][0]["packet_receipt_sha256"])
        b["receipt_sha256"]=world.digest({
            k:v for k,v in b.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Duplicate"):
            evidence_graph.build(self.frozen,b)

    def test_operator_provenance_cannot_be_forged_with_plain_hash(self):
        a=deepcopy(self.frozen)
        new=a["winning_program"]
        new["source_derived_contextual_cue_operators"][0]["cue"]=[
            "approve","unsafe","remote","access"]
        new["receipt_sha256"]=world.digest({
            k:v for k,v in new.items() if k!="receipt_sha256"})
        a["receipt_sha256"]=world.digest({
            k:v for k,v in a.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(benchmark.HOLD,"reproducible"):
            benchmark.verify_artifact(a)


if __name__=="__main__":
    unittest.main()
