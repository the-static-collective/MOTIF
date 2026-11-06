"""Evidence incidence keeps source-native demonstration separate from task proof."""
import copy
import hashlib
import json
import unittest

import hypergraph as hg
import receipt_bridge as bridge
import triad


def digest(v):
    x={k:z for k,z in v.items() if k!="receipt_sha256"}
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def native_fixture():
    results=[]
    for ad in triad.ADAPTERS:
        results.append({
            "adapter":ad.id,
            "source_commit":ad.commit,
            "artifact_kind":ad.artifact_kind,
            "source_native_demo":True,
            "this_is_synthetic_not_shared_real_evidence":True,
            "isolated_no_network_read_only":True,
            "reduced_result":{"synthetic_example":"fixture only"},
            "native_receipt_sha256":"a"*64,
        })
    obj={
        "schema":triad.SCHEMA,
        "status":"SOURCE_NATIVE_SYNTHETIC_TRIAL",
        "selected":[x.id for x in triad.ADAPTERS],
        "results":results,
        "no_inference_transfer_across_distinct_synthetic_worlds":True,
        "cross_method_compatibility":"UNPROVEN",
        "automatically_approved_additional_branches":0,
        "external_action_executed":False,
        "authority":"NONE",
    }
    obj["receipt_sha256"]=digest(obj)
    return obj


class ReceiptBridgeTests(unittest.TestCase):
    def test_valid_independent_receipts_do_not_create_affordance_truth(self):
        evidence=bridge.validate_native(native_fixture())
        self.assertEqual(len(evidence["evidence_vertices"]),3)
        self.assertEqual(len(evidence["evidence_hyperedges"]),3)
        self.assertEqual(evidence["admitted_new_affordance_edges"],0)
        self.assertFalse(evidence["cross_method_task_improvement_measured"])
        self.assertEqual(evidence["authority"],"NONE")

    def test_cross_method_proposal_remains_hypothesis(self):
        task=hg.example_tasks()[0]
        result=bridge.join(task,native_fixture())
        self.assertEqual(len(result["route"]["selected"]["selected"]),2)
        self.assertIsNone(result["actual_shared_task_outcomes"])
        self.assertEqual(result["cross_method_interoperability"],"UNPROVEN")
        self.assertTrue(result["source_demo_worlds_are_distinct"])

    def test_checksum_tampering_hold(self):
        bad=native_fixture()
        bad["results"][0]["reduced_result"]["synthetic_example"]="rewrite"
        with self.assertRaisesRegex(hg.HOLD,"checksum"):
            bridge.validate_native(bad)

    def test_identity_tampering_holds_even_with_recalculated_checksum(self):
        bad=native_fixture()
        bad["results"][0]["source_commit"]="f"*40
        bad["receipt_sha256"]=digest(bad)
        with self.assertRaisesRegex(hg.HOLD,"Pinned"):
            bridge.validate_native(bad)

    def test_authority_tampering_holds_even_with_recomputed_checksum(self):
        bad=native_fixture()
        bad["authority"]="AUTONOMOUS"
        bad["receipt_sha256"]=digest(bad)
        with self.assertRaisesRegex(hg.HOLD,"authority"):
            bridge.validate_native(bad)

    def test_claimed_joint_interoperability_holds(self):
        bad=native_fixture()
        bad["cross_method_compatibility"]="VERIFIED"
        bad["receipt_sha256"]=digest(bad)
        with self.assertRaisesRegex(hg.HOLD,"authority"):
            bridge.validate_native(bad)

    def test_missing_method_receipt_holds(self):
        bad=native_fixture()
        bad["results"].pop()
        bad["receipt_sha256"]=digest(bad)
        with self.assertRaisesRegex(hg.HOLD,"Misaligned"):
            bridge.validate_native(bad)

    def test_future_unreviewed_branch_receipt_holds(self):
        bad=native_fixture()
        bad["selected"]=["future.unreviewed"]
        bad["results"]=bad["results"][:1]
        bad["receipt_sha256"]=digest(bad)
        with self.assertRaisesRegex(hg.HOLD,"Unknown installed"):
            bridge.validate_native(bad)


if __name__=="__main__":
    unittest.main()
