import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {designInstrument,conditionalPosterior} from './instrument_garden.mjs';

const seed=()=>JSON.parse(readFileSync(fileURLToPath(
  new URL('seeded_minecraft.json',import.meta.url)),'utf8'));
const run=q=>designInstrument(q);

test('instrument invented from held two-world evidence is a new B at -13 measurement',()=>{
  const d=run(seed());
  assert.equal(d.status,'PROPOSE_NEW_INSTRUMENT');
  assert.equal(d.selected.target.world,'B');
  assert.equal(d.selected.target.fault_x,-13);
  assert.equal(d.selected.target.threshold,4);
  assert.equal(d.selected.expected_information_bits>0.7,true);
  assert.equal(d.first_seeded_composition,
    'relatte.minecraft.redstone-hypothesis-garden/v0');
  assert.equal(d.real_game_execution,false);
  assert.equal(d.source_history_disposition,'HOLD');
  assert.equal(d.permission,'PROPOSE_ONLY');
});

test('instrument is not a redundant read of previously observed world data',()=>{
  const d=run(seed());
  assert.ok(!seed().observed.some(o=>
    o.world===d.selected.target.world&&o.fault_x===d.selected.target.fault_x));
  assert.ok(d.candidates.every(x=>x.independent_game_witness_required));
});

test('expensive instrument is not forced by curiosity',()=>{
  const q=seed();q.budget=0;
  const d=run(q);
  assert.equal(d.status,'HOLD');
  assert.equal(d.reason,'NO_AFFORDABLE_DISCRIMINATING_MEASUREMENT');
});

test('explicit cost of doing nothing changes decision when measurement is marginal',()=>{
  const q=seed();q.value_per_bit=0;q.cost_of_inaction=0;
  const a=run(q);assert.equal(a.status,'HOLD');
  q.cost_of_inaction=5;
  const b=run(q);assert.equal(b.status,'PROPOSE_NEW_INSTRUMENT');
});

test('no differentiating observation means HOLD even with huge inaction cost',()=>{
  const q=seed();q.cost_of_inaction=1e6;
  q.hypotheses[1].predictions['B:-13']=3;
  q.hypotheses[1].predictions['A:-28']=2;
  const d=run(q);
  assert.equal(d.status,'HOLD');
});

test('replaying a previously observed condition is rejected as new evidence',()=>{
  const q=seed();q.targets[0].world='A';
  assert.throws(()=>run(q),/ALREADY_OBSERVED_TARGET/);
});

test('archival evidence contradicted by a seed hypothesis is refused',()=>{
  const q=seed();q.hypotheses[1].predictions['A:-13']=5;
  assert.throws(()=>run(q),/RIVAL_DISAGREES_WITH_ARCHIVED_OBSERVATION/);
});

test('a forged decision cannot be smuggled in via fake source authority',()=>{
  for (const patch of [
    {classification:'unsigned-overview'},
    {disposition:'ADMIT'},
    {owner_admitted:true},
  ]) {
    const q=seed();Object.assign(q.source,patch);
    assert.throws(()=>run(q),/UNVERIFIED_SOURCE|SOURCE_AUTHORITY_ESCALATED/);
  }
});

test('unbounded action coordinates and impossible sensor reliability refuse',()=>{
  const q=seed();q.targets[0].fault_x=100;
  assert.throws(()=>run(q),/BAD_TARGET/);
  const q2=seed();q2.targets[0].reliability=2;
  assert.throws(()=>run(q2),/BAD_TARGET_COST_OR_RELIABILITY/);
});

test('posterior change is conditional and never claims game execution',()=>{
  const q=seed(),d=run(q);
  const low=conditionalPosterior(d,q.hypotheses,3);
  const high=conditionalPosterior(d,q.hypotheses,4);
  assert.ok(low.posterior[0].posterior>0.9);
  assert.ok(high.posterior[1].posterior>0.9);
  assert.equal(low.observation_verified,false);
  assert.equal(high.authority,'NONE');
  assert.equal(high.admission,'NONE');
});

test('previously authenticated result cannot be replaced by a fabricated data row',()=>{
  const q=seed();q.observed[0].lit_count=9;
  assert.throws(()=>run(q),/RIVAL_DISAGREES_WITH_ARCHIVED_OBSERVATION/);
});

test('unreviewed operator mode cannot silently authorize real Minecraft mutation',()=>{
  const q=seed();q.operator_permission='EXECUTE_NOW';
  assert.throws(()=>run(q),/PERMISSION/);
});
