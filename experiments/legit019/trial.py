"""LEGIT-019: two-frontier attempted falsification, without invented novelty.

FRONTIER ONE: the symbolic conjecture engine autonomously proposes
equalities from small probes, passes each to external Z3 to find either
a full 64-bit proof or a concrete counterexample, and injects the
counterexample into subsequent probes. This establishes theorem *proof
within the encoded bitvector theory*, NOT historical mathematical novelty.

FRONTIER TWO: the engine carries its proof-certified identity library
into multiple original independently authored 2017 SyGuS public
benchmarks. Same candidate grammar, same search budget, and strong
observational deduplication in BOTH control and treatment. Only the
proven mathematical rewrite capability differs. It tests 10-example
training then freezes source before opening the public 100-example
corpus. Having an external challenge AUTHOR does not mean independently
BLIND adjudication; our own code and runner perform the experiment.

No open-ended invention or causal compounding is precommitted as true.
The acceptance gates may fail. No external actions or promotion.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from statistics import median
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from corpus import load,train_only,external_test_for,provenance,HOLD
from algebra import conjecture_mine,verified_rewrites,prove_equal,val
from search import search,frozen_public_evaluation,as_tuple

REPEATS=3
STATUS="RESEARCH_HOLD_UNVERIFIED_HISTORICAL_NOVELTY_AND_COMPOUNDING"

def run():
    tasks=load()
    sources=provenance(tasks)
    training=train_only(tasks)
    # All source training and theorem discovery happens before the
    # external 100-example challenge is accessed through the task API.
    proofs=conjecture_mine()
    rewrites=verified_rewrites(proofs)
    frozen={}
    for identifier,rows in training:
        runs={}
        for arm in ("UNASSISTED","WITH_SELF_PROVED_LEMMAS"):
            history=[search(rows,rewrites if arm!="UNASSISTED" else ())
                     for i in range(REPEATS)]
            key=("program","solved_10_training_examples")
            if any(tuple(row[x] for x in key)!=
                   tuple(history[0][x] for x in key) for row in history):
                raise HOLD("Nondeterministic search altered output program")
            observation=dict(history[0])
            observation["raw_search_runs"]=[
                {"wall_ms":r["wall_ms"],"cpu_ms":r["cpu_ms"],
                 "candidates_evaluated":r["candidates_evaluated"]}
                for r in history]
            observation["median_wall_ms"]=round(
                median(r["wall_ms"] for r in history),6)
            observation["median_cpu_ms"]=round(
                median(r["cpu_ms"] for r in history),6)
            observation["no_external_source_100_examples_used"]=True
            runs[arm]=observation
        frozen[identifier]=runs
    # SOURCE DECISIONS ARE NOW FROZEN before ANY _100 examples are
    # extracted. Public benchmark source was present in fixture,
    # hence this is architectural separation, NOT cryptographic blinding.
    frozen_hash=sha256(json.dumps(
        {str(i):{
            arm:{"program":r["program"],
                 "candidates_evaluated":r["candidates_evaluated"]}
            for arm,r in arms.items()
        }for i,arms in frozen.items()},sort_keys=True).encode()).hexdigest()
    external=external_test_for(tasks,frozen)
    assessed={}
    for identifier in frozen:
        assessed[identifier]={}
        for arm in ("UNASSISTED","WITH_SELF_PROVED_LEMMAS"):
            assessed[identifier][arm]=frozen_public_evaluation(
                frozen[identifier][arm],external[identifier])
    wins=[]
    for identifier,arms in assessed.items():
        a=arms["UNASSISTED"]
        b=arms["WITH_SELF_PROVED_LEMMAS"]
        if b["solved"] and not a["solved"]:
            wins.append(identifier)
    self_proved_count=len(proofs["z3_formal_proved"])
    actual_refutations=len(proofs["z3_formal_refuted"])
    total_compute_no=sum(frozen[i]["UNASSISTED"]["median_cpu_ms"]
                         for i in frozen)
    total_compute_treated=sum(
        frozen[i]["WITH_SELF_PROVED_LEMMAS"]["median_cpu_ms"]
        for i in frozen)
    gates={
        "actual_third_party_SMT_proofs":self_proved_count>=1,
        "actual_SMT_counterexamples":actual_refutations>=1,
        "externally_authored_public_math_challenges":True,
        "historically_novel_mathematical_theorem_independently_certified":False,
        "competition_benchmark_adjudication_blinded_by_external_organizer":False,
        "matched_research_search_language_and_budget":True,
        "second_generation_beats_first_on_entire_published_test_for_at_least_one_task":bool(wins),
        "second_generation_end_to_end_proof_cost_and_search_beat_control":False,
        "actually_adopted_research_upgrade_causally_enables_later_new_invention":False,
        "full_human_research_labor_accounted":False,
        "external_operator_verified_compounding_growth":False,
        "software_auto_deploy_permitted":False,
    }
    result={
        "schema":"motif.independent-math-and-compounding-challenge.v1",
        "experiment":"MOTIF-LEGIT-019",
        "title":"THE_TWO_FRONTIER_FALSIFICATION",
        "status":STATUS,
        "external_benchmark_provenance":sources,
        "math_discovery":{
            "conjecture_search":proofs,
            "verified_rewrite_count":len(rewrites),
            "proved_64bit_equations":self_proved_count,
            "genuine_wrong_conjectures_refuted":actual_refutations,
            "all_generated_hypotheses_from_code_not_handwritten_equations":True,
            "validity_proven_in_64bit_BitVec_not_arbitrary_integers":True,
            "formal_checker_is_external_z3":True,
            "second_exhaustive_8bit_verifier_executed":True,
            "historical_originality_not_tested_or_verified":True
        },
        "equal_budget_research_trial":{
            "train_examples_per_task":10,
            "published_public_test_examples_per_task":100,
            "public_external_task_ids":[t.identifier for t in tasks],
            "repeat_searches_per_arm":REPEATS,
            "same_observational_semantic_deduplication_for_both_arms":True,
            "previously_discovered_proven_rewrites_available_only_to_treatment":True,
            "frozen_train_decisions_sha256":frozen_hash,
            "training_search":{
                str(i):{k:v for k,v in arms.items()}for i,arms in frozen.items()
            },
            "published_external_100_example_results":{
                str(i):arms for i,arms in assessed.items()
            },
            "heldout_full_success_only_with_rewrites":wins,
            "unassisted_total_median_search_cpu_ms":round(total_compute_no,6),
            "assisted_total_median_search_cpu_ms_excluding_proof":round(total_compute_treated,6),
            "Z3_lemma_discovery_and_checker_compute_cost_fully_measured":False,
            "researcher_chose_tasks_after_inspecting_some_training_examples":True,
            "public_100_example_tasks_not_cryptographically_blinded":True,
        },
        "gate":gates,
        "claimed_novel_mathematics":False,
        "claimed_independently_verified_compounding":False,
        "reported_result":"OBSERVED_PROGRAM_SYNTHESIS_AND_THEOREM_PROOFS_ONLY",
        "new_tool_autonomously_promoted":False,
        "external_write_actions":0,
    }
    return result

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python experiments/legit019/trial.py [--emit]")
    result=run()
    if sys.argv[1:]:
        Path("/tmp/motif-legit019-two-frontier-receipt.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment":result["experiment"],
        "status":result["status"],
        "theorem_discovery":{
            "proved":result["math_discovery"]["proved_64bit_equations"],
            "refuted":result["math_discovery"]["genuine_wrong_conjectures_refuted"]},
        "public_SyGuS_100_example_outcomes":{
            i:{arm:{"passed":r["passed"],"of":r["examples"],
                     "solved":r["solved"]}
               for arm,r in arms.items()}
            for i,arms in result["equal_budget_research_trial"]
            ["published_external_100_example_results"].items()},
        "matched_compounding_test":result["gate"][
            "second_generation_beats_first_on_entire_published_test_for_at_least_one_task"
        ],
        "historical_math_novelty_certified":False,
        "independent_research_compounding_certified":False,
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
