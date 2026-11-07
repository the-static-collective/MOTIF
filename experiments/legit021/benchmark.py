"""MOTIF-LEGIT-021: THE APERTURE INVENTOR — executable research experiment.

The previous LEGIT-020 can preserve several interpretations and
mathematically evaluate known views. This experiment lets the system
GENERATE a new measurement *source* from a bounded graph grammar,
rather than only selecting between previously named viewpoints.

It tests:
  1. The all-path equivalence gap of real Dogram graph carriers.
  2. Enumerative discovery of new source-graph questions (triangle, claw,
     four-cycle) rather than hardcoding them as search candidates.
  3. Adaptive questions that distinguish three worlds under a frozen
     graph hypothesis set, compared with exact classical DP optimum.
  4. Research generation transfer: learned questions reused on later
     generated graphs, compared with scratch search and independent
     exhaustive source enumeration.
  5. Z3 discovery of a minimal signedness counterexample AND formal
     refusal when no numeric probe distinguishes equivalent operations.
  6. Actual LEGIT-020 APERTURE raw-source preservation and model/HOLD
     boundaries.

All graph problems are researcher authored. This is known mathematics,
not a novel theorem, general program invention or independently
confirmed compounding of research productivity.
"""
from __future__ import annotations

from pathlib import Path
from statistics import mean,median
from time import perf_counter_ns,process_time_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit020"))
from aperture import open_aperture,mathalize,receipt_hash

from graph_inventor import (
    HOLD,cycles,dogram_calibration,grammar,characterize,
    count,reference_count,all_path_collision,invent_separator,
    independent_minimal_separator,adaptive_aperture_lift,classical_optimal_tree,
    selected_action_tree,execute_tree
)
from math_apertures import (
    invent_bitvector_counterprobe,indistinguishable_math,
    perspective_lattice_for_worlds,verify_dogram_source
)

STATUS="HOLD_RESEARCH_ONLY_BOUNDED_APERTURE_DISCOVERY_NOT_NEW_MATH"

CALIBRATION=(
    ("PATH_COLLISION_TRIANGLE", (cycles(6),cycles(3,3))),
    ("DOGRAM_PATH_COLLISION_BRANCH", dogram_calibration()),
)
VALIDATION=(
    ("NEW_7_VERTEX_TRIANGLE", (cycles(7),cycles(3,4))),
    ("NEW_8_VERTEX_TRIANGLE", (cycles(8),cycles(3,5))),
    ("NEW_8_VERTEX_SQUARE", (cycles(8),cycles(4,4))),
)

def time_ms(fn,repeats=5):
    wall=[]
    cpu=[]
    for _ in range(repeats):
        start=perf_counter_ns()
        startcpu=process_time_ns()
        fn()
        wall.append(round((perf_counter_ns()-start)/1e6,6))
        cpu.append(round((process_time_ns()-startcpu)/1e6,6))
    return {
        "wall_ms":wall,"cpu_ms":cpu,
        "median_wall_ms":median(wall),
        "median_cpu_ms":median(cpu),
        "repeats":repeats
    }

def experiment_on_pair(name,targets):
    # This proof prevents a finite sample of colliding paths from being
    # mislabeled "same for every path" by a language generator.
    prior=all_path_collision(targets)
    source=invent_separator(targets)
    candidate=source["first_separating_probe"]
    if not candidate:
        raise HOLD("This fixture must require an actually invented probe")
    return {
        "name":name,
        "same_under_every_finite_path":prior,
        "new_probe":source,
        "verified_separating_source_type":candidate,
        "does_not_establish_carrier_identity_from_path_equality":True,
    }

def reuse_search(targets,learned):
    """Reuse verified created probes, then search whole same grammar.

    The strong scratch control and independent classical full assignment
    validator still see the SAME set of admissible questions. Reuse
    changes evaluation ORDER, not allowed mathematics.
    """
    tried=set()
    trace=[]
    def ask(p,from_bank):
        if p in tried:return False
        tried.add(p)
        vals=tuple(count(p,t) for t in targets)
        trace.append({
            "probe":characterize(p),
            "origin":"PRIOR_GENERATION" if from_bank else "NEW_ENUMERATION",
            "values":list(vals),
            "separates":len(set(vals))>1,
        })
        return len(set(vals))>1
    selected=None
    for p in learned:
        if ask(p,True):
            selected=p
            break
    if selected is None:
        for p in grammar():
            if ask(p,False):
                selected=p
                break
    independent,values,checked=independent_minimal_separator(targets)
    if selected is not None:
        if (tuple(count(selected,t) for t in targets)!=
            tuple(reference_count(selected,t) for t in targets)):
            raise HOLD("Novel/refreshed probe contradicted independent oracle")
    return {
        "selected":characterize(selected) if selected else None,
        "selected_matches_grammar_global_minimum":selected==independent,
        "reference_oracle_minimum":characterize(independent) if independent else None,
        "original_prior_probes_reused":[characterize(p) for p in learned],
        "probes_evaluated_including_prior_failures":len(trace),
        "actual_trace":trace,
        "strong_exhaustive_classical_comparison_probes":checked,
        "does_not_declare_open_world_discovery":True,
    }

