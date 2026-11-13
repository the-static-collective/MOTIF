"use strict";
/* METHOD-TOURNAMENT-003: independently authored, synthetic future-report evaluation.
 *
 * Run against ORIGINAL RECIPROCAL-003 in a read-only, no-network container.
 * The candidate module receives calibration events ONLY. It never sees future
 * observations until after methodCandidate has returned frozen predictions.
 * Baselines: global plurality and independently implemented (strong classical)
 * role-conditioned plurality on identical first-two-per-role calibration rows.
 * These are all classical algorithms; no algorithm novelty is inferred.
 */
const fs=require("node:fs");
const assert=require("node:assert/strict");
const crypto=require("node:crypto");
const M=require("../experiments/reciprocal-002/two_doors.js");
const R=require("../experiments/reciprocal-003/reason_loop.js");
const T=1800000000000;
const sourcePath=process.argv[2];
assert(sourcePath && /^evaluation\/[A-Za-z0-9._/-]+\.json$/.test(sourcePath),
  "Only approved read-only fixture path is allowed");
const raw=fs.readFileSync(sourcePath);
assert(raw.length<=65536,"Fixture exceeds bounded evaluation budget");
const pack=JSON.parse(raw.toString("utf8"));
assert.equal(pack.schema,"motif.method-tournament-fixture/v1");
assert.equal(pack.sample_kind,"AUTHORED_SYNTHETIC_NO_HUMANS");
assert.deepEqual(pack.roles,["newcomer","maker"]);
assert.equal(pack.cases.length,6,"All preregistered stress cases required");
const roles=pack.roles;
function plurality(labels) {
  assert(labels.length>0);
  const n=[0,0];
  for(const x of labels){assert(x===0||x===1);n[x]++;}
  return n[0]>=n[1]?0:1;
}
const summarize=values=>values.reduce((s,x)=>s+x,0);
function processCase(fixture,i) {
  assert(/^[a-z][a-z0-9-]{4,64}$/.test(fixture.id));
  for(const role of roles){
    const cal=fixture.calibration[role],future=fixture.future[role];
    assert(Array.isArray(cal)&&cal.length>=2&&cal.length<=5);
    assert(Array.isArray(future)&&future.length>=2&&future.length<=8);
    assert([...cal,...future].every(x=>x===0||x===1));
  }
  const qid="bench_case_"+String(i);
  let state=M.addQuestion(M.empty(),{
    title:"Synthetic report categorization: "+fixture.id,
    why:"Test future generalization and failure under independent scenario shifts.",
    decision:"Should a conditional proposal remain only a held research candidate?",
    options:["choice zero","choice one"],
    roles,priority:3,minRoots:3,maxRoots:20,
    openAt:T,closeAt:T+86400000
  },T,qid);
  let n=0;
  for(const role of roles) {
    fixture.calibration[role].forEach((choice,j)=>{
      n++;
      state=M.event(state,{
        id:"event_"+i+"_"+n,questionId:qid,
        root:"fictional_"+role+"_"+i+"_"+j,
        role,at:T+200+10*j+(role==="maker"?1:0),
        kind:"ANSWER",choice,method:"experience",
        note:"author-designed synthetic calibration, not a human",
      });
    });
  }
  const calibrationEventIds=state.events.map(x=>x.id);
  const candidate=R.methodCandidate(state,qid,T+2000);
  assert(candidate.automatic_admission===false);
  assert(candidate.external_actions===false);
  assert(candidate.evidence_truth==="unverified_claimed_reports");
  assert(candidate.training_event_ids.every(x=>calibrationEventIds.includes(x)));
  assert(candidate.heldout_event_ids.every(x=>calibrationEventIds.includes(x)));
  assert(candidate.training_event_ids.every(x=>!candidate.heldout_event_ids.includes(x)));

  // In a separate independent harness, reconstruct the baseline on the
  // exact two earliest chronological calibration reports for EACH role.
  // No future data are included in this calculation.
  const byRole=Object.fromEntries(roles.map(role=>[
    role,[...state.events].filter(x=>x.role===role)
      .sort((a,b)=>a.at-b.at||a.id.localeCompare(b.id))
  ]));
  const training=roles.flatMap(role=>byRole[role].slice(0,2));
  const baselineOption=plurality(training.map(x=>x.choice));
  const strongMapping=Object.fromEntries(roles.map(role=>[
    role,plurality(byRole[role].slice(0,2).map(x=>x.choice))
  ]));
  if(candidate.global_policy)assert.equal(candidate.global_policy.option,baselineOption);
  if(candidate.role_policy)assert.deepEqual(candidate.role_policy.mapping,strongMapping);

  // Only now consume the separate future-report labels. They were not part
  // of MOTIF's original event stream, internal validation, or training.
  const future=roles.flatMap(role=>fixture.future[role].map(choice=>({role,choice})));
  const globalCorrect=future.filter(x=>x.choice===baselineOption).length;
  const strongCorrect=future.filter(x=>x.choice===strongMapping[x.role]).length;
  const proposed=candidate.status==="PROPOSED_FOR_HUMAN_REVIEW";
  if(proposed)assert(candidate.role_policy);
  const candidateCorrect=proposed?future.filter(x=>
    x.choice===candidate.role_policy.mapping[x.role]).length:null;
  if(proposed)assert.equal(candidateCorrect,strongCorrect,
    "Role-conditioned method must tie its independently implemented strong classical comparator");

  return {
    case_id:fixture.id,
    regime:fixture.why,
    calibration_n:state.events.length,
    future_n:future.length,
    training_event_ids:candidate.training_event_ids,
    calibration_validation_event_ids:candidate.heldout_event_ids,
    source_scoped_original_candidate_status:candidate.status,
    original_candidate_proposed:proposed,
    global_classical_correct:globalCorrect,
    independent_strong_classical_correct:strongCorrect,
    original_branch_candidate_correct:candidateCorrect,
    delta_candidate_vs_global:proposed?candidateCorrect-globalCorrect:null,
    delta_candidate_vs_strong:proposed?candidateCorrect-strongCorrect:null,
    original_claimed_source_roots_only:true,
    future_labels_not_passed_to_original_method:true,
    fact_verified:false,
    automatic_admission:false
  };
}
const results=pack.cases.map(processCase);
const eligible=results.filter(x=>x.original_candidate_proposed);
const futureN=summarize(eligible.map(x=>x.future_n));
const candidateCorrect=summarize(eligible.map(x=>x.original_branch_candidate_correct));
const globalCorrect=summarize(eligible.map(x=>x.global_classical_correct));
const strongCorrect=summarize(eligible.map(x=>x.independent_strong_classical_correct));
assert(eligible.length>=3,"Insufficient active transfer cases");
assert(results.some(x=>x.delta_candidate_vs_global>0),"Positive control not exercised");
assert(results.some(x=>x.delta_candidate_vs_global<0),"Negative transfer control not exercised");
assert(results.some(x=>x.source_scoped_original_candidate_status==="HOLD"),
  "Original algorithm's HOLD boundary not exercised");
