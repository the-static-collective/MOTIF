import test from 'node:test';
import assert from 'node:assert/strict';
import {
 exampleWorld,reliability,posterior,batchRisk,batchOptimum,
 sequentialOptimum,questionDesk,propose,checkCartridge,
 syntheticTrial,observe,demonstration
} from './question_machine.mjs';

let cached;
const desk=()=>cached??(cached=questionDesk());
test('original National Treasure Question Box and Dogram native math execute',()=>{
 const d=desk();
 assert.equal(d.question_receipt.schema,'national-treasure.question-receipt/v0');
 assert.equal(d.question_receipt.aperture.id,'discriminator');
 assert.equal(d.dogram_receipt.schema,'motif014.dogram-native-probe-receipt/v0');
 assert.equal(d.dogram_receipt.source_blob,
  'c201ce28ff7bb18a28496c0a2eefe2f9451526cc');
 assert.equal(Object.hasOwn(d.question_receipt,'answer'),false);
});
test('original National Treasure missing-source question holds before Dogram',()=>{
 const d=questionDesk({source_locator:''});
 assert.equal(d.question_receipt.aperture.id,'source-object');
 assert.equal(d.dogram_receipt,null);
 const p=propose(exampleWorld(),d);
 assert.equal(p.status,'HOLD_NATIONAL_TREASURE_FRONTIER');
 assert.equal(p.proposed_questions.length,0);
});
test('two cheap independent questions are worthwhile together',()=>{
 const w=exampleWorld('pair'),o=batchOptimum(w);
 assert.deepEqual(o.ids,['a','b']);
 assert.deepEqual(o.origins,['family_a','family_b']);
 assert.ok(o.predicted_total_risk<o.risk_if_stop);
 const c=propose(w,desk());
 assert.equal(c.status,'PROPOSE_SIMULTANEOUS_SYNTHETIC_QUESTIONS');
 assert.equal(c.proposed_questions.length,2);
 assert.equal(c.admission,'HUMAN_REVIEW_REQUIRED');
 assert.equal(c.no_external_action,true);
 checkCartridge(c);
});
test('high-confidence solo measurement is sufficient, expensive weak extra is not',()=>{
 const c=propose(exampleWorld('solo'),desk());
 assert.equal(c.status,'PROPOSE_SIMULTANEOUS_SYNTHETIC_QUESTIONS');
 assert.deepEqual(c.proposed_questions.map(x=>x.source_id),['accurate']);
});
test('expensive and forwarded-copy questions produce HOLD rather than waste',()=>{
 for(const family of ['expensive','copies']){
   const c=propose(exampleWorld(family),desk());
   assert.equal(c.status,'HOLD_INSUFFICIENT_EVIDENCE');
   assert.deepEqual(c.proposed_questions,[]);
 }
 assert.equal(batchOptimum(exampleWorld('copies')).candidate_count,3);
});
test('an independently calibrated contrarian can provide useful inverted signal',()=>{
 const w=exampleWorld('anti'),r=reliability(w.sources[0]);
 assert.ok(r<0.5);
 assert.ok(posterior(0.5,r,'robust')>0.5);
 const c=propose(w,desk());
 assert.deepEqual(c.proposed_questions.map(x=>x.source_id),['contrarian']);
});
test('two agreeing synthetic witnesses suggest review, not autonomous method adoption',()=>{
 const w=exampleWorld('pair'),trials=[
  {schema:'motif017.synthetic-report/v0',id:'a',origin:'family_a',claim:'expected',synthetic_only:true},
  {schema:'motif017.synthetic-report/v0',id:'b',origin:'family_b',claim:'expected',synthetic_only:true}
 ];
 const c=propose(w,desk(),trials);
 assert.equal(c.status,'HOLD_METHOD_REVIEW');
 assert.equal(c.candidate_method,'PROPOSE_EXPECTED');
 assert.equal(c.automatically_revised,false);
});
test('independent disagreeing witnesses do not fabricate confidence',()=>{
 const w=exampleWorld('pair'),history=[
  {schema:'motif017.synthetic-report/v0',id:'a',origin:'family_a',claim:'expected',synthetic_only:true},
  {schema:'motif017.synthetic-report/v0',id:'b',origin:'family_b',claim:'robust',synthetic_only:true}
 ];
 const c=propose(w,desk(),history);
 assert.equal(c.status,'HOLD_INSUFFICIENT_EVIDENCE');
 assert.ok(Math.abs(c.posterior_expected_method-0.5)<1e-12);
});
test('forwarded duplicates count once; conflicting same-origin copies HOLD',()=>{
 const w=exampleWorld('copies'),d=desk();
 const a={schema:'motif017.synthetic-report/v0',id:'a',origin:'shared',
   claim:'expected',synthetic_only:true};
 const b={...a,id:'forwarded'};
 const one=propose(w,d,[a]),duplicate=propose(w,d,[a,b]);
 assert.equal(one.posterior_expected_method,duplicate.posterior_expected_method);
 assert.equal(propose(w,d,[a,{...b,claim:'robust'}]).status,
   'HOLD_CONFLICTING_COPIES');
});
test('exact classical sequential Bayesian baseline dominates one-round batch optimum',()=>{
 for(const name of ['pair','solo','expensive','copies','anti']){
   const w=exampleWorld(name),b=batchOptimum(w);
   assert.ok(sequentialOptimum(w)<=b.predicted_total_risk+1e-9,name);
 }
});
test('unadjudicated calibration cannot be silently promoted to reliability',()=>{
 assert.throws(()=>propose(exampleWorld('untrusted'),desk()),/UNAUDITED/);
 const w=exampleWorld();
 w.sources[0].calibration.total=0;
 assert.throws(()=>batchOptimum(w),/UNAUDITED/);
});
test('hidden simulated evaluator truth is not read when selecting questions',()=>{
 const trial=syntheticTrial('expected','stable',713);
 const w={...trial.public_descriptor};
 Object.defineProperty(w,'evaluator_only',{get(){throw Error('LEAK_OF_HIDDEN_TRUTH');}});
 const p=propose(w,desk());
 assert.equal(p.status,'PROPOSE_SIMULTANEOUS_SYNTHETIC_QUESTIONS');
});
test('unannounced inversion may fool posterior: evidence is not an authenticated fact',()=>{
 const world=syntheticTrial('expected','unannounced_inversion',71);
 const w=world.public_descriptor,first=propose(w,desk());
 const reports=observe(world,first.proposed_questions.map(q=>q.source_id),71);
 const follow=propose(w,desk(),reports);
 assert.equal(follow.admission,'HUMAN_REVIEW_REQUIRED');
 assert.equal(follow.identity_authenticated,false);
 assert.equal(follow.automatically_revised,false);
});
test('malformed external reports, invalid costs, altered method cartridge are refused',()=>{
 const w=exampleWorld(),d=desk();
 const forged={schema:'motif017.synthetic-report/v0',id:'a',origin:'family_a',
   claim:'expected',synthetic_only:false};
 assert.throws(()=>propose(w,d,[forged]),/UNKNOWN_REPORT/);
 const over=exampleWorld();over.budget=Infinity;
 assert.throws(()=>propose(over,d),/INVALID_OR_UNAUDITED/);
 const c=propose(w,d);
 assert.throws(()=>checkCartridge({...c,posterior_expected_method:0.999}),/TAMPERED/);
 assert.throws(()=>checkCartridge({...c,automatically_revised:true}),/BAD_CARTRIDGE/);
});
test('study retains negative cases, native parent lineage and never acts externally',()=>{
 const r=demonstration();
 assert.equal(r.scenarios.pair.questions.length,2);
 assert.equal(r.scenarios.copies.questions.length,0);
 assert.equal(r.national_treasure_gap.aperture,'source-object');
 assert.equal(r.genuine_organs.question_box,'national-treasure.question-receipt/v0');
 assert.equal(r.external_effects,0);
 assert.equal(r.autonomous_edits,false);
 assert.equal(r.real_world_witnesses,0);
});
