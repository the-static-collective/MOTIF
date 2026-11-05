// MOTIF-019F — source-pinned National Treasure Question Box adapter.
// Does not answer the question and cannot grant tool or execution authority.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildQuestionFrontier } from './upstream/national_treasure_engine.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const source = readFileSync(path.join(root, 'upstream', 'national_treasure_engine.mjs'));
const digest = createHash('sha1')
  .update('blob ' + source.length + '\0').update(source).digest('hex');
if (digest !== '83574ed0a927fdefe1a53b3ece0960f011b875d0') {
  process.stderr.write('HOLD_SOURCE_DRIFT_NATIONAL_TREASURE\n');
  process.exit(2);
}

const chunks = [];
let size = 0;
for await (const chunk of process.stdin) {
  chunks.push(chunk);
  size += chunk.length;
  if (size > 30000) {
    process.stderr.write('HOLD_INPUT_TOO_LARGE\n');
    process.exit(2);
  }
}
try {
  const record = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  if (!record || typeof record !== 'object' || Array.isArray(record)) {
    throw new Error('HOLD_INVALID_CLUE');
  }
  const question = buildQuestionFrontier(record);
  if (question.schema !== 'national-treasure.question-receipt/v0'
      || Object.hasOwn(question, 'answer') || Object.hasOwn(question, 'conclusion')) {
    throw new Error('HOLD_QUESTION_BOX_AUTHORITY');
  }
  process.stdout.write(JSON.stringify({
    schema: 'motif019f.native-question-gate/v0',
    original_source_blob: digest,
    aperture: question.aperture.id,
    question: question.question,
    native_receipt: question,
    authority: 'none',
    synthetic_only: true,
  }) + '\n');
} catch (error) {
  process.stderr.write('HOLD_NATIVE_QUESTION: ' + String(error.message).slice(0, 180) + '\n');
  process.exit(2);
}
