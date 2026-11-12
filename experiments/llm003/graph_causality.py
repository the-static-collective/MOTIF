"""LLM-003C: can low-rank control learn the graph when text is held fixed?

Post-hoc shortcut-resistance falsifier motivated by the real 003B result:
91.7% accuracy persisted after graph-bit shuffling. The first benchmark could
be solved largely by 'probe' versus 'publish' words. Here EVERY candidate is
the same 'use' token string. Only tool/permission graph bits can differentiate
the four owner-defined scenarios. Exact classical AND remains a perfect baseline.
"""
from __future__ import annotations
import json,random,time
import torch
import torch.nn.functional as F

from real_pretrained import load,MODEL,REVISION
from train_pretrained_adapter import Runner,Adapter,TRAIN_PREFIXES,TEST_PREFIXES

def owner_truth(tool,permit):
    return int(tool and permit)

def evaluate(runner,adapter=None,flip_graph=False):
    records=[]
    with torch.no_grad():
        for pre in TEST_PREFIXES:
            for tool in (0,1):
                for permit in (0,1):
                    original=(tool,permit)
                    test_features=(1-tool,1-permit) if flip_graph else original
                    z,norm=runner.logits(pre,*test_features,"use",adapter=adapter)
                    prob=float(z.softmax(-1)[1])
                    pred=int(z[1]>=z[0])
                    y=owner_truth(*original)
                    records.append({"prompt_index":TEST_PREFIXES.index(pre),
                        "original_tool":tool,"original_permission":permit,
                        "presented_graph_tool":test_features[0],
                        "presented_graph_permission":test_features[1],
                        "owner_true_label":y,"prediction":pred,
                        "p_one":round(prob,5),"correct":pred==y,
                        "hidden_injection_norm":round(norm,4)})
    return {"n":len(records),"correct":sum(r["correct"] for r in records),
            "accuracy":round(sum(r["correct"] for r in records)/len(records),5),
            "positive_recall":round(sum(r["correct"] for r in records if r["owner_true_label"]==1)/
                                   sum(r["owner_true_label"]==1 for r in records),5),
            "negative_recall":round(sum(r["correct"] for r in records if r["owner_true_label"]==0)/
                                   sum(r["owner_true_label"]==0 for r in records),5),
            "records":records}

def learn(runner,mode):
    if mode not in ("verified","positive_only","corrupt_negative"):raise ValueError("UNKNOWN_MODE")
    adapter=Adapter(runner.hidden)
    opt=torch.optim.AdamW(adapter.parameters(),lr=.075,weight_decay=.001)
    rng=random.Random(20261112)
    negatives=[(0,0),(0,1),(1,0)]
    plan=[]
    for i in range(48):
        if mode=="positive_only" or i%2==0:
            state=(1,1)
        else:
            state=negatives[rng.randrange(3)]
        prefix=TRAIN_PREFIXES[rng.randrange(len(TRAIN_PREFIXES))]
        label=owner_truth(*state)
        if mode=="corrupt_negative" and label==0 and random.Random(92000+i).random()<.5:
            label=1
        plan.append((state,prefix,label))
    losses=[]
    started=time.perf_counter()
    for (tool,permit),pre,label in plan:
        opt.zero_grad(set_to_none=True)
        z,_=runner.logits(pre,tool,permit,"use",adapter)
        loss=F.cross_entropy(z.reshape(1,2),torch.tensor([label],dtype=torch.long))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(adapter.parameters(),2.)
        opt.step()
        losses.append(float(loss.detach()))
    return adapter,{"steps":48,"seconds":round(time.perf_counter()-started,3),
                    "first_loss":round(losses[0],5),"last_loss":round(losses[-1],5),
                    "positive_label_fraction":round(sum(e[2] for e in plan)/len(plan),4)}

def main():
    model,tok,load_sec=load()
    runner=Runner(model,tok)
    baseline=evaluate(runner)
    arms={}
    for mode in ("verified","positive_only","corrupt_negative"):
        adapter,train=learn(runner,mode)
        normal=evaluate(runner,adapter)
        counterfactual=evaluate(runner,adapter,flip_graph=True)
        arms[mode]={"training":train,"heldout":normal,
                    "graph_flip_control":counterfactual,
                    "accuracy_drop_when_graph_flipped":round(normal["accuracy"]-counterfactual["accuracy"],5)}
    r={"status":"REAL_PRETRAINED_GRAPH_CAUSALITY_SHORTCUT_AUDIT",
       "model":MODEL,"revision":REVISION,"model_weights_frozen":all(not p.requires_grad for p in model.parameters()),
       "candidate_action_text":"USE_FOR_EVERY_CASE","train_examples":48,"heldout_cases":16,
       "label_rule":"tool_present AND permission_granted",
       "unadapted":baseline,"constant_majority_baseline_accuracy":.75,
       "exact_classical_oracle_accuracy":1.0,"arms":arms,
       "posthoc_after_original_003B_91_7PCT_NOT_DEGRADED_BY_SHUFFLING":True,
       "real_world_consent_or_safety_certified":False,"external_actions":False}
    print("LLM003C_JSON_BEGIN")
    print(json.dumps(r,sort_keys=True))
    print("LLM003C_JSON_END")

if __name__=="__main__":
    main()
