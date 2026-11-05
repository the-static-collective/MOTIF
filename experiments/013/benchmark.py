"""MOTIF-013 independent evaluator: calibrated uncertainty vs Bayesian controls.

Four known Boolean truth tables + catch-all .5 form the bounded model family.
Realized interventions, latent outcomes, source accuracy, compliance and
actual regime family are evaluator-only. Source-level calibration is supplied
as independent adjudicated aggregate counts; training labels remain hidden.

A strong, classical, nonparametric four-cell Bayesian baseline uses the EXACT
SAME training reports, calibration and actuator receipts. It updates a grid
posterior over each input's unknown success probability under Beta(2,2)
priors. Unlike the four-program ensemble, it does not assume .15/.85 effects.

Scoring uses actual stochastic Bernoulli test outcomes, Brier/log loss and
calibration bins; abstentions are separately disclosed. This is NOT a real
sensor validation or proof of better generalization.
"""
from __future__ import annotations

from collections import defaultdict,Counter
from math import log,exp,sqrt
from statistics import mean
import json

from oracle import (FAMILIES,SEEDS,PAIRS,ORIGINS,world,records,calibration,
                    oracle_plan_probability)
from witness_model import (HOLD,fit,predict,decision,confidence_intervals,
                           choose_question,event_predictive_log_ratio,
                           tree_cartridges,_independent_claims,
                           _mixture_likelihood)

VERSION="probabilistic-witness-v1"
TRAIN=80
VALIDATION=32
TEST=120
GRID=121
PROBABILITY_FLOOR=1e-9


def bayesian_four_cell(training,learned_fit):
    """Classical independent-cell Bayes with a numerical probability grid.

    Audited applied settings are essential. Unknown actual intervention
    settings remain HELD from this inference, exactly as for the structural
    ensemble. Source reliabilities are plug-in Beta posterior means in BOTH.
    """
    r=learned_fit.origins()
    bins={pair:[] for pair in PAIRS}
    for row in training:
        claims,_=_independent_claims(row,r)
        if row.audited_applied is None or not claims:
            continue
        bins[row.audited_applied].append(claims)
    means={}
    for pair in PAIRS:
        points=[(i+.5)/GRID for i in range(GRID)]
        # Beta(2,2) density is proportional to p*(1-p).
        logweights=[log(p)+log(1-p) for p in points]
        for observed in bins[pair]:
            logweights=[v+log(max(_mixture_likelihood(
                observed,r,p),1e-300)) for v,p in zip(logweights,points)]
        mx=max(logweights)
        weights=[exp(v-mx) for v in logweights]
        means[pair]=sum(p*w for p,w in zip(points,weights))/sum(weights)
    return means


def four_cell_forecast(means,learned_fit,command):
    compliance=learned_fit.compliance_means()
    total=0.0
    for actual in PAIRS:
        probability=1.0
        for i in (0,1):
            probability*=compliance[i] if command[i]==actual[i] else (
                1-compliance[i])
        total+=probability*means[actual]
    return total


def naive_unweighted(training,command):
    """A deliberately WEAK diagnostic, not our statistical comparator.

    Treats all unique origin reports as equally credible and issued commands
    as if applied; included to quantify the harm of uncalibrated witnesses.
    """
    observations=[]
    for case in training:
        if case.commanded!=command:
            continue
        seen={}
        for report in case.witnesses:
            seen[report.origin]=report.claim
        observations.extend(seen.values())
    return (sum(observations)+2)/(len(observations)+4)


def brier(y,p):
    return (p-int(y))**2


def logloss(y,p):
    p=min(max(p,PROBABILITY_FLOOR),1-PROBABILITY_FLOOR)
    return -log(p if y else (1-p))


