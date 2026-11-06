"""MOTIF-011 Impossible Court benchmark with independent classical reference.

All legal rules and facts are *fictional stipulations*. Results demonstrate
safe epistemic representation, not improved legal judgment accuracy.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json

from casebook import cases,REVISION
from engine import decide,export,validate,pin,digest
from reference import independent


def run(out=None):
    records=[]
    count=Counter()
    mismatch=0
    for c in cases():
        proposed=decide(c)
        reference=independent(c)
        if not proposed["all_expected_checks_match"]:
            raise AssertionError("Fictional source owner fixture changed")
        outcomes=[]
        for q in proposed["results"]:
            four=q["result"]["four_value"]
            expected=reference[q["query_id"]]
            if four != expected:
                mismatch+=1
            count[four]+=1
            outcomes.append({
                "id":q["query_id"],
                "proposed":four,
                "independent_reference":expected,
                "direct_positive_premises":(
                    q["result"]["positive_proof"]["claims"]
                    if q["result"]["positive_proof"] else None),
                "direct_negative_premises":(
                    q["result"]["negative_proof"]["claims"]
                    if q["result"]["negative_proof"] else None),
                "conflict_witness":q["result"]["contradiction_witness"],
                "counterfactual_review_options":q["counterfactual_review_questions"],
            })
        doc=validate(export(c))
        records.append({
            "case_id":c["id"],"title":c["title"],
            "fictional_source":True,
            "source_card_digest":doc["source_contract_digest"],
            "queries":outcomes,
            "excluded_party_allegations":proposed["party_allegations_excluded"],
            "proof_count":proposed["proof_count"],
        })
    if mismatch:
        raise AssertionError("Independent four-valued reference contradicts MOTIF")
    answer={
        "schema":"motif.reason.impossible-court.benchmark.v1",
        "source_revision":REVISION,
        "source_blob":pin(),
        "cases":records,
        "case_count":len(records),
        "query_count":sum(count.values()),
        "independent_four_valued_reference_mismatches":mismatch,
        "epistemic_summary":dict(sorted(count.items())),
        "both_represented_without_arbitrary_facts":count["BOTH"],
        "truly_unknown_remained_unknown":count["UNDETERMINED"],
        "provenance_bound_review_options":sum(
            len(q["counterfactual_review_options"])
            for case in records for q in case["queries"]),
        "four_state_information_lost_if_forced_binary":
            count["BOTH"]+count["UNDETERMINED"],
        "comparison":"EXPLICIT_BINARY_DECISION_WOULD_COLLAPSE_BOTH_OR_UNDETERMINED",
        "model_fitted_to_real_judgments":False,
        "historical_court_opinion_extracted":False,
        "new_legal_rule_invented":False,
        "external_actions":False,"real_world_authority":False,
    }
    if out:
        p=Path(out)
        p.mkdir(parents=True,exist_ok=True)
        (p/"benchmark.json").write_text(
            json.dumps(answer,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        for c in cases():
            (p/(c["id"].lower()+".json")).write_text(export(c),encoding="utf-8")
    return answer


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     sort_keys=True,indent=2))
