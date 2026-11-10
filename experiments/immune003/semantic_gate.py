"""IMMUNE-003R: conservative *role-aware* evidence admission on public BIPIA email QA.

Post-hoc engineering response to source-only false promotions. A quote that
contains $20 and is in the primary email is NOT evidence that $20 was *paid
to the named recipient*. This module adds a narrow, inspectable template for
*some* outgoing payments. It is NOT a general NLP parser, signed source, or
proof of real financial semantics; unrecognized claims HOLD.

IMPORTANT: This is a read-only evidence filter. Gold BIPIA labels, the attack
message, and prior model answers are never inputs to the admission function.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import re

from epistemic import MONEY, check_provenance, money_values

PAID = re.compile(r"\bpaid\s+(to|by)\s+([^?]+)\?", re.IGNORECASE)
OUTGOING = re.compile(
    r"\b(?:charged|preauthorized|paid|debited|billed|withdrawn)\b",
    re.IGNORECASE,
)
INBOUND = re.compile(
    r"\b(?:received|credited|incoming)\b|\bach\s+in\b",
    re.IGNORECASE,
)
# This intentionally does not treat a mention of "to [entity]" anywhere
# in a document as a verified payment to that entity.
PAYEE_MARKERS = ("by", "to", "at")


@dataclass(frozen=True)
class RelationCertificate:
    status: str
    named_party: str | None
    direction: str | None
    admitted_amount: str | None
    source_sha256: str
    rule: str | None
    exact_quote_in_primary: bool
    general_semantic_truth_proven: bool = False


def _named_question(question: str) -> tuple[str, str] | None:
    if type(question) is not str or len(question) > 500:
        return None
    match = PAID.search(question)
    if not match:
        return None
    direction, named = match.group(1).lower(), match.group(2).strip()
    if not named or len(named) > 90 or not re.fullmatch(
            r"[\w .,&'-]+", named, flags=re.UNICODE):
        return None
    return direction, named


def _name_pattern(name: str) -> re.Pattern:
    # Source-oriented literal match (never evaluate user-supplied regex).
    return re.compile(r"(?<!\w)" + re.escape(name).replace(r"\ ", r"\s+")
                      + r"(?!\w)", re.IGNORECASE)


def check_relation(question: str, answer: str,
                   evidence: str, primary_email: str) -> RelationCertificate:
    """Return an *epistemic admission label*, never an unconditional fact.

    The small algorithm only recognizes a few local 'charged ... by X'
    patterns. An inbound payment is explicitly distinguishable from an
    outgoing payment; an unrelated amount without X is not a proof.
    Unknown is always abstention, not proof of absence.
    """
    if any(type(x) is not str for x in
           (question, answer, evidence, primary_email)):
        return RelationCertificate("HOLD_MALFORMED", None, None, None,
                                   "", None, False)
    digest = sha256(primary_email.encode("utf-8")).hexdigest()
    parsed = _named_question(question)
    if parsed is None:
        return RelationCertificate("HOLD_UNSUPPORTED_QUESTION", None, None, None,
                                   digest, None, False)
    direction, entity = parsed
    if answer.strip().lower() == "unknown":
        return RelationCertificate("ABSTAIN_UNVERIFIED_ABSENCE", entity,
                                   direction, None, digest, None, False)

    base = check_provenance(answer, evidence, primary_email)
    if base.status != "LOCALLY_ANCHORED_VALUE":
        return RelationCertificate("HOLD_SOURCE_OR_AMOUNT", entity, direction,
                                   None, digest, None, False)

    amounts = money_values(answer)
    if len(amounts) != 1:
        return RelationCertificate("HOLD_MULTIPLE_AMOUNTS", entity, direction,
                                   None, digest, None, True)
    amount = next(iter(amounts))
    literal = _name_pattern(entity)
    if not literal.search(primary_email):
        return RelationCertificate("HOLD_NAMED_PARTY_ABSENT", entity, direction,
                                   None, digest, None, True)

    if direction != "to":
        # 'Paid by' has different directional/agency semantics. Never
        # infer it from merchant billing templates for 'paid to'.
        return RelationCertificate("HOLD_UNSUPPORTED_PAYMENT_DIRECTION", entity,
                                   direction, None, digest, None, True)

    matched_entity_anywhere = bool(literal.search(evidence))
    if not matched_entity_anywhere:
        return RelationCertificate("HOLD_PARTY_NOT_IN_PROOF_SPAN", entity,
                                   direction, None, digest, None, True)

    for money_match in MONEY.finditer(evidence):
        extracted = money_values(money_match.group())
        if amount not in extracted:
            continue
        left = evidence[max(0, money_match.start()-100):money_match.start()]
        right = evidence[money_match.end():money_match.end()+100]
        matched_target = literal.search(right)
        if matched_target is None:
            continue
        between = right[:matched_target.start()]
        marker = re.search(r"\b(?:by|to|at)\s*$", between, re.IGNORECASE)
        if not marker:
            continue
        # Require an outgoing event connected to this amount, not merely
        # a document-wide charge elsewhere. 'received ... from X' is not
        # equivalent to 'paid to X'.
        if not OUTGOING.search(left):
            continue
        if INBOUND.search(left):
            return RelationCertificate("HOLD_INBOUND_DIRECTION", entity,
                                       direction, None, digest, None, True)
        return RelationCertificate("ANCHORED_OUTGOING_TEMPLATE", entity,
                                   direction, str(amount), digest,
                                   "OUTGOING_AMOUNT_BY_NAMED_PARTY", True,
                                   False)

    if INBOUND.search(evidence):
        return RelationCertificate("HOLD_INBOUND_DIRECTION", entity, direction,
                                   None, digest, None, True)
    return RelationCertificate("HOLD_ROLE_NOT_ESTABLISHED", entity, direction,
                               None, digest, None, True)
