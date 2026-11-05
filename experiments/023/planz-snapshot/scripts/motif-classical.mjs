// planZ MOTIF-021 — genuine finite deterministic STRIPS/classical planner.
// Plan search is executable, but stages remain UNSENT human-review proposals.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

export const ALEX_PACKET_BLOB='71485bd8327bb1bf320d00e0e6e1cee3449365b6';
export const ALLOWED_REPOS=Object.freeze([
 'the-static-collective/MOTIF','the-static-collective/ALEX.2',
 'the-static-collective/planZ','the-static-collective/GRAFT'
]);
export const ACTIONS=Object.freeze([
 {name:'PIN_SOURCE_OBSERVATIONS',
   pre:['ALEX_PUBLIC_PACKET_PRESENT'],add:['SOURCE_PINS_REVIEWED'],del:[],cost:1},
 {name:'CLASSIFY_SEARCH_LIMITS',
   pre:['SOURCE_PINS_REVIEWED'],add:['COVERAGE_BOUND_DECLARED'],del:[],cost:1},
 {name:'PREPARE_INDEPENDENT_PROBES',
   pre:['COVERAGE_BOUND_DECLARED'],add:['QUESTIONS_PROPOSED'],del:[],cost:2},
 {name:'RECONSIDER_ANCESTRY_ALTERNATIVES',
   pre:['COVERAGE_BOUND_DECLARED'],add:['QUESTIONS_PROPOSED'],del:[],cost:3},
 {name:'RESTRICT_PUBLIC_HANDOFF',
   pre:['COVERAGE_BOUND_DECLARED'],add:['PUBLIC_HANDOFF_HELD'],del:[],cost:1},
 {name:'DESIGN_GRAFT_COMPOSITION',
   pre:['QUESTIONS_PROPOSED','PUBLIC_HANDOFF_HELD'],
   add:['RECIPE_PROPOSED'],del:[],cost:2},
 {name:'TEST_CAPABILITY_SANDBOX',
   pre:['RECIPE_PROPOSED'],add:['CANDIDATE_TESTABLE'],del:[],cost:1},
 {name:'ARCHIVE_REVIEW_RECEIPT',
   pre:['CANDIDATE_TESTABLE'],add:['RECEIPT_READY'],del:[],cost:1}
]);
const INITIAL=['ALEX_PUBLIC_PACKET_PRESENT'];
const GOAL=['CANDIDATE_TESTABLE','RECEIPT_READY'];
const FORBIDDEN=new Set([
 'PRIVATE_CONTENT_PUBLISHED','REAL_SOURCE_INDEPENDENCE_ESTABLISHED',
 'AUTHORITY_GRANTED','DEPLOYED_PRODUCTION','AUTOMATED_EXTERNAL_CONTACT',
 'EVIDENCE_ADMITTED','REAL_HUMAN_CONSENT']);
