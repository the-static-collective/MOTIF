"""CONFLUENCE-001: bounded, evidence-preserving orchestration over a toy field.

No live sensing, autonomous external action, identity verification, or physical
fence design. All world candidates and observations are engineer-authored.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True, order=True)
class World:
    panel_span: int
    mesh_safe: bool

    def identifier(self):
        return f"span={self.panel_span};mesh_safe={int(self.mesh_safe)}"


WORLDS = tuple(World(n, safe) for n, safe in product((1, 2), (False, True)))
SENSORS = {
    "measure_panel": ("panel_span", 1),
    "inspect_mesh": ("mesh_safe", 2),
}
# Integer fixture ticks, NOT calibrated real-world expiry times.
FRESH_FOR = {"permission": 1, "panel_span": 3, "mesh_safe": 2}
PLANS = {
    "PANEL_AND_CHAIR": ("brace_panel", "place_panel", "place_chair"),
    "MESH_AND_CHAIR": ("prepare_mesh", "place_mesh", "place_chair"),
}


class SyntheticOwner:
    """Single simulated source. A hash is integrity, not authentic identity."""

    def __init__(self, panel_span=2, mesh_safe=False, permission=True):
        if type(panel_span) is not int or panel_span not in (1, 2) or type(mesh_safe) is not bool or type(permission) is not bool:
            raise ValueError("invalid controlled fixture")
        self.state = dict(panel_span=panel_span, mesh_safe=mesh_safe, permission=permission)
        self.clock = 0
        self._issued = []
        self.origin = "ONE_SYNTHETIC_OWNER"

    def change(self, **values):
        if not values or any(k not in self.state for k in values):
            raise ValueError("unrecognized change")
        proposed = {**self.state, **values}
        if type(proposed["panel_span"]) is not int or proposed["panel_span"] not in (1, 2) or any(
            type(proposed[k]) is not bool for k in ("mesh_safe", "permission")
        ):
            raise ValueError("invalid change")
        self.clock += 1
        self.state = proposed

    def advance(self, ticks):
        if type(ticks) is not int or ticks < 0:
            raise ValueError("invalid simulated time")
        self.clock += ticks

    def read(self, sensor):
        if sensor not in ("permission", *SENSORS):
            raise ValueError("unreviewed read instrument")
        key = SENSORS[sensor][0] if sensor in SENSORS else "permission"
        body = dict(schema="motif.confluence001.source.v1",
                    type="SOURCE_OBSERVATION", sensor=sensor, key=key,
                    value=self.state[key], time=self.clock, origin=self.origin,
                    scope="ENGINEER_AUTHORED_SYNTHETIC_WORLD")
        receipt = {**body, "sha256": digest(body)}
        self._issued.append(deepcopy(receipt))
        return receipt

    def verify(self, receipt):
        if not isinstance(receipt, dict) or receipt not in self._issued:
            return False
        body = {k: v for k, v in receipt.items() if k != "sha256"}
        return (receipt.get("sha256") == digest(body)
                and receipt.get("origin") == self.origin
                and receipt.get("type") == "SOURCE_OBSERVATION")

    def simulate(self, plan):
        """Independent fixture check of a proposed plan. No physical effects."""
        if plan not in PLANS:
            raise ValueError("unreviewed simulation plan")
        safe = self.state["permission"] and (
            (plan == "PANEL_AND_CHAIR" and self.state["panel_span"] == 2)
            or (plan == "MESH_AND_CHAIR" and self.state["mesh_safe"])
        )
        body = dict(type="SYNTHETIC_PLAN_OUTCOME", plan=plan, goal_met=bool(safe),
                    time=self.clock, origin=self.origin, physical_actions=0)
        return {**body, "sha256": digest(body)}


class Ledger:
    """Append-only hash chain. Source membership is independently rechecked."""

    def __init__(self):
        self.events = []

    def append(self, kind, payload):
        if kind not in ("PENCIL_PROPOSAL", "INK_OBSERVATION", "PLAN_HOLD", "PLAN_PREVIEW"):
            raise ValueError("unreviewed evidence status")
        body = dict(sequence=len(self.events), kind=kind, payload=deepcopy(payload),
                    prev=self.events[-1]["sha256"] if self.events else None)
        event = {**body, "sha256": digest(body)}
        self.events.append(event)
        return event

    def valid(self, owner):
        previous = None
        for i, event in enumerate(self.events):
            body = {k: v for k, v in event.items() if k != "sha256"}
            if (event.get("sha256") != digest(body) or event.get("sequence") != i
                    or event.get("prev") != previous):
                return False
            if event["kind"] == "INK_OBSERVATION" and not owner.verify(event["payload"]):
                return False
            if event["kind"] == "PENCIL_PROPOSAL" and event["payload"].get("status") != "PENCIL":
                return False
            previous = event["sha256"]
        return True


def plan_for(worlds):
    """Only a plan safe in EVERY surviving world may enter the preview."""
    if not worlds:
        return None
    if all(w.panel_span == 2 for w in worlds):
        return "PANEL_AND_CHAIR"
    if all(w.mesh_safe for w in worlds):
        return "MESH_AND_CHAIR"
    return None


class Confluence:
    def __init__(self, owner):
        self.owner = owner
        self.ledger = Ledger()

    def _fresh(self, key):
        for event in reversed(self.ledger.events):
            if event["kind"] != "INK_OBSERVATION":
                continue
            receipt = event["payload"]
            if receipt["key"] == key and self.owner.clock - receipt["time"] <= FRESH_FOR[key]:
                if not self.owner.verify(receipt):
                    raise ValueError("source verification failed")
                return receipt["value"]
        return None

    def _observe(self, name):
        receipt = self.owner.read(name)
        if not self.owner.verify(receipt):
            raise ValueError("unverified owner response")
        self.ledger.append("INK_OBSERVATION", receipt)
        return receipt

    def candidates(self):
        span, safe = self._fresh("panel_span"), self._fresh("mesh_safe")
        return tuple(w for w in WORLDS
                     if (span is None or w.panel_span == span)
                     and (safe is None or w.mesh_safe == safe))

    @staticmethod
    def _groups(worlds, key):
        groups = {}
        for w in worlds:
            groups.setdefault(getattr(w, key), []).append(w)
        return groups

    def hinge(self, worlds):
        """One-step utility lookahead; alternatives remain explicit PENCIL."""
        choices = []
        for instrument, (key, cost) in SENSORS.items():
            if self._fresh(key) is not None:
                continue
            groups = self._groups(worlds, key)
            if len(groups) <= 1:
                continue
            actionable = sum(len(group) for group in groups.values()
                             if plan_for(group) is not None)
            # 'actionable' is a count in a finite candidate catalogue, not
            # a real-world probability of truth or an ethical utility.
            choices.append((-actionable, cost, instrument, groups))
        if not choices:
            return None
        return min(choices, key=lambda row: row[:3])[2]

    def run(self, budget=2):
        if type(budget) is not int or budget < 0:
            raise ValueError("invalid question budget")
        permission = self._fresh("permission")
        if permission is None:  # No permission inherited from old/stale reports.
            permission = self._observe("permission")["value"]
        if permission is not True:
            self.ledger.append("PLAN_HOLD", {"reason": "PERMISSION_UNVERIFIED_OR_DENIED"})
            return self.report("HOLD", None, "PERMISSION_UNVERIFIED_OR_DENIED")
        for _ in range(budget + 1):
            worlds = self.candidates()
            selected = plan_for(worlds)
            if selected is not None:
                from adapter003 import assess
                assessment = assess(selected, worlds)
                outcome = self.owner.simulate(selected)
                # Owner simulation is *not* an observed physical intervention.
                if not outcome["goal_met"] or not assessment["goal_reached"]:
                    self.ledger.append("PLAN_HOLD", {"reason": "SIMULATION_DISAGREEMENT"})
                    return self.report("HOLD", None, "SIMULATION_DISAGREEMENT")
                self.ledger.append("PLAN_PREVIEW", {
                    "plan": selected, "status": "SYNTHETIC_ONLY",
                    "owner_simulated_outcome": outcome,
                    "motif003": assessment,
                })
                return self.report("PLAN_SIMULATED", selected, None)
            if _ == budget:
                break
            instrument = self.hinge(worlds)
            if instrument is None:
                break
            # This PENCIL event is frozen before the hidden owner is questioned.
            proposal = dict(status="PENCIL", query=instrument,
                            alternatives=[w.identifier() for w in worlds],
                            conditional_plans={
                                w.identifier(): plan_for((w,)) for w in worlds
                            }, source_origin_count=1,
                            authority="PROPOSAL_NOT_OBSERVATION")
            self.ledger.append("PENCIL_PROPOSAL", proposal)
            observed = self._observe(instrument)
            assert observed["type"] == "SOURCE_OBSERVATION"
        reason = "UNRESOLVED_WITHIN_BUDGET_OR_NO_SAFE_PLAN"
        self.ledger.append("PLAN_HOLD", {"reason": reason})
        return self.report("HOLD", None, reason)

    def report(self, status, plan, reason):
        if not self.ledger.valid(self.owner):
            raise ValueError("invalid source ledger")
        return {
            "schema": "motif.confluence001.result.v1", "status": status,
            "plan": plan, "steps": list(PLANS[plan]) if plan else [],
            "reason": reason,
            "remaining_conditional_worlds": [w.identifier() for w in self.candidates()],
            "review_due_keys": [key for key in FRESH_FOR if self._fresh(key) is None],
            "source_origins": [self.owner.origin],  # NOT count of repeated reports
            "ink_count": sum(e["kind"] == "INK_OBSERVATION" for e in self.ledger.events),
            "pencil_count": sum(e["kind"] == "PENCIL_PROPOSAL" for e in self.ledger.events),
            "proof_chain": deepcopy(self.ledger.events),
            "proof_chain_tip": self.ledger.events[-1]["sha256"],
            "limitations": ["synthetic source, not an independently authenticated witness",
                            "hashes prove integrity within this fixture, not worldly truth",
                            "no construction, physical measurement, or external action",
                            "not an autonomous general reasoning agent"],
        }
