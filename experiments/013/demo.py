"""MOTIF-013: one tangible, fully reproducible probabilistic witness dossier.

Reveals synthetic evaluator truths ONLY after predictions are recorded.
Includes successful calibration, uncertain/unsupported mechanism abstentions,
and explicit false negatives—because noise and drift are genuinely difficult.
"""
from __future__ import annotations
import json

import oracle  # EVALUATOR ONLY
import benchmark  # Resolve local module before 009 changes sys.path.
from witness_model import (fit,predict,decision,confidence_intervals,
                           source_reliability_intervals,choose_question,
                           event_predictive_log_ratio,tree_cartridges)


def case_report(family,seed,include_tree=False):
    world=oracle.world(family,seed)
    audit=oracle.calibration(world)
    source=oracle.records(world,"train",benchmark.TRAIN)
    public=tuple(x.public for x in source)
    frozen=tuple(x.before for x in public)
    estimate=fit(audit,public)
    evidence=oracle.records(world,"validation",benchmark.VALIDATION)
    check=event_predictive_log_ratio(estimate,tuple(x.public for x in evidence))
    command=(False,True)
    predicted=decision(estimate,command,check["shift_warning"])
    test=oracle.trial(world,"test",17,command=command)
    # The learner never receives either truth or realized applied settings.
    predicted_before_truth_reveal=predict(estimate,command)
    interesting=next((x for x in public if len(
        {r.claim for r in x.witnesses if r.reporter!="source_0_forwarded"})>1
        and any(r.reporter=="source_0_forwarded" for r in x.witnesses)),None)
    if interesting is None:
        interesting=next((x for x in public if x.witnesses),public[0])
    visible={
        "ticket":interesting.ticket,
        "command":list(interesting.commanded),
        "audited_applied":list(interesting.audited_applied)
                          if interesting.audited_applied is not None else None,
        "reported_claims":[{
            "upstream_origin":x.origin,
            "reporter":x.reporter,
            "reported_success":x.claim}
            for x in interesting.witnesses],
        "separately_verified_true_outcome_supplied_to_learner":False,
    }
    output={
        "family_in_evaluator_only":family,
        "seed":seed,
        "source_beta_posteriors_90pct":source_reliability_intervals(
            estimate,seed=seed,draws=800),
        "compliance_beta_posterior_means":{
            str(k):round(v,5) for k,v in estimate.compliance_means().items()},
        "training_after_provenance_checks":{
            "used":estimate.admissible_records,
            "held_without_verified_controls":estimate.unverifiable_actuation,
            "held_without_outcome_witness":estimate.missing_witnesses,
            "independent_claims":estimate.independent_origins,
            "forwarded_copies_not_double_counted":
                estimate.duplicate_forwarded_claims},
        "example_disagreeing_witnesses":visible,
        "posterior_hypothesis_weights":{
            m:round(v,8) for m,v in estimate.posterior},
        "validation_shift_diagnostic":check,
        "next_command_probability_and_release_decision":predicted,
        "conditional_model_compliance_interval_90pct":list(
            confidence_intervals(estimate,command,seed=seed+33,draws=800)),
        "heldout_trial_scored_only_in_evaluator":{
            "ticket":test.public.ticket,
            "command":list(command),
            "prediction_frozen_before_truth_reveal":
                round(predicted_before_truth_reveal,6),
            "truth_revealed_after_evaluator_scoring":test.truth,
            "realized_setting_revealed_only_in_evaluator":
                list(test.realized),
            "was_admitted_to_issue_prediction":
                predicted["status"]=="PREDICT_PROBABILITY_ONLY"},
        "test_measured_brier":benchmark.evaluate(family,seed)[
            "internal_forecast_brier"],
        "test_classical_bayesian_cell_brier":benchmark.evaluate(family,seed)[
            "classical_bayesian_four_cell_brier"],
        "original_before_graphs_unchanged":
            frozen==tuple(x.before for x in public),
        "real_world_authority":False,
    }
    if include_tree:
        output["portable_uncertain_tree_cartridge_ensemble"] = tree_cartridges(
            estimate,public,world.control_predicates)
        output["bounded_next_synthetic_question"]=choose_question(
            estimate,budget=2)
    return output


def demonstration():
    cases={
        "known_in_grammar":"FIRST",
        "unsupported_rule_recognized":"XOR",
        "unsupported_rule_not_recognized":"XOR",
        "shift_recognized":"SHIFT",
        "shift_not_recognized":"SHIFT",
    }
    settings={
        "known_in_grammar":("FIRST",11,True),
        "unsupported_rule_recognized":("XOR",23,False),
        "unsupported_rule_not_recognized":("XOR",41,False),
        "shift_recognized":("SHIFT",23,False),
        "shift_not_recognized":("SHIFT",11,False),
    }
    samples={key:case_report(*params) for key,params in settings.items()}
    assert samples["unsupported_rule_recognized"][
        "next_command_probability_and_release_decision"]["status"]!=(
            "PREDICT_PROBABILITY_ONLY")
    assert samples["unsupported_rule_not_recognized"][
        "next_command_probability_and_release_decision"]["status"]==(
            "PREDICT_PROBABILITY_ONLY")
    assert samples["shift_recognized"][
        "next_command_probability_and_release_decision"]["status"]==(
            "HOLD_PREDICTIVE_SHIFT")
    assert samples["shift_not_recognized"][
        "next_command_probability_and_release_decision"]["status"]==(
            "PREDICT_PROBABILITY_ONLY")
    calibration_data=oracle.calibration(oracle.world("FIRST",11))
    prior=fit(calibration_data,())
    return {
        "experiment":"MOTIF-013",
        "artifact":"UNCERTAIN_WITNESS_AND_PROBABILISTIC_TREE_CARTRIDGES",
        "examples":samples,
        "synthetic_information_budget_examples":{
            "available":choose_question(prior,budget=1),
            "prohibited":choose_question(prior,allowed=(),budget=1),
            "unaffordable":choose_question(
                prior,budget=1,costs={key:5 for key in oracle.PAIRS}),
        },
        "known_failure_modes_present":True,
        "bayesian_comparison_can_outperform_motif":True,
        "calibration_is_synthetic_not_verified_human_evidence":True,
        "network_calls_or_real_actions":0,
    }


if __name__=="__main__":
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
