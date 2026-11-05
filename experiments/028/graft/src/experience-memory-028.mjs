// GRAFT-028 — source-owned structural memory of experiments.
// Every record is a content-addressed, explicitly captured synthetic fixture
// with an independently replayable GRAFT-027 evaluation. No network or install.
import {createHash} from 'node:crypto';
import {cultivate} from './capability-gardener-027.mjs';
import {verifyDiscovery} from '../vendor/alex/api-discovery-026.mjs';

const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const MAX={records:128,recordBytes:190000,fixtures:36,featurePaths:72,matchResults:5};
const BAD=new Set(['__proto__','constructor','prototype']);
const privatePattern=/(?:[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|-----BEGIN.{0,32}PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9_-]{20,}|"(?:(?:api_)?token|password|secret|authorization)"\s*:)/i;
function requireSynthetic(cases){
 if(!cases||typeof cases!=='object'||Array.isArray(cases)||
  !['train','holdout','negative'].every(k=>Array.isArray(cases[k])&&cases[k].length>0&&cases[k].length<=12)||
  typeof cases.hint!=='string'||cases.hint.length<3||cases.hint.length>60)
  throw Error('HOLD_028_ONLY_BOUNDED_LABELED_FIXTURES');
 const serialized=JSON.stringify(cases);
 if(serialized===undefined||serialized.length>MAX.recordBytes||privatePattern.test(serialized))
  throw Error('HOLD_028_PRIVATE_OR_OVERSIZED_EXPERIMENT');
 return serialized;
}
function walkFields(obj,prefix=[],acc=[]){
 if(acc.length>=MAX.featurePaths||prefix.length>=4||
    !obj||typeof obj!=='object'||Array.isArray(obj))return acc;
 for(const key of Object.keys(obj).slice(0,32)){
  if(!/^[A-Za-z][A-Za-z0-9_]{0,40}$/.test(key)||BAD.has(key))continue;
  const child=obj[key],p=[...prefix,key];
  if(child&&typeof child==='object'&&!Array.isArray(child))walkFields(child,p,acc);
  else if(acc.length<MAX.featurePaths)acc.push(p.join('.')+':'+
   (typeof child==='number'?'number':Array.isArray(child)?'array':typeof child));
 }
 return acc;
}
export function fingerprint(cases){
 requireSynthetic(cases);
 const paths=new Set();
 for(const f of [...cases.train,...cases.holdout,...cases.negative]){
  for(const p of walkFields(f.response?.body))paths.add(p);
 }
 return {
  schema:'graft028.fixture-structure/v0',
  paths:[...paths].sort().slice(0,MAX.featurePaths),
  target_words:[...new Set(cases.hint.toLowerCase().split(/[^a-z0-9]+/).filter(x=>x.length>2))].sort().slice(0,8),
  negative_http:cases.negative.some(f=>f.response?.status!==200),
  negative_missing:cases.negative.some(f=>Object.keys(f.response?.body||{}).length===0),
  training_cases:cases.train.length,
  holdout_cases:cases.holdout.length,
  negative_cases:cases.negative.length
 };
}
export function verifyExperience(record){
 if(!record||record.schema!=='graft028.experience/v0'||record.provenance!=='SYNTHETIC_LABELED_FIXTURES_ONLY'||
    record.authorization!=='NONE'||record.production_install!==false||
    record.network_requests!==0||record.source_owner_approval!==false||
    !record.cases||!record.source_packet||!record.evaluation||
    typeof record.receipt_sha256!=='string'||record.receipt_sha256.length!==64)
  throw Error('HOLD_028_INVALID_MEMORY_RECORD');
 const {receipt_sha256,...body}=record;
 if(digest(body)!==receipt_sha256)throw Error('HOLD_028_RECORD_CHANGED');
 if(JSON.stringify(record).length>MAX.recordBytes)throw Error('HOLD_028_RECORD_EXCEEDS_BUDGET');
 requireSynthetic(record.cases);
 verifyDiscovery(record.source_packet);
 if(record.structure.schema!=='graft028.fixture-structure/v0'||
    JSON.stringify(record.structure)!==JSON.stringify(fingerprint(record.cases))||
    record.source_spec_blob!==record.source_packet.public_provider_proposals[0]?.git_blob||
    digest(record.evaluation)!==record.evaluation_sha256||
    record.evaluation.authority!=='none'||record.evaluation.production_install!==false||
    record.outcome!==record.evaluation.status||
    !['HELD_BEST_FIXTURE_CANDIDATE','HOLD_ALL_VARIANTS_FAIL'].includes(record.evaluation.status))
  throw Error('HOLD_028_UNSUPPORTED_EVALUATION');
 return true;
}
export async function captureExperience({source_packet,cases,approvedSyntheticCapture=false}={}){
 if(approvedSyntheticCapture!==true)throw Error('HOLD_028_EXPLICIT_CAPTURE_APPROVAL_REQUIRED');
 requireSynthetic(cases);
 verifyDiscovery(source_packet);
 if(source_packet.status!=='PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER')
  throw Error('HOLD_028_UNSUPPORTED_SOURCE_PACKET');
 const evaluation=await cultivate(source_packet,cases);
 const body={
  schema:'graft028.experience/v0',
  provenance:'SYNTHETIC_LABELED_FIXTURES_ONLY',
  source_spec_blob:source_packet.public_provider_proposals[0].git_blob,
  source_packet,structure:fingerprint(cases),cases,
  evaluation,evaluation_sha256:digest(evaluation),
  outcome:evaluation.status,
  learned_boundary:evaluation.winner?
    'Fixture result survived recorded holdout tests; real-world validity remains unproved.':
    'All candidate paths failed at least one recorded test; request new labeled evidence.',
  replay_engine:'ORIGINAL_GRAFT_027_CULTIVATE',
  source_owner_approval:false,authorization:'NONE',
  production_install:false,network_requests:0
 };
 const result={...body,receipt_sha256:digest(body)};
 verifyExperience(result);
 return result;
}
export async function replayExperience(record){
 verifyExperience(record);
 const rerun=await cultivate(record.source_packet,record.cases);
 if(digest(rerun)!==record.evaluation_sha256||
    JSON.stringify(rerun)!==JSON.stringify(record.evaluation))
  throw Error('HOLD_028_REPLAY_DIVERGED');
 return {
  schema:'graft028.replayed-experience/v0',
  status:'EXACT_EXECUTABLE_REPLAY_MATCH',
  record_sha256:record.receipt_sha256,
  evaluation_sha256:record.evaluation_sha256,
  winner:rerun.winner,
  failed_candidates:rerun.leaderboard.filter(x=>x.failures.length>0).length,
  original_program_execution_repeated:true,
  source_owner_review_not_inherited:true,
  external_actions:0,authority:'none'
 };
}
function similarity(a,b){
 const x=new Set(a.paths),y=new Set(b.paths);
 const intersection=[...x].filter(v=>y.has(v)).length;
 const union=new Set([...x,...y]).size;
 const j=union?intersection/union:0;
 const aw=new Set(a.target_words),bw=new Set(b.target_words);
 const target=[...aw].some(v=>bw.has(v));
 return {score:Math.round((j*0.8+(target?0.2:0))*1000)/1000,
  shared_paths:intersection,union_paths:union,shared_target:target};
}
export function recallSimilar(records,cases,{limit=MAX.matchResults}={}){
 requireSynthetic(cases);
 if(!Array.isArray(records)||records.length>MAX.records||!Number.isSafeInteger(limit)||
    limit<1||limit>MAX.matchResults)
  throw Error('HOLD_028_MEMORY_QUERY_BUDGET');
 const search=fingerprint(cases);
 const hits=[];
 for(const r of records){
  verifyExperience(r);
  const m=similarity(search,r.structure);
  if(m.shared_paths===0||m.score<0.28)continue;
  const failed=r.evaluation.leaderboard
    .filter(v=>!v.admissible_for_fixture_review).slice(0,5)
    .map(v=>({selector:v.selector,failed_cases:v.failures}));
  hits.push({record_sha256:r.receipt_sha256,score:m.score,
   shared_paths:m.shared_paths,shared_target:m.shared_target,
   prior_outcome:r.outcome,previous_winner:r.evaluation.winner?.selector??null,
   previously_failed:failed,lesson:r.learned_boundary,
   inference:'STRUCTURAL_NEIGHBOR_NOT_CAUSAL_PROOF',
   source_blob:r.source_spec_blob,code_promotion:'NONE'});
 }
 hits.sort((a,b)=>b.score-a.score||b.shared_paths-a.shared_paths||
  a.record_sha256.localeCompare(b.record_sha256));
 return {
  schema:'graft028.memory-recall/v0',
  status:hits.length?'STRUCTURALLY_SIMILAR_PRIOR_EXPERIMENTS':'NO_CLOSE_STRUCTURAL_PRECEDENT',
  query_structure:search,examined_records:records.length,
  matches:hits.slice(0,limit),
  next_question:hits.length?
   'Which new withheld fixture distinguishes this case from the closest remembered failure?':
   'Which initial controlled experiment would establish a reproducible precedent?',
  no_automatic_candidate_selection:true,
  past_failures_not_equivalent_to_new_failures:true,
  external_actions:0,authority:'none'
 };
}
