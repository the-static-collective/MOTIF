"""LEGIT-016: epistemic and economic promotion gate for measured improvements.

A relative speed difference is a measured effect on ONE workload, not a
probability that future inventions will succeed. A source-level safety proof
is not evidence of a useful performance improvement. One selected candidate
timed eleven times is not eleven independent innovations.

This gate refuses "compound growth" extrapolation unless the system has
actual evidence for repeated DEPLOYED, independently verified improvements
on comparable workloads. Current evidence has none: LEGIT-014 HOLD.

A prospective trial format is provided for the next experiment, but no
unverified claim of external authorship can force promotion.
"""
from __future__ import annotations
from math import isfinite
from statistics import median
from hashlib import sha256
import json

from evidence import HOLD,BASELINES,archive,summarize

RAW_ARMS=("prior_012","prior_013","candidate_014","strong_classical")
MIN_GAIN=.08
MAX_REGRESSION=.10

def _checked(episode):
    if (not isinstance(episode,dict) or
        episode.get("schema")!="motif.empirical-improvement-episode.v1" or
        episode.get("source")!="EXECUTED_ACTUAL_GENERATED_SOLVERS" or
        episode.get("external_z3_reverified_prior_finite_rewrite") is not True or
        episode.get("output_mismatches")!=0 or
        episode.get("new_seed_graphs")!=24 or
        episode.get("test_set_independently_authored") is not False or
        episode.get("automatic_promotion") is not False or
        episode.get("source_self_improved_in_this_experiment") is not False):
        raise HOLD("Wrong measured evidence scope")
    observations=episode.get("raw_repeat_samples")
    if not isinstance(observations,dict) or set(observations)!=set(RAW_ARMS):
        raise HOLD("Missing strong baseline or raw source")
    sample_count=episode.get("sample_count_per_arm")
    if sample_count!=9:
        raise HOLD("Incomplete repeated measurement protocol")
    results={}
    for name,record in observations.items():
        if set(record)!={"wall_ms","cpu_ms"}:
            raise HOLD("Missing CPU/wall separation")
        for unit in ("wall_ms","cpu_ms"):
            arr=record[unit]
            if (not isinstance(arr,list) or len(arr)!=sample_count or
                any(type(x) not in (float,int) or not isfinite(x) or x<=0
                    for x in arr)):
                raise HOLD("Malformed/repeated performance evidence")
            actual=median(arr)
            recorded=episode["descriptive_medians_ms"][name][
                "wall" if unit=="wall_ms" else "cpu"]
            if abs(actual-recorded)>1e-5:
                raise HOLD("Reported sample median does not match observations")
        results[name]={unit:median(record[unit]) for unit in ("wall_ms","cpu_ms")}
    return results

