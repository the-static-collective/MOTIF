"""RING-011: honest post-freeze nested-meaning test, with same-data Bayes control.

Reads ONLY a verified, already frozen source-derived program. The separate
heldout module is not imported until after verifying its original train/dev
identity and re-deriving its rules without accessing new labels.

No private manuscript phrases are mounted, committed, or echoed. Public
stress tests are newly authored paraphrase *structures*, not quote recovery.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path

import corpus,binder,search

SCHEMA="motif.ring011.postfreeze-nested-carrier-trial.v1"

class HOLD(ValueError):
    pass


class Bayes:
    """Conventional supervised factorized bag-of-words/bigrams graph baseline.

    Uses the same source event variable abstraction and the same train labels
    as the induced binder. No access to challenge data until program frozen.
    """
    def __init__(self,examples,*,mode):
        if mode not in ("WORD","BIGRAM"):
            raise HOLD("Unreviewed baseline graph features")
        self.mode=mode
        dataset=[(self.feats(x["text"],x["observed_event"]),
                  search.corpus.graph_map(x["semantic_graph"]))
                 for x in examples]
        self.vocab=set(k for f,_ in dataset for k in f)
        self.clf={}
        for rel in corpus.RELATIONS:
            byclass=Counter()
            byword=defaultdict(Counter)
            totals=Counter()
            for features,graph in dataset:
                label=graph[("ROOT","FORCE") if rel=="ROOT_FORCE" else
                            ("EVENT","SCOPE") if rel=="EVENT_SCOPE" else
                            ("EVENT","POLARITY")]
                byclass[label]+=1
                byword[label].update(features)
                totals[label]+=sum(features.values())
            self.clf[rel]=(byclass,byword,totals)

    def feats(self,text,observed):
        info=binder.abstract(text,observed)
        words=info["tokens"]
        result=Counter("w:"+t for t in words)
        if self.mode=="BIGRAM":
            result.update("b:"+a+"|"+b for a,b in zip(words,words[1:]))
        return result

    def parse(self,text,observed,carrier):
        try:
            features=self.feats(text,observed)
        except binder.HOLD:
            return {"status":"HOLD","graph":None,
                    "original_sha256":sha256(text.encode()).hexdigest()}
        assigned={}
        for rel,(classes,frequency,totals) in self.clf.items():
            scores={}
            for label,count in classes.items():
                prior=math.log(count+1)
                den=totals[label]+len(self.vocab)+1
                scores[label]=prior+sum(
                    n*math.log((frequency[label][word]+1)/den)
                    for word,n in features.items())
            assigned[rel]=max(scores,key=lambda key:(scores[key],key))
        return {
            "status":"NONAUTHORITATIVE_CLASSICAL_GRAPH_HYPOTHESIS",
            "graph":corpus.frame(
                assigned["ROOT_FORCE"],assigned["EVENT_SCOPE"],
                assigned["EVENT_POLARITY"],carrier,observed),
            "original_sha256":sha256(text.encode()).hexdigest(),
            "external_effect_permission":"NONE",
        }


class Hold:
    def parse(self,text,observed,carrier):
        return {"status":"HOLD","graph":None,
                "original_sha256":sha256(text.encode()).hexdigest()}


class Induced:
    def __init__(self,program):
        self.program=program
    def parse(self,text,observed,carrier):
        return binder.predict(self.program,text,observed,carrier)


def verify_frozen(doc):
    if (not isinstance(doc,dict) or doc.get("schema")!=search.SCHEMA
            or doc.get("status")!="SOURCE_DERIVED_NESTED_VOICE_PROGRAM_FROZEN"
            or doc.get("receipt_sha256")!=corpus.digest({
                k:v for k,v in doc.items() if k!="receipt_sha256"})
            or doc.get("sealed_test_imported_during_search") is not False
            or doc.get("sealed_test_labels_used_to_select_model") is not False
            or doc.get("source_book_private_text_committed") is not False
            or doc.get("outside_actions_authorized") is not False
            or doc.get("authority")!="NONE"):
        raise HOLD("Source model not legitimately frozen")
    model=binder.validate(doc.get("winning_program"))
    train=corpus.generate("train",seed=2026111101,rounds=5)
    dev=corpus.generate("dev",seed=2026111102,rounds=5)
    if (doc.get("source_train_sha256")!=train["receipt_sha256"]
            or doc.get("source_dev_sha256")!=dev["receipt_sha256"]
            or model["source_train_sha256"]!=train["receipt_sha256"]):
        raise HOLD("Selected binder not bound to original source packets")
    regenerated=binder.derive(train,**model["parameters"])
    if regenerated!=model:
        raise HOLD("Derived binding program not reproducible from original examples")
    return train,model


def evaluate_frozen(frozen):
    train,model=verify_frozen(frozen)
    # Absolute isolation: the invented program and its config are already
    # selected, source-bound, and have been re-derived before this import.
    import novel,novel_harder
    cases=corpus.flatten(train)
    systems={
        "source_induced_scope_binder":Induced(model),
        "same_data_word_bayes":Bayes(cases,mode="WORD"),
        "same_data_bigram_bayes":Bayes(cases,mode="BIGRAM"),
        "always_hold":Hold(),
    }
    groups=[]
    for family,seed in (
        ("OOV_CONTENT",2026111108),
        ("CRYPTIC_NESTED",2026111109),
        ("COUNTEREXAMPLE_FOLLOWUP",2026111119),
    ):
        new=(novel_harder.generate(seed=seed,rounds=6)
             if family=="COUNTEREXAMPLE_FOLLOWUP" else
             novel.generate(family=family,seed=seed,rounds=5))
        examples=corpus.flatten(new)
        rows={name:search.measure(
            decoder.parse,examples)
              for name,decoder in systems.items()}
        groups.append({
            "family":family,
            "author_created_source_sha256":new["receipt_sha256"],
            "case_count":len(examples),
            "synthetic_carrier_breakdown":{
                carrier:sum(x["carrier"]==carrier for x in examples)
                for carrier in corpus.CARRIERS},
            "comparisons":rows,
            "labels_not_seen_by_algorithm_search":True,
            "source_events_and_carriers_externally_supplied":True,
            "private_manuscript_contents_not_in_test":True,
            "is_fresh_to_repaired_algorithm":family=="COUNTEREXAMPLE_FOLLOWUP",
            "first_two_families_used_to_identify_previous_model_defect":
                family!="COUNTEREXAMPLE_FOLLOWUP",
        })
    totals={}
    for name in systems:
        totals[name]={
            key:sum(group["comparisons"][name]["metrics"][key]
                    for group in groups)
            for key in groups[0]["comparisons"][name]["metrics"]
        }
    context={
        "speaker":"mina","agent":"noa","verb":"carry","patient":"map",
    }
    adversarial=[]
    for line in novel.UNBOUND_UTTERANCES:
        out=binder.predict(model,line,context,"SONG")
        adversarial.append({
            "source_sha256":sha256(line.encode()).hexdigest(),
            "status":out["status"],
            "hallucinated_event_graph":out["graph"] is not None,
            "not_real_world_intent":True,
        })
    result={
        "schema":SCHEMA,
        "status":"NESTED_VOICE_BINDER_FROZEN_AND_FALSIFIED",
        "source_train_sha256":train["receipt_sha256"],
        "frozen_program_sha256":frozen["receipt_sha256"],
        "source_derived_program_sha256":model["receipt_sha256"],
        "test_packets":groups,
        "combined":totals,
        "unbound_cryptic_diagnostics":adversarial,
        "corpus_inspired_by_private_editing_structure_not_private_quotes":True,
        "synthetic_editorial_carrier_categories_from_read_source":True,
        "not_independently_human_authored_or_annotated":True,
        "original_two_test_families_are_now_debugging_regressions":True,
        "third_family_created_after_post_falsifier_source_fix":True,
        "source_event_and_carrier_not_open_language_discoveries":True,
        "scope_grammar_runtime_predefined":True,
        "new_base_computational_operator_invented":False,
        "general_natural_language_understanding_verified":False,
        "event_truth_and_corresponding_record_authenticated":False,
        "new_cartridge_or_external_tool_admissions":0,
        "outside_actions_executed":False,
        "authority":"NONE",
    }
    result["receipt_sha256"]=corpus.digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        x=evaluate_frozen(json.loads(args.frozen.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
        print(json.dumps({
            "schema":x["schema"],
            "test_cases":sum(p["case_count"] for p in x["test_packets"]),
            "results":x["combined"],
            "unbound_cryptic_refused":sum(not v["hallucinated_event_graph"]
                                         for v in x["unbound_cryptic_diagnostics"]),
            "total_unbound_cryptic":len(x["unbound_cryptic_diagnostics"]),
            "receipt_sha256":x["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,binder.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
