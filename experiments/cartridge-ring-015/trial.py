"""RING-015 post-freeze source experiment: value of a second real test.

The selected action policy FIRST decides whether to run cheap TRIAGE,
expensive FULL, or STOP using estimates frozen from prior source tests.
If TRIAGE runs, it observes the actual changed code region inside
read-only Docker before selecting a focused MATH or CONTROL test and
possibly FULL afterward.

Every other baseline is evaluated ONLY AFTER the live action sequence is
over, using real tests on the same immutable source copy. The frozen agent
does not receive hidden mutation labels, future outputs or counters.

The reported win/loss metrics use developer-seeded source bugs and
developer-chosen utility; no independent real-world tool competence.
"""
from __future__ import annotations
import argparse
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
import tempfile

import fixtures,learn,policy,runner

SCHEMA="motif.ring015.real-conditional-second-test-trial.v1"
METHODS=(
    "SELECTED_LIVE",
    "ALWAYS_FULL",
    "ALWAYS_STOP",
    "TRIAGE_ONLY",
    "TRIAGE_THEN_TARGET",
    "TRIAGE_OPTIONAL_FOLLOWUP",
    "AUTO_COUNTERFACTUAL",
    "EXHAUSTIVE_UNTIL_FAIL",
)
class HOLD(ValueError):pass


def verify_frozen(frozen,repo):
    if (not isinstance(frozen,dict)
            or frozen.get("schema")!=learn.SCHEMA
            or frozen.get("status")!="SOURCE_MEASURED_CONDITIONAL_TEST_POLICY_FROZEN"
            or frozen.get("receipt_sha256")!=learn.digest({
                k:v for k,v in frozen.items() if k!="receipt_sha256"})
            or frozen.get("sealed_postfreeze_mutations_not_imported_during_calibration") is not True
            or frozen.get("sealed_test_results_not_used_for_policy_selection") is not True
            or frozen.get("real_source_tests_and_times_observed_not_simulated") is not True
            or frozen.get("selected_reward_weights_are_author_defined") is not True
            or frozen.get("outside_actions_executed")!=0
            or frozen.get("authority")!="NONE"):
        raise HOLD("Wrong or modified policy/authority")
    pre=runner.preflight(repo)
    if (pre!=frozen.get("runner_preflight")
            or pre["source_files"]!=frozen["reviewed_r013_source_sha256"]
            or pre["image_id"]!=frozen["docker_image_sha256"]):
        raise HOLD("Pinned original code or Docker image changed")
    from sys import path
    path.insert(0,str(Path(repo)/"experiments"/"cartridge-ring-014"))
    import adapter
    _,ring12=adapter.freeze.source_methods()
    if ring12["receipt_sha256"]!=frozen["source_r012_ambiguity_policy_sha256"]:
        raise HOLD("Lost original RING-012 ambiguity context")
    if (frozen.get("source_train_case_count")!=len(fixtures.TRAIN)
            or frozen.get("source_dev_case_count")!=len(fixtures.DEV)
            or frozen.get("actual_calibration_docker_test_invocations")!=(
                len(fixtures.TRAIN)+len(fixtures.DEV))*len(runner.PHASES)):
        raise HOLD("Original source experiment coverage fabricated")
    estimate=policy.fitted(frozen["source_train_real_measurements"])
    if estimate!=frozen["model_likelihoods_derived_from_train_only"]:
        raise HOLD("Rehashed failure likelihood learned from external test")
    policy.validate_settings(frozen["selected_settings"])
    if type(frozen["selected_force_triage"]) is not bool:
        raise HOLD("Unreviewed action execution policy")
    if frozen["candidate_action_policies_tested"]!=36:
        raise HOLD("Incomplete action policy comparison")
    return frozen


