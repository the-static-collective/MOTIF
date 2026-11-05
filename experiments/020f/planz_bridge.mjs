// MOTIF-020F — real planZ native validator, frozen public index snapshot.
// This is read-only import, not planZ authority, live enrollment, or field evidence.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validatePublicAttention } from './upstream/validate-attention.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const origins = [
  ['feed', 'planz_attention-v1.json', '49e70c0caeaf0bca430338829b69d51c8c617385'],
  ['validator', 'validate-attention.mjs', 'a6fb92b5242519fa1c72b88cf1d34eb6770063ea'],
];
const pinned = {};
for (const [name, filename, expected] of origins) {
  const bytes = readFileSync(path.join(root, 'upstream', filename));
  const blob = createHash('sha1').update('blob ' + bytes.length + '\0').update(bytes).digest('hex');
  if (blob !== expected) {
    console.error('HOLD_PLANZ_SOURCE_DRIFT:' + name);
    process.exit(2);
  }
  pinned[name] = { git_blob: blob, sha256: createHash('sha256').update(bytes).digest('hex') };
}
try {
  const payload = JSON.parse(readFileSync(path.join(root, 'upstream', 'planz_attention-v1.json'), 'utf8'));
  const checked = validatePublicAttention(payload); // invokes planZ's unmodified native validator
  const output = {
    schema: 'motif020f.planz-readonly-snapshot/v0',
    source_repository: 'the-static-collective/planZ',
    source_branch_at_capture: 'main',
    source_edition: checked.edition,
    published_reviewed_on: checked.reviewedOn,
    source_authority: checked.authority,
    original_schema: checked.schema,
    source_pins: pinned,
    temporal_fact: 'NONE_IN_ATTENTION_INDEX',
    field_outcome_established: false,
    source_entries: checked.entries.map(({ id, title, source, disposition,
       nextGate, blockedBy, related, fieldOutcome, executionAllowed, thirdPartyApproval, tags }) => ({
      id, title, source, disposition, nextGate, blockedBy, related,
      fieldOutcome, executionAllowed, thirdPartyApproval, tags
    })),
    execution_authority: 'NONE',
    dispatch: false
  };
  process.stdout.write(JSON.stringify(output) + '\n');
} catch (error) {
  console.error('HOLD_INVALID_PLANZ_ATTENTION:' + String(error.message).slice(0,200));
  process.exit(2);
}
