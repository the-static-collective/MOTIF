"""LAW-FORGE-008 — a bounded unknown-world learning desk.

The prior LAW-FORGE-007 typed binary-vector validator is reused directly.
Here the domain has 2**12 configurations, far larger than the query budget.
Exact lookup ALWAYS has precedence. On unobserved inputs, a finite classical
version space votes; prediction is supported only when all surviving models
agree. No posterior probabilities or global scientific certainty are claimed.

This learner has NO import of the owner/oracle and NO right to execute a
membership query. In particular an unobserved input and a false result are
never conflated.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-007"))
from lookup import vector as prior_binary_vector

WIDTH = 12
DOMAIN = 1 << WIDTH
MAX_QUERIES = 24
LIBRARY_VERSION = "bit-pair-triple-grammar-v1"


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def controls(x):
    return prior_binary_vector(x, WIDTH)


@dataclass(frozen=True)
class SourceContract:
    source: str
    revision: str
    challenge_id: str

    def __post_init__(self):
        if any(not isinstance(x, str) or not 1 <= len(x) <= 96
               for x in (self.source, self.revision, self.challenge_id)):
            raise ValueError("Invalid source identity or epoch")

    @property
    def id(self):
        return digest(self.packet())

    def packet(self):
        return {"schema": "motif.law-forge.unknown-world-contract.v1",
                "source": self.source, "revision": self.revision,
                "challenge_id": self.challenge_id,
                "channels": WIDTH, "domain_size": DOMAIN,
                "allowed_action": "LOCAL_SYNTHETIC_MEMBERSHIP_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, item):
        if (not isinstance(item, dict) or set(item) != {
            "schema", "source", "revision", "challenge_id", "channels",
            "domain_size", "allowed_action", "real_world_authority"
        } or item["schema"] != "motif.law-forge.unknown-world-contract.v1"
                or type(item["channels"]) is not int or item["channels"] != WIDTH
                or type(item["domain_size"]) is not int or item["domain_size"] != DOMAIN
                or item["allowed_action"] != "LOCAL_SYNTHETIC_MEMBERSHIP_ONLY"
                or item["real_world_authority"] is not False):
            raise ValueError("Source contract is malformed or privileged")
        return cls(item["source"], item["revision"], item["challenge_id"])


@dataclass(frozen=True)
class Observation:
    x: tuple[int, ...]
    y: int
    contract_id: str
    provenance: str = "SYNTHETIC_OWNER_MEASUREMENT"

    def __post_init__(self):
        controls(self.x)
        if (type(self.y) is not int or self.y not in (0, 1)
                or not isinstance(self.contract_id, str)
                or len(self.contract_id) != 64 or any(
                    ch not in "0123456789abcdef" for ch in self.contract_id)
                or self.provenance != "SYNTHETIC_OWNER_MEASUREMENT"):
            raise ValueError("Untrusted or malformed observation")


def exact_lookup(contract, observations):
    if not isinstance(contract, SourceContract):
        raise ValueError("Source contract required")
    seen = {}
    for obs in observations:
        if not isinstance(obs, Observation) or obs.contract_id != contract.id:
            raise ValueError("Foreign or untrusted source observation")
        if obs.x in seen and seen[obs.x] != obs.y:
            raise ValueError("Conflicting witnesses for identical controls")
        seen[obs.x] = obs.y
    if not seen:
        raise ValueError("Evidence cannot be empty")
    return tuple(sorted(seen.items()))


@dataclass(frozen=True)
class Rule:
    kind: str
    channels: tuple[int, ...]

    def __post_init__(self):
        counts = {"BIT": 1, "AND2": 2, "OR2": 2, "XOR2": 2,
                  "AND3": 3, "OR3": 3}
        if self.kind not in counts or len(self.channels) != counts[self.kind] or (
            not isinstance(self.channels, tuple)
        ) or tuple(sorted(set(self.channels))) != self.channels or any(
            type(x) is not int or not 0 <= x < WIDTH for x in self.channels
        ):
            raise ValueError("Rule outside frozen classical hypothesis family")

    def predict(self, x):
        x = controls(x)
        sampled = (x[i] for i in self.channels)
        if self.kind == "BIT":
            return x[self.channels[0]]
        if self.kind.startswith("AND"):
            return int(all(sampled))
        if self.kind.startswith("OR"):
            return int(any(sampled))
        return x[self.channels[0]] ^ x[self.channels[1]]

    def packet(self):
        return {"operation": self.kind, "channels": list(self.channels)}


@lru_cache(maxsize=1)
def rule_library():
    proposals = [Rule("BIT", (i,)) for i in range(WIDTH)]
    pairs = tuple(combinations(range(WIDTH), 2))
    triples = tuple(combinations(range(WIDTH), 3))
    for kind in ("AND2", "OR2", "XOR2"):
        proposals.extend(Rule(kind, tuple(pair)) for pair in pairs)
    for kind in ("AND3", "OR3"):
        proposals.extend(Rule(kind, tuple(triple)) for triple in triples)
    return tuple(proposals)


@lru_cache(maxsize=5000)
def signature(x):
    x = controls(x)
    return tuple(rule.predict(x) for rule in rule_library())


@dataclass(frozen=True)
class Question:
    x: tuple[int, ...]
    unit_cost: int
    consequence_weight: int
    provenance: str = "SYNTHETIC_OWNER_QUESTION_CATALOG"

    def __post_init__(self):
        controls(self.x)
        if (type(self.unit_cost) is not int or self.unit_cost not in (1, 2)
                or type(self.consequence_weight) is not int
                or self.consequence_weight not in (1, 5)
                or self.provenance != "SYNTHETIC_OWNER_QUESTION_CATALOG"):
            raise ValueError("Bounded, source-owned query catalog required")

    def packet(self):
        return {"schema": "motif.law-forge.question.v1",
                "x": list(self.x), "unit_cost": self.unit_cost,
                "consequence_weight": self.consequence_weight,
                "provenance": self.provenance,
                "authority": "SYNTHETIC_OWNER_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, item):
        if (not isinstance(item, dict) or set(item) != {
            "schema", "x", "unit_cost", "consequence_weight", "provenance",
            "authority", "real_world_authority"
        } or item["schema"] != "motif.law-forge.question.v1"
                or item["authority"] != "SYNTHETIC_OWNER_ONLY"
                or item["real_world_authority"] is not False):
            raise ValueError("Invalid or privileged proposed experiment")
        return cls(controls(item["x"]), item["unit_cost"],
                   item["consequence_weight"], item["provenance"])


def fitted_indices(rows):
    observed = tuple(rows)
    chosen = []
    for idx, rule in enumerate(rule_library()):
        if all(rule.predict(x) == y for x, y in observed):
            chosen.append(idx)
    return tuple(chosen)


def choose_question(rows, pool, method, budget, used):
    if method not in ("motif_consequence", "classical_entropy", "classical_fixed"):
        raise ValueError("Unknown method for frozen experiment-selection policy")
    if type(budget) is not int or budget < 0:
        raise ValueError("Invalid inquiry budget")
    seen = {x for x, _ in rows} | set(used)
    available = tuple(q for q in pool if q.x not in seen and q.unit_cost <= budget)
    if not available:
        return None
    if method == "classical_fixed":
        return available[0]
    survivors = fitted_indices(rows)
    if len(survivors) < 2:
        return None
    best, best_score = None, -1
    for item in available:
        labels = signature(item.x)
        positive = sum(labels[index] for index in survivors)
        n = len(survivors)
        # Classical Gini/variance reduction, not a novel reasoning law.
        disagreement = positive * (n - positive)
        if disagreement == 0:
            continue
        risk = item.consequence_weight if method == "motif_consequence" else 1
        score = (disagreement * risk) / (n * n * item.unit_cost)
        if score > best_score + 1e-12:
            best, best_score = item, score
    return best


@dataclass(frozen=True)
class DecisionNode:
    feature: int | None
    left: "DecisionNode | None"
    right: "DecisionNode | None"
    value: int | None
    support: int

    def predict(self, x):
        if self.feature is None:
            return self.value if self.support >= 3 else None
        return (self.right if x[self.feature] else self.left).predict(x)


def decision_tree(rows, max_depth=5):
    """Strong classical CART-like greedy Gini splitter (no dependency)."""
    rows = tuple(rows)
    def gini(samples):
        if not samples:
            return 0
        p = sum(y for _, y in samples) / len(samples)
        return p * (1 - p)
    def build(samples, depth, remaining):
        all_y = {y for _, y in samples}
        if len(all_y) == 1 or not remaining or depth >= max_depth:
            return DecisionNode(None, None, None,
                                next(iter(all_y)) if len(all_y) == 1 else None,
                                len(samples))
        best = None
        best_gain = 0.0
        for bit in remaining:
            left = tuple(row for row in samples if row[0][bit] == 0)
            right = tuple(row for row in samples if row[0][bit] == 1)
            if not left or not right:
                continue
            cost = (len(left)*gini(left) + len(right)*gini(right)) / len(samples)
            gain = gini(samples) - cost
            if gain > best_gain + 1e-12:
                best = (bit, left, right)
                best_gain = gain
        if best is None:
            return DecisionNode(None, None, None, None, len(samples))
        bit, left, right = best
        rest = tuple(i for i in remaining if i != bit)
        return DecisionNode(bit, build(left, depth + 1, rest),
                            build(right, depth + 1, rest), None, len(samples))
    return build(rows, 0, tuple(range(WIDTH)))


@dataclass(frozen=True)
class PredictionDesk:
    contract: SourceContract
    snapshot: tuple[tuple[tuple[int, ...], int], ...]
    method: str
    candidates: tuple[int, ...] = ()
    tree: DecisionNode | None = None

    @property
    def id(self):
        return digest({"source": self.contract.packet(),
                       "rows": [[list(x), y] for x, y in self.snapshot],
                       "method": self.method, "version": LIBRARY_VERSION})

    def predict(self, x, contract):
        if not isinstance(contract, SourceContract) or contract.id != self.contract.id:
            return {"status": "HOLD_SOURCE_REVISION_CHANGED", "value": None}
        x = controls(x)
        known = dict(self.snapshot)
        if x in known:
            return {"status": "LOOKUP_WITNESSED", "value": known[x]}
        if self.method == "lookup_only":
            return {"status": "HOLD_UNOBSERVED", "value": None}
        if self.method == "classical_tree":
            prediction = self.tree.predict(x) if self.tree else None
            return {"status": ("TREE_PURE_LEAF" if prediction is not None
                               else "HOLD_UNCERTAIN_TREE"),
                    "value": prediction}
        if not self.candidates:
            return {"status": "HOLD_NO_CONSISTENT_RULE", "value": None}
        labels = signature(x)
        value = labels[self.candidates[0]]
        if any(labels[index] != value for index in self.candidates[1:]):
            return {"status": "HOLD_VERSION_SPACE_DISAGREEMENT", "value": None}
        return {"status": "HYPOTHESIS_CONSENSUS_UNSEEN", "value": value}


def make_desk(contract, observations, method):
    rows = exact_lookup(contract, observations)
    if method not in ("motif_consequence", "classical_entropy",
                      "classical_fixed", "classical_tree", "lookup_only"):
        raise ValueError("Unknown desk method")
    if method == "classical_tree":
        return PredictionDesk(contract, rows, method, tree=decision_tree(rows))
    if method == "lookup_only":
        return PredictionDesk(contract, rows, method)
    return PredictionDesk(contract, rows, method, fitted_indices(rows))


def review(desk, contract, readouts, minimum_coverage=16):
    if not isinstance(desk, PredictionDesk):
        return {"status": "HOLD_NO_REVIEWABLE_DESK", "covered": 0, "wrong": None}
    rows = tuple(readouts)
    if (len(rows) < 128 or len({r.x for r in rows}) != len(rows)
            or any(not isinstance(r, Observation) or
                   r.contract_id != contract.id for r in rows)):
        return {"status": "HOLD_REVIEW_COVERAGE", "covered": 0, "wrong": None}
    if desk.contract.id != contract.id:
        return {"status": "HOLD_SOURCE_REVISION_CHANGED", "covered": 0, "wrong": None}
    covered = incorrect = weighted_covered = weighted_incorrect = 0
    for row in rows:
        result = desk.predict(row.x, contract)
        if result["value"] is None:
            continue
        weight = consequence_weight(row.x)
        covered += 1
        weighted_covered += weight
        if result["value"] != row.y:
            incorrect += 1
            weighted_incorrect += weight
    status = ("HOLD_INDEPENDENT_FALSIFIER" if incorrect else
              "HOLD_INSUFFICIENT_REVIEW_COVERAGE"
              if covered < minimum_coverage else
              "ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW")
    return {"status": status, "covered": covered, "wrong": incorrect,
            "weighted_covered": weighted_covered,
            "weighted_wrong": weighted_incorrect}


def consequence_weight(x):
    x = controls(x)
    return 5 if x[0] == 1 and x[1] == 1 else 1


def question_cost(x):
    x = controls(x)
    return 2 if sum(x[:4]) == 4 else 1
