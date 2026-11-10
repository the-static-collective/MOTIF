"""LEGIT-026 — The Method Mirror.

The system notices when an inherited *question-generation policy* is
insufficient, proposes bounded edits to that policy, validates the edits
across separate training worlds, freezes one strategy, and reuses it on
unseen seeded worlds. This is a finite engineer-designed policy-grammar
search, not autonomous algorithm invention or an LLM writing its own code.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from statistics import mean
from time import process_time_ns
import json
import sys

HERE = Path(__file__).resolve().parent
for sibling in ("legit021", "legit022", "legit023", "legit025"):
    sys.path.insert(0, str(HERE.parent / sibling))

from graph_inventor import grammar, reference_count, characterize
from methods import hom_count
from research import generate_extensions, make_plan, find_blindspots, HOLD
from worlds import training_worlds, evaluation_worlds, TRAIN_SEEDS, EVAL_SEEDS

STATUS = "RESEARCH_HOLD_NO_GENERAL_AUTONOMOUS_SELF_IMPROVEMENT"
PARENT = ("LEAF_FIRST", "GAIN_ALL", "STATIC")
GATES = ("LEAF_FIRST", "ALL", "NONLEAF_FIRST", "TREE_FIRST")
SCORERS = ("GAIN_ALL", "WORLD_BALANCED", "COUNT_DIVERSITY")
UPDATES = ("STATIC", "RESIDUAL")
MAX_CANDIDATES = 24
MAX_DP_STATES = 100_000


def candidate_programs():
    """A bounded, typed mutation grammar of three policy design choices.

    Each emitted program is a *search policy*, not a newly invented
    mathematical theorem, graph-source type, or unrestricted Python code.
    """
    recipes = []
    for gate in GATES:
        for scorer in SCORERS:
            for update in UPDATES:
                recipe = (gate, scorer, update)
                edits = sum(a != b for a, b in zip(recipe, PARENT))
                recipes.append({"program": recipe, "parent": PARENT,
                                "edits_from_parent": edits,
                                "operators": [
                                    "SET_SOURCE_GATE" if gate != PARENT[0] else "KEEP_SOURCE_GATE",
                                    "SET_PRIORITY_SCORER" if scorer != PARENT[1] else "KEEP_PRIORITY_SCORER",
                                    "SET_RESIDUAL_LEARNING" if update != PARENT[2] else "KEEP_STATIC_PRIORITY"
                                ]})
    if len(recipes) != MAX_CANDIDATES or len({
            tuple(r["program"]) for r in recipes}) != MAX_CANDIDATES:
        raise HOLD("mutator emitted duplicate/changed policy programs")
    return tuple(recipes)


def source_catalog():
    sources = generate_extensions()
    if len(sources) != 21 or len({s["atlas_source_id"] for s in sources}) != 21:
        raise HOLD("source question grammar was corrupted")
    return tuple(sources)


def _separation_matrix(worlds):
    """Compute once per task/source and retain actual two-world answers."""
    sources = source_catalog()
    records = {}
    for world, cases in worlds.items():
        item_list = []
        for identifiers, targets in cases:
            probes = {}
            for item in sources:
                src = item["source"]
                values = tuple(hom_count(src, g)["value"] for g in targets)
                probes[item["atlas_source_id"]] = values
            item_list.append({"pair_id": tuple(identifiers),
                              "targets": targets,
                              "answers": probes})
        records[world] = item_list
    return records


@lru_cache(maxsize=1)
def training_matrix():
    worlds, provenance = training_worlds()
    return _separation_matrix(worlds), provenance


def family_gate(item, name):
    if name == "LEAF_FIRST":
        return int(item["operator_arity"] != 1)
    if name == "NONLEAF_FIRST":
        return int(item["operator_arity"] == 1)
    if name == "TREE_FIRST":
        return int(len(item["source"][1]) != item["source"][0]-1)
    if name == "ALL":
        return 0
    raise HOLD("unrecognized operator gate")


def compile_program(program, matrix):
    """Learn an ordering from specified training-world observations only.

    Score candidates by two-world separation gain, macro-world robustness,
    or target-count diversity; optionally remove solved training tasks
    between choices. Every policy includes the SAME 21 source patterns.
    """
    gate, scorer, update = tuple(program)
    if gate not in GATES or scorer not in SCORERS or update not in UPDATES:
        raise HOLD("untyped graph question-selection policy")
    sources = source_catalog()
    current = {name: set(range(len(cases))) for name, cases in matrix.items()}
    chosen = []
    remaining = list(sources)

    while remaining:
        scores = {}
        for item in remaining:
            source_id = item["atlas_source_id"]
            if scorer == "COUNT_DIVERSITY":
                # This method ignores the gold separation labels, but
                # actually observes count values from TRAINING targets.
                count_values = {
                    answer for rows in matrix.values() for case in rows
                    for answer in case["answers"][source_id]}
                score = float(len(count_values))
            elif scorer == "GAIN_ALL":
                score = sum(
                    int(rows[j]["answers"][source_id][0] !=
                        rows[j]["answers"][source_id][1])
                    for name, rows in matrix.items() for j in current[name])
            elif scorer == "WORLD_BALANCED":
                score = sum(
                    sum(int(rows[j]["answers"][source_id][0] !=
                            rows[j]["answers"][source_id][1])
                        for j in current[name]) / max(1, len(current[name]))
                    for name, rows in matrix.items())
            scores[source_id] = score

        nxt = min(remaining, key=lambda entry: (
            family_gate(entry, gate),
            -scores[entry["atlas_source_id"]],
            entry["atlas_source_id"]))
        chosen.append(nxt)
        remaining.remove(nxt)
        if update == "RESIDUAL":
            src = nxt["atlas_source_id"]
            for name, rows in matrix.items():
                current[name] = {j for j in current[name] if
                    rows[j]["answers"][src][0] == rows[j]["answers"][src][1]}

    ids = tuple(x["atlas_source_id"] for x in chosen)
    if len(ids) != 21 or len(set(ids)) != 21:
        raise HOLD("candidate strategy skipped an eligible source")
    return ids


def simulated_cost(order, world_rows):
    """Total source questions on the same finite evaluated task set."""
    questions = 0
    resolved = 0
    per_case = []
    for row in world_rows:
        attempts = 0
        found = False
        for source_id in order:
            attempts += 1
            counts = row["answers"][source_id]
            if counts[0] != counts[1]:
                found = True
                break
        questions += attempts
        resolved += int(found)
        per_case.append(attempts)
    return {"questions": questions, "resolved": resolved,
            "cases": len(world_rows), "per_case": per_case}


def cross_validate(training):
    """Leave-one-TRAINING-WORLD-out method-grammar selection.

    We repeatedly learn source-order policies on three training-worlds,
    measure transfer to the fourth TRAINING-world and select a recipe
    based only on those out-of-fold scores. Future eval worlds are
    never constructed, read or referenced by this function.
    """
    worlds = tuple(sorted(training))
    if len(worlds) != 4:
        raise HOLD("wrong number of independent training environments")
    trial = []
    for mutation in candidate_programs():
        program = mutation["program"]
        fold_scores = []
        for left_out in worlds:
            fit = {w: training[w] for w in worlds if w != left_out}
            order = compile_program(program, fit)
            receipt = simulated_cost(order, training[left_out])
            if receipt["resolved"] != receipt["cases"]:
                raise HOLD("candidate source grammar cannot solve training test")
            fold_scores.append({
                "left_out_training_world": left_out,
                "questions": receipt["questions"],
                "cases": receipt["cases"],
                "average_questions": receipt["questions"] / receipt["cases"],
                "source_order_sha256": sha256(
                    json.dumps(order, separators=(",",":")).encode()).hexdigest(),
            })
        avg = mean(row["average_questions"] for row in fold_scores)
        # Strict fixed complexity penalty prevents gratuitous rewrites.
        penalty = 0.02 * mutation["edits_from_parent"]
        trial.append({
            **mutation, "folds": fold_scores,
            "leave_one_world_out_mean_questions": round(avg, 7),
            "complexity_penalty": penalty,
            "policy_selection_objective": round(avg + penalty, 7),
        })
    selected = min(trial, key=lambda x: (
        x["policy_selection_objective"], x["edits_from_parent"],
        tuple(x["program"])))
    classical_program = ("ALL", "GAIN_ALL", "RESIDUAL")
    classical_cv = next(x for x in trial if x["program"] == classical_program)
    parent_cv = next(x for x in trial if x["program"] == PARENT)

    # The proposal is REJECTED rather than promoted when it does not
    # beat the parent policy on training-world cross-validation.
    promotes_rewrite = (tuple(selected["program"]) != PARENT and
        selected["policy_selection_objective"] + 1e-9 <
        parent_cv["policy_selection_objective"])
    adopted_program = tuple(selected["program"]) if promotes_rewrite else PARENT
    return {
        "parent_program": PARENT,
        "candidate_count": len(trial),
        "bounded_generated_mutations": trial,
        "best_training_crossvalidation_candidate": selected,
        "parent_crossvalidation": parent_cv,
        "classical_greedy_crossvalidation": classical_cv,
        "proposed_rewrite_promoted_from_training_only": promotes_rewrite,
        "adopted_program": adopted_program,
        "rejection_reason_if_unimproved": (
            None if promotes_rewrite else
            "No cross-validation advantage beyond parent; refuse promotion"),
        "no_future_evaluation_data_consulted": True,
    }


def exact_training_dp(matrix):
    """Strong same-grammar conventional optimum on pooled TRAINING cases.

    Exact dynamic programming minimizes source questions on this finite
    observed training distribution; search is bounded to avoid exploding.
    The guarantee is TRAINING-only, not a prediction about new worlds.
    """
    from functools import lru_cache
    tasks = [row for cases in matrix.values() for row in cases]
    sources = source_catalog()
    target_mask = (1 << len(tasks)) - 1
    coverage = {}
    for source in sources:
        sid = source["atlas_source_id"]
        coverage[sid] = sum(
            (1 << i) for i, row in enumerate(tasks)
            if row["answers"][sid][0] != row["answers"][sid][1])
    reachable = 0
    for mask in coverage.values():
        reachable |= mask
    if reachable != target_mask:
        raise HOLD("source grammar fails to cover observed training tasks")
    candidate_ids = tuple(sorted(coverage))
    @lru_cache(maxsize=None)
    def dp(residual):
        if dp.cache_info().currsize > MAX_DP_STATES:
            raise HOLD("exact training planner exceeded declared state budget")
        if not residual:
            return (0, ())
        candidates = []
        for source_id in candidate_ids:
            nxt = residual & ~coverage[source_id]
            if nxt == residual:
                continue
            later, order = dp(nxt)
            candidates.append((residual.bit_count() + later,
                               (source_id,) + order))
        return min(candidates)
    objective, prefix = dp(reachable)
    rest = tuple(s for s in candidate_ids if s not in prefix)
    order = prefix + rest
    return {
        "order": order,
        "exact_training_questions": objective,
        "states_explored": dp.cache_info().currsize,
        "optimality_scope": "known_finite_training_pairs_only",
    }


def learn():
    """All training computations complete BEFORE evaluation world creation."""
    begin = process_time_ns()
    train, provenance = training_matrix()
    cv = cross_validate(train)
    sources = source_catalog()
    atlas_training, _, _ = find_blindspots()
    prior_policies, prior_receipt = make_plan(atlas_training)
    candidate_orders = {
        "PRIOR_025_FROZEN": tuple(
            x["atlas_source_id"] for x in
            prior_policies["COMPOSED_LEAF_FIRST_TRAINED"]),
        "CLASSICAL_TRAINED_GREEDY": compile_program(
            ("ALL", "GAIN_ALL", "RESIDUAL"), train),
        "METHOD_MIRROR_ADOPTED": compile_program(
            tuple(cv["adopted_program"]), train),
        "CANONICAL_21_SOURCES": tuple(
            x["atlas_source_id"] for x in sources),
    }
    dp = exact_training_dp(train)
    candidate_orders["EXACT_TRAINING_DP_CLASSICAL"] = dp["order"]
    unique = {x["atlas_source_id"] for x in sources}
    if any(set(order) != unique or len(order) != 21
           for order in candidate_orders.values()):
        raise HOLD("matched grammar broken in researcher portfolio")
    freeze = json.dumps(candidate_orders, sort_keys=True,
                        separators=(",",":")).encode()
    return candidate_orders, {
        "training_world_provenance": provenance,
        "training_world_counts": {name: len(rows)
                                   for name, rows in train.items()},
        "training_candidate_source_matrix_answers": {
            name: [{"pair_id": list(row["pair_id"]),
                    "by_source_id": {str(k): list(v) for k,v in
                                     row["answers"].items()}}
                   for row in rows]
            for name,rows in train.items()},
        "crossvalidation_method_invention": cv,
        "classical_exact_finite_training": dp,
        "previous_cartridge_hash": prior_receipt["policies_frozen_sha256"],
        "frozen_source_question_orders": candidate_orders,
        "frozen_sha256_before_eval_world_loading": sha256(freeze).hexdigest(),
        "training_total_cpu_ms_including_grammar_selection": round(
            (process_time_ns() - begin)/1e6,5),
        "future_world_generator_not_called_in_training": True,
    }


def evaluate_worlds(evaluation, orders):
    """Independent exact enumerator checks every attempted 5-source query."""
    by_world = {}
    source_by_id = {s["atlas_source_id"]: s["source"]
                    for s in source_catalog()}
    for world, cases in evaluation.items():
        arms = {}
        for method, order in orders.items():
            start = process_time_ns()
            records = []
            for identifiers, (a,b) in cases:
                trace = []
                for source_id in order:
                    source = source_by_id[source_id]
                    counts = [hom_count(source, g)["value"] for g in (a,b)]
                    exact = [reference_count(source, g) for g in (a,b)]
                    if counts != exact:
                        raise HOLD("new research method disagrees with independent oracle")
                    trace.append({
                        "source_id": source_id,
                        "source": characterize(source),
                        "observed_counts": counts,
                        "independently_checked": True,
                        "separates": counts[0] != counts[1],
                    })
                    if trace[-1]["separates"]:
                        break
                records.append({
                    "case_ids": list(identifiers),
                    "resolved": bool(trace and trace[-1]["separates"]),
                    "questions": len(trace),
                    "all_attempted_questions": trace,
                })
            arms[method] = {
                "cases": len(records),
                "resolved": sum(x["resolved"] for x in records),
                "questions": sum(x["questions"] for x in records),
                "cpu_ms_including_independent_verification": round(
                    (process_time_ns()-start)/1e6,5),
                "full_receipts": records,
            }
        by_world[world] = arms
    return by_world


def run():
    orders, training = learn()
    # This is the FIRST time new future-world carriers are materialized.
    future, future_provenance = evaluation_worlds()
    results = evaluate_worlds(future, orders)
    return {
        "experiment": "MOTIF-LEGIT-026",
        "title": "THE METHOD MIRROR — REWRITE HOW TO ASK BETTER QUESTIONS",
        "status": STATUS,
        "prior_motif_025_cartridge_replayed": True,
        "source_count": 21,
        "same_source_grammar_for_all_competing_methods": True,
        "mathematical_question_contract":
            "Find exact source graph F with hom(F,G1) != hom(F,G2)",
        "question_generator_self_diagnosis":
            "A fixed leaf-first source extension strategy may generalize "
            "poorly to new graph environments; propose bounded modifications "
            "to gate, scoring and residual-update rules.",
        "generated_policy_rewrites_are_engineer_specified_grammar": True,
        "training_and_meta_selection": training,
        "future_graph_world_provenance": future_provenance,
        "evaluation": results,
        "claims_not_demonstrated": [
            "autonomous invention of novel graph theory or mathematical algorithms",
            "independent externally hidden research administration",
            "sustained recursively compounding algorithm invention",
            "new proof system or historical theorem novelty",
            "total human development/review/maintenance cost superiority",
            "cross-domain general mathematical strategy improvement",
        ],
    }


if __name__ == "__main__":
    if sys.argv[1:] != ["--emit"]:
        raise SystemExit("Usage: python experiments/legit026/meta.py --emit")
    print(json.dumps(run(), indent=2, sort_keys=True))
