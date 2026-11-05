/* FIELD-001 browser operator desk. Only in-memory state until explicit export.
   No fetch/XHR/WebSocket, no third-party code, no automatic contact. */
(function () {
  "use strict";
  const F=globalThis.FieldPilot;
  if (!F) throw new Error("FIELD-001 engine missing");
  const $=id=>document.getElementById(id);
  let log=F.empty(), demo=false, dirty=false, selectedPair=null;
  const now=()=>F.utcNow();
  const timeLabel=s=>new Date(s).toLocaleString();
  const nice=s=>s.replaceAll("_"," ").replaceAll("-"," ");
  function el(tag,cl,value) {
    const x=document.createElement(tag);
    if(cl) x.className=cl;
    if(value!==undefined) x.textContent=value;
    return x;
  }
  function status(message,error=false) {
    $("statusline").textContent=message;
    $("statusline").className=error?"statusline error":"statusline";
  }
  function appendText(parent,tag,cl,value) {
    const x=el(tag,cl,value);parent.appendChild(x);return x;
  }
  function setDirty() {
    dirty=true;
    $("unsaved").textContent="UNSAVED FIELD LOG · export to keep your records";
  }
  function resetDirty() {
    dirty=false;
    $("unsaved").textContent="EXPORT AFTER EACH FIELD SESSION · browser memory is temporary";
  }
  function isDemo(logData) {return logData.cards.some(c=>c.id.startsWith("demo-"));}
  function setMode() {
    $("mode").textContent=demo?"FICTIONAL DEMONSTRATION · NOT FIELD EVIDENCE":
      "REAL-WORLD OPERATOR INTAKE · REPORTS ARE UNVERIFIED";
    $("mode").className=demo?"mode demo":"mode";
    for(const id of ["add-card","add-event"]) {
      const form=$(id);
      for(const input of form.querySelectorAll("input, select, textarea, button"))
        input.disabled=demo;
    }
  }
  function cards() {
    const zone=$("cards-list");zone.replaceChildren();
    const withdrawn=new Set(log.events.filter(e=>e.kind==="card_withdrawn").map(e=>e.subject));
    if(!log.cards.length) {appendText(zone,"p","empty","No records yet. Start with one offer or need.");return;}
    for(const c of log.cards.slice().reverse()){
      const wrap=el("article","record");
      const h=el("div","record-head");
      appendText(h,"strong","",c.kind.toUpperCase()+" · "+c.topic);
      appendText(h,"span","small",c.alias+" · "+c.area);
      wrap.appendChild(h);
      appendText(wrap,"p","",c.note||"No additional description.");
      const expired=Date.parse(c.expires_at)<=Date.now();
      const ended=withdrawn.has(c.id);
      appendText(wrap,"div","meta", (ended?"WITHDRAWN · ":expired?"EXPIRED · ":"ACTIVE REPORT · ")
        +nice(c.origin)+" · expires "+timeLabel(c.expires_at)
        +" · intro willingness "+(c.share_ok?"REPORTED":"NOT REPORTED"));
      if(!ended && !demo){
        const btn=el("button","textbutton","Record withdrawal");
        btn.type="button";
        btn.addEventListener("click",()=>{
          if(!confirm("Record withdrawal for this card? The original card will remain in the exported history."))return;
          const observer=$("observer").value.trim();
          if(!observer){status("Enter your reporter alias before recording a withdrawal.",true);return;}
          try{
            F.addEvent(log,{subject:c.id,kind:"card_withdrawn",reporter:observer,
              source:"operator_heard_owner",note:"Withdrawal recorded by operator"},now());
            setDirty();render();status("Withdrawal report appended; original entry retained.");
          }catch(e){status(e.message,true);}
        });
        wrap.appendChild(btn);
      }
      zone.appendChild(wrap);
    }
  }
  function candidates() {
    const box=$("matches-list");box.replaceChildren();
    const rows=F.eligible(log,now());
    if(!rows.length){
      appendText(box,"p","empty","No current eligible pairing. You need an unexpired OFFER and NEED for the same topic and broad area, with both parties' willingness to introduce reported. This is not proof that nobody needs help.");
    }
    for(const row of rows) {
      const wrap=el("article","match");
      const h=el("div","record-head");
      appendText(h,"strong","",row.offer_alias+" ↔ "+row.need_alias);
      appendText(h,"span","pill",row.topic+" · "+row.area);
      wrap.appendChild(h);
      appendText(wrap,"p","", "Both records describe a possible introduction. No real agreement, resource availability, travel time or exchange is verified.");
      const meta=el("div","meta",nice(row.disposition)+" · expires "+timeLabel(row.expires_at));
      if(row.disposition.includes("DECLINED")||row.disposition.includes("CONFLICT"))
        wrap.classList.add("warning");
      wrap.appendChild(meta);
      const buttons=el("div","buttonrow");
      const alreadyProposed=log.events.some(e=>e.subject===row.id&&e.kind==="candidate_proposed");
      const hasReports=log.events.some(e=>e.subject===row.id&&e.kind!=="candidate_proposed");
      const freeze=el("button","outline",alreadyProposed?"Candidate recorded":"Record prospective candidate");
      freeze.disabled=demo||alreadyProposed||hasReports;
      freeze.addEventListener("click",()=>{
        const observer=$("observer").value.trim();
        if(!observer){
          status("Enter your reporter alias in section 03 before freezing a prospective candidate.",true);
          $("observer").focus();return;
        }
        try{
          F.addEvent(log,{
            subject:row.id,kind:"candidate_proposed",reporter:observer,
            source:"operator_generated",
            note:"FIELD-001 exact topic+area proposal; no handoff outcome predicted or observed.",
          },now());
          setDirty();render();
          status("Candidate frozen BEFORE follow-up. Actual result remains unknown.");
        }catch(e){status(e.message,true);}
      });
      buttons.appendChild(freeze);
      const intro=el("button","outline","Prepare introduction");
      intro.addEventListener("click",()=>{
        $("intro-draft").value="Possible introduction (DRAFT — NOT SENT):\n\n"
          +row.offer_alias+" reports offering "+row.topic+" in the broad area \""+row.area+"\".\n"
          +row.need_alias+" reports needing "+row.topic+" there.\n\n"
          +"Before exchanging any contact details, confirm BOTH people currently agree to be introduced; confirm availability, timing, suitability, safety and any costs directly. No inventory is reserved and this draft proves no consent.";
        selectedPair=row.id;
        $("follow-subject").value=row.id;
        $("intro-draft").focus();
        status("Introduction draft prepared locally. Nothing sent.");
      });
      const follow=el("button","outline","Record follow-up");
      follow.addEventListener("click",()=>{
        selectedPair=row.id;
        $("follow-subject").value=row.id;
        $("add-event").scrollIntoView({behavior:"smooth",block:"center"});
      });
      buttons.append(intro,follow);wrap.appendChild(buttons);box.appendChild(wrap);
    }
    const select=$("follow-subject"),previous=select.value||selectedPair;
    select.replaceChildren();
    const option=el("option","", "Choose a previously eligible pair");
    option.value="";select.appendChild(option);
    for(const row of F.allCompatiblePairs(log)){
      const o=el("option","",row.offer.alias+" ↔ "+row.need.alias+" · "+row.offer.topic
        +(Date.parse(row.expires_at)<=Date.now()?" (EXPIRED; follow-up allowed)":""));
      o.value=row.id;select.appendChild(o);
    }
    if([...select.options].some(o=>o.value===previous)) select.value=previous;
  }
  function journal() {
    const box=$("journal-list");box.replaceChildren();
    if(!log.events.length){appendText(box,"p","empty","No reported encounters yet. Missing follow-up is UNKNOWN, not failure.");return;}
    for(const e of log.events.slice().reverse()) {
      const row=el("div","event");
      appendText(row,"strong","",nice(e.kind));
      appendText(row,"span","small",timeLabel(e.recorded_at)+" · "+e.reporter
        +" · "+nice(e.source));
      if(e.note) appendText(row,"p","",e.note);
      box.appendChild(row);
    }
  }
  function render() {
    setMode();
    let s;
    try {s=F.summary(log,now());}
    catch(e){status("Invalid field log: "+e.message,true);return;}
    $("metric-cards").textContent=String(log.cards.length);
    $("metric-proposed").textContent=String(s.prospective_proposals_recorded);
    $("metric-unresolved").textContent=String(s.unresolved_proposals);
    $("metric-pairs").textContent=String(s.active_candidate_pairs);
    $("metric-handoffs").textContent=String(s.handoff_reports);
    $("metric-benefit").textContent=String(s.benefit_reports);
    $("metric-no-benefit").textContent=String(s.no_benefit_reports);
    $("metric-unknown").textContent=String(s.unknown_reports);
    cards();candidates();journal();
  }
  function download(name,data,mime) {
    const blob=new Blob([data],{type:mime});
    const href=URL.createObjectURL(blob);
    const a=document.createElement("a");a.href=href;a.download=name;
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(href),2000);
  }
  $("add-card").addEventListener("submit",event=>{
    event.preventDefault();if(demo) return;
    const hours=Number($("card-hours").value);
    if(!Number.isInteger(hours)||hours<1||hours>168){
      status("Lifetime must be a whole number of hours from 1 to 168.",true);return;
    }
    const expiry=new Date(Date.now()+hours*3600000).toISOString().slice(0,19)+"Z";
    try {
      F.addCard(log,{
        kind:$("card-kind").value,alias:$("card-alias").value,
        topic:$("card-topic").value,area:$("card-area").value,
        note:$("card-note").value,expires_at:expiry,
        origin:$("card-origin").value,share_ok:$("card-share").checked
      },now());
      $("add-card").reset();$("card-hours").value="24";
      setDirty();render();
      status("Card appended. Matching is only a suggested introduction; no permission was verified.");
    }catch(e){status(e.message,true);}
  });
  $("add-event").addEventListener("submit",event=>{
    event.preventDefault();if(demo)return;
    try{
      if(!$("follow-subject").value) throw new Error("Choose a pair for follow-up.");
      F.addEvent(log,{
        subject:$("follow-subject").value,
        kind:$("follow-kind").value,
        reporter:$("observer").value,
        source:$("follow-source").value,
        note:$("follow-note").value,
      },now());
      $("follow-note").value="";setDirty();render();
      status("Report appended as an unverified observation; it is not proof of causality.");
    }catch(e){status(e.message,true);}
  });
  $("export").addEventListener("click",()=>{
    try {
      F.validate(log);
      const timestamp=now().replaceAll(":","-");
      download("motif-field-log-"+timestamp+(demo?"-DEMO":"")+".json",
        JSON.stringify(log,null,2)+"\n","application/json");
      resetDirty();
      status((demo?"Fictional example":"Unverified field log")+" exported. Store the file privately; it contains sensitive notes if you typed them.");
    }catch(e){status("Cannot export: "+e.message,true);}
  });
  $("import-file").addEventListener("change",async event=>{
    const file=event.target.files[0];
    if(!file)return;
    try{
      if(file.size>220000) throw new Error("File larger than the pilot's 220 KB import cap.");
      const imported=JSON.parse(await file.text());
      F.validate(imported);
      if(dirty&&!confirm("Replace unsaved field records? Export your current log first if needed."))return;
      log=imported;demo=isDemo(log);selectedPair=null;
      resetDirty();render();status("Imported local file; authorship and timestamps are NOT verified.");
    }catch(e){status("Import refused: "+e.message,true);}
    finally{event.target.value="";}
  });
  $("load-demo").addEventListener("click",()=>{
    if(dirty&&!confirm("Replace unsaved real field records with a fictional example?"))return;
    log=F.demo();demo=true;selectedPair=null;
    // The demo labels remain demo-*; shift expiry to future solely for display.
    const timestamp=now(), expiry=new Date(Date.now()+86400000).toISOString().slice(0,19)+"Z";
    for(const c of log.cards){c.created_at=timestamp;c.expires_at=expiry;}
    resetDirty();render();status("Fictional example loaded. It is not field evidence.");
  });
  $("new-log").addEventListener("click",()=>{
    if(dirty&&!confirm("Discard unsaved field records? Export them first if needed."))return;
    log=F.empty();demo=false;selectedPair=null;
    $("intro-draft").value="";resetDirty();render();
    status("Empty real-world field journal. No records have been entered.");
  });
  $("copy-intro").addEventListener("click",async()=>{
    const message=$("intro-draft").value;
    if(!message){status("Prepare a candidate introduction first.",true);return;}
    try {await navigator.clipboard.writeText(message);status("Draft copied. Nothing sent.");}
    catch(e){$("intro-draft").focus();$("intro-draft").select();
      status("Clipboard unavailable; draft selected for manual copy.",true);}
  });
  window.addEventListener("beforeunload",e=>{
    if(dirty&&!demo){e.preventDefault();e.returnValue="";}
  });
  resetDirty();render();
  status("Ready. Add genuine operator-reported offers or needs; no external connections will occur.");
})();
