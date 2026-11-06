# REASON-CARTRIDGE-009 — THE GRAMMAR INVENTOR

**Status:** implemented, synthetic, source-pinned research; stacked on experimental REASON-008 PR #93, with earlier drafts below it. This does **not** merge, deploy, publish or admit any method to a real-world agent.

## What we actually changed

REASON-008 discovered a missing *fixed* extension type: `OR(AND3,AND2)`. But it could only search the 100 candidate programs in a developer-supplied extension family.

**REASON-009 no longer receives that extension family.**

The learner receives only five named Boolean edge inputs and the two known binary primitive operators **AND** and **OR**. It builds binary recursive abstract syntax trees from these atoms using bottom-up dynamic programming, with a finite cost/node budget:

```text
EXPR := EDGE(i) | AND(EXPR, EXPR) | OR(EXPR, EXPR)
i in 0..4; no negation, no loops, no unknown operations
max expression tree nodes: 11
```

It canonicalizes by the resulting 32-state truth-table signature to avoid equivalent syntactic trees acquiring multiple artificial discovery credits.

The entire search enumerates **1,727 distinct semantic expressions** at odd AST sizes 1,3,5,7,9,11; not an infinite search and not new fundamental Boolean primitives.

### The real improvement: counterexample-guided grammar construction

The learner **never imports** the source-owned `source.py` BFS evaluator or reads sealed holdout labels. Instead:

1. Receive **five independently owned public examples**.
2. Start with the cheapest expression tier; enumerate *every semantic candidate* expressible at that tier.
3. When many candidates agree with examples, request the **most discriminating admissible observation**; the source owner returns one labeled synthetic graph.
4. When one candidate remains, challenge it with a source-owned bounded counterexample checker. The checker returns a single observed contradiction or a **PASS_ACQUISITION**, which expressly does not certify the eight sealed holdouts.
5. If all candidates at a tier are refuted by observed labels, record an independently recomputable SHA-addressed finite **gap certificate**, then widen the grammar budget.
6. Emit the smallest surviving typed AST and derive a human-readable macro shape **from the expression tree**, rather than choosing a preapproved AND3+AND2 shape.
7. A separate `Receiver` verifies that all public source labels match independent BFS; tests **eight sealed holdout graphs** and audits all 24 acquisition states **after** synthesis. It admits only a digest-bound **SUGGEST_ONLY** proposal.

Every attempted query, answer, challenge and tier widening can be **deterministically replayed from the public observations**; fabricated rehashed transcripts or grammar-gap proofs HOLD. The source owner can decline further queries when the explicitly bounded budget is exhausted.

## Two genuinely different source-owned graph structures

The same **unchanged inventor algorithm** is used on two nonisomorphic five-edge directed graphs. Both are independently evaluated by a classical source-owned BFS, not by the learner's synthesized Boolean formula.

**A. Long + short routes** (existing REASON-008 topology):

```text
S --e0--> A --e1--> B --e2--> T
  \\--e3--> C --e4--------------> T
```

The learned minimal binary AST has **9 nodes**, and represents `(e0&e1&e2) OR (e3&e4)`.

**B. Interconnecting bridge** (new, nonisomorphic topology):

```text
         A --------> T
        / \\       ^
       /   \\      |
      S ---> B -----+
```

Five edges: `e0 S→A; e1 A→T; e2 S→B; e3 B→T; e4 A→B`.

The reachable condition is `(e0&e1) OR (e2&e3) OR (e0&e4&e3)`. It admits a shorter factored form. The learner finds an **11-node binary AST**, without being supplied a rule describing the three alternative route terms or how to factor them.

The fixed prior REASON-008 `OR(AND3,AND2)` extension is **not sufficient** to describe the bridge function across all 32 states; the new recursive grammar is. This checks transfer of the **grammar-invention procedure** across different graph structures, **not** zero-shot transfer of one graph-specific formula.

| Criterion | Long + short | Bridge |
|---|---:|---:|
| Initial labeled examples | 5 | 5 |
| Minimal discovered AST size | **9** | **11** |
| Sealed independent owner checks | **8/8** | **8/8** |
| Full post-synthesis 32-state audit | **32/32** | **32/32** |
| Renamed future tasks | **64/64** | **64/64** |

All future tasks are isomorphic renamings within the corresponding already-discovered topology, not arbitrary new graph types, and the 32-state space is exhaustible because this is a small synthetic problem.

## Additional genuinely independent algorithm crosscheck

