"""Offline SVG viewer: two circles + source's newly learned third distinction.

All displayed "people" and statements are invented. The diagram visualizes
actual source receipts from the REASON-021 GitHub Actions benchmark, not an
authenticated real human or a live personal conversation. No network calls.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

HTML=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">
<title>MOTIF · The Other Teaches the Self</title>
<style>
:root{color-scheme:dark;--bg:#101820;--paper:#192938;--line:#34546a;--text:#f2f7fa;--muted:#bcd0d9;--self:#79c9d6;--other:#e8b679}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 ui-sans-serif,system-ui,Arial,sans-serif}
main{max-width:1100px;padding:25px 18px 65px;margin:0 auto}
h1{font-size:clamp(1.7rem,4vw,3rem);letter-spacing:-.04em;margin:.25em 0}
h2{font-size:1.08rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
p{line-height:1.55}small,.muted{color:var(--muted)}
.eyebrow{font-size:.8rem;color:#a9cce0;text-transform:uppercase;letter-spacing:.16em}
.card{border:1px solid var(--line);background:var(--paper);border-radius:18px;padding:20px;margin:17px 0}
select{font:inherit;color:white;background:#0e1c29;padding:13px;border:1px solid #84a0ae;border-radius:12px;max-width:100%;width:530px}
.diagram{display:block;width:100%;max-height:450px}
.diagram .self{fill:#138995;fill-opacity:.32;stroke:var(--self);stroke-width:3}
.diagram .other{fill:#b47634;fill-opacity:.31;stroke:var(--other);stroke-width:3}
.diagram text{font-family:ui-sans-serif,system-ui,sans-serif;fill:white}
.diagram .big{font-weight:750;font-size:28px}
.diagram .note{font-size:17px;fill:#e0eaf1}
.diagram .middle{font-size:17px;font-weight:700}
.pill{display:inline-block;border-radius:30px;background:#2a4d63;padding:5px 12px;font-size:.87rem;margin:6px 6px 2px 0}
.pill.yellow{background:#645031}
.columns{display:grid;grid-template-columns:repeat(auto-fit,minmax(265px,1fr));gap:14px}
.column{padding:18px;background:#0e202f;border:1px solid var(--line);border-radius:14px}
.column h3{margin:0 0 9px;font-size:1.03rem}.column pre{margin:8px 0;white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,monospace;color:#e2eff6}
.hero{border-left:4px solid #a4dfb0}
.hero strong{font-size:1.25rem;overflow-wrap:anywhere}
.warning{background:#3b3027;border:1px solid #9d855c;padding:16px;border-radius:14px;color:#ffeaca}
.counter{color:#ffe5b8}
</style></head><body><main>
<p class="eyebrow">The Static Collective · MOTIF · REASON-021 · simulated source evidence</p>
<h1>The Other Teaches the Self</h1>
<p>An invented recipient contradicts the helper's interpretation. Two situations look
identical to SELF, but OTHER reports opposite answers. The helper has to ask which distinction it missed—or HOLD when the source refuses.</p>
<div class="card"><label for="source-select"><strong>Choose a fictional source owner</strong></label><br>
<select id="source-select" aria-label="Fictional respondent"></select>
<p class="muted">11 synthetic scenes. No living person, personal data, external action or actual consent.</p></div>
<svg class="diagram" viewBox="0 0 1000 425" role="img"
aria-label="Self capability and the other's corrections in two overlapping circles, with a newly discovered feature suspended between them.">
<circle class="self" cx="382" cy="215" r="204"></circle>
<circle class="other" cx="618" cy="215" r="204"></circle>
<text x="242" y="140" text-anchor="middle" class="big">SELF</text>
<text x="242" y="178" text-anchor="middle" class="note">current model</text>
<text x="242" y="204" text-anchor="middle" class="note">limits · correction</text>
<text x="758" y="140" text-anchor="middle" class="big">OTHER</text>
<text x="758" y="178" text-anchor="middle" class="note">source testimony</text>
<text x="758" y="204" text-anchor="middle" class="note">boundaries · veto</text>
<text x="500" y="258" text-anchor="middle" class="middle">MIRROR</text>
<text x="500" y="288" text-anchor="middle" class="note">learn / HOLD</text>
<text x="500" y="313" text-anchor="middle" class="note">ask permission</text>
</svg>
<div class="card hero"><h2>Current proposal</h2><strong id="outcome"></strong>
<p id="desc"></p><span class="pill" id="old-model"></span>
<span class="pill yellow" id="new-model"></span></div>
<div class="columns">
<section class="column"><h3>1 · What SELF failed to distinguish</h3><p id="proof-title"></p><pre id="counterexample"></pre></section>
<section class="column"><h3>2 · What OTHER actually disclosed</h3><p id="disclosure"></p><pre id="responses"></pre></section>
<section class="column"><h3>3 · New executable representation</h3><p id="state"></p><pre id="model"></pre></section>
<section class="column"><h3>4 · Golden Rule check</h3><p id="reciprocity"></p><pre id="critic"></pre></section>
</div>
<div class="card warning">
<strong>Scientific boundaries:</strong> All recipients, rules and permission replies were invented by the same researcher.
The learner searches a finite DNF grammar over at most three Boolean variables; the source discloses the third variable.
The four original elves are deterministic Python processes, not secure VMs or conscious agents.
This does not measure love, empathy, objective human welfare or safety around real people.
Even a correct preference prediction is never permission to intervene.
</div>
<p class="muted">The display is compiled from the actual source-owned JSON and heldout checks. The standalone HTML uses no network resources, cookies, trackers or live personal records.</p>
</main>
<script id="evidence" type="application/json">__DATA__</script>
<script>
"use strict";
const dataset=JSON.parse(document.getElementById("evidence").textContent);
const rowSelect=document.getElementById("source-select");
const el=id=>document.getElementById(id);
const p=v=>JSON.stringify(v,null,2);
for(const x of dataset.case_results){
 const opt=document.createElement("option");opt.value=x.case;
 opt.textContent=x.case+" · "+x.learner_stage.replaceAll("_"," ");
 rowSelect.appendChild(opt);
}
function update(){
 const x=dataset.case_results.find(r=>r.case===rowSelect.value)||dataset.case_results[0];
 el("outcome").textContent=x.final_proposal.replaceAll("_"," ");
 el("desc").textContent="Target: "+x.case+" · permission to discuss: "+
   (x.scope_only_permission||"NOT GRANTED / NOT ASKED");
 el("old-model").textContent="Old known language: PRIVATE · CHOICE";
 el("new-model").textContent="Updated language: "+(x.new_feature||"NO NEW FEATURE");
 if(x.old_feature_contradiction_witness){
  const w=x.old_feature_contradiction_witness;
  const m=Object.fromEntries(x.synthetic_source_observations.map(y=>[y.id,y.reply]));
  el("proof-title").textContent="These observations are identical in the original model:";
  el("counterexample").textContent=p(w.same_public_features)+"\n"+
    w.different_source_answers[0]+" → "+m[w.different_source_answers[0]]+"\n"+
    w.different_source_answers[1]+" → "+m[w.different_source_answers[1]];
 }else{
  el("proof-title").textContent="No contradictory old-feature pair observed.";
  el("counterexample").textContent="Observed hypothetical answers: "+
    x.synthetic_source_observations.length;
 }
 el("disclosure").textContent=x.source_feature_veto_or_disclosure.replaceAll("_"," ");
 el("responses").textContent="Recipient-declared feature: "+(x.new_feature||"WITHHELD / NOT NEEDED")
    +"\nSource query receipts: "+x.source_question_receipts;
 el("state").textContent="Learned representation stage: "+x.learner_stage;
 el("model").textContent=x.DNF_program?p(x.DNF_program):"HOLD — No justified rule";
 el("reciprocity").textContent="If roles reversed, the tool would prefer: "+x.self_role_reversal_wish
    +"\nComparison: "+x.reciprocity;
 el("critic").textContent="Blocked because: "+p(x.critic_rejection_reasons)
    +"\nOffered options only: "+(x.final_proposal==="SUGGEST_DISCUSSION_ONLY")
    +"\nPermission to execute: FALSE";
}
rowSelect.addEventListener("change",update);
rowSelect.value=dataset.case_results[0].case;update();
</script></body></html>'''


def build(source,destination):
    evidence=json.loads(Path(source).read_text(encoding="utf8"))
    if (evidence.get("schema")!="motif.reason.other-teaches-self.benchmark.v1"
            or evidence.get("synthetic_source_owners")!=11
            or evidence.get("author_outcome_matches")!=11
            or evidence.get("no_external_actions") is not True
            or evidence.get("not_a_mind_or_love_measurement") is not True):
        raise ValueError("The viewer requires complete, verified, read-only synthetic evidence")
    blob=json.dumps({"case_results":evidence["case_results"]},
                    sort_keys=True,ensure_ascii=True,separators=(",",":"))
    blob=blob.replace("<","\\u003c").replace("&","\\u0026")
    rendered=HTML.replace("__DATA__",blob)
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(rendered,encoding="utf8")
    return {"html_path":str(dest),"bytes":dest.stat().st_size,
            "fictional_cases":len(evidence["case_results"]),
            "external_network_requests":False}


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: python viewer.py benchmark.json two-circles-learning.html")
    print(json.dumps(build(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
