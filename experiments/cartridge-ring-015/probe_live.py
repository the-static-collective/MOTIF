"""RING-015: deliberate LIVE two-step Docker demonstration (not selected winner).

Our dev-selected AUTO policy can rationally choose the stronger FULL test
first. To independently exercise the *conditional action mechanism*, this
script forces a permitted initial TRIAGE experiment (research intervention)
on completely new source copies and lets the ordinary calibrated
cue-conditioned planner select ACTUAL next Docker tests afterward.

This is a method capability demonstration, NOT evidence that forcing the
first observation is optimal or a naturally discovered new test strategy.

The code does not infer correctness from changing AST shape; it runs
a subsequent focused or full source test on the copied RING-013 program.
No private user data, network, GitHub writes or external effects.
"""
from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path

import fixtures,learn,policy,runner,trial

SCHEMA="motif.ring015.live-forced-first-observation-followups.v1"
NEW_REVIEWED_CASES=(
    ("live-math-a",("posterior_uninformed",)),
    ("live-control-a",("budget_nonconservation",)),
    ("live-benign-a",("benign_control",)),
)


def run(frozen,repo_root):
    repo=Path(repo_root).resolve()
    trial.verify_frozen(frozen,repo)
    # This is a researcher-initiated *diagnostic trial*, deliberately
    # distinct from the frozen autonomous strategy's selected mode.
    rows=[]
    with tempfile.TemporaryDirectory(prefix="motif-ring015-live-followup-") as d:
        root=Path(d);root.chmod(0o755)
        folder=root/"cases";folder.mkdir(mode=0o755)
        cases=fixtures.make(folder,repo,NEW_REVIEWED_CASES)
        for x in cases:
            cid=x["case_id"]
            executed=[]
            def do(phase):
                receipt=runner.observe(folder,cid,phase,repo)
                executed.append(receipt)
                return receipt
            result=policy.route(
                frozen["model_likelihoods_derived_from_train_only"],
                frozen["selected_settings"],do,force_triage=True)
            if executed!=result["receipts"]:
                raise ValueError("Real test return differs from planner action log")
            rows.append({
                "case":cid,
                "seeded_defect_evaluator_only":x["seeded_defect"],
                "planner_first_action_experimenter_forced":"TRIAGE",
                "subsequent_action_selected_after_real_first_test":True,
                "real_executed_phase_sequence":[z["phase"] for z in executed],
                "real_docker_test_receipts":executed,
                "actual_failure_found":result["saw_actual_failure"],
                "seconds":result["actual_test_seconds"],
                "not_an_independent_benchmark_of_decision_superiority":True,
                "outside_actions_executed":0,
            })
    final={
        "schema":SCHEMA,
        "status":"LIVE_CONDITIONAL_REAL_SOURCE_TESTS_ACTUALLY_EXECUTED",
        "source_frozen_value_policy_sha256":frozen["receipt_sha256"],
        "auto_policy_originally_selected_force_triage":frozen[
            "selected_force_triage"],
        "forced_first_action_is_developer_intervention_not_autonomous_selection":True,
        "source_cases":rows,
        "actual_second_source_test_cases":sum(
            len(x["real_executed_phase_sequence"])>=2 for x in rows),
        "live_first_test_receipts_precede_subsequent_test_invocation":True,
        "all_tests_approved_no_network_readonly":True,
        "novel_human_software_bug_detection_proven":False,
        "outside_actions_executed":0,
        "authority":"NONE",
    }
    final["receipt_sha256"]=learn.digest(final)
    return final


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,
                   default=Path(__file__).resolve().parents[2])
    p.add_argument("--frozen",required=True,type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        report=run(json.loads(a.frozen.read_text()),a.repo)
        if a.out:
            a.out.parent.mkdir(parents=True,exist_ok=True)
            a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        print(json.dumps({
            "schema":report["schema"],
            "actual_second_test_cases":report[
                "actual_second_source_test_cases"],
            "observed_real_phase_sequences":[
                x["real_executed_phase_sequence"] for x in report["source_cases"]],
            "receipt_sha256":report["receipt_sha256"],
        },sort_keys=True))
    except (trial.HOLD,runner.SandboxError,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)

if __name__=="__main__":main()
