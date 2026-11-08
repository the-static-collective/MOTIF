"""Negative evidence is an output of ambiguity, not permission to erase a reading."""
from __future__ import annotations
from copy import deepcopy
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import unittest

import lattice,calibration,evidence_graph

spec=spec_from_file_location(
    "ring012_trial_for_provenance",Path(__file__).resolve().parent/"benchmark.py")
trial=module_from_spec(spec)
spec.loader.exec_module(trial)


class EvidenceReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=calibration.calibrate()
        cls.report=trial.test(cls.policy)

    def test_one_multi_head_hyperedge_retains_ambiguity_and_wrong_singularity(self):
        graph=evidence_graph.build(self.policy,self.report)
        self.assertEqual(graph["schema"],evidence_graph.SCHEMA)
        self.assertEqual(len(graph["hyperedges"]),2)
        self.assertEqual(graph["hyperedges"][1]["total_test_cases"],120)
        self.assertGreater(graph["hyperedges"][1]["extra_hypothesized_readings"],0)
        self.assertTrue(graph["correlated_source_agreement_does_not_establish_truth"])
        self.assertTrue(graph["open_world_other_always_preserved"])
        self.assertFalse(graph["independent_real_world_language_competence_demonstrated"])
        self.assertEqual(graph["automatic_new_cartridge_admissions"],0)
        self.assertFalse(graph["external_action_executed"])

    def test_error_omission_even_with_new_digest_refused(self):
        forged=deepcopy(self.report)
        r=forged["test_packets"][1]["scores"]["open_perspective_lattice"]
        r["missing_authored_readings"]+=1
        forged["combined"]["open_perspective_lattice"]["missing_authored_readings"]+=1
        forged["receipt_sha256"]=lattice.digest({
            k:v for k,v in forged.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Evidence receipts"):
            evidence_graph.build(self.policy,forged)

    def test_forged_independent_witness_claim_fails(self):
        fake=deepcopy(self.report)
        fake["witnessed_source_methods_share_correlated_training"]=False
        fake["receipt_sha256"]=lattice.digest({
            k:v for k,v in fake.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Misrepresented"):
            evidence_graph.build(self.policy,fake)

    def test_duplicate_heldout_packet_cannot_double_as_evidence(self):
        forged=deepcopy(self.report)
        forged["test_packets"][1]["packet_sha256"]=forged[
            "test_packets"][0]["packet_sha256"]
        forged["receipt_sha256"]=lattice.digest({
            k:v for k,v in forged.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Duplicate"):
            evidence_graph.build(self.policy,forged)

    def test_unbound_author_missing_source_still_kept_as_question(self):
        g=evidence_graph.build(self.policy,self.report)
        held=g["hyperedges"][1]["unbound_cryptic_holds"]
        self.assertEqual(held,24)


if __name__=="__main__":
    unittest.main()
