// MOTIF-015 — Invented Graft: typed procedural synthesis over two exact, pinned donor organs.
// This module synthesizes executable READ-ONLY decision cartridges, NOT code patches.
// All models, labels and priors are fictional, declared and finite. No real actuation.
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { makeCase, runCase, verifyDonors } from '../014/organ_garden.mjs';

const OWN = fileURLToPath(import.meta.url);
export const SCHEMA = 'motif015.generated-inquiry-cartridge/v0';
const MAX_PROGRAMS = 10000;

export function knownWorld({
  id='world', labels=['yes','yes','no','no'],
  prior=[0.6,0.15,0.15,0.1], costs=null, probes=null,
  allowed=null, clue_overrides={}
}={}) {
  const sourceProbes = probes ?? {
    coarse:['all','all','all','all'],
    spot:['a','other','other','other'],
    vertical:['L','L','R','R'],
    diagonal:['U','D','U','D'],
    joint:['a','b','c','d']
  };
  const sourceCosts = costs ?? {coarse:1,spot:1,vertical:4,diagonal:3,joint:8};
  return {
    id, scope:'SYNTHETIC_KNOWN_MODEL_ONLY',
    states:['a','b','c','d'], labels:[...labels], prior:[...prior],
    probes:structuredClone(sourceProbes), costs:structuredClone(sourceCosts),
    allowed:[...(allowed ?? Object.keys(sourceProbes))],
    clue_overrides:{...clue_overrides},
  };
}
function validate(w) {
  if (!w || w.scope!=='SYNTHETIC_KNOWN_MODEL_ONLY' ||
      !Array.isArray(w.states) || w.states.length<2 || w.states.length>6 ||
      new Set(w.states).size!==w.states.length ||
      !Array.isArray(w.labels) || w.labels.length!==w.states.length ||
      w.labels.some(s=>typeof s!=='string' || s.length===0) ||
      !Array.isArray(w.prior) || w.prior.length!==w.states.length ||
      w.prior.some(p=>typeof p!=='number' || !Number.isFinite(p) || p<=0 || p>=1) ||
      Math.abs(w.prior.reduce((a,b)=>a+b,0)-1)>1e-9 ||
      !w.probes || !w.costs || !Array.isArray(w.allowed) ||
      !w.allowed.length || w.allowed.length>8 ||
      new Set(w.allowed).size!==w.allowed.length ||
      Object.keys(w.probes).length>8 ||
      Object.keys(w.probes).some(k=>!/^[a-z][a-z0-9_-]{0,30}$/.test(k) ||
        !Array.isArray(w.probes[k]) || w.probes[k].length!==w.states.length ||
        w.probes[k].some(v=>typeof v!=='string' || v.length>60)) ||
      Object.keys(w.costs).length!==Object.keys(w.probes).length ||
      Object.keys(w.probes).some(k=>!Object.hasOwn(w.costs,k) ||
        !Number.isSafeInteger(w.costs[k]) || w.costs[k]<1 || w.costs[k]>1000) ||
      w.allowed.some(k=>!Object.hasOwn(w.probes,k)) ||
      !w.clue_overrides || typeof w.clue_overrides!=='object') {
    throw new Error('HOLD_INVALID_SYNTHETIC_KNOWN_MODEL');
  }
}
function sameLabel(w,indices) {
  return indices.every(i=>w.labels[i]===w.labels[indices[0]]);
}
function buckets(w, indices,probe) {
  const map = new Map();
  for (const i of indices) {
    const value = w.probes[probe][i];
    if (!map.has(value)) map.set(value,[]);
    map.get(value).push(i);
  }
  return [...map.entries()].sort((a,b)=>a[0].localeCompare(b[0]));
}
function combine(branches, index=0, base={}, out=[]) {
  if(index===branches.length) {out.push({...base}); return out;}
  for (const tree of branches[index].programs) {
    combine(branches,index+1,{...base,[branches[index].output]:tree},out);
    if(out.length>MAX_PROGRAMS) throw new Error('HOLD_GENERATION_SEARCH_BUDGET');
  }
  return out;
}
// The grammar is STOP(label) | ASK(probe, observable-output -> program).
// No complete conditional procedure is supplied; the bounded enumerator constructs
// trees by composing primitives and culling non-separating or unlawful steps.
export function enumeratePrograms(w, indices, remaining, budget={count:0}) {
  if(sameLabel(w,indices)) {
    const candidate = {op:'STOP',label:w.labels[indices[0]]};
    budget.count++;
    if(budget.count>MAX_PROGRAMS) throw new Error('HOLD_GENERATION_SEARCH_BUDGET');
    return [candidate];
  }
  const all=[];
  for(const probe of remaining) {
    const groups=buckets(w,indices,probe);
    if(groups.length<2) continue; // repeat question, zero information
    const future=remaining.filter(k=>k!==probe);
    const branches=groups.map(([output, subset])=>({
      output,programs:enumeratePrograms(w,subset,future,budget)
    }));
    if(branches.some(b=>b.programs.length===0)) continue;
    const choices=combine(branches);
    for(const by of choices) {
      all.push({op:'ASK',probe,by});
      if(all.length>MAX_PROGRAMS) throw new Error('HOLD_GENERATION_SEARCH_BUDGET');
    }
  }
  return all;
}
export function executeProgram(program,w,index) {
  if(!Number.isInteger(index) || index<0 || index>=w.states.length)
    throw new Error('HOLD_INVALID_SIMULATED_STATE');
  let cursor=program,cost=0,probes=[],steps=0;
  while(cursor?.op==='ASK'){
    if(++steps>w.allowed.length || !w.allowed.includes(cursor.probe))
      throw new Error('HOLD_NONTERMINATING_OR_UNAUTHORIZED_METHOD');
    cost+=w.costs[cursor.probe];
    probes.push(cursor.probe);
    const output=w.probes[cursor.probe][index];
    if(!Object.hasOwn(cursor.by,output)) throw new Error('HOLD_MISSING_BRANCH');
    cursor=cursor.by[output];
  }
  if(!cursor || cursor.op!=='STOP' || cursor.label!==w.labels[index])
    throw new Error('HOLD_INCORRECT_METHOD_FOR_DECLARED_WORLD');
  return {label:cursor.label,cost,probes};
}
export function score(program,w,prior=w.prior) {
  const executions=w.states.map((_,i)=>executeProgram(program,w,i));
  return {
    mean_cost:executions.reduce((a,x,i)=>a+prior[i]*x.cost,0),
    worst_cost:Math.max(...executions.map(x=>x.cost)),
    paths:Object.fromEntries(w.states.map((s,i)=>[s,executions[i].probes]))
  };
}
// Independent classical dynamic-programming control, not a comparison to random
// or a deliberately weak fixed-sequence strawman. This solves the declared toy
// problem optimally under the same known model, objective and allowed probe set.
export function classicalOptimum(w,objective='expected') {
  validate(w);
  if(!['expected','worst'].includes(objective)) throw new Error('HOLD_UNKNOWN_OBJECTIVE');
  const memo=new Map();
  const cost=(indices,remaining)=>{
    if(sameLabel(w,indices)) return 0;
    const key=indices.join(',')+'|'+remaining.join(',');
    if(memo.has(key)) return memo.get(key);
    const mass=indices.reduce((a,i)=>a+w.prior[i],0);
    let best=Infinity;
    for(const probe of remaining) {
      const groups=buckets(w,indices,probe);
      if(groups.length<2) continue;
      const future=remaining.filter(p=>p!==probe);
      const subs=groups.map(([,subset])=>cost(subset,future));
      if(subs.some(x=>!Number.isFinite(x))) continue;
      const step=w.costs[probe]+(objective==='expected'?
        groups.reduce((a,[,subset],idx)=>
          a + subset.reduce((m,i)=>m+w.prior[i],0)/mass*subs[idx],0)
        : Math.max(...subs));
      best=Math.min(best,step);
    }
    memo.set(key,best);
    return best;
  };
  return cost(w.states.map((_,i)=>i),w.allowed);
}
function wholeProbeBaseline(w) {
  // Strong one-shot baseline: cheapest single probe fully determines declared labels.
  let best=null;
  for(const probe of w.allowed) {
    const groups=buckets(w,w.states.map((_,i)=>i),probe);
    if(groups.every(([,is])=>sameLabel(w,is)) &&
      (!best || w.costs[probe]<best.cost)) best={probe,cost:w.costs[probe]};
  }
  return best;
}
function hashCartridge(body) {
  return createHash('sha256').update(JSON.stringify(body)).digest('hex');
}
export function synthesize(w,objective='expected') {
  validate(w);
  if(!['expected','worst'].includes(objective)) throw new Error('HOLD_UNKNOWN_OBJECTIVE');
  const pins=verifyDonors();
  const distinct = w.states.findIndex((s,i)=>w.labels[i]!==w.labels[0]);
  if(distinct<0) throw new Error('HOLD_TRIVIAL_SINGLE_LABEL_WORLD');
  const caseForOrgans=makeCase(w.id,[w.states[0],w.states[distinct]],
    Object.fromEntries(w.allowed.map(k=>[k,w.costs[k]])),w.clue_overrides);
  caseForOrgans.states=[...w.states];
  caseForOrgans.probes=Object.fromEntries(w.allowed.map(k=>[k,[...w.probes[k]]]));
  const entrance=runCase(caseForOrgans,'dogram-cost');
  const q=entrance.national_treasure_question_receipt;
  if(q.aperture.id!=='discriminator') return {
    schema:'motif015.inquiry-hold/v0',status:'HOLD_QUESTION_EVIDENCE_GAP',
    question_receipt:q,program:null,issued_probes:0
  };
  if(entrance.status==='HOLD_NO_SEPARATOR') return {
    schema:'motif015.inquiry-hold/v0',status:'HOLD_NO_INITIAL_SEPARATOR',
    question_receipt:q,program:null,issued_probes:0
  };
  if(!entrance.dogram_receipt ||
    entrance.dogram_receipt.source_blob!==pins.dogram)
    throw new Error('HOLD_NO_PINNED_DOGRAM_RECEIPT');
  const search={count:0};
  const programs=enumeratePrograms(w,w.states.map((_,i)=>i),w.allowed,search);
  if(!programs.length) return {
    schema:'motif015.inquiry-hold/v0',status:'HOLD_NO_LAWFUL_COMPOSITION',
    question_receipt:q,program:null,issued_probes:0
  };
  const ranked=programs.map(program=>({program,stats:score(program,w)}));
  ranked.sort((a,b)=>(objective==='expected'
    ? a.stats.mean_cost-b.stats.mean_cost
    : a.stats.worst_cost-b.stats.worst_cost) ||
    JSON.stringify(a.program).length-JSON.stringify(b.program).length ||
    JSON.stringify(a.program).localeCompare(JSON.stringify(b.program)));
  const selected=ranked[0],optimal=classicalOptimum(w,objective);
  const earned=objective==='expected'?selected.stats.mean_cost:selected.stats.worst_cost;
  if(Math.abs(earned-optimal)>1e-8)
    throw new Error('HOLD_DID_NOT_MATCH_CLASSICAL_OPTIMUM');
  const body={
    schema:SCHEMA,status:'HOLD_FOR_HUMAN_REVIEW',origin:'BOUNDED_GRAMMAR_ENUMERATION',
    generated_not_selected_from_named_whole_methods:true,
    objective,world_id:w.id,source_pins:pins,
    question_receipt:q,
    dogram_receipt:entrance.dogram_receipt,
    model_scope:'KNOWN_DECLARED_SYNTHETIC_WORLD',
    generation:{grammar:'STOP(label) | ASK(probe,{output:program})',
      candidate_count:programs.length,expanded_nodes:search.count,
      max_programs:MAX_PROGRAMS},
    method:selected.program,expected_cost:selected.stats.mean_cost,
    worst_cost:selected.stats.worst_cost,
    classical_dynamic_programming_optimum:optimal,
    one_shot_baseline:wholeProbeBaseline(w),
    sampled_real_outcomes:0,external_actions:0,source_code_mutated:false,
    automatically_admitted:false,claim_new_intelligence:false
  };
  return {...body,checksum_sha256:hashCartridge(body)};
}
export function validateCartridge(cartridge) {
  if(!cartridge || cartridge.schema!==SCHEMA ||
    cartridge.status!=='HOLD_FOR_HUMAN_REVIEW' ||
    cartridge.automatically_admitted!==false ||
    typeof cartridge.checksum_sha256!=='string')
    throw new Error('HOLD_INVALID_METHOD_CARTRIDGE');
  const {checksum_sha256,...body}=cartridge;
  if(hashCartridge(body)!==checksum_sha256)
    throw new Error('HOLD_METHOD_CARTRIDGE_TAMPERED');
  return true;
}
export function worldFamilies() {
  const train=knownWorld({id:'training-weighted'});
  const shifted=knownWorld({id:'unseen-prior-shift',
    prior:[0.05,0.35,0.3,0.3]});
  const xor=knownWorld({
    id:'unseen-xor-no-one-shot',
    labels:['no','yes','yes','no'],prior:[0.25,0.25,0.25,0.25],
    probes:{coarse:['all','all','all','all'],
      vertical:['L','L','R','R'],diagonal:['U','D','U','D']},
    costs:{coarse:1,vertical:2,diagonal:2}
  });
  const prohibited=knownWorld({
    id:'unseen-refused-necessary-probe',
    labels:['no','yes','yes','no'],
    allowed:['coarse','vertical'],
    probes:{coarse:['all','all','all','all'],
      vertical:['L','L','R','R'],diagonal:['U','D','U','D']},
    costs:{coarse:1,vertical:2,diagonal:2}
  });
  return {train,shifted,xor,prohibited};
}
export function experiment() {
  const {train,shifted,xor,prohibited}=worldFamilies();
  const born=synthesize(train,'expected');
  const robust=synthesize(train,'worst');
  const xorBorn=synthesize(xor,'expected');
  const refused=synthesize(prohibited,'expected');
  validateCartridge(born);
  validateCartridge(robust);
  validateCartridge(xorBorn);
  const frozenOnShift=score(born.method,shifted);
  const robustOnShift=score(robust.method,shifted);
  const reoptimizedOnShift=synthesize(shifted,'expected');
  return {
    schema:'motif015.invented-graft-research-receipt/v0',
    status:'TESTED_IN_SYNTHETIC_KNOWN_MODELS_ONLY',
    train:{
      generated_method:born,competing_robust_objective:robust,
      classical_baseline:classicalOptimum(train,'expected')
    },
    holdout:{
      same_frozen_method_shifted_prior:{
        trained_prior:[...train.prior],heldout_prior:[...shifted.prior],
        frozen_method_cost:frozenOnShift.mean_cost,
        robust_method_cost:robustOnShift.mean_cost,
        fresh_optimal_cost:reoptimizedOnShift.expected_cost,
        old_method_regressed:frozenOnShift.mean_cost>reoptimizedOnShift.expected_cost,
        note:'The prior shift is an evaluator-supplied synthetic perturbation; no update to deployed method.'
      },
      new_probe_family:{
        generated_method:xorBorn,
        one_shot_full_classifier_exists:xorBorn.one_shot_baseline!==null,
        classical_baseline:classicalOptimum(xor,'expected')
      },
      withheld_permission:{status:refused.status,program:refused.program}
    },
    meta_question:{
      question:'Should the inquiry-method compiler optimize declared expected cost or worst-case cost when its prior may shift?',
      proposed_change:'RECOMPILE_WITH_WORST_CASE_OBJECTIVE',
      approved:false,empirically_superior_in_all_worlds:false,
      independent_admission_required:true
    },
    agent_ticket:{
      schema:'motif015.openmanus-implementation-ticket/v0',
      status:'PREPARED_NOT_EXECUTED',
      proposed_work:'Implement independent source-owner-reviewed tests for generated method cartridges; do not patch upstream organs.',
      scope:'disposable local workspace; synthetic data only; no network; no credentials',
      required_receipts:['actual source pins','negative transfer','failed permission case','classical baseline'],
      human_approval_required:true,model_execution_verified:false
    },
    source_repos_modified:false,
    no_real_actions:true,
    no_claim_recursive_self_improvement:true
  };
}
if(process.argv[1] && path.resolve(process.argv[1])===OWN)
  process.stdout.write(JSON.stringify(experiment(),null,2)+'\n');
