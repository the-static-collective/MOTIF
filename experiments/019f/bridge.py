"""MOTIF-019F: unchanged, hash-pinned Dogram and National Treasure adapters.

Both pinned sources are original donor modules; neither is granted authority.
Node and Python calls are local, bounded, and synthetic only. No network.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parent
PIN_DOGRAM = "c201ce28ff7bb18a28496c0a2eefe2f9451526cc"
PIN_QUESTION = "83574ed0a927fdefe1a53b3ece0960f011b875d0"


class OrganHold(ValueError):
    pass


def _blob_hash(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def verify_sources() -> dict:
    pins = {
        "national_treasure": ("national_treasure_engine.mjs", PIN_QUESTION),
        "dogram": ("dogram_probe_partition_refinement.py", PIN_DOGRAM),
    }
    result = {}
    for name, (filename, pin) in pins.items():
        path = ROOT / "upstream" / filename
        actual = _blob_hash(path.read_bytes())
        if actual != pin:
            raise OrganHold("HOLD_SOURCE_DRIFT_" + name.upper())
        result[name] = actual
    return result


def question_frontier(clue: Mapping) -> dict:
    verify_sources()
    if not isinstance(clue, dict):
        raise OrganHold("HOLD_INVALID_QUESTION_RECORD")
    try:
        process = subprocess.run(
            ["node", str(ROOT / "question_box.mjs")],
            input=json.dumps(clue), capture_output=True, text=True,
            timeout=4, check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise OrganHold("HOLD_NATIVE_QUESTION_UNAVAILABLE") from exc
    if process.returncode != 0:
        raise OrganHold("HOLD_NATIVE_QUESTION:" + process.stderr[:180])
    try:
        answer = json.loads(process.stdout)
        if (answer["schema"] != "motif019f.native-question-gate/v0"
            or answer["original_source_blob"] != PIN_QUESTION
            or answer["native_receipt"]["aperture"]["id"] != answer["aperture"]):
            raise OrganHold("HOLD_NATIVE_QUESTION_RECEIPT_MISMATCH")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise OrganHold("HOLD_NATIVE_QUESTION_FORMAT") from exc
    return answer


def dogram_probe(
    states: tuple[str, ...],
    probes: Mapping[str, tuple[str, ...]],
    target: tuple[str, str],
) -> dict:
    """Call the original finite partition mathematics, no reimplementation."""
    verify_sources()
    path = ROOT / "upstream" / "dogram_probe_partition_refinement.py"
    spec = importlib.util.spec_from_file_location("motif019f_pinned_original_dogram", path)
    if spec is None or spec.loader is None:
        raise OrganHold("HOLD_DOGRAM_MODULE_LOAD")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    receipt = module.analyze_probe_family(states, probes, target)
    return {
        "schema": "motif019f.dogram-bridge/v0",
        "source_blob": PIN_DOGRAM,
        "native_result": dataclasses.asdict(receipt),
        "observations_authenticated": False,
        "effect_authority": "none",
    }


def gated_discriminator(clue: dict, states: tuple[str, ...],
                         probes: Mapping[str, tuple[str, ...]],
                         target: tuple[str, str]) -> dict:
    question = question_frontier(clue)
    if question["aperture"] != "discriminator":
        return {
            "status": "HOLD_QUESTION_FRONTIER",
            "question": question,
            "dogram_was_called": False,
            "dogram": None,
        }
    receipt = dogram_probe(states, probes, target)
    return {
        "status": "PROPOSE_MINIMAL_DISCRIMINATOR",
        "question": question,
        "dogram_was_called": True,
        "dogram": receipt,
    }
