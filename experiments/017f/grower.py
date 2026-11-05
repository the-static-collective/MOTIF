"""MOTIF-017F: proposal-only question growth with independently witnessed admission.

A compositional query can be *proposed* from two allowed feature probes,
but cannot be executed until an independently reviewed provider offer exists.
A proposal/receipt is not authority, provenance authentication, or new physics.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from json import dumps
from math import isfinite
from pathlib import Path
from typing import Mapping, Sequence
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "016"))
from forest import Road  # noqa: E402


@dataclass(frozen=True)
class QuestionOffer:
    name: str
    components: tuple[str, str]
    provider: str
    price: float
    allowed: bool = True
    output_type: str = "PAIR_V1"
    scope: str = "SYNTHETIC_READ_ONLY"


@dataclass(frozen=True)
class QuestionProposal:
    offer: QuestionOffer
    candidate: Road
    source_component_names: tuple[str, str]
    digest: str
    status: str = "HOLD_UNREVIEWED"


@dataclass(frozen=True)
class IndependentReceipt:
    case_id: str
    known_world: str  # independent evaluator's adjudicated synthetic fixture
    declared_provider: str
    observed: str  # independently returned outcome, not read from prediction map
    charged_cost: float
    phase: str = "REVIEW"
    authenticated: bool = False  # synthetic fixtures never authenticate real people


@dataclass(frozen=True)
class Review:
    proposal_digest: str
    status: str
    reviewed: int
    counterexamples: tuple[str, ...]
    admissible_road: Road | None
    authority: str = "SYNTHETIC_PREDICTION_ONLY"


def _join(left: str, right: str) -> str:
    # Delimiter-safe deterministic composite rather than an ambiguous "a|bc".
    return dumps([left, right], separators=(",", ":"), ensure_ascii=False)


def draft_questions(
    hypotheses: Sequence[str],
    roads: Sequence[Road],
    offers: Sequence[QuestionOffer],
) -> tuple[QuestionProposal, ...]:
    """Generate typed question *expressions*, not new sensing capabilities.

    The price and ability to observe BOTH component probes must come from an
    offered provider contract. Nothing here turns an imaginary sensor into a
    deployed tool.
    """
    world_ids = tuple(hypotheses)
    if not world_ids or len(set(world_ids)) != len(world_ids):
        raise ValueError("World hypotheses must be unique and nonempty")
    by_name = {r.name: r for r in roads}
    if len(by_name) != len(roads):
        raise ValueError("Road names must be unique")
    proposals = []
    for offer in sorted(offers, key=lambda o: o.name):
        if (not offer.name or not offer.provider or not isfinite(offer.price)
                or offer.price < 0 or offer.output_type != "PAIR_V1"
                or len(offer.components) != 2 or offer.components[0] == offer.components[1]
                or offer.scope != "SYNTHETIC_READ_ONLY"):
            raise ValueError("Malformed contract")
        if offer.name in by_name or any(p.offer.name == offer.name for p in proposals):
            raise ValueError("Duplicate or existing question name")
        if any(c not in by_name for c in offer.components):
            raise ValueError("Unlicensed component; cannot fabricate a sensor")
        left, right = (by_name[c] for c in offer.components)
        if (not left.allowed or not right.allowed or left.requires or right.requires
                or set(left.predicted) != set(world_ids)
                or set(right.predicted) != set(world_ids)):
            raise ValueError("Both public component probes must be allowed and ungated")
        signals = {world: _join(left.predicted[world], right.predicted[world])
                   for world in world_ids}
        candidate = Road(offer.name, "ASK", offer.price, signals, offer.provider,
                         allowed=False, prompt="Proposed JOIN(" + ",".join(offer.components) + ")")
        fingerprint = {
            "offer": {
                "name": offer.name, "components": offer.components,
                "provider": offer.provider, "price": offer.price,
                "allowed": offer.allowed, "output_type": offer.output_type,
                "scope": offer.scope,
            },
            "hypothesis_signals": sorted(signals.items()),
            "status": "HOLD_UNREVIEWED",
        }
        digest = sha256(dumps(fingerprint, sort_keys=True).encode()).hexdigest()
        proposals.append(QuestionProposal(offer, candidate, offer.components, digest))
    return tuple(proposals)


def review_question(
    proposal: QuestionProposal,
    receipts: Sequence[IndependentReceipt],
    *,
    minimum_cases: int = 8,
) -> Review:
    """Separate locally adjudicated fixtures can admit a *synthetic* question.

    This checks exact independent receipts, not probabilistic calibration. It
    cannot detect hidden post-review drift. No automatic network authority.
    """
    if minimum_cases < 1:
        raise ValueError("Minimum review count must be positive")
    if not proposal.offer.allowed:
        return Review(proposal.digest, "HOLD_PERMISSION", 0, (), None)
    if len(receipts) < minimum_cases:
        return Review(proposal.digest, "HOLD_INSUFFICIENT_REVIEW", len(receipts), (), None)
    seen = set()
    failures = []
    covered = set()
    for receipt in receipts:
        if receipt.case_id in seen:
            failures.append("DUPLICATE_CASE:" + receipt.case_id)
        seen.add(receipt.case_id)
        if receipt.phase != "REVIEW":
            failures.append("UNAUTHORIZED_PHASE:" + receipt.case_id)
        if receipt.declared_provider != proposal.offer.provider:
            failures.append("SOURCE_MISMATCH:" + receipt.case_id)
        if receipt.known_world not in proposal.candidate.predicted:
            failures.append("UNKNOWN_WORLD:" + receipt.case_id)
        else:
            covered.add(receipt.known_world)
            if receipt.observed != proposal.candidate.predicted[receipt.known_world]:
                failures.append("COUNTEREXAMPLE:" + receipt.case_id)
        if (not isfinite(receipt.charged_cost)
                or abs(receipt.charged_cost - proposal.offer.price) > 1e-9):
            failures.append("COST_MISMATCH:" + receipt.case_id)
    # A provider may be perfect on a narrow subset but wrong elsewhere.
    if covered != set(proposal.candidate.predicted):
        failures.append("MISSING_STRUCTURAL_COVERAGE")
    if failures:
        return Review(proposal.digest, "REFUSE_INDEPENDENT_FALSIFICATION",
                      len(receipts), tuple(failures), None)
    admitted = Road(
        proposal.candidate.name, proposal.candidate.kind,
        proposal.candidate.cost, proposal.candidate.predicted,
        proposal.candidate.origin, allowed=True, prompt=proposal.candidate.prompt,
    )
    return Review(proposal.digest, "ELIGIBLE_SYNTHETIC_ONLY",
                  len(receipts), (), admitted)
