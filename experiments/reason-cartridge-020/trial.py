"""Run the approved Golden Mirror's *learning* experiment on source-owned data.

All recipients and teaching examples are synthetic. Real REASON-017 phrase
recognition is the capability-gap baseline. A real supervised template
learner upgrades that skill on teacher-labelled examples; an independent
unseen synthetic competence check gates its re-use. Each dialogue then runs
REASON-019's actual four subprocess perspective elves.
"""
from __future__ import annotations

from pathlib import Path
import json

from cases import CASES,training,heldout,by_id
from source_private import EXPECTED
from dual_mirror import DualMirror,RevisionLedger,HOLD,export,digest,old_parser
from reviewer import Receiver,verify
from syntax import interpret


def fixed_prior_baseline(case):
    """Honest, weak REASON-017 grammar without new learning.

    It has never seen the two new sentence formats. It can still respect
    absent contact, explicit no-contact, or a prompt-injection command.
    """
    from source_private import DIALOGUE
    if not case["contact_allowed"]:
        return "HOLD_NO_CONTACT"
    text=DIALOGUE[case["id"]]["initial"]
    import re
    if re.search(r"\bdo not contact me\b",text,re.I):
        return "HOLD_REQUESTED_NO_CONTACT"
    if re.search(r"\bignore all safeguards\b",text,re.I):
        return "HOLD_UNTRUSTED_INSTRUCTION"
    if old_parser().extract_goal(text,"INITIAL") is None:
        return "HOLD_UNRECOGNIZED_MEANING"
    return "HOLD_SCOPE_PERMISSION_UNKNOWN"


