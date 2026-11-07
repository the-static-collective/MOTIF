"""RING-009: synthesize NEW TYPED RELATIONAL OPERATOR INSTANCES from contrasts.

No hand-coded 'please', 'what if', 'send', 'relay' or semantic template
phrases occur in this learner. It only sees paired (utterance, typed meaning)
samples and discovers shared action spans and DISTINCTIVE context cues.

1. Anti-unify each opposite-speech-act minimal pair to discover the longest
   contiguous SHARED EVENT SPAN (pivot); no source pivot positions supplied.
2. Treat the differing token contexts before/after that event as candidate
   cue-RELATION expressions.
3. Accumulate and contrast mode support for cue rules; automatically create
   new data-only executable relational operator ASTs at training time.
4. At inference, require a seen action-anchor and a discriminating ordered
   context cue. Ambiguity or no anchored evidence -> HOLD, never take action.

The opcode family (MATCH_CUE_BEFORE/AFTER_PIVOT) and its runtime are written
by the developer. Invented operator INSTANCES are learned, NOT fundamentally
new computational primitives. The model is not allowed external authority.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from hashlib import sha256
import json
import re
from pathlib import Path
import sys

import contrasts
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cartridge-ring-008"))
import engine

SCHEMA="motif.ring009.discovered-relational-operator-program.v1"
MAX_RULES=200
OPCODES=("CUE_PRECEDES_SHARED_EVENT","CUE_FOLLOWS_SHARED_EVENT")

class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def tokens(text):
    if type(text) is not str or not 1<=len(text)<=320:
        raise HOLD("Invalid phrase")
    return re.findall(r"[a-z]+",text.casefold())


def common_span(a,b):
    """Exact longest contiguous shared span, with deterministic tie break."""
    a,b=tokens(a),tokens(b)
    best=(0,0,0)
    # Explicit O(n²)-bounded comparison, inputs <= 320 chars.
    for i in range(len(a)):
        for j in range(len(b)):
            z=0
            while i+z<len(a) and j+z<len(b) and a[i+z]==b[j+z]:
                z+=1
            if z>best[0] or z==best[0] and (i,j)<(best[1],best[2]):
                best=z,i,j
    length,i,j=best
    return {
        "common_tokens":a[i:i+length],
        "arm_a_before":a[:i],"arm_a_after":a[i+length:],
        "arm_b_before":b[:j],"arm_b_after":b[j+length:],
    }


def ngrams(seq,max_n):
    out=set()
    for length in range(1,min(max_n,len(seq))+1):
        for i in range(len(seq)-length+1):
            out.add(tuple(seq[i:i+length]))
    return out


def construct(train,*,min_support=3,max_cue_tokens=3,max_gap=9,
              min_purity=0.96):
    contrasts.check(train,split="train")
    if (type(min_support) is not int or not 1<=min_support<=20
            or type(max_cue_tokens) is not int or not 1<=max_cue_tokens<=4
            or type(max_gap) is not int or not 0<=max_gap<=16
            or type(min_purity) is not float or min_purity not in (0.75,0.9,0.96,1.0)):
        raise HOLD("Invalid synthesis grammar/configuration")
    supports=Counter()
    anchor_roles=defaultdict(Counter)
    comparable=0
    evidence_hashes=[]
    for pair in train["pairs"]:
        a,b=pair["a"],pair["b"]
        found=common_span(a["text"],b["text"])
        shared=found["common_tokens"]
        if len(shared)<2:
            continue
        comparable+=1
        # The event's first token is INFERRED from the pair overlap;
        # lexicon is learned rather than compiled from template constants.
        anchor=shared[0]
        role=(a["frame"]["topic"],a["frame"]["operator"])
        anchor_roles[anchor][role]+=1
        evidence_hashes.append(digest({"a":a,"b":b,"pivot":shared}))
        for arm,mode in (("a","ACT"),("b","META")):
            other="b" if arm=="a" else "a"
            for region,relation in (("before",OPCODES[0]),("after",OPCODES[1])):
                context=found["arm_"+arm+"_"+region]
                opposite=found["arm_"+other+"_"+region]
                distinct=ngrams(context,max_cue_tokens)-ngrams(opposite,max_cue_tokens)
                for cue in distinct:
                    supports[(relation,cue,mode)]+=1
    if comparable<5:
        raise HOLD("Insufficient comparable minimal pairs")
    # Aggregate *all* observed evidence and create operator ASTs with
    # learned cue phrases. Never use the forbidden template identity.
    rules=[]
    for (relation,cue,mode),support in sorted(supports.items()):
        opposite="META" if mode=="ACT" else "ACT"
        conflicting=supports.get((relation,cue,opposite),0)
        purity=support/max(1,support+conflicting)
        if support<min_support or purity<min_purity:
            continue
        rules.append({
            "opcode":relation,
            "cue":list(cue),
            "inferred_speech_act":mode,
            "contrast_support":support,
            "opposing_mode_support":conflicting,
            "purity_on_training_pairs":round(purity,6),
            "derived_from":"ANTI_UNIFICATION_OF_OPPOSITE_LABELS",
        })
    # Prune to highest-support data rules, deterministically. This is a
    # learned lexicon/relational program, not hand-curated hardcoded phrases.
    rules.sort(key=lambda x:(-x["contrast_support"],-len(x["cue"]),
                              x["opcode"],x["cue"],x["inferred_speech_act"]))
    rules=rules[:MAX_RULES]
    anchors={}
    for anchor,roles in sorted(anchor_roles.items()):
        winner,frequency=roles.most_common(1)[0]
        if len(roles)>1 and frequency!=sum(roles.values()):
            continue
        anchors[anchor]={
            "topic":winner[0],"operator":winner[1],
            "support":frequency,
        }
    if not rules or not anchors:
        raise HOLD("No operators could be learned from the source contrasts")
    ast={
        "schema":SCHEMA,
        "source_training_sha256":train["receipt_sha256"],
        "opcodes_implemented_by_developer":list(OPCODES),
        "operator_instances_induced_from_examples":len(rules),
        "source_minimal_pairs":len(train["pairs"]),
        "comparable_pairs":comparable,
        "antiunification_witness_sha256":digest(evidence_hashes),
        "semantic_anchors_inferred_from_overlapping_utterances":anchors,
        "discovered_relational_operators":rules,
        "parameters":{"min_support":min_support,
                      "max_cue_tokens":max_cue_tokens,
                      "max_gap":max_gap,
                      "min_purity":min_purity},
        "label_names_are_training_supervision_not_effect_authorization":True,
        "full_natural_language_understanding_claimed":False,
        "no_new_python_opcodes_generated":True,
        "execution_authority":"NONE",
    }
    ast["receipt_sha256"]=digest(ast)
    return ast


def validate(ast):
    if (not isinstance(ast,dict) or ast.get("schema")!=SCHEMA
            or ast.get("execution_authority")!="NONE"
            or ast.get("no_new_python_opcodes_generated") is not True
            or ast.get("full_natural_language_understanding_claimed") is not False
            or ast.get("opcodes_implemented_by_developer")!=list(OPCODES)
            or ast.get("operator_instances_induced_from_examples")!=len(
                ast.get("discovered_relational_operators",[]))
            or not 1<=len(ast["discovered_relational_operators"])<=MAX_RULES
            or not isinstance(ast.get("semantic_anchors_inferred_from_overlapping_utterances"),dict)
            or ast.get("receipt_sha256")!=digest({
                k:v for k,v in ast.items() if k!="receipt_sha256"})):
        raise HOLD("Unreviewed or changed relational operator program")
    params=ast.get("parameters")
    if not isinstance(params,dict) or set(params)!={"min_support","max_cue_tokens","max_gap","min_purity"}:
        raise HOLD("Missing source program grammar")
    for rule in ast["discovered_relational_operators"]:
        if (rule.get("opcode") not in OPCODES
                or rule.get("inferred_speech_act") not in ("ACT","META")
                or not isinstance(rule.get("cue"),list)
                or not 1<=len(rule["cue"])<=params["max_cue_tokens"]
                or any(type(x) is not str or not re.fullmatch("[a-z]+",x)
                       for x in rule["cue"])
                or type(rule.get("contrast_support")) is not int
                or rule["contrast_support"]<params["min_support"]):
            raise HOLD("Forbidden synthesized relational opcode")
    for action,role in ast["semantic_anchors_inferred_from_overlapping_utterances"].items():
        if (type(action) is not str or not re.fullmatch("[a-z]+",action)
                or role.get("topic") not in ("RECORD","SCHEDULE")
                or role.get("operator") not in ("TRANSFER","MODIFY")
                or type(role.get("support")) is not int):
            raise HOLD("Malformed learned relational anchor")
    return ast


def match_cue(words,cue,start,end,opcode,max_gap):
    n=len(cue)
    for i in range(len(words)-n+1):
        if words[i:i+n]!=cue:
            continue
        if opcode=="CUE_PRECEDES_SHARED_EVENT":
            distance=start-(i+n)
        else:
            distance=i-end
        if 0<=distance<=max_gap:
            return True
    return False


def parse(ast,text):
    validate(ast)
    words=tokens(text)
    anchors=ast["semantic_anchors_inferred_from_overlapping_utterances"]
    matches=[]
    for i,word in enumerate(words):
        role=anchors.get(word)
        if role is None:
            continue
        for rule in ast["discovered_relational_operators"]:
            if match_cue(words,rule["cue"],i,i+1,rule["opcode"],
                         ast["parameters"]["max_gap"]):
                matches.append((rule,role))
    modes={rule["inferred_speech_act"] for rule,role in matches}
    roles={(role["topic"],role["operator"]) for rule,role in matches}
    if len(modes)!=1 or len(roles)!=1:
        return {"status":"HOLD","frame":None,
                "reason":"NO_UNAMBIGUOUS_CONTRASTIVELY_GROUNDED_RELATION",
                "matching_rule_instances":len(matches),
                "raw_text_sha256":sha256(text.encode()).hexdigest()}
    mode=next(iter(modes))
    topic,operator=next(iter(roles))
    return {"status":"NONAUTHORITATIVE_FRAME_HYPOTHESIS",
            "frame":{"mode":mode,"topic":topic,"operator":operator},
            "reason":"GENERATED_ORDERED_CUE_SHARED_EVENT_RELATION",
            "matching_rule_instances":len(matches),
            "raw_text_sha256":sha256(text.encode()).hexdigest(),
            "execution_authority":"NONE"}
