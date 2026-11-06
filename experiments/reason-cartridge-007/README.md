# REASON-CARTRIDGE-007 — THE DISCOVERY MARKET

**Status:** implemented but unmerged experimental research branch, stacked on REASON-006 PR #88, itself stacked on REASON-005 #84 / REASON-004 #80 / REASON-003 #77 / REASON-002 #73 / REASON-001 #70. Standard-library Python only. Synthetic graphs, finite allowlisted methods, no live service or external actions.

## Research question

Can a market of reasoning contributions reward an independently verified *new reusable capability* rather than loud claims, repeated reasoning, unsupported votes, or a single cheap answer? And can it distinguish when a one-off answer is better than investing up front in a method useful for **a whole class of structurally similar problems**?

This market has **nontransferable accounting points**, not currency, tokens, money, betting or payment. It does not buy or launch external tools.

## The new invention (bounded, actually executable)

**Source owner:** `source.py`, a genuinely separate classical BFS evaluator for a synthetic graph containing four independently declared edge-presence features:
`S→A, A→T, S→B, B→T`. It produces 5 designated teaching observations, 11 different withheld certification observations, and renamed future graph tasks.

**Learner:** `compiler.py` does NOT import the source evaluator or access withheld labels. It searches a source-authorized, finite Boolean DSL of **15** circuits of the form `(x[a] AND x[b]) OR (x[c] AND x[d])`. From the source-owned five teaching receipts, it derives exactly one matching read-only instrument:

```text
EDGE_0 && EDGE_1   OR   EDGE_2 && EDGE_3
```

This is **composition of known Boolean primitives**; no novel fundamental primitive, arbitrary algorithm, free-form code generation, learned language model, or autonomous GRAFT/CANNON action. The prior strongly limits what can be discovered.

**Independent receiver:** `receiver.py` invokes the original source-owned BFS on the **11 previously unseen feature configurations** and independently verifies the compiled circuit. Only explicit digest-bound `ADMIT_READ_ONLY` enables **SUGGEST_ONLY** evaluation on renamed cases. A content hash checks source revisions but is **not a cryptographic identity credential**.

**The market:** `market.py` compares independently certified offers:

- `COMPILE_SENSOR`: pay for source training/certification, one-time composition, and cheap repeated read-only evaluations.
- `DIRECT_CLASSICAL_QUERY`: source-owned classical BFS answers each instance.
- `ABSTAIN`: return no answer, with a declared hypothetical omission cost.
- Repeated composition offers from a different author produce the **same semantic fingerprint**, receive **zero second novelty credit**, and cannot inflate evidence by claiming astronomical benefits.

The market rejects undefined bid methods, cycles in offer dependencies, mixed/unverified domains, uncertified sensors, unauthorized execution, altered receipts and false claims even if their digest is recomputed. The selected offer is verified against source-owned BFS on each portfolio case **after** bidding. Only then may an improvement in explicitly declared synthetic utility units be recorded. This does not provide real money, empirical compute cost, probability calibration or trusted-world facts.

## The key reversal

The cost model is an *illustrative assumption*, not a measurement:

| Synthetic cost | Declared unit price |
|---|---:|
| One training label | 0.5 |
| One independent certification label | 0.5 |
| One-time compilation | 2 |
| One compiled answer | 0.25 |
| One source-owned direct BFS query | 1.5 |
| Omission / no answer | 6 |

Certification is charged for all 11 heldout cases; we do **not** pretend verification was free.

**For one post-certification task:** new method total cost 10.25, one-off direct lookup 1.5. **The market chooses direct lookup.**

**For 16 renamed task instances:** the new method total cost `5×0.5 + 11×0.5 + 2 + 16×0.25 = 14`. Source-owned direct lookup costs `16×1.5 = 24`. **The market chooses composition**, with a modelled 10-unit advantage and 16/16 independent source-owned answers correct.

For 32 renamed tasks it also chooses compilation (subject to the same predeclared cost model and bounded 32-case universe).

**Strong-control caveat:** a fully informed classical BFS evaluator also solves every case correctly. A classical optimizer with identical costs can choose the exact same plan. In fact, if classical graph search is already locally available at low cost, our compiled sensor might be **less** economical. This is not evidence of a breakthrough in computational complexity or superiority over classical Bayesian decision theory. It is a concrete finite demonstration of amortized, evidence-gated **capability selection and reuse**, compared to one-off source lookups.

**Generalization limitation:** heldout certification includes the other 11 of the 16 four-bit configurations. The future portfolio uses renamed graph nodes and repeats the four-bit feature space; it does not test different graph topologies, missing inputs, causal transfer, unbounded tasks, or genuine external data. That is the next strict falsifier.

## Actually connected to REASON-006

`bridge006.py` imports the **original pinned REASON-006 Commonwealth Ledger** (Git blob `4f0e897b19e658f5f01a0a2e91a472ad023e1b8f`), and only after the independently verified compiled method yields a positive modeled advantage:

- Records one new validated **read-only method contribution**.
- Records zero for its exact repeat.
- Records **zero new worldly/source facts** because producing an algorithm does not make new observations true.
- Grants no external execution authority.

This is actual reuse of earlier repository code, not a marketing relabeling of a separate mock ledger.

## Tests and reproducibility

```sh
python -m unittest discover -s experiments/reason-cartridge-007 -p 'test_*.py' -v
python experiments/reason-cartridge-007/trial.py
```

Dedicated `.github/workflows/reason-cartridge-007.yml` also runs inherited REASON-001 through REASON-006 tests. It produces artifacts:

```text
reason-007-evidence/
  compiled-sensor.json
  market-receipt.json
  benchmark.json
```

These contain source pins, teaching receipts, compiled circuit, independent certificate/review digest, cost model, chosen offer, duplicate contribution accounting, a REASON-006 handoff, and validated task-by-task answers.

**Main falsifiers:** if the learner sees heldout truth during learning; if 5 observations do not identify one valid program; if any of the 11 withheld cases fail; if a bidder receives credit for a false, duplicate, rehashed or unauthorized contribution; if one-off lookup does not beat compilation when only one query exists; if compiler does not win under its explicitly specified 16-case cost schedule; or if source version changes are silently ignored, the experiment fails/HOLDs.

## Next frontier

Use a genuinely **different graph topology** and an independently source-owned external algorithm (or real authorized problem corpus) as an out-of-distribution witness. Compare against optimal classical active learning, exact graph search, memoization, partial evaluation and competing program-synthesis techniques. Once a method measurably transfers, a separate owner-reviewed proposal may be sent to GRAFT for compilation and CANNON for build tests. **Neither is invoked or permissioned here.**