const report={
  schema:"motif.method-tournament-scorecard/v1",
  sample_kind:pack.sample_kind,
  fixture_sha256:crypto.createHash("sha256").update(raw).digest("hex"),
  actual_original_source_module:"experiments/reciprocal-003/reason_loop.js",
  actual_original_dependency:"experiments/reciprocal-002/two_doors.js",
  original_native_algorithm_executed:true,
  independent_future_separate_from_candidate_input:true,
  independent_strong_baseline_implemented:true,
  cases:results,
  aggregate_on_proposed_only:{
    case_count:eligible.length,future_n:futureN,
    original_branch_candidate_correct:candidateCorrect,
    global_classical_correct:globalCorrect,
    independent_strong_classical_correct:strongCorrect,
    candidate_minus_global_correct:candidateCorrect-globalCorrect,
    candidate_minus_strong_correct:candidateCorrect-strongCorrect,
    cases_regressing_vs_global:eligible.filter(x=>x.delta_candidate_vs_global<0).map(x=>x.case_id),
  },
  reliable_improvement_over_strong_classical:false,
  winner:"NO_VERIFIED_GENERAL_SUPERIORITY",
  disposition:"RETAIN_SOURCE_POINTER_HELD_NOT_INSTALL",
  learned_weight_updates:false,
  external_action:false,
  automatic_merge:false,
  real_human_reports:false,
  historical_claim:"Classical role-conditioned plurality exactly ties the donor on each proposed case.",
  limitation:"Authored synthetic future labels and authored classical methods, not field outcomes, learned adaptation, or independent proof of a general reasoning advantage."
};
console.log("MOTIF_TOURNAMENT_RESULT "+JSON.stringify(report));
