"""LAW-FORGE-010 strict local JSON-stdio blind falsifier.

Actions: open, propose, ingest, diagnose, predict.
This is a *proposal-only* synthetic research desk. The source owner executes
actual questions. Typed observation provenance is not cryptographic proof.
"""
from __future__ import annotations

import json
import sys

from entropy_cartridge import EntropyCartridge
from falsifier import AuditLedger, POLICIES
from learner import Observation, Question, SourceContract
from learner import make_desk

SCHEMA = "motif.reason-cartridge.blind-falsifier-desk.v1"


def read_observation(row):
    if (not isinstance(row, dict) or set(row) != {
        "x", "y", "contract_id", "provenance"
    } or not isinstance(row["x"], list)):
        raise ValueError("Invalid typed synthetic source observation")
    return Observation(tuple(row["x"]), row["y"],
                       row["contract_id"], row["provenance"])


def dispatch(request):
    try:
        if not isinstance(request, dict) or request.get("schema") != SCHEMA:
            raise ValueError("Invalid blind-falsifier protocol")
        action = request.get("action")
        expected = {
            "open": {"schema", "action", "learning_cartridge", "policy"},
            "propose": {"schema", "action", "audit_cartridge", "catalog"},
            "ingest": {"schema", "action", "audit_cartridge", "catalog",
                       "proposed_challenge", "owner_observation"},
            "diagnose": {"schema", "action", "audit_cartridge"},
            "predict": {"schema", "action", "audit_cartridge",
                        "source", "x"}
        }
        if action not in expected or set(request) != expected[action]:
            raise ValueError("Unsupported or expanded action envelope")
        if action == "open":
            learning = EntropyCartridge.from_packet(request["learning_cartridge"])
            if request["policy"] not in POLICIES:
                raise ValueError("Unknown audit method")
            ledger = AuditLedger(learning, audit_policy=request["policy"])
            return {"schema": SCHEMA, "status": "PROPOSE_ONLY",
                    "audit_cartridge": ledger.packet(),
                    "real_world_authority": False}

        ledger = AuditLedger.from_packet(request["audit_cartridge"])
        if action in ("propose", "ingest"):
            if not isinstance(request["catalog"], list):
                raise ValueError("Source catalog must be a strict list")
            catalog = tuple(Question.from_packet(q) for q in request["catalog"])
            proposed = ledger.propose(catalog)
            if action == "propose":
                return {"schema": SCHEMA,
                        "status": ("PROPOSE_ONLY_SOURCE_QUESTION" if proposed
                                   else "HOLD_NO_SUPPORTED_CHALLENGE"),
                        "question": proposed.packet() if proposed else None,
                        "real_world_authority": False}
            if (proposed is None
                    or proposed.packet() != request["proposed_challenge"]):
                raise ValueError("Question altered or stale")
            reply = read_observation(request["owner_observation"])
            amended = ledger.ingest(proposed, reply, catalog)
            return {"schema": SCHEMA, "status": "PROPOSE_ONLY",
                    "audit_cartridge": amended.packet(),
                    "receipt_signature_verified": False,
                    "real_world_authority": False}

        if action == "diagnose":
            gap = ledger.diagnosis()
            return {"schema": SCHEMA,
                    "status": ("HOLD_GRAMMAR_GAP" if gap
                               else "NO_WITNESSED_GRAMMAR_GAP"),
                    "grammar_gap": gap.packet() if gap else None,
                    "real_world_authority": False}

        present = SourceContract.from_packet(request["source"])
        desk = make_desk(ledger.learning.source,
                         ledger.evidence.observations,
                         "classical_entropy")
        return {"schema": SCHEMA, "audit_id": ledger.id,
                "real_world_authority": False,
                **desk.predict(request["x"], present)}
    except (ValueError, TypeError, KeyError, IndexError) as error:
        return {"schema": SCHEMA, "status": "REFUSE",
                "reason": str(error), "real_world_authority": False}


def main():
    try:
        result = dispatch(json.load(sys.stdin))
    except (ValueError, TypeError) as error:
        result = {"schema": SCHEMA, "status": "REFUSE",
                  "reason": str(error), "real_world_authority": False}
    print(json.dumps(result, sort_keys=True))
    return 2 if result["status"] == "REFUSE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
