"use strict";
const assert = require("node:assert/strict");
const F=require("./field_pilot.js");
const t="2026-11-04T18:00:00Z";

const make=()=>F.demo();
function ev(kind, subject="pair:demo-offer:demo-need", id="a") {
 return {id,subject,kind,reporter:"Operator A",source:"operator_heard_owner",
         occurred_at:"2026-11-04T16:00:00Z",recorded_at:"2026-11-04T17:00:00Z",note:""};
}
function fails(f){assert.throws(f,Error);}
function run() {
 let log=make();
 assert.equal(F.eligible(log,t).length,1);
 assert.equal(F.eligible(log,t)[0].disposition,"HOLD_CONFIRM_DIRECTLY");
 assert.equal(F.eligible(log,"2026-11-05T15:00:00Z").length,0);
 assert.equal(F.eligible(log,"2026-11-03T15:00:00Z").length,0);
 assert.equal(F.summary(log,t).causal_effect_identified,false);
 assert.equal(F.summary(log,t).authorship_verified,false);
 assert.equal(F.empty().cards.length,0);

 for(const [key,value] of [["topic","other"],["area","elsewhere"],["alias","Demo A"]]){
  log=make();log.cards[1][key]=value;
  assert.equal(F.eligible(log,t).length,0);
 }
 log=make();log.cards[0].share_ok=false;
 assert.equal(F.eligible(log,t).length,0);
 log=make();log.cards[0].origin="third_party_unverified";
 fails(()=>F.validate(log));

 log=make();log.events=[ev("provider_yes_reported")];
 assert.equal(F.eligible(log,t)[0].disposition,"HOLD_CONFIRM_DIRECTLY");
 log.events.push(ev("requester_yes_reported",undefined,"b"));
 assert.equal(F.eligible(log,t)[0].disposition,"DUAL_YES_REPORTED_NOT_VERIFIED");

 log=make();let e=ev("provider_yes_reported");e.source="third_party_unverified";
 log.events=[e,ev("requester_yes_reported",undefined,"b")];
 assert.equal(F.eligible(log,t)[0].disposition,"HOLD_CONFIRM_DIRECTLY");

 log=make();log.events=[ev("benefit_reported")];
 assert.equal(F.eligible(log,t)[0].disposition,"BENEFIT_REPORTED_NOT_CAUSAL");
 log.events.push(ev("no_benefit_reported",undefined,"b"));
 assert.equal(F.eligible(log,t)[0].disposition,"CONFLICTING_OUTCOME_REPORTS");
 assert.equal(F.summary(log,t).benefit_reports,1);

 log=make();log.events=[ev("unknown_reported")];
 assert.equal(F.summary(log,t).no_benefit_reports,0);
 assert.equal(F.summary(log,t).unknown_reports,1);

 log=make();log.events=[ev("requester_no_reported")];
 assert.equal(F.eligible(log,t)[0].disposition,"CLOSED_DECLINED_REPORTED");

 log=make();log.events=[ev("card_withdrawn","demo-offer")];
 assert.equal(F.eligible(log,t).length,0);

 log=make();log.events=[ev("benefit_reported","pair:missing:pair")];
 fails(()=>F.validate(log));
 log=make();log.events=[ev("card_withdrawn","fake")];
 fails(()=>F.validate(log));
 log=make();log.events=[ev("benefit_reported"),ev("unknown_reported")];
 fails(()=>F.validate(log));
 log=make();log.events=[ev("unknown_reported")];
 log.events[0].occurred_at="2026-11-05T15:00:00Z";
 fails(()=>F.validate(log));

 log=F.empty();
 const first=F.addCard(log,{kind:"offer",alias:"Alias-A",topic:"  tool ",
   area:"waseca",note:"",expires_at:"2026-11-05T18:00:00Z",
   origin:"operator_heard_owner",share_ok:false},t);
 const second=F.addCard(log,{kind:"need",alias:"Alias-B",topic:"tool",
   area:"waseca",note:"",expires_at:"2026-11-05T18:00:00Z",
   origin:"operator_heard_owner",share_ok:true},t);
 assert.equal(F.eligible(log,t).length,0);
 assert.equal(first.topic,"tool");
 assert.equal(second.area,"waseca");
 assert.equal(log.cards.length,2);
 const withdrawal=F.addEvent(log,{subject:first.id,kind:"card_withdrawn",
   reporter:"Operator",source:"operator_heard_owner",note:""},t);
 assert.equal(withdrawal.kind,"card_withdrawn");
 assert.equal(log.events.length,1);

 log=make();log.cards[0].note="x".repeat(361);fails(()=>F.validate(log));
 log=make();log.cards.push(log.cards[0]);fails(()=>F.validate(log));
 console.log("FIELD-001 JavaScript tests passed");
}
run();
