"""LAW-FORGE-008 executable local Question-Machine-facing JSON-stdio desk.

No source oracle, private connector, web request, or GRAFT capability is
connected. The caller may prepare a bounded typed source questionnaire and
receive a PROPOSE_ONLY experiment; a source owner must decide whether and
how to execute it. Predict never fills unknown evidence with an invented fact.
"""
from __future__ import annotations

import json
import sys

from learner import (
    MAX_QUERIES, Observation, Question, SourceContract, choose_question,
    exact_lookup, make_desk, digest
)

SCHEMA = "motif.law-forge.unknown-world-desk.v1"


def dispatch(request):
    try:
        if (not isinstance(request, dict) or set(request) not in (
            {"schema", "action", "contract", "observations",
             "catalog", "remaining_budget", "method"},
            {"schema", "action", "contract", "observations",
             "controls", "method"}
        ) or request["schema"] != SCHEMA):
            raise ValueError("Strict research desk envelope required")
        contract = SourceContract.from_packet(request["contract"])
        if not isinstance(request["observations"], list) or not (
            1 <= len(request["observations"]) <= MAX_QUERIES + 4
        ):
            raise ValueError("Finite witnessed observations required")
        records = []
        for raw in request["observations"]:
            if (not isinstance(raw, dict) or set(raw) != {
                "x", "y", "contract_id", "provenance"
            } or not isinstance(raw["x"], list)):
                raise ValueError("Malformed source-owned observation")
            records.append(Observation(tuple(raw["x"]), raw["y"],
                                       raw["contract_id"], raw["provenance"]))
        known = exact_lookup(contract, records)
        if request["action"] == "propose":
            if not isinstance(request["catalog"], list) or len(request["catalog"]) > 160:
                raise ValueError("Owner question catalog must be bounded")
            qpool = tuple(Question.from_packet(row) for row in request["catalog"])
            remaining = request["remaining_budget"]
            if type(remaining) is not int or not 0 <= remaining <= MAX_QUERIES:
                raise ValueError("Excessive or noninteger experiment cost")
            candidate = choose_question(
                known, qpool, request["method"], remaining, ()
            )
            return {
                "schema": SCHEMA,
                "status": ("PROPOSE_ONLY_SYNTHETIC_QUESTION"
                           if candidate else "HOLD_NO_SUPPORTED_QUERY"),
                "query": candidate.packet() if candidate else None,
                "evidence_id": digest({
                    "contract": contract.packet(),
                    "rows": [[list(x), y] for x, y in known]
                }),
                "owner_must_execute": True,
                "real_world_authority": False
            }
        if request["action"] == "predict":
            desk = make_desk(contract, records, request["method"])
            result = desk.predict(request["controls"], contract)
            return {"schema": SCHEMA, "cartridge_id": desk.id,
                    "real_world_authority": False, **result}
        raise ValueError("Unknown research desk operation")
    except (KeyError, TypeError, ValueError, IndexError) as error:
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
