"""RING-015 calibration: actual Docker source test evidence, no heldout labels.

The action model is FIT only from 12 authored training source copies. Six
distinct development copies select among 18 value settings × 2 decision
modes, with proper source receipts. Model selection uses seeded defect labels
ONLY as controlled experimental rewards, not as a selector input.

All result PASS/FAIL and wall seconds derive from actual source test runs,
not fake simulations. The only invented part is author-valued benefit of
detecting a synthetic defect and cost of spending test time.
"""
from __future__ import annotations
import argparse
from itertools import product
import json
from pathlib import Path
import tempfile

import fixtures,policy,runner

SCHEMA="motif.ring015.frozen-observation-conditioned-test-policy.v1"
REWARD_SCHEMA="motif.ring015.authored-detection-vs-time-utility.v1"


def digest(x):
    from hashlib import sha256
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
                              allow_nan=False).encode()).hexdigest()


def measured_matrix(root,repo,specs):
    records=fixtures.make(root,repo,specs)
    for row in records:
        row["tests"]={
            stage:runner.observe(root,row["case_id"],stage,repo)
            for stage in runner.PHASES}
    return records


def simulate_from_existing(case,estimate,settings,*,force_triage):
    # Replays only prior TRAIN or DEV real returns. The callback sees
    # the source-owned receipts but never the hidden defect label.
    tests=case["tests"]
    return policy.route(
        estimate,settings,
        lambda phase:tests[phase],
        force_triage=force_triage)


def authored_utility(case,outcome,settings):
    seeded=case["seeded_defect"]
    failed=outcome["saw_actual_failure"]
    reward=(
        settings["detection_benefit"] if seeded and failed else
        -1.25*settings["detection_benefit"] if seeded and not failed else
        -settings["false_alarm_penalty"] if not seeded and failed else
        2.0)
    return round(
        reward-settings["time_weight"]*outcome["actual_test_seconds"],6)


def score(cases,estimate,settings,*,force_triage):
    receipts=[]
    for case in cases:
        result=simulate_from_existing(case,estimate,settings,
                                      force_triage=force_triage)
        receipts.append({
            "case":case["case_id"],
            "mutated":case["seeded_defect"],
            "real_actions":[x["phase"] for x in result["receipts"]],
            "detected":result["saw_actual_failure"],
            "actual_cost_seconds":result["actual_test_seconds"],
            "authored_utility":authored_utility(case,result,settings),
        })
    return {
        "cases":len(receipts),
        "mutated_cases":sum(x["mutated"] for x in receipts),
        "bugs_detected":sum(x["mutated"] and x["detected"] for x in receipts),
        "bugs_missed":sum(x["mutated"] and not x["detected"] for x in receipts),
        "clean_false_alarms":sum(
            not x["mutated"] and x["detected"] for x in receipts),
        "source_test_actions":sum(len(x["real_actions"]) for x in receipts),
        "cases_with_conditional_second_action":sum(
            len(x["real_actions"])>=2 for x in receipts),
        "seconds":round(sum(x["actual_cost_seconds"] for x in receipts),6),
        "author_utility":round(sum(x["authored_utility"] for x in receipts),6),
        "decision_receipts":receipts,
    }


def calibrate(repo_root):
    repo=Path(repo_root).resolve()
    preflight=runner.preflight(repo)
    # Call the real earlier ring policy, check source remains ambiguous
    # and cannot be promoted to tool permissions.
    from sys import path
    path.insert(0,str(repo/"experiments"/"cartridge-ring-014"))
    import adapter
    methods,model12=adapter.freeze.source_methods()
    example=adapter.prepare_language_context(
        methods,model12,seed=2026111515)
    if (example["other_unmodeled_readings_remain_possible"] is not True
            or example["authority"]!="NONE"):
        raise ValueError("Original ambiguity source became authoritative")
    with tempfile.TemporaryDirectory(prefix="motif-ring015-calibration-") as tmp:
        d=Path(tmp);d.chmod(0o755)
        train_dir=d/"train";train_dir.mkdir(mode=0o755)
        dev_dir=d/"dev";dev_dir.mkdir(mode=0o755)
        train=measured_matrix(train_dir,repo,fixtures.TRAIN)
        dev=measured_matrix(dev_dir,repo,fixtures.DEV)
    estimates=policy.fitted(train) # NEVER sample development class labels
    trials=[]
    for b,t,a,force_triage in product(
            policy.SETTINGS["detection_benefit"],
            policy.SETTINGS["time_weight"],
            policy.SETTINGS["false_alarm_penalty"],
            (False,True)):
        settings={"detection_benefit":b,"time_weight":t,
                  "false_alarm_penalty":a}
        train_score=score(train,estimates,settings,
                          force_triage=force_triage)
        dev_score=score(dev,estimates,settings,
                        force_triage=force_triage)
        trials.append({
            "settings":settings,
            "force_triage":force_triage,
            "train":{k:v for k,v in train_score.items()
                     if k!="decision_receipts"},
            "dev":{k:v for k,v in dev_score.items()
                   if k!="decision_receipts"},
            "dev_decisions":dev_score["decision_receipts"],
        })
    # Select using measured development performance, penalizing undetected
    # seeded faults and honoring the real resource costs. No heldout lookups.
    best=max(trials,key=lambda x:(
        x["dev"]["author_utility"],
        -x["dev"]["bugs_missed"],
        -x["dev"]["source_test_actions"],
        x["dev"]["cases_with_conditional_second_action"],
        digest(x["settings"]),
    ))
    artifact={
        "schema":SCHEMA,
        "status":"SOURCE_MEASURED_CONDITIONAL_TEST_POLICY_FROZEN",
        "source_train_case_count":len(train),
        "source_dev_case_count":len(dev),
        "actual_calibration_docker_test_invocations":(
            len(train)+len(dev))*len(runner.PHASES),
        "reviewed_r013_source_sha256":preflight["source_files"],
        "docker_image_sha256":preflight["image_id"],
        "runner_preflight":preflight,
        "source_r012_ambiguity_policy_sha256":model12["receipt_sha256"],
        "source_open_world_meanings_retained":True,
        "source_train_real_measurements":train,
        "source_dev_real_measurements":dev,
        "model_likelihoods_derived_from_train_only":estimates,
        "candidate_action_policies_tested":len(trials),
        "selection_trials":trials,
        "selected_settings":best["settings"],
        "selected_force_triage":best["force_triage"],
        "selected_dev":best["dev"],
        "utility":REWARD_SCHEMA,
        "selected_reward_weights_are_author_defined":True,
        "real_source_tests_and_times_observed_not_simulated":True,
        "hidden_mutation_labels_used_only_for_development_scores":True,
        "sealed_postfreeze_mutations_not_imported_during_calibration":True,
        "sealed_test_results_not_used_for_policy_selection":True,
        "approved_execution_scope":"NETWORKLESS_READONLY_DOCKER_TESTS",
        "outside_actions_executed":0,"authority":"NONE",
    }
    artifact["receipt_sha256"]=digest(artifact)
    return artifact


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,
                    default=Path(__file__).resolve().parents[2])
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    x=calibrate(a.repo)
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":x["status"],
        "real_calibration_test_calls":x[
            "actual_calibration_docker_test_invocations"],
        "settings_compared":x["candidate_action_policies_tested"],
        "selected_settings":x["selected_settings"],
        "force_triage":x["selected_force_triage"],
        "selected_dev":x["selected_dev"],
        "receipt":x["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":main()
