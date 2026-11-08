# MOTIF RING-014 — The First Real Source-Test Next-Move Frontier

**Research question:** Can the ambiguity-first, value-of-further-action architecture choose and **actually execute** a useful, reversible **software research test**, observe real interpreter results, and decide whether another test is worth running? Is further investigation interesting and valuable enough to *do*, not merely hypothesize?

**Implementation status:** Genuine reviewed-Python test execution under a tightly bounded Docker tool bridge, stacked on RING-013; no source branch merged or automatic real-world tool permissions installed.

**The critical distinction from RING-013:** RING-013's rewards and observations were entirely authored simulator outputs. In **RING-014, the PASS/FAIL and resource costs come from actually running Python tests on separately mounted copies of the reviewed RING-013 source**. Deliberately seeded code defects are still authored, and modeled utility still uses author-chosen weights. Detecting artificially seeded bugs is **not** independent evidence of generalized autonomous coding, software repair, research innovation, or real-world benefit.

## The actual source-owned experiment

The source under test is the genuine predecessor's `experiments/cartridge-ring-013/value.py` and `scenario.py`. The original version is copied byte-for-byte into each isolated fixture. Select fixtures receive a very small, explicit, hash-checked edit targeting one source behavior (a failing syntax import, broken STOP decision, false posterior update, improper budget use, an altered safety ranking, reversed entropy, or a false output-authorization flag). The original repository files are **not modified**.

MOTIF has three real, independently testable research cartridges:

| Cartridge | Actual code run | Permissions |
| --- | --- | --- |
| **AST** (`INSPECT`) | Python `ast.parse` on the real source copy and its reviewed scenario method. | Read-only source inspection. |
| **SMOKE** (`SMASH_A`) | Imports the actual source copy, calls its Bellman planner and checks the existing non-effectful STOP and forbidden-action behaviors. | Reversible source-only test. |
| **DEEP** (`SMASH_B`) | Runs the **actual inherited RING-013 `test_value.py` unittest suite** on that copy, plus independent Bayesian posterior, information-gain, and budget-conservation assertions. | Reversible source-only test. |

These are **three genuinely executed source tests**, not fixtures that simply report author-selected PASS/FAIL. Mutating a source method causes the Python interpreter or source-owned tests to produce the resulting behavior.

The `EXTERNAL_COMMIT` candidate remains an intentionally extreme apparent-value trap in the inherited planner and is **never executable**.

### Real isolation boundary

Every test is started with:

- **`docker run --network none --read-only`** and both source plus fixture files mounted **read-only**.
- `--user 65534:65534`, `--cap-drop ALL`, `--security-opt no-new-privileges`, `--pids-limit 64`, `--memory 384m`, and `--cpus 1`.
- A small isolated tmpfs for legitimate temporary Python operations; **no writable host mounts, network, Docker socket, repository write tokens, cloud credentials, or arbitrary source path options**.
- A reviewed, limited action enum; exact source hashes; an image content SHA256 recorded at calibration; bounded wall clock and JSON evidence sizes; explicit refusal rather than silently executing a test on the unrestricted host when Docker is unavailable.
- `python -I -S` and import paths that are hard-coded to the mounted copies of the reviewed source methods, not user-supplied packages or scripts.

This is a **practical bounded test runner**, not a formally verified sandbox against arbitrary hostile code. It accepts only this repository's deliberately reviewed source copies.

### It really uses the previous machinery

The tested planner reuses **RING-013's actual finite Bellman `value.choose` and posterior update operators**. It maps `INSPECT` to AST, `SMASH_A` to SMOKE, and `SMASH_B` to DEEP; it updates its belief after each **real** PASS/FAIL. It can choose STOP and has a bounded three-action budget. It can run a later test if the next expected value remains positive, but never bypasses the reviewed test allowlist.

The source-language context is still obtained from **the real RING-012 ambiguity lattice**, including its correlated source methods and permanently unresolved other interpretations. The lattice only widens opportunity uncertainty; it cannot supply real test results or grant execution rights.

### How the estimated value is learned

**Before post-freeze source tests:** 10 experimental training code copies and 4 development code copies were each run against all three tests: **42 real isolated source-test invocations**. The experiment records actual frequency of failure on seeded bugs vs unmodified source, and actual Docker wall-clock costs. Source identity and Docker image SHA are frozen.

**12 value-model settings** vary the author-set reward for detecting a seeded defect, its test-time cost conversion and false-alarm penalty, and are evaluated against the training/development source observations. The selected action model is frozen **before loading the separately written 12-case source-challenge file**. No new challenge outcomes were fed into selection.

The inherited RING-013 value weights still define a preference for follow-up options and caution about risk. The possibility of unseen/unmodeled interpretations remains nonzero.

**Important:** The numerical reward for finding a seeded bug and the cost of elapsed seconds are **researcher-chosen heuristic proxies**, not an objectively validated price of curiosity or software value.

## Post-freeze evaluation: 12 actual software research cases

The post-freeze source set includes **7 deliberately faulty source copies** (some new mutation patterns) and **5 clean controls**, all author-generated. The planner does **not** see the hidden source mutation identity before choosing a test. A subsequent complete three-phase measurement matrix is executed after each plan finishes, solely to compare strong alternative decision policies. Those baseline results are not shown to the frontier while it is choosing its next test.

