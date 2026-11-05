"""Generate a complete offline first-door desk from actual MOTIF bridge receipts.

One local HTML file. No server, third-party assets, analytics, external scripts,
user accounts, network calls, automated messages, or permission side effects.
"""
from __future__ import annotations

from dataclasses import replace
from html import escape
from pathlib import Path
import argparse
import json

from bridge import first_human_card, food, relay, solve, workshop

CASES = (
    ("workshop", "The Workshop", "Find a new repair capability without taking away a neighbor's only tool.",
     workshop()),
    ("workshop-free", "No Protection", "What happens if we optimize for cost while ignoring lost options?",
     (*workshop()[:3], replace(workshop()[3], preserve=False))),
    ("workshop-hold", "No One Offered Yet", "Suggest a missing human agreement; never manufacture it.",
     workshop(with_offers=False)),
    ("food", "The Perishable Relay", "Coordinate a fictional cooler, courier, and information under a deadline.",
     food()),
    ("food-urgent", "The Clock Runs Out", "See the system refuse to pretend a 14-minute plan fits in 10.",
     (*food()[:3], replace(food()[3], deadline_minutes=10))),
    ("relay", "The Second Teacher", "A newly taught person can become the next teacher.",
     relay()),
    ("relay-hold", "The Missing Yes", "Keep a proposed three-person relay HELD until recipient agreement.",
     relay(recipient_accepts=False)),
)


