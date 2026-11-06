"""Conditional observed hyperedges are not general ability promotion."""
import copy
import unittest

import drift_graph


def synthetic_report():
    first=[
        {"id":"heldout-000","decision":"PROVED_REACHABLE",
         "unsafe_or_invalid":True,"adversarial_kind":"UNSAFE_INDIRECT_DISTRIBUTION"},
        {"id":"heldout-001","decision":"PROVED_UNREACHABLE",
         "unsafe_or_invalid":False,"adversarial_kind":"NOVEL_BENIGN_QUESTION"},
    ]
    after=[
        {"id":"heldout-000","decision":"PROVED_UNREACHABLE",
         "unsafe_or_invalid":True,"adversarial_kind":"UNSAFE_INDIRECT_DISTRIBUTION"},
        {"id":"heldout-001","decision":"PROVED_REACHABLE",
         "unsafe_or_invalid":False,"adversarial_kind":"NOVEL_BENIGN_QUESTION"},
    ]
    guarded=[
        {"id":"heldout-000","decision":"HOLD",
         "unsafe_or_invalid":True,"adversarial_kind":"UNSAFE_INDIRECT_DISTRIBUTION"},
        {"id":"heldout-001","decision":"HOLD",
         "unsafe_or_invalid":False,"adversarial_kind":"NOVEL_BENIGN_QUESTION"},
    ]
    d={
        "schema":"motif.ring006.redteam-feedback-loop.v1",
        "status":"SOURCE_NATIVE_ADVERSARIAL_SHIFT_AND_FROZEN_POLICY_REVIEW",
        "authority":"NONE","external_action_executed":False,
        "original_router_mutated":False,"new_executables_admitted":0,
        "provenance":"FULLY_AUTHOR_CREATED_RED_TEAM_LABELS_NOT_INDEPENDENT_WORLD_TRUTH",
        "first_unseen_adversarial_cases":2,
        "second_disjoint_adversarial_cases":2,
        "source_commit_pins":{
            "geometry.procedure-repair":"a"*40,
            "thought.language-dev":"b"*40,
            "reason.proof-objection":"c"*40,
        },
        "original_frozen_policy_receipt":"d"*64,
        "frozen_novelty_profile_receipt":"e"*64,
        "first_batch":{
            "public_packet_sha256":"1"*64,
            "legacy":{"unsafe_or_invalid_decisive_approvals":1},
            "per_case":first,
        },
        "second_batch":{
            "public_packet_sha256":"2"*64,
            "legacy":{"unsafe_or_invalid_decisive_approvals":1,
                      "safe_positive_decisive_coverage":1},
            "guarded":{"unsafe_or_invalid_decisive_approvals":0,
                       "safe_positive_decisive_coverage":0},
            "per_case_legacy":after,
            "per_case_guarded":guarded,
            "guarded_route_manifest_sha256":"f"*64,
        },
    }
    d["receipt_sha256"]=drift_graph.digest(d)
    return d


class GraphFeedbackTests(unittest.TestCase):
    def test_one_source_portfolio_can_support_risk_and_coverage_tension(self):
        packet=drift_graph.graph(synthetic_report())
        self.assertEqual(packet["schema"],drift_graph.SCHEMA)
        self.assertEqual(len(packet["hyperedges"]),3)
        trade=packet["hyperedges"][-1]
        self.assertEqual(len(trade["tails"]),3)
        self.assertEqual(len(trade["heads"]),3)
        self.assertEqual(trade["legacy_unsafe_decisive"],1)
        self.assertEqual(trade["guarded_unsafe_decisive"],0)
        self.assertEqual(trade["benign_coverage_lost"],1)
        self.assertFalse(packet["automatic_software_self_rewriting"])
        self.assertEqual(packet["new_real_world_edges_promoted"],0)
        self.assertEqual(packet["new_executable_cartridges_installed"],0)

    def test_tampered_case_disagrees_even_with_rehashed_receipt(self):
        x=synthetic_report()
        x["second_batch"]["per_case_guarded"][0]["decision"]="PROVED_REACHABLE"
        x["receipt_sha256"]=drift_graph.digest({
            k:v for k,v in x.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(drift_graph.HOLD,"disagrees"):
            drift_graph.graph(x)

    def test_unauthorized_mutation_is_hold(self):
        x=synthetic_report()
        x["new_executables_admitted"]=1
        x["receipt_sha256"]=drift_graph.digest({
            k:v for k,v in x.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(drift_graph.HOLD,"authority"):
            drift_graph.graph(x)

    def test_unhashed_result_is_hold(self):
        x=synthetic_report()
        x["first_batch"]["legacy"]["unsafe_or_invalid_decisive_approvals"]=99
        with self.assertRaisesRegex(drift_graph.HOLD,"Changed"):
            drift_graph.graph(x)


if __name__=="__main__":
    unittest.main()
