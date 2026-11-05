"""MOTIF-025F: alternate experimental job — T5 as passive ENCODER.

No text generation, no typed decision output, no rewriting of native facts.
Frozen 36 labeled synthetic reference snippets and 24 different-phrasing
synthetic evaluation snippets. Mean-pool actual T5 encoder hidden states, then
nearest-neighbor retrieval; compare same-reference classical TF-IDF.

Choosing labels by untrained embeddings is only a shadow classifier, not
evidence that T5 has learned source authority or physical causality.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import log,sqrt
from pathlib import Path
import json
import os
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
for rel in ("021f","023f","025f"):
    p=str(ROOT/rel)
    if p not in sys.path:sys.path.append(p)

from chorus import LocalFlanT5Small
from frozen_jobs import CASES, JOBS
from semantic_holdout import SEMANTIC_QUERIES
from native_careers import native_rule, severe_false_permission


def sparse_features(note: str) -> Counter:
    words=re.findall(r"[a-z]+",note.lower())
    features=Counter()
    for word in words:
        features["word:"+word]+=1
    for a,b in zip(words,words[1:]):
        features["bigram:"+a+"_"+b]+=1
    compact=" ".join(words)
    for i in range(max(0,len(compact)-2)):
        features["char3:"+compact[i:i+3]]+=.2
    return features


def sparse_reference_vectors(refs,queries):
    raw=[sparse_features(s) for s in refs+queries]
    num_ref=len(refs)
    docfreq=Counter()
    for row in raw[:num_ref]:
        for k in row:
            docfreq[k]+=1
    vect=[]
    for row in raw:
        v={k:(1+log(max(1.,value))) * (1+log((1+num_ref)/(1+docfreq[k])))
           for k,value in row.items() if value>0 and docfreq[k]>0}
        norm=sqrt(sum(x*x for x in v.values())) or 1.
        vect.append({k:value/norm for k,value in v.items()})
    return vect[:num_ref],vect[num_ref:]


def sparse_sim(a,b) -> float:
    if len(a)>len(b):a,b=b,a
    return sum(value*b.get(k,0.) for k,value in a.items())


def dense_embeddings(model: LocalFlanT5Small, notes: list[str]):
    """Actual local model encoder hidden states, no decoder generation."""
    import torch
    import torch.nn.functional as F
    model._prepare()
    tokenizer=model._tokenizer
    net=model._model
    start=time.monotonic()
    vectors=[]
    for begin in range(0,len(notes),16):
        batch=notes[begin:begin+16]
        inputs=tokenizer(batch,return_tensors="pt",padding=True,
                         truncation=True,max_length=128)
        with torch.inference_mode():
            hidden=net.encoder(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                return_dict=True,
            ).last_hidden_state
            mask=inputs["attention_mask"].unsqueeze(-1)
            pooled=(hidden*mask).sum(dim=1)/mask.sum(dim=1).clamp(min=1)
            vectors.extend(F.normalize(pooled,dim=1).cpu().tolist())
    return vectors,round(time.monotonic()-start,4)


def choose_nearest(similarities, ref_labels, *, k=1) -> str:
    if not similarities:
        raise ValueError("HOLD_NO_REFERENCE_EXAMPLES")
    ordered=sorted(range(len(similarities)),
                   key=lambda i:(-similarities[i],i))[:k]
    scores=defaultdict(float)
    for idx in ordered:
        scores[ref_labels[idx]]+=max(0.,similarities[idx])
    if not any(scores.values()):
        # The fallback is explicit, not an LLM authorization.
        return ref_labels[ordered[0]]
    # On ties, use the first-ranked label for deterministic custody.
    return max(scores,key=lambda label:(scores[label],
                -next(j for j in range(len(ordered))
                      if ref_labels[ordered[j]]==label)))


def interview_encoder():
    import torch
    torch.set_num_threads(2)
    started=time.monotonic()
    model=LocalFlanT5Small(
        os.environ.get("MOTIF_FLAN_MODEL_DIR","google/flan-t5-small")
    )
    load_start=time.monotonic()
    model._prepare()
    load_seconds=round(time.monotonic()-load_start,4)
    outcomes=[]
    embed_cpu=0.
    sparse_cpu=0.
    for job in JOBS:
        refs=[c for c in CASES if c.job==job.id]
        trials=[c for c in SEMANTIC_QUERIES if c.job==job.id]
        notes=[c.note for c in refs+trials]
        vectors,elapsed=dense_embeddings(model,notes)
        embed_cpu+=elapsed
        ref_vectors=vectors[:len(refs)]
        query_vectors=vectors[len(refs):]
        t=time.monotonic()
        tfref,tfquery=sparse_reference_vectors(
            [c.note for c in refs],[c.note for c in trials],
        )
        sparse_cpu+=time.monotonic()-t
        labels=[c.gold for c in refs]
        for idx,case in enumerate(trials):
            dense_scores=[
                sum(a*b for a,b in zip(vector,query_vectors[idx]))
                for vector in ref_vectors
            ]
            sparse_scores=[
                sparse_sim(vector,tfquery[idx])
                for vector in tfref
            ]
            choices={
                "NATIVE_HANDWRITTEN_RULE":native_rule(job,case.note),
                "CLASSICAL_TFIDF_1NN":choose_nearest(sparse_scores,labels,k=1),
                "CLASSICAL_TFIDF_3NN":choose_nearest(sparse_scores,labels,k=3),
                "REAL_T5_ENCODER_1NN":choose_nearest(dense_scores,labels,k=1),
                "REAL_T5_ENCODER_3NN":choose_nearest(dense_scores,labels,k=3),
            }
            outcomes.append({
                "case_id":case.id,
                "job":case.job,
                "gold":case.gold,
                "choices":choices,
                "false_permissions":{
                    method:severe_false_permission(case,val)
                    for method,val in choices.items()
                },
                "source_examples_for_all_methods":len(refs),
                "true_simulated_label_not_shared_with_encoder":True,
            })
    names=list(outcomes[0]["choices"])
    metrics={}
    for name in names:
        score=sum(r["choices"][name]==r["gold"] for r in outcomes)
        unsafe=sum(r["false_permissions"][name] for r in outcomes)
        metrics[name]={
            "correct":score,"total":len(outcomes),
            "accuracy":round(score/len(outcomes),4),
            "false_permissions":unsafe,
            "by_job":{
                j.id:{
                    "correct":sum(r["choices"][name]==r["gold"]
                        for r in outcomes if r["job"]==j.id),
                    "total":sum(r["job"]==j.id for r in outcomes),
                } for j in JOBS
            },
        }
    strongest_classical=max(
        (metrics[k]["correct"] for k in names if not k.startswith("REAL_T5_")),
        default=0
    )
    best_encoder=max(metrics["REAL_T5_ENCODER_1NN"]["correct"],
                     metrics["REAL_T5_ENCODER_3NN"]["correct"])
    return {
        "schema":"motif025f.real-t5-encoder-job/v0",
        "model":"google/flan-t5-small",
        "revision":os.environ.get("MOTIF_FLAN_REVISION","LOCAL_UNPINNED"),
        "real_model_encoder_executed":model._model is not None,
        "model_decoder_calls":0,
        "frozen_reference_examples":len(CASES),
        "frozen_semantic_holdout_examples":len(SEMANTIC_QUERIES),
        "t5_load_seconds":load_seconds,
        "t5_encoder_cpu_seconds":round(embed_cpu,4),
        "classical_tfidf_build_and_search_seconds":round(sparse_cpu,4),
        "wall_seconds":round(time.monotonic()-started,4),
        "metrics":metrics,
        "records":outcomes,
        "best_t5_encoder_outperformed_best_classical":best_encoder>strongest_classical,
        "heldout_is_artificial_researcher_written":True,
        "training_or_finetune":False,
        "external_inference_or_action":False,
        "role_can_override_native_decision":False,
    }


if __name__=="__main__":
    print(json.dumps(interview_encoder(),indent=2,sort_keys=True))
