"""RING-014 first real reversible source-test frontier.

All test results come from executing original RING-013 tests on a read-only
copy of its source in isolated Docker. The policy *dynamically decides*
which trusted test to run next, then reads its real output. It can stop
after a discovered failure, after a healthy-looking pass, or after budget.

Strong comparator strategies are evaluated with actual test outputs obtained
in the same isolated suite. Additional exhaustive measurements are made
AFTER the chosen live frontier actions; their outcomes are not passed back
to the frontier or used for precommit selection.

No code from connected private sources is executed. No GitHub mutation or
real-world action is run by this planner. The source's test mutation labels
are evaluator-only ground truth, never seen by the action selector.
"""
from __future__ import annotations
import argparse
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
import tempfile

import adapter,fixtures,learn,runner

SCHEMA="motif.ring014.actual-source-action-frontier-trial.v1"
STRATEGIES=("FRONTIER","ALWAYS_STOP","AST_ONLY","SMOKE_ONLY",
            "DEEP_ONLY","EXHAUSTIVE")

class HOLD(ValueError):
    pass


def verify_frozen(frozen,repo):
    if (not isinstance(frozen,dict) or frozen.get("schema")!=learn.SCHEMA
            or frozen.get("status")!="REAL_SOURCE_BEHAVIOR_TEST_VALUE_POLICY_FROZEN"
            or frozen.get("receipt_sha256")!=adapter.digest({
                k:v for k,v in frozen.items() if k!="receipt_sha256"})
            or frozen.get("heldout_code_fixtures_imported_during_selection") is not False
            or frozen.get("heldout_docker_outcomes_seen_during_selection") is not False
            or frozen.get("source_test_outcomes_measured_by_real_python_not_simulated") is not True
            or frozen.get("synthetic_source_mutations_not_real_world_bug_reports") is not True
            or frozen.get("external_effects_executed") is not False
            or frozen.get("outside_permissions")!="NONE"):
        raise HOLD("Changed, fictional or unauthorized source-test policy")
    preflight=runner.preflight(repo)
    if preflight!=frozen.get("source_actual_tests_runner_preflight"):
        raise HOLD("Reviewed source hashes or executed Docker image changed")
    source_lattice=adapter.freeze.search()
    if source_lattice["receipt_sha256"]!=frozen[
            "source_013_original_policy_receipt"]:
        raise HOLD("Inherited value-of-action source is not pinned")
    samples=frozen["calibration_source_phase_measurements"]
    train=samples["training"]
    dev=samples["development"]
    if (len(train)!=len(fixtures.TRAIN) or len(dev)!=len(fixtures.DEV)
            or frozen.get("source_train_cases")!=len(train)
            or frozen.get("source_dev_cases")!=len(dev)):
        raise HOLD("Missing measured baseline calibration samples")
    derived=adapter.empirical(train+dev)
    if derived!=frozen["observed_source_test_likelihoods_and_costs"]:
        raise HOLD("Rehashed source-test likelihood estimates fabricated")
    candidate=frozen["selected_settings"]
    if (not isinstance(candidate,dict) or
            set(candidate)!={"detection_benefit","time_weight",
                             "false_alarm_penalty"}
            or candidate["detection_benefit"] not in (8.0,16.0,28.0)
            or candidate["time_weight"] not in (0.5,2.0)
            or candidate["false_alarm_penalty"] not in (3.0,12.0)
            or frozen["candidate_action_value_settings_executed"]!=12):
        raise HOLD("Unreviewed or altered risk/reward settings")
    return preflight


