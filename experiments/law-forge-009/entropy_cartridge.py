"""LAW-FORGE-009: portable classical Shannon-entropy active-learning cartridge.

Real classical technique, deliberately *assimilated* rather than claimed as
novel. This module imports the existing frozen 008 version space and exact
lookup. It does NOT import a hidden world, authorize probes, or inspect labels
outside its witnessed records.

A cartridge proposes a source-owned membership question. Its owner must
execute it; a future typed observation may update a NEW immutable cartridge.
A full snapshot is retained; never replace a measured fact with a hypothesis.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import log2
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-008"))
from learner import (
    WIDTH, DOMAIN, LIBRARY_VERSION, MAX_QUERIES,
    Observation, Question, SourceContract, controls, digest,
    exact_lookup, fitted_indices, rule_library, signature,
    make_desk,
)

SCHEMA = "motif.reason-cartridge.shannon-entropy.v1"
POLICY = "SHANNON_ENTROPY_PER_DECLARED_COST"
STATUS = "PROPOSE_ONLY_NOT_SOURCE_AUTHENTICATED"


def hypothesis_digest():
    return digest({"library": LIBRARY_VERSION,
                   "programs": [rule.packet() for rule in rule_library()]})


def shannon(p):
    if not (isinstance(p, (int, float)) and 0 <= p <= 1):
        raise ValueError("Invalid binary ensemble frequency")
    if p in (0, 1):
        return 0.0
    return -p * log2(p) - (1-p) * log2(1-p)


@dataclass(frozen=True)
class Proposal:
    card: Question
    entropy_bits: float
    information_per_cost: float
    surviving_hypotheses: int
    supporting_evidence: str

    def packet(self):
        return {"schema": "motif.reason-cartridge.question-proposal.v1",
                "question": self.card.packet(),
                "entropy_bits": round(self.entropy_bits, 9),
                "score_per_cost": round(self.information_per_cost, 9),
                "surviving_hypotheses": self.surviving_hypotheses,
                "supporting_evidence": self.supporting_evidence,
                "status": STATUS,
                "owner_must_execute": True,
                "real_world_authority": False}


@dataclass(frozen=True)
class EntropyCartridge:
    source: SourceContract
    observations: tuple[Observation, ...]
    budget_spent: int = 0

    def __post_init__(self):
        if not isinstance(self.source, SourceContract):
            raise ValueError("A typed source contract is required")
        if (not isinstance(self.observations, tuple) or
                len(self.observations) < 1 or
                len(self.observations) > MAX_QUERIES + 4 or
                type(self.budget_spent) is not int or not (
                    0 <= self.budget_spent <= MAX_QUERIES
                )):
            raise ValueError("Finite immutable evidence and budget required")
        # Also rejects foreign/contradictory witnesses (but not identity fraud).
        exact_lookup(self.source, self.observations)

    @property
    def snapshot(self):
        return exact_lookup(self.source, self.observations)

    @property
    def source_digest(self):
        return digest({"contract": self.source.packet(),
                       "observations": [[list(x), y] for x, y in self.snapshot]})

    @property
    def survivor_indices(self):
        return fitted_indices(self.snapshot)

    @property
    def id(self):
        return "entropy-" + digest({"evidence": self.source_digest,
                                    "spent": self.budget_spent,
                                    "rules": hypothesis_digest(),
                                    "policy": POLICY})[:24]

    def propose(self, catalog, remaining_budget=None):
        """Real Shannon expected information gain over a uniform finite
        version space, divided by owner-declared query cost.

        Uniformity here is over surviving *programs*, not a validated
        probability distribution over actual natural mechanisms.
        """
        if remaining_budget is None:
            remaining_budget = MAX_QUERIES - self.budget_spent
        if (type(remaining_budget) is not int or remaining_budget < 0 or
                remaining_budget > MAX_QUERIES - self.budget_spent):
            raise ValueError("Membership-query budget exceeded")
        cards = tuple(catalog)
        if len(cards) > 160 or any(not isinstance(c, Question) for c in cards):
            raise ValueError("Only bounded source-owned query cards")
        if len({c.x for c in cards}) != len(cards):
            raise ValueError("Duplicate entries in owner question catalog")
        indices = self.survivor_indices
        if len(indices) < 2:
            return None
        known = set(dict(self.snapshot))
        result, best = None, -1.0
        for card in cards:
            if card.x in known or card.unit_cost > remaining_budget:
                continue
            labels = signature(card.x)
            positive = sum(labels[i] for i in indices)
            entropy = shannon(positive / len(indices))
            if entropy == 0:
                continue
            benefit = entropy / card.unit_cost
            if benefit > best + 1e-12:
                result = Proposal(card, entropy, benefit, len(indices),
                                  self.source_digest)
                best = benefit
        return result

    def ingest(self, proposal, observed, catalog):
        """Immutable new evidence. Does not certify real owner signatures.
        Recheck the proposed card against the present owner catalog and
        require the returned controls to match the requested controls.
        """
        if (not isinstance(proposal, Proposal) or
                not isinstance(observed, Observation) or
                observed.contract_id != self.source.id or
                observed.x != proposal.card.x or
                proposal.supporting_evidence != self.source_digest or
                proposal.card not in tuple(catalog)):
            raise ValueError("Foreign, stale or unapproved source response")
        if self.budget_spent + proposal.card.unit_cost > MAX_QUERIES:
            raise ValueError("Source budget exceeded")
        if observed.x in dict(self.snapshot):
            raise ValueError("Repeated source response cannot add evidence")
        return EntropyCartridge(self.source, self.observations + (observed,),
                                self.budget_spent + proposal.card.unit_cost)

    def predict(self, x, present_source):
        if (not isinstance(present_source, SourceContract) or
                present_source.id != self.source.id):
            return {"status": "HOLD_CHANGED_SOURCE_CONTRACT",
                    "value": None}
        # Use the actual 008 exact-first conservative prediction algorithm.
        frozen = _frozen_desk(self)
        result = frozen.predict(controls(x), present_source)
        return {**result, "cartridge_id": self.id,
                "real_world_authority": False}

    def packet(self):
        return {"schema": SCHEMA, "id": self.id,
                "source": self.source.packet(),
                "hypothesis_language_digest": hypothesis_digest(),
                "policy": POLICY, "library_version": LIBRARY_VERSION,
                "observations": [
                    {"x": list(row.x), "y": row.y,
                     "contract_id": row.contract_id,
                     "provenance": row.provenance}
                    for row in self.observations
                ],
                "evidence_digest": self.source_digest,
                "budget_spent": self.budget_spent,
                "max_budget": MAX_QUERIES,
                "status": STATUS, "owner_must_execute": True,
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, item):
        if (not isinstance(item, dict) or set(item) != {
            "schema", "id", "source", "hypothesis_language_digest",
            "policy", "library_version", "observations",
            "evidence_digest", "budget_spent", "max_budget", "status",
            "owner_must_execute", "real_world_authority"
        } or item["schema"] != SCHEMA or item["policy"] != POLICY or
                item["library_version"] != LIBRARY_VERSION or
                item["hypothesis_language_digest"] != hypothesis_digest() or
                item["status"] != STATUS or
                item["owner_must_execute"] is not True or
                item["real_world_authority"] is not False or
                type(item["max_budget"]) is not int or
                item["max_budget"] != MAX_QUERIES or
                not isinstance(item["observations"], list)):
            raise ValueError("Modified or privileged entropy cartridge")
        source = SourceContract.from_packet(item["source"])
        evidence = []
        for row in item["observations"]:
            if (not isinstance(row, dict) or set(row) != {
                "x", "y", "contract_id", "provenance"
            } or not isinstance(row["x"], list)):
                raise ValueError("Malformed synthetic evidence")
            evidence.append(Observation(tuple(row["x"]), row["y"],
                                        row["contract_id"], row["provenance"]))
        skill = cls(source, tuple(evidence), item["budget_spent"])
        if skill.id != item["id"] or skill.source_digest != item["evidence_digest"]:
            raise ValueError("Evidence, digest or query budget tampered")
        return skill


@lru_cache(maxsize=1024)
def _frozen_desk(cartridge):
    # A single immutable source snapshot maps to one fixed classical model.
    return make_desk(cartridge.source, cartridge.observations,
                     "classical_entropy")
