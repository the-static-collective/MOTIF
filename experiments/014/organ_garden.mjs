// MOTIF-014: synthetic, source-pinned organ composition and method evaluation.
// No network, model launch, repository edits, promotion, or external action.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { buildQuestionFrontier } from './upstream/national_treasure_engine.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PINS = Object.freeze({
  national_treasure: '83574ed0a927fdefe1a53b3ece0960f011b875d0',
  dogram: 'c201ce28ff7bb18a28496c0a2eefe2f9451526cc'
});
export const PROBES = Object.freeze({
  coarse: ['all','all','all','all'],
  vertical: ['L','L','R','R'],
  diagonal: ['U','D','U','D'],
  joint: ['LU','LD','RU','RD']
});
export const STATES = Object.freeze(['a','b','c','d']);
export const POLICIES = Object.freeze(['fixed', 'dogram-minimal', 'dogram-cost']);

export function gitBlobSha(bytes) {
  const b = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  return createHash('sha1').update('blob ' + b.length + '\0').update(b).digest('hex');
}
export function verifyDonors() {
  const names = {
    national_treasure: 'national_treasure_engine.mjs',
    dogram: 'dogram_probe_partition_refinement.py'
  };
  for (const [id, filename] of Object.entries(names)) {
    const actual = gitBlobSha(readFileSync(path.join(ROOT, 'upstream', filename)));
    if (actual !== PINS[id]) throw new Error('HOLD_UPSTREAM_SOURCE_DRIFT:' + id);
  }
  return { ...PINS };
}
export function makeCase(id, target, costs = {coarse:1, vertical:2, diagonal:2, joint:6}, overrides = {}) {
  return {
    id, scope: 'SYNTHETIC_ONLY', states: [...STATES], target: [...target],
    probes: Object.fromEntries(Object.entries(PROBES).map(([k,v])=>[k,[...v]])),
    costs: {...costs},
    clue: {
      clue: 'A claimed difference between synthetic situations ' + target.join(' and '),
      provenance_class: 'speculation',
      support_confidence: 'unsupported',
      source_locator: 'SYNTHETIC_GENERATOR/' + id,
      chronology: 'All invented states generated in one frozen toy fixture.',
      counterevidence: 'The observable partitions may be equivalent on target states.',
      falsifier: 'A claimed separating probe maps target states to the same output.',
      source_families: ['fixture-A','fixture-B'],
      competing_explanations: ['first state','second state'],
      ...overrides
    }
  };
}
function validateCase(record) {
  if (!record || record.scope !== 'SYNTHETIC_ONLY' ||
      !Array.isArray(record.states) || record.states.length < 2 ||
      new Set(record.states).size !== record.states.length ||
      !Array.isArray(record.target) || record.target.length !== 2 ||
      record.target[0] === record.target[1] ||
      record.target.some(x=>!record.states.includes(x)) ||
      !record.probes || !record.costs ||
      Object.keys(record.probes).length !== Object.keys(record.costs).length ||
      Object.keys(record.probes).some(x=>!Object.hasOwn(record.costs,x) ||
        !Array.isArray(record.probes[x]) ||
        record.probes[x].length !== record.states.length ||
        !Number.isSafeInteger(record.costs[x]) || record.costs[x] < 1)) {
    throw new Error('HOLD_INVALID_FINITE_SYNTHETIC_CASE');
  }
}
function dogramNative(record) {
  const call = spawnSync('python3', [path.join(ROOT, 'dogram_bridge.py')], {
    input: JSON.stringify({states:record.states, probes:record.probes, target:record.target}),
    encoding: 'utf8', timeout: 5000, maxBuffer: 1024*1024
  });
  if (call.error || call.status !== 0) throw new Error('HOLD_DOGRAM_NATIVE:' +
    String(call.error?.message ?? call.stderr ?? call.status).slice(0,300));
  const receipt = JSON.parse(call.stdout);
  if (receipt.schema !== 'motif014.dogram-native-probe-receipt/v0' ||
      receipt.source_blob !== PINS.dogram) throw new Error('HOLD_DOGRAM_RECEIPT_MISMATCH');
  return receipt;
}
export function runCase(record, policy = 'fixed') {
  if (!POLICIES.includes(policy)) throw new Error('HOLD_UNKNOWN_POLICY');
  validateCase(record);
  verifyDonors();
  // This is the ACTUAL pinned National Treasure Question Box, not a paraphrase.
  const question = buildQuestionFrontier(record.clue);
  if (question.schema !== 'national-treasure.question-receipt/v0' ||
      Object.hasOwn(question, 'answer') || Object.hasOwn(question, 'conclusion'))
    throw new Error('HOLD_QUESTION_BOX_AUTHORITY');
  const base = {
    schema:'motif014.organ-garden-run/v0', case_id:record.id, policy,
    source_pins:{...PINS}, national_treasure_question_receipt:question,
    sim_only:true, dispatched:false, authority:'none'
  };
  if (question.aperture.id !== 'discriminator')
    return {...base, status:'HOLD_QUESTION_FRONTIER', chosen_probes:[],
      declared_cost:0, dogram_receipt:null};
  const calc = dogramNative(record);
  const separated = new Set(calc.separating_probes);
  let chosen = [];
  if (policy === 'fixed') {
    for (const name of Object.keys(record.probes)) {
      chosen.push(name);
      if (separated.has(name)) break;
    }
    if (!separated.has(chosen.at(-1))) chosen = [];
  } else {
    const eligible = policy === 'dogram-minimal'
      ? calc.minimal_separators : calc.separating_probes;
    const ranked = [...eligible].sort((a,b)=>
      record.costs[a]-record.costs[b] || a.localeCompare(b));
    if (ranked.length) chosen = [ranked[0]];
  }
  if (!chosen.length) return {...base, status:'HOLD_NO_SEPARATOR',
    chosen_probes:[], declared_cost:0, dogram_receipt:calc};
  return {...base, status:'PROPOSE_SYNTHETIC_ONLY',
    chosen_probes:chosen,
    declared_cost:chosen.reduce((sum,p)=>sum+record.costs[p],0),
    dogram_receipt:calc};
}
export function fixtures() {
  // These are NOT independent domains. Labels, costs and outcomes are author-supplied.
  const train = [
    makeCase('train-first', ['a','d']),
    makeCase('train-second', ['a','b'])
  ];
  const holdout = [
    makeCase('test-one', ['b','c']),
    makeCase('test-two', ['c','d']),
    makeCase('test-three', ['a','c']),
    makeCase('test-cheap-joint', ['a','d'],
      {coarse:1, vertical:4, diagonal:4, joint:1})
  ];
  return {train,holdout};
}
export function evaluateMethod(policy, cases) {
  const data = cases.map(c=> {
    const run = runCase(c,policy);
    const classical = runCase(c,'dogram-cost');
    const fixed = runCase(c,'fixed');
    if (run.status !== 'PROPOSE_SYNTHETIC_ONLY')
      throw new Error('HOLD_BENCHMARK_MISSING_PROPOSAL');
    return {
      case_id:c.id, policy:run.policy,
      cost:run.declared_cost, probes:run.chosen_probes,
      fixed_cost:fixed.declared_cost, classical_min_cost:classical.declared_cost,
      regret:run.declared_cost-classical.declared_cost,
      question_aperture:run.national_treasure_question_receipt.aperture.id
    };
  });
  return {policy, cases:data,
    cost_total:data.reduce((sum,x)=>sum+x.cost,0),
    regret_total:data.reduce((sum,x)=>sum+x.regret,0)};
}
export function gardenerExperiment() {
  verifyDonors();
  const {train,holdout} = fixtures();
  const baseline_train = evaluateMethod('fixed',train);
  const baseline_test = evaluateMethod('fixed',holdout);
  const candidates = ['dogram-minimal', 'dogram-cost'].map(policy => {
    // Candidate policy family supplied by developer, not autonomously invented.
    const training = evaluateMethod(policy,train);
    const tested = evaluateMethod(policy,holdout);
    const improves_training = training.cost_total < baseline_train.cost_total;
    const no_holdout_regret = tested.regret_total === 0;
    const no_holdout_regression = tested.cases.every(c=>c.cost<=c.fixed_cost);
    return {
      schema:'motif014.method-amendment/v0',
      from:'fixed', to:policy,
      provenance:'DEVELOPER_SUPPLIED_POLICY_FAMILY',
      training, heldout:tested, improves_training,
      independent_holdout_parity_with_classical: no_holdout_regret,
      no_holdout_regression,
      disposition: !improves_training ? 'REFUSE_NO_TRAINING_GAIN'
        : !no_holdout_regret ? 'REFUSE_HOLDOUT_REGRET'
        : !no_holdout_regression ? 'REFUSE_HOLDOUT_REGRESSION'
        : 'HOLD_FOR_HUMAN_REVIEW',
      automatic_install:false, source_repo_modified:false
    };
  });
  const missingSource = runCase(makeCase('missing-source',['a','d'],
    {coarse:1,vertical:2,diagonal:2,joint:6},
    {source_locator:''}), 'dogram-cost');
  return {
    schema:'motif014.organ-garden-study/v0',
    status:'SYNTHETIC_RESEARCH_ONLY',
    source_pins:{...PINS}, national_treasure_is_native:true,
    dogram_is_native:true,
    baseline_training:baseline_train, baseline_heldout:baseline_test,
    candidate_amendments:candidates, missing_source_hold:{
      aperture:missingSource.national_treasure_question_receipt.aperture.id,
      status:missingSource.status, dogram_was_called:missingSource.dogram_receipt!==null
    },
    no_external_calls:true, no_real_world_authority:true,
    no_autonomous_code_revision:true, no_real_organ_mutation:true
  };
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.stdout.write(JSON.stringify(gardenerExperiment(),null,2)+'\n');
}
