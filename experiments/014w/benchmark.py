"""MOTIF-014 matched joint Bayesian benchmark.

The learner receives PUBLIC projections only. The evaluator retains true
outcomes, realized actuations, source reliabilities, audit correctness and
program labels for *post-hoc* scoring.

Compared on identical calibration and interventions:
  (1) MOTIF: exact grid joint Bayesian inference over 4 009-tree templates + OTHER
  (2) CLASSICAL: same exact grid joint Bayesian latent-source model but with
      all 16 Boolean decision tables + OTHER. This is a stronger general
      grammar, not a simplistic random/majority strawman.
  (3) Privileged true-environment oracle, scorer only, not attainable.
All predictions scored, INCLUDING when the release gate abstains.
"""
from __future__ import annotations

from collections import Counter
from statistics import mean
from math import log
import json

from oracle import (FAMILIES,SEEDS,PORTS,create_world,calibration_set,
                    trial_set,true_command_probability)
from joint import (fit,decide,validation_diagnostic,propose_inquiry,
                   cartridge_ensemble)

VERSION="motif-014-joint-credibility-v1"
CALIBRATION=40
TRAIN=48
VALIDATION=24
TEST=96


def brier(truth,probability):
    return (int(truth)-probability)**2


def logloss(truth,probability):
    p=min(max(probability,1e-9),1-1e-9)
    return -log(p if truth else 1-p)


def fixed_calibration_bins(true_labels,predictions):
    bins=[]
    for index in range(5):
        vals=[(truth,p) for truth,p in zip(true_labels,predictions)
              if .2*index<=p<.2*(index+1) or
              (index==4 and p==1.0)]
        if vals:
            bins.append({
                "lower":round(.2*index,2),"upper":round(.2*(index+1),2),
                "n":len(vals),
                "mean_predicted":round(mean(p for _,p in vals),5),
                "observed_frequency":round(mean(int(y) for y,_ in vals),5)})
    ece=sum(x["n"]*abs(x["mean_predicted"]-x["observed_frequency"])
            for x in bins)/len(true_labels)
    return {"bins":bins,"empirical_calibration_error":round(ece,5)}


def evaluate(family,seed,details=False):
    spec=create_world(family,seed)
    cal=calibration_set(spec,CALIBRATION)
    train=trial_set(spec,"train",TRAIN)
    validation=trial_set(spec,"validation",VALIDATION)
    test=trial_set(spec,"test",TEST)
    # Explicit private/public separation:
    # NO SecretCalibration, SecretTrial or World is passed into joint.fit.
    public_cal=tuple(x.public for x in cal)
    public_train=tuple(x.public for x in train)
    public_validation=tuple(x.public for x in validation)
    controls=spec.predicate_names  # purely public ontology names
    motif=fit(public_cal,public_train,controls,"motif")
    classical=fit(public_cal,public_train,controls,"all_boolean")
    drift=validation_diagnostic(motif,public_validation,controls)
    drift_classical=validation_diagnostic(classical,public_validation,controls)

    # The simulator true outcome is exposed to the EVALUATOR only after every
    # command-based probability has been frozen below.
    commands=tuple(x.public.requested for x in test)
    unique=sorted(set(commands))
    ours={c:motif.forecast(c) for c in unique}
    baseline={c:classical.forecast(c) for c in unique}
    ideal={c:true_command_probability(spec,c,"test") for c in unique}
    decisions={c:decide(motif,c,drift["warning"]) for c in unique}
    truths=tuple(x.truth for x in test)
    pred=[ours[c] for c in commands]
    rival=[baseline[c] for c in commands]
    oracle=[ideal[c] for c in commands]
    statuses=[decisions[c]["status"] for c in commands]
    coverage=sum(s=="PREDICT_PROBABILITY_ONLY" for s in statuses)
    issued_wrong=sum((p>=.5)!=y for p,y,s in zip(pred,truths,statuses)
                     if s=="PREDICT_PROBABILITY_ONLY")
    params=motif.parameter_means()
    truth_params=dict(zip(("r0","r1","q","c"),
                          (*spec.source_truthfulness,
                           spec.auditor_truthfulness,
                           spec.actuator_compliance)))
    summary={
        "family_evaluator_only":family,"seed":seed,
        "source_samples":CALIBRATION,"training":TRAIN,
        "validation":VALIDATION,"heldout":TEST,
        "motif_credible_intervals_90":{
            n:[round(x,4) for x in motif.parameter_interval(n)]
            for n in ("r0","r1","q","c")},
        "motif_joint_parameter_posterior_means":{
            n:round(v,5) for n,v in params.items()},
        "hidden_training_parameters_for_evaluator_only":{
            n:round(v,5) for n,v in truth_params.items()},
        "posteriors_over_causal_models":{
            n:round(v,7) for n,v in motif.model_weights().items()},
        "classical_16_boolean_models_plus_other":len(
            classical.model_weights()),
        "motif_tree_models_plus_other":len(motif.model_weights()),
        "witness_forwarded_copies_counted_once":motif.forwarded_duplicates,
        "missing_fallible_control_receipts_integrated_not_discarded":
            motif.missing_audit_receipts,
        "training_trials_without_both_source_reports":motif.missing_reporters,
        "training_events_used_in_joint_update":motif.intervention_count,
        "validation_heldout_report_diagnostic":drift,
        "classical_validation_diagnostic":drift_classical,
        "score_motif_brier":round(mean(
            brier(y,p) for y,p in zip(truths,pred)),6),
        "score_classical_full_grammar_brier":round(mean(
            brier(y,p) for y,p in zip(truths,rival)),6),
        "score_privileged_true_world_oracle_brier":round(mean(
            brier(y,p) for y,p in zip(truths,oracle)),6),
        "score_motif_logloss":round(mean(
            logloss(y,p) for y,p in zip(truths,pred)),6),
        "score_classical_full_grammar_logloss":round(mean(
            logloss(y,p) for y,p in zip(truths,rival)),6),
        "score_motif_calibration":fixed_calibration_bins(truths,pred),
        "issued_prediction_coverage":round(coverage/TEST,5),
        "issued_prediction_count":coverage,
        "issued_thresholded_errors":issued_wrong,
        "issue_statuses":dict(sorted(Counter(statuses).items())),
        "stochastic_outcomes_belong_to_evaluator_only":True,
        "real_world_operations":0,
    }
    if details:
        summary["sample_question_proposal"]=propose_inquiry(motif)
        summary["sample_calibration_only_policy"]=propose_inquiry(
            motif,allowed=("CALIBRATION",),budget=1)
        summary["sample_forbidden_question"]=propose_inquiry(
            motif,allowed=(),budget=2)
        summary["sample_unaffordable_question"]=propose_inquiry(
            motif,budget=0)
        summary["sample_trial_receipt"]={
            "command":list(train[0].public.requested),
            "reported_audit_of_control":train[0].public.audit_says_first_port_applied,
            "upstream_reports":[{
                "origin":r.origin,
                "reporter":r.reporter,
                "says_success":r.says_success}
                for r in train[0].public.reporters],
            "hidden_truth_did_not_enter_inference":True,
            "evaluator_only_truth":train[0].truth,
            "evaluator_only_actually_applied":
                list(train[0].actually_applied),
        }
        summary["ensemble"]=cartridge_ensemble(motif,public_train,controls)
        summary["heldout_example_scored_only_after_forecast"]={
            "requested":list(test[0].public.requested),
            "motif_predicted_before_truth":round(pred[0],6),
            "classical_predicted_before_truth":round(rival[0],6),
            "evaluator_only_truth":test[0].truth,
            "evaluator_only_actual_controls":
                list(test[0].actually_applied),
        }
    return summary


