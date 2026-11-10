"""GENIUS-010: prespecified, source-protected convergence/decoy trial.

Validation samples are never used to tune a real-person belief model.
No policy grid optimization is performed: the joint 3/3 threshold, familywise
correction and origin-root abstention are fixed before any test generation.
A hash of the analysis *design* is constructed before future seeds run.
The task/regime generators and "ground truth" are all engineer-authored.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from convergence import (
    FAMILY_ALPHA, HYPOTHESES, MIN_EFFECT, REFERENCE_MOTIF_SCORE, REGIMES,
    THREADS, TRIALS_PER_ARM, OBSERVATIONAL_TRIALS, evaluate_world,
    generate, public_projection, rank_convergences,
)

VALIDATION_SEEDS = (101001, 101002)
HELDOUT_SEEDS = (101031, 101032, 101033, 101034, 101035, 101036)


def summarize(results: list[dict]) -> dict:
    by_regime = {}
    for regime in REGIMES:
        rows = [r for r in results if r["regime"] == regime]
        detection = Counter(
            key for r in rows
            for key in r["verdict"]["conditional_candidates"]
        )
        source_holds = Counter(
            c["status"] for r in rows for c in r["verdict"]["candidates"]
            if c["status"] != "HOLD_CONVERGENCE_NOT_ESTABLISHED"
            and c["status"] != "CONDITIONAL_THREE_THREAD_CONVERGENCE"
        )
        by_regime[regime] = {
            "evaluated_cases": len(rows),
            "conditional_candidate_frequency": dict(sorted(detection.items())),
            "source_or_attestation_hold_reasons": dict(sorted(source_holds.items())),
            "any_conditional_bridge_cases": sum(
                bool(r["verdict"]["conditional_candidates"]) for r in rows),
            "lexical_baseline_blue_ribbon_cases": sum(
                r["verdict"]["lexical_only_baseline"] == "blue_ribbon" for r in rows),
            "source_owned_reinterpretation_count": sum(
                len(r["weave"]["retrospective_callbacks"]) for r in rows),
            "public_records_processed": sum(r["public_records"] for r in rows),
            "withheld_never_ingested": sum(
                r["withheld_not_scored_or_ingested"] for r in rows),
        }
    return by_regime


def run() -> dict:
    design = {
        "study": "GENIUS-010-THREE-THREAD-CAUSAL-CONVERGENCE",
        "formal_objective": "three source-distinct positive intervention contrasts",
        "candidate_hypotheses": HYPOTHESES,
        "independent_thread_names": THREADS,
        "predeclared_scenarios": REGIMES,
        "observations_per_arm": TRIALS_PER_ARM,
        "observational_sample_count": OBSERVATIONAL_TRIALS,
        "per_comparison_familywise_alpha": FAMILY_ALPHA/(len(HYPOTHESES)*len(THREADS)),
        "min_effect": MIN_EFFECT,
        "analysis_rules": [
            "public_projection_excludes_withheld",
            "unique_receipt_ids",
            "unique_randomized_source_origin_roots",
            "FISHER_EXACT_TWO_SIDED",
            "THREE_OF_THREE_POSITIVE",
            "INTERPRETATION_ONLY_AFTER_CONDITIONAL_BRIDGE",
        ],
        "validation_seeds": VALIDATION_SEEDS,
        "heldout_seeds": HELDOUT_SEEDS,
        "historical_source_leaks_prohibited": True,
        "true_status": "SYNTHETIC_ONLY_NO_REAL_CAUSAL_IDENTIFICATION",
    }
    digest = sha256(json.dumps(design, sort_keys=True).encode()).hexdigest()

    # Separate validation seeds and heldout seeds. The design has no tuned
    # thresholds, so validation only records whether the mechanism functions.
    calibration = [
        evaluate_world(seed, regime)
        for seed in VALIDATION_SEEDS for regime in REGIMES
    ]
    # Generate completely new synthetic future data only after digest.
    futures = [
        evaluate_world(seed, regime)
        for seed in HELDOUT_SEEDS for regime in REGIMES
    ]
    # The exact classical audited baseline and MOTIF use the SAME statistical
    # tests. The difference is the typed story/source/time interpretation
    # packet, not a claim of better hypothesis-testing accuracy.
    assert all(
        set(r["verdict"]["strong_classical_source_aware_baseline_candidates"]) ==
        set(r["verdict"]["conditional_candidates"])
        for r in futures
    )
    # Example source-carrying logs on 1 future case per scenario, rather
    # than pretending synthetic evidence is an actual external source.
    examples = {regime: next(
        r for r in futures if r["regime"] == regime
    ) for regime in REGIMES}
    return {
        "status": "RESEARCH_HOLD_ENGINEER_AUTHORED_CONVERGENCE",
        "design_frozen_before_holdout_sha256": digest,
        "design": design,
        "validation_only": summarize(calibration),
        "holdout_summary": summarize(futures),
        "source_owned_case_receipts": examples,
        "independent_verifier_ground_truth_only_for_scoring": True,
        "strong_classical_baseline_statistically_identical": True,
        "no_spiritual_historical_or_real_world_causal_claim": True,
        "no_external_action": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
