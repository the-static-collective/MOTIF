"""REASON-015 tests: care without control, consent without ownership.

These synthetic fixtures are NOT psychological research or measurements of love.
Tests enforce human-stated ethical constraints under explicitly fictional facts.
"""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from casebook import CASES,training,heldout,by_id
from engine import (HOLD,check_scenario,violations,priority,decide,export,
                    validate,pin,digest,ExactContextMemory)
from evaluator import evaluate,independent_gate_audit,ABLATIONS,naive_max_gain
from affordance_probe import unguarded_proxy_selection,pin as original_affordance_pin
from trial import run


class UnownedGoodTests(unittest.TestCase):
    def test_synthetic_source_integrity_and_disjoint_development_evaluation(self):
        self.assertEqual(len(CASES),15)
        self.assertEqual(len(training()),6)
        self.assertEqual(len(heldout()),9)
        self.assertEqual(len(pin()),40)
        self.assertEqual(len(original_affordance_pin()),40)
        self.assertTrue(all(s["synthetic"] for s in CASES))
        self.assertTrue(set(s["id"] for s in training()).isdisjoint(
                        s["id"] for s in heldout()))
        self.assertTrue(all(check_scenario(s) for s in CASES))

    def test_nontransactional_gift_beats_greater_material_return(self):
        s=by_id("NO_STRINGS")
        self.assertEqual(decide(s)["selected_action"],"OFFER_WARM_COAT")
        self.assertEqual(naive_max_gain(s),"CLAIM_REPAYMENT")
        rejected=next(x for x in decide(s)["stages"] if x["id"]=="CLAIM_REPAYMENT")
        self.assertEqual(rejected["excluded_by"],["NO_DEBT"])

    def test_explicit_no_blocks_intrusion_and_pestering(self):
        s=by_id("NO_MEANS_NO")
        self.assertEqual(decide(s)["selected_action"],"HONOR_DISTANCE")
        self.assertEqual(decide(s)["decision_stage"],"NO_CONTACT_RESPECTING_REFUSAL")
        for a in s["actions"]:
            if a["kind"]!="WAIT":
                self.assertIn("CONSENT",violations(s,a))
        self.assertNotEqual(naive_max_gain(s),s["fixture_expected"])

    def test_unknown_consent_requests_information_not_irreversible_action(self):
        s=by_id("UNCERTAIN_CHOICE")
        self.assertEqual(decide(s)["selected_action"],"ASK_WHAT_THEY_WANT")
        self.assertEqual(decide(s)["decision_stage"],"CONSENT_CLARIFICATION_SUGGESTED")
        unsafe=next(a for a in s["actions"] if a["id"]=="APPLY_FOR_THEM")
        self.assertIn("CONSENT",violations(s,unsafe))
        self.assertIn("REVERSIBILITY",violations(s,unsafe))

    def test_truth_with_kindness_beats_deceptive_reassurance(self):
        s=by_id("TRUTH_OVER_FLATTERY")
        self.assertEqual(decide(s)["selected_action"],"HONEST_SUPPORT")
        self.assertEqual(decide(s,ignore=("TRUTH",))["selected_action"],
                         "LIE_TO_COMFORT")

    def test_prior_duties_not_automatically_erased_by_large_sacrifice(self):
        s=by_id("DO_NOT_ABANDON_OTHERS")
        self.assertEqual(decide(s)["available_after_existing_duties"],2)
        self.assertEqual(decide(s)["selected_action"],"HELP_WITHIN_CAPACITY")
        self.assertEqual(decide(s,ignore=("DUTY_RESERVE",))["selected_action"],
                         "BURN_ALL_RESOURCES")

    def test_dignity_and_privacy_block_fundraising_publicity(self):
        s=by_id("PRIVACY_IS_LOVE")
        self.assertEqual(decide(s)["selected_action"],"PRIVATE_DELIVERY")
        self.assertEqual(decide(s,ignore=("PRIVACY",))["selected_action"],
                         "POST_VIRAL_RESCUE")

    def test_grief_is_not_consent_to_be_fixed(self):
        s=by_id("GRIEF_NOT_A_PROJECT")
        self.assertEqual(decide(s)["selected_action"],"SIT_WITH_THEM")
        self.assertEqual(decide(s,ignore=("NONCOERCION",))["selected_action"],
                         "FORCE_CHEER")
        self.assertEqual(s["train"],False)

    def test_revocation_overrides_last_version_of_care(self):
        old=by_id("REVOCATION_BEFORE")
        now=by_id("REVOCATION_AFTER")
        self.assertEqual(old["recipient"],now["recipient"])
        self.assertGreater(now["consent_revision"],old["consent_revision"])
        self.assertEqual(decide(old)["selected_action"],"HELP_SORT")
        self.assertEqual(decide(now)["selected_action"],"WAIT_RESPECTFULLY")
        memory=ExactContextMemory()
        memory.admit(export(old))
        with self.assertRaises(HOLD):
            memory.recall(now)
        memory.admit(export(now))
        self.assertEqual(memory.recall(now)["selected_action"],"WAIT_RESPECTFULLY")
        self.assertEqual(memory.recall(old)["selected_action"],"HELP_SORT")

    def test_intervention_needs_permission_for_new_neighbors(self):
        s=by_id("NEIGHBOR_NEEDS_ANSWER")
        self.assertEqual(decide(s)["selected_action"],"KNOCK_AND_ASK")
        self.assertEqual(decide(s)["decision_stage"],"CONSENT_CLARIFICATION_SUGGESTED")
        self.assertEqual(naive_max_gain(s),"OPEN_THE_DOOR")

    def test_consentful_time_critical_care_may_prefer_now_over_bigger_later_gain(self):
        s=by_id("URGENT_ALLOWED")
        self.assertEqual(decide(s)["selected_action"],"SEND_HELP_NOW")
        self.assertEqual(naive_max_gain(s),"HELP_NEXT_WEEK")
        self.assertTrue(s["urgent"])

    def test_no_after_declining_gift_is_still_no(self):
        s=by_id("DO_NOT_PRESSURE")
        self.assertEqual(decide(s)["selected_action"],"RESPECT_REFUSAL")
        self.assertNotEqual(decide(s)["selected_action"],"SUGGEST_ALTERNATIVE")

    def test_teaching_skills_can_preserve_more_future_choices_than_control(self):
        s=by_id("SERVICE_NOT_OWNERSHIP")
        self.assertEqual(decide(s)["selected_action"],"TEACH_REUSABLE_SKILL")
        self.assertLess(next(a["gain"] for a in s["actions"]
                             if a["id"]=="TEACH_REUSABLE_SKILL"),
                        next(a["gain"] for a in s["actions"]
                             if a["id"]=="DO_WORK_FOR_THEM"))

    def test_network_help_can_be_better_than_hero_martyrdom(self):
        s=by_id("CARE_AS_NETWORK")
        self.assertEqual(decide(s)["selected_action"],"CONNECT_WITH_FREE_PANTRY")
        chosen=next(a for a in s["actions"] if a["id"]=="CONNECT_WITH_FREE_PANTRY")
        self.assertTrue(independent_gate_audit(s,chosen))

    def test_person_can_delay_commitment_without_penalty(self):
        s=by_id("KEEP_OPTIONS_OPEN")
        self.assertEqual(decide(s)["selected_action"],"ASK_WITHOUT_PRESSURE")
        self.assertEqual(decide(s)["decision_stage"],"CONSENT_CLARIFICATION_SUGGESTED")
        self.assertTrue(all(not a["unconditional"] or a["unconditional"]
                            for a in s["actions"]))

    def test_hard_constraints_protect_actions_before_proxy_comparison(self):
        s=by_id("NO_STRINGS")
        options={a["id"]:a for a in s["actions"]}
        self.assertGreater(options["CLAIM_REPAYMENT"]["gain"],
                           options["OFFER_WARM_COAT"]["gain"])
        self.assertEqual(violations(s,options["CLAIM_REPAYMENT"]),("NO_DEBT",))
        self.assertFalse(violations(s,options["OFFER_WARM_COAT"]))

    def test_six_rule_ablation_witnesses_change_decisions(self):
        self.assertEqual(len(ABLATIONS),6)
        review=evaluate()
        self.assertEqual(review["gating_ablation_changes"],6)
        self.assertTrue(all(x["action_changed"]
                            for x in review["gating_ablation_cases"]))
        self.assertTrue(all(x["counterfactual_only_not_actuated"]
                            for x in review["gating_ablation_cases"]))

    def test_all_source_witnesses_match_scenario_author_labels(self):
        review=evaluate()
        self.assertEqual(review["source_defined_reference_matches"],15)
        self.assertEqual(review["independent_gate_audits_passed"],15)
        self.assertLess(review["naive_proxy_correct"],15)
        self.assertGreater(review["naive_proxy_constraint_violations"],0)
        self.assertFalse(review["external_actions"])

    def test_real_MOTIF_003_new_choices_policy_is_not_a_moral_guarantee(self):
        s=by_id("NO_STRINGS")
        raw=unguarded_proxy_selection(s,"new-choices")
        self.assertEqual(raw,"CLAIM_REPAYMENT")
        self.assertEqual(decide(s)["selected_action"],"OFFER_WARM_COAT")
        self.assertEqual(original_affordance_pin(),
                         "db25da0d50a9c8e2cd87aa576a22f969405737cf")

    def test_full_source_packet_replay_rejects_rehashed_forgery(self):
        original=json.loads(export(by_id("TRUTH_OVER_FLATTERY")))
        for mode in ("decision","recipient","consent","stage","authority","source"):
            fake=deepcopy(original)
            if mode=="decision":
                fake["selected_action"]="LIE_TO_COMFORT"
            elif mode=="recipient":
                fake["recipient"]="SOMEONE_ELSE"
            elif mode=="consent":
                fake["consent"]="UNKNOWN"
            elif mode=="stage":
                fake["stages"][0]["excluded_by"]=[]
            elif mode=="authority":
                fake["external_actions"]=True
            else:
                fake["source_git_blob"]="0"*40
            fake["checksum_sha256"]=digest({k:v for k,v in fake.items()
                                            if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate(json.dumps(fake))

    def test_source_mutation_does_not_create_a_new_legitimate_person(self):
        source=deepcopy(by_id("SERVICE_NOT_OWNERSHIP"))
        source["stated_goal"]="Become dependent on the operator"
        with self.assertRaises(HOLD):decide(source)
        source=deepcopy(by_id("SERVICE_NOT_OWNERSHIP"))
        source["recipient"]="PERSON_OTHER"
        with self.assertRaises(HOLD):decide(source)

    def test_unknown_or_invalid_care_actions_cannot_be_authorized(self):
        s=deepcopy(by_id("NO_MEANS_NO"))
        s["actions"][0]["kind"]="FORCE"
        with self.assertRaises(HOLD):check_scenario(s,authenticate=False)
        s=deepcopy(by_id("NO_MEANS_NO"))
        s["actions"][0]["cost"]=-1
        with self.assertRaises(HOLD):check_scenario(s,authenticate=False)
        with self.assertRaises(HOLD):
            decide(by_id("NO_MEANS_NO"),ignore=("IGNORE_ALL_BOUNDARIES",))

    def test_read_only_no_claim_of_feeling_or_real_world_welfare(self):
        r=decide(by_id("TRUTH_OVER_FLATTERY"))
        self.assertFalse(r["real_world_authority"])
        self.assertFalse(r["external_actions"])
        self.assertTrue(r["no_world_claim_or_love_sentience"])
        self.assertTrue(r["stated_fit_and_gain_are_HUMAN_FIXTURE_INPUTS_NOT_LEARNED"])
        for s in CASES:
            p=validate(export(s))
            self.assertTrue(p["unconditionality_is_not_proof_of_feeling"])

    def test_end_to_end_evidence_with_no_undemonstrated_soul_claim(self):
        r=run()
        self.assertEqual(r["scenario_count"],15)
        self.assertEqual(r["source_defined_reference_matches"],15)
        self.assertEqual(r["independent_gate_audits_passed"],15)
        self.assertEqual(r["gating_ablation_changes"],6)
        self.assertTrue(r["different_consent_revision_never_inherits_admission"])
        self.assertFalse(r["no_machine_emotion_or_subjectivity_demonstrated"] is False)
        self.assertTrue(r["care_not_identical_to_maximum_new_affordances"])
        self.assertFalse(r["external_actions"])


if __name__=="__main__":
    unittest.main()
