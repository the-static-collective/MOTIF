"""LEGIT-004: learn tiny question surface grammars from contrasted corrections.

No pretrained language model; no paper reading; no arbitrary NLP. This is
source-bounded structural anti-unification of teacher-labeled examples:
replace two known spans (observed proxy, hidden target) and learn reusable
connective tokens. At inference, ONLY text is supplied for the question;
concept spans and claim direction are reconstructed by the learned patterns.

Out-of-grammar, negation, ambiguity or conflicting rules -> HOLD.
The set of possible logical claim *kinds* is developer-declared.
"""
from __future__ import annotations

import hashlib
import json
import re

SCHEMA = "motif.question-grammar.v1"
KINDS = frozenset(("PROXY_NEGATIVE_IMPLIES_TARGET_ABSENT",
                   "PROXY_POSITIVE_IMPLIES_TARGET_PRESENT"))
MAX_TEXT = 400
SLOT = re.compile(r"(\{proxy\}|\{target\})")
CAPTURE = r"([a-z][a-z0-9 -]{0,78}?)"


class HOLD(ValueError):
    pass


def normalized(value):
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT:
        raise HOLD("Missing or oversized source text")
    lower = " ".join(value.lower().strip().split())
    if (not lower.isascii() or any(c in lower for c in "{}[]\\") or
            re.search(r"[^a-z0-9 ,?.:'-]", lower)):
        raise HOLD("Unknown text alphabet or structural delimiter")
    return lower


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,
                          separators=(",",":"),ensure_ascii=True).encode()).hexdigest()


def abstraction(example):
    if not isinstance(example,dict) or set(example) != {
            "id", "question", "proxy", "target", "kind"}:
        raise HOLD("Invalid teacher record")
    if (not isinstance(example["id"], str) or
            not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", example["id"]) or
            example["kind"] not in KINDS):
        raise HOLD("Unknown teacher provenance or unsupported logical kind")
    text = normalized(example["question"])
    proxy = normalized(example["proxy"])
    target = normalized(example["target"])
    if not (1 <= len(proxy) <= 80 and 1 <= len(target) <= 80):
        raise HOLD("Teacher anchors too large")
    if proxy == target or text.count(proxy) != 1 or text.count(target) != 1:
        raise HOLD("Ambiguous teacher source anchors")
    a,b = text.index(proxy), text.index(target)
    if max(a,b) < min(a+len(proxy), b+len(target)):
        raise HOLD("Overlapping teacher source anchors")
    marks = sorted(((a,a+len(proxy),"{proxy}"),(b,b+len(target),"{target}")))
    pattern = ""
    cursor = 0
    for begin,end,symbol in marks:
        pattern += text[cursor:begin] + symbol
        cursor = end
    pattern += text[cursor:]
    if len(pattern) > 300 or pattern.count("{proxy}") != 1 or pattern.count("{target}") != 1:
        raise HOLD("Unusable learned grammar")
    return pattern


def learn(examples):
    """Induce patterns from two contrasting source worlds per grammar.

    The teacher supplies spans and logical kind during *training* only.
    New domain instances supply only an unannotated question plus a
    source-owned numeric observation table for proof construction.
    """
    if not isinstance(examples, list) or not 4 <= len(examples) <= 100:
        raise HOLD("Insufficient bounded teacher examples")
    seen = set()
    grouped = {}
    for row in examples:
        if not isinstance(row,dict) or row.get("id") in seen:
            raise HOLD("Repeated teacher example")
        seen.add(row["id"])
        pattern = abstraction(row)
        key = (pattern,row["kind"])
        grouped.setdefault(key,[]).append((normalized(row["proxy"]),
                                            normalized(row["target"])))
    patterns = {}
    for (pattern,kind), anchors in grouped.items():
        if (len(anchors) < 2 or len(set(x[0] for x in anchors)) < 2
                or len(set(x[1] for x in anchors)) < 2):
            raise HOLD("Template lacks cross-domain contrasting examples")
        if pattern in patterns and patterns[pattern] != kind:
            raise HOLD("Same surface implies contradictory logic")
        patterns[pattern] = kind
    if not patterns:
        raise HOLD("No fully demonstrated rules")
    rules = [{"template":x,"kind":k,"teacher_examples":len(grouped[(x,k)])}
             for x,k in sorted(patterns.items())]
    return {"schema":SCHEMA,"status":"PROPOSAL_ONLY","rules":rules,
            "teacher_count":len(examples),"teacher_digest":digest(examples),
            "executable_action_authority":False,
            "method":"CLASSICAL_TEMPLATE_ANTI_UNIFICATION"}


def _regexp(template):
    parts=SLOT.split(template)
    if parts.count("{proxy}") != 1 or parts.count("{target}") != 1:
        raise HOLD("Unrecognized training rule")
    pieces=[]
    order=[]
    for part in parts:
        if part in ("{proxy}","{target}"):
            pieces.append(CAPTURE)
            order.append(part[1:-1])
        else:
            pieces.append(re.escape(part))
    return re.compile(r"^"+"".join(pieces)+r"$"),order


def parse(question, grammar):
    """Return a proposal, never a forced choice of hidden semantics."""
    if not isinstance(grammar,dict) or grammar.get("schema") != SCHEMA or grammar.get("status") != "PROPOSAL_ONLY":
        raise HOLD("Unreviewed grammar")
    text=normalized(question)
    matches=[]
    for rule in grammar.get("rules",[]):
        if not isinstance(rule,dict) or rule.get("kind") not in KINDS:
            raise HOLD("Invalid rule semantics")
        regex,order = _regexp(rule.get("template",""))
        candidate=regex.fullmatch(text)
        if candidate is None:
            continue
        capture=dict(zip(order,candidate.groups()))
        if (not capture["proxy"] or not capture["target"]
                or capture["proxy"] == capture["target"]):
            continue
        matches.append({"kind":rule["kind"],"proxy":capture["proxy"],
                        "target":capture["target"],"teacher_template":rule["template"]})
    if len(matches)!=1:
        return {"status":"HOLD_AMBIGUOUS_GRAMMAR" if matches else "HOLD_UNKNOWN_GRAMMAR",
                "kind":None,"proxy":None,"target":None,
                "matched_rules":len(matches),"real_world_authority":False}
    match=matches[0]
    return dict(match, status="PARSE_PROPOSAL_ONLY",matched_rules=1,
                real_world_authority=False)
