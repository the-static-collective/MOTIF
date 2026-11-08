"""RING-014: freeze data-derived source-test value preferences BEFORE unseen code.

Execute real AST, SMOKE and DEEP methods against 10 train + 4 dev
source-derived reviewed Python copies inside no-network read-only Docker.
Use actual PASS/FAIL, measured Docker wall duration and known seeded defect
labels to choose how much testing is worthwhile.

The artificial success utility below is an AUTHOR-CHOOSEN research utility.
The underlying signals and costs are actual source-owned test executions;
this is materially different from RING-013's entirely authored rewards.
Heldout defects are defined in separate sealed.py and never imported here.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import itertools
import json
from pathlib import Path
import tempfile

import adapter,fixtures,runner

SCHEMA="motif.ring014.precommitted-real-test-action-policy.v1"
UTILITY_SCHEMA="motif.ring014.author-chosen-defect-utility.v1"


def gather(specs,folder,repo_root):
    generated=fixtures.make(folder,repo_root,specs)
    rows=[]
    for item in generated:
        tests={
            phase:runner.observe(folder,item["case_id"],phase,repo_root)
            for phase in runner.PHASES
        }
        rows.append({**item,"tests":tests})
    return rows


def utility(trace,has_seeded_defect):
    found=trace["detected_test_failure"]
    if has_seeded_defect and found:
        verified=12.0
    elif has_seeded_defect and not found:
        verified=-15.0
    elif not has_seeded_defect and found:
        verified=-12.0
    else:
        verified=2.0
    # Real wall cost, author-selected conversion to utility.
    return round(
        verified
        -0.40*trace["measured_total_seconds"]
        -0.35*trace["spent_source_tests"],6)


def scored_cases(rows,lattices,estimate,settings,params):
    history=[]
    for item in rows:
        case=item["case_id"]
        result=adapter.trace_from_observations(
            {"id":case},lattices[case],params,
            item["tests"],settings,estimate)
        history.append({
            "case_id":case,
            "has_deliberate_source_mutation":item["intentional_defect"],
            "selected_actions":[x["phase"] for x in result["actions"]],
            "detected_source_test_failure":result["detected_test_failure"],
            "source_actions_executed":result["spent_source_tests"],
            "measured_cost_seconds":result["measured_total_seconds"],
            "authored_research_utility":utility(
                result,item["intentional_defect"]),
        })
    return {
        "cases":len(history),
        "seeded_bug_count":sum(x["has_deliberate_source_mutation"]
                               for x in history),
        "correctly_detected_bug_cases":sum(
            x["has_deliberate_source_mutation"] and
            x["detected_source_test_failure"] for x in history),
        "missed_bug_cases":sum(
            x["has_deliberate_source_mutation"] and not
            x["detected_source_test_failure"] for x in history),
        "false_alarm_clean_cases":sum(
            not x["has_deliberate_source_mutation"] and
            x["detected_source_test_failure"] for x in history),
        "source_test_calls":sum(x["source_actions_executed"]
                                for x in history),
        "wall_seconds":round(sum(x["measured_cost_seconds"]
                                 for x in history),6),
        "total_authored_utility":round(sum(x["authored_research_utility"]
                                           for x in history),6),
        "individual_decisions":history,
    }


def calibrate(repo_root):
    repo=Path(repo_root).resolve()
    source=runner.preflight(repo)
    src_methods,source_lattice=adapter.freeze.source_methods()
    ring013=adapter.freeze.search()
    if ring013["source_ring012_lattice_policy_sha256"]!=source_lattice[
            "receipt_sha256"]:
        raise ValueError("Original RING-013 source policy cannot be re-used")
    params=ring013["policy_params"]
    with tempfile.TemporaryDirectory(prefix="motif-ring014-calibration-") as d:
        root=Path(d)
        root.chmod(0o755)
        train_dir=root/"train"
        dev_dir=root/"dev"
        train_dir.mkdir(mode=0o755)
        dev_dir.mkdir(mode=0o755)
        training=gather(fixtures.TRAIN,train_dir,repo)
        development=gather(fixtures.DEV,dev_dir,repo)
    estimate=adapter.empirical(training+development)
    lattices={}
    for i,x in enumerate(training+development):
        lattices[x["case_id"]]=adapter.prepare_language_context(
            src_methods,source_lattice,seed=2026111400+i)
    candidates=[]
    for benefit,time_weight,alarm in itertools.product(
            (8.0,16.0,28.0),(0.5,2.0),(3.0,12.0)):
        settings={
            "detection_benefit":benefit,
            "time_weight":time_weight,
            "false_alarm_penalty":alarm,
        }
        train_score=scored_cases(
            training,lattices,estimate,settings,params)
        dev_score=scored_cases(
            development,lattices,estimate,settings,params)
        candidates.append({
            "settings":settings,
            "train_summary":{k:v for k,v in train_score.items()
                             if k!="individual_decisions"},
            "dev_summary":{k:v for k,v in dev_score.items()
                           if k!="individual_decisions"},
            "source_train_decisions":train_score["individual_decisions"],
            "source_dev_decisions":dev_score["individual_decisions"],
        })
    winner=max(candidates,key=lambda x:(
        x["train_summary"]["total_authored_utility"]+
        x["dev_summary"]["total_authored_utility"],
        x["dev_summary"]["correctly_detected_bug_cases"],
        -x["dev_summary"]["missed_bug_cases"],
        -x["train_summary"]["source_test_calls"]-
         x["dev_summary"]["source_test_calls"],
        adapter.digest(x["settings"]),
    ))
    out={
        "schema":SCHEMA,
        "status":"REAL_SOURCE_BEHAVIOR_TEST_VALUE_POLICY_FROZEN",
        "source_013_original_policy_receipt":ring013["receipt_sha256"],
        "source_012_lattice_receipt":source_lattice["receipt_sha256"],
        "reviewed_source_fingerprints":source["source_files"],
        "tested_container_image":source["image"],
        "source_actual_tests_runner_preflight":source,
        "source_train_cases":len(training),
        "source_dev_cases":len(development),
        "source_test_invocations_for_calibration":(
            len(training)+len(development))*len(runner.PHASES),
        "calibration_source_phase_measurements":{
            "training":training,
            "development":development,
        },
        "observed_source_test_likelihoods_and_costs":estimate,
        "value_params_from_frozen_ring013":params,
        "candidate_action_value_settings_executed":len(candidates),
        "candidate_selection_trials":candidates,
        "selected_settings":winner["settings"],
        "selected_train":winner["train_summary"],
        "selected_dev":winner["dev_summary"],
        "utility_contract":UTILITY_SCHEMA,
        "source_test_outcomes_measured_by_real_python_not_simulated":True,
        "synthetic_source_mutations_not_real_world_bug_reports":True,
        "real_test_action_values_use_author_chosen_detection_rewards":True,
        "training_and_dev_labels_seen_only_to_calibration":True,
        "heldout_code_fixtures_imported_during_selection":False,
        "heldout_docker_outcomes_seen_during_selection":False,
        "external_effects_executed":False,
        "outside_permissions":"NONE",
    }
    out["receipt_sha256"]=adapter.digest(out)
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    doc=calibrate(args.repo)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "schema":doc["schema"],
        "candidate_value_models":doc[
            "candidate_action_value_settings_executed"],
        "actual_source_test_calls":doc[
            "source_test_invocations_for_calibration"],
        "selected_settings":doc["selected_settings"],
        "train":doc["selected_train"],
        "dev":doc["selected_dev"],
        "receipt_sha256":doc["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
