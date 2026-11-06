"""Independent conventional regex reference (does not import grammar learner).

Hand-written rules are a deliberately strong classical baseline. It includes
two additional paraphrases absent from teacher examples, so classical may
rightfully outperform exact learned patterns out of distribution.
"""
from __future__ import annotations

import re

NEG="PROXY_NEGATIVE_IMPLIES_TARGET_ABSENT"
POS="PROXY_POSITIVE_IMPLIES_TARGET_PRESENT"

RULES=(
    (re.compile(r"^if ([a-z][a-z0-9 -]*?) is negative, must ([a-z][a-z0-9 -]*?) be absent\?$"),NEG),
    (re.compile(r"^does a negative reading of ([a-z][a-z0-9 -]*?) prove ([a-z][a-z0-9 -]*?) is absent\?$"),NEG),
    (re.compile(r"^if ([a-z][a-z0-9 -]*?) is positive, must ([a-z][a-z0-9 -]*?) be present\?$"),POS),
    (re.compile(r"^does a positive ([a-z][a-z0-9 -]*?) prove that ([a-z][a-z0-9 -]*?) exists\?$"),POS),
    (re.compile(r"^does failing to detect ([a-z][a-z0-9 -]*?) rule out ([a-z][a-z0-9 -]*?)\?$"),NEG),
    (re.compile(r"^will a positive ([a-z][a-z0-9 -]*?) establish ([a-z][a-z0-9 -]*?) presence\?$"),POS),
)

def parse_reference(question):
    if not isinstance(question,str):
        return None
    query=" ".join(question.lower().split())
    found=[]
    for regex,kind in RULES:
        match=regex.fullmatch(query)
        if match and match.group(1)!=match.group(2):
            found.append((match.group(1), match.group(2), kind))
    return found[0] if len(found)==1 else None
