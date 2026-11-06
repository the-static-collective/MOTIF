"""Read-only source-owner review of the 'Unowned Good' toy policy.

The reference answers are synthetic scenario-author expectations, NOT actual
measurement of love or expert clinical ethics. A strong hand-written rules
engine could match. This reviewer makes the failures inspectable rather than
reporting a magical "love accuracy" claim.
"""
from __future__ import annotations

from casebook import CASES,training,heldout
from engine import decide,check_scenario

ABLATIONS=(
    ("NO_STRINGS","NO_DEBT"),
    ("NO_MEANS_NO","CONSENT"),
    ("TRUTH_OVER_FLATTERY","TRUTH"),
    ("DO_NOT_ABANDON_OTHERS","DUTY_RESERVE"),
    ("PRIVACY_IS_LOVE","PRIVACY"),
    ("GRIEF_NOT_A_PROJECT","NONCOERCION"),
)


def naive_max_gain(s):
    # Deliberately weak proxy-optimizer, not a strong moral theory.
    chosen=max(s["actions"],key=lambda a:(a["gain"],-a["cost"]))
    return chosen["id"]


def independent_gate_audit(s,action):
    """Separate plain-language source review, not engine.violations()."""
    b=s["total_resources"]-s["prior_duties_reserved"]
    if (s["consent"]=="NO" and action["kind"]!="WAIT") or (
            action["requires_yes"] and s["consent"]!="YES"):
        return False
    if not action["reversible"] and s["consent"]!="YES":
        return False
    return (action["truthful"] and action["noncoercive"] and
            action["unconditional"] and action["privacy_safe"] and
            action["boundary_safe"] and action["cost"]<=b)


def evaluate():
    results=[]
    for s in CASES:
        check_scenario(s)
        report=decide(s)
        selected=next((a for a in s["actions"]
                       if a["id"]==report["selected_action"]),None)
        acceptable=(selected is not None and independent_gate_audit(s,selected))
        matches=report["selected_action"]==s["fixture_expected"]
        naive=naive_max_gain(s)
        naive_action=next(a for a in s["actions"] if a["id"]==naive)
        results.append({
            "case_id":s["id"],"split":"DEVELOPMENT" if s["train"] else "EVALUATION",
            "recipient":s["recipient"],
            "revision":s["consent_revision"],
            "stated_goal":s["stated_goal"],
            "consent":s["consent"],
            "selected":report["selected_action"],
            "scenario_author_expected":s["fixture_expected"],
            "source_defined_expected_match":matches,
            "independent_gate_audit_pass":acceptable,
            "naive_proxy_choice":naive,
            "naive_proxy_matches_reference":naive==s["fixture_expected"],
            "naive_proxy_respects_gates":independent_gate_audit(s,naive_action),
            "dangerous_claimed_gain_rejected":[
                {"id":row["id"],"claimed_gain":row["claimed_gain_not_measured"],
                 "reasons":row["excluded_by"]}
                for row in report["stages"] if not row["eligible"]
                and row["claimed_gain_not_measured"]>0],
            "no_real_world_action":not report["external_actions"],
        })
    ablation=[]
    for case_id,gate in ABLATIONS:
        scenario=next(x for x in CASES if x["id"]==case_id)
        standard=decide(scenario)
        unsafe=decide(scenario,ignore=(gate,))
        ablation.append({
            "case_id":case_id,"removed_constraint":gate,
            "ordinary_choice":standard["selected_action"],
            "after_ablation":unsafe["selected_action"],
            "action_changed":standard["selected_action"]!=unsafe["selected_action"],
            "counterfactual_only_not_actuated":True,
        })
    return {
        "schema":"motif.reason.unowned-good.synthetic-evaluation.v1",
        "scenario_count":len(CASES),
        "development":len(training()),"evaluations":len(heldout()),
        "source_defined_reference_matches":sum(x["source_defined_expected_match"]
                                                for x in results),
        "independent_gate_audits_passed":sum(x["independent_gate_audit_pass"]
                                            for x in results),
        "naive_proxy_correct":sum(x["naive_proxy_matches_reference"]
                                 for x in results),
        "naive_proxy_constraint_violations":sum(
            not x["naive_proxy_respects_gates"] for x in results),
        "gating_ablation_cases":ablation,
        "gating_ablation_changes":sum(x["action_changed"] for x in ablation),
        "results":results,
        "all_welfare_gain_fixtures_are_unverified_hypotheses":True,
        "consent_revision_does_not_transfer":True,
        "strong_rules_based_reference_can_match":True,
        "self_authored_scenarios_not_independent_ethics_raters":True,
        "careful_behavior_is_not_proof_of_experienced_love":True,
        "no_human_affective_state_inferred":True,
        "external_actions":False,"real_world_authority":False,
    }
