"""LLM-003B: exploratory training of a rank-2 suffix graph adapter on actual SmolLM2.

All labels are programmer-defined fictional rules. Frozen pretrained backbone;
only rank-two U/V trained. Exact strong classical baseline is 100% by design.
The experiment cannot establish a new LLM architecture or real-world safety.
"""
from __future__ import annotations
import copy,json,time,random,sys
from pathlib import Path
import torch
import torch.nn.functional as NF

sys.path.insert(0,str(Path(__file__).resolve().parent))
from real_pretrained import load,MODEL,REVISION,graph_delta

ACTIONS=("probe","use","publish")
TRAIN_PREFIXES=(
 "Fictional tool review. The attached graph encodes tool status and steward permission. Decide if the proposed hypothetical action is allowed. Answer one digit: 0 or 1.\n",
 "Synthetic approval exercise: two private numeric features are conveyed only by the graph attachment. Assess proposed move permissibility. Return 0 or 1.\n",
)
TEST_PREFIXES=(
 "A research simulation considers a candidate next step. An accompanying graph encodes known facts. State the binary decision 0 or 1.\n",
 "In this imaginary workflow, the approved-action rule is implicit in verified training examples, and condition bits arrive in a graph. Choose 0 or 1.\n",
 "A separate fictional planning board provides typed binary context. Evaluate one requested action, output only its binary gate 0 or 1.\n",
 "For a synthetic safety check, use the attached graph features to judge a proposal; output the result as digit 0 or 1.\n",
)

def rule(tool,permit,action):
    return int(action=="probe" or (action=="use" and tool and permit))

def features(tool,permit,action):
    return torch.tensor([tool,permit,int(action=="probe"),int(action=="use"),
                         int(action=="publish"),1.0],dtype=torch.float32)

class Adapter(torch.nn.Module):
    def __init__(self,hidden):
        super().__init__()
        rng=torch.Generator().manual_seed(20261112)
        self.u=torch.nn.Parameter(torch.randn(hidden,2,generator=rng)*.025)
        self.v=torch.nn.Parameter(torch.randn(2,6,generator=rng)*.05)
    def forward(self,g):
        d=2.5*torch.tanh(self.u@(self.v@g))
        return d*torch.clamp(torch.tensor(8.0)/(d.norm()+1e-12),max=1.0)

class Runner:
    def __init__(self,model,tokenizer):
        self.model=model
        self.tok=tokenizer
        self.model.eval()
        for p in self.model.parameters():p.requires_grad_(False)
        self.embed=self.model.get_input_embeddings()
        self.hidden=self.embed.weight.shape[-1]
        self.digits=[tokenizer.encode(str(i),add_special_tokens=False) for i in (0,1)]
        if not all(len(z)==1 for z in self.digits):raise RuntimeError("BAD_DIGIT_TOKENS")
        self.digit_indices=[z[0] for z in self.digits]
        self.prefixes={}
        with torch.no_grad():
            for text in TRAIN_PREFIXES+TEST_PREFIXES:
                ids=tokenizer.encode(text,return_tensors="pt",add_special_tokens=True)
                if ids.shape[1]>=128:raise RuntimeError("PREFIX_TOO_LONG")
                self.prefixes[text]=(ids.shape[1],
                    self.model(input_ids=ids,use_cache=True,return_dict=True).past_key_values)
        self.suffixes={}
        for action in ACTIONS:
            ids=tokenizer.encode("Candidate action: "+action+". Decision: ",add_special_tokens=False,
                                 return_tensors="pt")
            self.suffixes[action]=self.embed(ids).detach().clone()
    def logits(self,prefix,tool,permit,action,adapter=None):
        n,kv=self.prefixes[prefix]
        suffix=self.suffixes[action]
        if adapter is None:
            e=suffix
            extra=0.
        else:
            d=adapter(features(tool,permit,action))
            extra=d.norm()
            # Branch-only latent perturbation at final suffix token.
            mask=torch.zeros_like(suffix)
            mask[0,-1,:]=1
            e=suffix+mask*d.view(1,1,-1)
        mask=torch.ones((1,n+e.shape[1]),dtype=torch.long)
        out=self.model(inputs_embeds=e,past_key_values=copy.deepcopy(kv),
                       attention_mask=mask,use_cache=True,return_dict=True).logits[0,-1]
        return out[self.digit_indices],float(extra.detach()) if isinstance(extra,torch.Tensor) else 0.
    def evaluate(self,adapter=None,shuffle=False):
        results=[];norms=[]
        with torch.no_grad():
            for prefix in TEST_PREFIXES:
                for tool in (0,1):
                    for permit in (0,1):
                        for action in ACTIONS:
                            lbl=rule(tool,permit,action)
                            ft,fp=(1-tool,1-permit) if shuffle else (tool,permit)
                            z,norm=self.logits(prefix,ft,fp,action,adapter)
                            prob=float(z.softmax(dim=-1)[lbl])
                            predicted=int(z[1]>=z[0])
                            results.append((lbl,predicted,prob))
                            norms.append(norm)
        n=len(results)
        neg=[x for x in results if x[0]==0]
        pos=[x for x in results if x[0]==1]
        return {"n":n,"accuracy":round(sum(y==p for y,p,_ in results)/n,5),
                "negative_recall":round(sum(p==0 for y,p,_ in neg)/len(neg),5),
                "positive_recall":round(sum(p==1 for y,p,_ in pos)/len(pos),5),
                "cross_entropy":round(-sum(__import__('math').log(max(prob,1e-10))
                                  for _,_,prob in results)/n,5),
                "max_hidden_injection_l2":round(max(norms),5),
                "correct_count":sum(y==p for y,p,_ in results)}

