/* MOTIF-020 Instrument Garden — bounded Bayesian experimental design.
 * This unit chooses a *proposed measurement*, never executes a game action,
 * authenticates source history or grants permission.
 *
 * Hypotheses and likely outcomes are supplied as provisional predictions.
 * A distinct reLATTE verifier must authenticate Minecraft evidence.
 */
export const SCHEMA='motif.instrument-garden/v0';
const assert=(b,x)=>{if(!b)throw Error('INSTRUMENT_GARDEN_'+x);};
const entropy=p=>p<=0||p>=1?0:-p*Math.log2(p)-(1-p)*Math.log2(1-p);
const round=v=>Number(v.toFixed(9));
const allowedX=new Set([-28,-13,2,17,32]);
const addr=t=>t.world+':'+t.fault_x;
const hold=(reason,extras={})=>({
  schema:'motif.instrument-decision/v0',
  status:'HOLD',reason,selected:null,candidates:[],
  real_game_execution:false,external_actions:0,permission:'NONE',
  ...extras,
});
function checkInputs(q) {
  assert(q?.schema===SCHEMA,'SCHEMA');
  assert(q.domain==='minecraft-vanilla-game-only','DOMAIN');
  assert(q.source?.classification==='native-relatte-p256-verified-game-history',
    'UNVERIFIED_SOURCE');
  assert(q.source.disposition==='HOLD'&&q.source.owner_admitted===false,
    'SOURCE_AUTHORITY_ESCALATED');
  assert(Array.isArray(q.source.source_ids)&&q.source.source_ids.length===2&&
    q.source.source_ids.every(x=>typeof x==='string'&&x.length>30),
    'SOURCE_IDS_MISSING');
  assert(Array.isArray(q.hypotheses)&&q.hypotheses.length>=2&&q.hypotheses.length<=12,
    'HYPOTHESES');
  const ids=new Set(q.hypotheses.map(h=>h.id));
  assert(ids.size===q.hypotheses.length&&
    q.hypotheses.every(h=>/^[a-z][a-z0-9-]{1,50}$/.test(h.id)&&
      Number.isFinite(h.prior)&&h.prior>0&&h.prior<1&&
      h.predictions&&typeof h.predictions==='object'),
    'HYPOTHESIS_BODY');
  assert(Math.abs(q.hypotheses.reduce((s,h)=>s+h.prior,0)-1)<1e-8,
    'PRIORS_NOT_NORMALIZED');
  assert(Array.isArray(q.observed)&&q.observed.length>=1&&q.observed.length<=32,
    'OBSERVED_ROWS');
  const observationIds=new Set();
  for(const o of q.observed) {
    assert(['A','B'].includes(o.world)&&allowedX.has(o.fault_x)&&
      Number.isInteger(o.lit_count)&&o.lit_count>=0&&o.lit_count<=9,
      'BAD_OBSERVATION');
    assert(!observationIds.has(addr(o)),'DUPLICATE_OBSERVATION');
    observationIds.add(addr(o));
    assert(q.hypotheses.every(h=>h.predictions[addr(o)]===o.lit_count),
      'RIVAL_DISAGREES_WITH_ARCHIVED_OBSERVATION');
  }
  assert(Array.isArray(q.targets)&&q.targets.length>=1&&q.targets.length<=32,
    'TARGET_LIST');
  const targetIds=new Set();
  for(const t of q.targets) {
    assert(['A','B'].includes(t.world)&&allowedX.has(t.fault_x),'BAD_TARGET');
    assert(!observationIds.has(addr(t)),'ALREADY_OBSERVED_TARGET');
    assert(!targetIds.has(addr(t)),'DUPLICATE_TARGET');
    targetIds.add(addr(t));
    assert(Number.isFinite(t.cost)&&t.cost>=0&&t.cost<=1e6&&
      Number.isFinite(t.latency)&&t.latency>=0&&t.latency<=1e4 &&
      Number.isFinite(t.reliability)&&t.reliability>0.5&&t.reliability<=1,
      'BAD_TARGET_COST_OR_RELIABILITY');
    assert(q.hypotheses.every(h=>Number.isInteger(h.predictions[addr(t)])&&
      h.predictions[addr(t)]>=0&&h.predictions[addr(t)]<=9),
      'MISSING_RIVAL_PREDICTION');
  }
  assert(Number.isFinite(q.budget)&&q.budget>=0&&
    Number.isFinite(q.cost_of_inaction)&&q.cost_of_inaction>=0&&
    Number.isFinite(q.value_per_bit)&&q.value_per_bit>=0&&
    Number.isFinite(q.latency_penalty)&&q.latency_penalty>=0,
    'BAD_BUDGET');
  assert(q.operator_permission==='PROPOSE_ONLY','PERMISSION');
}

