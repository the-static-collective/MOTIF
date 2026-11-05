// MOTIF-028 — append-only, content-chained experimental memory.
// Explicit local owner-only persistence. Reopening reads entire history and
// refuses corruption; actual replay reruns original GRAFT-027 code.
// SHA digests detect accidental changes, not malicious rewriting by a keyholder.
import {
 readFileSync,writeSync,openSync,closeSync,fsyncSync,unlinkSync,mkdirSync,
 existsSync,lstatSync,fstatSync,constants
} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {
 verifyExperience,recallSimilar,replayExperience,captureExperience
} from './graft/src/experience-memory-028.mjs';
import {solve} from '../023/planz-snapshot/scripts/motif-classical.mjs';
import {verifyGardenOwners as verify027} from '../027/gardener.mjs';

const sha=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const MAX={entries:128,bytes:10000000,line:200000,plans:3};
const NAME='experiences.jsonl';

const PINNED=Object.freeze({
 'graft/src/experience-memory-028.mjs':'b1cf697e5049a931fc4133d152e372d4b1e81ec1',
 'graft/src/capability-gardener-027.mjs':'a8d74c3b236f1a53018a458b767ed0ac0120d243',
 'graft/src/discovered-adapter-026.mjs':'3227361a543fbfaa19cc445edfa64757f2b52c71',
 'graft/vendor/alex/api-discovery-026.mjs':'67b851c9ea58d4aa92ca159000e982c312cd2335',
 'graft/vendor/alex/eagle-eye-providers-025.mjs':'5c095be409d2ace0d39765c4316471702d88acb5'
});
export function verifyMemorySourceOwners(){
 verify027();
 const mismatches=[];
 for(const [relative,expected] of Object.entries(PINNED)){
  const bytes=readFileSync(new URL(relative,import.meta.url));
  const blob=createHash('sha1').update(Buffer.from('blob '+bytes.length+'\\0'))
   .update(bytes).digest('hex');
  if(blob!==expected)mismatches.push(relative);
 }
 if(mismatches.length)throw Error('HOLD_028_CHANGED_SOURCE_OWNER_CODE_'+mismatches.join('_'));
 return {original_graft_git_blobs:PINNED,
  inherited_source_checks:true,source_owner_approval_not_inferred:true};
}

