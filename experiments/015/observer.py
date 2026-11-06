"""MOTIF-015: offline, aggregate-only PostHog observation witness (no API calls)."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "motif.observation.015.v1"
ALLOWED_METRICS = {"artifact_completion_rate", "useful_step_completion_rate"}


class UnsafeObservation(ValueError):
    """The input is not a suitable, consented aggregate observation."""


def _exact_keys(obj: Any, expected: set[str], where: str) -> Mapping[str, Any]:
    if type(obj) is not dict or set(obj) != expected:
        raise UnsafeObservation(f"{where}: expected exactly {sorted(expected)}")
    return obj


def _timestamp(value: Any, label: str) -> datetime:
    if type(value) is not str:
        raise UnsafeObservation(f"{label}: expected an ISO-8601 timezone-aware string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise UnsafeObservation(f"{label}: invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise UnsafeObservation(f"{label}: timezone required")
    return parsed.astimezone(timezone.utc)


def _whole(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise UnsafeObservation(f"{label}: expected a non-negative integer")
    return value


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """Approximate binomial confidence interval; not a causal estimate."""
    if trials <= 0 or not 0 <= successes <= trials:
        raise UnsafeObservation("invalid binomial counts")
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def evaluate(packet: Any, *, now: str, max_age_hours: float = 72) -> dict[str, Any]:
    """Turn one explicitly reviewed cohort summary into an *advisory* receipt.

    All accepted data are aggregate counts. Never import raw events, persons,
    sessions, text, URLs, identifiers, or prompts into a MOTIF observation.
    """
    p = _exact_keys(packet, {"schema", "source", "prediction", "observation"}, "packet")
    if p["schema"] != SCHEMA:
        raise UnsafeObservation("unsupported schema")
    source = _exact_keys(p["source"], {
        "provider", "query_ref", "window_start", "window_end", "exported_at",
        "method", "unique_actors", "same_cohort", "collection_consent",
        "personal_data_in_packet", "source_reviewed",
    }, "source")
    pred = _exact_keys(p["prediction"], {"metric", "expected_rate", "minimum_n"}, "prediction")
    observed = _exact_keys(p["observation"], {"entry_count", "completed_count"}, "observation")

    if source["provider"] != "posthog" or source["method"] != "same_cohort_funnel":
        raise UnsafeObservation("only reviewed PostHog same-cohort funnels are accepted")
    if type(source["query_ref"]) is not str or not 1 <= len(source["query_ref"]) <= 100:
        raise UnsafeObservation("query_ref must be an opaque, short reference")
    if any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:." for c in source["query_ref"]):
        raise UnsafeObservation("query_ref may not contain URLs or identifying content")
    for field in ("unique_actors", "same_cohort", "personal_data_in_packet", "source_reviewed"):
        if type(source[field]) is not bool:
            raise UnsafeObservation(f"{field}: expected boolean")
    if source["personal_data_in_packet"]:
        raise UnsafeObservation("never import personal-level telemetry")
    if source["collection_consent"] != "explicit_opt_in":
        raise UnsafeObservation("explicit opt-in collection required")
    if not source["same_cohort"] or not source["unique_actors"]:
        raise UnsafeObservation("independent event totals are not a funnel")

    if pred["metric"] not in ALLOWED_METRICS:
        raise UnsafeObservation("metric is not in the reviewed allowlist")
    expected = pred["expected_rate"]
    if type(expected) not in (int, float) or not math.isfinite(expected) or not 0 <= expected <= 1:
        raise UnsafeObservation("expected_rate must be a finite proportion")
    if type(pred["minimum_n"]) is not int or pred["minimum_n"] < 2:
        raise UnsafeObservation("minimum_n must be at least 2")

    entry = _whole(observed["entry_count"], "entry_count")
    completed = _whole(observed["completed_count"], "completed_count")
    if completed > entry:
        raise UnsafeObservation("completed_count exceeds entry_count")
    start = _timestamp(source["window_start"], "window_start")
    end = _timestamp(source["window_end"], "window_end")
    exported = _timestamp(source["exported_at"], "exported_at")
    current = _timestamp(now, "now")
    if start >= end or end > exported or exported > current:
        raise UnsafeObservation("invalid chronological order")
    if type(max_age_hours) not in (int, float) or not math.isfinite(max_age_hours) or max_age_hours <= 0:
        raise UnsafeObservation("invalid max_age_hours")

    holds: list[str] = []
    if not source["source_reviewed"]:
        holds.append("source_query_not_independently_reviewed")
    if (current - exported).total_seconds() > max_age_hours * 3600:
        holds.append("stale_export")
    if entry < pred["minimum_n"]:
        holds.append("insufficient_sample")
    if entry == 0:
        holds.append("no_observations")

    rate: float | None = completed / entry if entry else None
    bounds = wilson_interval(completed, entry) if entry else None
    departure: bool | None = (expected < bounds[0] or expected > bounds[1]) if bounds else None
    status = "HOLD" if holds else ("REVIEW_DEPARTURE" if departure else "REVIEW_NO_DEPARTURE")
    return {
        "schema": "motif.observation.receipt.015.v1",
        "status": status,
        "holds": holds,
        "source_ref": source["query_ref"],
        "metric": pred["metric"],
        "sample_size": entry,
        "completed_count": completed,
        "predicted_rate": expected,
        "observed_rate": round(rate, 6) if rate is not None else None,
        "wilson_95_interval": [round(x, 6) for x in bounds] if bounds else None,
        "prediction_outside_interval": departure if not holds else None,
        "next_question": "Was the cohort correctly defined, and does independent field evidence support any outcome claim?",
        "boundary": {
            "human_review_required": True,
            "permission_to_act": False,
            "causation_established": False,
            "field_outcome_verified": False,
            "posthog_connection_used": False,
        },
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate a reviewed aggregate JSON fixture offline")
    parser.add_argument("packet", type=Path)
    parser.add_argument("--now", required=True, help="Explicit verification clock (timezone-aware ISO 8601)")
    args = parser.parse_args()
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    print(json.dumps(evaluate(packet, now=args.now), indent=2))


if __name__ == "__main__":
    main()
