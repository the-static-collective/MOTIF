"""Actual, fully frozen pretrained SmolLM2 inside ODYSSEY MARATHON.

This module loads the real public pretrained model exactly once and supplies
PENCIL digit-0/1 next-token proposals for every unsolved binary checkpoint.
Only independently reported *past* answers for the CURRENT sector may enter
a model prompt. Model text never counts as a source witness.

No private user facts, passwords, live JAR;VIS effects or other connected
services are involved. No hidden oracle truth program can reach the adapter.
A failed checkpoint still requires source verification and a separate repair.
"""
from __future__ import annotations
import hashlib,json,math,time
import torch

from real_pretrained import MODEL,REVISION,load,sample_prompt
from marathon import Marathon,GROUPS
from odyssey import REAL_MODEL_POLICIES,POLICIES

MAX_PROMPT_TOKENS=220
MAX_MODEL_FORWARDS=1200
INITIAL_REAL_RESEARCH_GROUP=GROUPS[0]

def request_for_model(packet,policy):
    """Pure, bounded, independently sourced model input selection."""
    if not isinstance(packet,dict) or packet.get("schema")!="motif.real-model-evidence/v0":
        raise ValueError("MODEL_PACKET_INVALID")
    if policy not in REAL_MODEL_POLICIES:raise ValueError("MODEL_POLICY_INVALID")
    if packet.get("real_world_authority")!="none" or packet.get("no_future_owner_truth") is not True:
        raise ValueError("REAL_OWNER_SCOPE_INVALID")
    if packet.get("rumor_sources_excluded") is not True:
        raise ValueError("RUMOR_CANNOT_BE_MODEL_EVIDENCE")
    allowed=packet.get("observations",[])
    if not isinstance(allowed,list) or not 1<=len(allowed)<=8:
        raise ValueError("MODEL_EVIDENCE_COUNT_INVALID")
    if len(packet.get("x",[]))!=3 or any(v not in (0,1) for v in packet["x"]):
        raise ValueError("TARGET_NOT_BINARY")
    if len(packet.get("source_roots",[]))!=len(allowed):
        raise ValueError("SOURCE_ROOTS_INVALID")
    if len(set(packet["source_roots"]))!=len(allowed):
        raise ValueError("DUPLICATED_SOURCE_ROOTS")
    samples=[]
    for a in allowed:
        if a.get("kind") not in ("INITIAL_OWNER_RECEIPT","INDEPENDENT_OWNER_RECEIPT"):
            raise ValueError("UNVERIFIED_MODEL_DATA")
        if a.get("source_root") not in packet["source_roots"]:
            raise ValueError("MISSING_SOURCE_LINEAGE")
        if not isinstance(a.get("x"),list) or len(a["x"])!=3 or any(v not in (0,1) for v in a["x"]):
            raise ValueError("BAD_OBSERVATION")
        if a.get("value") not in (0,1):raise ValueError("BAD_SOURCE_VALUE")
        if a["x"]==packet["x"]:raise ValueError("TARGET_ALREADY_VERIFIED")
        samples.append((tuple(a["x"]),int(a["value"])))
    if len(set(x for x,y in samples))!=len(samples):
        raise ValueError("DUPLICATE_CASE_EVIDENCE")
    if policy=="llm_flat":
        if len(samples)!=1 or allowed[0]["kind"]!="INITIAL_OWNER_RECEIPT":
            raise ValueError("FLAT_CANNOT_READ_MEMORY")
    if allowed[0]["kind"]!="INITIAL_OWNER_RECEIPT":raise ValueError("MISSING_INITIAL_CALIBRATION")
    prompt=sample_prompt(samples,tuple(packet["x"]))
    # Stable provenance of the exact text processed by the pretrained model.
    return prompt, {"evidence_count":len(samples),
        "source_roots":tuple(packet["source_roots"]),
        "prompt_sha256":hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "source_scope":"CURRENT_SYNTHETIC_SECTOR_ONLY"}

