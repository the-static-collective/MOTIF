# MOTIF GEOM-012 — The Question That Builds Its Own Instrument

**Status: executable synthetic experiment on an isolated review branch; PENCIL only.**

GEOM-011 could choose declared, precomputed binary sensor readings and learn a small Boolean combination. That does **not** invent a measurement procedure. GEOM-012 instead receives only **time-tagged raw event records** plus a narrow **declared local capability/permission manifest**, then synthesizes a multi-step recipe that turns those records into a new distinguishing observation. It does **not** construct a physical device, access a service, discover a new physical measurement, or observe the world without supplied data. This is classical finite program synthesis.

## The challenge

All development cases have identical visible appearances and the same symbolic `bud -> branch` question, yet declared opposite labels. A deterministic classifier confined to those visible features cannot fit the labels. The raw recorded traces contain events tagged `a`, `b`, `noise`, and two deliberately misleading channels. The system is **not** told precomputed `signal-a`/`signal-b` bits or an XOR truth table. The generator's concealed law is parity(count(all `a` events during ticks `[0,8)`)) XOR parity(count(all `b` events during the same period)).

The system searches a **predeclared finite procedural grammar** of:

1. `FILTER_RECORDED_EVENTS(channel, [start,end))` from raw event logs;
2. `COUNT` qualifying events;
3. `ODD` (parity) or `NONZERO` (presence);
4. optional `NOT`, or two-branch `XOR`, `AND`, `OR` composition.

It selects the first exact development fit under explicit ordering: number of input atoms, local synthetic cost units, lexical recipe representation. **This is an optimum within the declared candidate enumeration, not over all possible scientific instruments.** No hard cap on the separate GEOM-008 graph's nodes/edges is introduced. This particular program search is intentionally finite and at most two atoms.

## What executes versus what is proposed

- `Instrument.recipe()` emits the complete proposed measurement plan, not a pretend observation. The plan has explicit intermediate filter, count, transform and composition stages.
- `Instrument.measure()` **replays previously supplied synthetic local event logs**; this executes the derived measurement algorithm on recorded data but does not acquire new events or use live sensors.
- `None` for an absent raw log means `HOLD_NO_RECORDED_TRACE`; an observed empty event log produces a legitimate zero count. Unknown is never silently converted to false.
- A capability with `permitted=false` or `available=false` is excluded even when its raw event channel perfectly predicts the target at lower declared cost. Saved procedures must revalidate against the *current* manifest; a later permission restriction rejects execution.
- Capability flags and source roots are **declared local test labels**, **not actual LOADOUT grants or authenticated ALEX witness roots**. No live external read or action is performed.
- A procedural instrument and its development-case digest are bound to exact observer/time/decoder scope and the declared capability/cost/window manifest. A deterministic cursor resumes finite work but may not skip an earlier complete solution. Claims of a complete procedure and development score are recomputed before evaluation or archive.
- Heldout labels and events are **not input to program selection**. Heldout evaluation is an explicit subsequent local replay; test-case ID overlap and cross-scope reuse fail closed.
- `archive_pencil` can place the proposed procedure and source-labeled development traces into GEOM-008's existing SQLite hypergraph **only as PENCIL** after exact score replay. Raw event records from restricted channels are redacted in the archived trace payload. The historical graph's rewrite grammar is not changed.

## Evidence and results

Run with Python 3.11+ standard library only:

```bash
cd experiments/geometry-012
python -m unittest -v test_instrument_lab.py
python demo.py
python benchmark.py
python interface.py example-input.json
```

The deterministic developer-authored synthetic development set contains **96** contexts with 4 balanced parity combinations for each of 6 separately named synthetic source families and 4 repetitions. Both single-channel parity readings are individually uninformative about the label (48/96 each). The bounded work-search examines a concrete sequence of candidate programs; it finds a composite 7-step measurement recipe:

```text
FILTER channel=a in ticks [0,8) → COUNT → ODD
FILTER channel=b in ticks [0,8) → COUNT → ODD
XOR the two bits → proposed_measurement
```

Synthetic heldout has **260** distinct-ID cases, with **20 raw-trace records deliberately absent**. The synthesized program scores **240 correct, 0 incorrect, 20 explicit abstentions**. An independently coded direct parity-count truth-table baseline **ties** (240/0/20), while a development-selected single predicate performs substantially worse. All these observations are from the same developer-constructed parity generator. **No new science or outperformance of general classical program synthesis is claimed.**

The test suite includes independent randomized event/count/Boolean controls, denied-perfect-answer channel, failure on missing raw records, withheld heldout, budget/permission re-checks, forged score and cursor rejection, strict scope, graph archival redaction and data-provenance identity.

**Local build verification** is recorded in the accompanying JSON artifacts; CI status must be checked separately on the PR.

## What this is *not*

- Not a physically constructed measuring device, newly discovered physical sensor, autonomous field experiment, or unrestricted interface to instruments.
- Not a language model that invents arbitrary experimental protocols. The **operators, event types, candidate time windows and local access declarations are supplied**; it discovers a composition of them.
- Not evidence that a geometric layout contributes to correctness. No spatial layout is required; GEOM-008's open graph remains source-preserving and optional.
- Not proof that two declared source roots are independent. The fixtures and labels are developer-generated.
- Not an automatic self-update, executable external permission, PEN admission, or integration with 3rdi, LOADOUT, ALEX, Free Graph, THOUGHT-006 or JAR;VIS.

## Proposed next falsifier

Freeze independent datasets and compare this procedure search against appropriately matched program synthesis, decision trees, automata and direct feature engineering, including hidden source correlations, timestamp perturbations, missingness, nonstationary observation windows, disjunctive/recursive protocols and cost-normalized utility. Extend the procedure grammar and typechecker before claiming to invent genuinely new instrument classes. External measurement would require separate verifiable access, identity and effect permission contracts.

**Research rule:** An invented measurement *recipe* does not supply a measurement *result*. Only a recorded, permitted observation can do that.
