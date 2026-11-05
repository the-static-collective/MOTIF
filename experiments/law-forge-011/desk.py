"""MOTIF-011 strict local signed-counterfactual reason-cartridge JSON desk.

Opening the desk does not permit access to any source. All questions are
proposal-only, and responses must arrive as source-labeled synthetic
observations. No authentication of real source identity is claimed.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-009"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-008"))

from entropy_cartridge import EntropyCartridge
from learner import Observation, Question, SourceContract, make_desk
from signed_critic import SignedAudit, POLICIES

SCHEMA="motif.reason-cartridge.signed-critic-desk.v1"


def witness(item):
    if (not isinstance(item,dict) or set(item) != {
        "x","y","contract_id","provenance"
    } or not isinstance(item["x"],list)):
        raise ValueError("Malformed typed source witness")
    return Observation(tuple(item["x"]),item["y"],
                       item["contract_id"],item["provenance"])


def dispatch(query):
    try:
        if not isinstance(query,dict) or query.get("schema") != SCHEMA:
            raise ValueError("Unsupported bounded research protocol")
        action=query.get("action")
        valid={
            "open":{"schema","action","learning_cartridge","policy"},
            "propose":{"schema","action","audit_cartridge","catalog"},
            "ingest":{"schema","action","audit_cartridge","catalog",
                      "proposed_question","source_observation"},
            "diagnose":{"schema","action","audit_cartridge"},
            "predict":{"schema","action","audit_cartridge","source","x"}
        }
        if action not in valid or set(query)!=valid[action]:
            raise ValueError("Unrecognized or expanded research action")
        if action=="open":
            prior=EntropyCartridge.from_packet(query["learning_cartridge"])
            if query["policy"] not in POLICIES:
                raise ValueError("Unregistered audit policy")
            result=SignedAudit(prior,query["policy"])
            return {"schema":SCHEMA,"status":"PROPOSE_ONLY",
                    "audit_cartridge":result.packet(),"real_world_authority":False}

        ledger=SignedAudit.from_packet(query["audit_cartridge"])
        if action in ("propose","ingest"):
            if not isinstance(query["catalog"],list):
                raise ValueError("Source catalog must be a typed list")
            cards=tuple(Question.from_packet(x) for x in query["catalog"])
            candidate=ledger.propose(cards)
            if action=="propose":
                return {"schema":SCHEMA,
                        "status":("PROPOSE_ONLY_SOURCE_QUESTION" if candidate
                                  else "HOLD_NO_SUPPORTED_CHALLENGE"),
                        "question":candidate.packet() if candidate else None,
                        "real_world_authority":False}
            if candidate is None or query["proposed_question"]!=candidate.packet():
                raise ValueError("Stale, altered or absent owner question")
            answer=witness(query["source_observation"])
            updated=ledger.ingest(candidate,answer,cards)
            return {"schema":SCHEMA,"status":"PROPOSE_ONLY",
                    "audit_cartridge":updated.packet(),
                    "source_signature_verified":False,
                    "real_world_authority":False}
        if action=="diagnose":
            gap=ledger.grammar_gap()
            return {"schema":SCHEMA,
                    "status":("HOLD_RELATIVE_GRAMMAR_GAP" if gap
                              else "NO_WITNESSED_GRAMMAR_GAP"),
                    "gap":gap.packet() if gap else None,
                    "real_world_authority":False}
        present=SourceContract.from_packet(query["source"])
        compiled=make_desk(ledger.learning.source,
                           ledger.evidence.observations,"classical_entropy")
        outcome=compiled.predict(query["x"],present)
        return {"schema":SCHEMA,"cartridge_id":ledger.id,
                **outcome,"real_world_authority":False}
    except (KeyError,ValueError,TypeError,IndexError) as exc:
        return {"schema":SCHEMA,"status":"REFUSE","reason":str(exc),
                "real_world_authority":False}


if __name__=="__main__":
    try:
        result=dispatch(json.load(sys.stdin))
    except (ValueError,TypeError) as exc:
        result={"schema":SCHEMA,"status":"REFUSE","reason":str(exc),
                "real_world_authority":False}
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(2 if result["status"]=="REFUSE" else 0)
