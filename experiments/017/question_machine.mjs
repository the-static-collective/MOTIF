// MOTIF-017 — The Question Before the Question.
// Synthetic active inquiry only. Exact source-pinned organs inherited from 014.
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {makeCase,runCase,verifyDonors} from '../014/organ_garden.mjs';
import {prepareMethodCartridges} from '../016/meta_gardener.mjs';
const SELF=fileURLToPath(import.meta.url);
const SCHEMA='motif017.question-cartridge/v0';
const EPS=1e-10;
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const finite=x=>typeof x==='number'&&Number.isFinite(x);

export function exampleWorld(kind='pair'){
 const source=(id,origin,cost,correct,total=48)=>({
   id,origin,cost,calibration:{schema:'motif017.synthetic-audit/v0',
     origin,correct,total,independently_adjudicated:true}});
 const base={scope:'SYNTHETIC_ONLY',prior:0.5,
   wrong_method_cost:8,hold_cost:1.5,budget:1,
   sources:[source('a','family_a',0.08,36),source('b','family_b',0.08,36)]};
 if(kind==='pair')return base;
 if(kind==='solo')return {...base,sources:[
   source('accurate','family_a',0.26,94,100),
   source('weak','family_b',0.8,26)]};
 if(kind==='expensive')return {...base,sources:[
   source('a','family_a',2,36),source('b','family_b',2,36)]};
 if(kind==='copies')return {...base,sources:[
   source('a','shared',0.08,36),source('forwarded','shared',0.08,36)]};
 if(kind==='anti')return {...base,sources:[
   source('contrarian','family_c',0.05,5),
   source('weak','family_b',1,24)]};
 if(kind==='untrusted'){
   const s=source('a','family_a',0.08,36);
   s.calibration.independently_adjudicated=false;
   return {...base,sources:[s]};
 }
 throw Error('HOLD_UNDECLARED_FIXTURE');
}
function validate(w){
 if(!w || w.scope!=='SYNTHETIC_ONLY' ||
  !finite(w.prior)||w.prior<=0||w.prior>=1 ||
  !finite(w.wrong_method_cost)||w.wrong_method_cost<=0 ||
  !finite(w.hold_cost)||w.hold_cost<=0 ||
  !finite(w.budget)||w.budget<0||w.budget>50 ||
  !Array.isArray(w.sources)||!w.sources.length||w.sources.length>8 ||
  !w.sources.every(s=>s &&
    typeof s.id==='string'&&/^[a-z][a-z0-9_-]{0,40}$/.test(s.id) &&
    typeof s.origin==='string'&&/^[a-z][a-z0-9_-]{0,40}$/.test(s.origin) &&
    finite(s.cost)&&s.cost>0&&s.cost<=50 &&
    s.calibration&&s.calibration.schema==='motif017.synthetic-audit/v0' &&
    s.calibration.origin===s.origin &&
    s.calibration.independently_adjudicated===true &&
    Number.isSafeInteger(s.calibration.total) &&
    Number.isSafeInteger(s.calibration.correct) &&
    s.calibration.total>0&&s.calibration.total<=10000 &&
    s.calibration.correct>=0&&s.calibration.correct<=s.calibration.total) ||
  new Set(w.sources.map(s=>s.id)).size!==w.sources.length)
   throw Error('HOLD_INVALID_OR_UNAUDITED_SOURCE');
}
export function reliability(s){
 const c=s.calibration;
 return (c.correct+2)/(c.total+4); // Beta(2,2), synthetic adjudications.
}
export function posterior(p,r,claim){
 if(!finite(p)||p<=0||p>=1||!finite(r)||r<=0||r>=1||
   !['expected','robust'].includes(claim))throw Error('HOLD_BAD_EVIDENCE');
 const a=claim==='expected'?r:1-r,b=1-a;
 return p*a/(p*a+(1-p)*b);
}
function reportProbability(p,r,claim){
 const a=claim==='expected'?r:1-r;
 return p*a+(1-p)*(1-a);
}
function decision(p,w){
 const options=[
  {choice:'HOLD',risk:w.hold_cost},
  {choice:'PROPOSE_EXPECTED',risk:w.wrong_method_cost*(1-p)},
  {choice:'PROPOSE_ROBUST',risk:w.wrong_method_cost*p}];
 options.sort((a,b)=>a.risk-b.risk ||
   (a.choice==='HOLD'?-1:b.choice==='HOLD'?1:
    a.choice.localeCompare(b.choice)));
 return options[0];
}
export function batchRisk(p,sources,w){
 let outcomes=[{p,mass:1}];
 for(const s of sources){
   const next=[],r=reliability(s);
   for(const o of outcomes){
     for(const claim of ['expected','robust']){
       next.push({p:posterior(o.p,r,claim),
         mass:o.mass*reportProbability(o.p,r,claim)});
     }
   }
   outcomes=next;
 }
 const terminal=outcomes.reduce((n,o)=>n+o.mass*decision(o.p,w).risk,0);
 const cost=sources.reduce((n,s)=>n+s.cost,0);
 return {terminal,cost,total:terminal+cost};
}
function candidates(sources,budget){
 const out=[[]];
 for(let i=0;i<sources.length;i++){
   const a=sources[i];
   if(a.cost<=budget+EPS)out.push([a]);
   for(let j=i+1;j<sources.length;j++){
     const b=sources[j];
     if(a.origin!==b.origin&&a.cost+b.cost<=budget+EPS)out.push([a,b]);
   }
 }
 return out;
}
export function batchOptimum(w,p=w.prior,sources=w.sources,budget=w.budget){
 validate(w);
 if(!finite(p)||p<=0||p>=1||!finite(budget)||budget<0||budget>50)
   throw Error('HOLD_INVALID_STATE');
 const choices=candidates(sources,budget).map(group=>({
    group,...batchRisk(p,group,w)}));
 choices.sort((a,b)=>a.total-b.total ||
    a.group.length-b.group.length ||
    a.cost-b.cost ||
    a.group.map(s=>s.id).join(',').localeCompare(b.group.map(s=>s.id).join(',')));
 const best=choices[0];
 return {ids:best.group.map(s=>s.id),origins:best.group.map(s=>s.origin),
   predicted_total_risk:best.total,
   risk_if_stop:batchRisk(p,[],w).total,candidate_count:choices.length,
   bundle_cost:best.cost};
}
// Classical optimal sequential two-step Bayesian experiment design.
// A sequential strategy can STOP after its first response. Strong comparator.
export function sequentialOptimum(w,p=w.prior,sources=w.sources,budget=w.budget){
 validate(w);
 if(!finite(p)||p<=0||p>=1||!finite(budget)||budget<0||budget>50)
   throw Error('HOLD_INVALID_DP');
 function solve(prob,available,money,remaining){
   let best=decision(prob,w).risk;
   if(remaining===0)return best;
   for(const s of available){
     if(s.cost>money+EPS)continue;
     const leftover=available.filter(q=>q.origin!==s.origin);
     const r=reliability(s);
     let expected=0;
     for(const claim of ['expected','robust']){
       expected+=reportProbability(prob,r,claim)*
         solve(posterior(prob,r,claim),leftover,money-s.cost,remaining-1);
     }
     best=Math.min(best,s.cost+expected);
   }
   return best;
 }
 return solve(p,sources,budget,2);
}
export function questionDesk(overrides={}){
 verifyDonors();
 const x=runCase(makeCase('motif017-method-witness',['a','d'],
   {coarse:1,vertical:2,diagonal:2,joint:6},{
    clue:'Does evidence warrant revising a reasoning-method selector?',
    claim:'Independent witnesses may distinguish a real method failure from a bad report.',
    provenance_class:'speculation',support_confidence:'unsupported',
    ...overrides
   }),'dogram-cost');
 return {schema:'motif017.question-desk/v0',gate:x.status,
  question_receipt:x.national_treasure_question_receipt,
  dogram_receipt:x.dogram_receipt,source_pins:x.source_pins};
}
function admissibleDesk(d){
 if(!d||d.schema!=='motif017.question-desk/v0')
   throw Error('HOLD_MISSING_QUESTION_DESK');
 if(d.gate!=='PROPOSE_SYNTHETIC_ONLY')return false;
 if(d.question_receipt.aperture.id!=='discriminator'||
    Object.hasOwn(d.question_receipt,'answer')||
    Object.hasOwn(d.question_receipt,'conclusion')||
    d.dogram_receipt.source_blob!==d.source_pins.dogram||
    d.dogram_receipt.authority!=='none')
   throw Error('HOLD_DONOR_AUTHORITY');
 return true;
}
export function propose(w,desk,history=[]){
 validate(w);
 if(!admissibleDesk(desk))
   return {schema:SCHEMA,status:'HOLD_NATIONAL_TREASURE_FRONTIER',
      proposed_questions:[],candidate_method:null,
      pending_question:desk.question_receipt.question,no_external_action:true};
 if(!Array.isArray(history)||history.length>8)throw Error('HOLD_BAD_REPORT_HISTORY');
 const seen=new Map();
 for(const row of history){
   if(!row||row.schema!=='motif017.synthetic-report/v0'||
     row.synthetic_only!==true||!['expected','robust'].includes(row.claim)||
     !w.sources.some(s=>s.id===row.id&&s.origin===row.origin))
       throw Error('HOLD_UNKNOWN_REPORT_PROVENANCE');
   const previous=seen.get(row.origin);
   if(previous && previous.claim!==row.claim)return {
      schema:SCHEMA,status:'HOLD_CONFLICTING_COPIES',
      proposed_questions:[],candidate_method:null,
      no_external_action:true};
   if(!previous)seen.set(row.origin,row);
 }
 let p=w.prior,spent=0;
 for(const h of seen.values()){
   const s=w.sources.find(s=>s.id===h.id);
   p=posterior(p,reliability(s),h.claim);
   spent+=s.cost;
 }
 const available=w.sources.filter(s=>!seen.has(s.origin));
 const remaining=Math.max(0,w.budget-spent);
 const best=batchOptimum(w,p,available,remaining);
 const dp=sequentialOptimum(w,p,available,remaining);
 const decisionNow=decision(p,w);
 const asking=best.ids.length>0;
 const body={
   schema:SCHEMA,
   status:asking?'PROPOSE_SIMULTANEOUS_SYNTHETIC_QUESTIONS':
     decisionNow.choice==='HOLD'?'HOLD_INSUFFICIENT_EVIDENCE':'HOLD_METHOD_REVIEW',
   posterior_expected_method:p,
   accepted_upstream_origins:[...seen.keys()],
   proposed_questions:best.ids.map(id=>{
     const s=w.sources.find(s=>s.id===id);
     return {source_id:id,origin:s.origin,declared_cost:s.cost,
       beta_calibrated_reliability:reliability(s)};
   }),
   candidate_method:asking?null:decisionNow.choice,
   predicted_batch_risk:best.predicted_total_risk,
   stop_now_risk:best.risk_if_stop,
   classical_sequential_risk:dp,
   remaining_budget:remaining,
   pending_question:desk.question_receipt.question,
   original_question_box_aperture:desk.question_receipt.aperture.id,
   original_dogram_source:desk.dogram_receipt.source_blob,
   source_pins:desk.source_pins,
   admission:'HUMAN_REVIEW_REQUIRED',no_external_action:true,
   identity_authenticated:false,automatically_revised:false
 };
 return {...body,checksum_sha256:hash(body)};
}
export function checkCartridge(c){
 if(!c||c.schema!==SCHEMA||typeof c.checksum_sha256!=='string'||
    c.no_external_action!==true||c.automatically_revised!==false||
    c.admission!=='HUMAN_REVIEW_REQUIRED')
   throw Error('HOLD_BAD_CARTRIDGE');
 const {checksum_sha256,...body}=c;
 if(hash(body)!==checksum_sha256)throw Error('HOLD_TAMPERED_CARTRIDGE');
 return true;
}
const seeded=seed=>{
 let state=seed>>>0;
 return ()=>((state=(Math.imul(state,1664525)+1013904223)>>>0)/4294967296);
};
export function syntheticTrial(theta='expected',regime='stable',seed=5){
 if(!['expected','robust'].includes(theta)||
    !['stable','unannounced_inversion'].includes(regime))
    throw Error('HOLD_UNKNOWN_TRIAL');
 return {
   public_descriptor:exampleWorld('pair'),
   evaluator_only:{theta,regime,seed}};
}
export function observe(trial,queries,seed=trial.evaluator_only.seed){
 if(!Array.isArray(queries)||queries.some(id=>
    !trial.public_descriptor.sources.some(s=>s.id===id)))
      throw Error('HOLD_UNKNOWN_SYNTHETIC_QUESTION');
 const rand=seeded(seed);
 return queries.map(id=>{
   const s=trial.public_descriptor.sources.find(s=>s.id===id);
   const r=reliability(s);
   const trueAccuracy=trial.evaluator_only.regime==='stable'?r:1-r;
   const correct=rand()<trueAccuracy;
   const theta=trial.evaluator_only.theta;
   return {schema:'motif017.synthetic-report/v0',id,origin:s.origin,
      claim:correct?theta:(theta==='expected'?'robust':'expected'),
      synthetic_only:true};
 });
}
// Independent post-freeze toy evaluation, not a source-training loop.
// Fixed detector, fixed synthetic calibration and frozen source menu.
// Scores hypothetical recommendations; no method is ever applied.
export function adversarialHoldout(desk,episodes=240){
 if(!Number.isSafeInteger(episodes)||episodes<20||episodes>1000)
  throw Error('HOLD_INVALID_EVALUATION_COUNT');
 const result={};
 for(const regime of ['stable','unannounced_inversion']){
   let losses=[],wrong=0,holds=0,candidate=0;
   for(let i=0;i<episodes;i++){
     const theta=i%2===0?'expected':'robust';
     const trial=syntheticTrial(theta,regime,104729+i*97);
     const w=trial.public_descriptor;
     const q=propose(w,desk);
     const requests=q.proposed_questions.map(x=>x.source_id);
     const reports=observe(trial,requests,104729+i*97);
     const after=propose(w,desk,reports);
     const choice=after.candidate_method;
     const totalCost=requests.reduce((acc,id)=>
       acc+w.sources.find(x=>x.id===id).cost,0);
     const stopped=choice===null||choice==='HOLD';
     const loss=stopped?w.hold_cost:
       (choice===('PROPOSE_'+theta.toUpperCase())?0:w.wrong_method_cost);
     if(stopped)holds++;
     else{
       candidate++;
       if(loss>0)wrong++;
     }
     losses.push(loss+totalCost);
   }
   result[regime]={
     episodes,
     hypothetical_method_candidates:candidate,
     held_for_uncertainty:holds,
     wrong_hypothetical_candidates:wrong,
     mean_realized_loss_including_probe_cost:
       losses.reduce((a,b)=>a+b,0)/episodes,
     always_hold_comparator_loss:exampleWorld().hold_cost,
     true_world_regime_exposed_to_planner:false
   };
 }
 return result;
}

