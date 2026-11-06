"""Offline interactive UI for the actual external typed benchmark and two circles.

This is a *document of evidence*, not a machine's felt experience or live
decision tool. It displays external bAbI scores/errors and separate fictional
consent/duty tests. It deliberately does not present the bAbI QA dataset as
evidence about the wishes, rights or needs of actual people.

No remote scripts, services, fonts, tracking, cookie stores or actions.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys

HTML=r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>MOTIF · The Unimagined Distinction</title>
<style>
:root{color-scheme:dark;--bg:#111a21;--card:#172837;--stroke:#3d5868;--ink:#f3f9fc;--muted:#c2d4dd;--self:#71d4d1;--other:#ffbe84}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);margin:0;font:16px/1.52 system-ui,sans-serif}
main{max-width:1150px;margin:auto;padding:24px 19px 68px}
h1{font-size:clamp(1.9rem,4.5vw,3.3rem);letter-spacing:-.05em;line-height:1.2;margin:.3em 0}
h2{font-size:1.05rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}
h3{margin:.25em 0}p{line-height:1.57}.sub{color:var(--muted)}
.eyebrow{font-size:.81rem;color:#aac8e7;letter-spacing:.15em;text-transform:uppercase}
.card{background:var(--card);border:1px solid var(--stroke);border-radius:17px;padding:22px;margin:18px 0}
.diagram{display:block;width:100%;max-height:440px}
.diagram .left{fill:#2b8f94;fill-opacity:.29;stroke:var(--self);stroke-width:3}
.diagram .right{fill:#be813a;fill-opacity:.31;stroke:var(--other);stroke-width:3}
.diagram text{fill:#f4f8ff;font-family:system-ui,sans-serif}
.diagram .title{font-size:28px;font-weight:750}
.diagram .note{font-size:17px}
.diagram .bridge{font-size:18px;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.metric{border:1px solid var(--stroke);background:#0d1d2a;border-radius:12px;padding:16px}
.metric b{display:block;font-size:1.65rem;color:#a8e3d2}
.split{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:15px}
.panel{padding:20px;background:#0d2030;border:1px solid var(--stroke);border-radius:15px}
select{font:inherit;color:var(--ink);background:#0c1c2b;border:1px solid #86a4b3;padding:11px 14px;border-radius:12px;max-width:100%}
pre{font:13px/1.5 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;color:#dbedf7}
.state{border-left:4px solid #96dbac}.warn{border:1px solid #a98e67;background:#3b2f25;color:#ffebd2;padding:16px;border-radius:14px}
.pill{border-radius:23px;background:#315366;display:inline-block;padding:4px 11px;margin:3px 5px 0 0;font-size:.82rem}
</style></head><body><main>
<p class="eyebrow">The Static Collective · MOTIF · REASON-022 · independent-source reasoning study</p>
<h1>The Unimagined Distinction</h1>
<p>Sometimes the right correction is not a new Boolean value but a different <strong>kind of model</strong>:
counted quantities, time order, directed three-party relationships, and conditional obligations.</p>
<svg class="diagram" viewBox="0 0 1000 425" role="img" aria-label="Two partial perspectives: self conceptual capabilities and another person's specific fictional statements, with typed reasoning between the circles">
<circle class="left" cx="388" cy="214" r="202"></circle>
<circle class="right" cx="615" cy="214" r="202"></circle>
<text class="title" x="244" y="139" text-anchor="middle">SELF</text>
<text class="note" x="240" y="178" text-anchor="middle">types · limitations</text>
<text class="note" x="240" y="205" text-anchor="middle">heldout failures</text>
<text class="title" x="759" y="139" text-anchor="middle">OTHER</text>
<text class="note" x="765" y="178" text-anchor="middle">source statements</text>
<text class="note" x="765" y="205" text-anchor="middle">permission · duties</text>
<text class="bridge" x="502" y="255" text-anchor="middle">MIRROR</text>
<text class="note" x="502" y="286" text-anchor="middle">typed correction</text>
<text class="note" x="502" y="310" text-anchor="middle">never overreach</text>
</svg>
<div class="card"><h2>Independent test source</h2><p>Original external benchmark: Facebook bAbI, from a third-party GitHub repository at a pinned commit and six checked Git blobs. These are independently authored <strong>toy QA problems</strong>, not real people or ethical rulings.</p>
<div class="grid">
<div class="metric"><span>External training questions</span><b id="training">—</b></div>
<div class="metric"><span>External heldout questions</span><b id="testing">—</b></div>
<div class="metric"><span>Typed interpreters</span><b>3</b></div>
<div class="metric"><span>Fictional duties cases</span><b id="duties">—</b></div>
</div></div>
<div class="card"><label for="family"><strong>Inspect an independent external task type</strong></label><br>
<select id="family" aria-label="Reasoning family">
<option value="COUNT">Quantity / counting</option>
<option value="TIME">Temporal ordering</option>
<option value="TRANSFER">Triadic giving / receiving</option>
</select><div class="grid" style="margin-top:16px">
<div class="metric">Exactly answered<b id="exact">—</b></div>
<div class="metric">Confident mistakes<b id="wrong">—</b></div>
<div class="metric">Explicit HOLD<b id="held">—</b></div>
<div class="metric">Weak fixed-answer control<b id="naive">—</b></div></div>
<p id="skill" class="sub"></p><h3>Selected source-linked failures and abstentions</h3><pre id="failures"></pre></div>
<div class="card"><h2>When the external benchmark's answer is not unique</h2>
<p>A separate <strong>posthoc</strong> evaluator found that a single bAbI question's
official answer is supported by one original story sentence, but a different
answer is ALSO supported by another original sentence. The typed solver chose
the latter with excessive confidence. This remains an official scoring mismatch
and is not retroactively corrected.</p><pre id="ambiguity"></pre></div>
<div class="card"><h2>Where an old Boolean view breaks</h2>
<p>Two independently authored training examples can share the same impoverished feature summary while requiring different answers. A model using <em>only</em> that old summary cannot fit both. This says nothing about the limits of general Boolean logic.</p>
<pre id="witnesses"></pre></div>
<div class="card"><label for="duty"><strong>Inspect a fictional multi-party duty</strong></label><br>
<select id="duty" aria-label="Fictional promise scenario"></select>
<div class="split" style="margin-top:16px">
<div class="panel"><h3>Directed prior commitments</h3><pre id="obligation"></pre></div>
<div class="panel"><h3>What the Golden Mirror permits</h3><p id="status"></p><pre id="critic"></pre></div>
</div></div>
<div class="warn"><strong>Critical limits:</strong> The external QA source is independently authored, but the
three classical typed engines and their routing rules are human-written. The third-party benchmark does not evaluate love, promises, human dignity, consent or ethical decisions. Seven Golden Mirror scenarios were scripted by this experiment's author. The four perspective workers are real deterministic Python subprocesses, not secure virtual machines or conscious minds. All suggestions remain READ-ONLY; no real action, contact or intervention.</div>
<p class="sub">The source-pinned GitHub CI run generated this fully offline page from its actual benchmark JSON and stores every source, negative result and four-elf receipt in the evidence artifact.</p>
</main><script type="application/json" id="data">__SOURCE__</script>
<script>
"use strict";
const source=JSON.parse(document.getElementById("data").textContent);
const el=id=>document.getElementById(id);
const fmt=o=>JSON.stringify(o,null,2);
el("training").textContent=source.training_questions;
el("testing").textContent=source.test_questions;
el("duties").textContent=source.fictional_obligation_cases;
function showFamily(){
 const f=el("family").value,s=source.external_test[f];
 el("exact").textContent=s.exact_source_answers+" / "+s.independently_authored_test_questions;
 el("wrong").textContent=s.incorrect_confident_answers;
 el("held").textContent=s.explicit_abstentions;
 el("naive").textContent=s.weak_fixed_answer_baseline_exact;
 el("skill").textContent="Training-selected representation: "+s.model_type_from_source_training
 +" · all examples: independently sourced · answers held out during inference.";
 el("failures").textContent=fmt(source.external_source_failed_or_abstained_examples.filter(r=>r.family===f));
}
el("family").addEventListener("change",showFamily);showFamily();
el("witnesses").textContent=fmt(source.source_training_boolean_projection_impossibilities);
el("ambiguity").textContent=fmt(source.independent_external_posthoc_ambiguous_gold_cases||[]);
for(const p of source.fictional_duty_source_proofs){
 const item=document.createElement("option");item.value=p.source_case_id;
 item.textContent=p.source_case_id.replaceAll("_"," ");
 el("duty").appendChild(item);
}
function showDuty(){
 const p=source.fictional_duty_source_proofs.find(x=>x.source_case_id===el("duty").value);
 const e=source.actual_original_019_elf_receipts.find(x=>x.source_case===el("duty").value);
 el("obligation").textContent=fmt({prior:p.relevant_deadlines,
   prior_units:p.prior_directed_duty_units,capacity:p.capacity_units,
   required:p.requested_units,due:p.new_request_deadline,
   now:p.current_hour,max_per_hour:p.production_capacity_per_hour});
 el("status").textContent=p.state;
 el("critic").textContent="Reason: "+p.reason+
   "\nOriginal REASON-019 critic approved limited discussion: "+
   e.critic_eligible_for_read_only_discussion+
   "\nExternal actions: FALSE";
}
el("duty").addEventListener("change",showDuty);
el("duty").value=source.fictional_duty_source_proofs[0].source_case_id;
showDuty();
</script></body></html>'''


def build(source,destination):
    evidence=json.loads(Path(source).read_text(encoding="utf8"))
    if (evidence.get("schema")!="motif.reason022.unimagined-distinction.benchmark.v1"
            or evidence.get("test_questions")!=750
            or evidence.get("fictional_obligation_cases")!=7
            or evidence.get("external_actions") is not False
            or evidence.get("permission_to_execute") is not False):
        raise ValueError("Only complete real evidence with no execution authority")
    embedded=json.dumps(evidence,sort_keys=True,ensure_ascii=True,
                        separators=(",",":")).replace("<","\\u003c").replace(
                            "&","\\u0026")
    html=HTML.replace("__SOURCE__",embedded)
    out=Path(destination);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html,encoding="utf8")
    return {"path":str(out),"bytes":out.stat().st_size,
            "real_external_benchmark_questions":evidence["test_questions"],
            "does_not_contact_a_person":True,"external_requests":False}


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: python viewer.py benchmark.json two-circles-typed.html")
    print(json.dumps(build(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
