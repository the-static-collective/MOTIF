"""LEGIT-015 empirical boundary: consume the ACTUAL rejected LEGIT-014 trial.

An economically appealing compounding narrative must not retroactively
turn a Z3-correct but empirically unaccepted optimization into a positive
observed self-improvement. This reader verifies the saved frozen source,
performance trial, and retention record without inserting fabricated
success probabilities or compound returns.

The output is source-dependent provenance, not a claim about future gain.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"legit014"/"generated"

class HOLD(ValueError):pass

def evidence():
    report=json.loads((PARENT/"performance_trial_report.json").read_text(encoding="utf-8"))
    manifest=json.loads((PARENT/"candidate_manifest.json").read_text(encoding="utf-8"))
    source=(PARENT/"candidate_rewrite.py").read_bytes()
    source_digest=sha256(source).hexdigest()
    if (report.get("experiment")!="MOTIF-LEGIT-014"
        or report.get("status")!="HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT"
        or report.get("internal_retain_gate_passed") is not False
        or report.get("automatic_merge_or_deploy") is not False
        or report.get("frozen_selected_source_sha256")!=source_digest
        or manifest.get("generated_source_sha256")!=source_digest
        or manifest.get("heldout_passed_internal_speed_gate") is not False
        or manifest.get("automatic_promotion_permitted") is not False
        or report.get("heldout_incorrect_outputs")!=0
        or report.get("full_partial_truth_lattice_checked")!=6561):
        raise HOLD("Actual prior experiment is inconsistent or no longer rejected")
    if (report.get("frozen_selected_plan")!=manifest.get("source_plan")
        or report.get("gate",{}).get("at_least_8_percent_faster_vs_prior") is not False
        or report.get("gate",{}).get("at_least_8_percent_faster_vs_earlier_012") is not False):
        raise HOLD("Disagreement with prior empirical retention gate")
    return {
        "source":"ACTUAL_COMMITTED_LEGIT014_FROZEN_TRIAL",
        "experiment":"MOTIF-LEGIT-014",
        "selected_source_sha256":source_digest,
        "observed_status":report["status"],
        "correctness_verified_for_prior_finite_scope":True,
        "actual_retention_gate_passed":False,
        "permitted_to_count_as_real_compounding_return":False,
        "future_gain_probability_calibrated_from_this_result":False,
        "independently_authored_heldout_evaluation":False,
        "measured_fraction_vs_prior_013":report["speedup_vs_prior_013_median_fraction"],
        "measured_fraction_vs_earlier_012":report["speedup_vs_earlier_012_median_fraction"],
        "observed_profile_cost_ms":report["training_profile_cost_ms"],
        "observed_total_candidate_proof_compile_cost_ms":
            report["candidate_formal_verification_and_compile_cost_ms"],
        "measured_setup_costs_are_not_per_future_upgrade":True,
        "explanation":"LEGIT-014 was correct but not a demonstrated improvement; every LEGIT-015 gain and probability is a visibly hypothetical scenario assumption.",
    }
