import test from 'node:test';
import assert from 'node:assert/strict';
import {
 mkdtempSync,rmSync,readFileSync,writeFileSync,chmodSync,symlinkSync
} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {
 verifyMemorySourceOwners,readLedger,appendLedger,captureAndRemember,
 recallAndReplay,planFromMemory,ledgerLimits
} from './ledger.mjs';
import {syntheticSource,normalCases,failedCases,futureCases,unrelatedCases}
 from './synthetic_examples.mjs';
import {
 captureExperience,replayExperience
} from './graft/src/experience-memory-028.mjs';
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
function home(){return mkdtempSync(path.join(tmpdir(),'motif-028-'))}
async function recorded(dir,cases){
 return captureAndRemember(dir,syntheticSource(),cases,
  {approvedSyntheticCapture:true,approvedPersistentSave:true});
}
test('new GRAFT source, original GRAFT-027 and old source organs remain exact pinned bytes',()=>{
 const v=verifyMemorySourceOwners();
 assert.equal(Object.keys(v.original_graft_git_blobs).length,5);
 assert.equal(v.inherited_source_checks,true);
});
test('first synthetic pass and conflicting failure survive append, reopened file and exact executed replay',async()=>{
 const dir=home();
 try{
  const first=await recorded(dir,normalCases());
  const second=await recorded(dir,failedCases());
  assert.equal(first.storage.status,'APPENDED_AND_FSYNCED');
  assert.equal(second.storage.status,'APPENDED_AND_FSYNCED');
  const h=readLedger(dir);
  assert.equal(h.entries.length,2);
  assert.equal(h.entries[1].previous_sha256,h.entries[0].entry_sha256);
  assert.equal(h.root_sha256,h.entries[1].entry_sha256);
  assert.equal(h.entries[0].experience.outcome,'HELD_BEST_FIXTURE_CANDIDATE');
  assert.equal(h.entries[1].experience.outcome,'HOLD_ALL_VARIANTS_FAIL');
  assert.equal((await replayExperience(h.entries[0].experience)).status,'EXACT_EXECUTABLE_REPLAY_MATCH');
  assert.equal((await replayExperience(h.entries[1].experience)).winner,null);
  const replay=await recallAndReplay(dir,futureCases());
  assert.equal(replay.stored_experiments,2);
  assert.ok(replay.replayed.length>=1);
  assert.ok(replay.replayed.every(r=>r.status==='EXACT_EXECUTABLE_REPLAY_MATCH'));
  assert.equal(replay.plan.steps.includes('RECREATE_PREVIOUS_FAILURE_AS_COUNTEREXAMPLE'),true);
  assert.equal(replay.automatic_program_promotion,false);
  assert.equal(replay.remote_requests,0);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('duplicate synthetic experience does not append duplicate or change hash-chain root',async()=>{
 const dir=home();
 try{
  const first=await recorded(dir,normalCases());
  const second=await recorded(dir,normalCases());
  assert.equal(second.storage.status,'DUPLICATE_NOT_REAPPENDED');
  assert.equal(second.storage.root_sha256,first.storage.root_sha256);
  assert.equal(readLedger(dir).entries.length,1);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('unrelated structure retrieves no nearby precedent and selects original classical baseline plan',async()=>{
 const dir=home();
 try{
  await recorded(dir,normalCases());
  const r=await recallAndReplay(dir,unrelatedCases());
  assert.equal(r.recall.status,'NO_CLOSE_STRUCTURAL_PRECEDENT');
  assert.equal(r.plan.steps.includes('DESIGN_FIRST_BASELINE_FIXTURE'),true);
  assert.equal(r.replayed.length,0);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('detect changed hash-chain entry, truncated write and symlink replacement',async()=>{
 const dir=home(),name=path.join(dir,ledgerLimits().filename);
 try{
  await recorded(dir,normalCases());
  const original=readFileSync(name,'utf8');
  writeFileSync(name,original.replace('"sequence":1','"sequence":2'),{mode:0o600});
  assert.throws(()=>readLedger(dir),/BROKEN_LEDGER_SEQUENCE/);
  writeFileSync(name,original.slice(0,-1),{mode:0o600});
  assert.throws(()=>readLedger(dir),/INCOMPLETE_LEDGER_LINE/);
  rmSync(name);
  const target=path.join(dir,'elsewhere.jsonl');
  writeFileSync(target,original,{mode:0o600});
  symlinkSync(target,name);
  assert.throws(()=>readLedger(dir),/UNSAFE_OR_OVERSIZED_MEMORY/);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('even a rehashed local record with altered expected values is caught by executable replay',async()=>{
 const dir=home(),name=path.join(dir,ledgerLimits().filename);
 try{
  await recorded(dir,normalCases());
  const entry=JSON.parse(readFileSync(name,'utf8').trim());
  entry.experience.cases.holdout[0].expected=123456;
  const exp={...entry.experience};delete exp.receipt_sha256;
  entry.experience.receipt_sha256=hash(exp);
  const body={...entry};delete body.entry_sha256;
  entry.entry_sha256=hash(body);
  writeFileSync(name,JSON.stringify(entry)+'\n',{mode:0o600});
  assert.equal(readLedger(dir).entries.length,1);
  await assert.rejects(recallAndReplay(dir,futureCases()),/REPLAY_DIVERGED/);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('no persistent retention without distinct explicit consent',async()=>{
 const dir=home();
 try{
  const record=await captureExperience({
   source_packet:syntheticSource(),cases:normalCases(),approvedSyntheticCapture:true});
  assert.throws(()=>appendLedger(dir,record),/PERSISTENCE_REQUIRES_APPROVAL/);
  await assert.rejects(captureAndRemember(dir,syntheticSource(),normalCases(),
   {approvedSyntheticCapture:true}),/SEPARATE_APPROVAL/);
  assert.equal(readLedger(dir).entries.length,0);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('local permissions deny publicly readable directory and stale-writer race',async()=>{
 const dir=home();
 try{
  const record=await captureExperience({
   source_packet:syntheticSource(),cases:normalCases(),approvedSyntheticCapture:true});
  chmodSync(dir,0o755);
  assert.throws(()=>appendLedger(dir,record,{approvedPersistentSave:true}),
   /INSECURE_MEMORY_DIRECTORY/);
  chmodSync(dir,0o700);
  writeFileSync(path.join(dir,ledgerLimits().filename+'.lock'),'other writer',{mode:0o600});
  assert.throws(()=>appendLedger(dir,record,{approvedPersistentSave:true}),/EEXIST/);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