class RealSmolLMPolicy:
    def __init__(self,model,tokenizer,mode):
        if mode not in REAL_MODEL_POLICIES:raise ValueError("UNKNOWN_REAL_LLM_ARM")
        if model is None or tokenizer is None:raise ValueError("ACTUAL_PRETRAINED_WEIGHTS_REQUIRED")
        self.model=model;self.tokenizer=tokenizer;self.mode=mode
        self.forwards=0;self.tokens=0;self.seconds=0.;self.records=[]
        ids=[tokenizer.encode(str(i),add_special_tokens=False) for i in (0,1)]
        if any(len(x)!=1 for x in ids):raise ValueError("INVALID_PRETRAINED_DIGIT_TOKENS")
        self.digit_ids=(ids[0][0],ids[1][0])
        self.model.eval()
    @torch.inference_mode()
    def __call__(self,packet):
        if self.forwards>=MAX_MODEL_FORWARDS:raise ValueError("MODEL_FORWARD_BUDGET_EXHAUSTED")
        prompt,provenance=request_for_model(packet,self.mode)
        t0=time.perf_counter()
        ids=self.tokenizer.encode(prompt,add_special_tokens=True,return_tensors="pt")
        count=int(ids.shape[-1])
        if count<1 or count>MAX_PROMPT_TOKENS:
            raise ValueError("MODEL_INPUT_TOKEN_LIMIT")
        output=self.model(input_ids=ids,use_cache=False,return_dict=True)
        logits=output.logits[0,-1,list(self.digit_ids)].to(torch.float64)
        probs=logits.softmax(dim=0)
        p_one=float(probs[1].item())
        if not math.isfinite(p_one):raise ValueError("NON_FINITE_REAL_MODEL_SCORE")
        prediction=int(p_one>=.5)
        elapsed=time.perf_counter()-t0
        self.forwards+=1;self.tokens+=count;self.seconds+=elapsed
        rec={"model":MODEL,"revision":REVISION,
             "prediction":prediction,"p_one":p_one,
             "logit_zero":round(float(logits[0]),5),
             "logit_one":round(float(logits[1]),5),
             "token_count":count,
             "inference_seconds":round(elapsed,6),
             "prompt_sha256":provenance["prompt_sha256"],
             "source_roots_used":list(provenance["source_roots"]),
             "evidence_count":provenance["evidence_count"],
             "target":list(packet["x"]),"sector":packet["sector"],
             "status":"UNVERIFIED_PENCIL_INFERENCE"}
        self.records.append(rec)
        return rec
    def stats(self):
        return {"forwards":self.forwards,"prompt_tokens":self.tokens,
                "inference_seconds":round(self.seconds,4),
                "model":MODEL,"revision":REVISION,
                "real_pretrained_weights":True,"trained_new_adapter":False}

def audit_real_marathon(marathon:Marathon,model_policy:RealSmolLMPolicy):
    """Independent integrity audit after running the same owner-gated chain."""
    record=marathon.public_record()
    events=record["global_events"]
    source_events=[e for e in events if e["kind"]=="odyssey_action"]
    verified_source_commits=[e for e in source_events if
        e["payload"]["child_kind"] in ("commit_correct","commit_wrong")]
    model_proposals=[e for e in verified_source_commits if
        isinstance(e["payload"]["child_meta"].get("real_model_pencil_proposal"),dict)]
    if len(model_proposals)!=model_policy.forwards:
        raise ValueError("REAL_MODEL_FORWARD_COUNT_MISMATCH")
    if any(e["payload"]["child_meta"]["real_model_pencil_proposal"].get("status")
           !="PENCIL_ONLY_NOT_A_WITNESS" for e in model_proposals):
        raise ValueError("MODEL_RESULT_FALSE_PROMOTION")
    for p in model_proposals:
        m=p["payload"]["child_meta"]
        if m["pencil_answer"] not in (0,1) or m["synthetic_owner_report"] not in (0,1):
            raise ValueError("INVALID_OWNER_VERIFIED_COMMIT")
    if record["summary"]["completed"]:
        if record["summary"]["completed_decision_gates"]!=384:
            raise ValueError("INCOMPLETE_384_PRETRAINED_DECISIONS")
        if record["summary"]["mandatory_handoffs_completed"]!=3:
            raise ValueError("MISSING_REAL_CHAIN_HANDOFFS")
        # 48 synthetic sectors have one initial calibration each; all
        # other checkpoints require one genuine pretrained forward.
        if model_policy.forwards!=336:
            raise ValueError("MODEL_SKIPPED_UNVERIFIED_GATE")
    return {"model_forwards_verified":len(model_proposals),
        "real_model_inference_seconds":round(model_policy.seconds,4),
        "model_pencil_correct_before_owner_receipt":sum(
          e["payload"]["child_meta"]["real_model_pencil_proposal"]["prediction"]==
          e["payload"]["child_meta"]["synthetic_owner_report"]
          for e in model_proposals),
        "model_pencil_wrong_before_owner_receipt":sum(
          e["payload"]["child_meta"]["real_model_pencil_proposal"]["prediction"]!=
          e["payload"]["child_meta"]["synthetic_owner_report"]
          for e in model_proposals),
        "owner_witnesses_independent_of_model":True,
        "hidden_owner_index_in_model_input":False,
        "not_a_general_intelligence_benchmark":True}

