"""MOTIF-027F: three specialized, CORRELATED T5 encoder nodes.

All three are read-only views of the SAME frozen public FLAN-T5-small
checkpoint; there are not three independently trained witnesses. Role
specialization is by distinct prototype banks and prompt embeddings,
not fine-tuning. Majority agreement is NOT proof.

Roles: SCOUT (nearest previously reviewed gate example), SKEPTIC (task-
prefixed 3NN with explicit NONE alternatives), CARTRIDGE_FINDER (match
phrasing to operator-predeclared question-use vignettes). Their only output
is a proposed *category* which needs an independent source-span relevance
witness and 022F/016 before any synthetic test may proceed.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from collections import Counter
from pathlib import Path
import sys
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
for part in ("021f","025f","026f","027f"):
    p=str(ROOT/part)
    if p not in sys.path:sys.path.append(p)
from frozen_jobs import CASES
from encoder_interview import dense_embeddings,choose_nearest
from semantic_router import CachedT5GateClassifier

# These are the native tool catalog's human-authored purposes, not
# authenticated accounts of past events or actual sensing capabilities.
CARTRIDGES={
 "FOOD":(
  "An unresolved issue with preparing, holding, serving or handling food.",
  "A question about keeping a buffet, meal or donated sandwiches safe.",
  "A question about the responsibility for sharing refreshments.",
 ),
 "AUDIO":(
  "An unresolved problem with microphone, sound equipment or speakers.",
  "A question about checking a broken PA or audio signal.",
  "A question about making a reliable musical amplifier setup.",
 ),
 "ACCESS":(
  "An unresolved entrance, step, ramp or wheelchair access issue.",
  "A question about barrier-free entry to the room.",
  "A question about a lift, doorway or route that guests cannot use.",
 ),
 "STAFF":(
  "An unresolved volunteer or human responsibility assignment.",
  "A question about who covers the door, cleanup or setup.",
  "A question about arranging enough people to run an event.",
 ),
 "NONE":(
  "No missing practical dependency is described.",
  "This is an optional design or ordinary update, not a service problem.",
  "All essentials are settled and there is no unresolved risk.",
 ),
}
TASK_PREFIX="What unmet practical dependency, if any, is described? "

@dataclass(frozen=True)
class NodeOutput:
    role:str
    label:str
    similarity:float
    elapsed_seconds:float
    reference_count:int
    certainty:"str"="UNCALIBRATED_SIMILARITY_NOT_PROBABILITY"


class ThreeSpecialistEncoder:
    """Load model once; cache 3 banks; query each specialization separately."""
    name="THREE_CORRELATED_FLAN_T5_ENCODER_SPECIALISTS"

    def __init__(self,model):
        self.model=model
        self.scout=CachedT5GateClassifier(model)
        self.gate_references=[c for c in CASES if c.job=="MISSING_GATE"]
        self.skeptic_labels=tuple(c.gold for c in self.gate_references)
        self.skeptic_vectors,self.skeptic_build_seconds=dense_embeddings(
            model,[TASK_PREFIX+c.note for c in self.gate_references])
        bank=[(gate,example) for gate,examples in CARTRIDGES.items()
              for example in examples]
        self.finder_labels=tuple(x[0] for x in bank)
        self.finder_vectors,self.finder_build_seconds=dense_embeddings(
            model,[x[1] for x in bank])
        self.calls=0
        self.inference_seconds=0.

    @staticmethod
    def _nearest(query,prototypes,labels,k=1):
        sims=[sum(x*y for x,y in zip(vec,query)) for vec in prototypes]
        return choose_nearest(sims,labels,k=k),max(sims)

    def opinions(self,note:str)->tuple[NodeOutput,...]:
        t0=monotonic()
        scout_label,scout_score=self.scout.classify(note)
        scout_seconds=monotonic()-t0

        t1=monotonic()
        skv,seconds=dense_embeddings(self.model,[TASK_PREFIX+note])
        skeptic_label,skeptic_score=self._nearest(
            skv[0],self.skeptic_vectors,self.skeptic_labels,k=3)
        skeptic_seconds=monotonic()-t1

        t2=monotonic()
        fv,seconds=dense_embeddings(self.model,[note])
        finder_label,finder_score=self._nearest(
            fv[0],self.finder_vectors,self.finder_labels,k=1)
        finder_seconds=monotonic()-t2
        self.calls+=3
        elapsed=scout_seconds+skeptic_seconds+finder_seconds
        self.inference_seconds+=elapsed
        return (
            NodeOutput("SCOUT",scout_label,round(scout_score,6),
                       round(scout_seconds,6),len(self.gate_references)),
            NodeOutput("SKEPTIC",skeptic_label,round(skeptic_score,6),
                       round(skeptic_seconds,6),len(self.skeptic_labels)),
            NodeOutput("CARTRIDGE_FINDER",finder_label,round(finder_score,6),
                       round(finder_seconds,6),len(self.finder_labels)),
        )


def combine_opinions(opinions:tuple[NodeOutput,...],*,quorum=2)->dict:
    if len(opinions)!=3 or len({o.role for o in opinions})!=3:
        raise ValueError("HOLD_INCOMPLETE_OR_REPEATED_T5_NODES")
    if quorum not in (2,3):
        raise ValueError("HOLD_INVALID_QUORUM")
    labels=Counter(o.label for o in opinions)
    label,count=sorted(labels.items(),key=lambda x:(-x[1],x[0]))[0]
    if label not in CARTRIDGES:
        return {"status":"HOLD_UNKNOWN_NODE_LABEL","candidate":None,
                "votes":dict(labels),"quorum":quorum,
                "three_are_independent_witnesses":False}
    if count<quorum or label=="NONE":
        return {"status":"HOLD_NO_REVIEWABLE_QUORUM","candidate":None,
                "votes":dict(labels),"quorum":quorum,
                "three_are_independent_witnesses":False}
    return {"status":"UNVERIFIED_SEMANTIC_QUORUM","candidate":label,
            "votes":dict(labels),"quorum":quorum,
            "three_are_independent_witnesses":False}
