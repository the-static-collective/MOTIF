# MOTIF LEGIT-014 — THE SELF-IMPROVEMENT TRIAL

**Status: HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT. Draft research only.**

This experiment closes a missing loop: **a formally correct change is not
automatically a useful or admissible change.** LEGIT-013 found safe
Boolean optimizations, but its new solver ran slightly slower than its
previous generation. LEGIT-014 makes that performance failure actionable.

## Mechanism actually executed

The research runner reads and SHA-256-checks MOTIF's **actual LEGIT-013
generated Python source**. The existing LEGIT-012/013 profiler inspects
24,904 original bitset transitions across 32 separate synthetic graphs.

Using those observations, the generator proposes bounded source-code
mutations: choose the first or last DAG parent, retain a branchless
intersection, or use up to two Boolean shortcut guards. The program
fragment grammar is explicitly predefined; this is not unrestricted
algorithm invention.

Each proposed shortcut must survive an **external Z3 SMT proof**, at bit
widths 8, 152 and 256, and a complete finite cross-check against a
separately implemented scanner and optimized classical DP on all
**6,561** possible partial three-input truth-table states.

The actual two-round loop does the following:

1. Propose mutations from the observed execution profile.
2. Prove or reject them with external Z3.
3. Measure correct proposals on **36 training-only graph workloads**.
4. Reject inferior measured variants.
5. Generate another set of previously unseen mutations from the
   observed best candidate.
6. Freeze exactly one winner **before accessing unseen test graphs**.
7. Test the frozen winner on heldout data against the preceding two
   generated MOTIF solvers **and** a separately authored optimized
   conventional DP.
8. HOLD unless prespecified correctness, speedup, repeat-win and
   graph-family regression gates are all satisfied.

No generated source is automatically installed, merged or deployed.

## Three possible outcomes — and what actually happened

**Incorrect transformation:** A deliberately injected adversarial
hypothesis claimed that an empty parent should become the new evidence
mask. Z3 returned an actual SAT counterexample (zero parent, nonzero
column). The source was rejected **without execution or timing**. This
is a negative control, not an independently discovered candidate.

**Correct but slower:** Nine candidate programs survived third-party
Z3 verification and full finite checking. The first training round
selected a best performer; the second generated **three additional
proposals** based on that measured result. Every rejected alternative
remains visible in the ledger.

**Correct and worth retaining:** The frozen candidate was a simple,
first-parent, branchless bitset intersection. It was mathematically
valid but did **not** pass the strict heldout speed gate. Therefore the
system declined to promote it.

## Measured results from the pinned passing CI trial

- **10** total proposed transformations; **9** formally verified;
  **1** refuted with an actual external Z3 witness.
- **36** training graphs and **80** separate-seed synthetic heldout
  graphs, containing **117,243** reasoning states.
- **0** mismatched answers; complete **6,561-state** finite check.
- **11 timing samples per solver** on one GitHub Actions machine.

| Solver across the same 80 test graphs | Median elapsed |
| --- | ---: |
| Earlier generated LEGIT-012 | 141.90 ms |
| Previous generated LEGIT-013 | 145.55 ms |
| **Frozen LEGIT-014 trial candidate** | **142.69 ms** |
| Strong independently written classical optimized DP | 161.33 ms |

The selected candidate was approximately **1.97% faster than LEGIT-013**,
**0.55% slower than LEGIT-012**, and **11.56% faster than this particular
classical Python DP** in this one-runner exploratory measurement.

The trial required at least **8% improvement over each of all three
comparators**, at least **10 wins from 11 repeats per comparator**, and
no density-family regression greater than 10% against the strong
classical implementation. It failed the two earlier-generation
speed thresholds. **Final verdict: HOLD.**

The source profiler cost about **1,851 ms**, and the candidate proof
and compilation work totaled about **2,874 ms**. Setup and proof costs
are recorded separately and were not included in the per-batch runtime
table. They materially matter for real end-to-end payback.

## Saved files

- **generated/candidate_rewrite.py** — actual frozen generated Python
  from a passing Actions run, still inert.
- **generated/candidate_manifest.json** — source plan, mathematical
  proof scope, human-review and no-promotion controls.
- **generated/performance_trial_report.json** — complete first- and
  second-round attempted candidates, actual Z3 counterexample, timed
  training and heldout results, raw timing samples and exact HOLD gates.
- **transform.py** — profile-driven source mutations, exact
  template-only execution, mandatory Z3 and finite regression.
- **benchmark.py** — separate train/test generation, empirical
  feedback, real wall-clock timing, strong conventional controls
  and strict retention gate.
- **test_trial.py** — 20 adversarial correctness, SAT-falsification,
  source integrity, holdout, baseline and archived-artifact checks.
- **.github/workflows/legit014.yml** — pinned external Z3 installation,
  complete trial, tests and archived receipts.

Run from repository root (Python 3.11, z3-solver 4.16.0.0):

    python -m unittest discover -s experiments/legit014 -p 'test_*.py' -v
    python experiments/legit014/benchmark.py --emit

The runner emits new report artifacts to /tmp without modifying the
committed frozen research results. Timing-based selection can vary with
runner noise; tests verify the saved program's actual mathematics
rather than requiring nondeterministic timings to match byte-for-byte.

## Boundaries

The transformation language, formal specifications, model distributions
and challenge selection were authored by the assistant; they are not
independently blinded. Z3 proves the encoded bounded bitvector
identities, not arbitrary Python behavior or all real-world graph
reasoning. Exact source-template matching is not a general security
sandbox. One Actions runner does not provide a rigorous performance
replication or a general algorithmic superiority result.

No autonomous merge, service deployment, outside-auditor
authentication, human decision or real-world action was performed.

**Meaningful result:** the self-improvement process generated
candidate modifications, obtained genuine mathematical counterexamples,
measured competing implementations, iterated from feedback, and
**correctly refused to admit an improvement that had not earned it**.

Next rigorous gate: independently authored unseen tasks, stronger
algorithm transformation grammars, proof certificates checked by
external tools, controlled multi-runner CPU/memory benchmarks, and
a resource-matched optimized classical algorithm portfolio.
