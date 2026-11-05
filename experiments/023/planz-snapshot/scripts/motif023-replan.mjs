// planZ-023: source-owning real STRIPS uniform-cost planning over *live* ALEX
// observations, followed by an explicit observation-conditioned REPLAN.
// No planned action is sent to GitHub or executed outside the local sandbox.
import {createHash} from 'node:crypto';
import {solve} from './motif-classical.mjs';

const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const HEX=/^[a-f0-9]{40}$/;
const ENFORCED=['the-static-collective/MOTIF','the-static-collective/ALEX.2',
 'the-static-collective/planZ','the-static-collective/GRAFT',
 'the-static-collective/the-daily-slice'];
export function verifyObservation(packet){
 if(!packet||packet.schema!=='alex.motif023.live-public-evidence/v0'||
   !['HELD_SOURCE_RESEARCH_PACKET','HOLD_NO_MATCHING_VERIFIED_SOURCE'].includes(packet.status)||
   !Array.isArray(packet.sources)||packet.sources.length>2||
   !Array.isArray(packet.hits)||packet.hits.length>20||
   !Array.isArray(packet.errors)||packet.errors.length>2||
   !packet.selection||!Array.isArray(packet.selection.repositories)||
   packet.selection.repositories.some(r=>!ENFORCED.includes(r))||
   packet.authority!=='none'||packet.remote_writes!==0||
   packet.private_material_accessed!==false||
   packet.evidence_admission!=='NONE'||
   packet.source_custody_authenticated!==false||
   typeof packet.question!=='string'||
   packet.question.length>320)
  throw Error('HOLD_INVALID_ALEX_LIVE_PACKET');
 const {receipt_sha256,...body}=packet;
 if(receipt_sha256!==hash(body))
  throw Error('HOLD_CHANGED_ALEX_LIVE_RECEIPT');
 const sourceMap=new Map(packet.sources.map(s=>[s.repository,s]));
 for(const s of packet.sources){
  if(!ENFORCED.includes(s.repository)||!HEX.test(s.source_commit)||
   !HEX.test(s.tree_sha)||s.public_eligibility_verified!==true||
   !Array.isArray(s.selected_documents)||s.selected_documents.length>2)
    throw Error('HOLD_UNVERIFIED_PUBLIC_SOURCE');
 }
 for(const hit of packet.hits){
  const s=sourceMap.get(hit.repository);
  if(!s||hit.source_commit!==s.source_commit||
    !s.selected_documents.some(d=>d.path===hit.path&&d.git_blob===hit.git_blob)||
    !Number.isSafeInteger(hit.line)||hit.line<=0||
    hit.support!=='SEARCH_LEAD_NOT_ADMITTED_SOURCE_EVIDENCE')
   throw Error('HOLD_UNATTRIBUTED_SOURCE_LINE');
 }
 return true;
}
function category(question){
 const q=question.toLowerCase();
 if(/\b(maxhinal|madd|ancestor|copy|lineage|carrier|custody)\b/.test(q))
  return 'LINEAGE';
 if(/\b(graft|capabilit\w*|compos\w*|compil\w*|code)\b/.test(q))
  return 'COMPOSITION';
 return 'REFERENCE';
}
const action=(name,cost,pre,add)=>({name,cost,pre,add,del:[]});
function initialDomain(kind,source_count){
 const checkCost=source_count===2?1:2;
 const initial=[
  action('ACKNOWLEDGE_LIVE_OBSERVATION',1,['QUESTION_GIVEN'],['OBSERVATION_TRACKED']),
  action('MARK_PARTIAL_SEARCH_COVERAGE',1,['OBSERVATION_TRACKED'],['COVERAGE_ACKNOWLEDGED']),
  action('REVIEW_PINNED_ORIGINALS',checkCost,['COVERAGE_ACKNOWLEDGED'],['SOURCE_REVIEWED'])
 ];
 const options=kind==='LINEAGE'?[
  action('PROPOSE_INDEPENDENT_CUSTODY_CHALLENGE',2,['SOURCE_REVIEWED'],['DISCRIMINATOR_PROPOSED']),
  action('RUN_UNBOUNDED_GENEALOGY_SEARCH',8,['SOURCE_REVIEWED'],['DISCRIMINATOR_PROPOSED'])
 ]:kind==='COMPOSITION'?[
  action('PROPOSE_CODE_CONTRACT_REVIEW',1,['SOURCE_REVIEWED'],['DISCRIMINATOR_PROPOSED']),
  action('REWRITE_ALL_ORGANS',10,['SOURCE_REVIEWED'],['DISCRIMINATOR_PROPOSED'])
 ]:[
  action('PROPOSE_REFERENCE_INDEPENDENCE_AUDIT',2,['SOURCE_REVIEWED'],['DISCRIMINATOR_PROPOSED']),
  action('ASSUME_SOURCE_IS_CORRECT',9,['SOURCE_REVIEWED'],['DISCRIMINATOR_PROPOSED'])
 ];
 const finish=[
  action('PREPARE_BOUNDED_COMPILATION',1,['DISCRIMINATOR_PROPOSED'],['CAPABILITY_DESIGNED']),
  action('REHEARSE_LOCAL_EXECUTION',1,['CAPABILITY_DESIGNED'],['SANDBOX_READY']),
  action('REQUIRE_REVIEW_RECEIPT',1,['SANDBOX_READY'],['HELD_PLAN_COMPLETE'])
 ];
 return [...initial,...options,...finish];
}
export function planEvidence(packet){
 verifyObservation(packet);
 if(packet.status!=='HELD_SOURCE_RESEARCH_PACKET'||
   !packet.hits.length||!packet.sources.length)
  return {schema:'planz.motif023.observed-plan/v0',
   status:'HOLD_NO_ADMISSIBLE_SOURCE_LEADS',
   source_receipt_sha256:packet.receipt_sha256,
   question:packet.question,actions:[],cost:null,
   no_remote_execution:true,authority:'none'};
 const kind=category(packet.question),actions=initialDomain(kind,packet.sources.length);
 const optimum=solve(actions,['QUESTION_GIVEN'],['HELD_PLAN_COMPLETE']);
 if(optimum.status!=='PLAN_FOUND')throw Error('HOLD_UNREACHABLE_RESEARCH_PLAN');
 const body={
  schema:'planz.motif023.observed-plan/v0',
  status:'HELD_CLASSICAL_PLAN',
  question:packet.question,mode:kind,
  source_receipt_sha256:packet.receipt_sha256,
  actually_observed_hit_count:packet.hits.length,
  actually_observed_source_count:packet.sources.length,
  source_pin_refs:packet.sources.map(s=>({repository:s.repository,source_commit:s.source_commit})),
  steps:optimum.steps,total_declared_cost:optimum.cost,
  search_expanded_states:optimum.expanded,
  plan_domain:'FINITE_PUBLIC_SOURCE_REVIEW_ONLY',
  preconditions_and_costs_optimized:true,
  evidence_admission:'NONE',no_remote_execution:true,
  field_effects_executed:0,source_owner_approval:false,
  authority:'none'
 };
 return {...body,receipt_sha256:hash(body)};
}
export function verifyPlan(plan,packet){
 if(!plan||plan.schema!=='planz.motif023.observed-plan/v0')
  throw Error('HOLD_UNKNOWN_CLASSICAL_PLAN');
 if(JSON.stringify(plan)!==JSON.stringify(planEvidence(packet)))
  throw Error('HOLD_CHANGED_CLASSICAL_PLAN_OR_SOURCE');
 return true;
}
export function replanAfterObservation(packet,plan,feedback){
 verifyPlan(plan,packet);
 if(plan.status!=='HELD_CLASSICAL_PLAN')throw Error('HOLD_NO_COMPILED_CANDIDATE_TO_REPLAN');
 if(!feedback||feedback.schema!=='graft.motif023.capability-observation/v0'||
  feedback.source_plan_receipt!==plan.receipt_sha256||
  feedback.source_alex_receipt!==packet.receipt_sha256||
  feedback.authority!=='none'||feedback.external_actions!==0||
  feedback.independent_custody_confirmed!==false||
  feedback.source_coverage_complete!==false||
  !Array.isArray(feedback.gaps)||feedback.gaps.length>10)
  throw Error('HOLD_UNVERIFIED_COMPOSED_FEEDBACK');
 const observedGaps=feedback.gaps;
 const nextKind=observedGaps.includes('SOURCE_FETCH_GAPS')||
  observedGaps.includes('SINGLE_REPO_SAMPLE')?
  'EXPAND_BOUNDED_PUBLIC_SOURCE_COVERAGE':
  observedGaps.includes('UNCERTIFIED_SOURCE_FAMILY')?
   'TEST_INDEPENDENT_SOURCE_FAMILY':'REVIEW_INDEPENDENT_REPLICA';
 const actions=[
  action('INSPECT_REPLAYED_CAPABILITY_OUTPUT',1,['FEEDBACK_PRESENT'],['FEEDBACK_READ']),
  action('DOCUMENT_UNRESOLVED_SOURCE_GAPS',1,['FEEDBACK_READ'],['GAPS_NOTED']),
  action('FORM_INDEPENDENCE_QUESTION',2,['GAPS_NOTED'],['NEXT_QUESTION_DESIGNED']),
  action('FORM_UNBOUNDED_QUESTION',9,['GAPS_NOTED'],['NEXT_QUESTION_DESIGNED']),
  action('RECORD_RESEARCH_CONTINUATION',1,['NEXT_QUESTION_DESIGNED'],['CONTINUATION_READY'])
 ];
 const optimum=solve(actions,['FEEDBACK_PRESENT'],['CONTINUATION_READY']);
 if(optimum.status!=='PLAN_FOUND')throw Error('HOLD_REPLAN_UNREACHABLE');
 const nextQuestion=nextKind==='TEST_INDEPENDENT_SOURCE_FAMILY'?
  'Which ALEX and GRAFT source custody records could verify an independent origin?':
  nextKind==='EXPAND_BOUNDED_PUBLIC_SOURCE_COVERAGE'?
   'Which planZ and GRAFT documentation exposes source review boundaries?':
   'Which ALEX research source explains independent witness verification?';
 const present=new Set(packet.selection.repositories);
 const nextCollections=nextKind==='TEST_INDEPENDENT_SOURCE_FAMILY'?
  ['the-static-collective/ALEX.2','the-static-collective/GRAFT']:
  nextKind==='EXPAND_BOUNDED_PUBLIC_SOURCE_COVERAGE'?
   ['the-static-collective/planZ','the-static-collective/GRAFT']:
   ['the-static-collective/ALEX.2','the-static-collective/MOTIF'];
 const body={
  schema:'planz.motif023.observation-replan/v0',
  status:'HELD_PROPOSED_NEXT_RESEARCH',
  previous_alex_receipt:packet.receipt_sha256,
  previous_plan_receipt:plan.receipt_sha256,
  observed_gaps:observedGaps,
  selected_next_discriminator:nextKind,
  next_question:nextQuestion,next_source_collections:nextCollections,
  new_collection_not_in_initial_query:nextCollections.some(r=>!present.has(r)),
  classical_steps:optimum.steps,
  next_plan_cost:optimum.cost,
  source_coverage_not_claimed_complete:true,
  no_automatic_external_contact:true,
  no_claim_of_real_source_independence:true,
  authority:'none',external_actions:0
 };
 return {...body,receipt_sha256:hash(body)};
}
