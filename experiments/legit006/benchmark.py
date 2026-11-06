"""LEGIT-006: freeze semantic minimal-pair adversaries and cold external OOD gate.

Comparison arms: induced 32-rule composed teacher grammar, exact-seen-pair rote
ablation, strong conventional hand-written regex parser, and always HOLD.

A separate human-authored FraCaS NLI development slice is used strictly as
an *out-of-distribution safety gate*, not as an NLI accuracy benchmark. NLI
requires premise-hypothesis inference, which this instrument-ledger router
does not implement. Full original labels remain intact and unused in training.
"""
from __future__ import annotations

from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path

from grammar import parse
from runner import examine, learned
from classical_reference import parse_reference, reference_truth
from ledger import SCHEMA as LEDGER_SCHEMA, inspect

HERE=Path(__file__).resolve().parent
CASES=HERE/"evaluation_cases.json"
EXTERNAL=HERE/"external"/"fracas_dev.csv"


def all_cases():
    with CASES.open(encoding="utf-8") as handle:
        source=json.load(handle)
    if source.get("schema")!="motif.semantic-adversary-eval.v1":
        raise AssertionError("Unknown registered questions")
    questions=source["items"]
    if len(questions)!=92 or len({q["id"] for q in questions})!=92:
        raise AssertionError("Question manifest corrupted")
    return questions


def report_entry(ident,root,kind,assurance="DECLARED_VALID",
                 coverage="UNSPECIFIED",detection="UNSPECIFIED"):
    return {"id":ident,"root":root,"kind":kind,"assurance":assurance,
            "coverage":coverage,"detection":detection}


def ledger_for(question):
    case=question["domain"]%8
    reports=[]
    if case==1:
        reports=[report_entry("n1","negative_root","NEGATIVE_SENSOR",
                              coverage="PARTIAL",detection="UNKNOWN")]
    elif case==2:
        reports=[report_entry("n1","negative_root","NEGATIVE_SENSOR",
                              coverage="EXHAUSTIVE",detection="GUARANTEED")]
    elif case==3:
        reports=[report_entry("p1","positive_root","POSITIVE_WITNESS")]
    elif case==4:
        reports=[report_entry(f"p{i}","positive_root","POSITIVE_WITNESS")
                 for i in range(1,5)]
    elif case==5:
        reports=[report_entry("n1","unverified_negative","NEGATIVE_SENSOR",
                              assurance="UNVERIFIED",coverage="EXHAUSTIVE",
                              detection="GUARANTEED")]
    elif case==6:
        reports=[
            report_entry("p1","positive_root","POSITIVE_WITNESS"),
            report_entry("n1","negative_root","NEGATIVE_SENSOR",
                         coverage="EXHAUSTIVE",detection="GUARANTEED")]
    elif case==7:
        reports=[
            report_entry("n1","negative_root","NEGATIVE_SENSOR",
                         coverage="PARTIAL",detection="UNKNOWN"),
            report_entry("p1","unverified_positive","POSITIVE_WITNESS",
                         assurance="UNVERIFIED")]
    return {"schema":LEDGER_SCHEMA,"id":"Ledger_"+question["id"],
            "scope":"SYNTHETIC_ONLY",
            "target":question["target"],"indicator":question["indicator"],
            "reports":reports}


def _metrics(rows,policy):
    groups=["ALL"]+sorted({r["group"] for r in rows})
    result={}
    for group in groups:
        subset=rows if group=="ALL" else [r for r in rows if r["group"]==group]
        supported=[r for r in subset if r["gold_kind"] is not None]
        correct=sum(r[policy] is not None and
                    r[policy]["kind"]==r["gold_kind"] and
                    r[policy]["value"]==r["gold_value"]
                    for r in supported)
        wrong_semantics=sum(r[policy] is not None and
                            r[policy]["kind"]!=r["gold_kind"]
                            for r in supported)
        wrong_value=sum(r[policy] is not None and
                        r[policy]["kind"]==r["gold_kind"] and
                        r[policy]["value"]!=r["gold_value"]
                        for r in supported)
        invalid_accept=sum(r[policy] is not None and r["gold_kind"] is None
                           for r in subset)
        missed=sum(r[policy] is None for r in supported)
        # Developer-chosen costs for conservative source reasoning. This is
        # not a calibrated decision criterion for any actual situation.
        toy_loss=invalid_accept+wrong_semantics+wrong_value+0.25*missed
        result[group]={
            "cases":len(subset),"valid":len(supported),
            "correct_kind_and_truth":correct,
            "invalid_accepted":invalid_accept,
            "wrong_kind":wrong_semantics,
            "wrong_logical_value":wrong_value,
            "missed_valid":missed,
            "selective_coverage":round(correct/len(supported),6) if supported else None,
            "toy_selective_loss":round(toy_loss,6)}
    return result