def calibration_summary(outcomes,probs):
    # Equal-frequency bins are not used. The fixed bin boundaries were
    # declared in this code, not selected on heldout outcomes.
    bins=[]
    for i in range(5):
        rows=[(y,p) for y,p in zip(outcomes,probs)
              if (i/5<=p< (i+1)/5 or (i==4 and p==1.0))]
        if rows:
            bins.append({
                "range":f"{i/5:.1f}-{(i+1)/5:.1f}",
                "n":len(rows),
                "mean_forecast":round(mean(p for _,p in rows),5),
                "event_frequency":round(mean(y for y,_ in rows),5)
            })
    ece=sum(x["n"]*abs(x["mean_forecast"]-x["event_frequency"])
            for x in bins)/max(len(outcomes),1)
    return {"bins":bins,"ece":round(ece,5)}


def evaluate(family,seed,*,include_details=False):
    spec=world(family,seed)
    calibration_data=calibration(spec)
    train=records(spec,"train",TRAIN)
    validation=records(spec,"validation",VALIDATION)
    test=records(spec,"test",TEST)
    # A hard source boundary: only the public, unadjudicated projection enters
    # inference. The latent y is available to the evaluator only at scoring.
    public_train=tuple(x.public for x in train)
    public_validation=tuple(x.public for x in validation)
    fitted=fit(calibration_data,public_train)
    shift=event_predictive_log_ratio(fitted,public_validation)
    baseline=bayesian_four_cell(public_train,fitted)
    beliefs=fitted.masses()
    forecast=[predict(fitted,x.public.commanded) for x in test]
    grid=[four_cell_forecast(baseline,fitted,x.public.commanded) for x in test]
    naive=[naive_unweighted(public_train,x.public.commanded) for x in test]
    oracle=[oracle_plan_probability(spec,x.public.commanded,"test")
            for x in test]
    truth=[int(x.truth) for x in test]
    flags=[decision(fitted,x.public.commanded,
                    validation_flag=shift["shift_warning"])["status"]
           for x in test]
    issued=sum(f=="PREDICT_PROBABILITY_ONLY" for f in flags)
    errors=sum((p>=.5)!=bool(y) for p,y,f in zip(forecast,truth,flags)
               if f=="PREDICT_PROBABILITY_ONLY")
    result={
        "family":family,"seed":seed,
        "source_reliabilities_true_evaluator_only":
            [round(x,4) for x in spec.source_accuracies],
        "source_reliabilities_estimated":
            {key:round(value,4) for key,value in fitted.origins().items()},
        "actuation_compliance_true_evaluator_only":
            [round(x,4) for x in spec.compliance],
        "actuation_compliance_estimated":
            {str(key):round(value,4)
             for key,value in fitted.compliance_means().items()},
        "training_tickets":len(train),
        "training_usable_with_audited_applied_and_witness":
            fitted.admissible_records,
        "training_held_without_audited_intervention":
            fitted.unverifiable_actuation,
        "training_held_without_any_witness":
            fitted.missing_witnesses,
        "raw_witness_claims":fitted.witness_claims,
        "independent_witness_origins":fitted.independent_origins,
        "forwarded_duplicate_reports_not_double_counted":
            fitted.duplicate_forwarded_claims,
        "calibration_source_samples":fitted.source_calibration_samples,
        "calibration_actuator_samples":fitted.applied_calibration_samples,
        "training_posterior":{key:round(value,7)
                              for key,value in beliefs.items()},
        "validation_drift_warning":shift,
        "heldout_trials":len(test),
        "internal_forecast_brier":round(mean(
            brier(y,p) for y,p in zip(truth,forecast)),6),
        "classical_bayesian_four_cell_brier":round(mean(
            brier(y,p) for y,p in zip(truth,grid)),6),
        "weak_source_blind_brier":round(mean(
            brier(y,p) for y,p in zip(truth,naive)),6),
        "oracle_unattainable_brier":round(mean(
            brier(y,p) for y,p in zip(truth,oracle)),6),
        "internal_forecast_logloss":round(mean(
            logloss(y,p) for y,p in zip(truth,forecast)),6),
        "classical_bayesian_four_cell_logloss":round(mean(
            logloss(y,p) for y,p in zip(truth,grid)),6),
        "heldout_brier_calibration":calibration_summary(truth,forecast),
        "issued_prediction_coverage":round(issued/len(test),4),
        "issued_thresholded_errors":errors,
        "issued_status_counts":dict(sorted(Counter(flags).items())),
        "other_posterior":round(beliefs["OTHER"],6),
        "external_actions":0,
    }
    if include_details:
        result["per_trial_scoring"]=[
            {"ticket":test[i].public.ticket,
             "command":list(test[i].public.commanded),
             "outcome_hidden_until_evaluator_scoring":False,
             "truth_at_evaluation_only":bool(truth[i]),
             "internal_pred":round(forecast[i],6),
             "bayesian_cell_pred":round(grid[i],6),
             "oracle_plan_pred":round(oracle[i],6),
             "issued_status":flags[i]}
            for i in range(TEST)]
        result["example_interval_model_and_compliance_only"]=list(
            confidence_intervals(fitted,(False,True),
                                 seed=1000+seed,draws=600))
        result["sample_next_question"]=choose_question(fitted)
    return result


