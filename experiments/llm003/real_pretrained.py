"""LLM-003 actual public pretrained weights: source-safe graph KV forks & errors.

Only PUBLIC invented binary fixtures. Actual pretrained SmolLM2-135M-Instruct
weights downloaded ephemerally by CI. No secrets, no private MEMENTO, no user
queries, no external actions and no claims that generated guesses are facts.
Runs on CPU in bounded fp32 inference mode. The adapter is an untrained,
fixed rank-two graph projection: demonstrates compatibility, NOT new ability.
"""
from __future__ import annotations
import copy, json, os, sys, time, hashlib, random
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0,str(Path(__file__).resolve().parent))
from error_dividend import Owner,DEV,HELDOUT,INPUTS,seeded,choose,initial_posterior

MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
REVISION="ee72e5415c002e8fc0566a191a07c0b2b708875a"
PROMPT_PREFIX="You are exploring a fictional decision system. Read evidence carefully. All proposals are hypothetical. Never claim a real action or authorization. Task: choose the next possible research move. Known source facts:\n"

def load():
    torch.manual_seed(20261112)
    torch.set_num_threads(2)
    start=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=REVISION,trust_remote_code=False,
        torch_dtype=torch.float32,attn_implementation="eager")
    model.eval().cpu()
    return model,tokenizer,time.perf_counter()-start

def graph_delta(dim,features,scale=.06):
    torch.manual_seed(11042026)
    U=torch.randn(dim,2,dtype=torch.float32)/dim**.5
    V=torch.randn(2,len(features),dtype=torch.float32)/len(features)**.5
    vec=U@(V@torch.tensor(features,dtype=torch.float32))
    return vec/(vec.norm()+1e-12)*scale

def safe_text(tokenizer,token_id):
    return tokenizer.decode([int(token_id)],clean_up_tokenization_spaces=False)[:40]

@torch.inference_mode()
def check_cache(model,tokenizer):
    prefix=(PROMPT_PREFIX+"The owner has an unverified diagram and a stated goal. "
            "Materials, locations and approvals are unknown. No physical construction is allowed.\n")
    pids=tokenizer.encode(prefix,add_special_tokens=True,return_tensors="pt")
    assert 4<pids.shape[1]<160
    embed=model.get_input_embeddings()
    branches=(
       ("measure", " Suggest a possible measurement.",(1,0,1,0,0,1)),
       ("hypothesis", " Propose a hypothetical alternative.",(0,1,0,1,0,1)),
       ("shuffled_features", " Suggest a possible measurement.",(0,0,1,1,0,1)),
       ("zero_control", " Suggest a possible measurement.",(0,0,0,0,0,0)),
    )
    prefix_embeddings=embed(pids).detach().clone()
    tp=time.perf_counter()
    po=model(input_ids=pids,use_cache=True,return_dict=True)
    prefix_time=time.perf_counter()-tp
    immutable_prefix=po.past_key_values
    results=[]
    full_total=0.;suffix_total=0.
    for name,suffix,features in branches:
        ids=tokenizer.encode(suffix,add_special_tokens=False,return_tensors="pt")
        assert 1<=ids.shape[1]<=24
        e=embed(ids).detach().clone()
        # Only the first suffix token is conditioned, the cached prefix never.
        if any(features):
            injection=graph_delta(e.shape[-1],features)
            e[0,0,:]+=injection
        full_embeddings=torch.cat([prefix_embeddings,e],dim=1)
        attn_mask=torch.ones((1,pids.shape[1]+ids.shape[1]),dtype=torch.long)
        t0=time.perf_counter()
        full=model(inputs_embeds=full_embeddings,attention_mask=attn_mask,
                   use_cache=False,return_dict=True).logits.detach()
        full_time=time.perf_counter()-t0;full_total+=full_time
        # Fork copies prefix cache, so no branch can mutate shared original.
        private_kv=copy.deepcopy(immutable_prefix)
        t1=time.perf_counter()
        cached=model(inputs_embeds=e,attention_mask=attn_mask,
                     past_key_values=private_kv,use_cache=True,
                     return_dict=True).logits.detach()
        cached_time=time.perf_counter()-t1;suffix_total+=cached_time
        diff=(full[:,-1,:]-cached[:,-1,:]).abs().max().item()
        results.append({"name":name,"source_graph_features":list(features),
                        "suffix_tokens":int(ids.shape[1]),
                        "max_abs_final_vocab_logits_delta":diff,
                        "top_token":safe_text(tokenizer,cached[0,-1,:].argmax()),
                        "full_forward_seconds":round(full_time,5),
                        "cached_suffix_seconds":round(cached_time,5),
                        "pencil_only":True})
        if diff>=1e-3:raise AssertionError("REAL_PRETRAINED_CACHE_PARITY_FAILURE")
    return {"model":MODEL,"pinned_revision":REVISION,"prefix_tokens":int(pids.shape[1]),
            "prefix_prefill_seconds":round(prefix_time,5),
            "full_independent_seconds":round(full_total,5),
            "one_prefix_plus_forks_seconds":round(prefix_time+suffix_total,5),
            "wall_clock_may_be_noisy":True,"exact_model_output_not_ground_truth":True,
            "suffix_graph_adaptor":"FIXED_UNTRAINED_RANK_TWO","forks":results,
            "all_forks_parity":True,"pretrained_weights_loaded":True}

