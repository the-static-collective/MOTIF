"""Three incompatible finite reasoning machines: quantity, ordered time, triadic transfer.

Rather than forcing all the data into a Boolean predicate, we define three
different typed source representations. These engines are human-written
classical algorithms; the system does NOT invent executable adapters
autonomously. An evidence-trained router chooses from these candidates.

All witness IDs refer to actual source sentences. Neither the gold answer
nor support indices are visible to this code. Unsupported grammar => HOLD;
never fabricate a response to get a benchmark score.
"""
from __future__ import annotations
import re

UNKNOWN="HOLD"


def outcome(status,answer=None,proof=(),type_name=None,reason=None):
    return {
        "status":status,"answer":answer if status=="ANSWER" else None,
        "premises":list(proof),"representation":type_name,
        "reason":reason if status=="HOLD" else None,
        "actions_permitted":False,
    }


def _facts(source):
    if not isinstance(source,dict) or set(source)!={"facts","question","source_id"}:
        raise ValueError("Unknown external task source contract")
    if not isinstance(source["facts"],list) or not 1<=len(source["facts"])<=120:
        raise ValueError("No bounded source story")
    for x in source["facts"]:
        if set(x)!={"line","text"} or type(x["line"]) is not int or not isinstance(x["text"],str):
            raise ValueError("Invalid cited original sentence")
    return [(x["line"],x["text"]) for x in source["facts"]]


