"""GENIUS-011: generate candidate patterns BEFORE observing heldout outcomes.

Hypothesis generation: from THREE public but independently named signed
directed graphs, enumerate their common connected 2-edge substructures.
Hypothesis confirmation: separately generated synthetic intervention trials,
Fisher exact tests, predeclared Bonferroni family budget and source custody.

Methods are classical; data and hidden truths come from the SAME engineer.
This is more than choosing a supplied *list of candidate names*, but it is
NOT unrestricted question invention, real causal discovery, or external proof.
"""
from __future__ import annotations
from hashlib import sha256
import json

from discovery import (REGIMES, THREADS, ALPHA, N_PER_ARM, MIN_RISK_DIFFERENCE,
                       PATTERN_FAMILY_BUDGET, evaluate_case, make_world,
                       question_synthesis)

VALIDATION_SEEDS = (11001, 11002)
TEST_SEEDS = (11031, 11032, 11033, 11034, 11035, 11036)


def summarize(cases: list[dict]) -> dict:
    summary = {}
    for regime in REGIMES:
        rows = [r for r in cases if r["regime"]==regime]
        single = [r for r in rows if len(r["conditionally_supported"])==1]
        misleading = [
            r for r in single if r["conditionally_supported"][0] not in (
                r["actual_secret_for_evaluator_only"],
                r.get("synthetic_secondary_for_evaluator_only"))
        ]
        summary[regime] = {
            "cases": len(rows),
            "common_structure_found": sum(r["tests_performed"]>0 for r in rows),
            "generated_conjectures_evaluated": sum(r["tests_performed"] for r in rows),
            "single_supported_bridge_count": len(single),
            "spurious_supported_bridge_count": len(misleading),
            "three_way_retrospective_relation_count": sum(
                len(r["two_clock"]["retrospective_callbacks"])
                if r["two_clock"] else 0 for r in rows),
            "hold_reasons": {
                k: sum(r.get("bridge_status",r["synthesis_status"])==k
                       for r in rows)
                for k in sorted({r.get("bridge_status",r["synthesis_status"])
                                 for r in rows if not r["conditionally_supported"]})
            },
        }
    return summary


def run() -> dict:
    design = {
        "experiment": "GENIUS-011-UNSUSPECTED-RELATION",
        "source_graphs": "3 strands with independent local symbolic vertex names",
        "candidate_grammar": "all connected directed two-edge signed subgraphs",
        "canonical_form": "minimum serialized code across vertex permutations",
        "predeclared_scenarios": REGIMES,
        "thread_names": THREADS,
        "hypothesis_mining": "three-way intersection of independently sourced graph motifs",
        "requested_intervention": "separate binary two-arm synthetic trial per generated candidate x thread",
        "per_arm": N_PER_ARM,
        "familywise_alpha": ALPHA,
        "fixed_family_budget_including_unselected_candidates": PATTERN_FAMILY_BUDGET,
        "minimum_positive_risk_difference": MIN_RISK_DIFFERENCE,
        "required_independence": "three distinct strand roots; unique tested event roots",
        "confirmed_criteria": "3/3 positive corrected Fisher and only one supported explanation",
        "design_attestation_not_experiment_authentication": True,
        "validation_seeds": VALIDATION_SEEDS,
        "heldout_seeds": TEST_SEEDS,
        "external_author_not_present": True,
    }
    frozen = sha256(json.dumps(design, sort_keys=True).encode()).hexdigest()
    # Validation is diagnostic only: not a threshold-selection sweep.
    val = [evaluate_case(seed,regime)
           for seed in VALIDATION_SEEDS for regime in REGIMES]
    # Different seed worlds materialize only after creating the freeze record.
    test = [evaluate_case(seed,regime)
            for seed in TEST_SEEDS for regime in REGIMES]
    # Classical enumerative graph mining and classical exact tests are strong
    # controls with identical evidence/access. They would get identical
    # candidates and verdicts. The new contribution is dataflow composition.
    return {
        "status": "RESEARCH_HOLD_ENGINEER_AUTHORED_SYNTHESIS",
        "experimental_question": (
            "Can an unfamiliar common relational hypothesis be composed "
            "rather than supplied, and independently falsified?"
        ),
        "study_protocol_sha256_before_test_generation": frozen,
        "protocol": design,
        "validation_only": summarize(val),
        "future": summarize(test),
        "proof_carrying_source_cases": {
            regime: next(r for r in test if r["regime"]==regime)
            for regime in REGIMES
        },
        "strong_classical_exact_graph_miner_and_fisher_same_outcomes": True,
        "lexical_repetition_is_not_common_mechanism": True,
        "source_fingerprints_are_not_signatures": True,
        "no_novel_mathematical_algorithm": True,
        "no_real_world_causal_finding": True,
        "no_external_action": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