def counterfactual(strategy,receipts):
    phases={
        "ALWAYS_STOP":(),
        "AST_ONLY":("AST",),
        "SMOKE_ONLY":("SMOKE",),
        "DEEP_ONLY":("DEEP",),
        "EXHAUSTIVE":("AST","SMOKE","DEEP"),
    }
    if strategy not in phases:
        raise HOLD("Unregistered comparison policy")
    output=[]
    for phase in phases[strategy]:
        r=receipts[phase]
        output.append(r)
        if not r["actual_source_tests_passed"]:
            break
    return {
        "actions":[{"phase":r["phase"],
                    "actual_measured_test":r,
                    "signal":"PASS" if r["actual_source_tests_passed"] else "FAIL"}
                   for r in output],
        "detected_test_failure":any(
            not r["actual_source_tests_passed"] for r in output),
        "spent_source_tests":len(output),
        "measured_total_seconds":round(sum(
            r["sandbox_elapsed_wall_seconds"] for r in output),6),
        "no_external_effects":True,
        "comparison_uses_actual_executed_test_results":True,
    }


def grade(results,records):
    totals={
        "cases":0,"seeded_defect_cases":0,"clean_control_cases":0,
        "true_mutated_source_defects_detected":0,
        "seeded_source_defects_missed":0,
        "false_alarms_on_clean_source":0,
        "real_source_test_calls_selected":0,
        "real_assertions_executed_by_selected_tests":0,
        "measured_wall_seconds":0.0,
        "negative_author_utility_cases":0,
        "sum_author_utility":0.0,
        "real_external_effects":0,
    }
    witness=[]
    for case in records:
        cid=case["case_id"]
        trace=results[cid]
        has_bug=case["intentional_defect"]
        found=trace["detected_test_failure"]
        u=learn.utility(trace,has_bug)
        totals["cases"]+=1
        totals["seeded_defect_cases"]+=int(has_bug)
        totals["clean_control_cases"]+=int(not has_bug)
        totals["true_mutated_source_defects_detected"]+=int(has_bug and found)
        totals["seeded_source_defects_missed"]+=int(has_bug and not found)
        totals["false_alarms_on_clean_source"]+=int(not has_bug and found)
        totals["real_source_test_calls_selected"]+=trace["spent_source_tests"]
        totals["real_assertions_executed_by_selected_tests"]+=sum(
            x["actual_measured_test"]["real_source_assertions_executed"]
            for x in trace["actions"])
        totals["measured_wall_seconds"]+=trace["measured_total_seconds"]
        totals["negative_author_utility_cases"]+=int(u<0)
        totals["sum_author_utility"]+=u
        witness.append({
            "case_id":cid,
            "source_copy_sha256":case["source_copy_sha256"],
            "is_intentionally_mutated":has_bug,
            "mutation_labels_not_supplied_to_decision_agent":True,
            "observed_failure":found,
            "selected_phase_order":[x["phase"] for x in trace["actions"]],
            "source_test_calls":trace["spent_source_tests"],
            "source_assertions":sum(
                x["actual_measured_test"]["real_source_assertions_executed"]
                for x in trace["actions"]),
            "source_seconds":trace["measured_total_seconds"],
            "authored_research_utility":u,
            "action_receipts":[x["actual_measured_test"] for x in trace["actions"]],
        })
    for k in ("measured_wall_seconds","sum_author_utility"):
        totals[k]=round(totals[k],6)
    totals["mean_author_utility_per_case"]=round(
        totals["sum_author_utility"]/max(1,totals["cases"]),6)
    return totals,witness