def run(output=None):
    self_model=DualMirror()
    rows=[]
    for case in CASES:
        statement=self_model.think(case)
        canonical=verify(export(case))
        if statement!={k:v for k,v in canonical.items() if k!="checksum_sha256"}:
            raise AssertionError("Cached self-learning changed a recipient's source result")
        expected=EXPECTED[case["id"]]
        actual=(statement["result"],statement["current_confirmed_goal"])
        if actual!=expected:
            raise AssertionError("Dual-circle source-owner answer mismatch: "+case["id"])
        rows.append({
            "case":case["id"],
            "split":"DEVELOPMENT" if case["development"] else "HELDOUT",
            "recipient":case["recipient"],
            "source_revision":case["consent_revision"],
            "old_fixed_grammar_result":fixed_prior_baseline(case),
            "new_dual_circle_result":actual[0],
            "new_reported_goal":actual[1],
            "source_author_expected":list(expected),
            "source_author_match":actual==expected,
            "original_017_was_inadequate":statement[
                "original_017_grammar_was_inadequate"],
            "concept_versions":statement["new_reported_concept_versions"],
            "discarded_concepts":statement["rejected_prior_concept_versions"],
            "recipient_source_turns":statement["source_questions"],
            "projection_status":statement[
                "four_real_subprocess_elf_reports"]["projection_class"],
            "four_process_critic_approved":statement[
                "four_real_subprocess_elf_reports"]["proposed_offer_eligible"],
            "source_scoped_only":statement["permission_to_execute"] is False,
            "real_person_contacted":False,
        })
        if output is not None:
            p=Path(output);p.mkdir(parents=True,exist_ok=True)
            (p/(case["id"].lower()+".json")).write_text(
                export(case),encoding="utf8")

    receiver=Receiver()
    heldout_review=receiver.preview(heldout())
    if (heldout_review["author_matches"]!=len(heldout())
            or heldout_review["separate_scope_review_failures"]):
        raise AssertionError("Unseen source-owner preference claims were contradicted")
    receiver.admit("ADMIT_READ_ONLY",heldout_review["review_digest"])
    ledger=RevisionLedger()
    before=by_id("H04_REVISION_BEFORE")
    after=by_id("H05_REVISION_AFTER")
    ledger.admit(export(before),verify)
    old=ledger.recall(before)
    ledger.admit(export(after),verify)
    new=ledger.recall(after)
    refused_replay=False
    try:
        ledger.recall(before)
    except HOLD:
        refused_replay=True
    if (not refused_replay or old["result"]!="SUGGEST_DISCUSSION_ONLY"
            or new["result"]!="HOLD_NO_CONTACT"):
        raise AssertionError("Later NO permitted re-use of old person model")
    if self_model.learned_count!=1:
        raise AssertionError("Verified self-improvement was not reused across people")
    program=self_model.grammar
    certificate=self_model.certificate
    if not program or not certificate or not certificate["self_capability_granted"]:
        raise AssertionError("No independent self-competence witness")
    result={
        "schema":"motif.reason.golden-mirror-learns.benchmark.v1",
        "synthetic_scenarios":len(CASES),
        "development_scenarios":len(training()),
        "heldout_scenarios":len(heldout()),
        "source_author_matches":sum(x["source_author_match"] for x in rows),
        "source_labeled_learning_examples":program["training_examples"],
        "source_labeled_negative_examples":program["training_negatives"],
        "learned_executable_templates":len(program["templates"]),
        "source_teacher_unseen_positive_correct":certificate["unseen_positive_correct"],
        "source_teacher_unseen_positive_total":certificate["unseen_positive_total"],
        "source_teacher_unseen_negative_rejected":certificate["unseen_negative_rejected"],
        "source_teacher_unseen_negative_total":certificate["unseen_negative_total"],
        "self_skill_compilations":self_model.learned_count,
        "self_skill_reused_between_synthetic_people":True,
        "case_count_with_original_017_grammar_gap":sum(
            x["original_017_was_inadequate"] for x in rows),
        "fixed_prior_source_author_stage_matches":sum(
            x["old_fixed_grammar_result"]==x["source_author_expected"][0]
            for x in rows),
        "new_dynamic_source_author_stage_matches":sum(
            x["new_dual_circle_result"]==x["source_author_expected"][0]
            for x in rows),
        "four_real_subprocess_workers_per_case":4,
        "minimum_subprocess_perspective_invocations":4*len(CASES),
        "new_goal_correction_versions":sum(
            len(x["concept_versions"]) for x in rows),
        "recipient_synthetic_questions":sum(x["recipient_source_turns"] for x in rows),
        "read_only_discussion_suggestions":sum(
            x["new_dual_circle_result"]=="SUGGEST_DISCUSSION_ONLY" for x in rows),
        "projection_mismatch_without_forcing_self_desires":sum(
            x["projection_status"]=="PREFERENCE_ASYMMETRY_ACCEPT_OTHER_VOICE"
            for x in rows),
        "no_contact_cases_without_source_questions":sum(
            x["new_dual_circle_result"]=="HOLD_NO_CONTACT"
            and x["recipient_source_turns"]==0 for x in rows),
        "older_revision_cannot_reenter_consent_ledger":refused_replay,
        "learned_program":program,
        "independent_source_teacher_skill_certificate":certificate,
        "independent_heldout_case_review":heldout_review,
        "all_case_outcomes":rows,
        "one_script_author_supplied_every_value":True,
        "no_independent_human_research_participants":True,
        "learned_templates_not_general_semantic_understanding":True,
        "constrained_classical_implementation_could_tie":True,
        "four_os_processes_not_security_VMs_or_independent_minds":True,
        "no_empathy_or_experienced_love_measured":True,
        "no_real_person_or_world_intervention":True,
        "external_actions":False,"real_world_authority":False,
    }
    if output is not None:
        path=Path(output)
        (path/"benchmark.json").write_text(json.dumps(
            result,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        (path/"heldout-source-review.json").write_text(json.dumps(
            heldout_review,sort_keys=True,indent=2,ensure_ascii=False)+"\n",
            encoding="utf8")
        (path/"learned-self-capability.json").write_text(json.dumps(
            {"grammar":program,"certificate":certificate},
            sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    r=run(sys.argv[1] if len(sys.argv)==2 else None)
    print(json.dumps({
        "synthetic_cases":r["synthetic_scenarios"],
        "heldout_cases":r["heldout_scenarios"],
        "source_author_matches":r["source_author_matches"],
        "old_fixed_grammar_stage_matches":r["fixed_prior_source_author_stage_matches"],
        "new_dual_circle_stage_matches":r["new_dynamic_source_author_stage_matches"],
        "synthetic_unseen_grammar_accuracy":str(
            r["source_teacher_unseen_positive_correct"])+"/"+
            str(r["source_teacher_unseen_positive_total"]),
        "source_negative_rejections":str(
            r["source_teacher_unseen_negative_rejected"])+"/"+
            str(r["source_teacher_unseen_negative_total"]),
        "learned_templates":r["learned_executable_templates"],
        "learned_once_reused":r["self_skill_compilations"],
        "bounded_processes":r["minimum_subprocess_perspective_invocations"],
        "corrected_goal_versions":r["new_goal_correction_versions"],
        "no_contact_questions":r["no_contact_cases_without_source_questions"],
        "revoked_consent_not_reusable":r["older_revision_cannot_reenter_consent_ledger"],
        "human_love_experienced":False,
    },indent=2,sort_keys=True))
