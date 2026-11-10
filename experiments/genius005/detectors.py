"""MOTIF GENIUS-005 — Evidence Before Revision.

A source-bound sequential detection benchmark, not a model of human minds.
Compares elementary false alarms with an *exact* classical conditional
two-sample permutation test at fixed checkpoints, and classical CUSUM.

Key distinction: Fisher's conditional two-sided p-value is exact under
the iid Bernoulli no-change null for **unconditioned** reference/future
samples; the alpha-spending union bound controls per-stream probability
of >=1 false alarm across a predeclared finite test schedule. It does
not imply robustness to temporal dependence, nonrandom reporting,
strategic reports, selection bias or changing sampling regimes.

Pure standard library. No remote action or human participation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

REFERENCE_N = 40
WIDTH = 24
CHECK_TIMES = tuple(range(WIDTH, 113, 8))  # At most 12 tests per stream
ALPHA = 0.05
NAIVE_DIFF = 0.30


def fisher_two_sided(a_yes: int, a_n: int, b_yes: int, b_n: int) -> float:
    """Fisher's two-sided exact conditional hypergeometric p-value.

    Sum probabilities <= observed table probability for given margins.
    No scipy/network. Exact integer binomial coefficients, finite floats.
    """
    if min(a_n, b_n) <= 0:
        raise ValueError("Both samples must be nonempty")
    if not (0 <= a_yes <= a_n and 0 <= b_yes <= b_n):
        raise ValueError("Yes counts must fall within their sample sizes")
    total_yes = a_yes + b_yes
    denominator = math.comb(a_n + b_n, total_yes)
    low = max(0, total_yes - b_n)
    high = min(a_n, total_yes)
    numerators = {
        k: math.comb(a_n, k) * math.comb(b_n, total_yes - k)
        for k in range(low, high + 1)
    }
    observed = numerators[a_yes]
    return min(1.0, sum(n for n in numerators.values() if n <= observed) / denominator)


def beta_rate(items: list[bool] | tuple[bool, ...], alpha: float = 2.0) -> float:
    return (sum(items) + alpha / 2) / (len(items) + alpha)


@dataclass
class Detectors:
    """Only an already-shared public binary report may trigger an update."""

    reference: tuple[bool, ...]
    cusum_threshold: float = 6.0
    stream_id: str = ""
    history: list[bool] = field(default_factory=list)
    seen_evidence_ids: set[str] = field(default_factory=set)
    alarms: dict[str, int] = field(default_factory=dict)
    traces: list[dict] = field(default_factory=list)
    pos: float = 0.0
    neg: float = 0.0

    def __post_init__(self):
        if len(self.reference) != REFERENCE_N:
            raise ValueError("Reference must have exactly 40 shared samples")
        if any(type(x) is not bool for x in self.reference):
            raise ValueError("Reference requires boolean reports")
        if self.cusum_threshold <= 0:
            raise ValueError("CUSUM threshold must be positive")

    def update(self, value: bool, evidence_id: str) -> dict:
        if type(value) is not bool or not evidence_id:
            raise ValueError("Only a source-attributed publicly shared boolean report")
        if evidence_id in self.seen_evidence_ids:
            raise ValueError("Replayed evidence identifier")
        self.seen_evidence_ids.add(evidence_id)
        self.history.append(value)
        t = len(self.history)
        p0 = beta_rate(self.reference)
        alternative_hi = min(0.95, p0 + .25)
        alternative_lo = max(0.05, p0 - .25)
        # Classical two-sided fixed-alternative Bernoulli CUSUM;
        # the estimated p0 does NOT grant a false-alarm guarantee.
        self.pos = max(0.0, self.pos + math.log(
            (alternative_hi if value else (1 - alternative_hi)) /
            (p0 if value else (1 - p0))))
        self.neg = max(0.0, self.neg + math.log(
            (alternative_lo if value else (1 - alternative_lo)) /
            (p0 if value else (1 - p0))))

        record = {"shared_index": t, "evidence_id": evidence_id, "new_alarms": []}
        if t >= 8 and "NAIVE" not in self.alarms:
            gap = abs(beta_rate(self.history[-8:], alpha=0) -
                      beta_rate(self.reference, alpha=0))
            if gap >= NAIVE_DIFF:
                self.alarms["NAIVE"] = t
                record["new_alarms"].append("NAIVE")

        if t in CHECK_TIMES and "EXACT" not in self.alarms:
            p_value = fisher_two_sided(
                sum(self.reference), REFERENCE_N,
                sum(self.history[-WIDTH:]), WIDTH)
            record["fisher_p_value"] = p_value
            record["per_test_threshold"] = ALPHA / len(CHECK_TIMES)
            if p_value <= ALPHA / len(CHECK_TIMES):
                self.alarms["EXACT"] = t
                record["new_alarms"].append("EXACT")

        if "CUSUM" not in self.alarms and max(self.pos, self.neg) >= self.cusum_threshold:
            self.alarms["CUSUM"] = t
            record["new_alarms"].append("CUSUM")
        # No episode outcome, private content or simulator rate in trace.
        if t in CHECK_TIMES or record["new_alarms"]:
            self.traces.append(record)
        return record


def detection_summary(detector: Detectors, actual_change_round: int | None,
                      shared_rounds: tuple[int, ...]) -> dict:
    """Ground truth provided only to evaluator AFTER the detector ran."""
    summary = {}
    for arm in ("NAIVE", "EXACT", "CUSUM"):
        shared_index = detector.alarms.get(arm)
        event_round = shared_rounds[shared_index - 1] if shared_index else None
        false_alarm = event_round is not None and (
            actual_change_round is None or event_round < actual_change_round)
        true_positive = event_round is not None and (
            actual_change_round is not None and event_round >= actual_change_round)
        summary[arm] = {
            "first_alarm_round": event_round,
            "false_alarm": bool(false_alarm),
            "true_detection": bool(true_positive),
            "delay_rounds": (event_round - actual_change_round)
                            if true_positive else None,
            "alarm_exists": event_round is not None,
        }
    return summary
