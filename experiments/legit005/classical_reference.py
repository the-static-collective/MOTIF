"""LEGIT-005 conventional classical comparator.

Independently coded, hand-built compositional regex rules plus selected
unseen paraphrases. This reference does not import the learner, training
examples or its compiled rules, and is intentionally a *stronger* baseline.
It is not a separate human evaluator or independent research team.
"""
from __future__ import annotations

import re

KINDS={
    "U_NEG":("does",("missing {proxy}","no {proxy}"),
             ("rule out {target}","establish that {target} is absent")),
    "CAN_NEG":("can",("{target} exist","{target} be present"),
               ("without {proxy}","despite missing {proxy}")),
    "U_POS":("does",("detecting {proxy}","a positive {proxy}"),
             ("guarantee {target}","establish that {target} is present")),
    "CAN_POS":("can",("{proxy} appear","{proxy} be detected"),
               ("without {target}","when {target} is absent")),
}

EXTRAS={
    "U_NEG":["does an undetected {proxy} establish that {target} is absent"],
    "CAN_NEG":["could {target} still be present with no {proxy}"],
}
SLOT=re.compile(r"(\{proxy\}|\{target\})")
UNSAFE=re.compile(r"\\b(not|never|except|unless|despite|without|neither|nor|isnt|arent|cannot|can't|won't|no|that|is|are|was|were|present|absent|exists|exist|and|or)\\b")


def _render(template):
    chunks=SLOT.split(template)
    fields=[]
    result=""
    for chunk in chunks:
        if chunk in ("{proxy}","{target}"):
            fields.append(chunk[1:-1])
            result+=r"([a-z][a-z0-9 -]{0,79}?)"
        else:
            result+=re.escape(chunk)
    return re.compile("^"+result+r"\?$"),fields


def parse_classical(question,indicator):
    if not isinstance(question,str) or not isinstance(indicator,str):
        return None
    q=" ".join(question.lower().split())
    indicator=" ".join(indicator.lower().split())
    if not 1<=len(q)<=400:
        return None
    matches=[]
    for kind,(frame,left,right) in KINDS.items():
        templates=[f"{frame} {a} {b}" for a in left for b in right]
        templates+=EXTRAS.get(kind,[])
        for template in templates:
            regex,roles=_render(template)
            m=regex.fullmatch(q)
            if m is None:
                continue
            attrs=dict(zip(roles,m.groups()))
            if (attrs.get("proxy")!=indicator or
                    attrs.get("proxy")==attrs.get("target") or
                    any(UNSAFE.search(v) for v in attrs.values())):
                continue
            matches.append({"kind":kind,**attrs})
    return matches[0] if len(matches)==1 else None
