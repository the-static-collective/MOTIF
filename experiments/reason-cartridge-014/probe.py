"""One-time source-acquisition diagnosis of original Cornell opinion HTML."""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from collections import Counter

cases={
 "MCBOYLE":"https://www.law.cornell.edu/supremecourt/text/283/25",
 "NIX":"https://www.law.cornell.edu/supremecourt/text/149/304",
 "KIRBY":"https://www.law.cornell.edu/supremecourt/text/74/482",
 "BALLARD":"https://www.law.cornell.edu/supremecourt/text/322/78",
}
targets=["The statute of Congress by its terms applies","The petitioner was convicted","The single question in this case","Respondents were indicted"]

class Peek(HTMLParser):
 def __init__(self):
  super().__init__();self.stack=[];self.hit=False;self.tags=Counter()
 def handle_starttag(self,t,a):
  self.stack.append((t,dict(a)))
 def handle_startendtag(self,t,a):pass
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==t:
    del self.stack[i:];return
 def handle_data(self,d):
  for name in targets:
   if name.lower()[:18] in d.lower() and not self.hit:
    self.hit=True
    print("BODY_ANCESTORS",[(t,{k:v for k,v in a.items() if k in ('id','class')}) for t,a in self.stack[-12:]])
    print("FIRST_HIT",repr(d[:170]))
    return

for label,url in cases.items():
 try:
  req=Request(url,headers={"User-Agent":"MOTIF-source-audit/0.1 (public research; GitHub Actions)"})
  with urlopen(req,timeout=25) as h:
   raw=h.read()
   print(label,"http",h.status,"bytes",len(raw),"type",h.headers.get("Content-Type"))
  parser=Peek();parser.feed(raw.decode("utf8","replace"));print(label,"hit",parser.hit)
 except Exception as exc:
  print(label,"ERROR",type(exc).__name__,str(exc)[:200])
