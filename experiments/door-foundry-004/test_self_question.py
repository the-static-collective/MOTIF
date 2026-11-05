"""MOTIF-004: first source-native, falsifiable self-posed question gate."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import question
import answer


class InquiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(os.environ["MOTIF_ORIGINAL"])
        cls.graft=Path(os.environ["GRAFT_SOURCE"])
        cls.packet=Path(os.environ["CANNON_GRAFT_RECEIPT"])
        cls.root=tempfile.TemporaryDirectory(prefix="motif-inquiry-")
        cls.work=Path(cls.root.name)
        cls.request=cls.work/"self-question.json"
        cls.generated=cls.work/"motif-born-answer"
        cls.report=cls.work/"self-answer.json"
        cls.query=question.inspect(cls.source)
        cls.request.write_text(json.dumps(cls.query))
        cls.answer=answer.evaluate(
            cls.request,cls.packet,cls.graft,cls.source,
            cls.generated,cls.report)

    @classmethod
    def tearDownClass(cls):
        cls.root.cleanup()

    def test_question_precedes_receiving_generated_operator(self):
        q=self.query
        self.assertEqual(q["schema"],"motif.self-inquiry.v0")
        self.assertEqual(q["status"],"QUESTION_PROPOSED_BEFORE_GRAFT_SELECTION")
        self.assertFalse(q["candidate_executable_examined"])
        self.assertIsNone(q["missing_capability_contract"]["target_path"])
        self.assertFalse(q["missing_capability_contract"]["target_path_known_to_questioner"])
        self.assertNotIn("observed.reachable_actions",json.dumps(q))

    def test_original_motif_003_really_detected_conflicting_moves(self):
        immediate=self.query["evidence"]["immediate_priority_first"]
        choices=self.query["evidence"]["new_choices_priority_first"]
        self.assertNotEqual((immediate["operator"],immediate["roles"]),
                            (choices["operator"],choices["roles"]))
        self.assertTrue(self.query["evidence"]["policy_disagreement"])
        self.assertGreaterEqual(self.query["evidence"]["candidate_first_moves"],2)

    def test_missing_synthetic_permission_does_not_generate_question(self):
        with self.assertRaises(question.HOLD):
            question.inspect(self.source,world_mode="no-permissions")

    def test_unknown_world_variant_cannot_request_authority(self):
        with self.assertRaises(question.HOLD):
            question.inspect(self.source,world_mode="secret-world")

    def test_question_is_derived_from_exact_original_motif_source(self):
        self.assertEqual(question.verify_question(self.query,self.source),
                         self.query["content_sha256"])
        self.assertEqual(self.query["original_source_pins"],question.PINS)
        self.assertEqual(self.query["original_source_commit"],question.SOURCE_SHA)

    def test_self_rehashed_forged_target_path_is_rejected(self):
        q=json.loads(json.dumps(self.query))
        q["missing_capability_contract"]["target_path"]="observed.reachable_actions"
        base=dict(q);base.pop("content_sha256")
        q["content_sha256"]=question.digest(base)
        with self.assertRaises(question.HOLD):
            question.verify_question(q,self.source)

    def test_hacked_policy_threshold_is_refused_even_after_rehash(self):
        q=json.loads(json.dumps(self.query))
        q["missing_capability_contract"]["decision_rule"]["threshold"]=100
        base=dict(q);base.pop("content_sha256")
        q["content_sha256"]=question.digest(base)
        with self.assertRaises(question.HOLD):
            question.verify_question(q,self.source)

    def test_fake_evidence_to_force_question_is_refused(self):
        q=json.loads(json.dumps(self.query))
        q["evidence"]["policy_disagreement"]=False
        base=dict(q);base.pop("content_sha256")
        q["content_sha256"]=question.digest(base)
        with self.assertRaises(question.HOLD):
            question.verify_question(q,self.source)

    def test_unpinned_original_operator_fails_before_inquiry(self):
        with patch.object(question,"git_blob",return_value="0"*40):
            with self.assertRaises(question.HOLD):
                question.inspect(self.source)

    def test_actual_graft_and_cannon_receipt_selected_through_question(self):
        r=self.answer
        self.assertEqual(r["schema"],"motif.self-question-answer.v0")
        self.assertEqual(r["original_question_sha256"],self.query["content_sha256"])
        self.assertEqual(r["status"],"SYNTHETIC_GAP_ADDRESSED_IN_HELD_BUILD")
        self.assertEqual(r["source_owner"],"the-static-collective/GRAFT")
        self.assertEqual(r["review_owner"],"the-static-collective/CANNON")
        self.assertTrue(r["question_asked_before_candidate"])

    def test_question_answer_contains_real_new_generated_js(self):
        raw=(self.generated/"generated_sensor.mjs").read_text()
        self.assertIn("const FIELD_PATH=",raw)
        self.assertIn("observed",raw)
        self.assertIn("reachable_actions",raw)
        self.assertEqual(self.answer["new_generated_operator_sha256"],
                         answer.graft.sha256(raw.encode()).hexdigest())

    def test_information_benefit_is_bounded_but_real_within_fixture(self):
        self.assertEqual(self.answer["case_count"],4)
        self.assertEqual(self.answer["fixed_immediate_no_sensor_matches"],2)
        self.assertEqual(self.answer["new_sensor_matches"],4)
        self.assertEqual(self.answer["recommendations_changed"],2)

    def test_fair_classical_selector_ties_the_new_sensor(self):
        self.assertEqual(self.answer["fair_classical_same_evidence_matches"],4)
        self.assertFalse(self.answer["claimed_classical_superiority"])

    def test_no_authority_or_external_actions_from_new_questions(self):
        q=self.query
        self.assertFalse(q["next_steps_authorized"]["connect_apis"])
        self.assertFalse(q["next_steps_authorized"]["contact_people"])
        self.assertFalse(q["next_steps_authorized"]["deploy"])
        self.assertEqual(self.answer["real_world_actions"],0)
        self.assertEqual(self.answer["automatic_source_changes"],0)
        self.assertFalse(self.answer["admitted"])

    def test_next_question_is_an_unsent_research_proposal(self):
        r=self.answer
        self.assertIn("unknown",r["next_question"])
        self.assertFalse(r["next_question_submitted"])
        self.assertFalse(r["real_human_outcomes"])

    def test_answer_checksum_recomputes(self):
        d=answer.document(self.report)
        raw=dict(d);claimed=raw.pop("content_sha256")
        self.assertEqual(question.digest(raw),claimed)

    def test_questioner_refuses_second_build_overwrite(self):
        with self.assertRaises(answer.graft.HOLD):
            answer.evaluate(self.request,self.packet,self.graft,self.source,
                            self.generated,self.work/"new.json")

    def test_cannon_receipt_with_fake_field_outcome_is_refused(self):
        original=answer.document(self.packet)
        original["observed_real_world_outcome"]=True
        raw=dict(original);raw.pop("content_sha256")
        original["content_sha256"]=answer.graft.jsdigest(raw)
        fake=self.work/"forged-cannon.json"
        fake.write_text(json.dumps(original))
        with self.assertRaises(answer.graft.HOLD):
            answer.evaluate(self.request,fake,self.graft,self.source,
                            self.work/"bad-build",self.work/"bad-report")

    def test_source_field_candidate_cannot_be_selected_without_question(self):
        fake=self.work/"fake-question.json"
        q=json.loads(json.dumps(self.query))
        q["current_world"]="no-permissions"
        raw=dict(q);raw.pop("content_sha256")
        q["content_sha256"]=question.digest(raw)
        fake.write_text(json.dumps(q))
        with self.assertRaises(question.HOLD):
            answer.evaluate(fake,self.packet,self.graft,self.source,
                            self.work/"forbidden-build",self.work/"forbidden-report")


if __name__=="__main__":unittest.main()
