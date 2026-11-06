"""LEGIT-008 bounded meta-policy *synthesis* using training packets only.

The generator searches a small, PREDECLARED family of reasoning procedures:
always solve one step, always solve two steps, or invoke the deeper
solver only for near-ambiguous posterior beliefs / copied-source profiles.

Training uses source-conditional *expected* loss, never latent world truth,
future audit results or test-case outcomes. A separate untouched heldout
population evaluates selected recipe. This is classical strategy selection,
not mathematical transcendence, autonomous theorem discovery, or proof of
real-world generalization.
"""
from __future__ import annotations

from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit007"))
from provenance import posterior
from planner import plan

GRAMMAR=(
    ("ALWAYS_ONE",0.0),
    ("ALWAYS_TWO",0.0),
) + tuple(("POSTERIOR_MARGIN",t) for t in
          (0.02,0.05,0.10,0.15,0.20,0.25,0.35,0.50)) + tuple(
          ("COPY_FRACTION",t) for t in (0.0,.20,.40,.60,.80))
COMPUTE_PRICE_PER_STATE=.0006
TRAIN_SAMPLES=160

def select_depth(recipe,p,copy_fraction):
    if recipe[0]=="ALWAYS_ONE":
        return 1
    if recipe[0]=="ALWAYS_TWO":
        return 2
    if recipe[0]=="POSTERIOR_MARGIN":
        return 2 if abs(p-.5)<=recipe[1] else 1
    if recipe[0]=="COPY_FRACTION":
        return 2 if copy_fraction>recipe[1] else 1
    raise ValueError("Unknown candidate strategy")

def features(packet):
    fitted=posterior(packet)
    distinct=len(fitted["origin_signature"])
    ratio=(len(packet["nodes"])-distinct)/len(packet["nodes"])
    return fitted["posterior"],ratio

def synthesize(training_packets):
    if not isinstance(training_packets,list) or len(training_packets)!=TRAIN_SAMPLES:
        raise ValueError("Only registered, separate public training packets")
    if any(set(p)!={"schema","id","scope","nodes","calibration","audits"}
           for p in training_packets):
        raise ValueError("Raw source data may not contain hidden truth")
    # Freeze all relevant exact policy consequences, without touching truth.
    prepared=[]
    for packet in training_packets:
        p,echoes=features(packet)
        results={depth:plan(p,packet["audits"],depth) for depth in (1,2)}
        prepared.append((p,echoes,results))
    candidates=[]
    for recipe in GRAMMAR:
        expected=0.
        states=0
        deeper=0
        for p,echoes,results in prepared:
            depth=select_depth(recipe,p,echoes)
            score=results[depth]
            expected+=score["tree"]["expected_risk"]
            states+=score["states_visited"]
            deeper+=int(depth==2)
        objective=(expected+COMPUTE_PRICE_PER_STATE*states)/len(prepared)
        candidates.append({"kind":recipe[0],"threshold":recipe[1],
                           "expected_risk_mean":expected/len(prepared),
                           "states_mean":states/len(prepared),
                           "two_step_fraction":deeper/len(prepared),
                           "objective":objective})
    best=min(candidates,key=lambda r:(r["objective"],r["kind"],r["threshold"]))
    return {"schema":"motif.strategy-composition-proposal.v1",
            "status":"HOLD_PENDING_INDEPENDENT_REVIEW",
            "method":"BOUNDED_CLASSICAL_STRATEGY_ENUMERATION",
            "train_count":len(prepared),"recipe":{
                "kind":best["kind"],"threshold":best["threshold"]},
            "training_objective":best["objective"],
            "training_expected_risk":best["expected_risk_mean"],
            "training_states_mean":best["states_mean"],
            "candidate_count":len(candidates),
            "compute_price_per_state":COMPUTE_PRICE_PER_STATE,
            "used_hidden_outcomes":False,
            "autonomously_invented_new_mathematics":False,
            "externally_authorized":False,
            "real_world_authority":False}

def selected_plan(packet,artifact):
    if (artifact.get("schema")!="motif.strategy-composition-proposal.v1"
            or artifact.get("status")!="HOLD_PENDING_INDEPENDENT_REVIEW"):
        raise ValueError("Untrusted strategy recipe")
    row=artifact["recipe"]
    recipe=(row["kind"],row["threshold"])
    if recipe not in GRAMMAR:
        raise ValueError("Unrecognized strategy recipe")
    p,echoes=features(packet)
    depth=select_depth(recipe,p,echoes)
    choice=plan(p,packet["audits"],depth)
    return {"depth":depth,"plan":choice,"method":"LEARNED_FIXED_GRAMMAR_POLICY",
            "real_world_authority":False}
