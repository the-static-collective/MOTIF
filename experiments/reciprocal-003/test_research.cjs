"use strict";
const assert=require("node:assert/strict");
const M=require("../reciprocal-002/two_doors.js");
const R=require("./reason_loop.js");
const T=1800000000000,DAY=86400000;
const standard={title:"What is confusing at the entry?",
 why:"Discover which explanation needs revision before any pilot.",
 decision:"Rewrite the first screen to eliminate confusion.",
 options:["Opening route","Answer handling","No confusion"],
 roles:["newcomer","maker"],priority:4,
 minRoots:3,maxRoots:12,openAt:T,closeAt:T+7*DAY};
function initial(override={}){
 return M.addQuestion(M.empty(),{...standard,...override},T,"q_003");
}
function add(s,{root,role,choice,at,method="experience",kind="ANSWER",revises}){
 return M.event(s,{id:"evt_"+root+"_"+at,questionId:"q_003",
 root,role,at,kind,choice,method,note:"synthetic authored report",revises});
}
function fixtures(newcomers,maker,override={}){
 let s=initial(override);
 newcomers.forEach((choice,i)=>{s=add(s,{root:"newcomer_"+i,role:"newcomer",choice,at:T+100+i*2});});
 maker.forEach((choice,i)=>{s=add(s,{root:"maker_"+i,role:"maker",choice,at:T+101+i*2});});
 return s;
}
const tests=[];
function test(name,fn){tests.push([name,fn]);}
test("adapter consumes real source-owned TwoDoors state and preserves provenance",()=>{
 const s=fixtures([0,0,0,0],[1,1,1,1]);
 const g=R.toGraph(s,"q_003",T+500);
 assert.equal(g.schema,R.SCHEMA);
 assert.equal(g.current_claimed_roots,8);
 assert.equal(g.question_status,"OPEN");
 assert.equal(g.owner_truth,"not_available");
 assert.equal(g.action_authority,"none");
 assert.equal(g.source_provenance.blob,"33e0ed2521f9d1eb4bdaf9208b68e434ce80eda0");
 const edges=g.hyperedges.filter(x=>x.kind==="source_reports");
 assert.equal(edges.length,8);
 assert.ok(edges.every(e=>e.tails.length===2&&e.heads.length===2));
 assert.ok(g.nodes.some(x=>x.kind==="missing_distinction"&&x.status==="proposed"));
 assert.ok(!g.hyperedges.some(x=>x.authority!=="none"||x.no_fact_promotion!==true));
});
test("counterfactuals fork actual TwoDoors inspector and cannot mutate observations",()=>{
 const s=fixtures([0,0],[1]);
 const before=JSON.stringify(s);
 const c=R.previewOneMore(s,"q_003",T+500);
 assert.equal(c.branches.length,3);
 assert.equal(c.status,"PENCIL_ONLY");
 assert.equal(new Set(c.branches.map(x=>x.choice)).size,3);
 for(const f of c.branches){
  assert.equal(f.status,"HYPOTHETICAL_ONLY_NOT_OBSERVED");
  assert.equal(f.counts_if_reported.reduce((a,b)=>a+b,0),4);
  assert.equal(f.after_entropy>=0,true);
 }
 assert.equal(JSON.stringify(s),before);
});
test("method foundry proposes source-conditioned method only after actual heldout gain",()=>{
 const s=fixtures([0,0,0,0],[1,1,1,1]);
 const m=R.methodCandidate(s,"q_003",T+500);
 assert.equal(m.status,"PROPOSED_FOR_HUMAN_REVIEW");
 assert.equal(m.global_policy.correct,2);
 assert.equal(m.role_policy.correct,4);
 assert.equal(m.gain_over_global_on_later_reports,2);
 assert.equal(m.training_event_ids.length,4);
 assert.equal(m.heldout_event_ids.length,4);
 assert.equal(new Set(m.training_event_ids.concat(m.heldout_event_ids)).size,8);
 assert.equal(m.role_policy.mapping.newcomer,0);
 assert.equal(m.role_policy.mapping.maker,1);
 assert.equal(m.automatic_admission,false);
 assert.match(m.matched_strong_classical_control,/exact tie/i);
});
test("uniform response yields no new role-specific algorithm claim",()=>{
 const s=fixtures([0,0,0],[0,0,0]);
 const m=R.methodCandidate(s,"q_003",T+500);
 assert.equal(m.status,"HOLD");
 assert.equal(m.gain_over_global_on_later_reports,0);
 assert.match(m.reason,/no different outcome/i);
});
test("reversed heldout labels falsify method and produce recorded regression",()=>{
 const s=fixtures([0,0,1,1],[1,1,0,0]);
 const m=R.methodCandidate(s,"q_003",T+500);
 assert.equal(m.status,"HOLD");
 assert.equal(m.global_policy.correct,2);
 assert.equal(m.role_policy.correct,0);
 assert.equal(m.gain_over_global_on_later_reports,-2);
 assert.match(m.reason,/regressed/i);
});
test("too few distinct source roots must HOLD without compressing into a cartridge",()=>{
 const s=fixtures([0,0],[1,1]);
 const m=R.methodCandidate(s,"q_003",T+500);
 assert.equal(m.status,"HOLD");
 assert.equal(m.role_policy,null);
 assert.match(m.reason,/three distinct claimed roots/);
});
test("contested duplicate pseudonymous answer prevents candidate method admission",()=>{
 let s=fixtures([0,0,0,0],[1,1,1,1]);
 s=add(s,{root:"maker_0",role:"maker",choice:0,at:T+900});
 assert.equal(M.inspect(s,"q_003",T+1000).status,"HOLD_CONTEST");
 const m=R.methodCandidate(s,"q_003",T+1000);
 const g=R.toGraph(s,"q_003",T+1000);
 assert.equal(m.status,"HOLD");
 assert.equal(g.contested_events,1);
 assert.ok(g.nodes.some(x=>x.status==="contested"));
 assert.equal(R.previewOneMore(s,"q_003",T+1000).branches.length,0);
});
test("role declarations are testimony labels, not causal truth or independent identification",()=>{
 const s=fixtures([0,0,0],[1,1,1]);
 const g=R.toGraph(s,"q_003",T+600);
 assert.equal(g.all_reports_are_claimed_unverified,true);
 assert.ok(g.nodes.filter(x=>x.kind==="claimed_source").every(x=>x.status==="unverified"));
 assert.ok(g.hyperedges.filter(x=>x.kind==="suggests_test").every(x=>x.status==="proposed"));
});
test("revisions remain visible; only current latest event influences learning",()=>{
 let s=fixtures([0,0,0,0],[1,1,1,1]);
 const old=s.events.find(e=>e.root==="maker_3");
 s=M.event(s,{id:"rev_maker_3",questionId:"q_003",root:"maker_3",
   role:"maker",at:T+2000,kind:"REVISE",choice:0,method:"reasoning",
   note:"fictional correction",revises:old.id});
 const m=R.methodCandidate(s,"q_003",T+2001),g=R.toGraph(s,"q_003",T+2001);
 assert.equal(m.status,"HOLD"); // gain falls from 2 to 1
 assert.equal(m.gain_over_global_on_later_reports,1);
 assert.equal(g.hyperedges.filter(x=>x.kind==="revises_record").length,1);
 assert.ok(g.nodes.some(x=>x.id==="event:"+old.id&&x.status==="superseded"));
 assert.ok(g.nodes.some(x=>x.id==="event:rev_maker_3"&&x.status==="reported"));
});
test("expired or completed questions are not subjected to fake future human asking",()=>{
 const s=fixtures([0,0,0,0],[1,1,1,1]);
 const c=R.previewOneMore(s,"q_003",T+8*DAY);
 assert.equal(c.status,"HOLD_NOT_ASKING");
 assert.equal(c.branches.length,0);
 assert.equal(c.before.status,"HOLD_EXPIRED");
});
test("lesson never implies a human has demonstrably learned or models have changed",()=>{
 const s=fixtures([0,0,0,0],[1,1,1,1]);
 const l=R.lesson(s,"q_003",T+900);
 assert.equal(l.not_measured_human_learning,true);
 assert.match(l.transfer_exercise,/Before reading any future answer/);
 assert.match(l.lesson_for_human,/independently owned decision outcome/);
});
test("unrecognized question refuses graph, test or method generation",()=>{
 const s=initial();
 for(const f of [R.toGraph,R.previewOneMore,R.methodCandidate,R.lesson]){
  assert.throws(()=>f(s,"missing",T+1),/UNKNOWN_QUESTION/);
 }
});
test("authored example is explicitly fictional and demonstrates proposed learner without network people",()=>{
 const s=R.authoredDemo(T);
 assert.equal(s.questions.length,1);
 assert.equal(s.questions[0].seed,true);
 assert.equal(s.events.length,8);
 assert.ok(s.events.every(e=>e.root.includes("fictional")));
 assert.equal(R.methodCandidate(s,"fixture_role_divergence",T).status,"PROPOSED_FOR_HUMAN_REVIEW");
 assert.equal(R.previewOneMore(s,"fixture_role_divergence",T).branches.length,3);
});
test("no raw report note is exported as graph label or inferred as verified fact",()=>{
 let s=initial();
 s=add(s,{root:"newcomer_01",role:"newcomer",choice:0,at:T+100});
 // HTML is constructed via textContent, but exporter also avoids prose notes.
 const g=R.toGraph(s,"q_003",T+200);
 assert.ok(!JSON.stringify(g).includes("synthetic authored report"));
 assert.equal(g.action_authority,"none");
});
let pass=0;
for(const [name,fn] of tests){fn();pass++;console.log("PASS",name);}
console.log("RECIPROCAL-003 PASSED "+pass+" / "+tests.length+" tests");
