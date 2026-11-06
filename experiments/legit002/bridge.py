"""Cross the strict native LEGIT-001 boundary honestly.

The finite synthetic router cannot accept a scientific paper evidence packet.
Do not inject invented world priors or report a fabricated native answer.
A separately labeled deterministic source-evidence adapter is shown afterward.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "legit001"))
from router import Hold as NativeHold, route as native_route
from evidence_router import load_packet, run as curated_check


def demonstrate():
    packet = load_packet()
    native_was_held = False
    try:
        native_route(packet)
    except NativeHold:
        native_was_held = True
    if not native_was_held:
        raise AssertionError("Native MOTIF misread an out-of-grammar scientific packet")
    return {
        "question_id": packet["id"],
        "native_MOTIF_legit001": {
            "decision": "HOLD_UNSUPPORTED_SCIENTIFIC_EVIDENCE_SCHEMA",
            "native_answer_to_consciousness_question": None,
            "status": "HOLD",
            "why": "Finite synthetic world/prior/query schema cannot interpret empirical clinical research."
        },
        "separately_authored_typed_adapter": curated_check(packet),
        "winner": None,
        "independent_blind_comparison": False,
        "real_world_authority": False
    }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), sort_keys=True, indent=2))