export function demonstration(){
 const desk=questionDesk(),parents=prepareMethodCartridges();
 const scenarios=Object.fromEntries(['pair','solo','expensive','copies','anti'].map(kind=>{
   const w=exampleWorld(kind),c=propose(w,desk);
   return [kind,{status:c.status,
     questions:c.proposed_questions.map(q=>q.source_id),
     batch_cost:c.predicted_batch_risk,
     strong_classical_cost:c.classical_sequential_risk,
     hold_cost:w.hold_cost}];
 }));
 const trial=syntheticTrial('expected','stable',823);
 const initial=propose(trial.public_descriptor,desk);
 const reports=observe(trial,initial.proposed_questions.map(q=>q.source_id));
 const followed=propose(trial.public_descriptor,desk,reports);
 const shifted=syntheticTrial('expected','unannounced_inversion',823);
 const inverted=observe(shifted,initial.proposed_questions.map(q=>q.source_id));
 const adversarial=propose(shifted.public_descriptor,desk,inverted);
 const gap=questionDesk({source_locator:''});
 const held=propose(exampleWorld(),gap);
 return {
  schema:'motif017.question-before-question-study/v0',
  status:'EXECUTED_SYNTHETIC_ONLY',
  parent_method_shas:{
    expected:parents.expected.checksum_sha256,
    robust:parents.robust.checksum_sha256},
  genuine_organs:{question_box:desk.question_receipt.schema,
    dogram:desk.dogram_receipt.schema},
  scenarios,holdout_source_shift:adversarialHoldout(desk),
  first_question:initial,fictional_reports:reports,
  after_reports:followed,
  unannounced_inversion:{reports:inverted,response:adversarial},
  national_treasure_gap:{status:held.status,
    aperture:gap.question_receipt.aperture.id},
  explicit_limitations:[
    'invented source origins, reliabilities, calibration audits, and independent-source assumption',
    'known binary regime, hand-supplied costs, Bayesian model, and wrong-answer loss',
    'unannounced inverted reporting may produce incorrect method changes',
    'classical exact sequential design is a strong comparator; no superiority claim',
    'cryptographic content checks do not authenticate any real source or permission',
    'No questions were sent, no OpenManus or ELF worker ran, no organs were modified'
  ],
  external_effects:0,autonomous_edits:false,real_world_witnesses:0
 };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF)
 process.stdout.write(JSON.stringify(demonstration(),null,2)+'\n');
