/* MOTIF chooses a candidate relation-derived discriminator, then MEMENTO's
 * actual Role Nursery executes the probe. This is a bounded, synthetic
 * research experiment, not permission to act on people or external worlds.
 */
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

function assert(ok, why) { if (!ok) throw Error(why); }

function parseProgram(value) {
  if (typeof value !== 'string') return null;
  const m = /^(direct|path2)\(([a-zA-Z0-9_-]+)(?:,([a-zA-Z0-9_-]+))?\)$/.exec(value);
  if (!m || (m[1] === 'direct' && m[3]) || (m[1] === 'path2' && !m[3])) return null;
  return { kind: m[1], relations: [m[2], m[3]].filter(Boolean) };
}

function collisionPairs(profiles, keys) {
  const pairs = [];
  for (let i = 0; i < profiles.length; i++) {
    for (let j = i + 1; j < profiles.length; j++) {
      if (keys.every(k => Object.is(profiles[i][k], profiles[j][k])))
        pairs.push([i, j]);
    }
  }
  return pairs;
}

export function proposeNextProbe(motif, nursery, existingKeys = ['carries']) {
  assert(nursery?.schema === 'memento.role-nursery/v0', 'Native Role Nursery state required');
  assert(Array.isArray(nursery.candidates) && nursery.candidates.length >= 2,
    'At least two MEMENTO role candidates required');
  const hold = reason => ({
    schema: 'motif019.probe-proposal/v0',
    status: 'HOLD',
    reason,
    candidates: [],
    selectedProbe: null,
    expectedPairReduction: 0,
    permission: 'SYNTHETIC_PROPOSAL_ONLY',
  });
  if (motif?.status !== 'HOLD_FOR_HUMAN_REVIEW' ||
      motif?.cartridge?.authority !== 'NONE' ||
      motif?.cartridge?.human_review_required !== true ||
      motif?.selection_used_holdout !== false ||
      motif?.observation_authenticated !== false)
    return hold('NO_VALID_REVIEWABLE_MOTIF_CONCEPT');
  const program = parseProgram(motif.cartridge.program);
  if (!program) return hold('UNSUPPORTED_CONCEPT_PROGRAM');
  const profiles = nursery.candidates.map(c => c.proposal?.probeProfile);
  if (profiles.some(x => !x || typeof x !== 'object'))
    return hold('INCOMPLETE_ROLE_PROFILES');
  if (existingKeys.some(k => profiles.some(x => !Object.hasOwn(x, k))))
    return hold('EXISTING_PROBE_NOT_AVAILABLE');
  const oldPairs = collisionPairs(profiles, existingKeys);
  const scores = [];
  for (const key of new Set(program.relations)) {
    if (existingKeys.includes(key)) continue;
    if (profiles.some(p => !Object.hasOwn(p, key))) continue;
    const newPairs = collisionPairs(profiles, [...existingKeys, key]);
    const reduction = oldPairs.length - newPairs.length;
    scores.push({ probeKey: key, remainingCollisions: newPairs.length,
                  pairReduction: reduction });
  }
  scores.sort((a, b) => b.pairReduction - a.pairReduction ||
    a.remainingCollisions - b.remainingCollisions ||
    a.probeKey.localeCompare(b.probeKey));
  if (!scores.length) return hold('NO_AVAILABLE_CONCEPT_DERIVED_PROBE');
  if (scores[0].pairReduction <= 0) return hold('NO_DISCRIMINATING_OBSERVATION');
  const selected = scores[0];
  return {
    schema:'motif019.probe-proposal/v0',
    status:'PROPOSE_ADDITIONAL_MEASUREMENT',
    sourceProgram: motif.cartridge.program,
    existingKeys: [...existingKeys],
    selectedProbe: selected.probeKey,
    expectedPairReduction: selected.pairReduction,
    expectedCollisionsAfter: selected.remainingCollisions,
    candidates: scores,
    originalPairCount: oldPairs.length,
    permission:'SYNTHETIC_PROPOSAL_ONLY',
    actionNeeded:'EXECUTE_NATIVE_MEMENTO_PROBE_IN_MEMORY',
    evidenceAuthenticated:false,
  };
}

// Explicitly invoke MEMENTO's real implementation. A proposal never mutates
// the source nursery or grants MEMENTO role, route, canon, or external power.
export async function executeNativeProbe(mementoRoot, nursery, proposal, {
  authorizeSyntheticProbe = false,
} = {}) {
  if (proposal.status !== 'PROPOSE_ADDITIONAL_MEASUREMENT')
    return { status:'HOLD_NO_EXECUTABLE_PROPOSAL', nursery, receipt:null };
  if (!authorizeSyntheticProbe)
    return { status:'HOLD_OPERATOR_GATE', nursery, receipt:null };
  assert(mementoRoot, 'Owner-authorized private MEMENTO checkout required');
  const path = join(resolve(mementoRoot),
    'experiments/understory-fractal-particular-001/role-nursery.mjs');
  const roles = await import(pathToFileURL(path).href);
  const tested = roles.probeRoleCandidates(nursery, {
    candidateIds: nursery.candidates.map(c => c.id),
    probeKeys: [...proposal.existingKeys, proposal.selectedProbe],
    methodRef: 'motif019:concept-derived:' + proposal.sourceProgram,
  });
  assert(tested.nursery.candidates.every(c => c.status === 'proposed'),
    'Probe attempted to constitute a candidate');
  assert(tested.receipt.authority === 'none', 'Unexpected native probe authority');
  assert(tested.receipt.indistinguishablePairs.length ===
    proposal.expectedCollisionsAfter, 'Native result differs from anticipated collision count');
  return {
    status: tested.receipt.separatesCandidates ?
      'SEPARATED_UNDER_PROBE_NOT_ESTABLISHED_TRUTH' :
      'HOLD_RIVAL_ROLES',
    nursery: tested.nursery,
    receipt: tested.receipt,
    authority:'NONE',
    persistentWrites:0,
    externalActions:0,
    methodIsNativeMemento:true,
  };
}