def replay(name,tests,estimate,settings,*,selected_force_triage):
    """Counterfactual uses actual source tests measured AFTER agent stopped."""
    if name=="SELECTED_LIVE":raise ValueError("Live policy cannot be re-run as a control")
    if name in ("TRIAGE_OPTIONAL_FOLLOWUP","AUTO_COUNTERFACTUAL"):
        return policy.route(estimate,settings,
                            lambda p:tests[p],
                            force_triage=(name=="TRIAGE_OPTIONAL_FOLLOWUP"))
    if name=="ALWAYS_STOP":
        phases=()
    elif name=="ALWAYS_FULL":
        phases=("FULL",)
    elif name=="TRIAGE_ONLY":
        phases=("TRIAGE",)
    elif name=="EXHAUSTIVE_UNTIL_FAIL":
        phases=runner.PHASES
    elif name=="TRIAGE_THEN_TARGET":
        cue=tests["TRIAGE"]["source_cue"]
        target={"MATH":"MATH","CONTROL":"CONTROL",
                "MIXED":"FULL","OTHER":"FULL"}.get(cue)
        phases=("TRIAGE",)+(tuple([target]) if target else ())
    else:raise ValueError("Unregistered reviewer control")
    outcomes=[]
    for phase in phases:
        r=tests[phase]
        outcomes.append(r)
        if not r["actual_source_tests_passed"]:
            break
    return {
        **policy.summarize_case(outcomes),
        "receipts":outcomes,
        "decision_trace":[{"method":name,"source":"EXPLICIT_CONTROL"}],
        "external_actions_authorized":False,
        "ambiguity_preserved":True,
    }


def measured_score(records):
    results={
        "cases":0,"seeded_defects":0,"clean_or_benign_controls":0,
        "seeded_defects_detected":0,"seeded_defects_missed":0,
        "clean_false_alarms":0,
        "real_tests_executed":0,"real_source_assertions":0,
        "cases_with_real_second_test":0,"cases_with_third_test":0,
        "changed_source_triage_cases":0,
        "measured_source_wall_seconds":0.0,
        "author_utility":0.0,
    }
    for item in records:
        bug=item["seeded_defect"]
        observed=item["outcome"]
        fail=observed["saw_actual_failure"]
        n=observed["number_source_tests"]
        results["cases"]+=1
        results["seeded_defects"]+=int(bug)
        results["clean_or_benign_controls"]+=int(not bug)
        results["seeded_defects_detected"]+=int(bug and fail)
        results["seeded_defects_missed"]+=int(bug and not fail)
        results["clean_false_alarms"]+=int(not bug and fail)
        results["real_tests_executed"]+=n
        results["real_source_assertions"]+=observed["source_assertions"]
        results["cases_with_real_second_test"]+=int(n>=2)
        results["cases_with_third_test"]+=int(n>=3)
        results["changed_source_triage_cases"]+=int(
            observed["first_observed_cue"] not in (None,"UNCHANGED"))
        results["measured_source_wall_seconds"]+=observed[
            "actual_test_seconds"]
        results["author_utility"]+=item["author_utility"]
    for key in ("measured_source_wall_seconds","author_utility"):
        results[key]=round(results[key],6)
    results["author_utility_per_case"]=round(
        results["author_utility"]/max(1,results["cases"]),6)
    return results


