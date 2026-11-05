// MOTIF-021 — Actual source-pinned ALEX search → planZ classical planner
// → GRAFT compiled executable candidate, informed by MOTIF-019/020.
// Frozen public materializations only: NOT a live cross-app daemon.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {researchPacket} from './alex-snapshot/tools/motif021-search.mjs';
import {makePlan,validateSavedPlan,solve} from
 './planz-snapshot/scripts/motif-classical.mjs';
import {composeCandidate} from './graft-snapshot/src/motif021-composer.mjs';
import {executePublicSourceReview,executeLineageCaution}
 from './graft-snapshot/generated/motif021-source-review.mjs';
import {simulate,questionGate,investigate} from '../019/common_ancestor.mjs';
import {runMaxhinal,hypothesisQuestionBundle} from '../020/madd_custody.mjs';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const SELF=fileURLToPath(import.meta.url);
const read=(name)=>readFileSync(path.join(HERE,name));
const gitBlob=bytes=>createHash('sha1').update(
 Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');

export function verifySourceOrgans(){
 const manifest=JSON.parse(read('pins.json'));
 if(manifest.schema!=='motif021.pinned-organ-snapshots/v0' ||
   Object.keys(manifest.files).length!==16)
  throw Error('HOLD_MISSING_SOURCE_ORGAN_PINSET');
 for(const [file,expected] of Object.entries(manifest.files)){
   if(!/^(alex-snapshot|planz-snapshot|graft-snapshot)\//.test(file)||
      !/^[0-9a-f]{40}$/.test(expected)||
      gitBlob(read(file))!==expected)
    throw Error('HOLD_SOURCE_ORGAN_BYTES_CHANGED_'+file);
 }
 return manifest;
}
export function runResearchCycle(){
 const pins=verifySourceOrgans();
 // Actual ALEX search scans five exact checked full public Markdown files.
 const alex=researchPacket();
 const rawAlex=read('alex-snapshot/research/packets/MOTIF-021/research-packet.json');
 if(JSON.stringify(alex)!==JSON.stringify(JSON.parse(rawAlex)))
  throw Error('HOLD_ALEX_SEARCH_AND_SAVED_RECEIPT_DIVERGE');

 // Actual classical search with explicitly modeled preconditions/effects.
 const plan=makePlan(alex,rawAlex);
 const rawPlan=read('planz-snapshot/plans/MOTIF-021-classical.json');
 if(JSON.stringify(plan)!==JSON.stringify(JSON.parse(rawPlan)))
  throw Error('HOLD_PLANNER_AND_SAVED_PLAN_DIVERGE');
 validateSavedPlan(plan,alex,rawAlex);

 // Actual GRAFT composer verifies the exact two source cuts, the original
 // planZ program and the closed preapproved recipe before giving us JS.
 const composed=composeCandidate(rawAlex,rawPlan);
 if(composed.source!==read('graft-snapshot/generated/motif021-source-review.mjs').toString('utf8'))
  throw Error('HOLD_COMPILED_GRAFT_MODULE_DIVERGED');
 const capabilityReview=executePublicSourceReview(alex,rawAlex,plan);
 const lineage=executeLineageCaution(alex,rawAlex,plan);

 // The preserved earlier MOTIF organs still run independently, on synthetic
 // 019 data; the research search was prepared as a frozen, bounded lead.
 const gate=questionGate();
 const shared=investigate(simulate('hidden_ancestor',643).records,gate);
 const maxhinal=runMaxhinal(shared,'main','motif021-chain');
 const challenges=hypothesisQuestionBundle(shared,maxhinal.ride);
 return {
  schema:'motif021.four-organ-source-inquiry-run/v0',
  status:'EXECUTED_LOCAL_FROZEN_PUBLIC_RESEARCH_ONLY',
  donor_ref_heads:pins.branches,
  verified_source_blob_count:Object.keys(pins.files).length,
  originating_motif:{
    native_019_source_receipt_sha256:shared.checksum_sha256,
    original_maxhinal_ride_id:maxhinal.ride.ride_id,
    original_maxhinal_ride_sha256:digest(JSON.stringify(maxhinal.ride)),
    original_madd_operation_count:maxhinal.ride.operations.length,
    unresolved_source_custody_question:challenges.required_next_action
  },
  alex_search:{
    packet_id:alex.packet_id,
    original_git_blob:pins.files['alex-snapshot/research/packets/MOTIF-021/research-packet.json'],
    scope:alex.search_observation.coverage_status,
    source_count:alex.source_inventory.length,
    hit_count:alex.hits.length,
    findings:alex.research_findings.map(x=>({
      claim:x.claim,classification:x.status,source_ids:x.source_ids
    }))
  },
  planz_classical:{
    plan_id:plan.plan_id,
    plan_source_git_blob:pins.files['planz-snapshot/plans/MOTIF-021-classical.json'],
    true_classical_optimal_cost:solve().cost,
    actions:plan.actions,
    status:plan.status,
    externally_executed_planned_actions:0
  },
  graft_compilation:{
    capability_id:composed.capability_id,
    generated_module_sha256:composed.generated_source_sha256,
    generated_code_is_executed:true,
    source_owner_approval:false,
    executable_candidate_status:composed.status,
    output_public_source_review:capabilityReview,
    output_lineage_caution:lineage
  },
  missing_deeper_capabilities:[
   'live unrestricted ALEX crawling',
   'real authenticated third-party original source custody',
   'remote cross-app writable scheduled runtime',
   'owner-approved independent code promotion or deployment'
  ],
  dynamic_network_search_executed:false,
  persistent_cross_repo_write_performed_at_runtime:false,
  real_human_evidence_accessed:false,
  actual_owner_admission:false,
  no_evidence_laundering:true,no_production_deployment:true
 };
}
if(process.argv[1]&&path.resolve(process.argv[1])===SELF)
 process.stdout.write(JSON.stringify(runResearchCycle(),null,2)+'\n');