The following are **actual measured test results** on the first source-equivalent successful research run, with Docker startup included:

| Method | Seeded bugs detected (7) | Test actions selected | Measured test time | False clean alarms |
| --- | ---: | ---: | ---: | ---: |
| **RING-014 value-driven real-test selection** | **7/7** | **12** | **5.59 sec** | **0/5** |
| **DEEP-only** | **7/7** | **12** | **5.59 sec** | **0/5** |
| AST → SMOKE → DEEP until failure | **7/7** | 32 | 13.68 sec | 0/5 |
| SMOKE-only | 3/7 | 12 | 5.01 sec | 0/5 |
| AST-only | 1/7 | 12 | 4.81 sec | 0/5 |
| Always STOP | 0/7 | 0 | 0 sec | 0/5 |

**This is a valid but modest outcome.** The source-value planner selected **DEEP directly on every case**. It therefore **tied the simple DEEP-only control**, not outperformed it. It avoided the extra 20 real test invocations of the exhaustive control. The fact that it CAN run a further source test after observing a prior PASS is established by the executor design, but **this frozen test policy did not choose a multi-step trajectory on these heldout cases**.

Under the explicit author proxy utility, the frontier and DEEP-only both scored about **+87.56 utility units**, compared with +77.33 for exhaustive and −95 for always STOP. These are **not independent real-world gains**.

A source failure is reported with the real interpreter/test error and source checksum. A PASS is evidence about that specific test invocation, **not a proof** that the reviewed program has no defects or that a human's cryptic instruction was interpreted correctly.

### What a real decision looks like

```text
  unresolved language / multiple meanings (RING-012)
                  |
    test likelihood + measured cost model
                  |
       finite next-move scorer (RING-013)
                  |
          select AST, SMOKE, DEEP or STOP
                  |
         Docker: real source-owned Python tests
                  |
            PASS / FAIL + runtime + test traceback
                  |
       read actual result; update source belief
                  |
     either preserve failure receipt and stop,
     choose another valuable test, or stop safely
```

The planner only performs **already approved local source tests**. It cannot use semantic guesses, a potential future option, a book passage, or user enthusiasm to edit a repository, send a message, acquire network data, deploy software, or claim new authority.

## Inspectable provenance and falsification

- `fixtures.py`: reviewed source-copy generator, exact mutation anchors, source hashes; no original-source edits.
- `worker.py`: actual interpreter, source test import and unittest assertions inside a restricted container. Structured source outcome includes assertion count, timing, real exception and reviewed source fingerprint.
- `runner.py`: no-network, read-only Docker admission and receipt verification, quotas, timeouts, and **no unsandboxed fallback**.
- `adapter.py`: adapts actual RING-013 option valuation and RING-012 language ambiguity to a real source-test action budget; training-based test failure likelihood, runtime cost and posterior update.
- `learn.py`: executes 42 real source tests, estimates failure probability and test costs, searches 12 bounded action-value settings, and freezes source method/image provenance prior to challenge.
- `sealed.py`: 12 newly author-created code variants reserved for post-selection tests.
- `trial.py`: **live** value-policy-selected source test execution, then additional real tests for comparison. Holds all source receipts, mutation labels (evaluator-only) and baseline counterfactual source-matched results.
- `evidence_graph.py`: independently reconciles every real test receipt and all baseline statistics, preserves successful and missed regressions and resource cost in the same source-bound many-tail hypergraph.
- `test_contracts.py`: actually executes clean Python code and intentionally broken copies in Docker, verifies safety STOP, an incorrect source posterior, a deep-only budget defect, and forbidden unreviewed permission.
- GitHub Actions: provisions a reviewed Python image, runs all tests, executes actual code tests across source calibration and heldout source, audits the evidence graph, and uploads three inspectable artifacts.

### Reproduce

```sh
docker pull python:3.11-slim

python -m unittest discover -s experiments/cartridge-ring-014 -p 'test_*.py' -v

python experiments/cartridge-ring-014/learn.py --out /tmp/ring014-frozen.json
python experiments/cartridge-ring-014/trial.py \
  --frozen /tmp/ring014-frozen.json --out /tmp/ring014-tested.json
python experiments/cartridge-ring-014/evidence_graph.py \
  --frozen /tmp/ring014-frozen.json \
  --trial /tmp/ring014-tested.json \
  --out /tmp/ring014-source-evidence.json
```

## Research conclusion

**RING-014 genuinely crossed from simulated opportunities to actual, bounded, approved source-tool execution.** It used measured Python test failures and actual runtime. It did not demonstrate autonomous source repair, unknown algorithm discovery, independently novel mathematical insight, real-world user preference inference, nor permission to perform outside-world actions. The selected model's outcomes tied a strong single-test control on deliberately injected defects, so claims of superior autonomous decision quality would be unjustified.

### RING-015 frontier

Make the value of **a second real test** matter rather than always selecting DEEP: introduce separate diagnostics with different costs and error sensitivities; test cases with flaky/partial findings; update the method model only using prior source data, and measure whether conditional follow-up tests outperform a single strongest static test. Then connect any permitted trial to **disposable source-build verification**, with explicit rollback and no automatic merge or deployment.