def run_frozen(frozen,repo_root):
    repo=Path(repo_root).resolve()
    verify_frozen(frozen,repo)
    # This module was absent from all training / development selection.
    sealed_spec=spec_from_file_location(
        "ring015_reserved_real_test_cases",
        Path(__file__).resolve().parent/"sealed.py")
    sealed=module_from_spec(sealed_spec)
    sealed_spec.loader.exec_module(sealed)
    from sys import path
    path.insert(0,str(repo/"experiments"/"cartridge-ring-014"))
    import adapter
    methods,model12=adapter.freeze.source_methods()
    estimate=frozen["model_likelihoods_derived_from_train_only"]
    settings=frozen["selected_settings"]
    score_rows={x:[] for x in METHODS}
    receipts=[]
    with tempfile.TemporaryDirectory(prefix="motif-ring015-postfreeze-") as d:
        folder=Path(d)
        folder.chmod(0o755)
        cases_dir=folder/"cases"
        cases_dir.mkdir(mode=0o755)
        cases=fixtures.make(cases_dir,repo,sealed.CASES)
        for i,case in enumerate(cases):
            cid=case["case_id"]
            lattice=adapter.prepare_language_context(
                methods,model12,seed=2026111580+i)
            if (lattice["other_unmodeled_readings_remain_possible"] is not True
                    or lattice["authority"]!="NONE"
                    or lattice["external_action_executed"] is not False):
                raise HOLD("Open-world source context lost or authorized an effect")
            # CRITICAL: the next test is CHOSEN before runner.observe runs.
            # Mutated labels are NOT passed to the policy callback.
            active=policy.route(
                estimate,settings,
                lambda phase:runner.observe(cases_dir,cid,phase,repo),
                force_triage=frozen["selected_force_triage"])
            observations={x["phase"]:x for x in active["receipts"]}
            # Only once the selected live policy has terminated do we
            # gather other real source results for control comparisons.
            for phase in runner.PHASES:
                if phase not in observations:
                    observations[phase]=runner.observe(
                        cases_dir,cid,phase,repo)
            case_summary={
                **case,
                "lattice_source_sha256":learn.digest(lattice),
                "ambiguity_remains_open":True,
                "selected_real_action_sequence":active,
                "complete_source_test_matrix":observations,
                "control_results_gathered_after_live_policy_stopped":True,
                "hidden_defect_labels_never_given_to_action_callback":True,
                "external_actions_executed":0,
            }
            for name in METHODS:
                result=(active if name=="SELECTED_LIVE" else
                        replay(name,observations,estimate,settings,
                               selected_force_triage=frozen[
                                   "selected_force_triage"]))
                scored=learn.authored_utility(case,result,settings)
                score_rows[name].append({
                    "case_id":cid,
                    "seeded_defect":case["seeded_defect"],
                    "benign_edit":case["benign_edit"],
                    "outcome":result,
                    "author_utility":scored,
                })
            receipts.append(case_summary)
    scores={k:measured_score(rows) for k,rows in score_rows.items()}
    result={
        "schema":SCHEMA,
        "status":"REAL_CONDITIONAL_FOLLOWUP_TESTS_EXECUTED_AND_MEASURED",
        "frozen_policy_sha256":frozen["receipt_sha256"],
        "reviewed_source_fingerprints":frozen["reviewed_r013_source_sha256"],
        "docker_image_sha256":frozen["docker_image_sha256"],
        "source_test_cases":len(cases),
        "source_test_case_id_sha256":learn.digest([x["case_id"] for x in cases]),
        "selected_training_sized_action_parameters":settings,
        "selected_mode_force_triage":frozen["selected_force_triage"],
        "individual_code_and_test_receipts":receipts,
        "method_score_rows":score_rows,
        "method_scores":scores,
        "real_test_invocations_including_comparator_measurement":(
            len(cases)*len(runner.PHASES)),
        "source_only_and_immutable_fixture_copies":True,
        "decision_actions_selected_before_receiving_their_test_result":True,
        "all_baseline_results_measured_after_live_policy":True,
        "precomputed_test_matrix_not_exposed_to_live_planner":True,
        "source_method_test_signals_are_real_interpreter_outputs":True,
        "utility_numbers_are_author_values_not_verified_savings":True,
        "private_user_documents_not_read_by_test_worker":True,
        "independent_real_world_defect_generalization_proven":False,
        "outside_effectful_actions_executed":0,
        "new_agent_tool_permissions_granted":0,
        "authority":"NONE",
    }
    result["receipt_sha256"]=learn.digest(result)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,
                   default=Path(__file__).resolve().parents[2])
    p.add_argument("--frozen",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        report=run_frozen(json.loads(args.frozen.read_text()),args.repo)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        print(json.dumps({
            "schema":report["schema"],
            "case_count":report["source_test_cases"],
            "chosen_mode_force_triage":report["selected_mode_force_triage"],
            "scores":report["method_scores"],
            "source_test_receipt_sha256":report["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,runner.SandboxError,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":main()
