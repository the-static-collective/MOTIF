import test from 'node:test';
import assert from 'node:assert/strict';
import {
  simulate,evaluateWitnesses,checkReceipt,questionForWitness,auditPlan,study
} from './witness_machine.mjs';

let memo;
function world(kind){return simulate(kind,777).public_records;}
function healthy(kind){return evaluateWitnesses(world(kind),'late');}
function gate(){return memo??(memo=questionForWitness());}

test('the actual National Treasure Question Box and source-pinned native Dogram run',()=>{
 const x=gate();
 assert.equal(x.question_receipt.schema,'national-treasure.question-receipt/v0');
 assert.equal(x.question_receipt.aperture.id,'discriminator');
 assert.equal(x.native_dogram_receipt.schema,
   'motif014.dogram-native-probe-receipt/v0');
 assert.equal(x.native_dogram_receipt.source_blob,
   'c201ce28ff7bb18a28496c0a2eefe2f9451526cc');
 assert.equal(x.action_permitted,false);
 assert.equal(Object.hasOwn(x.question_receipt,'answer'),false);
});
test('a missing original evidence source HOLDs before math and before audits',()=>{
 const x=questionForWitness({source_locator:''});
 assert.equal(x.question_receipt.aperture.id,'source-object');
 assert.equal(x.native_dogram_receipt,null);
 const p=auditPlan([{origin:'north',
  auditor_origin:'synthetic_reference_alpha',impact:5,audit_cost:.2}],1,x);
 assert.equal(p.status,'HOLD_NATIONAL_TREASURE_SOURCE_FRONTIER');
 assert.deepEqual(p.source_audits,[]);
});
test('bounded simultaneous independent-origin synthetic audit questions are proposals only',()=>{
 const p=auditPlan([
  {origin:'north',auditor_origin:'synthetic_reference_alpha',impact:4,audit_cost:.4},
  {origin:'north',auditor_origin:'synthetic_reference_beta',impact:2,audit_cost:.2},
  {origin:'south',auditor_origin:'synthetic_reference_beta',impact:3,audit_cost:.4}
 ],.8,gate());
 assert.equal(p.status,'PROPOSE_SYNTHETIC_AUDIT_QUESTIONS');
 assert.equal(p.source_audits.length,2);
 assert.equal(new Set(p.source_audits.map(x=>x.origin)).size,2);
 assert.equal(p.proposal_only,true);
 assert.equal(p.source_verification_performed,false);
 assert.equal(p.criterion,'DECLARED_IMPACT_PER_COST_HEURISTIC_NOT_OPTIMAL_VOI');
 const p2=auditPlan([
  {origin:'north',auditor_origin:'synthetic_reference_beta',impact:3,audit_cost:.4}
 ],.2,gate());
 assert.equal(p2.status,'HOLD_BUDGET');
});
test('unchanged observed source health does not become a claim of established stability',()=>{
 const r=healthy('stable');
 assert.equal(r.status,'HOLD_FOR_INDEPENDENT_SOURCE_REVIEW');
 assert.deepEqual(r.source_change_flags,[]);
 assert.deepEqual(r.reference_prevalence_flags,[]);
 assert.equal(r.interpretation,'NO_CHANGE_DETECTED_NOT_PROOF_OF_STABILITY');
 assert.equal(r.audit_method.predeclared_tests,8);
 assert.equal(r.audit_method.declared_familywise_alpha,0.05);
 checkReceipt(r);
});
test('an actual truth-prevalence shift is distinguishable from a reporter-accuracy shift on this toy model',()=>{
 const r=healthy('world_shift');
 assert.deepEqual(r.source_change_flags,[]);
 assert.ok(r.reference_prevalence_flags.length>0);
 assert.ok(r.naive_raw_report_prevalence_flags.length>0);
 assert.equal(r.interpretation,
   'REFERENCE_DISTRIBUTION_CHANGED_WITHOUT_DETECTED_REPORTER_DRIFT');
});
test('reporter inversion with unchanged world is detected as a different failure',()=>{
 const r=healthy('witness_flip');
 assert.deepEqual(r.source_change_flags,['north']);
 assert.deepEqual(r.reference_prevalence_flags,[]);
 assert.equal(r.interpretation,
   'REPORTER_ACCURACY_CHANGE_WITNESSED_IN_SYNTHETIC_AUDIT');
 assert.equal(r.admitted_method_change,false);
 assert.equal(r.auto_source_quarantine,false);
});
test('simultaneous world and source shift must remain TWO unresolved hypotheses',()=>{
 const r=healthy('both_shift');
 assert.ok(r.reference_prevalence_flags.length>0);
 assert.deepEqual(r.source_change_flags,['north']);
 assert.equal(r.interpretation,'BOTH_REPORTER_AND_REFERENCE_DISTRIBUTIONS_CHANGED');
});
test('a small change below declared detectable threshold cannot be called stable or definitively detected',()=>{
 const r=healthy('subtle_shift');
 assert.equal(r.status,'HOLD_FOR_INDEPENDENT_SOURCE_REVIEW');
 assert.equal(r.analysis.north.n_baseline,480);
 assert.equal(r.analysis.north.n_recent,320);
 const c=r.analysis.north.accuracy;
 assert.ok(c.declared_detection_threshold>0);
 assert.equal(c.flagged,Math.abs(c.difference)>c.declared_detection_threshold);
});
test('early and later checkpoints use predeclared familywise error budget',()=>{
 const early=evaluateWitnesses(world('witness_flip'),'early');
 const late=evaluateWitnesses(world('witness_flip'),'late');
 assert.equal(early.checkpoint,'early');
 assert.equal(late.checkpoint,'late');
 assert.equal(early.analysis.north.n_recent,80);
 assert.equal(late.analysis.north.n_recent,320);
 assert.ok(early.analysis.north.accuracy.declared_detection_threshold>
           late.analysis.north.accuracy.declared_detection_threshold);
});
test('forwarded copies do not artificially increase evidence strength',()=>{
 const plain=healthy('stable');
 const copied=healthy('forwarded');
 assert.equal(copied.deduplicated_forwarded_copies,880);
 assert.deepEqual(copied.analysis,plain.analysis);
});
test('contradictory copies of same original receipt HOLD',()=>{
 const rows=world('stable').slice();
 const first=rows[0];
 rows.push({...first,reporter:'north_forwarded',reported:
  first.reported==='yes'?'no':'yes'});
 assert.throws(()=>evaluateWitnesses(rows),/CONTRADICTORY_SAME_ORIGIN_COPIES/);
});
test('two reference families that disagree cause HOLD; missing reference also HOLD',()=>{
 assert.throws(()=>healthy('reference_conflict'),/REFERENCE_DISAGREEMENT/);
 assert.throws(()=>healthy('missing_reference'),/INCOMPLETE_INDEPENDENT_REFERENCES/);
});
test('coordinated false references can fool the whole detector',()=>{
 const r=healthy('reference_collusion');
 assert.equal(r.status,'HOLD_FOR_INDEPENDENT_SOURCE_REVIEW');
 assert.ok(r.source_change_flags.includes('north'));
 assert.ok(r.source_change_flags.includes('south'));
 assert.equal(r.independently_authenticated_real_sources,false);
 assert.equal(r.two_reference_agreement_does_not_establish_truth,true);
 // The sealed generator says the reporters did NOT change. The detector cannot
 // see that fact and misattributes the colluding reference shift.
 assert.equal(simulate('reference_collusion',777).evaluator_only.reference_is_colluding,true);
});
test('no sealed simulator world fields are read by the monitoring calculation',()=>{
 const fixture=simulate('world_shift',777);
 const publicOnly={...fixture};
 Object.defineProperty(publicOnly,'evaluator_only',{get(){
  throw Error('HIDDEN_TRUTH_LEAK');}});
 const answer=evaluateWitnesses(publicOnly.public_records);
 assert.ok(answer.reference_prevalence_flags.length>0);
});
test('out of scope evidence, origin impersonation, insufficient source cases and altered checksum refuse',()=>{
 const rows=world('stable');
 assert.throws(()=>evaluateWitnesses(
  rows.map((r,i)=>i===0?{...r,source_scope:'CLAIMED_REAL_WORLD'}:r)
 ),/INVALID_SYNTHETIC/);
 assert.throws(()=>evaluateWitnesses(
  rows.map((r,i)=>i===0?{...r,origin:'synthetic_reference_alpha'}:r)
 ),/INVALID_SYNTHETIC/);
 assert.equal(evaluateWitnesses(rows.slice(0,190)).status,
   'HOLD_NOT_ENOUGH_ADJUDICATED_CASES');
 const r=healthy('stable');
 assert.throws(()=>checkReceipt({...r,interpretation:'CERTAINLY_TRUSTED'}),/TAMPERED/);
});
test('multi-seed stable-versus-shift benchmark preserves limitations and quantitative failures',()=>{
 const r=study();
 assert.equal(r.external_actions,0);
 assert.equal(r.autonomous_method_changes,0);
 assert.equal(r.openmanus_worker_executed,false);
 assert.equal(r.missing_original_source.math_executed,false);
 assert.equal(r.independent_seed_comparison.stable.trials,15);
 assert.equal(r.independent_seed_comparison.witness_flip.trials,15);
 assert.equal(r.independent_seed_comparison.reference_collusion.trials,15);
 assert.ok(r.independent_seed_comparison.witness_flip.source_change_flags>
    r.independent_seed_comparison.stable.source_change_flags);
 assert.ok(r.independent_seed_comparison.reference_collusion.source_change_flags>0);
 assert.equal(r.negative_case.cannot_repair_or_prove_source_trust,true);
});
