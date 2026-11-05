// MOTIF-020 — MADD Source-Custody Maxhinal
// Pin and invoke actual MADD Hugh Jackman Maxhinal source-owned CommonJS modules.
// Each product is a synthetic projection, never verified evidence or permission.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {
  simulate,investigate,questionGate,proposedDiscriminators,
  validateReceipt as verify019
} from '../019/common_ancestor.mjs';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const SELF=fileURLToPath(import.meta.url);
const REPO='the-static-collective/the-daily-slice';
const DONOR_COMMIT='23c3d4bf7e4febb89919a3d54b6e8aaf3a764120';
const BLOBS=Object.freeze({
 'maxhinal-modes.js':'0e62e21e802d727373ae7c19b421dde52b495f0b',
 'maxhinal-chambers.js':'97fbc799836c2f4dfe379bc26a5b14b9ff3348eb',
 'maxhinal-core.js':'302ad18bfbb4bf03368bd859c3ba7d0dd3a2b684'
});
const SCHEMA='motif020.maxhinal-graft-receipt/v0';
const HYP=['carrier','difficulty','reference','independent'];
const IDS=HYP.map(x=>'hyp-'+x);
const MAX_OPERATIONS=20;
const MAX_BYTES=262144;

const hash=b=>createHash('sha256').update(b).digest('hex');
function gitBlob(buffer){
 return createHash('sha1').update(Buffer.from('blob '+buffer.length+'\0'))
   .update(buffer).digest('hex');
}
export function verifyPinnedMaxhinal(){
 const proof={};
 for(const [name,expected] of Object.entries(BLOBS)){
  const input=readFileSync(path.join(HERE,'upstream',name));
  if(gitBlob(input)!==expected)throw Error('HOLD_MADD_DONOR_BLOB_MISMATCH_'+name);
  proof[name]=expected;
 }
 return {origin_repository:REPO,donor_commit:DONOR_COMMIT,
   exact_git_blobs:proof,
   source_authenticity:'CONTENT_PIN_ONLY_REQUIRES_SOURCE_OWNER_REVIEW',
   local_execution_licensed_as_read_only_experiment:true};
}
const require=createRequire(import.meta.url);
let core;
function pinnedCore(){
 verifyPinnedMaxhinal();
 if(!core){
  // Registration modifies the in-memory Maxhinal module registry only.
  // It does NOT mutate repository files or source-owner code.
  require('./upstream/maxhinal-chambers.js');
  core=require('./upstream/maxhinal-core.js');
 }
 if(core.FORMAT!=='maxhinal/v0'||core.JOB_FORMAT!=='maxhinal-job/v0')
  throw Error('HOLD_MADD_RUNTIME_FORMAT_DRIFT');
 return core;
}
const STRATA={
 carrier:{
  title:'Shared upstream carrier — hypothetical',
  date:'2026-08-30',
  summary:'shared source error observations may descend from one attributable carrier',
  carry:'shared errors candidate literal source ancestry NOT VERIFIED',
  text:'carrier custody original and transfer receipts missing; shared error association is not identity proof',
  hypothesis:'LITERAL_CARRIER_COMMON_ANCESTOR'
 },
 difficulty:{
  title:'Shared environmental difficulty — hypothetical',
  date:'2026-08-31',
  summary:'shared source error observations may arise from common environmental difficulty',
  carry:'shared errors candidate common cause NOT VERIFIED',
  text:'item level hardness makes independent reporters fail together without copying an original carrier',
  hypothesis:'COMMON_ENVIRONMENT_WITHOUT_CARRIER_ANCESTRY'
 },
 reference:{
  title:'Shared reference corruption — hypothetical',
  date:'2026-09-01',
  summary:'shared source error observations may be manufactured by joint reference corruption',
  carry:'shared errors candidate colluding references NOT VERIFIED',
  text:'two declared independent reference feeds can share one hidden error in labeling',
  hypothesis:'COMMON_MODE_REFERENCE_FAILURE'
 },
 independent:{
  title:'Independent noise — hypothetical',
  date:'2026-09-02',
  summary:'apparently shared source errors could be incidental on finite evidence',
  carry:'independence cannot be proven by lack of detected common error',
  text:'finite data and ordinary noise create occasional correlations with no known common source',
  hypothesis:'INDEPENDENT_NOISE_UNRESOLVED'
 }
};
function require019(receipt){
 if(!receipt)throw Error('HOLD_NO_MOTIF019_RECEIPT');
 verify019(receipt);
 if(receipt.study_scope!=='SYNTHETIC_DECLARED_REFERENCE_COHORT' ||
   !receipt.all_pairwise_tests?.length ||
   receipt.no_causal_ancestry_identification_from_observational_dependence!==true ||
   receipt.real_reference_independence_authenticated!==false)
  throw Error('HOLD_MOTIF019_EVIDENCE_BOUNDARY');
 return receipt;
}
export function buildHypothesisGas(sourceReceipt){
 require019(sourceReceipt);
 const records=HYP.map((k)=>{
  const entry=STRATA[k];
  return {id:'hyp-'+k,title:entry.title,date:entry.date,
    summary:entry.summary,carry:entry.carry,text:entry.text,
    hypothesis:entry.hypothesis,
    path:'synthetic:/motif020/'+k,
    origin_receipt_checksum:sourceReceipt.checksum_sha256,
    evidence_status:'HYPOTHESIS_NOT_ADMITTED'};
 });
 const digest='sha256:'+hash(JSON.stringify({
   upstream:sourceReceipt.checksum_sha256,
   records
 }));
 return {
   records,
   meta:{
     format:'motif020.synthetic-hypothesis-gas/v0',
     digest,record_count:records.length,
     upstream_receipt_checksum:sourceReceipt.checksum_sha256,
     source_type:'MOTIF019_TEST_FIXTURE_NOT_DAILY_SLICE',
     evidence_authority:'none'
   }
 };
}
const sref=id=>({kind:'slice',slice_id:id});
function operations(){
 const all=IDS.map(sref);
 return Object.freeze({
  fiber:{
    mode:'fiber',inputs:all,
    parameters:{target:'shared errors'},
    co_phase:'unknown'
  },
  origin:{
    mode:'moving-origin',inputs:all,
    parameters:{origin_slice_id:'hyp-carrier'},
    co_phase:'unknown'
  },
  pressure_lineage:{
    mode:'pressure',inputs:[sref('hyp-carrier')],
    parameters:{candidate_kind:'lineage'},
    co_phase:'unknown'
  },
  pressure_causation:{
    mode:'pressure',inputs:[sref('hyp-difficulty')],
    parameters:{candidate_kind:'causation'},
    co_phase:'unknown'
  },
  clown:{
    mode:'maddclown',inputs:[sref('hyp-carrier'),sref('hyp-reference')],
    parameters:{context_text:'Do shared errors prove a literal source ancestor?'},
    co_phase:'not-co'
  },
  braid:{
    mode:'walk-braid',inputs:all,
    parameters:{steps:[
      {verb:'predict',co_phase:'unknown'},
      {verb:'construct',co_phase:'not-co'},
      {verb:'compose',co_phase:'co'}],
      operator_model:'co-sensitive'},
    co_phase:'unknown'
  },
  compose:{
    mode:'compose',inputs:all.slice(0,3),
    parameters:{order:['hyp-reference','hyp-carrier','hyp-difficulty'],
      seams:['candidate coexistence, not verified causal ancestry']},
    co_phase:'unknown'
  },
  discontinuity:{
    mode:'discontinuity',inputs:[sref('hyp-carrier'),sref('hyp-difficulty')],
    parameters:{verdict:'unresolved',
      reason:'Shared errors cannot uniquely identify a literal ancestor',
      avoid_kind:'refusal'},
    co_phase:'unknown'
  }
 });
}
const PROGRAMS=Object.freeze({
 main:['fiber','origin','pressure_lineage','pressure_causation','clown','braid','compose','discontinuity'],
 alternate:['clown','pressure_causation','fiber','origin','discontinuity','compose','braid','pressure_lineage']
});
export function compileJob(phase='main',seed='madd-custody-020'){
 if(!Object.hasOwn(PROGRAMS,phase))throw Error('HOLD_UNAUTHORIZED_GRAFT_PROGRAM');
 if(typeof seed!=='string'||!seed||seed.length>80)
   throw Error('HOLD_UNAUTHORIZED_SEED');
 const dictionary=operations();
 const program=PROGRAMS[phase].map(x=>dictionary[x]);
 if(program.length>MAX_OPERATIONS)throw Error('HOLD_GRAFT_OPERATION_BUDGET');
 return {format:'maxhinal-job/v0',seed,gas:[...IDS],
   operations:structuredClone(program)};
}
export function runMaxhinal(sourceReceipt,phase='main',seed='madd-custody-020'){
 const Core=pinnedCore();
 const gas=buildHypothesisGas(sourceReceipt);
 const job=compileJob(phase,seed);
 const ride=Core.runJob(gas,job);
 if(ride.authority!=='none'||ride.promotion!=='NONE'||
   ride.operations.length!==job.operations.length ||
   ride.operations.some(op=>op.receipt?.authority!=='none'||
     op.receipt?.promotion!=='NONE')||
   ride.replay.status!=='EXACT')
  throw Error('HOLD_MAXHINAL_AUTHORITY_BOUNDARY');
 if(!ride.operations.some(x=>x.mode==='maddclown')||
   !ride.operations.some(x=>x.mode==='fiber')||
   !ride.operations.some(x=>x.mode==='pressure'))
  throw Error('HOLD_MADD_CHAMBERS_NOT_EXERCISED');
 if(ride.outputs.some(x=>x.status==='INVALID_MODEL') ||
   ride.residuals.some(x=>x.code==='MISSING_INPUT'))
  throw Error('HOLD_MAXHINAL_INVALID_SOURCE');
 if(Buffer.byteLength(Core.serializeRide(ride))>MAX_BYTES)
  throw Error('HOLD_MAXHINAL_RIDE_TOO_LARGE');
 return {gas,job,ride};
}
export function validateRide(gas,ride){
 const Core=pinnedCore();
 if(!gas?.meta?.digest ||
   gas.meta.source_type!=='MOTIF019_TEST_FIXTURE_NOT_DAILY_SLICE' ||
   !ride||ride.format!=='maxhinal/v0'||
   ride.corpus?.digest!==gas.meta.digest ||
   ride.authority!=='none'||ride.promotion!=='NONE' ||
   ride.replay?.status!=='EXACT' ||
   !Array.isArray(ride.operations) ||
   ride.operations.length>MAX_OPERATIONS ||
   ride.operations.some(op=>!['fiber','moving-origin','pressure',
      'maddclown','walk-braid','compose','discontinuity'].includes(op.mode)) ||
   ride.gas.some(x=>!IDS.includes(x.slice_id))||
   ride.outputs.some(x=>x.kind!=='derived'||
     !ride.operations.some(op=>op.operation_id===x.source_operation_id)))
  throw Error('HOLD_MAXHINAL_RIDE_CONTRACT');
 const encoded=Core.serializeRide(ride);
 if(Buffer.byteLength(encoded)>MAX_BYTES)
  throw Error('HOLD_MAXHINAL_RIDE_TOO_LARGE');
 return Core.hydrateRide(JSON.parse(encoded),gas.meta);
}
export function challengeTheRide(inputRide,outputId){
 const Core=pinnedCore();
 if(!inputRide || inputRide.authority!=='none' ||
   !inputRide.outputs?.some(x=>x.output_id===outputId))
  throw Error('HOLD_UNKNOWN_DERIVED_OUTPUT');
 // This does not erase a mistaken hypothesis, operation, or projection.
 const challenged=Core.appendBadSpin(inputRide,{
   kind:'epistemic-counterpressure',output_ref:outputId,
   reason:'Text overlap and creative composition do not establish an actual common ancestor or authenticated custody.'
 });
 if(challenged.outputs.length!==inputRide.outputs.length||
   challenged.operations.length!==inputRide.operations.length)
  throw Error('HOLD_NONAPPEND_CHALLENGE');
 return challenged;
}
export function replayBranch(gas,first,more,seed='ignored-for-existing-ride'){
 const Core=pinnedCore();
 validateRide(gas,first);
 const add=compileJob(more,seed);
 if(first.seed!==add.seed){
   // Core.runJob intentionally retains the *existing* seed; the rejoin
   // cannot secretly replace historical seed or corpus identity.
   add.seed=first.seed;
 }
 const resumed=Core.runJob(gas,add,first);
 if(resumed.replay.status!=='EXACT'||resumed.seed!==first.seed||
   resumed.operations.length!==first.operations.length+add.operations.length ||
   resumed.operations.slice(0,first.operations.length).some((x,i)=>
     JSON.stringify(x)!==JSON.stringify(first.operations[i])))
  throw Error('HOLD_APPEND_ONLY_REPLAY_BOUNDARY');
 return resumed;
}
export function hypothesisQuestionBundle(receipt,ride){
 require019(receipt);
 const pressures=ride.outputs.filter(x=>x.mode==='pressure').map(o=>({
   original_mode:o.mode,source_operation:o.source_operation_id,
   question:o.value?.candidate_probe??null,
   evidence_status:'PROJECTION_ONLY_NOT_AUTHENTICATED'
 }));
 const draft=proposedDiscriminators(receipt,1.5);
 return {
   schema:'motif020.source-custody-inquiry-bundle/v0',
   motif019_candidates:receipt.statistically_suspected_shared_failure_links.length,
   projected_original_maxhinal_pressures:pressures,
   motif019_independent_tests:draft.actions,
   required_next_action:'RECOVER_REAL_ORIGINAL_CUSTODY_BEFORE_GENEALOGY_PROMOTION',
   unsupported_common_ancestor_hypotheses_kept:true,
   materialized_evidence:false,
   synthetic_test_bench_only:true,
   automatically_executed_probes:0
 };
}
export function experiment(){
 const donor=verifyPinnedMaxhinal();
 const gate=questionGate();
 const models={};
 for(const regime of ['hidden_ancestor','shared_difficulty','reference_collusion']){
  const simulated=simulate(regime,643);
  const result=investigate(simulated.records,gate);
  require019(result);
  const main=runMaxhinal(result);
  const second=runMaxhinal(result,'alternate');
  const challenged=challengeTheRide(main.ride,main.ride.outputs[0].output_id);
  validateRide(main.gas,challenged);
  const resumed=replayBranch(main.gas,challenged,'alternate','madd-custody-020');
  const drift=structuredClone(main.gas.meta);
  drift.digest='sha256:deliberately-altered-corpus';
  const drifted=pinnedCore().hydrateRide(challenged,drift);
  models[regime]={
   input_019_checksum:result.checksum_sha256,
   motif019_suspected_links:result.statistically_suspected_shared_failure_links.length,
   main_ride:challenged,alternate_ride:second.ride,
   continuation:{
    operations:resumed.operations.length,
    earliest_operation_still_present:
      JSON.stringify(resumed.operations[0])===JSON.stringify(challenged.operations[0]),
    bad_spin_count:resumed.bad_spins.length,
    replay_status:resumed.replay.status
   },
   corpus_drift_not_silently_rebound:drifted.replay.status==='CORPUS_DRIFT',
   questions:hypothesisQuestionBundle(result,challenged),
   maxhinal_fiber_compatible_refs:challenged.outputs.find(x=>x.mode==='fiber')?.value?.compatible_refs,
   literal_ancestor_established:false
  };
 }
 const entry=gate.question_receipt;
 return {
  schema:SCHEMA,status:'SYNTHETIC_READ_ONLY_SOURCE_CUSTODY_EXPERIMENT',
  exact_original_donors:donor,
  original_national_treasure_question:entry.question,
  original_dogram_blob:gate.dogram_receipt.source_blob,
  regimes:models,
  essential_negative_result:'All three generator worlds can retain the same token-compatible hypothesis fiber; source-based ancestry stays unidentified.',
  additional_external_modules:{ALEX:'NOT_BOUND',GRAFT:'NOT_BOUND',
    MADDlibMaxhine:'NOT_BOUND',PLANZ_Maxhinal:'NOT_BOUND'},
  no_origins_authenticated:true,no_real_slices_edited:true,
  no_external_network_or_workers:true,
  no_automatic_method_repair:true,no_evidence_promoted:true
 };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF)
 process.stdout.write(JSON.stringify(experiment(),null,2)+'\n');