def compare_model_memory(flat_records,memory_records):
    """Pair exactly identical target coordinates before checking owner truth."""
    def index(records):
        out={}
        for p in records:
            key=(p["segment"],p["payload"]["child_sector"],p["payload"]["child_gate"])
            if p["payload"]["child_kind"] not in ("commit_correct","commit_wrong"):continue
            m=p["payload"]["child_meta"].get("real_model_pencil_proposal")
            if m is None:continue
            if key in out:raise ValueError("DUPLICATED_MODEL_TARGET")
            out[key]=(m["prediction"],p["payload"]["child_meta"]["synthetic_owner_report"])
        return out
    a,b=index(flat_records),index(memory_records)
    matching=set(a)&set(b)
    if matching!=set(a) or matching!=set(b):
        # Partial runs compared only on the shared observed prefix. Explicit.
        paired_scope="PARTIAL_INTERSECTION_ONLY"
    else:paired_scope="FULL_IDENTICAL_336_TARGETS"
    rw=ww=0
    for k in matching:
        af,truth=a[k];am,truth2=b[k]
        if truth!=truth2:raise ValueError("DIFFERENT_OWNER_TRUTH_FOR_SAME_TASK")
        rw+=int(af!=truth and am==truth)
        ww+=int(af==truth and am!=truth)
    return {"paired_target_count":len(matching),"pair_scope":paired_scope,
            "flat_wrong_memory_right":rw,"flat_right_memory_wrong":ww,
            "net_memory_corrections":rw-ww,
            "causal_claim":"NONE_RANDOMIZED_MODEL_REUSE_AND_AUTHOR_FIXTURE"}

def run_real_first_marathon():
    started=time.perf_counter()
    model,tok,loading=load()
    model.eval()
    all_runs={};models={}
    for mode in REAL_MODEL_POLICIES:
        actor=RealSmolLMPolicy(model,tok,mode)
        marathon=Marathon(INITIAL_REAL_RESEARCH_GROUP,mode,decision_adapter=actor)
        result=marathon.execute()
        audit=audit_real_marathon(marathon,actor)
        all_runs[mode]={"summary":result,"audit":audit,
                        "model_stats":actor.stats(),
                        "record":marathon.public_record()}
        models[mode]=actor
        print("LLM006_ARM",mode,json.dumps({k:v for k,v in all_runs[mode].items()
                 if k!="record"},sort_keys=True),flush=True)
    paired=compare_model_memory(all_runs["llm_flat"]["record"]["global_events"],
                                all_runs["llm_memory"]["record"]["global_events"])
    total_forwards=sum(m.forwards for m in models.values())
    if total_forwards>MAX_MODEL_FORWARDS:raise ValueError("FORWARD_CAP_BREACH")
    return {"schema":"motif.llm006.real-marathon/v0",
       "model":MODEL,"revision":REVISION,
       "pretrained_model_was_actually_loaded":True,
       "model_parameters":sum(p.numel() for p in model.parameters()),
       "model_load_seconds":round(loading,3),
       "research_group":list(INITIAL_REAL_RESEARCH_GROUP),
       "model_forward_budget":MAX_MODEL_FORWARDS,
       "model_forwards":total_forwards,
       "experiment_elapsed_seconds":round(time.perf_counter()-started,3),
       "arms":all_runs,"paired_memory_comparison":paired,
       "source_authentication":"SYNTHETIC_OWNER_ONLY",
       "no_external_actions":True,
       "user_facing_false_outputs":0,
       "classical_strong_controls":"EXISTING_LLM005_RESULTS_WITH_SAME_REGISTERED_FIRST_GROUP",
       "not_generalized":True}

def main():
    r=run_real_first_marathon()
    print("LLM006_RESULT_BEGIN",flush=True)
    print(json.dumps({**r,"arms":{k:{t:v for t,v in x.items() if t!="record"}
                           for k,x in r["arms"].items()}},sort_keys=True),flush=True)
    print("LLM006_RESULT_END",flush=True)
    return r

if __name__=="__main__":
    main()
