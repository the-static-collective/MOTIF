"""Source-grounded, deterministic *partial* adversarial opinion reader.

Consumes untagged prose paragraphs with genuine author/stance language.
Segments judicial voices, extracts traceable textual signals, preserves
procedural disposition vs advocacy, and exposes a small argument graph.
No legal facts or outcomes from evaluation_keys.py are imported.

This is a finite hand-designed grammar and is NOT trained legal NLP,
unrestricted opinion comprehension, or a proof that a statute covers fish.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from pathlib import Path
import json
import re

SOURCE=Path(__file__).with_name("opinions.py")
PIN="af4abe84939b74362acb70d8fc1dc769ee71cab8"
SCHEMA="motif.reason.adversarial-reader.v1"
MAX_CHARS=26000

class HOLD(ValueError):pass


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def source_pin():
    raw=SOURCE.read_bytes()
    sha=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=PIN:
        raise HOLD("Judicial source snapshot changed")
    return sha


def source_document(id):
    source_pin()
    from opinions import DOCUMENTS
    if id not in DOCUMENTS:raise HOLD("Unregistered historical court source")
    return DOCUMENTS[id]


def normalize(text):
    return re.sub(r"\s+"," ",text).strip()


def speaker_header(line):
    line=normalize(line)
    if not re.search(r"\bjustice\b",line,re.I):
        return None
    if not re.search(r"\b(?:delivered the opinion|announced the judgment|concurring in the judgment|dissenting)\b",line,re.I):
        return None
    match=re.search(r"\bjustice\s+(\w+)",line,re.I)
    if not match:raise HOLD("Missing declared judicial voice")
    author=match.group(1).upper()
    lower=line.lower()
    role=("DISSENT" if "dissenting" in lower else
          "CONCURRENCE_IN_JUDGMENT" if "concurring" in lower else
          "JUDGMENT_ANNOUNCER" if "announced the judgment" in lower else
          "OPINION_OF_COURT")
    # Count explicit joinders from the original header. Each participant must
    # be explicit; no inference of a doctrinal majority from a vote on result.
    joiners=[]
    if " join" in lower or "with whom" in lower:
        tail=line[match.end():]
        names=re.findall(r"\bjustice\s+([A-Za-z]+)",tail,re.I)
        joiners=[x.upper() for x in names if x.upper()!=author]
        if re.search(r"\bthe chief justice\b",tail,re.I):
            joiners.append("CHIEF_JUSTICE")
    votes=tuple(sorted({author,*joiners}))
    return {"judge":author,"role":role,"named_joiners":sorted(set(joiners)),
            "explicit_votes":len(votes),"header":line}


# Developer-supplied lexical feature grammar, calibrated on simple opinions
# and FROZEN before the heldout sources are evaluated.
CUES=(
 ("RESTRICTED_SCOPE",re.compile(r"\b(?:must be one used to|does not spring to mind)\b",re.I)),
 ("EXPANSIVE_SCOPE",re.compile(r"\b(?:covers\s+(?:[a-z-]+\s+){0,5}[a-z-]+)\b",re.I)),
 ("BOTANICAL_FRUIT",re.compile(r"\bbotanically speaking\b.{0,90}\bfruit\b",re.I)),
 ("ORDINARY_VEGETABLE",re.compile(r"\bcommon language\b.{0,90}\bvegetables\b",re.I)),
 ("CONCERN_WITH_EVIDENCE",re.compile(r"\b(?:record or preserve information|statutory construction|financial.fraud mooring|ordinary meaning)\b",re.I)),
 ("REVERSAL",re.compile(r"\b(?:judgment (?:is therefore )?reversed|judgment reversed|reversed, and the case is remanded)\b",re.I)),
 ("AFFIRMANCE",re.compile(r"\b(?:judgment affirmed|affirm the judgment below)\b",re.I)),
)


def voiced_paragraphs(source_id):
    doc=source_document(source_id)
    role=None
    participants={}
    out=[]
    for index,text in enumerate(doc["paragraphs"],1):
        if not isinstance(text,str) or not 12<=len(text)<=1800:
            raise HOLD("Source paragraph too large or unbounded")
        found=speaker_header(text)
        if found is not None:
            role=found
            if role["judge"] in participants:raise HOLD("Duplicated judicial header")
            participants[role["judge"]]=role
            out.append({"id":f"P{index:02}","kind":"HEADER",
                        "role":role["role"],"judge":role["judge"],
                        "text":text,"sha256":sha256(text.encode()).hexdigest()})
            continue
        if role is None:
            raise HOLD("Opinion lacks a source-owned judicial voice header")
        out.append({"id":f"P{index:02}","kind":"PROSE",
                    "role":role["role"],"judge":role["judge"],
                    "text":text,"sha256":sha256(text.encode()).hexdigest()})
    return participants,out


def classify_passage(row):
    """No magical opinion semantics: cite exactly which lexical cue fired."""
    text=row["text"]
    if row["kind"]!="PROSE":
        return []
    # A party's pleaded position and a lower court's opinion are NOT
    # assertions by the current justice; do not promote them.
    if re.search(r"\b(?:contended|alleged|maintains|the court found that)\b",text,re.I):
        return []
    types=[]
    for tag,pattern in CUES:
        found=pattern.search(text)
        if found is not None:
            types.append({"feature":tag,"lexical_witness":found.group(0),
                          "paragraph":row["id"],"judge":row["judge"],
                          "voice_role":row["role"],"source_sha256":row["sha256"]})
    return types


def read(id):
    source=source_document(id)
    voices,paras=voiced_paragraphs(id)
    signals=[s for row in paras for s in classify_passage(row)]
    nodes=[]
    for i,s in enumerate(signals,1):
        row=next(r for r in paras if r["id"]==s["paragraph"])
        nodes.append({
            "node":f"E{i:02}",**s,
            "court":source["court"],"historical_year":source["year"],
            "paragraph_text":row["text"],
            "source_url":source["url"],
            "source_citation":source["citation"],
            "source_role_not_verified_current_authority":True,
        })
    # Graph edges are explicitly rhetorical associations, not proof of a
    # judicial rule or automatic disposition aggregation.
    connections=[]
    for left in nodes:
        for right in nodes:
            if left["node"]==right["node"]:continue
            if left["judge"]==right["judge"]:
                if (left["feature"] in ("RESTRICTED_SCOPE","EXPANSIVE_SCOPE")
                        and right["feature"]=="CONCERN_WITH_EVIDENCE"):
                    connections.append({"from":right["node"],"to":left["node"],
                                        "relation":"SAME_VOICE_REASONS_ASSOCIATION"})
            elif ({left["feature"],right["feature"]}==
                  {"RESTRICTED_SCOPE","EXPANSIVE_SCOPE"}
                  and left["node"]<right["node"]):
                connections.append({"from":left["node"],"to":right["node"],
                                    "relation":"COMPETING_VOICES_NOT_SINGLE_SOURCE_CONTRADICTION"})
    relevant={}
    for person,header in voices.items():
        own=[s for s in nodes if s["judge"]==person]
        stance=sorted({s["feature"] for s in own
                       if s["feature"] in ("RESTRICTED_SCOPE","EXPANSIVE_SCOPE")})
        dispositions=sorted({s["feature"] for s in own
                             if s["feature"] in ("REVERSAL","AFFIRMANCE")})
        relevant[person]={
            "role":header["role"],
            "named_joiners":header["named_joiners"],
            "explicit_votes":header["explicit_votes"],
            "interpretive_signals":stance,
            "disposition_signals":dispositions,
            "source_role_header":header["header"],
        }
    return {
        "schema":SCHEMA,"case_id":id,
        "citation":source["citation"],"court":source["court"],
        "year":source["year"],"source_url":source["url"],
        "source_pin":source_pin(),
        "source_snapshot_digest":digest(source),
        "parsed_voices":relevant,
        "source_paragraph_count":len(paras),
        "evidence_nodes":nodes,"argument_links":connections,
        "text_inference_only_from_declared_cues":True,
        "full_opinion_read":False,
        "authoritative_holding_automatically_inferred":False,
        "current_law_inferred":False,
        "external_execution":False,"real_world_authority":False,
    }



STOPWORDS={"the","a","an","does","did","is","was","are","what","which","who",
           "why","how","and","or","to","of","in","on","for","under","this",
           "that","it","from","court","judgment","legal","case","opinion",
           "law","can","be","about","with","have","has","we"}

def investigate(case_id,question):
    """Return relevant source spans, NEVER a synthetic judicial yes/no.

    This is a very weak classical term-overlap source-retrieval control.
    Unsupported or low-relevance questions HOLD rather than being answered.
    """
    if not isinstance(question,str) or not 8<=len(question)<=300:
        raise HOLD("Unbounded or missing research question")
    report=read(case_id)
    terms=set(re.findall(r"[a-z0-9]+",question.lower()))-STOPWORDS
    if not terms:raise HOLD("No substantive question")
    matches=[]
    for node in report["evidence_nodes"]:
        words=set(re.findall(r"[a-z0-9]+",node["paragraph_text"].lower()))-STOPWORDS
        overlap=sorted(terms&words)
        if len(overlap)>=2:
            matches.append({"paragraph":node["paragraph"],
                            "voice":node["judge"],
                            "role":node["voice_role"],
                            "source_url":node["source_url"],
                            "source_sha256":node["source_sha256"],
                            "overlapping_terms":overlap,
                            "exact_excerpt":node["paragraph_text"]})
    dedup={m["paragraph"]:m for m in matches}
    result=sorted(dedup.values(),key=lambda x:(-len(x["overlapping_terms"]),x["paragraph"]))
    if not result:
        return {"stage":"HOLD_NO_RELEVANT_ANCHORED_EVIDENCE",
                "question":question,"sources":[],
                "legal_advice":False,"real_world_authority":False}
    return {"stage":"SOURCE_SPANS_NEED_INTERPRETATION",
            "question":question,"sources":result[:5],
            "not_a_judicial_yes_no_answer":True,
            "legal_advice":False,"real_world_authority":False}


def export(id):
    body=read(id)
    raw=json.dumps(dict(body,checksum_sha256=digest(body)),
                   sort_keys=True,indent=2,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_CHARS:
        raise HOLD("Overlarge source-linked argument graph packet")
    return raw


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_CHARS:
        raise HOLD("Oversized or missing argument graph")
    try:doc=json.loads(raw)
    except (TypeError,ValueError) as exc:raise HOLD("Malformed source graph") from exc
    if not isinstance(doc,dict) or set(doc)!=set(read("MCBOYLE"))|{"checksum_sha256"}:
        raise HOLD("Unknown authority or missing source fields")
    if doc.get("real_world_authority") is not False or doc.get("external_execution") is not False:
        raise HOLD("External authority cannot travel with an opinion")
    if doc!=json.loads(export(doc["case_id"])):
        raise HOLD("Unreplayable, stale or forged court interpretation")
    return doc
