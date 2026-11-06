# REASON-CARTRIDGE-008 — THE MISSING PRIMITIVE

**Experimental, source-pinned and read-only.** Stacked on unmerged REASON-007 PR #90 (itself on #88, #84, #80, #77, #73 and #70). This is NOT a deployed reasoning system or evidence of universal invention, original computer architecture, calibrated intelligence or general-purpose program synthesis.

## What is actually missing?

In REASON-007, the method inventor used **one flat OR of two 2-input AND terms**, each over four Boolean graph-edge features. Such a grammar can recognize a union of two 2-hop paths.

REASON-008 introduces a **new graph structure** with five potential directed edges:

```text
S --e0--> A --e1--> B --e2--> T
 \                             
  +----e3--> C ----e4-------> T
```

Reachability requires `(e0 AND e1 AND e2) OR (e3 AND e4)`.

We give the old language the benefit of the doubt: expand its input count to **five**, allow *any two* of the ten possible 2-input edge conjunctions, and enumerate **all 45** candidate programs. None matches the five publicly observed teacher cases `[3,5,6,7,24]`.

The learner supplies a **checkable counterexample for every one of the 45 candidates**. Thus the *declared finite DSL* cannot represent the observed behavior. This does **not** show Boolean logic itself is insufficient: a nested AND2 can express AND3. The "missing primitive" is a missing **typed macro / allowed grammar shape**, not the discovery of a mathematically novel fundamental Boolean operator.

## Controlled invention

Only after proving that finite gap does `discover.py` search a deliberately restricted extension: `OR(AND3,AND2)`. There are `10 triple choices × 10 pair choices = 100` candidate typed programs on five inputs.

Exactly **one** of the 100 is consistent with all five public lessons:

```text
AND3(e0,e1,e2) OR AND2(e3,e4)
```

The learner **does not import or call `source.py`'s original BFS**, and never reads its withheld source labels during invention. It recomputes the proposed typed expression through a bounded, non-`eval`, non-shell interpreter. Its data-only method cartridge, `motif.reason.missing-primitive.v1`, includes all five lessons, 45 finite refutation witnesses, the one typed macro, source Git blob, checksum and explicit no-authority fields.

This is finite constructive grammar repair and symbolic macro synthesis, not unrestricted invention of adapters, neural representations, generators, external actions or novel general algorithms. The grammar-extension family is **developer supplied**.

## Independent certification

- **27/27** remaining five-edge feature configurations are withheld from synthesis and tested by `receiver.py` using independently implemented source-owned classical BFS.
- **32/32** possible configurations are independently checked by the actual unmodified **original Dogram** at Git commit `551b5f9df18f17ec69b452ddcdff01718e0ff771` in GitHub Actions. Native `dogram.specimen/v0` ablation removes a disconnected decoy edge `U→V`, leaving graph reachability `S→T` unchanged. Actual native `dogram.receipt/v0` results must agree with the source-owned independent BFS; the checkout is **removed** before final native-receipt review.
- A source-owner receiver requires the complete 27-case review and digest-bound explicit `ADMIT_READ_ONLY` for local **SUGGEST_ONLY** use.
- The "new topology" differs from REASON-007's two 2-hop routes. Future tasks are **isomorphic relabelings** of this same five-edge topology, not tests against arbitrary unseen graph classes. A six-edge or unknown schema **refuses**, not guessed.
- Agreement between native Dogram and independent BFS tests *computation under synthetic declared graph inputs*. It does **not** establish that graph edges describe the external world.

## Evaluate whether invention is worth its price

The previous REASON-006 Commonwealth `Ledger` is actually reused from its exact content-pinned source. A market with bounded choices and duplicate-credit suppression compares one-off classical BFS with the new certified macro.

All prices are fictional declared utility units, **not observed GPU time, money, emissions, or inference latency**. The cost model **does not include** original Dogram extra audit/CI runtime:

