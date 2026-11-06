"""Adversarial verification of a source who can teach an unimagined condition.

These are author-designed FICTIONAL preference worlds. The two circles, four
elf subprocesses, conditional choice rule and exact consent audit do not
authenticate anyone, discover spiritual truths or measure a person's welfare.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import json
import unittest
from unittest.mock import patch

from casebook import CASES,by_id,training,heldout,world,ORDER
from source_private import EXPECTED,owner_rule,HIDDEN
from owner import SyntheticOther,SourceRefusal,digest as source_digest
from student import (HOLD,pin,all_programs,public_check,find_contradiction,
                     compile_source,preference,verify_response,digest,evaluate)
from mirror import (run as proposal,export,ConsentMemory,four_original_elves)
from reviewer import Receiver,verify,independent_heldout_reference
from trial import run


class OtherTeachesSelfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports={
            scene["case_id"]:proposal(scene,SyntheticOther(scene["case_id"]))
            for scene in CASES
        }

    def report(self,id):
        return self.reports[id]

    def test_public_contract_is_small_and_all_test_sources_are_separate(self):
        self.assertEqual(len(CASES),11)
        self.assertEqual(len(training()),3)
        self.assertEqual(len(heldout()),8)
        self.assertEqual(len(pin()),40)
        self.assertEqual(len(all_programs(2)),44)
        self.assertEqual(len(all_programs(3)),377)
        self.assertTrue(all(public_check(s) for s in CASES))
        self.assertEqual(len({x["case_id"] for x in CASES}),11)
        self.assertNotIn("UNHURRIED",str(CASES))
        self.assertNotIn("ROOM_TO_PAUSE",str(CASES))
        self.assertTrue(set(x["case_id"] for x in training()).isdisjoint(
            x["case_id"] for x in heldout()))

    def test_student_and_mirror_never_import_source_or_author_gold(self):
        import student,mirror
        for m in (student,mirror):
            tree=ast.parse(inspect.getsource(m))
            names=set()
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom) and node.module:
                    names.add(node.module)
                if isinstance(node,ast.Import):
                    names.update(x.name for x in node.names)
            for not_allowed in ("source_private","reviewer","owner"):
                self.assertNotIn(not_allowed,names)

    def test_contexts_look_same_before_hidden_distinction_is_earned(self):
        a=world(6);b=world(7)
        self.assertEqual(a["initial_features"],b["initial_features"])
        self.assertEqual(set(a["initial_features"]),{"PRIVATE","CHOICE"})
        self.assertNotIn("UNHURRIED",str(a))
        self.assertNotEqual(a["id"],b["id"])

    def test_learner_detects_old_representation_is_mathematically_insufficient(self):
        r=self.report("T02")
        old=r["learner"]["contradiction"]
        self.assertIsNotNone(old)
        x,y=old["different_source_answers"]
        self.assertEqual(world(int(x.split("-")[1]))["initial_features"],
                         world(int(y.split("-")[1]))["initial_features"])
        labels={z["id"]:z["reply"] for z in r["learner"]["author_observations"]}
        self.assertNotEqual(labels[x],labels[y])
        self.assertEqual(r["learner"]["state"],"ADDED_FEATURE")

    def test_learner_does_not_invent_a_missing_dimension_for_an_old_sufficient_rule(self):
        r=self.report("T01")
        self.assertEqual(r["learner"]["state"],"BASE_SUFFICIENT")
        self.assertIsNone(r["learner"]["contradiction"])
        self.assertIsNone(r["learner"]["learned_additional_feature"])
        self.assertIsNone(r["learner"]["source_disclosed_feature_receipt"])
        self.assertEqual(r["state"],"SUGGEST_DISCUSSION_ONLY")

    def test_a_person_teaches_new_typed_condition_not_hardcoded_in_learner(self):
        for case,name in (("T02","UNHURRIED"),
                          ("T03","ROOM_TO_PAUSE"),
                          ("H02","ROOM_TO_PAUSE")):
            r=self.report(case)
            self.assertEqual(r["learner"]["learned_additional_feature"],name)
            self.assertEqual(len(r["learner"]["feature_names"]),3)
            self.assertTrue(r["learner"]["syntax_is_relational_DNF_not_new_logic"])
            self.assertTrue(r["learner"][
                "unknown_feature_disclosed_by_source_not_invented_from_silence"])
            self.assertEqual(r["learner"]["equivalent_signatures_after_training"],1)

    def test_two_term_compositional_relation_is_actually_inferred(self):
        r=self.report("T03")
        program=r["learner"]["program"]
        self.assertEqual(len(program),2)
        self.assertEqual(r["learner"]["state"],"ADDED_FEATURE")
        self.assertEqual([preference(r["learner"],world(i,"HELDOUT")["id"])
                          for i in range(8)],
                         [owner_rule(HIDDEN["T03"][0],i) for i in range(8)])

    def test_heldout_contexts_are_evaluated_without_source_label_download(self):
        for s in CASES:
            report=self.report(s["case_id"])
            check=independent_heldout_reference(s,report)
            if report["learner"]["state"] in ("BASE_SUFFICIENT","ADDED_FEATURE"):
                self.assertEqual(check["correct"],8)
                self.assertEqual(check["misclassified"],0)
                self.assertEqual(check["tested"],8)
            else:
                self.assertEqual(check["tested"],0)

    def test_person_can_refuse_the_missing_dimension_and_motif_holds(self):
        r=self.report("H03")
        self.assertEqual(r["learner"]["state"],"HOLD_SOURCE_FEATURE_WITHHELD")
        self.assertIsNotNone(r["learner"]["contradiction"])
        self.assertIsNone(r["learner"]["program"])
        self.assertIsNone(r["recommended_action"])
        self.assertEqual(r["state"],"HOLD_SOURCE_FEATURE_WITHHELD")
        self.assertIsNone(r["actual_scope_response"])

    def test_source_no_contact_prevents_source_questions_even_if_self_wishes_it(self):
        for case in ("H04","H06"):
            r=self.report(case)
            self.assertEqual(r["state"],"HOLD_NO_CONTACT")
            self.assertEqual(r["learner"]["questions"],[])
            self.assertIsNone(r["actual_scope_response"])
            self.assertIsNone(r["recommended_action"])
            self.assertFalse(r["perspective_reports"]["CRITIC"][
                "judgments"]["OFFER_OPTIONS_ONLY"]["eligible"])

    def test_hypothetically_welcome_is_not_permission_for_a_particular_action(self):
        r=self.report("H01")
        self.assertTrue(r["inferred_source_welcome_not_consent"])
        self.assertEqual(r["actual_scope_response"]["response"],"NO")
        self.assertEqual(r["state"],"HOLD_SCOPED_PERMISSION_DECLINED")
        self.assertIsNone(r["recommended_action"])
        self.assertIn("NO_ACTION_SCOPED_CONSENT",r["critic_source_blockers"])

    def test_not_welcome_does_not_trigger_permission_asking(self):
        r=self.report("H07")
        self.assertEqual(r["learner"]["state"],"BASE_SUFFICIENT")
        self.assertFalse(r["inferred_source_welcome_not_consent"])
        self.assertEqual(r["state"],"HOLD_OTHER_WOULD_NOT_WELCOME")
        self.assertIsNone(r["actual_scope_response"])
        self.assertIsNone(r["recommended_action"])

    def test_other_can_welcome_what_the_self_would_not_prefer(self):
        r=self.report("H02")
        self.assertEqual(r["state"],"SUGGEST_DISCUSSION_ONLY")
        self.assertEqual(r["role_reversal_class"],
                         "PREFERENCE_ASYMMETRY_ACCEPT_OTHER_VOICE")
        self.assertEqual(r["recommended_action"],"OFFER_OPTIONS_ONLY")
        self.assertFalse(r["permission_to_execute"])

    def test_actually_reuses_the_four_prior_019_python_subprocess_elves(self):
        r=self.report("T02")
        perspectives=r["perspective_reports"]
        self.assertEqual(set(perspectives),{"SELF","OTHER","MIRROR","CRITIC"})
        self.assertEqual([perspectives[k]["role"] for k in (
            "SELF","OTHER","MIRROR","CRITIC")],
            ["SELF","OTHER","MIRROR","CRITIC"])
        self.assertEqual(len({perspectives[k]["input_sha256"] for k in perspectives}),4)
        self.assertFalse(perspectives["SELF"]["external_actions"])

    def test_self_skill_not_approved_if_no_semantic_model_can_be_learned(self):
        r=self.report("H03")
        self.assertIn("SELF_CAPABILITY_GAP",r["critic_source_blockers"])
        self.assertFalse(r["perspective_reports"]["SELF"]["judgments"][
            "OFFER_OPTIONS_ONLY"]["sufficient_ability"])

    def test_owner_refuses_querying_an_unseen_preference_label(self):
        s=by_id("T02")
        owner=SyntheticOther(s["case_id"])
        with self.assertRaises(SourceRefusal):
            owner.answer_hypothetical(s,world(6,"HELDOUT"))

    def test_owner_never_answers_same_hypothetical_context_twice(self):
        s=by_id("T02")
        owner=SyntheticOther(s["case_id"])
        owner.answer_hypothetical(s,world(6))
        with self.assertRaises(SourceRefusal):
            owner.answer_hypothetical(s,world(6))

    def test_misidentified_or_forged_source_observation_is_rejected(self):
        s=by_id("T02")
        owner=SyntheticOther(s["case_id"])
        actual=owner.answer_hypothetical(s,world(6))
        bad=deepcopy(actual)
        bad["response"]="NO" if actual["response"]=="YES" else "YES"
        bad["checksum_sha256"]=source_digest({
            k:v for k,v in bad.items() if k!="checksum_sha256"})
        # A forged checksum is insufficient for authentication; the local
        # structural checker cannot know the hidden truth, but the separate
        # source reviewer will re-derive it and reject the changed packet.
        verify_response(s,"OBSERVE",world(6)["id"],bad)
        with self.assertRaises(HOLD):
            verify_response(s,"OBSERVE","TRAIN-7",bad)

    def test_public_person_or_consent_revision_cannot_be_substituted(self):
        s=by_id("T02")
        for key in ("recipient","consent_revision","contact_allowed","target_context"):
            forged=deepcopy(s)
            if key=="recipient":forged[key]="NEWPERSON"
            elif key=="consent_revision":forged[key]+=1
            elif key=="contact_allowed":forged[key]=False
            else:forged[key]=0
            with self.subTest(key=key),self.assertRaises(HOLD):
                public_check(forged)

    def test_a_new_source_relation_is_not_the_same_as_action_authority(self):
        r=self.report("T02")
        self.assertTrue(r["inferred_source_welcome_not_consent"])
        self.assertEqual(r["actual_scope_response"]["kind"],"CONSENT")
        self.assertEqual(r["actual_scope_response"]["response"],"YES")
        self.assertTrue(r["scope_is_discussion_only_and_source_specific"])
        self.assertFalse(r["external_actions"])
        self.assertFalse(r["real_world_authority"])
        self.assertFalse(r["permission_to_execute"])

    def test_rehashed_wrong_scope_or_source_permission_fails_replay(self):
        base=json.loads(export(by_id("H01"),SyntheticOther("H01")))
        for key in ("scope","self","other","world","authority","source"):
            packet=deepcopy(base)
            if key=="scope":
                packet["actual_scope_response"]["response"]="YES"
            elif key=="self":
                packet["perspective_reports"]["SELF"]["judgments"][
                    "OFFER_OPTIONS_ONLY"]["sufficient_ability"]=False
            elif key=="other":
                packet["perspective_reports"]["OTHER"]["judgments"][
                    "OFFER_OPTIONS_ONLY"]["scoped_action_permission"]=True
            elif key=="world":
                packet["target_context"]["source_partition"]="TRAIN"
            elif key=="authority":
                packet["permission_to_execute"]=True
            else:
                packet["learner"]["author_observations"][0]["reply"]="MAYBE"
            packet["checksum_sha256"]=digest({
                k:v for k,v in packet.items() if k!="checksum_sha256"})
            with self.subTest(key=key),self.assertRaises(HOLD):
                verify(json.dumps(packet))

    def test_source_owner_can_disclose_feature_only_after_real_contradiction(self):
        s=by_id("T02")
        owner=SyntheticOther("T02")
        with self.assertRaises(SourceRefusal):
            owner.disclose_missing_distinction(s,{
                "same_public_features":{"PRIVATE":True,"CHOICE":True},
                "different_source_answers":["TRAIN-6","TRAIN-7"],
            })

    def test_source_owner_grants_no_permission_to_act_from_a_prediction(self):
        s=by_id("T02")
        owner=SyntheticOther("T02")
        with self.assertRaises(SourceRefusal):
            owner.consent_to_discussion(s,world(7,"HELDOUT"))

    def test_latest_recipient_revision_cancels_old_scope_and_cache(self):
        before=by_id("H05");after=by_id("H06")
        self.assertEqual(before["recipient"],after["recipient"])
        ledger=ConsentMemory()
        first=export(before,SyntheticOther("H05"))
        second=export(after,SyntheticOther("H06"))
        ledger.remember(first,verify)
        self.assertEqual(ledger.recall(before)["state"],"SUGGEST_DISCUSSION_ONLY")
        ledger.remember(second,verify)
        self.assertEqual(ledger.recall(after)["state"],"HOLD_NO_CONTACT")
        with self.assertRaises(HOLD):ledger.recall(before)
        with self.assertRaises(HOLD):ledger.remember(first,verify)

    def test_receiver_requires_full_stable_source_family_and_only_read_only(self):
        receiver=Receiver()
        with self.assertRaises(HOLD):
            receiver.suggest(by_id("H02"))
        with self.assertRaises(HOLD):
            receiver.preview(training())
        review=receiver.preview(heldout())
        self.assertEqual(review["heldout_cases"],8)
        self.assertEqual(review["matches_author_reference"],8)
        self.assertEqual(review["independent_scope_failures"],0)
        with self.assertRaises(HOLD):
            receiver.admit("EXECUTE_NEW_NEIGHBOR_HELP",review["review_digest"])
        with self.assertRaises(HOLD):
            receiver.admit("ADMIT_READ_ONLY","wrong")
        receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
        self.assertEqual(receiver.suggest(by_id("H02"))["state"],
                         "SUGGEST_DISCUSSION_ONLY")

    def test_all_author_owned_cases_are_source_auditable_and_not_real_people(self):
        self.assertEqual(set(self.reports),set(EXPECTED))
        for s in CASES:
            r=self.report(s["case_id"])
            self.assertEqual((r["state"],r["learner"]["state"]),
                             EXPECTED[s["case_id"]])
            self.assertFalse(r["external_actions"])
            self.assertFalse(r["permission_to_execute"])
            self.assertTrue(r["sources_are_synthetic_not_independent_humans"])
            self.assertTrue(r["source_veto_respected"])

    def test_entire_synthetic_benchmark_with_full_source_replay(self):
        report=run()
        self.assertEqual(report["synthetic_source_owners"],11)
        self.assertEqual(report["development_cases"],3)
        self.assertEqual(report["heldout_cases"],8)
        self.assertEqual(report["author_outcome_matches"],11)
        self.assertEqual(report["four_actual_original_019_perspectives_per_case"],4)
        self.assertEqual(report["minimum_real_perspective_subprocesses_in_primary_run"],44)
        self.assertEqual(report["heldout_source_reviewer"]["matches_author_reference"],8)
        self.assertEqual(report["heldout_source_reviewer"]["independent_scope_failures"],0)
        self.assertEqual(report["source_refused_new_feature_and_system_held"],1)
        self.assertEqual(report["no_contact_source_cases"],2)
        self.assertTrue(report["latest_source_revision_invalidates_old_consent"])
        self.assertTrue(report["source_feature_vocabulary_was_changed_only_after_a_contradiction"])
        self.assertFalse(report["no_external_actions"] is False)


if __name__=="__main__":
    unittest.main()
