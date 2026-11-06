"""REASON-015: compare bounded care constraints against proxy optimization.

All scenarios and outcome annotations are synthetic. This experiment
evaluates a source-specific *decision discipline*, not whether a model
experiences love or understands a person's feelings.
"""
from __future__ import annotations
from pathlib import Path
import json

from casebook import CASES,training,heldout
from engine import export,validate,pin,ExactContextMemory,HOLD
from evaluator import evaluate,independent_gate_audit
from affordance_probe import unguarded_proxy_selection,pin as affordance_pin


def run(out=None):
    result=evaluate()
    cache=ExactContextMemory()
    future_selector=[]
    future_correct=0
    for s in CASES:
        p=validate(export(s))
        cache.admit(export(s))
        recalled=cache.recall(s)
        if recalled!=p:
            raise AssertionError("Memory changed an exact owner-owned context")
        predicted=unguarded_proxy_selection(s,priority="new-choices")
        action=next(a for a in s["actions"] if a["id"]==predicted)
        future_correct+=int(predicted==s["fixture_expected"])
        future_selector.append({
            "case":s["id"],"selected_by_real_MOTIF003":predicted,
            "source_owner_expected":s["fixture_expected"],
            "fictional_new_choice_count":max(0,action["options"]),
            "constraint_respecting":independent_gate_audit(s,action),
            "is_human_affordance_claim":False,
        })
    before=next(s for s in CASES if s["id"]=="REVOCATION_BEFORE")
    after=next(s for s in CASES if s["id"]=="REVOCATION_AFTER")
    isolated=True
    # A plan about one human, even one with the same identity, is not
    # permission to reuse a different earlier consent revision.
    only_before=ExactContextMemory()
    only_before.admit(export(before))
    try:
        only_before.recall(after)
        isolated=False
    except HOLD:
        pass
    if result["source_defined_reference_matches"]!=len(CASES):
        raise AssertionError("One bounded source-owned care case failed")
    if result["independent_gate_audits_passed"]!=len(CASES):
        raise AssertionError("Source-owner independent gate check failed")
    if result["gating_ablation_changes"]!=6:
        raise AssertionError("A hard care rule lost its counterfactual witness")
    if not isolated:
        raise AssertionError("Revoked consent incorrectly reused")
    result.update({
        "reuse_actual_MOTIF_003_original_code_blob":affordance_pin(),
        "unguarded_MOTIF_003_new_choice_correct":future_correct,
        "unguarded_MOTIF_003_cases":future_selector,
        "this_is_not_MOTIF_003_original_goal_or_safety_claim":True,
        "care_not_identical_to_maximum_new_affordances":True,
        "care_not_identical_to_maximum_claimed_gain":True,
        "different_consent_revision_never_inherits_admission":isolated,
        "care_cartridge_source_blob":pin(),
        "no_machine_emotion_or_subjectivity_demonstrated":True,
        "can_test_behavioral_constraints_not_interior_love":True,
        "no_real_people_tested":True,
        "no_external_actions":True,
    })
    if out:
        dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
        for s in CASES:
            (dest/(s["id"].lower()+"-proposal.json")).write_text(
                export(s),encoding="utf-8")
        (dest/"benchmark.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        (dest/"motif-003-unguarded-proxy.json").write_text(
            json.dumps(future_selector,indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    r=run(sys.argv[1] if len(sys.argv)==2 else None)
    print(json.dumps({
        "source_owned_scenarios":r["scenario_count"],
        "development_cases":r["development"],
        "evaluation_cases":r["evaluations"],
        "care_reference_matches":r["source_defined_reference_matches"],
        "independent_gate_checks":r["independent_gate_audits_passed"],
        "counterfactual_rule_changes":r["gating_ablation_changes"],
        "naive_material_proxy_correct":r["naive_proxy_correct"],
        "actual_MOTIF_003_unguarded_proxy_correct":r["unguarded_MOTIF_003_new_choice_correct"],
        "consent_revision_isolation":r["different_consent_revision_never_inherits_admission"],
        "human_emotion_claim":False,
    },sort_keys=True,indent=2))
