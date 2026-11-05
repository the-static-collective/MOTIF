"""MOTIF-020F: read the exact, indexed planZ public plan pointers without authority.

The upstream bytes and validator are copied unchanged from planZ/main at the
captured edition. The native Node adapter invokes planZ's own schema validator.
No GitHub network fetch, private data, plan mutations or field action occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Mapping


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PlanPointer:
    id: str
    title: str
    source: str
    disposition: str
    next_gate: str
    blocked_by: tuple[str, ...]
    related: tuple[str, ...]
    field_outcome: str
    execution_allowed: bool
    third_party_approval: str

    def __post_init__(self):
        if (not self.id or not self.source.startswith("https://github.com/the-static-collective/")
                or not self.blocked_by or self.field_outcome != "NOT_VERIFIED"
                or self.execution_allowed or self.third_party_approval != "NOT_ESTABLISHED"):
            raise ValueError("HOLD_INVALID_PLANZ_SOURCE_BOUNDARY")


@dataclass(frozen=True)
class ReadonlySnapshot:
    edition: str
    reviewed_on: str
    git_blob: str
    sha256: str
    planz_validator_git_blob: str
    plans: tuple[PlanPointer, ...]
    authority: str = "INDEX_ONLY"
    temporal_fact: str = "NONE_IN_ATTENTION_INDEX"
    external_execution: bool = False

    def get(self, plan_id: str) -> PlanPointer:
        match = next((x for x in self.plans if x.id == plan_id), None)
        if match is None:
            raise KeyError("HOLD_UNKNOWN_PLANZ_ID:" + plan_id)
        return match


def read_planz_snapshot() -> ReadonlySnapshot:
    """Run exact native validator with source pins; refuse any drift or error."""
    try:
        process = subprocess.run(
            ["node", str(ROOT / "planz_bridge.mjs")],
            input="", text=True, capture_output=True,
            timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("HOLD_NATIVE_PLANZ_VALIDATOR_UNAVAILABLE") from exc
    if process.returncode != 0:
        raise ValueError("HOLD_PLANZ_SOURCE_VALIDATION:" + process.stderr[:220])
    try:
        data = json.loads(process.stdout)
        if (data["schema"] != "motif020f.planz-readonly-snapshot/v0"
                or data["source_authority"] != "INDEX_ONLY"
                or data["temporal_fact"] != "NONE_IN_ATTENTION_INDEX"
                or data["field_outcome_established"] is not False
                or data["execution_authority"] != "NONE"
                or data["dispatch"] is not False):
            raise ValueError("HOLD_PLANZ_BOUNDARY")
        plans = tuple(
            PlanPointer(
                id=entry["id"], title=entry["title"], source=entry["source"],
                disposition=entry["disposition"], next_gate=entry["nextGate"],
                blocked_by=tuple(entry["blockedBy"]),
                related=tuple(entry["related"]),
                field_outcome=entry["fieldOutcome"],
                execution_allowed=entry["executionAllowed"],
                third_party_approval=entry["thirdPartyApproval"],
            ) for entry in data["source_entries"]
        )
        return ReadonlySnapshot(
            edition=data["source_edition"],
            reviewed_on=data["published_reviewed_on"],
            git_blob=data["source_pins"]["feed"]["git_blob"],
            sha256=data["source_pins"]["feed"]["sha256"],
            planz_validator_git_blob=data["source_pins"]["validator"]["git_blob"],
            plans=plans,
        )
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("HOLD_UNPARSABLE_PLANZ_SOURCE") from exc
