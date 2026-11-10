"""LEGIT-024 two-stage, inspectable tool ecology experiment.

Stage I: independently verify candidate methods on TRAINING only, measure
actual work and freeze method priority by task family. Stage II: evaluate
fixed-order vs inherited tool-selection policy on heldout tasks.

This is an engineered portfolio selection demonstration, NOT autonomous tool
invention, independent mathematical novelty or recursive improvement.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "legit022"))
from portfolio import DEFAULT, METHODS, NOT_INTEGRATED, try_method, execute_portfolio
from fixtures import suite


def _json_safe(value):
    # Structural conversion: output is inspectable JSON without arbitrary repr
    # of classes/functions. Tuple graph edges become arrays.
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError("nonportable evidence field")


def train_selector(training):
    by_family = defaultdict(list)
    for task in training:
        by_family[task["kind"]].append(task)
    # Measure each eligible method on the same training items.
    observations = {}
    order = {}
    for kind, cases in sorted(by_family.items()):
        candidates = {}
        for method in METHODS[kind]:
            rows = [try_method(task, method) for task in cases]
            successes = sum(row["status"] == "VERIFIED" for row in rows)
            total_ms = sum(row["cpu_ms"] for row in rows)
            candidates[method] = {
                "verified_train": successes, "train_count": len(rows),
                "actual_training_cpu_ms": round(total_ms,5),
                "train_status_counts": dict(Counter(x["status"] for x in rows)),
                "train_case_receipts": [
                    {"id": task["id"], "status": result["status"],
                     "cpu_ms": result["cpu_ms"],
                     "verification": result.get("verification"),
                     "reason": result.get("reason")}
                    for task, result in zip(cases, rows)
                ],
            }
        # Priority: more actual verified coverage, then observed training CPU.
        # This single-run measurement is sensitive to noise and setup costs.
        ranked = sorted(candidates, key=lambda name: (
            -candidates[name]["verified_train"],
            candidates[name]["actual_training_cpu_ms"],
            name))
        order[kind] = tuple(ranked)
        observations[kind] = candidates

    # Freeze the entire method order *before any heldout evaluation*.
    blob = json.dumps(order,sort_keys=True,separators=(",",":")).encode()
    return order, {
        "selection_criterion": "training_verified_coverage_then_measured_cpu",
        "method_order_sha256": sha256(blob).hexdigest(),
        "frozen_method_order": order,
        "only_training_queries_used_for_ranking": True,
        "train_all_candidate_methods_not_only_selected": True,
        "training_receipts": observations,
    }


def evaluation(heldout, orders):
    rows = [execute_portfolio(task, orders[task["kind"]])
            for task in heldout]
    by_family = {}
    for kind in sorted(METHODS):
        group = [r for r in rows if r["kind"] == kind]
        by_family[kind] = {
            "task_count": len(group),
            "verified": sum(r["status"] == "VERIFIED" for r in group),
            "total_solver_attempts": sum(r["method_count"] for r in group),
            "summed_cpu_ms": round(sum(r["cpu_ms"] for r in group), 5),
            "unresolved_task_ids": [r["task_id"] for r in group
                                   if r["status"] != "VERIFIED"],
        }
    return {"by_family": by_family, "per_case": rows,
            "all_verified": all(r["status"] == "VERIFIED" for r in rows)}


def run():
    training, heldout, provenance = suite()
    priority, freeze = train_selector(training)
    baseline = evaluation(heldout, DEFAULT)
    learned = evaluation(heldout, priority)
    installed = {}
    for pkg in ("networkx", "sympy", "z3-solver", "ortools"):
        try:
            installed[pkg] = version(pkg)
        except PackageNotFoundError:
            installed[pkg] = "NOT_INSTALLED"
    return _json_safe({
        "experiment": "MOTIF-LEGIT-024",
        "title": "RESEARCH METHOD ECOLOGY — THE NEXT QUESTION ENGINE",
        "status": "RESEARCH_HOLD_NO_NOVEL_MATH_OR_RECURSIVE_IMPROVEMENT",
        "task_contracts": list(METHODS),
        "executable_method_contracts": METHODS,
        "not_integrated": NOT_INTEGRATED,
        "pinned_installed_dependency_versions": installed,
        "source_provenance": {
            "graph_corpus": provenance,
            "other_tasks": "ENGINEER_AUTHORED_NONBLINDED",
            "training_case_count": len(training),
            "heldout_case_count": len(heldout),
            "heldout_not_accessed_by_policy_selection": True,
            "source_authorship_independent_only_for_original_graphs": True,
        },
        "trained_selector": freeze,
        "matched_heldout_evaluations": {
            "fixed_classical_priority": baseline,
            "learned_training_only_priority": learned,
        },
        "criteria_for_future_ability_not_yet_measured": [
            "ability to solve completely new task types",
            "automatic invention of a verified new method adapter",
            "future-research value beyond this predeclared corpus",
            "external independent theorem review",
            "full engineer and verifier labour costs",
            "multi-generation autonomous compounding",
        ],
    })


if __name__ == "__main__":
    if sys.argv[1:] != ["--emit"]:
        raise SystemExit("Usage: python experiments/legit024/trial.py --emit")
    print(json.dumps(run(), indent=2, sort_keys=True))
