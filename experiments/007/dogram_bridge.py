"""Optional native Dogram calculations for MOTIF-007's synthetic two-key crossing.

Use a trusted explicit local checkout. No network, external execution, consent
transfer or auto-discovery. Dogram measures the declared 2x2 interaction and
which state distinctions collapse under an opportunity-only projection.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import argparse
import json
import sys

from smallest_key import fixture, options, simulate


def dogram_report(dogram_root: str) -> dict[str, object]:
    root = Path(dogram_root).resolve()
    if not (root / "dogram" / "rectangle.py").is_file():
        raise ValueError("pass a trusted checkout containing Dogram rectangle.py")
    sys.path.insert(0, str(root))
    try:
        from dogram.rectangle import evaluate_rectangle
        from dogram.anti_collapse_reachability import analyze_collapse
    finally:
        sys.path.pop(0)

    initial, actions = fixture()
    lookup = {action.id: action for action in actions}

    def run(*ids: str):
        world = initial
        for action_id in ids:
            future = simulate(world, lookup[action_id])
            if future is None:
                raise AssertionError("declared admitted synthetic step is unavailable")
            world = future
        return world

    states = {
        "00": initial,
        "10": run("teach-ben-well"),
        "01": run("tell-ben-well"),
        "11": run("teach-ben-well", "tell-ben-well"),
    }

    def target_visible(world):
        return int(("ben", "well") in options(world)["visible"])

    cells = {key: {"kind": "integer", "value": target_visible(world)}
             for key, world in states.items()}
    rectangle, consumed = evaluate_rectangle({
        "axis_a": "hypothetical teaching",
        "axis_b": "hypothetical permission-awareness message",
        "cells": cells,
    })

    # The rich state projection retains the typed skill/knowledge variations.
    # The coarser projection sees only currently visible (actor,task) options.
    rich = tuple((
        tuple(sorted(world.skills)),
        tuple(sorted(world.known)),
        tuple(sorted(world.access)),
        tuple(sorted(world.custody)),
    ) for world in states.values())
    coarse = tuple(tuple(sorted(options(world)["visible"]))
                   for world in states.values())
    collapse = analyze_collapse(
        ("00", "10", "01", "11"), rich, coarse)
    return {
        "schema": "motif.dogram-two-key/v0",
        "dogram_source": "trusted-local-checkout",
        "cells": cells,
        "rectangle": rectangle,
        "rectangle_consumed": consumed,
        "anti_collapse": asdict(collapse),
        "limitations": (
            "A nonzero mixed difference within four invented states is not "
            "measured human cooperation, causal identification, inferred ethics, "
            "or execution authority. Dogram does not choose a plan."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dogram-root", required=True)
    args = parser.parse_args()
    print(json.dumps(dogram_report(args.dogram_root), indent=2))
