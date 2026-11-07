# MOTIF QC-002 — INTO THE BREACH: THE UNNAMED TOPOLOGICAL VERB

**Status:** Synthetic graph rewrite induction; local preview only; NOT installed or merged.

## Provenance

QC-001 (MOTIF PR #182) mapped a given decoder, carrier, and named operation to a supplied next carrier. QC-002 removes that last assumption: it learns anonymous edge additions and removals directly from before/after graphs, and tests whether the learned effects work on larger, renamed, unseen graphs.

Source doors:

- [National Treasure: Primal Overlap](https://github.com/the-static-collective/national-treasure/blob/main/cases/quantum-code-glyph-circuit/PRIMAL-OVERLAP.md) — investigate operations on topology before attaching interpretive names.
- [National Treasure: QC claim ledger](https://github.com/the-static-collective/national-treasure/blob/main/cases/quantum-code-glyph-circuit/CLAIMS.md) — distinguish constructed mathematical models from physics claims.
- [Daily Slice: The Field Is Not the Message](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-26/the-field-is-not-the-message.md) — path, glyph, field, meaning, and authority differ.
- [Daily Slice: Grow a World That Knows How to Read the Seed](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-26/grow-a-world-that-knows-how-to-read-the-seed.md) — small carrier and changing decoder.
- [MOTIF-002](../002/motif002.py) — earlier graph-edit learning; unlike QC-002, this earlier method did not create new graph vertices.
- [MOTIF-006](../006/composition.py) — established source-pinned composite operators.

This new experiment builds on existing capabilities; it is not the first graph induction or macro composition in MOTIF.

## Frozen experiment question

Can a bounded learner infer an **unnamed graph transformation** from synthetic before/after pairs, transfer it to larger unseen graphs, and compose it to generate an induced four-cycle never demonstrated in any example?

## What was supplied, and what was not

Supplied: undirected simple graphs; two explicitly named anchor vertices; opaque intervention signals; before/after pairs; a finite grammar admitting exactly one new vertex and edits confined to the anchors and that new vertex; three TRAIN examples per signal, two VALIDATE examples per signal, six TEST examples per signal; a two-step / 500-state research search limit.

**Not supplied to the learner:** signal semantics, add/remove edge recipes, or the two-step solution. The evaluator fixture, separate from the learning functions, constructs outcomes for reproducibility.

The three hidden evaluator programs are (a) fresh-vertex brace that retains the anchor edge; (b) fresh-vertex edge subdivision that removes the anchor edge; (c) an apparent leaf-growing rule that contradicts its TRAIN effect in VALIDATE. The last one must HOLD.

Every learned candidate has reconstructible training evidence, independent local validation, and source checksums. A changed graph is the next step's input. A successful path becomes a pinned, replay-checked local macro. No source rule installs itself, and no tool call executes from that macro.

## Predeclared success/failure metrics

- **Novel effect induction:** 3 candidates; 2 validated; decoy signal held. A candidate with mixed training signatures or contradictory validation must never be admitted.
- **Unseen-size transfer:** 12/12 correct on covered held-out TEST examples, 6/18 held decoys. A whole-input memorization baseline has 0/18 coverage, because every TEST graph has new labels and a larger size.
- **Structural emergence:** output is an **induced four-cycle** from a two-vertex single edge within exactly 2 new operations; neither a 1-step plan nor a 0-rule planner should solve it. No example in TRAIN, VALIDATE, or TEST may contain that output topology.
- **Strong classical control:** an exact exhaustive classical depth-limited enumerator operating on the *same induced rules* must return the same optimal depth. A tie is expected.
- **Provenance/authority:** preserve stepwise source pins; changed signal, withdrawn rule, forged goal, forged receipts, overlapping splits, unallowed nonlocal edit, missing anchors, too many new vertices or unauthorized status must fail.

No test labels inform training or selection. The generated four-cycle is a new *composition of already inferred local rewrites*, not a newly invented physical law.

## Boundaries

This is ordinary classical symbolic graph rewriting. The two-anchor aperture, single-new-vertex grammar, simple-graph representation, signal cue, deterministic synthetic simulator, goal detector, state budget and test scenarios are all researcher-authored. The learner infers only the **specific edit effect**. It does not infer its own open-ended grammar, discover anchors from pixels, identify a new natural law, understand arbitrary human speech, invent quantum mechanics, or alter installed MOTIF. A conventional graph-rewrite learner may tie or beat it. Evidence IDs distinguish toy examples; they are not real independent witnesses.

The phrase **Quantum Code** names the user's research thread. This experiment contains no quantum algorithm, quantum hardware or physical glyph-wave measurement.

## Reproduction

Python 3.10+, standard library only:

    cd experiments/quantumcode002
    python -m unittest -v test_structural.py
    python structural.py

Workflow: .github/workflows/quantum-code-002.yml. Check the actual run, not just code presence.

## Next falsifier

Remove the hand-provided two-anchor aperture and the one-new-vertex cap, generate candidate rewrites from unlabeled neighborhoods, and compare against a **matched classical graph-grammar learner** on externally authored blind holdouts. Add contradictory sources and report unsupported patterns without guessing. This is a plausible next experiment, not a result of QC-002.
