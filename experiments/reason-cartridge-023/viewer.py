"""Offline interactive evidence viewer for the actual MANY-TRUTH trial.

The display never calls external sites or uses personal accounts. bAbI
historical story answers are not human preferences; the other-person
reciprocity section is a DIFFERENT fictional experiment.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

HTML=r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>MOTIF • The Many-Truth Mirror</title>
<style>
:root{color-scheme:dark;--bg:#101821;--panel:#182837;--line:#3a566b;--ink:#f3f8fa;--muted:#b9d0d8;--accent:#a4e3d6;--amber:#f3ba78}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:26px 19px 60px}
h1{font-size:clamp(2rem,4.5vw,3.4rem);letter-spacing:-.05em;line-height:1.1;margin:8px 0}
h2{color:var(--muted);text-transform:uppercase;letter-spacing:.07em;font-size:1rem}
h3{margin:10px 0 7px}.eyebrow{color:#b3dbfa;letter-spacing:.15em;font-size:.82rem;text-transform:uppercase}
.card{background:var(--panel);border:1px solid var(--line);border-radius:17px;padding:20px;margin:16px 0}
.metrics,.split{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:13px}
.metric{padding:16px;border:1px solid var(--line);border-radius:13px;background:#0e1e2d}
.metric strong{display:block;font-size:1.8rem;color:var(--accent)}
.note{color:var(--muted);font-size:.92rem}select{background:#101e2d;color:var(--ink);padding:12px;border:1px solid #8da5b8;border-radius:11px;font:inherit;max-width:100%;width:min(100%,650px)}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,monospace;color:#dcecf3}
.diagram{display:block;width:100%;height:auto;max-height:400px}.diagram .self{fill:#1d9e98;fill-opacity:.28;stroke:#73d7cc;stroke-width:3}.diagram .other{fill:#d48942;fill-opacity:.28;stroke:#ffc88d;stroke-width:3}.diagram text{font:19px ui-sans-serif,system-ui;fill:#f3f7ff}.diagram .big{font-size:28px;font-weight:750}
.warning{border:1px solid #a88656;background:#3c3025;padding:15px;border-radius:15px;color:#ffe6c3}.status{border-left:4px solid var(--accent)}
</style></head><body><main>
<p class="eyebrow">The Static Collective · MOTIF · REASON-023 · source-grounded, read-only</p>
<h1>The Many-Truth Mirror</h1>
<p>One source question can have several supported answers. That is not necessarily a contradiction.
One explicit proposition may also have both supporting and refuting testimony.
These are different evidential situations—and neither grants authority over someone else.</p>
<svg viewBox="0 0 1000 390" class="diagram" role="img" aria-label="Two overlapping perspectives. Left self uncertainty and assumptions. Right evidence, sources and separate consent. Their overlap is a mirror examining unsupported certainty.">
<circle class="self" cx="386" cy="197" r="183"></circle><circle class="other" cx="616" cy="197" r="183"></circle>
<text x="243" y="125" text-anchor="middle" class="big">SELF</text>
<text x="245" y="160" text-anchor="middle">assumptions</text><text x="245" y="189" text-anchor="middle">uncertainty</text>
<text x="760" y="125" text-anchor="middle" class="big">OTHER</text>
<text x="760" y="160" text-anchor="middle">source evidence</text><text x="760" y="189" text-anchor="middle">distinct permission</text>
<text x="500" y="242" text-anchor="middle">MULTI-TRUTH</text>
<text x="500" y="272" text-anchor="middle">ASK / HOLD</text>
</svg>
<div class="metrics card">
<div class="metric"><span>Independent prospective story questions</span><strong id="tested">—</strong></div>
<div class="metric"><span>Source-unique answers</span><strong id="unique">—</strong></div>
<div class="metric"><span>Ambiguous answer sets</span><strong id="multiple">—</strong></div>
<div class="metric"><span>Wrong confident answers</span><strong id="wrong">—</strong></div>
</div>
<div class="card"><h2>Independent external source evidence</h2>
<p>These are published bAbI artificial stories, not interviews with real people.</p>
<label for="example"><strong>Inspect a source-backed multi-answer example</strong></label><br>
<select id="example"></select>
<div class="split" style="margin-top:17px">
<section class="metric"><h3>Original source question</h3><p id="query"></p><h3>Source answers and assumptions</h3><pre id="alts"></pre></section>
<section class="metric"><h3>Source-linked witness graph</h3><pre id="evidence"></pre></section></div>
</div>
<div class="card"><h2>What is a contradiction?</h2>
<p>Explicit YES and NO to the exact same scoped claim = <strong>BOTH</strong>.
Different possible answers to a historical transfer question are <strong>ambiguity</strong>, not a reason to label every answer contradictory.</p>
<label for="polar"><strong>Inspect fictional four-valued testimony</strong></label><br><select id="polar"></select>
<pre id="polar-result"></pre></div>
<div class="card status"><h2>May the helper ask the source?</h2>
<p id="inquiry"></p><h3>Original Golden Mirror subprocess constraints</h3><pre id="golden"></pre></div>
<div class="warning"><strong>Boundaries:</strong> The externally authored benchmark evaluates artificial story QA, not love, consent or ethics. The four-valued examples and clarifier are fictional, source-author-scripted tests. The original REASON-011 and REASON-019 engines are imported as exact source-pinned code. The system does not read anyone's mind or contact anyone. The inquiry's claimed uniform prior is a stated assumption, not a probability about a person. The strong classical source-evidence baseline ties by design. No actual intervention is permitted.</div>
<p class="note">This HTML is generated directly from the latest CI benchmark JSON with no trackers, remote scripts or network requests. Every supported hypothesis is linked to source lines; failures and abstentions are reported without deletion.</p>
</main><script type="application/json" id="data">__DATA__</script>
<script>
"use strict";const r=JSON.parse(document.getElementById("data").textContent);
const el=id=>document.getElementById(id),p=v=>JSON.stringify(v,null,2);
const n=r.external_test_counts;el("tested").textContent=n.total;
el("unique").textContent=n.source_single_answer;
el("multiple").textContent=n.source_non_unique;
el("wrong").textContent=n.single_answer_wrong;
const examples=r.source_nonunique_examples;
for(const x of examples){const option=document.createElement("option");
 option.value=x.source_id;option.textContent=x.source_id+" · "+x.question;
 el("example").appendChild(option);}
function showExample(){
 const x=examples.find(e=>e.source_id===el("example").value);
 if(!x){el("query").textContent="No nonunique question in this reserved evaluation slice.";
 el("alts").textContent="No source-grounded alternatives found.";el("evidence").textContent="None";return;}
 el("query").textContent=x.question;
 el("alts").textContent="Explicit alternatives: "+p(x.all_source_supported_answers)
 +"\nOfficial scorer answer: "+x.source_gold_for_scoring_only
 +"\nPrior single choice: "+x.old_answer
 +"\nGold supported among alternatives: "+x.gold_is_in_ambiguity_set;
 el("evidence").textContent=p({proof_edges:x.complete_source_witnessed_graph.proof_edges,
    assumptions:x.complete_source_witnessed_graph.assumptions_considered});
}
el("example").addEventListener("change",showExample);
if(examples.length)el("example").value=examples[0].source_id;showExample();
const polar=r.independently_pinned_011_four_value_cases;
for(const x of polar){const item=document.createElement("option");
item.value=x.case;item.textContent=x.case+" — "+x.status;el("polar").appendChild(item);}
function showPolar(){
 const x=polar.find(y=>y.case===el("polar").value);
 el("polar-result").textContent=p({context:x.context,four_value:x.status,
 support:x.support_source_ids,refute:x.refute_source_ids,
 scope_excluded:x.unrelated_scoped_source_claims,
 original_011_verdict:x.original_011_verdict});
}
el("polar").addEventListener("change",showPolar);el("polar").value=polar[0].case;showPolar();
const q=r.scripted_ambiguous_case;el("inquiry").textContent=
 "Synthetic owner clarified: "+q.owner_confirmed.current_source_hypothesis+
 " · Refused inquiry: "+q.owner_declined.stage+
 " · Without permission: "+q.no_contact.stage+
 " · No owner: "+q.no_source_owner.stage;
el("golden").textContent=p(r.scope_sensitive_original_019_elves.map(x=>({
 choice:x.recommended_read_only_question_or_wait,
 blockers:x.four_original_subprocess_reports.CRITIC.judgments.ASK_PREFERENCE.refusals,
 external_actions:false
})));
</script></body></html>'''


def build(source,destination):
    payload=json.loads(Path(source).read_text(encoding="utf8"))
    counts=payload.get("external_test_counts",{})
    if (payload.get("schema")!="motif.reason023.many-truth-benchmark.v1"
            or counts.get("total")!=250
            or payload.get("external_actions") is not False
            or payload.get("permission_to_execute") is not False):
        raise ValueError("Cannot publish incomplete or action-enabled source claims")
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),
                   ensure_ascii=True).replace("<","\\u003c").replace(
                       "&","\\u0026")
    path=Path(destination);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(HTML.replace("__DATA__",raw),encoding="utf8")
    return {
        "path":str(path),"bytes":path.stat().st_size,
        "external_test_cases":counts["total"],
        "network_requests":False,"fictional_only_personal_examples":True,
    }


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: python viewer.py benchmark.json many-truth-mirror.html")
    print(json.dumps(build(sys.argv[1],sys.argv[2]),sort_keys=True,indent=2))