def aggregate(rows):
    model=[x["internal_forecast_brier"] for x in rows]
    cell=[x["classical_bayesian_four_cell_brier"] for x in rows]
    oracle=[x["oracle_unattainable_brier"] for x in rows]
    total=sum(x["heldout_trials"] for x in rows)
    counts={}
    for family in FAMILIES:
        part=[x for x in rows if x["family"]==family]
        counts[family]={
            "worlds":len(part),
            "internal_brier":round(mean(x["internal_forecast_brier"]
                                         for x in part),6),
            "classical_bayesian_four_cell_brier":round(mean(
                x["classical_bayesian_four_cell_brier"] for x in part),6),
            "mean_other_posterior":round(mean(
                x["other_posterior"] for x in part),5),
            "validation_shift_flags":sum(
                x["validation_drift_warning"]["shift_warning"] for x in part),
            "issued_coverage":round(mean(
                x["issued_prediction_coverage"] for x in part),4),
            "issued_errors":sum(x["issued_thresholded_errors"] for x in part)
        }
    return {
        "version":VERSION,
        "scope":"PSEUDORANDOM_SYNTHETIC_UNCERTAINTY",
        "worlds":len(rows),
        "families":list(FAMILIES),
        "seeds":list(SEEDS),
        "heldout_trial_total":total,
        "training_each":TRAIN,
        "validation_each":VALIDATION,
        "test_each":TEST,
        "calibration_samples_per_source":60,
        "calibration_samples_per_actuator":80,
        "independent_source_groups":3,
        "heldout_truth_exposed_to_learner":False,
        "training_truth_exposed_to_learner":False,
        "oracle_module_imported_by_learner":False,
        "model_is_approximate_plug_in_bayesian":True,
        "comparison_classical_bayesian_independent_cells":True,
        "other_model_is_constant_half_not_causal_explanation":True,
        "mean_internal_brier":round(mean(model),6),
        "mean_classical_bayesian_four_cell_brier":round(mean(cell),6),
        "mean_weak_unweighted_brier":round(mean(
            x["weak_source_blind_brier"] for x in rows),6),
        "mean_oracle_unattainable_brier":round(mean(oracle),6),
        "mean_internal_logloss":round(mean(
            x["internal_forecast_logloss"] for x in rows),6),
        "mean_bayesian_four_cell_logloss":round(mean(
            x["classical_bayesian_four_cell_logloss"] for x in rows),6),
        "sum_deduplicated_forwarded_claims":sum(
            x["forwarded_duplicate_reports_not_double_counted"] for x in rows),
        "sum_held_unverified_controls":sum(
            x["training_held_without_audited_intervention"] for x in rows),
        "overall_prediction_issued_coverage":round(sum(
            x["issued_prediction_coverage"] for x in rows)/len(rows),4),
        "overall_issued_errors":sum(x["issued_thresholded_errors"]
                                    for x in rows),
        "per_family":counts,
        "external_actions":0,
    }


def benchmark():
    rows=[evaluate(family,seed) for family in FAMILIES for seed in SEEDS]
    return {"experiment":"MOTIF-013",
            "summary":aggregate(rows),
            "worlds":rows}


if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
