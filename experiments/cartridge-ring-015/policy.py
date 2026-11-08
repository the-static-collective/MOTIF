"""RING-015: calibrated value of a SECOND REAL source test.

A cheap read-only TRIAGE is an observation about where AST structure
changed. It is NOT a secret synthetic label nor proof of an actual fault.
On observing it the policy decides whether to run the targeted reviewed
MATH or CONTROL tests, broader FULL regression, or STOP. If a targeted
test passes but a defect remains plausible, a third action can be FULL.

The decision uses RING-013's explicit 'value of action' principle:
a test is worthwhile only when expected detection benefit exceeds
measured resource cost and false-positive risk. Unlike RING-013, failure
probabilities and execution times are measured by RING-015 actual Docker
tests, not authored signal outputs.

All utility numbers (bug benefit, time conversion, false-alarm penalty)
remain researcher-chosen. Bayesian estimates from sparse seeded mutations
are NOT calibrated real-world software failure probabilities.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import math

import runner

SCHEMA="motif.ring015.source-observation-conditioned-policy.v1"
CUES=("MATH","CONTROL","MIXED","UNCHANGED","OTHER","SYNTAX_ERROR")
OPTIONS={
    "MATH":("MATH","FULL"),
    "CONTROL":("CONTROL","FULL"),
    "MIXED":("FULL",),
    "UNCHANGED":("FULL",),
    "OTHER":("FULL",),
}
SETTINGS={
    "detection_benefit":(6.0,12.0,24.0),
    "time_weight":(0.5,1.5,3.0),
    "false_alarm_penalty":(3.0,10.0),
}
ACTION_WHITELIST=("TRIAGE","MATH","CONTROL","FULL","STOP")


def validate_settings(params):
    if (not isinstance(params,dict) or set(params)!=set(SETTINGS)
            or any(params[k] not in SETINGS for k,SETINGS in SETTINGS.items())):
        raise ValueError("Not a reviewed value policy setting")
    return params


def fitted(source):
    """Estimate only from already executed train/dev test receipts."""
    if not isinstance(source,list) or len(source)<10:
        raise ValueError("Sparse or unmeasured source testing")
    cue_counts=Counter()
    bad_counts=Counter()
    observations=defaultdict(lambda:defaultdict(Counter))
    times=defaultdict(list)
    for case in source:
        tests=case["tests"]
        if set(tests)!=set(runner.PHASES):
            raise ValueError("Complete prior-sample source-test matrix required")
        cue=tests["TRIAGE"]["source_cue"]
        if cue not in CUES:
            raise ValueError("Unrecognized actual structural observation")
        label=bool(case["seeded_defect"])
        cue_counts[cue]+=1
        bad_counts[cue]+=int(label)
        for phase,r in tests.items():
            if (r.get("schema")!=runner.SCHEMA
                    or r.get("phase")!=phase
                    or r.get("case_id")!=case["case_id"]
                    or r.get("external_effects_executed")!=0
                    or not all(r.get("isolation",{}).values())):
                raise ValueError("Not a genuine source-owned no-network Docker receipt")
            times[phase].append(r["measured_wall_seconds"])
            observations[cue][phase][
                "bug_total" if label else "clean_total"]+=1
            observations[cue][phase][
                "bug_fail" if label and not r["actual_source_tests_passed"]
                else "clean_fail" if not label and not r[
                    "actual_source_tests_passed"] else "pass"]+=1
    if (not any(bad_counts.values())
            or sum(cue_counts.values())==sum(bad_counts.values())):
        raise ValueError("Both reviewed clean and synthetic defective source required")
    return {
        "cases":len(source),
        "seeded_defects":sum(bad_counts.values()),
        "cue_frequencies":{
            cue:round(cue_counts[cue]/len(source),8) for cue in CUES},
        "cue_totals":{cue:cue_counts[cue] for cue in CUES},
        "cue_bugs":{cue:bad_counts[cue] for cue in CUES},
        "mean_wall_seconds":{
            phase:round(sum(times[phase])/len(times[phase]),6)
            for phase in runner.PHASES},
        "actual_source_detection_observations":{
            cue:{phase:dict(observations[cue][phase])
                 for phase in runner.PHASES} for cue in CUES},
        "created_from_measured_source_outputs":True,
        "author_seeded_fault_truth_only_used_in_calibration":True,
    }


def prevalence(evidence,cue=None):
    if cue is None:
        n=evidence["cases"]
        x=evidence["seeded_defects"]
    else:
        n=evidence["cue_totals"][cue]
        x=evidence["cue_bugs"][cue]
    # beta(1,1) regularization prevents categorical certainty
    return (x+1)/(n+2)


def sensitivity(evidence,cue,phase,*,bad):
    if cue is None:
        counts={
            "bug_total":0,"bug_fail":0,"clean_total":0,"clean_fail":0,
        }
        for c in CUES:
            sub=evidence["actual_source_detection_observations"][c][phase]
            for k in counts:counts[k]+=sub.get(k,0)
    else:
        counts=evidence["actual_source_detection_observations"][cue][phase]
    suffix="bug" if bad else "clean"
    total=counts.get("bug_total" if bad else "clean_total",0)
    fails=counts.get("bug_fail" if bad else "clean_fail",0)
    # For sensitivity: Beta(1,1). For false alarms: prior expectation
    # closer to 0, reflecting our reviewed source test, but not perfect.
    if bad:return (fails+1)/(total+2)
    return (fails+1)/(total+8)


def net(phase,p,evidence,settings,cue=None):
    """Expected author-valued detection minus measured wall and alarm risk."""
    validate_settings(settings)
    if phase not in ("MATH","CONTROL","FULL"):
        raise ValueError("Only real reviewed focused/full source tests")
    return (
        p*sensitivity(evidence,cue,phase,bad=True)*
        settings["detection_benefit"]
        -(1-p)*sensitivity(evidence,cue,phase,bad=False)*
        settings["false_alarm_penalty"]
        -settings["time_weight"]*evidence["mean_wall_seconds"][phase]
    )


def choose_after_cue(evidence,settings,cue,*,already=()):
    """One observation can change which second test is valuable."""
    validate_settings(settings)
    if cue not in CUES:
        raise ValueError("Unknown observed code-scope cue")
    if cue=="SYNTAX_ERROR":
        return {"action":"STOP","reason":"SYNTAX_FAILURE_ALREADY_OBSERVED",
                "expected_value":0.0,"alternatives":[]}
    prior=prevalence(evidence,cue)
    options=[
        {"action":stage,"expected_value":round(
            net(stage,prior,evidence,settings,cue),6)}
        for stage in OPTIONS[cue] if stage not in already
    ]
    options.sort(key=lambda x:(-x["expected_value"],x["action"]))
    if not options or options[0]["expected_value"]<=0:
        return {"action":"STOP","expected_value":0.0,
                "reason":"FURTHER_TEST_NOT_WORTH_MODELED_COST",
                "alternatives":options}
    return {**options[0],"reason":"EXPECTED_DETECTION_BENEFIT_EXCEEDS_COST",
            "alternatives":options}


def choose_followup_after_pass(evidence,settings,cue,focused):
    """The THIRD test is optional: update defect belief after real PASS."""
    if focused not in ("MATH","CONTROL"):
        return {"action":"STOP","reason":"NO_FOCUSED_TEST_TO_UPDATE"}
    prior=prevalence(evidence,cue)
    detect=sensitivity(evidence,cue,focused,bad=True)
    false=sensitivity(evidence,cue,focused,bad=False)
    total=prior*(1-detect)+(1-prior)*(1-false)
    if total<=0:
        return {"action":"STOP","reason":"IMPOSSIBLE_PASS_UNDER_AUTHOR_MODEL"}
    posterior=prior*(1-detect)/total
    value_after=net("FULL",posterior,evidence,settings,cue)
    if value_after<=0:
        return {"action":"STOP","reason":"POST_PASS_RESIDUAL_RISK_BELOW_TEST_COST",
                "posterior_defect_probability":round(posterior,6),
                "expected_full_value":round(value_after,6)}
    return {"action":"FULL","reason":"POST_PASS_RESIDUAL_RISK_MERITS_DEEPER_TEST",
            "posterior_defect_probability":round(posterior,6),
            "expected_full_value":round(value_after,6)}


def choose_first(evidence,settings,*,force_triage=False):
    """Compares direct full test vs cheap observation's option value."""
    validate_settings(settings)
    p=prevalence(evidence)
    direct=net("FULL",p,evidence,settings,None)
    orientation=(
        -evidence["mean_wall_seconds"]["TRIAGE"]*
        settings["time_weight"])
    for cue,frequency in evidence["cue_frequencies"].items():
        if cue=="SYNTAX_ERROR":
            # A syntax error is a real source failure, detected in TRIAGE.
            contribution=prevalence(evidence,cue)*settings[
                "detection_benefit"]
        else:
            option=choose_after_cue(evidence,settings,cue)
            contribution=option["expected_value"]
        orientation+=frequency*contribution
    rankings={
        "FULL":round(direct,6),
        "TRIAGE":round(orientation,6),
        "STOP":0.0,
    }
    if force_triage:
        return {"action":"TRIAGE","ranked":rankings,
                "strategy_mode":"RESEARCH_CONDITIONAL_TRIAGE_FIRST"}
    chosen=max(rankings,key=lambda x:(rankings[x],x))
    return {"action":chosen,"ranked":rankings,
            "strategy_mode":"AUTONOMOUS_OPTION_VALUE_SELECTION"}


