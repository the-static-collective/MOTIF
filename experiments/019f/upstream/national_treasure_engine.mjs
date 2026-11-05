const PROVENANCE_CLASSES = new Set([
  'observed',
  'primary',
  'inference',
  'speculation',
  'failed',
]);

const SUPPORT_CONFIDENCE = new Set([
  'established',
  'probable',
  'possible',
  'unsupported',
]);

function text(value = '') {
  return String(value ?? '').trim();
}

function list(value = []) {
  if (Array.isArray(value)) return value.map(text).filter(Boolean);
  return text(value).split('|').map((item) => item.trim()).filter(Boolean);
}

function normalizeEnum(value, allowed, fallback) {
  const candidate = text(value).toLowerCase();
  return allowed.has(candidate) ? candidate : fallback;
}

function shortSubject(record) {
  const raw = record.claim || record.clue || 'this clue';
  return raw.length > 160 ? raw.slice(0, 157) + '...' : raw;
}

export function normalizeRecord(input = {}) {
  return {
    clue: text(input.clue),
    claim: text(input.claim),
    provenance_class: normalizeEnum(input.provenance_class, PROVENANCE_CLASSES, 'speculation'),
    support_confidence: normalizeEnum(input.support_confidence, SUPPORT_CONFIDENCE, 'possible'),
    source_locator: text(input.source_locator),
    source_families: list(input.source_families),
    chronology: text(input.chronology),
    counterevidence: text(input.counterevidence),
    falsifier: text(input.falsifier),
    competing_explanations: list(input.competing_explanations),
  };
}

export function buildQuestionFrontier(input = {}) {
  const record = normalizeRecord(input);
  if (!record.clue && !record.claim) {
    throw new Error('question-box requires a clue or claim');
  }

  const subject = shortSubject(record);
  const candidates = [];

  if (!record.source_locator) {
    candidates.push({
      id: 'source-object',
      score: 100,
      missing: 'recoverable source object',
      reason: 'The clue cannot yet be re-found independently.',
      question: `What is the earliest recoverable source object for “${subject},” and what does that object actually show before interpretation?`,
    });
  }

  if (!record.chronology) {
    candidates.push({
      id: 'chronology',
      score: 95,
      missing: 'chronology',
      reason: 'Similarity without ordering can manufacture ancestry.',
      question: `What is the earliest date at which the relation implied by “${subject}” can be demonstrated without importing a later meaning backward?`,
    });
  }

  if (!record.counterevidence) {
    candidates.push({
      id: 'counterevidence',
      score: 90,
      missing: 'counterevidence',
      reason: 'A clue gets stronger only after surviving ordinary alternatives and failed alignments.',
      question: `What observation would make “${subject}” look ordinary, unrelated, or incorrectly framed?`,
    });
  }

  if (!record.falsifier) {
    candidates.push({
      id: 'falsifier',
      score: 85,
      missing: 'falsifier',
      reason: 'A mystery that cannot lose has no discriminator.',
      question: `What single finding would most clearly count against the strongest reading of “${subject}”?`,
    });
  }

  if (record.competing_explanations.length < 2) {
    candidates.push({
      id: 'rival-models',
      score: 82,
      missing: 'competing explanations',
      reason: 'One story is not yet a comparison.',
      question: `What are two materially different explanations for “${subject}” that fit the evidence so far, and where would their predictions diverge?`,
    });
  }

  if (record.source_families.length < 2) {
    candidates.push({
      id: 'independent-convergence',
      score: 80,
      missing: 'independent source families',
      reason: 'Repeated descendants of one source do not constitute independent convergence.',
      question: `Which apparently separate witnesses to “${subject}” are actually independent, and which descend from the same evidentiary family?`,
    });
  }

  candidates.push({
    id: 'discriminator',
    score: 75,
    missing: 'minimum discriminator',
    reason: 'The best next move is the smallest observation that separates live models.',
    question: `What is the cheapest discriminating observation that would separate the strongest surviving explanations for “${subject}”?`,
  });

  candidates.push({
    id: 'relation',
    score: 70,
    missing: 'witnessed relation',
    reason: 'Resemblance is weaker than an inspectable relation through change.',
    question: `Which relation around “${subject}” is directly witnessed, and which part of the apparent pattern exists only in our projection?`,
  });

  candidates.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  const selected = candidates[0];

  return {
    schema: 'national-treasure.question-receipt/v0',
    kind: 'question_frontier',
    input: {
      clue: record.clue,
      claim: record.claim,
    },
    evidence: {
      provenance_class: record.provenance_class,
      support_confidence: record.support_confidence,
      source_locator: record.source_locator,
      source_families: record.source_families,
      chronology: record.chronology,
      counterevidence: record.counterevidence,
      falsifier: record.falsifier,
      competing_explanations: record.competing_explanations,
    },
    aperture: {
      id: selected.id,
      missing: selected.missing,
      reason: selected.reason,
    },
    question: selected.question,
    other_doors: candidates.slice(1, 4).map((candidate) => ({
      aperture: candidate.id,
      question: candidate.question,
    })),
    non_claims: [
      'This receipt does not answer the question.',
      'This receipt does not upgrade provenance class or support confidence.',
      'This receipt does not establish ancestry, causation, legal validity, or historical truth.',
      'A compelling pattern remains a clue until independent evidence earns convergence.',
    ],
  };
}
