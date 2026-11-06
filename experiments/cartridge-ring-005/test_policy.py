"""Falsify trained-policy source boundaries, future leakage and cost claims."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cartridge-ring-004"))
import fixtures, comparator, feedback
import policy, adaptive
import selective_worker as worker


def stub_training(seed,count=32):
    """TEST-ONLY substitute. Actual CI must also execute original 3 sources."""
    p,l=fixtures.generate(seed=seed,count=count)
    labels={x["id"]:x["expected"] for x in l["labels"]}
    rows=[]
    for item in p["cases"]:
        expected=labels[item["id"]]
        safe=expected!="HOLD"
        bit=expected=="PROVED_REACHABLE"
        rows.append({
            "id":item["id"],
            "native_source_types":[
                "GEOM-013.Revision.measure",
                "THOUGHT-014.LanguageSpace.explore",
                "REASON-006.run_council"],
            "language":{"speech_act":"CHALLENGE" if safe else "HOLD_EFFECT_REQUEST",
                        "status":"TYPED_ONLY" if safe else "HOLD",
                        "safe":safe,"baseline_safe":safe,"pen_state":"UNCHANGED"},
            "geometry":{
                "raw":{"value":bit,"authority":"NONE","status":"LOCAL_SYNTHETIC_REPLAY"},
                "repaired":{"value":bit,"authority":"NONE","status":"LOCAL_SYNTHETIC_REPLAY"},
                "learned_distinct_steps":2},
            "reason":{
                "raw":{"conclusion":expected if safe else None,
                       "source_revision":"test-owner","status":"CERTIFIED_SYNTHETIC_GRAPH_DECISION"},
                "repaired":{"conclusion":expected if safe else None,
                            "source_revision":"test-owner","status":"CERTIFIED_SYNTHETIC_GRAPH_DECISION"}},
        })
    native={
        "schema":"motif.shared-native-output.v1",
        "world":"ONE_SHARED_AUTHORED_SYNTHETIC_EVIDENCE_PACKET",
        "public_digest_sha256":comparator.canonical_digest(p),
        "authority":"NONE","external_action_executed":False,
        "language_model_kind":"TRAINED_NAIVE_BAYES_NOT_LLM",
        "language_model_calls":0,
        "results":rows,
    }
    report=comparator.summarize(p,l,native)
    return p,report


class ContextTests(unittest.TestCase):
    def test_all_five_possible_public_contexts_are_derived_without_hidden_truth(self):
        p,_=fixtures.generate(count=32)
        observed={policy.inspect(c)["context"] for c in p["cases"]}
        self.assertEqual(observed,set(policy.CONTENTS))

    def test_no_secret_label_in_feature_function_or_manifest(self):
        pairs=[stub_training(2026110615),stub_training(2026110616)]
        trained=policy.learn(pairs)
        public,_=fixtures.generate(seed=2026110617)
        plan=adaptive.manifest_for(trained,public)
        self.assertNotIn("labels",str(plan))
        self.assertTrue(plan["no_labels_in_route_manifest"])
        self.assertEqual(len(plan["routes"]),32)
        self.assertEqual(plan["public_digest_sha256"],policy.canonical(public))

    def test_frozen_policy_does_not_accept_unknown_source(self):
        p=policy.learn([stub_training(2026110615),stub_training(2026110616)])
        bad=copy.deepcopy(p)
        bad["source_pins"]["reason.proof-objection"]="a"*40
        bad["receipt_sha256"]=policy.canonical({
            k:v for k,v in bad.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(policy.HOLD,"policy contract"):
            policy.validate_policy(bad)

    def test_wrong_but_validly_rehashed_policy_cannot_automatically_admit(self):
        p=policy.learn([stub_training(2026110615),stub_training(2026110616)])
        bad=copy.deepcopy(p)
        bad["context_routes"]["RAW"]="RUN_NEW_GITHUB_BRANCH"
        bad["receipt_sha256"]=policy.canonical({
            k:v for k,v in bad.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(policy.HOLD,"invented"):
            policy.validate_policy(bad)

    def test_untested_context_remains_full_source_fallback(self):
        p,report=stub_training(2026110615,count=8)
        # No holdout from untrained contexts is inspected.
        trained=policy.learn([(p,report)])
        for label,data in trained["context_training"].items():
            if data["training_cases"]<policy.MIN_SUPPORT:
                self.assertFalse(data["candidate_accepted"])
                self.assertEqual(trained["context_routes"][label],
                                 policy.METHODS["PROOF"])

    def test_source_training_duplicates_do_not_count_as_independent(self):
        pair=stub_training(42)
        with self.assertRaisesRegex(policy.HOLD,"Duplicate"):
            policy.learn([pair,pair])

    def test_synthetic_proof_requested_never_omits_source_council(self):
        public,_=fixtures.generate(count=32)
        p=policy.learn([stub_training(2026110615),stub_training(2026110616)])
        routes=adaptive.manifest_for(p,public)
        for row in routes["routes"]:
            if row["requires_proof"] and row["context"]!="HOLD":
                self.assertEqual(row["route"],policy.METHODS["PROOF"])

    def test_native_worker_rejects_host_route_disagreement(self):
        public,_=fixtures.generate(count=32)
        p=policy.learn([stub_training(2026110615),stub_training(2026110616)])
        routes=adaptive.manifest_for(p,public)
        worker.validate_routes(public,routes)
        bad=copy.deepcopy(routes)
        bad["routes"][0]["route"]="STATIC_GATE_CUT_NO_NATIVE"
        bad["receipt_sha256"]=worker.digest({
            k:v for k,v in bad.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(ValueError,"incompatible"):
            worker.validate_routes(public,bad)

    def test_strong_policy_review_cannot_promote_uncertain_branch(self):
        p=policy.learn([stub_training(2026110615),stub_training(2026110616)])
        public,_=fixtures.generate(seed=2026110617)
        manifest=adaptive.manifest_for(p,public)
        native={
            "schema":"motif.ring005.selective-output.v1",
            "public_digest_sha256":worker.digest(public),
            "policy_digest_sha256":p["receipt_sha256"],
            "route_manifest_sha256":manifest["receipt_sha256"],
            "authority":"NONE","external_action_executed":False,
            "labels_not_provided":True,
            "results":[],
        }
        with self.assertRaisesRegex(adaptive.HOLD,"Unbound"):
            adaptive.check_execution(p,public,manifest,native)

    def test_feedback_can_only_demote_proven_failing_shortcut(self):
        p=policy.learn([stub_training(2026110615),stub_training(2026110616)])
        # Use an explicit test-only synthetic evaluation of a context failure.
        wrong_context=next(x for x in sorted(policy.CONTENTS)
                           if p["context_routes"][x]!=policy.METHODS["PROOF"])
        report={
            "schema":"motif.ring005.separate-heldout-evaluation.v1",
            "frozen_policy_receipt_sha256":p["receipt_sha256"],
            "public_source_sha256":"e"*64,
            "per_case":[{"context":wrong_context,"correct":False}],
        }
        report["receipt_sha256"]=adaptive.digest(report)
        newer=adaptive.revise(p,report)
        self.assertEqual(newer["context_routes"][wrong_context],policy.METHODS["PROOF"])
        self.assertEqual(newer["revision_status"],"DEMOTED_AFTER_MEASURED_ERROR")
        self.assertNotEqual(newer["receipt_sha256"],p["receipt_sha256"])
        policy.validate_policy(newer)


if __name__=="__main__":
    unittest.main()
