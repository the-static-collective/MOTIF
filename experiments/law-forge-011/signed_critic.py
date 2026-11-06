"""LAW-FORGE-011 — SIGNED COUNTERFACTUAL CHALLENGER.

First genuinely non-vacuous critic from the 010 failure. A bounded mutant
is the surviving 009 model XOR an AND of *positive and negative* bit
literals. Each such term is FALSE on both the all-zero and all-one anchors,
so the original 010 degeneracy cannot automatically eliminate it.

This is classical Boolean hypothesis testing, not new mathematics. The
counterfactual terms are never silently admitted to the learned grammar;
their sole job is to select a source-owned falsification question.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

sys.path.extend((str(Path(__file__).resolve().parents[1] / "law-forge-010"),
                 str(Path(__file__).resolve().parents[1] / "law-forge-009")))
from entropy_cartridge import EntropyCartridge
from gap import diagnose, independent_core_check
from falsifier import LEARN_BUDGET, AUDIT_BUDGET, hamming
from learner import (
    Observation, Question, SourceContract, controls, digest, rule_library,
)

WIDTH = 12
POLICIES = ("signed_counterfactual", "classical_diversity",
            "classical_boundary", "classical_fixed",
            "classical_seeded_random", "no_audit")
SCHEMA = "motif.reason-cartridge.signed-falsifier.v1"
AUTHORITY = "PROPOSE_SOURCE_OWNED_AUDIT_ONLY"


def bits(x):
    x = controls(x)
    return sum(int(bit) << i for i, bit in enumerate(x))


@dataclass(frozen=True)
class SignedTerm:
    positive: tuple[int, ...]
    negative: tuple[int, ...]

    def __post_init__(self):
        if (not isinstance(self.positive, tuple)
                or not isinstance(self.negative, tuple)
                or not self.positive or not self.negative
                or tuple(sorted(set(self.positive))) != self.positive
                or tuple(sorted(set(self.negative))) != self.negative
                or set(self.positive) & set(self.negative)
                or len(self.positive) + len(self.negative) not in (2, 3)
                or any(type(i) is not int or not 0 <= i < WIDTH
                       for i in self.positive + self.negative)):
            raise ValueError("Only 2–3 signed distinct Boolean literals")

    @property
    def p_mask(self):
        return sum(1 << i for i in self.positive)

    @property
    def n_mask(self):
        return sum(1 << i for i in self.negative)

    def fires(self, x):
        x = bits(x) if not isinstance(x, int) else x
        return ((x & self.p_mask) == self.p_mask and
                (x & self.n_mask) == 0)

    def packet(self):
        return {"positive": list(self.positive),
                "negative": list(self.negative)}


@lru_cache(maxsize=1)
def signed_library():
    terms = []
    for width in (2, 3):
        for positions in combinations(range(WIDTH), width):
            for positives in range(1, (1 << width)-1):
                pos = tuple(p for i, p in enumerate(positions)
                            if positives & (1 << i))
                neg = tuple(p for i, p in enumerate(positions)
                            if not positives & (1 << i))
                terms.append(SignedTerm(pos, neg))
    return tuple(terms)


def surviving_critics(cartridge):
    """Only defined once a single frozen program fits all source evidence."""
    if not isinstance(cartridge, EntropyCartridge):
        raise ValueError("Need original source-owned entropy cartridge")
    if len(cartridge.survivor_indices) != 1:
        return ()
    # The one remaining champion already matches every witnessed outcome.
    # Its XOR-signed-term mutant matches exactly when term never fires.
    witnessed = tuple(bits(x) for x, _ in cartridge.snapshot)
    return tuple(term for term in signed_library()
                 if not any(term.fires(x) for x in witnessed))


@dataclass(frozen=True)
class CounterfactualQuestion:
    card: Question
    policy: str
    source_digest: str
    champion: dict
    active_critics: int
    score: float

    def packet(self):
        return {"schema": "motif.reason-cartridge.signed-question.v1",
                "question": self.card.packet(),
                "policy": self.policy,
                "source_evidence_digest": self.source_digest,
                "champion": self.champion,
                "surviving_signed_counterfactuals": self.active_critics,
                "selection_score": round(self.score, 9),
                "status": AUTHORITY,
                "owner_must_execute": True,
                "real_world_authority": False}


def question(cartridge, catalog, policy, remaining_cost):
    if policy not in POLICIES:
        raise ValueError("Unregistered audit method")
    if (not isinstance(cartridge, EntropyCartridge)
            or type(remaining_cost) is not int
            or not 0 <= remaining_cost <= AUDIT_BUDGET
            or not isinstance(catalog, tuple)
            or len(catalog) > 192
            or any(not isinstance(q, Question) for q in catalog)
            or len(set(q.x for q in catalog)) != len(catalog)):
        raise ValueError("Bounded typed owner catalog and budget required")
    if policy == "no_audit" or len(cartridge.survivor_indices) != 1:
        return None
    known = set(dict(cartridge.snapshot))
    cards = tuple(q for q in catalog
                  if q.x not in known and q.unit_cost <= remaining_cost)
    if not cards:
        return None

    signed = surviving_critics(cartridge) if policy == "signed_counterfactual" else ()
    champion = rule_library()[cartridge.survivor_indices[0]]
    measured = tuple(bits(x) for x, _ in cartridge.snapshot)

    best, value = None, -1.0
    for index, card in enumerate(cards):
        mask = bits(card.x)
        if policy == "signed_counterfactual" and signed:
            score = sum(term.fires(mask) for term in signed) / (
                len(signed) * card.unit_cost)
        elif policy in ("classical_diversity", "signed_counterfactual"):
            score = min((mask ^ earlier).bit_count()
                        for earlier in measured) / card.unit_cost
        elif policy == "classical_boundary":
            # Conventional minimum-distance boundary challenge; the
            # opposite of space-filling diversity, with explicit cost.
            score = 1.0 / (1 + min((mask ^ earlier).bit_count()
                                  for earlier in measured))
            score /= card.unit_cost
        elif policy == "classical_seeded_random":
            score = int(digest({
                "contract": cartridge.source.id,
                "evidence": cartridge.source_digest,
                "configuration": list(card.x)
            })[:12], 16) / (0xffffffffffff * card.unit_cost)
        else:
            score = 1.0 / (index+1)
        if score > value + 1e-12:
            best, value = card, score
    return CounterfactualQuestion(
        best, policy, cartridge.source_digest, champion.packet(),
        len(signed), value
    )


@dataclass(frozen=True)
class SignedAudit:
    learning: EntropyCartridge
    policy: str = "signed_counterfactual"
    audit: tuple[Observation, ...] = ()
    audit_spent: int = 0

    def __post_init__(self):
        if (not isinstance(self.learning, EntropyCartridge)
                or self.policy not in POLICIES
                or self.learning.budget_spent > LEARN_BUDGET
                or not isinstance(self.audit, tuple)
                or type(self.audit_spent) is not int
                or not 0 <= self.audit_spent <= AUDIT_BUDGET
                or len(self.audit) > self.audit_spent):
            raise ValueError("Bounded immutable source-owned audit")
        self.evidence

    @property
    def evidence(self):
        return EntropyCartridge(
            self.learning.source, self.learning.observations + self.audit,
            self.learning.budget_spent + self.audit_spent
        )

    @property
    def id(self):
        return "signed-" + digest({
            "learning": self.learning.id, "audit": self.evidence.source_digest,
            "spent": self.audit_spent, "policy": self.policy})[:24]

    def propose(self, catalog):
        return question(self.evidence, tuple(catalog), self.policy,
                        AUDIT_BUDGET - self.audit_spent)

    def ingest(self, candidate, observed, catalog):
        if (not isinstance(candidate, CounterfactualQuestion)
                or not isinstance(observed, Observation)
                or candidate != self.propose(catalog)
                or observed.contract_id != self.learning.source.id
                or observed.x != candidate.card.x
                or candidate.card not in tuple(catalog)
                or self.audit_spent + candidate.card.unit_cost > AUDIT_BUDGET
                or observed.x in dict(self.evidence.snapshot)):
            raise ValueError("Unapproved, stale or repeated source evidence")
        return SignedAudit(self.learning, self.policy,
                           self.audit + (observed,),
                           self.audit_spent + candidate.card.unit_cost)

    def grammar_gap(self):
        packet = diagnose(self.evidence)
        if packet and not independent_core_check(self.evidence, packet):
            raise AssertionError("Uncheckable source grammar contradiction")
        return packet

    def packet(self):
        gap = self.grammar_gap()
        return {
            "schema": SCHEMA, "id": self.id,
            "learning_cartridge": self.learning.packet(),
            "policy": self.policy,
            "audit_observations": [
                {"x": list(r.x), "y": r.y,
                 "contract_id": r.contract_id, "provenance": r.provenance}
                for r in self.audit
            ],
            "audit_spent": self.audit_spent,
            "learning_budget": LEARN_BUDGET,
            "audit_budget": AUDIT_BUDGET,
            "source_digest": self.evidence.source_digest,
            "survivors": len(self.evidence.survivor_indices),
            "witnessed_relative_grammar_gap": gap.packet() if gap else None,
            "status": "HOLD_GRAMMAR_GAP" if gap else AUTHORITY,
            "owner_must_execute": True, "real_world_authority": False
        }

    @classmethod
    def from_packet(cls, data):
        if (not isinstance(data, dict) or set(data) != {
            "schema","id","learning_cartridge","policy","audit_observations",
            "audit_spent","learning_budget","audit_budget","source_digest",
            "survivors","witnessed_relative_grammar_gap","status",
            "owner_must_execute","real_world_authority"
        } or data["schema"] != SCHEMA
                or data["owner_must_execute"] is not True
                or data["real_world_authority"] is not False
                or data["learning_budget"] != LEARN_BUDGET
                or data["audit_budget"] != AUDIT_BUDGET
                or not isinstance(data["audit_observations"], list)):
            raise ValueError("Invalid signed critique cartridge schema")
        prior = EntropyCartridge.from_packet(data["learning_cartridge"])
        rows = []
        for r in data["audit_observations"]:
            if (not isinstance(r, dict) or set(r) != {
                "x", "y", "contract_id", "provenance"
            } or not isinstance(r["x"], list)):
                raise ValueError("Malformed source audit evidence")
            rows.append(Observation(tuple(r["x"]), r["y"],
                                    r["contract_id"], r["provenance"]))
        if (type(data["audit_spent"]) is not int or
                not len(rows) <= data["audit_spent"] <= 2*len(rows)
                or len(set(r.x for r in rows)) != len(rows)
                or set(r.x for r in rows) & set(dict(prior.snapshot))):
            raise ValueError("Tampered cost or duplicate source evidence")
        model = cls(prior, data["policy"], tuple(rows), data["audit_spent"])
        if model.packet() != data:
            raise ValueError("Tampered source snapshot, grammar, or status")
        return model
