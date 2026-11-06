"""REASON-007 Discovery Market: evidence-gated offers, not financial tokens.

This market selects a read-only task method from bounded source-owned bids.
All costs are explicit synthetic units; no credits can be traded or spent.
No bid can grant network, shell, database or other external authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import json
import re

from compiler import HOLD, digest, validate
from receiver import Receiver
from source import Case, bfs_truth, deployment

SCHEMA = "motif.reason.discovery-market.v1"
ALLOWED = {"COMPILE_SENSOR", "DIRECT_CLASSICAL_QUERY", "ABSTAIN"}
NAME = re.compile(r"^[A-Za-z0-9_.:-]{1,72}$")
COST = {"training_label":0.5, "certification_label":0.5,
        "compile":2.0, "inference":0.25, "direct_query":1.5,
        "omission":6.0}
MAX_SIZE = 25000


@dataclass(frozen=True)
class Bid:
    bid_id: str
    author: str
    kind: str
    advertised_gain: float = 0.0
    depends_on: tuple[str,...] = ()

    def __post_init__(self):
        if (not NAME.fullmatch(self.bid_id or "")
                or not NAME.fullmatch(self.author or "")
                or self.kind not in ALLOWED
                or type(self.advertised_gain) not in (int,float)
                or not isfinite(self.advertised_gain)
                or not isinstance(self.depends_on,tuple)
                or len(self.depends_on)>3
                or any(not NAME.fullmatch(x or "") for x in self.depends_on)
                or self.bid_id in self.depends_on):
            raise HOLD("Unbounded, circular or unauthorized market offer")


class DiscoveryMarket:
    def __init__(self, raw_method, receiver, bids, cases):
        self.method = validate(raw_method)
        if (not isinstance(receiver,Receiver)
                or not receiver.admitted
                or receiver.packet["checksum_sha256"] != self.method["checksum_sha256"]
                or not isinstance(bids,tuple) or not 1 <= len(bids) <= 8
                or any(not isinstance(b,Bid) for b in bids)
                or len({b.bid_id for b in bids}) != len(bids)
                or not isinstance(cases,tuple) or not 1 <= len(cases) <= 32
                or any(not isinstance(c,Case) or c.variant=="cedar" for c in cases)
                or len({(c.mask,c.variant) for c in cases}) != len(cases)):
            raise HOLD("No independently certified method, unique bids or bounded tasks")
        ids={b.bid_id for b in bids}
        if any(d not in ids for b in bids for d in b.depends_on):
            raise HOLD("Missing referenced predecessor")
        outgoing={b.bid_id:set(b.depends_on) for b in bids}
        def visit(x,chain):
            if x in chain:raise HOLD("Self-referential credit loop")
            for y in outgoing[x]:
                visit(y,chain|{x})
        for key in outgoing:visit(key,set())
        self.receiver=receiver
        self.bids=bids
        self.cases=cases
        self.n=len(cases)

    def estimate(self,kind):
        n=self.n
        if kind=="COMPILE_SENSOR":
            return (len(self.method["training_receipts"])*COST["training_label"]
                    + 11*COST["certification_label"]+COST["compile"]
                    + n*COST["inference"])
        if kind=="DIRECT_CLASSICAL_QUERY":
            return n*COST["direct_query"]
        if kind=="ABSTAIN":
            return n*COST["omission"]
        raise HOLD("Unknown offer semantics")

    def _semantic_key(self,bid):
        # The same sensor, renamed by another author, is ONE contribution.
        return digest({"kind":bid.kind,
                       "program":self.method["program"] if bid.kind=="COMPILE_SENSOR" else None,
                       "source":self.method["source_owner_blob"]})

    def evaluate(self):
        events=[]
        seen=set()
        for b in self.bids:
            fingerprint=self._semantic_key(b)
            novel=fingerprint not in seen
            seen.add(fingerprint)
            events.append({"id":b.bid_id,"author":b.author,"kind":b.kind,
                           "semantic_key":fingerprint,
                           "new_validated_offer":novel,
                           "credit_for_duplicate":0,
                           "advertised_gain_ignored":True,
                           "estimated_cost":round(self.estimate(b.kind),6)})
        eligible=[e for e in events if e["new_validated_offer"]]
        choice=min(eligible,key=lambda x:(x["estimated_cost"],x["semantic_key"]))
        winner=choice["kind"]
        verified=[]
        for c in self.cases:
            actual=bfs_truth(c)  # INDEPENDENT SOURCE OWNER: never used in bidding
            if winner=="COMPILE_SENSOR":
                predicted=self.receiver.suggest(c)["prediction"]
            elif winner=="DIRECT_CLASSICAL_QUERY":
                predicted=actual  # explicit owner query, source-owned baseline
            else:
                predicted=None  # no claimed conclusion
            verified.append({"case":[c.variant,c.mask],"source_truth":actual,
                             "market_answer":predicted,
                             "correct":predicted is not None and predicted==actual})
        accurate=sum(x["correct"] for x in verified)
        # Reward is computed AFTER independently verifying all answers.
        direct_cost=self.estimate("DIRECT_CLASSICAL_QUERY")
        avoided=round(max(0.0,direct_cost-choice["estimated_cost"]),6)
        credited=avoided if accurate==self.n and winner=="COMPILE_SENSOR" else 0.0
        # No credit for advertising large gain, repetitions or no answers.
        for event in events:
            event["earned_nontransferable_utility_points"]=(
                credited if event["semantic_key"]==choice["semantic_key"]
                and event["id"]==choice["id"] else 0.0)
        return {"schema":SCHEMA,
                "method_source_sha256":self.method["checksum_sha256"],
                "independent_certification_digest":self.receiver.review_digest,
                "task_count":self.n,"eligible_offer_count":len(eligible),
                "duplicate_offers":len(events)-len(eligible),
                "offers":events,
                "winning_offer":choice["id"],
                "winning_kind":winner,
                "independently_verified_correct":accurate,
                "incorrect_or_abstained":self.n-accurate,
                "reviewed_tasks":verified,
                "hypothetical_costs":dict(COST),
                "winner_hypothetical_cost":choice["estimated_cost"],
                "direct_query_hypothetical_cost":round(direct_cost,6),
                "marginal_verified_savings_points":credited,
                "real_money_or_tradeable_credits":False,
                "strong_classical_bfs_full_information_correct":self.n,
                "classical_optimizing_planner_may_tie_or_outperform":True,
                "any_external_actions":False,"real_world_authority":False}


def packet(raw_method, receiver, bids, cases):
    summary=DiscoveryMarket(raw_method,receiver,bids,cases).evaluate()
    body={"schema":"motif.reason.discovery-market-receipt.v1",
          "source_method":validate(raw_method),
          "bids":[{"bid_id":b.bid_id,"author":b.author,"kind":b.kind,
                   "advertised_gain":b.advertised_gain,
                   "depends_on":list(b.depends_on)} for b in bids],
          "portfolio":[{"mask":c.mask,"variant":c.variant} for c in cases],
          "receipt":summary,
          "stage":"LOCAL_SYNTHETIC_READ_ONLY",
          "external_execution":False,"real_world_authority":False}
    obj=dict(body,checksum_sha256=digest(body))
    raw=json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_SIZE:
        raise HOLD("Market receipt exceeded finite bounds")
    return raw


def validate_packet(raw, receiver):
    if not isinstance(raw,str) or len(raw.encode())>MAX_SIZE:
        raise HOLD("Missing/oversized market receipt")
    try:doc=json.loads(raw)
    except (ValueError,TypeError) as exc:raise HOLD("Malformed market result") from exc
    keys={"schema","source_method","bids","portfolio","receipt","stage",
          "external_execution","real_world_authority","checksum_sha256"}
    if not isinstance(doc,dict) or set(doc)!=keys:
        raise HOLD("Unrecognized market claim")
    if (doc["schema"]!="motif.reason.discovery-market-receipt.v1"
            or doc["stage"]!="LOCAL_SYNTHETIC_READ_ONLY"
            or doc["external_execution"] is not False
            or doc["real_world_authority"] is not False
            or doc["checksum_sha256"]!=digest({k:v for k,v in doc.items()
                                              if k!="checksum_sha256"})):
        raise HOLD("Altered scope or fabricated integrity")
    try:
        bids=tuple(Bid(b["bid_id"],b["author"],b["kind"],b["advertised_gain"],
                       tuple(b["depends_on"])) for b in doc["bids"])
        cases=tuple(Case(c["mask"],c["variant"]) for c in doc["portfolio"])
        expected=json.loads(packet(json.dumps(doc["source_method"]),receiver,bids,cases))
    except (KeyError,TypeError,ValueError) as exc:
        raise HOLD("Unreplayable source market receipt") from exc
    if expected!=doc:
        raise HOLD("Winner, score or source truth cannot be replayed")
    return doc
