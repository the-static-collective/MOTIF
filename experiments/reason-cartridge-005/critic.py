"""Bounded second-order criticism: reject bad objections or review material ones.

The ranking prior is declared synthetic. A rival could implement the same
policy with classical decision theory. No autonomous investigation occurs.
"""
from __future__ import annotations
import json
from engine import (HOLD, Objection, ToyOwner, Model, owner4, stress,
                    build_record, validate, hashed, enc_objection, pinned_owner)


class Critic:
    def __init__(self, inquiry, candidates, model=Model(), budget=1):
        if (not isinstance(inquiry, owner4.Inquiry)
                or not isinstance(candidates, tuple) or not 1 <= len(candidates) <= 8
                or any(not isinstance(x, Objection) for x in candidates)
                or type(budget) is not int or budget not in (0, 1)
                or not isinstance(model, Model)):
            raise HOLD("Unbounded or unrecognized meta-critic")
        if len({x.reference for x in candidates}) != len(candidates):
            raise HOLD("Duplicate objection reference may create a loop")
        if len({(x.kind,x.edges) for x in candidates}) != len(candidates):
            raise HOLD("Repeated objection pattern")
        self.inquiry = inquiry
        self.candidates = candidates
        self.model = model
        self.budget = budget

    def plan(self):
        defenses, material, holds = [], [], []
        for candidate in self.candidates:
            result = stress(self.inquiry, candidate)
            if result["classification"] == "DEFENSE":
                record = build_record(self.inquiry, candidate, "DEFENSE")
                defenses.append({"objection":candidate.reference,
                                 "cartridge":json.loads(record),
                                 "reason":"ALT_PROOF_SURVIVES_PROPOSED_OBJECTION"})
            elif result["classification"] == "MATERIAL_OBJECTION":
                estimate = self.model.value()
                material.append({"objection":candidate.reference,
                                 "candidate":enc_objection(candidate),
                                 "hypothetical_counterfactual":result["counterfactual"],
                                 "economy":estimate})
            else:
                holds.append({"objection":candidate.reference,
                              "reason":result["classification"]})
        material.sort(key=lambda x: (-x["economy"]["net_value_of_further_reasoning"],
                                     x["objection"]))
        chosen = next((entry for entry in material if
                       entry["economy"]["net_value_of_further_reasoning"] > 0),None)
        return {"defenses":defenses, "material":material, "holds":holds,
                "chosen":chosen if self.budget > 0 else None,
                "reasoning_budget":self.budget,
                "reasoning_cost_model_hypothetical":True,
                "no_live_external_actions":True}

    def run(self, source_owner=None):
        plan = self.plan()
        candidate = plan["chosen"]
        status = ("STOP_NO_POSITIVE_VALUE" if not candidate and self.budget
                  else "STOP_BUDGET_EXHAUSTED" if not candidate
                  else "HOLD_OWNER_REVIEW_REQUIRED")
        decision = {"status":status, "proof_defenses":plan["defenses"],
                    "objected":len(self.candidates),
                    "material_objections":len(plan["material"]),
                    "owner_reviews":0, "candidate":candidate,
                    "reused_real_world_authority":False,
                    "no_external_queries":True}
        if candidate is None or source_owner is None:
            return decision
        if not isinstance(source_owner, ToyOwner):
            raise HOLD("Only explicit independent synthetic fixture owner admitted")
        selected = next(x for x in self.candidates
                        if x.reference == candidate["objection"])
        after, receipt = source_owner.review(self.inquiry,selected)
        now = owner4.decide(after)
        before = owner4.decide(self.inquiry)
        classification = ("CORRECTION" if now["status"] != before["status"]
                          else "OWNER_DEFENSE")
        record = build_record(self.inquiry,selected,classification,
                              after=after, owner_receipt=receipt)
        decision.update({"status":classification, "owner_reviews":1,
                         "outcome_cartridge":validate(record),
                         "synthetic_source_only":True})
        return decision


class Receiver:
    """Independent receiver validates method plus unlike heldout objections."""
    def __init__(self, raw):
        self.packet = validate(raw)
        self.approved = False
        self.review_hash = None
        self.passed = False

    def preview(self, heldout):
        if not isinstance(heldout, tuple) or len(heldout) < 2:
            raise HOLD("Missing independent meta-criticism challenge cases")
        actual = []
        seen = set()
        for q, challenge, expected in heldout:
            if not isinstance(q,owner4.Inquiry) or not isinstance(challenge,Objection):
                raise HOLD("Malformed independent reviewer scenario")
            key = hashed([owner4.encode(q),enc_objection(challenge)])
            if key in seen or owner4.encode(q) == self.packet["original_inquiry"]:
                raise HOLD("Teaching example leaked into independent review")
            seen.add(key)
            got=stress(q,challenge)["classification"]
            actual.append({"case":key, "expected":expected, "result":got})
        if {r["expected"] for r in actual} != {"DEFENSE","MATERIAL_OBJECTION"}:
            raise HOLD("No positive and negative objection controls")
        errors=sum(r["expected"]!=r["result"] for r in actual)
        self.passed=errors==0
        self.review_hash=hashed({"source":self.packet["checksum_sha256"],
                                 "review":actual})
        return {"cases":len(actual), "errors":errors,
                "stage":"HOLD_INDEPENDENT_REVIEW",
                "review_digest":self.review_hash}

    def admit(self,decision,review_digest):
        if decision!="ADMIT_READ_ONLY" or not self.passed or review_digest!=self.review_hash:
            raise HOLD("Method cannot inherit owner's permission")
        self.approved=True

    def suggest(self):
        if not self.approved:
            raise HOLD("No local independent approval")
        return {"stage":"SUGGEST_ONLY",
                "classification":self.packet["classification"],
                "outcome":self.packet["outcome"],
                "external_execution":False,
                "real_world_authority":False}


class Memory:
    """Exact-context reusable local defenses/corrections, never global rules."""
    def __init__(self):
        self.entries={}

    def store(self, raw):
        packet=validate(raw)
        key=hashed([packet["source_revision"],
                    packet["owner_reason004_blob"],
                    packet["original_inquiry"],
                    packet["objection"]])
        self.entries[key]=raw
        return key

    def recall(self,q,candidate):
        key=hashed(["reason-005-synthetic-source-v1",pinned_owner(),
                    owner4.encode(q),enc_objection(candidate)])
        if key not in self.entries:
            return {"status":"HOLD_NO_REUSABLE_CONTEXT"}
        packet=validate(self.entries[key])
        return {"status":"EXACT_CONTEXT_ONLY",
                "classification":packet["classification"],
                "record_digest":packet["checksum_sha256"],
                "no_new_external_observation":True}
