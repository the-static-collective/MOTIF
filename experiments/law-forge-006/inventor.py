"""LAW-FORGE-006: invent a bounded measurement *program* rather than choose a menu.

Input contract: six individually readable binary links, with owner-assigned
addresses. No named reachability, path count, or composite sensor exists in
the researcher's program menu. The researcher composes read-only AND/OR
expressions directly from low-level link primitives. Neither world rules
nor review labels enter this module.

This is a finite, classical monotone-DNF synthesizer, NOT open-ended
instrument or algorithm invention. All proposed programs have no authority
outside an evaluator-owned synthetic simulation.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
from functools import lru_cache
import json

EDGE_COUNT = 6
MAX_CLAUSES = 3
MAX_CLAUSE_WIDTH = 2
READ_CAPABILITY = "READ_ONE_SYNTHETIC_LINK"
SCHEMA = "motif.law-forge.instrument-program.v1"


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def edges(value):
    if (not isinstance(value, (list, tuple)) or len(value) != EDGE_COUNT
            or any(type(n) is not int or n not in (0, 1) for n in value)):
        raise ValueError("Expected exactly six Boolean link observations")
    return tuple(value)


@dataclass(frozen=True)
class Witness:
    inputs: tuple[int, ...]
    result: int
    token: str
    provenance: str = "SYNTHETIC_OWNER_OBSERVATION"

    def __post_init__(self):
        edges(self.inputs)
        if (type(self.result) is not int or self.result not in (0, 1)
                or not isinstance(self.token, str) or len(self.token) < 10
                or self.provenance != "SYNTHETIC_OWNER_OBSERVATION"):
            raise ValueError("Only typed local synthetic witnesses supported")


def evidence_table(rows):
    seen = {}
    for row in rows:
        if not isinstance(row, Witness):
            raise ValueError("Untrusted witness object")
        if row.inputs in seen and seen[row.inputs] != row.result:
            raise ValueError("Conflicting observations for identical controls")
        seen[row.inputs] = row.result
    return seen


def evidence_digest(rows):
    seen = evidence_table(rows)
    return digest([[list(k), seen[k]] for k in sorted(seen)])


@dataclass(frozen=True)
class Instrument:
    """Data-only sensor AST: OR of <=3 terms, each AND of 1..2 link reads."""
    clauses: tuple[tuple[int, ...], ...]

    def __post_init__(self):
        if (not isinstance(self.clauses, tuple) or
                not 1 <= len(self.clauses) <= MAX_CLAUSES):
            raise ValueError("Bounded nonempty program clauses required")
        if tuple(sorted(set(self.clauses))) != self.clauses:
            raise ValueError("Only canonical unique sorted clauses")
        for clause in self.clauses:
            if (not isinstance(clause, tuple) or
                    not 1 <= len(clause) <= MAX_CLAUSE_WIDTH or
                    tuple(sorted(set(clause))) != clause or
                    any(type(i) is not int or not 0 <= i < EDGE_COUNT
                        for i in clause)):
                raise ValueError("Only bounded ANDs of source-owned links")

    def predict(self, inputs):
        values = edges(inputs)
        return int(any(all(values[i] for i in clause)
                       for clause in self.clauses))

    def program(self):
        return {"operator": "OR_OF_AND",
                "clauses": [list(c) for c in self.clauses],
                "atoms": READ_CAPABILITY,
                "read_only": True}

    @classmethod
    def from_program(cls, obj):
        if (not isinstance(obj, dict) or set(obj) != {
            "operator", "clauses", "atoms", "read_only"
        } or obj["operator"] != "OR_OF_AND" or
                obj["atoms"] != READ_CAPABILITY or
                obj["read_only"] is not True or
                not isinstance(obj["clauses"], list)):
            raise ValueError("Unrecognized or privileged program")
        return cls(tuple(tuple(c) if isinstance(c, list) else ()
                         for c in obj["clauses"]))

    @property
    def complexity(self):
        # Explicit descriptive complexity only; NOT measured compute Joules.
        return (sum(len(c) for c in self.clauses), len(self.clauses))

    @property
    def referenced_links(self):
        return tuple(sorted({i for c in self.clauses for i in c}))


@dataclass(frozen=True)
class Proposal:
    sensor: Instrument
    source_digest: str

    @property
    def id(self):
        return "instrument-" + digest({
            "program": self.sensor.program(),
            "source_digest": self.source_digest
        })[:24]

    def packet(self):
        return {"schema": SCHEMA, "id": self.id,
                "sensor": self.sensor.program(),
                "source_digest": self.source_digest,
                "status": "PROPOSE_ONLY",
                "authority": "SYNTHETIC_READ_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, data):
        if (not isinstance(data, dict) or set(data) != {
            "schema", "id", "sensor", "source_digest", "status",
            "authority", "real_world_authority"
        } or data["schema"] != SCHEMA or data["status"] != "PROPOSE_ONLY"
                or data["authority"] != "SYNTHETIC_READ_ONLY"
                or data["real_world_authority"] is not False
                or not isinstance(data["source_digest"], str)
                or len(data["source_digest"]) != 64
                or any(c not in "0123456789abcdef"
                       for c in data["source_digest"])):
            raise ValueError("Invalid or privileged instrument packet")
        out = cls(Instrument.from_program(data["sensor"]), data["source_digest"])
        if data["id"] != out.id:
            raise ValueError("Source/program fingerprint mismatch")
        return out


@lru_cache(maxsize=1)
def generated_programs():
    """Exhaustively build compositions from source primitives; no path template.

    The grammar is supplied; particular combinations are discovered from
    owner observations. Exhaustive search over 1,561 short monotone DNFs.
    """
    terms = tuple((i,) for i in range(EDGE_COUNT)) + tuple(
        combinations(range(EDGE_COUNT), 2))
    candidates = (Instrument(tuple(c)) for n in range(1, MAX_CLAUSES + 1)
                  for c in combinations(terms, n))
    return tuple(sorted(candidates,
                        key=lambda p: (p.complexity, p.clauses)))


def synthesize(rows):
    seen = evidence_table(rows)
    if not seen:
        raise ValueError("Missing typed source evidence")
    for candidate in generated_programs():
        if all(candidate.predict(x) == y for x, y in seen.items()):
            return Proposal(candidate, evidence_digest(rows))
    return None


@dataclass(frozen=True)
class GraphQuery:
    controls: tuple[int, ...]

    def __post_init__(self):
        edges(self.controls)

    def packet(self):
        return {"schema": "motif.law-forge.six-link-query.v1",
                "controls": list(self.controls),
                "authority": "LOCAL_SYNTHETIC_GRAPH_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, obj):
        if (not isinstance(obj, dict) or set(obj) != {
            "schema", "controls", "authority", "real_world_authority"
        } or obj["schema"] != "motif.law-forge.six-link-query.v1"
                or obj["authority"] != "LOCAL_SYNTHETIC_GRAPH_ONLY"
                or obj["real_world_authority"] is not False):
            raise ValueError("Invalid synthetic probe authorization")
        return cls(edges(obj["controls"]))


def query_missing(observed, budget):
    if type(budget) is not int or not 0 <= budget <= 64:
        raise ValueError("Bounded synthetic probe budget required")
    known = {row.inputs for row in observed}
    remaining = tuple(GraphQuery(k) for k in product((0, 1), repeat=EDGE_COUNT)
                      if k not in known)
    return remaining if len(remaining) <= budget else ()


def fit_old_four_edge(rows):
    """Exact test of the prior experiment's four-link observation ceiling."""
    mapping = {}
    for word, outcome in evidence_table(rows).items():
        key = word[:4]
        if key in mapping and mapping[key] != outcome:
            return None
        mapping[key] = outcome
    return mapping


def fit_full_raw(rows):
    """Strong classical baseline: a raw six-link lookup table."""
    return evidence_table(rows)


def review(proposal, observations):
    if proposal is None:
        return {"status": "HOLD_UNEXPRESSIBLE_IN_GRAMMAR",
                "contradictions": None}
    rows = tuple(observations)
    if len(rows) < 64 or any(not isinstance(x, Witness) for x in rows):
        return {"status": "HOLD_INSUFFICIENT_REVIEW",
                "contradictions": None}
    if len({r.inputs for r in rows}) != 64:
        return {"status": "HOLD_REVIEW_COVERAGE",
                "contradictions": None}
    errors = sum(proposal.sensor.predict(r.inputs) != r.result for r in rows)
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if not errors else "HOLD_INDEPENDENT_FALSIFIER"),
            "contradictions": errors}
