"""LEGIT-028: finite, goal-aware information geometry and its limits.

Objective is a *verified distinguishing witness*, not entropy for its own
sake. Shannon entropy of a question's outputs is not interchangeable with
P(exact witness). The geometrical posterior uses an empirical ordinal
feature map from TRAINING ONLY; no black-box learned latent state, no LLM
and no invocation of any unsafe method.
"""
from __future__ import annotations

from bisect import bisect_left
from collections import Counter
from hashlib import sha256
from math import log2
import json

from information_worlds import (candidate_questions, observation, is_witness,
                                HOLD)

METHODS = (
    "RAW_OBSERVATION_DIVERSITY",
    "JOINT_SHANNON_ENTROPY",
    "WITNESS_BERNOULLI_ENTROPY",
    "MARGINAL_WITNESS_PROBABILITY",
    "CONTEXTUAL_BAYES_WITNESS",
    "CONTEXTUAL_VALUE_OF_INFORMATION",
)
STATIC = set(METHODS[:4])
ADAPTIVE = set(METHODS[4:])
CONVENTIONAL = "CLASSICAL_RESIDUAL_GREEDY"
CANONICAL = "CANONICAL_FIXED"
ALL_METHODS = METHODS + (CONVENTIONAL, CANONICAL)
EDIT_PENALTY = 0.025  # per-case expected-query cost, fixed pre-evaluation


def _entropy(values):
    values = tuple(values)
    if not values:
        return 0.0
    counts = Counter(values)
    n = len(values)
    return -sum((count/n)*log2(count/n) for count in counts.values())


def records(domain, cases):
    q = candidate_questions(domain)
    result = []
    for case in cases:
        result.append({
            "id": case["id"],
            "answers": {probe: tuple(observation(domain, case, probe))
                        for probe in q}
        })
    if len({r["id"] for r in result}) != len(result):
        raise HOLD("duplicate training cases")
    return tuple(result)


def morphology(domain, rows):
    questions = candidate_questions(domain)
    if not rows:
        raise HOLD("no morphology observations")
    by_question = {}
    for q in questions:
        values = [v for row in rows for v in row["answers"][q]]
        paired = [row["answers"][q] for row in rows]
        witness = [is_witness(pair) for pair in paired]
        by_question[q] = {
            "distinct_observation_values": len(set(values)),
            "observation_entropy_bits": _entropy(values),
            "joint_pair_entropy_bits": _entropy(paired),
            "witness_entropy_bits": _entropy(witness),
            "witness_probability_empirical": sum(witness)/len(witness),
            "outcome_values": tuple(sorted(set(values))),
        }
    max_unique = max(x["distinct_observation_values"]
                     for x in by_question.values())
    # These are empirical properties of TRAINING observation alphabets,
    # NOT intrinsic or universal domain classifications.
    return {
        "training_alphabet_kind": (
            "EMPIRICALLY_BINARY" if max_unique <= 2 else
            "EMPIRICALLY_MULTIVALUED"),
        "max_observed_distinct_values": max_unique,
        "per_question": by_question,
        "goal_utility": "find a question whose two exact outputs differ",
        "finite_equal_outputs_do_not_prove_equivalence": True,
    }


def static_order(domain, rows, method, signature):
    qs = candidate_questions(domain)
    if method == CANONICAL:
        return qs
    if method == CONVENTIONAL:
        remaining = list(qs)
        pending = list(rows)
        order = []
        while remaining:
            best = min(remaining, key=lambda q: (
                -sum(is_witness(row["answers"][q]) for row in pending),
                qs.index(q)))
            order.append(best)
            remaining.remove(best)
            pending = [row for row in pending
                       if not is_witness(row["answers"][best])]
        return tuple(order)
    if method not in STATIC:
        raise HOLD("not a static method")
    def score(q):
        x = signature["per_question"][q]
        return {
            "RAW_OBSERVATION_DIVERSITY": x["distinct_observation_values"],
            "JOINT_SHANNON_ENTROPY": x["joint_pair_entropy_bits"],
            "WITNESS_BERNOULLI_ENTROPY": x["witness_entropy_bits"],
            "MARGINAL_WITNESS_PROBABILITY":
                x["witness_probability_empirical"],
        }[method]
    return tuple(sorted(qs, key=lambda q: (-score(q), qs.index(q))))


def _cdf(value, values):
    """Ordinal geometry: train-only rank, not arbitrary numeric scale."""
    if not values:
        raise HOLD("missing training observation alphabet")
    return bisect_left(values, value) / len(values)


def _similarity(previous_pair, train_pair, values):
    return max(0.0, 1.0 - (
        abs(_cdf(previous_pair[0], values)-_cdf(train_pair[0], values)) +
        abs(_cdf(previous_pair[1], values)-_cdf(train_pair[1], values))) / 2)