def sample_prompt(observations,target):
    samples="\n".join(f"A={x[0]}, B={x[1]}, C={x[2]} => {y}"
                    for x,y in observations)
    return ("A fictional machine receives three binary inputs A, B, C. "
            "Its output is either 0 or 1. Use only the verified examples below. "
            "If the rule is uncertain, take a best guess. "
            "Reply with only one digit: 0 or 1.\n"
            "Verified examples:\n"+samples+"\n"
            f"Question: A={target[0]}, B={target[1]}, C={target[2]} => ")

@torch.inference_mode()
def guess(model,tokenizer,observations,target):
    ids=tokenizer.encode(sample_prompt(observations,target),
                         add_special_tokens=True,return_tensors="pt")
    out=model(input_ids=ids,use_cache=False,return_dict=True).logits[0,-1,:]
    zero=tokenizer.encode("0",add_special_tokens=False)
    one=tokenizer.encode("1",add_special_tokens=False)
    if len(zero)!=1 or len(one)!=1:
        raise ValueError("MODEL_DIGITS_ARE_NOT_SINGLE_TOKEN")
    logits=[float(out[zero[0]]),float(out[one[0]])]
    return (int(logits[1]>=logits[0]),len(ids[0]))

def test_model_revision(model,tokenizer):
    # Numeric pretrained behavior is model-specific. The model ID and
    # revision are pinned, but checkpoint bytes are downloaded by HF Hub.
    if not hasattr(model,"get_input_embeddings") or len(tokenizer)<100:
        raise RuntimeError("INVALID_REAL_MODEL")
    return {"architecture":model.__class__.__name__,
            "parameters":sum(p.numel() for p in model.parameters()),
            "vocab_size":len(tokenizer),
            "dtype":str(next(model.parameters()).dtype)}

@torch.inference_mode()
def error_feedback_trial(model,tokenizer,count=8):
    # The model is not given the hidden owner program. Two strategies receive
    # one independently verified NEW example each, with equal probe count.
    # A wrong model answer is never published. Negative examples are PENCIL.
    rows=[]
    for seed in HELDOUT[:count]:
        owner=Owner(seed,"truthful")
        baseline=[(owner.start_x,owner.initial["value"])]
        remaining=tuple(x for x in INPUTS if x!=owner.start_x)
        target=remaining[seeded(seed,"real-target").randrange(len(remaining))]
        possible=tuple(x for x in remaining if x!=target)
        prior,base_tokens=guess(model,tokenizer,baseline,target)
        policy_prior=initial_posterior(owner)
        challenge=choose("challenge_favorite",policy_prior,possible,seed,0)
        random_query=choose("uniform_random",policy_prior,possible,seed,0)
        y_true=owner.truth(target)
        each={"seed":seed,"target":list(target),
              "baseline_correct":prior==y_true,"baseline_prediction":prior,
              "base_prompt_tokens":base_tokens}
        for label,query in (("challenge",challenge),("random",random_query)):
            receipt_y=owner.truth(query)
            pred,tokens=guess(model,tokenizer,baseline+[(query,receipt_y)],target)
            each[label]={"probe":list(query),"provisional_prediction":pred,
                "correct":pred==y_true,
                "corrected_wrong":prior!=y_true and pred==y_true,
                "degraded_correct":prior==y_true and pred!=y_true,
                "verified_example_from_independent_owner":True,
                "prompt_tokens":tokens}
        rows.append(each)
    return {"cases":len(rows),"same_one_probe_budget_each":True,
            "baseline_correct":sum(x["baseline_correct"] for x in rows),
            "challenge_correct":sum(x["challenge"]["correct"] for x in rows),
            "random_correct":sum(x["random"]["correct"] for x in rows),
            "challenge_wrong_to_right":sum(x["challenge"]["corrected_wrong"] for x in rows),
            "challenge_right_to_wrong":sum(x["challenge"]["degraded_correct"] for x in rows),
            "random_wrong_to_right":sum(x["random"]["corrected_wrong"] for x in rows),
            "random_right_to_wrong":sum(x["random"]["degraded_correct"] for x in rows),
            "interpretation":"TINY_REAL_MODEL_SOURCE_GROUNDED_SAMPLE_NOT_EXTERNAL_GENERALIZATION",
            "rows":rows}

def main():
    start=time.perf_counter()
    try:
        model,tok,load_time=load()
        meta=test_model_revision(model,tok)
        cache=check_cache(model,tok)
        feedback=error_feedback_trial(model,tok)
        report={"status":"REAL_PRETRAINED_MODEL_EXECUTED","model_info":meta,
                "model_load_seconds_including_download":round(load_time,3),
                "kv":cache,"feedback":feedback,
                "elapsed_including_model_load_seconds":round(time.perf_counter()-start,3),
                "scope":"PUBLIC_AUTHOR_SYNTHETIC_INPUTS_ONLY","external_actions":False,
                "trained_adapter":False,"scientific_breakthrough":False}
        print("LLM003_JSON_BEGIN")
        print(json.dumps(report,sort_keys=True))
        print("LLM003_JSON_END")
    except Exception as e:
        # CI must FAIL; never silently substitute fake toy model.
        print("LLM003_REAL_MODEL_HOLD",type(e).__name__,str(e)[:500],file=sys.stderr)
        raise

if __name__=="__main__":
    main()
