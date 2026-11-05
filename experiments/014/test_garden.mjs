import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {gitBlobSha,verifyDonors,makeCase,runCase,fixtures,evaluateMethod,gardenerExperiment} from './organ_garden.mjs';

test('original National Treasure and Dogram source blobs are exact',()=>{
  const pins = verifyDonors();
  assert.equal(pins.national_treasure,'83574ed0a927fdefe1a53b3ece0960f011b875d0');
  assert.equal(pins.dogram,'c201ce28ff7bb18a28496c0a2eefe2f9451526cc');
  assert.notEqual(gitBlobSha('tampered source'),pins.national_treasure);
});
test('National Treasure first asks for missing source; no Dogram invoked',()=>{
  const r=runCase(makeCase('missing',['a','d'],undefined,{source_locator:''}),'dogram-cost');
  assert.equal(r.status,'HOLD_QUESTION_FRONTIER');
  assert.equal(r.national_treasure_question_receipt.aperture.id,'source-object');
  assert.equal(r.dogram_receipt,null);
  assert.equal(r.declared_cost,0);
});
test('National Treasure demands chronology before discriminator',()=>{
  const r=runCase(makeCase('bad-chronology',['a','d'],undefined,{chronology:''}));
  assert.equal(r.national_treasure_question_receipt.aperture.id,'chronology');
  assert.equal(r.status,'HOLD_QUESTION_FRONTIER');
});
test('uses the actual Question Box receipt rather than inventing a conclusion',()=>{
  const r=runCase(makeCase('saturated',['a','b']),'dogram-minimal');
  const q=r.national_treasure_question_receipt;
  assert.equal(q.schema,'national-treasure.question-receipt/v0');
  assert.equal(q.aperture.id,'discriminator');
  assert.match(q.question,/cheapest discriminating observation/);
  assert.equal(q.evidence.support_confidence,'unsupported');
  assert.equal(Object.hasOwn(q,'answer'),false);
  assert.equal(Object.hasOwn(q,'conclusion'),false);
  assert.equal(r.status,'PROPOSE_SYNTHETIC_ONLY');
});
test('native Dogram computes two incomparable minimal separators',()=>{
  const r=runCase(makeCase('dogram',['a','d']),'dogram-minimal');
  assert.deepEqual(r.dogram_receipt.minimal_separators,['vertical','diagonal']);
  assert.ok(r.dogram_receipt.cover_relations.some(x=>x.join('/')==='joint/vertical'));
  assert.deepEqual(r.chosen_probes,['diagonal']);
  assert.equal(r.declared_cost,2);
  assert.equal(r.dogram_receipt.authority,'none');
});
test('fixed baseline wastes a probe on training cases',()=>{
  const {train}=fixtures();
  const fixed=evaluateMethod('fixed',train);
  const min=evaluateMethod('dogram-minimal',train);
  assert.equal(fixed.cost_total,8);
  assert.equal(min.cost_total,4);
  assert.equal(min.regret_total,0);
});
test('the attractive minimal separator approach fails an unseen cheap-joint counterexample',()=>{
  const c=makeCase('hostile',['a','d'],{coarse:1,vertical:4,diagonal:4,joint:1});
  const min=runCase(c,'dogram-minimal');
  const optimum=runCase(c,'dogram-cost');
  assert.equal(min.declared_cost,4);
  assert.equal(optimum.declared_cost,1);
  assert.deepEqual(optimum.chosen_probes,['joint']);
});
test('retain failures; do not declare an untested policy a better intelligence',()=>{
  const x=gardenerExperiment();
  assert.equal(x.missing_source_hold.status,'HOLD_QUESTION_FRONTIER');
  assert.equal(x.missing_source_hold.dogram_was_called,false);
  assert.equal(x.candidate_amendments[0].disposition,'REFUSE_HOLDOUT_REGRET');
  assert.ok(x.candidate_amendments[0].heldout.regret_total>0);
  assert.equal(x.candidate_amendments[1].disposition,'HOLD_FOR_HUMAN_REVIEW');
  assert.equal(x.candidate_amendments[1].heldout.regret_total,0);
  assert.equal(x.candidate_amendments[1].automatic_install,false);
  assert.equal(x.no_external_calls,true);
});
test('invalid and unsafe inputs fail before invoking any organ',()=>{
  assert.throws(()=>runCase(makeCase('x',['a','a'])) ,/HOLD_INVALID/);
  assert.throws(()=>runCase(makeCase('x',['a','d'],{coarse:-1,vertical:2,diagonal:2,joint:6})),/HOLD_INVALID/);
  assert.throws(()=>runCase(makeCase('x',['a','d']),'untrusted-execute'),/HOLD_UNKNOWN/);
  const r=runCase(makeCase('x',['a','d']));
  assert.equal(r.dispatched,false);
  assert.equal(r.authority,'none');
});