The GitHub Actions workflow checks out **original unmodified Dogram** at pinned revision `551b5f9df18f17ec69b452ddcdff01718e0ff771`, executes its *actual* native ablation engine on **64 instances** (32 of each source family), and saves the original `dogram.receipt/v0` records.

A disconnected decoy edge `U→V` is removed, leaving `S→T` reachability unchanged. The original Dogram checkout is then **deleted**. Only after its removal does an independently implemented verifier replay the source-owned classical BFS result and validate the 64 native Dogram receipts.

**64/64 original Dogram vs independent source BFS agreement.**

This is an **independent algorithm crosscheck on declared synthetic graph inputs**, not a second observed fact about the external world. Native source hashes and content digests do not authenticate human identity.

## Critical controls and limitations

The important scientific distinction:

- **A new restricted grammar shape is synthesized; a new mathematical primitive is not.** Boolean AND/OR and a strict search bound are developer-defined.
- The two source graph topologies and five source examples are synthetic, not discovered in the wild.
- The source owner's acquisition checker knows the finite truth labels, but only releases queries/counterexamples outside the eight sealed holdout masks.
- Eight holdouts are independent of fitting and challenges; all 32 inputs are checked in the **post-synthesis evaluation**, after learner output is frozen.
- The same program-synthesis procedure can be written in classical search/CEGIS; we claim no superiority over optimal program synthesis or automated theorem proving.
- The general expression grammar searches at most **11 nodes**, without recursion as an executable runtime capability, real third-party adapter invention, arbitrary code emission, neural training or new operators.
- The cost model charges source questions, independent holdout checks, enumeration over all 1,727 semantic candidate signatures and future inference under **explicitly hypothetical per-operation units**. It is not measured speed, GPU energy or financial value. Under these declared costs, a single task favors direct BFS and a 64-case workload favors compiling a reusable graph-specific method.
- A query budget exhausted before certification HOLDS. An unsupported topology HOLDS. Additional observations never become real-world facts merely because an inference is mathematically sound.

## GRAFT and CANNON boundary

REASON-008 already produces a source-review-only proposal compatible with actual GRAFT and CANNON policies. REASON-009 does **not** import or publish into GRAFT, does **not** select a CANNON canon, does **not** sign an authorization, and does not run any external build. Any promotion would require separate source-owner review, code/history/licensing checks and explicit authority.

## Reproduction and provenance

```sh
python -m unittest discover -s experiments/reason-cartridge-009 -p 'test_*.py' -v
python experiments/reason-cartridge-009/trial.py reason-009-evidence
```

The local command uses a deliberately identified synthetic source-owner oracle; **native original Dogram execution is CI-only** in `.github/workflows/reason-cartridge-009.yml`.

The workflow runs inherited REASON-001…008 regressions; new grammar, evidence, forgery, source isolation and owner review tests; all 64 original pinned Dogram experiments; and creates inspectable artifacts:

```text
reason-009-evidence/
  long_short-method.json
  bridge-method.json
  long_short-certification.json
  bridge-certification.json
  long_short-oracle-trace.json
  bridge-oracle-trace.json
  benchmark.json
reason-009-native/
  manifest.json
  reason-009-long_short-00..31.json
  reason-009-long_short-00..31.receipt.json
  reason-009-bridge-00..31.json
  reason-009-bridge-00..31.receipt.json
  conformance.json
```

## What would falsify this step?

- A 9-node grammar representation passes all **bridge** source states: the claimed need to widen to 11 is false.
- Source-owner query responses mismatch the requested feature mask, are repeated or reach protected holdouts: HOLD.
- Any lower-tier language-gap certificate cannot be reproduced from observed source labels: HOLD.
- A modified program, changed authority, rehashed fake counterexample, skipped review or modified source pin is accepted: fail.
- Any one of the eight withheld cases is wrong: receiver must not admit.
- Original Dogram gives a different result on any of the 64 native specimens: native CI fails.
- An optimal classical solver matches or outperforms the proposed inventor: **not a contradiction**; expected under this design.

## Next genuinely harder scientific test

The next honest improvement is to let different source-owned problem domains compete for the same grammar-repair machinery—not just two kinds of five-edge reachability—and compare against **enumerative synthesis, e-graphs, CEGIS and solver-guided inductive synthesis** on genuinely heldout DSL tasks. More broadly, the learner would need to propose **which operators, types and semantics** should be added, rather than only building new shapes from the same fixed AND/OR vocabulary. That would be a more meaningful test of primitive invention.

This experiment is a precise, inspectable step toward that frontier—not a claim of already having crossed it.