def run_frozen(frozen,repo_root):
    repo=Path(repo_root).resolve()
    preflight=verify_frozen(frozen,repo)
    # AFTER ALL preceding source checks: load the sealed challenge module.
    spec=spec_from_file_location(
        "ring014_postfreeze_mutations",
        Path(__file__).resolve().parent/"sealed.py")
    unseen=module_from_spec(spec)
    spec.loader.exec_module(unseen)
    sources,policy12=adapter.freeze.source_methods()
    if policy12["receipt_sha256"]!=frozen["source_012_lattice_receipt"]:
        raise HOLD("Source-language uncertainty model drifted")
    with tempfile.TemporaryDirectory(prefix="motif-ring014-postfreeze-") as d:
        root=Path(d)
        root.chmod(0o755)
        fixture_root=root/"cases"
        fixture_root.mkdir(mode=0o755)
        cases=fixtures.make(fixture_root,repo,unseen.CASES)
        frontier={}
        baselines={x:{} for x in STRATEGIES if x!="FRONTIER"}
        per_case=[]
        for idx,source in enumerate(cases):
            case=source["case_id"]
            # Source-owned RING-012 ambiguity, not source case mutant labels.
            lattice_result=adapter.prepare_language_context(
                sources,policy12,seed=2026111511+idx)
            # This is the crucial genuinely LIVE execution: the planner
            # chooses WHICH Docker test to run BEFORE receiving its result.
            active=adapter.execute_live(
                case,fixture_root,repo,lattice_result,
                frozen["observed_source_test_likelihoods_and_costs"],
                frozen["selected_settings"],
                frozen["value_params_from_frozen_ring013"])
            frontier[case]=active
            actual_observations={
                x["phase"]:x["actual_measured_test"]
                for x in active["actions"]}
            # Only after policy has stopped/finished do we run extra
            # bounded genuine code tests for the comparison strategies.
            for phase in runner.PHASES:
                if phase not in actual_observations:
                    actual_observations[phase]=runner.observe(
                        fixture_root,case,phase,repo)
            for strategy in baselines:
                baselines[strategy][case]=counterfactual(
                    strategy,actual_observations)
            per_case.append({
                **source,
                "lattice_sha256":adapter.digest(lattice_result),
                "source_lattice_candidate_count":len(lattice_result[
                    "supported_worlds"]),
                "other_unmodeled_interpretations_remain_possible":
                    lattice_result["other_unmodeled_readings_remain_possible"],
                "policy_selected_phase_order":[x["phase"]
                                               for x in active["actions"]],
                "policy_real_test_trace":active,
                "full_observed_real_test_matrix":actual_observations,
                "baseline_results_use_test_results_measured_after_policy_completed":True,
                "no_real_world_effects":True,
            })
    all_results={"FRONTIER":frontier,**baselines}
    metrics={}
    summaries={}
    for strategy,lookup in all_results.items():
        metrics[strategy],summaries[strategy]=grade(lookup,cases)
    out={
        "schema":SCHEMA,
        "status":"APPROVED_INTERNAL_DOCKER_CARTRIDGES_ACTUALLY_RUN_BY_VALUE_POLICY",
        "frozen_calibration_receipt_sha256":frozen["receipt_sha256"],
        "docker_image_sha256":preflight["image_id"],
        "source_copy_fingerprints":preflight["source_files"],
        "test_case_count":len(cases),
        "test_case_source_ids_sha256":adapter.digest([
            x["case_id"] for x in cases]),
        "real_source_test_case_receipts":per_case,
        "method_scores":metrics,
        "method_source_witnesses":summaries,
        "author_utility_contract":learn.UTILITY_SCHEMA,
        "selection_before_test_result_observed":True,
        "baseline_replays_use_actual_isolated_test_observations":True,
        "source_013_value_function_executes_next_action":True,
        "source_012_open_world_ambiguity_preserved":True,
        "outside_source_test_mutation_labels_unseen_by_planner":True,
        "no_internet_no_host_writes_no_credential_access":True,
        "private_how_to_live_or_other_user_data_not_used":True,
        "code_does_not_install_any_external_agent_capabilities":True,
        "real_work_measured_as_reviewed_Python_tests_not_authored_payoff":True,
        "mutations_are_developer_artificial_not_external_bugs":True,
        "automatic_external_effects_executed":0,
        "authority":"NONE",
    }
    out["receipt_sha256"]=adapter.digest(out)
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        report=run_frozen(json.loads(args.frozen.read_text()),args.repo)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print(json.dumps({
            "status":report["status"],"test_cases":report["test_case_count"],
            "scores":report["method_scores"],
            "source_test_invocation_count":sum(
                len(c["full_observed_real_test_matrix"])
                for c in report["real_source_test_case_receipts"]),
            "receipt_sha256":report["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,ValueError,runner.SandboxError,adapter.HOLD) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
