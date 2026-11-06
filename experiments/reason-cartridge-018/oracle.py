"""Independent synthetic SOURCE OWNER for an undisclosed relational concept.

The source knows the target rule; inventor.py is prohibited from importing
this module. We ask only whether positive and negative source evidence is
present, not for the witness or the final source rule.

This entirely artificial "unowned way" concept means: A offers B a path to
an option that can return to A, with an explicit no-claim/free statement. If
a contrary claim also exists, retain BOTH. If neither sign of claim exists,
remain UNDETERMINED. These words are analogies, not claims about real love.
"""
from __future__ import annotations

from hashlib import sha256
import json

from worlds import make,RELATIONS

REVISION="motif.reason.living-concept.source-owner.v1"


def digest(o):
    return sha256(json.dumps(o,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def verify_world(world):
    if not isinstance(world,dict) or set(world)!={
        "schema","id","source_partition","seed","actor","recipient","nodes",
        "edges","relations","source_kind","new_concept_not_a_relation_primitive",
        "real_person_welfare_not_observed"}:
        raise ValueError("Untrusted graph schema")
    if (world["source_partition"] not in ("TRAIN","HELDOUT")
            or world["relations"]!=list(RELATIONS)
            or world["actor"]!="A" or world["recipient"]!="B"
            or world["source_kind"]!="SYNTHETIC_FINITE_RELATIONAL_GRAPH"
            or world["new_concept_not_a_relation_primitive"] is not True
            or world["real_person_welfare_not_observed"] is not True):
        raise ValueError("Invented real-world authority")
    prefix="TR-" if world["source_partition"]=="TRAIN" else "HO-"
    if not world["id"].startswith(prefix):raise ValueError("Changed source identifier")
    try: i=int(world["id"][3:])
    except ValueError as exc:raise ValueError("Noncanonical source ID") from exc
    if i<0 or i>= (88 if world["source_partition"]=="TRAIN" else 55):
        raise ValueError("Source ID beyond allowed pool")
    if world!=make(i,world["source_partition"]):
        raise ValueError("Graph source changed, mislabeled or reordered")
    return world


def source_label(world):
    verify_world(world)
    E={tuple(x) for x in world["edges"]}
    a,b=world["actor"],world["recipient"]
    # Owner's direct relational graph program: deliberately distinct from
    # invented AST enumeration in inventor.py.
    if ("OFFER",a,b) in E:
        intermediates={d for rel,s,d in E if rel=="OPEN" and s==b}
        returned={s for rel,s,d in E if rel=="RELEASE" and d==a}
        path_witness=sorted(intermediates & returned)
    else:
        path_witness=[]
    core=bool(path_witness)
    positive=core and ("FREE",a,b) in E
    negative=(not core) or ("CLAIM",a,b) in E
    status=(
        "BOTH" if positive and negative else
        "SUPPORTED" if positive else
        "REFUTED" if negative else "UNDETERMINED"
    )
    body={
        "schema":"motif.reason.living-concept.source-label.v1",
        "case_id":world["id"],
        "source_world_sha256":digest(world),
        "source_revision":REVISION,
        "status":status,
        "positive_support":positive,
        "negative_support":negative,
        "owner_witness_not_disclosed_to_inventor":True,
        "synthetic_source_only":True,
        "real_world_permission":False,
    }
    return dict(body,checksum_sha256=digest(body))


class SourceOwner:
    def __init__(self,max_training_questions=88):
        self.reads=[]
        self.limit=max_training_questions

    def label(self,world):
        verify_world(world)
        if world["source_partition"]!="TRAIN":
            raise ValueError("Training instrument may not query heldout labels")
        if len(self.reads)>=self.limit:
            raise ValueError("Limited source-owner inquiry budget exhausted")
        if world["id"] in self.reads:
            raise ValueError("Cannot purchase the same evidence twice")
        self.reads.append(world["id"])
        return source_label(world)
