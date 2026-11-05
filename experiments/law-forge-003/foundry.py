"""LAW-FORGE-003 — source-separated operator synthesis from a NAND primitive.

Only declarative examples enter this researcher. The hidden oracle and review
partitions live in world.py, which is never imported here. Neither circuits
nor request packets execute arbitrary code or contact outside services.

The NAND and left-fold interpreter are PRE-SUPPLIED universal machinery:
the learner discovers specific bounded circuit *definitions*, not new logic.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
from math import log2

SCHEMA = "motif.law-forge.operator-nand.v1"


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def bits(items, lo=2, hi=12):
    if (not isinstance(items, (tuple, list)) or not lo <= len(items) <= hi
            or any(type(x) is not int or x not in (0, 1) for x in items)):
        raise ValueError("Only a bounded tuple of binary observations is permitted")
    return tuple(items)


@dataclass(frozen=True)
class Example:
    inputs: tuple[int, ...]
    outcome: int
    provenance: str = "SYNTHETIC_OBSERVATION"

    def __post_init__(self):
        bits(self.inputs)
        if type(self.outcome) is not int or self.outcome not in (0, 1) or (
            self.provenance != "SYNTHETIC_OBSERVATION"
        ):
            raise ValueError("Invalid or non-synthetic witness")


@dataclass(frozen=True)
class NandCircuit:
    # Every gate output appends a wire; inputs occupy wire slots 0 and 1.
    # Output is the final wire, or pin 0/1 for an empty gate array.
    gates: tuple[tuple[int, int], ...]
    output_pin: int = 0

    def __post_init__(self):
        if not isinstance(self.gates, tuple) or len(self.gates) > 4:
            raise ValueError("At most four NAND gates")
        if type(self.output_pin) is not int or self.output_pin not in (0, 1):
            raise ValueError("Invalid initial output pin")
        for depth, gate in enumerate(self.gates):
            if (not isinstance(gate, tuple) or len(gate) != 2 or
                    any(type(i) is not int or i < 0 or i >= depth + 2
                        for i in gate) or gate[0] > gate[1]):
                raise ValueError("Gate inputs must be prior wires in canonical order")

    def compute(self, a, b):
        if type(a) is not int or type(b) is not int or a not in (0, 1) or b not in (0, 1):
            raise ValueError("NAND requires two binary signals")
        wires = [a, b]
        for first, second in self.gates:
            wires.append(1 - (wires[first] & wires[second]))
        return wires[-1] if self.gates else wires[self.output_pin]

    def signature(self):
        return tuple(self.compute(a, b) for a, b in product((0, 1), repeat=2))

    def run(self, values):
        values = bits(values)
        state = values[0]
        for value in values[1:]:
            state = self.compute(state, value)
        return state

    def data(self):
        return {"primitive": "NAND", "wires": 2,
                "gates": [list(pair) for pair in self.gates],
                "output_pin": self.output_pin}

    @classmethod
    def from_data(cls, data):
        if not isinstance(data, dict) or set(data) != {
            "primitive", "wires", "gates", "output_pin"
        } or data["primitive"] != "NAND" or type(data["wires"]) is not int or (
            data["wires"] != 2
        ) or not isinstance(data["gates"], list):
            raise ValueError("Strict NAND-only gate netlist required")
        pairs = []
        for p in data["gates"]:
            if not isinstance(p, list):
                raise ValueError("Gate is a pair of earlier wire indices")
            pairs.append(tuple(p))
        return cls(tuple(pairs), data["output_pin"])


@lru_cache(maxsize=1)
def gate_library():
    """Exhaustively search <=4 NAND gates; keep shortest program per behavior.

    Every circuit is actually evaluated on the four two-bit inputs.
    Never uses names like XOR, OR or AND to construct a candidate.
    """
    best = {}
    def remember(c):
        signature = c.signature()
        if signature not in best:
            best[signature] = c
    remember(NandCircuit((), 0))
    remember(NandCircuit((), 1))
    for size in range(1, 5):
        def enumerate_gates(prefix):
            index = len(prefix)
            if index == size:
                remember(NandCircuit(tuple(prefix)))
                return
            for pair in combinations_with_replacement(range(2 + index), 2):
                enumerate_gates(prefix + (pair,))
        enumerate_gates(())
    return tuple(sorted(best.items()))


def observed_digest(rows):
    return digest(sorted([[list(x.inputs), x.outcome] for x in rows]))


@dataclass(frozen=True)
class Operator:
    implementation: str  # NAND_CIRCUIT or CLASSICAL_TABLE
    signature: tuple[int, int, int, int]
    source_digest: str
    circuit: NandCircuit | None = None

    def __post_init__(self):
        if self.implementation not in ("NAND_CIRCUIT", "CLASSICAL_TABLE"):
            raise ValueError("Unsupported operator implementation")
        if len(self.signature) != 4 or any(
            type(b) is not int or b not in (0, 1) for b in self.signature
        ):
            raise ValueError("Binary truth table only")
        if not isinstance(self.source_digest, str) or len(self.source_digest) != 64 or any(
            c not in "0123456789abcdef" for c in self.source_digest
        ):
            raise ValueError("Invalid content provenance digest")
        if self.implementation == "NAND_CIRCUIT":
            if not isinstance(self.circuit, NandCircuit) or (
                self.circuit.signature() != self.signature
            ):
                raise ValueError("Circuit does not implement signed truth table")
        elif self.circuit is not None:
            raise ValueError("Classical control may not smuggle executable gates")

    def compute(self, a, b):
        if self.circuit is not None:
            return self.circuit.compute(a, b)
        return self.signature[2 * a + b]

    def predict(self, items):
        items = bits(items)
        state = items[0]
        for value in items[1:]:
            state = self.compute(state, value)
        return state

    @property
    def id(self):
        return "operator-" + digest({
            "implementation": self.implementation,
            "signature": list(self.signature),
            "circuit": self.circuit.data() if self.circuit else None,
            "source": self.source_digest
        })[:24]

    def packet(self):
        return {
            "schema": SCHEMA,
            "id": self.id,
            "implementation": self.implementation,
            "signature": list(self.signature),
            "netlist": self.circuit.data() if self.circuit else None,
            "source_digest": self.source_digest,
            "application": "LEFT_FOLD_OVER_BOOLEAN_SEQUENCE",
            "status": "PROPOSAL_ONLY",
            "authority": "SYNTHETIC_PREDICTION_ONLY",
            "real_world_authority": False
        }

    @classmethod
    def from_packet(cls, packet):
        if not isinstance(packet, dict) or set(packet) != {
            "schema", "id", "implementation", "signature", "netlist",
            "source_digest", "application", "status", "authority",
            "real_world_authority"
        } or packet["schema"] != SCHEMA or (
            packet["application"] != "LEFT_FOLD_OVER_BOOLEAN_SEQUENCE"
        ) or packet["status"] != "PROPOSAL_ONLY" or (
            packet["authority"] != "SYNTHETIC_PREDICTION_ONLY"
        ) or packet["real_world_authority"] is not False:
            raise ValueError("Invalid or privileged operator packet")
        signature = packet["signature"]
        if not isinstance(signature, list):
            raise ValueError("Signature must be JSON array")
        netlist = (NandCircuit.from_data(packet["netlist"])
                   if packet["netlist"] is not None else None)
        op = cls(packet["implementation"], tuple(signature),
                 packet["source_digest"], netlist)
        if op.id != packet["id"]:
            raise ValueError("Operator checksum does not match content")
        return op


def possibilities(rows, method="nand"):
    """Fit reproducible binary operator programs without seeing hidden laws."""
    rows = tuple(rows)
    if not rows or any(not isinstance(row, Example) for row in rows):
        raise ValueError("Typed synthetic observations required")
    if method not in ("nand", "classical"):
        raise ValueError("Unsupported comparison method")
    options = (gate_library() if method == "nand" else
               ((tuple(output), None)
                for output in product((0, 1), repeat=4)))
    source = observed_digest(rows)
    fitted = []
    for sig, circuit in options:
        op = Operator("NAND_CIRCUIT" if method == "nand" else "CLASSICAL_TABLE",
                      sig, source, circuit)
        if all(op.predict(row.inputs) == row.outcome for row in rows):
            fitted.append(op)
    return tuple(fitted)


@dataclass(frozen=True)
class Query:
    inputs: tuple[int, ...]
    information_bits: float
    cost: int
    authority: str = "SYNTHETIC_SIMULATOR_ONLY"

    def packet(self):
        return {"schema": "motif.law-forge.operator-query.v1",
                "inputs": list(self.inputs), "declared_cost": self.cost,
                "authority": self.authority}

    @classmethod
    def from_packet(cls, packet):
        if not isinstance(packet, dict) or set(packet) != {
            "schema", "inputs", "declared_cost", "authority"
        } or packet["schema"] != "motif.law-forge.operator-query.v1" or (
            packet["authority"] != "SYNTHETIC_SIMULATOR_ONLY"
        ):
            raise ValueError("Unapproved synthetic query")
        values = bits(packet["inputs"], hi=4)
        cost = 1 + len(values)
        if type(packet["declared_cost"]) is not int or packet["declared_cost"] != cost:
            raise ValueError("Invalid query resource receipt")
        return cls(values, 0.0, cost)


def propose(models, rows, remaining_cost=3, prohibited=()):
    """Finite max-entropy per synthetic sequence cost. Pure proposal only."""
    if type(remaining_cost) is not int or remaining_cost < 0:
        raise ValueError("Nonnegative integer resource budget required")
    if len(models) < 2:
        return None
    seen = {row.inputs for row in rows}
    forbidden = set(prohibited)
    best, best_score = None, 0.0
    for n in (2, 3, 4):
        cost = n + 1
        if cost > remaining_cost:
            continue
        for vals in product((0, 1), repeat=n):
            if vals in seen or vals in forbidden:
                continue
            votes = [m.predict(vals) for m in models]
            p = sum(votes) / len(votes)
            entropy = (0.0 if p in (0, 1) else
                       -p * log2(p) - (1 - p) * log2(1 - p))
            score = entropy / cost
            if score > best_score + 1e-12:
                best = Query(vals, round(entropy, 6), cost)
                best_score = score
    return best


def review(operator, examples):
    """Separate evaluator review, never grants execution or real provenance."""
    if operator is None:
        return {"status": "HOLD_NOT_IDENTIFIED", "contradictions": None}
    rows = tuple(examples)
    if len(rows) < 32:
        return {"status": "HOLD_INSUFFICIENT_REVIEW", "contradictions": None}
    witnessed = {e.inputs for e in rows}
    if (not {tuple(x) for x in product((0, 1), repeat=2)} <= witnessed or
        not {tuple(x) for x in product((0, 1), repeat=3)} <= witnessed or
        not any(len(x) == 5 for x in witnessed) or
        not any(len(x) == 8 for x in witnessed)):
        return {"status": "HOLD_REVIEW_COVERAGE", "contradictions": None}
    if any(not isinstance(row, Example) for row in rows):
        raise ValueError("Independent synthetic typed evidence required")
    failures = sum(operator.predict(x.inputs) != x.outcome for x in rows)
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if failures == 0 else "HOLD_INDEPENDENT_FALSIFIER"),
            "contradictions": failures}
