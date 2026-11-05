"""MOTIF-009 — Portable decision-tree cartridges for graph observations.

A cartridge is an inspectable 2-question Boolean classifier over MOTIF-008's
role-relative graph motifs; the learner chooses the questions from observed
synthetic outcomes. Its path may encode XOR, conjunction, or a joined relation.

Portable JSON is checksummed, NOT authenticated. Local receiver HOLDS by default;
review admits *read-only prediction only*, never physical execution, consent,
action dispatch, or an external authority. Python 3.10+ standard library.
"""
from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
import re

from learner import (Motif, FeatureSet, features, observed_outcome,
                     balanced_accuracy, candidate_features)

SCHEMA = "motif.decision-tree-cartridge.v0"
MAX_BYTES = 22000
MAX_VOCAB = 72
MAX_ATOMS = 50
SAFE = re.compile(r"^[A-Za-z0-9_?.:-]{1,96}$")


class HOLD(ValueError):
    pass


def checksum(body):
    # Preserve cross-language JSON numeric equivalence for this schema:
    # JavaScript JSON.stringify(1.0) produces 1, whereas Python emits 1.0.
    # Canonicalize the sole fractional statistic back to float before hashing.
    # This remains a CONTENT checksum, never a signature or identity proof.
    if isinstance(body, dict) and "fit_balanced" in body:
        body = dict(body, fit_balanced=float(body["fit_balanced"]))
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode("utf-8")).hexdigest()


def vocabulary(episodes) -> tuple[str, ...]:
    """The recipient must explicitly review a local vocabulary adaptation."""
    return tuple(sorted({fact[0] for ep in episodes for fact in ep.before}))


def motif_to_json(value: Motif):
    return [list(f) for f in value]


def motif_from_json(value):
    if not isinstance(value, list) or not (0 <= len(value) <= 2):
        raise HOLD("Invalid motif length")
    rows = []
    for fact in value:
        if not isinstance(fact, list) or not (2 <= len(fact) <= 3):
            raise HOLD("Invalid motif arity")
        if any(not isinstance(x, str) or not SAFE.fullmatch(x) for x in fact):
            raise HOLD("Invalid symbolic token")
        rows.append(tuple(fact))
    if len(set(rows)) != len(rows):
        raise HOLD("Repeated motif facts")
    return tuple(sorted(rows))


@dataclass(frozen=True)
class Cartridge:
    id: str
    schema: str
    vocab: tuple[str, ...]
    first: Motif
    second: Motif
    leaves: tuple[bool, bool, bool, bool]
    counts: tuple[tuple[int, int], ...]  # negative, positive for each leaf
    fit_balanced: float
    evidence_count: int
    source_digest: str
    status: str = "PROPOSAL_ONLY"

    def leaf(self, row: FeatureSet) -> int:
        return 2 * int(self.first in row) + int(self.second in row)

    def predict(self, row: FeatureSet) -> bool:
        return self.leaves[self.leaf(row)]

    def probability(self, row: FeatureSet) -> float:
        neg, pos = self.counts[self.leaf(row)]
        return (pos + 1) / (neg + pos + 2)  # heuristic, NOT calibrated

    def explain(self, row: FeatureSet) -> dict:
        leaf = self.leaf(row)
        return {
            "first_present": self.first in row,
            "second_present": self.second in row,
            "leaf_index": leaf,
            "training_counts": self.counts[leaf],
            "hypothesis": self.leaves[leaf],
            "heuristic_probability": round(self.probability(row), 5),
            "real_world_authority": False,
        }


def _body(car: Cartridge):
    return {
        "schema": car.schema, "id": car.id,
        "vocab": list(car.vocab), "first": motif_to_json(car.first),
        "second": motif_to_json(car.second),
        "leaves": list(car.leaves),
        "counts": [list(x) for x in car.counts],
        "fit_balanced": car.fit_balanced,
        "evidence_count": car.evidence_count,
        "source_digest": car.source_digest,
        "status": car.status,
    }


def export_cartridge(car: Cartridge) -> str:
    raw = json.dumps(dict(_body(car), checksum_sha256=checksum(_body(car))),
                     indent=2, sort_keys=True) + "\n"
    if len(raw.encode()) > MAX_BYTES:
        raise HOLD("Oversized cartridge")
    validate_cartridge(raw)
    return raw


