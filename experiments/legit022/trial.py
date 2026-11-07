"""LEGIT-022 — Two-episode causal AB test on independently sourced graphs.

1. Reconstruct and verify the ACTUAL LEGIT-021 prior aperture sources.
2. Mine a known mathematical factorization law from TRAINING only and
   check it with a separate exhaustive mathematical evaluator.
3. Compare three same-grammar questions policies on an independently
   originated 1998 graph atlas:
      - canonical exhaustive connected source sequence,
      - reuse actual 021 triangle/claw/square inventions before fallback,
      - classical data-trained greedy priority (strong conventional).
   Also include a deliberately inefficient all-source control to show
   the *known* theorem's redundant disconnected probes.
4. Freeze ALL source/probe selections BEFORE heldout task query results
   are evaluated. Count every actual pair of source homomorphism
   evaluations (including negative attempts) and assignment budgets.
5. Do not infer a historical new theorem or multi-generation autonomous
   compounding from a single matched researcher-administered A/B.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
from pathlib import Path
from statistics import median
from time import perf_counter_ns,process_time_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit021"))
from graph_inventor import (
    grammar,characterize,reference_count,count,normalized,
    independent_minimal_separator
)
from atlas import cohort,verify_prepared,TRAIN_SIZE,TEST_SIZE,HOLD
from theorems import (all_unlabeled_sources_up_to_four,components,
    propose_composition_rule,certify_factorization,challenge_degree_conjecture)

PREVIOUS=HERE.parent/"legit021"/"generated"/"aperture_inventor_report.json"
STATUS="RESEARCH_HOLD_NO_VERIFIED_HISTORICAL_NOVELTY_OR_RECURSIVE_COMPOUNDING"
REPEATS=5

def prior_apertures():
    previous=json.loads(PREVIOUS.read_text(encoding="utf-8"))
    if (previous.get("experiment")!="MOTIF-LEGIT-021"
        or previous.get("measured_planner_comparison",{})
           .get("independently_demonstrated_recursive_compounding") is not False):
        raise HOLD("Old evidence provenance/hold missing")
    recorded=[]
    # Reconstruct actual prior generated source patterns from the
    # previous archive. Do not just accept a self-attested label.
    for item in previous["two_calibration_invention_trials"]:
        recorded.append(item["verified_separating_source_type"])
    recorded.append(previous["validation_trials"][-1]["scratch"]
                    ["first_separating_probe"])
    found=[]
    for expected in recorded:
        matches=[p for p in grammar() if characterize(p)==expected]
        if len(matches)!=1:
            raise HOLD("Previously generated source pattern was forged")
        found.append(matches[0])
    if (len(set(found))!=3 or
        not characterize(found[0])["triangle"] or
        not characterize(found[1])["three_leaf_star"] or
        not characterize(found[2])["four_cycle"]):
        raise HOLD("Wrong predecessor discovery corpus")
    # Check each source with its actual old test graph observations again.
    expected_counts=[(0,12),(48,54),(48,64)]
    from graph_inventor import cycles,dogram_calibration
    original_targets=[
        (cycles(6),cycles(3,3)),dogram_calibration(),
        (cycles(8),cycles(4,4))]
    for pattern,targets,expected in zip(found,original_targets,
                                         expected_counts):
        if tuple(reference_count(pattern,x) for x in targets)!=expected:
            raise HOLD("Historical discovered aperture failed re-evaluation")
    return tuple(found),{
        "prior_experiment":"MOTIF-LEGIT-021",
        "prior_source_receipt_sha256":sha256(PREVIOUS.read_bytes()).hexdigest(),
        "prior_apertures":[characterize(p) for p in found],
        "prior_mathematical_witnesses_replayed":True,
        "prior_source_selection_not_based_on_atlas_heldout":True,
        "previously_historical_math_novelty_claimed":False,
    }

def query_matrix(pair,source):
    # An actual full homomorphism calculation; cannot substitute an
    # external Atlas graph identifier or isomorphism answer.
    return tuple(count(source,carrier) for carrier in pair.graphs)

def training_priority(train,patterns):
    """Strong conventional data-trained cost-sensitive greedy ranking.

    Uses exactly the available training input/output comparisons;
    its policy is frozen for heldout tests. Neither prior 021 nor
    theorem-pruned arm has access to privileged test responses.
    """
    residual=set(range(len(train)))
    remaining=list(patterns)
    ordering=[]
    while remaining:
        ranked=[]
        for probe in remaining:
            covered=sum(query_matrix(train[i],probe)[0]!=
                        query_matrix(train[i],probe)[1]
                        for i in residual)
            # Conservative simple computational cost for the same
            # primitive enumeration used by each arm: n^source_size
            # vertex assignments in each seven-node target.
            attempts=7**probe[0]
            ranked.append((-covered/attempts,
                           probe[0],len(probe[1]),probe))
        chosen=min(ranked)[-1]
        remaining.remove(chosen)
        ordering.append(chosen)
        residual={i for i in residual
                  if query_matrix(train[i],chosen)[0]==
                     query_matrix(train[i],chosen)[1]}
    return tuple(ordering)

def study(pair,ordered,independent=True):
    trace=[]
    found=None
    for probe in ordered:
        outputs=query_matrix(pair,probe)
        separate=outputs[0]!=outputs[1]
        trace.append({
            "source_vertices":probe[0],
            "source_edges":len(probe[1]),
            "probe":characterize(probe),
            "counts":list(outputs),
            "separates":separate,
            "pair_graph_assignment_trials":2*(7**probe[0]),
        })
        if separate:
            found=probe
            if independent:
                observed=tuple(reference_count(probe,g)
                               for g in pair.graphs)
                if outputs!=observed:
                    raise HOLD("Source mathematician and independent counter disagree")
            break
    return {
        "resolved":found is not None,
        "probe":characterize(found) if found else None,
        "number_of_questions":len(trace),
        "two_world_source_hom_calls":2*len(trace),
        "enumerative_assignment_trial_budget":
            sum(row["pair_graph_assignment_trials"] for row in trace),
        "all_actual_probe_answers":trace,
        "all_unsolved_probes_form_explicit_hold":found is None,
    }

def run_policy(test,order):
    return [study(pair,order) for pair in test]

def counterfactual(train,test,priors):
    all_sources=all_unlabeled_sources_up_to_four()
    connected=grammar()
    if len(connected)!=10 or len(all_sources)!=18:
        raise HOLD("Graph grammar identity changed")
    ordered_prior=priors+tuple(p for p in connected if p not in priors)
    trained=training_priority(train,connected)
    control=tuple(connected)
    raw=all_sources
    policies={
        "ALL_UNFILTERED_SOURCE_GRAPHS":raw,
        "CANONICAL_CONNECTED_ONLY":control,
        "LEGIT021_ACQUIRED_APERTURES_FIRST":ordered_prior,
        "STRONG_CLASSICAL_TRAINED_COST_SENSITIVE":trained,
    }
    # frozen BEFORE the first heldout query count is materialized
    frozen={
        arm:[[p[0],[list(e) for e in p[1]]] for p in items]
        for arm,items in policies.items()
    }
    frozen_hash=sha256(json.dumps(frozen,sort_keys=True,
                                  separators=(",",":")).encode()).hexdigest()
    observed={arm:run_policy(test,items) for arm,items in policies.items()}
    summary={}
    for arm,records in observed.items():
        n=sum(int(x["resolved"]) for x in records)
        questions=sum(x["number_of_questions"] for x in records)
        assignments=sum(x["enumerative_assignment_trial_budget"] for x in records)
        summary[arm]={
            "resolved_pairs":n,
            "correct_hold_pairs":len(records)-n,
            "total_queries":questions,
            "total_homomorphism_calls":2*questions,
            "all_vertex_mapping_trial_budget":assignments,
            "mean_questions_per_external_pair":questions/len(records),
            "source_question_grammar_same_connected_for_three_arms":
                arm!="ALL_UNFILTERED_SOURCE_GRAPHS",
        }
    # The unfiltered arm includes disconnected patterns and is a
    # deliberately weak ablation. The strong comparator is the
    # training-optimized conventional cost-sensitive policy.
    if any(observed[k][i]["resolved"]!=observed[
            "STRONG_CLASSICAL_TRAINED_COST_SENSITIVE"][i]["resolved"]
           for k in observed for i in range(len(test))):
        raise HOLD("A source policy falsely asserted identity when unresolved")
    return {
        "source_plans_frozen_sha256":frozen_hash,
        "actual_frozen_probe_orders":frozen,
        "heldout_matched_observations":summary,
        "query_receipts":{k:[
            {"pair_atlas_ids":list(t.atlas_ids),**x}
            for t,x in zip(test,items)]
            for k,items in observed.items()},
        "shared_heldout_pairs_across_all_arms":True,
        "independent_source_hom_oracle_for_positive_answers":True,
        "candidate_probes_not_retrained_after_heldout":True,
        "number_of_independently_origined_graph_pairs":len(test),
        "standard_greedy_classical_cost_sensitive_baseline":True,
        "strong_classical_source_ordering_same_grammar_as_prior":True,
        "unfiltered_baseline_known_weaker_by_design":True,
        "prior_reuse_is_one_matched_research_episode_not_recursive_compounding":
            True,
    }

def run():
    train,test,atlas_source=cohort()
    verify_prepared(train,test,atlas_source)
    priors,history=prior_apertures()
    # Separate SOURCE discovery and formal theorem proof, training only.
    hypothesis=propose_composition_rule(train)
    factorization=certify_factorization(train[:5])
    invalid=challenge_degree_conjecture(train)
    if hypothesis["selected"]!="PRODUCT":
        raise HOLD("No mathematical theorem candidate")
    verdict=counterfactual(train,test,priors)
    summaries=verdict["heldout_matched_observations"]
    discovered=summaries["LEGIT021_ACQUIRED_APERTURES_FIRST"]
    classical=summaries["STRONG_CLASSICAL_TRAINED_COST_SENSITIVE"]
    canonical=summaries["CANONICAL_CONNECTED_ONLY"]
    theorem=summaries["ALL_UNFILTERED_SOURCE_GRAPHS"]
    if discovered["resolved_pairs"]!=classical["resolved_pairs"]:
        raise HOLD("Found differing solved status")
    return {
        "schema":"motif.legit022.independent-atlas-aperture-dividend.v1",
        "experiment":"MOTIF-LEGIT-022",
        "title":"THE_ATLAS_APERTURE_DIVIDEND",
        "status":STATUS,
        "externally_originated_carrier_source":atlas_source,
        "source_predecessor":history,
        "math_novelty_attempt":{
            "source_decomposition_rule_hypothesis":hypothesis,
            "independent_finite_and_combinatorial_certificate":factorization,
            "overgeneralized_degree_to_tree_conjecture":invalid,
            "historically_novel_theorem_credible":False,
            "external_literature_screening_note":
                "Lovasz 1967 graph-hom count characterization; "
                "multiplicativity of disjoint source hom counts is elementary and established",
            "source_grammar_discovery_is_bounded_by_handwritten_ops":True,
        },
        "two_research_episodes":{
            "previous_mathematical_probe_generation":"LEGIT021",
            "current_math_law_mining_and_experiment":"LEGIT022",
            "prior_aperture_reuse":verdict,
            "benefit_over_canonical_connected_in_probes":
                canonical["total_queries"]-discovered["total_queries"],
            "benefit_over_strong_classical_trained_in_probes":
                classical["total_queries"]-discovered["total_queries"],
            "theorem_pruned_source_savings_in_probes":
                theorem["total_queries"]-canonical["total_queries"],
        },
        "evidence_and_scope":{
            "external_graph_carrier_authorship_independent":True,
            "external_challenge_pairing_independently_authored":False,
            "test_public_cryptographic_blinding":False,
            "new_historical_mathematics_demonstrated":False,
            "complete_cpu_human_cost_of_all_prior_research_measured":False,
            "independent_adjudicator_of_recursive_improvement":False,
            "repeated_adopted_successive_optimizations_causally_proved":False,
            "economic_compounding_rate_identifiable":False,
            "source_questions_bounded_at_four_vertices":True,
            "strong_classical_control_present":True,
            "no_new_software_auto_promotion":True,
            "no_real_world_authority":True,
        },
    }

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python experiments/legit022/trial.py [--emit]")
    output=run()
    if sys.argv[1:]:
        Path("/tmp/motif-legit022-atlas-evidence.json").write_text(
            json.dumps(output,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    details=output["two_research_episodes"]["prior_aperture_reuse"]
    print(json.dumps({
        "experiment":output["experiment"],
        "status":output["status"],
        "external_source":{
            "version":output["externally_originated_carrier_source"]["networkx_version"],
            "sha256":output["externally_originated_carrier_source"]["atlas_data_sha256"]
        },
        "theorem_candidate":output["math_novelty_attempt"]
            ["source_decomposition_rule_hypothesis"]["selected"],
        "degree_based_conjecture_refuted":output["math_novelty_attempt"]
            ["overgeneralized_degree_to_tree_conjecture"]["hypothesis_refuted"],
        "matched_holdout":details["heldout_matched_observations"],
        "historical_math_novelty":False,
        "recursive_compounding_independently_verified":False
    },indent=2,sort_keys=True))
if __name__=="__main__":
    main()
