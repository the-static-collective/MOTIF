// MOTIF-018 — WITNESS OF THE WITNESS
// Independently referenced, source-family-aware synthetic change monitoring.
// All source evidence, audit families, references and classifications are invented.
// This module NEVER edits upstream organs or dispatches an actual audit.
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {questionDesk} from '../017/question_machine.mjs';

const SELF=fileURLToPath(import.meta.url);
const SCHEMA='motif018.witness-of-witness-receipt/v0';
const INPUT='motif018.synthetic-audited-report/v0';
const REFERENCE='motif018.synthetic-reference/v0';
const SOURCES=['north','south'];
const PHASES=['baseline','early','late'];
const MIN_BASELINE=200;
const MIN_CHECKPOINT=60;
const ALPHA=0.05;
const TESTS=8; // predeclared family: 2 sources × 2 looks × 2 audited metrics
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');

function rng(seed){
 let s=seed>>>0;
 return ()=>((s=(Math.imul(s,1664525)+1013904223)>>>0)/4294967296);
}
function invert(s){return s==='yes'?'no':'yes';}
function requireClass(x){
 if(!['yes','no'].includes(x))throw Error('HOLD_UNDECLARED_BINARY_LABEL');
}
function makeReference(family,label){
 return {schema:REFERENCE,origin:family,label,
   evidence_scope:'SYNTHETIC_GENERATED_REFERENCE'};
}
function makeRow(phase,index,origin,reported,referenceA,referenceB,
                 reporter=origin+'_firsthand'){
 return {schema:INPUT,phase,sample_id:phase+'-'+index,origin,reporter,
   reported,references:[
    makeReference('synthetic_reference_alpha',referenceA),
    makeReference('synthetic_reference_beta',referenceB)],
   source_scope:'SYNTHETIC_ONLY'};
}
export function simulate(kind='stable',seed=771) {
 const allowed=['stable','world_shift','witness_flip','both_shift',
   'subtle_shift','reference_conflict','reference_collusion',
   'missing_reference','forwarded'];
 if(!allowed.includes(kind)||!Number.isSafeInteger(seed))
   throw Error('HOLD_UNDECLARED_SYNTHETIC_REGIME');
 const random=rng(seed),rows=[];
 const counts={baseline:480,early:80,late:320};
 for(const phase of PHASES){
  const later=phase!=='baseline';
  for(let i=0;i<counts[phase];i++){
   const prevalence=later&&['world_shift','both_shift'].includes(kind)?0.82:0.18;
   const truth=random()<prevalence?'yes':'no';
   for(const origin of SOURCES){
    const wasReliable=origin==='north'?0.86:0.82;
    const flip=origin==='north'&&later&&
      ['witness_flip','both_shift'].includes(kind);
    const subtle=origin==='north'&&later&&kind==='subtle_shift';
    const accuracy=flip?0.14:subtle?0.75:wasReliable;
    const reported=random()<accuracy?truth:invert(truth);
    const jointReferenceError=later&&kind==='reference_collusion';
    const referenceA=jointReferenceError?invert(truth):truth;
    const referenceB=later&&kind==='reference_conflict'&&i===0
      ?invert(referenceA):referenceA;
    const row=makeRow(phase,i,origin,reported,referenceA,referenceB);
    if(later&&kind==='missing_reference'&&i===0)
      row.references.pop();
    rows.push(row);
    if(kind==='forwarded'&&origin==='north')
      rows.push({...row,reporter:'north_forwarded_copy'});
   }
  }
 }
 return {
  public_records:rows,
  evaluator_only:{
   kind,source_error_model:'SYNTHETIC_SEALED_FROM_MONITOR',
   truth_prevalence_later:['world_shift','both_shift'].includes(kind)?0.82:0.18,
   true_north_accuracy_later:['witness_flip','both_shift'].includes(kind)?
     0.14:kind==='subtle_shift'?0.75:0.86,
   reference_is_colluding:kind==='reference_collusion'
  }
 };
}
function checkRow(r){
 if(!r||r.schema!==INPUT||r.source_scope!=='SYNTHETIC_ONLY'||
  !PHASES.includes(r.phase)||typeof r.sample_id!=='string'||
  !/^(baseline|early|late)-[0-9]+$/.test(r.sample_id)||
  !SOURCES.includes(r.origin)||typeof r.reporter!=='string'||
  !r.reporter.startsWith(r.origin+'_')||
  !['yes','no'].includes(r.reported))
   throw Error('HOLD_INVALID_SYNTHETIC_SOURCE_RECORD');
 if(!Array.isArray(r.references)||r.references.length!==2)
   throw Error('HOLD_INCOMPLETE_INDEPENDENT_REFERENCES');
 const families=new Set();
 for(const ref of r.references){
  if(!ref||ref.schema!==REFERENCE||
    ref.evidence_scope!=='SYNTHETIC_GENERATED_REFERENCE'||
    !['yes','no'].includes(ref.label)||
    typeof ref.origin!=='string'||ref.origin===r.origin||
    families.has(ref.origin)||
    !['synthetic_reference_alpha','synthetic_reference_beta'].includes(ref.origin))
    throw Error('HOLD_UNINDEPENDENT_OR_INVALID_REFERENCE');
  families.add(ref.origin);
 }
 if(r.references[0].label!==r.references[1].label)
   throw Error('HOLD_REFERENCE_DISAGREEMENT');
}
function canonical(rows){
 if(!Array.isArray(rows)||!rows.length||rows.length>6000)
  throw Error('HOLD_INVALID_RECORD_BOOK');
 const seen=new Map(),bySpecimen=new Map(),duplicates=[];
 for(const row of rows){
  checkRow(row);
  const k=row.phase+'|'+row.sample_id+'|'+row.origin;
  const existing=seen.get(k);
  if(existing){
   if(existing.reported!==row.reported||
     JSON.stringify(existing.references)!==JSON.stringify(row.references))
     throw Error('HOLD_CONTRADICTORY_SAME_ORIGIN_COPIES');
   duplicates.push(k);
   continue;
  }
  seen.set(k,row);
  const shared=row.phase+'|'+row.sample_id;
  const prior=bySpecimen.get(shared);
  if(prior && JSON.stringify(prior)!==JSON.stringify(row.references))
   throw Error('HOLD_CONFLICTING_REFERENCE_FOR_SAME_SPECIMEN');
  bySpecimen.set(shared,row.references);
 }
 return {rows:[...seen.values()],duplicates};
}
function stats(rows,origin,phase){
 const values=rows.filter(r=>r.origin===origin&&r.phase===phase);
 const n=values.length;
 return {
  n,
  accuracy:values.filter(r=>r.reported===r.references[0].label).length/n,
  prevalence:values.filter(r=>r.references[0].label==='yes').length/n,
  raw_yes_rate:values.filter(r=>r.reported==='yes').length/n
 };
}
function threshold(n,m,alpha=ALPHA){
 if(!Number.isSafeInteger(n)||!Number.isSafeInteger(m)||n<=0||m<=0||
  typeof alpha!=='number'||alpha<=0||alpha>=1)throw Error('HOLD_BAD_CONFIDENCE');
 // Two-sample bounded Hoeffding with union bound over the full frozen family.
 return Math.sqrt(0.5*(1/n+1/m)*Math.log(2*TESTS/alpha));
}
function contrast(before,after,field){
 const delta=after[field]-before[field];
 const bound=threshold(before.n,after.n);
 return {baseline:before[field],current:after[field],
   difference:delta,abs_difference:Math.abs(delta),
   declared_detection_threshold:bound,
   flagged:Math.abs(delta)>bound};
}
export function evaluateWitnesses(records,checkpoint='late'){
 if(!['early','late'].includes(checkpoint))
  throw Error('HOLD_UNREGISTERED_CHECKPOINT');
 const {rows,duplicates}=canonical(records);
 const analysis={};
 for(const origin of SOURCES){
  const old=stats(rows,origin,'baseline');
  const fresh=stats(rows,origin,checkpoint);
  if(old.n<MIN_BASELINE||fresh.n<MIN_CHECKPOINT)
   return {schema:SCHEMA,status:'HOLD_NOT_ENOUGH_ADJUDICATED_CASES',
    checkpoint,source:origin,required_baseline:MIN_BASELINE,
    required_recent:MIN_CHECKPOINT,
    real_source_authentication:false,automatic_repair:false};
  const accuracy=contrast(old,fresh,'accuracy');
  const prevalence=contrast(old,fresh,'prevalence');
  const raw=contrast(old,fresh,'raw_yes_rate');
  analysis[origin]={
   n_baseline:old.n,n_recent:fresh.n,
   accuracy,adjudicated_truth_prevalence:prevalence,
   unadjudicated_report_prevalence:raw,
   source_change_evidence:accuracy.flagged,
   world_regime_evidence:prevalence.flagged
  };
 }
 const drift=SOURCES.filter(x=>analysis[x].source_change_evidence);
 const world=SOURCES.filter(x=>analysis[x].world_regime_evidence);
 const naive=SOURCES.filter(x=>analysis[x].unadjudicated_report_prevalence.flagged);
 const interpretation=drift.length&&world.length
  ?'BOTH_REPORTER_AND_REFERENCE_DISTRIBUTIONS_CHANGED'
  :drift.length?'REPORTER_ACCURACY_CHANGE_WITNESSED_IN_SYNTHETIC_AUDIT'
  :world.length?'REFERENCE_DISTRIBUTION_CHANGED_WITHOUT_DETECTED_REPORTER_DRIFT'
  :'NO_CHANGE_DETECTED_NOT_PROOF_OF_STABILITY';
 const body={
  schema:SCHEMA,status:'HOLD_FOR_INDEPENDENT_SOURCE_REVIEW',
  checkpoint,interpretation,
  source_change_flags:drift,reference_prevalence_flags:world,
  naive_raw_report_prevalence_flags:naive,
  analysis,
  deduplicated_forwarded_copies:duplicates.length,
  audit_method:{
   name:'TWO_SAMPLE_HOEFFDING_BONFERRONI',
   declared_familywise_alpha:ALPHA,predeclared_tests:TESTS,
   fixed_checkpoints:['early','late'],within_era_iid_assumed:true,
   correction_is_conservative:true,
   reference_family_origins:[
    'synthetic_reference_alpha','synthetic_reference_beta']
  },
  national_treasure_evidence_class:'speculation',
  independently_authenticated_real_sources:false,
  two_reference_agreement_does_not_establish_truth:true,
  admitted_method_change:false,
  auto_source_quarantine:false,
  external_actions:0
 };
 return {...body,checksum_sha256:hash(body)};
}
export function checkReceipt(r){
 if(!r||r.schema!==SCHEMA||
  r.status!=='HOLD_FOR_INDEPENDENT_SOURCE_REVIEW'||
  r.admitted_method_change!==false||
  r.auto_source_quarantine!==false||
  typeof r.checksum_sha256!=='string')throw Error('HOLD_INVALID_RECEIPT');
 const {checksum_sha256,...body}=r;
 if(hash(body)!==checksum_sha256)throw Error('HOLD_RECEIPT_TAMPERED');
 return true;
}
export function questionForWitness(overrides={}){
 const d=questionDesk({
  clue:'An observation says a reasoning-method selector is failing.',
  claim:'Which original source or environmental distribution changed?',
  provenance_class:'speculation',
  support_confidence:'unsupported',
  ...overrides
 });
 return {
  schema:'motif018.question-gate/v0',
  status:d.gate,question_receipt:d.question_receipt,
  native_dogram_receipt:d.dogram_receipt,
  donor_pins:d.source_pins,
  action_permitted:false
 };
}
export function auditPlan(options,budget=1.2,question=questionForWitness()){
 if(!question || question.schema!=='motif018.question-gate/v0')
  throw Error('HOLD_NO_NATIONAL_TREASURE_GATE');
 if(question.status!=='PROPOSE_SYNTHETIC_ONLY')
  return {status:'HOLD_NATIONAL_TREASURE_SOURCE_FRONTIER',
   question:question.question_receipt.question,source_audits:[]};
 if(!Array.isArray(options)||!options.length||options.length>10||
    typeof budget!=='number'||!Number.isFinite(budget)||budget<0||
    options.some(s=>!s || !SOURCES.includes(s.origin)||
      typeof s.auditor_origin!=='string'||
      !s.auditor_origin.startsWith('synthetic_reference_')||
      typeof s.audit_cost!=='number'||s.audit_cost<=0||
      typeof s.impact!=='number'||s.impact<=0||
      !Number.isFinite(s.audit_cost)||!Number.isFinite(s.impact)||
      s.audit_cost>10||s.impact>10))
  throw Error('HOLD_BAD_SOURCE_AUDIT_OFFER');
 const ordered=[...options].sort((a,b)=>
   b.impact/b.audit_cost-a.impact/a.audit_cost||
   a.origin.localeCompare(b.origin));
 const chosen=[],origins=new Set(),auditors=new Set(),spent={value:0};
 for(const item of ordered){
  if(chosen.length>=2)break;
  if(!origins.has(item.origin)&&!auditors.has(item.auditor_origin)&&
     spent.value+item.audit_cost<=budget){
   chosen.push(item);spent.value+=item.audit_cost;
   origins.add(item.origin);
   auditors.add(item.auditor_origin);
  }
 }
 return {
  schema:'motif018.audit-question-portfolio/v0',
  status:chosen.length?'PROPOSE_SYNTHETIC_AUDIT_QUESTIONS':
    'HOLD_BUDGET',
  source_audits:chosen.map(x=>({origin:x.origin,
    reference_origin:x.auditor_origin,declared_cost:x.audit_cost,
    declared_impact:x.impact,
    question:'Can independent adjudicated observations verify whether '+x.origin+
      ' is still reporting reliably?'})),
  spent_budget:spent.value,unspent_budget:budget-spent.value,
  criterion:'DECLARED_IMPACT_PER_COST_HEURISTIC_NOT_OPTIMAL_VOI',
  proposal_only:true,source_verification_performed:false
 };
}
export function study(){
 const gate=questionForWitness(),gap=questionForWitness({source_locator:''});
 const plan=auditPlan([
  {origin:'north',auditor_origin:'synthetic_reference_alpha',impact:4,audit_cost:0.45},
  {origin:'south',auditor_origin:'synthetic_reference_beta',impact:3,audit_cost:0.4}
 ],1.2,gate);
 const regimes=['stable','world_shift','witness_flip','both_shift',
  'subtle_shift','reference_conflict','reference_collusion',
  'missing_reference','forwarded'];
 const table={};
 for(const kind of regimes){
  const fixture=simulate(kind,777);
  try{
   const report=evaluateWitnesses(fixture.public_records);
   table[kind]={
    interpretation:report.interpretation,
    changed_sources:report.source_change_flags,
    world_flags:report.reference_prevalence_flags,
    naive_unverified_flags:report.naive_raw_report_prevalence_flags,
    duplicates:report.deduplicated_forwarded_copies,
    would_misattribute_a_reference_failure:
      kind==='reference_collusion'&&report.source_change_flags.includes('north'),
    status:report.status
   };
  }catch(e){
   if(!String(e.message).startsWith('HOLD_'))throw e;
   table[kind]={status:e.message};
  }
 }
 const aggregates={};
 for(const kind of ['stable','world_shift','witness_flip','reference_collusion']){
  let sourceFlags=0,worldFlags=0,holds=0;
  for(let seed=900;seed<915;seed++){
   const result=evaluateWitnesses(simulate(kind,seed).public_records);
   if(result.source_change_flags.length)sourceFlags++;
   if(result.reference_prevalence_flags.length)worldFlags++;
   if(result.status.startsWith('HOLD'))holds++;
  }
  aggregates[kind]={trials:15,source_change_flags:sourceFlags,
    reference_distribution_flags:worldFlags,
    review_holds:holds};
 }
 return {
  schema:'motif018.witness-of-witness-study/v0',
  status:'SYNTHETIC_WITNESS_HEALTH_RESEARCH',
  question_gate:{
    original_national_treasure_question:gate.question_receipt.question,
    original_national_treasure_aperture:gate.question_receipt.aperture.id,
    original_native_dogram:gate.native_dogram_receipt?.schema,
    source_pins:gate.donor_pins
  },
  missing_original_source:{
    gate:gap.status,aperture:gap.question_receipt.aperture.id,
    math_executed:gap.native_dogram_receipt!==null
  },
  audit_plan:plan,
  fixed_regime_cases:table,
  independent_seed_comparison:aggregates,
  negative_case:{
   kind:'REFERENCE_COLLUSION',
   meaning:'Two purportedly independent adjudicators agreeing on the same false label can fool this detector.',
   independently_verified_real_reference:false,
   cannot_repair_or_prove_source_trust:true
  },
  next_question:{
   question:'What third, genuinely independent measurement could detect shared-reference corruption rather than corroborate it?',
   answer_provided:false
  },
  external_actions:0,real_source_authentication:false,
  autonomous_method_changes:0,openmanus_worker_executed:false
 };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF)
 process.stdout.write(JSON.stringify(study(),null,2)+'\n');