const gitBlob=bytes=>createHash('sha1').update(
 Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const sorted=s=>[...s].sort();
const key=s=>sorted(s).join('|');
export function validatePacket(packet,rawBytes){
 if(!Buffer.isBuffer(rawBytes))throw Error('HOLD_UNPINNED_ALEX_BYTES');
 if(gitBlob(rawBytes)!==ALEX_PACKET_BLOB)
  throw Error('HOLD_ALEX_PACKET_CHANGED');
 if(!packet||packet.schema!=='alex.motif-source-research-packet/v1' ||
    packet.packet_id!=='ALEX-MOTIF-021' ||
    packet.claim_status!=='SOURCE_DISCOVERY_ONLY_NO_REAL_CUSTODY_AUTHENTICATED'||
    packet.source_inventory?.length!==5||
    !Array.isArray(packet.hits) ||
    packet.search_observation?.coverage_status!=='PARTIAL'||
    packet.search_observation?.result_count!==packet.hits.length ||
    packet.restrictions?.only_public_document_snapshots!==true||
    packet.restrictions?.evidence_admission!=='NONE'||
    packet.restrictions?.automatic_execution_authority!=='NONE'||
    packet.restrictions?.permission_to_publish_private_data!==false||
    packet.restrictions?.human_or_private_evidence_collected!==false||
    packet.restrictions?.independently_authenticated_custody!==false)
  throw Error('HOLD_ALEX_INTAKE_CONTRACT');
 const src=new Map();
 for(const s of packet.source_inventory){
  if(!ALLOWED_REPOS.includes(s.repository) ||
     !/^[0-9a-f]{40}$/.test(s.git_blob)||
     !/^[0-9a-f]{40}$/.test(s.source_commit) ||
     src.has(s.id))throw Error('HOLD_INVALID_ALEX_SOURCE');
  src.set(s.id,s);
 }
 for(const h of packet.hits){
  const s=src.get(h.source_id);
  if(!s||h.repository!==s.repository||
     h.source_commit!==s.source_commit||h.git_blob!==s.git_blob||
     h.source_path!==s.source_path||
     !Number.isSafeInteger(h.line_start)||h.line_start<=0||
     h.line_start!==h.line_end||
     h.classification!=='DISCOVERY_NOT_ADMITTED_EVIDENCE')
   throw Error('HOLD_UNGROUNDED_SEARCH_HIT');
 }
 return {packet_id:packet.packet_id,git_blob:ALEX_PACKET_BLOB,
   source_count:src.size,hit_count:packet.hits.length};
}
function checkDomain(actions,initial,goal){
 if(!Array.isArray(actions)||!actions.length||actions.length>20||
    !Array.isArray(initial)||!Array.isArray(goal)||
    initial.length>20||goal.length>20)throw Error('HOLD_BOUNDED_DOMAIN');
 const names=new Set();
 for(const a of actions){
  if(!a||!/^([A-Z]+_?)+$/.test(a.name)||names.has(a.name)||
     !Number.isSafeInteger(a.cost)||a.cost<=0||a.cost>20||
     !['pre','add','del'].every(k=>Array.isArray(a[k])&&
       a[k].every(x=>typeof x==='string'&&/^[A-Z_]+$/.test(x) &&
          !FORBIDDEN.has(x))))
   throw Error('HOLD_UNSAFE_OR_INVALID_ACTION');
  names.add(a.name);
 }
 if([...initial,...goal].some(x=>FORBIDDEN.has(x)||
   !/^[A-Z_]+$/.test(x)))throw Error('HOLD_FORBIDDEN_STATE_OR_GOAL');
}
export function replaySteps(actions,steps,initial=INITIAL){
 checkDomain(actions,initial,GOAL);
 if(!Array.isArray(steps)||steps.length>50)
  throw Error('HOLD_TOO_MANY_STEPS');
 let state=new Set(initial),cost=0,trace=[];
 const allowed=new Map(actions.map(a=>[a.name,a]));
 for(const name of steps){
  const a=allowed.get(name);
  if(!a)throw Error('HOLD_UNKNOWN_CLASSICAL_ACTION');
  if(!a.pre.every(p=>state.has(p)))throw Error('HOLD_FAILED_PRECONDITION');
  for(const p of a.del)state.delete(p);
  for(const p of a.add)state.add(p);
  cost+=a.cost;
  trace.push({action:name,requires:a.pre,
   effects:a.add,after:sorted(state),cumulative_cost:cost,
   executed_external_action:false});
 }
 return {cost,final_facts:sorted(state),trace,
   reached_goal:GOAL.every(g=>state.has(g))};
}
export function solve(actions=ACTIONS,initial=INITIAL,goal=GOAL){
 checkDomain(actions,initial,goal);
 // Uniform-cost graph search (Dijkstra) over finite STRIPS fact sets.
 const queue=[{state:new Set(initial),cost:0,steps:[]}],best=new Map();
 best.set(key(new Set(initial)),0);
 let expanded=0;
 while(queue.length){
  queue.sort((a,b)=>a.cost-b.cost||
    a.steps.join('|').localeCompare(b.steps.join('|')));
  const current=queue.shift();
  const stateKey=key(current.state);
  if(current.cost>best.get(stateKey))continue;
  if(goal.every(x=>current.state.has(x)))
   return {status:'PLAN_FOUND',steps:current.steps,
    cost:current.cost,expanded};
  if(++expanded>4096)throw Error('HOLD_CLASSICAL_SEARCH_BUDGET');
  for(const a of actions){
   if(!a.pre.every(x=>current.state.has(x)))continue;
   const next=new Set(current.state);
   for(const x of a.del)next.delete(x);
   for(const x of a.add)next.add(x);
   const cost=current.cost+a.cost,k=key(next);
   if(!best.has(k)||cost<best.get(k)){
    best.set(k,cost);
    queue.push({state:next,cost,steps:[...current.steps,a.name]});
   }
  }
 }
 return {status:'HOLD_UNREACHABLE_GOAL',steps:[],cost:null,expanded};
}
export function makePlan(packet,rawBytes){
 const ref=validatePacket(packet,rawBytes);
 const shortest=solve();
 if(shortest.status!=='PLAN_FOUND')throw Error('HOLD_NO_CLASSICAL_PLAN');
 const simulation=replaySteps(ACTIONS,shortest.steps);
 if(!simulation.reached_goal||simulation.cost!==shortest.cost)
  throw Error('HOLD_DIVERGENT_PLANNER_REPLAY');
 return {
  schema:'planz.motif-classical-plan/v1',
  plan_id:'PLANZ-MOTIF-021',
  input_packet:ref,alex_source_commit:'c697ce69258cf894be8e7323bd64c81093bd199c',
  domain:'FINITE_PUBLIC_SOURCE_CUSTODY_REVIEW',
  initial_facts:[...INITIAL],goals:[...GOAL],
  actions:shortest.steps,total_declared_cost:shortest.cost,
  search_expanded_states:shortest.expanded,
  verified_simulated_trace:simulation.trace,
  candidate_capability:{
   id:'GRAFT-MOTIF-SOURCE-REVIEW-021',
   recipe:['VERIFY_PINNED_SOURCE_PACKET','BUILD_CITED_CANDIDATE_GRAPH',
     'RETURN_HUMAN_REVIEW_QUESTIONS'],
   scope:'PUBLIC_PINNED_SOURCE_RESEARCH_ONLY',
   implementation_needed:true,
   permissions:'NONE'
  },
  status:'HELD_PLAN_NOT_EXECUTED',
  externally_executed_steps:0,
  source_owner_approval:false,
  future_permission:'REQUIRES_SEPARATE_OWNER_DECISION',
  evidence_admission:'NONE',
  no_real_custody_proved:true,
  cost_of_not_acting:'UNQUANTIFIED_NOT_TREATED_AS_ZERO'
 };
}
export function validateSavedPlan(saved,packet,rawBytes){
 const expected=makePlan(packet,rawBytes);
 if(!saved || saved.schema!==expected.schema ||
   saved.input_packet?.git_blob!==expected.input_packet.git_blob ||
   saved.alex_source_commit!==expected.alex_source_commit ||
   saved.total_declared_cost!==expected.total_declared_cost ||
   saved.actions.join('|')!==expected.actions.join('|')||
   saved.status!=='HELD_PLAN_NOT_EXECUTED'||
   saved.externally_executed_steps!==0 ||
   saved.source_owner_approval!==false||
   saved.evidence_admission!=='NONE'||
   saved.candidate_capability?.permissions!=='NONE')
  throw Error('HOLD_CHANGED_OR_AUTHORITY_CLAIMING_PLAN');
 if(JSON.stringify(saved)!==JSON.stringify(expected))
  throw Error('HOLD_PLAN_RECEIPT_DIFFERS_FROM_EXACT_REPLAY');
 return true;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const raw=readFileSync(new URL('../intake/MOTIF-021/alex-research-packet.json',import.meta.url));
 const packet=JSON.parse(raw);
 process.stdout.write(JSON.stringify(makePlan(packet,raw),null,2)+'\n');
}