def train(runner,mode,steps=48):
    if mode not in ("verified","positive_only","corrupt_negative"):raise ValueError("BAD_ARM")
    adapter=Adapter(runner.hidden)
    opt=torch.optim.AdamW(adapter.parameters(),lr=.075,weight_decay=.001)
    samples=[(prefix,tool,permit,action,rule(tool,permit,action))
            for prefix in TRAIN_PREFIXES for tool in (0,1) for permit in (0,1)
            for action in ACTIONS]
    rng=random.Random(20261112)
    plan=[]
    for i in range(steps):
        if mode=="positive_only":
            candidates=[e for e in samples if e[-1]==1]
            plan.append(candidates[rng.randrange(len(candidates))])
        else:
            plan.append(samples[rng.randrange(len(samples))])
    t0=time.perf_counter()
    losses=[]
    for i,(prefix,tool,permit,action,y_true) in enumerate(plan):
        label=y_true
        if mode=="corrupt_negative" and y_true==0:
            # Exactly deterministic ~50% expected report corruption, not
            # independent physical verification; deliberately misleading.
            if random.Random(6100+i).random()<.5:label=1
        opt.zero_grad(set_to_none=True)
        z,_=runner.logits(prefix,tool,permit,action,adapter)
        loss=NF.cross_entropy(z.reshape(1,2),torch.tensor([label],dtype=torch.long))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(adapter.parameters(),max_norm=2.)
        opt.step()
        losses.append(float(loss.detach()))
    return adapter,{"steps":len(plan),"seconds":round(time.perf_counter()-t0,3),
        "loss_first":round(losses[0],5),"loss_last":round(losses[-1],5)}

def main():
    model,tok,load_time=load()
    runner=Runner(model,tok)
    base=runner.evaluate()
    arms={}
    for mode in ("verified","positive_only","corrupt_negative"):
        a,training=train(runner,mode)
        arms[mode]={"train":training,"test":runner.evaluate(a),
                    "shuffled_graph_test":runner.evaluate(a,shuffle=True)}
    out={"status":"REAL_PRETRAINED_GRAPH_ADAPTER_TRAINED",
         "model":MODEL,"revision":REVISION,"hidden_dim":runner.hidden,
         "rank":2,"frozen_model_parameters":all(not p.requires_grad for p in model.parameters()),
         "tested_heldout_prompts":len(TEST_PREFIXES),"cases_per_prompt":12,
         "unadapted_test":base,"arms":arms,
         "classical_exact":{"accuracy":1.0,"note":"ENGINEER_AUTHORED_RULE"},
         "source":"PUBLIC_AUTHOR_SYNTHETIC_ONLY",
         "external_actions":False,"verified_negative_training_was_human_authored":True,
         "interpretation":"EXPLORATORY_POSTHOC_NOT_GENERAL_LLM_REASONING"}
    print("LLM003B_JSON_BEGIN")
    print(json.dumps(out,sort_keys=True))
    print("LLM003B_JSON_END")
if __name__=="__main__":main()
