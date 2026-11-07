"""LEGIT-020 — APERTURE: language is a carrier, not an admitted equation.

Research implementation of the user-origin APERTURE / TRIAD / BRAID:
 RAW -> SIGNAL/CONTEXT/GAP -> candidate SENSE FIELD ->
 FACT/IDEA/RELATION × SUBSTANCE/LINEAGE/AUTHORITY.

"mathalizing" is treated as a user-proposed name for a cautious,
loss-inspectable translation of small English utterances into *candidate*
typed mathematical questions. This is a narrow deterministic transducer,
not general natural language understanding or automatic interpretation.

Explicit contextual cuts constrain but never overwrite the original
ambiguous reading receipt. No current reading mints permission, evidence,
intent or authority, regardless of confidence or future Z3 results.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import re

AXIS1=("SIGNAL","CONTEXT","GAP")
AXIS2=("FACT","IDEA","RELATION")
AXIS3=("SUBSTANCE","LINEAGE","AUTHORITY")
ALL_CELLS=frozenset((x,y,z) for x in AXIS1 for y in AXIS2 for z in AXIS3)
assert len(ALL_CELLS)==27

class HOLD(ValueError):pass

@dataclass(frozen=True)
class Reading:
    name: str
    domain: str
    executable_question: str | None
    linguistic_form: str
    epistemic_status: str="POSSIBLE_NOT_ADMITTED"

@dataclass(frozen=True)
class SenseField:
    raw: str
    source_sha256: str
    context: str
    parent_sha256: str | None
    candidates: tuple[Reading,...]
    pending: tuple[str,...]
    sparse_addresses: tuple[tuple[str,str,str],...]
    admitted: bool=False

G=("WALK_EQ","CLAW_EQ","ISOMORPHIC")
S=("SHIFT_UNSIGNED","SHIFT_SIGNED")
B=("RIVERBANK","BANK_INSTITUTION")
D=("DOUBLE_ADD","DOUBLE_SHIFT")

VIEWS={
"WALK_EQ":Reading("WALK_EQ","GRAPH","WALK_HOM_COUNT_EQUAL",
                 "same total counts of finite linear walks"),
"CLAW_EQ":Reading("CLAW_EQ","GRAPH","K13_HOM_COUNT_EQUAL",
                 "same counts of branching three-leaf star mappings"),
"ISOMORPHIC":Reading("ISOMORPHIC","GRAPH","GRAPH_ISOMORPHIC",
                     "same full graph structure up to relabelling"),
"SHIFT_UNSIGNED":Reading("SHIFT_UNSIGNED","BITVECTOR","LOGICAL_SHR1",
                         "64-bit logical right shift of an unsigned word"),
"SHIFT_SIGNED":Reading("SHIFT_SIGNED","BITVECTOR","ARITH_SHR1",
                       "64-bit arithmetic right shift of a signed word"),
"RIVERBANK":Reading("RIVERBANK","LANGUAGE",None,
                    "the physical riverbank changed its position"),
"BANK_INSTITUTION":Reading("BANK_INSTITUTION","LANGUAGE",None,
                    "a banking institution or branch relocated"),
"DOUBLE_ADD":Reading("DOUBLE_ADD","BITVECTOR","BV64_ADD_X_X",
                     "x + x modulo 2^64"),
"DOUBLE_SHIFT":Reading("DOUBLE_SHIFT","BITVECTOR","BV64_SHL1",
                       "x shifted left once as a 64-bit word"),
}
FIXED_SENTENCES={
 "are these two graphs the same?":G,
 "are these graphs the same?":G,
 "the two graphs look the same.":G,
 "shift x right by one bit.":S,
 "shift x right by one.":S,
 "the bank moved.":B,
 "double x modulo 2^64.":D,
}
REFINEMENTS={
 "i mean compare linear walks.":"WALK_EQ",
 "compare the path-walk totals.":"WALK_EQ",
 "i mean compare branching three-leaf trees.":"CLAW_EQ",
 "compare the three-leaf star counts.":"CLAW_EQ",
 "i mean compare graph isomorphism.":"ISOMORPHIC",
 "treat x as an unsigned 64-bit word.":"SHIFT_UNSIGNED",
 "treat x as a signed 64-bit word.":"SHIFT_SIGNED",
 "erosion shifted the riverbank.":"RIVERBANK",
 "a financial institution moved its branch office.":"BANK_INSTITUTION",
 "use bitvector addition.":"DOUBLE_ADD",
 "use bitvector left shift.":"DOUBLE_SHIFT",
}
SIGNAL_CELL=("SIGNAL","FACT","SUBSTANCE")
GAP_CELL=("GAP","IDEA","AUTHORITY")
CONTEXT_CELL=("CONTEXT","RELATION","LINEAGE")

def _key(raw):
    if type(raw) is not str or not raw.strip() or len(raw)>1024:
        raise HOLD("No bounded source text")
    return " ".join(raw.strip().lower().split())

def receipt_hash(field):
    raw={"text":field.raw,"source_sha256":field.source_sha256,
         "context":field.context,"parent_sha256":field.parent_sha256,
         "candidates":[v.name for v in field.candidates],
         "pending":field.pending,"sparse_addresses":field.sparse_addresses}
    return sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()

def open_aperture(utterance):
    key=_key(utterance)
    names=FIXED_SENTENCES.get(key)
    if names is None:
        # Absence of a deterministic grammar is a *successful HOLD*.
        return SenseField(utterance,sha256(utterance.encode()).hexdigest(),
             "",None,(),("NO_DECLARED_LANGUAGE_TO_MATH_DECODER",),
             (SIGNAL_CELL,GAP_CELL),False)
    return SenseField(utterance,sha256(utterance.encode()).hexdigest(),
        "",None,tuple(VIEWS[x] for x in names),
        (("INTENDED_READING_NOT_ESTABLISHED",) if len(names)>1 else ()),
        (SIGNAL_CELL,GAP_CELL),False)

def update_context(previous,context):
    if not isinstance(previous,SenseField):
        raise HOLD("No earlier raw receipt")
    key=_key(context)
    name=REFINEMENTS.get(key)
    prior_names={x.name for x in previous.candidates}
    if name not in prior_names:
        raise HOLD("Unrelated context cannot conjure a new meaning")
    new=tuple(x for x in previous.candidates if x.name==name)
    # contextual compatibility is not observed human intention.
    return SenseField(previous.raw,previous.source_sha256,context,
         receipt_hash(previous),new,
         ("INTENT_REQUIRES_EXPLICIT_HUMAN_ADMISSION",),
         (SIGNAL_CELL,CONTEXT_CELL,GAP_CELL),False)

def mathalize(field):
    if not isinstance(field,SenseField):raise HOLD("Unknown aperture")
    return {
        "schema":"motif.aperture.mathalizer.v1",
        "original_raw":field.raw,
        "original_raw_sha256":field.source_sha256,
        "receipt_sha256":receipt_hash(field),
        "parent_receipt_sha256":field.parent_sha256,
        "declared_context":field.context,
        "sparse_27_cell_addresses":[list(x) for x in field.sparse_addresses],
        "language_to_math_candidates":[{
            "id":r.name,"domain":r.domain,
            "typed_mathematical_question":r.executable_question,
            "readable_gloss":r.linguistic_form,
            "epistemic_status":r.epistemic_status,
            "semantic_role":"IDEA",
            "substance":"SOURCE_BOUND_INTERPRETATION",
            "lineage":field.source_sha256,
            "authority":"PROPOSAL_ONLY",
        }for r in field.candidates],
        "unresolved_gaps":list(field.pending),
        "accepted_meaning":None,
        "human_authority_admitted":False,
        "mathematical_proof_establishes_linguistic_intent":False,
        "general_language_comprehension_claimed":False,
    }

def speak_math(name):
    """Math -> language; explanatory gloss, not a proven reverse parse."""
    if name not in VIEWS:raise HOLD("Unknown mathematical interpretation")
    return VIEWS[name].linguistic_form

def allow_admission(field):
    """Always return HOLD; different human boundary must authorize."""
    raise HOLD("APERTURE does not admit human meaning or real-world claims")
