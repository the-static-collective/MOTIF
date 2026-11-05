// MOTIF-022 — a new question drives genuine pinned ALEX → planZ → GRAFT code.
// All searches are limited to the approved five public pinned Markdown sources.
// All GRAFT results are local executable review candidates, not world actions.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {verifySourceOrgans,runResearchCycle} from '../021/cross_organ.mjs';
import {ask,validate as validateAlex} from './alex-snapshot/tools/motif022-question.mjs';
import {planQuestion,validatePlan} from './planz-snapshot/scripts/motif022-plan.mjs';
import {compileCapability} from './graft-snapshot/src/motif022-inquiry-compiler.mjs';
import {execute as lineage} from './graft-snapshot/generated/motif022-lineage.mjs';
import {execute as composition} from './graft-snapshot/generated/motif022-composition.mjs';
import {execute as reliability} from './graft-snapshot/generated/motif022-reliability.mjs';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const OWN=path.resolve(HERE,'../021/alex-snapshot/research/packets/MOTIF-021');
const MODES={LINEAGE:lineage,COMPOSITION:composition,RELIABILITY:reliability};
const gitBlob=bytes=>createHash('sha1')
 .update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export const QUESTIONS=[
 'Which original carrier supports a suspected hidden common ancestor?',
 'Which source plans can compose a bounded GRAFT capability?',
 'How could independent reference witnesses suffer shared failures?',
 'Can flibbergast quasarship make xyzzymorphs in squarzonium?'
];
export function verifyPinnedOrgans(){
 const older=verifySourceOrgans();
 const p=JSON.parse(readFileSync(path.join(HERE,'pins.json'),'utf8'));
 if(p.schema!=='motif022.original-donor-pins/v0'||
    Object.keys(p.files).length!==7)
   throw Error('HOLD_MOTIF022_PINSET_MISSING');
 for(const [file,blob] of Object.entries(p.files)){
  if(!/^(alex-snapshot|planz-snapshot|graft-snapshot)\//.test(file)||
     !/^[a-f0-9]{40}$/.test(blob)||
     gitBlob(readFileSync(path.join(HERE,file)))!==blob)
   throw Error('HOLD_MOTIF022_SOURCE_BLOB_CHANGED_'+file);
 }
 return {prior_021:older.schema,source_code_blobs:p.files,
   source_owner_commit_refs:p.source_owners};
}
export function runQuestion(question){
 const pins=verifyPinnedOrgans();
 const packet=ask(question,OWN);
 validateAlex(packet);
 const plan=planQuestion(packet);
 validatePlan(plan,packet);
 if(packet.status!=='RESEARCH_PACKET_HELD'){
  return {
   schema:'motif022.question-to-executable/v0',
   status:'HOLD_NO_RELEVANT_SOURCE_MATERIAL',
   question,alex_packet:packet,planz_plan:plan,
   generated_capability:null,executed_capability:null,
   source_owners:pins.source_owner_commit_refs,
   real_world_search_executed:false,external_actions:0,
   production_install:false,source_custody_authenticated:false
  };
 }
 const candidate=compileCapability(packet,plan);
 const execute=MODES[plan.intent];
 if(typeof execute!=='function'||candidate.mode!==plan.intent)
  throw Error('HOLD_NO_WHITELISTED_EXECUTABLE_MODE');
 const filename='graft-snapshot/generated/motif022-'+
  plan.intent.toLowerCase()+'.mjs';
 const source=readFileSync(path.join(HERE,filename),'utf8');
 if(candidate.source!==source||sha(source)!==candidate.sha256)
  throw Error('HOLD_GRAFT_COMPILED_SOURCE_DIVERGES');
 const result=execute(packet);
 if(result.mode!==plan.intent||result.authority!=='none'||
    result.external_actions!==0||result.evidence_admission!=='NONE'||
    result.source_custody_verified!==false)
  throw Error('HOLD_GRAFT_EXECUTION_AUTHORITY');
 const receipt={
  schema:'motif022.question-to-executable/v0',
  status:'EXECUTED_LOCAL_HELD_CAPABILITY',
  question,alex_packet:packet,planz_plan:plan,
  generated_capability:{
   id:'MOTIF022_'+plan.intent,
   source_sha256:candidate.sha256,
   source_relative_path:filename,
   compilation_kind:candidate.compilation_kind,
   code_review_needed:true,
   user_input_interpolated_into_code:false
  },
  executed_capability:result,
  source_owners:pins.source_owner_commit_refs,
  source_pin_count:Object.keys(pins.source_code_blobs).length,
  real_world_search_executed:false,
  live_external_source_crawl:false,
  independently_verified_real_ancestry:false,
  any_owner_approval_inherited:false,
  external_actions:0,production_install:false,
  source_custody_authenticated:false
 };
 return {...receipt,checksum_sha256:sha(JSON.stringify(receipt))};
}
export function demonstration(){
 const cases=QUESTIONS.map(runQuestion);
 const inherited=runResearchCycle();
 return {
  schema:'motif022.multiple-new-questions-study/v0',
  status:'EXECUTED_SOURCE_PINNED_NEW_QUESTION_PIPELINE',
  cases,
  inherited_original_madd_ride_id:
    inherited.originating_motif.original_maxhinal_ride_id,
  inherited_original_native_research_pins:
    inherited.verified_source_blob_count,
  limitations:[
   'five publicly materialized frozen documents; not universal or current ALEX search',
   'question classification and STRIPS actions are finite human-designed grammar',
   'GRAFT code generation selects fixed checked templates; no arbitrary code invention',
   'source hits are leads; document-level distinctness is not witness independence',
   'no external effects, source-owner admission, production deployment, or real custody verified'
  ],
  held_review_required:true,
  persistent_runtime_across_sessions:false
 };
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const raw=process.argv.slice(2).join(' ');
 try{process.stdout.write(JSON.stringify(raw?runQuestion(raw):demonstration(),null,2)+'\n')}
 catch(e){process.stderr.write(String(e.message)+'\n');process.exitCode=2}
}
