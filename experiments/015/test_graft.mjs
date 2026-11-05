import test from 'node:test';
import assert from 'node:assert/strict';
import {knownWorld,synthesize,validateCartridge,classicalOptimum,
  executeProgram,score,worldFamilies,experiment} from './invented_graft.mjs';

test('the existing original Question Box and Dogram both run and remain pinned',()=>{
  const x=synthesize(knownWorld(),'expected');
  assert.equal(x.question_receipt.aperture.id,'discriminator');
  assert.match(x.question_receipt.question,/cheapest discriminating observation/);
  assert.equal(x.dogram_receipt.schema,'motif014.dogram-native-probe-receipt/v0');
  assert.equal(x.dogram_receipt.source_blob,'c201ce28ff7bb18a28496c0a2eefe2f9451526cc');
  assert.equal(Object.hasOwn(x.question_receipt,'answer'),false);
  assert.equal(Object.hasOwn(x.question_receipt,'conclusion'),false);
});
test('a missing recoverable source gets a real National Treasure HOLD',()=>{
  const x=synthesize(knownWorld({clue_overrides:{source_locator:''}}));
  assert.equal(x.status,'HOLD_QUESTION_EVIDENCE_GAP');
  assert.equal(x.question_receipt.aperture.id,'source-object');
  assert.equal(x.program,null);
  assert.equal(x.issued_probes,0);
});
test('generator makes branching procedure not one of three named 014 policies',()=>{
  const w=knownWorld();
  const x=synthesize(w);
  assert.ok(x.generation.candidate_count>2);
  assert.equal(x.origin,'BOUNDED_GRAMMAR_ENUMERATION');
  assert.equal(x.method.op,'ASK');
  assert.equal(x.method.probe,'spot');
  assert.equal(x.method.by.a.op,'STOP');
  assert.equal(x.method.by.other.op,'ASK');
  for(let i=0;i<w.states.length;i++)
    assert.equal(executeProgram(x.method,w,i).label,w.labels[i]);
  assert.ok(x.expected_cost<x.one_shot_baseline.cost);
  assert.equal(x.automatically_admitted,false);
});
test('matches independent exact dynamic-programming optimal known-model baseline',()=>{
  const w=knownWorld();
  const x=synthesize(w,'expected');
  const y=synthesize(w,'worst');
  assert.ok(Math.abs(x.expected_cost-classicalOptimum(w,'expected'))<1e-9);
  assert.ok(Math.abs(y.worst_cost-classicalOptimum(w,'worst'))<1e-9);
  assert.ok(y.worst_cost<=x.worst_cost);
  assert.ok(x.expected_cost<=y.expected_cost);
});
test('a new XOR family has no single lawful question but gets a composite',()=>{
  const w=worldFamilies().xor;
  const x=synthesize(w);
  assert.equal(x.one_shot_baseline,null);
  assert.equal(x.expected_cost,4);
  assert.equal(x.classical_dynamic_programming_optimum,4);
  assert.equal(x.method.op,'ASK');
  for(let i=0;i<w.states.length;i++){
    assert.equal(executeProgram(x.method,w,i).label,w.labels[i]);
    assert.equal(executeProgram(x.method,w,i).probes.length,2);
  }
});
test('unknown non-permitted probes cannot be added by imagination',()=>{
  const x=synthesize(worldFamilies().prohibited);
  assert.ok(['HOLD_NO_INITIAL_SEPARATOR','HOLD_NO_LAWFUL_COMPOSITION'].includes(x.status));
  assert.equal(x.program,null);
  assert.equal(x.issued_probes,0);
});
test('expected-cost gain can FAIL to transfer under a frozen distribution shift',()=>{
  const {train,shifted}=worldFamilies();
  const x=synthesize(train,'expected');
  const y=synthesize(train,'worst');
  const old=score(x.method,shifted).mean_cost;
  const robust=score(y.method,shifted).mean_cost;
  const fresh=classicalOptimum(shifted,'expected');
  assert.ok(old>fresh);
  assert.ok(old>robust);
  assert.ok(x.expected_cost<y.expected_cost);
});
test('no unchecked model modifications or promotions',()=>{
  const x=synthesize(knownWorld());
  validateCartridge(x);
  assert.throws(()=>validateCartridge({...x,expected_cost:1}),/TAMPERED/);
  assert.throws(()=>validateCartridge({...x,automatically_admitted:true}),/INVALID/);
  const study=experiment();
  assert.equal(study.agent_ticket.model_execution_verified,false);
  assert.equal(study.no_real_actions,true);
  assert.equal(study.no_claim_recursive_self_improvement,true);
  assert.equal(study.holdout.withheld_permission.program,null);
  assert.equal(study.meta_question.approved,false);
});
test('reject untrusted scope, non-probabilities, unavailable origins and objectives',()=>{
  const bad=knownWorld();
  bad.scope='UNKNOWN_REAL_WORLD';
  assert.throws(()=>synthesize(bad),/INVALID_SYNTHETIC/);
  const p=knownWorld();
  p.prior=[1,0,0,0];
  assert.throws(()=>synthesize(p),/INVALID_SYNTHETIC/);
  assert.throws(()=>synthesize(knownWorld(),'reward-hack'),/UNKNOWN_OBJECTIVE/);
  const c=knownWorld();
  c.allowed.push('remote-shell');
  assert.throws(()=>synthesize(c),/INVALID_SYNTHETIC/);
});
