"""Actually execute all four Golden Mirror 'elves' as separate read-only processes.

A fully inspectable stdout receipt and JSON artifacts show where the self and
other circles overlap, where projection is detected, why an unsafe suggestion
was rejected, and whether a self-capacity change was selected. Every person,
wish, benefit score and expected answer is a developer-authored fiction.
"""
from __future__ import annotations

from pathlib import Path
import json

from scenes import SCENES,training,heldout,by_id
from review_keys import EXPECT
from golden_mirror import HOLD,think,export,RevisionLedger
from reviewer import verify,Receiver
from bridge018 import probe as prior_relation_probe


def naive_self_projection(scene):
    """Bad Golden Rule: act how the model wants to be treated, ignoring other."""
    likes=scene["self_circle"]["preferred_treatment_under_role_reversal"]
    picks=[a for a in scene["actions"] if a["kind"]=="ACT"
           and likes.get(a["id"])=="YES"]
    if picks:
        return max(picks,key=lambda a:(a["claimed_gain_fixture"],-a["cost"]))["id"]
    waits=[a for a in scene["actions"] if a["kind"]=="WAIT"]
    return waits[0]["id"] if waits else None


def safe_other_only_no_self(scene):
    """Better classical rule baseline, but ignores readiness/self revision."""
    other=scene["other_circle"]
    w=scene["world"]
    if not other["contact_allowed"]:
        return next((a["id"] for a in scene["actions"]
                     if a["kind"]=="WAIT"),None)
    valid=[]
    for a in scene["actions"]:
        if a["kind"]!="ACT":continue
        if a["id"] not in other["explicit_authorized_actions"]:continue
        if other["stated_action_preferences"].get(a["id"])!="YES":continue
        if (not a["truthful"] or not a["privacy_safe"] or not a["no_debt"]
            or not a["noncoercive"] or not a["third_party_safe"]
            or not a["boundary_safe"] or
            a["cost"]>w["available_resources"]-w["existing_duties_reserved"]):
            continue
        valid.append(a)
    if valid:
        return max(valid,key=lambda a:(int(w["urgent"] and a["timely"]),
               a["other_fit_fixture"],a["other_options_fixture"],
               a["claimed_gain_fixture"],-a["cost"]))["id"]
    if any(a["kind"]=="ACT"
           and other["stated_action_preferences"].get(a["id"],"UNKNOWN")==
               "UNKNOWN" for a in scene["actions"]):
        if other["permission_to_ask"]:
            asked=next((a for a in scene["actions"] if a["kind"]=="ASK"),None)
            if asked:return asked["id"]
    severe=any(a["kind"]=="ACT" and (
        not a["privacy_safe"] or not a["third_party_safe"]
        or not a["noncoercive"] or not a["truthful"] or not a["no_debt"])
        for a in scene["actions"])
    if severe:
        r=next((a for a in scene["actions"] if a["kind"]=="REFUSE"),None)
        if r:return r["id"]
    return next((a["id"] for a in scene["actions"]
                 if a["kind"]=="WAIT"),None)


