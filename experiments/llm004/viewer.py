"""Generate a self-contained, offline, READ-ONLY human Reason Hypermap.

This displays only public authored synthetic map snapshots. The browser has
no network calls, model calls, mutations or source authority. The rendered
graph is from the engine's JSON output; no invented diagram topology.
"""
from __future__ import annotations
import html,json
from pathlib import Path

TEMPLATE=r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MOTIF Reason Hypermap — Synthetic Research Specimen</title>
<style>
:root{color-scheme:dark;font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;
--bg:#12151a;--panel:#1c2229;--line:#465460;--text:#eff3f4;--muted:#b0bec8;
--blue:#93c8d9;--warm:#e5be7d;--rose:#e39da5;--green:#9bcea5}
*{box-sizing:border-box}body{margin:0;padding:clamp(12px,2.6vw,30px);background:var(--bg);color:var(--text)}
a{color:var(--blue)}header{max-width:1100px}h1{font-family:Georgia,serif;
font-size:clamp(27px,4vw,42px);margin:0 0 8px}h2{font-size:18px;margin:0 0 9px}
p{margin:6px 0 12px;color:var(--muted);max-width:100ch}.strap{text-transform:uppercase;
letter-spacing:.16em;color:var(--warm);font-size:12px}
kbd{padding:2px 5px;border:1px solid var(--line);border-radius:4px}
aside{background:#242c34;border-left:3px solid var(--warm);padding:10px 14px;
color:var(--muted);margin:15px 0 20px}
.controls{display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin:16px 0}
label{display:flex;gap:6px;flex-direction:column;color:var(--muted);min-width:190px}
select,button{font:inherit;color:var(--text);background:var(--panel);
border:1px solid var(--line);border-radius:7px;padding:10px;min-height:44px}
button{cursor:pointer}button:focus-visible,select:focus-visible{outline:2px solid var(--blue);outline-offset:3px}
.grid{display:grid;grid-template-columns:minmax(0,3fr) minmax(250px,1fr);gap:15px}
@media(max-width:850px){.grid{grid-template-columns:minmax(0,1fr)}}
.box{background:var(--panel);border:1px solid #34414b;border-radius:11px;padding:14px;min-width:0}
.map-scroll{overflow-x:auto;max-width:100%;border:1px solid #34414b;border-radius:8px;background:#151b21}
svg{width:1150px;height:680px;display:block}
.path{fill:none;stroke:#607786;stroke-width:1.1;opacity:.45}
.path.active{stroke:#e5be7d;stroke-width:1.7;opacity:.9}
.port{stroke:#151b21;stroke-width:2;cursor:pointer}
.port:focus{stroke:#fff;stroke-width:3}
.pointlabel{fill:#edf3f4;font-size:12px;pointer-events:none}
.hub{fill:#8d9ea8;stroke:#20292e;stroke-width:2;cursor:pointer}
.hub.active{fill:#e5be7d}
.hub-label{fill:#b8c4cc;font-size:10px;pointer-events:none}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.5;color:#d5e1e7;max-height:420px;overflow:auto}
.legend{display:flex;gap:15px;flex-wrap:wrap;margin:10px 0;color:var(--muted);font-size:12px}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px}
.posterior-row{display:grid;grid-template-columns:32px 1fr 50px;gap:8px;
align-items:center;font-size:12px;margin:8px 0}
.track{height:10px;background:#303b44;border-radius:4px;overflow:hidden}
.fill{height:100%;background:var(--blue)}
.event-status{font-weight:700;color:var(--warm)}
.small{font-size:12px;color:var(--muted)}
</style>
</head>
<body>
<header>
<div class="strap">MOTIF / LLM-004 / research fixture</div>
<h1>Reason Hypermap</h1>
<p>A navigable memory of what was believed, what was tested, what evidence arrived,
and which possibilities changed. The map separates a provisional mistake from
the verified learning it might produce.</p>
<aside><strong>Public synthetic specimen only.</strong> Every named hypothesis and
report in this visualization comes from an authored simulator. No real user,
person, permission, engineering measurement, or project decision is represented.
Changing a lens does not change evidence or confer authority.</aside>
</header>
<div class="controls">
<label>Reasoning lens<select id="lens">
<option value="causal">Causal — test → consequence</option>
<option value="epistemic">Epistemic — competing claims</option>
<option value="decision">Decision — changed possibilities</option>
<option value="lineage">Lineage — why this test exists</option>
<option value="narrative">Narrative — history of correction</option>
</select></label>
<label>Investigative event<select id="event"></select></label>
<button type="button" id="reset">Show complete map</button>
</div>
<section class="grid">
<div class="box">
<h2 id="lensTitle">Reasoning connections</h2>
<div class="map-scroll" tabindex="0" role="region" aria-label="Scroll horizontally to explore the synthetic reason graph">
<svg id="plot" viewBox="0 0 1150 680" role="img" aria-label="Actual typed hypothesis nodes, tested receipts and hyperedges from the selected authored fixture."></svg>
</div>
<div class="legend">
<span><span class="dot" style="background:#93c8d9"></span>Hypotheses</span>
<span><span class="dot" style="background:#e5be7d"></span>Tests / predictions</span>
<span><span class="dot" style="background:#9bcea5"></span>Source reports</span>
<span><span class="dot" style="background:#e39da5"></span>Contradictions / revisions</span>
</div>
<div class="small" id="counts"></div>
</div>
<div class="box">
<h2>Selected record</h2>
<div class="small">Select a circle or square on the map to inspect its sources and exact relation.</div>
<pre id="detail" aria-live="polite">Select a source record.</pre>
<hr style="border:0;border-top:1px solid #43515c;margin:15px 0">
<h2>Current hypothetical posterior</h2>
<div id="posterior"></div>
<hr style="border:0;border-top:1px solid #43515c;margin:15px 0">
<h2>Experimental event</h2>
<div id="eventDetail" class="small"></div>
</div>
</section>
<p class="small">Export format: MOTIF reason-hypermap/v0 with reified many-to-many
relations. Independent Free Graph v0 projection validates historical traversability,
not truth or local adoption. This viewer is entirely offline and read-only.</p>
<script id="specimen" type="application/json">__PAYLOAD__</script>
<script>
(()=>{
"use strict";
const map=JSON.parse(document.getElementById("specimen").textContent);
const ids=Object.keys(map.nodes);
const root=document.getElementById("plot");
const svgNS="http://www.w3.org/2000/svg";
const xs={hypothesis:100,observation:100,prediction:370,test:510,
          receipt:745,counterexample:1000,revision:1000,question:1010};
const slots={hypothesis:0,observation:0,prediction:1,test:1,
             receipt:2,counterexample:3,revision:3,question:3};
const groups=[[],[],[],[]];
ids.forEach(id=>groups[slots[map.nodes[id].kind]??3].push(id));
const pos={};
groups.forEach((items,k)=>items.forEach((id,i)=>{
  const n=items.length;
  pos[id]={x:xs[map.nodes[id].kind]??(150+k*280),
           y:64+(i+.5)*560/Math.max(n,1)};
}));
const hue={hypothesis:"#93c8d9",observation:"#a9bdd0",prediction:"#e5be7d",
           test:"#e5be7d",receipt:"#9bcea5",counterexample:"#e39da5",
           revision:"#e39da5",question:"#b7c4cc"};
const connections={
  causal:()=>true,
  epistemic:e=>["report-bears-on-rivals","report-supports-rivals"].includes(e.relation),
  decision:e=>e.relation==="test-revises-possibilities",
  lineage:e=>e.relation==="proposes-test",
  narrative:e=>e.relation==="test-revises-possibilities"
};
const descriptions={
  causal:"Causal lens · which tested reports led to changes?",
  epistemic:"Epistemic lens · which rivals did a report bear on?",
  decision:"Decision lens · what did a test revise?",
  lineage:"Lineage lens · where did the test proposal come from?",
  narrative:"Narrative lens · how did the belief story change?"
};
let focused=null;
function el(tag,attributes={},parent=root){
  const n=document.createElementNS(svgNS,tag);
  for(const [key,value] of Object.entries(attributes))n.setAttribute(key,String(value));
  parent.appendChild(n);return n;
}
function show(record){document.getElementById("detail").textContent=JSON.stringify(record,null,2)}
function coordsForHub(edge,index){
  const pts=[...edge.tails,...edge.heads].map(id=>pos[id]).filter(Boolean);
  const ax=pts.reduce((z,p)=>z+p.x,0)/Math.max(pts.length,1);
  const ay=pts.reduce((z,p)=>z+p.y,0)/Math.max(pts.length,1);
  return {x:Math.min(935,Math.max(240,ax)),y:Math.min(630,Math.max(48,ay+((index%5)-2)*19))};
}
function line(a,b,active){
  el("path",{d:"M"+a.x+","+a.y+" Q"+((a.x+b.x)/2)+","+
     (a.y-22)+" "+b.x+","+b.y,
     class:"path"+(active?" active":"")});
}
function draw(){
  while(root.firstChild)root.removeChild(root.firstChild);
  const lens=document.getElementById("lens").value;
  const edges=Object.entries(map.hyperedges).filter(([id,e])=>connections[lens](e));
  document.getElementById("lensTitle").textContent=descriptions[lens];
  edges.forEach(([id,e],i)=>{
    const hub=coordsForHub(e,i);
    e.tails.forEach(n=>{if(pos[n])line(pos[n],hub,false)});
    e.heads.forEach(n=>{if(pos[n])line(hub,pos[n],true)});
    const h=el("rect",{x:hub.x-6,y:hub.y-6,width:12,height:12,rx:2,
                fill:"#e5be7d",class:"hub",tabindex:0,role:"button",
                "aria-label":"Inspect hyperedge "+e.relation});
    h.addEventListener("click",()=>show({id,...e}));
    h.addEventListener("keydown",ev=>{
      if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();show({id,...e})}
    });
  });
  ids.forEach(id=>{
    const n=map.nodes[id],p=pos[id];
    const c=el("circle",{cx:p.x,cy:p.y,r:11,
      fill:hue[n.kind]||"#a8b4bf",class:"port",tabindex:0,role:"button",
      "aria-label":"Inspect "+n.kind+" "+n.label});
    const label=el("text",{x:p.x,y:p.y+26,
       "text-anchor":"middle",class:"pointlabel"});
    label.textContent=n.label.length>26?n.label.slice(0,25)+"…":n.label;
    const inspect=()=>{focused=id;show({id,...n})};
    c.addEventListener("click",inspect);
    c.addEventListener("keydown",ev=>{
      if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();inspect()}
    });
  });
  document.getElementById("counts").textContent=ids.length+
    " typed source-backed nodes · "+edges.length+" visible multi-terminal hyperedges · "+
    Object.keys(map.sources).length+" unique source roots · zero owner-local authority.";
}
const posterior=document.getElementById("posterior");
(map.posterior||[]).forEach((prob,i)=>{
  const row=document.createElement("div");row.className="posterior-row";
  const label=document.createElement("span");label.textContent="H"+i;
  const track=document.createElement("div");track.className="track";
  const fill=document.createElement("div");fill.className="fill";
  fill.style.width=Math.max(0,Math.min(100,prob*100))+"%";
  track.appendChild(fill);
  const pct=document.createElement("span");pct.textContent=(100*prob).toFixed(1)+"%";
  row.append(label,track,pct);posterior.appendChild(row);
});
const select=document.getElementById("event");
(map.events||[]).forEach((event,i)=>{
  const option=document.createElement("option");
  option.value=String(i);option.textContent="Probe "+(i+1)+": "+event.x.join("");
  select.appendChild(option);
});
if(!map.events.length){const opt=document.createElement("option");opt.textContent="No tests";
  select.appendChild(opt);select.disabled=true;}
function inspectEvent(){
  const ev=map.events[Number(select.value)||0];
  const detail=document.getElementById("eventDetail");
  if(!ev){detail.textContent="No source-owner test yet.";return}
  detail.textContent=(ev.contradiction_reported?
      "A source report contradicted the favorite PENCIL hypothesis. ":
      "The source report did not contradict the favorite hypothesis. ")+
    "Independent source: "+(ev.independent?"yes":"no")+
    ". Posterior changed: "+(ev.posterior_changed?"yes":"no")+
    ". Entropy before/after: "+ev.entropy_before+" / "+ev.entropy_after+
    ". Report kind: "+ev.response_kind+". "+
    "This is not a hidden-owner truth grade.";
}
document.getElementById("lens").addEventListener("change",draw);
select.addEventListener("change",inspectEvent);
document.getElementById("reset").addEventListener("click",()=>{
  document.getElementById("lens").value="causal";select.selectedIndex=0;
  show({scope:"public authored synthetic",schema:map.schema,state_id:map.state_id,
        nonimports:"No real actions. Truth inaccessible to the visualization."});
  draw();inspectEvent();
});
draw();inspectEvent();
show({scope:"public authored synthetic",schema:map.schema,state_id:map.state_id,
      prompt:"Tap nodes and square hyperedges. Change lenses to inspect evidence."});
})();
</script>
</body>
</html>'''

def render(map_data):
    if map_data.get("schema")!="motif.reason-hypermap/v0" or map_data.get("world")!="PUBLIC_AUTHOR_SYNTHETIC_ONLY":
        raise ValueError("NOT_PUBLIC_SYNTHETIC_MAP")
    if map_data.get("external_actions") is not False or map_data.get("authority")!="none":
        raise ValueError("UNSAFE_VIEWER_INPUT")
    payload=json.dumps(map_data,ensure_ascii=False,sort_keys=True).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    return TEMPLATE.replace("__PAYLOAD__",payload)
if __name__=="__main__":
    import sys
    src=Path(sys.argv[1]);dst=Path(sys.argv[2])
    page=render(json.loads(src.read_text()))
    dst.write_text(page,encoding="utf-8")
    print("VIEWER",dst,"BYTES",len(page.encode()))
