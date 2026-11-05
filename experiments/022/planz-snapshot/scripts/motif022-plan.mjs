// planZ MOTIF-022: classical dynamic question-to-review-plan compiler.
// Same source-owned finite STRIPS/Dijkstra solver as MOTIF-021.
import {createHash} from 'node:crypto';
import {solve} from './motif-classical.mjs';
const sha=x=>createHash('sha256').update(x).digest('hex');
export function classifyQuestion(question){
 if(typeof question!=='string'||question.length<16||question.length>300)
  throw Error('HOLD_INVALID_QUESTION');
 if(/\b(carrier|ancestor|ancestry|origin|lineage|copy|custody)\b/i.test(question))
  return 'LINEAGE';
 if(/\b(plan|capabilit|graft|compile|execute|recipe)\w*/i.test(question))
  return 'COMPOSITION';
 return 'RELIABILITY';
}
function validateAlex(p){
 if(!p||p.schema!=='alex.motif022.question-packet/v0'||
  !['RESEARCH_PACKET_HELD','HOLD_NO_MATCHES'].includes(p.status)||
  p.authority!=='none'||p.external_actions!==0||
  p.partial_coverage!==true||p.real_independence_proved!==false||
  !Array.isArray(p.hits)||p.hits.length>18||
  p.source_count!==5||!Array.isArray(p.coverage)||p.coverage.length!==5||
  !p.hits.every(h=>h.source_blob?.length===40&&h.source_commit?.length===40&&h.line>0))
  throw Error('HOLD_UNTRUSTED_ALEX_HANDOFF');
 const {checksum,...body}=p;
 if(checksum!==sha(JSON.stringify(body)))throw Error('HOLD_CHANGED_ALEX_HANDOFF');
}
export function planQuestion(packet){
 validateAlex(packet);
 const intent=classifyQuestion(packet.question);
 const basis={alex_checksum:packet.checksum,intent};
 if(packet.status==='HOLD_NO_MATCHES'||!packet.hits.length)
  return {schema:'planz.motif022.question-plan/v0',status:'HOLD_NO_SOURCED_LEADS',
   ...basis,actions:[],cost:null,authority:'none',external_actions:0};
 const make=(name,cost,pre,add)=>({name,pre,add,del:[],cost});
 const common=[
  make('VERIFY_SEARCH_RECEIPT',1,['QUESTION_RECEIVED'],['ALEX_RECEIPT_CHECKED']),
  make('RECORD_SCOPE_LIMITS',1,['ALEX_RECEIPT_CHECKED'],['COVERAGE_DECLARED'])
 ];
 const route=intent==='LINEAGE'?[
   make('TRACE_ORIGINAL_PROVENANCE',2,['COVERAGE_DECLARED'],['CAPABILITY_DEFINED']),
   make('COMPARE_SUSPECTED_FAMILIES',4,['COVERAGE_DECLARED'],['CAPABILITY_DEFINED'])
 ]:intent==='COMPOSITION'?[
   make('COMPOSE_ALLOWED_RECIPE',1,['COVERAGE_DECLARED'],['CAPABILITY_DEFINED']),
   make('RECONSTRUCT_ENTIRE_STACK',6,['COVERAGE_DECLARED'],['CAPABILITY_DEFINED'])
 ]:[
   make('TEST_INDEPENDENT_REPORTS',2,['COVERAGE_DECLARED'],['CAPABILITY_DEFINED']),
   make('EXHAUST_ALL_REFERENCES',5,['COVERAGE_DECLARED'],['CAPABILITY_DEFINED'])
 ];
 const finish=[
  make('PREPARE_DISCRIMINATOR',1,['CAPABILITY_DEFINED'],['QUESTION_READY']),
  make('EMIT_HELD_CANDIDATE',1,['QUESTION_READY'],['CAPABILITY_READY']),
  make('RECORD_REVIEW_RECEIPT',1,['CAPABILITY_READY'],['REVIEW_READY'])
 ];
 const actions=[...common,...route,...finish];
 const optimum=solve(actions,['QUESTION_RECEIVED'],['REVIEW_READY']);
 if(optimum.status!=='PLAN_FOUND')throw Error('HOLD_PLAN_SEARCH_FAILED');
 const expected={schema:'planz.motif022.question-plan/v0',status:'PLAN_HELD_FOR_OWNER',
  ...basis,actions:optimum.steps,cost:optimum.cost,
  search_expansions:optimum.expanded,goal:'REVIEW_READY',
  source_hits:packet.hits.length,
  no_claim_of_external_execution:true,
  no_owner_approval:true,
  no_independence_certification:true,
  authority:'none',external_actions:0};
 return {...expected,checksum:sha(JSON.stringify(expected))};
}
export function validatePlan(plan,packet){
 const expected=planQuestion(packet);
 if(JSON.stringify(plan)!==JSON.stringify(expected))
  throw Error('HOLD_PLAN_NOT_REPLAYABLE_FOR_QUESTION');
 return true;
}