def summarize_case(actions):
    return {
        "attempted_phases":[x["phase"] for x in actions],
        "saw_actual_failure":any(
            not x["actual_source_tests_passed"] for x in actions),
        "number_source_tests":len(actions),
        "actual_test_seconds":round(sum(
            x["measured_wall_seconds"] for x in actions),6),
        "source_assertions":sum(
            x["real_source_assertions_executed"] for x in actions),
        "first_observed_cue":next((x["source_cue"] for x in actions
                                   if x["phase"]=="TRIAGE"),None),
    }


def route(evidence,settings,observe,*,force_triage=False):
    """Real action-admission function. NEXT test decided after output."""
    first=choose_first(evidence,settings,force_triage=force_triage)
    actions=[]
    reasons=[]
    phase=first["action"]
    if phase=="STOP":
        return {
            **summarize_case(actions),"receipts":actions,
            "decision_trace":[first],"initial_option_value":first["ranked"],
            "external_actions_authorized":False,
            "ambiguity_preserved":True,
        }
    real=observe(phase)
    actions.append(real)
    reasons.append(first)
    if phase=="TRIAGE":
        cue=real["source_cue"]
        if real["actual_source_tests_passed"]:
            decision=choose_after_cue(evidence,settings,cue)
            reasons.append(decision)
            phase=decision["action"]
            if phase!="STOP":
                second=observe(phase)
                actions.append(second)
                if second["actual_source_tests_passed"] and phase in (
                        "MATH","CONTROL"):
                    third=choose_followup_after_pass(
                        evidence,settings,cue,phase)
                    reasons.append(third)
                    if third["action"]=="FULL":
                        actions.append(observe("FULL"))
        else:
            reasons.append({
                "action":"STOP","reason":"SOURCE_SYNTAX_ERROR_ALREADY_OBSERVED"})
    # If starting with FULL it is a complete test; stop after it.
    if len(actions)>3 or any(x["phase"] not in runner.PHASES for x in actions):
        raise ValueError("Invalid or unbounded research action sequence")
    return {
        **summarize_case(actions),
        "receipts":actions,"decision_trace":reasons,
        "initial_option_value":first["ranked"],
        "external_actions_authorized":False,
        "ambiguity_preserved":True,
    }
