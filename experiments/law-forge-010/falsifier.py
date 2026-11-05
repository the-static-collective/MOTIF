"""LAW-FORGE-010 — THE BLIND FALSIFIER.

Distinguish a *learning question* from a post-identification *challenge
question*. When the classical Shannon version space in LAW-FORGE-009 reaches
one candidate, keep asking bounded source-owned questions which may refute it.

All policies are explicit classical methods. The critic generates simple
counterfactual **mutations of the remaining program**, not a new ontology.
No hidden owner rule, reviewer label, network endpoint, or live authority
enters this module. A failed hypothesis is recorded as a relative grammar gap
only when the witnessed evidence falsifies all 650 frozen source models.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-009"))
from entropy_cartridge import EntropyCartridge, Proposal as EntropyProposal
from gap import diagnose, independent_core_check
from learner import (Question, Observation, SourceContract, controls, digest,
                     fitted_indices, rule_library, signature, MAX_QUERIES)

LEARN_BUDGET = 12
AUDIT_BUDGET = 12
POLICIES = ("mutant_challenge", "classical_diversity", "classical_fixed",
            "classical_random", "no_audit")
REVIEW_STATUS = "SOURCE_ONLY_PROPOSE_NO_ADMISSION"


def hamming(a, b):
    a, b = controls(a), controls(b)
    return sum(x != y for x, y in zip(a, b))


@dataclass(frozen=True)
class Mutant:
    """Counterfactual challenger: selected rule XORs one simple Boolean term.

    Mutant alternatives are *not* part of the primary 650-rule learned
    hypothesis class and are *not* declared to be true. They exist to design
    discriminating tests for the remaining model.
    """
    atom_indices: tuple[int, ...]

    def __post_init__(self):
        if (not isinstance(self.atom_indices, tuple)
                or len(self.atom_indices) not in (1, 2, 3)
                or tuple(sorted(set(self.atom_indices))) != self.atom_indices
                or any(type(i) is not int or not 0 <= i < 12
                       for i in self.atom_indices)):
            raise ValueError("Only bounded deterministic XOR-of-AND mutations")

    def changes(self, x):
        x = controls(x)
        return int(all(x[i] for i in self.atom_indices))


def counterfactual_library():
    return tuple(Mutant(c) for width in (1, 2, 3)
                 for c in combinations(range(12), width))


def candidate_critics(cartridge):
    if not isinstance(cartridge, EntropyCartridge):
        raise ValueError("Only pinned entropy source evidence")
    if len(cartridge.survivor_indices) != 1:
        return ()
    model = rule_library()[cartridge.survivor_indices[0]]
    # All critic functions are proposed independently of hidden labels.
    critics = tuple(m for m in counterfactual_library()
                    if all((model.predict(x) ^ m.changes(x)) == y
                           for x, y in cartridge.snapshot))
    return critics


@dataclass(frozen=True)
class Challenge:
    card: Question
    policy: str
    source_evidence_digest: str
    champion_rule: dict
    surviving_mutants: int
    declared_score: float

    def __post_init__(self):
        if (not isinstance(self.card, Question) or self.policy not in POLICIES
                or not isinstance(self.source_evidence_digest, str)
                or len(self.source_evidence_digest) != 64
                or not isinstance(self.champion_rule, dict)
                or type(self.surviving_mutants) is not int
                or self.surviving_mutants < 0
                or not isinstance(self.declared_score, (int, float))
                or self.declared_score < 0):
            raise ValueError("Malformed bounded proposed challenge")

    def packet(self):
        return {
            "schema": "motif.law-forge.blind-falsifier-question.v1",
            "question": self.card.packet(),
            "method": self.policy,
            "source_evidence_digest": self.source_evidence_digest,
            "champion_rule": self.champion_rule,
            "surviving_counterfactual_mutants": self.surviving_mutants,
            "declared_score": round(self.declared_score, 9),
            "status": REVIEW_STATUS,
            "owner_must_execute": True,
            "real_world_authority": False
        }


def choose_challenge(cartridge, catalog, policy, budget, previously=()):
    if policy not in POLICIES:
        raise ValueError("Unregistered classical falsification policy")
    if policy == "no_audit":
        return None
    if (not isinstance(cartridge, EntropyCartridge)
            or type(budget) is not int or not 0 <= budget <= AUDIT_BUDGET
            or not isinstance(catalog, tuple) or len(catalog) > 160
            or any(not isinstance(q, Question) for q in catalog)
            or len(set(q.x for q in catalog)) != len(catalog)):
        raise ValueError("Owner-owned finite synthetic audit catalog required")
    # Important: never start this protocol from a *guess* when the frozen
    # learning language still contains two or more explanations.
    survivors = cartridge.survivor_indices
    if len(survivors) != 1:
        return None
    known = set(dict(cartridge.snapshot)) | set(previously)
    available = tuple(q for q in catalog
                      if q.x not in known and q.unit_cost <= budget)
    if not available:
        return None
    champion = rule_library()[survivors[0]]
    critics = candidate_critics(cartridge) if policy == "mutant_challenge" else ()
    best, best_score = None, -1.0
    for index, card in enumerate(available):
        if policy == "mutant_challenge" and critics:
            # A mutant surviving all observed cases is a *hypothetical*
            # alternative. Queries exposing more alternatives are attractive.
            score = sum(m.changes(card.x) for m in critics)
            score = score / (len(critics) * card.unit_cost)
        elif policy == "classical_diversity" or (
            policy == "mutant_challenge" and not critics
        ):
            # Strong classical space-filling challenger. Maximize minimum
            # Hamming distance to any witnessed graph configuration.
            score = min(hamming(card.x, x) for x, _ in cartridge.snapshot)
            score = score / card.unit_cost
        elif policy == "classical_random":
            # Reproducible pseudo-random ordering keyed ONLY by the source
            # contract, current evidence and card. Neither hidden truth nor
            # reviewer labels can influence the ordering.
            seed = int(digest({
                "source": cartridge.source.id,
                "evidence": cartridge.source_digest,
                "card": list(card.x)
            })[:12], 16)
            score = seed / (0xffffffffffff * card.unit_cost)
        else:
            # Source-catalog order as a strong simple fixed baseline.
            score = 1.0 / (index + 1)
        if score > best_score + 1e-12:
            best, best_score = card, score
    return Challenge(best, policy, cartridge.source_digest,
                     champion.packet(), len(critics), best_score)


@dataclass(frozen=True)
class AuditLedger:
    """Immutable separation of active identification and model challenge."""
    learning: EntropyCartridge
    audit: tuple[Observation, ...] = ()
    audit_spent: int = 0
    audit_policy: str = "mutant_challenge"

    def __post_init__(self):
        if (not isinstance(self.learning, EntropyCartridge)
                or self.learning.budget_spent > LEARN_BUDGET
                or not isinstance(self.audit, tuple)
                or len(self.audit) > AUDIT_BUDGET
                or type(self.audit_spent) is not int
                or not 0 <= self.audit_spent <= AUDIT_BUDGET
                or self.audit_policy not in POLICIES):
            raise ValueError("Sealed, bounded local challenge ledger")
        # Always uphold the inherited source contract/lookup integrity.
        self.evidence

    @property
    def evidence(self):
        observations = self.learning.observations + self.audit
        if len(observations) > MAX_QUERIES + 4:
            raise ValueError("Total source observations exceed 009 constraint")
        return EntropyCartridge(
            self.learning.source, observations,
            self.learning.budget_spent + self.audit_spent
        )

    @property
    def id(self):
        return "blind-falsifier-" + digest({
            "learn": self.learning.id,
            "source": self.evidence.source_digest,
            "audit_spent": self.audit_spent,
            "policy": self.audit_policy
        })[:24]

    def propose(self, catalog):
        return choose_challenge(self.evidence, tuple(catalog),
                                self.audit_policy,
                                AUDIT_BUDGET - self.audit_spent)

    def ingest(self, challenge, response, catalog):
        if (not isinstance(challenge, Challenge)
                or not isinstance(response, Observation)
                or challenge.policy != self.audit_policy
                or challenge.source_evidence_digest != self.evidence.source_digest
                or response.contract_id != self.learning.source.id
                or response.x != challenge.card.x
                or challenge.card not in tuple(catalog)
                or challenge.card.unit_cost + self.audit_spent > AUDIT_BUDGET):
            raise ValueError("Unfunded, unapproved or stale source challenge")
        # Require the deterministic *current* policy choice. Prohibits a
        # forged lower-cost/attacker-swapped question at the same source.
        if challenge != self.propose(catalog):
            raise ValueError("Proposed challenge was altered or superseded")
        if response.x in dict(self.evidence.snapshot):
            raise ValueError("Cannot replay a source answer")
        return AuditLedger(self.learning, self.audit + (response,),
                           self.audit_spent + challenge.card.unit_cost,
                           self.audit_policy)

    def diagnosis(self):
        gap = diagnose(self.evidence)
        if gap is not None and not independent_core_check(self.evidence, gap):
            raise AssertionError("Unverifiable claimed grammar-gap core")
        return gap

    def packet(self):
        gap = self.diagnosis()
        return {
            "schema": "motif.reason-cartridge.blind-falsifier.v1",
            "id": self.id,
            "learning_cartridge": self.learning.packet(),
            "audit_observations": [
                {"x": list(row.x), "y": row.y,
                 "contract_id": row.contract_id,
                 "provenance": row.provenance}
                for row in self.audit
            ],
            "audit_policy": self.audit_policy,
            "learning_cost_units": self.learning.budget_spent,
            "audit_cost_units": self.audit_spent,
            "audit_budget_units": AUDIT_BUDGET,
            "source_evidence_digest": self.evidence.source_digest,
            "surviving_frozen_hypotheses": len(self.evidence.survivor_indices),
            "relative_grammar_gap": gap.packet() if gap else None,
            "status": "HOLD_GRAMMAR_GAP" if gap else REVIEW_STATUS,
            "owner_must_execute": True,
            "real_world_authority": False
        }
