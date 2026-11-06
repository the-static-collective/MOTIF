"""POSTHOC source-ambiguity audit for independently authored bAbI questions.

This reviewer is separate from the answer engine. It may read gold/source
support annotations AFTER a heldout evaluation. A benchmark question may
provide one official answer while its passage explicitly supports two
different answers. This doesn't prove which answer the original task author
intended; it shows why a model should not pretend the evidence is unique.

Do NOT pass this audit's gold label or support metadata into model inference.
Inspecting these cases means they are not blind for any future modifications.
"""
from __future__ import annotations

from corpus import query_input
from engines import GIVE,solve
import re


def transfer_source_audit(examples):
    findings=[]
    for ordinal,q in enumerate(examples,1):
        request=query_input(q)
        prediction=solve("TRIADIC_TRANSFER",request)
        if prediction["status"]!="ANSWER" or prediction["answer"]==q.answer:
            continue
        query=re.fullmatch(r"What did ([A-Z][a-z]+) give to ([A-Z][a-z]+)\?",
                           q.question)
        if query is None:continue
        giver,receiver=query.groups()
        alternatives={}
        for number,text in q.facts:
            row=GIVE.fullmatch(text)
            if row and row.group(1)==giver and row.group(3)==receiver:
                alternatives.setdefault(row.group(2),[]).append({
                    "original_source_line":number,"original_source_text":text,
                })
        if q.answer in alternatives and prediction["answer"] in alternatives:
            findings.append({
                "source_id":q.id,
                "source_case_ordinal_within_reserved_slice":ordinal,
                "question":q.question,
                "official_dataset_gold":q.answer,
                "model_latest_matching_transfer":prediction["answer"],
                "official_supporting_line_ids_for_scoring":list(q.supporting_ids),
                "all_source_supported_distinct_answer_options":dict(
                    sorted(alternatives.items())),
                "posthoc_finding":"MULTIPLE_EXPLICITLY_SUPPORTED_ANSWERS",
                "scorer_marks_model_wrong_even_though_a_source_line_supports_it":True,
                "model_was_overconfident_about_a_non_unique_answer":True,
                "source_is_external_babi_not_a_real_person":True,
                "gold_used_only_in_posthoc_audit_not_in_engine":True,
            })
    return findings
