import assert from 'node:assert/strict';
import test from 'node:test';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runNativeBridge } from './runner.mjs';

const mementoRoot = process.env.MEMENTO_ROOT;

test('the adapter has valid JavaScript and no secret-dependent commands', () => {
  for (const name of ['native_memento.mjs','understory.mjs','runner.mjs','probe_selection.mjs']) {
    const path = fileURLToPath(new URL(name,import.meta.url));
    const proc = spawnSync(process.execPath,['--check',path],{encoding:'utf8'});
    assert.equal(proc.status,0,proc.stderr);
  }
});

test('native MEMENTO + UNDERSTORY + MOTIF cross-repository witness', {
  skip: !mementoRoot && 'Native private MEMENTO checkout not provided',
}, async () => {
  const p = await runNativeBridge({mementoRoot});
  assert.equal(p.schema,'motif019.memento-understory/v0');
  assert.equal(p.motif.status,'HOLD_FOR_HUMAN_REVIEW');
  assert.equal(p.motif.surface_holdout.accuracy,0.5);
  assert.equal(p.motif.selected_holdout.accuracy,1);
  assert.equal(p.motif.classical_holdout.accuracy,1);
  assert.equal(p.actualMemento.witnessedActs,16);
  assert.equal(p.actualMemento.derivedGrammarRules,2);
  assert.equal(p.actualMemento.proposedRoles,2);
  assert.equal(p.actualMemento.coarseProbeSeparates,false);
  assert.equal(p.actualMemento.motifSelectedProbe,'reaches');
  assert.equal(p.actualMemento.nativeProbeSeparates,true);
  assert.equal(p.probeProposal.expectedPairReduction,1);
  assert.equal(p.nativeProbeReceipt.methodRef,
    'motif019:concept-derived:path2(carries,reaches)');
  assert.equal(p.actualMemento.installedGrammarRules,0);
  assert.equal(p.actualMemento.admittedRoles,0);
  assert.equal(p.understory.recordCount,6);
  assert.equal(p.understory.stance,'held');
  assert.equal(p.understory.association,'unresolved');
  assert.equal(p.understory.ledgerWrites,0);
  assert.equal(p.externalActions,0);
});

test('holdout outcome reversal cannot change selected concept or old memory', {
  skip: !mementoRoot && 'Native private MEMENTO checkout not provided',
}, async () => {
  const initial = await runNativeBridge({mementoRoot});
  const hostile = await runNativeBridge({mementoRoot,perturbHoldout:true});
  assert.deepEqual(initial.motif.cartridge,hostile.motif.cartridge);
  assert.equal(initial.probeProposal.selectedProbe,hostile.probeProposal.selectedProbe);
  assert.equal(hostile.actualMemento.nativeProbeSeparates,true);
  assert.equal(hostile.motif.selected_holdout.accuracy,0);
  assert.equal(initial.understory.recordCount,hostile.understory.recordCount);
  assert.equal(initial.understory.stance,'held');
  assert.equal(hostile.understory.stance,'held');
  assert.equal(hostile.understory.canonAdmissions,0);
});
