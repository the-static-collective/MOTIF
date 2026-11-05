# LAW-FORGE-006 — THE INSTRUMENT INVENTOR

## Can MOTIF propose a new measurement from low-level source capabilities, without receiving a finished sensor menu?

**Research question:** A previous four-link sensor interface is incapable of representing a newly encountered six-link graph. Does a finite learner discover a useful *derived observation program* by composing source-owned primitive link reads, and can that program survive independent source review, held-out tests, and an actual native Dogram mathematical challenge?

**Status:** bounded synthetic experiment, stacked on LAW-FORGE-005 (PR #65). No production merge, permission to scan real systems or unrestricted tool invention.

## What changes from LAW-FORGE-005?

005 compared seven **predeclared complete sensor categories**, including a ready-made reachability sensor and a ready-made ternary path count, on a **four-edge** graph.

006 receives **none** of those ready-made composite sensor categories. The new evaluator owns a six-link graph with three distinct two-hop relays:

```text
      R0
     /  \
  S       T
     \  /
      R1
     \  /
      R2          (three independent S→relay→T paths)
```

The source contract advertises only one low-level capability: `READ_ONE_SYNTHETIC_LINK`, indexed 0–5. The learner may **compose** source-owned primitives using a typed, read-only `OR_OF_AND` AST with up to three clauses and up to two link atoms per clause. It exhaustively enumerates 1,561 permitted candidate programs (six single-edge atoms and all two-edge conjunctions; up to three OR terms), derives predictions from original source observations, and chooses the simplest consistent formula.

A proposed example discovered from data:

```text
(READ_LINK(0) AND READ_LINK(1))
 OR
(READ_LINK(2) AND READ_LINK(3))
 OR
(READ_LINK(4) AND READ_LINK(5))
```

This is a genuinely *new executable measurement program relative to the previously provided sensor menu*. It is **not** invention of the underlying Boolean logic, unrestricted code synthesis, new physical hardware, or an independently discovered topology; the six link addresses and topology are disclosed by the source owner.

The source owns the actual graph evaluator and separately checks every candidate. The learner cannot call it freely, alter its rules, or authorize itself to deploy. Source packets are data only, content-addressed, strictly schema-checked, and explicitly `PROPOSE_ONLY`.

## Query / training / falsification boundaries

A fixed source-owned initial batch supplies 32 graphs with link 4 absent. The proposed inquiry requests the remaining 32 controlled graph settings, under a strict 32-query cap. The source owner evaluates these locally. **No claim of active query optimization** is made: this first trial uses complete finite factorial coverage by design.

The synthesizer then fits its AST against 64 distinct source observations. The owner separately reviews it on all 64 graph configurations with a different synthetic partition, and tests it on 64 further withheld observations. Matching graph configurations under separate partitions do **not** prove new-domain generalization.

The source rejects proposals which cannot be expressed by the allowed max-three-term, max-two-atom grammar or which fail independent review. Models that are only superficially compatible with inquiry data but become false under changed hidden context must be **held**, not promoted. A renamed destination must re-review. The owner's local compiler cannot grant GRAFT intake or production authorization.

## Thirteen hidden evaluator worlds

| Hidden evaluator condition | Expected behavior |
| --- | --- |
| Any of three two-hop paths exists | Invent three-conjunction / three-disjunction measurement |
| Any of first two paths | Invent two-conjunction measurement |
| Last two-hop path only | Invent one-conjunction measurement reading the new last two links |
| Two cross-link conjunctions | Invent a different two-term measurement |
| OR of two separated edges | Invent two single-read clauses |
| Single middle link | Retain a one-atom sensor |
| First two-hop path | Retain a simple two-atom sensor |
| At least two paths | HOLD: needs four-atom interactions |
| Exactly one path | HOLD: non-monotone concept absent from grammar |
| Parity of six links | HOLD: XOR absent from grammar |
| Three edges jointly active | HOLD: three-way conjunction absent |
| Review-phase hidden shift | HOLD independent falsification |
| Hidden context on fully active graph | HOLD independent falsification |

The worlds are **researcher-authored simulations**. Seeds generate no new hidden laws. Independent tests protect training/test boundaries but do not constitute independent physical science.

## Explicit strong baselines and controls

All methods receive the **same 64 controlled source observations** and identical review partitions.

1. **Instrument inventor:** composes the restricted read-only AND/OR AST; must abstain on out-of-grammar worlds.
2. **Old four-link interface:** classical exact lookup on only the first four observable links; cannot distinguish facts dependent on links five and six.
3. **Complete six-link raw baseline:** classical 64-entry lookup table on all six source readings; serves as an information-complete upper-bound control.

A source-language expansion should improve coverage over the artificially restricted old four-link interface, but the complete raw baseline can represent **every stationary binary function** on six known bits. It should generally win on coverage; the AST may provide an interpretable, compact measurement description instead. Any apparent advantage must account for synthesis work, sensor acquisition, deployment, and other costs not measured here.

Development seeds 0–1, heldout seeds 2–6. A frozen method-promotion rule requires the proposed method exceed the full raw baseline by at least two eligible worlds without extra errors; otherwise `NO_METHOD_PROMOTION`. No automatic promotion occurs regardless.

## REAL native Dogram bridge; ALEX and GRAFT proposals remain separate

Here is the practical new seam:

- **Dogram:** the GitHub Actions workflow checks out the **original** public `the-static-collective/Dogram` repository at immutable commit `551b5f9df18f17ec69b452ddcdff01718e0ff771`, and executes **its native** `python -m dogram.cli` binary on three local `dogram.specimen/v0` graph-`ablate@1` specimens. In each specimen one two-hop path exists, and one edge is removed. The experiment asserts native `dogram.receipt/v0` reports that `S → T` was reachable before and not afterward. This is independently implemented graph arithmetic; it does **not** prove real causality or unrestricted sensor validity. Dogram produces its own native receipts; a synthetic imitation is rejected by the verification tests.
- **ALEX.2:** emit a complete, layered **`motif.law-forge.alex-intake-proposal.v1`** envelope retaining raw synthetic source observations separately from model interpretation and independent review. Status is `PROPOSE_TO_ALEX_NOT_STORED`. This does **not** invoke ALEX's native persistence or claim that ALEX has accepted the packet; it is a proposal for source-owned intake.
- **GRAFT:** emit `motif.law-forge.graft-intake-proposal.v1`, including original source capability contract, data-only synthesized program and the synthetic source's independent read-only compiler result. Status is `PROPOSE_TO_GRAFT_NOT_IMPORTED`. No original GRAFT compiler or admission path is invoked, and no new GRAFT branch or production adapter exists from this PR.

The latter two are *explicitly MOTIF-authored handoff proposals*, not impersonations of ALEX or GRAFT schemas. They are useful for an owning-project review before claiming any genuine integration. The native Dogram validation is the one real cross-repository operation built in this experimental slice.

This separation respects ALEX's object→scan→reading→interpretation→claim layers and Dogram's principle that graph reachability is **not** proof of causal or historical occurrence.

## Reproduce

Python 3.10+; the main synthesizer uses only the standard library:

```sh
python -m unittest discover -s experiments/law-forge-006 -p 'test_*.py' -v
python experiments/law-forge-006/trial.py > law-forge-006-results.json
python experiments/law-forge-006/bridge.py emit law-forge-006-receipts
```

Run the [dedicated GitHub Actions workflow](../../.github/workflows/law-forge-006.yml) to execute native Dogram in its pinned original repository. The workflow verifies all inherited LAW-FORGE-001..005 tests, new 006 adversarial tests, stores a complete JSON benchmark receipt, emits ALEX/GRAFT proposal handoffs, and verifies all three original Dogram ablation receipts.

**Do not state benchmarks or native integration as verified until CI completes successfully.**

## This is not proven

- The source supplies low-level link identities and topology; unknown sensors are *not* automatically discovered in arbitrary external systems.
- The finite grammar is pre-supplied (AND/OR of source links), and the batch protocol is exhaustive, not adaptive or energy-optimized.
- Result is a classically synthesized derived measurement—not previously unknown mathematics, a spontaneously invented source API, or unrestricted new senses.
- The source owner and learner are separately packaged **within a single research team**; independent human/device validation is absent.
- No trinary axiom is privileged. A new three-path graph is not evidence that the number three is fundamental.
- The Dogram comparison is *native and cross-repository* but confined to chosen toy paths; the ALEX and GRAFT **real runtimes remain unconnected**.
- Content SHA-256 checksums prove byte identity, not the legitimacy of witnesses, permissions, or causation.

## Next exact frontier

Require the source owner to reveal **only a typed primitive capability contract** for a novel input schema while the learner's AST template remains frozen. Ask it to propose a new *safe interpreter primitive*, not merely an AND/OR composition, and verify it under cross-project source-owned GRAFT conformance. Build native ALEX intake only after its current code contract has been inspected and accepted. The new source owner must hold back the test semantics; no benchmark may be rewritten after test results.