def external_ood_probe(grammar):
    """FraCaS is a genuinely independently authored NLI benchmark.

    It is the WRONG task schema for this narrow evidence ledger.
    We check whether a single hypothesis accidentally resembles a registered
    evidence statement. HOLD is required instead of falsely assigning an
    entailment/contradiction/neutral label.
    """
    with EXTERNAL.open(encoding="utf-8",newline="") as handle:
        rows=list(csv.DictReader(handle))
    if not rows or not all(set(r)=={"premise","hypothesis","label"} for r in rows):
        raise AssertionError("External benchmark corrupted")
    if not all(r["label"] in ("entailment","contradiction","neutral") for r in rows):
        raise AssertionError("Unexpected external gold labels")
    apparent=0
    for item in rows:
        try:
            parsed=parse(item["hypothesis"],grammar)
        except Exception:
            continue
        if parsed["status"]=="PARSE_PROPOSAL_ONLY":
            apparent+=1
    return {
        "upstream":"FraCaS Consortium (1996), via independent MacCartney XML edition and Felsal MIT licensed NLI_datasets/dev.csv",
        "upstream_repo":"https://github.com/felipessalvatore/NLI_datasets",
        "upstream_commit":"9551b739a830fafb2ec4b98d49a9ecd4bf3dcbd0",
        "source_file_sha256":sha256(EXTERNAL.read_bytes()).hexdigest(),
        "independently_authored_nli_pairs":len(rows),
        "source_label_distribution":dict(sorted(Counter(x["label"] for x in rows).items())),
        "accidental_question_grammar_matches":apparent,
        "actual_nli_answers_issued":0,
        "nli_accuracy":None,
        "reason":"Native input requires an instrument evidence ledger, not premises/hypotheses. All independent NLI tasks remain HOLD.",
        "status":"HOLD_UNSUPPORTED_NLI_TASK",
    }


def run():
    grammar=learned()
    results=[]
    for case in all_cases():
        ledger=ledger_for(case)
        independent=inspect(ledger)
        if case["gold_kind"] is None:
            expected=None
        else:
            expected=reference_truth(ledger,case["gold_kind"])
        answer=examine(case["sentence"],ledger,grammar)
        if answer["status"] in ("RESEARCH_PROPOSAL_ONLY",
                                "HOLD_CONFLICTING_EVIDENCE"):
            pupil={"kind":answer["claim"]["kind"],"value":answer["answer"]}
            rote=pupil if answer["claim"]["seen_pair_in_teacher"] else None
        else:
            pupil=rote=None
        baseline_kind=parse_reference(case["sentence"],ledger["target"],
                                      ledger["indicator"])
        conventional=({"kind":baseline_kind,
                       "value":reference_truth(ledger,baseline_kind)}
                      if baseline_kind is not None else None)
        results.append({
            "id":case["id"],"group":case["split"],
            "gold_kind":case["gold_kind"],"gold_value":expected,
            "induced":pupil,"rote":rote,
            "classical":conventional,"always_hold":None,
            "induced_status":answer["status"],
            "ledger_state":independent["state"]})
    group={method:_metrics(results,method) for method in
           ("induced","rote","classical","always_hold")}
    return {
        "experiment":"MOTIF-LEGIT-006",
        "registered_cases":len(results),
        "registered_author_independent":False,
        "teacher_records":grammar["teacher_count"],
        "induced_rules":len(grammar["rules"]),
        "unseen_full_combinations":grammar["unseen_full_pairs"],
        "frozen_authored_cases_sha256":sha256(CASES.read_bytes()).hexdigest(),
        "methods":group,
        "cold_external_nli_boundary":external_ood_probe(grammar),
        "real_world_authority":False,
        "source_trust_cryptographically_verified":False,
        "no_live_actions":True,
        "status":"RESEARCH_HOLD",
        "cases":results,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
