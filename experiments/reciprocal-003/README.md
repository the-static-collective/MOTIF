# RECIPROCAL-003 — The Question That Changes the Questioner

**Status:** executable offline research lab, source-scoped, **not production**, not native LLM-004 `ReasonHypermap` input, not autonomous self-modification. Project: MOTIF. Date: 2026-11-12.

## Why this is the next step

RECIPROCAL-001 taught a bounded machine and a human using a finite Boolean lesson. RECIPROCAL-002 provided two entrances: `Ask MOTIF` or `Let MOTIF ask`. This experiment connects the actual **RECIPROCAL-002 question/event engine** to a reasoning record and a falsifiable candidate-method trial.

```
Human question + named useful decision
                 ↓
RECIPROCAL-002 intentional question queue
                 ↓
Opt-in claimed source response / correction
                 ↓
RECIPROCAL-003 source-scoped reason field
   ├─ reported evidence graph with multi-terminal links
   ├─ hypothetical one-more-answer forks (PENCIL)
   └─ classical role-conditioned method candidate
                 ↓
Independent later reported choices (held-out)
                 ↓
PROPOSED_FOR_HUMAN_REVIEW / HOLD
                 ↓
Human can learn why it is proposed or refused
```

### Real executable components

- [reason_loop.js](reason_loop.js): `toGraph(state,qid,now)`, `previewOneMore(state,qid,now)`, `methodCandidate(state,qid,now)`, `lesson(state,qid,now)`, and `authoredDemo(now)`. Uses the **original** `../reciprocal-002/two_doors.js` engine and its exact source-effective view, question validation, counterfactual cloning and stopping logic.
- [lab.html](lab.html): real browser user interface with the **two original doors intact**, a new inspectable Research Lens, counterfactual branch preview, method experiments and a reasoning lesson. An explicitly labeled fictional example loads eight synthetic answers for seeing the method foundry without recruiting anyone.
- [test_research.cjs](test_research.cjs): deterministic executable falsifiers for source conflicts, revisions, closed/expired questions, before/after forks, heldout source IDs and a negative regime where method transfer regresses.
- [PREREGISTRATION.md](PREREGISTRATION.md): hypotheses and decision thresholds committed before writing the implementation.
- [../../.github/workflows/reciprocal-003.yml](../../.github/workflows/reciprocal-003.yml): runs inherited RECIPROCAL-002 checks plus the 003 checks, builds a single offline self-contained HTML file, checks scripts for syntax and the absence of background network messaging, and uploads an inspectable artifact.

## The new Reason Hypermap-style field

The **new** schema `motif.reciprocal003.reason-field/v0` is a conservative projection of recorded question and source events. It preserves:

- the question's declared purpose and hoped-for decision consequence;
- mutually exclusive answer possibilities;
- claimed sources and their original event IDs (without pretending pseudonyms verify human identity);
- multi-terminal relations: question + claimed source → report + its proposed answer;
- explicit corrections pointing at their historical record;
- a tentative hypothesis that answers might depend on volunteered context;
- the source-scoped status of the inquiry, refusal to equate reported majority with truth, and **no authority**.

This was inspired by the original LLM-004 [Reason Hypermap PR #318](https://github.com/the-static-collective/MOTIF/pull/318), but deliberately **does not** instantiate its `Owner`-typed Python oracle, Bayesian posterior or official Free Graph exporter. Its `source_provenance` field records the pinned original blob, not code import. The safe next integration would require a reviewed generic evidence/hyperedge schema to prevent accidental elevation of crowd reports into owner truth.

## What-if questions

For a currently open question, the engine makes an isolated cloned copy of the actual evidence state for each possible next answer and runs **the original** `TwoDoors.inspect` again. It produces a status/answer-count forecast only. Every branch is labeled `HYPOTHETICAL_ONLY_NOT_OBSERVED`; none changes the actual event ledger.

Why useful: a human can see *which additional observation would change the decision to continue asking, seek another role, review, or reframe*, without treating a fictional response as evidence.

## The bounded Algorithm Foundry

We do not train weights or claim novel mathematics. The experimental cartridge is a simple, falsifiable classically known conditional method:

- At least three distinct claimed roots in each of two self-declared roles. No conflicting source events.
- Train a **global-majority baseline** and **role-conditioned plurality** on the same **first two chronological reports per role**.
- Hold back every later report for testing. The test reads only reported answer categories, not actual external-world truth or independent decision outcomes.
- Promote to `PROPOSED_FOR_HUMAN_REVIEW` only if the conditional method predicts **at least two more later reports correctly** than the global-majority baseline. It is **never automatically installed** or treated as reliable outside its two named roles.
- A strong classical role-conditioned method with equal information **ties the candidate by design**. This is proof of a functioning source-scoped experimental comparison, not proof of MOTIF superiority.

**Synthetic demonstration:** Eight author-created reports: four fictional newcomers choose option 1; four fictional makers choose option 2. First two reports in each role train the methods; next two in each role are held out. Global plurality predicts **2/4** heldout reports, role-conditioned plurality **4/4**, difference **+2 reports**. Reversed heldout labels make the conditional policy fail **0/4** versus global **2/4**, a regression of **-2**. Neither scenario establishes real-world truth, useful action, causality or human teaching effectiveness.

## Run

From MOTIF repository root:

```bash
node experiments/reciprocal-002/test_engine.cjs
node experiments/reciprocal-003/test_research.cjs
```

Open `experiments/reciprocal-003/lab.html` from the repository tree for local usage (it loads scripts from its sibling and parent directories). Or use the **single HTML file** generated by CI without any server, JS build system, login, credits or network connection.

**Try it:** Open lab → Research Lens → **Load fictional learning example** → choose **Can a role-sensitive method improve predictions?**. Explore the alternative answer futures, inspect the source events, then start over and submit a meaningful new question through the Ask door.

## What has NOT been established

No real people have been recruited; no independently verified identity, demographic inference, scientific truth or improvement in human reasoning has been observed. No external source authenticity, secure collaborative protocol, online public app, Supabase backend, MEMENTO transfer, GRAFT promotion, self-modifying executable neural model, JAR;VIS rollout or independent discovery of new algorithms. The current decision function and test threshold are authored and classical.

The actual next ambitious hypothesis is whether sourced disagreement can help humans and a model **generate and choose different kinds of questions**, then demonstrate *independent* improvements on new consequential tasks. That requires source-owner verification, protected voluntary cross-device evidence, post-action outcome reviews, and strong classical active-learning controls.

**Principle:** A person who learns to reason without MOTIF is an outcome to celebrate, not an engagement loss. The machine is not entitled to data because more data might help it.
