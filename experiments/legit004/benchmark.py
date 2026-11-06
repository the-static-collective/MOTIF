"""LEGIT-004 preregistered source-separated grammatical stress test.

All 30 questions were authored by the same assistant, not independently
blinded. The strong classical regex baseline deliberately has two additional
paraphrase rules, so a measured classical advantage is expected and valid.
"""
from __future__ import annotations

import json
from pathlib import Path

from bridge import RAW_SCHEMA, trained_grammar, examine, historical_neuroscience
from classical_reference import parse_reference

HERE=Path(__file__).resolve().parent
CASES=HERE/"evaluation_cases.json"

def registered():
    with open(CASES,encoding="utf-8") as inp:
        src=json.load(inp)
    if src.get("schema")!="motif.question-grammar-evaluation.v1":
        raise RuntimeError("Changed evaluation fixture")
    items=src["cases"]
    if len(items)!=30 or len(set(x["id"] for x in items))!=30:
        raise RuntimeError("Unexpected or repeated test cases")
    return items

def raw_case(case,index):
    # Structured evidence is deliberately present. The latent target, grammar
    # type and hidden label are NOT supplied to the pupil.
    return {
        "schema":RAW_SCHEMA,
        "id":"Eval_"+case["id"],
        "scope":"SYNTHETIC_ONLY",
        "question":case["question"],
        "indicator":case["indicator"],
        "sources":[{"id":"SRC","url":"synthetic://frozen-grammar-evidence",
                    "provenance":"SYNTHETIC_SIMULATOR"}],
        "observations":[{"group":"g_a","positive":3+index%5,
                         "negative":2+index%7,"source_id":"SRC"},
                        {"group":"g_b","positive":5+index%4,
                         "negative":4+index%6,"source_id":"SRC"}],
    }

def classical(raw):
    proposed=parse_reference(raw["question"])
    if proposed is None or proposed[0]!=raw["indicator"].lower().strip():
        return None
    proxy,target,kind=proposed
    return {"kind":kind,"proxy":proxy,"target":target}

def learned(raw,grammar):
    result=examine(raw,grammar)
    if result["status"]!="RESEARCH_HOLD":
        return None,result
    parsed=result["parser"]
    return {"kind":parsed["kind"],"proxy":parsed["proxy"],"target":parsed["target"]},result

def _score(rows):
    summary={}
    for policy in ("induced","classical","always_hold"):
        accepted=[row for row in rows if row[policy] is not None]
        supported=[row for row in rows if row["gold"] is not None]
        correct=[row for row in rows if row[policy] is not None and
                 row[policy]==row["gold"]]
        false_accept=[row for row in rows if row["gold"] is None and
                      row[policy] is not None]
        wrong_parse=[row for row in rows if row["gold"] is not None and
                     row[policy] is not None and row[policy]!=row["gold"]]
        missed=len(supported)-len(correct)-len(wrong_parse)
        # Explicit toy loss: wrong confident parses cost 1, unanswered valid
        # questions cost 1/4, and justified refusal costs zero.
        toy_loss=len(false_accept)+len(wrong_parse)+.25*missed
        per_group={}
        for group in sorted(set(x["group"] for x in rows)):
            subset=[x for x in rows if x["group"]==group]
            per_group[group]={
                "total":len(subset),
                "correct_accepted":sum(x[policy]==x["gold"] and
                                        x["gold"] is not None for x in subset),
                "unjustified_accept":sum(x["gold"] is None and x[policy] is not None
                                          for x in subset),
                "held":sum(x[policy] is None for x in subset),
            }
        summary[policy]={
            "correct_accepted":len(correct),
            "total_supported":len(supported),
            "false_accept":len(false_accept),
            "wrong_confident_parse":len(wrong_parse),
            "missed_supported":missed,
            "selective_coverage":round(len(correct)/len(supported),6),
            "toy_loss":round(toy_loss,6),
            "per_group":per_group,
        }
    return summary

def report():
    grammar=trained_grammar()
    rows=[]
    for index,case in enumerate(registered()):
        raw=raw_case(case,index)
        proposed,result=learned(raw,grammar)
        if proposed is not None:
            rationale=result["reasoned_claim"]
            if (rationale["verdict"]!="NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE"
                    or rationale["individual_probability"] is not None
                    or not result["countermodels_preserve_evidence"]):
                raise AssertionError("Parser promoted unobserved target")
        rows.append({"id":case["id"],"group":case["group"],"gold":case["gold"],
                     "induced":proposed,"classical":classical(raw),
                     "always_hold":None,"induced_status":result["status"]})
    stats=_score(rows)
    # Exact classical on human-authored textbook grammar is strong; no forced
    # claim that the learner must win. Any negative result is retained.
    neuroscience=examine(historical_neuroscience(),grammar)
    return {"experiment":"MOTIF-LEGIT-004",
            "teacher_count":grammar["teacher_count"],
            "induced_grammars":len(grammar["rules"]),
            "evaluation_cases":len(rows),
            "source_type":"ASSISTANT_AUTHORED_NONBLIND",
            "objective":"COLD_QUESTION_TEXT_TO_PREDEFINED_LOGIC_WITH_STRUCTURED_COUNTS",
            "full_text_to_evidence_comprehension":False,
            "unseen_language_generalization":False,
            "methods":{"induced":stats["induced"],
                       "strong_classical_regex":stats["classical"],
                       "always_hold":stats["always_hold"]},
            "clinical_packet_status":neuroscience["status"],
            "clinical_packet_implication":neuroscience["reasoned_claim"]["verdict"],
            "all_cases":rows,
            "real_world_authority":False,
            "status":"RESEARCH_HOLD"}

if __name__=="__main__":
    print(json.dumps(report(),sort_keys=True,indent=2))
