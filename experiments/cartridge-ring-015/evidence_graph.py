"""RING-015: measured source hypergraph for follow-up action vs cost.

No claims based on hand-filled PASS/FAIL: all action receipts must match
phase- and case-specific Docker source executions. The selected action
sequence is independently reconstructible from the frozen policy and
observations. Bug-detection scores, clean false alarms, measured wall time
and missed defects travel through the SAME many-tail hyperedge.

Content hashes prove internal consistency, not that developer-seeded faults
measure autonomous bug discovery on unrelated real software.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

import fixtures,learn,policy,runner,trial

SCHEMA="motif.ring015.real-conditional-investigation-evidence.v1"
class HOLD(ValueError):pass


def verify(frozen,report,repo_root):
    trial.verify_frozen(frozen,repo_root)
    if (not isinstance(report,dict)
            or report.get("schema")!=trial.SCHEMA
            or report.get("status")!=
            "REAL_CONDITIONAL_FOLLOWUP_TESTS_EXECUTED_AND_MEASURED"
            or report.get("receipt_sha256")!=learn.digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("frozen_policy_sha256")!=frozen["receipt_sha256"]
            or report.get("docker_image_sha256")!=frozen["docker_image_sha256"]
            or report.get("reviewed_source_fingerprints")!=frozen[
                "reviewed_r013_source_sha256"]
            or report.get("decision_actions_selected_before_receiving_their_test_result") is not True
            or report.get("all_baseline_results_measured_after_live_policy") is not True
            or report.get("precomputed_test_matrix_not_exposed_to_live_planner") is not True
            or report.get("source_method_test_signals_are_real_interpreter_outputs") is not True
            or report.get("utility_numbers_are_author_values_not_verified_savings") is not True
            or report.get("private_user_documents_not_read_by_test_worker") is not True
            or report.get("outside_effectful_actions_executed")!=0
            or report.get("new_agent_tool_permissions_granted")!=0
            or report.get("authority")!="NONE"):
        raise HOLD("Altered source evidence or illegitimate authority")
    rows=report.get("individual_code_and_test_receipts")
    if (not isinstance(rows,list) or len(rows)!=18
            or report.get("source_test_cases")!=18
            or report.get("real_test_invocations_including_comparator_measurement")!=
            len(rows)*len(runner.PHASES)
            or len({x["case_id"] for x in rows})!=len(rows)
            or learn.digest([x["case_id"] for x in rows])!=report[
                "source_test_case_id_sha256"]):
        raise HOLD("Lost or duplicated authored source experiment")
    estimate=frozen["model_likelihoods_derived_from_train_only"]
    settings=frozen["selected_settings"]
    scored={name:[] for name in trial.METHODS}
    for case in rows:
        cid=case["case_id"]
        if (not cid.startswith("heldout-")
                or case.get("ambiguity_remains_open") is not True
                or case.get("control_results_gathered_after_live_policy_stopped") is not True
                or case.get("hidden_defect_labels_never_given_to_action_callback") is not True
                or case.get("external_actions_executed")!=0
                or case.get("hidden_mutation_labels_not_visible_to_selector") is not True
                or case.get("seeded_defect")!=any(x in fixtures.SEVERE for x
                    in case.get("mutation_labels_visible_only_to_calibration_and_scorer",[]))
                or type(case.get("benign_edit")) is not bool):
            raise HOLD("Case identity, defect grade or open-world provenance changed")
        matrix=case.get("complete_source_test_matrix")
        if not isinstance(matrix,dict) or set(matrix)!=set(runner.PHASES):
            raise HOLD("Missing actual four-phase source test comparison")
        for phase,r in matrix.items():
            if (r.get("schema")!=runner.SCHEMA
                    or r.get("phase")!=phase
                    or r.get("case_id")!=cid
                    or r.get("source_copy_sha256")!=case[
                        "source_copy_sha256"]
                    or r.get("external_effects_executed")!=0
                    or r.get("authority")!="NONE"
                    or r.get("host_approved_method_only") is not True
                    or r.get("source_labels_not_supplied_to_planner") is not True
                    or not all(r.get("isolation",{}).values())
                    or len(r.get("isolation",{}))!=9
                    or type(r.get("actual_source_tests_passed")) is not bool
                    or type(r.get("measured_wall_seconds")) not in (int,float)
                    or r["measured_wall_seconds"]<0):
                raise HOLD("Forged or non-isolated actual Python measurement")
        actual=case.get("selected_real_action_sequence")
        if (not isinstance(actual,dict)
                or actual.get("external_actions_authorized") is not False
                or actual.get("ambiguity_preserved") is not True
                or len(actual.get("receipts",[]))>3
                or len({r["phase"] for r in actual["receipts"]})!=len(
                    actual["receipts"])
                or any(r!=matrix[r["phase"]] for r in actual["receipts"])):
            raise HOLD("Planner used an unreviewed source test or hidden result")
        # Recompute the action sequence solely from frozen estimates +
        # observed returns: no hidden bug tags available to this callback.
        expected=policy.route(
            estimate,settings,lambda phase:matrix[phase],
            force_triage=frozen["selected_force_triage"])
        if expected!=actual:
            raise HOLD("Selected next test not reproducible from earlier observations")
        if case["selected_real_action_sequence"]!=actual:
            raise HOLD("Source test action transcript changed")
        for name in trial.METHODS:
            measured=(actual if name=="SELECTED_LIVE" else
                      trial.replay(name,matrix,estimate,settings,
                                   selected_force_triage=frozen[
                                       "selected_force_triage"]))
            grade={
                "case_id":cid,
                "seeded_defect":case["seeded_defect"],
                "benign_edit":case["benign_edit"],
                "outcome":measured,
                "author_utility":learn.authored_utility(case,measured,settings),
            }
            scored[name].append(grade)
    if scored!=report.get("method_score_rows"):
        raise HOLD("Case-level false-positive/negative cost or control receipt changed")
    totals={name:trial.measured_score(rows)
            for name,rows in scored.items()}
    if totals!=report.get("method_scores"):
        raise HOLD("Outcome headline does not match source test receipts")
    return rows


def build(frozen,report,repo_root):
    cases=verify(frozen,report,repo_root)
    src="source:"+learn.digest(frozen["reviewed_r013_source_sha256"])
    measured="calibration:"+frozen["receipt_sha256"]
    ambiguity="open-world:"+frozen["source_r012_ambiguity_policy_sha256"]
    vertices=[
        {"id":src,"type":"PINNED_REVIEWED_R013_PYTHON_SOURCE"},
        {"id":measured,"type":"MEASURED_PRECOMMITTED_R015_TEST_LIKELIHOOD",
         "calibration_source_calls":frozen[
             "actual_calibration_docker_test_invocations"]},
        {"id":ambiguity,"type":"NONAUTHORITATIVE_OPEN_WORLD_PERSPECTIVES"},
    ]
    tokens=[]
    for case in cases:
        name="actual-test:"+case["case_id"]+":"+case["source_copy_sha256"]
        tokens.append(name)
        vertices.append({
            "id":name,"type":"POSTFREEZE_REVIEWED_DOCKER_SOURCE_COPY",
            "artificial_mutation":case["seeded_defect"],
            "no_independent_production_bug_corroboration":True,
        })
    active=report["method_scores"]["SELECTED_LIVE"]
    full=report["method_scores"]["ALWAYS_FULL"]
    triage=report["method_scores"]["TRIAGE_OPTIONAL_FOLLOWUP"]
    exhaustive=report["method_scores"]["EXHAUSTIVE_UNTIL_FAIL"]
    constructed={
        "id":"method:measure-option-value-after-a-real-observation",
        "type":"SOURCE_BOUND_CONDITIONAL_INTERPRETER_TESTS",
        "tails":[src,measured,ambiguity],
        "heads":[
            "method:triage-source-change-region-not-truth",
            "method:choose-first-test-from-measured-cost",
            "method:choose-second-test-after-real-triage",
            "method:optional-third-test-after-real-focused-pass",
            "method:STOP-if-further-test-cost-exceeds-expected-benefit",
        ],
        "source_train_cases":frozen["source_train_case_count"],
        "source_dev_cases":frozen["source_dev_case_count"],
        "frozen_candidate_value_policies":frozen[
            "candidate_action_policies_tested"],
        "selected_force_triage":frozen["selected_force_triage"],
        "utility_scores_author_defined":True,
        "no_semantic_graph_authority_promoted":True,
    }
    observed={
        "id":"outcome:source-real-second-test-and-cost-versus-simple-full",
        "type":"REAL_DOCKER_SOURCE_MEASUREMENTS_WITH_CONDITIONAL_FOLLOWUP",
        "tails":[src,measured,ambiguity,*tokens],
        "heads":[
            "outcome:actual_selected_software_tests",
            "outcome:observed_seeded_faults_found",
            "risk:synthetic_bugs_missed",
            "risk:benign_source_changes_misclassified",
            "cost:real_test_calls_and_wall_time",
            "comparison:strong_full_suite_baseline",
            "frontier:independent-real-repository-issues-not-yet_proven",
        ],
        "cases":len(cases),
        "selected":active,
        "single_full_baseline":full,
        "conditional_triage_baseline":triage,
        "exhaustive_baseline":exhaustive,
        "selected_real_second_test_cases":active[
            "cases_with_real_second_test"],
        "selected_real_third_test_cases":active["cases_with_third_test"],
        "artificial_bug_misses_preserved":active["seeded_defects_missed"],
        "false_alarm_count_preserved":active["clean_false_alarms"],
        "detected_bugs_not_a_real_world_generalization_result":True,
        "score_in_author_units_not_dollars":True,
        "outside_effectful_work_done":0,
    }
    result={
        "schema":SCHEMA,
        "frozen_policy_sha256":frozen["receipt_sha256"],
        "actual_test_report_sha256":report["receipt_sha256"],
        "vertices":vertices,"hyperedges":[constructed,observed],
        "second_test_traces_reconciled_to_real_receipts":True,
        "strong_single_full_control_measured":True,
        "full_data_source_asymmetric_visibility_preserved":True,
        "private_user_text_not_committed_to_source":True,
        "novel_general_software_repair_proven":False,
        "real_user_preferences_or_language_truth_proven":False,
        "new_external_tool_permissions":0,
        "external_effects_executed":0,
        "authority":"NONE",
    }
    result["receipt_sha256"]=learn.digest(result)
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
        out=build(json.loads(args.frozen.read_text()),
                  json.loads(args.trial.read_text()),args.repo)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        selected=out["hyperedges"][1]["selected"]
        print(json.dumps({
            "status":"SOURCE_RECONCILED_CONDITIONAL_TEST_EVIDENCE",
            "real_selected_tests":selected["real_tests_executed"],
            "real_second_test_cases":selected["cases_with_real_second_test"],
            "seeded_faults_found":selected["seeded_defects_detected"],
            "seeded_faults_missed":selected["seeded_defects_missed"],
            "real_test_seconds":selected["measured_source_wall_seconds"],
            "receipt_sha256":out["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,trial.HOLD,runner.SandboxError,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)

if __name__=="__main__":main()
