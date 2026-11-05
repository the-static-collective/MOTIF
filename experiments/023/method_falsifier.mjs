/* MOTIF-023: Adversarial method falsification.
 * Deliberately ask for a game-only intervention that should make a
 * previously observed prefix-rule *possibly* fail.
 * No authenticated source claim: caller must reverify signed 010 bytes.
 * No execution permission or permanent MEMENTO mutation.
 */
export const SCHEMA='motif023.method-falsifier/v0';
const f=(b,x)=>{if(!b)throw Error('MOTIF_023_'+x)};
const slots=Array.from({length:9},(_,i)=>({index:i,x:-40+i*10,y:65,z:46}));
const isPrefix=(bits)=>bits.every((v,i)=>v===(i<bits.filter(Boolean).length));
export function proposeFalsification(verified010,game010, {
  approved_game_targets=[6], experimental_cost_budget=3,
}={}) {
  f(verified010?.schema==='relatte.minecraft-010-independent-game-return/v0'&&
    verified010.source_signatures_verified===true &&
    verified010.source_004_005_008_009_chain_verification===true &&
    verified010.actual_lamps_lit===2 &&
    verified010.micro_sensor_inferred_count===2 &&
    verified010.result_status==='GAME_MICRO_INSTRUMENT_CONFIRMED_BY_NINE_LAMP_AUDIT' &&
    verified010.source_009_crossing?.startsWith('relatte-crossing-v0:') &&
    verified010.signed_game_crossing?.startsWith('relatte-crossing-v0:') &&
    verified010.disposition==='R3_HOLD' && verified010.owner_admission===false,
    'UNVERIFIED_PRIOR_GAME_METHOD');
  const prior=game010?.states?.fault?.server?.map(x=>x.lit);
  f(prior?.length===9 && prior.every(x=>typeof x==='boolean') &&
    isPrefix(prior) && prior.filter(Boolean).length===2,
    'PRIOR_PREFIX_NOT_OBSERVED');
  f(Array.isArray(approved_game_targets)&&
    approved_game_targets.length>=1&&approved_game_targets.length<=3 &&
    approved_game_targets.every(x=>Number.isInteger(x)&&x>=5&&x<=7) &&
    Number.isFinite(experimental_cost_budget)&&experimental_cost_budget>=0,
    'UNBOUNDED_GAME_TARGET');
  const possible=approved_game_targets.map(index=>{
    const stage=slots[index];
    const cost=2.1+.2*Math.abs(index-6);
    return {
      method:'bounded-lateral-redstone-power',
      stage_index:index, stage,
      source_block:{x:stage.x,y:65,z:47,block:'minecraft:redstone_block'},
      prior_stage_lit:prior[index],
      predicted_under_simple_lamp_adjacency:true,
      // This is a conjecture about game mechanics, not an observation.
      original_micro_indexes:[2,3],
      falsification_pattern_expected:'micro-read-still-2-but-nonprefix-nine-lamp-census',
      cost_units:cost,
      game_only:true,
    };
  }).sort((a,b)=>a.cost_units-b.cost_units||a.stage_index-b.stage_index);
  const best=possible.find(x=>x.cost_units<=experimental_cost_budget);
  return {
    schema:SCHEMA,
    status:best?'PROPOSE_HOSTILE_GAME_FOR_METHOD':'HOLD_NO_BUDGETED_COUNTEREXAMPLE',
    selected:best??null,
    candidate_tests:possible,
    parent_game:verified010.signed_game_crossing,
    source_method:'MOTIF-022 two-lamp primary sensor, prefix assumption',
    question:'Can a lateral redstone source break the prefix while the two sampled lamps remain unchanged?',
    original_prefix_bits:prior,
    precommitted_failure_criterion:'full-nine-lamp-nonprefix-even-if-original-micro-inference-looks-correct',
    must_record_actual_outcome_even_if_hypothesis_survives:true,
    independent_game_client_and_full_audit_required:true,
    permission:'SYNTHETIC_GAME_PROPOSAL_ONLY',
    automatic_execution:false,
    signed_receipt_disposition:'R3_HOLD',
  };
}

export function diagnoseMethod(verified011,trace011) {
  f(verified011?.schema==='relatte.minecraft-011-independent-return/v0'&&
    verified011.all_source_signatures_verified===true&&
    verified011.game_world==='A'&&verified011.fault_x===-28 &&
    verified011.nonoperator_nine_lamp_agreement===true&&
    verified011.disposition==='R3_HOLD'&&
    verified011.game_011_crossing?.startsWith('relatte-crossing-v0:'),
    'NOT_INDEPENDENTLY_VERIFIED');
  const bits=trace011?.states?.fault?.server?.map(x=>x.lit);
  f(bits?.length===9&&bits.every(x=>typeof x==='boolean'),
    'MISSING_COMPLETE_011_BLOCKSTATES');
  const micro=trace011?.micro_readout?.stages;
  f(micro?.length===2&&micro[0].index===2&&micro[1].index===3&&
    micro.every(x=>x.lit===bits[x.index]),'MICRO_NOT_BOUND_TO_RAW_GAME');
  const prefix=isPrefix(bits),baseline=[true,true,false,false,false,false,false,false,false];
  const anomalies=bits.map((lit,i)=>({lit,i})).filter(x=>x.lit!==baseline[x.i]);
  if(prefix)return {
    schema:'motif023.method-revision/v0',
    status:'HOLD_FALSIFIER_DID_NOT_BREAK_METHOD',
    original_method_still_provisional:true,
    source_crossing:verified011.game_011_crossing,
    next_question:'What independent bounded intervention would break the prefix assumption?',
    new_probe:null,permission:'NONE',external_actions:0,
  };
  const newlyLit=anomalies.filter(x=>x.lit&&x.i>3);
  if(!newlyLit.length)return {
    schema:'motif023.method-revision/v0',
    status:'HOLD_NONPREFIX_WITHOUT_LOCALIZABLE_SIDE_ISLAND',
    source_crossing:verified011.game_011_crossing,
    new_probe:null,permission:'NONE',external_actions:0,
  };
  const island=newlyLit[0].i;
  // Select from observed actual *counterexample*: not a predeclared
  // universal sensor. New-stage choice must be tested in another world run.
  return {
    schema:'motif023.method-revision/v0',
    status:'PROPOSE_REVISED_THREE_STAGE_GAME_PROBE',
    source_crossing:verified011.game_011_crossing,
    old_probe_indexes:[2,3],
    new_probe_indexes:[2,3,island],
    new_probe_positions:[2,3,island].map(i=>slots[i]),
    observed_fault_bits:bits,
    compressed_original_result:micro[0].lit?3:2,
    observed_total:bits.filter(Boolean).length,
    prefix_falsified:!prefix,
    method_diagnostic:'ORIGINAL_TWO_STAGE_PROBE_MISSES_DISCONNECTED_LIT_ISLAND',
    scope:'one-characterized-lateral-island-only',
    expected_generalization:'NONE',
    request_independent_retest_on_new_game_instance:true,
    instruction_if_new_island_moves:'HOLD_REVISE_INSTRUMENT',
    prior_evidence_immutable:true,
    no_external_actions:true,
    external_actions:0,
    permission:'PROPOSE_ONLY',
    disposition:'R3_HOLD',
  };
}
