"""Data-only routing distillation from verified marginal reasoning contributions.

This does not synthesize new graph-search or objection algorithms. It selects
which already-source-owned specialist method to consult for a status, and
requires an independent receiver to validate that routing on different cases.
"""
from __future__ import annotations
import json
from commonwealth import HOLD, owner4, sha, pins, exact_proof, SOURCE_SCHEMA

SCHEMA = "motif.reason.commonwealth-method.v1"
ROUTES = {
    "PROVED_REACHABLE": "CHALLENGE_AND_OPTIONALLY_RECHECK_SOURCE",
    "PROVED_UNREACHABLE": "CHALLENGE_AND_OPTIONALLY_RECHECK_SOURCE",
    "UNKNOWN": "ASK_CONSEQUENTIAL_QUESTION_IF_WORTH_IT",
    "HOLD_OPEN_WORLD": "STOP_AND_REQUEST_SCOPE",
}
MAX_BYTES = 24000


def _lesson(report):
    if (not isinstance(report, dict) or report.get("schema") != SOURCE_SCHEMA
            or report.get("owner_blobs") != pins()
            or report.get("real_world_authority") is not False
            or report.get("external_actions") is not False
            or report.get("before") not in ROUTES
            or not isinstance(report.get("ledger"), list)
            or not report["ledger"]):
        raise HOLD("Unsupported source-owned council lesson")
    if report["marginal"]["no_vote_on_truth"] is not True:
        raise HOLD("Teacher attempted to turn council votes into truth")
    ledger=report["ledger"]
    roles={event["role"] for event in ledger
           if event["new_validated_contribution"]}
    status=report["before"]
    if ("PROOF" not in roles or
            (status.startswith("PROVED_") and "OBJECTION" not in roles) or
            (status=="UNKNOWN" and "QUESTION" not in roles) or
            (status=="HOLD_OPEN_WORLD" and ("OBJECTION" in roles or "QUESTION" in roles))):
        raise HOLD("Insufficient role-separated teaching evidence")
    if report["marginal"]["duplicates_rejected"] < 1:
        raise HOLD("No repetition-control witness")
    expected = ROUTES[status]
    return {"case": report["case"], "before": status, "after": report["after"],
            "roles": sorted(roles), "route": expected, "receipt_digest": sha(report),
            "marginal_proof_or_information": report["marginal"]["novel"]}


