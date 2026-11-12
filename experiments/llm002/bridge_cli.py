"""LLM-002 bridge: numeric model forks for a validated LLM-001 world packet.

Reads ONLY synthetic public fixture JSON over stdin. Reports scores, not
source-cited hypotheses or task solutions. Does not read MEMENTO, photos,
the filesystem, or call real providers. No external actions.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import (TinyCausal,LowRankGraph,context,prefill,branch,full,
                    graph_features,train,PREFIX,sigmoid)

TOKENS={"probe":"probe","simulate":"use"}
def run(payload):
    if not isinstance(payload,dict) or payload.get("schema")!="motif.llm002.weave.v0":
        raise ValueError("BAD_WEAVE")
    if payload.get("scope")!="PUBLIC_SYNTHETIC_FIXTURE" or not isinstance(payload.get("tenant"),str) or not payload["tenant"]:
        raise ValueError("BAD_SCOPE")
    if not isinstance(payload.get("root"),str) or len(payload["root"])!=64:
        raise ValueError("BAD_ROOT")
    branches=payload.get("branches")
    if not isinstance(branches,list) or not 1<=len(branches)<=6:
        raise ValueError("BAD_BRANCH_COUNT")
    if len({b.get("id") for b in branches if isinstance(b,dict)})!=len(branches):
        raise ValueError("DUPLICATE_BRANCHES")
    model=TinyCausal()
    adapter=train(model,LowRankGraph(),epochs=80)
    ctx=context(tenant=payload["tenant"],authority="public-synthetic-fixture",
                root=payload["root"],model=model,adapter=adapter.version)
    cache=prefill(model,PREFIX,ctx)
    rows=[]
    for b in branches:
        if not isinstance(b,dict) or b.get("kind") not in TOKENS or not isinstance(b.get("id"),str):
            raise ValueError("BAD_BRANCH")
        token=TOKENS[b["kind"]]
        if b.get("tool") not in (0,1) or b.get("permission") not in (0,1):
            raise ValueError("UNVERIFIED_FEATURES")
        f=graph_features(tool=b["tool"],permission=b["permission"],action=token)
        cached=branch(model,cache,ctx,token,f,adapter,expected_prefix=PREFIX)
        exact=full(model,PREFIX,ctx,token,f,adapter)
        if abs(cached["logit"]-exact["logit"])>1e-11:
            raise RuntimeError("CACHE_NUMERIC_DIVERGENCE")
        rows.append({"id":b["id"],"kind":b["kind"],
                     "latent_logit":round(cached["logit"],8),
                     "illustrative_probability":round(sigmoid(cached["logit"]),8),
                     "position":len(PREFIX),"status":"PENCIL_SCORE_ONLY",
                     "cached_vs_full_delta":abs(cached["logit"]-exact["logit"])})
    flat=sum(full(model,PREFIX,ctx,TOKENS[b["kind"]],
                graph_features(tool=b["tool"],permission=b["permission"],
                               action=TOKENS[b["kind"]]),adapter)["qk_ops_total"]
             for b in branches)
    share=cache.qk_ops+len(branches)*(len(PREFIX)+1)
    return {"schema":"motif.llm002.weave-result.v0","world_id":payload.get("world_id"),
            "source_root":payload["root"],"forks":rows,
            "attention_qk_full":flat,"attention_qk_shared":share,
            "verified_equal":True,
            "model_kind":"SYNTHETIC_RANDOM_ATTENTION_WITH_RANK2_TRAINED_ADAPTER",
            "real_model":False,"external_actions":False,"decision_authority":"NONE"}
if __name__=="__main__":
    payload=json.load(sys.stdin)
    print(json.dumps(run(payload),sort_keys=True))
