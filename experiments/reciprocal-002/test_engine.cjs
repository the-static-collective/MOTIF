"use strict";
const assert=require("node:assert/strict");
const M=require("./two_doors.js");
const T=1800000000000,DAY=86400000;
const base={title:"Which step blocks first understanding?",why:"Improve an actual entry experience.",
 decision:"Decide which page explanation to revise.",options:["Door confusing","Answer confusing","Clear"],
 roles:["anyone"],priority:4,minRoots:3,maxRoots:8,openAt:T,closeAt:T+7*DAY};
let tests=[];
function test(name,fn){tests.push([name,fn]);}
function newState(patch={},id="q_001"){return M.addQuestion(M.empty(),{...base,...patch},T,id);}
function contribute(s,root,choice,at,role="newcomer",extra={}){
 return M.event(s,{id:"e_"+root+"_"+at,questionId:s.questions[0].id,
   root,role,at,kind:"ANSWER",choice,method:"experience",note:"",...extra});
}
function profile(root,roles=["anyone"],willing=true){return {root,roles,willing};}
test("every queued question has a meaningful declared purpose and bounded life",()=>{
 const s=newState();M.validateState(s);
 assert.equal(s.questions[0].decision,base.decision);
 assert.throws(()=>newState({decision:""}),/MISSING_PURPOSE/);
 assert.throws(()=>newState({options:["same","same"]}),/INVALID_OPTIONS/);
 assert.throws(()=>newState({maxRoots:1}),/INVALID_BUDGET/);
 assert.throws(()=>newState({closeAt:T+31*DAY}),/INVALID_WINDOW/);
 assert.throws(()=>newState({roles:["personal-secret"]}),/INVALID_ROLES/);
});
test("consent gate means no volunteer, no automated question",()=>{
 const s=newState();
 assert.throws(()=>M.choose(s,profile("source1",["anyone"],false),T+1),/NOT_OPTED_IN/);
 assert.ok(M.choose(s,profile("source1"),T+1));
});
test("expertise is a self-declared source match, not a demographic or anonymous wildcard",()=>{
 const s=newState({roles:["organizer","maker"]});
 assert.equal(M.choose(s,profile("source1",["anyone"]),T+1),null);
 assert.equal(M.choose(s,profile("source1",["researcher"]),T+1),null);
 assert.equal(M.choose(s,profile("source1",["organizer"]),T+1).question.id,"q_001");
});
test("status separates not-yet-open, open, and expired",()=>{
 const s=newState({openAt:T+2*DAY,closeAt:T+3*DAY});
 assert.equal(M.inspect(s,"q_001",T).status,"WAIT_WINDOW");
 assert.equal(M.choose(s,profile("source1"),T),null);
 assert.equal(M.inspect(s,"q_001",T+2*DAY+1).status,"OPEN");
 assert.equal(M.inspect(s,"q_001",T+3*DAY).status,"HOLD_EXPIRED");
});
test("three independent claimed sources justify REVIEW, never truth",()=>{
 let s=newState();
 for(let i=0;i<3;i++)s=contribute(s,"source"+i,0,T+100+i);
 const a=M.inspect(s,"q_001",T+200);
 assert.equal(a.n,3);assert.equal(a.status,"READY_FOR_REVIEW");
 assert.equal(a.evidenceLabel,"CLAIMED_LOCAL_SOURCES_NOT_VERIFIED_GROUND_TRUTH");
 assert.equal(M.choose(s,profile("source11"),T+200),null);
});
test("same pseudonym cannot vote twice without conflict; preserves both source events",()=>{
 let s=newState();
 s=contribute(s,"source1",0,T+100);
 s=contribute(s,"source1",2,T+101);
 const a=M.inspect(s,"q_001",T+102);
 assert.equal(a.n,1);assert.equal(a.contested,1);
 assert.equal(a.status,"HOLD_CONTEST");
 assert.equal(s.events.length,2);
 assert.equal(M.choose(s,profile("source2"),T+102),null);
});
test("explicit revision supersedes current vote, leaves original preserved",()=>{
 let s=newState();
 s=contribute(s,"source1",0,T+100);
 s=M.event(s,{id:"revised_01",questionId:"q_001",root:"source1",role:"newcomer",
  at:T+102,kind:"REVISE",revises:s.events[0].id,choice:1,method:"reasoning",note:"I changed my view."});
 const e=M.effective(s,"q_001");
 assert.equal(e.answers.length,1);assert.equal(e.answers[0].choice,1);
 assert.equal(e.contested.length,0);assert.equal(s.events[0].choice,0);assert.equal(s.events.length,2);
 assert.throws(()=>M.event(s,{id:"revised_02",questionId:"q_001",root:"other",role:"anyone",
  at:T+103,kind:"REVISE",revises:s.events[0].id,choice:2,method:"reasoning",note:""}),/INVALID_REVISION_TARGET/);
});
test("decline means no repeat solicitation; willingness never inferred",()=>{
 let s=newState();
 s=M.event(s,{id:"decline_001",questionId:"q_001",root:"source1",role:"newcomer",
  at:T+2,kind:"DECLINE"});
 assert.equal(M.choose(s,profile("source1"),T+5),null);
 assert.ok(M.choose(s,profile("source2"),T+5));
});
test("insufficient perspective diversity halts redundant audiences",()=>{
 let s=newState({roles:["newcomer","maker"]});
 for(let i=0;i<3;i++)s=contribute(s,"src"+i,0,T+100+i,"newcomer");
 assert.equal(M.inspect(s,"q_001",T+200).status,"NEED_OTHER_ROLE");
 assert.equal(M.choose(s,profile("source10",["newcomer"]),T+200),null);
 assert.equal(M.choose(s,profile("source10",["maker"]),T+200).question.id,"q_001");
 s=contribute(s,"source10",0,T+201,"maker");
 assert.equal(M.inspect(s,"q_001",T+202).status,"READY_FOR_REVIEW");
});
test("meaningful unresolved contradiction produces early REFRAME not polling forever",()=>{
 let s=newState();
 for(let i=0;i<6;i++)s=contribute(s,"source"+i,i%2,T+100+i);
 assert.equal(M.inspect(s,"q_001",T+300).status,"NEEDS_REFRAME");
 assert.equal(M.choose(s,profile("another"),T+301),null);
});
test("budget expiration stops asking even without convergence",()=>{
 let s=newState();
 for(let i=0;i<8;i++)s=contribute(s,"source"+i,i<5?0:1,T+100+i);
 assert.equal(M.inspect(s,"q_001",T+300).status,"HOLD_BUDGET");
 assert.equal(M.choose(s,profile("another"),T+301),null);
});
test("questions are actually ranked, with purpose importance and urgency",()=>{
 let s=M.empty();
 s=M.addQuestion(s,{...base,priority:2,closeAt:T+7*DAY},T,"q_low");
 s=M.addQuestion(s,{...base,title:"Another useful decision",priority:5},T,"q_high");
 const picked=M.choose(s,profile("source1"),T+10);
 assert.equal(picked.question.id,"q_high");
 assert.ok(picked.why[0].startsWith("Could change:"));
});
test("valid exports merge deduplicated source events without inventing conclusions",()=>{
 let a=newState(),b=M.empty();
 b=M.addQuestion(b,{...base},T,"q_001");
 b=contribute(b,"source1",0,T+100);
 a=M.merge(a,b);
 assert.equal(a.events.length,1);
 assert.equal(M.merge(a,b).events.length,1);
 assert.equal(M.inspect(a,"q_001",T+100).n,1);
});
test("conflicting question identifiers and conflicting event identifiers refuse import",()=>{
 let a=newState(),b=newState({title:"A different question with same ID"});
 assert.throws(()=>M.merge(a,b),/QUESTION_SOURCE_CONFLICT/);
 b=newState();
 a=contribute(a,"source1",0,T+100);
 b=contribute(b,"source2",0,T+101);
 // Both events use different IDs, still merge.
 assert.equal(M.merge(a,b).events.length,2);
 b=JSON.parse(JSON.stringify(a));
 b.events[0].choice=1;
 assert.throws(()=>M.merge(a,b),/EVENT_SOURCE_CONFLICT/);
});
test("resists malicious import, malformed events, unbounded text and source signatures",()=>{
 let a=newState();
 for(const invalid of [
   {...a,schema:"motif.unknown"},
   {...a,questions:[{...a.questions[0],title:""}]},
   {...a,events:[{id:"evil_script",questionId:"q_001",root:"source1",role:"secret",
     at:T+1,kind:"ANSWER",choice:0,method:"experience",note:"",revises:null}]}
 ])assert.throws(()=>M.validateState(invalid));
 assert.throws(()=>contribute(a,"ab",0,T+100),/BAD_SOURCE/);
 assert.throws(()=>contribute(a,"source1",9,T+100),/BAD_CHOICE/);
});
test("intentional demo cards are responses-free and visibly marked as authored samples",()=>{
 const s=M.demo(T);assert.equal(s.questions.length,2);
 assert.equal(s.events.length,0);assert.ok(s.questions.every(q=>q.seed));
 assert.ok(M.choose(s,profile("source1",["anyone"]),T+1));
});
let pass=0;
for(const [name,fn] of tests){fn();pass++;console.log("PASS "+name);}
console.log("RECIPROCAL-002 PASSED "+pass+" / "+tests.length+" tests");
