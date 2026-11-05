"""BRIDGE-001: generate missing cooperation moves from facts, offers and gates.

Offline fictional-world laboratory. Generates candidate links, not new physics.
No input can authorize a real person, send a message, book a resource, change
a server, or create real consent. Proposed moves are HELD by default.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from heapq import heappop, heappush
from typing import Iterable
import json


@dataclass(frozen=True)
class Scene:
    requirements: frozenset[tuple[str, str]]  # (task, required_tool_kind)
    skills: frozenset[tuple[str, str]]
    assets: frozenset[tuple[str, str]]        # (asset_id, tool_kind)
    custody: frozenset[tuple[str, str]]       # (actor, asset_id)
    access: frozenset[tuple[str, str]]        # synthetic site/world gate
    known: frozenset[tuple[str, str]]

    def __post_init__(self) -> None:
        required = dict(self.requirements)
        assets = dict(self.assets)
        if len(required) != len(self.requirements) or not required:
            raise ValueError("task requirements must have unique task names")
        if len(assets) != len(self.assets):
            raise ValueError("asset identifiers must be unique")
        held = [asset for _, asset in self.custody]
        if len(set(held)) != len(held) or any(x not in assets for x in held):
            raise ValueError("one existing asset may have only one custodian")
        if any(task not in required for _, task in
               (self.skills | self.access | self.known)):
            raise ValueError("unregistered task in scene")
        if any(not x or not y for x, y in
               self.requirements | self.skills | self.assets |
               self.custody | self.access | self.known):
            raise ValueError("empty identifiers are invalid")


@dataclass(frozen=True)
class Offer:
    id: str
    kind: str                    # teach | inform | loan | make
    provider: str
    subject: str                 # task, asset ID, or tool kind
    recipients: frozenset[str]
    cost: int
    minutes: int
    declared: bool = True       # still fictional; not verified real consent

    def __post_init__(self) -> None:
        if self.kind not in ("teach", "inform", "loan", "make"):
            raise ValueError("unsupported offer family")
        if not self.id or not self.provider or not self.subject or not self.recipients:
            raise ValueError("empty offer fields")
        if type(self.cost) is not int or self.cost < 0:
            raise ValueError("cost must be a nonnegative integer")
        if type(self.minutes) is not int or self.minutes <= 0:
            raise ValueError("minutes must be positive")


@dataclass(frozen=True)
class Acceptance:
    offer_id: str
    recipient: str


@dataclass(frozen=True)
class Goal:
    task: str
    actor: str | None = None
    preserve: bool = True
    deadline_minutes: int | None = None


@dataclass(frozen=True)
class Candidate:
    id: str
    kind: str
    source: str
    recipient: str
    subject: str
    status: str               # ADMITTED_SIM | HOLD_OFFER | HOLD_ACCEPTANCE
    offer_id: str | None
    cost: int | None
    minutes: int | None
    minted_tool: str = ""

    @property
    def held(self) -> bool:
        return self.status != "ADMITTED_SIM"


def options(scene: Scene) -> dict[str, frozenset[tuple[str, str]]]:
    requirements = dict(scene.requirements)
    assets = dict(scene.assets)
    possessed: dict[str, set[str]] = {}
    for actor, asset in scene.custody:
        possessed.setdefault(actor, set()).add(assets[asset])
    physical = frozenset(
        (actor, task) for actor, task in scene.skills
        if requirements[task] in possessed.get(actor, set())
    )
    admitted = physical & scene.access
    return {
        "physical": physical,
        "admitted": admitted,
        "visible": admitted & scene.known,
    }


def _render(keys: Iterable[tuple[str, str]]) -> list[str]:
    return [f"{a}:{b}" for a, b in sorted(keys)]


def _delta(before: Scene, after: Scene) -> dict[str, dict[str, list[str]]]:
    a, b = options(before), options(after)
    return {scope: {"gained": _render(b[scope] - a[scope]),
                    "lost": _render(a[scope] - b[scope])}
            for scope in ("physical", "admitted", "visible")}


def _require_consistency(offers: tuple[Offer, ...],
                         acceptances: frozenset[Acceptance]) -> None:
    if len({o.id for o in offers}) != len(offers):
        raise ValueError("offer ids must be unique")
    refs = {o.id: o for o in offers}
    for acceptance in acceptances:
        if acceptance.offer_id not in refs:
            raise ValueError("acceptance references an unknown offer")
        if acceptance.recipient not in refs[acceptance.offer_id].recipients:
            raise ValueError("recipient cannot accept an offer outside its scope")


def generate(scene: Scene, offers: tuple[Offer, ...],
             acceptances: frozenset[Acceptance], goal: Goal) -> tuple[Candidate, ...]:
    """Infer candidate *bindings*; neither destinations nor moves are supplied.

    It can synthesize a previously unlisted recipient/action pairing and a
    multi-move plan. It cannot invent an unknown physical action primitive.
    """
    _require_consistency(offers, acceptances)
    requirements = dict(scene.requirements)
    if goal.task not in requirements:
        raise ValueError("goal task is unknown")
    tool_kind = requirements[goal.task]
    assets = dict(scene.assets)
    # Never infer a new grant. Only actors already covered by site/world access
    # may be suggested as final target performers.
    final_recipients = {
        actor for actor, task in scene.access if task == goal.task
        and (goal.actor is None or goal.actor == actor)
    }
    # Backward-chain through *explicit offered future relay roles*.
    # A relay teacher may first need to acquire the skill before teaching
    # the actual target. This is where one action births a new possible action.
    relevant = set(final_recipients)
    changed = True
    while changed:
        changed = False
        for offer in offers:
            if (not offer.declared or offer.subject != goal.task
                    or not offer.recipients.intersection(relevant)):
                continue
            must_gain = (
                offer.kind == "teach" and
                (offer.provider, goal.task) not in scene.skills
            ) or (
                offer.kind == "inform" and
                (offer.provider, goal.task) not in scene.known
            )
            if must_gain and offer.provider not in relevant:
                relevant.add(offer.provider)
                changed = True
    recipients = sorted(relevant)
    proposals: list[Candidate] = []

    def make(kind: str, source: str, recipient: str, subject: str,
             tool: str = "") -> None:
        matching = sorted(
            (o for o in offers
             if o.kind == kind and o.provider == source
             and o.subject == subject and recipient in o.recipients
             and o.declared),
            key=lambda o: (o.cost, o.minutes, o.id),
        )
        if not matching:
            proposals.append(Candidate(
                id=f"held:{kind}:{source}:{recipient}:{subject}",
                kind=kind, source=source, recipient=recipient,
                subject=subject, status="HOLD_OFFER", offer_id=None,
                cost=None, minutes=None, minted_tool=tool,
            ))
        else:
            for offer in matching:
                status = ("ADMITTED_SIM"
                          if Acceptance(offer.id, recipient) in acceptances
                          else "HOLD_ACCEPTANCE")
                proposals.append(Candidate(
                    id=f"{status}:{offer.id}:{recipient}",
                    kind=kind, source=source, recipient=recipient,
                    subject=subject, status=status, offer_id=offer.id,
                    cost=offer.cost, minutes=offer.minutes, minted_tool=tool,
                ))

    for recipient in recipients:
        if (recipient, goal.task) not in scene.skills:
            teachers = {
                actor for actor, task in scene.skills if task == goal.task
            } | {
                offer.provider for offer in offers
                if offer.kind == "teach" and offer.subject == goal.task
                and recipient in offer.recipients and offer.declared
            }
            for teacher in sorted(teachers):
                if teacher != recipient:
                    make("teach", teacher, recipient, goal.task)

        if (recipient, goal.task) not in scene.known:
            informers = {
                actor for actor, task in scene.known if task == goal.task
            } | {
                offer.provider for offer in offers
                if offer.kind == "inform" and offer.subject == goal.task
                and recipient in offer.recipients and offer.declared
            }
            for informer in sorted(informers):
                if informer != recipient:
                    make("inform", informer, recipient, goal.task)

        if recipient in final_recipients and tool_kind not in {
            assets[asset] for actor, asset in scene.custody if actor == recipient
        }:
            for holder, asset_id in sorted(scene.custody):
                if holder != recipient and assets[asset_id] == tool_kind:
                    make("loan", holder, recipient, asset_id)
            # Physical tool production cannot be inferred from mere desire:
            # it needs an explicit declared maker offer even for hypothetical
            # generation. A minted tool is still only a synthetic assumption.
            for offer in sorted(offers, key=lambda o: o.id):
                if (offer.kind == "make" and offer.subject == tool_kind
                        and recipient in offer.recipients and offer.declared):
                    make("make", offer.provider, recipient, tool_kind,
                         tool=tool_kind)

    return tuple(sorted(proposals, key=lambda candidate: candidate.id))


def transition(scene: Scene, move: Candidate, *, counterfactual: bool = False
               ) -> Scene | None:
    """Never execute any side effect. Only change an immutable toy Scene.

    Held candidate mutations require an explicit *counterfactual* flag.
    """
    if move.held and not counterfactual:
        return None
    key = (move.source, move.subject)
    target = (move.recipient, move.subject)
    if move.source == move.recipient:
        return None
    if move.kind == "teach" and key in scene.skills and target not in scene.skills:
        return replace(scene, skills=scene.skills | {target})
    if move.kind == "inform" and key in scene.known and target not in scene.known:
        return replace(scene, known=scene.known | {target})
    if move.kind == "loan" and key in scene.custody:
        return replace(scene, custody=(scene.custody - {key}) | {target})
    if move.kind == "make" and move.minted_tool:
        asset_id = f"synthetic:{move.source}:{move.recipient}:{move.subject}"
        if asset_id not in dict(scene.assets):
            return replace(scene, assets=scene.assets | {(asset_id, move.minted_tool)},
                           custody=scene.custody | {(move.recipient, asset_id)})
    return None


def _goal_met(scene: Scene, goal: Goal) -> bool:
    return any(task == goal.task and (goal.actor is None or actor == goal.actor)
               for actor, task in options(scene)["visible"])


def _preserved(before: Scene, after: Scene) -> bool:
    a, b = options(before), options(after)
    return all(a[scope].issubset(b[scope])
               for scope in ("physical", "admitted", "visible"))


def solve(
    initial: Scene, offers: tuple[Offer, ...],
    acceptances: frozenset[Acceptance], goal: Goal,
    *, max_steps: int = 4, max_states: int = 3000
) -> dict[str, object]:
    """Fewest held agreements, then least declared cost, then fewest moves.

    Provisional steps have UNKNOWN real cost and duration; their zero numerical
    contribution is only a tie convention. A HOLD result makes NO feasibility
    or minimum-real-cost claim. Only fully admitted plans get deadline checks.
    """
    if max_steps < 0 or max_states < 1:
        raise ValueError("invalid search bounds")
    if goal.deadline_minutes is not None and (
        type(goal.deadline_minutes) is not int or goal.deadline_minutes < 0
    ):
        raise ValueError("invalid deadline")
    moves = generate(initial, offers, acceptances, goal)
    meta = {
        "schema": "motif.bridge-synthesis/v0",
        "domain": "FICTIONAL_GRAPH_ONLY",
        "goal": {"task": goal.task, "actor": goal.actor,
                 "preserve": goal.preserve,
                 "deadline_minutes": goal.deadline_minutes},
        "candidate_bindings": len(moves),
        "held_bindings": sum(x.held for x in moves),
        "simulated_only": True,
    }
    initial_options = options(initial)
    if _goal_met(initial, goal):
        return {**meta, "status": "ALREADY_REACHABLE",
                "actions": [], "held_steps": [],
                "known_cost": 0, "known_minutes": 0,
                "delta": _delta(initial, initial), "explored_states": 1}

    # Priority: fewer held commitments -> fewer *completely unoffered*
    # commitments -> lower known cost -> fewer steps -> stable IDs.
    # A recipient's pending acceptance of a real (toy) offer is grounded
    # better than an entirely unoffered direct proposal.
    # Unknown costs are never equated to actual zero costs.
    queue: list[tuple[int, int, int, int, tuple[str, ...], int, Scene]] = [
        (0, 0, 0, 0, (), 0, initial)
    ]
    seen: dict[tuple[Scene, int], tuple[int, int, int, int, tuple[str, ...]]] = {
        (initial, 0): (0, 0, 0, 0, ())
    }
    by_id = {m.id: m for m in moves}
    explored = 0
    while queue:
        held_count, unoffered, cost, steps, path, minutes, world = heappop(queue)
        if (held_count, unoffered, cost, steps, path) != seen.get((world, minutes)):
            continue
        explored += 1
        if explored > max_states:
            return {**meta, "status": "HOLD_TRUNCATED",
                    "actions": [], "held_steps": [],
                    "known_cost": None, "known_minutes": None,
                    "delta": None, "explored_states": explored}

        if _goal_met(world, goal):
            actions = [by_id[x] for x in path]
            held = [a for a in actions if a.held]
            out = {
                **meta,
                "status": ("HOLD_UNVERIFIED_BRIDGE"
                           if held else "PROPOSED_SYNTHETIC_ONLY"),
                "actions": [
                    {"id": a.id, "kind": a.kind,
                     "source": a.source, "recipient": a.recipient,
                     "subject": a.subject, "status": a.status,
                     "offer_id": a.offer_id,
                     "declared_cost": a.cost, "declared_minutes": a.minutes}
                    for a in actions
                ],
                "held_steps": [a.id for a in held],
                "known_cost": cost,
                "known_minutes": minutes,
                "total_cost_known": not bool(held),
                "total_duration_known": not bool(held),
                "deadline_feasible": (
                    None if held or goal.deadline_minutes is None
                    else minutes <= goal.deadline_minutes
                ),
                "delta": _delta(initial, world),
                "explored_states": explored,
            }
            return out

        if steps >= max_steps:
            continue
        # Recompute bindings from the new state. The source of a proposed
        # teaching/information transfer can itself be a newly trained actor.
        # Source facts are not added as evidence; only hypothetical successor
        # states are searched.
        live_moves = generate(world, offers, acceptances, goal)
        for action in live_moves:
            by_id[action.id] = action
            after = transition(world, action, counterfactual=True)
            if after is None or after == world:
                continue
            if goal.preserve and not _preserved(initial, after):
                continue
            new_minutes = minutes + (action.minutes or 0)
            if (goal.deadline_minutes is not None
                    and not action.held and new_minutes > goal.deadline_minutes):
                continue
            if (goal.deadline_minutes is not None and
                    any(by_id[action_id].held for action_id in path)):
                # Holds keep timing unknown. Known portion can still exceed a
                # deadline and be definitively infeasible.
                if new_minutes > goal.deadline_minutes:
                    continue
            new_cost = cost + (action.cost or 0)
            new_held = held_count + int(action.held)
            new_unoffered = unoffered + int(action.status == "HOLD_OFFER")
            new_path = path + (action.id,)
            score = (new_held, new_unoffered, new_cost, steps + 1, new_path)
            state_key = (after, new_minutes)
            if state_key not in seen or score < seen[state_key]:
                seen[state_key] = score
                heappush(queue, (*score, new_minutes, after))

    return {**meta, "status": "ABSTAIN_NO_BOUNDED_BRIDGE",
            "actions": [], "held_steps": [], "known_cost": None,
            "known_minutes": None, "delta": None,
            "explored_states": explored}


def first_human_card(result: dict[str, object]) -> dict[str, object]:
    """An actionable review question or a concrete candidate; never delivered."""
    actions = result.get("actions", [])
    if not actions:
        return {"schema": "motif.field-card/v0", "state": "NO_OUTBOUND_ACTION",
                "first_step": "No supported first action under the stated constraints.",
                "source_status": result["status"]}
    held = next((a for a in actions if a["status"] != "ADMITTED_SIM"), None)
    first = held if held is not None else actions[0]
    descriptions = {
        "teach": f"{first['source']} could teach {first['recipient']} {first['subject']}.",
        "inform": f"{first['source']} could inform {first['recipient']} about {first['subject']}.",
        "loan": f"{first['source']} could offer {first['subject']} to {first['recipient']}.",
        "make": f"{first['source']} could provide a {first['subject']} to {first['recipient']}.",
    }
    suffix = {
        "ADMITTED_SIM": "Fictional conditions supplied; verify in reality before any action.",
        "HOLD_ACCEPTANCE": "Recipient agreement has not been supplied. Ask without assuming yes.",
        "HOLD_OFFER": "Provider has not offered this. Ask without assuming yes.",
    }
    return {"schema": "motif.field-card/v0", "state": "DRAFT_NOT_SENT",
            "first_step": descriptions[first["kind"]] + " " + suffix[first["status"]],
            "source_status": result["status"], "requires_human_review": True,
            "no_auto_contact": True}


def workshop(with_offers: bool = True
             ) -> tuple[Scene, tuple[Offer, ...], frozenset[Acceptance], Goal]:
    scene = Scene(
        requirements=frozenset({("well", "kit"), ("bike", "kit")}),
        skills=frozenset({("ada", "well"), ("ben", "bike")}),
        assets=frozenset({("tool1", "kit")}),
        custody=frozenset({("ben", "tool1")}),
        access=frozenset({("ada", "well"), ("ben", "bike"), ("ben", "well")}),
        known=frozenset({("ada", "well"), ("ben", "bike")}),
    )
    offers = (
        Offer("teach-well", "teach", "ada", "well", frozenset({"ben"}), 2, 12),
        Offer("inform-well", "inform", "ada", "well", frozenset({"ben"}), 1, 4),
        Offer("lend-kit", "loan", "ben", "tool1", frozenset({"ada"}), 1, 8),
        Offer("make-kit", "make", "maker", "kit", frozenset({"ada"}), 4, 20),
    ) if with_offers else (Offer("lend-kit", "loan", "ben", "tool1",
                              frozenset({"ada"}), 1, 8),)
    accepted = frozenset(Acceptance(o.id, recipient)
                         for o in offers for recipient in o.recipients)
    return scene, offers, accepted, Goal("well", preserve=True)


def food() -> tuple[Scene, tuple[Offer, ...], frozenset[Acceptance], Goal]:
    # Fictional relationships, not claims about actual perishable food safety.
    scene = Scene(
        requirements=frozenset({("food_relay", "cooler"),
                                ("medical_run", "cooler")}),
        skills=frozenset({("courier", "food_relay"),
                          ("medic", "medical_run")}),
        assets=frozenset({("cooler1", "cooler")}),
        custody=frozenset({("medic", "cooler1")}),
        access=frozenset({("courier", "food_relay"),
                          ("medic", "medical_run")}),
        known=frozenset({("host", "food_relay"),
                         ("medic", "medical_run")}),
    )
    offers = (
        Offer("tell-route", "inform", "host", "food_relay",
              frozenset({"courier"}), 1, 2),
        Offer("lend-cooler", "loan", "medic", "cooler1",
              frozenset({"courier"}), 1, 5),
        Offer("provide-cooler", "make", "depot", "cooler",
              frozenset({"courier"}), 3, 12),
    )
    accepted = frozenset(Acceptance(o.id, next(iter(o.recipients)))
                         for o in offers)
    return scene, offers, accepted, Goal("food_relay", actor="courier",
                                          preserve=True, deadline_minutes=20)


def relay(*, recipient_accepts: bool = True
          ) -> tuple[Scene, tuple[Offer, ...], frozenset[Acceptance], Goal]:
    """A taught intermediary unlocks a later action absent at the first cut."""
    scene = Scene(
        requirements=frozenset({("relay", "transmitter")}),
        skills=frozenset({("ari", "relay")}),
        assets=frozenset({("t1", "transmitter")}),
        custody=frozenset({("cy", "t1")}),
        access=frozenset({("cy", "relay")}),
        known=frozenset({("cy", "relay")}),
    )
    offers = (
        Offer("ari-to-bea", "teach", "ari", "relay",
              frozenset({"bea"}), 2, 6),
        Offer("bea-to-cy", "teach", "bea", "relay",
              frozenset({"cy"}), 2, 6),
    )
    accepted = {Acceptance("bea-to-cy", "cy")}
    if recipient_accepts:
        accepted.add(Acceptance("ari-to-bea", "bea"))
    return scene, offers, frozenset(accepted), Goal("relay", actor="cy")


def run_demo() -> dict[str, object]:
    a = workshop()
    b = workshop(with_offers=False)
    c = food()
    d = relay()
    e = relay(recipient_accepts=False)
    return {"experiment": "MOTIF-BRIDGE-001",
            "full_offers": {"result": solve(*a),
                            "card": first_human_card(solve(*a))},
            "missing_offers": {"result": solve(*b),
                               "card": first_human_card(solve(*b))},
            "other_domain": {"result": solve(*c),
                             "card": first_human_card(solve(*c))},
            "emergent_relay": {"result": solve(*d),
                              "card": first_human_card(solve(*d))},
            "held_relay": {"result": solve(*e),
                           "card": first_human_card(solve(*e))},
            "limits": ("synthetic named-world grammar only; no real "
                       "consent, food safety, verified source, or external execution")}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
