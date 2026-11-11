"""FIRE-006: The Price of Revision — live alternatives and reversible weights.

A synthetic, prequential experiment. Three *actual prior FIRE methods* produce
independent forecasts; six resource-matched policies combine them. Each policy
sees only those current forecasts and earlier verified labels. The generator's
truth, regime, actual source roots and future are NEVER passed to a governor.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import exp, log, sqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fire005"))
from discernment import BayesianChangePredictor
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fire004"))
from flame import (
    N_STEPS, REGIMES, Fixed003, Hedge, PublicEpisode, VerifiedLabel,
    make_world, oracle_prediction, validate_receipt,
)

EXPERTS = ("fire003", "hedge", "bocpd")
POLICIES = ("equal3", "exp3", "fixed_share3", "proximal3",
            "fire006_no_rollback", "fire006")
UNIFORM = (1. / 3, 1. / 3, 1. / 3)
REVISION_PRICE = .03
LOOKBACK = 16
FIT_STEPS = 12
STEP_SIZE = .35
PROX_PENALTY = .015
LOOKAHEAD = 8
ENTRY_MARGIN = .012
UNCERTAINTY_WEIGHT = .012
ENTRY_COOLDOWN = 8
TRIAL_WINDOW = 8
ROLLBACK_MARGIN = .005


def clip(p: float) -> float:
    return min(.9999, max(.0001, p))


def project_simplex(z: tuple[float, ...]) -> tuple[float, ...]:
    """Euclidean projection to {w >=0, sum(w)=1}, deterministic and exact."""
    ordered = sorted(z, reverse=True)
    cum = 0.
    threshold = 0.
    for idx, v in enumerate(ordered):
        cum += v
        t = (cum - 1.) / (idx + 1)
        if v > t:
            threshold = t
    weights = tuple(max(0., v - threshold) for v in z)
    normal = sum(weights)
    return tuple(v / normal for v in weights)


def blend(weights, probs):
    return clip(sum(w * p for w, p in zip(weights, probs)))


def tv(left, right):
    return .5 * sum(abs(x - y) for x, y in zip(left, right))


def entropy_effective_number(weights) -> float:
    return 1. / sum(w * w for w in weights)


def fit_candidate(history, previous, penalty=PROX_PENALTY):
    """Receding-horizon online convex optimization of past verified Brier.

    No hidden future outcomes. Deterministic projected gradient iterations;
    returns an admissible convex 3-expert portfolio.
    """
    rows = tuple(history)[-LOOKBACK:]
    if not rows:
        return previous
    w = previous
    for _ in range(FIT_STEPS):
        gradient = [2. * penalty * (w[i] - previous[i]) for i in range(3)]
        for probabilities, actual in rows:
            error = blend(w, probabilities) - actual
            for i in range(3):
                gradient[i] += 2. * error * probabilities[i] / len(rows)
        w = project_simplex(tuple(w[i] - STEP_SIZE * gradient[i]
                                  for i in range(3)))
    return w


@dataclass(frozen=True)
class RevisionReceipt:
    step: int
    operation: str
    previous: tuple[float, ...]
    proposed: tuple[float, ...]
    expected_eight_step_gain: float
    quoted_price: float
    verification_count: int
    status: str = "PENCIL_METHOD_REVISION"
    subsequent_verified_regret: float | None = None


@dataclass
class Portfolio:
    policy: str
    weights: tuple[float, ...] = UNIFORM
    history: deque = field(default_factory=lambda: deque(maxlen=LOOKBACK))
    paid_price: float = 0.
    revisions: int = 0
    held_proposals: int = 0
    rollbacks: int = 0
    receipts: list[RevisionReceipt] = field(default_factory=list)
    _trial: dict | None = None
    _last_edit: int = -ENTRY_COOLDOWN
    _last_forecast_step: int = -1
    _last_update_step: int = -1
    _last_probs: tuple[float, ...] | None = None

    def __post_init__(self):
        if self.policy not in POLICIES:
            raise ValueError("Unknown experimental portfolio policy")

    def forecast(self, step: int, probs: tuple[float, ...]) -> float:
        if step <= self._last_forecast_step or len(probs) != 3:
            raise ValueError("One ordered forecast per independent round required")
        self._last_probs = tuple(clip(p) for p in probs)
        self._last_forecast_step = step
        return blend(self.weights, probs)

    def _change(self, step: int, target, operation: str,
                forecast_gain: float = 0., evidence_count: int = 0,
                verified_regret: float | None = None):
        old = self.weights
        target = project_simplex(tuple(target))
        cost = REVISION_PRICE * tv(old, target)
        if cost <= 1e-12:
            return
        self.weights = target
        self.paid_price += cost
        self._last_edit = step
        if operation == "ROLLBACK":
            self.rollbacks += 1
        else:
            self.revisions += 1
        self.receipts.append(RevisionReceipt(
            step=step, operation=operation,
            previous=old, proposed=target,
            expected_eight_step_gain=round(forecast_gain, 9),
            quoted_price=round(cost, 9),
            verification_count=evidence_count,
            subsequent_verified_regret=None if verified_regret is None
                                     else round(verified_regret, 9)
        ))

    def update(self, case: PublicEpisode, receipt: VerifiedLabel,
               last_step: bool = False):
        validate_receipt(case, receipt)
        if (self._last_forecast_step != case.step or
                self._last_update_step >= case.step or self._last_probs is None):
            raise ValueError("Cannot revise method without preceding forecast")
        y = int(receipt.actual)
        probs = self._last_probs
        self._last_update_step = case.step
        self.history.append((probs, y))
        if self._trial is not None:
            trial = self._trial
            old_p = blend(trial["old"], probs)
            new_p = blend(trial["new"], probs)
            trial["loss_deltas"].append((new_p - y) ** 2 - (old_p - y) ** 2)
            if len(trial["loss_deltas"]) == TRIAL_WINDOW:
                empirical = sum(trial["loss_deltas"]) / TRIAL_WINDOW
                if empirical > ROLLBACK_MARGIN and not last_step:
                    self._change(case.step, trial["old"], "ROLLBACK",
                                 evidence_count=TRIAL_WINDOW,
                                 verified_regret=empirical)
                self._trial = None

        if last_step:
            return
        if self.policy == "equal3":
            return
        if self.policy in ("exp3", "fixed_share3"):
            scores = [w * exp(-2. * (p - y) ** 2)
                      for w, p in zip(self.weights, probs)]
            denom = sum(scores)
            proposal = tuple(x / denom for x in scores)
            if self.policy == "fixed_share3":
                proposal = tuple(.98 * x + .02 / 3 for x in proposal)
            self._change(case.step, proposal, self.policy.upper(),
                         evidence_count=len(self.history))
            return
        if len(self.history) < LOOKBACK:
            return
        if self.policy == "proximal3":
            proposal = fit_candidate(self.history, self.weights)
            self._change(case.step, proposal, "PROXIMAL",
                         evidence_count=len(self.history))
            return
        if self._trial is not None or case.step - self._last_edit < ENTRY_COOLDOWN:
            return
        # Both FIRE-006 variants use the *same* candidate and same cost model.
        proposal = fit_candidate(self.history, self.weights)
        future_gain = []
        for row_probs, answer in self.history:
            future_gain.append((blend(self.weights, row_probs) - answer) ** 2 -
                               (blend(proposal, row_probs) - answer) ** 2)
        mean_gain = sum(future_gain) / len(future_gain)
        uncertainty = sqrt(sum((gain - mean_gain) ** 2 for gain in future_gain) /
                           len(future_gain))
        expected = LOOKAHEAD * mean_gain
        price = REVISION_PRICE * tv(self.weights, proposal)
        condition = expected >= price + ENTRY_MARGIN + UNCERTAINTY_WEIGHT * uncertainty
        if not condition:
            if tv(self.weights, proposal) > 1e-9:
                self.held_proposals += 1
                self.receipts.append(RevisionReceipt(
                    step=case.step, operation="PRESERVE_PENCIL",
                    previous=self.weights, proposed=tuple(proposal),
                    expected_eight_step_gain=round(expected, 9),
                    quoted_price=round(price, 9),
                    verification_count=len(self.history)
                ))
            return
        if (self.policy == "fire006" and
                case.step + TRIAL_WINDOW >= N_STEPS):
            return  # Cannot verify an eight-step trial beyond the experiment.
        old = self.weights
        self._change(case.step, proposal, "TRIAL_REVISION",
                     forecast_gain=expected, evidence_count=len(self.history))
        if self.policy == "fire006" and tv(old, self.weights) > 1e-12:
            self._trial = {"old": old, "new": self.weights, "loss_deltas": []}


def evaluate(seed: int, regime: str) -> dict:
    """Shared three live experts; all policies see the same public predictions."""
    w = make_world(seed, regime)
    experts = (Fixed003(), Hedge(False), BayesianChangePredictor())
    portfolios = {key: Portfolio(key) for key in POLICIES}
    results = {name: {"brier": 0., "log_loss": 0., "covered": 0,
                      "covered_correct": 0, "high_confidence_wrong": 0,
                      "eff_number": 0., "errors": []}
               for name in POLICIES}
    for step in range(N_STEPS):
        case = w.view(step)
        predictions = tuple(expert.predict(case) for expert in experts)
        proposed = {key: policy.forecast(step, predictions)
                    for key, policy in portfolios.items()}
        receipt = w.verify(step)  # Independent synthetic ground truth gate.
        y = int(receipt.actual)
        for name, prob in proposed.items():
            row = results[name]
            err = (prob - y) ** 2
            row["brier"] += err
            row["log_loss"] -= log(prob if y else 1. - prob)
            row["errors"].append(err)
            row["eff_number"] += entropy_effective_number(portfolios[name].weights)
            if max(prob, 1 - prob) >= .7:
                row["covered"] += 1
                row["covered_correct"] += int((prob >= .5) is receipt.actual)
            if max(prob, 1 - prob) >= .95 and ((prob >= .5) is not receipt.actual):
                row["high_confidence_wrong"] += 1
        for expert in experts:
            expert.update(case, receipt)
        for policy in portfolios.values():
            policy.update(case, receipt, last_step=(step == N_STEPS - 1))
    output = {}
    for name, row in results.items():
        policy = portfolios[name]
        output[name] = {
            "brier": round(row["brier"] / N_STEPS, 8),
            "log_loss": round(row["log_loss"] / N_STEPS, 8),
            "revision_price": round(policy.paid_price / N_STEPS, 8),
            "total_loss_with_price": round((row["brier"] + policy.paid_price) /
                                            N_STEPS, 8),
            "coverage": round(row["covered"] / N_STEPS, 8),
            "selective_accuracy": round(row["covered_correct"] /
                                        row["covered"], 8) if row["covered"] else None,
            "overconfident_errors": row["high_confidence_wrong"],
            "effective_hypotheses": round(row["eff_number"] / N_STEPS, 8),
            "revisions": policy.revisions,
            "rollback_count": policy.rollbacks,
            "rejected_proposals": policy.held_proposals,
            "early_post48_brier": round(sum(row["errors"][48:64]) / 16, 8),
            "late_post48_brier": round(sum(row["errors"][80:96]) / 16, 8),
            "receipts": [vars(r) for r in policy.receipts]
        }
    return output
