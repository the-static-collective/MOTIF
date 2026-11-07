"""RING-008 finite program foundry: SEARCH creates a semantic algorithm AST.

Search space is a typed, limited algebra of feature operators, probabilistic
classifiers, role-binding layouts and calibrated abstention. Unlike a single
prewritten parser, the *combination chosen* is not specified in advance:
a deterministic evolutionary beam synthesizes candidate programs, tests each
on held-aside DEV examples, and keeps one frozen winner.

This is algorithm configuration synthesis within an explicitly human-designed
DSL; it is NOT invention of a novel universal NLP algorithm, nor open-ended
Python self-writing. In particular, dev is model-selection evidence, NOT a
valid generalization test. The NOVEL challenge is NOT imported here.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse
import json

import engine,world

SCHEMA="motif.ring008.frozen-generated-semantic-program.v1"
MAX_EVAL=160
BEAM=7
WAVES=4


def key(p):
    return engine.digest(p)


def build(ops,decoder,binding,margin,overlap):
    return engine.validate({
        "ops":sorted(ops),"decoder":decoder,"binding":binding,
        "margin":margin,"overlap":overlap})


def mutate(p):
    """Generate other ALGORITHMS as data by typed local graph rewriting."""
    result=[]
    ops=p["ops"]
    for op in engine.PROGRAM_OPS:
        if op not in ops and len(ops)<engine.MAX_OPS:
            result.append(build(ops+[op],p["decoder"],p["binding"],
                                p["margin"],p["overlap"]))
        if op in ops and len(ops)>1:
            result.append(build([x for x in ops if x!=op],p["decoder"],
                                p["binding"],p["margin"],p["overlap"]))
    for decoder in engine.DECODERS:
        if decoder!=p["decoder"]:
            result.append(build(ops,decoder,p["binding"],p["margin"],p["overlap"]))
    for binding in engine.BINDINGS:
        if binding!=p["binding"]:
            result.append(build(ops,p["decoder"],binding,p["margin"],p["overlap"]))
    ix=engine.MARGINS.index(p["margin"])
    for i in (ix-1,ix+1):
        if 0<=i<len(engine.MARGINS):
            result.append(build(ops,p["decoder"],p["binding"],
                                engine.MARGINS[i],p["overlap"]))
    ix=engine.OVERLAPS.index(p["overlap"])
    for i in (ix-1,ix+1):
        if 0<=i<len(engine.OVERLAPS):
            result.append(build(ops,p["decoder"],p["binding"],
                                p["margin"],engine.OVERLAPS[i]))
    return result


def crossover(a,b):
    """Two selected parents compose a previously unenumerated feature grammar."""
    ops=sorted(set(a["ops"])|set(b["ops"]))[:engine.MAX_OPS]
    return build(ops,a["decoder"],b["binding"],
                 min(a["margin"],b["margin"]),
                 max(a["overlap"],b["overlap"]))


def score_entry(entry):
    # Hard rank an unsafe false-readonly interpretation below ANY program
    # with zero such development mistakes; within the same risk tier reward
    # higher coverage, calibrated typed semantics and simpler code.
    m=entry["dev"]["metrics"]
    return (m["unsafe_false_readonly"]==0,
            entry["dev"]["declared_objective"],
            m["exact_frames"],
            -len(entry["spec"]["ops"]),
            -m["wrong_decisive"],
            entry["program_sha256"])


def synthesize(train,dev):
    world.check(train,expected="train")
    world.check(dev,expected="dev")
    if train["receipt_sha256"]==dev["receipt_sha256"]:
        raise engine.HOLD("Training and selection packet must be distinct")
    # Seeds are intentionally weak simple programs. Later combinations
    # emerge through mutation / recombination; inspect winners honestly.
    initial=[
        build([op],decoder,binding,0.04,2)
        for op in ("word","bigram","char3","edge")
        for decoder,binding in (("bayes","factorized"),
                                ("centroid","joint"))
    ]
    pool={}
    lineage={}
    visited=0
    discovered=[]
    def consider(spec,parents,operator):
        nonlocal visited
        sid=key(spec)
        if sid in pool or visited>=MAX_EVAL:
            return
        model=engine.train(train,spec)
        observed=engine.evaluate(model,dev["rows"])
        entry={
            "spec":spec,
            "program_sha256":sid,
            "dev":observed,
            "parents":list(parents),
            "generation_operator":operator,
            "training_source_sha256":train["receipt_sha256"],
        }
        pool[sid]=entry
        lineage[sid]={"parents":list(parents),"operator":operator}
        visited+=1
    for spec in initial:
        consider(spec,[],"INITIAL_AUDITED_ATOM")
    seed_ids=set(pool)
    frontier=sorted(pool.values(),key=score_entry,reverse=True)[:BEAM]
    history=[]
    for wave in range(WAVES):
        if visited>=MAX_EVAL:break
        candidates=[]
        for parent in frontier:
            for candidate in mutate(parent["spec"]):
                candidates.append((candidate,[parent["program_sha256"]],
                                   "TYPED_ALGEBRA_REWRITE"))
        for i in range(len(frontier)):
            for j in range(i+1,len(frontier)):
                candidates.append((crossover(frontier[i]["spec"],
                                              frontier[j]["spec"]),
                                   [frontier[i]["program_sha256"],
                                    frontier[j]["program_sha256"]],
                                   "COMPOSITIONAL_PROGRAM_CROSSOVER"))
        # Generator order is stable; cap prevents unlimited search costs.
        for spec,parents,mutation in candidates:
            if visited>=MAX_EVAL:break
            consider(spec,parents,mutation)
        frontier=sorted(pool.values(),key=score_entry,reverse=True)[:BEAM]
        leader=frontier[0]
        history.append({
            "wave":wave,
            "programs_executed":visited,
            "leader_program_sha256":leader["program_sha256"],
            "leader_score":leader["dev"]["declared_objective"],
            "leader_unsafe_false_readonly":leader["dev"]["metrics"][
                "unsafe_false_readonly"],
        })
    winners=sorted(pool.values(),key=score_entry,reverse=True)
    champion=winners[0]
    root=max((pool[x] for x in seed_ids),key=score_entry)
    winner_id=champion["program_sha256"]
    report={
        "schema":SCHEMA,
        "status":"FINITE_EXECUTABLE_PROGRAM_SEARCH_COMPLETED",
        "source_train_sha256":train["receipt_sha256"],
        "source_dev_sha256":dev["receipt_sha256"],
        "candidate_programs_tried":visited,
        "seed_program_count":len(seed_ids),
        "program_search_waves":history,
        "found_beyond_seed_set":winner_id not in seed_ids,
        "selected_program":champion["spec"],
        "selected_program_sha256":winner_id,
        "selected_program_lineage":lineage[winner_id],
        "selected_dev_metrics":champion["dev"]["metrics"],
        "selected_declared_dev_objective":champion["dev"]["declared_objective"],
        "strongest_atomic_seed":root["spec"],
        "strongest_atomic_seed_dev_metrics":root["dev"]["metrics"],
        "strongest_atomic_seed_objective":root["dev"]["declared_objective"],
        "program_is_executable_with_fixed_audited_operators":True,
        "search_was_not_able_to_create_new_python_operators":True,
        "all_language_meaning_labels_human_authored":True,
        "heldout_challenge_module_imported":False,
        "test_outcomes_consulted_during_search":False,
        "tool_execution_authority":"NONE",
        "external_action_executed":False,
    }
    report["receipt_sha256"]=engine.digest(report)
    return report


def run():
    train=world.generate("train",seed=2026110801,rounds=5)
    dev=world.generate("dev",seed=2026110802,rounds=5)
    return synthesize(train,dev)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out")
    args=p.parse_args()
    artifact=run()
    data=json.dumps(artifact,sort_keys=True,indent=2)+"\n"
    if args.out:
        from pathlib import Path
        x=Path(args.out)
        x.parent.mkdir(parents=True,exist_ok=True)
        x.write_text(data)
    print(json.dumps({
        "status":artifact["status"],
        "evaluated":artifact["candidate_programs_tried"],
        "selected":artifact["selected_program"],
        "selected_dev":artifact["selected_dev_metrics"],
        "beyond_seeds":artifact["found_beyond_seed_set"],
        "receipt":artifact["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
