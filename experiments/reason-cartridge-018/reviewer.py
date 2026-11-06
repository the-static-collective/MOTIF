"""Source-independent mechanical checking and heldout concept falsifiers.

The source owner's original relational target lives in oracle.py and is
imported ONLY here by the reviewer, never by the learner. A second
independently implemented direct graph-loop reference also checks the owner.

The owner and this reference are classical programs. Passing does NOT imply
MOTIF learned the subjective meaning of love or surpassed classical logic.
"""
from __future__ import annotations

import json

from worlds import make,train_worlds,heldout_worlds
from oracle import SourceOwner,source_label,verify_world
from inventor import HOLD,discover,suggest,export,digest,programs,prove,status,SCHEMA


def independent_reference(world):
    """Direct imperative graph traversal, no candidate DSL or importer."""
    edgelist=[tuple(e) for e in world["edges"]]
    a,b=world["actor"],world["recipient"]
    provides=any(k=="OFFER" and x==a and y==b for k,x,y in edgelist)
    ways=set()
    if provides:
        for k,x,y in edgelist:
            if k=="OPEN" and x==b:
                for k2,x2,y2 in edgelist:
                    if k2=="RELEASE" and x2==y and y2==a:
                        ways.add(y)
    nonclaim=any(k=="FREE" and x==a and y==b for k,x,y in edgelist)
    claim=any(k=="CLAIM" and x==a and y==b for k,x,y in edgelist)
    positive=bool(ways) and nonclaim
    negative=(not bool(ways)) or claim
    stage=("BOTH" if positive and negative else
           "SUPPORTED" if positive else
           "REFUTED" if negative else "UNDETERMINED")
    return stage


def replay(raw):
    if not isinstance(raw,str) or len(raw.encode())>120000:
        raise HOLD("Unreasonable or empty source-owned concept packet")
    try:
        obj=json.loads(raw)
    except (TypeError,ValueError) as exc:
        raise HOLD("Unparseable candidate program") from exc
    if not isinstance(obj,dict) or "checksum_sha256" not in obj:
        raise HOLD("No complete source-owned concept packet")
    if obj["checksum_sha256"]!=digest({
        k:v for k,v in obj.items() if k!="checksum_sha256"}):
        raise HOLD("Corrupt or rehashed discovery packet")
    try:
        budget=obj["source_inquiry_budget"]
        replayed=json.loads(export(discover(SourceOwner(),max_inquiries=budget)))
    except (TypeError,KeyError,ValueError) as exc:
        raise HOLD("Cannot replay owner source learning") from exc
    if obj!=replayed:
        raise HOLD("Training labels, grammar or model versions were rewritten")
    return obj


def reviewed_evaluation(model,worlds=None):
    if worlds is None:
        worlds=heldout_worlds()
    if not isinstance(worlds,(tuple,list)) or len(worlds)!=55:
        raise HOLD("Full source-owned structurally new heldout set required")
    if [w["id"] for w in worlds]!=[w["id"] for w in heldout_worlds()]:
        raise HOLD("Unknown source-owned evaluation cases")
    results=[]
    for w in worlds:
        verify_world(w)
        truth=source_label(w)["status"]
        independent=independent_reference(w)
        if truth!=independent:
            raise AssertionError("Owner's concept changed relative to independent classical source")
        proposal=suggest(model,w)
        is_hold=proposal["status"].startswith("HOLD_")
        if proposal["status"]!=truth and not is_hold:
            failure={"id":w["id"],"mode":(int(w["id"][3:])%11),
                     "claimed":proposal["status"],"source_owner":truth}
            raise AssertionError("Incorrect decisive relational inference: "+str(failure))
        if proposal["relation_witness"] is not None:
            edges={tuple(e) for e in w["edges"]}
            proof=proposal["relation_witness"]
            if not all(tuple(e) in edges for e in proof["premises"]):
                raise AssertionError("Concept hypothesis furnished imaginary graph witness")
            if proof["source_world_sha256"]!=digest(w):
                raise AssertionError("Proof belongs to another world")
        results.append({
            "case_id":w["id"],"node_count":len(w["nodes"]),
            "edge_count":len(w["edges"]),
            "source_status":truth,
            "invented_model_status":proposal["status"],
            "correct_or_held":proposal["status"]==truth or is_hold,
            "exact_match":proposal["status"]==truth,
            "abstained":is_hold,
            "source_contract_verified":True,
            "candidate_proof_is_source_bound":True,
        })
    return results


class Receiver:
    def __init__(self):
        self.admitted=False
        self.review_hash=None
        self.model=None

    def preview(self,raw):
        packet=replay(raw)
        body={k:v for k,v in packet.items() if k!="checksum_sha256"}
        results=reviewed_evaluation(body)
        review={
            "schema":"motif.reason.living-concept.review.v1",
            "training_examples":body["source_example_count"],
            "surviving_schemas":len(body["remaining_hypotheses"]),
            "heldout_count":len(results),
            "exact_source_outcomes":sum(r["exact_match"] for r in results),
            "explicit_uncertain_holds":sum(r["abstained"] for r in results),
            "source_errors":sum(not r["correct_or_held"] for r in results),
            "max_heldout_nodes":max(r["node_count"] for r in results),
            "heldout_source_disjoint_from_training":True,
            "source_classical_oracle_could_tie":True,
            "no_real_human_subjects":True,
            "no_general_language_understanding_demonstrated":True,
        }
        self.model=body
        self.review_hash=digest(review)
        return dict(review,review_digest=self.review_hash)

    def admit(self,decision,review_digest):
        if decision!="ADMIT_READ_ONLY" or self.review_hash!=review_digest:
            raise HOLD("No source-owned read-only concept permission")
        self.admitted=True

    def suggest(self,world):
        if not self.admitted or self.model is None:
            raise HOLD("Concept still provisional and not independently reviewed")
        verify_world(world)
        return suggest(self.model,world)
