"""LAW-FORGE-005: speculative sensor-language laboratory.

"Ternary" is an unprivileged candidate encoding, not a premise about nature.
This learner never imports the hidden world or its causal rules. It only gets
typed, source-owned readouts and binary toy outcomes. All instrument grammars
are finite, declared and non-executable outside the simulator.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
from math import ceil, log2
import json

OPERATIONS = frozenset(("BIT", "PAIR", "COUNT2", "REACH2", "PATHCOUNT",
                        "PATHPAIR", "RAW4"))
OP_ORDER = {"BIT": 0, "PAIR": 1, "REACH2": 2, "PATHPAIR": 3,
            "COUNT2": 4, "PATHCOUNT": 5, "RAW4": 6}


def hash_data(value):
    return sha256(json.dumps(value, separators=(",", ":"),
                             sort_keys=True).encode()).hexdigest()


def bits4(data):
    if (not isinstance(data, (tuple, list)) or len(data) != 4
            or any(type(x) is not int or x not in (0, 1) for x in data)):
        raise ValueError("Only a four-edge controlled synthetic graph is supported")
    return tuple(data)


@dataclass(frozen=True)
class Sensor:
    operation: str
    edges: tuple[int, ...] = ()

    def __post_init__(self):
        if self.operation not in OPERATIONS or not isinstance(self.edges, tuple):
            raise ValueError("Unknown or malformed sensor operator")
        expected = {"BIT": 1, "PAIR": 2, "COUNT2": 2, "REACH2": 0,
                    "PATHCOUNT": 0, "PATHPAIR": 0, "RAW4": 0}[self.operation]
        if (len(self.edges) != expected or any(
            type(i) is not int or i not in range(4) for i in self.edges
        ) or tuple(sorted(set(self.edges))) != self.edges):
            raise ValueError("Sensor must reference unique ascending edge indices")

    @property
    def source_reads(self):
        return {"BIT": 1, "PAIR": 2, "COUNT2": 2, "REACH2": 4,
                "PATHCOUNT": 4, "PATHPAIR": 4, "RAW4": 4}[self.operation]

    @property
    def cardinality(self):
        return {"BIT": 2, "PAIR": 4, "COUNT2": 3, "REACH2": 2,
                "PATHCOUNT": 3, "PATHPAIR": 4, "RAW4": 16}[self.operation]

    def packet(self):
        return {"schema": "motif.law-forge.sensor.v1",
                "operation": self.operation, "edges": list(self.edges),
                "authority": "SYNTHETIC_READOUT_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, data):
        if not isinstance(data, dict) or set(data) != {
            "schema", "operation", "edges", "authority", "real_world_authority"
        } or data["schema"] != "motif.law-forge.sensor.v1" or (
            data["authority"] != "SYNTHETIC_READOUT_ONLY" or
            data["real_world_authority"] is not False or
            not isinstance(data["edges"], list)
        ):
            raise ValueError("Unknown or privileged sensor packet")
        return cls(data["operation"], tuple(data["edges"]))


def generate_sensor_language():
    # This AST grammar is offered to the learner in advance. Its semantics
    # remain source-owned; this is NOT autonomous invention of sensing hardware.
    result = [Sensor("BIT", (i,)) for i in range(4)]
    for i, j in combinations(range(4), 2):
        result.extend((Sensor("PAIR", (i, j)), Sensor("COUNT2", (i, j))))
    result.extend(Sensor(op) for op in (
        "REACH2", "PATHCOUNT", "PATHPAIR", "RAW4"))
    return tuple(result)


def normalize_value(value):
    if type(value) is int and 0 <= value <= 15:
        return value
    if (isinstance(value, (tuple, list)) and len(value) in (2, 4)
            and all(type(x) is int and x in (0, 1) for x in value)):
        return tuple(value)
    raise ValueError("Out-of-vocabulary sensor value")


@dataclass(frozen=True)
class Readout:
    """Read-only synthetic source response, stripped of raw topology."""
    token: str
    readings: tuple[tuple[Sensor, object], ...]
    outcome: int
    provenance: str = "SYNTHETIC_SOURCE_ONLY"

    def __post_init__(self):
        if (not isinstance(self.token, str) or not self.token or
                self.provenance != "SYNTHETIC_SOURCE_ONLY" or
                type(self.outcome) is not int or self.outcome not in (0, 1)):
            raise ValueError("Untrusted outcome or synthetic source")
        if (not isinstance(self.readings, tuple) or
                len(self.readings) != len(generate_sensor_language())):
            raise ValueError("Source must provide the declared common sensor panel")
        found = set()
        expected = set(generate_sensor_language())
        for sensor, value in self.readings:
            if sensor in found or sensor not in expected:
                raise ValueError("Duplicate or unregistered source sensor")
            found.add(sensor)
            v = normalize_value(value)
            if sensor.operation in ("BIT", "REACH2") and (
                type(v) is not int or v not in (0, 1)
            ):
                raise ValueError("Malformed Boolean readout")
            if sensor.operation in ("COUNT2", "PATHCOUNT") and (
                type(v) is not int or v not in (0, 1, 2)
            ):
                raise ValueError("Malformed three-valued readout")
            if sensor.operation in ("PAIR", "PATHPAIR") and (
                not isinstance(v, tuple) or len(v) != 2
            ):
                raise ValueError("Malformed two-bit pair readout")
            if sensor.operation == "RAW4" and (
                not isinstance(v, tuple) or len(v) != 4
            ):
                raise ValueError("Malformed four-bit raw readout")
        if found != expected:
            raise ValueError("Incomplete readout panel")

    def value(self, sensor):
        return next(v for s, v in self.readings if s == sensor)


def witness_digest(rows):
    return hash_data(sorted(
        [[r.token, r.outcome,
          [(s.packet(), list(v) if isinstance(v, tuple) else v)
           for s, v in r.readings]]
         for r in rows], key=lambda x: x[0]))


@dataclass(frozen=True)
class SensorModel:
    sensor: Sensor
    mapping: tuple[tuple[object, int], ...]
    source_digest: str
    cost_model: str

    def predict(self, sample):
        if not isinstance(sample, Readout):
            raise ValueError("Only typed observed synthetic panels")
        key = sample.value(self.sensor)
        return next((y for v, y in self.mapping if v == key), None)

    @property
    def id(self):
        return "sensor-model-" + hash_data({
            "sensor": self.sensor.packet(),
            "mapping": [(list(x) if isinstance(x, tuple) else x, y)
                        for x, y in self.mapping],
            "source": self.source_digest, "cost_model": self.cost_model
        })[:20]

    def packet(self):
        return {"schema": "motif.law-forge.sensor-model.v1",
                "id": self.id, "sensor": self.sensor.packet(),
                "mapping": [[list(x) if isinstance(x, tuple) else x, y]
                            for x, y in self.mapping],
                "source_digest": self.source_digest, "cost_model": self.cost_model,
                "status": "PROPOSAL_ONLY", "real_world_authority": False}


def score(sensor, cost_model):
    if cost_model not in ("symbolic_capacity", "binary_encoded"):
        raise ValueError("Unknown declared capacity model")
    capacity = (ceil(log2(sensor.cardinality) * 1000)
                if cost_model == "symbolic_capacity"
                else ceil(log2(sensor.cardinality)) * 1000)
    # First minimize source-read obligations, then representational capacity.
    # Ties favor conventional binary operators. Not measured energy/latency.
    return (sensor.source_reads, capacity, OP_ORDER[sensor.operation],
            sensor.operation, sensor.edges)


def fit(rows, sensor, cost_model="symbolic_capacity"):
    rows = tuple(rows)
    if not rows or any(not isinstance(row, Readout) for row in rows):
        raise ValueError("Typed source readouts required")
    seen = {}
    for row in rows:
        v = row.value(sensor)
        if v in seen and seen[v] != row.outcome:
            return None
        seen[v] = row.outcome
    vals = tuple(sorted(seen.items()))
    return SensorModel(sensor, vals, witness_digest(rows), cost_model)


def discover(rows, menu="all", cost_model="symbolic_capacity"):
    if menu not in ("all", "binary", "ternary", "full_raw"):
        raise ValueError("Unregistered sensor comparison")
    rows = tuple(rows)
    offers = generate_sensor_language()
    if menu == "binary":
        offers = tuple(s for s in offers
                       if s.operation not in ("COUNT2", "PATHCOUNT"))
    elif menu == "ternary":
        offers = tuple(s for s in offers
                       if s.operation in ("COUNT2", "PATHCOUNT"))
    elif menu == "full_raw":
        offers = (Sensor("RAW4"),)
    candidates = tuple(model for sensor in offers
                       if (model := fit(rows, sensor, cost_model)) is not None)
    if not candidates:
        return None, "HOLD_NO_PREDICTIVE_SENSOR"
    winner = min(candidates, key=lambda m: score(m.sensor, cost_model))
    return winner, "PROPOSE_REPRESENTATION_ONLY"


@dataclass(frozen=True)
class Query:
    graph_controls: tuple[int, int, int, int]

    def __post_init__(self):
        bits4(self.graph_controls)

    def packet(self):
        return {"schema": "motif.law-forge.graph-probe.v1",
                "controls": list(self.graph_controls),
                "authority": "SYNTHETIC_GRAPH_PROBE_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, data):
        if not isinstance(data, dict) or set(data) != {
            "schema", "controls", "authority", "real_world_authority"
        } or data["schema"] != "motif.law-forge.graph-probe.v1" or (
            data["authority"] != "SYNTHETIC_GRAPH_PROBE_ONLY" or
            data["real_world_authority"] is not False
        ):
            raise ValueError("Unauthenticated or privileged source query")
        return cls(bits4(data["controls"]))


def remaining_probes(visible_graph_controls, budget):
    """Bounded factorial source request; not an optimal inquiry selector."""
    if type(budget) is not int or budget < 0:
        raise ValueError("Nonnegative exact query budget")
    seen = {bits4(v) for v in visible_graph_controls}
    missing = [Query(v) for v in product((0, 1), repeat=4)
               if v not in seen]
    return tuple(missing) if len(missing) <= budget else ()


def independent_review(model, rows):
    if model is None:
        return {"status": "HOLD_NO_SUPPORTED_REPRESENTATION", "failures": None}
    rows = tuple(rows)
    if len(rows) < 32 or any(not isinstance(r, Readout) for r in rows):
        return {"status": "HOLD_INSUFFICIENT_REVIEW", "failures": None}
    tokens = {r.token for r in rows}
    if len(tokens) < 32:
        return {"status": "HOLD_DISTINCT_REVIEW_COVERAGE", "failures": None}
    wrong = sum(model.predict(r) != r.outcome for r in rows)
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if wrong == 0 else "HOLD_INDEPENDENT_FALSIFIER"),
            "failures": wrong}
