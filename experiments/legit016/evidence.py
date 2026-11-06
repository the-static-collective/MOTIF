"""LEGIT-016: immutable, inspectable evidence for real attempted improvements.

This is a retrospective record of ONE assistant-authored research episode,
not a sample of independent innovations. Eleven repeated timings of one
winner do NOT constitute eleven independent improvement attempts, nor do
nine formally correct trial programs estimate future discovery probability.

Never conflate Z3 proof of semantic equivalence with proven runtime gain.
The actual LEGIT-014 status is HOLD. Source IDs here are integrity checks
against the committed archive, not authenticating third parties.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from math import isfinite
from statistics import median
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TRIAL=ROOT/"legit014"/"generated"
ECONOMY=ROOT/"legit015"/"generated"/"economy_trial_report.json"
SOURCE_ID="LEGIT014_FROZEN_WINNER"
BASELINES=("prior_012","prior_013","strong_classical")

class HOLD(ValueError): pass

def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def _samples(arm):
    if (not isinstance(arm,dict) or
        set(arm)!={"median_ms","min_ms","max_ms","samples_ms"} or
        not isinstance(arm["samples_ms"],list) or
        len(arm["samples_ms"])!=11):
        raise HOLD("Incomplete frozen measured source")
    values=arm["samples_ms"]
    if any(type(v) not in (int,float) or not isfinite(v) or v<=0
           for v in values):
        raise HOLD("Invalid, unbounded or fabricated performance unit")
    if (abs(median(values)-arm["median_ms"])>1e-5 or
        abs(min(values)-arm["min_ms"])>1e-5 or
        abs(max(values)-arm["max_ms"])>1e-5):
        raise HOLD("Frozen reported timing statistics disagree with raw samples")
    return values

def archive():
    report=_read(TRIAL/"performance_trial_report.json")
    manifest=_read(TRIAL/"candidate_manifest.json")
    code=(TRIAL/"candidate_rewrite.py").read_bytes()
    sha=sha256(code).hexdigest()
    economic=_read(ECONOMY)
    if (report.get("experiment")!="MOTIF-LEGIT-014" or
        report.get("frozen_selected_source_sha256")!=sha or
        manifest.get("generated_source_sha256")!=sha or
        report.get("frozen_selected_plan")!=manifest.get("source_plan") or
        report.get("status")!="HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT" or
        manifest.get("heldout_status")!=report.get("status") or
        report.get("internal_retain_gate_passed") is not False or
        manifest.get("heldout_passed_internal_speed_gate") is not False or
        manifest.get("automatic_promotion_permitted") is not False or
        report.get("heldout_incorrect_outputs")!=0 or
        report.get("full_partial_truth_lattice_checked")!=6561 or
        report.get("heldout_graphs")!=80 or
        report.get("selection_used_holdout_data") is not False or
        report.get("independently_authored_external_challenge") is not False or
        economic.get("real_prior_trial_boundary",{}).get(
            "selected_source_sha256")!=sha or
        economic.get("scenario_assumptions")!="SYNTHETIC_NOT_CALIBRATED_FROM_LEGIT014"):
        raise HOLD("Prior empirical result is stale, modified, not held out, or falsely promoted")
    arms=report.get("heldout_repeated_ms")
    if not isinstance(arms,dict) or set(arms)!=set(BASELINES)|{"candidate"}:
        raise HOLD("Absent real comparison arm")
    observations={k:_samples(v) for k,v in arms.items()}
    reviews=report.get("training_reviews")
    if not isinstance(reviews,list) or len(reviews)!=report.get("proposed_candidate_count"):
        raise HOLD("Incomplete trial selection evidence")
    winners=[x for x in reviews if x.get("status")=="TRAINING_FROZEN_WINNER"]
    rejected=[x for x in reviews if x.get("status")=="REJECT_INCORRECT_OR_UNPROVED"]
    proven=[x for x in reviews if x.get("finite_proof",{}).get("states")==6561]
    if (len(winners)!=1 or winners[0].get("plan")!=report["frozen_selected_plan"]
        or len(rejected)!=1 or len(proven)!=report["formally_proved_candidate_count"]
        or report["formally_proved_candidate_count"]!=9 or
        rejected[0].get("round")!="ROUND_ONE_INJECTED_UNSOUND_FALSIFIER"
        or not rejected[0].get("error_detail","").startswith("SMT_SAT_COUNTEREXAMPLE:")):
        raise HOLD("Mistakenly counting artificial falsifiers as empirical improvement odds")
    return {
        "source_id":SOURCE_ID,
        "source_sha256":sha,
        "prior_status":report["status"],
        "heldout_graphs":report["heldout_graphs"],
        "heldout_states":report["heldout_states"],
        "all_outputs_correct_in_old_finite_domain":True,
        "raw_ms":observations,
        "recorded_median_ms":{k:arms[k]["median_ms"] for k in arms},
        "recorded_wins_out_of_11":report["wins_out_of_11_repeats"],
        "setup_ms":{
            "research_profile":report["training_profile_cost_ms"],
            "all_attempts_formal_proof_and_compilation":
                report["candidate_formal_verification_and_compile_cost_ms"],
        },
        "candidate_count":len(reviews),
        "proven_candidate_count":len(proven),
        "injected_unsound_negative_controls":len(rejected),
        "independent_trial_count":0,
        "research_project_episode_count":1,
        "heldout_from_different_seeds_not_different_authors":True,
        "future_success_probability_identifiable":False,
        "actual_compound_reinvestment_measured":False,
        "real_third_party_challenge_authorship":False,
        "prior_014_source":"experiments/legit014/generated/performance_trial_report.json",
        "prior_014_manifest":"experiments/legit014/generated/candidate_manifest.json",
        "prior_015_model":"experiments/legit015/generated/economy_trial_report.json",
        "real_world_authority":False,
    }

def summarize(prior=None):
    doc=archive() if prior is None else prior
    candidate=doc["raw_ms"]["candidate"]
    med=median(candidate)
    total_setup=sum(doc["setup_ms"].values())
    comparisons={}
    for key in BASELINES:
        b=doc["raw_ms"][key]
        base=median(b)
        saved=base-med
        # Index-aligned samples are NOT independent matched pairs: timing
        # order rotated; counts are descriptive, not a confidence interval.
        wins=sum(x<y for x,y in zip(candidate,b))
        req=None if saved<=0 else int(total_setup//saved)+1
        comparisons[key]={
            "candidate_median_ms":round(med,6),
            "baseline_median_ms":round(base,6),
            "observed_median_ms_saved_per_80_graph_batch":round(saved,6),
            "observed_median_relative_gain":round(saved/base,7),
            "index_aligned_sample_wins_out_of_11":wins,
            "all_candidate_samples_ms_range":[min(candidate),max(candidate)],
            "all_baseline_samples_ms_range":[min(b),max(b)],
            "exploratory_full_cost_break_even_batches":req,
            "break_even_interpretation":"Illustrative only; entire recorded discovery/proof setup cost is treated as attributable to this selected candidate, with an unchanged future workload and identical marginal cost.",
        }
        if wins!=doc["recorded_wins_out_of_11"][key]:
            raise HOLD("Descriptive sample win count does not match archived evidence")
    return {
        "experiment":"MOTIF-LEGIT-016",
        "source":"ACTUAL_FROZEN_LEGIT014",
        "source_sha256":doc["source_sha256"],
        "retrospective_status":doc["prior_status"],
        "baseline_comparisons":comparisons,
        "discovery_and_verification_setup_ms":total_setup,
        "previous_trial_counting":"10 attempted source plans; 9 formally proved, 1 deliberately injected unsound falsifier; NOT 10 independent innovation trials.",
        "independent_research_success_trials":0,
        "posterior_success_probability":"UNIDENTIFIABLE",
        "estimated_compounding_factor":"UNIDENTIFIABLE",
        "has_observed_successive_approved_improvements":False,
        "no_claim_of_general_superiority":True,
        "read_only":True,
    }
