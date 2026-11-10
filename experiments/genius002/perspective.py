"""MOTIF-GENIUS-002: perspective-taking without identity or evidence collapse.

A *local-only* Trench-node-compatible experimental exchange protocol.
Not a live Trench app, a social predictor, a mind-reading engine, or a
verified collective intelligence improvement. No network, credentials,
external execution, or machine learning.

The distinction between understanding another's *reported* position
and acquiring authority over that person is a hard interface boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Claim:
    claim_id: str
    owner_id: str
    local_term: str
    proposition: str
    polarity: str                 # AFFIRM, DENY, or UNCERTAIN
    evidence_ref: str             # pointer, NOT evidence verification
    shareable: bool = False


@dataclass(frozen=True)
class Vote:
    option_id: str
    response: str                 # YES_TO_DRAFT, NO, or HOLD
    utility: Optional[int] = None  # owner-reported ordinal 0..3, not predicted
    reason: str = ""
    shareable: bool = False


@dataclass(frozen=True)
class PerspectiveGuess:
    target_node_id: str
    option_id: str
    expected_response: str
    shareable: bool = False


@dataclass(frozen=True)
class NodeState:
    """Local state. A packet projection must NEVER serialize unshared fields."""

    node_id: str
    claims: tuple[Claim, ...] = ()
    votes: tuple[Vote, ...] = ()
    perspective_guesses: tuple[PerspectiveGuess, ...] = ()


@dataclass(frozen=True)
class Crosswalk:
    """A source-owned, reviewed translation; not a forced equivalence."""

    owner_id: str
    local_term: str
    canonical_concept: str
    reviewed_by_owner: bool = False
    limitation: str = ""


@dataclass(frozen=True)
class Proposal:
    option_id: str
    description: str
    stakeholders: tuple[str, ...]


def _validate(nodes: tuple[NodeState, ...], options: tuple[Proposal, ...],
              crosswalks: tuple[Crosswalk, ...]) -> None:
    ids = [n.node_id for n in nodes]
    if not ids or any(not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Each distinct participant needs one nonempty node id")
    opt_ids = [o.option_id for o in options]
    if len(opt_ids) != len(set(opt_ids)) or any(not x for x in opt_ids):
        raise ValueError("Proposal ids must be unique and nonempty")
    for o in options:
        if not o.stakeholders or len(o.stakeholders) != len(set(o.stakeholders)):
            raise ValueError("Explicit, unique stakeholder set required")
        if not set(o.stakeholders) <= set(ids):
            raise ValueError("Unknown stakeholder")
    for n in nodes:
        claim_ids = [x.claim_id for x in n.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("Duplicate claim ids within a source")
        for c in n.claims:
            if c.owner_id != n.node_id or c.polarity not in ("AFFIRM", "DENY", "UNCERTAIN"):
                raise ValueError("Invalid source-owned claim")
            if not c.claim_id or not c.evidence_ref or not c.local_term or not c.proposition:
                raise ValueError("Claim requires source, evidence pointer, term and proposition")
        vote_ids = [v.option_id for v in n.votes]
        if len(vote_ids) != len(set(vote_ids)):
            raise ValueError("One vote per option per participant")
        for v in n.votes:
            if v.response not in ("YES_TO_DRAFT", "NO", "HOLD"):
                raise ValueError("Unknown response")
            if v.response == "YES_TO_DRAFT" and (type(v.utility) is not int or not 0 <= v.utility <= 3):
                raise ValueError("Owner must provide an ordinal utility for a YES")
            if v.utility is not None and (type(v.utility) is not int or not 0 <= v.utility <= 3):
                raise ValueError("Utility must be an explicitly supplied ordinal")
        guess_keys = [(g.target_node_id, g.option_id) for g in n.perspective_guesses]
        if len(guess_keys) != len(set(guess_keys)):
            raise ValueError("Duplicate predictions")
        for g in n.perspective_guesses:
            if g.target_node_id not in ids or g.expected_response not in ("YES_TO_DRAFT", "NO", "HOLD"):
                raise ValueError("Perspective guess must target a known node and legal response")
    seen = set()
    for c in crosswalks:
        key = (c.owner_id, c.local_term)
        if key in seen or c.owner_id not in ids:
            raise ValueError("Ambiguous or incorrectly owned crosswalk")
        seen.add(key)
        if c.reviewed_by_owner and not c.canonical_concept:
            raise ValueError("Approved translation needs a target concept")


def project_packet(node: NodeState) -> dict:
    """A voluntary **public** packet. Private state is not part of its schema."""
    return {
        "node_id": node.node_id,
        "claims": [
            {"claim_id": c.claim_id, "owner_id": c.owner_id,
             "local_term": c.local_term, "proposition": c.proposition,
             "polarity": c.polarity, "evidence_ref": c.evidence_ref}
            for c in node.claims if c.shareable
        ],
        "votes": [
            {"option_id": v.option_id, "response": v.response,
             "utility": v.utility if v.response == "YES_TO_DRAFT" else None,
             "reason": v.reason}
            for v in node.votes if v.shareable
        ],
        "perspective_guesses": [
            {"target_node_id": g.target_node_id,
             "option_id": g.option_id, "expected_response": g.expected_response}
            for g in node.perspective_guesses if g.shareable
        ],
    }


def _evidence_ledger(packets: list[dict],
                     crosswalks: tuple[Crosswalk, ...]) -> tuple[list[dict], list[dict], list[str]]:
    reviewed = {(x.owner_id, x.local_term): x
                for x in crosswalks if x.reviewed_by_owner}
    ledger = []
    for p in packets:
        for c in p["claims"]:
            x = reviewed.get((p["node_id"], c["local_term"]))
            ledger.append({
                **c, "canonical_concept": x.canonical_concept if x else None,
                "translation_limitation": x.limitation if x else None,
                "translation_status": "OWNER_REVIEWED" if x else "UNMAPPED",
            })
    # A contradiction requires an identical proposition AND a reviewed
    # shared concept; grouping by keyword alone would invent a dispute.
    buckets: dict[tuple[str, str], list[dict]] = {}
    for c in ledger:
        if c["canonical_concept"]:
            key = (c["canonical_concept"], c["proposition"].strip().lower())
            buckets.setdefault(key, []).append(c)
    contests = []
    for (concept, proposition), claims in sorted(buckets.items()):
        affirmative = sorted({x["owner_id"] for x in claims if x["polarity"] == "AFFIRM"})
        denying = sorted({x["owner_id"] for x in claims if x["polarity"] == "DENY"})
        if affirmative and denying:
            contests.append({
                "concept": concept, "proposition": proposition,
                "affirming_nodes": affirmative, "denying_nodes": denying,
                "status": "CONTESTED_NOT_ADJUDICATED",
                "question": "Which independent observation could test this disputed proposition?",
            })
    unmapped = sorted({f'{c["owner_id"]}:{c["local_term"]}' for c in ledger
                       if c["translation_status"] == "UNMAPPED"})
    return ledger, contests, unmapped


def _perspective_checks(packets: list[dict]) -> list[dict]:
    by_id = {p["node_id"]: p for p in packets}
    checked = []
    for p in packets:
        for guess in p["perspective_guesses"]:
            target = by_id[guess["target_node_id"]]
            observed = next((v["response"] for v in target["votes"]
                             if v["option_id"] == guess["option_id"]), None)
            if observed is None:
                # A withheld response is never surfaced by a 'guesser'.
                checked.append({
                    "from": p["node_id"], "about": target["node_id"],
                    "option_id": guess["option_id"],
                    "status": "HOLD_NO_SHARED_TARGET_RESPONSE",
                    "question": "Would the other participant choose to share their position?",
                })
            else:
                checked.append({
                    "from": p["node_id"], "about": target["node_id"],
                    "option_id": guess["option_id"],
                    "hypothesis": guess["expected_response"],
                    "target_self_report": observed,
                    "status": "MATCHED_SELF_REPORT" if guess["expected_response"] == observed
                              else "CORRECTED_BY_TARGET",
                    "question": "What did the other participant say was missed?",
                })
    return checked


def deliberate(nodes: tuple[NodeState, ...], options: tuple[Proposal, ...],
               crosswalks: tuple[Crosswalk, ...] = ()) -> dict:
    """Find a consent-eligible *draft*, never enact a group decision.

    All stakeholders must share YES_TO_DRAFT; withheld or missing input
    means HOLD; a public NO means REFUSED. On eligible options we use
    max-min owner-declared utility then total utility with a stable
    lexical tie break. This is a simple classical finite optimizer,
    NOT a novel group-intelligence algorithm or utility estimator.
    """
    _validate(nodes, options, crosswalks)
    packets = [project_packet(n) for n in nodes]
    views = {p["node_id"]: p for p in packets}
    ledger, contested, unmapped = _evidence_ledger(packets, crosswalks)
    guesses = _perspective_checks(packets)
    examined = []
    candidates = []

    for option in options:
        replies = {}
        for stakeholder in option.stakeholders:
            row = next((v for v in views[stakeholder]["votes"]
                        if v["option_id"] == option.option_id), None)
            replies[stakeholder] = (
                {"response": row["response"],
                 "utility": row["utility"],
                 "reason": row["reason"]} if row is not None
                else {"response": "NOT_SHARED", "utility": None, "reason": ""}
            )
        values = [r["utility"] for r in replies.values()
                  if r["response"] == "YES_TO_DRAFT"]
        if any(r["response"] == "NO" for r in replies.values()):
            status = "REFUSED_BY_STAKEHOLDER"
        elif any(r["response"] != "YES_TO_DRAFT" for r in replies.values()):
            status = "HOLD_INCOMPLETE_CONSENT"
        else:
            status = "ELIGIBLE_DRAFT_NOT_EXECUTED"
        examined.append({
            "option_id": option.option_id, "description": option.description,
            "status": status, "public_responses": replies,
        })
        if status == "ELIGIBLE_DRAFT_NOT_EXECUTED":
            candidates.append((min(values), sum(values), option.option_id))

    winner_id = (
        sorted(candidates, key=lambda x: (-x[0], -x[1], x[2]))[0][2]
        if candidates else None
    )
    # Deliberately weak control: first majority-supported option (including
    # scenarios in which a minority refuses). Explicitly labeled unsafe.
    unsafe_baseline = next((
        option.option_id for option in options
        if sum(1 for v in examined if v["option_id"] == option.option_id
               for reply in v["public_responses"].values()
               if reply["response"] == "YES_TO_DRAFT") >
        len(option.stakeholders) / 2
    ), None)

    questions = [f"Would {term} like to authorize a precise concept mapping?"
                 for term in unmapped]
    questions.extend(f'Can we verify disputed claim: {x["proposition"]}?'
                     for x in contested)
    questions.extend(
        f'Would {p["node_id"]} share or clarify its view of {o["option_id"]}?'
        for o in examined for p in packets
        if p["node_id"] in next(opt.stakeholders for opt in options
                                if opt.option_id == o["option_id"])
        and o["public_responses"][p["node_id"]]["response"] == "NOT_SHARED"
    )
    if not questions and guesses:
        questions.append("Where did predictions of other nodes differ from their own reports?")
    return {
        "status": "CANDIDATE_FOR_HUMAN_REVIEW" if winner_id else "HOLD_NO_SHARED_JOINT_PLAN",
        "selected_option_id": winner_id,
        "no_external_action_taken": True,
        "consent_scope": "YES_TO_DRAFT is permission to consider a draft only",
        "public_packets": packets,
        "source_bound_claim_ledger": ledger,
        "contested_claims": contested,
        "perspective_checks": guesses,
        "options": examined,
        "unsafe_first_majority_control": unsafe_baseline,
        "questions_for_human_return": questions,
        "method": "EXACT_FINITE_ENUMERATION_OF_SHARED_STANCES_AND_DECLARED_UTILITY",
    }


def demo() -> dict:
    """Synthetic independently readable Trench-style three-node exchange."""
    food_claim = "The rush route keeps the food within safe handling limits"
    states = (
        NodeState("grower",
                  claims=(Claim("g1", "grower", "fast", food_claim, "AFFIRM",
                                "synthetic:g1", True),),
                  votes=(Vote("a_rush", "YES_TO_DRAFT", 3, shareable=True),
                         Vote("b_shared", "YES_TO_DRAFT", 2, shareable=True)),
                  perspective_guesses=(PerspectiveGuess("courier", "a_rush",
                                                       "YES_TO_DRAFT", True),)),
        NodeState("kitchen",
                  claims=(Claim("k_private", "kitchen", "secret",
                                "DO_NOT_EXPORT_PRIVATE_CONTENT", "UNCERTAIN",
                                "synthetic:private", False),),
                  votes=(Vote("a_rush", "YES_TO_DRAFT", 3, shareable=True),
                         Vote("b_shared", "YES_TO_DRAFT", 2, shareable=True))),
        NodeState("courier",
                  claims=(Claim("c1", "courier", "timely", food_claim, "DENY",
                                "synthetic:c1", True),),
                  votes=(Vote("a_rush", "NO", reason="No suitable transport slot", shareable=True),
                         Vote("b_shared", "YES_TO_DRAFT", 2, shareable=True)),
                  perspective_guesses=(PerspectiveGuess("kitchen", "b_shared",
                                                       "YES_TO_DRAFT", True),)),
    )
    proposals = (
        Proposal("a_rush", "Rushed pickup (synthetic)", ("grower", "kitchen", "courier")),
        Proposal("b_shared", "Staggered, consented pickup (synthetic)",
                 ("grower", "kitchen", "courier")),
    )
    crosswalks = (
        Crosswalk("grower", "fast", "food_handling_safety", True,
                  "Different parties may mean different things by 'fast'"),
        Crosswalk("courier", "timely", "food_handling_safety", True,
                  "Mapped solely for this exact synthetic proposition"),
    )
    return deliberate(states, proposals, crosswalks)


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True))