def payload() -> list[dict[str, object]]:
    return [
        {
            "id": identifier, "title": title, "summary": summary,
            "receipt": receipt, "card": first_human_card(receipt),
        }
        for identifier, title, summary, specimen in CASES
        for receipt in (solve(*specimen),)
    ]


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>MOTIF — The First Door Field Desk</title>
<style>
:root { --paper:#f1e9d6; --ivory:#f9f4e9; --ink:#273843; --muted:#536265;
        --red:#993a2e; --green:#315b48; --line:#b7ad96; --gold:#b68a49; }
*{box-sizing:border-box}
html{background:var(--paper)}
body{margin:0;color:var(--ink);font-family:Georgia,"Times New Roman",serif;line-height:1.55;
     background:radial-gradient(circle at 10% 3%,#fdf8e8 0,transparent 38%),
        repeating-linear-gradient(0deg,transparent 0,transparent 26px,#52412c06 27px),var(--paper)}
main{max-width:1050px;margin:0 auto;padding:clamp(16px,5vw,54px)}
header{border-top:3px double var(--ink);border-bottom:1px solid var(--line);padding:16px 0 24px;
       display:flex;align-items:flex-start;justify-content:space-between;gap:20px}
.kicker,.small,label,.stamp,button{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.kicker{letter-spacing:.16em;text-transform:uppercase;font-size:11px;font-weight:700;color:var(--red)}
h1{font-size:clamp(37px,7vw,76px);line-height:1.05;margin:12px 0 10px;font-weight:400;
   letter-spacing:-.045em}
.dek{font-size:clamp(16px,2.3vw,22px);color:#4a5556;max-width:600px;margin:0}
.stamp{color:var(--red);border:2px solid var(--red);transform:rotate(6deg);padding:8px;
       text-transform:uppercase;font-size:10px;letter-spacing:.1em;flex-shrink:0;text-align:center}
section{margin-top:34px}
h2{font-size:26px;font-weight:400;letter-spacing:-.02em;margin:0 0 7px}
.tabs{display:flex;flex-wrap:wrap;gap:9px;margin-top:16px}
button{font-size:12px;border:1px solid var(--ink);background:transparent;color:var(--ink);
       padding:10px 12px;cursor:pointer;border-radius:2px;touch-action:manipulation}
button:hover,button:focus-visible{background:#ded4c2;outline-offset:2px}
button[aria-pressed="true"]{background:var(--ink);color:var(--ivory)}
.paper{background:var(--ivory);border:1px solid #c4baa4;box-shadow:3px 5px 0 #514b3b17;
       padding:clamp(18px,4vw,38px)}
.columns{display:grid;grid-template-columns:1.2fr 1fr;gap:22px}
.flag{display:inline-block;border:1px solid currentColor;padding:4px 7px;font-size:11px;
      font-family:ui-monospace,monospace;letter-spacing:.05em}
.flag.hold{color:var(--red)}.flag.sim{color:var(--green)}
.card-text{font-size:clamp(18px,2.6vw,26px);font-style:italic;line-height:1.36;
           padding:19px 0;border-block:1px solid var(--line)}
.summary{font-size:16px;color:var(--muted)}
.steps{counter-reset:s;margin:16px 0 0;padding:0;list-style:none}
.steps li{margin:0 0 11px;padding:11px 14px 11px 42px;background:#eee8db;position:relative;
          border-left:3px solid var(--gold)}
.steps li::before{counter-increment:s;content:counter(s);font-family:ui-monospace,monospace;
                  position:absolute;left:15px;top:13px;color:var(--red)}
.steps li.held{border-color:var(--red)}
.meta{font:12px/1.6 ui-monospace,monospace;color:var(--muted);margin-top:6px}
dl{margin:13px 0 0;display:grid;grid-template-columns:auto 1fr;gap:7px 14px;font-size:14px}
dt{font-weight:bold}dd{margin:0}
.pair{display:flex;gap:18px;flex-wrap:wrap;font-size:14px;margin-top:14px}
.gain{color:var(--green)}.loss{color:var(--red)}
.small{font-size:12px;color:var(--muted)}
.note{border-left:3px solid var(--red);padding:10px 13px;background:#efdfd4;line-height:1.45;
      margin:20px 0}
details{margin-top:16px;border-top:1px dashed var(--line);padding-top:10px}
summary{cursor:pointer;font-family:ui-monospace,monospace;font-size:12px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:350px;overflow:auto;font-size:11px;
    background:#e7e0d2;padding:13px}
.actions{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}
.actions button{background:#efe4d1}
footer{margin-top:46px;padding-top:15px;border-top:3px double var(--ink);font:12px/1.7 ui-monospace,monospace;color:var(--muted)}
@media(max-width:680px){header{display:block}.stamp{display:inline-block;margin-top:20px;transform:rotate(-3deg)}
 .columns{grid-template-columns:1fr}main{padding:15px}.paper{padding:18px}}
</style>
</head>
<body>
<main>
<header>
<div>
<div class="kicker">THE STATIC COLLECTIVE / MOTIF / BRIDGE-001</div>
<h1>What opens<br>the next door?</h1>
<p class="dek">A small laboratory for discovering useful actions between people, resources and unanswered questions.</p>
</div>
<div class="stamp">Offline<br>research specimen<br>not a live service</div>
</header>
<section>
<h2>Choose a world</h2>
<p class="small">Every example is fictional. Switch cases to see how timing, missing agreement and another person's lost options change the answer.</p>
<div id="tabs" class="tabs" role="group" aria-label="Synthetic scenario selector"></div>
</section>
<section class="paper">
<div class="kicker">FIELD RETURN / HELD FOR HUMAN REVIEW</div>
<h2 id="title"></h2>
<p id="summary" class="summary"></p>
<div class="columns">
<div>
<div id="status" class="flag"></div>
<p id="first-step" class="card-text"></p>
<h2>Possible path</h2>
<ol id="steps" class="steps"></ol>
<div class="actions"><button id="copy" type="button">Copy this field card</button></div>
<p id="copy-status" class="small" aria-live="polite"></p>
</div>
<div>
<h2>What changes?</h2>
<div class="pair"><div class="gain" id="gain"></div><div class="loss" id="loss"></div></div>
<dl id="metrics"></dl>
<div class="note"><strong>Important boundary.</strong> No one was contacted, no agreement was verified, and no physical result occurred. Even an admitted synthetic move is only a proposed human decision.</div>
<details><summary>Inspect the full synthetic receipt</summary><pre id="receipt"></pre></details>
</div>
</div>
</section>
<footer>LOCAL-FIRST: THIS FILE MAKES NO NETWORK REQUESTS · NO ACCOUNTS · NO ANALYTICS · NO AUTO-MESSAGES<br>
MOTIF generates hypothetical bridges. Dogram measures declared differences. People decide what is actually permitted and worthwhile.</footer>
</main>
<script type="application/json" id="case-data">__PAYLOAD__</script>
<script>
"use strict";
const cases = JSON.parse(document.getElementById('case-data').textContent);
const byId = Object.fromEntries(cases.map(x => [x.id,x]));
const tabs = document.getElementById('tabs');
function put(id, value) { document.getElementById(id).textContent = value; }
function show(id) {
 const row=byId[id], r=row.receipt, card=row.card;
 for (const btn of tabs.querySelectorAll('button')) btn.setAttribute('aria-pressed',String(btn.dataset.case===id));
 put('title',row.title); put('summary',row.summary);
 const sim=r.status==='PROPOSED_SYNTHETIC_ONLY';
 const badge=document.getElementById('status');
 badge.className='flag '+(sim?'sim':'hold');
 badge.textContent=r.status.replaceAll('_',' ');
 put('first-step',card.first_step);
 const steps=document.getElementById('steps'); steps.replaceChildren();
 if (r.actions.length) {
   for(const action of r.actions) {
     const li=document.createElement('li');
     li.className=action.status==='ADMITTED_SIM'?'':'held';
     const label=document.createElement('span');
     label.textContent=action.source+' → '+action.recipient+' · '+action.kind+' '+action.subject;
     li.appendChild(label);
     const meta=document.createElement('div');meta.className='meta';
     meta.textContent=action.status.replaceAll('_',' ')+' · '+(action.declared_cost===null?'cost unknown':'cost '+action.declared_cost)+' · '+(action.declared_minutes===null?'duration unknown':action.declared_minutes+' minutes');
     li.appendChild(meta); steps.appendChild(li);
   }
 } else {
  const li=document.createElement('li'); li.textContent='No bounded supported path under these constraints.'; steps.appendChild(li);
 }
 const delta=(r.delta||{}).visible||{gained:[],lost:[]};
 put('gain','NEW OPTIONS\\n'+(delta.gained.length?delta.gained.join(', '):'none established'));
 put('loss','OPTIONS LOST\\n'+(delta.lost.length?delta.lost.join(', '):'none in the model'));
 const metrics=document.getElementById('metrics');metrics.replaceChildren();
 const pairs=[
   ['Held agreements',String(r.held_steps.length)],
   ['Total cost known?',String(r.total_cost_known===true)],
   ['Known cost',r.known_cost===null?'unknown':String(r.known_cost)],
   ['Known minutes',r.known_minutes===null?'unknown':String(r.known_minutes)],
   ['Deadline',r.goal.deadline_minutes===null?'none declared':r.goal.deadline_minutes+' min'],
   ['States explored',String(r.explored_states)]
 ];
 for(const [k,v] of pairs){
  const dt=document.createElement('dt');dt.textContent=k;
  const dd=document.createElement('dd');dd.textContent=v;
  metrics.append(dt,dd);
 }
 put('receipt',JSON.stringify(r,null,2));
 document.getElementById('copy').onclick=async()=>{
   const lines=['MOTIF FIELD CARD / FICTIONAL RESEARCH',row.title,r.status,card.first_step,
     ...r.actions.map(x=>x.source+' -> '+x.recipient+' / '+x.kind+' '+x.subject+' / '+x.status),
     'No real consent verified. Nothing sent. Human review required.'];
   const text=lines.join('\\n');
   try { await navigator.clipboard.writeText(text);put('copy-status','Copied. This is an unverified draft.');}
   catch (_) {put('copy-status','Clipboard unavailable. Select and copy the receipt above.');}
 };
}
for(const c of cases){
 const btn=document.createElement('button');btn.type='button';
 btn.dataset.case=c.id;btn.textContent=c.title;btn.setAttribute('aria-pressed','false');
 btn.onclick=()=>show(c.id);tabs.appendChild(btn);
}
show(cases[0].id);
</script>
</body>
</html>"""


def render() -> str:
    json_safe = json.dumps(payload(), ensure_ascii=True, separators=(",", ":"))
    # Prevent a user-provided string from terminating a script element if
    # later specimens are imported from untrusted material.
    json_safe = json_safe.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return PAGE.replace("__PAYLOAD__", json_safe)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("field-desk.html"))
    args = parser.parse_args()
    args.output.write_text(render(), encoding="utf-8")
    print(f"Prepared offline specimen: {args.output}")
