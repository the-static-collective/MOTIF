"""RING-014 real-source evidence hypergraph.

Reconciles individual Docker source-test receipts (actual PASS/FAIL, source
SHA, CPU/wall observations) with the chosen action traces and all baseline
scores. Source test defects are intentional authored mutations. The model's
value numbers remain hypothetical opportunity estimates; actual capability
measured here is the **selection/execution** of allowed real Python tests.

There is no promotion from "test passed" to general code correctness,
source-language truth, outside-world authority or unreviewed future tools.
"""
from __future__ import annotations
import argparse
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path

import adapter,fixtures,learn,runner

# Earlier rings also had "trial.py"; bind exact current source file.
TRIAL_FILE=Path(__file__).resolve().parent/"trial.py"
spec=spec_from_file_location("ring014_actual_source_trial",TRIAL_FILE)
trial=module_from_spec(spec)
spec.loader.exec_module(trial)

SCHEMA="motif.ring014.measured-safe-tool-frontier-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return adapter.digest(x)


def verify(frozen,report,repo_root):
    trial.verify_frozen(frozen,repo_root)
    if (not isinstance(report,dict) or report.get("schema")!=trial.SCHEMA
            or report.get("status")!=
            "APPROVED_INTERNAL_DOCKER_CARTRIDGES_ACTUALLY_RUN_BY_VALUE_POLICY"
            or report.get("receipt_sha256")!=digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("frozen_calibration_receipt_sha256")!=frozen["receipt_sha256"]
            or report.get("selection_before_test_result_observed") is not True
            or report.get("source_013_value_function_executes_next_action") is not True
            or report.get("source_012_open_world_ambiguity_preserved") is not True
            or report.get("baseline_replays_use_actual_isolated_test_observations") is not True
            or report.get("real_work_measured_as_reviewed_Python_tests_not_authored_payoff") is not True
            or report.get("private_how_to_live_or_other_user_data_not_used") is not True
            or report.get("automatic_external_effects_executed")!=0
            or report.get("authority")!="NONE"):
        raise HOLD("Modified test results or invented external action rights")
    if (report["docker_image_sha256"]!=frozen[
            "source_actual_tests_runner_preflight"]["image_id"]
            or report["source_copy_fingerprints"]!=frozen[
                "reviewed_source_fingerprints"]):
        raise HOLD("Actual execution source or image not pinned to training")
    rows=report.get("real_source_test_case_receipts")
    if (not isinstance(rows,list) or len(rows)!=12
            or report.get("test_case_count")!=len(rows)
            or len({x["case_id"] for x in rows})!=12):
        raise HOLD("Missing or duplicated source test task")
    if digest([x["case_id"] for x in rows])!=report.get(
            "test_case_source_ids_sha256"):
        raise HOLD("Source trial task identities were re-ordered or modified")
    strategies={name:{} for name in trial.STRATEGIES}
    for case in rows:
        cid=case["case_id"]
        if (not cid.startswith("unseen-")
                or case.get("no_real_world_effects") is not True
                or case.get("other_unmodeled_interpretations_remain_possible") is not True
                or case.get("baseline_results_use_test_results_measured_after_policy_completed") is not True):
            raise HOLD("Ungrounded language / untrusted source task assertion")
        matrix=case.get("full_observed_real_test_matrix")
        if not isinstance(matrix,dict) or set(matrix)!=set(runner.PHASES):
            raise HOLD("Must preserve complete actual source test matrix")
        for phase,receipt in matrix.items():
            if (receipt.get("schema")!=runner.SCHEMA
                    or receipt.get("case")!=cid
                    or receipt.get("phase")!=phase
                    or receipt.get("source_copy_sha256")!=case["source_copy_sha256"]
                    or type(receipt.get("actual_source_tests_passed")) is not bool
                    or type(receipt.get("real_source_assertions_executed")) is not int
                    or receipt.get("outside_actions_executed")!=0
                    or receipt.get("no_unreviewed_code_execution") is not True
                    or receipt.get("sandbox_is_not_arbitrary_hostile_code_security_proof") is not True
                    or not all(receipt.get("isolation_controls",{}).values())
                    or len(receipt.get("isolation_controls",{}))!=9):
                raise HOLD("Forged, foreign or incomplete executable Docker source receipt")
        active=case.get("policy_real_test_trace")
        if (not isinstance(active,dict)
                or active.get("case")!=cid
                or active.get("real_tests_triggered_by_dynamic_value_policy") is not True
                or active.get("no_unsandboxed_fallback") is not True
                or active.get("external_effects")!=0
                or active.get("ambiguity_kept_open") is not True
                or active.get("spent_source_tests")!=len(active.get("actions",[]))
                or len(active["actions"])>3):
            raise HOLD("Non-dynamic or external-action policy receipt")
        selected=set()
        for i,action in enumerate(active["actions"]):
            phase=action.get("phase")
            if (phase not in runner.PHASES or phase in selected
                    or action.get("action")!=adapter.PHASE_ACTION[phase]
                    or action.get("actual_measured_test")!=matrix[phase]
                    or action.get("signal")!=(
                        "PASS" if matrix[phase]["actual_source_tests_passed"]
                        else "FAIL")
                    or action.get("used_real_source_test_return") is not True
                    or (i>0 and active["actions"][i-1]["signal"]=="FAIL")):
                raise HOLD("Policy action was not executed as a reviewed source test")
            selected.add(phase)
        if (case.get("policy_selected_phase_order")!=[
                x["phase"] for x in active["actions"]]
                or active.get("detected_test_failure")!=any(
                    x["signal"]=="FAIL" for x in active["actions"])
                or abs(active["measured_total_seconds"]-sum(
                    x["actual_measured_test"]["sandbox_elapsed_wall_seconds"]
                    for x in active["actions"]))>1e-4):
            raise HOLD("Selected source test trace contradicts actual observation")
        strategies["FRONTIER"][cid]=active
        for name in trial.STRATEGIES:
            if name=="FRONTIER":continue
            strategies[name][cid]=trial.counterfactual(name,matrix)
    # Validate all actual baseline aggregates from the same source test
    # receipts, not new author-selected outcome flags.
    for name,lookup in strategies.items():
        aggregate,receipts=trial.grade(lookup,rows)
        if (aggregate!=report.get("method_scores",{}).get(name)
                or receipts!=report.get("method_source_witnesses",{}).get(name)):
            raise HOLD("Method headline suppresses source failure or resource cost")
    return rows


