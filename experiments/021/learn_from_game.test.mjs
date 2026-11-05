import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {designInstrument} from '../020/instrument_garden.mjs';
import {interpretVerifiedMinecraftReturn} from './learn_from_game.mjs';

const seed=()=>JSON.parse(readFileSync(fileURLToPath(
  new URL('../020/seeded_minecraft.json',import.meta.url)),'utf8'));
const receipt=(n=3)=>{
  const input=seed(),selected=designInstrument(input).selected;
  return {
    schema:'relatte.motif-minecraft-009-independent-return/v0',
    original_two_world_history_verified:true,
    new_game_result_p256_signature_verified:true,
    raw_blockstates_recomputed:true,
    separate_fresh_nonop_game_witness_in_source_runner:true,
    official_minecraft_version:'26.1.1',
    source_original_005_crossing:input.source.source_ids[1],
    new_game_crossing:'relatte-crossing-v0:'+'a'.repeat(64),
    new_instrument_crossing:'relatte-crossing-v0:'+'b'.repeat(64),
    world:'B',fault_x:-13,
    rival_seed_predictions:selected.predictions,
    observed_fault_lit_count:n,
    disposition:'HOLD',owner_admission:false,
    physical_environment_effect:false,
  };
};

test('021: three observed lamps disfavors hidden-relay while preserving HOLD',()=>{
  const r=interpretVerifiedMinecraftReturn(seed(),receipt(3));
  assert.equal(r.status,'RECEIPT_INTERPRETED_NOT_PROMOTED');
  assert.equal(r.measured_lamps,3);
  assert.equal(r.best_provisional_model,'position-invariant-prefix');
  assert.ok(r.posterior.posterior.find(x=>x.id==='position-invariant-prefix').posterior>0.9);
  assert.equal(r.next_measurement.status,'HOLD');
  assert.equal(r.automatic_world_actions,0);
  assert.equal(r.stored_to_understory,false);
  assert.equal(r.interpretation_not_authentication,true);
});

test('021: four observed lamps favors rival model with same update code',()=>{
  const r=interpretVerifiedMinecraftReturn(seed(),receipt(4));
  assert.equal(r.class,'GE_4');
  assert.equal(r.best_provisional_model,'world-local-hidden-relay');
  assert.ok(r.posterior.posterior.find(x=>x.id==='world-local-hidden-relay').posterior>0.9);
  assert.equal(r.next_measurement.status,'HOLD');
});

test('021: out-of-model result opens an unknown rather than falsifying it away',()=>{
  const r=interpretVerifiedMinecraftReturn(seed(),receipt(7));
  assert.equal(r.status,'HOLD_OUT_OF_MODEL_OBSERVATION');
  assert.equal(r.posterior,null);
  assert.equal(r.next_measurement,null);
  assert.match(r.next_question,/missing/);
});

test('021: cannot reuse the just-observed probe as new information',()=>{
  const r=interpretVerifiedMinecraftReturn(seed(),receipt(3));
  assert.ok(r.next_measurement.candidates.every(
    x=>x.target.world!=='B'||x.target.fault_x!==-13));
});

test('021: bad original ancestor, operator admission, or forged game flag refused',()=>{
  const patches=[
    {source_original_005_crossing:'relatte-crossing-v0:'+'c'.repeat(64)},
    {owner_admission:true},
    {new_game_result_p256_signature_verified:false},
    {disposition:'ADMIT'},
    {physical_environment_effect:true},
    {world:'A'},
  ];
  for(const patch of patches)
    assert.throws(()=>interpretVerifiedMinecraftReturn(seed(),{
      ...receipt(3),...patch,
    }),/MOTIF_021_/);
});

test('021: synthetic test fixtures are not a substitute for upstream cryptographic verification',()=>{
  const r=interpretVerifiedMinecraftReturn(seed(),receipt(3));
  assert.equal(r.interpretation_not_authentication,true);
  assert.equal(r.admitted_authority,false);
  assert.equal(r.historical_evidence_changed,false);
});
