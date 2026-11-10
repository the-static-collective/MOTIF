"""MOTIF GENIUS-004 — THE HUMILITY APERTURE.

A tiny, conventional, source-bound online shift/rejection policy:
RETAIN / REVISE / REFRAME / RELEASE / ASK / HOLD.
These are experiment labels, NOT mental states or judgments of people.
The only labels are simulated participants' explicit binary self-reports.
Never contact anyone, reveal withheld reports, or authorize action.

All results are authored synthetic, not externally blinded. Policy search
uses earlier simulator worlds, and compares strong classical competitors.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
import json
import math
import random
from typing import Optional

TOPICS = ("speed", "safety", "privacy", "fairness")
ARMS = ("FROZEN", "CUMULATIVE", "WINDOW4", "WINDOW8", "EWMA", "HEDGE", "GLOBAL")
ABSTAIN_COST = 0.25  # fixed nonzero review/abstention cost in Brier units
MIN_HISTORY = 4      # below this, decline to invent a new participant profile


@dataclass(frozen=True)
class Observation:
    event_id: str
    node: str
    topic: str
    yes: bool
    shareable: bool
    opt_in: bool
    evidence_ref: str
    private_note: str = ""


def public_projection(rows: tuple[Observation, ...]) -> tuple[Observation, ...]:
    """Remove all private observations AND redact private notes in public ones."""
    return tuple(
        Observation(r.event_id, r.node, r.topic, r.yes, True, r.opt_in,
                    r.evidence_ref, "") for r in rows if r.shareable
    )


def smoothed(items: list[bool], *, alpha: float = 2.0) -> float:
    return (sum(items) + alpha / 2) / (len(items) + alpha)


def brier(prob: float, label: bool) -> float:
    return (prob - int(label)) ** 2


@dataclass
class Learner:
    """All branches see exactly the same past public reports."""

    history: dict[tuple[str, str], list[bool]] = field(
        default_factory=lambda: defaultdict(list))
    global_history: list[bool] = field(default_factory=list)
    seen_ids: set[str] = field(default_factory=set)
    baseline: dict[tuple[str, str], float] = field(default_factory=dict)
    expert_weights: dict[tuple[str, str], dict[str, float]] = field(
        default_factory=dict)
    frozen: bool = False

    def seed(self, training: tuple[Observation, ...]) -> "Learner":
        for r in public_projection(training):
            self.ingest(r)
        self.baseline = {
            key: smoothed(vals) for key, vals in self.history.items()
            if len(vals) >= MIN_HISTORY
        }
        self.frozen = True
        return self

    def _estimated(self, key: tuple[str, str]) -> dict[str, Optional[float]]:
        obs = self.history.get(key, [])
        if len(obs) < MIN_HISTORY:
            return {name: None for name in ARMS}
        c = smoothed(obs)
        w4 = smoothed(obs[-4:], alpha=1.0)
        w8 = smoothed(obs[-8:], alpha=2.0)
        p = .5
        for outcome in obs:
            p = 0.72 * p + 0.28 * int(outcome)
        experts = {"CUMULATIVE": c, "WINDOW4": w4, "WINDOW8": w8, "EWMA": p}
        weights = self.expert_weights.get(key)
        if weights is None:
            weights = {k: 1.0 for k in experts}
        weight_total = sum(weights.values())
        hedge = sum(experts[k] * weights[k] for k in experts) / weight_total
        return {
            "FROZEN": self.baseline.get(key),
            "CUMULATIVE": c, "WINDOW4": w4, "WINDOW8": w8,
            "EWMA": p, "HEDGE": hedge,
            "GLOBAL": smoothed(self.global_history),
        }

    def predict(self, node: str, topic: str) -> dict[str, Optional[float]]:
        return self._estimated((node, topic))

    def ingest(self, r: Observation) -> bool:
        if not r.shareable:
            return False
        if not r.event_id or not r.node or not r.topic or not r.evidence_ref:
            raise ValueError("A shared report requires a unique ID, owner, topic, evidence pointer")
        if type(r.yes) is not bool:
            raise ValueError("Only explicit binary responses allowed in this toy")
        if r.event_id in self.seen_ids:
            raise ValueError("Source report cannot be replayed")
        if r.private_note:
            # The model only accepts the minimal public representation.
            raise ValueError("Private note must be stripped before ingress")
        self.seen_ids.add(r.event_id)
        key = (r.node, r.topic)
        priors = self._estimated(key) if key in self.history else {}
        if priors and priors.get("CUMULATIVE") is not None:
            weights = self.expert_weights.setdefault(
                key, {k: 1.0 for k in ("CUMULATIVE", "WINDOW4", "WINDOW8", "EWMA")})
            for arm in weights:
                weights[arm] *= math.exp(-2.0 * brier(priors[arm], r.yes))
            # ratios, not absolute weights, matter: normalize to avoid underflow.
            total = sum(weights.values())
            if total <= 0:
                weights.update({name: 1.0 for name in weights})
            else:
                weights.update({name: w / total for name, w in weights.items()})
        self.history[key].append(r.yes)
        self.global_history.append(r.yes)
        return True


@dataclass(frozen=True)
class Policy:
    revise_gap: float
    release_gap: float
    ask_margin: float
    reframe_topics: int = 2

    def as_dict(self) -> dict:
        return {
            "revise_gap": self.revise_gap,
            "release_gap": self.release_gap,
            "ask_margin": self.ask_margin,
            "reframe_topics": self.reframe_topics,
        }


POLICIES = tuple(
    Policy(r, l, q) for r in (0.12, 0.20, 0.30)
    for l in (0.35, 0.48, 0.60)
    for q in (0.0, 0.06)
)


def decide(model: Learner, row: Observation, policy: Policy) -> dict:
    """Plan a prediction or an ASK; only current and past data are inspectable."""
    probs = model.predict(row.node, row.topic)
    key = (row.node, row.topic)
    h = model.history.get(key, [])
    c = probs["CUMULATIVE"]
    if c is None:
        action = "ASK" if row.opt_in else "HOLD"
        return {"action": action, "probability": None, "gap": None,
                "reasons": ["no sufficiently documented prior for this node/topic"],
                "question": "Would you voluntarily state your preference?"
                            if action == "ASK" else None}

    recent = probs["WINDOW4"]
    gap = abs(c - recent)
    # An agreement across >=2 topics is not proof of global preference shift,
    # but it warrants questioning a single-topic explanation.
    divergent_topics = sum(
        abs(p["CUMULATIVE"] - p["WINDOW4"]) >= policy.revise_gap
        for topic in TOPICS
        if (p := model.predict(row.node, topic))["CUMULATIVE"] is not None
    )

    if len(h) >= 8 and gap >= policy.release_gap:
        action, probability = "RELEASE", None
        reasons = ["large conflict between historical and recent reports; withhold forecast"]
    elif gap >= policy.revise_gap and divergent_topics >= policy.reframe_topics:
        action, probability = "REFRAME", probs["EWMA"]
        reasons = ["multiple topics conflict with old assumptions; use a short-memory representation"]
    elif gap >= policy.revise_gap:
        action, probability = "REVISE", recent
        reasons = ["recent public evidence differs from accumulated history"]
    elif abs(c - .5) <= policy.ask_margin and row.opt_in:
        action, probability = "ASK", None
        reasons = ["prediction equivocal; voluntary clarification could help"]
    else:
        action, probability = "RETAIN", c
        reasons = ["no strong source-observed contradiction requiring replacement"]

    return {
        "action": action,
        "probability": probability,
        "gap": round(gap, 6),
        "reasons": reasons,
        "observed_history_size": len(h),
        "divergent_topics": divergent_topics,
        "question": "Would you voluntarily clarify this topic?" if action == "ASK" else None,
        "no_external_action": True,
    }


def _metrics(losses: list[float], accepted_losses: list[float],
             counts: Counter, false_flags: int = 0) -> dict:
    return {
        "graded_events": len(losses),
        "accepted_events": len(accepted_losses),
        "coverage": round(len(accepted_losses) / len(losses), 6) if losses else None,
        "mean_costed_brier": round(sum(losses) / len(losses), 6) if losses else None,
        "selective_brier": round(sum(accepted_losses) / len(accepted_losses), 6)
                           if accepted_losses else None,
        "action_counts": dict(sorted(counts.items())),
        "false_alarm_events_on_stable": false_flags,
    }


def evaluate(training: tuple[Observation, ...],
             future: tuple[Observation, ...], policy: Policy,
             scenario: str, *, record_receipts: bool = False) -> dict:
    """A strict prequential (predict-then-update) evaluation for all arms.

    Withheld events are not scored or fed back. Novel targets may not get
    predictions even if a global prior exists. Every forecast is made
    BEFORE the current self-report is read.
    """
    model = Learner().seed(training)
    counts = Counter()
    losses = {arm: [] for arm in ARMS + ("HUMILITY",)}
    accepted = {arm: [] for arm in ARMS + ("HUMILITY",)}
    marked_false = 0
    withheld = 0
    novelty = 0
    receipts = []
    for row in future:
        if not row.shareable:
            withheld += 1
            continue
        current = Observation(row.event_id, row.node, row.topic, row.yes,
                              True, row.opt_in, row.evidence_ref)
        probs = model.predict(current.node, current.topic)
        out = decide(model, current, policy)
        countable = any(p is not None for p in probs.values())
        if not countable:
            novelty += 1
        counts[out["action"]] += 1
        if scenario.startswith("STABLE") and out["action"] in ("REVISE", "REFRAME", "RELEASE"):
            marked_false += 1
        for arm in ARMS:
            p = probs[arm]
            score = ABSTAIN_COST if p is None else brier(p, current.yes)
            losses[arm].append(score)
            if p is not None:
                accepted[arm].append(score)
        chosen_p = out["probability"]
        chosen_loss = ABSTAIN_COST if chosen_p is None else brier(chosen_p, current.yes)
        losses["HUMILITY"].append(chosen_loss)
        if chosen_p is not None:
            accepted["HUMILITY"].append(chosen_loss)
        if record_receipts:
            receipts.append({
                "event_id": current.event_id, "node": current.node, "topic": current.topic,
                "evidence_ref": current.evidence_ref,
                "prior_heldout_forecast": None if chosen_p is None else round(chosen_p, 6),
                "action": out["action"],
                "public_self_report": current.yes,
                "costed_brier": round(chosen_loss, 6),
                "reason": out["reasons"][0],
                "new_evidence_used_only_after_forecast": True,
            })
        model.ingest(current)

    return {
        "scenario": scenario, "withheld_excluded": withheld,
        "unseen_pair_first_response_abstentions": novelty,
        "policy": policy.as_dict(),
        "method": {k: _metrics(losses[k], accepted[k], counts if k == "HUMILITY" else Counter(),
                               marked_false if k == "HUMILITY" else 0)
                   for k in ARMS + ("HUMILITY",)},
        "receipts": receipts if record_receipts else [],
    }


def build_world(seed: int, regime: str, *,
                n_targets: int = 12, train_rounds: int = 18,
                future_rounds: int = 16) -> tuple[tuple[Observation, ...], tuple[Observation, ...]]:
    """Synthetic, temporally ordered future; only simulator knows latent rates."""
    if regime not in ("STABLE", "ABRUPT", "LOCAL", "GRADUAL", "STABLE_NOISY"):
        raise ValueError("Unknown scenario")
    rng = random.Random(seed)
    nodes = tuple("node_%02d" % i for i in range(n_targets))
    rates = {
        (n, topic): (
            rng.choice((.44, .56)) if regime == "STABLE_NOISY"
            else rng.choice((.08, .18, .28, .72, .82, .92))
        ) for n in nodes for topic in TOPICS
    }
    def make_rows(rounds: int, stage: str) -> tuple[Observation, ...]:
        rows = []
        for t in range(rounds):
            for i, node in enumerate(nodes):
                for j, topic in enumerate(TOPICS):
                    p = rates[(node, topic)]
                    if stage == "future":
                        if regime == "ABRUPT" and t >= 5:
                            p = 1 - p
                        elif regime == "LOCAL" and t >= 5 and topic == "safety" and i % 3 == 0:
                            p = 1 - p
                        elif regime == "GRADUAL":
                            fraction = t / max(1, rounds - 1)
                            p = (1 - fraction) * p + fraction * (1 - p)
                    can_share = (t + i + 2*j) % 11 != 0
                    yes = rng.random() < p
                    rows.append(Observation(
                        event_id=f"{seed}/{stage}/{t}/{node}/{topic}",
                        node=node, topic=topic, yes=yes,
                        shareable=can_share,
                        opt_in=(i + j) % 2 == 0,
                        evidence_ref=f"synthetic:{seed}/{stage}/{t}/{node}/{topic}",
                        private_note="NEVER_EXPOSE_PRIVATE_SIMULATOR_NOTES"))
            # The future includes an unknown visitor to test abstention.
            if stage == "future":
                node = f"visitor_{seed}"
                rows.append(Observation(
                    event_id=f"{seed}/future/{t}/{node}",
                    node=node, topic="safety", yes=rng.random() < .5,
                    shareable=t % 4 != 0, opt_in=t % 2 == 0,
                    evidence_ref=f"synthetic:{seed}/future/{t}/{node}",
                    private_note="NEVER_EXPOSE_PRIVATE_SIMULATOR_NOTES"))
        return tuple(rows)
    return make_rows(train_rounds, "train"), make_rows(future_rounds, "future")


def run() -> dict:
    """Tuning regimes and seeds are preset; holdout authored by same engineer."""
    val_seeds = (40401, 40402)
    future_seeds = (40421, 40422)
    regimes = ("STABLE", "ABRUPT", "LOCAL", "GRADUAL", "STABLE_NOISY")
    validation_worlds = [
        (s, regime, *build_world(s, regime))
        for s in val_seeds for regime in regimes
    ]
    scores = []
    for policy in POLICIES:
        costs = [
            evaluate(train, future, policy, regime)["method"]["HUMILITY"]["mean_costed_brier"]
            for _, regime, train, future in validation_worlds
        ]
        scores.append({
            "policy": policy,
            "mean_validation_cost": sum(costs) / len(costs),
            "worst_validation_cost": max(costs),
        })
    # Minimize macro-average cost first; penalize overly selective policies
    # through explicit ABSTAIN_COST rather than giving abstention zero loss.
    selected = min(scores, key=lambda x: (
        round(x["mean_validation_cost"], 9),
        round(x["worst_validation_cost"], 9),
        POLICIES.index(x["policy"]),
    ))["policy"]
    freeze = {
        "policy": selected.as_dict(),
        "validation_seeds": val_seeds,
        "future_seeds": future_seeds,
        "regimes": regimes,
        "fixed_abstain_cost": ABSTAIN_COST,
        "evaluation": "PREQUENTIAL_BRIER_WITH_COSTED_DEFERRAL",
        "model_operators": "CLASSICAL_FIXED_RULES_AND_FREQUENCY_EXPERTS",
    }
    frozen_sha = sha256(json.dumps(freeze, sort_keys=True).encode()).hexdigest()
    # New challenge worlds materialize only *after* policy and hash freeze.
    results = {}
    for seed in future_seeds:
        results[str(seed)] = {}
        for regime in regimes:
            train, future = build_world(seed, regime)
            results[str(seed)][regime] = evaluate(
                train, future, selected, regime, record_receipts=True)
    totals = {}
    for regime in regimes:
        totals[regime] = {
            arm: round(
                sum(results[str(s)][regime]["method"][arm]["mean_costed_brier"]
                    for s in future_seeds) / len(future_seeds), 6)
            for arm in ARMS + ("HUMILITY",)
        }
    return {
        "status": "RESEARCH_HOLD_NOT_EXTERNAL_PROOF",
        "experiment": "MOTIF-GENIUS-004",
        "authorship": "ALL_GENERATORS_AND_ACTION_GRAMMARS_ENGINEER_AUTHORED",
        "selected_policy": selected.as_dict(),
        "validation_world_count": len(validation_worlds),
        "validation_scores": [{
            "policy": x["policy"].as_dict(),
            "mean_cost": round(x["mean_validation_cost"], 6),
            "worst_cost": round(x["worst_validation_cost"], 6),
        } for x in scores],
        "pre_future_policy_sha256": frozen_sha,
        "costed_brier_by_regime": totals,
        "holdouts": results,
        "interpretation": "HUMILITY is a threshold selector over classical methods, not a novel estimator",
        "no_human_contact_no_external_action": True,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, sort_keys=True, indent=2))
