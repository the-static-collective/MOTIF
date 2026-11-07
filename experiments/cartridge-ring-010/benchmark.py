"""RING-010 post-freeze graph semantics falsifier with SAME-DATA classical control.

The sealed language challenge module is imported only by evaluate_frozen,
after training-source identity and exact graph-rule re-induction are verified.
An ordinary factorized multinomial Bayes model is trained on the SAME
train data (same separately provided event context), to prevent artificial
claims that graph-rule invention necessarily exceeds classical methods.

All outputs are untrusted typed hypotheses, with no side effects.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import argparse

import world,induce,search

SCHEMA="motif.ring010.postfreeze-compositional-graph-trial.v1"

class HOLD(ValueError):
    pass


class GraphBayes:
    def __init__(self,examples,*,mode="word"):
        if mode not in ("word","bigram"):
            raise HOLD("Unsupported classical graph model")
        self.mode=mode
        self.models={}
        vocab=set()
        for ex in examples:
            vocab.update(self.features(ex).keys())
        self.vocab=len(vocab)+1
        for rel in world.RELATIONS:
            counts=Counter()
            freq=defaultdict(Counter)
            total=Counter()
            for ex in examples:
                category=induce.graphmap(ex["semantic_graph"])[rel]
                feats=self.features(ex)
                counts[category]+=1
                freq[category].update(feats)
                total[category]+=sum(feats.values())
            self.models[rel]=(counts,freq,total)

    def features(self,ex):
        tokens=induce.abstract(ex["text"],ex["observed_event"])
        rows=["w:"+x for x in tokens]
        if self.mode=="bigram":
            rows.extend("b:"+a+"|"+b for a,b in zip(tokens,tokens[1:]))
        return Counter(rows)

    def parse(self,utterance,observed):
        ex={"text":utterance,"observed_event":observed}
        try:
            feature=self.features(ex)
        except induce.HOLD:
            return {"status":"HOLD","semantic_graph":None,
                    "source_text_sha256":sha256(utterance.encode()).hexdigest()}
        assigned={}
        for rel,(classes,counts,total) in self.models.items():
            scores={}
            for val,n in classes.items():
                numerator=math.log(n+1)
                denominator=total[val]+self.vocab
                scores[val]=numerator+sum(k*math.log((counts[val][word]+1)/denominator)
                                            for word,k in feature.items())
            assigned[rel]=max(scores,key=lambda v:(scores[v],v))
        return {
            "status":"NONAUTHORITATIVE_CLASSICAL_FRAME",
            "semantic_graph":world.graph(tuple(assigned[r] for r in world.RELATIONS)),
            "source_text_sha256":sha256(utterance.encode()).hexdigest(),
            "external_action_authority":"NONE",
        }


class AlwaysHold:
    def parse(self,utterance,observed):
        return {"status":"HOLD","semantic_graph":None,
                "source_text_sha256":sha256(utterance.encode()).hexdigest()}


class RelationalDecoder:
    def __init__(self,program):
        self.program=program
    def parse(self,utterance,observed):
        return induce.parse(self.program,utterance,observed)


def evaluate(model,examples):
    totals={
        "cases":0,"exact_semantic_graph":0,"wrong_decisive":0,
        "abstained":0,"false_directive_clearance":0,
        "missed_directive":0,"wrong_polarity":0,"wrong_scope":0,
    }
    witnesses=[]
    for case in examples:
        response=model.parse(case["text"],case["observed_event"])
        actual=induce.graphmap(case["semantic_graph"])
        prediction=response["semantic_graph"]
        vals=None if prediction is None else induce.graphmap(prediction)
        right=vals==actual
        danger=(vals is not None and vals["FORCE"]=="DIRECTIVE"
                and actual["FORCE"]!="DIRECTIVE")
        totals["cases"]+=1
        totals["exact_semantic_graph"]+=int(right)
        totals["wrong_decisive"]+=int(vals is not None and not right)
        totals["abstained"]+=int(vals is None)
        totals["false_directive_clearance"]+=int(danger)
        if vals is not None:
            totals["missed_directive"]+=int(vals["FORCE"]!="DIRECTIVE" and
                                            actual["FORCE"]=="DIRECTIVE")
            totals["wrong_polarity"]+=int(vals["POLARITY"]!=actual["POLARITY"])
            totals["wrong_scope"]+=int(vals["SCOPE"]!=actual["SCOPE"])
        witnesses.append({
            "source_text_sha256":response["source_text_sha256"],
            "expected_semantics":actual,
            "predicted_semantics":vals,
            "exact":bool(right),
            "false_directive":bool(danger),
            "abstained":vals is None,
            "operator_receipts":response.get("source_graph_edits",[]),
        })
    return {"metrics":totals,"per_case":witnesses}


def verify_artifact(frozen):
    if (not isinstance(frozen,dict) or frozen.get("schema")!=search.SCHEMA
            or frozen.get("status")!="SOURCE_DERIVED_GRAPH_EDIT_PROGRAM_FROZEN"
            or frozen.get("receipt_sha256")!=world.digest({
                k:v for k,v in frozen.items() if k!="receipt_sha256"})
            or frozen.get("base_graph_rewrite_opcode_invented") is not False
            or frozen.get("heldout_language_module_imported_during_search") is not False
            or frozen.get("heldout_labels_consulted") is not False
            or frozen.get("external_action_executed") is not False
            or frozen.get("authority")!="NONE"):
        raise HOLD("Unreviewed or test-contaminated source graph-rewrite program")
    program=induce.validate(frozen.get("winning_program"))
    train=world.generate("train",seed=2026111001,repeats=6)
    dev=world.generate("dev",seed=2026111002,repeats=6)
    if (train["receipt_sha256"]!=frozen["source_training_sha256"]
            or dev["receipt_sha256"]!=frozen["source_development_sha256"]
            or program["source_training_sha256"]!=train["receipt_sha256"]):
        raise HOLD("Frozen graph program not bound to its original evidence")
    # Recompute the exact learned rule set; a changed-but-rehashed AST fails.
    if induce.construct(train,**program["parameters"])!=program:
        raise HOLD("Graph transitions/cues not reproducible from claimed contrasts")
    return train,program


def evaluate_frozen(frozen):
    train,program=verify_artifact(frozen)
    # The first import of the heldout language templates occurs HERE.
    import novel
    corpus=world.flatten(train)
    models={
        "induced_graph_relations":RelationalDecoder(program),
        "word_bayes_same_training":GraphBayes(corpus,mode="word"),
        "word_bigram_bayes_same_training":GraphBayes(corpus,mode="bigram"),
        "always_hold":AlwaysHold(),
    }
    trials=[]
    for family,seed,repeats in (
        ("OOV_CONTENT_TRANSFER",2026111021,12),
        ("NESTED_SCOPE_COMPOSITION",2026111022,10),
    ):
        data=novel.generate(family=family,seed=seed,repeats=repeats)
        cases=world.flatten(data)
        measurements={
            model:evaluate(decoder,cases)
            for model,decoder in models.items()
        }
        trials.append({
            "family":family,
            "seed":seed,
            "packet_receipt_sha256":data["receipt_sha256"],
            "count":len(cases),
            "models":measurements,
            "heldout_labels_were_not_used_to_select_program":True,
            "source_content_bindings_provided_by_event_record":True,
            "utterances_were_author_generated":True,
        })
    combined={}
    for name in models:
        combined[name]={
            k:sum(t["models"][name]["metrics"][k] for t in trials)
            for k in trials[0]["models"][name]["metrics"]
        }
    report={
        "schema":SCHEMA,
        "status":"GENERATED_GRAPH_RELATIONS_FROZEN_AND_FALSIFIED",
        "training_source_sha256":train["receipt_sha256"],
        "frozen_program_receipt_sha256":frozen["receipt_sha256"],
        "induced_program_receipt_sha256":program["receipt_sha256"],
        "operator_instances_derived_from_graph_differences":program[
            "derived_transition_count"]+program["derived_cue_count"],
        "sampled_new_verb_and_entity_lexemes_heldout_from_training":True,
        "speaker_agent_verb_patient_bound_externally":True,
        "novel_graph_primitives_invented":False,
        "open_domain_language_understanding_demonstrated":False,
        "independent_human_language_annotation":False,
        "test_packets":trials,"combined":combined,
        "real_world_authority":"NONE",
        "newly_installed_cartridge_methods":0,
        "external_actions_executed":False,
    }
    report["receipt_sha256"]=world.digest(report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        frozen=json.loads(args.frozen.read_text())
        result=evaluate_frozen(frozen)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        print(json.dumps({
            "schema":result["schema"],
            "total_cases":sum(x["count"] for x in result["test_packets"]),
            "source_induced_operator_instances":result[
                "operator_instances_derived_from_graph_differences"],
            "families":{x["family"]:{
                name:obs["metrics"] for name,obs in x["models"].items()}
                for x in result["test_packets"]},
            "combined":result["combined"],
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,induce.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
