"""REASON-022: run independently authored examples and source-scoped ethics.

This is deliberately two separate experiments:
(A) typed reasoning vs external, third-party-authored bAbI questions
(B) fictional Golden Mirror duties and scoped consent

Success on (A) NEVER validates moral meaning or grants rights in (B).
The third-party data challenge was authored long before MOTIF; the typed
interpreters and router are classical human-engineered, NOT autonomous
software synthesis, and can fail or abstain. We report ALL errors.
"""
from __future__ import annotations

from pathlib import Path
from collections import Counter
import json

from acquire import SOURCES,get_sources
from corpus import read,query_input
from router import discover,infer,boolean_projection_witness,question_family
from engines import ENGINES,solve,count_before_source_repair
from obligations import CASES,all_proofs,contradiction
from mirror_bridge import run_all,pin as pin019


def naive_flat_baseline(q):
    # This is a deliberately *weak* older representation, not a state-of-
    # the-art classical reasoner. It only knows the most frequent answer.
    if q.family=="COUNT":return "one"
    if q.family=="TIME":return "kitchen"
    if q.family=="TRANSFER":return "Mary"
    raise ValueError("Unrecognized source family")


def run(source_dir="reason-022-sources",out=None,train_limit=60,test_limit=250):
    source_audit=get_sources(source_dir)
    root=Path(source_dir)
    training={kind:read(root/entry["train"][0],kind,"train",limit=train_limit)
              for kind,entry in SOURCES.items()}
    model=discover(training)
    # The first 250 queries per task were inspected during initial
    # debugging (24 counting errors). They are now DEVELOPMENT, not blind.
    dev={kind:read(root/entry["test"][0],kind,"test",limit=250,skip=0)
         for kind,entry in SOURCES.items()}
    # The following 250 questions per task are a separate, previously
    # uninspected set reserved for the prospective post-repair evaluation.
    test={kind:read(root/entry["test"][0],kind,"test",limit=test_limit,skip=250)
          for kind,entry in SOURCES.items()}
    original_count=sum(count_before_source_repair(query_input(q))["answer"]==q.answer
                       for q in dev["COUNT"])
    repaired_dev_count=sum(solve("QUANTITY",query_input(q))["answer"]==q.answer
                           for q in dev["COUNT"])
    witness=boolean_projection_witness(training)
    families={}
    bad_examples=[]
    for family,queries in test.items():
        exact=0;incorrect=0;held=0;baseline=0;source_witness_valid=0
        for q in queries:
            request=query_input(q)
            # The question family is inferred by query grammar, not supplied
            # as part of the query to the candidate logic.
            proposal=infer(model,request)
            if naive_flat_baseline(q)==q.answer:baseline+=1
            if proposal["status"]=="ANSWER":
                if proposal["answer"]==q.answer:exact+=1
                else:incorrect+=1
                # All positive evidence must exist in original source text.
                if all(any(a["line"]==no and a["text"]==text
                           for a in request["facts"])
                       for no,text in proposal["premises"]):
                    source_witness_valid+=1
                else:raise AssertionError("Typed engine produced fabricated evidence")
            else:
                held+=1
            if proposal["status"]=="HOLD" or proposal["answer"]!=q.answer:
                if len([x for x in bad_examples if x["family"]==family])<7:
                    bad_examples.append({
                        "family":family,"source_id":q.id,
                        "question":q.question,"source_gold":q.answer,
                        "model_answer":proposal["answer"],
                        "model_status":proposal["status"],
                        "reason":proposal["reason"],
                    })
        families[family]={
            "independently_authored_test_questions":len(queries),
            "exact_source_answers":exact,
            "incorrect_confident_answers":incorrect,
            "explicit_abstentions":held,
            "weak_fixed_answer_baseline_exact":baseline,
            "source_bound_evidence_receipts":source_witness_valid,
            "accuracy_including_abstentions":exact/len(queries),
            "accuracy_among_attempts":(
                exact/(exact+incorrect) if exact+incorrect else None),
            "model_type_from_source_training":model[
                "selected_engine_by_external_training_family"][family],
            "heldout_source_outcome_is_not_human_welfare":True,
        }
    mirror=run_all()
    proof=all_proofs()
    cross=contradiction()
    if not all(row["source_case"]==p["source_case_id"]
               for row,p in zip(mirror,proof)):
        raise AssertionError("The moral source itself changed between evaluations")
    return_doc={
        "schema":"motif.reason022.unimagined-distinction.benchmark.v1",
        "external_dataset":"Facebook bAbI v1.1 copy from independent GitHub source",
        "original_external_source":source_audit,
        "training_questions":sum(map(len,training.values())),
        "test_questions":sum(map(len,test.values())),
        "inspected_development_questions":sum(map(len,dev.values())),
        "first_run_counting_development_exact_before_repair":original_count,
        "same_inspected_counting_development_exact_after_repair":repaired_dev_count,
        "source_repair_from_inspected_test_is_not_blind":True,
        "prospective_external_test_starts_after_first_250_per_family":True,
        "external_test":families,
        "external_source_failed_or_abstained_examples":bad_examples,
        "three_typed_representations_are_developer_written":True,
        "trained_question_type_router":model,
        "source_training_boolean_projection_impossibilities":witness,
        "obligation_old_boolean_impossibility":cross,
        "fictional_obligation_cases":len(CASES),
        "fictional_duty_source_proofs":proof,
        "actual_original_019_elf_receipts":mirror,
        "verified_original_golden_mirror_git_blob":pin019(),
        "actual_original_worker_subprocesses_primary_pass":4*len(CASES),
        "correct_obligation_source_to_critic_agreement":sum(
            m["typed_proof"]["state"]==(
                "SUGGEST_DISCUSSION_ONLY" if m[
                    "critic_eligible_for_read_only_discussion"] else
                m["typed_proof"]["state"]) for m in mirror),
        "no_real_world_permission_or_personal_assistance":True,
        "independent_external_QA_is_not_independent_human_ethics_evaluation":True,
        "external_examples_and_gold_never_enter_the_moral_other_circle":True,
        "no_automatic_arbitrary_new_program_invention":True,
        "classical_typed_baselines_can_match_or_exceed":True,
        "no_subjective_empathy_or_love_demonstrated":True,
        "permission_to_execute":False,
        "external_actions":False,
    }
    if out:
        dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
        (dest/"benchmark.json").write_text(
            json.dumps(return_doc,sort_keys=True,indent=2)+"\n",encoding="utf8")
        (dest/"external-typed-source-audit.json").write_text(json.dumps({
            "external_source":source_audit,
            "routed_models":model,"families":families,
            "negative_examples":bad_examples,
            "boolean_representation_counterexamples":witness,
        },sort_keys=True,indent=2)+"\n",encoding="utf8")
        (dest/"fictional-duties-and-original-elves.json").write_text(
            json.dumps({"proofs":proof,"counterexample":cross,
                        "original_elves":mirror},sort_keys=True,indent=2)+"\n",
            encoding="utf8")
    return return_doc


