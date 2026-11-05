"""LAW-FORGE-002: a source-separated, finite feature-program synthesizer.

Extends LAW-FORGE-001's typed observations, but never imports the simulator.
A proposed constructor is a data-only AST made from generic Boolean primitives,
not arbitrary Python/JS and not a discovered new mathematical primitive.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from json import dumps
from math import log2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "law-forge-001"))
from forge import Probe, Observation, hypotheses as original_hypotheses

COMMUTATIVE = ("AND", "OR", "XOR")
FEATURE_SCHEMA = "motif.law-forge.constructor.v1"


def digest(value):
    return sha256(dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atoms():
    return (("LAG", 0), ("LAG", 1))


def feature_programs():
    """Enumerate finite typed compositions; no hidden world labels supplied."""
    one, two = atoms()
    return (one, two) + tuple((op, one, two) for op in COMMUTATIVE)


def serialize(expr):
    if not isinstance(expr, tuple) or not expr:
        raise ValueError("Malformed feature expression")
    if len(expr) == 2 and expr[0] == "LAG" and type(expr[1]) is int and expr[1] in (0, 1):
        return {"op": "LAG", "index": expr[1]}
    if len(expr) == 3 and expr[0] in COMMUTATIVE:
        return {"op": expr[0], "args": [serialize(expr[1]), serialize(expr[2])]}
    raise ValueError("Unsupported feature AST")


def deserialize(packet):
    if not isinstance(packet, dict):
        raise ValueError("Only a strict JSON AST is accepted")
    if set(packet) == {"op", "index"} and packet["op"] == "LAG" and (
        type(packet["index"]) is int and packet["index"] in (0, 1)
    ):
        return ("LAG", packet["index"])
    if set(packet) == {"op", "args"} and packet["op"] in COMMUTATIVE:
        args = packet["args"]
        if not isinstance(args, list) or len(args) != 2:
            raise ValueError("Binary constructor requires exactly two inputs")
        left, right = deserialize(args[0]), deserialize(args[1])
        # Bounds check: no executable or recursive unbounded code.
        def count(x):
            return 1 if x[0] == "LAG" else 1 + count(x[1]) + count(x[2])
        if 1 + count(left) + count(right) > 3:
            raise ValueError("Only one binary composition is permitted")
        return (packet["op"], left, right)
    raise ValueError("Unknown operation, extra fields or executable instruction")


def evaluate(expr, probe):
    if not isinstance(probe, Probe):
        raise ValueError("Read-only typed synthetic probe required")
    expr = deserialize(serialize(expr))  # validate local AST before evaluation
    if expr[0] == "LAG":
        return probe.history[-1][expr[1]]
    left, right = evaluate(expr[1], probe), evaluate(expr[2], probe)
    return {"AND": left & right, "OR": left | right, "XOR": left ^ right}[expr[0]]


def evidence_digest(observations):
    normalized = []
    for row in observations:
        if not isinstance(row, Observation):
            raise ValueError("Untrusted observation type")
        normalized.append([row.probe.packet(), row.outcome])
    return digest(sorted(normalized, key=lambda item: dumps(item, sort_keys=True)))


@dataclass(frozen=True)
class ConstructorModel:
    program: tuple
    table: tuple[tuple[int, int, int, int], ...]
    source_digest: str

    @property
    def id(self):
        return "constructor-" + digest({
            "program": serialize(self.program),
            "table": self.table, "source_digest": self.source_digest
        })[:24]

    def predict(self, probe):
        if not isinstance(probe, Probe):
            raise ValueError("Only typed local synthetic predictions are supported")
        key = (*probe.controls, evaluate(self.program, probe))
        return next((y for a, b, f, y in self.table if (a, b, f) == key), None)

    def packet(self):
        return {
            "schema": FEATURE_SCHEMA,
            "id": self.id,
            "program": serialize(self.program),
            "table": [list(row) for row in self.table],
            "source_digest": self.source_digest,
            "status": "PROPOSAL_ONLY",
            "authority": "PREDICT_SYNTHETIC_ONLY",
            "real_world_authority": False
        }

    @classmethod
    def from_packet(cls, packet):
        if not isinstance(packet, dict) or set(packet) != {
            "schema", "id", "program", "table", "source_digest",
            "status", "authority", "real_world_authority"
        } or packet["schema"] != FEATURE_SCHEMA or (
            packet["status"] != "PROPOSAL_ONLY"
        ) or packet["authority"] != "PREDICT_SYNTHETIC_ONLY" or (
            packet["real_world_authority"] is not False
        ):
            raise ValueError("Invalid constructor cartridge or authority")
        expr = deserialize(packet["program"])
        rows = packet["table"]
        if not isinstance(rows, list) or len(rows) > 8:
            raise ValueError("Invalid binary truth table")
        normalized = []
        for row in rows:
            if not isinstance(row, list) or len(row) != 4 or any(
                type(v) is not int or v not in (0, 1) for v in row
            ):
                raise ValueError("Malformed truth-table row")
            normalized.append(tuple(row))
        if len({row[:3] for row in normalized}) != len(normalized):
            raise ValueError("Conflicting truth-table cells")
        source_digest = packet["source_digest"]
        if not isinstance(source_digest, str) or len(source_digest) != 64 or (
            any(ch not in "0123456789abcdef" for ch in source_digest)
        ):
            raise ValueError("Malformed evidence identifier")
        model = cls(expr, tuple(sorted(normalized)), source_digest)
        if model.id != packet["id"]:
            raise ValueError("Cartridge checksum mismatch")
        return model


def fit(observations, expr):
    rows = tuple(observations)
    if not rows:
        raise ValueError("No synthetic evidence")
    vals = {}
    for row in rows:
        if not isinstance(row, Observation):
            raise ValueError("Untrusted evidence type")
        key = (*row.probe.controls, evaluate(expr, row.probe))
        if key in vals and vals[key] != row.outcome:
            return None
        vals[key] = row.outcome
    return ConstructorModel(expr, tuple(sorted((*k, v) for k, v in vals.items())),
                            evidence_digest(rows))


def synthesize(observations):
    rows = tuple(observations)
    if not rows:
        raise ValueError("No examples")
    incumbent = original_hypotheses(rows)
    if incumbent:
        return {"state": "INCUMBENT_SUFFICIENT", "proposals": (),
                "failed_original": False, "programs_considered": 0}
    # The new generator is searched only after original features all fail.
    candidates = tuple(model for program in feature_programs()
                       if (model := fit(rows, program)) is not None)
    return {"state": "PROPOSE_CONSTRUCTORS" if candidates else "HOLD_NO_GRAMMAR",
            "proposals": candidates, "failed_original": True,
            "programs_considered": len(feature_programs())}


def query(models, observed, budget=1, prohibited=()):
    """Choose a synthetic discriminating test, never execute it."""
    if type(budget) is not int or budget < 0:
        raise ValueError("Nonnegative integer synthetic budget required")
    if budget == 0 or len(models) < 2:
        return None
    already = {row.probe for row in observed}
    excluded = set(prohibited)
    best, high_gain = None, 0.0
    for p, q, a, b in product((0, 1), repeat=4):
        probe = Probe(((p, q),), (a, b))
        if probe in already or probe in excluded:
            continue
        guesses = tuple(m.predict(probe) for m in models)
        if any(v is None for v in guesses):
            continue
        probability = sum(guesses) / len(guesses)
        gain = (0.0 if probability in (0, 1) else
                -probability * log2(probability) -
                (1 - probability) * log2(1 - probability))
        if gain > high_gain:
            best, high_gain = probe, gain
    return best


def distinct(models):
    """No forced selection: two observationally compatible programs HOLD."""
    return models[0] if len(models) == 1 else None


def review(model, observations):
    """Independent local evaluator review is NOT admission or a real witness."""
    if model is None:
        return {"status": "HOLD_UNIDENTIFIED", "contradictions": None}
    rows = tuple(observations)
    if len(rows) < 16:
        return {"status": "HOLD_INSUFFICIENT_REVIEW", "contradictions": None}
    cells = {(tuple(r.probe.history[-1]), r.probe.controls) for r in rows}
    if len(cells) != 16:
        return {"status": "HOLD_COVERAGE", "contradictions": None}
    wrong = sum(model.predict(row.probe) != row.outcome for row in rows)
    return {
        "status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                   if wrong == 0 else "HOLD_INDEPENDENT_FALSIFICATION"),
        "contradictions": wrong
    }
