"""Opt-in native Dogram calculations over inferred bridge candidate bindings.

Dogram checks one declared 2x2 interaction and information collapse.
It neither invents offers nor proves participant consent or causation.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import sys

from bridge import Goal, generate, options, transition, workshop


def calculate(dogram_root: str) -> dict[str, object]:
    root = Path(dogram_root).resolve()
    if not (root / "dogram" / "rectangle.py").is_file():
        raise ValueError("explicit trusted Dogram checkout required")
    sys.path.insert(0, str(root))
    try:
        from dogram.rectangle import evaluate_rectangle
        from dogram.anti_collapse_reachability import analyze_collapse
    finally:
        sys.path.pop(0)

    scene, offers, accepted, goal = workshop()
    bindings = generate(scene, offers, accepted, goal)
    teach = next(x for x in bindings if x.kind == "teach" and not x.held)
    inform = next(x for x in bindings if x.kind == "inform" and not x.held)
    one = transition(scene, teach)
    two = transition(scene, inform)
    both = transition(one, inform)
    if not one or not two or not both:
        raise AssertionError("constructed synthetic 2x2 interaction is invalid")
    worlds = {"00": scene, "10": one, "01": two, "11": both}

    def gained_visible(world):
        return int(("ben", "well") in options(world)["visible"])

    counts = {key: {"kind": "integer", "value": gained_visible(world)}
              for key, world in worlds.items()}
    rectangle, consumed = evaluate_rectangle({
        "axis_a": "generated teaching binding",
        "axis_b": "generated information binding",
        "cells": counts,
    })
    rich = tuple((tuple(sorted(world.skills)), tuple(sorted(world.known)))
                 for world in worlds.values())
    coarse = tuple(tuple(sorted(options(world)["visible"]))
                   for world in worlds.values())
    collapse = analyze_collapse(("00", "10", "01", "11"), rich, coarse)

    return {"schema": "motif.bridge-dogram/v0",
            "source": "pinned externally chosen Dogram checkout",
            "binding_ids": [teach.id, inform.id],
            "rectangle": rectangle,
            "consumed": consumed,
            "information_collapse": asdict(collapse),
            "boundary": ("Declared synthetic interaction and finite "
                         "indistinguishability, not real-world social science, "
                         "causality, evidence, or authorization.")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dogram-root", required=True)
    args = parser.parse_args()
    print(json.dumps(calculate(args.dogram_root), indent=2))
