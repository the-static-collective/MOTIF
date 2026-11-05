import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verifyPinnedOrgans,runQuestion,demonstration,QUESTIONS} from './next_question.mjs';
import {ask,validate as validateAlex} from './alex-snapshot/tools/motif022-question.mjs';
import {planQuestion,validatePlan} from './planz-snapshot/scripts/motif022-plan.mjs';
import {compileCapability} from './graft-snapshot/src/motif022-inquiry-compiler.mjs';

test('three new source-owner organs are actual unchanged Git blob code',()=>{
 const p=verifyPinnedOrgans();
 assert.equal(Object.keys(p.source_code_blobs).length,7);
 assert.equal(p.source_code_blobs['alex-snapshot/tools/motif022-question.mjs'],
  'c6e1a03d2765a0ab6dc480432db76a276f8f3ae9');
 assert.equal(p.source_code_blobs['planz-snapshot/scripts/motif-classical.mjs'],
  '22d75c26039e5783b59cf71be02982428603128c');
 assert.equal(p.source_code_blobs['graft-snapshot/src/motif022-inquiry-compiler.mjs'],
  'ecab7f890873adcfbf5ebc700b43e041806e1fdd');
});
test('new question one executes original ALEX + classical plan + compiled lineage module',()=>{
 const r=runQuestion(QUESTIONS[0]);
 assert.equal(r.status,'EXECUTED_LOCAL_HELD_CAPABILITY');
 assert.equal(r.planz_plan.intent,'LINEAGE');
 assert.ok(r.planz_plan.actions.includes('TRACE_ORIGINAL_PROVENANCE'));
 assert.equal(r.executed_capability.mode,'LINEAGE');
 assert.ok(r.alex_packet.hits.length>0);
 assert.ok(r.alex_packet.hits.every(h=>h.line>0&&h.source_blob.length===40));
 assert.equal(r.executed_capability.source_custody_verified,false);
 assert.equal(r.generated_capability.compilation_kind,'FINITE_ALLOWLIST_TEMPLATE');
});
test('new question two selects different optimized plan and a different executable module',()=>{
 const a=runQuestion(QUESTIONS[0]),b=runQuestion(QUESTIONS[1]);
 assert.equal(b.planz_plan.intent,'COMPOSITION');
 assert.ok(b.planz_plan.actions.includes('COMPOSE_ALLOWED_RECIPE'));
 assert.equal(b.executed_capability.mode,'COMPOSITION');
 assert.notDeepEqual(a.alex_packet.hits,b.alex_packet.hits);
 assert.notDeepEqual(a.planz_plan.actions,b.planz_plan.actions);
 assert.notEqual(a.generated_capability.source_sha256,b.generated_capability.source_sha256);
 assert.ok(b.planz_plan.cost<a.planz_plan.cost);
});
test('new question three selects a distinct source-trust investigation',()=>{
 const r=runQuestion(QUESTIONS[2]);
 assert.equal(r.planz_plan.intent,'RELIABILITY');
 assert.equal(r.executed_capability.mode,'RELIABILITY');
 assert.ok(r.planz_plan.actions.includes('TEST_INDEPENDENT_REPORTS'));
 assert.ok(r.executed_capability.questions.some(q=>q.includes('upstream failure')));
 assert.equal(r.external_actions,0);
 assert.equal(r.real_world_search_executed,false);
});
test('unknown evidence produces a true HOLD, no fake plan or compiled program',()=>{
 const r=runQuestion(QUESTIONS[3]);
 assert.equal(r.status,'HOLD_NO_RELEVANT_SOURCE_MATERIAL');
 assert.equal(r.alex_packet.status,'HOLD_NO_MATCHES');
 assert.equal(r.planz_plan.status,'HOLD_NO_SOURCED_LEADS');
 assert.equal(r.generated_capability,null);
 assert.equal(r.executed_capability,null);
});
test('all source owner contracts reject edited source evidence or unauthorized promotion',()=>{
 const p=runQuestion(QUESTIONS[0]);
 assert.equal(validateAlex(p.alex_packet),true);
 assert.equal(validatePlan(p.planz_plan,p.alex_packet),true);
 assert.throws(()=>validateAlex({...p.alex_packet,question:'altered'}),/CHANGED/);
 assert.throws(()=>validatePlan({...p.planz_plan,cost:0},p.alex_packet),/NOT_REPLAYABLE/);
 assert.throws(()=>compileCapability(p.alex_packet,{
  ...p.planz_plan,no_owner_approval:false}),/UNADMITTED/);
});
test('multiple new questions are deterministic and never inherit owner authority',()=>{
 assert.deepEqual(runQuestion(QUESTIONS[0]),runQuestion(QUESTIONS[0]));
 const r=runQuestion(QUESTIONS[0]);
 assert.equal(r.executed_capability.evidence_admission,'NONE');
 assert.equal(r.any_owner_approval_inherited,false);
 assert.equal(r.production_install,false);
 assert.equal(r.live_external_source_crawl,false);
 assert.equal(r.external_actions,0);
});
test('complete demonstration preserves inherited original MADD source-custody ride',()=>{
 const demo=demonstration();
 assert.equal(demo.cases.length,4);
 assert.deepEqual(demo.cases.map(x=>x.status),[
  'EXECUTED_LOCAL_HELD_CAPABILITY',
  'EXECUTED_LOCAL_HELD_CAPABILITY',
  'EXECUTED_LOCAL_HELD_CAPABILITY',
  'HOLD_NO_RELEVANT_SOURCE_MATERIAL'
 ]);
 assert.ok(demo.inherited_original_madd_ride_id.startsWith('ride-'));
 assert.equal(demo.inherited_original_native_research_pins,16);
 assert.equal(demo.persistent_runtime_across_sessions,false);
});
