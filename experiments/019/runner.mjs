/* Native MEMENTO modules run in an owner-provided checkout.
 * MOTIF receives structural-only, synthetic JSON; UNDERSTORY validates
 * in-memory receipts, never writes to private ledger.
 */
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { buildNativeEvidence } from './native_memento.mjs';
import { checkUnderstory } from './understory.mjs';

export async function runNativeBridge({
  mementoRoot = process.env.MEMENTO_ROOT,
  python = process.env.PYTHON || 'python3',
  perturbHoldout = false,
} = {}) {
  if (!mementoRoot) throw Error('Set MEMENTO_ROOT to an owner-accessible MEMENTO checkout');
  const source = await buildNativeEvidence(mementoRoot);
  const packet = structuredClone(source.packet);
  if (perturbHoldout) for (const row of packet.holdout) row.outcome ^= 1;
  const cli = fileURLToPath(new URL('../018/interop_stdio.py', import.meta.url));
  const child = spawnSync(python, [cli], {
    input:JSON.stringify(packet),
    encoding:'utf8',
    timeout:10000,
    maxBuffer:300000,
  });
  if (child.status !== 0)
    throw Error('MOTIF interop rejected the synthetic packet');
  const result = JSON.parse(child.stdout);
  if (result.schema !== 'motif018.memento-bridge-result/v0' ||
      result.authority !== 'NONE' || result.external_actions !== 0)
    throw Error('Invalid or unsafe MOTIF interop result');

  const understory = await checkUnderstory(mementoRoot,result);
  return {
    schema:'motif019.memento-understory/v0',
    sourceModules:'DIRECT_RUNTIME_IMPORT_FROM_MEMENTO',
    note:'No MEMENTO source code, owner records, or private testimony copied to MOTIF.',
    syntheticOnly:true,
    actualMemento:{
      versions:source.nativeVersions,
      witnessedActs:source.field.acts.length,
      derivedGrammarRules:source.grammar.rules.length,
      proposedAffordances:source.field.affordanceSchemas.length,
      proposedRoles:source.nursery.candidates.length,
      coarseProbeSeparates:source.coarse.separatesCandidates,
      expandedProbeSeparates:source.expanded.separatesCandidates,
      installedGrammarRules:source.grammar.rules.filter(r=>r.status==='admitted').length,
      admittedRoles:source.nursery.candidates.filter(c=>c.status==='admitted').length,
    },
    motif:result,
    understory,
    sourceEvidenceAuthenticated:false,
    externalActions:0,
    manualReviewRequired:true,
  };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = await runNativeBridge();
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
}
