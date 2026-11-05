/* FIELD-001: browser-side review engine, no network or storage side effects.
   Mirrored against field_protocol.py through golden and hostile tests. */
(function (root) {
  "use strict";
  const SCHEMA = "motif.field-log/v0";
  const ORIGINS = ["owner_self_report", "operator_heard_owner", "third_party_unverified"];
  const EVENTS = [
    "candidate_proposed",
    "provider_yes_reported", "requester_yes_reported",
    "provider_no_reported", "requester_no_reported", "handoff_reported",
    "benefit_reported", "no_benefit_reported", "unknown_reported",
    "card_withdrawn"
  ];
  const CARD_KEYS = ["id","kind","alias","topic","area","note","created_at","expires_at","origin","share_ok"];
  const EVENT_KEYS = ["id","subject","kind","reporter","source","occurred_at","recorded_at","note"];
  function fail(message) { throw new Error(message); }
  function exact(o, keys, label) {
    if (!o || typeof o !== "object" || Array.isArray(o)) fail(label + " must be an object");
    const actual = Object.keys(o).sort().join("|");
    if (actual !== keys.slice().sort().join("|")) fail(label + " has missing or unexpected fields");
  }
  function stamp(value) {
    if (typeof value !== "string" || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value)) fail("UTC timestamp required");
    const date = new Date(value);
    if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0,19)+"Z" !== value) fail("invalid UTC timestamp");
    return date.getTime();
  }
  function id(value) {
    return typeof value === "string" && /^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$/.test(value);
  }
  function text(value, max, blank) {
    return typeof value === "string" && value.length <= max && (blank || value.trim().length > 0);
  }
  function compatible(a,b) {
    return a.topic===b.topic && a.area===b.area && a.alias!==b.alias
      && a.share_ok && b.share_ok
      && a.origin!=="third_party_unverified"
      && b.origin!=="third_party_unverified";
  }
  function pairId(a,b) { return "pair:"+a.id+":"+b.id; }
  function validate(log) {
    exact(log, ["schema","cards","events"], "field log");
    if (log.schema !== SCHEMA || !Array.isArray(log.cards) || log.cards.length>300
        || !Array.isArray(log.events) || log.events.length>2000) fail("invalid field-log schema or size");
    const ids = new Set(), cards = new Map();
    for (const c of log.cards) {
      exact(c,CARD_KEYS,"card");
      if (!id(c.id) || ids.has(c.id)) fail("invalid or duplicate card ID");
      ids.add(c.id); cards.set(c.id,c);
      if (!["offer","need"].includes(c.kind) || !text(c.alias,60,false)
          || !/^[a-z0-9][a-z0-9 _-]{0,39}$/.test(c.topic)
          || !/^[a-z0-9][a-z0-9 _-]{0,39}$/.test(c.area)
          || !text(c.note,360,true) || !ORIGINS.includes(c.origin)
          || typeof c.share_ok!=="boolean"
          || (c.origin==="third_party_unverified" && c.share_ok)) fail("invalid or unauthorized card");
      if (stamp(c.created_at)>=stamp(c.expires_at)) fail("card expiry must follow creation");
    }
    const pairs = new Set();
    for (const a of log.cards) for (const b of log.cards) {
      if (a.kind==="offer" && b.kind==="need" && compatible(a,b)) pairs.add(pairId(a,b));
    }
    const eventIds = new Set(), proposalSeen=new Set(), observedSubjects=new Set();
    let lastRecorded=-Infinity;
    for (const e of log.events) {
      exact(e,EVENT_KEYS,"event");
      if (!id(e.id) || eventIds.has(e.id) || !EVENTS.includes(e.kind)
          || ![...ORIGINS,"operator_generated"].includes(e.source)
          || (e.kind==="candidate_proposed") !== (e.source==="operator_generated")
          || !text(e.reporter,60,false)
          || !text(e.note,360,true)) fail("invalid or duplicate event");
      eventIds.add(e.id);
      const recorded=stamp(e.recorded_at);
      if (stamp(e.occurred_at)>recorded) fail("future occurrence is not an observation");
      if(recorded<lastRecorded)fail("event recording order must be append-only");
      lastRecorded=recorded;
      if (e.kind==="card_withdrawn" ? !cards.has(e.subject) : !pairs.has(e.subject))
        fail("event references unknown card or unsupported pair");
      if(e.kind==="candidate_proposed") {
        if(proposalSeen.has(e.subject)||observedSubjects.has(e.subject))
          fail("cannot backdate or duplicate a prospective model proposal");
        proposalSeen.add(e.subject);
      } else if(e.kind!=="card_withdrawn") observedSubjects.add(e.subject);
    }
    return log;
  }
  function empty() { return {schema:SCHEMA,cards:[],events:[]}; }
  function utcNow() {return new Date().toISOString().slice(0,19)+"Z";}
  function generateId(prefix, log) {
    const used = new Set([...log.cards.map(x=>x.id),...log.events.map(x=>x.id)]);
    // random UUID if available; fall back to sufficiently variable local-only
    // identifier. An ID is not an identity, authentication or provenance proof.
    for (let i=0;i<50;i++) {
      const bits = typeof crypto!=="undefined" && crypto.getRandomValues
        ? Array.from(crypto.getRandomValues(new Uint8Array(8)),
                     b=>b.toString(16).padStart(2,"0")).join("")
        : String(Date.now())+"-"+String(Math.floor(Math.random()*1e12));
      const candidate=prefix+"-"+bits;
      if (!used.has(candidate)) return candidate;
    }
    fail("could not allocate unique local record ID");
  }
  function addCard(log, data, now=utcNow()) {
    validate(log); stamp(now);
    const c = {
      id:generateId("card",log),kind:data.kind,alias:data.alias.trim(),
      topic:data.topic.trim().toLowerCase(),
      area:data.area.trim().toLowerCase(),note:data.note.trim(),
      created_at:now,expires_at:data.expires_at,origin:data.origin,
      share_ok:!!data.share_ok,
    };
    validate({...log,cards:[...log.cards,c]});
    log.cards.push(c);
    return c;
  }
  function addEvent(log,data,now=utcNow()) {
    validate(log); stamp(now);
    const event = {
      id:generateId("event",log),subject:data.subject,kind:data.kind,
      reporter:data.reporter.trim(),source:data.source,
      occurred_at:now,recorded_at:now,note:data.note.trim(),
    };
    validate({...log,events:[...log.events,event]});
    log.events.push(event); return event;
  }
  function allCompatiblePairs(log) {
    validate(log);
    const out=[];
    for (const a of log.cards.filter(c=>c.kind==="offer"))
      for (const b of log.cards.filter(c=>c.kind==="need"))
        if (compatible(a,b)) out.push({
          id:pairId(a,b), offer:a,need:b,
          expires_at:a.expires_at<b.expires_at?a.expires_at:b.expires_at
        });
    return out.sort((a,b)=>a.id.localeCompare(b.id));
  }
  function eligible(log,now=utcNow()) {
    validate(log);
    const at=stamp(now);
    const withdrawn = new Set(log.events.filter(e=>
      e.kind==="card_withdrawn" && stamp(e.occurred_at)<=at
    ).map(e=>e.subject));
    const active = c => stamp(c.created_at)<=at && at<stamp(c.expires_at)
      && !withdrawn.has(c.id);
    const offers=log.cards.filter(c=>c.kind==="offer"&&active(c));
    const needs=log.cards.filter(c=>c.kind==="need"&&active(c));
    const out=[];
    for (const a of offers) for (const b of needs) {
      if (!compatible(a,b)) continue;
      const mid=pairId(a,b);
      const history=log.events.filter(e=>e.subject===mid&&stamp(e.occurred_at)<=at);
      const types=new Set(history.filter(e=>
        e.source!=="third_party_unverified"
        || !["provider_yes_reported","requester_yes_reported"].includes(e.kind)
      ).map(e=>e.kind));
      let disposition="HOLD_CONFIRM_DIRECTLY";
      if (types.has("provider_no_reported") || types.has("requester_no_reported"))
        disposition="CLOSED_DECLINED_REPORTED";
      else if (types.has("benefit_reported") && types.has("no_benefit_reported"))
        disposition="CONFLICTING_OUTCOME_REPORTS";
      else if (types.has("benefit_reported")) disposition="BENEFIT_REPORTED_NOT_CAUSAL";
      else if (types.has("no_benefit_reported")) disposition="NO_BENEFIT_REPORTED";
      else if (types.has("handoff_reported")) disposition="HANDOFF_REPORTED_NOT_VERIFIED";
      else if (types.has("provider_yes_reported")&&types.has("requester_yes_reported"))
        disposition="DUAL_YES_REPORTED_NOT_VERIFIED";
      out.push({
        id:mid,offer_id:a.id,need_id:b.id,
        offer_alias:a.alias,need_alias:b.alias,
        topic:a.topic,area:a.area,
        expires_at:a.expires_at<b.expires_at?a.expires_at:b.expires_at,
        disposition,events:history.length,
        boundary:"candidate only; direct agreement and safety unverified"
      });
    }
    return out.sort((a,b)=>a.expires_at.localeCompare(b.expires_at)||a.id.localeCompare(b.id));
  }
  function summary(log,now=utcNow()) {
    const pairs=eligible(log,now),counts={};
    for(const e of log.events) counts[e.kind]=(counts[e.kind]||0)+1;
    const proposed=new Set(log.events.filter(e=>e.kind==="candidate_proposed").map(e=>e.subject));
    const followed=new Set(log.events.filter(e=>e.kind!=="candidate_proposed"&&e.kind!=="card_withdrawn").map(e=>e.subject));
    return {
      prospective_proposals_recorded:counts.candidate_proposed||0,
      unresolved_proposals:[...proposed].filter(id=>!followed.has(id)).length,
      eligible_pairs:pairs.length,
      active_candidate_pairs:pairs.filter(x=>
        ["HOLD_CONFIRM_DIRECTLY","DUAL_YES_REPORTED_NOT_VERIFIED"].includes(x.disposition)).length,
      benefit_reports:counts.benefit_reported||0,
      no_benefit_reports:counts.no_benefit_reported||0,
      handoff_reports:counts.handoff_reported||0,
      unknown_reports:counts.unknown_reported||0,
      declined_reports:(counts.provider_no_reported||0)+(counts.requester_no_reported||0),
      causal_effect_identified:false,authorship_verified:false,
      pairs
    };
  }
  function demo() {
    return {schema:SCHEMA,cards:[
      {id:"demo-offer",kind:"offer",alias:"Demo A",topic:"cooler",
       area:"fictional-town",note:"Spare insulated box",
       created_at:"2026-11-04T15:00:00Z",expires_at:"2026-11-05T15:00:00Z",
       origin:"owner_self_report",share_ok:true},
      {id:"demo-need",kind:"need",alias:"Demo B",topic:"cooler",
       area:"fictional-town",note:"Need a box for a short trip",
       created_at:"2026-11-04T15:00:00Z",expires_at:"2026-11-05T15:00:00Z",
       origin:"owner_self_report",share_ok:true}
    ],events:[]};
  }
  const api={SCHEMA,empty,validate,utcNow,addCard,addEvent,eligible,allCompatiblePairs,summary,demo,pairId};
  if (typeof module!=="undefined" && module.exports) module.exports=api;
  root.FieldPilot=api;
})(typeof globalThis==="object"?globalThis:this);
