"""LEGIT-028: learn which meaning of information is useful, then hold it out.

The selector compares entropy and utility *per task goal*, with a strong
conventional residual greedy method. It never calls the future-world
generator before writing and hashing the complete fitted model plan.
Candidate policy grammar, worlds, thresholds, and external dependencies
are engineer-designed; this is an experiment in reliable method selection,
not evidence of autonomous general scientific discovery.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from time import process_time_ns
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import information_worlds as worlds
import information_engine as engine

STATUS = "RESEARCH_HOLD_NO_GENERAL_INFORMATION_GEOMETRY_DISCOVERY"
MIN_DELTA = 0.025


def _all_training_observations(by_world):
    rows = []
    for _, selected in sorted(by_world.items()):
        rows.extend(selected)
    return tuple(rows)


def leave_one_world_out(domain, by_world):
    """Out-of-training-world validation; no new future world may be read.

    Adaptive methods are fitted on training outcomes of other worlds.
    Validation observations are requested sequentially via an oracle,
    so no policy can read the label of an unasked question.
    """
    labels = tuple(sorted(by_world))
    if len(labels) < 2:
        raise worlds.HOLD("at least two training environments required")
    comparisons = {}
    for method in engine.ALL_METHODS:
        folds = []
        for excluded in labels:
            fit = _all_training_observations({
                name: rows for name, rows in by_world.items()
                if name != excluded})
            policy = engine.compile_policy(domain, fit, method)
            tests = by_world[excluded]
            scores = []
            for row in tests:
                seen = engine.simulate(
                    policy, row["id"], lambda q, row=row: row["answers"][q])
                if not seen["solved"]:
                    raise worlds.HOLD("candidate failed training-fold task")
                scores.append(seen["question_count"])
            folds.append({
                "excluded_training_world": excluded,
                "case_count": len(tests),
                "questions": sum(scores),
                "average_questions": sum(scores)/len(scores),
            })
        macro = sum(x["average_questions"] for x in folds)/len(folds)
        comparisons[method] = {
            "folds": folds,
            "macro_world_mean_questions": round(macro, 8),
        }
    # Novel geometry must demonstrate an actual CV improvement over
    # the strong conventional trained greedy: ties REFUSE promotion.
    contenders = sorted(
        engine.METHODS,
        key=lambda m: (comparisons[m]["macro_world_mean_questions"], m))
    best = contenders[0]
    guard = engine.CONVENTIONAL
    best_objective = (comparisons[best]["macro_world_mean_questions"] +
                      MIN_DELTA)
    incumbent = comparisons[guard]["macro_world_mean_questions"]
    promoted = best_objective < incumbent - 1e-9
    adopted = best if promoted else guard
    return {
        "domain": domain,
        "candidate_method_count": len(engine.ALL_METHODS),
        "comparators": comparisons,
        "best_candidate_geometry_method": best,
        "conventional_incumbent": guard,
        "complexity_penalty_questions": MIN_DELTA,
        "trained_geometry_objective_with_penalty": round(
            best_objective, 8),
        "conventional_incumbent_cv": incumbent,
        "geometry_promoted": promoted,
        "adopted_method": adopted,
        "rejection_reason": (None if promoted else
            "Insufficient out-of-world gain over classical residual greedy"),
        "future_worlds_not_read_for_selection": True,
        "equal_question_grammar": True,
    }


def training_and_freeze():
    begin = process_time_ns()
    by_domain, provenance = worlds.training_worlds()
    frozen = {}
    policies = {}
    receipts = {}
    for domain in worlds.DOMAINS:
        by_world = {
            label: engine.records(domain, cases)
            for label, cases in by_domain[domain].items()
        }
        chooser = leave_one_world_out(domain, by_world)
        fit = _all_training_observations(by_world)
        named = {m:engine.compile_policy(domain,fit,m)
                 for m in engine.ALL_METHODS}
        # The router is also explicitly trained only on existing worlds.
        named["GEOMETRY_CV_GUARDED_ROUTER"] = named[chooser[
            "adopted_method"]]
        hashes = {m:engine.sha256_plan(policy)
                  for m,policy in named.items()}
        if any(len(engine.candidate_questions(domain)) != len(
               engine.candidate_questions(policy["domain"]))
               for policy in named.values()):
            raise worlds.HOLD("unequal candidate grammars")
        policies[domain] = named
        frozen[domain] = hashes
        signature = named["GEOMETRY_CV_GUARDED_ROUTER"]["signature"]
        receipts[domain] = {
            "training_world_sizes": {name:len(rows)
                                     for name,rows in by_world.items()},
            "leave_one_training_world_out": chooser,
            "observational_morphology": {
                "kind": signature["training_alphabet_kind"],
                "max_observed_distinct_values":
                    signature["max_observed_distinct_values"],
                "all_questions_tested_have_utility_concept": True,
                "entropy_is_not_a_counterexample_certificate": True,
            },
            "frozen_method_sha256": hashes,
        }
    freeze = sha256(json.dumps(frozen,sort_keys=True,
                    separators=(",",":")).encode()).hexdigest()
    return policies,{
        "training_provenance": provenance,
        "domains": receipts,
        "all_domain_policy_fingerprints": frozen,
        "frozen_all_domain_policy_sha256": freeze,
        "future_graph_and_math_worlds_not_requested_before_frozen_hash": True,
        "training_cpu_ms_including_cv_and_program_fits": round(
            (process_time_ns()-begin)/1e6,5),
    }


def evaluate(domain, cases, named):
    results = {}
    old_limit = (10 if domain == "graph_hom_witness" else 2)
    for method, policy in [
        ("NO_EXPANSION_OLD_QUESTIONS", None), *named.items()
    ]:
        start = process_time_ns()
        receipts = []
        for case in cases:
            def checked_oracle(q):
                proposed = worlds.observation(domain, case, q)
                independent = worlds.independent_observation(domain, case, q)
                if proposed != independent:
                    raise worlds.HOLD("failed exact independent question verification")
                return proposed
            if policy is None:
                seen = []
                for q in engine.candidate_questions(domain)[:old_limit]:
                    # On graph domain old probes are NOT the 5-node
                    # question vocabulary. Use genuine existing <=4.
                    if domain == "graph_hom_witness":
                        break
                    pair = checked_oracle(q)
                    seen.append((q,pair))
                    if engine.is_witness(pair):
                        break
                if domain == "graph_hom_witness":
                    from graph_inventor import grammar, reference_count
                    from methods import hom_count
                    a,b = case["payload"]
                    for source in grammar():
                        proposed = (hom_count(source,a)["value"],
                                    hom_count(source,b)["value"])
                        exact = (reference_count(source,a),
                                 reference_count(source,b))
                        if proposed != exact:
                            raise worlds.HOLD("old graph query oracle mismatch")
                        seen.append((source,proposed))
                        if engine.is_witness(proposed):
                            break
                transcript = {
                    "id": case["id"],
                    "solved": bool(seen and engine.is_witness(seen[-1][1])),
                    "question_count":len(seen),
                    "all_attempted_questions": seen,
                }
            else:
                transcript = engine.simulate(policy,case["id"],checked_oracle)
            receipts.append({
                "id": transcript["id"],
                "solved": transcript["solved"],
                "questions": transcript["question_count"],
                "all_questions_exactly_verified": True,
                "all_attempted_questions": [{
                    "question": (list(q) if isinstance(q,tuple) else q),
                    "observed_pair":list(pair),
                    "is_exact_witness":engine.is_witness(pair),
                    "independent_oracle_agreed":True,
                } for q,pair in transcript["all_attempted_questions"]],
            })
        results[method] = {
            "cases":len(cases),
            "solved":sum(row["solved"] for row in receipts),
            "questions":sum(row["questions"] for row in receipts),
            "cpu_ms_with_per_question_exact_verification":round(
                (process_time_ns()-start)/1e6,5),
            "receipts":receipts,
        }
    return results


def run():
    strategies, training = training_and_freeze()
    # Future world construction must occur strictly after the hash above.
    future, origin = worlds.future_worlds()
    results = {}
    for domain in worlds.DOMAINS:
        results[domain] = {}
        for label, cases in future[domain].items():
            results[domain][label] = evaluate(
                domain,cases,strategies[domain])
    totals = {}
    for domain, caseworlds in results.items():
        totals[domain] = {}
        methods = next(iter(caseworlds.values()))
        for method in methods:
            rows = [w[method] for w in caseworlds.values()]
            totals[domain][method] = {
                "cases":sum(x["cases"] for x in rows),
                "solved":sum(x["solved"] for x in rows),
                "questions":sum(x["questions"] for x in rows),
                "cpu_ms":round(sum(x["cpu_ms_with_per_question_exact_verification"]
                                   for x in rows),5),
            }
    # POST-HOC only: these measurements exist AFTER all strategies have
    # been frozen. They are counterexamples and future-experiment prompts,
    # NEVER a selector that feeds back into this evaluation.
    diagnosis = {}
    for domain, methods in totals.items():
        routed = methods["GEOMETRY_CV_GUARDED_ROUTER"]
        incumbent = methods[engine.CONVENTIONAL]
        eligible = {k:v for k,v in methods.items()
                    if k not in ("NO_EXPANSION_OLD_QUESTIONS",
                                 "GEOMETRY_CV_GUARDED_ROUTER")}
        retrospective = min(eligible,key=lambda k:(eligible[k]["questions"],k))
        regret = routed["questions"]-incumbent["questions"]
        selected = training["domains"][domain][
            "leave_one_training_world_out"]
        diagnosis[domain] = {
            "goal": "verified exact distinguishing witness",
            "empirical_outcome_geometry":training["domains"][domain][
                "observational_morphology"]["kind"],
            "training_only_adopted_method":selected["adopted_method"],
            "observed_future_questions_adopted":routed["questions"],
            "observed_future_questions_classical_greedy":incumbent["questions"],
            "future_regret_in_questions_vs_classical":regret,
            "cv_selected_method_failed_to_beat_classical_in_future":
                selected["geometry_promoted"] and regret>0,
            "retrospectively_best_experimental_method":retrospective,
            "retrospective_best_questions":eligible[retrospective]["questions"],
            "posthoc_best_method_not_promoted_to_current_evaluation":True,
            "next_research_question":(
                "Can repeated independent training environments and a "
                "distribution-shift-aware guard predict when this "
                "information criterion will lose to strong classical "
                "witness-gain search on truly future examples?"),
        }
    return {
        "experiment":"MOTIF-LEGIT-028",
        "title":"INFORMATION GEOMETRY — ENTROPY IS NOT RESEARCH UTILITY",
        "status":STATUS,
        "domain_contracts":list(worlds.DOMAINS),
        "candidate_research_policies":list(engine.ALL_METHODS),
        "router_rule":"PROMOTE_ONLY_IF_BEST_GEOMETRY_POLICY_WINS_OUT_OF_TRAINING_WORLD_CV",
        "goal_exact_distinguishing_witness_in_all_domains":True,
        "no_unproven_equivalence_from_negative_observations":True,
        "training_and_frozen_research_strategy":training,
        "future_world_provenance":origin,
        "new_world_evidence":results,
        "aggregate_results":totals,
        "posthoc_research_diagnosis_not_used_for_selection": diagnosis,
        "aggregate_routed_vs_classical_query_difference":sum(
            x["future_regret_in_questions_vs_classical"]
            for x in diagnosis.values()),
        "limitations":[
            "Mathematical questions, priors, metric choices and routing algorithm engineer-designed",
            "All challenge worlds selected for existing old-probe failures",
            "All new graph, modular and Boolean fixtures engineered, not independently blinded",
            "Conditional posterior similarity is empirical, not exact calibrated Bayesian inference",
            "VOI proxy is not a proof of optimal Bayesian experimental design",
            "Few fixed future worlds per goal; no statistically generalized superiority",
            "No historical novel mathematics, independent new algorithm invention or recursive compounding",
            "No human research/development/maintenance labor included in CPU measurements",
        ],
    }


if __name__ == "__main__":
    if sys.argv[1:] != ["--emit"]:
        raise SystemExit("Usage: python experiments/legit028/run_information_geometry.py --emit")
    print(json.dumps(run(),indent=2,sort_keys=True))
