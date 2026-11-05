/* MOTIF-021 — observational learning *after* a separate reLATTE source
 * verifier has authenticated original game bytes, signatures and witnesses.
 * This pure interpreter does NOT verify signatures and is not a source of
 * permission, a storage organ or a substitute for an independent verifier.
 */
import {designInstrument,conditionalPosterior} from '../020/instrument_garden.mjs';

const req=(x,why)=>{if(!x)throw Error('MOTIF_021_'+why)};
const isID=x=>typeof x==='string'&&x.startsWith('relatte-crossing-v0:')&&
  /^[a-f0-9]{64}$/.test(x.slice('relatte-crossing-v0:'.length));

export function interpretVerifiedMinecraftReturn(seed,receipt) {
  req(seed?.schema==='motif.instrument-garden/v0','SEED_SCHEMA');
  req(receipt?.schema==='relatte.motif-minecraft-009-independent-return/v0' &&
    receipt.original_two_world_history_verified===true &&
    receipt.new_game_result_p256_signature_verified===true &&
    receipt.raw_blockstates_recomputed===true &&
    receipt.separate_fresh_nonop_game_witness_in_source_runner===true &&
    receipt.official_minecraft_version==='26.1.1' &&
    receipt.world==='B'&&receipt.fault_x===-13 &&
    Number.isInteger(receipt.observed_fault_lit_count) &&
    receipt.observed_fault_lit_count>=0&&receipt.observed_fault_lit_count<=9 &&
    receipt.disposition==='HOLD'&&receipt.owner_admission===false &&
    receipt.physical_environment_effect===false &&
    isID(receipt.new_game_crossing) &&
    isID(receipt.new_instrument_crossing),
    'UNSUPPORTED_OR_UNVERIFIED_RETURN_FORMAT');
  req(receipt.source_original_005_crossing===seed.source.source_ids[1],
    'WRONG_SIGNED_ANCESTOR');
  // This evaluator trusts *only the context* of a prior reLATTE verification;
  // the receipt body itself is not cryptographic evidence until the caller
  // has independently reverified its originating packet.
  const original=designInstrument(seed);
  req(original.status==='PROPOSE_NEW_INSTRUMENT'&&
    original.selected.target.world===receipt.world&&
    original.selected.target.fault_x===receipt.fault_x,
    'DIFFERENT_SELECTED_INSTRUMENT');
  const selected=original.selected;
  req(JSON.stringify(receipt.rival_seed_predictions)===
    JSON.stringify(selected.predictions),'RIVAL_PREDICTIONS_SUBSTITUTED');
  const lit=receipt.observed_fault_lit_count;
  const predictions=Object.fromEntries(seed.hypotheses.map(h=>[
    h.id,h.predictions[receipt.world+':'+receipt.fault_x],
  ]));
  const counts=new Set(Object.values(predictions));
  const outside=!counts.has(lit);
  const base={
    schema:'motif021.minecraft-instrument-interpretation/v0',
    interpretation_not_authentication:true,
    game_evidence_claimed_by_verified_relatte_receipt:receipt.new_game_crossing,
    previous_instrument:receipt.new_instrument_crossing,
    source_005:receipt.source_original_005_crossing,
    world:receipt.world,fault_x:receipt.fault_x,
    measured_lamps:lit,threshold:selected.target.threshold,
    initial_forecasts:predictions,
    class:lit>=selected.target.threshold?'GE_4':'LT_4',
    historical_evidence_changed:false,
    stored_to_understory:false,
    automatic_world_actions:0,
    admitted_authority:false,
  };
  if(outside) return {
    ...base,
    status:'HOLD_OUT_OF_MODEL_OBSERVATION',
    posterior:null,next_measurement:null,
    next_question:'Which assumed causal relation or sensor property is missing from both seeded models?',
    reason:'The observed total differs from every exact seeded forecast. Binary threshold alone cannot justify a posterior or a claim of explanation.',
  };
  const posterior=conditionalPosterior(original,seed.hypotheses,lit);
  // Avoid selecting the same instrument twice. Soft likelihoods preserve
  // rival models as uncertain, even when one predicted count is disfavored.
  const nextInput={
    ...seed,
    hypotheses:seed.hypotheses.map(h=>({
      ...h,
      prior:posterior.posterior.find(x=>x.id===h.id).posterior,
    })),
    targets:seed.targets.filter(x=>!(x.world===receipt.world &&
      x.fault_x===receipt.fault_x)),
  };
  const next=designInstrument(nextInput);
  return {
    ...base,
    status:'RECEIPT_INTERPRETED_NOT_PROMOTED',
    posterior,
    next_measurement:next,
    best_provisional_model:posterior.posterior.reduce(
      (a,b)=>a.posterior>=b.posterior?a:b).id,
    question_if_hold:next.status==='HOLD' ?
      'What cheaper new test or additional budget could distinguish these remaining hypotheses without reusing an observed result?' : null,
    reason:'Posterior depends on seeded priors and assumed measurement reliability, not a theorem of the real game.',
  };
}
