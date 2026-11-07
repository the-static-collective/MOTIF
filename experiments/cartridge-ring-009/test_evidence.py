"""RING-009: case-witness, graph-honesty, relabeling and tamper tests.

The source-only unit fixtures below are NOT independent real-language
evidence; the workflow also runs the complete original program generator.
"""
from __future__ import annotations
from copy import deepcopy
import unittest

import benchmark,induce,search
# RING-008 also has an evidence_graph.py, and importing its engine can put
# RING-008 ahead of this directory on sys.path. Force the scoped module.
sys.path.insert(0,str(Path(__file__).resolve().parent))
import evidence_graph


class HypergraphAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=search.run()
        cls.heldout=benchmark.evaluate_frozen(cls.frozen)

    def test_automatic_source_rule_invention_and_falsification_both_preserved(self):
        g=evidence_graph.build(self.frozen,self.heldout)
        self.assertEqual(g["schema"],evidence_graph.SCHEMA)
        self.assertEqual(len(g["hyperedges"]),2)
        self.assertGreater(g["learned_new_relational_rule_instances"],5)
        self.assertFalse(g["invented_new_unrestricted_programming_primitives"])
        self.assertFalse(g["source_labels_independently_human_verified"])
        self.assertEqual(g["new_real_world_capability_edges_promoted"],0)
        target=g["hyperedges"][1]
        self.assertGreater(target["induced_abstention_count"],0)
        self.assertTrue(any(x.startswith("test:") for x in target["tails"]))
        self.assertGreater(len(target["heads"]),2)

    def test_lying_about_wrong_decisions_fails_even_with_rehashed_receipt(self):
        modified=deepcopy(self.heldout)
        row=modified["test_packets"][0]["models"]["induced_relational_operator"]
        row["metrics"]["wrong_decisive"]+=1
        modified["combined"]["induced_relational_operator"]["wrong_decisive"]+=1
        modified["receipt_sha256"]=induce.digest({
            k:v for k,v in modified.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"witnesses"):
            evidence_graph.build(self.frozen,modified)

    def test_forged_derived_rule_does_not_become_provenance_even_with_content_digest(self):
        broken=deepcopy(self.frozen)
        # Pretend to have learned an extra semantic cue never in train.
        new_rule=dict(broken["program"]["discovered_relational_operators"][0])
        new_rule["cue"]=["secret","new","capability"]
        broken["program"]["discovered_relational_operators"][0]=new_rule
        broken["program"]["receipt_sha256"]=induce.digest({
            k:v for k,v in broken["program"].items() if k!="receipt_sha256"})
        broken["receipt_sha256"]=induce.digest({
            k:v for k,v in broken.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(induce.HOLD,"Forbidden"):
            benchmark.verify_artifact(broken)

    def test_repeated_test_packet_does_not_count_as_independent_seed(self):
        altered=deepcopy(self.heldout)
        altered["test_packets"][1]["source_sha256"]=(
            altered["test_packets"][0]["source_sha256"])
        altered["receipt_sha256"]=induce.digest({
            k:v for k,v in altered.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Duplicate"):
            evidence_graph.build(self.frozen,altered)


if __name__=="__main__":
    unittest.main()
