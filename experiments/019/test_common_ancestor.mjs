import test from 'node:test';
import assert from 'node:assert/strict';
import {
  simulate,fisherUpperTail,questionGate,investigate,
  validateReceipt,proposedDiscriminators,study
} from './common_ancestor.mjs';

let memo;
const gate=()=>memo??(memo=questionGate());
const run=(kind,seed=643)=>investigate(simulate(kind,seed).records,gate());
const links=x=>x.statistically_suspected_shared_failure_links;
const cedarElm=x=>links(x).find(l=>l.a==='cedar'&&l.b==='elm');

test('actual source-pinned National Treasure Question Box and Dogram execute',()=>{
 const d=gate();
 assert.equal(d.question_receipt.schema,'national-treasure.question-receipt/v0');
 assert.equal(d.question_receipt.aperture.id,'discriminator');
 assert.equal(d.dogram_receipt.schema,'motif014.dogram-native-probe-receipt/v0');
 assert.equal(d.dogram_receipt.source_blob,'c201ce28ff7bb18a28496c0a2eefe2f9451526cc');
 assert.equal(Object.hasOwn(d.question_receipt,'answer'),false);
 assert.equal(Object.hasOwn(d.question_receipt,'conclusion'),false);
 assert.equal(d.no_external_actions,true);
});
test('National Treasure missing-source aperture holds before native Dogram',()=>{
 const d=questionGate({source_locator:''});
 assert.equal(d.question_receipt.aperture.id,'source-object');
 assert.equal(d.dogram_receipt,null);
 const x=investigate(simulate('independent',643).records,d);
 assert.equal(x.status,'HOLD_SOURCE_QUESTION_FIRST');
 assert.equal(x.math_invoked,false);
});
test('exact one-sided Fisher test is sensitive to positive error association',()=>{
 const strong=fisherUpperTail(45,2,2,45);
 const nullish=fisherUpperTail(25,25,25,25);
 assert.ok(strong<1e-12);
 assert.ok(nullish>0.1);
 assert.equal(fisherUpperTail(0,0,0,4),1);
 assert.throws(()=>fisherUpperTail(1,-1,0,5),/BAD_CONTINGENCY/);
});
test('conditional on truth, independent sources are not spuriously merged',()=>{
 const r=run('independent');
 assert.equal(r.status,'HOLD_FOR_SOURCE_GENEALOGY_REVIEW');
 assert.equal(links(r).length,0);
 assert.equal(r.conservative_group_count,6);
 assert.equal(r.audit.predeclared_tests,30);
 assert.equal(r.audit.alpha_familywise,0.05);
 assert.equal(r.no_independence_certified_from_non_significance,true);
 validateReceipt(r);
});
test('latent common ancestor generates conditional shared-error evidence, not proof',()=>{
 const r=run('hidden_ancestor');
 assert.equal(r.raw_reporter_count,6);
 assert.ok(cedarElm(r));
 assert.equal(r.conservative_group_count,5);
 assert.equal(r.declared_same_carrier_links.length,0);
 assert.equal(r.no_causal_ancestry_identification_from_observational_dependence,true);
 assert.ok(cedarElm(r).min_adjusted_p<0.05);
});
test('a known declared forwarded carrier is deduplicated, original source remains a claim',()=>{
 const r=run('declared_copy');
 assert.equal(r.forwarded_duplicate_count,900);
 assert.ok(r.declared_same_carrier_links.some(e=>e.a==='cedar'&&e.b==='elm'));
 assert.equal(r.conservative_group_count,5);
 assert.equal(r.real_reference_independence_authenticated,false);
});
test('an independent world shift changes raw agreement but not conditional error dependence',()=>{
 const r=run('world_shift');
 assert.equal(r.sample_count,1200);
 assert.ok(r.reference_label_counts.yes>1000);
 assert.equal(links(r).length,0);
 assert.equal(r.conservative_group_count,6);
});
test('shared difficulty can mimic common genealogy with no literal ancestor',()=>{
 const fixture=simulate('shared_difficulty',643);
 assert.equal(fixture.evaluator_only.shared_literal_parent,false);
 assert.equal(fixture.evaluator_only.common_item_difficulty_not_literal_lineage,true);
 const r=investigate(fixture.records,gate());
 assert.ok(links(r).length>0);
 assert.ok(r.conservative_group_count<6);
 assert.equal(r.no_causal_ancestry_identification_from_observational_dependence,true);
});
test('jointly corrupted reference feeds can produce false ancestry suspicions',()=>{
 const fixture=simulate('reference_collusion',643);
 assert.equal(fixture.evaluator_only.shared_literal_parent,false);
 assert.equal(fixture.evaluator_only.reference_common_mode_corruption,true);
 const r=investigate(fixture.records,gate());
 assert.ok(links(r).length>0);
 assert.equal(r.audit.reference_labels_assumed_correct_NOT_VERIFIED,true);
 assert.equal(r.no_evidence_promoted_to_truth,true);
});
test('weak or rare links may escape detection and cannot be called independent',()=>{
 const r=run('weak_ancestor');
 assert.equal(r.status,'HOLD_FOR_SOURCE_GENEALOGY_REVIEW');
 assert.equal(r.no_independence_certified_from_non_significance,true);
 assert.equal(r.no_causal_ancestry_identification_from_observational_dependence,true);
});
test('missing or conflicting synthetic reference families cause HOLD',()=>{
 assert.throws(()=>run('missing_reference'),/INVALID_OR_INCOMPLETE/);
 assert.throws(()=>run('conflicting_reference'),/REFERENCE_WITNESSES_DISAGREE/);
 const fake=simulate('independent',643).records;
 fake[0].references[1].family='reference_alpha';
 assert.throws(()=>investigate(fake,gate()),/UNAUTHENTICATED_REFERENCE_ORIGIN/);
});
test('very sparse reference stratum cannot be treated as failed independence test',()=>{
 const r=run('small_sample');
 assert.equal(r.status,'HOLD_UNDERPOWERED_REFERENCE_STRATUM');
 assert.equal(r.minimum_per_label,45);
 assert.equal(r.no_external_actions,true);
});
test('identical copies and contradictory copies cannot manufacture independent testimony',()=>{
 const f=simulate('declared_copy',643);
 const r=investigate(f.records,gate());
 assert.equal(r.forwarded_duplicate_count,900);
 const firstElm=f.records.find(x=>x.reporter==='elm');
 const divergent={...firstElm,carrier_claim:firstElm.carrier_claim==='yes'?'no':'yes',
  forwarded_copy_id:'fraud'};
 assert.throws(()=>investigate([...f.records,divergent],gate()),
  /CONTRADICTORY_SAME_ORIGIN_COPY/);
});
test('declared source parent assertion must match actual panels',()=>{
 const f=simulate('declared_copy',643);
 const changed=f.records.map(x=>x.reporter==='elm'?{
    ...x,carrier_claim:x.carrier_claim==='yes'?'no':'yes'}:x);
 assert.throws(()=>investigate(changed,gate()),/DECLARED_COPY_DOES_NOT_MATCH_SOURCE/);
});
test('claiming different parent metadata on one origin triggers explicit HOLD',()=>{
 const f=simulate('declared_copy',643);
 const changed=f.records.map(x=>x.reporter==='elm'&&x.sample_id==='specimen-00001'
   ?{...x,declared_parent:null}:x);
 assert.throws(()=>investigate(changed,gate()),
  /SOURCE_PARENT_CHANGED_WITHOUT_RECEIPT|CONTRADICTORY_SAME_ORIGIN_COPY/);
});
test('source-graph proposal asks for discriminating original provenance, not automatic action',()=>{
 const r=run('hidden_ancestor');
 const p=proposedDiscriminators(r,1.5);
 assert.equal(p.status,'PROPOSE_SYNTHETIC_DISCRIMINATORS');
 assert.ok(p.actions.some(x=>x.kind==='PROPOSE_ORIGINAL_CARRIER_PROVENANCE_REVIEW'));
 assert.ok(p.actions.some(x=>x.kind==='PROPOSE_THIRD_INDEPENDENT_REFERENCE_FAMILY'));
 assert.ok(p.spent<=1.5);
 assert.equal(p.human_review_required,true);
 assert.equal(p.evidence_admitted,false);
 assert.equal(p.no_real_probes_executed,true);
 assert.equal(proposedDiscriminators(r,0.1).status,'HOLD_BUDGET');
});
test('unknown source, claim scope, sample label and altered checksum refuse',()=>{
 const f=simulate('independent',643);
 const edits=f.records.map((r,i)=>i===0?{...r,source_scope:'REAL_EXTERNAL'}:r);
 assert.throws(()=>investigate(edits,gate()),/INVALID_OR_INCOMPLETE/);
 const c=f.records.map((r,i)=>i===0?{...r,reporter:'nobody'}:r);
 assert.throws(()=>investigate(c,gate()),/INVALID_OR_INCOMPLETE/);
 const r=run('hidden_ancestor');
 assert.throws(()=>validateReceipt({...r,conservative_group_count:1}),
   /TAMPERED/);
 assert.throws(()=>validateReceipt({...r,no_upstream_mutations:false}),
   /INVALID/);
});
test('simulator hidden genealogy cannot enter the public observation path',()=>{
 const sim=simulate('hidden_ancestor',643);
 const prop={...sim};
 Object.defineProperty(prop,'evaluator_only',{get(){throw Error('ORACLE_LEAK');}});
 const r=investigate(prop.records,gate());
 assert.ok(cedarElm(r));
});
test('multi-seed controlled comparison preserves false positives, source-collusion failure',()=>{
 const r=study();
 assert.equal(r.status,'EXPERIMENTAL_UNADMITTED_SYNTHETIC_STUDY');
 assert.equal(r.preregistered_seed_sweep.independent.trials,12);
 assert.equal(r.preregistered_seed_sweep.hidden_ancestor.trials,12);
 assert.ok(r.preregistered_seed_sweep.hidden_ancestor.cedar_elm_flag_trials>
   r.preregistered_seed_sweep.independent.cedar_elm_flag_trials);
 assert.ok(r.preregistered_seed_sweep.reference_collusion.any_flag_trials>0);
 assert.ok(r.preregistered_seed_sweep.shared_difficulty.any_flag_trials>0);
 assert.equal(r.actual_source_owners_modified,false);
 assert.equal(r.source_authentication_performed,false);
 assert.equal(r.real_world_actions,0);
});
