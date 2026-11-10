# FIELD-002 — The Invented Probe (bounded grammar repair)

**Research question.** After one source-owned observation, can a small investigator discover that its current question language is insufficient, compose a more expressive question language from explicit primitives, ask fresh questions *before knowing their answers*, and retain evidence-backed results across more than one domain?

**Status: RESEARCH HOLD — finite executable test, no live system.** This is not autonomous method invention, new science, practical electrical/hydraulic guidance, nor validation on external physical sources. The four evaluator worlds were **engineer-authored**. This code does not access the Internet or a real circuit, pipe system, material inventory, resource exchange or agent.

## Architecture

1. Begin with exactly **one simulator observation** (`state=all_off/absent`, output `false`) and the primitives `toggle(field_i)`, `observe(state)`, `AND`, `OR`, `NOT`, and source-independent data records. The learner receives axes and observations but does not inspect the evaluator's hidden `outcome()` code.
2. Starting model grammar is only constants and **one-variable conditions** (`UNARY`). Each proposed model and each switch-setting question is a hypothesis, not a fact.
3. Build an active question by minimizing hypothesis disagreements across not-yet-observed settings; deterministic move-cost tie-breaking and a fallback that probes even unanimous predictions. Before receiving the outcome, freeze the selected question, its multi-step toggle plan, the model count, and prediction counts.
4. If the observed answers make **every UNARY hypothesis inconsistent**, build a new grammar by typed composition of conjunctions and disjunctions with **at most two conjunctive clauses** (`DNF2`). The new function candidates are normalized by complete finite truth signatures (16 possible on two variables, 158 representable on three). This is an authored bounded synthesis method, not free-form language invention.
5. Re-run candidate consistency after fresh independent evaluator observations. Promote a state to a `SIMULATOR_OBSERVATION` fact only after `Witness.observe`; proof packets retain exact source revision, state, output, question genealogy and SHA-256 checksum. A checksum is not source authentication, so `check_packet()` also recomputes original observations and choice order.
6. `FINITE_DOMAIN_VERIFIED` requires that all settings were queried and a consistent program survives. If the richer grammar also becomes inconsistent, return `HOLD_GRAMMAR_INSUFFICIENT` rather than inventing an answer. Absent independent physical evidence, verified here means **exhaustively consistent with the finite evaluator**, not verified in reality.

## Distinct evaluator worlds

| World | Source mechanism | Initial hypothesis language | Generated extension |
| --- | --- | --- | --- |
| Two-way lamp | Graph path connectivity with two changeover switch contacts | A single switch or constant | `(A and not B) OR (not A and B)` |
| Parallel pipe | Graph path connectivity through one valve in series with two parallel valves | Any single valve or constant | `A and (B or C)` |
| Shelter recipe | Separately implemented membership check against two resource sets | Any single resource or constant | `frame and (rope or screws)` |
| Three-lever parity (negative control) | Even/odd lever count | Any single lever or constant | Not expressible in this authored two-clause grammar → HOLD |

The pipe and recipe share an intentionally authored Boolean structure, so their apparent transfer is **not** a blind independent cross-domain discovery. The two connectivity cases are also related graph problems. No real materials or safe build designs were tested.

## Executed results

| Case | Queries | Initial grammar rejected? | Distinct queried multi-toggle plans | Verdict |
| --- | ---: | --- | ---: | --- |
| Two-way lamp | 4/4 | yes, after 3 facts | 0 | finite exact |
| Parallel pipe | 8/8 | yes, after 4 facts | 3 | finite exact |
| Shelter recipe | 8/8 | yes, after 4 facts | 3 | finite exact |
| Three-lever parity | 7/8 | yes, after 4 facts | 3 | **HOLD** (no consistent composed program) |
| **Total** | **27** | 4 grammar expansions | **9** | **3 exact, 1 HOLD** |

For the 3 exact worlds, the system reconstructs the entire small truth table and outputs a witnessed two-clause program not representable in its original unary grammar. It also constructs and executes 9 multi-toggle internal plans across the four worlds.

**Classical controls.** An always-on, already-expanded DNF2 search with the same selection policy uses exactly the **same number of observations** in all four cases. An exhaustive classical truth-table collector also uses 4/8 observations for complete two-/three-variable coverage: **zero query savings** on the three exact cases. A unary-only investigator returns HOLD in all four. The parity case stops one observation early *only because it fails to find a consistent hypothesis*; this is **not a discovery-efficiency gain**. The experiment demonstrates a bounded model-language expansion and transparent abstention, not a performance advantage over strong classical controls.

## Reproduce

```bash
cd experiments/field002
python -m unittest -v test_field002.py
python field002.py > /tmp/field002.json
python - <<'PY'
import json
assert json.load(open('/tmp/field002.json')) == json.load(open('experiment-results.json'))
print('FIELD-002: exact reproduction')
PY
```

**No dependencies beyond Python 3.10+ standard library.** Tests cover original observation integrity, forged-and-rehashed evidence, source drift, wrong revisions, out-of-vocabulary source, live query order, program language insufficiency, classical-baseline parity, multi-toggle plans, bounded HOLD, and exact artifact reproduction.

## Remaining falsifiers

1. Freeze this entire policy and confront **independently authored** input/output logs that were not selected to match the DNF2 grammar. Strong matched Bayesian/active-learning and automated grammar-synthesis baselines need equal budgets.
2. Allow **unseen variables, observation noise, time delays and state-changing dynamics** rather than deterministic binary tables. Test how often unsatisfied models trigger appropriate re-questioning versus false conclusions.
3. Provide an independent reviewer-controlled external measurement oracle (not an authored toy function) with owner authentication, resource limits, and consent where required.
4. Test whether *methods* invented from one world measurably reduce inquiry or error on disjoint heldout sources. The current exact-coverage results do not show compounding improvement.

**Continuity.** FIELD-001's separate, independently published Atlas benchmark remains in its draft branch. This FIELD-002 branch stacks upon FIELD-001 and explores the next question—bounded language growth in alternative toy domains—but does not silently replace or merge FIELD-001.