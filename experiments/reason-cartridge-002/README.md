# REASON-CARTRIDGE-002 — THE METHOD DISTILLERY

**Status:** experimental, stacked on [REASON-CARTRIDGE-001 PR #70](https://github.com/the-static-collective/MOTIF/pull/70); not merged, deployed, or externally executed.

## Hypothesis

Can MOTIF learn a **new, conditional reasoning procedure** by studying the *publicly observable steps and corrections* of two different solvers? The pupil is not granted either teacher's private implementation, model internals, raw chain-of-thought, credentials, or decision authority.

In this strict Python standard-library synthetic test, **TEACHER_A** knows how to check a source, perform an exact lookup, and draft. **TEACHER_B** knows how to check a source, test a counterexample, and draft. One neutral question distinguishes conditional from unconditional steps.

Neither teacher is demonstrated solving a case that needs **both** lookup and counterexample testing. The pupil therefore has three public demonstrations: lookup-only, counterexample-only, neither.

The pupil uses an explicit **small guard grammar** and a bounded partial-order synthesis procedure. It validates every claimed transition against the source-owned toy interpreter. It infers:

```text
VERIFY_SOURCE
IF need_lookup:    EXACT_LOOKUP
IF need_challenge: TEST_COUNTEREXAMPLE
DRAFT_HYPOTHESIS
```

This is a third conditional **method program**. Neither teacher supplied it as a whole. The unresolved relative order of lookup and challenge is **explicitly preserved in the cartridge**; both possible orderings are compared by the receiving evaluator in unfamiliar combined cases.

## Actual results of the local synthetic run

| Control | Independently labeled synthetic cases |
|---|---:|
| Single-teacher router / rote procedure replay | 8/9 |
| Learned method cartridge | **9/9** |
| Fully informed classical breadth-first search (same exact source interpreter) | **9/9** |

The ninth case is a joint challenge that the two isolated teachers did not demonstrate. Five of the nine are deliberately refused missing-source / missing-tool / unresolved-contradiction cases, four are successful toy procedures. There are **no external teachers, language tasks, novel primitives, or real-world outcomes** in the benchmark.

**Important:** a fully informed classical planner matches the distilled method exactly. The result is not an algorithmic breakthrough over classical graph search. It establishes that observed *teacher procedures* can be converted to a different conditional program under a fixed, inspectable DSL and independently tested in an unseen combined configuration.

## Source ownership and admission

- `teachers.py` owns both test teachers; `distillery.py` imports **only** `language.py`, never the teacher program.
- A teacher offers a *claimed*, content-hashed sequence of public before/after step observations. Hashes are **not signatures or authenticated custody**. The pupil checks each step against the owner-supplied simulator; identity and real expertise are not authenticated.
- The portable artifact has schema `motif.reason-procedure-cartridge.v1`, strict allowlisted steps/guards, a pinned source-revision string, and references to three lesson receipts. No raw conversations or private teacher reasoning are exported.
- A new receiver **HOLDs by default**, tests independent positive/negative cases **and both undetermined step orderings**, and requires an explicit digest-bound `ADMIT_READ_ONLY` decision.
- Even admission permits only **SUGGEST_ONLY** read-only synthetic recommendations. It does not grant real-world access or exercise actual lookup, authorizations, messages, or external actions.
- Contradictory/missing lessons, corrupted transcripts, unknown methods, changed source semantics, stale review digests and privilege-bearing packets are refused.

## Reproduce

```sh
python -m unittest discover -s experiments/reason-cartridge-002 -p 'test_*.py' -v
python experiments/reason-cartridge-002/demo.py
```

Both commands use Python 3.10+ standard library, offline and without API credits.

## Falsifiable next crossing

Replace a synthetic teacher with a **source-owned adapter** to an actual opt-in trace-producing instrument (Dogram, ALEX, T5 sidecar, classical planning or a human teacher). The teacher must voluntarily expose inspectable procedures and source revisions. Compare learned procedures against **strong matched classical program-synthesis baselines**, include changed-world failures, and seek independent owner review before any Door Foundry/GRAFT proposal. Importing a program must never import the donor's permissions.

**Not claimed:** hidden-thought extraction; general algorithm invention; neural learning; metacognition; arbitrary teacher assimilation; autonomous action; cross-domain empirical transfer; physical-world verification; GRAFT or CANNON integration; production readiness.
