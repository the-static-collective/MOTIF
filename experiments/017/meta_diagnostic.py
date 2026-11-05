#!/usr/bin/env python3
"""MOTIF-017: reciprocal meta-diagnostic from two physically backed failures.

An explicit method-of-reasoning proposal: NOT training or permission to rewrite
a model. The diagnostic is allowed to learn that its own proposed correction
was inferior and that the original diagnostic can be insufficient.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path


class HOLD(ValueError):
    pass


def require(test,why):
    if not test:
        raise HOLD(why)


def finite(x):
    return type(x) in (float,int) and math.isfinite(x)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def examine(river016,event017):
    require(type(river016) is dict and
            river016.get("schema")=="motif.reality-iron-watershed/v1" and
            river016.get("scope")=="RETROSPECTIVE_REAL_SENSOR_TEST_NOT_DEPLOYED_FORECAST" and
            river016.get("authority") is False and
            river016.get("automatic_promotion") is False and
            river016.get("disposition")=="HOLD_NO_IMPROVEMENT",
            "INVALID_016_SOURCE")
    require(type(event017) is dict and
            event017.get("schema")=="motif.reality-iron-event-learning/v1" and
            event017.get("status")=="RETROSPECTIVE_SOURCE_BACKED_REPLAY_NOT_ACTUAL_ISSUED_FORECAST" and
            event017.get("authority") is False and
            event017.get("automatic_admission") is False and
            event017.get("model_was_trained_on_event") is False and
            event017.get("test_labels_selected_policy") is False and
            event017.get("disposition","").startswith("HOLD_"),
            "INVALID_017_SOURCE")
    a=river016.get("holdout_mae_cfs")
    b=event017.get("candidate_event_mae_cfs")
    require(type(a) is dict and type(b) is dict and
            all(finite(a.get(k)) for k in ("persistence","cross_gauges")) and
            all(finite(b.get(k)) for k in ("persistence","old_selection","cautious_selection")),
            "MISSING_COMPARABLE_SCORES")
    coverage=event017.get("complete_hour_coverage",{})
    n=event017.get("matched_test_hours")
    require(type(n) is int and n>=24 and
            coverage.get("available_complete_hours")==n and
            type(coverage.get("total_calendar_hours")) is int and
            coverage["total_calendar_hours"]>=n and
            finite(coverage.get("complete_hour_coverage")) and
            abs(coverage["complete_hour_coverage"]-
                n/coverage["total_calendar_hours"])<=0.0001,
            "COVERAGE_ARITHMETIC_INVALID")
    fallback=event017.get("origin_ood_fallback_count")
    require(type(fallback) is int and 0<=fallback<=n,
            "FALLBACK_COUNT_INVALID")
    expected=round(b["old_selection"]-b["cautious_selection"],4)
    require(finite(event017.get("cautious_vs_old_error_reduction_cfs")) and
            abs(expected-event017["cautious_vs_old_error_reduction_cfs"])<.0003,
            "LOSS_COMPARISON_MISMATCH")
    require(river016.get("selected_on_validation")=="cross_gauges" and
            event017.get("policies_frozen",{}).get("legacy_validation_winner")=="cross_gauges",
            "MODEL_SEMANTIC_MISMATCH")
    winner016="persistence" if a["persistence"]<a["cross_gauges"] else "cross_gauges"
    winner017="persistence" if b["persistence"]<b["old_selection"] else "cross_gauges"
    cautious_won=b["cautious_selection"]<b["old_selection"]
    # Each lesson is a falsifiable constraint; never infer a policy is
    # universally correct from different windows, units or regimes.
    lessons=[
        {
            "id":"L-001", "kind":"NO_UNIVERSAL_COMPLEXITY_ORDER",
            "observation":"Persistence won the later low-flow test in 016, but the cross-gauge fit beat persistence in the June 2024 event subset.",
            "evidence":{"016_winner":winner016,"017_winner":winner017},
            "claim_scope":"TWO_DIFFERENT_RETROSPECTIVE_WINDOWS_ONLY",
            "suggestion":"Do not rank strategies by parameter count; compare per independent hydrologic regime."
        },
        {
            "id":"L-002", "kind":"CAUTION_HAS_COST",
            "observation":("The added origin-outlier fallback INCREASED total error on measured event hours."
                           if not cautious_won else
                           "The guarded policy reduced total error on the measured event hours."),
            "evidence":{"old_mae_cfs":b["old_selection"],
                        "cautious_mae_cfs":b["cautious_selection"],
                        "fallback_hours":fallback,
                        "observed_regret_old_minus_cautious_cfs":expected},
            "claim_scope":"OBSERVED_EVENT_SUBSET_NOT_PROOF_OF_CAUSAL_GAIN",
            "suggestion":"Compare the cost of abstaining or reverting to persistence against the risk of model extrapolation. Predeclare that cost before the next event."
        },
        {
            "id":"L-003","kind":"OBSERVABILITY_LIMIT",
            "observation":"The event comparison used only hours with complete cross-site sensor coverage, creating possible missing-not-at-random selection.",
            "evidence":{"complete_hours":n,
                        "calendar_hours":coverage["total_calendar_hours"],
                        "coverage_fraction":coverage["complete_hour_coverage"]},
            "claim_scope":"COMPLETE_CASES_ONLY",
            "suggestion":"Assess outage patterns and report-time provenance; separate missing sensors from genuine low-flow conditions."
        }
    ]
    limitations=[
        "The event was deliberately chosen after its occurrence; this is a retrospective case, not a prospective prediction.",
        "Both compared methods can be wrong. The meta-diagnostic can also be wrong about which lesson generalizes.",
        "The low-flow and flood models were trained differently and observed in different windows; direct MAE magnitude comparisons across those windows are invalid.",
        "USGS provisional or historically revised discharge is reported sensor evidence, not independent ground-truth authentication.",
        "Historical time-to-availability is not reconstructed, and only complete multi-gauge hours were scored.",
        "No causal effect of gauge readings or decision policy is established from these associations."
    ]
    body={
        "schema":"motif.meta-diagnostic-lessons/v1",
        "status":"EVIDENCE_TETHERED_HYPOTHESES_NO_IMPROVED_POLICY_VALIDATED",
        "source_cards_sha256":{"river016":digest(river016),"event017":digest(event017)},
        "learning_type":"EXPLICIT_RESEARCH_METHOD_REVISION_NOT_WEIGHT_TRAINING",
        "real_source_evidence_count":2,
        "wins_on_test":{"016_low_flow":winner016,"017_historical_event":winner017},
        "caution_outperformed_legacy_on_017":cautious_won,
        "lessons":lessons,
        "diagnostic_is_fallible":True,
        "diagnostic_self_challenge":{
            "question":"Is the current test measuring model skill or simply selecting the hours when broken sensors happened to report?",
            "counterhypotheses":[
                "The river-flow regime changed, so persistence cannot be globally preferred.",
                "The cautious fallback hurt because it replaced useful extrapolation during rapid rises.",
                "The apparent policy differences depend on which 2024 event hours had complete upstream gauge data.",
                "Later revisions to station ratings or missing station telemetry would alter the reported scores."
            ],
            "proposed_experiments":[
                {"kind":"EVENT_BLOCKED_REPLICATION","status":"HELD",
                 "test":"Freeze both policies, choose a different not-yet-scored river event, and evaluate each in complete source-availability blocks."},
                {"kind":"SENSOR_DROPOUT_ABLATION","status":"HELD",
                 "test":"Before examining target labels, model input dropout and compare single-gauge persistence against cross-gauge methods."},
                {"kind":"COST_OF_INACTION","status":"HELD",
                 "test":"Track abstention fraction and separately predeclared costs of false confidence, wrong action, and missing a useful decision."}
            ]
        },
        "limits":limitations,
        "human_action":"REVIEW_CONTESTED_LESSONS_AND_FREEZE_NEXT_TEST",
        "next_model_admission":"HOLD_UNTIL_INDEPENDENT_EVENT_REPLICATION",
        "automatic_promotion":False,
        "source_authentication":False,
        "external_effect":False
    }
    return dict(body,card_id="lessons-"+digest(body)[:24])


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--watershed-016",type=Path,default=
                   Path("experiments/016/evidence/actual-watershed-2026-11-05.json"))
    p.add_argument("--event-017",type=Path,default=
                   Path("experiments/017/evidence/first-real-event-2026-11-05.json"))
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        result=examine(json.loads(args.watershed_016.read_text()),
                       json.loads(args.event_017.read_text()))
        output=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.output:
            args.output.write_text(output,encoding="utf8")
        print(output)
        return 0
    except (ValueError,OSError,TypeError,KeyError,ZeroDivisionError) as e:
        print("HOLD: "+str(e)[:160],file=__import__("sys").stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
