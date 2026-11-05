"""LAW-FORGE-007 — assimilate exact classical lookup as a first-class skill.

A source-revision-bound truth table is the *authoritative local snapshot*.
Derived sensor programs, when useful, are independently verifiable compact
representations of that same table, with at most three exact exceptions.

Unknown inputs, changed source contracts, unsupported authority and incomplete
coverage must HOLD. This is classical finite-domain model selection, not
knowledge of an unobserved or changing world.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-006"))
from inventor import Instrument, generated_programs

SCHEMA = "motif.law-forge.lookup-skill.v1"
MAX_WIDTH = 8
MAX_EXCEPTIONS = 3


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def vector(value, width):
    if (not isinstance(value, (list, tuple)) or len(value) != width or
            any(type(v) is not int or v not in (0, 1) for v in value)):
        raise ValueError("Strict binary source vector required")
    return tuple(value)


@dataclass(frozen=True)
class Contract:
    source: str
    revision: str
    channels: tuple[str, ...]

    def __post_init__(self):
        if (not isinstance(self.source, str) or not 1 <= len(self.source) <= 128
                or not isinstance(self.revision, str)
                or not 1 <= len(self.revision) <= 128
                or not isinstance(self.channels, tuple)
                or not 1 <= len(self.channels) <= MAX_WIDTH
                or any(not isinstance(s, str) or not s or len(s) > 48
                       for s in self.channels)
                or len(set(self.channels)) != len(self.channels)):
            raise ValueError("Malformed bounded source capability contract")

    @property
    def width(self):
        return len(self.channels)

    @property
    def id(self):
        return digest(self.packet())

    def packet(self):
        return {"schema": "motif.law-forge.lookup-source.v1",
                "source": self.source, "revision": self.revision,
                "channels": list(self.channels),
                "allowed_operation": "LOCAL_BINARY_READ_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, obj):
        if (not isinstance(obj, dict) or set(obj) != {
            "schema", "source", "revision", "channels",
            "allowed_operation", "real_world_authority"
        } or obj["schema"] != "motif.law-forge.lookup-source.v1"
                or obj["allowed_operation"] != "LOCAL_BINARY_READ_ONLY"
                or obj["real_world_authority"] is not False
                or not isinstance(obj["channels"], list)):
            raise ValueError("Invalid or privileged source contract")
        return cls(obj["source"], obj["revision"], tuple(obj["channels"]))


@dataclass(frozen=True)
class Reading:
    vector: tuple[int, ...]
    outcome: int
    contract_id: str
    provenance: str = "SYNTHETIC_SOURCE_OBSERVATION"

    def __post_init__(self):
        if (not isinstance(self.vector, tuple)
                or not 1 <= len(self.vector) <= MAX_WIDTH):
            raise ValueError("Wrong vector")
        vector(self.vector, len(self.vector))
        if (type(self.outcome) is not int or self.outcome not in (0, 1)
                or not isinstance(self.contract_id, str)
                or len(self.contract_id) != 64 or
                any(c not in "0123456789abcdef" for c in self.contract_id)
                or self.provenance != "SYNTHETIC_SOURCE_OBSERVATION"):
            raise ValueError("Only typed local source evidence")


def normalized(contract, observations):
    if not isinstance(contract, Contract):
        raise ValueError("Missing typed owner capability contract")
    result = {}
    for row in observations:
        if (not isinstance(row, Reading) or
                row.contract_id != contract.id or
                len(row.vector) != contract.width):
            raise ValueError("Evidence does not match pinned source contract")
        if row.vector in result and result[row.vector] != row.outcome:
            raise ValueError("Conflicting outcomes for the same source setting")
        result[row.vector] = row.outcome
    if not result:
        raise ValueError("No source observations")
    return tuple(sorted(result.items()))


def snapshot_id(contract, rows):
    return digest({"contract": contract.packet(),
                   "observations": [[list(x), y] for x, y in rows]})


def compact_cost(program, exception_count):
    # Approximate *description units*, NOT measured hardware/energy.
    return (16 + 8 * len(program.clauses) +
            8 * sum(len(clause) for clause in program.clauses) +
            7 * exception_count)


def find_compact(rows, width):
    """Find an exactly equivalent bounded circuit + exceptions.

    Only six-link graphs use the 006 DNF language. Larger source contracts
    retain classical lookup rather than pretending the old grammar generalized.
    """
    if width != 6 or len(rows) != 2 ** width:
        return None
    limit = (width + 1) * len(rows)
    best = None
    best_key = None
    for sensor in generated_programs():
        failures = tuple((x, y) for x, y in rows
                         if sensor.predict(x) != y)
        if len(failures) > MAX_EXCEPTIONS:
            continue
        score = compact_cost(sensor, len(failures))
        key = (score, len(failures), sensor.clauses)
        if score < limit and (best_key is None or key < best_key):
            best = (sensor, failures)
            best_key = key
    return best


@dataclass(frozen=True)
class LookupSkill:
    contract: Contract
    observations: tuple[tuple[tuple[int, ...], int], ...]
    source_digest: str
    program: Instrument | None = None
    corrections: tuple[tuple[tuple[int, ...], int], ...] = ()

    def __post_init__(self):
        if not isinstance(self.contract, Contract):
            raise ValueError("Contract required")
        if (not isinstance(self.observations, tuple) or
                len(self.observations) > 2 ** self.contract.width):
            raise ValueError("Invalid snapshot entries")
        expected = tuple(sorted(set(x for x, _ in self.observations)))
        if len(expected) != len(self.observations):
            raise ValueError("Conflicting or duplicate snapshot settings")
        for x, y in self.observations:
            vector(x, self.contract.width)
            if type(y) is not int or y not in (0, 1):
                raise ValueError("Non-binary source outcome")
        if self.source_digest != snapshot_id(self.contract, self.observations):
            raise ValueError("Snapshot fingerprint does not match source observations")
        if self.program is None:
            if self.corrections:
                raise ValueError("Raw lookup may not carry uncompiled corrections")
            return
        if (self.contract.width != 6 or
                len(self.observations) != 64 or
                not isinstance(self.program, Instrument) or
                len(self.corrections) > MAX_EXCEPTIONS):
            raise ValueError("Untrusted or partial compact program")
        if tuple(sorted(set(x for x, _ in self.corrections))) != tuple(
                x for x, _ in self.corrections):
            raise ValueError("Duplicate or unordered compact corrections")
        raw = dict(self.observations)
        if any(x not in raw or type(y) is not int or y not in (0, 1)
               for x, y in self.corrections):
            raise ValueError("Corrections must be witnessed snapshot cells")
        corrections = dict(self.corrections)
        for x, y in self.observations:
            if corrections.get(x, self.program.predict(x)) != y:
                raise ValueError("Compact program and source truth table disagree")
        if compact_cost(self.program, len(self.corrections)) >= (
                self.contract.width + 1) * len(self.observations):
            raise ValueError("Compact candidate did not reduce declared cost")

    @property
    def complete(self):
        return len(self.observations) == 2 ** self.contract.width

    @property
    def representation(self):
        if self.program is None:
            return "RAW_LOOKUP"
        return "COMPACT_EXACT" if not self.corrections else "COMPACT_WITH_EXCEPTIONS"

    @property
    def id(self):
        return "lookup-" + digest({"source": self.source_digest,
                                     "program": (self.program.program()
                                                 if self.program else None),
                                     "corrections": self.corrections})[:24]

    def predict(self, inputs, presented_contract):
        if (not isinstance(presented_contract, Contract) or
                presented_contract.id != self.contract.id):
            return {"status": "HOLD_SOURCE_CONTRACT_CHANGED",
                    "value": None, "evidence": self.source_digest}
        values = vector(inputs, self.contract.width)
        lookup = dict(self.observations)
        if values not in lookup:
            return {"status": "HOLD_UNOBSERVED_CONFIGURATION",
                    "value": None, "evidence": self.source_digest}
        reference = lookup[values]
        if self.program is not None:
            measured = dict(self.corrections).get(
                values, self.program.predict(values))
            if measured != reference:
                raise AssertionError("Compact instrument disagrees with locked lookup")
        return {"status": "SUPPORTED_SYNTHETIC_SNAPSHOT",
                "value": reference,
                "route": self.representation,
                "evidence": self.source_digest,
                "source_contract_id": self.contract.id,
                "real_world_authority": False}

    def packet(self):
        return {"schema": SCHEMA, "id": self.id,
                "source_contract": self.contract.packet(),
                "source_digest": self.source_digest,
                "truth_table": [[list(x), y] for x, y in self.observations],
                "representation": self.representation,
                "program": self.program.program() if self.program else None,
                "corrections": [[list(x), y] for x, y in self.corrections],
                "complete_domain": self.complete,
                "status": "PROPOSAL_ONLY",
                "authority": "SYNTHETIC_PREDICTION_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, data):
        if (not isinstance(data, dict) or set(data) != {
            "schema", "id", "source_contract", "source_digest",
            "truth_table", "representation", "program", "corrections",
            "complete_domain", "status", "authority", "real_world_authority"
        } or data["schema"] != SCHEMA or
                data["status"] != "PROPOSAL_ONLY" or
                data["authority"] != "SYNTHETIC_PREDICTION_ONLY" or
                data["real_world_authority"] is not False or
                not isinstance(data["truth_table"], list) or
                not isinstance(data["corrections"], list)):
            raise ValueError("Tampered or privileged lookup cartridge")
        contract = Contract.from_packet(data["source_contract"])
        def unpack_row(row):
            if (not isinstance(row, list) or len(row) != 2
                    or not isinstance(row[0], list)):
                raise ValueError("Malformed snapshot truth table")
            return (vector(row[0], contract.width), row[1])
        rows = tuple(unpack_row(row) for row in data["truth_table"])
        corrections = tuple(unpack_row(row) for row in data["corrections"])
        model = cls(contract, rows, data["source_digest"],
                    Instrument.from_program(data["program"])
                    if data["program"] is not None else None, corrections)
        if (model.id != data["id"] or
                data["complete_domain"] is not model.complete or
                data["representation"] != model.representation):
            raise ValueError("Cartridge content disagrees with identifier")
        return model


def assimilate(contract, observations):
    rows = normalized(contract, observations)
    source = snapshot_id(contract, rows)
    candidate = find_compact(rows, contract.width)
    if candidate is None:
        return LookupSkill(contract, rows, source)
    sensor, errors = candidate
    return LookupSkill(contract, rows, source, sensor, errors)


def independent_review(model, contract, rows):
    if not isinstance(model, LookupSkill):
        return {"status": "HOLD_NO_SKILL", "contradictions": None}
    if not model.complete:
        return {"status": "HOLD_INCOMPLETE_SOURCE_SNAPSHOT",
                "contradictions": None}
    if contract.id != model.contract.id:
        return {"status": "HOLD_SOURCE_CONTRACT_CHANGED",
                "contradictions": None}
    readings = tuple(rows)
    try:
        actual = normalized(contract, readings)
    except ValueError:
        return {"status": "HOLD_BAD_INDEPENDENT_EVIDENCE",
                "contradictions": None}
    if len(actual) != 2 ** contract.width:
        return {"status": "HOLD_INDEPENDENT_REVIEW_COVERAGE",
                "contradictions": None}
    contradictions = sum(
        model.predict(x, contract)["value"] != y for x, y in actual
    )
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if contradictions == 0 else "HOLD_INDEPENDENT_FALSIFIER"),
            "contradictions": contradictions}
