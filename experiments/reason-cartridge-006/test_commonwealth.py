"""Independent local test doubles; only native CI uses ORIGINAL Dogram."""
import json
import unittest

from commonwealth import (HOLD, Model, Ledger, pins, owner4, ToyOwner,
                          LocalObservationOwner, independent_specimen,
                          foreign_crosscheck, run_council, sha)
from cases import (redundant, fragile, absent, unresolved,
                   open_world, episodes)
from distill import learn, validate, Receiver, ROUTES
from trial import run, heldouts


def fake_dogram_receipt(q,name):
    """Tests ONLY: a local stub, not an original Dogram response."""
    specimen=independent_specimen(q,name+"-dogram")
    status=owner4.decide(q)["status"]
    reachable=status=="PROVED_REACHABLE"
    from pupil import digest
    receipt={
        "schema":"dogram.receipt/v0",
        "specimen_id":specimen["specimen_id"],
        "operator":"ablate","operator_version":1,
        "status":"OK","input_digest":"sha256:"+digest(specimen),
        "consumed_inputs":["inputs.graph","inputs.requested_targets","inputs.target"],
        "result":{"requested_targets":[{
            "source":"S","target":"T",
            "reachable_before":True,
            "reachable_after":reachable,
        }]},
    }
    return specimen,receipt