def posterior_weights(rows, history, signature):
    """Kernel conditioned ONLY on observed unsuccessful past questions."""
    weights = []
    for row in rows:
        w = 1.0
        for q, actual_observation in history:
            observed = row["answers"][q]
            if is_witness(observed):
                # Training hypothesis impossible given an unsuccessful query.
                w *= 0.02
            else:
                w *= 0.05 + 0.95*_similarity(
                    actual_observation, observed,
                    signature["per_question"][q]["outcome_values"])
        weights.append(w)
    return weights


def adaptive_choice(domain, rows, signature, history, unused, method):
    qs = candidate_questions(domain)
    weights = posterior_weights(rows, history, signature)
    mass = sum(weights)
    if mass <= 1e-16:
        weights = [1.0] * len(rows)
        mass = float(len(rows))
    candidates = []
    for q in unused:
        witness_mass = sum(w*is_witness(row["answers"][q])
                           for row, w in zip(rows,weights))
        # Weak Beta(1,1) prior limits overconfident extrapolation from
        # sparse or irrelevant matching training cases.
        probability = (1 + witness_mass)/(2 + mass)
        if method == "CONTEXTUAL_VALUE_OF_INFORMATION":
            groups = Counter()
            for row,w in zip(rows,weights):
                groups[row["answers"][q]] += w
            probs = [w/mass for w in groups.values() if w > 0]
            conditional_entropy = -sum(p*log2(p) for p in probs)
            max_entropy = log2(len(groups)) if len(groups) > 1 else 1
            score = probability + 0.15 * conditional_entropy/max_entropy
        elif method == "CONTEXTUAL_BAYES_WITNESS":
            score = probability
        else:
            raise HOLD("unsupported adaptive rule")
        candidates.append((-score, qs.index(q), q))
    return min(candidates)[2]


def compile_policy(domain, train_rows, method):
    if method not in ALL_METHODS:
        raise HOLD("unrecognized evaluation strategy")
    signature = morphology(domain, train_rows)
    order = (None if method in ADAPTIVE else
             static_order(domain, train_rows, method, signature))
    qs = candidate_questions(domain)
    if order is not None and (len(order) != len(qs) or set(order) != set(qs)):
        raise HOLD("unequal question grammar")
    return {
        "domain": domain,
        "method": method,
        "train_rows": tuple(train_rows),
        "signature": signature,
        "order": order,
    }


def next_question(policy, seen):
    qs = candidate_questions(policy["domain"])
    unused = [q for q in qs if q not in {x[0] for x in seen}]
    if not unused:
        raise HOLD("finite question vocabulary exhausted")
    if policy["order"] is not None:
        return next(q for q in policy["order"]
                    if q not in {x[0] for x in seen})
    return adaptive_choice(policy["domain"], policy["train_rows"],
                           policy["signature"], seen, unused,
                           policy["method"])


def simulate(policy, case_id, oracle):
    """Oracle supplies ONLY queried answers, never a full future answer map."""
    transcript = []
    for _ in candidate_questions(policy["domain"]):
        q = next_question(policy, transcript)
        outcome = tuple(oracle(q))
        if len(outcome) != 2:
            raise HOLD("malformed exact observation")
        success = is_witness(outcome)
        transcript.append((q, outcome))
        if success:
            return {
                "id": case_id, "solved": True,
                "question_count": len(transcript),
                "all_attempted_questions": transcript,
            }
    return {
        "id": case_id, "solved": False,
        "question_count": len(transcript),
        "all_attempted_questions": transcript,
    }


def frozen_spec(policy):
    """No future cases, execution state or hidden live callbacks in digest."""
    signature = policy["signature"]
    qs = candidate_questions(policy["domain"])
    fields = [{
        "q": list(q) if isinstance(q, tuple) else q,
        "distinct": signature["per_question"][q]["distinct_observation_values"],
        "witness_probability":
            signature["per_question"][q]["witness_probability_empirical"],
        "observation_entropy":
            signature["per_question"][q]["observation_entropy_bits"],
        "joint_entropy": signature["per_question"][q][
            "joint_pair_entropy_bits"],
        "witness_entropy": signature["per_question"][q][
            "witness_entropy_bits"],
    } for q in qs]
    observations = [
        {"id": row["id"], "answers": [
            list(row["answers"][q]) for q in qs]}
        for row in policy["train_rows"]]
    return {
        "domain": policy["domain"], "method": policy["method"],
        "static_order": ([
            list(q) if isinstance(q, tuple) else q
            for q in policy["order"]] if policy["order"] else None),
        "question_geometry": fields,
        "train_observations": observations,
        "training_alphabet_kind": signature["training_alphabet_kind"],
        "equal_candidate_question_grammar": True,
        "exact_positive_witness_required": True,
    }


def sha256_plan(policy):
    return sha256(json.dumps(frozen_spec(policy),sort_keys=True,
                separators=(",",":")).encode()).hexdigest()