def compare(episode):
    previous=summarize(archive())
    current=_checked(episode)
    candidate=episode["raw_repeat_samples"]["candidate_014"]
    current_walls={k:v["wall_ms"] for k,v in episode["raw_repeat_samples"].items()}
    comparison={}
    for name in ("prior_012","prior_013","strong_classical"):
        prior_median=current[name]["wall_ms"]
        cand_median=current["candidate_014"]["wall_ms"]
        gain=(prior_median-cand_median)/prior_median
        wins=sum(x<y for x,y in zip(current_walls["candidate_014"],current_walls[name]))
        # 9 same-run index-aligned repeat samples are *not* 9 independent
        # research outcomes and not truly simultaneously paired timings.
        comparison[name]={
            "candidate_wall_median_ms":round(cand_median,6),
            "reference_wall_median_ms":round(prior_median,6),
            "candidate_cpu_median_ms":round(current["candidate_014"]["cpu_ms"],6),
            "reference_cpu_median_ms":round(current[name]["cpu_ms"],6),
            "relative_gain_wall":round(gain,7),
            "wins_out_of_9_index_aligned_samples":wins,
            "all_candidate_samples_faster_than_all_reference_samples":
                max(current_walls["candidate_014"])<min(current_walls[name]),
            "meets_8_percent_and_8_of_9_descriptive_gate":
                gain>=MIN_GAIN and wins>=8,
        }
    raw=previous["baseline_comparisons"]
    history={
        key:{
            "prior_014_median_gain":raw[key]["observed_median_relative_gain"],
            "new_016_median_gain":comparison[key]["relative_gain_wall"],
            "same_source_programs":True,
            "same_exact_graphs":False,
            "same_graph_generator_family":True,
            "separate_research_innovation_trials":False,
            "independent_external_test_authorship":False,
        } for key in ("prior_012","prior_013","strong_classical")
    }
    # Even if one fast microbenchmark passes, a promotion would require
    # independent task authorship, statistically credible resource gains,
    # actual proven full cost, and external human review.
    candidate_performance_gate=all(
        d["meets_8_percent_and_8_of_9_descriptive_gate"]
        for d in comparison.values())
    gate={
        "real_source_mathematically_checked":True,
        "same_source_real_code_measured_again":True,
        "old_014_formal_correctness_proved":True,
        "old_014_heldout_improvement_accepted":False,
        "new_016_candidate_meets_all_descriptive_thresholds":candidate_performance_gate,
        "independent_test_author":False,
        "external_custody_authentication":False,
        "observed_two_successive_promoted_improvements":False,
        "calibrated_probability_of_future_upgrade_success":False,
        "full_end_to_end_cost_amortization_demonstrated":False,
        "statistical_generalization_across_hardware":False,
        "production_promotion_allowed":False,
    }
    if gate["production_promotion_allowed"]:
        raise HOLD("Research-only task cannot grant production authority")
    return {
        "experiment":"MOTIF-LEGIT-016",
        "title":"THE_EMPIRICAL_COMPOUNDING_WITNESS",
        "real_014_retrospective":previous,
        "new_016_observed_episode":episode,
        "current_observations":comparison,
        "cross_trial_descriptive_comparisons":history,
        "promotion_gate":gate,
        "promotion_decision":"HOLD_NOT_ENOUGH_INDEPENDENT_EVIDENCE",
        "observed_compounding_rate":"NOT_ESTIMABLE",
        "hypothetical_015_growth_rate_not_used":True,
        "new_algorithm_source_generated":False,
        "research_only":True,
        "advice_for_next_trial":"REGISTER a previously unseen external problem suite and independent custodial provenance before evaluating; include code/discovery/proof/human-review costs, wall/CPU/memory, at least two machines and a strong matched classical portfolio. Do not infer success rates from researcher-chosen variants.",
        "real_world_authority":False,
    }

def prospective_record(record):
    """Fail-closed typed shape for future external study invitations.

    A textual assertion of independent authorship is NOT authentication.
    This function returns a document status, never a verified signature or
    an authorization to change code.
    """
    necessary={
        "candidate_sha256","reference_sha256","preregistered_plan_sha256",
        "research_cost_ms","proof_and_review_cost_ms","rollback_cost_ms",
        "workload_family","outcome","source_external_custody_verified",
        "raw_test_timings","source_generated_from_same_test_set"
    }
    if not isinstance(record,dict) or set(record)!=necessary:
        raise HOLD("Incomplete future episode source contract")
    hashes=[record[k] for k in ("candidate_sha256","reference_sha256",
                              "preregistered_plan_sha256")]
    if (any(type(x) is not str or len(x)!=64 or
            any(ch not in "0123456789abcdef" for ch in x) for x in hashes)
        or hashes[0]==hashes[1]):
        raise HOLD("Missing independently pinned source and baseline")
    for k in ("research_cost_ms","proof_and_review_cost_ms","rollback_cost_ms"):
        v=record[k]
        if type(v) not in (float,int) or not isfinite(v) or v<0:
            raise HOLD("Unbounded discovery or rollback cost")
    if record["outcome"] not in ("VERIFIED_GAIN","VERIFIED_NO_GAIN","REJECT_UNSOUND"):
        raise HOLD("Unknown externally witnessed outcome")
    if (type(record["workload_family"]) is not str or
        len(record["workload_family"])>60 or
        not record["workload_family"].replace("_","").isalnum()):
        raise HOLD("Invalid source-specific workload")
    times=record["raw_test_timings"]
    if (type(times) is not list or len(times)<3 or len(times)>100 or
        any(type(v) not in (float,int) or not isfinite(v) or v<=0 for v in times)):
        raise HOLD("Missing raw observations")
    if (type(record["source_external_custody_verified"]) is not bool or
        type(record["source_generated_from_same_test_set"]) is not bool):
        raise HOLD("Invalid provenance assertion")
    if record["source_external_custody_verified"] is True:
        # No independent signature/custody checker exists yet.
        # Even a forged true boolean must be HOLD.
        return {"status":"HOLD_UNVERIFIABLE_EXTERNAL_ATTESTATION",
                "automatically_calibrated":False,
                "algorithm_promoted":False}
    return {"status":"RECEIVED_UNVERIFIED_FOR_RESEARCH_ONLY",
            "automatically_calibrated":False,
            "algorithm_promoted":False}
