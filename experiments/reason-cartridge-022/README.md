# REASON-022 — THE UNIMAGINED DISTINCTION
### Sometimes the helper has the *wrong kind* of concept

**Status: draft experimental code, completely read-only.** This branch stacks on REASON-021 draft PR #144 and the earlier unmerged MOTIF/REASON work. No source is a live person, no real moral or spiritual authority is claimed, and none of the hypothetical actions executes.

## Research question

REASON-021 showed that two hypothetical situations can have **identical known Boolean properties** and yet receive **different source-owner judgments**. That is a mathematically meaningful counterexample to the currently modeled feature set. The original experiment allowed the synthetic source to supply one more Boolean.

But what if the missing distinction is **not another YES/NO variable**?

- **Quantity:** "I need one more" is not the same state as "I have one already." Object identity, ownership and cardinality matter.
- **Time:** "Before I promised to come" is not interchangeable with "after." Order matters even if identical events appear somewhere in the story.
- **Triadic relationships:** "Alex gave Mary a parcel" is not the same as "Mary gave Alex a parcel." Directed source, object and recipient matter.
- **Duties:** A prior promise to a third person carries commitments and deadlines that cannot be replaced by "someone already has a duty." The parties and timing matter.

A neighbor's words may require us to **revise the representation language**, not just adjust a parameter. To test this without pretending we recruited real people, this experiment separates a **genuinely independently authored public reasoning benchmark** from **explicitly artificial Golden Rule and obligation scenarios**.

## A meaningful first: independent external source questions

