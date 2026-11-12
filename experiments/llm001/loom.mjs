/* LLM-001. Dependency-free, OFFLINE, synthetic branch compiler.
 * This is not native MOTIF-003, a trained language model, a safety certifier,
 * or a real-world actuator. Verification source is an independent test owner.
 * Three boundaries: observed state, model PENCIL proposal, owner TEST receipt.
 */
const copy = x => JSON.parse(JSON.stringify(x));
const unique = xs => new Set(xs).size === xs.length;
const stable = x => JSON.stringify(x, (key,value) => (value && typeof value==='object' && !Array.isArray(value)) ? Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b))) : value);
function keyOf(x) {
  // A deterministic NON-CRYPTOGRAPHIC memoization label. Never a provenance proof.
  const s=stable(x); let h=2166136261;
  for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619)>>>0;
  return 'cache-only:'+s.length+':'+h.toString(16);
}
function valid(w) {
  if(!w || w.schema!=='motif.llm001.world.v0' || typeof w.id!=='string' || !Array.isArray(w.facts) || !unique(w.facts) ||
     !Array.isArray(w.unknown) || !unique(w.unknown) || !Array.isArray(w.evidence) || !Array.isArray(w.moves) ||
     !Array.isArray(w.history) || w.moves.length>100 || w.evidence.length>100 ||
     !w.facts.every(x=>typeof x==='string'&&x.length<120) || !w.unknown.every(x=>typeof x==='string'&&x.length<120) ||
     w.facts.some(f=>w.unknown.includes(f)))throw Error('INVALID_WORLD');
  if(!unique(w.evidence.map(e=>e.id))||!unique(w.moves.map(m=>m.id)))throw Error('DUPLICATE_ID');
  for(const e of w.evidence) {
    if(!e || typeof e.id!=='string' || typeof e.root!=='string'||!e.root||
       !['observed','unknown','assumed'].includes(e.kind)|| typeof e.fact!=='string' ||
       (e.kind==='observed'&&!w.facts.includes(e.fact)) ||
       (e.kind==='unknown'&&!w.unknown.includes(e.fact)) ||
       (e.kind==='assumed'&&w.facts.includes(e.fact)))throw Error('INVALID_EVIDENCE');
  }
  for(const m of w.moves) {
    if(!m || typeof m.id!=='string' || !Array.isArray(m.requires)||!Array.isArray(m.may_grant)||
       !unique(m.requires)||!unique(m.may_grant)||!m.requires.every(f=>typeof f==='string')||
       !m.may_grant.every(f=>typeof f==='string')||
       !['probe','simulate','external'].includes(m.kind)||!Number.isFinite(m.immediate)||m.immediate<0||
       m.requires.length>20||m.may_grant.length>20)throw Error('INVALID_MOVE');
  }
  return w;
}
function available(w) {
  valid(w);
  const state=new Set(w.facts);
  return w.moves.filter(m=>m.kind!=='external'&&m.requires.every(x=>state.has(x)));
}
function imagined(w,move) {
  const out=copy(w);
  out.facts=[...new Set([...out.facts,...move.may_grant])].sort();
  out.unknown=out.unknown.filter(x=>!out.facts.includes(x));
  out.evidence=out.evidence.filter(e=>e.kind!=='unknown'||!out.facts.includes(e.fact));
  // Crucial: imagined facts are NEVER written as observed testimony.
  return out;
}
function search(w,goal,depth=3) {
  valid(w);if(depth>8||depth<0)throw Error('BAD_DEPTH');
  const q=[[w,[]]],seen=new Set([w.facts.slice().sort().join('|')]);
  while(q.length) {
    const [world,path]=q.shift();
    if(goal.every(f=>world.facts.includes(f)))return path;
    if(path.length===depth)continue;
    for(const m of available(world)) {
      const next=imagined(world,m),id=next.facts.slice().sort().join('|');
      if(!seen.has(id)){seen.add(id);q.push([next,[...path,m.id]]);}
    }
  }
  return null;
}
function rank(w,mode='affordance',goal=[],depth=3) {
  valid(w);if(!['greedy','affordance','classical'].includes(mode))throw Error('BAD_MODE');
  const choices=available(w), old=new Set(choices.map(m=>m.id));
  const rows=choices.map(m=>{
    const future=imagined(w,m),newChoices=available(future).filter(x=>!old.has(x.id)).map(x=>x.id).sort();
    const path=search(future,goal,Math.max(depth-1,0));
    return {id:m.id,immediate:m.immediate,new_choices:newChoices,goal_distance:path?path.length+1:Infinity,route:path?[m.id,...path]:null};
  });
  rows.sort((a,b)=>mode==='greedy'?(b.immediate-a.immediate||a.id.localeCompare(b.id)):
    mode==='affordance'?(b.new_choices.length-a.new_choices.length||b.immediate-a.immediate||a.id.localeCompare(b.id)):
    (a.goal_distance-b.goal_distance||b.immediate-a.immediate||a.id.localeCompare(b.id)));
  return {mode,preferred:rows[0]||null,rows};
}
function frontier(w) {
  // Two-step opportunity set, including options reachable after one
  // conditional successful hypothetical action. Never observed effects.
  const ids=new Set(available(w).map(m=>m.id));
  for(const m of available(w))for(const f of available(imagined(w,m)))ids.add(f.id);
  return ids;
}
function counterfactualImpact(w,e) {
  // Source-anchored estimate of how much ONE fact changes the safe frontier.
  // This is decision-value *structure*, not actual information gain or value.
  const other=copy(w);
  if(e.kind==='observed') {
    other.facts=other.facts.filter(x=>x!==e.fact);
    other.unknown=[...new Set([...other.unknown,e.fact])];
    other.evidence=other.evidence.filter(x=>!(x.kind==='observed'&&x.fact===e.fact));
  } else {
    other.facts=[...new Set([...other.facts,e.fact])];
    other.unknown=other.unknown.filter(x=>x!==e.fact);
    other.evidence=other.evidence.filter(x=>!(x.kind==='unknown'&&x.fact===e.fact));
  }
  const a=frontier(w),b=frontier(other);
  return [...new Set([...a,...b])].filter(x=>a.has(x)!==b.has(x)).length;
}
function compile(w,{budget=8,goal=[]}={}) {
  valid(w);if(!Number.isInteger(budget)||budget<1||budget>100)throw Error('BAD_BUDGET');
  // A witness's shared root is ONE origin regardless of the number of claims.
  const origin=new Set(),selected=[],omitted=[];
  const scored=w.evidence.map(e=>({...e,counterfactual_action_impact:counterfactualImpact(w,e)}));
  const evidence=scored.sort((a,b)=>
    b.counterfactual_action_impact-a.counterfactual_action_impact||
    ((b.kind==='unknown'?1:0)-(a.kind==='unknown'?1:0))||
    a.id.localeCompare(b.id));
  for(const e of evidence) {
    if(origin.has(e.root)){omitted.push({id:e.id,reason:'SAME_ORIGIN'});continue;}
    origin.add(e.root);
    if(selected.length<budget)selected.push(copy(e));
    else omitted.push({id:e.id,reason:'BUDGET'});
  }
  const omittedHard=omitted.some(e=>e.reason==='BUDGET'&&w.evidence.some(a=>a.id===e.id&&a.kind==='unknown'));
  const choices=rank(w,'affordance',goal).rows.map(row=>({id:row.id,new_choices:row.new_choices,hypothetical_goal_distance:Number.isFinite(row.goal_distance)?row.goal_distance:null}));
  const packet={
    schema:'motif.llm001.prompt.v0',task:'Propose ONE reversible, source-cited probe or simulated next move. Not an answer or a real act.',
    world_id:w.id,observed_facts:[...w.facts],unknown_facts:[...w.unknown],
    witnesses:selected,possible_moves:choices,
    prohibitions:['No real-world act','No promotion of PENCIL','No measurement/consent claim without owner receipt','No new facts from generation'],
    output_contract:{action_id:'one possible_moves.id',cite:['existing witness id'],hypothesis:'text <= 300 chars'},
    withheld_evidence_count:omitted.length,
    status:omittedHard?'HOLD_MISSING_UNKNOWNS':'READY_FOR_PENCIL',
  };
  return {packet,cache_key:keyOf({facts:w.facts,unknown:w.unknown,selected,choices,goal}),
          pseudo_tokens:Math.ceil(stable(packet).length/4),omitted};
}
function gate(w,compiled,proposal) {
  valid(w);
  if(compiled?.packet?.status!=='READY_FOR_PENCIL'||compiled.packet.world_id!==w.id)return {status:'HOLD_CONTEXT'};
  if(!proposal||typeof proposal.action_id!=='string'||!Array.isArray(proposal.cite)||
     proposal.cite.length<1||!unique(proposal.cite)||!proposal.cite.every(x=>typeof x==='string')||
     typeof proposal.hypothesis!=='string'||proposal.hypothesis.length>300)return {status:'REJECT_FORMAT'};
  const ids=new Set(compiled.packet.witnesses.map(e=>e.id));
  if(!proposal.cite.every(id=>ids.has(id)))return {status:'REJECT_UNSOURCED'};
  const move=available(w).find(m=>m.id===proposal.action_id);
  if(!move)return {status:'REJECT_NOT_AVAILABLE'};
  return {status:'PENCIL_REVIEW_ONLY',proposal:copy(proposal),world_id:w.id,cache_key:compiled.cache_key,
    receipt:'NO_STATE_CHANGE'};
}
function ownerTest(w,held,receipt) {
  valid(w);
  if(held?.status!=='PENCIL_REVIEW_ONLY'||held.world_id!==w.id||
     !receipt||receipt.authority!=='INDEPENDENT_SYNTHETIC_TEST_OWNER'||
     typeof receipt.id!=='string'||receipt.id.length<3||
     receipt.action_id!==held.proposal.action_id||typeof receipt.passed!=='boolean'||
     !Array.isArray(receipt.grants)||!unique(receipt.grants)||
     w.history.some(h=>h.receipt_id===receipt.id))throw Error('RECEIPT_HOLD');
  const move=available(w).find(m=>m.id===receipt.action_id);
  if(!move||receipt.grants.some(f=>!move.may_grant.includes(f))||
     (!receipt.passed&&receipt.grants.length))throw Error('RECEIPT_HOLD');
  const next=copy(w);
  if(receipt.passed) {
    next.facts=[...new Set([...next.facts,...receipt.grants])].sort();
    next.unknown=next.unknown.filter(x=>!next.facts.includes(x));
    next.evidence=next.evidence.filter(e=>e.kind!=='unknown'||!next.facts.includes(e.fact));
    // Simulated receipts are not real observations. Never relabel them as actual field evidence.
    for(const fact of receipt.grants)next.evidence.push({id:'sim-'+receipt.id+'-'+fact,root:'sim-owner-'+receipt.id,kind:'observed',fact});
  }
  next.history.push({receipt_id:receipt.id,action_id:receipt.action_id,passed:receipt.passed,
    grants:[...receipt.grants],authority:'INDEPENDENT_SYNTHETIC_TEST_OWNER',scope:'SIMULATION_ONLY'});
  valid(next);
  return next;
}
function field014Aperture(exported) {
  if(!exported||exported.schema!=='motif.field014.v1'||!Array.isArray(exported.events)||
     !exported.scale||typeof exported.scale.kind!=='string')throw Error('NOT_FIELD014');
  return {source_branch:'experiment/field-014-reality-has-depth-20261112',
    source_commit:'5f1f0ddca303616a4fd1805522c58a45baff934e',
    source_kind:'UNMERGED_SEPARATE_DIAGRAM',events:exported.events.length,
    measured_reference:exported.scale.kind==='conditional_reference'&&
      Number.isFinite(exported.scale.meters_per_unit)&&exported.scale.meters_per_unit>0,
    physical_load_certified:false,photo_to_yard_pose_certified:false,assembly_authorized:false};
}
// Explicitly not executable model inference. A model adapter must call compile,
// parse structured output, and pass it through gate; ownerTest stays separate.
export {valid,available,imagined,search,rank,frontier,counterfactualImpact,compile,gate,ownerTest,field014Aperture,keyOf};
