"""Build a zero-dependency, self-contained two-circle Golden Mirror viewer.

This renders synthetic source-evidence results, NOT a real person's private
psychological profile. There are no network requests, cookie stores or tools.
The two overlapping circles are explicitly *partial* perspective models.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

HTML=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">
<title>MOTIF-019 • The Golden Mirror</title>
<style>
:root{color-scheme:dark;--bg:#0c1620;--panel:#142536;--muted:#c4d2db;--ink:#eff5f7;--line:#365066;--left:#57c7d4;--right:#ffc27d}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);margin:0;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:auto;padding:24px 20px 60px}h1{font-size:clamp(1.7rem,4vw,3rem);letter-spacing:-.025em;margin:.2em 0}
h2{font-size:1rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
p{line-height:1.55}p.small,.small{font-size:.91rem;color:var(--muted)}
.eyebrow{color:#a4bce9;text-transform:uppercase;font-size:.82rem;letter-spacing:.14em}
.card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px;margin:16px 0}
select{background:#091622;color:white;font:inherit;padding:12px 16px;border:1px solid #6b8b9b;border-radius:12px;max-width:100%;min-width:min(100%,380px)}
.diagram{width:100%;height:auto;max-height:450px;display:block}
.diagram .self{fill:#2d98aa;fill-opacity:.29;stroke:var(--left);stroke-width:3}
.diagram .other{fill:#d18b39;fill-opacity:.27;stroke:var(--right);stroke-width:3}
.diagram text{fill:#fff;font-family:ui-sans-serif,system-ui}
.diagram .title{font-size:27px;font-weight:750}.diagram .note{font-size:17px;fill:#d2e1e8}
.diagram .center{font-size:17px;font-weight:650;fill:white}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.field{background:#0d1c2a;border:1px solid var(--line);border-radius:13px;padding:17px}
.field h3{margin:0 0 11px;font-size:1.03rem}.field p{margin:7px 0;white-space:pre-wrap;overflow-wrap:anywhere}
.tag{display:inline-block;border-radius:22px;background:#254557;padding:7px 12px;margin-right:5px;font-size:.86rem}
.outcome{border-left:4px solid #abdbaa}.outcome strong{font-size:1.3rem;color:#f6ffe9}
p.warning{border:1px solid #a05b52;background:#3c2329;border-radius:10px;padding:14px;color:#ffdfd9}
code{font-size:.92em;white-space:normal;overflow-wrap:anywhere}
</style></head><body><main>
<p class="eyebrow">MOTIF · REASON-019 · experimental read-only evidence</p>
<h1>The Golden Mirror</h1>
<p>Two partially informed perspectives. Four independently executed, deterministic <em>elf</em> processes.
The overlap is a reciprocity <strong>question</strong>, not permission to act.</p>
<div class="card"><label for="case-select"><strong>Choose a fictional test scenario</strong></label><br><br>
<select id="case-select" aria-label="Synthetic scenario"></select>
<p class="small">All people, goals, permissions, scores and answers in this viewer are synthetic source-authored fixtures, not observations about a living person.</p></div>
<svg class="diagram" viewBox="0 0 1000 430" role="img" aria-label="Two overlapping circles. Left is MOTIF's self capabilities; right is the recipient's stated wishes. Their overlap is a reciprocity comparison, not authorization.">
<circle class="self" cx="384" cy="215" r="208"></circle>
<circle class="other" cx="616" cy="215" r="208"></circle>
<text class="title" x="245" y="154" text-anchor="middle">SELF</text>
<text class="note" x="225" y="186" text-anchor="middle">capability · limits</text>
<text class="note" x="225" y="212" text-anchor="middle">role-reversal test</text>
<text class="title" x="755" y="154" text-anchor="middle">OTHER</text>
<text class="note" x="778" y="186" text-anchor="middle">stated preference</text>
<text class="note" x="778" y="212" text-anchor="middle">scoped permission</text>
<text class="center" x="500" y="260" text-anchor="middle">Mirror</text>
<text class="note" x="500" y="289" text-anchor="middle">do not project</text>
<text class="note" x="500" y="315" text-anchor="middle">do not assume consent</text>
</svg>
<div class="card outcome"><h2>Supervised result</h2><p><strong id="choice"></strong></p><p class="small" id="stage"></p>
<p id="baseline"></p></div>
<div class="grid">
<div class="field"><h3>Circle 1 · Self-elf</h3><p id="self-data"></p></div>
<div class="field"><h3>Circle 2 · Other-elf</h3><p id="other-data"></p></div>
<div class="field"><h3>Bridge · Mirror-elf</h3><p id="mirror-data"></p></div>
<div class="field"><h3>Safety · Critic-elf</h3><p id="critic-data"></p></div>
</div>
<p class="warning"><strong>Boundary:</strong> This is executable thought-experiment code. The four elves are Python subprocesses,
not secure virtual machines or human-like conscious agents. The output is a non-executing suggestion.
No independent human ethics panel or real-world welfare experiment was conducted.</p>
<p class="small">Source &amp; audit: experiment/reason-cartridge-019 in the MOTIF repository. All four process results,
source-bound scenarios and independent audit data are included with the CI artifact.</p>
</main><script id="evidence" type="application/json">__DATA_JSON__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("evidence").textContent);
const scenes=data.case_results;
const selector=document.getElementById("case-select");
for(const record of scenes){
  const opt=document.createElement("option");opt.value=record.case;opt.textContent=record.case.replaceAll("_"," ");selector.appendChild(opt);
}
function format(o){return JSON.stringify(o,null,2)}
function update(){
 const row=scenes.find(x=>x.case===selector.value)||scenes[0];
 document.getElementById("choice").textContent=row.chosen||"HOLD — no safe action";
 document.getElementById("stage").textContent=row.stage+" · "+row.case;
 document.getElementById("baseline").textContent="Naïve project-self choice: "+(row.naive_self_projection_choice||"HOLD")
  +" · Other-only classic rules: "+(row.other_only_no_self_choice||"HOLD");
 document.getElementById("self-data").textContent=format(row.self_assumed_welcome);
 document.getElementById("other-data").textContent="Wish statements: "+format(row.other_explicit_wishes)
  +"\nExplicit action authorization: "+format(row.other_scoped_permissions);
 document.getElementById("mirror-data").textContent="Projection hazards: "+format(row.projection_dangers)
  +"\nDifferences respected: "+format(row.difference_preserved);
 document.getElementById("critic-data").textContent="Excluded proposals and reasons: "+format(row.blocked_actions);
}
selector.addEventListener("change",update);selector.value=scenes[0].case;update();
</script></body></html>'''


def build(result_path,out_path):
    data=json.loads(Path(result_path).read_text(encoding="utf8"))
    if (data.get("schema")!="motif.reason.golden-mirror.benchmark.v1"
            or data.get("source_scenarios")!=24
            or data.get("human_love_or_welfare_not_measured") is not True):
        raise ValueError("Viewer requires verified, synthetic source records")
    payload=json.dumps({"case_results":data["case_results"]},
                       ensure_ascii=True,separators=(",",":"))
    payload=payload.replace("<","\\u003c").replace("&","\\u0026")
    doc=HTML.replace("__DATA_JSON__",payload)
    dest=Path(out_path);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(doc,encoding="utf8")
    return {"path":str(dest),"scenes":len(data["case_results"]),
            "bytes":dest.stat().st_size,"external_requests":False}


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: python viewer.py benchmark.json golden-mirror-viewer.html")
    print(json.dumps(build(sys.argv[1],sys.argv[2]),indent=2))