def validate_cartridge(raw: str) -> Cartridge:
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Oversized or invalid cartridge")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Invalid JSON") from exc
    fields = {"schema", "id", "vocab", "first", "second", "leaves",
              "counts", "fit_balanced", "evidence_count", "source_digest",
              "status", "checksum_sha256"}
    if not isinstance(obj, dict) or set(obj) != fields:
        raise HOLD("Unrecognized cartridge fields")
    if obj["schema"] != SCHEMA or obj["status"] != "PROPOSAL_ONLY":
        raise HOLD("Unsupported cartridge schema/status")
    body = {k: v for k, v in obj.items() if k != "checksum_sha256"}
    if obj["checksum_sha256"] != checksum(body):
        raise HOLD("Checksum mismatch (not a proof of author)")
    vocab = obj["vocab"]
    if (not isinstance(vocab, list) or len(vocab) > MAX_VOCAB or
            any(not isinstance(x, str) or not SAFE.fullmatch(x) for x in vocab)
            or vocab != sorted(set(vocab))):
        raise HOLD("Invalid vocabulary")
    a, b = motif_from_json(obj["first"]), motif_from_json(obj["second"])
    if any(f[0] not in vocab for motif in (a,b) for f in motif):
        raise HOLD("Motif uses unknown relation")
    leaves = obj["leaves"]
    if not isinstance(leaves, list) or len(leaves) != 4 or any(
            type(x) is not bool for x in leaves):
        raise HOLD("Invalid Boolean leaves")
    counts = obj["counts"]
    if not isinstance(counts, list) or len(counts) != 4 or any(
        not isinstance(x, list) or len(x) != 2 or
        any(type(v) is not int or v < 0 or v > 100000 for v in x)
        for x in counts):
        raise HOLD("Invalid leaf evidence counts")
    n = obj["evidence_count"]
    if type(n) is not int or not 1 <= n <= 100000 or sum(
            sum(pair) for pair in counts) != n:
        raise HOLD("Evidence counts inconsistent")
    fit = obj["fit_balanced"]
    if type(fit) not in (int, float) or not 0 <= fit <= 1:
        raise HOLD("Invalid fit statistic")
    evidence_hash = obj["source_digest"]
    if not isinstance(evidence_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", evidence_hash):
        raise HOLD("Invalid evidence fingerprint")
    ident = obj["id"]
    expected = "tree-" + checksum({k: body[k] for k in body if k != "id"})[:16]
    if ident != expected:
        raise HOLD("Cartridge ID does not match its declared semantics")
    return Cartridge(ident, SCHEMA, tuple(vocab), a, b, tuple(leaves),
                     tuple(tuple(x) for x in counts), float(fit), n,
                     evidence_hash)


def _vote(groups, fallback) -> tuple[bool, bool, bool, bool]:
    return tuple(sum(group) > len(group) / 2 if group else fallback
                 for group in groups)


def fit_cartridge(episodes, cap=MAX_ATOMS) -> Cartridge:
    """Read-only trained decision-tree *cartridge* from observed graph changes.

    Select the best of <= cap²/2 pair tests on **training alone**. No heldout
    labels or oracle-rule code are consulted. In-sample fit is not validation.
    """
    episodes = tuple(episodes)
    if not episodes or len(episodes) > 100000:
        raise ValueError("Need bounded observed episodes")
    corpus = tuple((features(x.before, x.roles), observed_outcome(x))
                   for x in episodes)
    labels = tuple(y for _, y in corpus)
    observed_vocabulary = vocabulary(episodes)
    atoms, _ = candidate_features(corpus, max_features=cap)
    # For too-few observations, use an honest majority-only cartridge.
    fallback = sum(labels) > len(labels) / 2
    if not atoms or not any(labels) or all(labels):
        pair_options = [((), ())]
    else:
        pair_options = [(a, b) for i, a in enumerate(atoms)
                        for b in atoms[i:]]
    best_key = None
    selected = None
    for first, second in pair_options:
        groups = [[] for _ in range(4)]
        for row, y in corpus:
            groups[2 * int(first in row) + int(second in row)].append(y)
        leaves = _vote(groups, fallback)
        if 0 < sum(labels) < len(labels):
            metric = balanced_accuracy(labels, (leaves[
                2 * int(first in row) + int(second in row)]
                for row, _ in corpus))
        else:
            metric = 0.5  # both classes absent; fit not meaningful
        complexity = len(first) + len(second)
        key = (round(metric, 8), -complexity, -int(first != second))
        if best_key is None or key > best_key:
            best_key = key
            selected = first, second, leaves, tuple(
                (len(group) - sum(group), sum(group)) for group in groups), metric
    first, second, leaves, counts, metric = selected
    # No raw before/after graphs or entity names in a portable cartridge.
    # Source fingerprint identifies a derivation, but isn't a signature.
    evidence = checksum(sorted((sorted(tuple(
        tuple(token for token in fact) for atom in row for fact in atom)),
        int(y)) for row, y in corpus))
    fields = dict(schema=SCHEMA, vocab=list(observed_vocabulary),
                  first=motif_to_json(first), second=motif_to_json(second),
                  leaves=list(leaves), counts=[list(x) for x in counts],
                  fit_balanced=round(metric, 6), evidence_count=len(episodes),
                  source_digest=evidence, status="PROPOSAL_ONLY")
    ident = "tree-" + checksum(fields)[:16]
    return Cartridge(ident, SCHEMA, observed_vocabulary, first, second,
                     leaves, counts, round(metric, 6), len(episodes), evidence)


class CartridgeBay:
    """Local HOLD/REFUSE/ADMIT for classifier predictions only.

    Reviewer labels are UNSIGNED synthetic fixture text. No physical action
    or authentication is possible via this experimental class.
    """

    def __init__(self):
        self.pending: dict[str, Cartridge] = {}
        self.admitted: dict[str, Cartridge] = {}
        self.reviews: list[dict] = []

    def offer(self, raw: str) -> str:
        car = validate_cartridge(raw)
        self.pending[car.id] = car
        return car.id

    def review(self, identifier: str, decision: str, reviewer: str,
               local_observations=(), min_balanced=0.65):
        if identifier not in self.pending:
            raise HOLD("No pending cartridge")
        if decision not in ("ADMIT_PREDICT_ONLY", "REFUSE"):
            raise HOLD("Invalid local decision")
        if not isinstance(reviewer, str) or not SAFE.fullmatch(reviewer):
            raise HOLD("Unverified local reviewer label required")
        car = self.pending[identifier]
        if decision == "ADMIT_PREDICT_ONLY":
            observations = tuple(local_observations)
            if len(observations) < 8 or vocabulary(observations) != car.vocab:
                raise HOLD("Insufficient or incompatible local evidence/vocabulary")
            labels = tuple(observed_outcome(x) for x in observations)
            if len(set(labels)) != 2:
                raise HOLD("Local evidence lacks contrasting outcomes")
            guesses = [car.predict(features(x.before, x.roles))
                       for x in observations]
            metric = balanced_accuracy(labels, guesses)
            if metric < min_balanced:
                raise HOLD("Local predictive evidence does not support admission")
            self.admitted[identifier] = car
        else:
            self.admitted.pop(identifier, None)
            metric = None
        receipt = dict(cartridge=identifier, decision=decision,
                       reviewer_claim=reviewer, local_score=metric,
                       real_world_authority=False)
        self.reviews.append(receipt)
        return receipt

    def predict_admitted(self, identifier, before, roles):
        if identifier not in self.admitted:
            raise HOLD("Cartridge not locally admitted")
        car = self.admitted[identifier]
        present = {f[0] for f in before}
        # Closed-world Boolean feature semantics: a port relation may be absent
        # because its value is FALSE. Requiring EVERY vocabulary item to be
        # present incorrectly refused valid negative examples.
        expected_structure = {"role_actor", "role_target", "pending"}
        if (not present.issubset(car.vocab)
                or not expected_structure.issubset(present)):
            raise HOLD("Current graph uses unreviewed or incomplete schema")
        return car.explain(features(before, roles))

    def revoke(self, identifier, reviewer):
        return self.review(identifier, "REFUSE", reviewer)