function directory(dir,{create=false}={}){
 if(typeof dir!=='string'||!path.isAbsolute(dir)||dir.length>350)
  throw Error('HOLD_028_ABSOLUTE_EXPLICIT_STORE_REQUIRED');
 if(create)mkdirSync(dir,{recursive:true,mode:0o700});
 if(!existsSync(dir))throw Error('HOLD_028_MEMORY_DIRECTORY_MISSING');
 const s=lstatSync(dir);
 if(s.isSymbolicLink()||!s.isDirectory()||(s.mode&0o077)!==0)
  throw Error('HOLD_028_INSECURE_MEMORY_DIRECTORY');
 return path.join(dir,NAME);
}
function checkedFile(file){
 if(!existsSync(file))return false;
 const s=lstatSync(file);
 if(s.isSymbolicLink()||!s.isFile()||(s.mode&0o077)!==0||s.size>MAX.bytes)
  throw Error('HOLD_028_UNSAFE_OR_OVERSIZED_MEMORY');
 return true;
}
export function readLedger(dir){
 verifyMemorySourceOwners();
 const file=directory(dir);
 if(!checkedFile(file))return {schema:'motif028.ledger-snapshot/v0',entries:[],
  root_sha256:null,filename:NAME};
 const text=readFileSync(file,'utf8');
 if(!text)return {schema:'motif028.ledger-snapshot/v0',entries:[],
  root_sha256:null,filename:NAME};
 if(!text.endsWith('\n'))throw Error('HOLD_028_INCOMPLETE_LEDGER_LINE');
 const lines=text.slice(0,-1).split('\n');
 if(lines.length>MAX.entries)throw Error('HOLD_028_LEDGER_CAPACITY_EXCEEDED');
 let previous=null;const entries=[],ids=new Set();
 for(const [i,line] of lines.entries()){
  if(line.length>MAX.line)throw Error('HOLD_028_LEDGER_LINE_BUDGET');
  let entry;
  try{entry=JSON.parse(line)}catch{throw Error('HOLD_028_MALFORMED_LEDGER_LINE')}
  if(!entry||entry.schema!=='motif028.ledger-entry/v0'||
   entry.sequence!==i+1||entry.previous_sha256!==previous||
   typeof entry.entry_sha256!=='string')
   throw Error('HOLD_028_BROKEN_LEDGER_SEQUENCE');
  const {entry_sha256,...body}=entry;
  if(sha(body)!==entry_sha256)throw Error('HOLD_028_LEDGER_CHAIN_CHANGED');
  verifyExperience(entry.experience);
  if(ids.has(entry.experience.receipt_sha256))
   throw Error('HOLD_028_DUPLICATE_EXPERIENCE');
  ids.add(entry.experience.receipt_sha256);
  previous=entry_sha256;entries.push(entry);
 }
 return {schema:'motif028.ledger-snapshot/v0',entries,root_sha256:previous,filename:NAME};
}
export function appendLedger(dir,record,{approvedPersistentSave=false}={}){
 verifyMemorySourceOwners();
 if(approvedPersistentSave!==true)throw Error('HOLD_028_PERSISTENCE_REQUIRES_APPROVAL');
 verifyExperience(record);
 const file=directory(dir,{create:true});
 const lock=file+'.lock';
 // One-writer local lock; no silent stale-lock reset. Interrupted writes
 // that end without newline fail closed when the ledger is read again.
 let lockFd,fd;
 try{
  lockFd=openSync(lock,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|
    (constants.O_NOFOLLOW||0),0o600);
  const existing=readLedger(dir);
  const found=existing.entries.find(x=>x.experience.receipt_sha256===record.receipt_sha256);
  if(found)return {status:'DUPLICATE_NOT_REAPPENDED',count:existing.entries.length,
    entry_sha256:found.entry_sha256,root_sha256:existing.root_sha256};
  if(existing.entries.length>=MAX.entries)throw Error('HOLD_028_LEDGER_FULL');
  const body={schema:'motif028.ledger-entry/v0',
   sequence:existing.entries.length+1,
   previous_sha256:existing.root_sha256,experience:record};
  const entry={...body,entry_sha256:sha(body)};
  const line=JSON.stringify(entry)+'\n';
  if(Buffer.byteLength(line)>MAX.line)throw Error('HOLD_028_NEW_LINE_BUDGET');
  checkedFile(file);
  fd=openSync(file,constants.O_WRONLY|constants.O_APPEND|constants.O_CREAT|
    (constants.O_NOFOLLOW||0),0o600);
  if(!fstatSync(fd).isFile())throw Error('HOLD_028_STORE_NOT_A_REGULAR_FILE');
  const bytes=Buffer.from(line);
  if(writeSync(fd,bytes,0,bytes.length,null)!==bytes.length)
   throw Error('HOLD_028_INCOMPLETE_LEDGER_WRITE');
  fsyncSync(fd);
  return {status:'APPENDED_AND_FSYNCED',count:entry.sequence,
   entry_sha256:entry.entry_sha256,root_sha256:entry.entry_sha256};
 }finally{
  if(fd!==undefined)closeSync(fd);
  if(lockFd!==undefined){closeSync(lockFd);unlinkSync(lock)}
 }
}
const a=(name,cost,pre,add)=>({name,cost,pre,add,del:[]});
export function planFromMemory(recall){
 if(!recall||recall.schema!=='graft028.memory-recall/v0'||
  recall.authority!=='none'||!Array.isArray(recall.matches))throw Error('HOLD_028_UNTRUSTED_RECALL');
 const failed=recall.matches.some(x=>x.prior_outcome==='HOLD_ALL_VARIANTS_FAIL');
 const matched=recall.matches.length>0;
 const operation=failed?'RECREATE_PREVIOUS_FAILURE_AS_COUNTEREXAMPLE':
  matched?'VERIFY_PREVIOUS_SUCCESS_ON_FRESH_CASES':'DESIGN_FIRST_BASELINE_FIXTURE';
 const steps=[
  a('EXAMINE_CONTENT_ADDRESSED_PRECEDENTS',1,['QUESTION'],['PRECEDENTS_READ']),
  a(operation,2,['PRECEDENTS_READ'],['NEXT_CASE_DESIGNED']),
  a('ASSUME_PRIOR_SUCCESS_IS_PROOF',9,['PRECEDENTS_READ'],['NEXT_CASE_DESIGNED']),
  a('REQUIRE_NEW_INDEPENDENT_TEST',1,['NEXT_CASE_DESIGNED'],['REVIEW_READY'])
 ];
 const optimal=solve(steps,['QUESTION'],['REVIEW_READY']);
 if(optimal.status!=='PLAN_FOUND'||optimal.steps.includes('ASSUME_PRIOR_SUCCESS_IS_PROOF'))
  throw Error('HOLD_028_MEMORY_PLAN_NOT_SAFE');
 return {schema:'motif028.classical-memory-plan/v0',
  steps:optimal.steps,cost:optimal.cost,top_prior_outcome:recall.matches[0]?.prior_outcome??null,
  memory_is_not_authority:true,recommended_next_question:recall.next_question,
  original_planz_optimizer:true,external_actions:0};
}
export async function recallAndReplay(dir,cases,{limit=3}={}){
 verifyMemorySourceOwners();
 const history=readLedger(dir);
 const recall=recallSimilar(history.entries.map(x=>x.experience),cases,{limit});
 const replayed=[];
 for(const hit of recall.matches.slice(0,MAX.plans)){
  const entry=history.entries.find(x=>x.experience.receipt_sha256===hit.record_sha256);
  const verify=await replayExperience(entry.experience);
  replayed.push({record_sha256:hit.record_sha256,
   score:hit.score,status:verify.status,failed_candidates:verify.failed_candidates,
   original_result_reproduced:true});
 }
 return {schema:'motif028.replay-research/v0',
  stored_experiments:history.entries.length,
  hash_chain_tip:history.root_sha256,
  recall,replayed,plan:planFromMemory(recall),
  search_basis:'ACTUAL_SYNTHETIC_FIXTURE_STRUCTURE',
  not_motivational_text_generation:true,
  prior_failures_replayed_before_recommendation:true,
  automatic_program_promotion:false,
  remote_requests:0,authority:'none'};
}
export async function captureAndRemember(dir,sourcePacket,cases,
 {approvedSyntheticCapture=false,approvedPersistentSave=false}={}){
 if(approvedSyntheticCapture!==true||approvedPersistentSave!==true)
  throw Error('HOLD_028_CAPTURE_AND_PERSIST_NEED_SEPARATE_APPROVAL');
 const record=await captureExperience({
  source_packet:sourcePacket,cases,approvedSyntheticCapture:true});
 return {record,storage:appendLedger(dir,record,{approvedPersistentSave:true})};
}
export function ledgerLimits(){return {...MAX,filename:NAME};}
