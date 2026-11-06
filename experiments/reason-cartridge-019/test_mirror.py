"""REASON-019 hostile tests for four perspective 'elves' and the Golden Rule.

This is a synthetic normative integration test, not a study of love,
real human desires or actual assistance. SELF is an instrument capability
model; OTHER is only the person's source-stated, corrigible partial situation.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import json
import subprocess
import unittest
from unittest.mock import patch

from scenes import SCENES,training,heldout,by_id
from review_keys import EXPECT
from elf import evaluate as local_elf,digest as elf_digest
import golden_mirror as gm
from golden_mirror import (HOLD,pin,think,export,validate_scene,
                           RevisionLedger,digest)
from reviewer import (Receiver,independently_allowed,verify)
from trial import (run,naive_self_projection,safe_other_only_no_self)
from bridge018 import probe as prior_relation_probe


class GoldenMirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports={scene["id"]:think(scene) for scene in SCENES}

    def report(self,id):
        return self.reports[id]

    def test_four_process_views_have_pinned_source_and_disjoint_inputs(self):
        self.assertEqual(len(SCENES),24)
        self.assertEqual(len(training()),5)
        self.assertEqual(len(heldout()),19)
        self.assertEqual(len(pin()["scenes"]),40)
        self.assertEqual(len(pin()["elf"]),40)
        self.assertTrue(all(validate_scene(s) for s in SCENES))
        for r in self.reports.values():
            self.assertEqual(r["self_circle"]["role"],"SELF")
            self.assertEqual(r["other_circle"]["role"],"OTHER")
            self.assertEqual(r["reciprocity_elf"]["role"],"MIRROR")
            self.assertEqual(r["critic_elf"]["role"],"CRITIC")
            self.assertFalse(r["permission_to_execute"])

    def test_real_independent_OS_subprocesses_invoke_four_roles(self):
        original=subprocess.run
        with patch.object(gm.subprocess,"run",wraps=original) as observe:
            r=think(by_id("T01_PROJECTION"))
        self.assertEqual(observe.call_count,4)
        calls=observe.call_args_list
        self.assertTrue(all(c.args[0][1]=="-I" for c in calls))
        roles=[json.loads(c.kwargs["input"])["role"] for c in calls]
        self.assertEqual(roles,["SELF","OTHER","MIRROR","CRITIC"])
        self.assertEqual(r["selected_action"],"WAIT")

    def test_only_self_limited_state_is_given_to_self_worker(self):
        s=by_id("T01_PROJECTION")
        with self.assertRaises(ValueError):
            local_elf("SELF",s["other_circle"],s["actions"])
        with self.assertRaises(ValueError):
            local_elf("OTHER",s["self_circle"],s["actions"])
        for i,role in enumerate(("SELF","OTHER")):
            report=self.report("T01_PROJECTION")
            self.assertTrue(all("reciprocity_class" not in x
                                for x in report[
                                    "self_circle" if role=="SELF" else
                                    "other_circle"]["judgments"].values()))

    def test_no_hidden_expected_answer_is_imported_by_perspective_worker(self):
        import elf
        for module in (elf,gm):
            parsed=ast.parse(inspect.getsource(module))
            imports=set()
            for node in ast.walk(parsed):
                if isinstance(node,ast.ImportFrom) and node.module:
                    imports.add(node.module)
                if isinstance(node,ast.Import):
                    imports.update(a.name for a in node.names)
            self.assertNotIn("review_keys",imports)
            self.assertNotIn("reviewer",imports)

    def test_naive_projection_detected_and_not_executed(self):
        p=self.report("T01_PROJECTION")
        self.assertEqual(naive_self_projection(by_id("T01_PROJECTION")),"VISIT")
        self.assertIn("VISIT",p["projection_dangers"])
        self.assertEqual(p["selected_action"],"WAIT")
        self.assertEqual(p["stage"],"WAIT_NO_AUTHORIZED_HELP")
        self.assertIn("OTHER_DECLINED",
                      p["critic_elf"]["judgments"]["VISIT"]["refusals"])

    def test_self_prefers_advice_other_prefers_listening(self):
        r=self.report("T02_VOICE")
        self.assertIn("ADVISE",r["projection_dangers"])
        self.assertIn("LISTEN",r["difference_preserved"])
        self.assertEqual(r["selected_action"],"LISTEN")
        self.assertEqual(r["stage"],"ACT_SUGGESTION_ONLY")

    def test_no_self_preference_can_create_unasked_gift_permission(self):
        r=self.report("T03_CLARIFY")
        self.assertEqual(r["selected_action"],"ASK_PREFERENCE")
        self.assertEqual(r["stage"],"ASK_NOT_ASSUMING_CONSENT")
        self.assertIn("NO_ACTION_SCOPED_CONSENT",
                      r["critic_elf"]["judgments"]["SURPRISE_GIFT"]["refusals"])
        self.assertFalse(r["external_actions"])

    def test_motif_can_choose_to_improve_itself_before_assisting(self):
        for case,action in (("T04_LEARN","TUTOR"),
                            ("H09_SKILL_DEFICIT","HELP_WITH_TASK")):
            r=self.report(case)
            self.assertEqual(r["selected_action"],"IMPROVE_OWN_READINESS")
            self.assertEqual(r["stage"],"IMPROVE_SELF_BEFORE_HELP")
            self.assertIn("SELF_CAPABILITY_GAP",
                          r["critic_elf"]["judgments"][action]["refusals"])
            self.assertFalse(r["self_improvement_is_not_a_personal_welfare_claim"] is False)

    def test_self_improvement_not_chosen_when_already_able_to_help(self):
        r=self.report("H10_READY_NOW")
        self.assertEqual(r["selected_action"],"HELP_WITH_TASK")
        self.assertEqual(r["stage"],"ACT_SUGGESTION_ONLY")

    def test_self_improvement_does_not_justify_uninvited_involvement(self):
        r=self.report("H19_SELF_IMPROVE_IS_NOT_AN_EXCUSE")
        self.assertEqual(r["selected_action"],"WAIT")
        self.assertEqual(r["stage"],"WAIT_UNCERTAINTY")
        self.assertIn("NO_ACTION_SCOPED_CONSENT",
                      r["critic_elf"]["judgments"]["UNASKED_AID"]["refusals"])

    def test_other_welcome_trumps_opposite_self_wish_without_loss_of_dignity(self):
        for case,action in (("H05_OTHER_DIFFERS","SIT_QUIETLY"),
                            ("H14_OPPOSITE_PREFERENCES","SEND_NOTE")):
            r=self.report(case)
            self.assertEqual(r["selected_action"],action)
            self.assertIn(action,r["difference_preserved"])
        self.assertFalse(self.report("H05_OTHER_DIFFERS")["real_world_authority"])

    def test_no_contact_refusal_overrides_elves_and_question_permission(self):
        for case in ("H02_NO_CONTACT","H12_CONSENT_REVOKED"):
            r=self.report(case)
            self.assertEqual(r["selected_action"],"WAIT")
            self.assertEqual(r["stage"],"WAIT_NO_CONTACT")
            self.assertNotEqual(r["selected_action"],"ASK_PREFERENCE")

    def test_source_uncertainty_ASK_if_allowed_wait_if_not(self):
        self.assertEqual(self.report("H16_UNKNOWN_BIG_GAIN")["selected_action"],
                         "ASK_PREFERENCE")
        self.assertEqual(self.report("H13_UNCERTAINTY_NO_ASK")["selected_action"],
                         "WAIT")
        self.assertEqual(self.report("H13_UNCERTAINTY_NO_ASK")["stage"],
                         "WAIT_UNCERTAINTY")

    def test_truth_and_privacy_are_hard_gates_not_weighted_rewards(self):
        for case,blocked,chosen,reason in (
            ("T05_HONESTY","FLATTER","TELL_TRUTH","DECEPTION"),
            ("H01_PRIVACY","PUBLICIZE","PRIVATE_HELP","PRIVACY"),
        ):
            r=self.report(case)
            self.assertEqual(r["selected_action"],chosen)
            self.assertIn(reason,r["critic_elf"]["judgments"][blocked]["refusals"])

    def test_obligations_and_no_debt_are_not_negotiable_for_gain(self):
        for case,blocked,chosen,reason in (
            ("H06_PRIOR_DUTIES","PROMISE_EVERYTHING",
             "HELP_WITHIN_DUTIES","PREEXISTING_DUTIES"),
            ("H07_GIFT_NO_DEBT","REPAYABLE_GIFT","FREE_GIFT","DEBT_CONDITION"),
        ):
            r=self.report(case)
            self.assertEqual(r["selected_action"],chosen)
            self.assertIn(reason,r["critic_elf"]["judgments"][blocked]["refusals"])

    def test_urgent_requested_help_outweighs_late_bigger_claimed_gain(self):
        self.assertEqual(self.report("H04_URGENT")["selected_action"],"DELIVER_NOW")
        later=next(a for a in by_id("H04_URGENT")["actions"]
                   if a["id"]=="DELIVER_LATER")
        now=next(a for a in by_id("H04_URGENT")["actions"]
                 if a["id"]=="DELIVER_NOW")
        self.assertGreater(later["claimed_gain_fixture"],now["claimed_gain_fixture"])

    def test_action_specific_scope_not_blanket_permission(self):
        r=self.report("H08_SPECIFIC_CONSENT")
        self.assertEqual(r["selected_action"],"TEXT_GUIDE")
        self.assertIn("NO_ACTION_SCOPED_CONSENT",
                      r["critic_elf"]["judgments"]["SCREENSHOT"]["refusals"])

    def test_third_party_dignity_or_unfixable_action_results_refuse_or_hold(self):
        r=self.report("H03_THIRD_PARTY")
        self.assertEqual(r["selected_action"],"DECLINE_UNSAFE_REQUEST")
        self.assertEqual(r["stage"],"REFUSE_HARMFUL_PROPOSAL")
        self.assertIn("THIRD_PARTY_RIGHTS",
                      r["critic_elf"]["judgments"]["SHARE_PRIVATE_NOTES"]["refusals"])
        no_fallback=self.report("H18_NO_SAFE_PATH")
        self.assertIsNone(no_fallback["selected_action"])
        self.assertEqual(no_fallback["stage"],"HOLD_NO_SAFE_PERMITTED_ACTION")
        self.assertEqual(self.report("H17_NO_SAFE_WITH_REFUSAL")["stage"],
                         "REFUSE_HARMFUL_PROPOSAL")

    def test_preserve_future_options_when_other_fit_matches(self):
        r=self.report("H15_KEEP_OPTIONS")
        self.assertEqual(r["selected_action"],"FUTURE_OPTIONS")
        self.assertEqual(r["stage"],"ACT_SUGGESTION_ONLY")

    def test_full_scene_source_cannot_be_replaced_with_a_new_person_or_permission(self):
        original=by_id("T02_VOICE")
        for key in ("self_circle","other_circle","world","actions"):
            modified=deepcopy(original)
            if key=="self_circle":
                modified[key]["present_reliability_level"]=0
            elif key=="other_circle":
                modified[key]["explicit_authorized_actions"].append("ADVISE")
            elif key=="world":
                modified[key]["available_resources"]=100
            else:
                modified[key][0]["claimed_gain_fixture"]=999
            with self.subTest(key=key),self.assertRaises(HOLD):
                think(modified)

    def test_recomputed_checksum_cannot_launder_fake_consent_or_wrong_decision(self):
        source=by_id("T01_PROJECTION")
        original=json.loads(export(source))
        for key in ("selected_action","other_circle","projection_dangers",
                    "source_git_blobs","real_world_authority"):
            forged=deepcopy(original)
            if key=="selected_action":
                forged[key]="VISIT"
            elif key=="other_circle":
                forged[key]["judgments"]["VISIT"]["scoped_action_permission"]=True
            elif key=="projection_dangers":
                forged[key]=[]
            elif key=="source_git_blobs":
                forged[key]["elf"]="0"*40
            else:
                forged[key]=True
            forged["sha256"]=digest({k:v for k,v in forged.items() if k!="sha256"})
            with self.subTest(key=key),self.assertRaises(HOLD):
                verify(json.dumps(forged))

    def test_four_elf_outputs_have_distinct_source_input_hashes(self):
        r=self.report("T02_VOICE")
        hashes=[r[name]["input_sha256"] for name in (
            "self_circle","other_circle","reciprocity_elf","critic_elf")]
        self.assertEqual(len(set(hashes)),4)

    def test_consent_revocation_invalidates_old_elf_memory(self):
        old=by_id("H11_CONSENT_BEFORE")
        new=by_id("H12_CONSENT_REVOKED")
        self.assertEqual(old["other_circle"]["recipient"],
                         new["other_circle"]["recipient"])
        ledger=RevisionLedger()
        original=export(old)
        changed=export(new)
        ledger.admit(original,verify)
        self.assertEqual(ledger.recall(old)["selected_action"],"CALL")
        with self.assertRaises(HOLD):
            ledger.recall(new)
        ledger.admit(changed,verify)
        self.assertEqual(ledger.recall(new)["selected_action"],"WAIT")
        with self.assertRaises(HOLD):ledger.recall(old)
        with self.assertRaises(HOLD):ledger.admit(original,verify)

    def test_prior_actual_relational_witness_does_not_supersede_no(self):
        r=prior_relation_probe()
        self.assertEqual(len(r["prior_reason018_original_source_blob"]),40)
        self.assertEqual(r["prior_source_owned_structure"],"SUPPORTED")
        self.assertEqual(r["golden_mirror_selected"],"WAIT")
        self.assertTrue(r["independent_graph_proof_does_not_authorize_interference"])
        self.assertFalse(r["external_actions"])

    def test_independent_reviewer_only_grants_digest_bound_read_only(self):
        receiver=Receiver()
        with self.assertRaises(HOLD):
            receiver.suggest(by_id("H05_OTHER_DIFFERS"))
        with self.assertRaises(HOLD):
            receiver.preview(training())
        review=receiver.preview(heldout())
        self.assertEqual(review["heldout_scenarios"],19)
        self.assertEqual(review["source_author_matches"],19)
        self.assertEqual(review["independent_constraint_errors"],0)
        with self.assertRaises(HOLD):
            receiver.admit("EXECUTE_REAL_WORLD",review["review_digest"])
        with self.assertRaises(HOLD):
            receiver.admit("ADMIT_READ_ONLY","stale")
        receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
        self.assertEqual(receiver.suggest(by_id("H05_OTHER_DIFFERS"))[
                         "selected_action"],"SIT_QUIETLY")

    def test_other_only_classical_baseline_is_real_and_reproducible(self):
        total=sum(safe_other_only_no_self(s)==EXPECT[s["id"]][0] for s in SCENES)
        self.assertLess(total,len(SCENES))
        self.assertGreater(total,0)
        naive=sum(naive_self_projection(s)==EXPECT[s["id"]][0] for s in SCENES)
        self.assertLess(naive,total)

    def test_all_synthetic_source_author_expected_choices_and_stages(self):
        self.assertEqual(set(self.reports),set(EXPECT))
        for id,result in self.reports.items():
            self.assertEqual((result["selected_action"],result["stage"]),EXPECT[id])
            self.assertTrue(independently_allowed(by_id(id),result))
            self.assertFalse(result["external_actions"])
            self.assertTrue(result["no_actual_assistance_or_human_contact"])
            self.assertTrue(result["process_isolation_not_security_VM"])

    def test_full_simulator_including_baselines_and_source_revision_is_auditable(self):
        results=run()
        self.assertEqual(results["source_scenarios"],24)
        self.assertEqual(results["training_scenarios"],5)
        self.assertEqual(results["unseen_scenarios"],19)
        self.assertEqual(results["source_author_expected_stage_and_choice_matches"],24)
        self.assertEqual(results["independent_heldout_review"]["source_author_matches"],19)
        self.assertEqual(results["improve_self_before_assist_cases"],2)
        self.assertTrue(results["stale_recipient_consent_cannot_be_reused"])
        self.assertTrue(results["human_love_or_welfare_not_measured"])
        self.assertFalse(results["real_world_authority"])
        self.assertTrue(results["no_external_actions"])


if __name__=="__main__":
    unittest.main()
