"""FIRE-005: Bayesian change-point research and reversible methods.

All forecasts use public FIRE-004 episode observations and *previous* verified
feedback only. The hidden physical generator, future labels, true roots, and
experiment regime are never visible to a predictor or switch controller.
No autonomous code changes or real-world actuation are permitted.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import exp, log
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fire004"))
from flame import (
    N_STEPS, REGIMES, Fixed003, Hedge, PublicEpisode, VerifiedLabel,
    make_world, oracle_prediction, roots_only, aggregate, validate_receipt,
)

REGRET_WINDOW = 12
CP_WINDOW = 6
MIN_SUCCESSFUL_REGRETS = 8
ENTRY_REGRET = .012
ROLLBACK_REGRET = -.007
ENTRY_CP_SCORE = .035
MIN_CP_EVENTS = 2
MIN_ENTRY_GAP = 12
MIN_ACTIVE = 8
BOCPD_HAZARD = .025
BOCPD_PRIOR = (2., 1.)
BOCPD_MAX_STATES = 40


@dataclass(frozen=True)
class RunState:
    mass: float
    successes: float
    failures: float


class RootRunLength:
    """Beta--Bernoulli Bayesian online changepoint posterior, per source root.

    p_t(y | state) is evaluated on current verified correctness *after* the
    earlier forecast. A hazard change hypothesis starts a new Beta(2,1)
    segment. Up to 40 posterior components are kept; truncation is explicit.
    """
    def __init__(self, hazard=BOCPD_HAZARD, alpha=BOCPD_PRIOR[0],
                 beta=BOCPD_PRIOR[1], maximum=BOCPD_MAX_STATES):
        if not (0 <= hazard <= 1) or alpha <= 0 or beta <= 0 or maximum < 2:
            raise ValueError("Invalid Bayesian change filter configuration")
        self.hazard, self.alpha, self.beta, self.maximum = hazard, alpha, beta, maximum
        self.states = [RunState(1., alpha, beta)]
        self.last_changepoint_posterior = hazard
        self.updates = 0

    def predict_correctness(self) -> float:
        return sum(state.mass * state.successes /
                   (state.successes + state.failures) for state in self.states)

    def learn(self, correct: bool) -> float:
        if type(correct) is not bool:
            raise ValueError("Cannot update without a Boolean verified match")
        y = int(correct)
        old_states = self.states
        restart_like = self.alpha / (self.alpha + self.beta) if y else (
            self.beta / (self.alpha + self.beta))
        restart_mass = self.hazard * restart_like
        candidates = [RunState(restart_mass, self.alpha + y, self.beta + 1 - y)]
        for old in old_states:
            evidence_like = (old.successes if y else old.failures) / (
                old.successes + old.failures)
            candidates.append(RunState(old.mass * (1 - self.hazard) * evidence_like,
                                       old.successes + y, old.failures + 1 - y))
        total = sum(row.mass for row in candidates)
        if total <= 0:
            raise ArithmeticError("Filter lost all probability mass")
        self.last_changepoint_posterior = restart_mass / total
        candidates = sorted(candidates, key=lambda row: row.mass, reverse=True)
        keep = candidates[:self.maximum]
        normalization = sum(row.mass for row in keep)
        self.states = [RunState(row.mass / normalization, row.successes, row.failures)
                       for row in keep]
        self.updates += 1
        return self.last_changepoint_posterior


class BayesianChangePredictor:
    """Live source identities come from attestation, NOT true hidden ancestry."""
    def __init__(self):
        self.roots: dict[str, RootRunLength] = {}
        self.last_forecast_step = -1
        self.last_update_step = -1
        self.changepoint_score = 0.
        self.forecast_history: list[dict] = []

    def predict(self, case: PublicEpisode) -> float:
        if case.step <= self.last_forecast_step:
            raise ValueError("Nonmonotone or repeated BOCPD forecast")
        rows = roots_only(case)
        prediction = aggregate(rows, {
            root: self.roots[root].predict_correctness()
                  if root in self.roots else BOCPD_PRIOR[0] / sum(BOCPD_PRIOR)
            for root, _ in rows
        })
        self.last_forecast_step = case.step
        return prediction

    def update(self, case: PublicEpisode, receipt: VerifiedLabel) -> float:
        validate_receipt(case, receipt)
        if self.last_forecast_step != case.step or self.last_update_step >= case.step:
            raise ValueError("No valid prequential prediction before BOCPD update")
        change_posteriors = []
        for root, answer in roots_only(case):
            state = self.roots.setdefault(root, RootRunLength())
            change_posteriors.append(state.learn(answer is receipt.actual))
        self.changepoint_score = sum(change_posteriors) / len(change_posteriors)
        self.forecast_history.append({
            "step": case.step, "mean_changepoint_posterior":
                round(self.changepoint_score, 8),
            "attested_distinct_roots": len(change_posteriors)
        })
        self.last_update_step = case.step
        return self.changepoint_score


@dataclass(frozen=True)
class PolicyReceipt:
    step: int
    from_method: str
    to_method: str
    reason: str
    mean_verified_regret: float
    change_indicators: int
    status: str = "PENCIL_REVERSIBLE_METHOD_EDIT"


class ReversibleGovernor:
    """Evidence-triggered method switch with explicit rollback and cooldown."""
    def __init__(self, require_change_indicator=True):
        self.require_change_indicator = require_change_indicator
        self.mode = "hedge"
        self.regrets = deque(maxlen=REGRET_WINDOW)
        self.change_indicators = deque(maxlen=CP_WINDOW)
        self.last_change_step = -MIN_ENTRY_GAP
        self.last_reentry_step = -MIN_ENTRY_GAP
        self.receipts: list[PolicyReceipt] = []
        self.history: list[tuple[int, str]] = []

    def predict(self, step: int, hedge_p: float, bocpd_p: float) -> float:
        self.history.append((step, self.mode))
        return hedge_p if self.mode == "hedge" else bocpd_p

    def update(self, case: PublicEpisode, receipt: VerifiedLabel,
               hedge_p: float, bocpd_p: float, changepoint_score: float):
        validate_receipt(case, receipt)
        y = int(receipt.actual)
        regret = (hedge_p - y) ** 2 - (bocpd_p - y) ** 2
        self.regrets.append(regret)
        self.change_indicators.append(changepoint_score > ENTRY_CP_SCORE)
        if self.mode == "hedge":
            recent = list(self.regrets)
            has_regret_support = (len(recent) >= REGRET_WINDOW and
                                  sum(recent) / len(recent) >= ENTRY_REGRET and
                                  sum(d > 0 for d in recent) >= MIN_SUCCESSFUL_REGRETS)
            has_change_support = (not self.require_change_indicator or
                                  (len(self.change_indicators) == CP_WINDOW and
                                   sum(self.change_indicators) >= MIN_CP_EVENTS))
            allowed_reentry = case.step - self.last_change_step >= MIN_ENTRY_GAP
            if has_regret_support and has_change_support and allowed_reentry:
                self._switch(case.step, "bocpd", "SUSTAINED_VERIFIED_ADVANTAGE")
        elif case.step - self.last_change_step >= MIN_ACTIVE:
            recent = list(self.regrets)[-MIN_ACTIVE:]
            if len(recent) == MIN_ACTIVE and sum(recent) / len(recent) <= ROLLBACK_REGRET:
                self._switch(case.step, "hedge", "REVOKED_BY_VERIFIED_REGRET")

    def _switch(self, step: int, target: str, reason: str):
        previous = self.mode
        if previous == target:
            raise ValueError("No method revision occurred")
        self.mode = target
        self.last_change_step = step
        self.receipts.append(PolicyReceipt(
            step, previous, target, reason,
            round(sum(self.regrets) / len(self.regrets), 8),
            sum(self.change_indicators)))


class ClassicalTwoExpertHedge:
    """Standard online model averaging with prequential Brier-loss updates."""
    def __init__(self):
        self.weights = [.5, .5]
        self.forgetting = .97
        self.eta = 2.

    def predict(self, hedge_p: float, bocpd_p: float) -> float:
        return self.weights[0] * hedge_p + self.weights[1] * bocpd_p

    def update(self, case: PublicEpisode, receipt: VerifiedLabel,
               hedge_p: float, bocpd_p: float):
        validate_receipt(case, receipt)
        y = int(receipt.actual)
        scores = [(weight ** self.forgetting) *
                  exp(-self.eta * (p - y) ** 2)
                  for weight, p in zip(self.weights, (hedge_p, bocpd_p))]
        total = sum(scores)
        self.weights = [score / total for score in scores]


MODEL_NAMES = ("fire003", "fire004", "hedge", "bocpd",
               "mix50", "hedge2", "regret_only", "fire005", "oracle")


def evaluate(seed: int, regime: str) -> dict:
    """Every model forecasts BEFORE the independent synthetic label is revealed."""
    world = make_world(seed, regime)
    fire003 = Fixed003()
    fire004 = Hedge(True)
    hedge = Hedge(False)
    bocpd = BayesianChangePredictor()
    hedge2 = ClassicalTwoExpertHedge()
    regret_only = ReversibleGovernor(False)
    fire005 = ReversibleGovernor(True)
    store = {name: {
        "brier": 0., "log_loss": 0., "answered": 0,
        "correct_on_answered": 0, "overconfident_errors": 0,
        "squared": []} for name in MODEL_NAMES}

    for step in range(N_STEPS):
        case = world.view(step)
        p_fixed = fire003.predict(case)
        p_fire004 = fire004.predict(case)
        p_hedge = hedge.predict(case)
        p_bocpd = bocpd.predict(case)
        predictions = {
            "fire003": p_fixed, "fire004": p_fire004,
            "hedge": p_hedge, "bocpd": p_bocpd,
            "mix50": .5 * (p_hedge + p_bocpd),
            "hedge2": hedge2.predict(p_hedge, p_bocpd),
            "regret_only": regret_only.predict(step, p_hedge, p_bocpd),
            "fire005": fire005.predict(step, p_hedge, p_bocpd),
            "oracle": oracle_prediction(world, step),
        }
        receipt = world.verify(step)
        y = int(receipt.actual)
        for name, probability in predictions.items():
            probability = max(.0001, min(.9999, probability))
            row = store[name]
            err = (probability - y) ** 2
            row["brier"] += err
            row["squared"].append(err)
            row["log_loss"] -= log(probability if y else 1 - probability)
            if max(probability, 1 - probability) >= .95 and (
                    (probability >= .5) is not receipt.actual):
                row["overconfident_errors"] += 1
            if max(probability, 1 - probability) >= .70:
                row["answered"] += 1
                row["correct_on_answered"] += int(
                    (probability >= .5) is receipt.actual)
        # Feedback only now crosses from the independent synthetic owner.
        fire003.update(case, receipt)
        fire004.update(case, receipt)
        hedge.update(case, receipt)
        cp_score = bocpd.update(case, receipt)
        hedge2.update(case, receipt, p_hedge, p_bocpd)
        regret_only.update(case, receipt, p_hedge, p_bocpd, cp_score)
        fire005.update(case, receipt, p_hedge, p_bocpd, cp_score)

    out = {}
    for name, row in store.items():
        out[name] = {
            "brier": round(row["brier"] / N_STEPS, 8),
            "log_loss": round(row["log_loss"] / N_STEPS, 8),
            "coverage": round(row["answered"] / N_STEPS, 8),
            "selective_accuracy": round(row["correct_on_answered"] /
                                        row["answered"], 8) if row["answered"] else None,
            "high_confidence_wrong": row["overconfident_errors"],
            "early_post_48_brier": round(sum(row["squared"][48:64]) / 16, 8),
            "late_post_48_brier": round(sum(row["squared"][80:96]) / 16, 8),
        }
    for key, governor in (("fire005", fire005), ("regret_only", regret_only)):
        events = governor.receipts
        out[key]["switches"] = sum(r.to_method == "bocpd" for r in events)
        out[key]["rollbacks"] = sum(r.to_method == "hedge" for r in events)
        out[key]["switch_steps"] = [r.step for r in events if r.to_method == "bocpd"]
        out[key]["rollback_steps"] = [r.step for r in events if r.to_method == "hedge"]
        out[key]["receipts"] = [vars(r) for r in events]
    out["bocpd"]["cp_scores"] = [
        entry["mean_changepoint_posterior"] for entry in bocpd.forecast_history]
    return out