if __name__=="__main__":
    import sys
    if len(sys.argv)>3:
        raise SystemExit("usage: python trial.py [download-folder] [evidence-folder]")
    source=sys.argv[1] if len(sys.argv)>=2 else "reason-022-sources"
    out=sys.argv[2] if len(sys.argv)>=3 else None
    r=run(source,out)
    print(json.dumps({
        "independent_external_training_questions":r["training_questions"],
        "independent_external_test_questions":r["test_questions"],
        "inspected_development_questions":r["inspected_development_questions"],
        "count_initial_dev_exact":r["first_run_counting_development_exact_before_repair"],
        "count_repaired_dev_exact":r["same_inspected_counting_development_exact_after_repair"],
        "routed_representations":{
            k:v["model_type_from_source_training"] for k,v in r["external_test"].items()},
        "external_development_count_before_repair":r["first_run_counting_development_exact_before_repair"],
        "external_development_count_after_repair":r["same_inspected_counting_development_exact_after_repair"],
        "independent_external_results":{
            k:{"exact":v["exact_source_answers"],
               "wrong":v["incorrect_confident_answers"],
               "hold":v["explicit_abstentions"],
               "weak_baseline":v["weak_fixed_answer_baseline_exact"]}
            for k,v in r["external_test"].items()},
        "documented_boolean_insufficiency_pairs":sum(
            x.get("different_answer_to_same_old_view",False)
            for x in r["source_training_boolean_projection_impossibilities"]),
        "fictional_duty_cases":r["fictional_obligation_cases"],
        "actual_original_019_subprocesses":
            r["actual_original_worker_subprocesses_primary_pass"],
        "permission_to_execute":False,
    },sort_keys=True,indent=2))
