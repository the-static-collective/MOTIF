"""FIRE-002: productive combustion — a proof-yield learning governor.

Deliberate research sandbox. Truth and unrevealed source reports are held by
a separate synthetic owner. Policy calls ONLY receive PublicView, plus
completed verification receipts. No real-world actuation or source authentication.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fire001'))
from combustion import Furnace, Owner, PublicView, make_world, select as fire001_select


REGIMES = ('steady', 'drift', 'correlated')


def world(seed: int, regime: str):
    """Ground truth never enters a policy call. Correlation is deliberately hidden."""
    if regime not in REGIMES:
        raise ValueError('Unknown declared test regime')
    questions, original_owner = make_world(seed)
    rng = Random(seed * 103 + 620_017)
    reports = {}
    for key, q in questions.items():
        truth = original_owner.truth[key]
        p = (.82 if regime == 'steady'
             else (.88 if key in ('Q0', 'Q1', 'Q2', 'Q3') else .56)
             if regime == 'drift' else .78)
        if regime == 'correlated':
            # Every nominally distinct report derives from the SAME hidden event.
            # Their synthetic IDs look distinct: tests challenge this assumption.
            shared = truth if rng.random() < p else not truth
            reports[key] = (shared,) * q.source_count
        else:
            reports[key] = tuple(truth if rng.random() < p else not truth
                                 for _ in range(q.source_count))
    return questions, Owner(original_owner.truth, reports)


def probability_of_majority_correct(observed: tuple[bool, ...],
                                    needed: int, accuracy: float) -> float:
    """Finite Bayesian forecast using only observed reports and learned accuracy.

    A 1/2 prior over a hidden binary answer is an explicit modelling assumption.
    Future source outcomes are summed out, NOT read. This can fail when sources
    are correlated, drift, or share unverified upstream origins.
    """
    if needed < 1 or needed % 2 != 1 or len(observed) > needed:
        raise ValueError('Only positive odd independent source quorums supported')
    p = min(.999, max(.001, accuracy))
    ones = sum(observed)
    zeros = len(observed) - ones
    like_true = p ** ones * (1 - p) ** zeros
    like_false = (1 - p) ** ones * p ** zeros
    normal = like_true + like_false
    probability_true = like_true / normal
    remaining = needed - len(observed)

    def success_given_truth(truth: bool):
        # Distribution of unseen Boolean reports conditioned on hidden truth.
        result = 0.
        rate_ones = p if truth else 1. - p
        for extra_ones in range(remaining + 1):
            count = ones + extra_ones
            guess = (count > needed // 2)
            if guess is truth:
                result += (comb(remaining, extra_ones) *
                           rate_ones ** extra_ones *
                           (1. - rate_ones) ** (remaining - extra_ones))
        return result

    return (probability_true * success_given_truth(True) +
            (1. - probability_true) * success_given_truth(False))


@dataclass
class EpistemicLedger:
    # Flat, regularized reliability from *certified* past answers only.
    correct_reports: int = 2
    incorrect_reports: int = 1
    certified_children: int = 3
    rejected_children: int = 1
    verified_count: int = 0
    realized_value: int = 0

    @property
    def source_accuracy(self):
        return self.correct_reports / (self.correct_reports + self.incorrect_reports)

    @property
    def child_yield(self):
        return self.certified_children / (
            self.certified_children + self.rejected_children)

    def learn(self, receipt: dict, observed: tuple[bool, ...],
              value: int, is_child: bool):
        """Only independently certified synthetic outcomes may teach the ledger."""
        if receipt.get('action') != 'verify' or type(receipt.get('certified')) is not bool:
            raise ValueError('No verified answer; cannot update learned state')
        if not observed:
            raise ValueError('A verifier needs source receipts')
        actual = receipt['guess'] if receipt['certified'] else not receipt['guess']
        self.correct_reports += sum(ans is actual for ans in observed)
        self.incorrect_reports += sum(ans is not actual for ans in observed)
        self.verified_count += 1
        if receipt['certified']:
            self.realized_value += value
        if is_child:
            if receipt['certified']:
                self.certified_children += 1
            else:
                self.rejected_children += 1


def productive_select(view: PublicView, ledger: EpistemicLedger,
                      spark_weight: float = 1.) -> str | None:
    """Spend effort on likely *certified* value, not raw question propagation."""
    if not view.eligible:
        return None
    remaining_budget = view.budget - view.spent

    def reliability(key: str) -> float:
        q = view.questions[key]
        revealed = tuple(r.answer for r in view.observed.get(key, ()))
        return probability_of_majority_correct(revealed, q.evidence_need,
                                                ledger.source_accuracy)

    def priority(key):
        q = view.questions[key]
        cost = view.remaining[key]
        p_certified = reliability(key)
        free_after = remaining_budget - cost
        hypothetical_dividend = 0.
        for child_key in q.children:
            child = view.questions[child_key]
            child_cost = child.evidence_need + child.heat_need + 1
            if (child_key in view.unlocked or child.source_count < child.evidence_need
                    or child_cost > free_after):
                continue
            # Count only feasible future inquiry; its outcome stays hypothetical.
            predicted_child = reliability(child_key)
            expected_yield = (predicted_child + ledger.child_yield) / 2.
            hypothetical_dividend += (child.value * expected_yield *
                                      min(1., free_after / (2 * child_cost)))
        score = p_certified * (q.value + spark_weight * hypothetical_dividend) / cost
        return score, -cost, key

    return max(view.eligible, key=priority)


def run(seed: int, regime: str, policy: str, spark_weight: float = 1.,
        budget: int = 24) -> dict:
    questions, owner = world(seed, regime)
    furnace = Furnace(questions, owner, budget=budget)
    ledger = EpistemicLedger()
    # Defined independently of latent truth and of the eventual owner receipts.
    child_keys = {child for q in questions.values() for child in q.children}
    while furnace.spent < budget:
        view = furnace.public_view()
        if policy in ('value', 'ratio', 'information'):
            key = fire001_select(view, policy)
        elif policy == 'fire001':
            key = fire001_select(view, 'fire', 1.0)
        elif policy in ('productive_online', 'productive_frozen'):
            key = productive_select(view, ledger, spark_weight)
        else:
            raise ValueError('Unknown policy')
        if key is None:
            break
        receipt = furnace.apply(key)
        if receipt['action'] == 'verify' and policy == 'productive_online':
            ledger.learn(receipt, tuple(x.answer for x in furnace.observed[key]),
                         questions[key].value, key in child_keys)
    return {
        'seed': seed, 'regime': regime, 'policy': policy,
        'verified_value': furnace.score,
        'certified_questions': len(furnace.finished),
        'failed_verifications': furnace.false_attempts,
        'questions_unlocked': len(furnace.unlocked),
        'steps': furnace.spent, 'learning_events': ledger.verified_count,
        'source_accuracy_estimate': round(ledger.source_accuracy, 5),
        'actions': furnace.history,
    }
