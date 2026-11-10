"""GENIUS-005 benchmark: prequential drift alarms versus conventional adaptation.

Simulator authorship, drift times and rates are isolated from monitor APIs.
The finite policy grid is scored on validation seeds only; all heldout
streams are constructed after a SHA256 config freeze. This is NOT a blinded
external trial. Inputs are fictional Bernoulli reports, not human data.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
import json
import math
import random

from detectors import Detectors, beta_rate, detection_summary, ALPHA, CHECK_TIMES

REGIMES = ("STABLE", "NOISY_STABLE", "ABRUPT", "LOCAL", "GRADUAL")
FORECASTS = ("FROZEN", "CUMULATIVE", "WINDOW8", "WINDOW24", "EWMA",
             "HEDGE", "EXACT_SWITCH", "CUSUM_SWITCH")
VALIDATION_SEEDS = (50501, 50502)
FUTURE_SEEDS = (50541, 50542, 50543)
STREAMS = 12
FUTURE_ROUNDS = 120
CHANGE_START = 40
CUSUM_OPTIONS = (4.5, 6.0, 8.0)


@dataclass(frozen=True)
class PublicReport:
    event_id: str
    yes: bool
    can_share: bool
    evidence_ref: str
    private_text: str = ""


def project(report: PublicReport) -> PublicReport | None:
    if not report.can_share:
        return None
    return PublicReport(report.event_id, report.yes, True,
                        report.evidence_ref, "")


@dataclass
class StandardForecasts:
    """Classical fixed, cumulative, recent, EWMA, loss-hedged estimators."""

    reference: tuple[bool, ...]
    observed: list[bool] = field(default_factory=list)
    ewma: float = 0.5
    weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.reference) != 40:
            raise ValueError("Exactly 40 reference labels required")
        self.ewma = beta_rate(self.reference)
        self.weights = {k: 0.25 for k in
                        ("CUMULATIVE", "WINDOW8", "WINDOW24", "EWMA")}

    def forecasts(self, exact_detected: bool, cusum_detected: bool) -> dict[str, float]:
        accumulated = list(self.reference) + self.observed
        cumulative = beta_rate(accumulated)
        w8 = beta_rate(accumulated[-8:])
        w24 = beta_rate(accumulated[-24:])
        raw = {
            "FROZEN": beta_rate(self.reference),
            "CUMULATIVE": cumulative,
            "WINDOW8": w8,
            "WINDOW24": w24,
            "EWMA": self.ewma,
        }
        raw["HEDGE"] = sum(self.weights[k] * raw[k] for k in self.weights)
        raw["EXACT_SWITCH"] = w8 if exact_detected else cumulative
        raw["CUSUM_SWITCH"] = w8 if cusum_detected else cumulative
        return raw

    def update(self, yes: bool, prior: dict[str, float]) -> None:
        # Update only after a voluntarily shared label has been scored.
        if type(yes) is not bool:
            raise ValueError("Public label must be a boolean")
        eta = 1.0
        updated = {k: max(1e-250, v * math.exp(
            -eta * (prior[k] - int(yes)) ** 2))
            for k, v in self.weights.items()}
        total = sum(updated.values())
        self.weights = {k: v / total for k, v in updated.items()}
        self.ewma = .77 * self.ewma + .23 * int(yes)
        self.observed.append(yes)


def source_world(seed: int, regime: str, stream_index: int) -> tuple[
        tuple[bool, ...], tuple[PublicReport, ...], int | None]:
    """The simulator's drift timing stays OUTSIDE the prediction interface."""
    if regime not in REGIMES:
        raise ValueError("Unrecognized regime")
    rng = random.Random(seed * 1009 + stream_index * 31 +
                        REGIMES.index(regime) * 379)
    p = (.13, .23, .77, .87)[(seed + stream_index) % 4]
    if regime == "NOISY_STABLE":
        p = .48 if stream_index % 2 else .52
    reference = tuple(rng.random() < p for _ in range(40))
    actual_change = (
        CHANGE_START if regime in ("ABRUPT", "GRADUAL")
        or (regime == "LOCAL" and stream_index % 3 == 0)
        else None
    )
    future = []
    for t in range(FUTURE_ROUNDS):
        target_p = p
        if actual_change is not None:
            if regime in ("ABRUPT", "LOCAL") and t >= CHANGE_START:
                target_p = 1 - p
            elif regime == "GRADUAL" and t >= CHANGE_START:
                phase = min(1.0, (t - CHANGE_START) / 48)
                target_p = p * (1 - phase) + (1 - p) * phase
        label = rng.random() < target_p
        is_shared = (t + stream_index * 3) % 17 != 0
        future.append(PublicReport(
            event_id=f"synthetic:{seed}/{regime}/{stream_index}/{t}",
            yes=label, can_share=is_shared,
            evidence_ref=f"synthetic://{seed}/{regime}/{stream_index}/{t}",
            private_text="PRIVATE_SIMULATOR_FIELD_MUST_NOT_EXPORT"))
    return reference, tuple(future), actual_change


