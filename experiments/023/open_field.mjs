// MOTIF-023 — The Open Question Field
// Real read-only live public GitHub discovery -> original classical planning
// -> compiled executable GRAFT review -> observation -> next research question.
// Exactly two bounded iterations; never source-owner authority or production.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {
  investigatePublic,selectCollections,verifyPacket
} from './alex-snapshot/tools/motif023-live.mjs';
import {
  planEvidence,verifyPlan,replanAfterObservation
} from './planz-snapshot/scripts/motif023-replan.mjs';
import {
  compileEvidenceCapability,executeCandidate,verifyNativePlanZ
} from './graft-snapshot/src/motif023-compiler.mjs';
import {questionGate,simulate,investigate} from '../019/common_ancestor.mjs';
import {runMaxhinal,hypothesisQuestionBundle} from '../020/madd_custody.mjs';
import {verifySourceOrgans} from '../021/cross_organ.mjs';
import {verifyPinnedOrgans as verify022} from '../022/next_question.mjs';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const SELF=fileURLToPath(import.meta.url);
const gitBlob=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0'))
 .update(b).digest('hex');
const sha=x=>createHash('sha256').update(x).digest('hex');

export function verifyOrgans(){
 verifySourceOrgans();
 verify022();
 const manifest=JSON.parse(readFileSync(path.join(HERE,'pins.json'),'utf8'));
 if(manifest.schema!=='motif023.pinned-source-organs/v0'||
   Object.keys(manifest.source_blobs).length!==6)
  throw Error('HOLD_MOTIF023_INVALID_SOURCE_PINSET');
 for(const [relative,expected] of Object.entries(manifest.source_blobs)){
  if(!/^(alex-snapshot|planz-snapshot|graft-snapshot)\//.test(relative)||
    !/^[0-9a-f]{40}$/.test(expected)||
    gitBlob(readFileSync(path.join(HERE,relative)))!==expected)
   throw Error('HOLD_MOTIF023_SOURCE_BLOB_DRIFT_'+relative);
 }
 const planZ=verifyNativePlanZ();
 if(planZ.exact_replan_blob!==
    manifest.source_blobs['planz-snapshot/scripts/motif023-replan.mjs'])
  throw Error('HOLD_DISAGREEING_PLANZ_DONOR');
 return manifest;
}
async function oneRound(question,collections,transport,token){
 const packet=await investigatePublic({question,collections},{transport,token});
 if(packet.status==='HOLD_NO_REGISTERED_PUBLIC_COLLECTION')
  return {status:'HOLD_OUTSIDE_REGISTERED_SOURCE_CATALOG',
   packet,plan:null,candidate:null,execution:null};
 verifyPacket(packet);
 const plan=planEvidence(packet);
 verifyPlan(plan,packet);
 if(plan.status!=='HELD_CLASSICAL_PLAN'){
  return {status:'HOLD_MISSING_VERIFIED_SOURCE_LEADS',
   packet,plan,candidate:null,execution:null};
 }
 const candidate=compileEvidenceCapability(packet,plan);
 const execution=await executeCandidate(candidate,packet,plan);
 return {
  status:'EXECUTED_LOCAL_SOURCE_REVIEW',
  packet,plan,
  candidate:{
   schema:candidate.schema,mode:candidate.mode,
   generated_source_sha256:candidate.source_sha256,
   generated_source_length:candidate.source.length,
   synthesis:candidate.synthesis,
   production_installed:candidate.production_installed,
   authority:candidate.authority
  },
  execution
 };
}
export async function runOpenField(question,options={}){
 const pins=verifyOrgans();
 const {collections=null,transport=globalThis.fetch,token=null,
  secondPass=true}=options;
 const initialSelection=selectCollections(question,collections);
 if(initialSelection.repositories.length===0)
  return {
   schema:'motif023.open-question-field/v0',status:'HOLD_NO_AUTHORIZED_COLLECTION',
   question,initial_selection:initialSelection,
   first:null,second:null,feedback_plan:null,
   external_actions:0,source_custody_proved:false
  };
 const first=await oneRound(question,collections,transport,token);
 if(first.status!=='EXECUTED_LOCAL_SOURCE_REVIEW'){
  return {
   schema:'motif023.open-question-field/v0',
   status:'HOLD_SOURCE_ACQUISITION_OR_COVERAGE',
   question,initial_selection:initialSelection,
   first,second:null,feedback_plan:null,
   complete_source_corpus:false,
   external_actions:0,source_custody_proved:false
  };
 }
 const replan=replanAfterObservation(first.packet,first.plan,first.execution);
 let second=null;
 if(secondPass){
  // The observed runtime result determined a different **bounded public**
  // source collection. This is a new real read, not fabricated program output.
  second=await oneRound(replan.next_question,replan.next_source_collections,
   transport,token);
 }
 const receipt={
  schema:'motif023.open-question-field/v0',
  status:secondPass&&second?.status==='EXECUTED_LOCAL_SOURCE_REVIEW'?
   'TWO_LIVE_PUBLIC_INQUIRIES_AND_TWO_LOCAL_CAPABILITIES':
   secondPass?'HELD_SECOND_RESEARCH':
   'FIRST_INQUIRY_EXECUTED_NEXT_PROPOSED',
  question,initial_selection:initialSelection,
  source_owner_pins:pins.source_owners,
  first,feedback_plan:replan,second,
  actually_found_new_public_source_collection:
   !!second&&second.packet.sources.some(s=>
    !first.packet.sources.some(p=>p.repository===s.repository)),
  next_question_from_real_local_observation:true,
  no_real_independent_ancestry_established:true,
  no_live_private_sources_read:true,
  no_source_owner_grants_inherited:true,
  source_custody_proved:false,
  complete_source_corpus:false,
  autonomy_scope:'TWO_PUBLIC_READ_ROUNDS_AND_BOUNDED_LOCAL_COMPUTATION',
  external_actions:0,production_installed:false
 };
 return {...receipt,checksum_sha256:sha(JSON.stringify(receipt))};
}
export async function demonstrate(options={}){
 const prior=investigate(simulate('hidden_ancestor',643).records,questionGate());
 const madd=runMaxhinal(prior,'main','motif023-example');
 const priorQuestions=hypothesisQuestionBundle(prior,madd.ride);
 const q='Which original Maxhinal Fiber and Pressure chambers preserve source custody?';
 const result=await runOpenField(q,options);
 return {
  schema:'motif023.open-question-field-study/v0',
  premise:{
   source:'REAL_ORIGINAL_MADD_MAXHINAL_CHAMBERS_PLUS_NATIVE_DOGRAM',
   original_madd_ride_id:madd.ride.ride_id,
   unresolved_question:priorQuestions.required_next_action
  },
  experiment:result,
  critical_limits:[
   'Public GitHub repo allowlist, maximum two repositories and two small Markdown files per repository per round.',
   'Two live source rounds, not a background unrestricted search agent.',
   'Search hits and repository metadata do not authenticate an independent original human witness.',
   'Finite original classical STRIPS and fixed audited code fragments, not arbitrary unconstrained code synthesis.',
   'Original ALEX, planZ, GRAFT, MOTIF, Dogram and Maxhinal source owners unchanged.',
   'No merges, deployment, external contact, real source-owner admission or private reads.'
  ]
 };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF){
 const question=process.argv.slice(2).join(' ');
 (question?runOpenField(question,{token:process.env.GITHUB_TOKEN||null}):
  demonstrate({token:process.env.GITHUB_TOKEN||null}))
  .then(r=>process.stdout.write(JSON.stringify(r,null,2)+'\n'))
  .catch(e=>{process.stderr.write(String(e.message)+'\n');process.exitCode=2});
}
