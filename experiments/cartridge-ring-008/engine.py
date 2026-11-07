"""RING-008: typed executable semantics PROGRAM DSL, safe to synthesize as data.

The program combines learned statistical maps to *multiple relational slots*:
  utterance -> (mode, topic, operator) with optional abstention.
This is a small supervised semantic parser and code-free algorithm search,
NOT natural language understanding generally or permission to take an action.

Operators are inspectable, preaudited and fully offline. New searched programs
change which operators are composed, the decoder and whether they parse slots
separately vs jointly; the search cannot generate Python, tools or connectors.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
import json
import math
import re

import world

SCHEMA="motif.ring008.generated-meaning-program.v1"
PROGRAM_OPS=("word","bigram","skip","char3","edge","affix","order")
DECODERS=("bayes","centroid")
BINDINGS=("factorized","joint")
MARGINS=(0.0,0.04,0.12,0.25,0.4)
OVERLAPS=(0,2,5)
MAX_OPS=4
MAX_TEXT=320

class HOLD(ValueError):
    pass


def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def validate(spec):
    if (not isinstance(spec,dict)
            or set(spec)!={"ops","decoder","binding","margin","overlap"}
            or not isinstance(spec["ops"],list)
            or not 1<=len(spec["ops"])<=MAX_OPS
            or len(set(spec["ops"]))!=len(spec["ops"])
            or spec["ops"]!=sorted(spec["ops"])
            or any(x not in PROGRAM_OPS for x in spec["ops"])
            or spec["decoder"] not in DECODERS
            or spec["binding"] not in BINDINGS
            or spec["margin"] not in MARGINS
            or spec["overlap"] not in OVERLAPS):
        raise HOLD("Executable DSL grammar violation")
    return spec


def tokens(text):
    if type(text) is not str or not 1<=len(text)<=MAX_TEXT:
        raise HOLD("Malformed or excessive text")
    return re.findall(r"[a-z]+(?:'[a-z]+)?",text.casefold())


def features(text,ops):
    ts=tokens(text)
    out=Counter()
    if "word" in ops:
        out.update("w:"+t for t in ts)
    if "bigram" in ops:
        out.update("b:"+a+"|"+b for a,b in zip(ts,ts[1:]))
    if "skip" in ops:
        out.update("s:"+ts[i]+"|"+ts[i+gap]
                   for gap in (2,3) for i in range(len(ts)-gap))
    if "char3" in ops:
        for token in ts:
            marked="^"+token+"$"
            out.update("c:"+marked[i:i+3] for i in range(len(marked)-2))
    if "edge" in ops:
        for i,token in enumerate(ts[:2]):
            out["head:"+str(i)+":"+token]+=1
        for i,token in enumerate(reversed(ts[-2:])):
            out["tail:"+str(i)+":"+token]+=1
    if "affix" in ops:
        for token in ts:
            if len(token)>=4:
                out["pre:"+token[:3]]+=1
                out["suf:"+token[-3:]]+=1
    if "order" in ops:
        # Learned token-pair order. No preconfigured intent or meaning words.
        for i in range(len(ts)):
            for j in range(i+1,min(len(ts),i+5)):
                out["o:"+ts[i]+">"+ts[j]]+=1
    if len(out)>3000:
        raise HOLD("Excessive emitted features")
    return out


def label(frame,binding):
    if binding=="joint":
        return "|".join(frame[s] for s in world.SLOTS)
    raise HOLD("The joint label encoder requires joint binding")


class LearnedDecoder:
    def __init__(self,examples,spec):
        validate(spec)
        self.spec=spec
        self.rows=[(features(x["text"],spec["ops"]),x["frame"])
                   for x in examples]
        if not self.rows:
            raise HOLD("Source-owned training evidence missing")
        self.vocabulary=set(k for v,_ in self.rows for k in v)
        self.models={}
        for slot in (world.SLOTS if spec["binding"]=="factorized" else ("joint",)):
            docs=Counter()
            wordcounts=defaultdict(Counter)
            total=Counter()
            for feats,frame in self.rows:
                k=frame[slot] if slot!="joint" else label(frame,"joint")
                docs[k]+=1
                wordcounts[k].update(feats)
                total[k]+=sum(feats.values())
            self.models[slot]={
                "docs":docs,"terms":wordcounts,"total":total,
                "classes":tuple(sorted(docs)),
            }
        self.train_count=len(self.rows)

    def _scores(self,feats,model):
        vocab=len(self.vocabulary)+1
        scored={}
        for k in model["classes"]:
            counts=model["terms"][k]
            if self.spec["decoder"]=="bayes":
                denom=model["total"][k]+vocab
                prior=math.log((model["docs"][k]+1)/
                               (self.train_count+len(model["classes"])))
                score=prior+sum(count*math.log((counts[t]+1)/denom)
                                for t,count in feats.items())
                # Scale by observed feature number; equal code across
                # candidates avoids numerical overflow, not calibration.
                scored[k]=score/max(1,sum(feats.values()))
            else:
                # Class centroid cosine similarity, not a vague magic model:
                # TF-IDF-like idf is intentionally omitted to make the source
                # feature geometry inspectable and deterministic.
                numer=sum(feats[t]*counts.get(t,0) for t in feats)
                fden=math.sqrt(sum(v*v for v in feats.values()))
                cden=math.sqrt(sum(v*v for v in counts.values()))
                scored[k]=4*numer/max(1.0,fden*cden)
        high=max(scored.values())
        masses={k:math.exp(v-high) for k,v in scored.items()}
        den=sum(masses.values())
        ranking=sorted(scored,key=lambda k:(-masses[k],k))
        best=ranking[0]
        second=ranking[1] if len(ranking)>1 else None
        margin=(masses[best]-(masses[second] if second else 0))/den
        return best,margin,round(masses[best]/den,6)

    def parse(self,text):
        feats=features(text,self.spec["ops"])
        known=sum(v for k,v in feats.items() if k in self.vocabulary)
        if known<self.spec["overlap"]:
            return {"status":"HOLD","frame":None,
                    "reason":"INSUFFICIENT_GROUNDED_FEATURE_OVERLAP",
                    "known_feature_occurrences":known,
                    "raw_text_sha256":sha256(text.encode()).hexdigest()}
        frame={}
        margins=[]
        confidences=[]
        for slot,model in self.models.items():
            choice,margin,conf=self._scores(feats,model)
            margins.append(margin)
            confidences.append(conf)
            if slot=="joint":
                parts=choice.split("|")
                if len(parts)!=len(world.SLOTS):
                    raise HOLD("Malformed learned joint label")
                frame=dict(zip(world.SLOTS,parts))
            else:
                frame[slot]=choice
        assert set(frame)==set(world.SLOTS)
        if (min(margins)<self.spec["margin"]
                or "UNKNOWN" in frame.values()):
            return {"status":"HOLD","frame":None,
                    "reason":"LOW_MARGIN_OR_UNGROUNDED_ROLE",
                    "raw_text_sha256":sha256(text.encode()).hexdigest(),
                    "known_feature_occurrences":known}
        return {"status":"NONAUTHORITATIVE_FRAME_HYPOTHESIS",
                "frame":frame,"reason":"SUPERVISED_TYPED_SOURCE_FEATURES_ONLY",
                "role_margin_min":round(min(margins),6),
                "role_confidence_min":round(min(confidences),6),
                "raw_text_sha256":sha256(text.encode()).hexdigest(),
                "known_feature_occurrences":known,
                "execution_authority":"NONE"}

def train(dataset,spec):
    world.check(dataset,expected="train")
    return LearnedDecoder(dataset["rows"],spec)


def evaluate(decoder,examples):
    outcomes={
        "count":0,"exact_frames":0,"decisive":0,
        "wrong_decisive":0,"unsafe_false_readonly":0,
        "benign_exact_decisive":0,"benign_abstained":0,
        "correct_unknown_holds":0,"unsupported_frame_hypotheses":0,
    }
    witnesses=[]
    for row in examples:
        actual=row["frame"]
        decoded=decoder.parse(row["text"])
        frame=decoded["frame"]
        unknown=actual["mode"]=="UNKNOWN"
        decisive=frame is not None
        correct=decisive and frame==actual
        false_readonly=(decisive and actual["mode"]=="ACT"
                        and frame["mode"] in ("INQUIRE","META"))
        outcomes["count"]+=1
        if correct:outcomes["exact_frames"]+=1
        if decisive:outcomes["decisive"]+=1
        if decisive and not correct:outcomes["wrong_decisive"]+=1
        if false_readonly:outcomes["unsafe_false_readonly"]+=1
        if correct and actual["mode"]!="ACT":outcomes["benign_exact_decisive"]+=1
        if not decisive and actual["mode"]!="ACT" and not unknown:
            outcomes["benign_abstained"]+=1
        if not decisive and unknown:outcomes["correct_unknown_holds"]+=1
        if decisive and unknown:outcomes["unsupported_frame_hypotheses"]+=1
        witnesses.append({
            "source_sha256":decoded["raw_text_sha256"],
            "target_frame":actual,"predicted_frame":frame,
            "status":decoded["status"],
            "false_readonly":bool(false_readonly),"exact":bool(correct),
        })
    # The declared objective is developer-chosen; maximizing this does not
    # prove a general or ethically correct language learning algorithm.
    metric=(5*outcomes["exact_frames"]
            -8*outcomes["wrong_decisive"]
            -30*outcomes["unsafe_false_readonly"]
            -1*outcomes["benign_abstained"]
            -2*outcomes["unsupported_frame_hypotheses"])
    return {"metrics":outcomes,"declared_objective":metric,"per_case":witnesses}
