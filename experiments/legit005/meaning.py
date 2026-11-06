"""MOTIF LEGIT-005 — meaning from *composed* teacher-corrected clauses.

This is a tiny, finite **classical** semantic grammar, not natural-language
comprehension. A teacher explicitly identifies the two phrases, their
surface spans, and one of FOUR declared logical query types. Cross-domain
phrases are abstracted into slot patterns, then combined in new pairs.

The semantic critic maps two surface questions to the same counterexample
predicate with opposite quantifier (entailment vs compatible possibility).
No hidden source labels, priors, live actions or LLMs enter inference.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import re

KINDS = ("U_NEG", "CAN_NEG", "U_POS", "CAN_POS")
SCHEMA = "motif.composed-meaning-grammar.v1"
FRAMES = {"U_NEG":"does", "CAN_NEG":"can",
          "U_POS":"does", "CAN_POS":"can"}
# Roles supplied in TEACHING only. At inference, neither slot nor kind exists.
ROLES = {"U_NEG":("proxy","target"), "CAN_NEG":("target","proxy"),
         "U_POS":("proxy","target"), "CAN_POS":("proxy","target")}
CAPTURE = r"([a-z][a-z0-9 -]{0,79}?)"
SLOT = re.compile(r"(\{proxy\}|\{target\})")
FORBIDDEN_CAPTURE = re.compile(r"\b(not|never|except|unless|despite|without|neither|nor|isnt|arent|cannot|can't|won't|no|that|is|are|was|were|present|absent|exists|exist|and|or)\b")
ACCEPTED = re.compile(r"^[a-z0-9 ,?.:'-]{1,400}$")


class HOLD(ValueError):
    pass


def normalize(raw):
    if not isinstance(raw,str):
        raise HOLD("Question text required")
    s=" ".join(raw.lower().split())
    if not ACCEPTED.fullmatch(s):
        raise HOLD("Unsupported alphabet or length")
    return s


def fingerprint(item):
    return sha256(json.dumps(item,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True).encode()).hexdigest()


def _abstract_piece(piece,span,label):
    piece=normalize(piece)
    span=normalize(span)
    # Strictly one complete token-boundary occurrence: no substring aliasing.
    hits=list(re.finditer(r"(?<![a-z0-9])"+re.escape(span)+r"(?![a-z0-9])",piece))
    if len(hits)!=1:
        raise HOLD("Training annotation not uniquely grounded in text")
    hit=hits[0]
    return piece[:hit.start()]+"{"+label+"}"+piece[hit.end():]


def _teacher(row):
    if not isinstance(row,dict) or set(row)!={
            "id","question","frame","left","right","proxy","target","meaning"}:
        raise HOLD("Teacher schema unknown")
    if (not isinstance(row["id"],str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,64}",row["id"])):
        raise HOLD("Unidentified training record")
    kind=row["meaning"]
    if kind not in KINDS or normalize(row["frame"])!=FRAMES[kind]:
        raise HOLD("Undefined semantic query kind or frame")
    left,right=normalize(row["left"]),normalize(row["right"])
    reconstructed=f'{FRAMES[kind]} {left} {right}?'
    if reconstructed!=normalize(row["question"]):
        raise HOLD("Teacher source text disagrees with marked phrases")
    first,second=ROLES[kind]
    l=_abstract_piece(left,row[first],first)
    r=_abstract_piece(right,row[second],second)
    if l==r or l.count("{")!=1 or r.count("{")!=1:
        raise HOLD("Invalid role abstraction")
    return kind,l,r,(normalize(row["proxy"]),normalize(row["target"]))


def learn(teacher):
    if not isinstance(teacher,list) or not 16<=len(teacher)<=100:
        raise HOLD("Insufficient contrasted teacher data")
    ids=set()
    by_kind=defaultdict(list)
    for row in teacher:
        if row.get("id") in ids:
            raise HOLD("Repeated teacher sample")
        ids.add(row.get("id"))
        kind,left,right,domains=_teacher(row)
        by_kind[kind].append((left,right,domains))
    if set(by_kind)!=set(KINDS):
        raise HOLD("Incomplete semantic contrast training")
    rules=[]
    for kind in KINDS:
        rows=by_kind[kind]
        if len(rows)<4:
            raise HOLD("Every semantic kind requires four source samples")
        left_items=defaultdict(set)
        right_items=defaultdict(set)
        seen_pairs=set()
        for l,r,domain in rows:
            left_items[l].add(domain)
            right_items[r].add(domain)
            seen_pairs.add((l,r))
        # At least two robust lexical realizations of each side, each
        # independently observed in at least two distinct domains.
        if len(left_items)<2 or len(right_items)<2:
            raise HOLD("No compositional variation between teacher phrases")
        if any(len(domains)<2 for domains in
               list(left_items.values())+list(right_items.values())):
            raise HOLD("Each phrase needs >=2 independent teacher domains")
        for l in sorted(left_items):
            for r in sorted(right_items):
                rules.append({"frame":FRAMES[kind], "kind":kind,
                              "left":l,"right":r,
                              "seen_pair_in_teacher":(l,r) in seen_pairs})
    return {"schema":SCHEMA,"status":"PROPOSAL_ONLY",
            "method":"COMPOSITIONAL_CLASSICAL_ANTI_UNIFICATION",
            "teacher_count":len(teacher),"teacher_digest":fingerprint(teacher),
            "rules":rules,
            "novel_combinations":sum(not x["seen_pair_in_teacher"] for x in rules),
            "source_authenticated":False,"real_world_authority":False}


def _pattern(frame,l,r):
    expression=frame+" "+l+" "+r+"?"
    components=SLOT.split(expression)
    regex=""
    order=[]
    for part in components:
        if part in ("{proxy}","{target}"):
            order.append(part[1:-1])
            regex+=CAPTURE
        else:
            regex+=re.escape(part)
    if sorted(order)!=["proxy","target"]:
        raise HOLD("Unreviewed or malformed learned pattern")
    return re.compile("^"+regex+"$"),order


def parse(question,grammar):
    if (not isinstance(grammar,dict) or grammar.get("schema")!=SCHEMA
            or grammar.get("status")!="PROPOSAL_ONLY"
            or not isinstance(grammar.get("rules"),list)):
        raise HOLD("Unknown rule source")
    source=normalize(question)
    matches=[]
    for rule in grammar["rules"]:
        if (not isinstance(rule,dict) or rule.get("kind") not in KINDS
                or rule.get("frame")!=FRAMES[rule["kind"]]):
            raise HOLD("Unknown rule semantics")
        pattern,order=_pattern(rule["frame"],rule["left"],rule["right"])
        m=pattern.fullmatch(source)
        if m is None:continue
        captures=dict(zip(order,m.groups()))
        if (captures["proxy"]==captures["target"]
                or any(FORBIDDEN_CAPTURE.search(value) for value in captures.values())):
            continue
        matches.append({"kind":rule["kind"],"proxy":captures["proxy"],
                        "target":captures["target"],
                        "seen_pair_in_teacher":rule["seen_pair_in_teacher"]})
    # If multiple reasonable interpretations arise, refuse to choose.
    if len(matches)!=1:
        return {"status":("HOLD_AMBIGUOUS_MEANING" if matches else
                          "HOLD_UNSUPPORTED_MEANING"),
                "matched_rules":len(matches),"real_world_authority":False}
    return dict(matches[0],status="PARSED_PROPOSAL_ONLY",
                matched_rules=1,real_world_authority=False)


def counterexample_truth(kind,proxy_is_positive,target_exists):
    """Truth table of a violation to the putative diagnostic implication.

    The same counterexample event is used for a universal-necessity question
    and for its converse question about whether a counterexample is possible.
    """
    if kind not in KINDS or type(proxy_is_positive) is not bool or type(target_exists) is not bool:
        raise HOLD("Unknown logical atoms")
    if kind in ("U_NEG","CAN_NEG"):
        return not proxy_is_positive and target_exists
    return proxy_is_positive and not target_exists


def complement_certificate():
    """Code-level truth-table witness: CAN_? is the existential challenge to U_?."""
    return {
        "negative":[{"proxy_positive":p,"target_present":t,
                     "counterexample":counterexample_truth("U_NEG",p,t),
                     "possibility_witness":counterexample_truth("CAN_NEG",p,t)}
                    for p in (False,True) for t in (False,True)],
        "positive":[{"proxy_positive":p,"target_present":t,
                     "counterexample":counterexample_truth("U_POS",p,t),
                     "possibility_witness":counterexample_truth("CAN_POS",p,t)}
                    for p in (False,True) for t in (False,True)]}
