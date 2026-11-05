"""FIELD-001 optional native Dogram analysis of unverified reported histories.

This tool never downloads data or transmits a log. An explicit local log and
trusted local Dogram checkout are required. The output is an information-loss
calculation on *operator-reported traces*, not evidence, approval or causality.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import argparse
import json
import sys

from field_protocol import _pair_compatible, match_id, validate


def calculate(log: object, dogram_root: str) -> dict[str, object]:
    data = validate(log)
    root = Path(dogram_root).resolve()
    if not (root / "dogram" / "anti_collapse_reachability.py").is_file():
        raise ValueError("pass an explicit trusted local Dogram checkout")

    sys.path.insert(0, str(root))
    try:
        from dogram.anti_collapse_reachability import analyze_collapse
    finally:
        sys.path.pop(0)

    pairs = sorted(
        ((a,b) for a in data["cards"] if a["kind"] == "offer"
         for b in data["cards"] if b["kind"] == "need"
         and _pair_compatible(a,b)),
        key=lambda item: match_id(*item),
    )
    if len(pairs) < 2:
        return {
            "schema": "motif.field-dogram/v0",
            "status": "INSUFFICIENT_COMPARABLE_PAIRS",
            "pair_count": len(pairs),
            "calculation": None,
            "causal_effect_identified": False,
        }
    if len(pairs) > 80:
        raise ValueError("limit Dogram comparison to at most 80 local pairs")

    ids = tuple(match_id(a,b) for a,b in pairs)
    rich, collapsed = [], []
    for a,b in pairs:
        history = [e for e in data["events"] if e["subject"] == match_id(a,b)]
        # Notes, names, contact data and raw identity are NEVER passed as
        # projection payload. We retain typed origin/trace distinctions only.
        trace = tuple((e["kind"],e["source"]) for e in history)
        rich.append((a["origin"], b["origin"], trace))
        types = {e["kind"] for e in history}
        if "benefit_reported" in types and "no_benefit_reported" in types:
            summary = "CONFLICT"
        elif "benefit_reported" in types:
            summary = "BENEFIT_REPORTED"
        elif "no_benefit_reported" in types:
            summary = "NO_BENEFIT_REPORTED"
        else:
            summary = "NO_OUTCOME_REPORT"
        collapsed.append(summary)

    receipt = analyze_collapse(ids, tuple(rich), tuple(collapsed))
    return {
        "schema": "motif.field-dogram/v0",
        "status": "DECLARED_CALCULATION_ONLY",
        "pair_count": len(ids),
        "calculation": asdict(receipt),
        "projection": "typed-origin-and-event-traces -> reported outcome label",
        "causal_effect_identified": False,
        "verification_claimed": False,
        "limitation": (
            "Local finite information loss under operator-entered reports; "
            "not proof of identity, truth, consent, effect, or absence of harm."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-log", required=True, type=Path)
    parser.add_argument("--dogram-root", required=True)
    args = parser.parse_args()
    with args.field_log.open(encoding="utf-8") as source:
        source_log = json.load(source)
    print(json.dumps(calculate(source_log, args.dogram_root), indent=2))
