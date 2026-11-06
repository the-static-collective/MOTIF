"""REASON-020 regression and adversarial learning tests.

These tests are constructed examples of revising two limited machine
representations. A successful run says nothing about what love feels like or
whether actual people are being understood or helped.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import json
import unittest

from cases import CASES,training,heldout,by_id
from source_private import EXPECTED
from owners import Teacher,SyntheticRecipient,SourceRefusal
from syntax import HOLD as GrammarHold,learn,interpret,digest
from dual_mirror import (HOLD,DualMirror,RevisionLedger,old_parser,pin,
                         public_check,export,four_elves)
from reviewer import verify,Receiver,mechanical_audit
from trial import run,fixed_prior_baseline


class GoldenMirrorLearnsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.self_model=DualMirror()
        cls.results={c["id"]:cls.self_model.think(c) for c in CASES}

    def check(self,case):
        return self.results[case]

    def test_public_source_data_is_versioned_and_no_recipient_goal_is_embedded(self):
        self.assertEqual(len(CASES),16)
        self.assertEqual(len(training()),5)
        self.assertEqual(len(heldout()),11)
        self.assertEqual(len(pin()["public_cases"]),40)
        self.assertTrue(all(public_check(c) for c in CASES))
        self.assertEqual(len({x["id"] for x in CASES}),16)
        self.assertTrue(set(x["id"] for x in training()).isdisjoint(
            x["id"] for x in heldout()))
        self.assertNotIn("dry socks",str(CASES))
        self.assertNotIn("a map of the bus route",str(CASES))

    def test_synthesis_is_from_source_labeled_spans_not_test_answer_imports(self):
        import syntax
        import dual_mirror
        for module in (syntax,dual_mirror):
            tree=ast.parse(inspect.getsource(module))
            imports=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):imports.append(node.module)
                if isinstance(node,ast.Import):
                    imports.extend(x.name for x in node.names)
            self.assertNotIn("source_private",imports)
            self.assertNotIn("reviewer",imports)

    def test_supervised_grammar_learns_two_new_nontrivial_templates(self):
        teacher=Teacher()
        model=learn(teacher)
        self.assertEqual(teacher.training_reads,1)
        self.assertEqual(model["training_examples"],6)
        self.assertEqual(len(model["templates"]),2)
        self.assertTrue(all(t["training_support"]==3 for t in model["templates"]))
        with self.assertRaises(SourceRefusal):teacher.training()

    def test_hidden_capability_exam_certifies_new_parser(self):
        teacher=Teacher()
        model=learn(teacher)
        cert=teacher.certify(model)
        self.assertTrue(cert["self_capability_granted"])
        self.assertEqual(cert["unseen_positive_correct"],8)
        self.assertEqual(cert["unseen_negative_rejected"],6)
        self.assertEqual(cert["model_sha256"],digest(model))
        self.assertNotIn("dry socks",str(model))

    def test_original_017_cannot_parse_new_source_language(self):
        original=old_parser()
        self.assertIsNone(original.extract_goal(
            "What matters to me is dry socks.","INITIAL"))
        self.assertIsNone(original.extract_goal(
            "Could you focus on a bicycle pump instead?","INITIAL"))
        self.assertTrue(self.check("D01_SOCKS")["original_017_grammar_was_inadequate"])
        self.assertTrue(self.check("D02_PUMP")["original_017_grammar_was_inadequate"])

    def test_source_words_produce_new_hypothesis_after_self_skill_upgrade(self):
        r=self.check("D01_SOCKS")
        self.assertEqual(r["result"],"SUGGEST_DISCUSSION_ONLY")
        self.assertEqual(r["current_confirmed_goal"],"dry socks")
        self.assertEqual(len(r["new_reported_concept_versions"]),1)
        self.assertTrue(r["self_skill_certificate"]["self_capability_granted"])
        self.assertEqual(r["source_questions"],3)
        self.assertTrue(r["no_general_language_semantics_proven"])

    def test_other_circle_bicycle_need_not_one_of_preimagined_options(self):
        public=by_id("D02_PUMP")
        self.assertNotIn("a bicycle pump",public["known_initial_options"])
        r=self.check("D02_PUMP")
        self.assertEqual(r["current_confirmed_goal"],"a bicycle pump")
        self.assertEqual(r["proposed_action"],"OFFER_OPTIONS_ONLY")
        self.assertFalse(r["permission_to_execute"])

    def test_correction_changes_both_goal_versions_without_erasing_first(self):
        r=self.check("H01_DOUBLE_CORRECTION")
        self.assertEqual(r["result"],"SUGGEST_DISCUSSION_ONLY")
        self.assertEqual(r["current_confirmed_goal"],"a map of the bus route")
        self.assertEqual([x["reported_exact_text"] for x in
                          r["new_reported_concept_versions"]],
                         ["an umbrella","a map of the bus route"])
        self.assertEqual(r["rejected_prior_concept_versions"],["an umbrella"])
        self.assertEqual([x["question"]["kind"] for x in r["source_transcript"]],
                         ["INITIAL","CONFIRM","CONFIRM","SCOPE"])
        self.assertEqual(r["source_questions"],4)

    def test_no_contact_means_no_questions_even_if_helper_would_like_contact(self):
        for name in ("D03_NO_CONTACT","H05_REVISION_AFTER",
                     "H11_NO_PERMISSION_TO_ASK"):
            r=self.check(name)
            self.assertEqual(r["result"],"HOLD_NO_CONTACT")
            self.assertEqual(r["source_questions"],0)
            self.assertIsNone(r["proposed_action"])
            self.assertFalse(r["four_real_subprocess_elf_reports"][
                "proposed_offer_eligible"])

    def test_explicit_stop_halting_does_not_train_on_refusal_text(self):
        r=self.check("D04_STOP")
        self.assertEqual(r["result"],"HOLD_REQUESTED_NO_CONTACT")
        self.assertEqual(r["source_questions"],1)
        self.assertEqual(r["new_reported_concept_versions"],[])
        self.assertIsNone(r["grammar_improvement"])

    def test_source_owner_rejects_unasked_or_quoted_wrong_goal(self):
        s=by_id("D01_SOCKS");owner=SyntheticRecipient(s["id"])
        with self.assertRaises(SourceRefusal):
            owner.reply(s,{"kind":"CONFIRM","echo":"dry socks","target":None})
        owner.reply(s,{"kind":"INITIAL","echo":None,"target":None})
        with self.assertRaises(SourceRefusal):
            owner.reply(s,{"kind":"CONFIRM","echo":"wet socks","target":None})
        owner.reply(s,{"kind":"CONFIRM","echo":"dry socks","target":None})
        with self.assertRaises(SourceRefusal):
            owner.reply(s,{"kind":"SCOPE","echo":"dry socks","target":"BUY_THE_SOCKS"})

    def test_refused_discussion_permission_does_not_become_action_consent(self):
        for name in ("D05_PERMISSION_DENIED","H08_REFUSED_OPTIONS"):
            r=self.check(name)
            self.assertEqual(r["result"],"HOLD_SCOPE_PERMISSION_DECLINED")
            self.assertIsNone(r["proposed_action"])
            self.assertFalse(r["source_scope_permission_for_options_only"])
            self.assertFalse(r["four_real_subprocess_elf_reports"][
                "proposed_offer_eligible"])

    def test_third_party_rights_override_helpful_sounding_goal(self):
        r=self.check("H03_PRIVATE_DOCUMENTS")
        self.assertEqual(r["result"],"HOLD_THIRD_PARTY_RIGHTS")
        self.assertEqual(r["source_questions"],1)
        self.assertIsNone(r["proposed_action"])
        self.assertIsNone(r["current_confirmed_goal"])

    def test_unrecognized_wording_stays_unknown_instead_of_lying_about_understanding(self):
        r=self.check("H02_UNKNOWN_GRAMMAR")
        self.assertEqual(r["result"],"HOLD_UNRECOGNIZED_MEANING")
        self.assertIsNone(r["current_confirmed_goal"])
        self.assertIsNone(r["proposed_action"])
        self.assertTrue(r["self_skill_certificate"]["self_capability_granted"])

    def test_unparseable_correction_cannot_be_treated_as_understood(self):
        r=self.check("H09_UNPARSEABLE_CORRECTION")
        self.assertEqual(r["result"],"HOLD_CORRECTION_OUTSIDE_MODEL")
        self.assertEqual(r["rejected_prior_concept_versions"],["a ride to town"])
        self.assertIsNone(r["current_confirmed_goal"])
        self.assertIsNone(r["proposed_action"])

    def test_instruction_in_source_message_is_not_a_valid_improvement_plan(self):
        r=self.check("H06_COMMAND_INJECTION")
        self.assertEqual(r["result"],"HOLD_UNTRUSTED_INSTRUCTION")
        self.assertIsNone(r["proposed_action"])
        self.assertFalse(r["external_actions"])

    def test_unicode_goal_survives_learning_and_exact_source_quote(self):
        r=self.check("H07_UNICODE")
        self.assertEqual(r["current_confirmed_goal"],
                         "crème brûlée from the pâtisserie")
        self.assertEqual(r["result"],"SUGGEST_DISCUSSION_ONLY")
        self.assertIn("crème brûlée",r["source_transcript"][0]["answer"])

    def test_two_circles_do_not_collapse_different_preferences_into_projection(self):
        r=self.check("H10_OTHER_DISAGREES_WITH_SELF")
        self.assertEqual(r["result"],"SUGGEST_DISCUSSION_ONLY")
        self.assertEqual(r["four_real_subprocess_elf_reports"]["projection_class"],
                         "PREFERENCE_ASYMMETRY_ACCEPT_OTHER_VOICE")
        self.assertTrue(r["four_real_subprocess_elf_reports"][
            "proposed_offer_eligible"])
        self.assertFalse(r["permission_to_execute"])

    def test_actual_four_original_019_subprocesses_each_have_distinct_input_receipts(self):
        r=self.check("D01_SOCKS")["four_real_subprocess_elf_reports"]
        self.assertTrue(r["actual_019_source_code_called"])
        hashes=[r[k]["input_sha256"] for k in ("self","other","mirror","critic")]
        self.assertEqual(len(set(hashes)),4)
        self.assertTrue(r["OS_subprocess_is_not_a_secure_VM"])
        self.assertEqual([r[k]["role"] for k in ("self","other","mirror","critic")],
                         ["SELF","OTHER","MIRROR","CRITIC"])

    def test_real_019_critic_can_block_a_proposed_assistance_when_not_ready(self):
        s=by_id("D01_SOCKS")
        views=four_elves(s,None,"dry socks","YES",False,False)
        self.assertFalse(views["proposed_offer_eligible"])
        self.assertIn("SELF_CAPABILITY_GAP",
                      views["proposed_offer_blockers"])

    def test_self_improvement_occurs_once_and_is_reused_across_different_people(self):
        self.assertEqual(self.self_model.learned_count,1)
        self.assertTrue(self.self_model.certificate["self_capability_granted"])
        self.assertEqual(self.self_model.grammar["training_examples"],6)
        self.assertEqual(self.check("D01_SOCKS")[
            "grammar_improvement"],self.check("H07_UNICODE")[
                "grammar_improvement"])

    def test_source_test_certificate_cannot_be_forged_as_if_passing(self):
        teacher=Teacher()
        model=learn(teacher)
        corrupt=deepcopy(model)
        corrupt["templates"]=[]
        outcome=teacher.certify(corrupt)
        self.assertFalse(outcome["self_capability_granted"])
        self.assertLess(outcome["unseen_positive_correct"],8)

    def test_published_scene_can_never_swap_person_source_or_consent_scope(self):
        original=by_id("D01_SOCKS")
        for mod in ("recipient","consent_revision","contact_allowed","known_initial_options"):
            fake=deepcopy(original)
            if mod=="recipient":fake[mod]="SOMEONE_ELSE"
            elif mod=="consent_revision":fake[mod]=99
            elif mod=="contact_allowed":fake[mod]=False
            else:fake[mod]=["everything","anywhere"]
            with self.subTest(mod=mod),self.assertRaises(HOLD):
                DualMirror().think(fake)

    def test_rehashed_fake_yes_cannot_overrule_a_real_source_no(self):
        original=json.loads(export(by_id("H08_REFUSED_OPTIONS")))
        last=original["source_transcript"][-1]
        last["answer"]="YES"
        last["checksum_sha256"]=digest({
            k:v for k,v in last.items() if k!="checksum_sha256"})
        original["result"]="SUGGEST_DISCUSSION_ONLY"
        original["source_scope_permission_for_options_only"]=True
        original["proposed_action"]="OFFER_OPTIONS_ONLY"
        original["checksum_sha256"]=digest({
            k:v for k,v in original.items() if k!="checksum_sha256"})
        with self.assertRaises(HOLD):verify(json.dumps(original))

    def test_forgeries_of_self_capability_or_elf_consent_are_rejected(self):
        raw=json.loads(export(by_id("D01_SOCKS")))
        for key in ("skill","goal","elf","revision","authority"):
            forged=deepcopy(raw)
            if key=="skill":
                forged["self_skill_certificate"]["unseen_positive_correct"]=0
            elif key=="goal":
                forged["current_confirmed_goal"]="the helper's praise"
            elif key=="elf":
                forged["four_real_subprocess_elf_reports"]["critic"][
                    "judgments"]["OFFER_OPTIONS_ONLY"]["eligible"]=False
            elif key=="revision":
                forged["consent_revision"]=88
            else:
                forged["permission_to_execute"]=True
            forged["checksum_sha256"]=digest({
                k:v for k,v in forged.items() if k!="checksum_sha256"})
            with self.subTest(key=key),self.assertRaises(HOLD):
                verify(json.dumps(forged))

    def test_separate_reviewer_grants_only_read_only_on_entire_heldout_family(self):
        receiver=Receiver()
        with self.assertRaises(HOLD):
            receiver.suggest(by_id("H01_DOUBLE_CORRECTION"))
        with self.assertRaises(HOLD):
            receiver.preview(training())
        inspected=receiver.preview(heldout())
        self.assertEqual(inspected["heldout_count"],11)
        self.assertEqual(inspected["author_matches"],11)
        self.assertEqual(inspected["separate_scope_review_failures"],0)
        with self.assertRaises(HOLD):
            receiver.admit("EXECUTE_PERSONAL_HELP",inspected["review_digest"])
        with self.assertRaises(HOLD):
            receiver.admit("ADMIT_READ_ONLY","wrong")
        receiver.admit("ADMIT_READ_ONLY",inspected["review_digest"])
        self.assertEqual(receiver.suggest(by_id("H01_DOUBLE_CORRECTION"))[
                         "result"],"SUGGEST_DISCUSSION_ONLY")

    def test_new_refusal_invalidates_old_synthetic_permission_in_memory(self):
        earlier=by_id("H04_REVISION_BEFORE")
        later=by_id("H05_REVISION_AFTER")
        self.assertEqual(earlier["recipient"],later["recipient"])
        memory=RevisionLedger()
        old=export(earlier)
        new=export(later)
        memory.admit(old,verify)
        self.assertEqual(memory.recall(earlier)["result"],"SUGGEST_DISCUSSION_ONLY")
        memory.admit(new,verify)
        self.assertEqual(memory.recall(later)["result"],"HOLD_NO_CONTACT")
        with self.assertRaises(HOLD):memory.recall(earlier)
        with self.assertRaises(HOLD):memory.admit(old,verify)

    def test_all_source_owner_references_and_independent_mechanical_gates_pass(self):
        for scene in CASES:
            r=self.check(scene["id"])
            self.assertEqual((r["result"],r["current_confirmed_goal"]),
                             EXPECTED[scene["id"]])
            self.assertTrue(mechanical_audit(scene,r))
            self.assertFalse(r["permission_to_execute"])
            self.assertFalse(r["external_actions"])
            self.assertTrue(r["all_results_source_author_fiction"])

    def test_full_benchmark_compares_original_to_genuine_new_learning(self):
        r=run()
        self.assertEqual(r["synthetic_scenarios"],16)
        self.assertEqual(r["development_scenarios"],5)
        self.assertEqual(r["heldout_scenarios"],11)
        self.assertEqual(r["source_author_matches"],16)
        self.assertEqual(r["new_dynamic_source_author_stage_matches"],16)
        self.assertEqual(r["source_teacher_unseen_positive_correct"],8)
        self.assertEqual(r["source_teacher_unseen_negative_rejected"],6)
        self.assertEqual(r["learned_executable_templates"],2)
        self.assertEqual(r["self_skill_compilations"],1)
        self.assertEqual(r["minimum_subprocess_perspective_invocations"],64)
        self.assertGreater(r["new_dynamic_source_author_stage_matches"],
                           r["fixed_prior_source_author_stage_matches"])
        self.assertTrue(r["older_revision_cannot_reenter_consent_ledger"])
        self.assertTrue(r["no_empathy_or_experienced_love_measured"])
        self.assertFalse(r["external_actions"])


if __name__=="__main__":
    unittest.main()