def active_world_trial():
    states=(cycles(8),cycles(3,5),cycles(4,4))
    witness=all_path_collision(states)
    lattice=perspective_lattice_for_worlds(states)
    adaptive=selected_action_tree(states)
    replay=[execute_tree(adaptive["tree"],carrier) for carrier in states]
    if any(row["resolved_world_index"]!=i or row["unresolved"]
           for i,row in enumerate(replay)):
        raise HOLD("Constructed decision tree failed to identify worlds")
    measured=sum(len(x["trace"]) for x in replay)
    classical=classical_optimal_tree(states)
    if measured<classical["minimum_sum_questions"]:
        raise HOLD("Algorithm allegedly beats mathematical optimum")
    return {
        "world_description":["C8","C3_PLUS_C5","C4_PLUS_C4"],
        "original_path_aperture_cannot_separate_any_world":witness,
        "Dogram_probe_refinement":lattice,
        "invented_adaptive_tree":adaptive["tree"],
        "inventor_training_search_trace":adaptive["search_trace"],
        "replayed_all_worlds":replay,
        "total_questions_all_three_states":measured,
        "mean_questions_under_declared_uniform_world_prior":measured/len(replay),
        "strong_exact_classical_decision_tree":classical,
        "matches_exact_optimum_question_count":
            measured==classical["minimum_sum_questions"],
        "source_question_language_grammar_pinned":True,
        "uniform_world_prior_is_researcher_assumption":True,
    }

