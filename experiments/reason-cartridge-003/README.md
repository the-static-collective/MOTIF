# REASON-CARTRIDGE-003 — FOREIGN TEACHER / OBJECTION ENGINE

**Status:** source-pinned experimental cross-repository test, stacked on REASON-CARTRIDGE-002 (draft PR #73), itself stacked on REASON-CARTRIDGE-001 (#70). This is **not** merged, published as a service, permissioned for arbitrary action, or evidence of general intelligence.

## Research question

Can MOTIF observe an **original, independently owned reasoning instrument**, infer a reusable local *method choice* from its public answer receipts, then perform unfamiliar synthetic tests when the teacher's code is absent? And can it improve classical reasoning's **epistemic interface** without pretending Boolean logic is broken?

## Native foreign teacher: ORIGINAL Dogram

The CI workflow checks out **unmodified Dogram** at exact commit `551b5f9df18f17ec69b452ddcdff01718e0ff771`, runs its real `python -m dogram.cli` ablation engine on strict `dogram.specimen/v0` synthetic graph queries, and preserves its native `dogram.receipt/v0` results.

- **Training:** 12 source-owned Dogram receipts on five-node directed graph experiments, stratified into disconnected, vulnerable, and redundant route cases.
- **Withheld:** 18 native Dogram receipts on different six-node graph topologies, independently stratified, **not passed to the pupil**.
- Dogram is deleted from the job's external checkout **before** pupil learning and receiver evaluation. Its published outputs remain; neither pupil nor receiver imports Dogram.
- The pupil selects from **five developer-supplied read-only candidate algorithms** according to its match on independently verified, original native Dogram receipt labels. The only successful survivor is a *recheck of graph reachability after removal*.
- A separate local receiver must verify the pinned source contract and heldout native receipts, replay a strong complete BFS baseline, refuse stale/tampered claims, and explicitly `ADMIT_READ_ONLY` before offering any suggestion. This is an **offline fixture decision**, not a human adoption or production permission.

**Expected outcome on this preregistered synthetic fixture:**

| Strategy | Heldout native graph labels |
|---|---:|
| Always assume edge removal breaks the route | 12/18 |
| Reuse previous graph reachability | 12/18 |
| MOTIF's selected recheck-graph method | **18/18** |
| Full classical BFS on post-removal graph | **18/18** |

This is **behavioral teacher distillation** (choose among supplied methods based on its outputs), not reconstruction of Dogram's own internal algorithm, source code, private thoughts, or a newly invented graph-search algorithm. An ordinary classical BFS algorithm matches the learned method; no special advantage over complete-information classical reasoning is asserted.

The teacher's native receipt digests verify content consistency **only**, not real-world identity, authentication, or trust in arbitrary user-supplied data. The independently verifiable CI run and pinned Git revision provide the bounded execution provenance for this trial.

## The classical-reasoning gripe: “No proof of a route” ≠ “proof of no route”

`objection.py` introduces an **epistemic envelope** *around* classical graph search. It does not challenge classical logic's mathematical soundness.

Its key distinctions:

1. **Open world vs closed scope.** A positive path can be certified from confirmed edges even in an open world. A **negative** assertion requires either an explicit complete universe of possibilities or a separate stronger proof. The absence of an observed path does not by itself establish nonexistence.
2. **Conflict is evidence, not omniscience.** If two attributable sources disagree about an edge, the edge remains unresolved. No arbitrary conclusion or silent overwrite follows. This is a narrow paraconsistent *evidence-handling policy*, not a new theorem.
3. **Proofs or questions.** A positive answer returns a checkable path. A closed-world negative answer returns a checkable finite cut. Otherwise the engine returns `UNKNOWN` / `HOLD`, often with a specific edge whose verification would change the conclusion.
4. **Proof fragility: what would have to break?** Every confirmed reachable path can be accompanied by a minimum directed-edge cut over confirmed evidence. This says exactly how many independently supported graph edges must be retracted before all confirmed routes vanish. It is deterministic structural sensitivity, **not** an empirical failure probability or proof that sources are independent.\n5. **Cost of NOT asking.** When no proof exists, with at most eight uncertain edges and an **explicit hypothetical equal-weight prior**, enumerate compatible worlds, calculate asymmetric false-positive/false-negative regret, and propose the cheapest *consequential* single question. A high query cost or no discriminatory question yields HOLD. These are **illustrative decision-theoretic weights**, not observed probabilities, money or empirical harm.

The objection engine never invents a missing fact, presumes a response, sends a question, grants permission, or dispatches an external act. `check_certificate()` independently checks returned witnesses or cuts relative to declared assumptions.

## Source and project ownership

- MOTIF owns the portable read-only method and receiver contracts.
- Original Dogram owns its CLI runtime and answer semantics. No modifications to Dogram.
- Existing MOTIF-007 operator inheritance, MOTIF-009 decision tree cartridges, REASON-001/002 teaching research, GRAFT and CANNON remain separate from this run.
- No Dogram provenance/privileges transfer to MOTIF. No GRAFT code generation or admission. No ALEX storage or T5 calls.
- **Known limits:** finite pre-supplied solver menu, synthetic graphs, explicit finite scopes, no calibrated epistemic priors, no real teacher explanations, no dynamic source API, no cross-domain live outcomes.

## Reproduce

Local adversarial/test-double tests (no Dogram installed):

```sh
python -m unittest discover -s experiments/reason-cartridge-003 -p 'test_*.py' -v
```

The **real-native** experiment requires the dedicated GitHub Actions workflow `.github/workflows/reason-cartridge-003.yml`, which downloads pinned Dogram and writes its actual receipts, verifies absence after checkout deletion, then generates `reason-003-evidence/learned-cartridge.json` and `reason-003-evidence/evaluation.json`.

Test doubles in `test_foreign.py` are explicitly labeled local simulations and are *not* the independent native teacher used to substantiate the cross-repository claim.

## Falsifiers

- A mismatching or refused original Dogram receipt -> HOLD.
- No unique solver after the 12 lessons -> HOLD.
- Learned method failing any withheld native label -> receiver cannot admit.
- Strong full-information classical BFS matching our solver -> **no claim of improvement over classical search**.
- Contradictory or unlisted edge evidence -> UNKNOWN, not false or arbitrary true.
- Question whose declared expected regret reduction is lower than its inquiry cost -> no recommended question.
- Changed SHA/source contract, unsupported method, forged authority, missing receipt, broken proof -> HOLD.

**Next specific frontier:** discover a *reasoning question or proof obligation* for which classical BFS still supplies the correct answer but an ordinary planner is missing the **useful next observation**. Test the objection engine on a source-independent dynamic-world benchmark and measure how often its questions actually eliminate uncertainty at matched evidence budgets.
