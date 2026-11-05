/* MOTIF-022 — MINIMAL CAUSAL WITNESS
 * Research proposition: the full nine-lamp census can be replaced with a
 * smaller, falsifiable discriminating observation under a PARTICULAR
 * prefix-circuit assumption. A complete independent audit still tests the
 * assumption after the measurement.
 *
 * Never call this source authentication: caller must first verify the exact
 * signed reLATTE 009 return with native P256 + raw-game verifier.
 */
import {interpretVerifiedMinecraftReturn} from '../021/learn_from_game.mjs';

export const SCHEMA='motif022.minimum-witness/v0';
const fail=(ok,x)=>{if(!ok)throw Error('MOTIF_022_'+x)};
const entropy=p=>p===0||p===1?0:-p*Math.log2(p)-(1-p)*Math.log2(1-p);
const RANKED_STAGE_X=Object.freeze([-40,-30,-20,-10,0,10,20,30,40]);
const key=t=>t.world+':'+t.fault_x;
const round=x=>Number(x.toFixed(8));

const validPrefix=rows=>Array.isArray(rows)&&rows.length===9 &&
  rows.every((r,i)=>r?.lit===Boolean(i<rows.filter(x=>x.lit).length));

function reducedObservationInformation(p, q, reliability) {
  const predictions=[p,q];
  const priors=predictions.map(x=>x.prior);
  const probabilities=predictions.map(x=>x.binary?reliability:1-reliability);
  const mass=probabilities.reduce((acc,x,i)=>acc+priors[i]*x,0);
  return Math.max(0,entropy(mass)-entropy(reliability));
}

export function forgeMinimalWitness(seed,verifiedReceipt,actualGameTrace,{
  reliability=.95,
  worldSetupCost=1.8,
  eachLampReadCost=.18,
  auditCost=.2,
  sourceCertification='native-relatte-009-p256-verified-by-caller',
}={}) {
  fail(seed?.schema==='motif.instrument-garden/v0','SEED_SCHEMA');
  fail(sourceCertification==='native-relatte-009-p256-verified-by-caller',
    'UNVERIFIED_SOURCE_CONTEXT');
  fail(verifiedReceipt?.schema==='relatte.motif-minecraft-009-independent-return/v0'&&
    verifiedReceipt.new_game_result_p256_signature_verified===true&&
    verifiedReceipt.raw_blockstates_recomputed===true&&
    verifiedReceipt.separate_fresh_nonop_game_witness_in_source_runner===true &&
    verifiedReceipt.observed_fault_lit_count===3,'UNVERIFIED_009_CONTEXT');
  const game=actualGameTrace?.states?.fault?.server;
  fail(validPrefix(game)&&game.filter(x=>x.lit).length===3,
    'INSTRUMENT_PREFIX_INVARIANT_NOT_OBSERVED');
  const interpreted=interpretVerifiedMinecraftReturn(seed,verifiedReceipt);
  fail(interpreted.status==='RECEIPT_INTERPRETED_NOT_PROMOTED'&&
    interpreted.next_measurement?.status==='HOLD','UNEXPECTED_021_STATE');
  fail(Number.isFinite(reliability)&&reliability>0.5&&reliability<=1 &&
    [worldSetupCost,eachLampReadCost,auditCost].every(x=>Number.isFinite(x)&&x>=0),
    'COST_ASSUMPTIONS');
  const posterior=Object.fromEntries(interpreted.posterior.posterior.map(x=>[
    x.id,x.posterior,
  ]));
  const already=new Set([...seed.observed.map(key),
    verifiedReceipt.world+':'+verifiedReceipt.fault_x]);
  const candidates=[];
  for(const t of seed.targets) {
    if(already.has(key(t)))continue;
    const predictions=seed.hypotheses.map(h=>({
      id:h.id,
      prior:posterior[h.id],
      predictedCount:h.predictions[key(t)],
    }));
    if(predictions.length!==2 || predictions.some(p=>
      !Number.isInteger(p.predictedCount)||p.predictedCount<0||p.predictedCount>9))continue;
    for(let i=0;i<9;i++) {
      const binary=predictions.map(p=>({...p,binary:i<p.predictedCount}));
      if(binary[0].binary===binary[1].binary)continue;
      // Sentinel: observe immediately downstream. It does not prove prefix
      // by itself; the full 9-lamp server + fresh-client audit is mandatory.
      const sentinel=Math.min(8,i+1);
      const selectedStages=[...new Set([i,sentinel])];
      const expense=worldSetupCost+selectedStages.length*eachLampReadCost+auditCost;
      const info=reducedObservationInformation(binary[0],binary[1],reliability);
      const inaction=seed.cost_of_inaction;
      const utility=seed.value_per_bit*info-expense+inaction;
      const choice={
        world:t.world,
        world_seed:t.world==='A'?'381654729':'918273645',
        fault_x:t.fault_x,
        fault_position:{x:t.fault_x,y:66,z:46},
        discriminatory_stage_index:i,
        discriminator:RANKED_STAGE_X[i],
        discriminator_position:{x:RANKED_STAGE_X[i],y:65,z:46},
        sentinel_stage_index:sentinel,
        sentinel_position:{x:RANKED_STAGE_X[sentinel],y:65,z:46},
        minimal_witness_stage_indexes:selectedStages,
        parent_full_census_lamps:9,
        compressed_read_count:selectedStages.length,
        estimated_cost_units:round(expense),
        legacy_full_instrument_cost_units:t.cost,
        expected_information_bits:round(info),
        expected_net_value:round(utility),
        predictions:Object.fromEntries(binary.map(p=>[
          p.id,{full_lamp_count:p.predictedCount,
            predicted_discriminator_lit:p.binary},
        ])),
        full_nine_lamp_server_and_fresh_nonop_audit_required:true,
      };
      candidates.push(choice);
    }
  }
  candidates.sort((a,b)=>
    b.expected_net_value-a.expected_net_value||
    b.expected_information_bits-a.expected_information_bits||
    a.estimated_cost_units-b.estimated_cost_units||
    a.world.localeCompare(b.world)||a.fault_x-b.fault_x);
  const good=candidates.filter(x=>x.estimated_cost_units<=seed.budget&&
    x.expected_information_bits>0.000001&&
    x.expected_net_value>-seed.cost_of_inaction);
  if(!good.length)return {
    schema:SCHEMA,status:'HOLD_NO_VALID_BUDGETED_MICRO_INSTRUMENT',
    proposals:candidates,selected:null,
    source_009_verified_game_crossing:verifiedReceipt.new_game_crossing,
    prefix_observed_in_one_world_not_established_universally:true,
    model_confidence_does_not_equal_authority:true,
    actions:0,operator_review_required:true,
  };
  return {
    schema:SCHEMA,
    status:'PROPOSE_MINIMAL_CAUSAL_WITNESS',
    selected:good[0],
    candidates,
    parent_game_crossing:verifiedReceipt.new_game_crossing,
    prior_observed_3_of_9_true:true,
    parent_full_census_bitstates:game.map(x=>Boolean(x.lit)),
    posterior_021:interpreted.posterior.posterior,
    first_seeded_composition:'minecraft.world-A.fault-minus28.two-lamp-witness/v0',
    inaction_cost_units:seed.cost_of_inaction,
    reliability_is_seeded_not_calibrated:reliability,
    cost_units_are_hypotheses_not_measured_walltime:true,
    full_nine_lamp_recheck_may_refute_prefix_assumption:true,
    user_review_required:true,
    game_only:true,
    no_external_autonomous_actuation:true,
    dispositions:'R3_HOLD',
    actions:0,
  };
}