def run():
    source=verify_dogram_source()
    all_patterns=grammar()
    if len(all_patterns)!=10:
        raise HOLD("Unexpected source-graph grammar size")
    original=mathalize(open_aperture("Are these two graphs the same?"))
    if ([x["id"] for x in original["language_to_math_candidates"]] !=
        ["WALK_EQ","CLAW_EQ","ISOMORPHIC"]):
        raise HOLD("APERTURE bridge source was mutated")
    base=[experiment_on_pair(name,target) for name,target in CALIBRATION]
    # Output of genuine previous graph source invention is passed to
    # the next set; no oracle labels are used in probe ordering.
    by_name={r["name"]:r["verified_separating_source_type"] for r in base}
    def get_source(receipt):
        for p in grammar():
            if characterize(p)==receipt:return p
        raise HOLD("Previously discovered source not in current grammar")
    inherited=tuple(get_source(row["verified_separating_source_type"])
                    for row in base)
    if not (characterize(inherited[0])["triangle"]
            and characterize(inherited[1])["three_leaf_star"]):
        raise HOLD("Prior math discovery not actually graph-derived")
    heldout=[]
    for name,targets in VALIDATION:
        certificate=all_path_collision(targets)
        scratch=invent_separator(targets)
        reuse=reuse_search(targets,inherited)
        heldout.append({
            "name":name,
            "all_paths_certified_equal":certificate["same_all_finite_paths"],
            "scratch":scratch,
            "with_actual_prior_generated_apertures":reuse,
            "same_target_problems_and_allowed_question_grammar":True,
        })
    branching_pair=heldout[-1]
    if (not branching_pair["scratch"]["first_separating_probe"]["four_cycle"] or
        not branching_pair["with_actual_prior_generated_apertures"]["selected"]["four_cycle"]):
        raise HOLD("Must discover genuinely NEW four-cycle observation")
    tree=active_world_trial()
    # This trial is a source-language boundary, NOT a fabricated new
    # mathematical identity: every pattern with <=4 vertices collides,
    # but the distinct graph carriers differ in component count. Let
    # the generic grammar grow one approved arity and re-test.
    lift_carriers=(cycles(10),cycles(5,5))
    lift_path_certificate=all_path_collision(lift_carriers)
    aperture_lift=adaptive_aperture_lift(lift_carriers)
    if (not aperture_lift["lift_needed"] or
        not aperture_lift["new_separator"]["five_cycle"] or
        aperture_lift["new_mathematical_observation_counts"]!=[0,20]):
        raise HOLD("Arity-5 perspective generator failed exact graph test")
    bv=invent_bitvector_counterprobe()
    no_distinction=indistinguishable_math()
    identical=invent_separator((cycles(6),cycles(6)))
    if identical["first_separating_probe"] is not None:
        raise HOLD("Inventor manufactured a distinction between identical worlds")
    report={
        "schema":"motif.legit021.aperture-inventor.v1",
        "experiment":"MOTIF-LEGIT-021",
        "title":"THE_APERTURE_INVENTOR",
        "status":STATUS,
        "source_modules":{
            "aperture_protocol":"LEGIT020/APERTURE",
            "math_and_graph_kernel":"PINNED_CANONICAL_DOGRAM",
            "bitvector_proof":"EXTERNAL_Z3_THROUGH_MOTIF",
            "verified_original_Dogram":source,
        },
        "bounded_generated_source_grammar":{
            "connected_simple_undirected_source_graphs_at_most_vertices":4,
            "unlabeled_isomorphism_types":len(all_patterns),
            "actual_grammar":[characterize(x) for x in all_patterns],
            "no_triangle_star_or_cycle_templates_in_enumerator":True,
            "minimum_is_only_within_declared_grammar":True,
        },
        "raw_language_aperture":original,
        "two_calibration_invention_trials":base,
        "actual_previous_generation_apertures":[characterize(x) for x in inherited],
        "validation_trials":heldout,
        "active_three_world_mathematical_viewpoint":tree,
        "blind_below_four_vertices_therefore_expand_probe_language":{
            "all_length_path_collision":lift_path_certificate,
            "source_test_from_smaller_grammar_to_bounded_larger_grammar":
                aperture_lift,
        },
        "bitvector_new_counterprobe":bv,
        "bitvector_provably_no_possible_numeric_separator":no_distinction,
        "identical_world_abstention":{
            "input":"C6 vs C6",
            "candidate_pattern_count":len(all_patterns),
            "invented_separator":identical["first_separating_probe"],
            "correct_behavior":"HOLD_PROVABLY_NO_SEPARATION_WITHIN_REGISTERED_FINITE_GRAMMAR",
        },
        "measured_planner_comparison":{
            "unmodified_fixed_probe_order":False,
            "calibration_learned_apertures_are_really_reused":True,
            "transfer_proposal_counts_before_independent_proof":[
                {"name":d["name"],
                 "scratch":d["scratch"]["search_probes_inspected"],
                 "reuse":d["with_actual_prior_generated_apertures"]
                         ["probes_evaluated_including_prior_failures"]}
                for d in heldout
            ],
            "strong_classical_exact_minimality_compared":True,
            "strong_classical_exact_decision_tree_compared":True,
            "independent_external_challenge_author":False,
            "independently_demonstrated_recursive_compounding":False,
            "new_historical_math_proven":False,
            "theorem_graph_path_collision_known_from_Dogram":True,
            "previously_missing_probe_generated_within_declared_grammar":True,
        },
        "limits":{
            "assumed_carrier_worlds_are_known_finite_set":True,
            "problem_distribution_curated_by_experiment_author":True,
            "source_language_and_bitvector_ops_handwritten":True,
            "max_graph_query_arity_researcher_declared":5,
            "grown_source_language_does_not_prove_open_ended_invention":True,
            "not_general_mathematical_operation_invention":True,
            "public_SyGuS_benchmark_not_rerun":True,
            "automatic_source_merge_or_deploy":False,
            "human_intent_not_inferred_from_probe":True,
            "world_facts_not_established_by_language_parser":True,
        },
    }
    return report

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python experiments/legit021/benchmark.py [--emit]")
    report=run()
    if sys.argv[1:]:
        Path("/tmp/motif-legit021-aperture-inventor.json").write_text(
            json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment":report["experiment"],
        "status":report["status"],
        "generated_pattern_count":report["bounded_generated_source_grammar"]
                                  ["unlabeled_isomorphism_types"],
        "calibration_discoveries":[
            {"name":x["name"],"source":x["verified_separating_source_type"]}
            for x in report["two_calibration_invention_trials"]],
        "new_heldout_discoveries":[{
            "name":x["name"],
            "source":x["scratch"]["first_separating_probe"],
            "new_apertures_reused":x["with_actual_prior_generated_apertures"]
                                  ["probes_evaluated_including_prior_failures"],
            "scratch_probes":x["scratch"]["search_probes_inspected"]
            }for x in report["validation_trials"]],
        "adaptive_worlds":report["active_three_world_mathematical_viewpoint"]
                           ["mean_questions_under_declared_uniform_world_prior"],
        "strong_exact_classical_optimum":report["active_three_world_mathematical_viewpoint"]
                            ["strong_exact_classical_decision_tree"]
                            ["minimum_mean_questions"],
        "grown_aperture":report[
            "blind_below_four_vertices_therefore_expand_probe_language"
        ]["source_test_from_smaller_grammar_to_bounded_larger_grammar"]
        ["new_separator"],
        "signedness_counterexample":report["bitvector_new_counterprobe"]
                                     ["witness_unsigned_x"],
        "no_mathematical_separator_for_double":report[
            "bitvector_provably_no_possible_numeric_separator"][
            "different_observation_possible"],
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
