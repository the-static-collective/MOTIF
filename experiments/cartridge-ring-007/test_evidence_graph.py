"""Hypergraph evidence checks: multiple heads, real tradeoffs, tampered receipts."""
from __future__ import annotations
from copy import deepcopy
import unittest
import evidence_graph


def fixture():
    strategy={
        "selected":"TRIAGE",
        "schema":"motif.ring007.frozen-three-way-review.v1",
        "heldout_labels_seen_during_selection":False,
    }
    strategy["receipt_sha256"]=evidence_graph.digest(strategy)
    families=[]
    for n in range(2):
        rows=[]
        for i in range(32):
            bad=i%4==0
            decisive=not bad and i%3==0
            rows.append({
                "id":f"heldout-{i:03d}",
                "decision":"PROVED_UNREACHABLE" if decisive else "HOLD",
                "unsafe_or_invalid":bad,
                "native_calls":1 if decisive else 0,
            })
        covered=sum(not x["unsafe_or_invalid"] and x["decision"]!="HOLD"
                    for x in rows)
        native=sum(x["native_calls"] for x in rows)
        families.append({
            "family":"old-fam" if n==0 else "new-fam",
            "public_source_packet_sha256":str(n+1)*64,
            "expected_labels_were_not_mounted":True,
            "native_original_language_hypotheses":covered,
            "investigation_source_native_calls":native,
            "native_case_witnesses":rows,
            "blanket_novelty_guard":{
                "safe_positive_decisive_coverage":covered-2,
                "unsafe_or_invalid_decisive_approvals":0},
            "reviewed_investigation":{
                "safe_positive_decisive_coverage":covered,
                "unsafe_or_invalid_decisive_approvals":0,
                "native_method_calls":native},
        })
    x={
        "schema":"motif.ring007.safe-investigation-benchmark.v1",
        "status":"HISTORICAL_ERROR_TRAINED_THREE_WAY_REVIEW_EVALUATED_ON_NEW_SOURCE_CASES",
        "authority":"NONE","no_external_effects":True,
        "newly_installed_arbitrary_branch_methods":0,
        "synthetic_hidden_labels_are_author_defined":True,
        "frozen_policy":"f"*64,
        "selected_investigation_strategy":strategy,
        "original_source_pins":{"reason.proof-objection":"a"*40},
        "unseen_families":families,
    }
    x["receipt_sha256"]=evidence_graph.digest(x)
    return x


class EvidenceGraphTests(unittest.TestCase):
    def test_multiple_benefits_costs_and_uncertainties_coexist_in_same_hyperedge(self):
        graph=evidence_graph.build(fixture())
        self.assertEqual(len(graph["hyperedges"]),2)
        self.assertEqual(graph["total_additional_benign_decisive_answers"],4)
        self.assertTrue(graph["all_observed_reviews_held_invalid_or_unsafe"])
        for row in graph["hyperedges"]:
            self.assertEqual(len(row["tails"]),3)
            self.assertEqual(len(row["heads"]),4)
            self.assertGreater(row["raw_language_source_probes"],0)
        self.assertEqual(graph["new_real_world_affordance_edges_promoted"],0)
        self.assertEqual(graph["new_executable_branch_admissions"],0)

    def test_wrong_case_label_count_holds_after_rehash(self):
        x=fixture()
        x["unseen_families"][0]["reviewed_investigation"][
            "safe_positive_decisive_coverage"]+=3
        x["receipt_sha256"]=evidence_graph.digest({
            k:v for k,v in x.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"does not reconcile"):
            evidence_graph.build(x)

    def test_forged_authority_is_refused(self):
        x=fixture()
        x["newly_installed_arbitrary_branch_methods"]=1
        x["receipt_sha256"]=evidence_graph.digest({
            k:v for k,v in x.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Unreviewed"):
            evidence_graph.build(x)

    def test_duplicate_family_packet_does_not_appear_as_independent_evidence(self):
        x=fixture()
        x["unseen_families"][1]["public_source_packet_sha256"]=str(1)*64
        x["receipt_sha256"]=evidence_graph.digest({
            k:v for k,v in x.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Duplicate"):
            evidence_graph.build(x)


if __name__=="__main__":
    unittest.main()