def aggregate(rows):
    families={}
    for name in FAMILIES:
        subset=[row for row in rows if row["family_evaluator_only"]==name]
        families[name]={
            "worlds":len(subset),
            "mean_motif_brier":round(mean(x["score_motif_brier"] for x in subset),6),
            "mean_classical_brier":round(mean(x["score_classical_full_grammar_brier"]
                                               for x in subset),6),
            "mean_issued_coverage":round(mean(x["issued_prediction_coverage"]
                                               for x in subset),5),
            "validation_drift_flags":sum(
                x["validation_heldout_report_diagnostic"]["warning"]
                for x in subset),
            "mean_q_posterior":round(mean(
                x["motif_joint_parameter_posterior_means"]["q"] for x in subset),5),
        }
    return {
        "version":VERSION,
        "scope":"STOCHASTIC_SIMULATION_WITH_FALLIBLE_META_WITNESSES",
        "world_count":len(rows),
        "families":list(FAMILIES),
        "seeds":list(SEEDS),
        "source_calibration_each":CALIBRATION,
        "train_each":TRAIN,"validation_each":VALIDATION,
        "heldout_each":TEST,
        "total_heldout":len(rows)*TEST,
        "joint_grid_components_motif":5*4*4*4*3,
        "joint_grid_components_classical":17*4*4*4*3,
        "calibration_truth_exposed_to_learner":False,
        "test_outcome_truth_exposed_to_learner":False,
        "actuator_receipts_are_fallible_not_ground_truth":True,
        "auditor_quality_jointly_inferred_not_fixed":True,
        "model_is_classical_exact_finite_grid_joint_bayes":True,
        "classical_baseline_has_broader_grammar":True,
        "mean_motif_brier":round(mean(x["score_motif_brier"] for x in rows),6),
        "mean_classical_full_grammar_brier":round(mean(
            x["score_classical_full_grammar_brier"] for x in rows),6),
        "mean_privileged_oracle_brier":round(mean(
            x["score_privileged_true_world_oracle_brier"] for x in rows),6),
        "mean_motif_logloss":round(mean(x["score_motif_logloss"] for x in rows),6),
        "mean_classical_full_grammar_logloss":round(mean(
            x["score_classical_full_grammar_logloss"] for x in rows),6),
        "motif_minus_classical_brier":round(mean(
            x["score_motif_brier"]-x["score_classical_full_grammar_brier"]
            for x in rows),6),
        "total_forwarded_claims_deduplicated":sum(
            x["witness_forwarded_copies_counted_once"] for x in rows),
        "total_missing_fallible_control_receipts_integrated":sum(
            x["missing_fallible_control_receipts_integrated_not_discarded"]
            for x in rows),
        "mean_issued_coverage":round(mean(
            x["issued_prediction_coverage"] for x in rows),5),
        "issued_thresholded_errors":sum(
            x["issued_thresholded_errors"] for x in rows),
        "per_family":families,
        "external_actions":0,
    }


def benchmark():
    rows=[evaluate(family,seed) for family in FAMILIES for seed in SEEDS]
    return {"experiment":"MOTIF-014",
            "summary":aggregate(rows),
            "worlds":rows}


if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