def build(frozen,report,repo_root):
    rows=verify(frozen,report,repo_root)
    source="source:"+frozen["source_013_original_policy_receipt"]
    ambiguity="lattice:"+frozen["source_012_lattice_receipt"]
    calibration="tested:"+frozen["receipt_sha256"]
    nodes=[
        {"id":source,"kind":"PINNED_RING013_VALUE_OF_NEXT_ACTION_CODE"},
        {"id":ambiguity,"kind":"PINNED_OPEN_WORLD_SOURCE_LANGUAGE_HYPOTHESES"},
        {"id":calibration,"kind":"MEASURED_DOCKER_TRAINING_FAILURE_AND_COST_LIKELIHOODS",
         "cases":frozen["source_train_cases"]+frozen["source_dev_cases"],
         "real_source_test_invocations":frozen[
             "source_test_invocations_for_calibration"]},
    ]
    refs=[]
    for case in rows:
        ref="source-test:"+case["source_copy_sha256"]
        # Several clean controls share identical source contents: each
        # separately tested case needs an independently traceable witness ID.
        ref+=":"+case["case_id"]
        refs.append(ref)
        nodes.append({
            "id":ref,"kind":"REAL_READONLY_NO_NETWORK_PYTHON_SOURCE_TEST",
            "source_code_sha256":case["source_copy_sha256"],
            "seeded_reviewed_mutation":case["intentional_defect"],
            "real_external_effects":0,
        })
    frontier=report["method_scores"]["FRONTIER"]
    deep=report["method_scores"]["DEEP_ONLY"]
    exhaustive=report["method_scores"]["EXHAUSTIVE"]
    hold=report["method_scores"]["ALWAYS_STOP"]
    measured={
        "id":"observed:real-source-diagnostic-work-and-action-cost",
        "type":"RUNTIME_EXECUTED_SOURCE_TESTS_WITH_UNSEEN_SEEDED_MUTATIONS",
        "tails":[source,ambiguity,calibration,*refs],
        "heads":[
            "demonstration:planner_selected_and_executed_reviewed_real_tests",
            "benefit:seeded_source_regressions_detected",
            "risk:source_regressions_not_detected",
            "cost:measured_wall_seconds_and_test_calls",
            "frontier:real_useful_software_repair_or_new_cartridge_not_yet_proven",
        ],
        "source_test_cases":len(rows),
        "model_selected_actual_test_steps":frontier[
            "real_source_test_calls_selected"],
        "source_bug_cases":frontier["seeded_defect_cases"],
        "bug_cases_detected":frontier["true_mutated_source_defects_detected"],
        "bug_cases_missed":frontier["seeded_source_defects_missed"],
        "false_clean_alarms":frontier["false_alarms_on_clean_source"],
        "actual_test_wall_seconds":frontier["measured_wall_seconds"],
        "source_assertions_executed":frontier[
            "real_assertions_executed_by_selected_tests"],
        "authored_utility_after_measured_tests":frontier["sum_author_utility"],
        "deep_only_baseline":deep,
        "exhaustive_baseline":exhaustive,
        "always_stop_baseline":hold,
        "no_real_world_bug_fixes_demonstrated":True,
        "published_test_codes_reviewed_first":True,
        "all_methods_evaluated_on_same_immutably_copied_source":True,
    }
    hyperedges=[
        {
            "id":"constructed:prior-reasoning-to-source-executing-tool-bridge",
            "type":"REVIEWED_TOOL_EXECUTION_PERMISSIONS_FROM_SOURCE_CATALOG",
            "tails":[source,ambiguity,calibration],
            "heads":[
                "method:finite_budget_actions_ast_smoke_deep",
                "method:prioritize_future_research_after_real_observation",
                "method:stop_on_observed_failure",
                "frontier:measured_repair_or_new_method_admission",
            ],
            "proposed_value_weights_are_heuristics":True,
            "actual_source_test_returns_not_simulated":True,
            "safe_internal_python_tools_are_real":True,
            "external_effect_authority":"NONE",
        },
        measured,
    ]
    result={
        "schema":SCHEMA,
        "source_frozen_calibration_receipt":frozen["receipt_sha256"],
        "source_real_trial_receipt":report["receipt_sha256"],
        "vertices":nodes,"hyperedges":hyperedges,
        "real_source_test_execution_demonstrated":True,
        "unreviewed_real_world_tool_use_demonstrated":False,
        "real_program_repair_autonomy_demonstrated":False,
        "source_language_truth_or_users_interest_verified":False,
        "new_external_authority":0,
        "outside_actions_executed":0,
        "authority":"NONE",
    }
    result["receipt_sha256"]=adapter.digest(result)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--trial",type=Path,required=True)
    p.add_argument("--repo",type=Path,
                   default=Path(__file__).resolve().parents[2])
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=build(json.loads(args.frozen.read_text()),
                     json.loads(args.trial.read_text()),
                     args.repo)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        summary=result["hyperedges"][1]
        print(json.dumps({
            "schema":result["schema"],
            "test_cases":summary["source_test_cases"],
            "actual_executed_policy_tests":summary["model_selected_actual_test_steps"],
            "mutation_cases_detected":summary["bug_cases_detected"],
            "mutation_cases_missed":summary["bug_cases_missed"],
            "measured_source_runtime":summary["actual_test_wall_seconds"],
            "deep_control":summary["deep_only_baseline"][
                "true_mutated_source_defects_detected"],
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,trial.HOLD,runner.SandboxError,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
