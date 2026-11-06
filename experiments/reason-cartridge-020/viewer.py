"""Make an OFFLINE, interactive dual-circle evidence viewer from the real run.

Nothing is observed about living people. No scripts, fonts, images or analytics
are loaded from the network. It does not update source files or execute actions.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

TEMPLATE=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">
<title>MOTIF — The Golden Mirror Learns</title>
<style>
:root{color-scheme:dark;--bg:#10151c;--card:#182635;--ink:#f2f6fa;--muted:#b9cbda;--line:#385267;--self:#62d5ce;--other:#f8bd7b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 ui-sans-serif,system-ui,sans-serif}
main{max-width:1150px;margin:auto;padding:26px 18px 55px}
h1{font-size:clamp(1.8rem,4.3vw,3rem);line-height:1.15;letter-spacing:-.03em;margin:.3em 0}
h2{font-size:1rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin:.4em 0}
p{margin:.8em 0;line-height:1.55}.small{font-size:.9rem;color:var(--muted)}
.eyebrow{color:#a9d5f5;letter-spacing:.15em;text-transform:uppercase;font-size:.79rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:17px;padding:19px;margin:18px 0}
select{background:#10202d;color:var(--ink);padding:12px 14px;font:inherit;border:1px solid #7890a1;border-radius:12px;max-width:100%;width:560px}
.diagram{display:block;width:100%;max-height:440px}
.diagram circle:first-of-type{fill:#157a7a;fill-opacity:.35;stroke:var(--self);stroke-width:3}
.diagram circle:nth-of-type(2){fill:#b37425;fill-opacity:.31;stroke:var(--other);stroke-width:3}
.diagram text{font-family:ui-sans-serif,system-ui;fill:#fff}
.diagram .big{font-size:28px;font-weight:750}
.diagram .smalltext{font-size:18px;fill:#d8e7ed}
.diagram .center{font-size:20px;font-weight:650}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.metric{padding:14px;background:#0f1d2a;border-radius:12px;border:1px solid var(--line)}
.metric b{display:block;font-size:1.35rem;color:#d0f5ed}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
h3{margin:0 0 12px}.panel{border:1px solid var(--line);border-radius:14px;padding:18px;background:#112132}
label{display:block;margin-bottom:9px}.field{white-space:pre-wrap;overflow-wrap:anywhere;margin:8px 0}
.badge{display:inline-block;border-radius:40px;background:#264558;padding:4px 11px;margin-right:6px;font-size:.84rem}
.green{border-left:4px solid #9bdda7}.warn{background:#372b25;border:1px solid #a68c69;color:#f2dfcc;border-radius:14px;padding:15px}
code{white-space:normal;overflow-wrap:anywhere;font-size:.9em}
</style></head><body><main>
<p class="eyebrow">The Static Collective · MOTIF · REASON-020 · simulated evidence</p>
<h1>The Golden Mirror Learns</h1>
<p>Both circles are incomplete. One learns how to read previously unfamiliar words;
the other is revised by the recipient's testimony. The overlap never authorizes real-world action.</p>
<div class="card"><label for="case"><strong>Choose a fictional encounter</strong></label><select id="case"></select>
<p class="small">This visual is generated from the actual CI experiment, not live chat or personal records.</p></div>
<svg class="diagram" viewBox="0 0 1000 420" role="img" aria-label="Two overlapping circles. Left self capacity and independently tested skill. Right recipient's declared words and explicit consent. Overlap reciprocity and caution.">
<circle cx="384" cy="211" r="202"></circle><circle cx="617" cy="211" r="202"></circle>
<text x="246" y="137" text-anchor="middle" class="big">SELF</text>
<text x="236" y="175" text-anchor="middle" class="smalltext">limited ability</text>
<text x="236" y="204" text-anchor="middle" class="smalltext">verified learning</text>
<text x="758" y="137" text-anchor="middle" class="big">OTHER</text>
<text x="766" y="175" text-anchor="middle" class="smalltext">stated needs</text>
<text x="766" y="204" text-anchor="middle" class="smalltext">correction · consent</text>
<text x="500" y="252" text-anchor="middle" class="center">MIRROR</text>
<text x="500" y="282" text-anchor="middle" class="smalltext">do not project</text>
<text x="500" y="312" text-anchor="middle" class="smalltext">do not overreach</text>
</svg>
<div class="metrics">
<div class="metric"><span>Supervised text patterns learned</span><b id="templates">—</b></div>
<div class="metric"><span>Unseen source-positive language tests</span><b id="positive">—</b></div>
<div class="metric"><span>Unseen source-negative rejections</span><b id="negative">—</b></div>
<div class="metric"><span>Scenario-author matches</span><b id="matches">—</b></div>
</div>
<div class="card green"><h2>Current read-only result</h2><p id="outcome" style="font-size:1.32rem;font-weight:700"></p>
<p id="goal"></p><p class="small" id="baseline"></p></div>
<div class="two">
<div class="panel"><h3>Self circle — what changed?</h3><p id="self" class="field"></p></div>
<div class="panel"><h3>Other circle — what was actually reported?</h3><p id="other" class="field"></p></div>
<div class="panel"><h3>Mirror — disagreement and correction</h3><p id="mirror" class="field"></p></div>
<div class="panel"><h3>Critic — source scope</h3><p id="critic" class="field"></p></div>
</div>
<div class="card warn"><strong>Experimental limits.</strong> All examples, reported wishes, skill exams and expected outcomes are invented by one source author. The elf workers are Python subprocesses, not security VMs or conscious agents. The learned grammar is an exact-prefix/suffix pattern learner, not general natural-language or moral understanding. Nothing reaches, diagnoses, evaluates or helps a real person.</div>
<p class="small">Source: <code>experiments/reason-cartridge-020/</code> · Four actual original REASON-019 worker processes were invoked for each synthetic case. The underlying JSON source receipts and full independent mechanical review are in the Actions evidence artifact.</p>
</main>
<script type="application/json" id="source">__EVIDENCE__</script>
<script>
"use strict";
const records=JSON.parse(document.getElementById("source").textContent);
const select=document.getElementById("case");
const d=id=>document.getElementById(id);
const printer=v=>JSON.stringify(v,null,2);
for(const r of records.all_case_outcomes){
  const item=document.createElement("option");
  item.value=r.case;
  item.textContent=r.case.replaceAll("_"," ");
  select.appendChild(item);
}
d("templates").textContent=records.learned_executable_templates;
d("positive").textContent=records.source_teacher_unseen_positive_correct+" / "+records.source_teacher_unseen_positive_total;
d("negative").textContent=records.source_teacher_unseen_negative_rejected+" / "+records.source_teacher_unseen_negative_total;
d("matches").textContent=records.source_author_matches+" / "+records.synthetic_scenarios;
function render(){
 const r=records.all_case_outcomes.find(x=>x.case===select.value)||records.all_case_outcomes[0];
 d("outcome").textContent=r.new_dual_circle_result.replaceAll("_"," ");
 d("goal").textContent="Latest confirmed synthetic need: "+(r.new_reported_goal||"UNKNOWN / UNCONFIRMED");
 d("baseline").textContent="REASON-017 original: "+r.old_fixed_grammar_result
  +" · REASON-020 corrected view: "+r.new_dual_circle_result;
 d("self").textContent="Prior grammar insufficient: "+r.original_017_was_inadequate
  +"\nTeacher-derived skill verified: "+
    records.independent_source_teacher_skill_certificate.self_capability_granted
  +"\nTemplates:\n"+printer(records.learned_program.templates);
 d("other").textContent="Source-owned revisions: "+r.source_revision
  +"\nNew quoted goal: "+(r.new_reported_goal||"none")
  +"\nRecipient source turns: "+r.recipient_source_turns;
 d("mirror").textContent="Projection report: "+r.projection_status
  +"\nNew concept versions:\n"+printer(r.concept_versions)
  +"\nExplicitly rejected concepts:\n"+printer(r.discarded_concepts);
 d("critic").textContent="Four-process critic eligible to suggest an options discussion: "+
  r.four_process_critic_approved+"\nExternal actions: FALSE\nPermission to execute: FALSE";
}
select.addEventListener("change",render);select.value=records.all_case_outcomes[0].case;render();
</script></body></html>'''


def build(benchmark,outfile):
    r=json.loads(Path(benchmark).read_text(encoding="utf8"))
    if (r.get("schema")!="motif.reason.golden-mirror-learns.benchmark.v1"
            or r.get("synthetic_scenarios")!=16
            or r.get("no_empathy_or_experienced_love_measured") is not True
            or r.get("external_actions") is not False):
        raise ValueError("Only complete, honest synthetic source records may be visualized")
    data=json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    # Prevent source text from ending the inert JSON script tag.
    data=data.replace("<","\\u003c").replace("&","\\u0026")
    out=Path(outfile);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(TEMPLATE.replace("__EVIDENCE__",data),encoding="utf8")
    return {"path":str(out),"bytes":out.stat().st_size,
            "case_count":len(r["all_case_outcomes"]),
            "external_requests":False}


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: python viewer.py benchmark.json golden-mirror-learns.html")
    print(json.dumps(build(sys.argv[1],sys.argv[2]),sort_keys=True))
