import assert from 'node:assert/strict';
import test from 'node:test';

import { proposeNextProbe, executeNativeProbe } from './probe_selection.mjs';

const candidate = (id,profile) => ({
  id, status:'proposed', proposal:{ probeProfile:profile },
});
const nursery = (profiles) => ({
  schema:'memento.role-nursery/v0',
  candidates:profiles.map((p,i)=>candidate('role-candidate-'+i,p)),
});
const nativeResult = (program = 'path2(carries,reaches)') => ({
  status:'HOLD_FOR_HUMAN_REVIEW',
  selection_used_holdout:false,
  observation_authenticated:false,
  cartridge:{
    authority:'NONE',
    human_review_required:true,
    program,
  },
});

const two = () => nursery([
  {carries:true,reaches:false,marked:false},
  {carries:true,reaches:true,marked:true},
]);

test('MOTIF actually determines next MEMENTO probe rather than runner preselecting one',()=>{
  const proposal = proposeNextProbe(nativeResult(),two(),['carries']);
  assert.equal(proposal.status,'PROPOSE_ADDITIONAL_MEASUREMENT');
  assert.equal(proposal.selectedProbe,'reaches');
  assert.equal(proposal.originalPairCount,1);
  assert.equal(proposal.expectedPairReduction,1);
  assert.equal(proposal.expectedCollisionsAfter,0);
  assert.deepEqual(proposal.existingKeys,['carries']);
});

test('distinct validated MOTIF concept induces a distinct probe',()=>{
  const p = proposeNextProbe(nativeResult('direct(marked)'),two());
  assert.equal(p.selectedProbe,'marked');
  assert.equal(p.expectedPairReduction,1);
});

test('HOLD and rival-model results do not invent a diagnostic action',()=>{
  for (const status of ['HOLD_RIVAL_MODELS','HOLD_UNEXPLAINED_SURPRISE','HOLD_NO_OBSERVED_GAP']) {
    const p = proposeNextProbe({...nativeResult(),status},two());
    assert.equal(p.status,'HOLD');
    assert.equal(p.selectedProbe,null);
  }
});

test('unsupported model operation does not silently expand grammar',()=>{
  const p = proposeNextProbe(nativeResult('path3(carries,passes,reaches)'),two());
  assert.equal(p.status,'HOLD');
  assert.equal(p.reason,'UNSUPPORTED_CONCEPT_PROGRAM');
});

test('a feature that cannot distinguish remaining roles is rejected',()=>{
  const p = proposeNextProbe(nativeResult(),
    nursery([{carries:true,reaches:true},{carries:true,reaches:true}]));
  assert.equal(p.status,'HOLD');
  assert.equal(p.reason,'NO_DISCRIMINATING_OBSERVATION');
});

test('missing measurements are not silently filled with guessed values',()=>{
  const p = proposeNextProbe(nativeResult(),
    nursery([{carries:true,reaches:false},{carries:true}]));
  assert.equal(p.status,'HOLD');
  assert.equal(p.reason,'NO_AVAILABLE_CONCEPT_DERIVED_PROBE');
});

test('unreviewable or unauthorized cartridges cannot choose a probe',()=>{
  const base = nativeResult();
  for (const changed of [
    {...base,observation_authenticated:true},
    {...base,selection_used_holdout:true},
    {...base,cartridge:{...base.cartridge,authority:'SUPERVISOR'}},
    {...base,cartridge:{...base.cartridge,human_review_required:false}},
  ]) {
    assert.equal(proposeNextProbe(changed,two()).status,'HOLD');
  }
});

test('no operator authorization: never execute even when model proposes',async()=>{
  const n = two();
  const before = structuredClone(n);
  const p = proposeNextProbe(nativeResult(),n);
  const x = await executeNativeProbe(null,n,p,{authorizeSyntheticProbe:false});
  assert.equal(x.status,'HOLD_OPERATOR_GATE');
  assert.equal(x.receipt,null);
  assert.deepEqual(n,before);
});

test('HOLD proposal cannot execute even with experimental permission',async()=>{
  const n = two();
  const p = proposeNextProbe({...nativeResult(),status:'HOLD_RIVAL_MODELS'},n);
  const x = await executeNativeProbe(null,n,p,{authorizeSyntheticProbe:true});
  assert.equal(x.status,'HOLD_NO_EXECUTABLE_PROPOSAL');
  assert.equal(x.receipt,null);
});

test('competing eligible probes tie deterministically, without a truth claim',()=>{
  const n = nursery([
    {carries:true,marked:false,reaches:false},
    {carries:true,marked:true,reaches:true},
  ]);
  const p = proposeNextProbe(nativeResult('path2(marked,reaches)'),n);
  assert.equal(p.selectedProbe,'marked');
  assert.equal(p.candidates.length,2);
  assert.equal(p.permission,'SYNTHETIC_PROPOSAL_ONLY');
  assert.equal(p.evidenceAuthenticated,false);
});