class CouncilTests(unittest.TestCase):
    def test_pinned_internal_sources(self):
        result=pins()
        self.assertEqual(len(result),3)
        self.assertEqual(len(result["003/pupil.py"]),40)

    def test_redundant_proof_critic_can_defend_without_reviewer(self):
        result=run_council(redundant(),name="t-strong")
        self.assertEqual(result["before"],"PROVED_REACHABLE")
        self.assertEqual(result["after"],"PROVED_REACHABLE")
        self.assertEqual(result["reason_for_stop"],"STOP_NO_MATERIAL_INQUIRY")
        self.assertEqual(result["marginal"]["contributions"]["OBJECTION"],2)
        self.assertEqual(result["marginal"]["new_source_facts"],0)
        self.assertEqual(result["marginal"]["duplicates_rejected"],1)

    def test_source_correction_resets_conclusion_no_vote(self):
        owner=ToyOwner("t-source",{("A","T"):False,("S","A"):True})
        r=run_council(fragile(),name="t-correction",source=owner)
        self.assertEqual((r["before"],r["after"]),
                         ("PROVED_REACHABLE","PROVED_UNREACHABLE"))
        self.assertEqual(owner.calls,1)
        self.assertEqual(r["marginal"]["new_source_facts"],1)
        self.assertTrue(r["marginal"]["no_vote_on_truth"])
        self.assertTrue(r["source_witnesses_changed"])

    def test_negative_claim_can_be_corrected(self):
        owner=ToyOwner("t-negative",{("A","T"):True})
        r=run_council(absent(),name="t-absence",source=owner)
        self.assertEqual((r["before"],r["after"]),
                         ("PROVED_UNREACHABLE","PROVED_REACHABLE"))
        self.assertEqual(owner.calls,1)

    def test_unknown_question_and_owner_observation(self):
        owner=LocalObservationOwner("t-new",{("S","B"):False,("A","T"):True})
        r=run_council(unresolved(),name="t-new-evidence",source=owner)
        self.assertEqual((r["before"],r["after"]),("UNKNOWN","PROVED_REACHABLE"))
        self.assertEqual(r["marginal"]["contributions"]["QUESTION"],1)
        self.assertEqual(owner.calls,1)
        self.assertEqual(r["marginal"]["new_source_facts"],1)

    def test_open_world_holds_and_no_one_invents_a_fact(self):
        r=run_council(open_world(),name="t-open")
        self.assertEqual(r["reason_for_stop"],"HOLD_OPEN_WORLD_OR_UNPROVED")
        self.assertFalse(r["source_witnesses_changed"])
        self.assertEqual(r["marginal"]["new_source_facts"],0)

    def test_without_owner_cannot_repair_proof(self):
        r=run_council(fragile(),name="t-no-source")
        self.assertEqual(r["reason_for_stop"],"HOLD_EXTERNAL_SOURCE_NOT_CONNECTED")
        self.assertEqual(r["after"],"PROVED_REACHABLE")
        r=run_council(unresolved(),name="t-no-source2")
        self.assertEqual(r["reason_for_stop"],"HOLD_SOURCE_OBSERVATION_NOT_AUTHORIZED")
        self.assertEqual(r["after"],"UNKNOWN")

    def test_economic_cost_prevents_source_review(self):
        owner=ToyOwner("expensive",{("A","T"):False,("S","A"):True})
        model=Model(.1,1.0,4.0,1.0)
        r=run_council(fragile(),name="t-expensive",source=owner,model=model)
        self.assertEqual(r["reason_for_stop"],"STOP_QUERY_COST_OR_BUDGET")
        self.assertEqual(owner.calls,0)
        self.assertEqual(r["after"],"PROVED_REACHABLE")

    def test_no_self_loop_rewards_or_unauthorized_credit(self):
        l=Ledger()
        first=l.add("PROOF","SOURCE_BOUND_CONCLUSION",
                    {"certified":True},"CHECKED",True)
        second=l.repeat(first)
        self.assertEqual((first["score"],second["score"]),(1,0))
        self.assertEqual(l.summary()["duplicates_rejected"],1)
        with self.assertRaises(HOLD):
            l.add("SOURCE_OWNER","SOURCE_REVISION",{"forged":True},"false",False)

    def test_native_dogram_is_different_algorithm_not_new_world_fact(self):
        q=fragile()
        sp,receipt=fake_dogram_receipt(q,"t-native")
        result=foreign_crosscheck(q,sp,receipt,"t-native-dogram")
        self.assertTrue(result["native_reachable"])
        self.assertFalse(result["source_authority_transferred"])
        self.assertTrue(result["does_not_count_as_independent_observed_fact"])
        with self.assertRaises(HOLD):
            foreign_crosscheck(q,sp,dict(receipt,status="REFUSE"),"t-native-dogram")
        corrupted=json.loads(json.dumps(receipt))
        corrupted["result"]["requested_targets"][0]["reachable_after"]=False
        with self.assertRaises(HOLD):
            foreign_crosscheck(q,sp,corrupted,"t-native-dogram")

    def test_native_source_refused_for_incomplete_or_open_world(self):
        with self.assertRaises(HOLD):
            independent_specimen(unresolved(),"t-refuse")
        with self.assertRaises(HOLD):
            independent_specimen(open_world(),"t-refuse")

    def test_bounded_training_is_not_majority_vote(self):
        reports=[run_council(q,name=name,source=owner)
                 for name,q,owner in episodes()]
        raw=learn(tuple(reports))
        packet=validate(raw)
        self.assertEqual(len(packet["routes"]),4)
        self.assertEqual(len(packet["teacher_episodes"]),5)
        self.assertEqual(packet["inference"],
                         "FIXED_ALLOWLIST_ROUTING_FROM_OBSERVED_VERIFIED_CONTRIBUTIONS")
        receiver=Receiver(raw)
        with self.assertRaises(HOLD):
            receiver.suggest(unresolved())
        review=receiver.preview(heldouts())
        self.assertEqual((review["cases"],review["errors"]),(5,0))
        with self.assertRaises(HOLD):
            receiver.admit("NOT_APPROVED",review["review_digest"])
        receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
        self.assertEqual(receiver.suggest(unresolved())["method"],
                         ROUTES["UNKNOWN"])

    def test_rehashed_routing_or_authority_tamper_rejected(self):
        raw=learn(tuple(run_council(q,name=name,source=src)
                        for name,q,src in episodes()))
        packet=json.loads(raw)
        for edit in ("route","authority","owner","status"):
            p=json.loads(json.dumps(packet))
            if edit=="route": p["routes"][0]["method"]="SEND_MESSAGE"
            elif edit=="authority":p["real_world_authority"]=True
            elif edit=="owner":p["source_blobs"]["005/engine.py"]="0"*40
            else:p["status"]="AUTO_EXECUTE"
            p["checksum_sha256"]=sha({k:v for k,v in p.items()
                                       if k!="checksum_sha256"})
            with self.subTest(edit=edit),self.assertRaises(HOLD):
                validate(json.dumps(p))

    def test_independent_reviewer_detects_false_expectations(self):
        raw=learn(tuple(run_council(q,name=name,source=src)
                        for name,q,src in episodes()))
        rec=Receiver(raw)
        changed=list(heldouts())
        changed[0]=(changed[0][0],changed[0][1],ROUTES["UNKNOWN"])
        report=rec.preview(tuple(changed))
        self.assertGreater(report["errors"],0)
        with self.assertRaises(HOLD):
            rec.admit("ADMIT_READ_ONLY",report["review_digest"])

    def test_local_trial_no_external_source_claim(self):
        report=run()
        self.assertEqual(report["source_reviews"],3)
        self.assertEqual(report["new_conclusions_from_local_fixture_reviews"],3)
        self.assertEqual(report["independent_method_review"],{"cases":5,"errors":0})
        self.assertEqual(report["duplicate_proposals_suppressed"],5)
        self.assertEqual(report["native_foreign_teacher_mode"],"NOT_RUN_LOCAL_ONLY")
        self.assertFalse(report["external_actions"])


if __name__=="__main__":
    unittest.main()
