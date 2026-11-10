# COLLECTIVE-001 — The Proof-Carrying Answer Weave

**Status: stacked DRAFT experiment on THOUGHT-028, itself unmerged.**
Synthetic, source-owned three-bit set tasks only. No production agent, external
data retrieval, multi-agent negotiation, real-world permission, or model calls.

## Research question

When an inquiry has actually produced verifiable evidence, can MOTIF emit a
portable answer **with its relevant evidence, proof, source scope, and unresolved
questions**, so a later inquiry can re-enter the same verified result without
re-discovering the applicable rule?

This is an *answer-layer projection*, not an invented replacement for existing
THOUGHT-027 proof cards, THOUGHT-028 proof weave, or REASON-006 reasoning
commonwealth. The concrete reentry contract is the new result.

## Implementation

answer_weave.py reuses actual THOUGHT-028 EvidenceStore, its scoped source
proofs, its derived proof, and the exact task owner's independent 64-case
oracle and fixed-template execution. For authored cancel_or_add:

1. Independently re-check source-backed DIFFERENCE and UNION card precedents.
2. Compose and choose a scoped XOR rule through the existing active experiment.
3. Check the selected rule against source owner's 64-case full finite domain
   and the separate source-owned template executor.
4. Emit a single **proof-carrying answer node** with a concrete input/output,
   its complete original inquiry receipt, exact task definition, evidence
   ancestry, minimal portable proof-memory subset, and explicit limitations.
5. Re-import the serialized node in a new process. On re-entry, validate the
   packet integrity, source-task definition, source cards, derived proof and
   lineage, original development observations, result value, and all 64 cases.
   The question-selection phase is not rerun for **that exact task**.
6. For a different task, old proof cards are **candidates**, not automatically
   true semantics. New active development questions and fresh independent
   checks are mandatory.

The answer object carries only public, inspectable proof/evidence artifacts.
It does not expose a model's private chain-of-thought. A SHA-256 checksum is
an integrity guard, **not** authenticated source identity. Evidence statements
are scoped to synthetic tasks; installed=false and external_authority=NONE.

### Output contract

- question_scope, task_spec_sha256: exact task definition and checked scope.
- answer: concrete input/output, typed executable rule, independent owner
  comparison, 64/64 finite certificate and 64/64 template-runtime certificate.
- relevant_evidence_nodes: ancestry from two source proof cards to one
  derived card, all with exact digests (not an unverified vote tally).
- inquiry_receipt: selected probes, their observed outcomes, caveats,
  and status; hash checked and each observed value rechecked.
- proof_memory: smallest independently revalidated proof store containing
  the conclusion and its ancestors.
- unresolved: source identity, external applicability, linguistic mapping,
  and authority limits.
- cache_key: exact task+input-specific retrieval key.
- integrity_digest: canonical payload integrity fingerprint.

**A verified finite calculation is not a proof that the user's story is
correct, that a real-world source is authentic, or that a new task with similar
words has identical semantics.** Unknown/out-of-grammar tasks must HOLD.

## Reproduce

From repository root (Python 3.10+, standard library):

    python -m unittest discover -s experiments/collective001 -p "test_*.py" -v
    python experiments/collective001/demo.py > collective001-proof-answer.json

The demo includes full portable answer node and a separate re-entry receipt.
CI uploads that output as an inspection artifact.

## Evaluation discipline

Report **development questions** separately from total owner verification
work and CPU time. Re-entry avoids selecting new questions for the same
source-owned scope but **still reruns expensive independent verification**
of the stored proofs. No unmeasured end-to-end speedup is claimed.

This uses scripted developer-authored task worlds and **zero model calls**.
It does not independently reproduce HiddenBench or demonstrate collective
reasoning advantage over a fully informed classical baseline.

### Next falsifier: Collective-002

Distribute source facts across genuinely separated, independently authored
agent contexts with no omniscient reader. Use an evidence-question router to
request only missing observation, then preserve source custody and proof
lineage. Compare with identical-information classical pooling, structured
multi-agent protocols, and equal-budget single-agent baselines. Measure new
facts, missing information recovered, answer accuracy, provenance damage,
development-query count, verification cost, and wall time separately.
