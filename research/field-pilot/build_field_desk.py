"""Build one offline HTML FIELD-001 page from two inspectable JS sources.

No CDN, fonts, fetched assets, analytics, service worker, database, external
connection, or server. User-entered data remains in memory unless exported.
"""
from pathlib import Path
import argparse


PAGE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>MOTIF · Field Witness — the first real door</title>
<style>
:root { --paper:#f4ecd8; --sheet:#fcf9f0; --ink:#243439; --muted:#576464; --line:#bdb19c;
  --red:#a34836; --green:#365b46; --blue:#366174; --tan:#e9deca; --gold:#c0a574; }
* {box-sizing:border-box}
html {background:var(--paper)}
body {margin:0;color:var(--ink);font-family:Georgia,"Times New Roman",serif;line-height:1.5;
  background:radial-gradient(circle at 82% 5%,#e5d3b79c,transparent 34%),
             repeating-linear-gradient(0deg,transparent,transparent 29px,#66553a07 30px),var(--paper)}
button,input,textarea,select {font:inherit}
button {cursor:pointer;touch-action:manipulation}
header,main,footer {max-width:1160px;margin:auto;padding-inline:clamp(16px,4vw,48px)}
header {padding-top:35px}
header .top {display:flex;justify-content:space-between;align-items:flex-start;gap:25px;
  border-top:3px double var(--ink);padding-top:18px}
.kicker,.small,.mono,.eyebrow,label,.metric span,button,select,.statusline {font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.kicker {font-size:11px;color:var(--red);letter-spacing:.16em;text-transform:uppercase;font-weight:bold}
h1 {font-size:clamp(42px,8vw,84px);letter-spacing:-.055em;font-weight:400;line-height:.94;margin:12px 0 17px}
.dek {font-size:clamp(16px,2.2vw,23px);max-width:720px;line-height:1.45;margin:0 0 18px;color:#424c4c}
.stamp {color:var(--red);font:11px/1.45 ui-monospace,monospace;letter-spacing:.12em;
  border:2px solid var(--red);padding:12px;transform:rotate(6deg);text-align:center;min-width:125px}
.mode {font:11px/1.5 ui-monospace,monospace;letter-spacing:.07em;
  background:#e3ebde;border:1px solid #749078;padding:8px 12px;display:inline-block;color:var(--green)}
.mode.demo {color:var(--red);background:#f6dbce;border-color:var(--red)}
main {padding-top:22px}
h2 {font-size:clamp(23px,3vw,35px);letter-spacing:-.03em;font-weight:400;margin:0 0 6px}
h3 {font-size:20px;margin:0 0 10px;font-weight:400}
p {margin:7px 0 14px}
.small {font-size:12px;color:var(--muted)}
.note {padding:14px 17px;background:#f0dfd3;border-left:3px solid var(--red);font-size:14px;line-height:1.55}
.workflow {margin-top:24px;border-block:1px solid var(--line);padding-block:15px;
  font:12px/1.8 ui-monospace,monospace;letter-spacing:.035em;color:var(--muted)}
.metrics {display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin:22px 0 24px}
.metric {background:#e9e1ce;border:1px solid #cbc2ae;padding:12px;min-height:96px}
.metric strong {display:block;font-size:clamp(22px,3.8vw,38px);font-weight:400}
.metric span {font-size:10px;color:var(--muted);text-transform:uppercase;line-height:1.25;display:block}
.grid {display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start}
.paper {background:var(--sheet);border:1px solid #cbbda4;box-shadow:4px 5px 0 #574a3412;
  padding:clamp(17px,3vw,29px);min-width:0}
.paper > .eyebrow {margin-bottom:8px}
.eyebrow {font-size:11px;color:var(--red);letter-spacing:.12em;text-transform:uppercase}
.panel-head {border-bottom:1px solid var(--line);margin-bottom:16px;padding-bottom:12px}
.panel-head p {color:var(--muted);font-size:14px}
label {font-size:12px;display:block;margin:12px 0 4px;color:#3f494b}
input[type=text],input[type=number],select,textarea {
  width:100%;border:1px solid #9f9b90;background:#fffdfa;color:var(--ink);
  padding:10px 11px;border-radius:1px;outline-offset:3px;font-size:14px;min-height:43px}
textarea {min-height:85px;resize:vertical;font-family:Georgia,serif}
#intro-draft {min-height:175px;font-family:Georgia,serif}
input::placeholder,textarea::placeholder {color:#828989}
.inline {display:grid;grid-template-columns:1fr 1fr;gap:13px}
.check {display:flex;gap:9px;align-items:flex-start;margin:15px 0;font-family:Georgia,serif;font-size:14px}
.check input {flex-shrink:0;margin-top:5px;accent-color:var(--green)}
button {background:var(--ink);color:#fffdf7;border:1px solid var(--ink);padding:11px 14px;
  font-size:12px;text-align:center;border-radius:1px}
button:hover,button:focus-visible {filter:brightness(1.18);outline-offset:2px}
button:disabled {opacity:.45;cursor:not-allowed}
button.outline,button.textbutton {background:transparent;color:var(--ink);font-size:12px}
button.textbutton {font-size:11px;padding:6px 7px;margin-top:8px;color:var(--red);border-color:var(--red)}
.buttonrow {display:flex;flex-wrap:wrap;gap:9px;margin-top:14px}
.records {display:grid;gap:11px}
.record,.match,.event {border:1px solid #d5cabb;background:#f4ecdf;padding:13px 15px}
.match {border-left:3px solid var(--green);background:#f3f3e9}
.match.warning {border-left-color:var(--red)}
.record-head {display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.record-head strong {font-weight:normal;font-size:17px}
.record p,.match p {font-size:14px;color:#515c5b;line-height:1.45;margin:9px 0}
.meta,.pill {font:11px/1.6 ui-monospace,monospace;color:var(--muted)}
.pill {background:#e2e7de;padding:3px 7px;color:var(--green)}
.event {padding:11px 13px}
.event strong {font-weight:normal;font-size:14px;display:block}
.event .small {display:block}
.event p {font-size:13px}
.empty {font-style:italic;color:var(--muted);font-size:15px}
.statusline {font-size:12px;background:#e0e8dd;color:#315444;border-left:3px solid var(--green);
  padding:12px 14px;min-height:40px;line-height:1.55}
.statusline.error {color:#812f28;border-color:var(--red);background:#f5e2d8}
.utility {display:flex;flex-wrap:wrap;gap:10px}
.utility .subtle {background:transparent;color:var(--ink)}
.utility label {margin:0}
.utility input[type=file] {font-size:12px;max-width:225px}
.mono {font-size:12px}
section {margin:18px 0 27px}
.full {grid-column:1/-1}
footer {padding-top:10px;padding-bottom:35px}
footer p {font:11px/1.7 ui-monospace,monospace;color:var(--muted);
  border-top:3px double var(--ink);padding-top:17px}
#unsaved {margin-top:8px;color:var(--red)}
@media(max-width:790px){.metrics{grid-template-columns:repeat(3,1fr)}.grid{grid-template-columns:1fr}}
@media(max-width:500px){header .top{display:block}.stamp{display:inline-block;transform:rotate(-3deg);margin-bottom:16px}
  .metrics{grid-template-columns:repeat(2,1fr)}.inline{grid-template-columns:1fr}
  .paper{padding:17px}.utility{display:grid;grid-template-columns:1fr}}
@media print {body{background:#fff}.paper{box-shadow:none}button,input[type=file]{display:none}section{break-inside:avoid}}
</style>
</head>
<body>
<header>
<div class="top">
  <div>
    <div class="kicker">THE STATIC COLLECTIVE · MOTIF / FIELD-001</div>
    <h1>The Field<br>Witness</h1>
    <p class="dek">Take the first door outside the simulation. Record an actual <em>reported</em> offer or need, discover a possible introduction, and return with what someone says happened.</p>
  </div>
  <div class="stamp">FIELD EXPERIMENT<br>NOT A VERIFIED<br>EXCHANGE</div>
</div>
<div id="mode" class="mode">REAL-WORLD OPERATOR INTAKE · REPORTS ARE UNVERIFIED</div>
<div class="workflow">RECORD → FIND A POSSIBLE BRIDGE → ASK DIRECTLY → OBSERVE → RECORD A RESULT · NEVER AUTO-CONTACT</div>
</header>
<main>
<div class="note"><strong>Privacy and evidence boundary:</strong> This page has no network connection, accounts, automatic matching service or local autosave. It retains entries only in this tab until you explicitly export a JSON file. Use <strong>aliases and broad areas</strong>, not names, addresses, phone numbers, medical details, or information about children. Reported sharing willingness does not establish verified consent. Check in person before any introduction or handoff.</div>
<section>
  <h2>Field position</h2>
  <div class="metrics" aria-label="Noncausal report counts">
    <div class="metric"><strong id="metric-cards">0</strong><span>Cards recorded</span></div>
    <div class="metric"><strong id="metric-pairs">0</strong><span>Open suggestions</span></div>
    <div class="metric"><strong id="metric-handoffs">0</strong><span>Handoffs reported</span></div>
    <div class="metric"><strong id="metric-benefit">0</strong><span>Benefit reports</span></div>
    <div class="metric"><strong id="metric-no-benefit">0</strong><span>No-benefit reports</span></div>
    <div class="metric"><strong id="metric-unknown">0</strong><span>Unknown follow-ups</span></div>
  </div>
  <p class="small">Counts reflect operator-entered reports, not independently verified effects, causal impact, or total community need. No answer is not a failure.</p>
</section>
<section class="paper">
 <div class="eyebrow">LOCAL FIELD JOURNAL · EXPORT TO RETAIN</div>
 <h2>One portable file, no server</h2>
 <p class="small">Use a blank log for real reports. The demo is expressly fictional. Export after every session; a browser refresh can erase unsaved information.</p>
 <div class="utility">
  <button type="button" id="export">Save field log JSON</button>
  <button type="button" class="subtle" id="new-log">Start an empty log</button>
  <button type="button" class="subtle" id="load-demo">Load FICTIONAL example</button>
  <label class="small">Import a saved log <input id="import-file" type="file" accept=".json,application/json" aria-label="Import a saved field log"></label>
 </div>
 <div id="unsaved" class="mono">EXPORT AFTER EACH FIELD SESSION · browser memory is temporary</div>
 <div id="statusline" class="statusline" role="status" aria-live="polite">Ready.</div>
</section>
<div class="grid">
 <section class="paper">
  <div class="panel-head"><div class="eyebrow">01 · INTAKE</div>
   <h2>What do you have? What do you need?</h2>
   <p>Each card is a reported offer or need. It is not a validated inventory item or a promise.</p>
  </div>
  <form id="add-card">
    <div class="inline">
     <div><label for="card-kind">Record type</label>
       <select id="card-kind"><option value="offer">OFFER · I have / can do</option><option value="need">NEED · I need / seek</option></select></div>
     <div><label for="card-origin">How was this reported?</label>
       <select id="card-origin"><option value="operator_heard_owner">I heard it from the person</option><option value="owner_self_report">I am that person</option><option value="third_party_unverified">I heard it secondhand</option></select></div>
    </div>
    <label for="card-alias">Person or group alias · no full names</label>
    <input required id="card-alias" type="text" maxlength="60" placeholder="e.g., neighbor-a" autocomplete="off">
    <div class="inline">
     <div><label for="card-topic">Matching topic · use the same word</label>
      <input required id="card-topic" type="text" maxlength="40" placeholder="e.g., cooler" autocomplete="off"></div>
     <div><label for="card-area">Broad local area · not an address</label>
      <input required id="card-area" type="text" maxlength="40" placeholder="e.g., waseca" autocomplete="off"></div>
    </div>
    <div class="inline"><div><label for="card-hours">Expires after (hours) · 1–168</label>
       <input required id="card-hours" type="number" min="1" max="168" step="1" value="24"></div>
       <div><label for="card-note">Short description · optional</label>
       <input id="card-note" type="text" maxlength="360" placeholder="One safe, useful detail" autocomplete="off"></div></div>
    <label class="check"><input type="checkbox" id="card-share"><span>The owner expressly reported willingness to be considered for an introduction about <em>this</em> card. This is an operator report, not an authenticated consent receipt.</span></label>
    <button type="submit">Record this offer / need</button>
  </form>
 </section>
 <section class="paper">
  <div class="panel-head"><div class="eyebrow">02 · POSSIBILITIES</div>
   <h2>Who could help whom?</h2>
   <p>Suggestions require matching topic, broad area, current dates, and reported willingness from both owners.</p>
  </div>
  <div id="matches-list" class="records"></div>
  <h3 style="margin-top:28px">Unsent introduction draft</h3>
  <p class="small">For manual review only. This desk never messages anyone or shares contact details.</p>
  <textarea id="intro-draft" readonly aria-label="Draft for human-reviewed introduction" placeholder="Prepare a possible introduction above."></textarea>
  <button type="button" class="outline" id="copy-intro">Copy draft manually</button>
 </section>
 <section class="paper">
  <div class="panel-head"><div class="eyebrow">03 · OBSERVE</div>
   <h2>What did somebody report happened?</h2>
   <p>Keep disagreement, refusal, uncertainty, and the difference between an attempted handoff and an outcome.</p>
  </div>
  <form id="add-event">
   <label for="observer">Reporter alias · who enters this record?</label>
   <input id="observer" type="text" required maxlength="60" placeholder="e.g., operator-a" autocomplete="off">
   <label for="follow-subject">Candidate pair · expired pairs remain for later follow-up</label>
   <select id="follow-subject" required><option value="">Choose a pair</option></select>
   <div class="inline"><div><label for="follow-kind">Report type</label>
    <select id="follow-kind">
      <option value="provider_yes_reported">Offerer said yes (reported)</option>
      <option value="requester_yes_reported">Requester said yes (reported)</option>
      <option value="provider_no_reported">Offerer declined (reported)</option>
      <option value="requester_no_reported">Requester declined (reported)</option>
      <option value="handoff_reported">Handoff reported · not verified</option>
      <option value="benefit_reported">Benefit reported · not causal proof</option>
      <option value="no_benefit_reported">No benefit reported</option>
      <option value="unknown_reported">Outcome unknown</option>
    </select></div>
    <div><label for="follow-source">Source of account</label>
     <select id="follow-source"><option value="operator_heard_owner">I heard it from the person</option><option value="owner_self_report">I am that person</option><option value="third_party_unverified">Secondhand report</option></select>
    </div></div>
   <label for="follow-note">Witness note · separate what was heard from inference</label>
   <textarea id="follow-note" maxlength="360" placeholder="What was said? By whom? What remains unknown? (No personal details.)"></textarea>
   <button type="submit">Append unverified observation</button>
  </form>
 </section>
 <section class="paper">
  <div class="panel-head"><div class="eyebrow">04 · THE RECORD</div>
   <h2>What remains witnessed?</h2>
   <p>Original cards remain in this log when withdrawn. Reports are added rather than silently rewriting past claims.</p>
  </div>
  <h3>Reported cards</h3><div id="cards-list" class="records"></div>
  <h3 style="margin-top:25px">Encounter reports</h3><div id="journal-list" class="records"></div>
 </section>
</div>
<footer><p>MOTIF / FIELD-001 · OPERATOR-ENTERED REPORTS ONLY · CURRENT TIME COMES FROM DEVICE CLOCK · LOG HASHES, IF ANALYZED, ARE NOT SIGNATURES<br>
MATCHED RECORDS ≠ AUTHENTICATED CONSENT · REPORTED HANDOFF ≠ VERIFIED OUTCOME · REPORTED BENEFIT ≠ CAUSAL IMPACT<br>
THIS IS A LOCAL RESEARCH PROTOTYPE, NOT A LIVE MATCHMAKING OR EMERGENCY SERVICE. NEVER ENTER SENSITIVE PERSONAL DATA.</p></footer>
</main>
<script>
__ENGINE__
</script>
<script>
__APP__
</script>
</body>
</html>'''


def build() -> str:
    folder = Path(__file__).resolve().parent
    engine = (folder / "field_pilot.js").read_text(encoding="utf-8")
    app = (folder / "field_app.js").read_text(encoding="utf-8")
    if "</script" in engine.lower() or "</script" in app.lower():
        raise ValueError("script terminator in source")
    return PAGE.replace("__ENGINE__", engine).replace("__APP__", app)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("field-witness.html"))
    args = parser.parse_args()
    args.output.write_text(build(), encoding="utf-8")
    print("Created offline human field witness desk:", args.output)
