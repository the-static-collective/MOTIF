"""Measured-synthetic hyperedges do not mutate install authority or claim causation."""
import copy
import unittest

import feedback
import fixtures
import comparator
from test_shared_world import native_fixture


def packet(seed):
    public,labels=fixtures.generate(seed=seed,count=8)
    return comparator.summarize(public,labels,native_fixture(public))


class FeedbackTests(unittest.TestCase):
    def test_multiuse_measured_edges_with_actual_common_case_ids(self):
        a,b=packet(82),packet(83)
        result=feedback.feedback([a,b])
        self.assertEqual(result["tested_case_count"],16)
        self.assertEqual(len(result["hyperedges"]),len(feedback.CONTROLS))
        self.assertEqual(len(result["vertices"]),2)
        self.assertEqual(result["verified_real_world_affordance_edges_added"],0)
        self.assertEqual(result["installed_executable_adapters_added"],0)
        self.assertEqual(result["authority"],"NONE")
        for edge in result["hyperedges"]:
            self.assertEqual(edge["kind"],"OBSERVED_SYNTHETIC_CONDITIONAL_ABLATION")
            self.assertTrue(any(x.startswith("trial:") for x in edge["tails"]))
            self.assertEqual(len(edge["heads"]),1)

    def test_duplicate_packet_cannot_double_count_staged_evidence(self):
        p=packet(84)
        with self.assertRaisesRegex(feedback.HOLD,"Duplicate evidence"):
            feedback.feedback([p,p])

    def test_tampered_prediction_even_with_recomputed_receipt_holds(self):
        p=packet(85)
        p["per_case"][0]["results"]["all_three_native"]="HOLD"
        p["receipt_sha256"]=feedback._hash({k:v for k,v in p.items()
                                           if k!="receipt_sha256"})
        with self.assertRaisesRegex(feedback.HOLD,"Summary disagrees"):
            feedback.feedback([p])

    def test_missing_complete_source_pins_holds(self):
        p=packet(86)
        p["method_source_pins"]["geometry.procedure-repair"]="f"*40
        p["receipt_sha256"]=feedback._hash({k:v for k,v in p.items()
                                           if k!="receipt_sha256"})
        with self.assertRaisesRegex(feedback.HOLD,"source pins"):
            feedback.feedback([p])

    def test_duplicate_case_id_with_updated_receipt_holds(self):
        p=packet(87)
        p["per_case"][1]["case_id"]=p["per_case"][0]["case_id"]
        p["receipt_sha256"]=feedback._hash({k:v for k,v in p.items()
                                           if k!="receipt_sha256"})
        with self.assertRaisesRegex(feedback.HOLD,"repeated case"):
            feedback.feedback([p])

    def test_authored_commonworld_not_external_realworld_claim(self):
        p=packet(88)
        p["independent_human_labeled_real_data"]=True
        p["receipt_sha256"]=feedback._hash({k:v for k,v in p.items()
                                           if k!="receipt_sha256"})
        with self.assertRaisesRegex(feedback.HOLD,"Unpermitted claim"):
            feedback.feedback([p])


if __name__=="__main__":
    unittest.main()
