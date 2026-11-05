import test from 'node:test';
import assert from 'node:assert/strict';
import {
  verifyPinnedMaxhinal,buildHypothesisGas,compileJob,runMaxhinal,
  validateRide,challengeTheRide,replayBranch,hypothesisQuestionBundle,experiment
} from './madd_custody.mjs';
import {
  simulate,investigate,questionGate,proposedDiscriminators
} from '../019/common_ancestor.mjs';

const gate=questionGate();
const receipts=new Map();
const input=kind=>{
 if(!receipts.has(kind)){
  const sample=simulate(kind,643);
  receipts.set(kind,investigate(sample.records,gate));
 }
 return receipts.get(kind);
};

test('imports three byte-for-byte source-pinned original Maxhinal engines',()=>{
 const proof=verifyPinnedMaxhinal();
 assert.equal(proof.origin_repository,'the-static-collective/the-daily-slice');
 assert.equal(proof.exact_git_blobs['maxhinal-core.js'],
  '302ad18bfbb4bf03368bd859c3ba7d0dd3a2b684');
 assert.equal(proof.exact_git_blobs['maxhinal-chambers.js'],
  '97fbc799836c2f4dfe379bc26a5b14b9ff3348eb');
 assert.equal(proof.exact_git_blobs['maxhinal-modes.js'],
  '0e62e21e802d727373ae7c19b421dde52b495f0b');
 assert.equal(proof.source_authenticity,
  'CONTENT_PIN_ONLY_REQUIRES_SOURCE_OWNER_REVIEW');
});
test('019 input comes from native original National Treasure and Dogram crossing',()=>{
 assert.equal(gate.question_receipt.schema,
  'national-treasure.question-receipt/v0');
 assert.equal(gate.dogram_receipt.schema,
  'motif014.dogram-native-probe-receipt/v0');
 const receipt=input('hidden_ancestor');
 assert.equal(receipt.status,'HOLD_FOR_SOURCE_GENEALOGY_REVIEW');
 assert.ok(receipt.statistically_suspected_shared_failure_links.length>0);
 assert.equal(receipt.real_reference_independence_authenticated,false);
});
test('the Maxhinal consumes synthetic hypothesis gas, never original Slice files',()=>{
 const gas=buildHypothesisGas(input('hidden_ancestor'));
 assert.equal(gas.meta.format,'motif020.synthetic-hypothesis-gas/v0');
 assert.equal(gas.meta.record_count,4);
 assert.equal(gas.meta.source_type,'MOTIF019_TEST_FIXTURE_NOT_DAILY_SLICE');
 assert.ok(gas.meta.digest.startsWith('sha256:'));
 assert.deepEqual(gas.records.map(x=>x.id),
  ['hyp-carrier','hyp-difficulty','hyp-reference','hyp-independent']);
 assert.ok(gas.records.every(x=>x.evidence_status==='HYPOTHESIS_NOT_ADMITTED'));
 assert.ok(gas.records.every(x=>x.origin_receipt_checksum===
  input('hidden_ancestor').checksum_sha256));
});
test('real Maxhinal fiber preserves all text-compatible competing explanations',()=>{
 const {gas,ride}=runMaxhinal(input('hidden_ancestor'));
 const selected=ride.outputs.find(x=>x.mode==='fiber');
 assert.equal(selected.status,'OK');
 assert.equal(selected.value.posture,'FIBER_NOT_REPRESENTATIVE');
 assert.deepEqual(selected.value.compatible_refs,
  ['hyp-carrier','hyp-difficulty','hyp-reference','hyp-independent']);
 assert.equal(selected.value.representative,null);
 assert.equal(ride.authority,'none');
 assert.equal(ride.promotion,'NONE');
 validateRide(gas,ride);
});
test('original moving-origin chamber changes the cut without rewriting the source',()=>{
 const {ride,gas}=runMaxhinal(input('hidden_ancestor'));
 const origin=ride.outputs.find(x=>x.mode==='moving-origin');
 assert.equal(origin.value.origin_ref,'hyp-carrier');
 assert.equal(origin.value.before.length,0);
 assert.equal(origin.value.after.length,3);
 assert.equal(origin.value.posture,'NEW_CURRENT_NOT_OLD_CURRENT_REWRITTEN');
 assert.deepEqual(gas.records.map(x=>x.date),
  ['2026-08-30','2026-08-31','2026-09-01','2026-09-02']);
});
test('actual Pressure and MADDCL0WN chambers produce counterquestions only',()=>{
 const {ride}=runMaxhinal(input('hidden_ancestor'));
 const pressure=ride.outputs.filter(x=>x.mode==='pressure');
 assert.equal(pressure.length,2);
 assert.ok(pressure.some(x=>
  /attributable road or carrier/i.test(x.value.question)));
 assert.ok(pressure.some(x=>
  /causal influence from temporal or thematic adjacency/i.test(x.value.question)));
 assert.ok(pressure.every(x=>x.value.promotion==='NONE'));
 const clown=ride.outputs.find(x=>x.mode==='maddclown');
 assert.ok(clown);
 assert.equal(clown.value.promotion,'NONE');
 assert.ok(clown.value.overlap_tokens.includes('shared'));
 assert.equal(typeof clown.value.pressure_question,'string');
 const braid=ride.outputs.find(x=>x.mode==='walk-braid');
 assert.equal(braid.value.commuting_diagnostic,
  'ORDER_MAY_MATTER_BY_DECLARED_MODEL');
});
test('an original discontinuity chamber yields bounded creative pressure, not factual evidence',()=>{
 const {ride}=runMaxhinal(input('hidden_ancestor'));
 const projection=ride.outputs.find(x=>x.mode==='discontinuity').value;
 assert.equal(projection.verdict,'unresolved');
 assert.ok(['haiku','banger','law'].includes(projection.creative.kind));
 assert.equal(typeof projection.pressure_question,'string');
 assert.equal(ride.operations.length,8);
 assert.ok(ride.operations.every(x=>x.receipt.authority==='none'&&
  x.receipt.promotion==='NONE'));
});
test('deterministic seed gives identical ride and corpus, across independent executions',()=>{
 const sample=input('hidden_ancestor');
 const left=runMaxhinal(sample,'main','seed-proof');
 const right=runMaxhinal(sample,'main','seed-proof');
 assert.deepEqual(left.ride,right.ride);
 assert.deepEqual(left.gas,right.gas);
 assert.equal(left.ride.seed,'seed-proof');
 assert.equal(left.ride.created_at,null);
 assert.equal(left.ride.replay.status,'EXACT');
});
test('two experimental orderings are different while source gas remains fixed',()=>{
 const sample=input('hidden_ancestor');
 const left=runMaxhinal(sample,'main','order-compare');
 const right=runMaxhinal(sample,'alternate','order-compare');
 assert.deepEqual(left.gas,right.gas);
 assert.equal(left.ride.corpus.digest,right.ride.corpus.digest);
 assert.notDeepEqual(left.ride.operations.map(x=>x.mode),
  right.ride.operations.map(x=>x.mode));
 assert.equal(left.ride.authority,'none');
 assert.equal(right.ride.authority,'none');
 assert.ok(left.ride.outputs.some(x=>x.mode==='pressure'));
 assert.ok(right.ride.outputs.some(x=>x.mode==='pressure'));
});
test('rejected spin is appended without deleting a generated output',()=>{
 const {ride,gas}=runMaxhinal(input('hidden_ancestor'));
 const first=ride.outputs[0].output_id;
 const challenged=challengeTheRide(ride,first);
 assert.equal(challenged.outputs.length,ride.outputs.length);
 assert.equal(challenged.operations.length,ride.operations.length);
 assert.equal(challenged.bad_spins.length,ride.bad_spins.length+1);
 assert.equal(challenged.bad_spins.at(-1).output_ref,first);
 assert.equal(challenged.bad_spins.at(-1).kind,'epistemic-counterpressure');
 assert.deepEqual(challenged.outputs,ride.outputs);
 assert.deepEqual(ride.bad_spins,[]);
 validateRide(gas,challenged);
});
test('original Maxhinal serializes and resumes a held ride without rewriting history',()=>{
 const {ride,gas}=runMaxhinal(input('hidden_ancestor'));
 const challenged=challengeTheRide(ride,ride.outputs[0].output_id);
 const before=structuredClone(challenged);
 const next=replayBranch(gas,challenged,'alternate','attempted-new-seed');
 assert.equal(next.operations.length,16);
 assert.deepEqual(next.operations.slice(0,8),before.operations);
 assert.deepEqual(next.outputs.slice(0,ride.outputs.length),before.outputs);
 assert.equal(next.bad_spins.length,1);
 assert.equal(next.seed,challenged.seed);
 assert.equal(next.corpus.digest,challenged.corpus.digest);
 assert.equal(next.replay.status,'EXACT');
 assert.deepEqual(before,challenged);
});
test('a drifted corpus cannot masquerade as the same ride',()=>{
 const {ride,gas}=runMaxhinal(input('hidden_ancestor'));
 const mismatched=structuredClone(gas);
 mismatched.meta.digest='sha256:wrong-corpus';
 assert.throws(()=>validateRide(mismatched,ride),/RIDE_CONTRACT/);
});
test('source-custody question bundle preserves 019 questions and original chamber pressures',()=>{
 const receipt=input('hidden_ancestor');
 const {ride}=runMaxhinal(receipt);
 const bundle=hypothesisQuestionBundle(receipt,ride);
 assert.equal(bundle.materialized_evidence,false);
 assert.equal(bundle.automatically_executed_probes,0);
 assert.ok(bundle.projected_original_maxhinal_pressures.length===2);
 assert.ok(bundle.motif019_independent_tests.some(x=>
  x.kind==='PROPOSE_THIRD_INDEPENDENT_REFERENCE_FAMILY'));
 assert.ok(bundle.motif019_independent_tests.some(x=>
  x.kind==='PROPOSE_ORIGINAL_CARRIER_PROVENANCE_REVIEW'));
 assert.equal(bundle.required_next_action,
  'RECOVER_REAL_ORIGINAL_CUSTODY_BEFORE_GENEALOGY_PROMOTION');
});
test('three regimes generate text-compatible hypotheses; resemblance is not identification',()=>{
 const worlds=['hidden_ancestor','shared_difficulty','reference_collusion'];
 const fibers=worlds.map(world=>{
  const {ride}=runMaxhinal(input(world));
  return ride.outputs.find(x=>x.mode==='fiber').value.compatible_refs;
 });
 assert.deepEqual(fibers[0],fibers[1]);
 assert.deepEqual(fibers[1],fibers[2]);
 assert.ok(input('shared_difficulty').statistically_suspected_shared_failure_links.length>0);
 assert.ok(input('reference_collusion').statistically_suspected_shared_failure_links.length>0);
});
test('content tampering, missing 019 receipt and unauthorized program/seed cause HOLD',()=>{
 const receipt=input('hidden_ancestor');
 assert.throws(()=>buildHypothesisGas(null),/NO_MOTIF019_RECEIPT/);
 assert.throws(()=>buildHypothesisGas({...receipt,sample_count:0}),
  /TAMPERED/);
 assert.throws(()=>compileJob('enable-github-write'),/UNAUTHORIZED_GRAFT_PROGRAM/);
 assert.throws(()=>compileJob('main','a'.repeat(81)),/UNAUTHORIZED_SEED/);
 const {ride}=runMaxhinal(receipt);
 assert.throws(()=>challengeTheRide(ride,'out-9999'),/UNKNOWN_DERIVED_OUTPUT/);
});
test('graft study is a real read-only ride, with no upstream mutation or proof inflation',()=>{
 const r=experiment();
 assert.equal(r.status,'SYNTHETIC_READ_ONLY_SOURCE_CUSTODY_EXPERIMENT');
 assert.equal(Object.keys(r.regimes).length,3);
 assert.ok(r.regimes.hidden_ancestor.main_ride.operations.length===8);
 assert.ok(r.regimes.hidden_ancestor.main_ride.bad_spins.length===1);
 assert.equal(r.regimes.hidden_ancestor.continuation.operations,16);
 assert.equal(r.regimes.hidden_ancestor.continuation.replay_status,'EXACT');
 assert.equal(r.regimes.hidden_ancestor.corpus_drift_not_silently_rebound,true);
 assert.deepEqual(r.regimes.hidden_ancestor.maxhinal_fiber_compatible_refs,
  ['hyp-carrier','hyp-difficulty','hyp-reference','hyp-independent']);
 assert.equal(r.additional_external_modules.ALEX,'NOT_BOUND');
 assert.equal(r.additional_external_modules.GRAFT,'NOT_BOUND');
 assert.equal(r.no_origins_authenticated,true);
 assert.equal(r.no_evidence_promoted,true);
 assert.equal(r.no_external_network_or_workers,true);
 assert.equal(r.no_automatic_method_repair,true);
});