| Declared hypothetical unit cost | Units |
|---|---:|
| Source teaching label | 0.5 |
| Independently checked heldout label | 0.5 |
| One-time typed macro design | 3 |
| One macro evaluation | 0.25 |
| One classical BFS source lookup | 1.5 |
| Omitting an answer | 6 |

The upfront macro cost is `5×0.5 + 27×0.5 + 3 = 19`.

| Prospective workload | Direct source BFS | Composed macro | Winner |
|---|---:|---:|---|
| 1 task | **1.5** | 19.25 | Direct query |
| 32 tasks | 48 | **27** | Typed macro |
| 64 tasks | 96 | **35** | Typed macro |

With 32 renamed synthetic graph tasks, **32/32** composed answers match independent classical BFS. The market awards 21 *nontransferable hypothetical savings points*, zero for the duplicate macro offer, one first-seen source-validated **method** contribution to the inherited Commonwealth ledger, and **zero** new observations/facts about the world.

A classical optimizer with the same fully known source graph structure, program candidates and costs can make the same decision. We do **not** claim outperforming optimal classical planning, BFS, memoization, partial evaluation, program synthesis or verified compilation.

## The GRAFT / CANNON doorway — no automatic admission

We checked the actual public source-owning rules:

- **GRAFT** is a branch-separated clean-history source review/import nursery. Import requires reviewed code cuts, license and provenance, credential/secret checks, native tests and an explicit publication decision; it is not an auto-compiler.
- **CANNON** is owner-selected canon, not the default Git branch and **not a build/test executor**. Tests/merge do not themselves authorize owner selection, signatures or runtime effects.

`handoff.py` produces `motif.reason.eight.review-handoff.v1`: content-addressed candidate source files, program and certification references, a source-owner-checked market receipt, **GRAFT review requested, no branch created**, and **CANNON NOT_CANON, no signer/selection**. Both external projects remain unchanged. This packet is a review candidate only, not permission to import, publish, sign or execute.

## Reproduce and inspect

Standard-library Python 3.11+:

```sh
python -m unittest discover -s experiments/reason-cartridge-008 -p 'test_*.py' -v
python experiments/reason-cartridge-008/trial.py reason-008-evidence
```

The local run uses only source-owned toy fixtures, **not** the independent native Dogram executable.

The dedicated workflow `.github/workflows/reason-cartridge-008.yml` runs all inherited REASON-001…007 regressions; the new hostile-authorization, source-gap, forgery, out-of-domain, independent-review and market tests; emits original Dogram specimens; runs the actual pinned Dogram CLI; removes its checkout; independently verifies 32 original receipts; and uploads:

```text
reason-008-evidence/
    method-cartridge.json
    market-receipt.json
    graft-cannon-review-proposal.json
    benchmark.json
reason-008-native/
    manifest.json
    reason-008-native-00..31.json
    reason-008-native-00..31.receipt.json
    crosscheck.json
```

The new method carries no runtime capability beyond five-edge-graph read-only queries. Legacy theorem counterexamples refer **only** to the explicit 45-program grammar. File checksums detect altered bytes but do not authenticate third-party users or make synthetic teaching labels true.

## Falsifiers and next frontier

- At least one old grammar candidate fits all five lessons: **no missing primitive**; return HOLD.
- New grammar has zero or multiple surviving programs: no unique macro; HOLD.
- Any of 27 withheld owner cases fails, original 32 native Dogram cases disagree, source revision moves, a signed/rehashed method is altered or receiver review is absent: HOLD.
- A claimed new ability cannot lower total modeled cost on the specified future workload: select the source-owned classical query instead.
- A future genuinely **nonisomorphic graph topology** defeats this five-feature method: **a new discovery task**, not a license to stretch this method outside its domain.
- Strong next test: let the program synthesizer **propose an extension family**, rather than choosing the preapproved AND3+AND2 family. Score its successes, excessive search, unjustified extensions and calibrated abstentions on independently owned nonisomorphic problem families. Proposed GRAFT/CANNON admission remains a separate owner-reviewed process.
