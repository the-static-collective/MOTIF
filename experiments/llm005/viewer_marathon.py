"""Render an 879+ event, 384-decision global serial Reason Hypermap replay.

The JavaScript only reads embedded author-public synthetic metadata; no external
calls, image generation, production owner receipts or mutation controls.
"""
from __future__ import annotations
import json

PAGE=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MOTIF ODYSSEY MARATHON — 879+ Causal Actions</title>
<style>
:root{color-scheme:dark;--bg:#111820;--panel:#1e2933;--ink:#f0f4f5;--dim:#b8c9d1;
--border:#455762;--gold:#efc684;--teal:#8ed0d7;--good:#a9dca9;--bad:#eca2ab}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;
padding:clamp(12px,2.4vw,30px);max-width:1720px;margin-inline:auto}
h1{font:400 clamp(30px,4vw,50px) Georgia,serif;margin:0}
h2{font-size:18px;margin:0 0 9px}h3{font-size:14px;margin:14px 0 6px;color:var(--gold)}
p{color:var(--dim);max-width:110ch;margin:5px 0 14px}.eyebrow{font-size:12px;letter-spacing:.18em;
text-transform:uppercase;color:var(--teal);margin-bottom:8px}
.notice{padding:12px 16px;background:#28333c;border-left:4px solid var(--gold);
color:#d0dae0;border-radius:4px;max-width:1150px;margin:17px 0}
header{margin-bottom:16px}
button,select,input{font:inherit;color:var(--ink);border-radius:7px;border:1px solid var(--border);
background:#2b3945;padding:10px}button{cursor:pointer;min-height:44px}
button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
label{display:flex;flex-direction:column;gap:6px;color:var(--dim)}
.row{display:flex;flex-wrap:wrap;align-items:end;gap:12px;margin:10px 0 17px}
.box{background:var(--panel);border:1px solid var(--border);border-radius:11px;padding:14px;min-width:0}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
#seek{width:min(100%,920px);flex:1;accent-color:var(--gold)}
.metrics{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:13px 0}
@media(max-width:920px){.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
.metric .big{font-size:clamp(20px,2.7vw,31px);font-weight:700;font-variant-numeric:tabular-nums}
.metric .small{font-size:12px;color:var(--dim)}
.bodygrid{display:grid;grid-template-columns:minmax(0,2.1fr) minmax(290px,1fr);gap:12px}
@media(max-width:1000px){.bodygrid{grid-template-columns:1fr}}
.chapters{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
@media(max-width:700px){.chapters{grid-template-columns:1fr}}
.chapter{background:#22313d;border:1px solid #4a5d6c;border-radius:9px;padding:12px}
.chapter header{display:flex;justify-content:space-between;align-items:center;margin:0 0 10px}
.chapter b{color:#e7ecee}.chapter small{color:var(--dim)}
.sectors{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
@media(max-width:1250px){.sectors{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:380px){.sectors{grid-template-columns:1fr}}
.sector{background:#1a2731;border:1px solid #3e5563;padding:8px;border-radius:6px}
.sector .top{display:flex;justify-content:space-between;align-items:center;font-size:11px;margin-bottom:6px}
.sector small{font-size:10px}
.gates{display:grid;grid-template-columns:repeat(8,1fr);gap:3px}
.g{height:23px;min-width:0;font:600 10px/1.3 system-ui;border-radius:3px;padding:0;
background:#374750;border:1px solid #51636e;cursor:pointer}
.g.done{background:#285041;color:#c4f4d0;border-color:#70a48b}
.g.wrong{background:#593a44;color:#fce7e7;border-color:#d494aa}
.g.survey{background:#39556a;color:#cceaf2;border-color:#7cafc4}
.g.probe{background:#514361;color:#e7cffa;border-color:#a28cb6}
.bar{height:4px;background:#425563;margin-top:5px;border-radius:2px;overflow:hidden}
.fill{height:100%;background:var(--good);width:0}
#detail{white-space:pre-wrap;word-break:break-word;color:#d4e4e9;
font-size:12px;background:#131e27;padding:12px;border:1px solid #3b5364;border-radius:8px;
max-height:490px;overflow:auto}
#resume{white-space:pre-wrap;color:var(--dim);font-size:13px}
table{border-collapse:collapse;width:100%;min-width:650px}
th,td{text-align:left;border-bottom:1px solid var(--border);padding:10px 8px}
th{color:var(--dim)}.twrap{overflow-x:auto}.live{background:#2e424b}
.tip{font-size:12px;color:var(--dim)}
</style></head><body>
<header>
<div class="eyebrow">Static Collective / MOTIF / LLM-005 / Post-hoc Length Escalation</div>
<h1>ODYSSEY: THE MARATHON</h1>
<p><strong>879 minimum serial actions. 384 individually verified decisions. 48 shifting rule contexts.
96 evidence audits. 12 relay stages. Three mandatory inter-world handoffs.</strong></p>
<p>Every checkpoint depends on its predecessor. Every transition can be revisited. Failed
provisional answers stay in history; they cannot be silently corrected into success.</p>
<div class="notice"><strong>Critical boundary:</strong> this is a deterministic author-designed fictional simulator
using MOTIF's typed Reason Hypermap, not a pretrained LLM, external physical task, or real user decision.
Handoffs and signatures below are consistency hashes, not real-world witness authentication.</div>
</header>
<div class="row">
<label>Policy<select id="policy"></select></label>
<div class="box"><div class="tip">Mandatory serial actions</div><div style="font-size:27px;font-weight:700">879</div></div>
<div class="box"><div class="tip">Fictional chained source worlds</div><div style="font-size:27px;font-weight:700">48</div></div>
<div class="box"><div class="tip">Registered scenario group</div><div id="group"></div></div>
</div>
<div class="box">
<div class="controls">
<button id="start" type="button">⟲ Beginning</button>
<button id="previous" type="button">←</button>
<button id="play" type="button">▶ Replay the marathon</button>
<button id="next" type="button">→</button>
<button id="jump" type="button">Next failure</button>
<button id="handoff" type="button">Next handoff</button>
</div>
<div class="controls" style="margin-top:8px"><span id="position" style="color:var(--gold)">0 / 0</span>
<input type="range" id="seek" value="0" min="0" max="1" aria-label="Scrub through over 879 causally linked steps"></div>
<div class="tip">Scrub through the source-linked action chain, or jump directly to the next error or
inter-segment handoff. Choose a stage to inspect source coordinates and prior hashes.</div>
</div>
<div class="metrics">
<div class="box metric"><div id="commits" class="big">0/384</div><div class="small">accepted decisions</div></div>
<div class="box metric"><div id="wrong" class="big">0</div><div class="small">wrong provisional commitments</div></div>
<div class="box metric"><div id="probes" class="big">0</div><div class="small">paid independent probes</div></div>
<div class="box metric"><div id="handoffs" class="big">0/3</div><div class="small">verified chain handoffs</div></div>
<div class="box metric"><div id="cost" class="big">0</div><div class="small">synthetic cost consumed</div></div>
</div>
<section class="bodygrid">
<div class="box">
<h2>48 source-specific reasoning sectors · 384 ordered decisions</h2>
<p>Each chapter is a complete 12-sector synthetic task. The next chapter does not
open until its predecessor and a global source-hash handoff are complete.</p>
<div id="chapters" class="chapters"></div>
</div>
<div class="box">
<h2>Inspect the chain</h2>
<div id="resume">Start at step 0.</div>
<h3>Immutable event and original child provenance</h3>
<pre id="detail">No current event.</pre>
</div>
</section>
<section class="box" style="margin-top:14px">
<h2>Four registered marathon groups · descriptive study</h2>
<p>Same source-owner rules and action/cost limits within each group. A failed subchain terminates
the marathon and cannot be hidden by reduced costs. No external benchmark or statistical superiority
is established from this small authored sample.</p>
<div class="twrap"><table><thead><tr><th>Policy</th><th>Fully finished marathons</th>
<th>Mean actions</th><th>Mean cost</th><th>Mean wrong commits</th>
<th>Mean completed decisions</th></tr></thead><tbody id="results"></tbody></table></div>
</section>
<footer style="font-size:12px;color:var(--dim);margin-top:20px">
Research-only. MOTIF LLM-005 / ODYSSEY-240 → MARATHON. Historical graph, source digest and cost
are not execution authority. No remote requests or personal sources.</footer>
<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
(()=>{
"use strict";
const D=JSON.parse(document.getElementById("payload").textContent);
const $=id=>document.getElementById(id);
const policyNames={hypermap_voi:"HYPERMAP — pay for useful evidence",
classical_bayes:"CLASSICAL BAYES — remember owner receipts",
static:"STATIC — no cross-checkpoint memory",
contrarian:"CONTRARIAN — deliberately reverse uncertainty"};
const sel=$("policy");
for(const p of Object.keys(D.records)){
 const option=document.createElement("option");
 option.value=p;option.textContent=policyNames[p]||p;sel.appendChild(option);
}
sel.value=D.records.hypermap_voi?"hypermap_voi":Object.keys(D.records)[0];
let current=sel.value,at=0,timer=null;
const get=()=>D.records[current].global_events;
$("group").textContent=D.group.join(" → ");
const chapterNodes=[];
for(let chapter=0;chapter<4;chapter++){
 const card=document.createElement("section");card.className="chapter";
 const head=document.createElement("header"),name=document.createElement("b");
 name.textContent="CHAPTER "+(chapter+1)+" / 4";
 const note=document.createElement("small");note.id="chapter-note-"+chapter;
 note.textContent="Unstarted";
 head.append(name,note);card.appendChild(head);
 const sectors=document.createElement("div");sectors.className="sectors";
 for(let s=0;s<12;s++){
   const group=document.createElement("div");group.className="sector";
   const top=document.createElement("div");top.className="top";
   const title=document.createElement("b");
   title.textContent="S"+String(chapter*12+s+1).padStart(2,"0");
   const audit=document.createElement("small");audit.id="audit-"+chapter+"-"+s;
   audit.textContent="locked";top.append(title,audit);
   group.appendChild(top);
   const row=document.createElement("div");row.className="gates";
   for(let gate=0;gate<8;gate++){
     const b=document.createElement("button");
     b.type="button";b.className="g";b.textContent=gate+1;
     b.id="gate-"+chapter+"-"+s+"-"+gate;
     b.setAttribute("aria-label","Chapter "+(chapter+1)+" sector "+(s+1)+" checkpoint "+(gate+1));
     b.addEventListener("click",()=>inspectGate(chapter,s,gate));
     row.appendChild(b);
   }
   group.appendChild(row);
   const bar=document.createElement("div");bar.className="bar";
   const fill=document.createElement("div");fill.className="fill";
   fill.id="fill-"+chapter+"-"+s;bar.appendChild(fill);
   group.appendChild(bar);sectors.appendChild(group);
 }
 card.appendChild(sectors);$("chapters").appendChild(card);
 chapterNodes.push(card);
}
function inspectGate(chapter,sector,gate){
 const rows=get().filter(e=>e.kind==="odyssey_action"&&e.segment===chapter&&
   e.payload.child_sector===sector&&e.payload.child_gate===gate);
 const earlier=rows.filter(e=>e.index<=at);
 const e=earlier.length?earlier[earlier.length-1]:rows[0];
 if(!e){$("resume").textContent="That source-gated checkpoint was never executed.";return}
 $("detail").textContent=JSON.stringify(e,null,2);
 $("resume").textContent="Selected: chapter "+(chapter+1)+", sector "+(sector+1)+
 ", gate "+(gate+1)+", source-trace event "+e.index+".";
}
function draw(){
 const events=get(),partial=events.slice(0,at);
 const status=Array.from({length:4},()=>Array.from({length:12},()=>Array(8).fill("locked")));
 const audits=Array.from({length:4},()=>Array.from({length:12},()=>({half:false,terminal:false,relay:false})));
 let correct=0,wrong=0,probes=0,handoffs=0,cost=0;
 for(const e of partial){
   if(e.kind==="mandatory_handoff"){handoffs++;cost=e.cumulative_cost;continue}
   if(e.kind!=="odyssey_action")continue;
   const p=e.payload,ch=e.segment,s=p.child_sector,j=p.child_gate;
   const k=p.child_kind;
   if(k==="survey")status[ch][s][j]="survey";
   if(k==="independent_probe"){status[ch][s][j]="probe";probes++}
   if(k==="commit_wrong"){status[ch][s][j]="wrong";wrong++}
   if(k==="commit_correct"||k==="commit_repaired"){status[ch][s][j]="done";correct++}
   if(k==="half_audit")audits[ch][s].half=true;
   if(k==="terminal_audit")audits[ch][s].terminal=true;
   if(k==="bridge_relay")audits[ch][s].relay=true;
   cost=e.cumulative_cost;
 }
 for(let ch=0;ch<4;ch++){
   let chapterComplete=0;
   for(let s=0;s<12;s++){
     let complete=0;
     for(let j=0;j<8;j++){
       const b=$("gate-"+ch+"-"+s+"-"+j);
       b.className="g "+status[ch][s][j];
       if(status[ch][s][j]==="done")complete++;
     }
     chapterComplete+=complete;
     $("fill-"+ch+"-"+s).style.width=(complete/8*100)+"%";
     const a=audits[ch][s];
     $("audit-"+ch+"-"+s).textContent=a.relay?"relay ✓":
       a.terminal?"terminal ✓":a.half?"half ✓":"locked";
   }
   $("chapter-note-"+ch).textContent=chapterComplete+" / 96 accepted gates";
 }
 $("commits").textContent=correct+" / 384";
 $("wrong").textContent=wrong;$("probes").textContent=probes;
 $("handoffs").textContent=handoffs+" / 3";
 $("cost").textContent=cost.toFixed(2);
 $("position").textContent="Action "+at+" / "+events.length;
 $("seek").max=events.length;$("seek").value=at;
 const e=at?events[at-1]:null;
 if(!e){$("resume").textContent="All worlds are still blocked. No provisional decisions have been made.";
   $("detail").textContent="No current event."}
 else{
   const ch=e.segment+1;
   if(e.kind==="mandatory_handoff"){
     $("resume").textContent="MANDATORY WORLD-HANDOFF after chapter "+ch+
     ". Its previous terminal digest is bound into the global chain before chapter "+(ch+1)+" begins.";
   }else{
     $("resume").textContent="Action "+e.index+" · chapter "+ch+", sector "+(e.payload.child_sector+1)+
       ", gate "+(e.payload.child_gate+1)+". Event: "+e.payload.child_kind+
       ". Every step retains an immutable previous global digest and original child-event hash.";
   }
   $("detail").textContent=JSON.stringify(e,null,2);
 }
 $("play").textContent=timer?"Ⅱ Pause":"▶ Replay the marathon";
 const body=$("results");body.replaceChildren();
 for(const arm of D.study.arms){
   const tr=document.createElement("tr");if(arm.policy===current)tr.className="live";
   const vals=[policyNames[arm.policy]||arm.policy,arm.full_completions+" / "+arm.marathons,
     arm.mean_serial_actions,arm.mean_synthetic_cost,arm.mean_wrong_commits,arm.mean_completed_decisions];
   for(const v of vals){const td=document.createElement("td");td.textContent=v;tr.appendChild(td)}
   body.appendChild(tr);
 }
}
function stop(){if(timer){clearInterval(timer);timer=null}}
function seek(v){at=Math.max(0,Math.min(get().length,Number(v)||0));draw()}
function play(){
 if(timer){stop();draw();return}
 if(at>=get().length)at=0;
 timer=setInterval(()=>{if(at>=get().length){stop();draw();return}at++;draw()},35);
 draw();
}
sel.addEventListener("change",()=>{stop();current=sel.value;at=0;draw()});
$("seek").addEventListener("input",e=>{stop();seek(e.target.value)});
$("start").addEventListener("click",()=>{stop();seek(0)});
$("previous").addEventListener("click",()=>{stop();seek(at-1)});
$("next").addEventListener("click",()=>{stop();seek(at+1)});
$("play").addEventListener("click",play);
$("jump").addEventListener("click",()=>{
 stop();const i=get().findIndex((e,j)=>j>=at&&e.kind==="odyssey_action"&&e.payload.child_kind==="commit_wrong");
 seek(i<0?get().length:i+1);
});
$("handoff").addEventListener("click",()=>{
 stop();const i=get().findIndex((e,j)=>j>=at&&e.kind==="mandatory_handoff");
 seek(i<0?get().length:i+1);
});
draw();
})();
</script></body></html>'''

def render(data):
    if data.get("schema")!="motif.odyssey-marathon.viewer/v0" or not data.get("records"):
        raise ValueError("BAD_MARATHON_VIEWER")
    if data.get("study",{}).get("author_synthetic_only") is not True:
        raise ValueError("NON_SYNTHETIC_STUDY")
    for p,r in data["records"].items():
        if (r.get("schema")!="motif.odyssey-marathon/v0" or
            not r.get("hidden_owner_truth_excluded") or
            r.get("external_actions") is not False or r.get("authority")!="none"):
            raise ValueError("UNSAFE_MARATHON_RECORD")
    safe=json.dumps(data,ensure_ascii=False,sort_keys=True).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    return PAGE.replace("__PAYLOAD__",safe)

if __name__=="__main__":
    from pathlib import Path
    import sys
    src,dst=Path(sys.argv[1]),Path(sys.argv[2])
    page=render(json.loads(src.read_text()))
    dst.write_text(page)
    print("MARATHON_VIEWER",dst,"BYTES",len(page.encode()))
