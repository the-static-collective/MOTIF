"""Explicit, local read-only entry to an exact original Dogram calculation.
The source is a byte-identical vendored public research module. It is not a
promoted Dogram API, and the receipt cannot confer authority or source truth.
"""
from __future__ import annotations
import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PIN = "c201ce28ff7bb18a28496c0a2eefe2f9451526cc"
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "upstream" / "dogram_probe_partition_refinement.py"

def source_hash(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def native():
    data = SOURCE.read_bytes()
    if source_hash(data) != PIN:
        raise ValueError("HOLD_DOGRAM_SOURCE_DRIFT")
    spec = importlib.util.spec_from_file_location("motif014_exact_pinned_dogram", SOURCE)
    if spec is None or spec.loader is None:
        raise ValueError("HOLD_DOGRAM_IMPORT")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def perform(request):
    if type(request) is not dict or set(request) != {"states","probes","target"}:
        raise ValueError("HOLD_INVALID_INPUT")
    if type(request["probes"]) is not dict or not request["probes"]:
        raise ValueError("HOLD_EMPTY_PROBES")
    if any(type(x) is not list or any(type(v) is not str for v in x)
           for x in request["probes"].values()):
        raise ValueError("HOLD_PROBES_MUST_BE_STRING_VECTORS")
    states = tuple(request["states"])
    target = tuple(request["target"])
    probes = {name: tuple(values) for name,values in request["probes"].items()}
    receipt = native().analyze_probe_family(states, probes, target)
    result = dataclasses.asdict(receipt)
    return {
        "schema": "motif014.dogram-native-probe-receipt/v0",
        "source_blob": PIN,
        "origin": "the-static-collective/Dogram @ 551b5f9df18f17ec69b452ddcdff01718e0ff771",
        **result,
        "observation_verified": False,
        "authority": "none",
        "adopted_into_dogram_public_api": False
    }

if __name__ == "__main__":
    try:
        obj = json.load(sys.stdin)
        print(json.dumps(perform(obj),sort_keys=True))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(2)
