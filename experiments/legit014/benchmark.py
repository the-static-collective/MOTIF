"""LEGIT-014: verified feedback-driven self-improvement trial.

An examiner profiles actual generated code, proposes small source edits,
uses external Z3 plus exhaustive finite regression, measures real CPU
wall time on *training-only* graphs, rejects candidates that do not
improve the measured objective, and mutates the best candidate in a
second round. Only the frozen winner is examined on fresh heldout graphs.

The gate requires a material, repeatable improvement over BOTH the
existing generated solver and a separately implemented strong classical
solver. A failed gate is a valid NEGATIVE RESULT; no software is promoted.
This is researcher-authored synthetic data, not externally blind testing.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from math import isfinite
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from itertools import product
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit013"))
sys.path.insert(0,str(HERE.parent/"legit012"))
sys.path.insert(0,str(HERE))
from graph_reference import cases,check_graph,make_graph,all_states,scan
from classical_control import StrongClassicalDP
from examiner import actual_parent as previous_012
# The LEGIT-013 module prepends legacy directories to sys.path during import.
# Put this experiment first *after* loading it to avoid old transform.py.
sys.path.insert(0,str(HERE))
from transform import (
    SCHEMA,HOLD,digest,get_parent,catalog,_make_columns,
    train_profile,propose_round_one,next_round,compile_proved,
    independent_regression,validate,
)

SELECTION_REPEATS=5
HELDOUT_REPEATS=11
THRESHOLD=0.08
MIN_WINS=10
MAX_STRESS_REGRESSION=0.10

def graph_corpus(start,counts):
    """Disjoint deterministic sets. Never pass holdout to the generator."""
    out=[]
    for index,(family,n) in enumerate(counts):
        graph=check_graph(cases(start+index,n))
        out.append((family,graph))
    return out

def training_cases():
    return graph_corpus(81000,
        [("LIGHT",8+(i%4)*8) for i in range(12)]+
        [("MEDIUM",32+(i%4)*10) for i in range(12)]+
        [("DENSE",64+(i%4)*12) for i in range(12)])

def unseen_cases():
    return graph_corpus(91000,
        [("LIGHT",8+(i%4)*8) for i in range(24)]+
        [("MEDIUM",32+(i%4)*12) for i in range(32)]+
        [("DENSE",72+(i%4)*12) for i in range(24)])

def timed_batch(fn,normalized):
    t=perf_counter_ns()
    for _,graph in normalized:
        fn(graph)
    return (perf_counter_ns()-t)/1_000_000

def timed_family(fn,normalized,repeat=5):
    """Paired per-family repeats, descriptive not inferentially robust."""
    durations=[]
    for i in range(repeat):
        durations.append(timed_batch(fn,normalized))
    return round(median(durations),5)

def measure(engines,graphs,repeats):
    """Deterministically rotate call order; keep every raw timing sample."""
    if repeats<3:raise HOLD("Insufficient repeated measures")
    names=sorted(engines)
    samples={k:[] for k in names}
    for i in range(repeats):
        order=names[i%len(names):]+names[:i%len(names)]
        if i%2:order=list(reversed(order))
        for name in order:
            samples[name].append(round(timed_batch(engines[name],graphs),6))
    return {
        key:{"median_ms":round(median(vals),6),
             "min_ms":min(vals),"max_ms":max(vals),
             "samples_ms":vals}
        for key,vals in samples.items()}

def make_arms(methods,cols,strong):
    old_012=previous_012().solve
    old_013=get_parent().solve
    return {
        "prior_012":lambda graph:old_012(cols,len(methods),graph),
        "prior_013":lambda graph:old_013(cols,len(methods),graph),
        "strong_classical":strong.solve,
    }

def measured_feedback():
    before=perf_counter_ns()
    profiled=train_profile()
    profile_cost_ms=(perf_counter_ns()-before)/1e6
    methods=catalog()
    cols=_make_columns(methods)
    strong=StrongClassicalDP(methods)
    train=training_cases()
    armed=make_arms(methods,cols,strong)
    old_times=measure(armed,train,SELECTION_REPEATS)
    compiled={}
    reviews=[]
    known=set()
    cost_proof_ms=0.
    chosen_id=None

    def experiment(plan,round_id):
        nonlocal cost_proof_ms
        validate(plan)
        key=digest(plan)
        if key in known:return
        known.add(key)
        started=perf_counter_ns()
        try:
            built=compile_proved(plan)
            regression=independent_regression(methods,cols,built)
        except (HOLD,RuntimeError) as exc:
            reviews.append({"id":key,"round":round_id,"plan":plan,
                            "status":"REJECT_INCORRECT_OR_UNPROVED",
                            "reason":type(exc).__name__,
                            "error_detail":str(exc)[:400]})
            return
        elapsed=(perf_counter_ns()-started)/1e6
        cost_proof_ms+=elapsed
        compiled[key]=built
        timed=measure({"proposal":lambda graph:built["function"](
            cols,len(methods),graph)},train,SELECTION_REPEATS)["proposal"]
        prior=old_times["prior_013"]["median_ms"]
        strong_time=old_times["strong_classical"]["median_ms"]
        reviews.append({
            "id":key,"round":round_id,"plan":plan,
            "status":"CORRECT_BUT_TIME_UNPROVEN",
            "finite_proof":regression,
            "z3_rules_checked":len(plan["rules"]),
            "proof_and_compilation_ms":round(elapsed,5),
            "training_median_ms":timed["median_ms"],
            "training_samples_ms":timed["samples_ms"],
            "training_speed_ratio_vs_prior":round(
                prior/max(timed["median_ms"],1e-12),6),
            "training_speed_ratio_vs_strong_classical":round(
                strong_time/max(timed["median_ms"],1e-12),6),
        })

    first=propose_round_one(profiled)
    for plan in first:
        experiment(plan,"ROUND_ONE_FROM_REAL_EXECUTION_TRACE")
    # Adversarial negative control: attractive-looking but mathematically
    # invalid "zero parent -> use column". Z3 must construct a concrete
    # counterexample, and the resulting source must NEVER be timed or run.
    experiment({"parent":"FIRST","rules":[["P_ZERO","COLUMN"]]},
               "ROUND_ONE_INJECTED_UNSOUND_FALSIFIER")
    correct=[v for v in reviews if v["status"]=="CORRECT_BUT_TIME_UNPROVEN"]
    if not correct:
        raise HOLD("Nothing formally valid; cannot invent a second round")
    seed=min(correct,key=lambda x:(x["training_median_ms"],x["id"]))
    second=next_round(seed["plan"],profiled,known)
    for plan in second:
        experiment(plan,"ROUND_TWO_MUTATED_FROM_MEASURED_BEST")
    correct=[v for v in reviews if v["status"]=="CORRECT_BUT_TIME_UNPROVEN"]
    winner=min(correct,key=lambda x:(x["training_median_ms"],x["id"]))
    # IMPORTANT: this is frozen BEFORE touching any test examples.
    selected=compiled[winner["id"]]
    for row in reviews:
        if row["status"]!="CORRECT_BUT_TIME_UNPROVEN":continue
        row["status"]=("TRAINING_FROZEN_WINNER" if row["id"]==winner["id"]
                       else "REJECT_TRAINING_SLOWER_ALTERNATIVE")

    return {"selected":selected,
            "plan_id":winner["id"],
            "profile":profiled,
            "profile_cost_ms":profile_cost_ms,
            "proof_cost_ms":cost_proof_ms,
            "training_reference":old_times,
            "training_reviews":reviews,
            "trial_candidates_proposed":len(known),
            "trial_candidates_proved":len(compiled),
            "round_two_new_plans":len(second),
            "train_graphs":len(train),
            "model_selection_used_holdout":False,
            "methods":methods,"columns":cols,
            "strong":strong}

def _fraction(base,candidate):
    if base<=0:return None
    return (base-candidate)/base

def evaluate():
    selected=measured_feedback()
    if not selected["model_selection_used_holdout"] is False:
        raise AssertionError("Incorrect holdout leakage flag")
    methods=selected["methods"]
    cols=selected["columns"]
    strong=selected["strong"]
    new=selected["selected"]["function"]
    holdout=unseen_cases()
    arms=make_arms(methods,cols,strong)
    arms["candidate"]=lambda graph:new(cols,len(methods),graph)

    # Freeze the selection and source hash before constructing any heldout
    # performance measurements. The heldout graph distribution is separate.
    frozen_sha=selected["selected"]["source_sha256"]
    proof=selected["selected"]["proof"]
    verified_nodes=0
    mismatches=0
    operation_counts=defaultdict(int)
    for _,graph in holdout:
        outputs={}
        for name,execute_arm in arms.items():
            result,info=execute_arm(graph)
            outputs[name]=result
            if name=="candidate":
                operation_counts["generated_intersections"]+=info["bitset_intersections"]
                operation_counts["generated_shortcuts"]+=info["guarded_skips"]
            if name=="strong_classical":
                operation_counts["strong_intersections"]+=info["bitset_intersections"]
                operation_counts["strong_shortcuts"]+=info["branch_skips"]
        if not all(result==outputs["prior_012"] for result in outputs.values()):
            mismatches+=1
            raise AssertionError("Proof-passing algorithm changed a heldout answer")
        verified_nodes+=len(graph)
    # Match the old generation over EVERY possible 3-valued partial state,
    # not just whatever occurred on the heldout corpus.
    full=check_graph(make_graph("AllPossiblePartialEvidence",all_states()))
    gold,_=scan(methods,full)
    ours,_=new(cols,len(methods),full)
    if gold!=ours or len(gold)!=6561:
        raise AssertionError("Full 3**8 truth lattice mismatch")

    timed=measure(arms,holdout,HELDOUT_REPEATS)
    families={}
    for family in ("LIGHT","MEDIUM","DENSE"):
        subset=[x for x in holdout if x[0]==family]
        families[family]={
            "graphs":len(subset),
            "candidate_median_ms":timed_family(arms["candidate"],subset),
            "strong_median_ms":timed_family(arms["strong_classical"],subset),
            "prior_median_ms":timed_family(arms["prior_013"],subset),
        }
    can=timed["candidate"]["median_ms"]
    speedup_prior=_fraction(timed["prior_013"]["median_ms"],can)
    speedup_strong=_fraction(timed["strong_classical"]["median_ms"],can)
    wins={
        b:sum(x<y for x,y in
              zip(timed["candidate"]["samples_ms"],timed[b]["samples_ms"]))
        for b in ("prior_013","strong_classical")
    }
    per_family_acceptable=all(
        v["candidate_median_ms"]<=v["strong_median_ms"]*(1+MAX_STRESS_REGRESSION)
        for v in families.values())
    gates={
        "correct_all_cases":mismatches==0 and verified_nodes>0,
        "external_z3_proved":proof["all_rules_verified"],
        "train_test_isolation":True,
        "at_least_8_percent_faster_vs_prior":speedup_prior is not None and speedup_prior>=THRESHOLD,
        "at_least_8_percent_faster_vs_strong_classical":speedup_strong is not None and speedup_strong>=THRESHOLD,
        "win_at_least_10_of_11_repeats_vs_both":all(v>=MIN_WINS for v in wins.values()),
        "no_family_regression_gt_10_percent_vs_strong":per_family_acceptable,
        "independently_authored_test_corpus":False,
        "production_auto_merge":False,
    }
    internal_eligible=all(gates[x] for x in (
        "correct_all_cases","external_z3_proved","train_test_isolation",
        "at_least_8_percent_faster_vs_prior",
        "at_least_8_percent_faster_vs_strong_classical",
        "win_at_least_10_of_11_repeats_vs_both",
        "no_family_regression_gt_10_percent_vs_strong",
    ))
    status=("RETAIN_RESEARCH_CANDIDATE_FOR_INDEPENDENT_REVIEW" if internal_eligible
            else "HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT")
    # Keep objective honest: even a retaining research candidate NEVER
    # bypasses human approval, independent evaluation or formal scope.
    result={
        "experiment":"MOTIF-LEGIT-014",
        "research_question":"CAN_MOTIF_REJECT_SLOW_FORMALLY_VALID_SELF_REWRITES",
        "source":"ACTUAL_GENERATED_LEGIT013_PYTHON",
        "source_sha256":get_parent().__file__ and
                         sha256(Path(get_parent().__file__).read_bytes()).hexdigest(),
        "method":"TWO_ROUND_TRACE_GUIDED_Z3_PROVED_FEEDBACK_TRIAL",
        "training_profile_counts":selected["profile"]["support"],
        "training_graphs":selected["train_graphs"],
        "feedback_rounds":2,
        "proposed_candidate_count":selected["trial_candidates_proposed"],
        "formally_proved_candidate_count":selected["trial_candidates_proved"],
        "round_two_variants_created_from_measured_feedback":selected["round_two_new_plans"],
        "training_reviews":selected["training_reviews"],
        "training_reference_medians":{k:v["median_ms"] for k,v in selected["training_reference"].items()},
        "frozen_selected_source_sha256":frozen_sha,
        "frozen_selected_plan":selected["selected"]["plan"],
        "frozen_source_external_smt_receipt":proof,
        "heldout_graphs":len(holdout),
        "heldout_states":verified_nodes,
        "full_partial_truth_lattice_checked":len(full),
        "heldout_incorrect_outputs":mismatches,
        "heldout_repeated_ms":timed,
        "heldout_family_timings_ms":families,
        "speedup_vs_prior_013_median_fraction":round(speedup_prior,6),
        "speedup_vs_optimized_classical_median_fraction":round(speedup_strong,6),
        "wins_out_of_11_repeats":wins,
        "heldout_operation_counts":dict(operation_counts),
        "gate":gates,
        "internal_retain_gate_passed":internal_eligible,
        "selection_used_holdout_data":False,
        "independently_authored_external_challenge":False,
        "source_proved_general_Python_safe":False,
        "statistically_independent_RCT":False,
        "performance_proof_of_general_advantage":False,
        "automatic_merge_or_deploy":False,
        "real_world_authority":False,
        "status":status,
    }
    artifact={
        "schema":SCHEMA,
        "status":"DRAFT_NO_AUTOMATIC_PROMOTION",
        "generated_source_sha256":frozen_sha,
        "source_plan":selected["selected"]["plan"],
        "source_proof":proof,
        "training_trial_receipt":selected["training_reviews"],
        "heldout_status":status,
        "heldout_passed_internal_speed_gate":internal_eligible,
        "human_review_required":True,
        "independent_external_validation_complete":False,
        "automatic_promotion_permitted":False,
        "real_world_authority":False,
    }
    return result,{"source":selected["selected"]["source"],"manifest":artifact}

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("python benchmark.py [--emit]")
    result,artifact=evaluate()
    if sys.argv[1:]:
        Path("/tmp/motif-legit014-candidate-rewrite.py").write_text(
            artifact["source"],encoding="utf-8")
        Path("/tmp/motif-legit014-trial-manifest.json").write_text(
            json.dumps(artifact["manifest"],indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