def learn(reports):
    if not isinstance(reports, tuple) or not 4 <= len(reports) <= 10:
        raise HOLD("Insufficient distinct owner episodes")
    examples=[_lesson(x) for x in reports]
    if len({x["case"] for x in examples}) != len(examples):
        raise HOLD("Duplicated learning cases")
    for status in ROUTES:
        if not any(x["before"]==status for x in examples):
            raise HOLD("No teacher demonstration of " + status)
    # At least one source correction and one alternative proof defense are
    # needed to establish that the routing is not a one-size-fits-all vote.
    if not any(x["before"] in ("PROVED_REACHABLE","PROVED_UNREACHABLE") and
               x["after"]!=x["before"] for x in examples):
        raise HOLD("No actual source-reviewed conditional correction")
    body={
        "schema":SCHEMA,
        "source_blobs":pins(),
        "source_contract":owner4.REVISION,
        "routes": [{"when":status,"method":ROUTES[status]} for status in sorted(ROUTES)],
        "teacher_episodes":examples,
        "inference": "FIXED_ALLOWLIST_ROUTING_FROM_OBSERVED_VERIFIED_CONTRIBUTIONS",
        "status":"PROPOSE_ONLY",
        "local_scope":"SYNTHETIC_READ_ONLY",
        "external_execution":False,
        "real_world_authority":False,
    }
    out=dict(body,checksum_sha256=sha(body))
    raw=json.dumps(out,indent=2,sort_keys=True)+"\n"
    validate(raw)
    return raw


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_BYTES:
        raise HOLD("Unbounded method packet")
    try: obj=json.loads(raw)
    except (TypeError,ValueError) as exc: raise HOLD("Malformed method data") from exc
    keys={"schema","source_blobs","source_contract","routes","teacher_episodes",
          "inference","status","local_scope","external_execution",
          "real_world_authority","checksum_sha256"}
    if not isinstance(obj,dict) or set(obj)!=keys:
        raise HOLD("Unknown method-cartridge data")
    if (obj["schema"]!=SCHEMA or obj["source_blobs"]!=pins()
            or obj["source_contract"]!=owner4.REVISION
            or obj["status"]!="PROPOSE_ONLY"
            or obj["inference"]!="FIXED_ALLOWLIST_ROUTING_FROM_OBSERVED_VERIFIED_CONTRIBUTIONS"
            or obj["local_scope"]!="SYNTHETIC_READ_ONLY"
            or obj["real_world_authority"] is not False
            or obj["external_execution"] is not False):
        raise HOLD("Altered source or method privileges")
    if obj["routes"]!=[{"when":status,"method":ROUTES[status]} for status in sorted(ROUTES)]:
        raise HOLD("Unreviewed method or guard")
    episodes=obj["teacher_episodes"]
    if (not isinstance(episodes,list) or not 4<=len(episodes)<=10
            or len({x.get("case") for x in episodes if isinstance(x,dict)})!=len(episodes)
            or any(not isinstance(x,dict) or set(x)!={"case","before","after",
                  "roles","route","receipt_digest","marginal_proof_or_information"}
                   or x["before"] not in ROUTES or x["route"]!=ROUTES[x["before"]]
                   or x["receipt_digest"] is None or not isinstance(x["receipt_digest"],str)
                   or len(x["receipt_digest"])!=64 or not isinstance(x["roles"],list)
                   for x in episodes)):
        raise HOLD("Missing, altered or repeated lessons")
    if {x["before"] for x in episodes}!=set(ROUTES):
        raise HOLD("Untaught routing boundary")
    if obj["checksum_sha256"]!=sha({k:v for k,v in obj.items() if k!="checksum_sha256"}):
        raise HOLD("Method data altered")
    return obj


class Receiver:
    def __init__(self, raw):
        self.packet=validate(raw)
        self.approved=False
        self.digest=None
        self.passed=False

    def preview(self, heldout):
        if not isinstance(heldout,tuple) or len(heldout)<4:
            raise HOLD("Requires unlike independent scenarios")
        seen=set()
        reviewed=[]
        used_training={x["case"] for x in self.packet["teacher_episodes"]}
        for case_name,q,expected in heldout:
            if (not isinstance(case_name,str) or case_name in seen
                    or case_name in used_training or not isinstance(q,owner4.Inquiry)
                    or expected not in ROUTES.values()):
                raise HOLD("Invalid independent source-owned review")
            seen.add(case_name)
            got=ROUTES[exact_proof(q)["conclusion"]]
            reviewed.append({"name":case_name,"expected":expected,"actual":got,
                             "evidence_digest":sha(owner4.encode(q))})
        if {x["actual"] for x in reviewed}!=set(ROUTES.values()):
            raise HOLD("Independent scenarios omit a reasoning role")
        failures=sum(x["expected"]!=x["actual"] for x in reviewed)
        self.passed=failures==0
        self.digest=sha({"cartridge":self.packet["checksum_sha256"],"review":reviewed})
        return {"stage":"HOLD_REVIEW","cases":len(reviewed),"errors":failures,
                "review_digest":self.digest,
                "human_review_performed":False}

    def admit(self,decision,review_digest):
        if decision!="ADMIT_READ_ONLY" or not self.passed or review_digest!=self.digest:
            raise HOLD("No successful explicitly selected synthetic local admission")
        self.approved=True

    def suggest(self,q):
        if not self.approved:
            raise HOLD("Portable commonwealth method not admitted")
        return {"stage":"SUGGEST_ONLY",
                "method":ROUTES[exact_proof(q)["conclusion"]],
                "external_actions":False,"real_world_authority":False}
