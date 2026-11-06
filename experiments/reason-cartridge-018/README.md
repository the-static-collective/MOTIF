# REASON-CARTRIDGE-018 — THE LIVING CONCEPT

### Can MOTIF discover a relationship, rather than merely remember a new phrase?

**Status: experimental, source-owned, auditable and entirely synthetic.** This branch is stacked on the unmerged REASON-017 draft PR #127 (itself stacked on the prior experimental generations). It is not merged or deployed, has no third-party tool permissions, and must not be presented as evidence of artificial love, sentience or moral judgment.

## Why this is the next experiment

REASON-017 demonstrated a legitimate limitation of previous fixed vocabularies. When a simulated person said “Neither. I need dry socks,” MOTIF could preserve their words, confirm them, revise if corrected, and seek scoped permission before merely discussing options. That was **quote-level open vocabulary**, not understanding the new concept.

Now the target is a previously unnamed **relation**.

Can an executable reasoner infer **which relational structure** appears in source examples, discover a compact reusable composition of known graph primitives, and carry that concept across previously unseen and more complex graphs?

Can it preserve genuinely **contradictory** and **missing** evidence instead of forcing binary certainty?

And, when the source owner supplies **a new kind of relevant relation** that makes the previous interpretation inadequate, can it **HOLD instead of claiming to be permanently right**?

## Synthetic concept: “unowned assistance”

The target is an invented relational story, not an objective definition of love. It uses a graph of an actor A, recipient B, intermediary/alternative W, and declared edges chosen from exactly six primitive relations:

`OFFER`, `OPEN`, `RELEASE`, `FREE`, `CLAIM`, `LINK`.

The synthetic source owner stipulates that the new, *not primitively named* relation receives **positive evidence** when:

- A **offers** B an opportunity.
- B has an **open** path to some intermediary W.
- That **same W** has a **release/return** path to A.
- A and B have an explicit **FREE** (nonclaim) relationship.

This is an **existentially joined four-atom relational clause**. The identity of the *same* W matters: two disconnected “looks like a path” arcs do not amount to a complete route.

The source separately stipulates negative evidence if no complete joined path exists or if there is an explicit `CLAIM(A,B)`. Both FREE and CLAIM can be present; the engine must preserve that as `BOTH`. When an otherwise complete path has neither FREE nor CLAIM, the outcome is `UNDETERMINED`, not automatically proof of the negative.

These are formal toy predicates. A graph can exhibit these properties **without anyone actually caring or loving**, and a real loving relationship can lack them.

## What the code does

| Module | Role |
|---|---|
| `worlds.py` | Creates **88 unlabeled training worlds** and **55 distinct heldout worlds**; graphs include split-witness traps, reversed edges, contradictory FREE/CLAIM, unknown evidence, distractor edges, different node counts and longer irrelevant link networks. |
| `oracle.py` | An independently source-owned graph procedure supplies four-valued synthetic labels. **Not imported by the learner.** Source label receipts do not disclose the satisfying witness or hidden source rule. |
| `inventor.py` | Searches **5,184** automatically enumerated candidate relational ASTs, spanning four witness-direction families and ordered four-atom relation slots. It does not receive the target formula. |
| `inventor.discover` | Starts with one labeled example; chooses new synthetic training examples by **maximal disagreement among surviving four-valued predictions**. Each source answer eliminates inconsistent candidate expressions. Retains the complete evidence/version trace. |
| `inventor.prove` | Produces an explicit **single bound witness W and all four named source edges** when it makes a positive inference. It cannot invent a disconnected witness. |
| `reviewer.py` | Independently replays training against the original source owner, compares the fitted program to a different direct graph algorithm, and evaluates all **55** source-owned withheld graphs; refuses tampered/rehashed evidence. |
| `bridge017.py` | Imports the actual **source-blob-pinned REASON-017** `extract_goal` and confirms the old system produced only a quoted phrase, not a relational schema. |
| `drift.py` | Introduces a **new synthetic source revision** with a previously unavailable relation `WITHDRAWN`. An originally supported example now has contrary evidence. The existing grammar cannot represent this new source feature, so the result is **HOLD** and fresh learning is required—no silent retrofit or fabricated permission. |
| `trial.py` | Publishes the resulting learner, active counterexample sequence, all heldout four-state outcomes, source-drift evidence, and comparisons against a weak unjoined-edge baseline and a strong independent classical reference. |

### What was learned from source examples?

The CI demonstration searches the entire set of **5,184 syntactically distinct relational programs** and obtains source-owner answers on just **three selected training graphs**. In this deliberately constructed finite domain, these three observations reduce the program version space to **one source-consistent relational composition**.

