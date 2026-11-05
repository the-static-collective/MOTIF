// MOTIF-019 — The Hidden Common Ancestor.
// Pure synthetic inference of shared error factors, never a claim of lineage.
// Uses source-pinned original National Treasure and Dogram through MOTIF-018.
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {questionForWitness} from '../018/witness_machine.mjs';

const SELF=fileURLToPath(import.meta.url);
const ROW='motif019.synthetic-observation/v0';
const RECEIPT='motif019.common-ancestor-inquiry/v0';
const REPORTERS=['cedar','elm','pine','oak','birch','ash'];
const REFS=['reference_alpha','reference_beta'];
const FWER=0.05;
const NTESTS=REPORTERS.length*(REPORTERS.length-1); // 15 pairs x 2 strata = 30
const MIN_STRATUM=45;
const SOURCE_SCOPE='INVENTED_SIMULATED_ONLY';
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const other=x=>x==='yes'?'no':'yes';
const binary=x=>x==='yes'||x==='no';

function random(seed){
  let s=seed>>>0;
  return ()=>((s=(Math.imul(s,1664525)+1013904223)>>>0)/4294967296);
}
function config(kind){
  const known=['independent','hidden_ancestor','declared_copy','world_shift',
    'shared_difficulty','reference_collusion','weak_ancestor',
    'missing_reference','conflicting_reference','contradictory_copy','small_sample'];
  if(!known.includes(kind))throw Error('HOLD_UNKNOWN_SIMULATED_WORLD');
  return {
    kind,
    count:kind==='small_sample'?32:kind==='world_shift'?1200:900,
    prior:kind==='world_shift'?0.90:0.50
  };
}
function inventedReference(label,family){
  return {family,scope:SOURCE_SCOPE,label,identity_authenticated:false};
}
// This simulator is not an authenticated archive. Real origin assertions are
// impossible to derive from two reports alone.
export function simulate(kind='independent',seed=501){
  if(!Number.isSafeInteger(seed))throw Error('HOLD_BAD_SIMULATOR_SEED');
  const cfg=config(kind),rng=random(seed),records=[];
  const means={cedar:0.84,elm:0.84,pine:0.83,oak:0.82,birch:0.81,ash:0.85};
  for(let i=0;i<cfg.count;i++){
    const sample_id='specimen-'+String(i).padStart(5,'0');
    const truth=rng()<cfg.prior?'yes':'no';
    const hard=kind==='shared_difficulty'&&rng()<0.32;
    const rootWrong=(
      kind==='hidden_ancestor'||kind==='weak_ancestor'
    )&&rng()<(kind==='hidden_ancestor'?0.30:0.06);
    const rootLabel=rootWrong?other(truth):truth;
    let sharedCarrier;
    const colluded=kind==='reference_collusion'&&rng()<0.30;
    const proxy=colluded?other(truth):truth;
    for(const reporter of REPORTERS){
      let claim;
      if((kind==='declared_copy'||kind==='contradictory_copy')&&reporter==='elm'){
        claim=sharedCarrier;
      }else if((kind==='hidden_ancestor'||kind==='weak_ancestor')&&
               (reporter==='cedar'||reporter==='elm')){
        const copyChance=kind==='hidden_ancestor'?0.96:0.65;
        claim=rng()<copyChance?rootLabel:
          (rng()<0.84?truth:other(truth));
      }else{
        const accuracy=hard?0.34:means[reporter];
        claim=rng()<accuracy?truth:other(truth);
      }
      if(reporter==='cedar')sharedCarrier=claim;
      const refs=REFS.map(f=>inventedReference(proxy,f));
      if(kind==='missing_reference'&&i===0&&reporter==='cedar')
        refs.pop();
      if(kind==='conflicting_reference'&&i===0&&reporter==='cedar')
        refs[1]={...refs[1],label:other(proxy)};
      const parent=(kind==='declared_copy'||kind==='contradictory_copy')&&reporter==='elm'
        ?'cedar':null;
      const row={schema:ROW,source_scope:SOURCE_SCOPE,
        sample_id,reporter,carrier_claim:claim,declared_parent:parent,
        references:refs};
      records.push(row);
      if((kind==='declared_copy'||kind==='contradictory_copy')&&reporter==='elm'){
        records.push({...row,forwarded_copy_id:'extra-report-'+i});
        if(kind==='contradictory_copy'&&i===0){
          records.push({...row,carrier_claim:other(claim),
            forwarded_copy_id:'fabricated-divergence'});
        }
      }
    }
  }
  return {
    records,
    evaluator_only:{
      scenario:kind,
      actual_world_prevalence:cfg.prior,
      shared_literal_parent:kind==='hidden_ancestor' ||
        kind==='weak_ancestor'||kind==='declared_copy',
      common_item_difficulty_not_literal_lineage:kind==='shared_difficulty',
      reference_common_mode_corruption:kind==='reference_collusion',
      authenticated_real_ancestor:false
    }
  };
}
function assertRow(row){
  if(!row||row.schema!==ROW||row.source_scope!==SOURCE_SCOPE||
    !/^specimen-[0-9]{5}$/.test(row.sample_id)||
    !REPORTERS.includes(row.reporter)||!binary(row.carrier_claim)||
    !(row.declared_parent===null||
      (REPORTERS.includes(row.declared_parent)&&
       row.declared_parent!==row.reporter))||
    !Array.isArray(row.references)||row.references.length!==2)
    throw Error('HOLD_INVALID_OR_INCOMPLETE_SOURCE_PROVENANCE');
  const families=new Set();
  for(const ref of row.references){
    if(!ref||!REFS.includes(ref.family)||families.has(ref.family)||
      ref.scope!==SOURCE_SCOPE||!binary(ref.label)||
      ref.identity_authenticated!==false)
      throw Error('HOLD_UNAUTHENTICATED_REFERENCE_ORIGIN');
    families.add(ref.family);
  }
  if(row.references[0].label!==row.references[1].label)
    throw Error('HOLD_REFERENCE_WITNESSES_DISAGREE');
}
function inventory(records){
  if(!Array.isArray(records)||records.length<1||records.length>20000)
    throw Error('HOLD_INVALID_OBSERVATION_BOOK');
  const canonical=new Map(),refBook=new Map(),declaredParents=new Map();
  let copied=0;
  for(const row of records){
    assertRow(row);
    const key=row.sample_id+'|'+row.reporter;
    const previous=canonical.get(key);
    if(previous){
      if(previous.carrier_claim!==row.carrier_claim ||
         previous.declared_parent!==row.declared_parent||
         JSON.stringify(previous.references)!==JSON.stringify(row.references))
        throw Error('HOLD_CONTRADICTORY_SAME_ORIGIN_COPY');
      copied++;continue;
    }
    const refLabel=row.references[0].label;
    if(refBook.has(row.sample_id)&&refBook.get(row.sample_id)!==refLabel)
      throw Error('HOLD_CONFLICTING_REFERENCE_FOR_SPECIMEN');
    refBook.set(row.sample_id,refLabel);
    const old=declaredParents.get(row.reporter);
    if(old!==undefined&&old!==row.declared_parent)
      throw Error('HOLD_SOURCE_PARENT_CHANGED_WITHOUT_RECEIPT');
    declaredParents.set(row.reporter,row.declared_parent);
    canonical.set(key,row);
  }
  const samples=new Map();
  for(const row of canonical.values()){
    if(!samples.has(row.sample_id))samples.set(row.sample_id,new Map());
    samples.get(row.sample_id).set(row.reporter,row);
  }
  if([...samples.values()].some(m=>m.size!==REPORTERS.length))
    throw Error('HOLD_UNMATCHED_REPORTER_PANEL');
  for(const [name,parent] of declaredParents){
    if(!parent)continue;
    if(declaredParents.get(parent)!==null)
      throw Error('HOLD_UNSUPPORTED_MULTISTEP_OR_CYCLIC_LINEAGE');
    for(const specimen of samples.values()){
      if(specimen.get(name).carrier_claim!==specimen.get(parent).carrier_claim)
        throw Error('HOLD_DECLARED_COPY_DOES_NOT_MATCH_SOURCE');
    }
  }
  return {samples,declaredParents,copied};
}
// Exact one-sided Fisher/hypergeometric upper-tail test conditional on margins.
// Under stratum-wise independent IID reports, this controls false positive
// associations without guessing an arbitrary Pearson correlation threshold.
const logFactorial=[0];
function lf(n){
  for(let i=logFactorial.length;i<=n;i++){
    logFactorial.push(logFactorial[i-1]+Math.log(i));
  }
  return logFactorial[n];
}
const logChoose=(n,k)=>k<0||k>n?-Infinity:lf(n)-lf(k)-lf(n-k);
export function fisherUpperTail(n11,n10,n01,n00){
  const table=[n11,n10,n01,n00];
  if(table.some(x=>!Number.isSafeInteger(x)||x<0))
    throw Error('HOLD_BAD_CONTINGENCY_TABLE');
  const n=table.reduce((a,b)=>a+b,0);
  if(!n||n>20000)throw Error('HOLD_BAD_SAMPLE_SIZE');
  const row=n11+n10,col=n11+n01;
  const high=Math.min(row,col),low=Math.max(0,row+col-n);
  let sum=0;
  for(let k=n11;k<=high;k++){
    if(k<low)continue;
    const probability=Math.exp(
      logChoose(row,k)+logChoose(n-row,col-k)-logChoose(n,col));
    sum+=probability;
  }
  return Math.max(0,Math.min(1,sum));
}
function contingency(items,a,b,label){
  let n11=0,n10=0,n01=0,n00=0;
  for(const specimen of items.values()){
    const truth=specimen.get('cedar').references[0].label;
    if(truth!==label)continue;
    const x=Number(specimen.get(a).carrier_claim!==truth);
    const y=Number(specimen.get(b).carrier_claim!==truth);
    if(x&&y)n11++;
    else if(x)n10++;
    else if(y)n01++;
    else n00++;
  }
  const n=n11+n10+n01+n00;
  const e1=(n11+n10)/n,e2=(n11+n01)/n;
  const joint=n11/n,cov=joint-e1*e2;
  const p=n>0?fisherUpperTail(n11,n10,n01,n00):1;
  return {truth_label:label,n,n11,n10,n01,n00,
    error_rate_a:e1,error_rate_b:e2,joint_error_rate:joint,
    conditional_error_covariance:cov,
    one_sided_fisher_p:p,
    bonferroni_p:Math.min(1,p*NTESTS),
    significant_positive_error_dependence:n>=MIN_STRATUM&&p*NTESTS<FWER};
}
function disjointGroups(edges){
  const parent=new Map(REPORTERS.map(x=>[x,x]));
  const find=x=>{while(parent.get(x)!==x)x=parent.get(x);return x;};
  for(const e of edges){
    const x=find(e.a),y=find(e.b);
    if(x!==y)parent.set(y,x);
  }
  const groups=new Map();
  for(const x of REPORTERS){
    const root=find(x);
    if(!groups.has(root))groups.set(root,[]);
    groups.get(root).push(x);
  }
  return [...groups.values()].sort((a,b)=>a[0].localeCompare(b[0]));
}
export function questionGate(overrides={}){
  const d=questionForWitness({
    clue:'Are apparently independent testimony carriers downstream of one hidden source?',
    claim:'Agreement alone does not establish independent evidentiary lineage.',
    provenance_class:'speculation',
    support_confidence:'unsupported',
    ...overrides
  });
  return {
    schema:'motif019.ancestor-question-gate/v0',
    status:d.status,question_receipt:d.question_receipt,
    dogram_receipt:d.native_dogram_receipt,source_pins:d.donor_pins,
    no_external_actions:true
  };
}
export function investigate(records,gate){
  if(!gate||gate.schema!=='motif019.ancestor-question-gate/v0')
    throw Error('HOLD_MISSING_NATIONAL_TREASURE_GATE');
  if(gate.status!=='PROPOSE_SYNTHETIC_ONLY')
    return {schema:RECEIPT,status:'HOLD_SOURCE_QUESTION_FIRST',
      question_receipt:gate.question_receipt,math_invoked:gate.dogram_receipt!==null,
      no_external_actions:true};
  if(gate.question_receipt.aperture.id!=='discriminator'||
     Object.hasOwn(gate.question_receipt,'answer')||
     Object.hasOwn(gate.question_receipt,'conclusion')||
     gate.dogram_receipt?.source_blob!==gate.source_pins.dogram)
    throw Error('HOLD_ORIGINAL_ORGAN_CONTRACT');
  const book=inventory(records);
  const n=book.samples.size;
  const labelCounts={yes:0,no:0};
  for(const specimen of book.samples.values())
    labelCounts[specimen.get('cedar').references[0].label]++;
  if(Object.values(labelCounts).some(c=>c<MIN_STRATUM))
    return {schema:RECEIPT,status:'HOLD_UNDERPOWERED_REFERENCE_STRATUM',
      sample_count:n,reference_label_counts:labelCounts,
      minimum_per_label:MIN_STRATUM,question_receipt:gate.question_receipt,
      no_external_actions:true};
  const pairs=[],suspected=[],declared=[];
  for(let i=0;i<REPORTERS.length;i++){
    for(let j=i+1;j<REPORTERS.length;j++){
      const a=REPORTERS[i],b=REPORTERS[j];
      const strata=['yes','no'].map(label=>
        contingency(book.samples,a,b,label));
      const isDeclared=book.declaredParents.get(a)===b||
        book.declaredParents.get(b)===a;
      const both=strata.every(r=>r.significant_positive_error_dependence);
      const relation=isDeclared?'DECLARED_SAME_CARRIER':
        both?'SUSPECT_SHARED_ERROR_FACTOR':
        strata.some(r=>r.significant_positive_error_dependence)?
         'PARTIAL_CONDITIONAL_DEPENDENCE':'NO_DETECTABLE_PAIR_DEPENDENCE';
      const line={a,b,relation,strata,
        diagnosed_literal_common_ancestor:false,
        pairwise_test_not_a_genealogy_proof:true};
      pairs.push(line);
      if(isDeclared)declared.push({a,b,relation:'DECLARED_SAME_CARRIER'});
      if(both&&!isDeclared)suspected.push({a,b,
        relation:'SUSPECT_SHARED_ERROR_FACTOR',
        min_adjusted_p:Math.max(...strata.map(s=>s.bonferroni_p))});
    }
  }
  const inferredEdges=[...declared,...suspected];
  const conservative=disjointGroups(inferredEdges);
  const body={
    schema:RECEIPT,status:'HOLD_FOR_SOURCE_GENEALOGY_REVIEW',
    study_scope:'SYNTHETIC_DECLARED_REFERENCE_COHORT',
    original_national_treasure_question:gate.question_receipt.question,
    original_national_treasure_aperture:gate.question_receipt.aperture.id,
    original_dogram_pin:gate.dogram_receipt.source_blob,
    declared_source_pins:gate.source_pins,
    sample_count:n,reference_label_counts:labelCounts,
    reporters:[...REPORTERS],raw_reporter_count:REPORTERS.length,
    forwarded_duplicate_count:book.copied,
    declared_same_carrier_links:declared,
    statistically_suspected_shared_failure_links:suspected,
    all_pairwise_tests:pairs,
    conservative_evidentiary_groups:conservative,
    conservative_group_count:conservative.length,
    evidence_grouping_is_a_precaution_not_verified_genealogy:true,
    audit:{
      procedure:'STRATIFIED_EXACT_FISHER_UPPER_TAIL',
      hypotheses:'POSITIVE_PAIRWISE_ERROR_ASSOCIATION_GIVEN_REFERENCE_LABEL',
      predeclared_tests:NTESTS,alpha_familywise:FWER,
      multiple_test_correction:'BONFERRONI',
      minimum_cases_per_reference_label:MIN_STRATUM,
      within_stratum_independence_of_specimens_assumed:true,
      reference_labels_assumed_correct_NOT_VERIFIED:true
    },
    no_independence_certified_from_non_significance:true,
    no_causal_ancestry_identification_from_observational_dependence:true,
    real_reference_independence_authenticated:false,
    no_upstream_mutations:true,external_actions:0,
    no_evidence_promoted_to_truth:true
  };
  return {...body,checksum_sha256:hash(body)};
}
export function validateReceipt(receipt){
  if(!receipt||receipt.schema!==RECEIPT||
     receipt.status!=='HOLD_FOR_SOURCE_GENEALOGY_REVIEW'||
     receipt.external_actions!==0||
     receipt.no_upstream_mutations!==true||
     typeof receipt.checksum_sha256!=='string')
    throw Error('HOLD_INVALID_COMMON_ANCESTOR_RECEIPT');
  const {checksum_sha256,...body}=receipt;
  if(hash(body)!==checksum_sha256)
    throw Error('HOLD_TAMPERED_COMMON_ANCESTOR_RECEIPT');
  return true;
}
export function proposedDiscriminators(receipt,budget=1.5){
  validateReceipt(receipt);
  if(typeof budget!=='number'||!Number.isFinite(budget)||budget<0||budget>10)
    throw Error('HOLD_INVALID_DISCRIMINATOR_BUDGET');
  const links=receipt.statistically_suspected_shared_failure_links;
  const actions=[],used=new Set();let left=budget;
  // Challenge the declared reference family FIRST. Without that check,
  // an observationally strong common-error correlation may be a false
  // genealogy caused by two jointly corrupted reference streams.
  if(left>=0.5){
    actions.push({
      kind:'PROPOSE_THIRD_INDEPENDENT_REFERENCE_FAMILY',
      cost:0.5,
      question:'What independently adjudicated reference could reveal common-mode failure in both current references?',
      suggested_without_access_to_original_sources:true,
      purpose:'CHALLENGE_REFERENCE_COLLUSION'
    });
    left-=0.5;
  }
  // Next ask for original carrier custody. Never infer literal ancestry
  // from a conditional dependence edge or content hash.
  for(const link of links){
    if(actions.length>=2)break;
    const key=[link.a,link.b].sort().join('|');
    if(used.has(key)||left<0.6)continue;
    used.add(key);
    actions.push({
      kind:'PROPOSE_ORIGINAL_CARRIER_PROVENANCE_REVIEW',
      pair:[link.a,link.b],cost:0.6,
      question:'What independently recoverable originals, custody transfers, or source-family traces distinguish these two reports?',
      suggested_without_access_to_original_sources:true,
      purpose:'DISCRIMINATE_LITERAL_ANCESTRY_FROM_SHARED_ENVIRONMENT_OR_REFERENCE_ERROR'
    });
    left-=0.6;
  }
  return {
    schema:'motif019.inquiry-plan/v0',
    status:actions.length?'PROPOSE_SYNTHETIC_DISCRIMINATORS':'HOLD_BUDGET',
    actions,spent:budget-left,unspent:left,
    evidence_admitted:false,human_review_required:true,
    no_real_probes_executed:true
  };
}
export function study(){
  const gate=questionGate();
  const gap=questionGate({source_locator:''});
  const cases=['independent','hidden_ancestor','declared_copy','world_shift',
    'shared_difficulty','reference_collusion','weak_ancestor',
    'small_sample','conflicting_reference','missing_reference'];
  const specimen_results={};
  for(const kind of cases){
    const data=simulate(kind,643);
    try{
      const r=investigate(data.records,gate);
      specimen_results[kind]=r.status==='HOLD_FOR_SOURCE_GENEALOGY_REVIEW'?
        {status:r.status,
          declared_links:r.declared_same_carrier_links,
          suspected_links:r.statistically_suspected_shared_failure_links,
          group_count:r.conservative_group_count,
          audit_plan:proposedDiscriminators(r)}:
        {status:r.status};
    }catch(err){
      if(!String(err.message).startsWith('HOLD_'))throw err;
      specimen_results[kind]={status:err.message};
    }
  }
  const multi_seed={};
  for(const kind of ['independent','hidden_ancestor','world_shift',
    'shared_difficulty','reference_collusion','weak_ancestor']){
    let anythingFlagged=0,cedarElmFlagged=0,totalLinks=0;
    for(let seed=100;seed<112;seed++){
      const r=investigate(simulate(kind,seed).records,gate);
      const pairs=r.statistically_suspected_shared_failure_links;
      if(pairs.length)anythingFlagged++;
      if(pairs.some(x=>x.a==='cedar'&&x.b==='elm'))cedarElmFlagged++;
      totalLinks+=pairs.length;
    }
    multi_seed[kind]={trials:12,any_flag_trials:anythingFlagged,
      cedar_elm_flag_trials:cedarElmFlagged,
      mean_suspected_links:totalLinks/12};
  }
  const gateHold=investigate(simulate('independent',643).records,gap);
  return {
    schema:'motif019.hidden-common-ancestor-study/v0',
    status:'EXPERIMENTAL_UNADMITTED_SYNTHETIC_STUDY',
    genuine_native_organs:{
      national_treasure_question:gate.question_receipt.question,
      dogram_schema:gate.dogram_receipt?.schema,
      dogram_source_blob:gate.dogram_receipt?.source_blob,
      upstream_pins:gate.source_pins
    },
    missing_source_refusal:{status:gateHold.status,
      native_dogram_was_invoked:gateHold.math_invoked},
    fixed_synthetic_scenarios:specimen_results,
    preregistered_seed_sweep:multi_seed,
    essential_negative_results:[
      'shared item difficulty can mimic a literal common ancestor',
      'two colluding reference feeds can manufacture apparent reporter dependence',
      'absence of detection does not establish independent origin',
      'a declared lineage claim is not authenticated original-source custody'
    ],
    followup_question:'Which new independently sourced carrier or controlled observation can distinguish shared ancestry from merely shared errors?',
    actual_source_owners_modified:false,
    source_authentication_performed:false,
    openmanus_execution:false,
    real_world_actions:0
  };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF)
  process.stdout.write(JSON.stringify(study(),null,2)+'\n');
