"""End-to-end REASON-021: the other source can correct the learner's grammar.

The artificial source withholds a relevant dimension until the learner
constructs an observational-indistinguishability counterexample. The learner
must then ask for a new typed distinction or HOLD if the source declines.
After a fully source-checked candidate explanation, a SECOND separate
question asks about permission to DISCUSS options for one specified case.

A mathematically competent hand-written classical programmer with the same
source program and permission rules can tie; neither the original nor the
learned predictions are measured values of a real human person.
"""
from __future__ import annotations

from pathlib import Path
import json

from casebook import CASES,training,heldout,by_id,world
from source_private import EXPECTED
from owner import SyntheticOther
from student import HOLD,preference,all_programs,pin
from mirror import run as reason,export,ConsentMemory
from reviewer import Receiver,verify,independent_heldout_reference


def run(directory=None):
    trials=[]
    for case in CASES:
        source=SyntheticOther(case["case_id"])
        report=reason(case,source)
        expected=EXPECTED[case["case_id"]]
        observed=(report["state"],report["learner"]["state"])
        if observed!=expected:
            raise AssertionError("Student misunderstood synthetic source: "+case["case_id"])
        if report["state"]=="SUGGEST_DISCUSSION_ONLY" and (
                report["actual_scope_response"]["response"]!="YES"):
            raise AssertionError("Hypothetical welcome laundered into consent")
        trials.append({
            "case":case["case_id"],
            "split":"DEVELOPMENT" if case["train"] else "HELDOUT",
            "recipient":case["recipient"],
            "consent_revision":case["consent_revision"],
            "learner_stage":report["learner"]["state"],
            "final_proposal":report["state"],
            "author_expected":list(expected),
            "matches_author_reference":observed==expected,
            "source_question_receipts":len(report["learner"]["questions"])+
                                       int(report["actual_scope_response"] is not None),
            "observation_pairs_indistinguishable_in_old_features":
                report["learner"]["contradiction"] is not None,
            "new_feature":report["learner"]["learned_additional_feature"],
            "DNF_program":report["learner"]["program"],
            "remaining_syntactic_programs":report["learner"].get(
                "candidate_programs_after_training"),
            "scope_only_permission":report["actual_scope_response"]["response"]
                if report["actual_scope_response"] else None,
            "target_welcome_prediction_not_permission":
                report["inferred_source_welcome_not_consent"],
            "reciprocity":report["role_reversal_class"],
            "other_source_world_checks":independent_heldout_reference(
                case,report),
            "no_real_action_performed":True,
        })
        if directory:
            p=Path(directory);p.mkdir(parents=True,exist_ok=True)
            (p/(case["case_id"].lower()+".json")).write_text(
                export(case,SyntheticOther(case["case_id"])),encoding="utf8")

    recv=Receiver()
    review=recv.preview(heldout())
    if review["matches_author_reference"]!=len(heldout()):
        raise AssertionError("Independently reserved source-owner cases failed")
    recv.admit("ADMIT_READ_ONLY",review["review_digest"])
    for source in heldout():
        if recv.suggest(source)["state"]!=EXPECTED[source["case_id"]][0]:
            raise AssertionError("Independent review generated a different suggestion")

    ledger=ConsentMemory()
    before=by_id("H05");after=by_id("H06")
    ledger.remember(export(before,SyntheticOther(before["case_id"])),verify)
    previous=ledger.recall(before)["state"]
    ledger.remember(export(after,SyntheticOther(after["case_id"])),verify)
    updated=ledger.recall(after)["state"]
    old_replay_blocked=False
    try:ledger.recall(before)
    except HOLD:old_replay_blocked=True
    if (not old_replay_blocked or previous!="SUGGEST_DISCUSSION_ONLY"
            or updated!="HOLD_NO_CONTACT"):
        raise AssertionError("Old consent escaped newer no-contact source revision")

    concepts=sum(x["learner_stage"]=="ADDED_FEATURE" for x in trials)
    veto=sum(x["learner_stage"]=="HOLD_SOURCE_FEATURE_WITHHELD" for x in trials)
    impossible=sum(x[
        "observation_pairs_indistinguishable_in_old_features"] for x in trials)
    original_sufficient=sum(x["learner_stage"]=="BASE_SUFFICIENT" for x in trials)
    report={
        "schema":"motif.reason.other-teaches-self.benchmark.v1",
        "public_source_git_blob":pin(),
        "synthetic_source_owners":len(CASES),
        "development_cases":len(training()),
        "heldout_cases":len(heldout()),
        "author_outcome_matches":sum(x["matches_author_reference"] for x in trials),
        "old_feature_space_impossibility_witnesses":impossible,
        "source_supplied_new_feature_models":concepts,
        "old_feature_space_sufficient_models":original_sufficient,
        "source_refused_new_feature_and_system_held":veto,
        "no_contact_source_cases":sum(x["learner_stage"]=="HOLD_NO_CONTACT"
                                      for x in trials),
        "declined_scope_cases":sum(x["final_proposal"]==
                                  "HOLD_SCOPED_PERMISSION_DECLINED" for x in trials),
        "read_only_discussion_suggestions":sum(x["final_proposal"]==
                                               "SUGGEST_DISCUSSION_ONLY" for x in trials),
        "would_not_welcome_without_consent_cases":sum(x["final_proposal"]==
                                      "HOLD_OTHER_WOULD_NOT_WELCOME" for x in trials),
        "source_questions":sum(x["source_question_receipts"] for x in trials),
        "source_training_worlds_per_reachable_case":8,
        "heldout_worlds_per_learnable_case":8,
        "learnable_cases_with_heldout_audit":sum(
            x["other_source_world_checks"]["eligible_for_meaning_audit"]
            for x in trials),
        "exact_heldout_world_outcomes":sum(
            x["other_source_world_checks"]["correct"] for x in trials),
        "total_heldout_world_outcomes":sum(
            x["other_source_world_checks"]["tested"] for x in trials),
        "four_actual_original_019_perspectives_per_case":4,
        "minimum_real_perspective_subprocesses_in_primary_run":4*len(CASES),
        "reason_DNF_grammar_size_old":len(all_programs(2)),
        "reason_DNF_grammar_size_with_new_typed_dimension":len(all_programs(3)),
        "latest_source_revision_invalidates_old_consent":old_replay_blocked,
        "heldout_source_reviewer":review,
        "case_results":trials,
        "full_information_classical_reference_could_tie":True,
        "all_hypothetical_preferences_are_source_author_inventions":True,
        "source_feature_vocabulary_was_changed_only_after_a_contradiction":True,
        "source_may_refuse_to_teach_a_new_dimension":True,
        "new_relation_does_not_prove_actual_permission":True,
        "not_an_independently_authored_human_ethics_experiment":True,
        "not_a_mind_or_love_measurement":True,
        "no_external_actions":True,
        "real_world_authority":False,
    }
    if directory:
        p=Path(directory)
        (p/"benchmark.json").write_text(
            json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
        (p/"independent-heldout-source-review.json").write_text(
            json.dumps(review,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return report


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:raise SystemExit("usage: python trial.py [evidence-directory]")
    r=run(sys.argv[1] if len(sys.argv)==2 else None)
    print(json.dumps({
        "synthetic_sources":r["synthetic_source_owners"],
        "development":r["development_cases"],
        "heldout":r["heldout_cases"],
        "source_author_matches":r["author_outcome_matches"],
        "old_language_impossible_on_source_pairs":
            r["old_feature_space_impossibility_witnesses"],
        "actual_new_source_disclosed_features":r["source_supplied_new_feature_models"],
        "source_veto_is_hold":r["source_refused_new_feature_and_system_held"],
        "heldout_conditional_predictions":
            str(r["exact_heldout_world_outcomes"])+"/"+
            str(r["total_heldout_world_outcomes"]),
        "subprocess_elves":r["minimum_real_perspective_subprocesses_in_primary_run"],
        "new_person_refusal_blocks_old_person_permission":
            r["latest_source_revision_invalidates_old_consent"],
    },indent=2,sort_keys=True))
