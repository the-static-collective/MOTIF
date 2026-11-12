"""ONE THING 007 -> MOTIF-015: aggregate-only, operator-attested offline adapter.

No PostHog connection or network. Never import raw events, people, notes or URLs.
The input must be *actual reviewed* funnel aggregate counts, not event totals.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from observer import UnsafeObservation, evaluate

INPUT_SCHEMA = "posthog.one-thing.consented-funnel/v1"
EXACT = {"schema", "query_ref", "window_start", "window_end", "exported_at",
         "entry_count", "completed_count", "source_reviewed", "consent_confirmed"}


def packet_from_aggregate(raw: Any, *, expected_rate: float, minimum_n: int) -> dict:
    if type(raw) is not dict or set(raw) != EXACT:
        raise UnsafeObservation("aggregate export must contain only the approved keys")
    if raw["schema"] != INPUT_SCHEMA:
        raise UnsafeObservation("unsupported aggregate format")
    if type(raw["source_reviewed"]) is not bool or type(raw["consent_confirmed"]) is not bool:
        raise UnsafeObservation("explicit evidence and consent declarations are required")
    if not raw["consent_confirmed"]:
        raise UnsafeObservation("opt-in collection not verified")
    return {
        "schema": "motif.observation.015.v1",
        "source": {
            "provider": "posthog", "query_ref": raw["query_ref"],
            "window_start": raw["window_start"], "window_end": raw["window_end"],
            "exported_at": raw["exported_at"], "method": "same_cohort_funnel",
            # IDs represent opted-in journeys, NOT unique physical humans.
            "unique_actors": True, "same_cohort": True,
            "collection_consent": "explicit_opt_in",
            "personal_data_in_packet": False,
            "source_reviewed": raw["source_reviewed"],
        },
        "prediction": {
            "metric": "self_report_preparation_rate",
            "expected_rate": expected_rate, "minimum_n": minimum_n
        },
        "observation": {
            "entry_count": raw["entry_count"],
            "completed_count": raw["completed_count"]
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Review an operator-provided same-journey opt-in funnel export offline")
    parser.add_argument("aggregate", type=Path)
    parser.add_argument("--now", required=True, help="Explicit ISO 8601 clock for evidence freshness")
    parser.add_argument("--expected-rate", type=float, required=True, help="Prediction preregistered before the cohort window")
    parser.add_argument("--minimum-n", type=int, required=True)
    args = parser.parse_args()
    raw = json.loads(args.aggregate.read_text(encoding="utf-8"))
    packet = packet_from_aggregate(raw, expected_rate=args.expected_rate, minimum_n=args.minimum_n)
    result = evaluate(packet, now=args.now)
    print(json.dumps({"input_schema": INPUT_SCHEMA, "review": result}, indent=2))


if __name__ == "__main__":
    main()