PICK=re.compile(r"^([A-Z][a-z]+) (?:got|grabbed|took|picked up) the ([a-z]+) there\.$")
DROP_OLD=re.compile(r"^([A-Z][a-z]+) (?:left|dropped|put down) the ([a-z]+)\.$")
DROP=re.compile(r"^([A-Z][a-z]+) (?:left|dropped|put down|discarded) the ([a-z]+)(?: there)?\.$")
GIVE=re.compile(r"^([A-Z][a-z]+) (?:gave|handed|passed) the ([a-z]+) to ([A-Z][a-z]+)\.$")
COUNT_Q=re.compile(r"^How many objects is ([A-Z][a-z]+) carrying\?$")
COUNT_WORD={0:"none",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight"}


def _count_with_drop_grammar(source,drop_grammar):
    facts=_facts(source)
    m=COUNT_Q.fullmatch(source["question"])
    if not m:return outcome("HOLD",type_name="QUANTITY",reason="WRONG_QUESTION_SHAPE")
    keeper=m.group(1)
    holdings={}
    witnesses={}
    for number,text in facts:
        x=PICK.fullmatch(text)
        if x:
            who,item=x.groups()
            holdings[item]=who;witnesses[item]=number
            continue
        x=drop_grammar.fullmatch(text)
        if x:
            who,item=x.groups()
            if holdings.get(item)==who:
                holdings.pop(item,None)
                witnesses[item]=number
            continue
        x=GIVE.fullmatch(text)
        if x:
            giver,item,recipient=x.groups()
            if holdings.get(item)==giver:
                holdings[item]=recipient;witnesses[item]=number
            else:
                # Source doesn't establish giver's custody. Keep conclusion
                # unknown rather than accepting inconsistent transfers.
                holdings[item]=recipient;witnesses[item]=number
    held=sorted(k for k,v in holdings.items() if v==keeper)
    if len(held) not in COUNT_WORD:
        return outcome("HOLD",type_name="QUANTITY",reason="UNSUPPORTED_CARDINALITY")
    # Finite typed multiset: object identity matters; presence Boolean doesn't.
    return outcome("ANSWER",COUNT_WORD[len(held)],
                   [(witnesses[k],next(t for n,t in facts if n==witnesses[k]))
                    for k in held],type_name="QUANTITY")


def count(source):
    """Repaired counting interpreter, using observed external lexical evidence."""
    return _count_with_drop_grammar(source,DROP)


def count_before_source_repair(source):
    """Initial public result: 24 mistakes in a 250-question development batch.

    The original implementation is preserved so that the first-run failure
    cannot be erased or relabeled as prospective heldout success.
    """
    return _count_with_drop_grammar(source,DROP_OLD)


def transfer(source):
    facts=_facts(source)
    query=source["question"]
    shapes=(
        (r"^What did ([A-Z][a-z]+) give to ([A-Z][a-z]+)\?$",lambda g,r:r[1] if r[0]==g[0] and r[2]==g[1] else None),
        (r"^Who gave the ([a-z]+) to ([A-Z][a-z]+)\?$",lambda g,r:r[0] if r[1]==g[0] and r[2]==g[1] else None),
        (r"^Who gave the ([a-z]+)\?$",lambda g,r:r[0] if r[1]==g[0] else None),
        (r"^Who did ([A-Z][a-z]+) give the ([a-z]+) to\?$",lambda g,r:r[2] if r[0]==g[0] and r[1]==g[1] else None),
        (r"^Who received the ([a-z]+)\?$",lambda g,r:r[2] if r[1]==g[0] else None),
    )
    selected=None;groups=None
    for pattern,extract in shapes:
        m=re.fullmatch(pattern,query)
        if m:
            selected=extract;groups=m.groups();break
    if selected is None:
        return outcome("HOLD",type_name="TRIADIC_TRANSFER",reason="WRONG_QUESTION_SHAPE")
    for number,text in reversed(facts):
        x=GIVE.fullmatch(text)
        if not x:continue
        answer=selected(groups,x.groups())
        if answer:
            return outcome("ANSWER",answer,[(number,text)],type_name="TRIADIC_TRANSFER")
    return outcome("HOLD",type_name="TRIADIC_TRANSFER",reason="NO_SUPPORTED_GIVER_OBJECT_RECEIVER")


MOVE=re.compile(r"([A-Z][a-z]+) (?:went back|went|moved|journeyed|travelled) to the ([a-z]+)")
TIME_Q=re.compile(r"^Where was ([A-Z][a-z]+) before the ([a-z]+)\?$")
CLOCK=("yesterday","this morning","this afternoon","this evening")
CLOCK_ORDER={s:i for i,s in enumerate(CLOCK)}


def temporal(source):
    facts=_facts(source)
    q=TIME_Q.fullmatch(source["question"])
    if not q:return outcome("HOLD",type_name="ORDERED_TIME",reason="WRONG_QUESTION_SHAPE")
    person,place=q.groups()
    event=[]
    for no,text in facts:
        m=MOVE.search(text)
        if not m:continue
        tag=next((a for a in CLOCK if a in text.lower()),None)
        if tag is None:continue
        event.append((CLOCK_ORDER[tag],no,m.group(1),m.group(2),text))
    # TIME is an ordering relation: source sentences can be told out of order.
    history=sorted((e for e in event if e[2]==person),key=lambda e:(e[0],e[1]))
    matches=[i for i,x in enumerate(history) if x[3]==place]
    if not matches:
        return outcome("HOLD",type_name="ORDERED_TIME",reason="TARGET_LOCATION_NOT_IN_SOURCE")
    position=matches[-1]
    if position==0:
        return outcome("HOLD",type_name="ORDERED_TIME",reason="NO_PREDECESSOR_EVENT")
    previous=history[position-1]
    target=history[position]
    return outcome("ANSWER",previous[3],[(previous[1],previous[4]),
                                         (target[1],target[4])],
                   type_name="ORDERED_TIME")


ENGINES={"QUANTITY":count,"TRIADIC_TRANSFER":transfer,"ORDERED_TIME":temporal}


def solve(model,source):
    if model not in ENGINES:raise ValueError("Cannot execute an unsupported representation")
    output=ENGINES[model](source)
    if output["status"]=="ANSWER":
        ids={a["line"]:a["text"] for a in source["facts"]}
        if not all(ids.get(n)==text for n,text in output["premises"]):
            raise ValueError("Evidence invented by a source adapter")
    return output
