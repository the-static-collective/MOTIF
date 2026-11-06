"""LEGIT-005 frozen compositional-semantic benchmark.

48 cases, 36 valid / 12 invalid; source-separated, same assistant authored,
NOT investigator blind. Four policies: induced composition, teacher-pair rote
ablation, independent strong manual classical parser, always abstain.

The independent reference oracle exhaustively enumerates tiny hidden target
assignments; all cases use *the same* evidence tables and constraints.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

from runner import RAW_SCHEMA, examine, trained, neuro_packet
from classical_reference import parse_classical
from exact_reference import reference_oracle

HERE=Path(__file__).resolve().parent


def cases():
    with (HERE/"evaluation_cases.json").open(encoding="utf-8") as f:
        source=json.load(f)
    if source.get("schema")!="motif.meaning-evaluation.v1":
        raise AssertionError("Unsupported frozen evaluation file")
    items=source["cases"]
    if len(items)!=48 or len({x["id"] for x in items})!=48:
        raise AssertionError("Missing or duplicate sealed test cases")
    return items


def raw_case(record,index):
    n1p=2+index%3
    n1n=2+(index+1)%3
    n2p=3+(index+2)%3
    n2n=1+index%3
    data=[{"group":"g1","positive":n1p,"negative":n1n,"source_id":"SIM"},
          {"group":"g2","positive":n2p,"negative":n2n,"source_id":"SIM"}]
    anchors=[]
    mode=index%4
    if mode==1:
        anchors=[{"group":r["group"],"proxy":"negative","known_latent_true":0,
                  "known_latent_false":r["negative"],"origin":"SIMULATOR_TRUTH"}
                 for r in data]
    elif mode==2:
        anchors=[{"group":r["group"],"proxy":"positive",
                  "known_latent_true":r["positive"],"known_latent_false":0,
                  "origin":"SIMULATOR_TRUTH"} for r in data]
    elif mode==3:
        anchors=[{"group":"g1","proxy":"negative","known_latent_true":1,
                  "known_latent_false":0,"origin":"SIMULATOR_TRUTH"},
                 {"group":"g1","proxy":"positive","known_latent_true":0,
                  "known_latent_false":1,"origin":"SIMULATOR_TRUTH"}]
    return {"schema":RAW_SCHEMA,"id":"Semantics_"+record["id"],
            "scope":"SYNTHETIC_ONLY","question":record["question"],
            "indicator":record["indicator"],
            "sources":[{"id":"SIM","url":"synthetic://frozen-meaning-semantics",
                        "provenance":"SYNTHETIC_SIMULATOR"}],
            "observations":data,"anchors":anchors}


def rubric(rows,mode):
    measures={}
    for group in ("ALL",)+tuple(sorted({r["group"] for r in rows})):
        selected=rows if group=="ALL" else [r for r in rows if r["group"]==group]
        accepted=[r for r in selected if r[mode] is not None]
        valid=[r for r in selected if r["gold"] is not None]
        false_accept=sum(r["gold"] is None and r[mode] is not None for r in selected)
        correctly_parsed=sum(r[mode] is not None and r["gold"] is not None and
                            r[mode]["meaning"]==r["gold"]["meaning"] for r in selected)
        incorrect_semantics=sum(r[mode] is not None and r["gold"] is not None and
                                r[mode]["meaning"]!=r["gold"]["meaning"] for r in selected)
        incorrect_verdict=sum(r[mode] is not None and r["gold"] is not None and
                              r[mode]["meaning"]==r["gold"]["meaning"] and
                              r[mode]["answer"]!=r["gold"]["answer"] for r in selected)
        omitted=len(valid)-correctly_parsed-incorrect_semantics
        # Cost of wrong confident accept 1, valid unanswered .25, accepted
        # correct and unsupported held 0. Developer-chosen artificial utility.
        loss=false_accept+incorrect_semantics+incorrect_verdict+.25*omitted
        measures[group]={"cases":len(selected),"valid":len(valid),
                         "correct_semantics":correctly_parsed,
                         "incorrect_semantics":incorrect_semantics,
                         "incorrect_logical_verdict":incorrect_verdict,
                         "unjustified_accepts":false_accept,
                         "missed_supported":omitted,
                         "toy_selective_loss":round(loss,6),
                         "valid_coverage":round(correctly_parsed/len(valid),6)
                                          if valid else None}
    return measures


def benchmark():
    grammar=trained()
    records=cases()
    results=[]
    for i,example in enumerate(records):
        raw=raw_case(example,i)
        gold=(dict(meaning={**example["gold"]},
                   answer=reference_oracle(raw,example["gold"]["kind"]))
              if example["gold"] else None)
        # learner sees raw question/source counts, *no* gold.
        outcome=examine(raw,grammar)
        learner=(dict(meaning={k:outcome["parser"][k]
                    for k in ("kind","proxy","target")},
                    answer=outcome["claim"]["logical_answer_in_admitted_model"])
                 if outcome["status"]=="RESEARCH_HOLD" else None)
        # Conservative rote control only accepts already paired teacher phrases.
        rote=(learner if learner is not None and
              outcome["parser"]["seen_pair_in_teacher"] else None)
        conventional=parse_classical(raw["question"],raw["indicator"])
        classical=(dict(meaning=conventional,
                        answer=reference_oracle(raw,conventional["kind"]))
                   if conventional is not None else None)
        if learner is not None and learner["answer"] is None:
            raise AssertionError("Every synthetic case has antecedent observations")
        results.append({"id":example["id"],"group":example["group"],
                        "gold":gold,"induced":learner,"rote":rote,
                        "classical":classical,"always_hold":None,
                        "learner_status":outcome["status"]})
    reports={name:rubric(results,name) for name in
             ("induced","rote","classical","always_hold")}
    neuro=neuro_packet()
    # Logical complement: a counterexample is possible iff evidence
    # does NOT entail that none can exist.
    complementary=dict(neuro,question=(
        "Does missing neural command response rule out subjective experience?"))
    pair1=examine(neuro,grammar)
    pair2=examine(complementary,grammar)
    if pair1["status"]!="RESEARCH_HOLD" or pair2["status"]!="RESEARCH_HOLD":
        raise AssertionError("Cannot interpret direct public duality test")
    if pair1["claim"]["logical_answer_in_admitted_model"] == pair2["claim"]["logical_answer_in_admitted_model"]:
        raise AssertionError("Entailment / possibility duality not respected")
    return {"experiment":"MOTIF-LEGIT-005",
            "author_independent_blind_test":False,
            "method":"LEARNED_COMPOSITION_WITH_DECLARED_LOGICAL_OPERATORS",
            "teacher_count":grammar["teacher_count"],
            "learned_rules":len(grammar["rules"]),
            "cross_combinations_absent_from_training":grammar["novel_combinations"],
            "registered_cases":len(results),"valid_questions":36,
            "frozen_cases_sha256":sha256((HERE/"evaluation_cases.json").read_bytes()).hexdigest(),
            "teacher_digest":grammar["teacher_digest"],
            "metrics":reports,
            "neuroscience_counterexample_logically_possible":
                pair1["claim"]["logical_answer_in_admitted_model"],
            "neuroscience_negative_test_entails_absence":
                pair2["claim"]["logical_answer_in_admitted_model"],
            "neuroscience_actual_individual_consciousness":None,
            "observations_author_authenticated":False,
            "real_world_authority":False,
            "status":"RESEARCH_HOLD",
            "cases":results}


if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
