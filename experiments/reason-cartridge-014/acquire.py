"""Fetch and archive FULL opinion-body HTML + unabridged paragraph text.

Pinned URLs are published Cornell LII reproductions of U.S. Supreme Court
opinions. Uses stdlib only, extracts every <p> in source div.bodytext,
including majority and separate opinion portions. No editorial paragraph
selection, truncation, LLM, or text labeling. Records page bytes, line/paragraph
source anchors and SHA-256. External requests ONLY via explicit CLI --download;
the reasoning engine itself is offline and read-only.

Acquisition is not legal authenticity verification; LII is a reproduction,
not a signed Court feed. CI fails if minimum page/author/endpoint checks fail.
"""
from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from hashlib import sha256
import json
import re
import sys

CASES={
 "MCBOYLE":{"url":"https://www.law.cornell.edu/supremecourt/text/283/25",
            "citation":"283 U.S. 25 (1931)","split":"DEVELOPMENT",
            "min_words":350,"required":["vehicle","airplane","Judgment reversed"]},
 "NIX":{"url":"https://www.law.cornell.edu/supremecourt/text/149/304",
        "citation":"149 U.S. 304 (1893)","split":"DEVELOPMENT",
        "min_words":300,"required":["tomatoes","vegetables","Judgment affirmed"]},
 "KIRBY":{"url":"https://www.law.cornell.edu/supremecourt/text/74/482",
          "citation":"74 U.S. 482 (1868)","split":"SEALED_EVALUATION",
          "min_words":400,"required":["murder","carrier","surgeon","IN THE NEGATIVE"]},
 "BALLARD":{"url":"https://www.law.cornell.edu/supremecourt/text/322/78",
            "citation":"322 U.S. 78 (1944)","split":"SEALED_EVALUATION",
            "min_words":1900,"required":["religious","remand",
                "Justice JACKSON","Justice STONE"]},
}
SCHEMA="motif.reason.complete-opinion-source-v1"

class Body(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.stack=[]
  self.body_start=None
  self.inside=None
  self.parts=[]
  self.paragraphs=[]
  self.body_count=0
 def handle_starttag(self,t,a):
  d=dict(a)
  self.stack.append((t,d))
  if t=="div" and "bodytext" in d.get("class","").split():
   if self.body_start is None:
    self.body_start=len(self.stack)
    self.body_count+=1
  if t=="p" and self.body_start is not None and self.inside is None:
   self.inside=len(self.stack)
   self.parts=[]
 def handle_startendtag(self,t,a):
  pass
 def handle_data(self,data):
  if self.inside is not None:
   self.parts.append(data)
 def handle_endtag(self,t):
  if t=="p" and self.inside is not None:
   text=re.sub(r"\s+"," ",unescape("".join(self.parts))).strip()
   if text:
    source_id=next((a.get("id") for tag,a in self.stack[::-1]
                    if tag=="div" and re.fullmatch(r"p\d+",a.get("id",""))),None)
    self.paragraphs.append({"ordinal":len(self.paragraphs)+1,
                            "anchor":source_id or f"ordinal-{len(self.paragraphs)+1}",
                            "text":text,
                            "sha256":sha256(text.encode()).hexdigest()})
   self.inside=None;self.parts=[]
  while self.stack:
   previous=self.stack.pop()
   if self.body_start is not None and len(self.stack)<self.body_start:
    self.body_start=None
   if previous[0]==t:break


def extract(case_id,html):
 if case_id not in CASES or not isinstance(html,bytes) or not 10000<len(html)<1500000:
  raise ValueError("Unsupported or missing complete public opinion page")
 p=Body()
 p.feed(html.decode("utf8","replace"))
 merged="\n\n".join(x["text"] for x in p.paragraphs)
 cfg=CASES[case_id]
 if (len(merged.split())<cfg["min_words"]
       or len(p.paragraphs)<3
       or any(word.lower() not in merged.lower() for word in cfg["required"])
       or "Supreme Court Toolbox" in merged):
  raise ValueError(f"{case_id}: incomplete opinion, source changed, or site UI leaked")
 return {
  "schema":SCHEMA,"case_id":case_id,"url":cfg["url"],
  "citation":cfg["citation"],"split":cfg["split"],
  "raw_page_sha256":sha256(html).hexdigest(),
  "opinion_body_sha256":sha256(merged.encode()).hexdigest(),
  "full_untrimmed_body_paragraphs":p.paragraphs,
  "word_count":len(merged.split()),"paragraph_count":len(p.paragraphs),
  "source_kind":"LIVE_PUBLISHED_CORNELL_LII_JUDICIAL_OPINION_REPRODUCTION",
  "complete_source_body_not_manually_selected_quotes":True,
  "full_page_not_a_signed_official_court_feed":True,
  "current_law_not_verified":True,
 }


def fetch(case_id):
 if case_id not in CASES:raise ValueError("Invalid allowlisted opinion")
 req=Request(CASES[case_id]["url"],
             headers={"User-Agent":"MOTIF-014-research/0.1 (court opinion source audit)"})
 with urlopen(req,timeout=30) as response:
  if response.status!=200:raise ValueError("Source unavailable")
  html=response.read(1500001)
 return extract(case_id,html),html


def acquire(folder):
 dest=Path(folder)
 dest.mkdir(parents=True,exist_ok=True)
 summaries={}
 for case_id in CASES:
  page,html=fetch(case_id)
  (dest/(case_id.lower()+".raw.html")).write_bytes(html)
  (dest/(case_id.lower()+".full.json")).write_text(
      json.dumps(page,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
  summaries[case_id]={
    "raw_page_sha256":page["raw_page_sha256"],
    "opinion_body_sha256":page["opinion_body_sha256"],
    "words":page["word_count"],"paragraphs":page["paragraph_count"],
    "first_paragraph":page["full_untrimmed_body_paragraphs"][0]["text"][:100],
    "last_paragraph":page["full_untrimmed_body_paragraphs"][-1]["text"][-100:],
  }
 manifest={"schema":"motif.reason.complete-opinion-acquisition-manifest.v1",
           "cases":summaries,"download_source_is_live":True,
           "downloaded_text_reproductions_not_official_signed_records":True}
 (dest/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 return manifest


if __name__=="__main__":
 if len(sys.argv)!=2:raise SystemExit("usage: python acquire.py <source-dir>")
 print(json.dumps(acquire(sys.argv[1]),indent=2,sort_keys=True))
