"""LAW-FORGE-007 local JSON research desk: first-class callable lookup skill.

Accepts typed synthetic input, emits inspectable proposal-only cartridges,
and predicts only witnessed configurations at an unchanged source revision.
No network, file persistence, source discovery, or real-world authority.
"""
from __future__ import annotations
import json
import sys
from lookup import Contract, Reading, LookupSkill, assimilate

SCHEMA = "motif.law-forge.lookup-desk.v1"


def dispatch(request):
    try:
        if not isinstance(request, dict) or set(request) not in (
            {"schema", "action", "contract", "observations"},
            {"schema", "action", "cartridge", "contract", "controls"}
        ) or request["schema"] != SCHEMA:
            raise ValueError("Invalid strict lookup-desk request")
        if request["action"] == "assimilate":
            contract = Contract.from_packet(request["contract"])
            if not isinstance(request["observations"], list):
                raise ValueError("Observations must be a finite array")
            if len(request["observations"]) > 2 ** contract.width:
                raise ValueError("More than the finite source-domain capacity")
            observations = []
            for row in request["observations"]:
                if (not isinstance(row, dict) or set(row) != {
                    "inputs", "outcome", "contract_id", "provenance"
                } or not isinstance(row["inputs"], list)):
                    raise ValueError("Malformed synthetic observation")
                observations.append(Reading(tuple(row["inputs"]), row["outcome"],
                                            row["contract_id"], row["provenance"]))
            model = assimilate(contract, observations)
            return {"schema": SCHEMA, "status": "PROPOSE_ONLY",
                    "cartridge": model.packet(), "real_world_authority": False}
        if request["action"] == "predict":
            current = Contract.from_packet(request["contract"])
            model = LookupSkill.from_packet(request["cartridge"])
            response = model.predict(request["controls"], current)
            return {"schema": SCHEMA, **response}
        raise ValueError("Unsupported research desk action")
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        return {"schema": SCHEMA, "status": "REFUSE",
                "reason": str(exc), "real_world_authority": False}


def main():
    try:
        payload = json.load(sys.stdin)
        output = dispatch(payload)
    except (ValueError, TypeError) as error:
        output = {"schema": SCHEMA, "status": "REFUSE",
                  "reason": str(error), "real_world_authority": False}
    print(json.dumps(output, sort_keys=True))
    return 0 if output["status"] != "REFUSE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
