// MOTIF-016: generate a question-selection META procedure from recorded failure.
// Research-only, synthetic, no model launch or code mutation.
// Frozen parent: 015 Invented Graft; pinned organs: 014 National Treasure + Dogram.
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import {
  knownWorld, synthesize, validateCartridge, score
} from '../015/invented_graft.mjs';
import { verifyDonors } from '../014/organ_garden.mjs';
import { buildQuestionFrontier } from '../014/upstream/national_treasure_engine.mjs';

const SELF=fileURLToPath(import.meta.url);
const PROGRAM='motif016.generated-meta-inquiry-cartridge/v0';
const COUNT=16;
const PS=Object.freeze([0.06,0.13,0.20,0.32,0.63,0.82]);
const SALTS=Object.freeze({training:30949,validation:62071,holdout:99191,hostile:11107,stealth:62137});

function requirePositiveInteger(x) {
  if(!Number.isSafeInteger(x)||x<1||x>100)throw Error('HOLD_INVALID_SAMPLE_SIZE');
}
function hash(obj) {
  return createHash('sha256').update(JSON.stringify(obj)).digest('hex');
}
function seedRng(seed) {
  // A reproducible fixture generator, not a security-quality random source.
  let state=seed>>>0;
  return ()=>((state=(Math.imul(state,1664525)+1013904223)>>>0)/4294967296);
}
function trial(id, priorA, rng, tamper=false, disclosure=true) {
  const truePrior=[priorA,(1-priorA)*0.36,(1-priorA)*0.34,(1-priorA)*0.30];
  const count=Array.from({length:COUNT},()=>rng()<(tamper ? 1-priorA:priorA)?1:0)
    .reduce((a,b)=>a+b,0);
  return {
    observed:Object.freeze({
      schema:'motif016.inquiry-observation/v0',
      id, sample_size:COUNT, a_count:count,
      source:'SYNTHETIC_SAMPLED_CATEGORICAL_REPORT',
      audit:'INVENTED_REGIME_SAMPLE_ONLY',
      noise_warning:(tamper && disclosure)?'KNOWN_SENSOR_FAILURE':'NONE_DECLARED'
    }),
    // Hidden world is available to evaluator, never passed to chooseMetaMethod.
    evaluator_only:Object.freeze({prior:truePrior,phase:id.split('-')[0]})
  };
}
export function scenarioFamily(phase,count=36) {
  if(!Object.hasOwn(SALTS,phase) || !Number.isSafeInteger(count)||count<6||count>100)
    throw Error('HOLD_INVALID_FROZEN_PHASE');
  const rng=seedRng(SALTS[phase]);
  const shift=phase==='training'?0:phase==='validation'?2:phase==='holdout'?4:1;
  return Array.from({length:count},(_,i)=>{
    const p=PS[(i+shift)%PS.length];
    return trial(phase+'-'+String(i).padStart(3,'0'),p,rng,phase==='hostile'||phase==='stealth',phase!=='stealth');
  });
}
export function prepareMethodCartridges() {
  verifyDonors();
  const reference=knownWorld({id:'motif016-reference-before-shift'});
  const expected=synthesize(reference,'expected');
  const robust=synthesize(reference,'worst');
  validateCartridge(expected);validateCartridge(robust);
  if(expected.method.op!=='ASK'||robust.method.op!=='ASK')
    throw Error('HOLD_INVALID_PARENT_METHODS');
  return Object.freeze({
    schema:'motif016.parent-method-cartridges/v0',
    reference_prior:[...reference.prior],
    expected,robust,
    source_pins:{...expected.source_pins},
    inherited_question_receipt:expected.question_receipt,
    inherited_dogram_receipt:expected.dogram_receipt,
    authority:'none'
  });
}
function outcome(trial,parents) {
  const world=knownWorld({
    id:trial.observed.id,
    prior:[...trial.evaluator_only.prior]
  });
  const a=score(parents.expected.method,world).mean_cost;
  const b=score(parents.robust.method,world).mean_cost;
  return Object.freeze({expected:a,robust:b});
}
function assertObservation(o) {
  if(!o || o.schema!=='motif016.inquiry-observation/v0' ||
    typeof o.id!=='string' ||
    o.source!=='SYNTHETIC_SAMPLED_CATEGORICAL_REPORT' ||
    o.audit!=='INVENTED_REGIME_SAMPLE_ONLY' ||
    o.noise_warning!=='NONE_DECLARED' ||
    !Number.isSafeInteger(o.sample_size) || o.sample_size!==COUNT ||
    !Number.isSafeInteger(o.a_count) ||
    o.a_count<0 || o.a_count>o.sample_size)
    throw Error('HOLD_UNTRUSTED_OR_MISSING_OBSERVATION');
}
export function recordedFeedback(trials,parents) {
  return trials.map(t=>({
    observation:t.observed,
    // These known-model expected costs are revealed only after a finished
    // SYNTHETIC training episode, as an evaluator's audit.
    audited_result:outcome(t,parents),
    evidence_type:'POST_EPISODE_SYNTHETIC_EVALUATOR_RECEIPT'
  }));
}
function validateFeedback(entries) {
  if(!Array.isArray(entries)||entries.length<6)throw Error('HOLD_INSUFFICIENT_EPISODES');
  const ids=new Set();
  for(const row of entries) {
    if(!row || row.evidence_type!=='POST_EPISODE_SYNTHETIC_EVALUATOR_RECEIPT')
      throw Error('HOLD_MISSING_AUDITED_OUTCOME');
    assertObservation(row.observation);
    if(ids.has(row.observation.id))throw Error('HOLD_DUPLICATE_EPISODE');
    ids.add(row.observation.id);
    if(!row.audited_result ||
      !['expected','robust'].every(k=>
        Number.isFinite(row.audited_result[k]) && row.audited_result[k]>=0))
      throw Error('HOLD_INVALID_AUDITED_COST');
  }
}
function choose(grammar,observable) {
  assertObservation(observable);
  if(grammar.op==='CONST' && ['expected','robust'].includes(grammar.method))
    return grammar.method;
  if(grammar.op==='IF_COUNT_AT_LEAST' &&
    Number.isSafeInteger(grammar.threshold) &&
    grammar.threshold>=0 && grammar.threshold<=COUNT+1 &&
    ['expected','robust'].includes(grammar.then) &&
    ['expected','robust'].includes(grammar.else) &&
    grammar.then!==grammar.else)
    return observable.a_count>=grammar.threshold ? grammar.then : grammar.else;
  throw Error('HOLD_INVALID_METAPROGRAM');
}
function mean(values) {
  return values.reduce((a,b)=>a+b,0)/values.length;
}
export function judgeGrammar(grammar,records) {
  validateFeedback(records);
  let costs=[],regrets=[],mistakes=0;
  for(const row of records){
    const selected=choose(grammar,row.observation);
    const selectedCost=row.audited_result[selected];
    const optimum=Math.min(row.audited_result.expected,row.audited_result.robust);
    costs.push(selectedCost);
    regrets.push(Math.max(0,selectedCost-optimum));
    if(selectedCost>optimum+1e-9)mistakes++;
  }
  return {
    n:records.length,
    mean_cost:mean(costs),
    mean_regret_to_privileged_case_oracle:mean(regrets),
    wrong_method_choices:mistakes
  };
}
export function generationCandidates(sampleSize=COUNT){
  requirePositiveInteger(sampleSize);
  const constant=[
    {op:'CONST',method:'expected'},
    {op:'CONST',method:'robust'}
  ];
  const extended=[
    ...constant,
    ...Array.from({length:sampleSize+2},(_,threshold)=>[
      {op:'IF_COUNT_AT_LEAST',threshold,then:'expected',else:'robust'},
      {op:'IF_COUNT_AT_LEAST',threshold,then:'robust',else:'expected'}
    ]).flat()
  ];
  return {constant,extended};
}
function objective(stats,grammar){
  // Tiny prespecified procedural complexity penalty to break trivial gains.
  return stats.mean_cost+(grammar.op==='CONST'?0:0.01);
}
function fitPolicies(programs,feedback){
  return programs.map(method=>{
    const metrics=judgeGrammar(method,feedback);
    return {method,metrics,objective:objective(metrics,method)};
  }).sort((a,b)=>a.objective-b.objective ||
    JSON.stringify(a.method).localeCompare(JSON.stringify(b.method)));
}
// A separate analytic Bayesian control for the toy source likelihood. Observed
// a_count has a Beta(1,1) prior on p(a); the posterior predictive is
// (k+1)/(n+2). It chooses which frozen 015 method has less EXPECTED cost
// under that posterior probability. It sees the same observed count only.
export function classicalPosteriorPolicy(o) {
  assertObservation(o);
  const posteriorMean=(o.a_count+1)/(o.sample_size+2);
  return 1+4*(1-posteriorMean)<4 ? 'expected' : 'robust';
}
function classicalControlMetric(feedback){
  validateFeedback(feedback);
  return {
    mean_cost:mean(feedback.map(x=>
      x.audited_result[classicalPosteriorPolicy(x.observation)])),
    n:feedback.length
  };
}
function extractFailure(feedback){
  const eps=1e-9;
  const casesExpectedBad=feedback.filter(x=>
    x.audited_result.expected>x.audited_result.robust+eps);
  const casesRobustBad=feedback.filter(x=>
    x.audited_result.robust>x.audited_result.expected+eps);
  return {
    expected_method_regressions:casesExpectedBad.length,
    robust_method_regressions:casesRobustBad.length,
    both_failed_across_different_episodes:
      casesExpectedBad.length>0 && casesRobustBad.length>0,
    first_expected_failure:casesExpectedBad[0]?.observation.id ?? null,
    first_robust_failure:casesRobustBad[0]?.observation.id ?? null
  };
}
function diagnosticQuestion(failure){
  return buildQuestionFrontier({
    clue:'A prior-optimized synthetic inquiry compiler fails on changed input regimes.',
    claim:'A conditional policy may avoid some cost regressions.',
    source_locator:'MOTIF-016/SYNTHETIC_POST_EPISODE_AUDIT',
    chronology:'Two frozen 015 parent method cartridges precede separate 016 synthetic feedback.',
    counterevidence:'A simple constant method could dominate all observations.',
    falsifier:'The conditional policy fails to outperform the best constant method on held-out samples.',
    source_families:['simulated regime sample','simulated post-episode evaluator'],
    competing_explanations:['expected-cost objective mismatches a changed prior',
      'a noisy source report makes objective switching unreliable'],
    provenance_class:'speculation',
    support_confidence:'unsupported'
  });
}
export function proposeMetaprocedure(trainingFeedback,validationFeedback) {
  validateFeedback(trainingFeedback);validateFeedback(validationFeedback);
  const trainSet=new Set(trainingFeedback.map(x=>x.observation.id));
  if(validationFeedback.some(x=>trainSet.has(x.observation.id)))
    throw Error('HOLD_TRAIN_VALIDATION_OVERLAP');
  const failure=extractFailure(trainingFeedback);
  const question=diagnosticQuestion(failure);
  if(question.aperture.id!=='discriminator' ||
    Object.hasOwn(question,'answer') ||
    Object.hasOwn(question,'conclusion'))
    throw Error('HOLD_QUESTION_BOX_INVARIANT');
  const all=generationCandidates();
  const constant=fitPolicies(all.constant,trainingFeedback)[0];
  if(!failure.both_failed_across_different_episodes)
    return {status:'HOLD_NO_BIDIRECTIONAL_FAILURE_EVIDENCE',
      failure,question_receipt:question,old_method:constant.method,
      new_method:null,automatic_install:false};
  const extended=fitPolicies(all.extended,trainingFeedback)[0];
  const valConstant=judgeGrammar(constant.method,validationFeedback);
  const valExtended=judgeGrammar(extended.method,validationFeedback);
  const trainGain=constant.metrics.mean_cost-extended.metrics.mean_cost;
  const validationGain=valConstant.mean_cost-valExtended.mean_cost;
  const earned=extended.method.op==='IF_COUNT_AT_LEAST' &&
    trainGain>0.05 && validationGain>0.05;
  const body={
    schema:PROGRAM,
    status: earned?'HOLD_FOR_HUMAN_REVIEW':'REFUSE_NO_VALIDATED_GAIN',
    old_grammar:'CONST(method)',
    proposed_grammar:'IF_COUNT_AT_LEAST(observed_sample, threshold, method, method)',
    observed_reason:failure,
    question_receipt:question,
    old_method:constant.method,
    new_method:extended.method,
    candidate_count:all.extended.length,
    training:{baseline:constant.metrics,proposal:extended.metrics,gain:trainGain},
    validation:{baseline:valConstant,proposal:valExtended,gain:validationGain},
    strong_classical_posterior_validation:classicalControlMetric(validationFeedback),
    source:'DEVELOPER_SUPPLIED_META_GRAMMAR + FINITE SEARCH ON SYNTHETIC_FEEDBACK',
    objective:'MEAN_RECORDED_COST_PLUS_PREDECLARED_COMPLEXITY_PENALTY',
    only_observation_available_to_live_policy:'a_count out of 16',
    control_is_supervised_threshold:'YES',
    empirical_architectural_superiority:false,
    automatic_install:false,
    code_mutated:false,
    real_world_evidence:false,
    operator_permission:'none'
  };
  return {...body,checksum_sha256:hash(body)};
}
export function validateMetaCartridge(c){
  if(!c || c.schema!==PROGRAM ||
    !['HOLD_FOR_HUMAN_REVIEW','REFUSE_NO_VALIDATED_GAIN'].includes(c.status) ||
    c.automatic_install!==false || c.code_mutated!==false ||
    typeof c.checksum_sha256!=='string')
    throw Error('HOLD_INVALID_META_CARTRIDGE');
  const {checksum_sha256,...body}=c;
  if(hash(body)!==checksum_sha256)throw Error('HOLD_TAMPERED_META_CARTRIDGE');
  return true;
}
export function chooseMetaMethod(cartridge,observable){
  validateMetaCartridge(cartridge);
  if(cartridge.status!=='HOLD_FOR_HUMAN_REVIEW')
    throw Error('HOLD_METHOD_NOT_VALIDATED');
  return choose(cartridge.new_method,observable);
}
export function gradeFuture(trials,parents,meta) {
  const rows=[];
  for(const t of trials){
    const feedback=outcome(t,parents); // only the evaluator sees the true prior
    const o=t.observed;
    let chosen=null, status='HOLD';
    try {chosen=chooseMetaMethod(meta,o);status='PROPOSE_SYNTHETIC_ONLY';}
    catch(e) {
      if(!String(e.message).startsWith('HOLD_'))throw e;
    }
    rows.push({
      id:o.id,
      sensor_warning:o.noise_warning,
      observed_a_count:o.a_count,
      selection:chosen,
      status,
      selected_cost:chosen?feedback[chosen]:null,
      fixed_expected_cost:feedback.expected,
      fixed_robust_cost:feedback.robust,
      privileged_oracle_cost:Math.min(feedback.expected,feedback.robust),
      classical_posterior_selection:status==='HOLD'?null:classicalPosteriorPolicy(o)
    });
  }
  const admitted=rows.filter(x=>x.status==='PROPOSE_SYNTHETIC_ONLY');
  const meanField=k=>admitted.length?mean(admitted.map(x=>x[k])):null;
  return {
    evaluated_trials:trials.length,proposed_count:admitted.length,
    hold_count:trials.length-admitted.length,
    mean_proposed_cost:meanField('selected_cost'),
    mean_fixed_expected_cost:meanField('fixed_expected_cost'),
    mean_fixed_robust_cost:meanField('fixed_robust_cost'),
    mean_privileged_oracle_cost:meanField('privileged_oracle_cost'),
    mean_classical_posterior_cost:admitted.length
      ? mean(admitted.map(x=>x[x.classical_posterior_selection==='expected'
        ?'fixed_expected_cost':'fixed_robust_cost'])):null,
    rows
  };
}
export function metaExperiment() {
  const parents=prepareMethodCartridges();
  const training=scenarioFamily('training');
  const validation=scenarioFamily('validation',24);
  const holdout=scenarioFamily('holdout');
  // The generator sees post-episode TRAIN and VALIDATION only; it has no holdout
  // priors, observations or labels at compilation time.
  const learned=proposeMetaprocedure(
    recordedFeedback(training,parents),recordedFeedback(validation,parents));
  if(learned.new_method!==null)validateMetaCartridge(learned);
  const fresh=gradeFuture(holdout,parents,learned);
  const hostile=gradeFuture(scenarioFamily('hostile',12),parents,learned);
  const stealth=gradeFuture(scenarioFamily('stealth',24),parents,learned);
  return {
    schema:'motif016.self-revising-question-method-study/v0',
    status:'SYNTHETIC_INQUIRY_COMPILER_RESEARCH',
    parents:{
      generated_expected_015_sha:parents.expected.checksum_sha256,
      generated_robust_015_sha:parents.robust.checksum_sha256,
      national_treasure_question:parents.inherited_question_receipt.question,
      native_dogram_pin:parents.inherited_dogram_receipt.source_blob
    },
    meta_revision:learned,
    frozen_holdout:fresh,
    hostile_inverted_report:hostile,
    unflagged_inverted_report:stealth,
    next_question:{
      question:'What independent observation distinguishes an unannounced inverted sensor from a real regime change, before rewriting the inquiry-compiler grammar?',
      method_change_candidate:'add source-reliability and abstention grammar',
      performed:false
    },
    no_real_world_evidence:true,no_production_mutation:true,
    no_autonomous_code_editing:true,no_recursive_intelligence_gain_claim:true
  };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF)
  process.stdout.write(JSON.stringify(metaExperiment(),null,2)+'\n');
