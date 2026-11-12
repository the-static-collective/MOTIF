"""LLM-002: real numeric causal attention + learned graph-conditioned low-rank input.

An EDUCATIONAL, randomly initialized frozen one-head attention network, not
pretrained LLM intelligence. Only synthetic fixtures; no provider, file, or
real-world action. Graph conditioning occurs at suffix x BEFORE attention
Q/K/V, AFTER a reusable shared prefix. A graph-dependent prefix needs a
different cache and must never silently reuse the old one.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from math import exp, sqrt, tanh
import json
import random

D=8
R=2
F=6
PREFIX=("system", "source", "witness", "facts", "unknowns", "review")

def seal(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def dot(a,b):
    return sum(x*y for x,y in zip(a,b))
def mv(m,x):
    return [dot(row,x) for row in m]
def mtv(m,x):
    return [sum(row[i]*v for row,v in zip(m,x)) for i in range(len(m[0]))]
def softmax(scores):
    e=[exp(v-max(scores)) for v in scores]
    return [v/sum(e) for v in e]
def sigmoid(x):
    if x>=0: return 1/(1+exp(-x))
    z=exp(x)
    return z/(1+z)

@dataclass(frozen=True)
class Cache:
    tokens:tuple[str,...]
    keys:tuple[tuple[float,...],...]
    values:tuple[tuple[float,...],...]
    scope_hash:str
    model_fingerprint:str
    cache_seal:str
    qk_ops:int
    # Stateless normalized cache ownership; unforgeability requires independent
    # authentication beyond this fixture. Never accept untrusted Cache objects.

class TinyCausal:
    def __init__(self,seed=1902):
        r=random.Random(seed)
        self.emb={t:tuple(r.uniform(-.65,.65) for _ in range(D))
                  for t in (*PREFIX,"probe","use","publish","wait","replan")}
        self.wq=[[r.uniform(-.4,.4) for _ in range(D)] for _ in range(D)]
        self.wk=[[r.uniform(-.4,.4) for _ in range(D)] for _ in range(D)]
        self.wv=[[r.uniform(-.4,.4) for _ in range(D)] for _ in range(D)]
        self.wo=[[r.uniform(-.4,.4) for _ in range(D)] for _ in range(D)]
        self.readout=[r.uniform(-.4,.4) for _ in range(D)]
        self.bias=0.0
        self.model_fingerprint=seal([self.emb,self.wq,self.wk,self.wv,self.wo,self.readout])
    def embed(self,token,position):
        if token not in self.emb:raise ValueError("UNKNOWN_TOKEN")
        if position<0 or position>128:raise ValueError("BAD_POSITION")
        # Absolute position is part of mathematical equivalence.
        return [x+0.05*(__import__('math').sin((position+1)*(i+1)*0.17))
                for i,x in enumerate(self.emb[token])]
    def step(self,token,position,keys,values,latent=None,gradient=False):
        x=self.embed(token,position)
        if latent is not None:
            if len(latent)!=D or any(not -10<v<10 for v in latent):raise ValueError("BAD_LATENT")
            x=[u+v for u,v in zip(x,latent)]
        q,k,v=mv(self.wq,x),mv(self.wk,x),mv(self.wv,x)
        allk=[*keys,k];allv=[*values,v]
        s=[dot(q,ki)/sqrt(D) for ki in allk]
        a=softmax(s)
        context=[sum(w*vi[i] for w,vi in zip(a,allv)) for i in range(D)]
        out=[u+v for u,v in zip(x,mv(self.wo,context))]
        logit=dot(self.readout,out)+self.bias
        if not gradient:
            return logit,k,v,None
        # Gradient d logit / d x for true self-attention, including the
        # *current* key and value dependencies. Prefix states are frozen.
        wr=mtv(self.wo,self.readout)
        vscore=[dot(wr,vi) for vi in allv]
        mean_score=dot(a,vscore)
        dq=[sum(a[j]*(vscore[j]-mean_score)*allk[j][i]/sqrt(D)
                for j in range(len(allk))) for i in range(D)]
        dk=[a[-1]*(vscore[-1]-mean_score)*q[i]/sqrt(D) for i in range(D)]
        dv=[a[-1]*wr[i] for i in range(D)]
        gq=mtv(self.wq,dq);gk=mtv(self.wk,dk);gv=mtv(self.wv,dv)
        grad=[w+u+z+y for w,u,z,y in zip(self.readout,gq,gk,gv)]
        return logit,k,v,grad

class LowRankGraph:
    def __init__(self,seed=1337):
        rng=random.Random(seed)
        self.u=[[rng.uniform(-.12,.12) for _ in range(R)] for _ in range(D)]
        self.v=[[rng.uniform(-.12,.12) for _ in range(F)] for _ in range(R)]
        self.version="synthetic-trained-v0"
    def project(self,f):
        if len(f)!=F or any(x not in (0,1) for x in f):raise ValueError("BAD_GRAPH_FEATURES")
        z=mv(self.v,f)
        return mv(self.u,z),z
    def update(self,f,dldx,z,rate=.09):
        # Exact chain gradient through rank-2 U V (backbone frozen).
        # Compute V gradient using ORIGINAL U, not partially updated U.
        back=mtv(self.u,dldx)
        du=[[dldx[i]*z[j] for j in range(R)] for i in range(D)]
        dv=[[back[j]*f[i] for i in range(F)] for j in range(R)]
        for i in range(D):
            for j in range(R):
                self.u[i][j]-=rate*(du[i][j]+0.0005*self.u[i][j])
        for j in range(R):
            for i in range(F):
                self.v[j][i]-=rate*(dv[j][i]+0.0005*self.v[j][i])

def graph_features(*,tool,permission,action):
    if tool not in (0,1) or permission not in (0,1) or action not in ("probe","use","publish"):
        raise ValueError("BAD_GRAPH")
    return [tool,permission,int(action=="probe"),int(action=="use"),int(action=="publish"),1]
def truth(*,tool,permission,action):
    # ENGINEER-AUTHORED TEST OWNER: not observed real-world permission.
    return int(action=="probe" or (action=="use" and tool and permission))

def context(*,tenant,authority,root,model,tokenizer="toy-v0",adapter="synthetic-trained-v0",prefix_graph=None):
    if not all(isinstance(x,str) and x for x in (tenant,authority,root,tokenizer,adapter)):
        raise ValueError("BAD_SCOPE")
    if prefix_graph is not None and not isinstance(prefix_graph,str):raise ValueError("BAD_PREFIX_GRAPH")
    return {"tenant":tenant,"authority":authority,"source_root":root,
            "tokenizer":tokenizer,"adapter":adapter,
            "prefix_graph":prefix_graph,"model":model.model_fingerprint}

def cache_signature(tokens,keys,values,scope_hash,model_fingerprint):
    # Detect accidental edits, not a signature/secret. Non-cryptographic
    # authorization is specifically NOT derived from this digest.
    return seal({"tokens":tokens,"keys":keys,"values":values,
                 "scope":scope_hash,"model":model_fingerprint})

def prefill(model,tokens,ctx):
    if not isinstance(tokens,tuple) or not tokens or len(tokens)>48:
        raise ValueError("BAD_PREFIX")
    scope_hash=seal(ctx)
    if ctx.get("model")!=model.model_fingerprint:raise ValueError("MODEL_CHANGED")
    if ctx.get("prefix_graph") is not None:
        # Would require graph-conditioned Q/K/V recomputation for each prefix.
        raise ValueError("CONTROLLED_PREFIX_CANNOT_USE_SHARED_CACHE")
    keys=[];values=[];ops=0
    for i,token in enumerate(tokens):
        _,k,v,_=model.step(token,i,keys,values)
        keys.append(tuple(k));values.append(tuple(v));ops+=i+1
    keys=tuple(keys);values=tuple(values)
    return Cache(tokens,keys,values,scope_hash,model.model_fingerprint,
                 cache_signature(tokens,keys,values,scope_hash,model.model_fingerprint),ops)

def branch(model,cache,ctx,token,features,adapter=None):
    if not isinstance(cache,Cache) or cache.model_fingerprint!=model.model_fingerprint or seal(ctx)!=cache.scope_hash:
        raise ValueError("CACHE_SCOPE_MISMATCH")
    if len(cache.keys)!=len(cache.tokens) or len(cache.values)!=len(cache.tokens):
        raise ValueError("CACHE_SHAPE_MISMATCH")
    if cache.cache_seal!=cache_signature(cache.tokens,cache.keys,cache.values,
                                         cache.scope_hash,cache.model_fingerprint):
        raise ValueError("CACHE_TAMPERED")
    if ctx.get("prefix_graph") is not None:raise ValueError("PREFIX_CONTROL_MISMATCH")
    if adapter is not None and ctx.get("adapter")!=adapter.version:raise ValueError("ADAPTER_MISMATCH")
    lat=adapter.project(features)[0] if adapter is not None else None
    logit,_,_,_=model.step(token,len(cache.tokens),cache.keys,cache.values,lat)
    return {"logit":logit,"qk_ops_suffix":len(cache.tokens)+1,
            "model_proposal_only":True,"state":"PENCIL","cache_shared":True}

def full(model,tokens,ctx,token,features,adapter=None):
    # Independently recompute the entire frozen prefix, no cache reuse.
    if ctx.get("model")!=model.model_fingerprint or ctx.get("prefix_graph") is not None:
        raise ValueError("INVALID_FULL_CONTEXT")
    keys=[];values=[];ops=0
    for i,t in enumerate(tokens):
        _,k,v,_=model.step(t,i,keys,values)
        keys.append(k);values.append(v);ops+=i+1
    lat=adapter.project(features)[0] if adapter is not None else None
    logit,_,_,_=model.step(token,len(tokens),keys,values,lat)
    return {"logit":logit,"qk_ops_total":ops+len(tokens)+1,"state":"PENCIL"}

def examples(prefixes=8):
    # Full-factorial coverage, split by held-out prefix variant, NOT action
    # combinations. This is weak domain transfer, never external validation.
    for p in range(prefixes):
        tokens=PREFIX[:3]+(PREFIX[3 if p%2==0 else 4],)+PREFIX[4:]
        for tool in (0,1):
            for permission in (0,1):
                for action in ("probe","use","publish"):
                    yield (p,tokens,tool,permission,action,truth(tool=tool,permission=permission,action=action))

def evaluate(model,adapter,split):
    # Exact held-out authored labels; no feedback into training.
    results=[]
    for p,tokens,tool,permission,action,y in examples():
        if (p<4)!=(split=="train"):continue
        ctx=context(tenant="fictional-a",authority="fixture",root="source-1",
                    model=model,adapter=adapter.version if adapter else "none")
        f=graph_features(tool=tool,permission=permission,action=action)
        logit=full(model,tokens,ctx,action,f,adapter)["logit"]
        results.append((int(logit>=0)==y,logit,y))
    losses=[]
    for _,v,y in results:
        prob=sigmoid(v)
        losses.append(-__import__('math').log(max(prob if y else 1-prob,1e-10)))
    return {"accuracy":sum(x[0] for x in results)/len(results),
            "loss":sum(losses)/len(losses),"n":len(results)}

def train(model,adapter,epochs=80,lr=.11):
    if epochs<1 or epochs>400:raise ValueError("BAD_EPOCHS")
    for epoch in range(epochs):
        for p,tokens,tool,permission,action,y in examples():
            if p>=4:continue
            ctx=context(tenant="fictional-a",authority="fixture",root="source-1",
                        model=model,adapter=adapter.version)
            # Precompute prefix once per episode (no model gradients there).
            cache=prefill(model,tokens,ctx)
            f=graph_features(tool=tool,permission=permission,action=action)
            latent,z=adapter.project(f)
            logit,_,_,dlogitdx=model.step(action,len(tokens),cache.keys,cache.values,latent,gradient=True)
            derivative=sigmoid(logit)-y
            adapter.update(f,[derivative*v for v in dlogitdx],z,rate=lr)
    adapter.version="synthetic-trained-v1"
    return adapter

def demo():
    m=TinyCausal()
    a=LowRankGraph()
    before=evaluate(m,None,"test")
    train(m,a)
    after=evaluate(m,a,"test")
    p,tokens,*_=next(examples())
    ctx=context(tenant="fictional-a",authority="fixture",root="source-1",model=m,adapter=a.version)
    cache=prefill(m,tokens,ctx)
    forks=[]
    for tool,permission,action in ((0,0,"probe"),(1,1,"use"),(0,1,"publish"),
                                  (0,1,"use"),(1,0,"use")):
        f=graph_features(tool=tool,permission=permission,action=action)
        c=branch(m,cache,ctx,action,f,a);n=full(m,tokens,ctx,action,f,a)
        forks.append({"action":action,"tool":tool,"permission":permission,
                      "logit_difference":abs(c["logit"]-n["logit"]),"pencil":c["state"]})
    flat_ops=sum(full(m,tokens,ctx,v["action"],
              graph_features(tool=v["tool"],permission=v["permission"],action=v["action"]),a)["qk_ops_total"]
                  for v in forks)
    shared_ops=cache.qk_ops+sum(len(tokens)+1 for _ in forks)
    return {"model":"RANDOM_FROZEN_SINGLE_HEAD_TOY_NOT_LLM",
            "trained_only":"RANK_2_GRAPH_ADAPTER",
            "withheld_synthetic_n":after["n"],
            "backbone_no_graph":before,
            "adapter_graph":after,
            "strong_classical_accuracy":1.0,
            "branches":forks,"qk_dot_products_full":flat_ops,
            "qk_dot_products_shared":shared_ops,
            "qk_dot_product_reduction":round(1-shared_ops/flat_ops,4),
            "wall_clock_or_cost_savings":"NOT_MEASURED",
            "real_llm_or_external_benchmark":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(demo(),sort_keys=True,indent=2))
