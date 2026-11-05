"""027F: relevance BEFORE 022F + 016; no automatic third-party action.

The new check is independent of the T5 *output* (literal operator-note
spans), but it is NOT independent of operator-note truth. A high encoder
similarity, even when three correlated heads agree, cannot assert support.

If a note has two or more anchored candidate gates, the safest result is
a held ambiguity; do not silently choose one.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
for part in ("016","021f","022f","025f","026f","027f"):
    p=str(ROOT/part)
    if p not in sys.path:sys.path.append(p)
from semantic_router import route_semantic_hint,operator_projection
from question_relay import review_semantic_question
from relevance import relevance_witness,anchored_native_guess,GATE_SUBJECTS
from native_careers import native_rule
from semantic_router import NATIVE_JOB
from nodes import ThreeSpecialistEncoder,combine_opinions

class Forced:
    """A category nomination from a read-only encoder node, not model text."""
    def __init__(self,label,origin):
        self.name=origin
        self.label=label
    def classify(self,note):
        return self.label,0.0


def relevance_first_relay(
    note:str,candidate:str|None,*,mode:str="ENCODER",
    hidden_world:str="10",
):
    """Only a source-grounded candidate may reach real 022F validation.

    The result is an audit receipt; 022F still has its own independent
    *synthetic* source reviews and 016 question-value check.
    """
    projection=operator_projection(note)
    digest=projection.digest()
    receipts={
        gate:asdict(relevance_witness(note,gate))
        for gate in GATE_SUBJECTS
    }
    base={
        "schema":"motif027f.relevance-before-question/v0",
        "candidate":candidate,
        "origin":mode,
        "projection_digest":digest,
        "relevance_by_gate":receipts,
        "status":"HOLD_NO_NOMINATION",
        "native_review":None,
        "source_quote":None,
        "field_actions":0,
        "permission_granted":False,
        "new_source_authenticated":False,
        "operator_note_truth_proven":False,
        "model_outcome_promoted_to_fact":False,
        "actual_021f_chorus_worker_called":False,
    }
    if candidate is None or candidate=="NONE":
        return base
    if candidate not in GATE_SUBJECTS:
        base["status"]="HOLD_UNKNOWN_GATE_ID"
        return base
    hits=tuple(g for g in GATE_SUBJECTS
               if receipts[g]["status"]=="SOURCE_QUOTE_SUPPORTS_REVIEW")
    if candidate not in hits:
        base["status"]="HOLD_CANDIDATE_NOT_GROUNDED_IN_NOTE"
        return base
    if len(hits)!=1:
        base["status"]="HOLD_AMBIGUOUS_MULTIPLE_SUPPORTED_GATES"
        return base
    witness=receipts[candidate]
    baseline_gate=native_rule(NATIVE_JOB,note)
    if baseline_gate not in ("NONE",candidate):
        base["status"]="HOLD_NATIVE_AND_SEMANTIC_GATE_CONFLICT"
        return base
    base["source_quote"]=witness["source_quote"]
    actual=review_semantic_question(
        note,Forced(candidate,mode),
        hidden_world=hidden_world,
    )
    base["status"]=actual["status"]
    base["native_review"]=actual
    return base


def source_only(note:str)->str|None:
    """Strong classical comparator with the same independent anchor grammar."""
    operator_projection(note)
    hits=anchored_native_guess(note)
    return hits[0] if len(hits)==1 else None


def candidate_from_single(note:str,single)->str|None:
    """Model only if native has not found a category."""
    native=native_rule(NATIVE_JOB,note)
    if native!="NONE":
        return native
    return single.classify(note)[0]


def candidate_from_three(note:str,triple,*,quorum=2)->dict:
    """Three nodes must not run for a problem native already identified."""
    native=native_rule(NATIVE_JOB,note)
    if native!="NONE":
        return {
            "status":"NATIVE_SHORT_CIRCUIT",
            "candidate":native,"nodes_called":0,"node_outputs":(),
            "three_are_independent_witnesses":False
        }
    opinions=triple.opinions(note)
    merged=combine_opinions(opinions,quorum=quorum)
    merged.update({
        "nodes_called":3,
        "node_outputs":tuple(asdict(o) for o in opinions),
    })
    return merged