Instead of evaluating only our own answer-key-generating scripts, REASON-022 downloads authentic, byte-pinned **Facebook bAbI** question/story data from the public third-party [iamtrask/Grokking-Deep-Learning](https://github.com/iamtrask/Grokking-Deep-Learning) repository, exact commit `e665168b4aefe3256360951504103cf98827ca51`. Every one of the **six** train/test files is validated against its original Git blob SHA.

This is a publicly published bAbI v1.1 copy, distinct from the v1.2 Hugging Face archive. Dataset author and original source credit: Jason Weston et al., *Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks*, 2015, arXiv:1502.05698; bAbI public dataset CC BY 3.0. The repo source names and hashes are recorded in `acquire.py`, with a machine-verifiable `provenance.json`.

We use these actual task categories:

| Independent bAbI task | Source file family | Appropriate representation |
|---|---|---|
| Task 7, counting | `qa7_counting_*` | A **quantity** typed item/owner inventory over the story's event sequence |
| Task 14, time reasoning | `qa14_time-reasoning_*` | An **ordered timeline** for each person, with source-cited predecessor events |
| Task 5, three-argument relationships | `qa5_three-arg-relations_*` | A directed **giver–object–receiver** event relation |

**All three engine algorithms were written by the experiment developer.** MOTIF did **not** spontaneously invent their code or discover the meaning of English. A finite evidence-calibrated router checks those candidate engines on **60 independent train examples per family** and selects a representation by source-validated competence. The answering engine never receives the official gold answer or the original supporting-line IDs. It can cite only a numbered statement actually present in its source story. Unsupported questions `HOLD`.

This is a concrete shift beyond the all-Boolean experiments, though a competent classical model-specific algorithm could tie or exceed the result.

### An important correction exposed by independent data

The **first** genuine external source run on questions 1–250 of each task was:

| Source category | First-run exact | Mistakes |
|---|---:|---:|
| COUNT | **226/250** | 24 |
| TIME | **250/250** | 0 |
| TRANSFER | **250/250** | 0 |

Those are **not blindly prospective results anymore**. We inspected the 24 counting failures and discovered that the hand-coded item-custody model failed to recognize source sentences using **"discarded"** or **"dropped ... there"**. The system acted as though an object was still being carried after it was discarded.

We did not erase the old behavior. `engines.count_before_source_repair()` preserves the exact earlier parser, and the repair extends its event grammar. The original 250-case counting development batch consequently improves from **226/250 to 250/250**, but that is **development performance on observed mistakes**, not an unbiased performance claim.

**To avoid laundering inspection into a heldout score, we explicitly reserved source questions 251–500 of every test task as a separate, prospective evaluation slice.** That is an additional **750 independently authored test questions** beyond the inspected 750 used for diagnosis. The new slice is only evaluated **after the source-repair code was committed**. The CI artifact exposes all errors and abstentions. The exact prospective scores are read from `reason-022-evidence/benchmark.json`, not assumed to be perfect.

### Measured prospective, untouched-post-repair slice (questions 251–500)

The source-pinned GitHub Actions evaluation, using **750 further third-party-authored questions that were not inspected during the counting repair**, returned:

| Independently authored family | Correct | Confidently incorrect | HOLD | Weak flat-answer control |
|---|---:|---:|---:|---:|
| Counting | **250/250** | 0 | 0 | 130/250 |
| Ordered time | **250/250** | 0 | 0 | 55/250 |
| Three-party transfer | **249/250** | **1** | 0 | 48/250 |
| **Total** | **749/750** | **1** | **0** | **233/750** |

### The one mismatch exposed a deeper source ambiguity

After freezing the independent prospective score, we inspected the sole disagreement in the three-party transfer test.

In the dataset's question **313**, the question asks what **Bill gave Mary**. The official source answer is **football**, supported by original story **line 22**. Yet **line 25** explicitly states that Bill also gave Mary an **apple**. The interpreter's deterministic "most recent matching transfer" rule therefore returned **apple**.

The scorer is entitled to mark the output wrong relative to its **one designated annotation**, but **both objects have explicit supporting source lines**. This is more subtle than a false statement about the story. The model's actual mistake is presenting a unique answer **without recognizing that the question is underdetermined by its wording**.

`ambiguity.py` performs an independent, **posthoc** scan of original external source lines. It verifies each alternative from source text, notes the official supporting-line IDs and records `MULTIPLE_EXPLICITLY_SUPPORTED_ANSWERS` without modifying the original prospective score. The evidence/HTML viewer now preserves this discrepancy. It does **not** claim that the bAbI authors intended multiple valid responses or that the official key should be changed.

This is precisely where a future MOTIF reasoner should emit **the competing source-linked answers, a request for disambiguation, or HOLD**, rather than overconfidently committing to whichever transfer happened most recently.

**The wrong transfer prediction remains a genuine recorded failure.** Its source question ID, original gold label, emitted answer and original story receipts are available in the evidence artifact; it was not "corrected" after the reserved prospective evaluation. The three engines are still developer-supplied classical finite-state programs. Now that these results have been examined, **this slice must be considered inspected for any later changes**; a new prospective test would require a genuinely further untouched slice or a different benchmark.

The complete exact-head regression run also passes **425 automated tests** (407 inherited; 18 new REASON-022 tests), plus the published external source-provenance and two-circle viewer assertions.

A separate weak old-view baseline always uses a single fixed answer per task. It is presented only as a diagnostic, **not as an optimal classical comparator**. The independently authored source task answers still cannot measure real ethical competence.

### A concrete typed impossibility witness

The prior model asks only something like:

```text
source facts exist? YES
question about an object's count? YES
```

Two source-authored stories can have the **same** such deliberately impoverished Boolean summary but different numerically correct answers. The experiment records source question IDs, the identical old summary and the distinct source answers. **No rule based only on that old summary can satisfy both.** This is not proof that Boolean logic itself is insufficient: suitable Boolean encodings can represent arbitrary finite state; the issue is that the old representation omitted identity, magnitude, order or direction.

This difference is vital. We are developing a **typed reasoning router**, not claiming to surpass mathematics.

## The Golden Rule still matters, so we tested obligations separately

The external bAbI tasks are not about promises, care, consent, duties or real human needs. We therefore implemented a second, **clearly synthetic** experiment in `obligations.py`, rather than pretending that correct third-party story QA proves ethical insight.

The toy representation includes:

- a previously owed obligation **directed toward an identifiable third party**;
- an amount of resources already promised and a deadline;
- available total resources, the time of day, and a maximum number of units that can be produced per hour;
- an additional recipient with a new proposed commitment and deadline;
- a **separate, explicit limit** on whether even an options discussion is welcome.

The time-aware checker verifies both the **total** resource budget and the **cumulative capacity available by every deadline**. For example, a helper cannot promise a unit of service due *right now* if the fixture allows zero time to produce it, even if there is enough theoretical total capacity later.

Seven fictional cases cover available capacity, conflicting promises, absent scoped consent, no contact, impossible deadlines, multiple prior recipients, and insufficient resources. A simple Boolean "has capacity and owes somebody" view cannot distinguish a permissible fictional situation from a conflicting one; the exact differing typed facts are preserved.

**The actual REASON-019 SELF, OTHER, MIRROR and CRITIC subprocess workers are run on these seven cases** — 28 original `python -I` subprocess invocations on the primary pass. The typed constraint precheck informs the original critic whether the proposal violates a prior duty. The critic can only approve **a read-only suggestion to discuss options**. It cannot purchase goods, contact a person, keep a promise, spend money or infer what love means.

These are real processes, **not secure VM security sandboxes or agent minds**.

## Code map

| File | Reproducible responsibility |
|---|---|
| `acquire.py` | Download six independent bAbI files at an immutable external commit, byte-check Git blob hashes, record attribution and provenance. |
| `corpus.py` | Parse numbered source stories, keep only facts/question as engine input, preserve gold/support fields exclusively for supervision or evaluation. Support separate development and prospective test slices. |
| `engines.py` | Three hand-written, typed source-proving algorithms: inventory/counted items, ordered time, giver–object–recipient; explicit HOLD on unsupported forms. Keep the initial source-mistake counter for honest benchmarking. |
| `router.py` | Train a finite routing decision from independent source answers; expose the weakest old-view counterexample pairs, and preserve unsupported-type HOLD. |
| `obligations.py` | Artificial directed duties with numeric quantities and deadline-based cumulative capacity; explicit source-owned permission conditions. |
| `mirror_bridge.py` | Import the actual Git-blob-pinned REASON-019 Golden Mirror and run its four subprocess elves on the seven artificial duty cases. |
| `trial.py` | Independently score the prospectively reserved 750 questions, record every wrong/held model prediction and its source ID, compare weak baselines, test all toy duty cases. |
| `viewer.py` | Make a fully offline interactive SVG **two-circle viewer**, allowing inspection of all actual external scores, failures and synthetic directed-duty outcomes. |
| `test_typed.py` / `test_viewer.py` | Adversarial regression checks of typed differences, genuine source provenance, quote-only evidence, honest inspection labels, duties/consent and offline visualization. |
| `.github/workflows/reason-cartridge-022.yml` | Run original MOTIF-003 + REASON-001…021 regressions, acquire third-party sources, run new tests, evaluate the reserved external slice, produce offline viewer and evidence artifact. |

### Reproduce with Python 3.11+

~~~bash
python experiments/reason-cartridge-022/acquire.py reason-022-sources
python -m unittest discover -s experiments/reason-cartridge-022 -p 'test_*.py' -v
python experiments/reason-cartridge-022/trial.py reason-022-sources reason-022-evidence
python experiments/reason-cartridge-022/viewer.py \
  reason-022-evidence/benchmark.json \
  reason-022-evidence/unimagined-distinction.html
~~~

The GitHub Actions artifact `reason-022-third-party-babi-typed-reasoning-and-duty-evidence` contains `benchmark.json`, `external-typed-source-audit.json`, `fictional-duties-and-original-elves.json`, `unimagined-distinction.html`, the source file checksums and task attribution. It includes **negative examples and incorrect answers**, not only successes.

## Hard scientific and ethical boundaries

1. **Independently authored *reasoning tasks*, not independently sourced human ethics.** No real participant was asked to share preferences, correct a live system or provide consent. The seven care/duty examples are authored by this project.
2. **The source's new language types were supplied by a developer.** The router chooses among three human-written algorithms rather than inventing arbitrary new algorithms, connecting to live accounts or understanding unfamiliar concepts in free-form conversation.
3. **The initial 250-question slices were inspected.** They are labeled *development*. Only the later 251–500 slices are prospective post-repair evaluations.
4. **Known vocabulary and data generators.** All three external tasks come from a classic toy NLP dataset. High answer accuracy is not broad intelligence, social understanding, or a test of actual legal/spiritual responsibility.
5. **The Golden Rule is more than a Boolean policy, but this isn't proof of moral truth.** The numeric/ordered/party-specific duty check is a limited synthetic resource feasibility exercise. It doesn't determine objective love, duty, lawfulness or welfare.
6. **No authority or intervention.** All responses have `permission_to_execute=false`; no private source, personal record, connected service or actual person is contacted.
7. **A strong classical baseline can match these results.** The three reasoners themselves are classical finite-state programs; there is no demonstrated performance advantage over domain-competent alternatives.

The conceptual advance is specific: **a helper can discover that its old feature summary cannot represent the distinctions a separate source requires, select among demonstrably different typed reasoning tools, diagnose errors against genuinely independently authored questions, correct a concrete bug, and preserve consent and third-party duties as separate constraints.**

The Golden Rule remains a test against projection—not a blank check to own another person's perspective.

## Next severe falsifier

Give the system an independently authored context whose **representation type isn't preinstalled**: a changing network of obligations, uncertain time intervals, quantities that cannot be summed, conflicting promises, indefinite beneficiaries, or source expressions that defeat the three known parsers. Test whether it can explicitly describe which operators it needs, propose a limited **new program** in a safe sandbox, and earn independent source-owned evidence before any admission.

Until that is done, **MOTIF has not demonstrated autonomous invention of a genuinely new representation type**—only bounded, inspectable typed reasoning and self-correction.
