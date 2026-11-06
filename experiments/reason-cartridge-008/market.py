"""Discovery Market 008: pay for a missing macro only when it proves useful.

Hypothetical units only, no tradable token, autonomous code writing, network
access or remote invocation. Full independent correctness is checked AFTER the
bid and no external authority can be transferred.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1
from math import isfinite
from pathlib import Path
import json
import re
import sys

from discover import HOLD, validate, digest
from receiver import Receiver
from source import Case, bfs_truth

LEDGER_PATH=Path(__file__).resolve().parents[1]/"reason-cartridge-006"/"commonwealth.py"
LEDGER_BLOB="4f0e897b19e658f5f01a0a2e91a472ad023e1b8f"
SCHEMA="motif.reason.missing-primitive-market.v1"
TYPES=("GAP_REPAIR_MACRO","DIRECT_CLASSICAL_BFS","HOLD_NO_ANSWER")
SAFE=re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
COST={
    "teaching_label":0.5,
    "certification_label":0.5,
    "new_macro_design":3.0,
    "macro_inference":0.25,
    "source_bfs":1.5,
    "omission":6.0,
}


def pin_ledger():
    blob=LEDGER_PATH.read_bytes()
    current=sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest()
    if current!=LEDGER_BLOB:
        raise HOLD("Commonwealth owner ledger was changed")
    return current


pin_ledger()
sys.path.append(str(LEDGER_PATH.parent))
from commonwealth import Ledger


@dataclass(frozen=True)
class Bid:
    id: str
    author: str
    method: str
    asserted_gain: float=0.0
    dependencies: tuple[str,...]=()

    def __post_init__(self):
        if (not SAFE.fullmatch(self.id or "")
                or not SAFE.fullmatch(self.author or "")
                or self.method not in TYPES
                or type(self.asserted_gain) not in (float,int)
                or not isfinite(self.asserted_gain)
                or not isinstance(self.dependencies,tuple)
                or len(self.dependencies)>3
                or any(not SAFE.fullmatch(k or "") for k in self.dependencies)
                or self.id in self.dependencies):
            raise HOLD("Unbounded or unauthorized market bid")


class DiscoveryMarket:
    def __init__(self,raw,receiver,bids,cases):
        self.method=validate(raw)
        if (not isinstance(receiver,Receiver) or not receiver.admitted
                or receiver.packet["checksum_sha256"] != self.method["checksum_sha256"]
                or not isinstance(bids,tuple) or not 1<=len(bids)<=8
                or any(not isinstance(b,Bid) for b in bids)
                or len({b.id for b in bids})!=len(bids)
                or not isinstance(cases,tuple) or not 1<=len(cases)<=64
                or any(not isinstance(c,Case) or c.variant=="cedar" for c in cases)
                or len({(c.variant,c.mask) for c in cases})!=len(cases)):
            raise HOLD("Unknown method, unreviewed authority or unbounded portfolio")
        ids={b.id for b in bids}
        if any(d not in ids for b in bids for d in b.dependencies):
            raise HOLD("Missing dependency")
        links={b.id:set(b.dependencies) for b in bids}
        def visit(k,seen):
            if k in seen:
                raise HOLD("Recursive self-bidding credit loop")
            for nxt in links[k]:
                visit(nxt,seen|{k})
        for item in links:visit(item,set())
        self.bids=bids
        self.cases=cases
        self.receiver=receiver

    def cost(self,kind):
        n=len(self.cases)
        if kind=="GAP_REPAIR_MACRO":
            return (len(self.method["training_evidence"])*COST["teaching_label"]
                   +27*COST["certification_label"]+COST["new_macro_design"]
                   +n*COST["macro_inference"])
        if kind=="DIRECT_CLASSICAL_BFS":
            return n*COST["source_bfs"]
        if kind=="HOLD_NO_ANSWER":
            return n*COST["omission"]
        raise HOLD("Unknown candidate")

    def fingerprint(self,bid):
        # Content rather than proponent identity controls contribution credit.
        return digest({"method":bid.method,
                       "source":self.method["source_owner_git_blob"],
                       "program":self.method["proposed_extension"]["program"]
                                 if bid.method=="GAP_REPAIR_MACRO" else None})

    def evaluate(self):
        seen=set()
        bids=[]
        for bid in self.bids:
            key=self.fingerprint(bid)
            distinct=key not in seen
            seen.add(key)
            bids.append({
                "id":bid.id,"kind":bid.method,
                "semantic_key":key,
                "unseen_offer":distinct,
                "asserted_gain_ignored":True,
                "hypothetical_cost":round(self.cost(bid.method),6),
                "nontransferable_utility_reward":0,
            })
        eligible=[b for b in bids if b["unseen_offer"]]
        winner=min(eligible,key=lambda b:(b["hypothetical_cost"],b["semantic_key"]))
        answers=[]
        for case in self.cases:
            actual=bfs_truth(case)  # independent evaluator never supplies training data
            if winner["kind"]=="GAP_REPAIR_MACRO":
                prediction=self.receiver.suggest(case)["prediction"]
            elif winner["kind"]=="DIRECT_CLASSICAL_BFS":
                prediction=actual
            else:
                prediction=None
            answers.append({
                "mask":case.mask,"variant":case.variant,
                "source_reachable":actual,"proposed_answer":prediction,
                "correct":prediction is not None and prediction==actual,
            })
        success=sum(x["correct"] for x in answers)
        direct=round(self.cost("DIRECT_CLASSICAL_BFS"),6)
        saved=round(max(0,direct-winner["hypothetical_cost"]),6)
        verified_value=(saved if winner["kind"]=="GAP_REPAIR_MACRO"
                        and success==len(answers) else 0)
        for b in bids:
            if b["id"]==winner["id"]:
                b["nontransferable_utility_reward"]=verified_value
        ledger=Ledger()
        if verified_value>0:
            witness={
                "program":self.method["checksum_sha256"],
                "source_evidence":self.method["training_evidence_digest"],
                "certification":self.receiver.digest,
                "portfolio_hash":digest([(c.variant,c.mask) for c in self.cases]),
                "verified_correct":success,
            }
            first=ledger.add("DISCOVERY_008","VERIFIED_MACRO",witness,
                             "LOWER_DECLARED_REPEATED_QUERY_COST",True)
            repeated=ledger.repeat(first)
            if repeated["score"]!=0 or ledger.summary()["new_source_facts"]!=0:
                raise HOLD("Prior Commonwealth counted duplicate or invented facts")
        else:
            first=None
            repeated=None
        return {
            "schema":SCHEMA,"market_source_blob":pin_ledger(),
            "source_method_sha256":self.method["checksum_sha256"],
            "certification_digest":self.receiver.digest,
            "task_count":len(answers),
            "winning_offer":winner["id"],"winning_method":winner["kind"],
            "winning_hypothetical_cost":winner["hypothetical_cost"],
            "direct_classical_hypothetical_cost":direct,
            "independently_correct":success,
            "incorrect_or_abstained":len(answers)-success,
            "source_checked_answers":answers,
            "offers":bids,
            "duplicated_offers":len(bids)-len(eligible),
            "independent_evidence_gated_savings_points":verified_value,
            "commonwealth_new_method_credit":first["score"] if first else 0,
            "commonwealth_duplicate_credit":repeated["score"] if repeated else 0,
            "commonwealth_new_source_facts":ledger.summary()["new_source_facts"],
            "hypothetical_cost_model":dict(COST),
            "money_or_tradable_points":False,
            "classical_solver_with_full_information_correct":len(answers),
            "classical_optimizer_can_make_same_choice":True,
            "external_execution":False,"real_world_authority":False,
        }


def make_receipt(raw,receiver,bids,cases):
    result=DiscoveryMarket(raw,receiver,bids,cases).evaluate()
    document={
        "schema":"motif.reason.missing-primitive-market-receipt.v1",
        "source_method":validate(raw),
        "bids":[{"id":b.id,"author":b.author,"method":b.method,
                 "asserted_gain":b.asserted_gain,
                 "dependencies":list(b.dependencies)} for b in bids],
        "portfolio":[{"mask":c.mask,"variant":c.variant,"topology":c.topology}
                     for c in cases],
        "market":result,
        "status":"PROPOSE_ONLY",
        "external_execution":False,"real_world_authority":False,
    }
    return json.dumps(dict(document,checksum_sha256=digest(document)),
                      sort_keys=True,indent=2,allow_nan=False)+"\n"


def validate_receipt(raw,receiver):
    if not isinstance(raw,str) or len(raw.encode())>50000:
        raise HOLD("Overlarge or absent market packet")
    try:obj=json.loads(raw)
    except (ValueError,TypeError) as exc:
        raise HOLD("Malformed market packet") from exc
    keys={"schema","source_method","bids","portfolio","market","status",
          "external_execution","real_world_authority","checksum_sha256"}
    if not isinstance(obj,dict) or set(obj)!=keys:
        raise HOLD("Unknown market field")
    if (obj["schema"]!="motif.reason.missing-primitive-market-receipt.v1"
            or obj["status"]!="PROPOSE_ONLY"
            or obj["external_execution"] is not False
            or obj["real_world_authority"] is not False
            or obj["checksum_sha256"]!=digest({k:v for k,v in obj.items()
                                              if k!="checksum_sha256"})):
        raise HOLD("Changed market scope or data hash")
    try:
        bids=tuple(Bid(x["id"],x["author"],x["method"],x["asserted_gain"],
                       tuple(x["dependencies"])) for x in obj["bids"])
        cases=tuple(Case(x["mask"],x["variant"],x["topology"])
                    for x in obj["portfolio"])
        replay=json.loads(make_receipt(json.dumps(obj["source_method"]),
                                       receiver,bids,cases))
    except (TypeError,KeyError,ValueError) as exc:
        raise HOLD("Claim cannot be source-replayed") from exc
    if replay!=obj:
        raise HOLD("Rehashed market score, authority or owner truth mismatch")
    return obj
