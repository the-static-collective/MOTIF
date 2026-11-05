// Explicit local reproducible experiment memory. No network or private data.
// Examples: node experiments/028/cli.mjs seed /absolute/private/directory
//           node experiments/028/cli.mjs replay /absolute/private/directory
import {captureAndRemember,readLedger,recallAndReplay} from './ledger.mjs';
import {syntheticSource,normalCases,failedCases,futureCases}
 from './synthetic_examples.mjs';
const [verb,dir]=process.argv.slice(2);
if(!['seed','replay'].includes(verb)||!dir)
 throw Error('Usage: cli.mjs seed|replay /absolute/private/directory');
try{
 if(verb==='seed'){
  const a=await captureAndRemember(dir,syntheticSource(),normalCases(),
   {approvedSyntheticCapture:true,approvedPersistentSave:true});
  const b=await captureAndRemember(dir,syntheticSource(),failedCases(),
   {approvedSyntheticCapture:true,approvedPersistentSave:true});
  const l=readLedger(dir);
  process.stdout.write(JSON.stringify({status:'SYNTHETIC_LEDGER_WRITTEN',
   records:l.entries.length,root_sha256:l.root_sha256,
   first:a.storage.status,second:b.storage.status,no_network_calls:true})+'\n');
 }else{
  const r=await recallAndReplay(dir,futureCases());
  if(r.stored_experiments<2||r.replayed.length<1||
   !r.replayed.every(x=>x.status==='EXACT_EXECUTABLE_REPLAY_MATCH'))
   throw Error('HOLD_028_PROCESS_RESTART_REPLAY_FAILED');
  process.stdout.write(JSON.stringify({
   status:'EXPERIENCES_REPLAYED_IN_NEW_NODE_PROCESS',
   prior_count:r.stored_experiments,matched:r.replayed.length,
   plan:r.plan.steps,tip:r.hash_chain_tip,
   production_installed:false,remote_requests:0})+'\n');
 }
}catch(e){
 process.stderr.write(String(e.message)+'\n');process.exitCode=2;
}
