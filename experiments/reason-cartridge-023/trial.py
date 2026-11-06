"""REASON-023: run MANY-TRUTH MIRROR, preserve every wrong source hypothesis.

PART A: 250 next-slice independently authored bAbI three-party questions.
The preceding REASON-022 experiment had already inspected questions 1-500.
The proposed graph and ambiguity policy are fixed BEFORE inspecting this
additional question 501-750 slice. Gold stays solely in the evaluator.

PART B: an artificial source-owner can clarify which of two *literally
supported* hypotheses they intended, but cannot retroactively authenticate
the independent historical bAbI author or create real-person consent.

PART C: six fictional signed assertions run through the actual pinned 011
paraconsistent verifier. Explicit BOTH is not the same as multiple answers.

PART D: the original Golden Mirror's four subprocess elves check permission
to ASK; four cases exercise consent, refusal and lack of contact permission.

Nothing here acts in the world, and bAbI is NOT a test of the Golden Rule.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

from source_graph import compile_graph,verify_graph,original_022,digest,pin
from inquiry import SyntheticClarifier,investigate,select_question
from polarity import all_cases,pin as pin011
from mirror_bridge import reflect,pin as pin019

HERE=Path(__file__).resolve().parent
P022=HERE.parent/"reason-cartridge-022"
sys.path.append(str(P022))
from acquire import get_sources,SOURCES
from corpus import read,query_input

BENCHMARK_SLICE_OFFSET=500
BENCHMARK_SIZE=250


def source_test(q):
    return query_input(q)


def fixed_full_graph_baseline(source):
    """Strong classical baseline: re-extract every event, count distinct answers.

    This is intentionally the same policy with a separate simple loop:
    the multi-answer graph is a classical operation, not superior to
    another implementation of the same operation.
    """
    from engines import GIVE
    import re
    shapes=(
      (r"^What did ([A-Z][a-z]+) give to ([A-Z][a-z]+)\?$", lambda g,x:x[1] if (x[0],x[2])==g else None),
      (r"^Who gave the ([a-z]+) to ([A-Z][a-z]+)\?$", lambda g,x:x[0] if (x[1],x[2])==g else None),
      (r"^Who gave the ([a-z]+)\?$", lambda g,x:x[0] if x[1]==g[0] else None),
      (r"^Who did ([A-Z][a-z]+) give the ([a-z]+) to\?$", lambda g,x:x[2] if (x[0],x[1])==g else None),
      (r"^Who received the ([a-z]+)\?$", lambda g,x:x[2] if x[1]==g[0] else None),
    )
    shape=next(((m.groups(),check) for pattern,check in shapes
                for m in [re.fullmatch(pattern,source["question"])] if m),None)
    if shape is None:return []
    args,check=shape
    return sorted({
      check(args,m.groups())
      for entry in source["facts"]
      for m in [GIVE.fullmatch(entry["text"])]
      if m and check(args,m.groups()) is not None
    })


def synthetic_source():
    return {"source_id":"FICTIONAL-NEIGHBOR-AMBIGUOUS",
            "question":"What did Bill give to Mary?",
            "facts":[
                {"line":2,"text":"Bill gave the apple to Mary."},
                {"line":7,"text":"Anna handed the book to Fred."},
                {"line":11,"text":"Bill passed the football to Mary."},
            ]}


def run(source_dir="reason-023-sources",output=None):
    acquired=get_sources(source_dir)
    corpus_path=Path(source_dir)/SOURCES["TRANSFER"]["test"][0]
    source_questions=read(corpus_path,"TRANSFER","test",
                          limit=BENCHMARK_SIZE,skip=BENCHMARK_SLICE_OFFSET)
    if len(source_questions)!=BENCHMARK_SIZE:
        raise AssertionError("Independent untouched transfer slice missing")
    counts={
        "total":0,"source_single_answer":0,
        "source_non_unique":0,"source_no_answer":0,
        "single_answer_correct":0,"single_answer_wrong":0,
        "non_unique_gold_supported":0,"non_unique_gold_not_supported":0,
        "no_answer_gold_supported":0,
        "original_022_correct":0,"original_022_wrong":0,"original_022_hold":0,
        "original_wrong_now_ambiguous":0,
        "strong_classical_equivalence":0,
    }
    mistakes=[]
    held_examples=[]
    for q in source_questions:
        src=source_test(q)
        source_graph=compile_graph(src)
        verify_graph(src,source_graph)
        strong=fixed_full_graph_baseline(src)
        ours=sorted(x["answer"] for x in source_graph["candidates"])
        if strong==ours:counts["strong_classical_equivalence"]+=1
        else:raise AssertionError("Independent classical baseline disagreed")
        prior=original_022(src)
        counts["total"]+=1
        if prior["status"]=="ANSWER":
            if prior["answer"]==q.answer:counts["original_022_correct"]+=1
            else:counts["original_022_wrong"]+=1
        else:counts["original_022_hold"]+=1
        if source_graph["status"]=="ANSWER":
            counts["source_single_answer"]+=1
            if source_graph["selected_answer"]==q.answer:
                counts["single_answer_correct"]+=1
            else:
                counts["single_answer_wrong"]+=1
                mistakes.append({
                    "source_id":q.id,"question":q.question,
                    "model_answer":source_graph["selected_answer"],
                    "source_gold":q.answer,"source_graph":source_graph,
                    "official_support_indices_posthoc":list(q.supporting_ids),
                })
        elif len(ours)>1:
            counts["source_non_unique"]+=1
            if q.answer in ours:counts["non_unique_gold_supported"]+=1
            else:counts["non_unique_gold_not_supported"]+=1
            if prior["status"]=="ANSWER" and prior["answer"]!=q.answer:
                counts["original_wrong_now_ambiguous"]+=1
            held_examples.append({
                "source_id":q.id,"question":q.question,
                "source_gold_for_scoring_only":q.answer,
                "all_source_supported_answers":ours,
                "complete_source_witnessed_graph":source_graph,
                "old_answer":prior["answer"],
                "gold_is_in_ambiguity_set":q.answer in ours,
                "not_a_real_person_or_ethical_conclusion":True,
            })
        else:
            counts["source_no_answer"]+=1
            mistakes.append({
                "source_id":q.id,"source_gold":q.answer,"question":q.question,
                "model_answer":None,"reason":source_graph["reason"],
            })
    if sum(counts[k] for k in (
        "source_single_answer","source_non_unique","source_no_answer"))!=250:
        raise AssertionError("Source outcomes were omitted")

    # A separate synthetic source oracle decides one case; its "preference"
    # is NEVER retroactively applied to independent bAbI gold.
    toy=compile_graph(synthetic_source())
    clarifier=SyntheticClarifier("football",contact=True,question_permission=True)
    clarified=investigate(toy,clarifier)
    declined=investigate(toy,SyntheticClarifier(
        "football",contact=True,question_permission=True,refuse=True))
    uncontactable=investigate(toy,SyntheticClarifier(
        "football",contact=False,question_permission=False))
    no_owner=investigate(toy)
    balanced=select_question(["apple","book","football","map"])
    if clarified["current_source_hypothesis"]!="football":
        raise AssertionError("Source-owned clarification failed")
    if declined["stage"]!="HOLD_SOURCE_REFUSED" or (
            uncontactable["questions"] or no_owner["questions"]):
        raise AssertionError("Source veto was ignored")

    original_views=[
        reflect(contact=True,question_permission=True,self_would_ask=True),
        reflect(contact=True,question_permission=True,self_would_ask=False),
        reflect(contact=True,question_permission=False,self_would_ask=True),
        reflect(contact=False,question_permission=False,self_would_ask=True),
    ]
    hypothetical_signed=all_cases()
    four_states={x["case"]:x["status"] for x in hypothetical_signed}

    report={
        "schema":"motif.reason023.many-truth-benchmark.v1",
        "source_corpus":acquired,
        "exact_prior022_code_sha":pin(),
        "exact_prior011_source":pin011(),
        "exact_prior019_source":pin019(),
        "source_test_is_prospectively_reserved_after_prior_022_inspection":True,
        "external_source_test_task":"TRANSFER",
        "independent_test_first_ordinal":BENCHMARK_SLICE_OFFSET+1,
        "independent_test_last_ordinal":BENCHMARK_SLICE_OFFSET+BENCHMARK_SIZE,
        "external_test_counts":counts,
        "source_nonunique_examples":held_examples[:12],
        "confident_mistakes_and_no_source_examples":mistakes[:12],
        "strong_classical_multi_answer_reference_ties":True,
        "scripted_ambiguous_case":{
            "source_graph":toy,
            "owner_confirmed":clarified,
            "owner_declined":declined,
            "no_contact":uncontactable,
            "no_source_owner":no_owner,
            "balanced_question_four_alternatives":balanced,
        },
        "scope_sensitive_original_019_elves":original_views,
        "original_019_subprocesses_primary_pass":4*len(original_views),
        "independently_pinned_011_four_value_cases":hypothetical_signed,
        "four_value_stage_counts":{
            name:sum(v==name for v in four_states.values())
            for name in ("SUPPORTED","REFUTED","BOTH","UNDETERMINED")
        },
        "historical_source_ambiguity_not_fictional_consent":True,
        "distinct_candidates_do_not_automatically_mean_a_paraconsistent_BOTH":True,
        "fully_automated_world_view_not_a_human_judgment":True,
        "no_objective_ethics_love_or_real_person_measured":True,
        "permission_to_execute":False,"external_actions":False,
    }
    if output is not None:
        root=Path(output);root.mkdir(parents=True,exist_ok=True)
        for name,obj in (
            ("benchmark.json",report),
            ("all_source_candidate_groups.json",{
                "counts":counts,"source_ambiguous_examples":held_examples,
                "confident_errors":mistakes}),
            ("four-valued-fictional-polarity.json",hypothetical_signed),
            ("synthetic-active-inquiry-and-golden-mirror.json",{
                "inquiry":report["scripted_ambiguous_case"],
                "elves":original_views}),
        ):
            (root/name).write_text(
                json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n",
                encoding="utf8")
    return report


if __name__=="__main__":
    import sys
    if len(sys.argv)>3:
        raise SystemExit("usage: python trial.py [source-directory] [evidence-directory]")
    result=run(sys.argv[1] if len(sys.argv)>1 else "reason-023-sources",
               sys.argv[2] if len(sys.argv)>2 else None)
    print(json.dumps({
        "independent_source_test_cases":result["external_test_counts"]["total"],
        "original_re022_confident_wrong":result["external_test_counts"]["original_022_wrong"],
        "multi_answer_source_graph":{
            k:result["external_test_counts"][k] for k in (
                "source_single_answer","single_answer_correct",
                "single_answer_wrong","source_non_unique",
                "non_unique_gold_supported","non_unique_gold_not_supported",
                "source_no_answer","original_wrong_now_ambiguous",
                "strong_classical_equivalence")},
        "simulated_source_clarified":result["scripted_ambiguous_case"][
            "owner_confirmed"]["current_source_hypothesis"],
        "source_refusal_forces_hold":result["scripted_ambiguous_case"][
            "owner_declined"]["stage"],
        "scope_sensitive_actual_019_subprocesses":result[
            "original_019_subprocesses_primary_pass"],
        "four_valued_source_cases":result["four_value_stage_counts"],
        "actual_person_contacted":False,
    },indent=2,sort_keys=True))
