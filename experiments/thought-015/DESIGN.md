# MOTIF THOUGHT-015 — The experimental software developer

**Status:** Standard-library Python synthetic development experiment. Source-owned MOTIF feature branch stacked on THOUGHT-014. It does not update the live reasoner, install rules, grant PEN, merge code, execute external services, or run any live LLM.

## Research question

Can MOTIF *operate a trained model as its code-patch proposer*, synthesize executable candidate implementations using a constrained program grammar, run those candidates in an isolated temporary workspace, compare them with an independent oracle and hold out a reviewable patch only after fixed audits? This is a bounded mechanism for self-directed engineering, not unrestricted source self-modification or algorithm invention from first principles.

## The actual thought-development cycle

```text
CURRENT BROKEN PROGRAM (FIFO / first encounter / ignores risk)
       |
       v
  synthetic development failures -- descriptors / failing inputs
       |
       v
  TRAINED diagnostic model  --> exactly one known repair operator
       |
  strict typed DSL validation (no Python text from model)
       |
       v
  trusted local code generator --> actual Python candidate source
       |
  python -I -B in disposable temporary directory, timeout/output bounds
       |
  separate exact simple-path oracle + dev/safety comparisons
       |
  stage an improving OR neutral intermediate in scratch only, reject regressions
       | (4 rounds max normally)
  freeze candidate
       |
       +--> *separate random-seed held-out audit* 60 cases
       +--> *separate random-seed stress search* 55 cases
       +--> independent path/constraint validation
       |
       v
  code patch + hash receipts + counterexample or HOLD
       |
  HUMAN REVIEW REQUIRED; no automatic installation, commit or deployment
```

The four proposals are **WEIGHTED_PRIORITY**, **ENFORCE_BUDGET**, **RESOURCE_STATE**, **RELAX_IMPROVED**. A genuinely trained offline multinomial Naive Bayes model chooses operators from development failure descriptions; its role is deliberately limited. It does not generate arbitrary Python or select the correct answer, and cannot see audit/stress case labels until after the proposal process is over. The development descriptions explicitly hint at underlying failure mechanisms. A fairer future trial must blind these labels and author fixtures independently.

A separate optional local Ollama proposer uses the THOUGHT-014 explicit-loopback model gateway and may only return the same allowed enum repair and rationale; **no real generative LLM was invoked** in the default run. Missing/invalid model response must result in HOLD. This interface is not evidence of successful model-assisted coding on general tasks.

## Executable specimen

The experimental problem is shortest **cost** path through a small directed graph, subject to a total accumulated edge **risk budget**, with nonnegative integer weights. The source begins with an intentionally weak breadth-first/first-encounter strategy. A final correct finite-state Dijkstra-style solver requires weighting, pruning invalid risk totals, distinguishing `(vertex,risk)` states, and relaxing improved labels. The generator contains a single fixed, reviewed template, with four booleans substituted into actual Python code. The model can change those booleans but cannot author imports, arbitrary statements, files, network endpoints or effects.

A **distinct** `oracle.py` exhaustively enumerates simple paths of up to 8 vertices. It never imports or calls the generated solver. Each result is checked for real path validity, exact summed cost/risk, budget compliance, and oracle cost optimum (not just matching a claimed output). 8 development cases are designed to expose the four failure modes; four safety controls test reachability and constraint discipline. 60 audit graphs are generated with fixed seed 31337 and 55 stress graphs with seed 987654 (not used in proposal feedback).

Some repairs are **neutral intermediate changes** (no immediate score improvement). They are permitted *only inside the scratch workspace* if existing correct development cases and guard controls do not regress. They are NOT approved for deployment. The final patch is retained only if the full frozen audit, stress, and safety groups all pass, and the frozen audit does not regress versus baseline.

## Baseline and limitations

This finite synthetic instance intentionally permits the model to choose from *four pre-designed algorithmic building blocks*. The produced executable algorithm is a composition of already-known classical search ideas. It is **not novel algorithm discovery**, self-consciousness, full-stack autonomous software engineering, or a freeform model writing its own source. The seed-based holdout is separated from proposal feedback but was designed by the same authors and is not independent real-world validation. All success measurements below relate only to this synthetic test task. The generator supports positive integer weights only, small graphs, and one additive risk constraint.

Python `-I` plus temporary directories and timeouts are **not a security-grade operating-system sandbox**; executable code is safe only because the trusted source template is fixed and model-supplied source cannot be inserted. For arbitrary generated Python in a future THOUGHT-016, use a container/VM with OS-enforced network denial, nonroot sandbox, read-only mounts and CPU/memory limits. Do **not** launch unrestricted model code in this harness.

## Replication

```bash
cd experiments/thought-015
python -m unittest -v test_lab.py
python benchmark.py
cat experiment-results.json
cat candidate.diff
```

No third-party packages required. `benchmark.py` writes **only local experimental artifacts** (`reference_solver.py`, `candidate_solver.py`, `candidate.diff`, `experiment-results.json`) and does not alter a project reasoner. The workflow runs the new suite and the THOUGHT-014 regression test, then uploads the review packet. The test is not a claim of real-world utility.

## Guardrails and proof obligations

- No raw model-generated Python source accepted; unknown repair names, fields or effect requests HOLD.
- Data passed to model is development-only; holdout and stress are evaluated only after selection.
- No upgrade from pencil/proposal into PEN, project authority or installed runtime.
- Typed inputs 2..8 vertices and at most 35 edges; costs positive; risks bounded; loopback LLM optional and never automatically called.
- Candidate is executed locally in a throwaway directory and results checked by an independently implemented exhaustive oracle.
- Every candidate has a content hash and every development decision has an immutable receipt digest; these hashes do not authenticate an author.
- Search for adversarial counterexamples in distinct synthetic stress cases; any failure produces HOLD and retains the failed case, not automatic deployment.
- No repository mutation as a consequence of model output. This PR is an operator-directed experiment; `candidate.diff` is a review suggestion, not a self-committed production fix.

## Next meaningful frontier

Give a *real local model* a broader, still typed algorithm grammar, require it to propose its own diagnostic experiments before repair, and evaluate on **previously unseen tasks chosen by a separate evaluator**, comparing against static synthesis, random mutation, hand-tuned baseline and model-less methods at matched compute budget. The model should not have the ability to select its own tests and grades. If we eventually allow genuinely freeform code, that requires OS-enforced isolation, pinned dependencies and a human review crossing before applying any patch.
