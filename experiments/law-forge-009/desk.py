"""LAW-FORGE-009 portable entropy reason-cartridge JSON-stdio gateway.

create, propose, ingest, predict, diagnose. It never calls the source or
claims that a supplied synthetic witness is cryptographically authenticated.
Every submitted request must have an exact action-specific schema.
"""
from __future__ import annotations

import json
import sys

from entropy_cartridge import EntropyCartridge
from gap import diagnose
from learner import Observation, Question, SourceContract

SCHEMA = "motif.reason-cartridge.entropy-desk.v1"


def reading(row):
    if (not isinstance(row, dict) or set(row) != {
        "x", "y", "contract_id", "provenance"
    } or not isinstance(row["x"], list)):
        raise ValueError("Strict owner observation required")
    return Observation(tuple(row["x"]), row["y"], row["contract_id"],
                       row["provenance"])


def dispatch(req):
    try:
        if not isinstance(req, dict) or req.get("schema") != SCHEMA:
            raise ValueError("Unrecognized entropy desk schema")
        action = req.get("action")
        keys = {
            "create": {"schema", "action", "source", "observations"},
            "propose": {"schema", "action", "cartridge", "catalog",
                        "remaining_budget"},
            "ingest": {"schema", "action", "cartridge", "catalog",
                       "remaining_budget", "owner_observation",
                       "proposed_question"},
            "predict": {"schema", "action", "cartridge", "source", "x"},
            "diagnose": {"schema", "action", "cartridge"}
        }
        if action not in keys or set(req) != keys[action]:
            raise ValueError("Unexpected fields or unsupported operation")

        if action == "create":
            source = SourceContract.from_packet(req["source"])
            if not isinstance(req["observations"], list):
                raise ValueError("Source observations must be a list")
            skill = EntropyCartridge(
                source, tuple(reading(row) for row in req["observations"])
            )
            return {"schema": SCHEMA, "status": "PROPOSE_ONLY",
                    "cartridge": skill.packet(), "real_world_authority": False}

        skill = EntropyCartridge.from_packet(req["cartridge"])
        if action in ("propose", "ingest"):
            if not isinstance(req["catalog"], list):
                raise ValueError("Catalog must be a bounded list")
            catalog = tuple(Question.from_packet(q) for q in req["catalog"])
            proposed = skill.propose(catalog, req["remaining_budget"])
            if action == "propose":
                return {"schema": SCHEMA,
                        "status": ("PROPOSE_ONLY" if proposed
                                   else "HOLD_NO_DISCRIMINATING_QUERY"),
                        "proposal": proposed.packet() if proposed else None,
                        "real_world_authority": False}
            if proposed is None or not isinstance(req["proposed_question"], dict):
                raise ValueError("No outstanding source-owned proposal")
            if proposed.packet() != req["proposed_question"]:
                raise ValueError("Stale or changed proposed source question")
            observed = reading(req["owner_observation"])
            updated = skill.ingest(proposed, observed, catalog)
            return {"schema": SCHEMA, "status": "PROPOSE_ONLY",
                    "cartridge": updated.packet(),
                    "owner_receipt_authentication": "NOT_PROVIDED",
                    "real_world_authority": False}

        if action == "predict":
            present = SourceContract.from_packet(req["source"])
            response = skill.predict(req["x"], present)
            return {"schema": SCHEMA, **response}

        gap = diagnose(skill)
        return {"schema": SCHEMA,
                "status": ("HOLD_NO_RULE_IN_DECLARED_GRAMMAR" if gap
                           else "COMPATIBLE_WITH_DECLARED_GRAMMAR"),
                "grammar_gap": gap.packet() if gap else None,
                "real_world_authority": False}
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        return {"schema": SCHEMA, "status": "REFUSE",
                "reason": str(exc), "real_world_authority": False}


def main():
    try:
        out = dispatch(json.load(sys.stdin))
    except (ValueError, TypeError) as exc:
        out = {"schema": SCHEMA, "status": "REFUSE",
               "reason": str(exc), "real_world_authority": False}
    print(json.dumps(out, sort_keys=True))
    return 2 if out["status"] == "REFUSE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
