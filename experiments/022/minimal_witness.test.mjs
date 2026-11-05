import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {designInstrument} from '../020/instrument_garden.mjs';
import {forgeMinimalWitness} from './minimal_witness.mjs';

const seed=()=>JSON.parse(readFileSync(fileURLToPath(
  new URL('../020/seeded_minecraft.json',import.meta.url)),'utf8'));
const receipt=()=>{
  const s=seed();
  return {
    schema:'relatte.motif-minecraft-009-independent-return/v0',
    original_two_world_history_verified:true,
    new_game_result_p256_signature_verified:true,
    raw_blockstates_recomputed:true,
    separate_fresh_nonop_game_witness_in_source_runner:true,
    official_minecraft_version:'26.1.1',
    source_original_005_crossing:s.source.source_ids[1],
    new_game_crossing:'relatte-crossing-v0:'+'a'.repeat(64),
    new_instrument_crossing:'relatte-crossing-v0:'+'b'.repeat(64),
    world:'B',fault_x:-13,disposition:'HOLD',owner_admission:false,
    physical_environment_effect:false,
    observed_fault_lit_count:3,
    rival_seed_predictions:designInstrument(s).selected.predictions,
  };
};
const trace=()=>({states:{fault:{server:Array.from({length:9},(_,i)=>({
  cue:'synthetic-stage-'+i,lit:i<3,
}))}}});
const forge=(options={})=>forgeMinimalWitness(seed(),receipt(),trace(),options);

test('CRATER: from 3/9 verified game consequence, invent two-lamp World A next experiment',()=>{
  const m=forge();
  assert.equal(m.status,'PROPOSE_MINIMAL_CAUSAL_WITNESS');
  assert.equal(m.selected.world,'A');
  assert.equal(m.selected.fault_x,-28);
  assert.equal(m.selected.discriminator,-20);
  assert.equal(m.selected.discriminatory_stage_index,2);
  assert.deepEqual(m.selected.minimal_witness_stage_indexes,[2,3]);
  assert.equal(m.selected.predictions['position-invariant-prefix'].predicted_discriminator_lit,false);
  assert.equal(m.selected.predictions['world-local-hidden-relay'].predicted_discriminator_lit,true);
  assert.equal(m.selected.compressed_read_count,2);
  assert.equal(m.selected.parent_full_census_lamps,9);
  assert.equal(m.selected.full_nine_lamp_server_and_fresh_nonop_audit_required,true);
  assert.equal(m.selected.estimated_cost_units<4,true);
  assert.equal(m.selected.legacy_full_instrument_cost_units>4,true);
  assert.equal(m.actions,0);
});

test('The new candidate is not recycling previously witnessed A or B fault',()=>{
  const s=seed(),m=forge();
  assert.ok(s.observed.every(x=>x.world!==m.selected.world||x.fault_x!==m.selected.fault_x));
  assert.notEqual(m.selected.fault_x,-13);
});

test('No evidence of prefix form: refuse to compress observation',()=>{
  const t=trace();
  t.states.fault.server[6].lit=true;
  assert.throws(()=>forgeMinimalWitness(seed(),receipt(),t),
    /INSTRUMENT_PREFIX_INVARIANT_NOT_OBSERVED/);
});

test('Without verified game source context, refuse compression',()=>{
  const r=receipt();r.new_game_result_p256_signature_verified=false;
  assert.throws(()=>forgeMinimalWitness(seed(),r,trace()),
    /UNVERIFIED_009_CONTEXT/);
});

test('No invented reward if even the cheaper witness exceeds budget',()=>{
  const m=forge({currentBudget:.1});
  assert.equal(m.status,'HOLD_NO_VALID_BUDGETED_MICRO_INSTRUMENT');
  assert.equal(m.selected,null);
});

test('Uninformative rival agreement: do not pretend to have found a discriminator',()=>{
  const s=seed();
  s.hypotheses[1].predictions['A:-28']=2;
  const m=forgeMinimalWitness(s,receipt(),trace());
  assert.equal(m.status,'HOLD_NO_VALID_BUDGETED_MICRO_INSTRUMENT');
  assert.equal(m.proposals.length,0);
});

test('Action cost and measurement reliability remain assumptions and affect selection',()=>{
  const low=forge({reliability:.51});
  assert.equal(low.status,'HOLD_NO_VALID_BUDGETED_MICRO_INSTRUMENT');
  const big=forge({worldSetupCost:10});
  assert.equal(big.status,'HOLD_NO_VALID_BUDGETED_MICRO_INSTRUMENT');
  const high=forge({reliability:1});
  assert.equal(high.status,'PROPOSE_MINIMAL_CAUSAL_WITNESS');
});

test('Never allow exactly same past 009 observation to masquerade as novel',()=>{
  const m=forge({permittedTargets:['B:-13']});
  assert.equal(m.status,'HOLD_NO_VALID_BUDGETED_MICRO_INSTRUMENT');
});

test('Source claims do not grant external authority or establish truth',()=>{
  const m=forge();
  assert.equal(m.no_external_autonomous_actuation,true);
  assert.equal(m.full_nine_lamp_recheck_may_refute_prefix_assumption,true);
  assert.equal(m.reliability_is_seeded_not_calibrated,.95);
  assert.equal(m.dispositions,'R3_HOLD');
  assert.equal(m.cost_units_are_hypotheses_not_measured_walltime,true);
});
