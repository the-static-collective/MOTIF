"""LAW-FORGE-001: finite, source-separated representation repair.

Only structural observations enter this module. Hidden world rules, world-family
labels, reviewers, and held-out outcomes belong to oracle.py / trial.py.
All authority is limited to proposing a synthetic two-port probe packet.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import log2
import json


def _pair(value):
    if (not isinstance(value, (list, tuple)) or len(value) != 2
            or any(type(x) is not int or x not in (0, 1) for x in value)):
        raise ValueError("Exactly two Boolean synthetic controls required")
    return tuple(value)


@dataclass(frozen=True)
class Probe:
    history: tuple[tuple[int, int], ...]
    controls: tuple[int, int]

    def __post_init__(self):
        if not 1 <= len(self.history) <= 3:
            raise ValueError("A probe must have 1..3 prior synthetic ticks")
        for row in self.history:
            _pair(row)
        _pair(self.controls)

    def packet(self):
        return {"schema": "motif.law-forge.probe.v1",
                "history": [list(x) for x in self.history],
                "controls": list(self.controls),
                "authority": "SYNTHETIC_SIMULATOR_ONLY"}

    @classmethod
    def from_packet(cls, packet):
        if not isinstance(packet, dict) or set(packet) != {
            "schema", "history", "controls", "authority"
        } or packet["schema"] != "motif.law-forge.probe.v1" or (
            packet["authority"] != "SYNTHETIC_SIMULATOR_ONLY"
        ):
            raise ValueError("Invalid, expanded or privileged probe packet")
        rows = packet["history"]
        if not isinstance(rows, list):
            raise ValueError("History must be a JSON array")
        return cls(tuple(_pair(row) for row in rows), _pair(packet["controls"]))


@dataclass(frozen=True)
class Observation:
    probe: Probe
    outcome: int
    provenance: str = "SYNTHETIC_OBSERVATION"

    def __post_init__(self):
        if not isinstance(self.probe, Probe) or type(self.outcome) is not int or (
            self.outcome not in (0, 1)
        ) or self.provenance != "SYNTHETIC_OBSERVATION":
            raise ValueError("Untrusted or malformed synthetic observation")


def feature_grammar(port_count=2):
    """Generate one new *temporal* predicate for every declared input port.

    The generator is given neither a target rule nor the secret world family.
    This is a deliberately finite candidate grammar, NOT open-ended invention.
    """
    if port_count != 2:
        raise ValueError("Only the two-port toy interface is supported")
    return (("CURRENT", -1),) + tuple(("LAG_1", i)
                                     for i in range(port_count))


def flag(feature, probe):
    kind, index = feature
    return 0 if kind == "CURRENT" else probe.history[-1][index]


def _fingerprint(data):
    return sha256(json.dumps(data, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Model:
    feature: tuple[str, int]
    table: tuple[tuple[int, int, int, int], ...]
    source_digest: str

    @property
    def id(self):
        return "law-" + _fingerprint({"feature": self.feature,
                                      "table": self.table,
                                      "source": self.source_digest})[:16]

    def predict(self, probe):
        if not isinstance(probe, Probe):
            raise ValueError("Prediction only accepts a typed local probe")
        key = (*probe.controls, flag(self.feature, probe))
        return next((out for a, b, f, out in self.table
                     if (a, b, f) == key), None)

    def cartridge(self):
        return {"schema": "motif.law-forge.prediction.v1",
                "id": self.id, "temporal_feature": list(self.feature),
                "truth_table": [list(x) for x in self.table],
                "source_digest": self.source_digest,
                "status": "PROPOSAL_ONLY",
                "real_world_authority": False}


def fit(observations, feature):
    """Refuse deterministic explanations contradicted by ANY supplied row."""
    rows = tuple(observations)
    if not rows:
        raise ValueError("At least one recorded observation is required")
    cells = {}
    source = []
    for row in rows:
        if not isinstance(row, Observation):
            raise ValueError("Evidence must be a typed synthetic observation")
        key = (*row.probe.controls, flag(feature, row.probe))
        source.append([row.probe.packet(), row.outcome])
        if key in cells and cells[key] != row.outcome:
            return None
        cells[key] = row.outcome
    digest = _fingerprint(sorted(source, key=lambda x: json.dumps(x, sort_keys=True)))
    return Model(feature, tuple(sorted((*key, val) for key, val in cells.items())),
                 digest)


def hypotheses(observations):
    rows = tuple(observations)
    return tuple(m for feature in feature_grammar()
                 if (m := fit(rows, feature)) is not None)


def contrast(observations):
    """Report witness conflicts under the original instant-only grammar."""
    seen = {}
    conflicts = 0
    for row in observations:
        if not isinstance(row, Observation):
            raise ValueError("Malformed observation")
        key = row.probe.controls
        if key in seen and seen[key] != row.outcome:
            conflicts += 1
        seen[key] = row.outcome
    return conflicts


def _entropy(votes):
    p = sum(votes) / len(votes)
    return 0.0 if p in (0, 1) else -p * log2(p) - (1 - p) * log2(1 - p)


def propose(models, observations, budget, prohibited=()):
    """Pure finite information-gain proposal; NO oracle execution here.

    Controls are limited to two Boolean ports. Prohibition and budget filter
    every candidate before any information optimization.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("Nonnegative integer experiment budget required")
    if budget == 0 or len(models) < 2:
        return None
    seen = {row.probe for row in observations}
    banned = set(prohibited)
    best = None
    gain_best = 0.0
    for pa, pb, a, b in product((0, 1), repeat=4):
        probe = Probe(((pa, pb),), (a, b))
        if probe in seen or probe in banned:
            continue
        votes = [m.predict(probe) for m in models]
        if any(v is None for v in votes):
            continue
        gain = _entropy(votes)
        if gain > gain_best + 1e-10:
            best, gain_best = probe, gain
    return best


def choose(models):
    """No temporal concept if the simpler observed grammar still fits."""
    instant = [m for m in models if m.feature == ("CURRENT", -1)]
    if instant:
        return instant[0]
    return models[0] if len(models) == 1 else None


def independent_review(model, rows):
    """Independent simulated checks, not human approval or real admission."""
    if model is None:
        return {"status": "HOLD_AMBIGUOUS_OR_INADEQUATE", "failures": None}
    if len(rows) < 16:
        return {"status": "HOLD_INSUFFICIENT_REVIEW", "failures": None}
    cells = {(p, q, *row.probe.controls)
             for row in rows
             for p, q in [row.probe.history[-1]]}
    if len(cells) != 16:
        return {"status": "HOLD_REVIEW_COVERAGE", "failures": None}
    failures = sum(model.predict(row.probe) != row.outcome for row in rows)
    return {"status": "ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
            if failures == 0 else "HOLD_INDEPENDENT_FALSIFIER",
            "failures": failures}


def synthesis_record(training, inquiries, candidate, review):
    return {
        "schema": "motif.law-forge.receipt.v1",
        "original_instant_conflicts": contrast(training),
        "new_concept": list(candidate.feature) if candidate else None,
        "probe_packets": [p.packet() for p in inquiries],
        "prediction_cartridge": candidate.cartridge() if candidate else None,
        "review": review,
        "external_calls": 0,
        "automatic_admission": False,
        "real_world_authority": False
    }