function candidates(q) {
  const options=[];
  for(const target of q.targets) {
    const pos=addr(target);
    const values=[...new Set(q.hypotheses.map(h=>h.predictions[pos]))].sort((a,b)=>a-b);
    // An instrument consists of a real new observation and a decoder:
    // count the in-game redstone lamps, then discriminate at a chosen cutoff.
    // Replays are intentionally not new instruments.
    for(const threshold of values.slice(1)) {
      const bins=q.hypotheses.map(h=>{
        const prediction=h.predictions[pos]>=threshold;
        return prediction?target.reliability:1-target.reliability;
      });
      const mass=q.hypotheses.reduce((s,h,i)=>s+h.prior*bins[i],0);
      const ig=entropy(mass)-q.hypotheses.reduce(
        (s,h,i)=>s+h.prior*entropy(bins[i]),0);
      const cost=target.cost+target.latency*q.latency_penalty;
      const saved=Math.max(0,q.cost_of_inaction-target.latency*q.latency_penalty);
      const utility=q.value_per_bit*ig-cost+saved;
      options.push({
        id:'minecraft-fault-'+target.world+'-x'+target.fault_x+'-ge'+threshold,
        kind:'observe-fault-then-restore',
        target:{world:target.world,fault_x:target.fault_x,threshold,
          observation:'count-powered-redstone-lamps-of-nine'},
        predictions:Object.fromEntries(q.hypotheses.map((h,i)=>[
          h.id,{lit_count:h.predictions[pos],prob_ge_threshold:round(bins[i])}
        ])),
        expected_information_bits:round(ig),
        cost:round(cost),latency:target.latency,
        utility_vs_zero:round(utility),
        independent_game_witness_required:true,
        user_review_required:true,
        disposition:'PROPOSAL_ONLY',
      });
    }
  }
  return options.sort((a,b)=>
    b.utility_vs_zero-a.utility_vs_zero||
    b.expected_information_bits-a.expected_information_bits||
    a.id.localeCompare(b.id));
}

export function designInstrument(q) {
  checkInputs(q);
  const all=candidates(q);
  const feasible=all.filter(x=>x.cost<=q.budget&&
    x.expected_information_bits>=0.01);
  const best=feasible[0];
  const abstainUtility=-q.cost_of_inaction;
  if(!best||best.utility_vs_zero<=abstainUtility)
    return hold(!feasible.length?'NO_AFFORDABLE_DISCRIMINATING_MEASUREMENT':
      'HOLD_ACTION_COST_EXCEEDS_EXPECTED_INFORMATION',{
        candidates:all,abstain_utility:round(abstainUtility),
        cost_of_inaction:q.cost_of_inaction,
        next_question:'Which new observable would separate the remaining models?',
      });
  return {
    schema:'motif.instrument-decision/v0',
    status:'PROPOSE_NEW_INSTRUMENT',
    selected:best,candidates:all,
    information_gain_bits:best.expected_information_bits,
    cost_of_inaction:q.cost_of_inaction,
    abstain_utility:round(abstainUtility),
    first_seeded_composition:'relatte.minecraft.redstone-hypothesis-garden/v0',
    source_ids:[...q.source.source_ids],
    source_history_disposition:'HOLD',
    assumptions:'Hypotheses and outcome probabilities are seeded, not independently discovered facts.',
    real_game_execution:false,
    external_actions:0,
    permission:'PROPOSE_ONLY',
  };
}

// Conditional inference for an *externally verified* result. Not an
// observation, not a validator and never a persistent memory write.
export function conditionalPosterior(decision,hypotheses,observedLit) {
  assert(decision?.status==='PROPOSE_NEW_INSTRUMENT','NO_VALID_PROPOSAL');
  assert(Number.isInteger(observedLit)&&observedLit>=0&&observedLit<=9,
    'BAD_HYPOTHETICAL_RESULT');
  const threshold=decision.selected.target.threshold;
  const observed=observedLit>=threshold;
  const weights=hypotheses.map(h=>{
    const probability=decision.selected.predictions[h.id]?.prob_ge_threshold;
    assert(typeof probability==='number','UNRECOGNIZED_MODEL');
    return {id:h.id,prior:h.prior,
      likelihood:observed?probability:1-probability,
      unnormalized:h.prior*(observed?probability:1-probability)};
  });
  const sum=weights.reduce((a,b)=>a+b.unnormalized,0);
  assert(sum>0,'ZERO_LIKELIHOOD');
  return {
    schema:'motif.conditional-posterior/v0',
    interpretation_only:true,observation_verified:false,
    observed_lit_count_hypothetical:observedLit,
    posterior:weights.map(x=>({id:x.id,prior:x.prior,
      posterior:round(x.unnormalized/sum)})),
    authority:'NONE',admission:'NONE',
  };
}
