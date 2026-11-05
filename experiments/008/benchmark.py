"""MOTIF-008 predeclared, reproducible unknown-world comparison.

This evaluator can see oracle labels and families; learner.py cannot.
No model selection uses the test split. The results are synthetic, not
causal or general real-world evidence. Standard library only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import json
import math
import random
from statistics import mean

from oracle import FAMILIES, SUPPORTED, COUNTS, trial, paired_intervention
from learner import (features, observed_outcome, balanced_accuracy,
                     fit_relational, fit_tree, majority)

SEEDS = (11, 23, 37, 41, 59)
# Frozen benchmark definition. Do not change after looking at test results
# without creating a new benchmark version and recording the change.
BENCHMARK_VERSION = "unknown-world-v1"


def score(truth, predictions):
    if len(truth) != len(predictions):
        raise ValueError("Invalid prediction count")
    return round(balanced_accuracy(truth, predictions), 4)


def evaluate_world(family: str, seed: int) -> dict:
    task = trial(family, seed)
    motif = fit_relational(task.train, task.validation)
    single = fit_relational(task.train, task.validation, joins=False,
                            max_clauses=1, abstain_below=0.0)
    tree = fit_tree(task.train, task.validation)
    typical = majority(task.train)
    truth = [observed_outcome(x) for x in task.test]
    if not (0 < sum(truth) < len(truth)):
        raise ValueError("Test split lacks both outcomes")

    records = [features(e.before, e.roles) for e in task.test]
    edge_records = [features(e.before, e.roles, use_joins=False)
                    for e in task.test]
    baseline = [typical for _ in truth]
    edge_fallback = single.status != "PROPOSED"
    edge_preds = ([typical for _ in truth] if edge_fallback else
                  [single.predict(x) for x in edge_records])
    tree_preds = [tree.predict(x) for x in records]
    motif_preds = [motif.predict(x) for x in records]
    covered = motif.status == "PROPOSED"
    if covered != all(p is not None for p in motif_preds):
        raise ValueError("Partial coverage not implemented by this learner")

    intervention = None
    if family in ("forward_join", "reverse_join"):
        yes, no = paired_intervention(family, seed)
        a = motif.predict(features(yes.before, yes.roles))
        b = motif.predict(features(no.before, no.roles))
        intervention = {
            "evaluated": covered,
            "counterfactual_flipped_as_oracle": (a is True and b is False)
            if covered else None
        }
    return {
        "family": family, "seed": seed,
        "predicate_names_seen_in_training_only": True,
        "observed_train": len(task.train),
        "observed_validation": len(task.validation),
        "untouched_test": len(task.test),
        "test_successes": sum(truth),
        "relational_status": motif.status,
        "relational_feature_edges": sum(map(len, motif.condition)),
        "relational_validation_balanced": round(motif.validation_balanced, 4),
        "candidate_rules_checked": motif.considered,
        "search_truncated": motif.truncated,
        "relational_test_balanced": score(truth, motif_preds) if covered else None,
        "majority_test_balanced": score(truth, baseline),
        "single_edge_test_balanced": score(truth, edge_preds),
        "single_edge_used_majority_fallback": edge_fallback,
        "classical_tree_used_majority_fallback": tree.considered == 0,
        "classical_tree_test_balanced": score(truth, tree_preds),
        "paired_intervention": intervention
    }


def summarize(records: list[dict]) -> dict:
    per_family = {}
    for fam in FAMILIES:
        rows = [x for x in records if x["family"] == fam]
        accepted = [x for x in rows if x["relational_test_balanced"] is not None]
        intervened = [x["paired_intervention"] for x in rows
                      if x["paired_intervention"] is not None]
        per_family[fam] = {
            "worlds": len(rows),
            "relational_worlds_covered": len(accepted),
            "relational_test_balanced_if_covered": round(mean(
                x["relational_test_balanced"] for x in accepted), 4)
                if accepted else None,
            "majority_test_balanced": round(mean(
                x["majority_test_balanced"] for x in rows), 4),
            "single_edge_test_balanced": round(mean(
                x["single_edge_test_balanced"] for x in rows), 4),
            "classical_tree_test_balanced": round(mean(
                x["classical_tree_test_balanced"] for x in rows), 4),
            "tree_fallback_worlds": sum(x["classical_tree_used_majority_fallback"]
                                         for x in rows),
            "edge_fallback_worlds": sum(x["single_edge_used_majority_fallback"]
                                         for x in rows),
            "oracle_intervention_flips_observed_by_model": sum(
                x["counterfactual_flipped_as_oracle"] is True
                for x in intervened),
            "interventions_with_predictions": sum(
                x["evaluated"] for x in intervened),
        }
    covered = [x for x in records if x["relational_test_balanced"] is not None]
    support = [x for x in records if x["family"] in SUPPORTED]
    unsupported = [x for x in records if x["family"] not in SUPPORTED]
    return {
        "scope": "SYNTHETIC_GRAPHS_ONLY",
        "version": BENCHMARK_VERSION,
        "worlds": len(records),
        "vocabulary_disjoint_per_world": True,
        "seeds": list(SEEDS),
        "families": list(FAMILIES),
        "oracle_never_imported_by_learner": True,
        "few_shot_within_world_adaptation": True,
        "zero_shot_cross_world_transfer_demonstrated": False,
        "test_used_for_model_selection": False,
        "n_train_per_world": COUNTS["train"],
        "n_validation_per_world": COUNTS["validation"],
        "n_test_per_world": COUNTS["test"],
        "relational_coverage_worlds": len(covered),
        "relational_balanced_accuracy_if_covered": round(mean(
            x["relational_test_balanced"] for x in covered), 4)
            if covered else None,
        "supported_coverage": sum(x["relational_status"] == "PROPOSED"
                                  for x in support),
        "supported_worlds": len(support),
        "unsupported_coverage": sum(x["relational_status"] == "PROPOSED"
                                    for x in unsupported),
        "unsupported_worlds": len(unsupported),
        "majority_balanced_accuracy": round(mean(
            x["majority_test_balanced"] for x in records), 4),
        "single_edge_balanced_accuracy": round(mean(
            x["single_edge_test_balanced"] for x in records), 4),
        "classical_tree_balanced_accuracy": round(mean(
            x["classical_tree_test_balanced"] for x in records), 4),
        "per_family": per_family
    }


def run_benchmark(include_detail=True):
    data = [evaluate_world(family, seed)
            for family in FAMILIES for seed in SEEDS]
    report = {"experiment": "MOTIF-008",
              "evidence": "PREDECLARED_GENERATOR_SYNTHETIC",
              "summary": summarize(data)}
    if include_detail:
        report["worlds"] = data
    return report


if __name__ == "__main__":
    print(json.dumps(run_benchmark(), indent=2, sort_keys=True))
