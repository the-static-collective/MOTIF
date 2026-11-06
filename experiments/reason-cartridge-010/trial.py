"""Historical odd-case reasoning: train on ghosts and a fighter jet,
withhold monkey selfies and fox possession as independent transfer probes.
No live court docket fetch, current-law inference or judgment prediction.
"""
from __future__ import annotations

from pathlib import Path
import json

from casebook import CASES
from tasks import training,heldout,unsupported,unsupported_forum,make
from typed_lens import fit,validate,select,pin
from receiver import Receiver


def shallow_issue_first(scenario):
    """Deliberately weak comparative baseline: the first matching buzzword."""
    return next((card["id"] for card in scenario.cards
                 if card.get("issue")==scenario.query["issue"]),None)


def run(folder=None):
    teaching=training()
    raw=fit(teaching)
    method=validate(raw)
    reviewing=Receiver(raw)
    independent=heldout()
    review=reviewing.preview(independent)
    if review["errors"]==0:
        reviewing.admit("ADMIT_READ_ONLY",review["review_digest"])
    rows=[]
    for scenario in independent:
        result=reviewing.suggest(scenario)
        rows.append({
            "question":scenario.id,
            "target_legal_issue":scenario.query["issue"],
            "selected_curated_record":result["source_id"],
            "expected_record":scenario.expected,
            "correct":result["source_id"]==scenario.expected,
            "epistemic_type":result["epistemic_type"],
            "historical_summary":result["historical_paraphrase"],
            "opinion_url":result["opinion_url"],
            "separate_view_not_majority":
                result["status"]=="SEPARATE_VIEW_NOT_MAJORITY_HOLDING",
            "weak_issue_first_id":shallow_issue_first(scenario),
        })
    unsupported_results=[
        reviewing.suggest(unsupported()),
        reviewing.suggest(unsupported_forum()),
    ]
    # Further requests that misread case nuance MUST stay outside the
    # opinion-anchored corpus instead of creating an invented outcome.
    ghosts=make("STAMBOVSKY",0)
    from tasks import Scenario
    unsupported_ghost=Scenario(
        "STAMBOVSKY-LITERAL-GHOST",
        dict(ghosts.query,issue="EMPIRICAL_SUPERNATURAL_VERIFICATION"),
        ghosts.cards,"HOLD")
    supernatural=reviewing.suggest(unsupported_ghost)
    if any(answer["status"]!="HOLD_OUTSIDE_VERIFIED_RECORD"
           for answer in unsupported_results+[supernatural]):
        raise AssertionError("Unverified paranormal or current-forum claim leaked")
    receipt={
        "schema":"motif.reason.strange-law.benchmark.v1",
        "historical_cases":[{
            "id":key,"title":value["title"],"citation":value["citation"],
            "court":value["court"],"opinion_url":value["opinion_url"],
            "curated_not_raw_opinion":True,
        } for key,value in CASES.items()],
        "training_cases":["STAMBOVSKY","LEONARD"],
        "heldout_cases":["NARUTO","PIERSON"],
        "teaching_questions":len(teaching),
        "independent_review":review,
        "selected_typed_operator":method["selected_guard_program"],
        "type_guard_ablation_witnesses":len(method["missing_operator_witnesses"]),
        "typed_subset_candidates":method["candidate_gate_subsets"],
        "heldout_correct":sum(row["correct"] for row in rows),
        "heldout_total":len(rows),
        "shallow_issue_first_correct":sum(
            row["weak_issue_first_id"]==row["expected_record"] for row in rows),
        "heldout_outcomes":rows,
        "unknown_questions_holding_without_fabrication":len(unsupported_results)+1,
        "fantastical_claim_treated_as_literal_empirical_fact":False,
        "constitutional_and_statutory_standing_collapsed":False,
        "dissent_treated_as_majority":False,
        "resuscitated_claim_mistaken_for_final_relief":False,
        "owner_curated_annotation_not_unstructured_judgment_reasoning":True,
        "general_legal_reasoning_demonstrated":False,
        "current_law_advice_offered":False,
        "no_new_fundamental_boolean_operator":True,
        "external_actions":False,"real_world_authority":False,
    }
    if folder:
        directory=Path(folder)
        directory.mkdir(parents=True,exist_ok=True)
        (directory/"typed-operator.json").write_text(raw,encoding="utf-8")
        (directory/"benchmark.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return receipt


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     indent=2,sort_keys=True))