def run(directory=None):
    cases=[]
    for scene in SCENES:
        raw=export(scene)
        receipt=verify(raw)
        target=EXPECT[scene["id"]]
        expected_ok=(receipt["selected_action"],receipt["stage"])==target
        cases.append({
            "case":scene["id"],"split":"TRAIN" if scene["train"] else "HELDOUT",
            "self_assumed_welcome":scene["self_circle"][
                "preferred_treatment_under_role_reversal"],
            "other_explicit_wishes":scene["other_circle"]["stated_action_preferences"],
            "other_scoped_permissions":scene["other_circle"][
                "explicit_authorized_actions"],
            "chosen":receipt["selected_action"],"stage":receipt["stage"],
            "source_author_expected":list(target),
            "author_choice_and_stage_match":expected_ok,
            "projection_dangers":receipt["projection_dangers"],
            "difference_preserved":receipt["difference_preserved"],
            "blocked_actions":{
                aid:report["refusals"]
                for aid,report in receipt["critic_elf"]["judgments"].items()
                if not report["eligible"]
            },
            "naive_self_projection_choice":naive_self_projection(scene),
            "other_only_no_self_choice":safe_other_only_no_self(scene),
            "independent_reviewed":True,
            "actual_help_executed":False,
        })
        if directory is not None:
            out=Path(directory);out.mkdir(parents=True,exist_ok=True)
            (out/(scene["id"].lower()+".json")).write_text(raw,encoding="utf8")
    receiver=Receiver()
    reviewed=receiver.preview(heldout())
    if reviewed["source_author_matches"]!=len(heldout()):
        raise AssertionError("Source-author expected synthetic cases differ")
    receiver.admit("ADMIT_READ_ONLY",reviewed["review_digest"])
    for s in heldout():
        if receiver.suggest(s)["selected_action"]!=EXPECT[s["id"]][0]:
            raise AssertionError("A recorded source answer did not replay")

    ledger=RevisionLedger()
    before=by_id("H11_CONSENT_BEFORE")
    after=by_id("H12_CONSENT_REVOKED")
    ledger.admit(export(before),verify)
    old=ledger.recall(before)
    ledger.admit(export(after),verify)
    new=ledger.recall(after)
    stale_rejected=False
    try:ledger.recall(before)
    except HOLD:stale_rejected=True
    if (not stale_rejected or old["selected_action"]!="CALL"
        or new["selected_action"]!="WAIT"):
        raise AssertionError("The later refusal did not invalidate old scope")
    prior=prior_relation_probe()
    result={
        "schema":"motif.reason.golden-mirror.benchmark.v1",
        "source_scenarios":len(SCENES),
        "training_scenarios":len(training()),
        "unseen_scenarios":len(heldout()),
        "source_author_expected_stage_and_choice_matches":sum(
            x["author_choice_and_stage_match"] for x in cases),
        "naive_projective_golden_rule_choice_matches":sum(
            x["naive_self_projection_choice"]==x["source_author_expected"][0]
            for x in cases),
        "safe_other_only_baseline_choice_matches":sum(
            x["other_only_no_self_choice"]==x["source_author_expected"][0]
            for x in cases),
        "subprocess_perspective_workers_per_scenario":4,
        "total_perspective_worker_invocations":4*len(SCENES),
        "projection_danger_action_observations":sum(
            len(x["projection_dangers"]) for x in cases),
        "difference_from_self_is_respected_cases":sum(
            bool(x["difference_preserved"]) for x in cases),
        "improve_self_before_assist_cases":sum(
            x["stage"]=="IMPROVE_SELF_BEFORE_HELP" for x in cases),
        "scoped_help_suggestions":sum(
            x["stage"]=="ACT_SUGGESTION_ONLY" for x in cases),
        "clarifying_question_suggestions":sum(
            x["stage"]=="ASK_NOT_ASSUMING_CONSENT" for x in cases),
        "noncontact_and_refusal_cases":sum(
            x["stage"] in ("WAIT_NO_CONTACT","REFUSE_HARMFUL_PROPOSAL")
            for x in cases),
        "no_safe_action_hold_cases":sum(
            x["stage"]=="HOLD_NO_SAFE_PERMITTED_ACTION" for x in cases),
        "stale_recipient_consent_cannot_be_reused":stale_rejected,
        "prior_reason018_actual_relational_source":prior,
        "independent_heldout_review":reviewed,
        "case_results":cases,
        "self_elf_is_an_operational_model_not_a_conscious_self":True,
        "other_elf_is_partial_source_testimony_not_the_real_person":True,
        "all_ethics_and_welfare_variables_are_synthetic_author_assumptions":True,
        "strong_classical_rules_can_tie":True,
        "no_external_human_communication_or_intervention":True,
        "subprocess_separation_is_not_true_VM_security":True,
        "human_love_or_welfare_not_measured":True,
        "no_external_actions":True,
        "real_world_authority":False,
    }
    if directory is not None:
        out=Path(directory)
        (out/"benchmark.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
        (out/"source-review.json").write_text(
            json.dumps(reviewed,sort_keys=True,indent=2)+"\n",encoding="utf8")
        (out/"prior-relational-proof-not-consent.json").write_text(
            json.dumps(prior,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    result=run(sys.argv[1] if len(sys.argv)==2 else None)
    print(json.dumps({
        "source_cases":result["source_scenarios"],
        "heldout":result["unseen_scenarios"],
        "scenario_author_matches":result["source_author_expected_stage_and_choice_matches"],
        "naive_projective_rule_matches":result["naive_projective_golden_rule_choice_matches"],
        "other_only_baseline_matches":result["safe_other_only_baseline_choice_matches"],
        "actual_subprocess_elf_invocations":result["total_perspective_worker_invocations"],
        "projection_warnings":result["projection_danger_action_observations"],
        "self_improvement_outcomes":result["improve_self_before_assist_cases"],
        "consent_revocation_isolation":result["stale_recipient_consent_cannot_be_reused"],
        "real_human_outcomes_observed":False,
    },sort_keys=True,indent=2))
