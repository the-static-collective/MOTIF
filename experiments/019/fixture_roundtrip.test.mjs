/* Cross-language roundtrip of actual, source-derived synthetic MEMENTO fixture:
 * MEMENTO native modules -> frozen structural packet -> Python MOTIF 018 ->
 * concept-selected new MEMENTO Role Nursery *probe proposal*. The private
 * native execution test is still separate and requires an owner checkout.
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { proposeNextProbe } from './probe_selection.mjs';

const evidencePath = fileURLToPath(new URL('fixtures/memento-structural-cases.json',import.meta.url));
const rolesPath = fileURLToPath(new URL('fixtures/memento-role-profiles.json',import.meta.url));
const cliPath = fileURLToPath(new URL('../018/interop_stdio.py',import.meta.url));
const loadEvidence = () => JSON.parse(readFileSync(evidencePath,'utf8'));
const loadRoles = () => JSON.parse(readFileSync(rolesPath,'utf8'));

function model(packet) {
  const proc = spawnSync(process.env.PYTHON || 'python3',[cliPath],{
    input:JSON.stringify(packet),
    encoding:'utf8',timeout:10000,maxBuffer:300000,
  });
  assert.equal(proc.status,0,proc.stderr || proc.stdout);
  return JSON.parse(proc.stdout);
}

test('exact MEMENTO-derived synthetic packet drives actual MOTIF program and new probe',()=>{
  const evidence = loadEvidence();
  const profiles = loadRoles();
  assert.deepEqual([
    evidence.train.length,evidence.validation.length,evidence.holdout.length
  ],[4,4,8]);
  assert.equal(profiles.coarseCollisionCount,1);
  const motif = model(evidence);
  assert.equal(motif.status,'HOLD_FOR_HUMAN_REVIEW');
  assert.equal(motif.cartridge.program,'path2(carries,reaches)');
  assert.equal(motif.surface_holdout.accuracy,0.5);
  assert.equal(motif.selected_holdout.accuracy,1);
  assert.equal(motif.classical_holdout.accuracy,1);
  assert.equal(motif.external_actions,0);
  const proposal = proposeNextProbe(motif,profiles,profiles.coarseProbeKeys);
  assert.equal(proposal.status,'PROPOSE_ADDITIONAL_MEASUREMENT');
  assert.equal(proposal.selectedProbe,'reaches');
  assert.equal(proposal.expectedPairReduction,1);
  assert.equal(proposal.expectedCollisionsAfter,0);
  assert.equal(proposal.permission,'SYNTHETIC_PROPOSAL_ONLY');
});

test('false held-out world leaves model/probe unchanged but exposes prediction failure',()=>{
  const evidence = loadEvidence();
  const profiles = loadRoles();
  const before = model(evidence);
  const first = proposeNextProbe(before,profiles,profiles.coarseProbeKeys);
  for (const row of evidence.holdout) row.outcome ^= 1;
  const after = model(evidence);
  const second = proposeNextProbe(after,profiles,profiles.coarseProbeKeys);
  assert.deepEqual(before.cartridge,after.cartridge);
  assert.deepEqual(first,second);
  assert.equal(after.selected_holdout.accuracy,0);
  assert.equal(after.observation_authenticated,false);
});

test('source-derived packet and profile snapshot contain synthetic structural evidence only',()=>{
  const evidence = loadEvidence();
  const roles = loadRoles();
  assert.equal(evidence.schema,'motif018.memento-evidence/v0');
  for (const split of ['train','validation','holdout']) for (const row of evidence[split]) {
    assert.deepEqual(Object.keys(row).sort(),['authorized','edges','identity','outcome','x']);
    assert.ok(row.identity.startsWith('memento-'+split+'-'));
    assert.ok(row.edges.every(e=>e.length===3 && e.every(x=>typeof x==='string')));
  }
  assert.equal(roles.schema,'memento.role-nursery/v0');
  assert.ok(roles.candidates.every(c=>c.status==='proposed'));
});
