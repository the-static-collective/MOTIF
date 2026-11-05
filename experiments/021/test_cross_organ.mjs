import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {researchPacket} from './alex-snapshot/tools/motif021-search.mjs';
import {makePlan,solve,validatePacket} from
 './planz-snapshot/scripts/motif-classical.mjs';
import {composeCandidate} from './graft-snapshot/src/motif021-composer.mjs';
import {verifySourceOrgans,runResearchCycle} from './cross_organ.mjs';
const raw=readFileSync(new URL('./alex-snapshot/research/packets/MOTIF-021/research-packet.json',import.meta.url));
const rawPlan=readFileSync(new URL('./planz-snapshot/plans/MOTIF-021-classical.json',import.meta.url));

test('actual exact source code and data from three donor owners are pinned before use',()=>{
 const pins=verifySourceOrgans();
 assert.equal(Object.keys(pins.files).length,16);
 assert.equal(pins.files['alex-snapshot/tools/motif021-search.mjs'],
  '95e4b0ea003550d0442e800a72289cf2f8698446');
 assert.equal(pins.files['planz-snapshot/scripts/motif-classical.mjs'],
  '22d75c26039e5783b59cf71be02982428603128c');
 assert.equal(pins.files['graft-snapshot/src/motif021-composer.mjs'],
  '423496e4eba46715839621cc51e024bd238aedf3');
});
test('ALEX actually scans five pinned public source documents, with observable limits',()=>{
 const x=researchPacket();
 assert.deepEqual(x,JSON.parse(raw));
 assert.equal(x.hits.length,12);
 assert.equal(x.source_inventory.length,5);
 assert.equal(x.search_observation.coverage_status,'PARTIAL');
 assert.equal(x.restrictions.actual_external_repository_search_run,false);
 assert.equal(x.restrictions.evidence_admission,'NONE');
});
test('original planZ classical optimizer searches and ties stored optimal cost',()=>{
 const x=researchPacket(),p=makePlan(x,raw);
 assert.equal(validatePacket(x,raw).hit_count,12);
 assert.equal(solve().cost,9);
 assert.equal(p.total_declared_cost,9);
 assert.deepEqual(p,JSON.parse(rawPlan));
 assert.equal(p.status,'HELD_PLAN_NOT_EXECUTED');
 assert.equal(p.externally_executed_steps,0);
});
test('GRAFT composer actually checks source receipts, produces deterministic executable JS',()=>{
 const x=composeCandidate(raw,rawPlan);
 assert.equal(x.status,'EXECUTABLE_CANDIDATE_HELD_FOR_OWNER_REVIEW');
 assert.equal(x.authority,'none');
 assert.equal(x.external_effects,0);
 assert.equal(x.generated_module,'generated/motif021-source-review.mjs');
 assert.ok(x.source.includes('executePublicSourceReview'));
 assert.ok(x.source.includes('executeLineageCaution'));
 assert.equal(x.production_install,false);
});
test('an altered ALEX packet or held classical plan cannot be smuggled into GRAFT',()=>{
 assert.throws(()=>composeCandidate(Buffer.concat([raw,Buffer.from(' ')]),rawPlan),
  /STALE_OR_TAMPERED_SOURCE_CUT/);
 assert.throws(()=>composeCandidate(raw,Buffer.concat([rawPlan,Buffer.from(' ')])),
  /STALE_OR_TAMPERED_SOURCE_CUT/);
});
test('full runtime crossing invokes original Maxhinal and both executable GRAFT products',()=>{
 const result=runResearchCycle();
 assert.equal(result.status,'EXECUTED_LOCAL_FROZEN_PUBLIC_RESEARCH_ONLY');
 assert.equal(result.verified_source_blob_count,16);
 assert.equal(result.originating_motif.original_madd_operation_count,8);
 assert.equal(result.alex_search.hit_count,12);
 assert.equal(result.planz_classical.true_classical_optimal_cost,9);
 assert.equal(result.graft_compilation.generated_code_is_executed,true);
 assert.equal(result.graft_compilation.output_public_source_review.cited_candidate_claims.length,5);
 assert.equal(result.graft_compilation.output_lineage_caution.original_source_custody_proved,false);
 assert.equal(result.no_evidence_laundering,true);
 assert.equal(result.no_production_deployment,true);
});
test('loop is reproducible without a remote model or live network',()=>{
 assert.deepEqual(runResearchCycle(),runResearchCycle());
});
test('research plans, executable candidates and original witness sources never inherit authority',()=>{
 const r=runResearchCycle();
 assert.equal(r.dynamic_network_search_executed,false);
 assert.equal(r.persistent_cross_repo_write_performed_at_runtime,false);
 assert.equal(r.real_human_evidence_accessed,false);
 assert.equal(r.actual_owner_admission,false);
 assert.equal(r.graft_compilation.source_owner_approval,false);
 assert.equal(r.graft_compilation.output_public_source_review.external_actions,0);
 assert.equal(r.planz_classical.externally_executed_planned_actions,0);
});