The heldout population includes **different finite graph sizes, connectivity, distractor networks and missing or conflicting facts** rather than only renamed people. Neither the oracle nor the withheld reference labels are imported into the learner. However, **both train and test data were designed by the same source author and generator**, and the allowed program-language families were predefined. The result is not proof of generalization to independently authored natural-language ethical concepts.

### Exact experimental results

On the source-author's **55 heldout relational worlds**:

| System | Exact four-valued source outcomes |
|---|---:|
| **Discovered joined relational macro** | **55/55** |
| **Weak “any matching-looking edge anywhere” bag baseline** | **48/55** |
| **Strong independently implemented classical graph source reference** | **55/55** |

The new learner did **not** outperform a classical algorithm that already knows the source's rule. Indeed, the discovery process itself **is classical finite program synthesis**. It has created a new *named composite relation inside a DSL*, not a new logical connective, a language model, an emotional faculty or a source of moral authority.

Three observations are enough here because the fixture is designed to separate the candidate formulas. That number should not be extrapolated to unknown concepts or real people.

The **55/55** measures this fixed generated dataset, not human understanding. Each successful proof returns exact relation edges and the same-identity intermediary witness. All source-supported, refuted, contradictory and unknown categories are preserved.

### Falsifier: the model must admit its own representation is incomplete

The source owner later adds a seventh fact, `WITHDRAWN(B,A)`, with a new **source version**, invalidating a previously supported scenario.

This fact could not be expressed in the earlier six-relation alphabet.

The safe result is:

```text
old graph prediction:  SUPPORTED
new source evidence:   WITHDRAWN
new source conclusion: REFUTED
model response:        HOLD_NEW_SOURCE_FEATURE_REQUIRES_FRESH_LEARNING
automatic rewrite:     NO
human consent acted on: NO
```

This is source-versioned concept drift: **the corrected source outranks an outdated successful model**. The example is scripted and intentionally synthetic; nothing is inferred from a real person's withdrawal of consent. A mere invented new label or rehashed forged correction is rejected.

## Source provenance and anti-forgery

- Training graphs are source-recreated from original code, verified by their **Git blob** and digest; labels must reference a permitted training graph and answer exactly once within the allowed budget.
- The learner cannot obtain heldout labels through its training source interface.
- The independent reviewer replays the exact active-learning sequence against the owner, rather than trusting hashes supplied by the learner. Changing labels, source revision, premises, permissions, training samples or the compiled program causes failure.
- Graph witness edges are independently verified against the full original source graph; "the edges exist somewhere" without a **shared intermediary** is not evidence for the joined relation.
- The receiver requires an exact digest-bound **`ADMIT_READ_ONLY`** approval before producing evidence suggestions.
- The source-drift example produces a HOLD when a new required relation lies outside the learned grammar.
- Hashes bind records to known synthetic repository code. They do not authenticate external people, their identities, consent, actual well-being or any real-world fact.

## Reproduce

~~~bash
python -m unittest discover -s experiments/reason-cartridge-018 -p 'test_*.py' -v
python experiments/reason-cartridge-018/trial.py reason-018-evidence
~~~

GitHub Actions workflow: `.github/workflows/reason-cartridge-018.yml`. It also runs the original MOTIF-003 affordance tests, every REASON-001..017 regression test, and reacquires byte-pinned complete court opinion sources for REASON-014. It publishes an evidence artifact containing:

~~~text
reason-018-evidence/
    compiled-relation-cartridge.json
    benchmark.json
    heldout-four-valued-source-audit.json
    unrepresented-new-relation.json
~~~

### Critical limitations

This experiment does **not** show that MOTIF knows what love feels like, identifies real people's needs, understands unfamiliar English descriptions, makes trustworthy moral judgments, or creates new executable tools. The primitive graph symbols and relational AST shapes were designed in advance. The owner-rule and example generator were authored by the same developer. No independent human raters or diverse external tasks were used. This is not a blind study. The follow-up WITHDRAWN exception is a scripted new premise, not autonomous discovery from the world.

The real research advance is **a reproducible, source-bound step from quoted unfamiliar words toward inferred relational composition**, with correct source-witness binding and an explicit admission that a formerly successful model may become inadequate.

## Next rigorous step

Test with a concept supplied by an **independent source owner** whose relational vocabulary, example-generation process, and correction policy the learner designer never sees in advance. Let the reader generate *candidate graph predicates from ambiguous natural language*, require source-backed counterexamples and adjudicate disagreements among multiple interpreters. Preserve `HOLD` when meanings change or the source owner declines further questions.

**Care should involve not only good intentions or correct formulas, but also the willingness to be corrected by the other person.** REASON-018 models a tiny, checkable part of that requirement—without presuming that this is love itself.
