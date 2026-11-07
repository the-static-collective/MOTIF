"""RING-009: limited discovery search over entirely NEW induced relational rules.

The output program is a concrete executable **data AST** synthesized by
anti-unification; its cue strings and action anchors were NOT specified by
the engineer in the interpreter. A *small* finite search selects only
derivation settings on an author-created development split. The untouched
challenge module is NEVER imported from this file.

This is not unconstrained computational-primitive invention.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

import contrasts,induce
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cartridge-ring-008"))
import engine

SCHEMA="motif.ring009.frozen-contrastive-operator-invention.v1"


class BoundDecoder:
    def __init__(self,ast):
        self.ast=ast
    def parse(self,text):
        return induce.parse(self.ast,text)


def search(train,dev):
    contrasts.check(train,split="train")
    contrasts.check(dev,split="dev")
    if train["receipt_sha256"]==dev["receipt_sha256"]:
        raise induce.HOLD("Same source evidence is not a genuine selection split")
    reference=contrasts.flattened(dev)
    attempts=[]
    for min_support,max_tokens,max_gap,min_purity in itertools.product(
        (2,4,8),(1,2,3),(5,9,14),(0.9,1.0)
    ):
        ast=induce.construct(train,min_support=min_support,
                             max_cue_tokens=max_tokens,max_gap=max_gap,
                             min_purity=min_purity)
        score=engine.evaluate(BoundDecoder(ast),reference)
        m=score["metrics"]
        # Risk dominates: a single false-readonly clearance is disallowed
        # as a model-selection victory, even with more total predictions.
        rank=(m["unsafe_false_readonly"]==0,
              score["declared_objective"],
              m["exact_frames"],-m["wrong_decisive"],
              -ast["operator_instances_induced_from_examples"],
              ast["receipt_sha256"])
        attempts.append({"rank":rank,"ast":ast,"dev":score})
    winner=max(attempts,key=lambda x:x["rank"])
    no_pivot=BoundDecoder(winner["ast"])
    result={
        "schema":SCHEMA,
        "status":"ANTIUNIFICATION_GENERATED_NEW_RELATIONAL_OPERATOR_INSTANCES",
        "program":winner["ast"],
        "source_train_sha256":train["receipt_sha256"],
        "source_dev_sha256":dev["receipt_sha256"],
        "source_pair_count":len(train["pairs"]),
        "source_dev_pair_count":len(dev["pairs"]),
        "candidate_derivations_executed":len(attempts),
        "winner_dev_metrics":winner["dev"]["metrics"],
        "winner_dev_objective":winner["dev"]["declared_objective"],
        "invented_relational_rule_instances":winner["ast"][
            "operator_instances_induced_from_examples"],
        "new_python_semantic_primitives_invented":False,
        "new_distinct_relational_instances_automatically_derived":True,
        "all_semantic_labels_human_authored":True,
        "novel_test_module_imported_during_search":False,
        "heldout_labels_consulted":False,
        "original_program_code_modified":False,
        "external_action_executed":False,
        "authority":"NONE",
    }
    result["receipt_sha256"]=induce.digest(result)
    return result


def run():
    a=contrasts.generate("train",seed=2026110901,repeats=4)
    b=contrasts.generate("dev",seed=2026110902,repeats=4)
    return search(a,b)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    x=run()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":x["status"],"searched":x["candidate_derivations_executed"],
        "learned_operators":x["invented_relational_rule_instances"],
        "source_pairs":x["source_pair_count"],
        "dev":x["winner_dev_metrics"],
        "program_sha256":x["program"]["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