def run_stream(seed: int, regime: str, stream_index: int,
               threshold: float, *, detailed: bool = False) -> dict:
    reference, future, true_change = source_world(seed, regime, stream_index)
    monitor = Detectors(reference, threshold, f"{regime}:{stream_index}")
    predictor = StandardForecasts(reference)
    losses = {arm: [] for arm in FORECASTS}
    shared_rounds = []
    public_receipts = []

    for round_index, raw in enumerate(future):
        event = project(raw)
        if event is None:
            continue
        # Predict using old state only; no future labels or truth metadata.
        forecasts = predictor.forecasts("EXACT" in monitor.alarms,
                                        "CUSUM" in monitor.alarms)
        for arm in FORECASTS:
            losses[arm].append((forecasts[arm] - int(event.yes)) ** 2)
        prior_alarm_state = sorted(monitor.alarms)
        predictor.update(event.yes, forecasts)
        receipt = monitor.update(event.yes, event.evidence_ref)
        shared_rounds.append(round_index)
        if detailed and (receipt["new_alarms"] or round_index % 16 == 0):
            public_receipts.append({
                "event_id": event.event_id, "evidence_ref": event.evidence_ref,
                "round": round_index,
                "forecast_before_feedback": {k: round(v, 5)
                                             for k, v in forecasts.items()},
                "public_self_report": event.yes,
                "alarms_before_current_report": prior_alarm_state,
                "new_alarms_after_current_report": receipt["new_alarms"],
                "private_text": None,  # field purposely never transmitted
            })

    summary = detection_summary(monitor, true_change, tuple(shared_rounds))
    return {
        "scenario": regime, "stream_id": stream_index,
        "ground_truth_change_round_for_evaluator_only": true_change,
        "evidence_authorship": "INTERNAL_SIMULATOR_NOT_EXTERNAL_EVIDENCE",
        "shared_samples": len(shared_rounds),
        "withheld_samples": FUTURE_ROUNDS - len(shared_rounds),
        "detection": summary,
        "mean_prequential_brier": {k: sum(v) / len(v) for k, v in losses.items()},
        "detector_trace": monitor.traces if detailed else [],
        "public_prediction_receipts": public_receipts,
        "no_human_contact_or_external_actions": True,
    }


def summarize(rows: list[dict]) -> dict:
    detections = {}
    for arm in ("NAIVE", "CUSUM", "EXACT"):
        absent = [r for r in rows
                  if r["ground_truth_change_round_for_evaluator_only"] is None]
        shifted = [r for r in rows
                   if r["ground_truth_change_round_for_evaluator_only"] is not None]
        true = [r for r in shifted if r["detection"][arm]["true_detection"]]
        false = [r for r in rows if r["detection"][arm]["false_alarm"]]
        delays = [r["detection"][arm]["delay_rounds"] for r in true]
        detections[arm] = {
            "null_streams": len(absent),
            "changed_streams": len(shifted),
            "false_alarm_streams": len(false),
            "null_false_alarm_rate": round(sum(r["detection"][arm]["false_alarm"]
                                               for r in absent) / len(absent), 6)
                                          if absent else None,
            "true_positive_streams": len(true),
            "detection_rate_on_changed": round(len(true) / len(shifted), 6)
                                          if shifted else None,
            "mean_detection_delay_rounds": round(sum(delays)/len(delays), 3)
                                           if delays else None,
        }
    briers = {}
    for arm in FORECASTS:
        total = sum(r["mean_prequential_brier"][arm] * r["shared_samples"] for r in rows)
        count = sum(r["shared_samples"] for r in rows)
        briers[arm] = round(total/count, 6) if count else None
    return {
        "streams": len(rows),
        "shared_forecasts_scored": sum(r["shared_samples"] for r in rows),
        "withheld_excluded": sum(r["withheld_samples"] for r in rows),
        "detection": detections,
        "forecast_brier": briers,
    }


