"""Full-source heldout retrieval benchmark, no invented court decisions.

Classic BM25 against a simple overlap baseline, both over all acquired
judicial paragraphs. Gold anchors and voice labels are kept out of reader.py.
Scores are reported even if poor—never manufacture a passing metric.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import json

from acquire import CASES
from contract import DEVELOPMENT,UNSEEN,SHA,VERSION
from reader import read_source,attributed,retrieve,validate_receipt
from review_keys import HELDOUT_QUESTIONS,NEGATIVE_QUESTIONS,UNANSWERABLE_BUT_RELEVANT


def evaluate(sources,out=None):
 docs={case:read_source(sources,case) for case in CASES}
 by_case={case:attributed(doc) for case,doc in docs.items()}
 metrics={method:Counter() for method in ("BM25","OVERLAP")}
 question_results=[]
 for key in HELDOUT_QUESTIONS:
  case=key["case"]
  observed=by_case[case]
  matching=[p for p in observed if key["target"].lower() in p["text"].lower()]
  if not matching:
   raise AssertionError("Independent source-owner review phrase missing from COMPLETE opinion: "+key["id"])
  if not any(p["voice_role"]==key["voice"] for p in matching):
   raise AssertionError("Gold judicial-voice attribution failed source-owner check "+key["id"])
  annotations=[]
  for method in metrics:
   result=retrieve(sources,case,key["question"],method=method,k=5)
   validate_receipt(sources,result)
   predicted=result["results"]
   records=[]
   for rank,row in enumerate(predicted,1):
    hit=(key["target"].lower() in row["excerpt"].lower()
         and row["voice_role"]==key["voice"])
    records.append(hit)
   summary={"retrieved":len(predicted),"recall_at_1":any(records[:1]),
            "recall_at_3":any(records[:3]),"recall_at_5":any(records[:5]),
            "first_hit_rank":next((i+1 for i,flag in enumerate(records) if flag),None),
            "top_results":[{
                "rank":i+1,"paragraph":p["paragraph_ordinal"],
                "voice_role":p["voice_role"],"score":p["relevance"],
                "source_sha256":p["text_sha256"],
                "quote":p["excerpt"][:110]} for i,p in enumerate(predicted)],
           }
   for k in (1,3,5):metrics[method][f"recall_at_{k}"]+=int(summary[f"recall_at_{k}"])
   annotations.append({"method":method,**summary})
  question_results.append({
      "id":key["id"],"case":case,
      "question":key["question"],
      "independently_reviewed_gold_anchors":[p["ordinal"] for p in matching],
      "reviewed_opinion_voice":key["voice"],
      "reviewed_epistemic_issue":key["meaning"],
      "systems":annotations,
      "raw_document_was_not_truncated_for_model":True,
  })
 negative=[]
 for key in NEGATIVE_QUESTIONS:
  res=retrieve(sources,key["case"],key["question"])
  negative.append({"id":key["id"],"status":res["status"],
                   "retrievals":len(res["results"]),"question":key["question"],
                   "no_external_answer_inferred":res["no_legal_outcome_inferred"]})
 relevant=[]
 for key in UNANSWERABLE_BUT_RELEVANT:
  response=retrieve(sources,key["case"],key["question"])
  relevant.append({"id":key["id"],"status":response["status"],
                   "evidence_can_be_retrieved_without_answering_yes_no":True,
                   "no_legal_outcome_inferred":response["no_legal_outcome_inferred"]})
 source_count=sum(d["word_count"] for d in docs.values())
 fields={
  "schema":"motif.reason.complete-opinion-benchmark.v1",
  "source_contract_revision":VERSION,
  "development_cases":list(DEVELOPMENT),
  "never_developed_opinion_cases":list(UNSEEN),
  "complete_opinion_body_words":{c:d["word_count"] for c,d in docs.items()},
  "complete_opinion_body_paragraphs":{c:d["paragraph_count"] for c,d in docs.items()},
  "total_source_words":source_count,
  "full_source_html_pin_passed_for_all":True,
  "heldout_questions":question_results,
  "heldout_question_count":len(question_results),
  "classical_benchmarks":{m:{
    "questions":len(question_results),
    **{f"recall_at_{k}":n[f"recall_at_{k}"] for k in (1,3,5)}
   } for m,n in metrics.items()},
  "out_of_source_questions":negative,
  "relevant_but_epistemically_unanswerable":relevant,
  "independent_gold_lives_only_in_evaluator":True,
  "plain_BM25_is_a_strong_classical_retrieval_baseline":True,
  "opinion_page_is_a_reproduction_not_signed_court_feed":True,
  "whole_original_source_not_truncated_to_manually_selected_passages":True,
  "complete_appellate_reasoning_not_established":True,
  "legal_holding_from_text_automatically_inferred":False,
  "verified_current_law":False,"real_world_authority":False,
  "external_actions_in_reader":False,
 }
 if out:
  folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
  (folder/"benchmark.json").write_text(json.dumps(fields,sort_keys=True,indent=2)+"\n",encoding="utf8")
  (folder/"retrieval-evidence.json").write_text(
      json.dumps(question_results,indent=2,sort_keys=True)+"\n",encoding="utf8")
 return fields


if __name__=="__main__":
 import sys
 if len(sys.argv) not in (2,3):
  raise SystemExit("usage: python trial.py <complete-source-directory> [evidence-directory]")
 r=evaluate(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None)
 print(json.dumps({
    "source_cases":len(CASES),"full_body_words":r["total_source_words"],
    "heldout_questions":r["heldout_question_count"],
    "metrics":r["classical_benchmarks"],
    "negative_queries":r["out_of_source_questions"],
 },indent=2,sort_keys=True))
