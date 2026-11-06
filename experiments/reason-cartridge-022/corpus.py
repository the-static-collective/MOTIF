"""Parse independent, source-authored bAbI question data WITHOUT answer leakage.

Split original episodes at line 1; each question sees only prior facts in
its story. The gold answer and support indices remain evaluator-only data,
never supplied to the candidate typed engines or routing decision.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Question:
    family:str
    split:str
    id:str
    facts:tuple
    question:str
    answer:str
    supporting_ids:tuple


def read(path,family,split,limit=None,skip=0):
    if family not in ("TIME","COUNT","TRANSFER") or split not in ("train","test"):
        raise ValueError("Unknown independent dataset task family")
    lines=Path(path).read_text(encoding="utf8").splitlines()
    episode=0
    facts=[]
    questions=[]
    seen_questions=0
    for line in lines:
        m=re.fullmatch(r"(\d+)\s+(.+)",line)
        if not m:raise ValueError("Not a standard numbered bAbI episode")
        no=int(m.group(1));body=m.group(2)
        if no==1:
            episode+=1;facts=[]
        if "\t" in body:
            fragments=body.split("\t")
            if len(fragments)!=3:raise ValueError("Noncanonical bAbI answer/support annotation")
            q,answer,support=fragments
            if "?" not in q:raise ValueError("Unrecognized question row")
            seen_questions+=1
            if seen_questions<=skip:
                continue
            questions.append(Question(
                family=family,split=split,id=f"{family}-{split}-{episode}-{no}",
                facts=tuple(facts),question=q.strip(),
                answer=answer.strip(),supporting_ids=tuple(
                    int(x) for x in support.strip().split() if x)))
        else:
            facts.append((no,body.strip()))
        if limit is not None and len(questions)>=limit:break
    if not questions:raise ValueError("Empty third-party dataset or out-of-range slice")
    return tuple(questions)


def query_input(q):
    # The solver receives precisely this information: never gold answer,
    # source-supplied support indices, known family or split labels.
    return {
        "facts":[{"line":no,"text":line} for no,line in q.facts],
        "question":q.question,
        "source_id":q.id,
    }
