import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifySourceOwners} from '../026/discovery_machine.mjs';
import {solve,replaySteps} from '../023/planz-snapshot/scripts/motif-classical.mjs';
import {discoverMissingProvider} from '../026/alex/api-discovery-026.mjs';
import {cultivate} from './graft/src/capability-gardener-027.mjs';
import {probePublicExample} from './graft/src/live-pilot-027.mjs';
const sha=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const blob=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const PINS={
 'graft/src/capability-gardener-027.mjs':'a8d74c3b236f1a53018a458b767ed0ac0120d243',
 'graft/src/live-pilot-027.mjs':'841cb9ed72aa070254009975a036b023f917fa80',
 'graft/src/discovered-adapter-026.mjs':'3227361a543fbfaa19cc445edfa64757f2b52c71',
 'graft/vendor/alex/api-discovery-026.mjs':'67b851c9ea58d4aa92ca159000e982c312cd2335',
 'graft/vendor/alex/eagle-eye-providers-025.mjs':'5c095be409d2ace0d39765c4316471702d88acb5'
};
export function verifyGardenOwners(){
 verifySourceOwners();
 for(const [file,expected] of Object.entries(PINS)){
  if(blob(readFileSync(new URL(file,import.meta.url)))!==expected)
   throw Error('HOLD_SOURCE_CODE_DRIFT_'+file);
 }
 return {git_source_blobs:PINS,authenticated_external_service:false};
}
const a=(name,cost,pre,add)=>({name,cost,pre,add,del:[]});
export function nextPlan(evaluation){
 if(!evaluation||evaluation.schema!=='graft027.garden-evaluation/v0'||
  evaluation.authority!=='none'||evaluation.production_install!==false)
  throw Error('HOLD_INVALID_TEST_OBSERVATION');
 const winning=evaluation.status==='HELD_BEST_FIXTURE_CANDIDATE';
 const actions=[
  a('READ_FIXTURE_RECEIPT',1,['OBSERVED'],['READ']),
  a('RECORD_FAILURES',1,['READ'],['CHECKED']),
  a(winning?'SEEK_INDEPENDENT_EVIDENCE':'REQUEST_NEW_LABELED_CASES',2,['CHECKED'],['QUESTION_READY']),
  a('ASSUME_RESULTS_ARE_GENERAL',9,['CHECKED'],['QUESTION_READY']),
  a('HOLD_FOR_OWNER_REVIEW',1,['QUESTION_READY'],['DONE'])
 ];
 const plan=solve(actions,['OBSERVED'],['DONE']);
 const replay=replaySteps(actions,plan.steps,['OBSERVED']);
 if(plan.status!=='PLAN_FOUND'||replay.cost!==plan.cost||
  !replay.final_facts.includes('DONE')||plan.steps.includes('ASSUME_RESULTS_ARE_GENERAL'))
  throw Error('HOLD_PLAN_REPLAY_FAILED');
 return {schema:'motif027.feedback-plan/v0',steps:plan.steps,cost:plan.cost,
  next_question:evaluation.failure_driven_next_question,
  classically_optimized:true,production_admission:false};
}
