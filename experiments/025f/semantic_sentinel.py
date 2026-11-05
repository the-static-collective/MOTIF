"""MOTIF-025F: executable LOW-AUTHORITY T5 encoder assumption sentinel.

Never directly tags a real plan as blocked; never gives permission, contact or
execute authority. It is an *experimental synthetic review question offer*.
Only if a native check finds no obvious gate does a local cached encoder
provide a semantic similarity hint from a reviewed artificial catalog.

Even high similarity is NOT source provenance, certainty, or proof of impact.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
for folder in ("021f","023f","025f"):
    p=str(ROOT/folder)
    if p not in sys.path:sys.path.append(p)

from chorus import PublicProjection, LocalFlanT5Small
from frozen_jobs import CASES, JOBS, frozen_digest
from native_careers import native_rule
from encoder_interview import dense_embeddings,choose_nearest

GATES={
    "FOOD":"Would the responsible organizer verify food service requirements and a named safe-handling owner?",
    "AUDIO":"Would the responsible organizer verify the proposed audio/PA arrangement or choose an acoustic fallback?",
    "ACCESS":"Would the responsible organizer verify a workable accessible entrance and seating route?",
    "STAFF":"Would the responsible organizer verify who will cover welcome, supervision and cleanup?",
    "NONE":None,
}
SYNTHETIC_ONLY=True


def synthesize_review_offer(note: str, model: LocalFlanT5Small | None):
    projection=PublicProjection(
        problem="SIMULATED operator note about a December gathering; experimental question retrieval only.",
        facts=(note,),
        uncertainties=(
            "No human-confirmed blocker or authorization is established by this synthetic text.",
        ),
        proposed_next="Suggest a verification question for human review, never a permission or action.",
    )
    scope=next(j for j in JOBS if j.id=="MISSING_GATE")
    baseline=native_rule(scope,note)
    receipt={
        "schema":"motif025f.semantic-sentinel-offer/v0",
        "input_digest":projection.digest(),
        "frozen_reference_sha256":frozen_digest(),
        "source":"OPERATOR_PUBLIC_SAFE_SYNTHETIC_NOTE",
        "native_finding":baseline,
        "question_status":"HOLD_NO_ACTUAL_SOURCE_VERIFICATION",
        "possible_gate":None,
        "question_for_human_review":None,
        "model_used":False,
        "epistemic_status":"UNVERIFIED_TEXT_SIMILARITY_ONLY",
        "human_execution_approval":False,
        "action_dispatched":False,
        "field_fact_changed":False,
        "event_promise_published":False,
    }
    if baseline!="NONE":
        receipt["possible_gate"]=baseline
        receipt["question_for_human_review"]=GATES[baseline]
        receipt["question_status"]="NATIVE_LEXICAL_POSSIBILITY_REQUIRES_HUMAN_VERIFICATION"
        return receipt
    if model is None:
        receipt["question_status"]="HOLD_NO_MODEL_AVAILABLE"
        return receipt

    references=[c for c in CASES if c.job=="MISSING_GATE"]
    vectors,seconds=dense_embeddings(model,[c.note for c in references]+[note])
    target=vectors[-1]
    scores=[sum(x*y for x,y in zip(v,target)) for v in vectors[:-1]]
    label=choose_nearest(scores,[c.gold for c in references],k=1)
    receipt["model_used"]=True
    receipt["model_encoder_seconds"]=seconds
    receipt["uncalibrated_similarity"]=round(max(scores),6)
    if label not in GATES:
        receipt["question_status"]="HOLD_OUT_OF_REGISTERED_GATE_GRAMMAR"
        return receipt
    if label=="NONE":
        receipt["question_status"]="HOLD_NO_USEFUL_GATE_SUGGESTED"
    else:
        receipt["question_status"]="UNVERIFIED_SEMANTIC_GATE_FOR_HUMAN_REVIEW"
        receipt["possible_gate"]=label
        receipt["question_for_human_review"]=GATES[label]
    return receipt


if __name__=="__main__":
    import os
    import torch
    torch.set_num_threads(2)
    model=LocalFlanT5Small(
        os.environ.get("MOTIF_FLAN_MODEL_DIR","google/flan-t5-small")
    )
    # Synthetic phrase distinct from any real participant record; originally
    # part of the secondary 025F semantic evaluation, NOT a new blind test.
    print(json.dumps(synthesize_review_offer(
        "The speaker cables have not been checked.",model
    ),indent=2,sort_keys=True))
