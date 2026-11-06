"""REASON-018: bounded relational grammar discovery and counterexamples.

A newly named source-owned concept is compiled as a relational *composition*
rather than copied as an unfamiliar English phrase. Exhaustive program search
starts with permitted graph atoms, inventing their joined existential clause
by eliminating entire alternative relational schemas against queried examples.

The source's hidden concept/oracle.py is NEVER imported here. Primitive names
are supplied. Candidate composition shapes are supplied. This is inductive
logic-program synthesis within a finite predefined DSL, not spontaneous
creation of fundamentally new logical primitives or understanding of love.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from itertools import product
from pathlib import Path
import json

from worlds import RELATIONS,train_worlds,heldout_worlds,make

WORLD_SOURCE=Path(__file__).with_name("worlds.py")
WORLD_BLOB="41176cafaf679fbf42dbdb4632ebcfda98510499"
SCHEMA="motif.reason.living-concept.cartridge.v1"
PACKET="motif.reason.living-concept.training-receipt.v1"
SHAPES=(
    ("B","A"),  # B -> witness -> A: joined return path
    ("A","B"),  # A -> witness -> B: alternative directed route
    ("B","B"),  # B -> witness -> B: self-contained cycle
    ("A","A"),  # A -> witness -> A: self-contained actor cycle
)
MAX_INQUIRIES=88


class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    raw=WORLD_SOURCE.read_bytes()
    sha=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=WORLD_BLOB:
        raise HOLD("Public unlabeled relational graph source mutated")
    return sha


def programs():
    """All 4 * 6^4 finite joined-graph compositions; target not supplied."""
    return tuple((shape,one,two,three,gate)
                 for shape in range(len(SHAPES))
                 for one,two,three,gate in product(RELATIONS,repeat=4))


def edges(world):
    return {tuple(edge) for edge in world["edges"]}


def prove(program,world):
    shape,r1,r2,r3,gate=program
    E=edges(world)
    a,b=world["actor"],world["recipient"]
    if (r1,a,b) not in E or (gate,a,b) not in E:
        return None
    source= a if SHAPES[shape][0]=="A" else b
    dest= a if SHAPES[shape][1]=="A" else b
    for w in world["nodes"]:
        if w in (a,b):continue
        if (r2,source,w) in E and (r3,w,dest) in E:
            return {
                "bound_witness":w,
                "premises":[[r1,a,b],[r2,source,w],[r3,w,dest],[gate,a,b]],
                "schema_shape":list(SHAPES[shape]),
                "source_world_sha256":digest(world),
            }
    return None


def core(program,world):
    shape,r1,r2,r3,gate=program
    E=edges(world)
    a,b=world["actor"],world["recipient"]
    if (r1,a,b) not in E:return False
    source=a if SHAPES[shape][0]=="A" else b
    dest=a if SHAPES[shape][1]=="A" else b
    return any((r2,source,w) in E and (r3,w,dest) in E
               for w in world["nodes"] if w not in (a,b))


def status(program,world):
    positive=prove(program,world) is not None
    negative=not core(program,world) or (
        "CLAIM",world["actor"],world["recipient"]) in edges(world)
    return ("BOTH" if positive and negative else
            "SUPPORTED" if positive else
            "REFUTED" if negative else "UNDETERMINED")


def _check_label(world,source_record):
    if not isinstance(source_record,dict) or set(source_record)!={
        "schema","case_id","source_world_sha256","source_revision",
        "status","positive_support","negative_support",
        "owner_witness_not_disclosed_to_inventor","synthetic_source_only",
        "real_world_permission","checksum_sha256"}:
        raise HOLD("Unknown evidence from simulated source")
    if (source_record["schema"]!="motif.reason.living-concept.source-label.v1"
        or source_record["case_id"]!=world["id"]
        or source_record["source_world_sha256"]!=digest(world)
        or source_record["source_revision"]!="motif.reason.living-concept.source-owner.v1"
        or type(source_record["positive_support"]) is not bool
        or type(source_record["negative_support"]) is not bool
        or source_record["status"] not in ("SUPPORTED","REFUTED","BOTH","UNDETERMINED")
        or source_record["owner_witness_not_disclosed_to_inventor"] is not True
        or source_record["synthetic_source_only"] is not True
        or source_record["real_world_permission"] is not False
        or source_record["checksum_sha256"]!=digest({
            k:v for k,v in source_record.items() if k!="checksum_sha256"})):
        raise HOLD("Unpinned, mis-scoped, overconfident or tampered source label")


def _filter(programs_left,world,label):
    return [p for p in programs_left
            if (prove(p,world) is not None)==label["positive_support"]]


def _ask(owner,w,seen,labels,remaining):
    evidence=owner.label(w)
    _check_label(w,evidence)
    if w["id"] in seen:raise HOLD("Do not purchase duplicate source evidence")
    seen.add(w["id"])
    labels.append(evidence)
    survivors=_filter(remaining,w,evidence)
    if not survivors:
        raise HOLD("Counterexample contradicts every allowable composition")
    return survivors


def discover(owner,max_inquiries=40):
    """Classical active learning: sample maximum-disagreement source graph.

    Chooses the next graph among SOURCE-DECLARED TRAIN worlds, not heldout.
    Does not ask oracle for test labels or import the target predicate.
    """
    pin()
    if type(max_inquiries) is not int or not 3<=max_inquiries<=MAX_INQUIRIES:
        raise HOLD("Unbounded inquiry budget")
    pool=train_worlds()
    hypotheses=list(programs())
    seen=set()
    labels=[]
    versions=[]
    hypotheses=_ask(owner,pool[0],seen,labels,hypotheses)
    versions.append({"step":1,"remaining_programs":len(hypotheses),
                     "source_example":pool[0]["id"]})
    while len(hypotheses)>1 and len(labels)<max_inquiries:
        available=[w for w in pool if w["id"] not in seen]
        if not available:break
        # The optimal world distinguishes as many surviving syntactic
        # programs as possible. This is no epistemic claim about real people.
        scored=[]
        for world in available:
            positives=sum(prove(p,world) is not None for p in hypotheses)
            negatives=len(hypotheses)-positives
            disagreement=min(positives,negatives)
            scored.append((disagreement,-int(world["id"].split("-")[1]),world))
        best=max(scored,key=lambda x:(x[0],x[1]))
        if best[0]==0:break
        w=best[2]
        hypotheses=_ask(owner,w,seen,labels,hypotheses)
        versions.append({"step":len(labels),
                         "remaining_programs":len(hypotheses),
                         "source_example":w["id"],
                         "program_disagreement_before_answer":best[0]})
    # When multiple programs survive, a new example may still be confidently
    # represented if every surviving program predicts the same four-value.
    body={
        "schema":SCHEMA,"source_worlds_git_blob":pin(),
        "grammar_size":len(programs()),
        "grammar_family":"EXISTENTIALLY_JOINED_TWO_EDGE_WITNESS_WITH_DIRECT_ACTOR_RECIPIENT_GATES",
        "candidate_shapes":[list(s) for s in SHAPES],
        "primitive_relations":list(RELATIONS),
        "source_training_labels":labels,
        "source_example_count":len(labels),
        "source_inquiry_budget":max_inquiries,
        "remaining_hypotheses":[list(x) for x in hypotheses],
        "version_space_trace":versions,
        "hypothesis_unique":len(hypotheses)==1,
        "learning_method":"FINITE_DSL_VERSION_SPACE_AND_ACTIVE_DISAGREEMENT",
        "no_oracle_or_holdout_labels_imported":True,
        "novel_predicate_type":"SOURCE_OBSERVED_RELATIONAL_MACRO_NOT_A_NEW_PRIMITIVE",
        "strong_classical_synthesis_can_match":True,
        "human_love_or_welfare_not_observed":True,
        "external_actions":False,"permission_to_act":False,
        "real_world_authority":False,
    }
    return body


def suggest(cartridge,world):
    if not isinstance(cartridge,dict) or cartridge.get("schema")!=SCHEMA:
        raise HOLD("Unknown proof-carrying concept")
    if not isinstance(world,dict) or world.get("schema")!="motif.reason.living-concept.world.v1":
        raise HOLD("Unsupported evidence world")
    # No source-label access here. Only structural evidence and the fitted
    # hypothesis version space are available.
    remaining=[tuple(x) for x in cartridge["remaining_hypotheses"]]
    if not remaining:
        raise HOLD("No independently reviewable relational grammar")
    alternatives={status(p,world) for p in remaining}
    stage=(next(iter(alternatives)) if len(alternatives)==1
           else "HOLD_CONCEPT_UNDERDETERMINED_BY_TRAINING")
    witness=(prove(remaining[0],world)
             if stage in ("SUPPORTED","BOTH") and len(remaining)==1 else None)
    return {
        "schema":"motif.reason.living-concept.read-only-suggestion.v1",
        "source_world_id":world["id"],"source_world_sha256":digest(world),
        "status":stage,"possible_results":sorted(alternatives),
        "relation_witness":witness,
        "source_training_versions":len(cartridge["version_space_trace"]),
        "no_concept_authority_for_real_people":True,
        "no_emotion_or_love_inferred":True,
        "external_actions":False,
    }


def export(cartridge):
    if not isinstance(cartridge,dict) or cartridge.get("schema")!=SCHEMA:
        raise HOLD("Invalid grammar discovery record")
    doc=dict(cartridge,checksum_sha256=digest(cartridge))
    raw=json.dumps(doc,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if len(raw.encode())>120000:raise HOLD("Unbounded learning record")
    return raw
