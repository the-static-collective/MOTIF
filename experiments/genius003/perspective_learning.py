"""MOTIF-GENIUS-003 — correctable, source-bound perspective predictions.

Engineer-authored synthetic *self-report* benchmark, not a model of human
motives. Predict only a participant's explicitly shared option response.
Fit standard Beta/Bernoulli frequency estimators on earlier shared reports.
Never inspect withheld reports or future responses while fitting/freezing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import random
from typing import Optional


TOPICS = ("speed", "safety", "privacy", "fairness")
ARMS = ("global", "topic", "target", "target_topic", "shrink")


@dataclass(frozen=True)
class Report:
    case_id: str
    target: str
    topic: str
    yes: bool
    shareable: bool
    evidence_ref: str
    private_note: str = ""


def public_only(reports: tuple[Report, ...]) -> tuple[Report, ...]:
    """Projection: remove withheld records AND strip all simulator-private notes."""
    return tuple(
        Report(case_id=r.case_id, target=r.target, topic=r.topic, yes=r.yes,
               shareable=True, evidence_ref=r.evidence_ref, private_note="")
        for r in reports if r.shareable
    )


@dataclass
class FrequencyModel:
    """Classical smoothed Bernoulli counts; nothing is inferred about motives."""

    counts: dict[tuple[str, ...], list[int]] = field(default_factory=dict)
    known_targets: set[str] = field(default_factory=set)
    known_topics: set[str] = field(default_factory=set)
    seen_cases: set[tuple[str, str]] = field(default_factory=set)

    def update(self, row: Report) -> bool:
        if not row.shareable:
            return False
        if not row.target or not row.topic or not row.case_id or not row.evidence_ref:
            raise ValueError("Each public report requires source and evidence pointer")
        if type(row.yes) is not bool:
            raise ValueError("Self-report outcome must be boolean")
        key = (row.target, row.case_id)
        if key in self.seen_cases:
            raise ValueError("Duplicate source event; no echo amplification")
        self.seen_cases.add(key)
        self.known_targets.add(row.target)
        self.known_topics.add(row.topic)
        for k in (("global",), ("topic", row.topic), ("target", row.target),
                  ("target_topic", row.target, row.topic)):
            bucket = self.counts.setdefault(k, [0, 0])
            bucket[0] += int(row.yes)
            bucket[1] += 1
        return True

    def fit(self, reports: tuple[Report, ...]) -> "FrequencyModel":
        for row in public_only(reports):
            self.update(row)
        return self

    def count(self, target: str, topic: str) -> int:
        return self.counts.get(("target_topic", target, topic), [0, 0])[1]

    def predict(self, target: str, topic: str, arm: str) -> Optional[float]:
        if arm not in ARMS:
            raise ValueError("Unknown comparator")
        # We may have marginal information, but claim no personal understanding
        # of a target or topic that has never furnished public feedback.
        if target not in self.known_targets or topic not in self.known_topics:
            return None
        def rate(key: tuple[str, ...], alpha: float = 2) -> float:
            successes, n = self.counts.get(key, [0, 0])
            return (successes + alpha / 2) / (n + alpha)
        if arm == "global":
            return rate(("global",))
        if arm == "topic":
            return rate(("topic", topic))
        if arm == "target":
            return rate(("target", target))
        if arm == "target_topic":
            return rate(("target_topic", target, topic))
        # Standard empirical-Bayes-style smoothing (not fitted Bayes hyperparameters):
        # combine target-topic observations with five global-topic pseudocounts.
        yes, n = self.counts.get(("target_topic", target, topic), [0, 0])
        return (yes + 5 * rate(("topic", topic))) / (n + 5)


def choose_question(model: FrequencyModel, target: str,
                    topics: tuple[str, ...], *, target_opted_in: bool) -> dict:
    """Suggest an optional *question*, never contact the target automatically."""
    if not target_opted_in or target not in model.known_targets:
        return {"status": "HOLD", "question": "Has this participant opted in to questions?"}
    eligible = [t for t in topics if t in model.known_topics]
    if not eligible:
        return {"status": "HOLD", "question": "Which topic may be proposed without guessing?"}
    options = []
    for topic in eligible:
        p = model.predict(target, topic, "shrink")
        # Entropy surrogate: uncertain observations worth clarifying if invited.
        options.append((p * (1 - p), -model.count(target, topic), topic))
    uncertainty, _, chosen = sorted(options, key=lambda t: (-t[0], t[1], t[2]))[0]
    return {
        "status": "SUGGESTION_ONLY",
        "target": target, "topic": chosen,
        "uncertainty_proxy": round(uncertainty, 6),
        "question": "Would you voluntarily clarify your own view on this topic?",
        "requires_separate_disclosure_authorization": True,
    }


def brier(p: float, observed_yes: bool) -> float:
    return (p - int(observed_yes)) ** 2


@dataclass(frozen=True)
class SyntheticWorld:
    """Simulator-owned latent rates — never passed to FrequencyModel."""

    rates: dict[tuple[str, str], float]
    targets: tuple[str, ...]
    topics: tuple[str, ...]

    @classmethod
    def create(cls, seed: int = 30301, targets: int = 14) -> "SyntheticWorld":
        rng = random.Random(seed)
        people = tuple("node_%02d" % i for i in range(targets))
        # Orthogonal topic preferences create genuine heterogeneous perspectives.
        rates = {(p, topic): rng.choice((0.09, 0.22, 0.78, 0.91))
                 for p in people for topic in TOPICS}
        return cls(rates, people, TOPICS)

    def episodes(self, seed: int, count_per_pair: int, *,
                 shift: bool = False, withhold_mod: int = 7,
                 unknown_target: bool = False) -> tuple[Report, ...]:
        if count_per_pair <= 0:
            raise ValueError("positive episode count required")
        rng = random.Random(seed)
        rows = []
        targets = self.targets + (("unseen_visitor",) if unknown_target else ())
        for target in targets:
            for topic in self.topics:
                p = self.rates.get((target, topic), 0.5)
                if shift and target in self.targets:
                    p = 1.0 - p  # distribution shift explicitly authored
                for i in range(count_per_pair):
                    yes = rng.random() < p
                    can_share = (withhold_mod <= 0 or
                                 (i + self.topics.index(topic) + self.targets.index(target)
                                  if target in self.targets else i) % withhold_mod != 0)
                    rows.append(Report(
                        case_id="%s/%s/%s/%03d" % (seed, target, topic, i),
                        target=target, topic=topic, yes=yes,
                        shareable=can_share,
                        evidence_ref="synthetic://%s/%s/%s/%s" % (seed, target, topic, i),
                        private_note="PRIVATE_SIMULATOR_STATE_DO_NOT_EXPORT",
                    ))
        rng.shuffle(rows)
        return tuple(rows)


def _metrics(scores: list[float], correct: list[bool]) -> dict:
    return {
        "evaluated": len(scores),
        "brier": round(sum(scores) / len(scores), 6) if scores else None,
        "accuracy_at_half": round(sum(correct) / len(correct), 6) if correct else None,
    }


def _evaluate_frozen(model: FrequencyModel, rows: tuple[Report, ...]) -> dict:
    perf = {a: ([], []) for a in ARMS}
    held = 0
    unknown = 0
    for row in rows:
        if not row.shareable:
            held += 1
            continue
        for arm in ARMS:
            probability = model.predict(row.target, row.topic, arm)
            if probability is None:
                if arm == ARMS[0]:
                    unknown += 1
                continue
            perf[arm][0].append(brier(probability, row.yes))
            perf[arm][1].append((probability >= .5) == row.yes)
    return {
        "withheld_excluded": held,
        "unknown_target_or_topic_abstentions": unknown,
        "arms": {arm: _metrics(*perf[arm]) for arm in ARMS},
    }


def _online_correction(model: FrequencyModel, rows: tuple[Report, ...],
                       policy: str) -> dict:
    # Reconstruct state without any future responses, score each prior to
    # seeing its outcome, and update only after its opt-in feedback arrives.
    scores, right, receipts = [], [], []
    withheld = 0
    for r in rows:
        if not r.shareable:
            withheld += 1
            continue
        p = model.predict(r.target, r.topic, policy)
        if p is None:
            receipts.append({"case_id": r.case_id, "status": "HOLD_NEW_TARGET_OR_TOPIC"})
            continue
        predicted = p >= 0.5
        scores.append(brier(p, r.yes))
        right.append(predicted == r.yes)
        receipts.append({
            "case_id": r.case_id, "source": r.target,
            "topic": r.topic, "evidence_ref": r.evidence_ref,
            "predicted_probability_yes_before_feedback": round(p, 6),
            "public_self_report": r.yes,
            "prediction_corrected_by_self_report": predicted != r.yes,
            "status": "CORRECTED" if predicted != r.yes else "MATCHED",
        })
        model.update(r)
    return {
        "metrics": _metrics(scores, right),
        "withheld_excluded": withheld,
        "receipts": receipts,
    }


def run(seed: int = 30301) -> dict:
    """Predeclared training/validation and separately instantiated futures."""
    world = SyntheticWorld.create(seed)
    training = public_only(world.episodes(seed + 1, 16))
    validation = public_only(world.episodes(seed + 2, 8))
    base = FrequencyModel().fit(training)
    validation_scores = {}
    for arm in ARMS:
        ps = [base.predict(r.target, r.topic, arm) for r in validation]
        validation_scores[arm] = sum(brier(p, r.yes) for p, r in zip(ps, validation)) / len(validation)
    # Complexity penalty prevents gratuitous preference for personalized policy.
    penalties = {"global": 0, "topic": .001, "target": .001,
                 "target_topic": .003, "shrink": .004}
    selected = min(ARMS, key=lambda a: (validation_scores[a] + penalties[a], ARMS.index(a)))
    all_training = training + validation
    frozen = FrequencyModel().fit(all_training)
    # Only *public* training outcomes enter the hash, never latent simulator
    # rates, private notes or any test outcome.
    freeze_receipt = {
        "policy": selected,
        "penalties": penalties,
        "validation_brier": {k: round(v, 6) for k, v in validation_scores.items()},
        "training_case_ids": sorted(r.case_id for r in all_training),
        "training_public_outcomes": sorted((r.case_id, int(r.yes)) for r in all_training),
    }
    digest = sha256(json.dumps(freeze_receipt, sort_keys=True).encode()).hexdigest()
    # Generate new futures only *after* the training state and digest freeze.
    stable = world.episodes(seed + 3, 12, unknown_target=True)
    shifted = world.episodes(seed + 4, 12, shift=True, unknown_target=True)
    def evaluate(name: str, rows: tuple[Report, ...]) -> dict:
        frozen_scores = _evaluate_frozen(frozen, rows)
        fresh_model = FrequencyModel().fit(all_training)
        online = _online_correction(fresh_model, rows, selected)
        return {
            "regime": name,
            "fixed_comparators": frozen_scores,
            "online_selected": {
                "policy": selected,
                "metrics": online["metrics"],
                "withheld_excluded": online["withheld_excluded"],
            },
            "correction_receipts": online["receipts"],
        }
    return {
        "status": "SYNTHETIC_RESEARCH_HOLD",
        "world_authorship": "ENGINEER_AUTHORED_GENERATOR_NOT_EXTERNAL_OR_BLIND",
        "selected_train_only_policy": selected,
        "training_observations": len(training),
        "validation_observations": len(validation),
        "frozen_training_digest": digest,
        "training_cv_scores": freeze_receipt["validation_brier"],
        "stable": evaluate("STABLE_SYNTHETIC", stable),
        "shift": evaluate("REVERSED_PREFERENCES_SYNTHETIC", shifted),
        "next_question": choose_question(frozen, world.targets[0], TOPICS, target_opted_in=True),
        "no_live_people_contacted": True,
        "no_external_action_taken": True,
        "not_learned_human_intent_or_verified_collective_intelligence": True,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=30301)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run(args.seed)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for regime in ("stable", "shift"):
            print(regime, result[regime]["fixed_comparators"]["arms"])
        print("FROZEN", result["frozen_training_digest"])