def run() -> dict:
    # CUSUM tuning is strictly validation-only, with an explicit high
    # false-alarm cost and missed-alarm penalty. No future-world data read.
    validation = {}
    for threshold in CUSUM_OPTIONS:
        all_rows = [run_stream(seed, regime, i, threshold)
                    for seed in VALIDATION_SEEDS
                    for regime in REGIMES for i in range(STREAMS)]
        report = summarize(all_rows)
        det = report["detection"]["CUSUM"]
        # Cost counts warnings as costly, late detection as less useful.
        validation[str(threshold)] = {
            "objective": round(3 * det["false_alarm_streams"] +
                               2 * (det["changed_streams"] -
                                    det["true_positive_streams"]) +
                               .02 * sum(
                                   r["detection"]["CUSUM"]["delay_rounds"]
                                   for r in all_rows
                                   if r["detection"]["CUSUM"]["true_detection"]
                               ), 6),
            "report": det,
        }
    selected = min(CUSUM_OPTIONS, key=lambda t:
                   (validation[str(t)]["objective"], CUSUM_OPTIONS.index(t)))
    freeze = {
        "reference_n": 40, "window": 24, "fixed_checkpoints": CHECK_TIMES,
        "monitor_family_alpha": ALPHA, "streams_per_scenario": STREAMS,
        "future_rounds": FUTURE_ROUNDS,
        "scenario_names": REGIMES,
        "validation_seeds": VALIDATION_SEEDS,
        "future_seeds": FUTURE_SEEDS,
        "selected_classical_cusum_threshold": selected,
        "comparator_arms": FORECASTS,
        "only_public_labels": True,
    }
    digest = sha256(json.dumps(freeze, sort_keys=True).encode()).hexdigest()
    # Prospective holdouts from different seeds materialize only after freeze.
    by_regime = {}
    selected_receipts = []
    for regime in REGIMES:
        rows = [run_stream(seed, regime, i, selected,
                           detailed=(seed == FUTURE_SEEDS[0] and i == 0))
                for seed in FUTURE_SEEDS for i in range(STREAMS)]
        by_regime[regime] = summarize(rows)
        selected_receipts += [
            {"seed": FUTURE_SEEDS[0], "regime": regime,
             "source": r["stream_id"], "public_prediction_receipts": r["public_prediction_receipts"],
             "public_detector_trace": r["detector_trace"]}
            for r in rows if r["public_prediction_receipts"]
        ]
    totals = {
        "NOISE_FALSE_ALARM_NOTE": "Fisher/Bonferroni per-stream IID-null assumption; NO global guarantee for non-IID, strategic reporting or mixed streams",
        "EXACT_MONITOR_IS_CLASSICAL": True,
        "NOT_AUTONOMOUS_ALGORITHM_DISCOVERY": True,
    }
    return {
        "status": "RESEARCH_HOLD_ENGINEER_AUTHORED_SYNTHETIC",
        "research_id": "GENIUS-005",
        "initial_purpose": "DISTINGUISH_REAL_PERSISTENT_CHANGE_FROM_NOISE",
        "config_frozen_sha256_before_holdout": digest,
        "precommitted_settings": freeze,
        "validation_cusum_choice": validation,
        "future_scenarios": by_regime,
        "audit_traces": selected_receipts,
        "scientific_boundaries": totals,
        "no_live_people_contacted": True,
        "no_external_actions_taken": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
