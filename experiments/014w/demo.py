"""MOTIF-014 concrete 'witness of witnesses' cartridge and honest failures.

The artifact is generated from the same independently seeded stochastic
simulator and exact finite-grid Bayesian code as the full 28-world benchmark.
Model code receives only public reports, fallible meta-report and commands.
"""
from __future__ import annotations
import json

import oracle
import benchmark   # EVALUATOR only
import joint


def demonstrate():
    specimens={
        "supported_known_mechanism":("FIRST",11),
        "unknown_rule_abstained":("XOR",37),
        "source_drift_caught":("SOURCE_SHIFT",11),
        "source_drift_missed":("SOURCE_SHIFT",23),
        "auditor_drift_caught":("AUDIT_SHIFT",11),
        "auditor_drift_missed":("AUDIT_SHIFT",23),
        "actuator_drift_missed":("COMPLIANCE_SHIFT",41),
    }
    cases={}
    for key,(family,seed) in specimens.items():
        row=benchmark.evaluate(family,seed,
                               details=key=="supported_known_mechanism")
        # No full hidden parameter table is put into the user-visible
        # cartridge, except the explicit evaluator-only comparison summary.
        cases[key]={
            "family_is_evaluator_only":family,
            "seed":seed,
            "credible_truthfulness_parameters":{
                p:{"posterior_mean":row[
                    "motif_joint_parameter_posterior_means"][p],
                   "finite_grid_90pct_interval":row[
                    "motif_credible_intervals_90"][p]}
                for p in ("r0","r1","q","c")},
            "evaluator_only_hidden_true_training_parameters":
                row["hidden_training_parameters_for_evaluator_only"],
            "posterior_model_weights":
                row["posteriors_over_causal_models"],
            "validation_signaled_possible_shift":
                row["validation_heldout_report_diagnostic"],
            "issue_decisions":row["issue_statuses"],
            "heldout_brier_motif":row["score_motif_brier"],
            "heldout_brier_classical_full_boolean":
                row["score_classical_full_grammar_brier"],
            "evidence_provenance":{
                "duplicate_forwarded_reports":row[
                    "witness_forwarded_copies_counted_once"],
                "missing_meta_actuation_reports_marginalized":row[
                    "missing_fallible_control_receipts_integrated_not_discarded"],
                "training_intervention_events_used":row[
                    "training_events_used_in_joint_update"]},
        }
        if key=="supported_known_mechanism":
            cases[key]["actual_synthetic_witness_receipt"]=row[
                "sample_trial_receipt"]
            cases[key]["proposed_009_tree_cartridge_ensemble"]=row["ensemble"]
            cases[key]["next_joint_information_question"] = row[
                "sample_question_proposal"]
            cases[key]["calibration_only_question_policy"]=row[
                "sample_calibration_only_policy"]
            cases[key]["unsafe_question_refusal"]=row[
                "sample_forbidden_question"]
            cases[key]["unfunded_question_refusal"]=row[
                "sample_unaffordable_question"]
            cases[key]["evaluator_only_heldout_probability_then_truth"]=row[
                "heldout_example_scored_only_after_forecast"]
    source=cases["supported_known_mechanism"]
    assert source["unsafe_question_refusal"]["status"]=="HOLD_UNSAFE"
    assert source["unfunded_question_refusal"]["status"]=="HOLD_BUDGET"
    assert cases["source_drift_caught"]["validation_signaled_possible_shift"]["warning"]
    assert not cases["source_drift_missed"]["validation_signaled_possible_shift"]["warning"]
    assert cases["auditor_drift_caught"]["validation_signaled_possible_shift"]["warning"]
    assert not cases["auditor_drift_missed"]["validation_signaled_possible_shift"]["warning"]
    return {
        "experiment":"MOTIF-014",
        "scope":"SYNTHETIC_FALLIBLE_META_TESTIMONY",
        "claim":"uncertain witnesses' reliability is itself uncertain, not proven ground truth",
        "joint_parameter_model":"EXACT_BAYES_ON_HANDCRAFTED_FINITE_GRID",
        "cases":cases,
        "calibration_adjudicator_not_infallible":True,
        "source_identity_and_custody_not_authenticatable":True,
        "joint_model_does_not_guarantee_drift_detection":True,
        "stronger_classical_full_boolean_comparator_included":True,
        "external_actions":0,
    }


if __name__=="__main__":
    print(json.dumps(demonstrate(),indent=2,sort_keys=True))
