"""OFFLINE long-chain visualizer: interactive decision lattice and hypermap evidence.

Accepts only public authored synthetic fixture traces. No remote fonts,
scripts, network fetch, personal data, or real-world authorization. The
user can scrub any one of 200+ executed sequential actions and inspect the
source-rooted conditional progress. Not an image; genuine interactive HTML.
"""
from __future__ import annotations
import json
from pathlib import Path

MARKUP=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MOTIF ODYSSEY-240 — Long Reason Chain</title>
<style>
:root{color-scheme:dark;--bg:#10141a;--surface:#1b232a;--line:#394650;--muted:#b3c2c9;--bright:#f2f2ed;--blue:#9ec8d7;--amber:#f0c582;--rose:#e99da3;--green:#abdab0;--purple:#c8afe3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--bright);font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;padding:clamp(12px,2.6vw,30px)}
h1{font-family:Georgia,serif;font-size:clamp(27px,4vw,45px);margin:0 0 8px;font-weight:500}
h2{font-size:17px;margin:0 0 8px}h3{font-size:14px;color:var(--amber);margin:17px 0 6px}
p{color:var(--muted);margin:5px 0 13px;max-width:99ch}
a{color:var(--blue)}label{display:flex;flex-direction:column;gap:5px;color:var(--muted)}
button,select,input{font:inherit;color:var(--bright);background:#27323b;border:1px solid var(--line);border-radius:8px;padding:8px}
button{cursor:pointer;min-height:42px}button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
small{color:var(--muted)}strong,.highlight{color:var(--amber)}.eyebrow{color:var(--blue);letter-spacing:.13em;font-size:12px;text-transform:uppercase}
.notice{border-left:4px solid var(--amber);background:#262b30;padding:11px 14px;max-width:1100px;margin:15px 0}
.row{display:flex;align-items:flex-end;gap:12px;flex-wrap:wrap;margin:20px 0}
.frame{background:var(--surface);border:1px solid var(--line);padding:15px;border-radius:10px;min-width:0}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin:11px 0 16px}
@media(max-width:700px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.stat .number{font-size:clamp(18px,3vw,30px);font-weight:650;font-variant-numeric:tabular-nums}
.stat .caption{color:var(--muted);font-size:12px}
.controls{display:flex;gap:13px;flex-wrap:wrap;align-items:center}
#seek{width:min(100%,760px);flex:1;accent-color:var(--amber);min-height:30px}
.pair{display:grid;grid-template-columns: minmax(0,1.7fr) minmax(320px,1fr);gap:14px;margin:15px 0}
@media(max-width:930px){.pair{grid-template-columns:1fr}}
.sectors{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media(max-width:700px){.sectors{grid-template-columns:1fr}}
.sector{background:#202b33;border:1px solid #3a4751;padding:12px;border-radius:9px}
.sector-head{display:flex;justify-content:space-between;align-items:center;color:#d9e5e7;margin-bottom:8px}
.sector-head .audit{font-size:11px;color:var(--muted)}
.chain{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:5px}
.gate{min-width:0;height:40px;border-radius:6px;background:#323f49;border:1px solid #53626e;
color:#b7c5cb;font-weight:600;position:relative;cursor:pointer;font-variant-numeric:tabular-nums}
.gate.done{background:#284334;border-color:#5eaa7a;color:#e3f7e8}
.gate.wrong{background:#583136;border-color:#d98f9b;color:#ffe5e9}
.gate.repaired{background:#40513b;border-color:#bdd18e;color:#f5f5d8}
.gate.surveyed{background:#344852;border-color:#91c3cf;color:#e0f6ff}
.gate.probed{background:#493f57;border-color:#a68bcb;color:#f1e4ff}
.gate:focus-visible{outline:2px solid #fff}
.bar{height:5px;margin-top:7px;border-radius:8px;background:#3d4a54;overflow:hidden}
.bar>div{height:100%;width:0;background:var(--green);transition:width .08s linear}
.note{font-size:11px;color:var(--muted);margin-top:6px}
pre{background:#121a1f;border:1px solid #3d4b56;border-radius:7px;padding:12px;max-height:440px;overflow:auto;overflow-wrap:anywhere;white-space:pre-wrap;color:#d5e0e4;font-size:12px}
table{width:100%;border-collapse:collapse;min-width:640px}th,td{text-align:left;border-bottom:1px solid #38464d;padding:9px 10px}
th{color:var(--muted);font-size:12px;letter-spacing:.04em}td{font-variant-numeric:tabular-nums}
.table-scroll{overflow:auto}tr.hot{background:#293a42}tr:hover{background:#303c42}
.muted{color:var(--muted)}.good{color:var(--green)}.bad{color:var(--rose)}
code{color:var(--blue);word-break:break-all}.legend{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}
.swatch{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:-2px}
hr{border:0;border-top:1px solid var(--line);margin:15px 0}
#reasonLink{padding:8px;background:#2a3540;border-radius:8px;min-height:56px;white-space:pre-wrap;overflow-wrap:anywhere}
footer{margin-top:23px;color:var(--muted);font-size:12px}
</style></head><body>
<header>
<div class="eyebrow">THE STATIC COLLECTIVE / MOTIF / LLM-005</div>
<h1>ODYSSEY-240</h1>
<p>A deliberately unreasonable, source-verified <strong>sequential reasoning chain</strong>.
Twelve changing hidden worlds. Ninety-six decisions. Surveys, evidence tests, repairs,
24 audits and 3 relay dependencies. Every past decision stays in the record.</p>
<div class="notice"><strong>Research fixture only.</strong> All people, rules, resources, sources and actions here are
synthetic. Policies cannot access the hidden rule. Wrong guesses are PENCIL-only.
This is not a demonstration that an LLM solved the chain: these are programmatic
reasoning policies using MOTIF's source-owned Hypermap, not pretrained weights.</div>
</header>
<div class="row">
<label>Reasoning policy<select id="policy"></select></label>
<div class="frame"><small>Minimum successful causal chain</small><div style="font-size:23px;font-weight:700">219 required actions</div></div>
<div class="frame"><small>Scenario</small><div id="scenario" style="font-size:20px;font-weight:650"></div></div>
</div>
<div class="frame">
<div class="controls">
<button type="button" id="first">⟲ Restart</button>
<button type="button" id="back">← One step</button>
<button type="button" id="play">▶ Replay</button>
<button type="button" id="forward">One step →</button>
<button type="button" id="jumpError">Next wrong guess</button>
</div>
<div class="controls" style="margin:8px 0"><span id="progress" class="highlight">0 / 0</span>
<input id="seek" type="range" min="0" max="1" value="0" aria-label="Scrub through reason chain steps"></div>
<small>Scrub the chain or play it through. Every sector waits for its required predecessor and audits. This is a single serial chain, not a collage of unrelated questions.</small>
</div>
<div class="stats">
<div class="frame stat"><div id="completed" class="number">0 / 96</div><div class="caption">verified and completed decisions</div></div>
<div class="frame stat"><div id="spent" class="number">0</div><div class="caption">synthetic cost spent</div></div>
<div class="frame stat"><div id="wrong" class="number">0</div><div class="caption">wrong provisional commitments</div></div>
<div class="frame stat"><div id="probes" class="number">0</div><div class="caption">optional independent verifications</div></div>
</div>
<section class="pair">
<div class="frame">
<h2>Dependency graph · every cell requires the preceding cell</h2>
<p>All eight checkpoints in each sector must pass before its terminal audit. Sector changes
reset the hidden rule. Every fourth sector also requires a relay before proceeding.</p>
<div class="legend">
<span><i class="swatch" style="background:#284334"></i>Accepted</span>
<span><i class="swatch" style="background:#583136"></i>Wrong / needs repair</span>
<span><i class="swatch" style="background:#344852"></i>Surveyed</span>
<span><i class="swatch" style="background:#493f57"></i>Independent probe</span>
<span><i class="swatch" style="background:#323f49"></i>Blocked / unknown</span>
</div>
<div id="sectors" class="sectors"></div>
</div>
<div class="frame">
<h2>Current witnessed transition</h2>
<div id="current"></div>
<h3>Source-bound reasoning detail</h3>
<div id="reasonLink" class="muted">Select an action to inspect the evidence that changed the next possible decision.</div>
<h3>Exact event record</h3>
<pre id="eventJson"></pre>
</div>
</section>
<section class="frame">
<h2>64-world comparison · same gates, distinct strategies</h2>
<p>The table below is the actual held-out authored-simulator study across four policies. Completion under
action and cost budgets is primary; faster early termination by failure is not a victory.
Every policy sees the same calibration and source-owner results for a given world.</p>
<div class="table-scroll"><table><thead><tr>
<th>Policy</th><th>Completed / 64</th><th>Mean actions</th><th>Mean cost</th>
<th>Mean wrong commits</th><th>Optional probes</th><th>Useful corrections retained</th></tr></thead>
<tbody id="compare"></tbody></table></div>
<div class="notice"><strong>Scientific interpretation:</strong> A wrong provisional hypothesis is useful only
when an independent correction changes later decisions enough to justify the cost.
In this experiment, classical Bayes is a strong baseline. These authored Boolean puzzles
do not demonstrate general intelligence or novel mathematical reasoning.</div>
</section>
<footer>Source: MOTIF LLM-005 | Typed memory: LLM-004 Reason Hypermap | All payloads from public authored fixtures
| Read-only offline HTML | Zero external requests, owner permissions, deployments or physical effects.</footer>
<script id="data" type="application/json">__PAYLOAD__</script>
<script>
(()=>{
"use strict";
const DATA=JSON.parse(document.getElementById("data").textContent);
const $=id=>document.getElementById(id);
const LABELS={static:"STATIC — no later memory",classical_bayes:"CLASSICAL BAYES — source memory",
hypermap_voi:"HYPERMAP — value-of-verification",contrarian:"CONTRARIAN — deliberate provisional error"};
const policies=Object.keys(DATA.traces), select=$("policy");
for(const p of policies){const o=document.createElement("option");o.value=p;o.textContent=LABELS[p]||p;select.appendChild(o)}
select.value=policies.includes("hypermap_voi")?"hypermap_voi":policies[0];
$("scenario").textContent="Fictional owner seed "+DATA.seed;
let active=select.value,index=0,timer=null,lookup=[];
const rows=$("sectors");
for(let s=0;s<12;s++){
 const el=document.createElement("div");el.className="sector";
 const head=document.createElement("div");head.className="sector-head";
 const title=document.createElement("strong");title.textContent="SECTOR "+String(s+1).padStart(2,"0");
 const badge=document.createElement("span");badge.className="audit";badge.id="audit-"+s;badge.textContent="Locked";
 head.append(title,badge);el.appendChild(head);
 const chain=document.createElement("div");chain.className="chain";
 for(let j=0;j<8;j++){
   const btn=document.createElement("button");btn.type="button";btn.textContent=String(j+1);
   btn.className="gate";btn.id="gate-"+s+"-"+j;
   btn.setAttribute("aria-label","Sector "+(s+1)+" checkpoint "+(j+1));
   btn.addEventListener("click",()=>inspectGate(s,j));chain.appendChild(btn);
 }
 el.appendChild(chain);
 const bar=document.createElement("div");bar.className="bar";const fill=document.createElement("div");
 fill.id="bar-"+s;bar.appendChild(fill);el.appendChild(bar);
 const foot=document.createElement("div");foot.className="note";foot.id="stage-"+s;foot.textContent="Evidence awaits";el.appendChild(foot);
 rows.appendChild(el);
}
function getTrace(){return DATA.traces[active]}
function events(){return getTrace().events}
function rebuild(){
 const status=Array.from({length:12},()=>Array(8).fill("blocked"));
 const audits=Array.from({length:12},()=>({half:false,terminal:false,bridge:false}));
 let commits=0,wrong=0,probes=0,cost=0;
 const trail=events().slice(0,index);
 for(const e of trail){
   const s=e.sector,j=e.gate;
   if(e.kind==="survey")status[s][j]="surveyed";
   if(e.kind==="independent_probe"){status[s][j]="probed";probes++}
   if(e.kind==="commit_wrong"){status[s][j]="wrong";wrong++}
   if(e.kind==="repair")status[s][j]="wrong";
   if(e.kind==="commit_correct"||e.kind==="commit_repaired"){status[s][j]="done";commits++}
   if(e.kind==="half_audit")audits[s].half=true;
   if(e.kind==="terminal_audit")audits[s].terminal=true;
   if(e.kind==="bridge_relay")audits[s].bridge=true;
   cost=e.cumulative_cost;
 }
 for(let s=0;s<12;s++){
   let n=0;
   for(let j=0;j<8;j++){
     const b=$("gate-"+s+"-"+j);b.className="gate "+status[s][j];
     if(status[s][j]==="done")n++;
     b.setAttribute("aria-label","Sector "+(s+1)+" checkpoint "+(j+1)+" is "+status[s][j]);
   }
   $("bar-"+s).style.width=(n*12.5)+"%";
   let marks=[];
   if(audits[s].half)marks.push("½ audit");
   if(audits[s].terminal)marks.push("terminal audit");
   if(audits[s].bridge)marks.push("relay ✓");
   $("audit-"+s).textContent=marks.join(" · ")||"Unverified";
   $("stage-"+s).textContent=n+" / 8 gates accepted · "+(s>0?"preceded by prior sector":"first sector");
 }
 $("completed").textContent=commits+" / 96";
 $("wrong").textContent=wrong;
 $("probes").textContent=probes;
 $("spent").textContent=cost.toFixed(2);
 $("seek").max=String(events().length);$("seek").value=String(index);
 $("progress").textContent="Action "+index+" / "+events().length;
 const e=index?events()[index-1]:null;
 if(e){
   $("current").textContent="Action "+e.action+": "+e.kind.replaceAll("_"," ")+" · sector "+
       (e.sector+1)+", checkpoint "+(e.gate+1)+" · current cumulative cost "+e.cumulative_cost;
   $("eventJson").textContent=JSON.stringify(e,null,2);
   inspectEvidence(e);
 }else{
   $("current").textContent="Nothing has happened. All 96 gate decisions are still blocked.";
   $("eventJson").textContent="No event at step 0.";
   $("reasonLink").textContent="Choose an action or start replay.";
 }
 $("play").textContent=timer?"Ⅱ Pause":"▶ Replay";
}
function inspectEvidence(e){
 const div=getTrace().reason_dividends||[];
 const d=div.find(r=>r.sector===e.sector&&r.gate===e.gate);
 const root=e.meta?.source_root||d?.source_root||null;
 if(e.kind==="survey"){
   $("reasonLink").textContent="SURVEY: only the problem input was revealed. The hint uses a repeatedly forwarded rumor root and is NOT an independent source. No hidden answer was disclosed.";
   return;
 }
 if(!d){
   $("reasonLink").textContent="DEPENDENCY/AUDIT: this milestone summarizes previously verified source receipts. It does not invent a fresh independent witness.";
   return;
 }
 const msg=["Typed source root: "+(root||d.source_root),
  "Test type: "+d.test_kind,
  "Reported contradiction: "+(d.reported_contradiction?"yes":"no"),
  "Independently verified counterexample (simulated): "+(d.verified_counterexample?"yes":"no"),
  "Change in independently owner-scored later prediction accuracy after cost: "+d.net_owner_accuracy_gain,
  "Memory used by current policy: "+(d.model_learning_used_by_policy?"yes":"no")];
 const maps=DATA.reason_maps||{};
 const ownerMap=maps[String(e.sector)];
 if(active==="hypermap_voi"&&ownerMap){
   const matching=(ownerMap.events||[]).find(r=>r.source_root===d.source_root);
   if(matching){
     const h=ownerMap.hyperedges[matching.hyperedge];
     if(h){
       const labels=ids=>(ids||[]).map(id=>ownerMap.nodes[id]?.label||id);
       msg.push("HYPEREDGE INPUTS: "+labels(h.tails).join(" | "));
       msg.push("HYPEREDGE RESULTS: "+labels(h.heads).join(" | "));
       msg.push("This is a multi-terminal relation, not a truth/permission certificate.");
     }
   }
 }
 $("reasonLink").textContent=msg.join("\n");
}
function inspectGate(s,j){
 const matches=events().filter(e=>e.sector===s&&e.gate===j);
 if(matches.length===0){$("reasonLink").textContent="Checkpoint has not been visited in this run.";return}
 const upto=events().slice(0,index).filter(e=>e.sector===s&&e.gate===j);
 const x=upto.length?upto[upto.length-1]:matches[0];
 $("eventJson").textContent=JSON.stringify(x,null,2);
 inspectEvidence(x);
}
function stop(){if(timer){clearInterval(timer);timer=null}}
function setIndex(v){index=Math.max(0,Math.min(events().length,Number(v)||0));rebuild()}
function play(){
 if(timer){stop();rebuild();return}
 if(index>=events().length)index=0;
 timer=setInterval(()=>{if(index>=events().length){stop();rebuild();return}index++;rebuild()},90);
 rebuild();
}
select.addEventListener("change",()=>{stop();active=select.value;index=0;fillComparison();rebuild()});
$("seek").addEventListener("input",e=>{stop();setIndex(e.target.value)});
$("first").addEventListener("click",()=>{stop();setIndex(0)});
$("back").addEventListener("click",()=>{stop();setIndex(index-1)});
$("forward").addEventListener("click",()=>{stop();setIndex(index+1)});
$("play").addEventListener("click",play);
$("jumpError").addEventListener("click",()=>{
 stop();const i=events().findIndex((e,j)=>j>=index&&e.kind==="commit_wrong");
 setIndex(i<0?events().length:i+1);
});
function fillComparison(){
 const body=$("compare");body.replaceChildren();
 for(const arm of DATA.study.arms){
   const row=document.createElement("tr");
   if(arm.policy===active)row.className="hot";
   const values=[LABELS[arm.policy]||arm.policy,
      arm.completed+" / "+arm.worlds,arm.mean_actions,arm.mean_cost,
      arm.mean_wrong_commits,arm.mean_optional_probes,arm.total_learned_counterexamples];
   for(const val of values){const td=document.createElement("td");td.textContent=val;row.appendChild(td)}
   body.appendChild(row);
 }
}
fillComparison();rebuild();
})();
</script></body></html>'''

def render(payload):
    if payload.get("schema")!="motif.odyssey-viewer/v0" or not isinstance(payload.get("traces"),dict):
        raise ValueError("UNRECOGNIZED_VIEWER_DATA")
    if payload.get("study",{}).get("author_synthetic_only") is not True:
        raise ValueError("NONPUBLIC_STUDY")
    if any(t.get("schema")!="motif.odyssey-240/v0" or not t.get("hidden_owner_truth_excluded")
           or t.get("external_actions") is not False for t in payload["traces"].values()):
        raise ValueError("UNSAFE_SOURCE_OR_AUTHORITY")
    if not payload["traces"]:raise ValueError("MISSING_TRACES")
    safe=json.dumps(payload,sort_keys=True,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    return MARKUP.replace("__PAYLOAD__",safe)

if __name__=="__main__":
    import sys
    src,dst=Path(sys.argv[1]),Path(sys.argv[2])
    page=render(json.loads(src.read_text()))
    dst.write_text(page,encoding="utf-8")
    print("ODYSSEY_VIEWER",dst,"BYTES",len(page.encode("utf-8")))
