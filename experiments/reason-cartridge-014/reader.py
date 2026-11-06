"""REASON-014: offline source-linked retrieval over COMPLETE Cornell opinion bodies.

Not a full-text legal inference model. The retrieval methods are deliberately
ordinary classical information retrieval (BM25 and overlap baseline). The
engineering experiment is that NO manually selected snippet can replace the
full acquired document, the reader operates on every paragraph, attributed
judicial voices are separated, and every answer is traceable and read-only.

Never imports review_keys.py; benchmark gold remains evaluator-only.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from hashlib import sha256
from math import log
from pathlib import Path
import json
import re

from contract import SHA,DEVELOPMENT,UNSEEN,VERSION
from acquire import CASES,SCHEMA as SOURCE_SCHEMA

SCHEMA="motif.reason.complete-opinion-reader.v1"
STOP=set("""a an and are as at be been but by can did do does for from had has have
how in into is it its of on or our shall should so than that the their them
there these they this those through to under was were what when where whether
which who whom why will with would you your we were said court justice opinion
case question law statute supreme united states held holding""".split())
TOKEN=re.compile(r"[a-z0-9]+(?:'[a-z]+)?",re.I)
HEADER=re.compile(r"\b(?:Mr\.\s*)?(?:(?:Chief|Associate)\s+)?Justice\s+([A-Za-z]+)[,\s]+(.{0,130})",re.I)
MAX_OUTPUT=15000
MAX_PARAGRAPHS=120

class HOLD(ValueError):pass


def tokens(text):
 if not isinstance(text,str):raise HOLD("Invalid source or research query")
 return [x for x in TOKEN.findall(text.lower()) if len(x)>2 and x not in STOP]


def read_source(root,case_id):
 if case_id not in CASES:raise HOLD("Unregistered public court source")
 p=Path(root)
 try:
  document=json.loads((p/(case_id.lower()+".full.json")).read_text())
  raw=(p/(case_id.lower()+".raw.html")).read_bytes()
 except (OSError,ValueError) as exc:
  raise HOLD("Missing complete owner-acquired court source") from exc
 if (not isinstance(document,dict)
      or document.get("schema")!=SOURCE_SCHEMA
      or document.get("case_id")!=case_id
      or document.get("url")!=CASES[case_id]["url"]
      or document.get("citation")!=CASES[case_id]["citation"]
      or document.get("split")!=CASES[case_id]["split"]
      or document.get("complete_source_body_not_manually_selected_quotes") is not True
      or sha256(raw).hexdigest()!=SHA[case_id]["raw"]
      or document.get("raw_page_sha256")!=SHA[case_id]["raw"]):
  raise HOLD("Full HTML origin, split or exact source pin changed")
 paragraphs=document.get("full_untrimmed_body_paragraphs")
 if (not isinstance(paragraphs,list) or not 3<len(paragraphs)<=MAX_PARAGRAPHS
     or any(not isinstance(x,dict) or set(x)!={"ordinal","anchor","text","sha256"}
            or x["ordinal"]!=j+1 or
            sha256(x["text"].encode()).hexdigest()!=x["sha256"]
            or not isinstance(x["anchor"],str)
            for j,x in enumerate(paragraphs))):
  raise HOLD("Page paragraphs truncated, injected or reordered")
 text="\n\n".join(x["text"] for x in paragraphs)
 if (document.get("opinion_body_sha256")!=SHA[case_id]["body"]
      or sha256(text.encode()).hexdigest()!=SHA[case_id]["body"]
      or document.get("paragraph_count")!=len(paragraphs)
      or document.get("word_count")!=len(text.split())):
  raise HOLD("Opinion body changed even if metadata was rehashed")
 return document


def new_voice(text):
 if not isinstance(text,str):return None
 # Citation to somebody else's Justice mid-paragraph is not a voice switch.
 m=HEADER.search(text)
 if m is None or m.start()>45:return None
 tail=m.group(2).lower()
 if "dissenting" in tail:role="DISSENT"
 elif "concurring" in tail:role="CONCURRENCE"
 elif "delivered the opinion" in tail:role="OPINION_OF_COURT"
 else:return None
 return {"judge":m.group(1).upper(),"role":role}


def attributed(document):
 voice={"judge":None,"role":"BACKGROUND_OR_ADVOCACY"}
 rows=[]
 for p in document["full_untrimmed_body_paragraphs"]:
  speaker=new_voice(p["text"])
  if speaker is not None:voice=speaker
  # Keep source original text entirely, but mark boilerplate as not a legal
  # evidence candidate. Never erase paragraphs from audited source count.
  boilerplate=(p["text"].startswith("CC∅")
               or p["text"].startswith("Transformed by Public.Resource.Org"))
  rows.append({**p,"judge":voice["judge"],"voice_role":voice["role"],
               "is_site_boilerplate":boilerplate})
 return rows


def score(query,paragraphs,method):
 if method not in ("BM25","OVERLAP"):
  raise HOLD("Unrecognized classical retrieval method")
 qt=Counter(tokens(query))
 if not qt: return []
 documents=[Counter(tokens(p["text"])) if not p["is_site_boilerplate"] else Counter()
            for p in paragraphs]
 n=len(documents)
 df=Counter()
 for doc in documents:
  df.update(doc.keys())
 avg=sum(sum(d.values()) for d in documents)/max(n,1)
 scores=[]
 for i,(p,doc) in enumerate(zip(paragraphs,documents)):
  if not doc:continue
  score_value=0.0
  for term in qt:
   tf=doc.get(term,0)
   if not tf:continue
   if method=="OVERLAP":
    score_value+=1.0
   else:
    idf=log(1+(n-df[term]+0.5)/(df[term]+0.5))
    score_value+=idf*(tf*2.25)/(tf+1.25*(0.45+0.55*sum(doc.values())/max(avg,1)))
  # A search specifically naming a Justice prefers words attributable to the
  # correct opinion, rather than mentions of that Justice by a different one.
  if p["judge"] and p["judge"].lower() in qt:
   score_value+=1.5
  if "dissent" in qt and p["voice_role"]=="DISSENT":
   score_value+=0.2
  if score_value>0:scores.append((round(score_value,7),i))
 return sorted(scores,key=lambda t:(-t[0],t[1]))


def retrieve(root,case_id,question,*,method="BM25",k=5):
 if not isinstance(question,str) or not 10<=len(question)<=320:
  raise HOLD("Missing or unbounded evidence question")
 if type(k) is not int or not 1<=k<=10:
  raise HOLD("Unbounded retrieval budget")
 doc=read_source(root,case_id)
 rows=attributed(doc)
 found=score(question,rows,method)
 if not found:
  return {"schema":SCHEMA,"case_id":case_id,"status":"HOLD_NO_ANCHORED_EVIDENCE",
          "question":question,"algorithm":method,"source_url":doc["url"],
          "searched_paragraphs":len(rows),"results":[],
          "no_legal_outcome_inferred":True,"legal_advice":False,
          "real_world_authority":False}
 results=[]
 for s,i in found[:k]:
  p=rows[i]
  results.append({
   "paragraph_ordinal":p["ordinal"],"source_anchor":p["anchor"],
   "source_url":doc["url"]+(("#"+p["anchor"])
                            if re.fullmatch(r"p\d+",p["anchor"]) else ""),
   "citation":doc["citation"],"excerpt":p["text"],
   "text_sha256":p["sha256"],"judge":p["judge"],
   "voice_role":p["voice_role"],"relevance":s,
   "candidate_evidence_not_verified_judicial_holding":True,
  })
 return {"schema":SCHEMA,"case_id":case_id,
         "status":"EVIDENCE_CANDIDATES_REQUIRE_REVIEW",
         "question":question,"algorithm":method,
         "source_url":doc["url"],
         "searched_paragraphs":len(rows),
         "results":results,
         "no_legal_outcome_inferred":True,"legal_advice":False,
         "real_world_authority":False}


def validate_receipt(root,result):
 if not isinstance(result,dict) or set(result)!={
  "schema","case_id","status","question","algorithm","source_url",
  "searched_paragraphs","results","no_legal_outcome_inferred",
  "legal_advice","real_world_authority"}:
  raise HOLD("Unknown claim or legal authority in retrieval output")
 if (result["schema"]!=SCHEMA or result["real_world_authority"] is not False
     or result["legal_advice"] is not False
     or result["no_legal_outcome_inferred"] is not True):
  raise HOLD("Unreviewed permission or evidence assertions")
 expected=retrieve(root,result["case_id"],result["question"],
                   method=result["algorithm"],k=max(1,len(result["results"])))
 if expected!=result:
  raise HOLD("Missing, forged, stale, or edited judicial evidence")
 return result
