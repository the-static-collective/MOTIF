import test from 'node:test';
import assert from 'node:assert/strict';
import {
 scenarioFamily,prepareMethodCartridges,recordedFeedback,
 generationCandidates,judgeGrammar,classicalPosteriorPolicy,
 proposeMetaprocedure,chooseMetaMethod,gradeFuture,validateMetaCartridge,
 metaExperiment
} from './meta_gardener.mjs';

let memo;
function full(){
  if(!memo){
    const parents=prepareMethodCartridges();
    const training=recordedFeedback(scenarioFamily('training'),parents);
    const validation=recordedFeedback(scenarioFamily('validation',24),parents);
    const proposal=proposeMetaprocedure(training,validation);
    memo={parents,training,validation,proposal};
  }
  return memo;
}

test('real exact original Question Box and Dogram survive inheritance from 014/015',()=>{
  const x=full();
  assert.equal(x.parents.expected.question_receipt.schema,
    'national-treasure.question-receipt/v0');
  assert.equal(x.parents.robust.dogram_receipt.schema,
    'motif014.dogram-native-probe-receipt/v0');
  assert.equal(x.proposal.question_receipt.aperture.id,'discriminator');
  assert.equal(x.proposal.question_receipt.evidence.support_confidence,'unsupported');
  assert.equal(Object.hasOwn(x.proposal.question_receipt,'answer'),false);
  assert.equal(Object.hasOwn(x.proposal.question_receipt,'conclusion'),false);
});
test('development failure contains BOTH kinds of disagreement',()=>{
  const x=full();
  const f=x.proposal.observed_reason;
  assert.ok(f.expected_method_regressions>0);
  assert.ok(f.robust_method_regressions>0);
  assert.equal(f.both_failed_across_different_episodes,true);
});
test('the method-builder grammar extends from constants to a generated conditional',()=>{
  const x=full().proposal;
  assert.equal(x.old_grammar,'CONST(method)');
  assert.equal(x.new_method.op,'IF_COUNT_AT_LEAST');
  assert.ok(x.new_method.threshold>=0&&x.new_method.threshold<=17);
  assert.notEqual(x.new_method.then,x.new_method.else);
  assert.equal(x.candidate_count,generationCandidates().extended.length);
  assert.ok(x.training.gain>0.05);
  assert.ok(x.validation.gain>0.05);
  assert.equal(x.status,'HOLD_FOR_HUMAN_REVIEW');
  assert.equal(x.automatic_install,false);
});
test('revised compiler policy improves on both fixed constant controls on heldout mix',()=>{
  const {parents,proposal}=full();
  const evaluated=gradeFuture(scenarioFamily('holdout'),parents,proposal);
  assert.equal(evaluated.proposed_count,evaluated.evaluated_trials);
  assert.ok(evaluated.mean_proposed_cost<evaluated.mean_fixed_expected_cost);
  assert.ok(evaluated.mean_proposed_cost<evaluated.mean_fixed_robust_cost);
  assert.ok(evaluated.mean_proposed_cost>=evaluated.mean_privileged_oracle_cost);
  assert.ok(Number.isFinite(evaluated.mean_classical_posterior_cost));
});
test('strong classical posterior baseline is shown rather than suppressed',()=>{
  const x=full();
  const examples=scenarioFamily('holdout');
  const choices=examples.map(t=>classicalPosteriorPolicy(t.observed));
  assert.ok(choices.includes('expected'));
  assert.ok(choices.includes('robust'));
  const e=gradeFuture(examples,x.parents,x.proposal);
  assert.ok(Number.isFinite(e.mean_classical_posterior_cost));
  assert.ok(Number.isFinite(e.mean_proposed_cost));
});
test('unseen hostile inverted sensor causes HOLD; no false robustness claim',()=>{
  const x=full(), bad=scenarioFamily('hostile',12);
  const e=gradeFuture(bad,x.parents,x.proposal);
  assert.equal(e.proposed_count,0);
  assert.equal(e.hold_count,12);
  assert.ok(e.rows.every(r=>r.selection===null && r.status==='HOLD'));
});
test('undisclosed inverted sensor can fool this method: no universal self-repair claim',()=>{
  const {parents,proposal}=full();
  const result=gradeFuture(scenarioFamily('stealth',24),parents,proposal);
  assert.equal(result.proposed_count,24);
  assert.equal(result.hold_count,0);
  assert.ok(result.mean_proposed_cost>result.mean_fixed_robust_cost+0.10);
});
test('missing or tampered sensor information cannot be passed as permission to guess',()=>{
  const x=full();
  const o=scenarioFamily('holdout',6)[0].observed;
  assert.ok(['expected','robust'].includes(chooseMetaMethod(x.proposal,o)));
  assert.throws(()=>chooseMetaMethod(x.proposal,{...o,a_count:-1}),/UNTRUSTED/);
  assert.throws(()=>chooseMetaMethod(x.proposal,{...o,a_count:9.2}),/UNTRUSTED/);
  assert.throws(()=>chooseMetaMethod(x.proposal,{...o,noise_warning:'KNOWN_SENSOR_FAILURE'}),/UNTRUSTED/);
  assert.throws(()=>chooseMetaMethod(x.proposal,{...o,source:'EXTERNAL_DATA'}),/UNTRUSTED/);
});
test('tampering with meta instructions or training performance is rejected',()=>{
  const x=full().proposal;
  validateMetaCartridge(x);
  assert.throws(()=>validateMetaCartridge({...x,training:{...x.training,gain:1e6}}),
    /TAMPERED/);
  assert.throws(()=>validateMetaCartridge({...x,automatic_install:true}),/INVALID/);
});
test('questioner cannot read sealed evaluator world through its observable argument',()=>{
  const x=full();
  const o=scenarioFamily('holdout',6)[0].observed;
  const trap={...o};
  Object.defineProperty(trap,'evaluator_only',{get(){throw Error('ORACLE_LEAK');}});
  const result=chooseMetaMethod(x.proposal,trap);
  assert.ok(['expected','robust'].includes(result));
});
test('no bidirectional error evidence means no invented metaprocedure',()=>{
  const x=full();
  const expectedDominates=x.training.map(row=>({
    ...row,audited_result:{expected:1,robust:9}
  }));
  const out=proposeMetaprocedure(expectedDominates,x.validation);
  assert.equal(out.status,'HOLD_NO_BIDIRECTIONAL_FAILURE_EVIDENCE');
  assert.equal(out.new_method,null);
  assert.equal(out.automatic_install,false);
});
test('no train/validation leakage through episode identity',()=>{
  const x=full();
  assert.throws(()=>proposeMetaprocedure(x.training,x.training),/OVERLAP/);
  const bad=x.training.map((row,i)=>i===1?{
    ...row,observation:x.training[0].observation
  }:row);
  assert.throws(()=>proposeMetaprocedure(bad,x.validation),/DUPLICATE/);
});
test('study is reproducible and records limitations, sources, and holdout failures',()=>{
  const r=metaExperiment();
  assert.equal(r.meta_revision.status,'HOLD_FOR_HUMAN_REVIEW');
  assert.equal(r.frozen_holdout.evaluated_trials,36);
  assert.equal(r.hostile_inverted_report.proposed_count,0);
  assert.ok(r.unflagged_inverted_report.mean_proposed_cost>
    r.unflagged_inverted_report.mean_fixed_robust_cost);
  assert.equal(r.no_production_mutation,true);
  assert.equal(r.no_autonomous_code_editing,true);
  assert.equal(r.no_recursive_intelligence_gain_claim,true);
});
