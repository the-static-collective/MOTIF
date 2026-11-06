# MOTIF GEOM-013 — The Experiment That Redesigns Itself

**Status:** Synthetic, executable measurement-procedure debugging. Python 3.11+ stdlib. Separate **stacked** experimental PR on GEOM-012; not merged to main, no production service, live sensor, new physical instrument, or real-world action.

## The question

Can MOTIF notice that an existing measurement **procedure**, not merely an interpretation or conditional reasoning rule, becomes unreliable under a new data-generating regime, then propose and test a changed measurement procedure using development feedback only?

GEOM-012 generated `ODD(COUNT(a,[0,8))) XOR ODD(COUNT(b,[0,8)))` from recorded synthetic events. GEOM-013 **runs the actual GEOM-012 synthesizer** to obtain and validate that parent instrument, then wraps that exact program in a test-only typed program-transformation grammar.

An upstream event delivery regime now duplicates records, retaining declared event identifiers on duplicate rows. Unmodified `COUNT` counts both originals and delivered duplicates, changing count parity. The experiment's **new allowed instrumentation step** is `DISTINCT_BY_DECLARED_EVENT_ID` inserted *before* `COUNT`, per branch. This step is supplied by the designer: MOTIF selects where to insert it from feedback; it did **not** invent the primitive or independently discover that two source records denote one physical event.

## Three roles + iterative revision

1. **Explorer:** replay source-preserving hypothetical instrument variants on attributed development traces; never change observed data or external systems.
2. **Critic:** report false positives/negatives, specific counterexamples, declared duplicate-ID candidates, undecidable/missing recordings, and identical record sets with conflicting developer labels (fail closed).
3. **Inventor:** enumerate monotonic insertions of `DISTINCT_BY_DECLARED_EVENT_ID` into the existing instrument. Choose the simplest, cheapest complete development fit. Source/scope/capability-bound search cursor supports finite work slices; an incomplete search never claims completion or optimality.
4. **Second Critic:** challenge the current revised instrument with *new* developer-supplied conditions. Re-run the search from its new active procedure; a second revision can be proposed.

All transformations are read-only, `PENCIL` and `authority: NONE`. Restrict input to exactly one observer/time/decoder scope. Forbid inaccessible or unpermitted event identifiers. Explicitly HOLD if relevant identifiers are missing, if their channels/timestamps conflict, or if an entire recording is missing. An observed empty recording yields zero events and is distinguished from missing data. References to independent source roots are **declared**, not authenticated.

## Reproducible synthetic experiment

- **GEOM-012 parent:** original 7-step XOR-of-two-parities instrument, **not** hard-coded as an allegedly novel program.
- **Round 1, 64 development cases:** duplications of `a` only. Existing procedure yields 32 correct, 32 wrong. Critic identifies likely duplicate-record confound. Inventor inserts a `DISTINCT_BY_DECLARED_EVENT_ID` step before channel `a`'s count: 64/64 development fit.
- **Round 2, cumulative 128 cases:** new records duplicate `b` as well. First revision now yields 96 correct, 32 wrong on cumulative development. Inventor additionally inserts the ID-distinct step for `b`: 128/128 development fit.
- **After both selections, frozen holdout:** instantiate 300 new distinct-ID cases with different duplication frequencies and noise; 260 have complete usable traces, 20 have an absent entire trace, and 20 have an unidentifiable relevant record. **Parent: 141 correct, 139 wrong, 20 abstentions. First revision: 130 correct, 130 wrong, 40 abstentions. Final: 260 correct, 0 wrong, 40 abstentions.** The first revision generalizes worse than the original under the new shift—this is reported, not concealed.
- **Matched classical control:** a separately coded direct counting / unique-ID conditional enumeration ties final **260/0/40**. No claim of improvement over classical program synthesis or a live causal finding.
- A `perfect-answer` channel exists in synthetic raw records but is marked not permitted; an unavailable channel is also present. Neither may enter the inherited instrument or permitted revisions. Unit controls include manipulation of these channels.

**Important:** Both the newly available identifier metadata and the `DISTINCT_BY_DECLARED_EVENT_ID` operator are supplied by our test scenario. This is bounded program repair, not unconstrained invention of new experimental modalities. `PENCIL != PEN != authority`.

## Existing architecture crossings

- **GEOM-012:** real imported `Instrument`, `Atom`, `Capability` and validation; the parent is selected by its actual synthesis code during demo.
- **GEOM-009 / GEOM-008:** optional single-writer SQLite `LivingGraph` archive. Recomputes development score and procedure before appending a PENCIL revision node and n-ary feedback lineage. Stores feedback digests and identifiers, **not raw observations**, particularly not forbidden/hidden channels. Never rebinds expansion grammar.
- **ALEX / Free Graph / 3rdi / LOADOUT / THOUGHT-006:** not integrated. Their external authentication, observer-cut, capability-binding, and admission authorities remain separate. A synthetic Boolean `permitted` is not real LOADOUT authorization.
- **Free-form graph growth:** nothing in GEOM-013 re-imposes GEOM-007's 13-node bounds or GEOM-008's overall graph-size limits. This *measurement-repair* search itself is limited to two existing GEOM-012 atoms and a supplied distinct operation.

## Verification and ways to falsify

```bash
cd experiments/geometry-013
python3 -m unittest -v test_redesign.py
python3 demo.py > /tmp/geom013-demo.json
python3 benchmark.py > /tmp/geom013-benchmark.json
python3 interface.py example-input.json > /tmp/geom013-interface.json
python3 -m json.tool /tmp/geom013-benchmark.json > /dev/null
```

Tests include independent randomized duplicate-counting oracles, tampered receipts, source-scope and permission fences, missing-event ambiguity, duplicate-ID collision, exact-label contradictions, developer/heldout identity separation, and GEOM-009 SQLite archive integrity. The workflow runs only bounded reproducible checks.

**Next falsifiers:** unreliable/reused event IDs, records whose duplicate semantics cannot be reliably inferred, changing event windows, correlated source declarations, non-XOR targets, different event definitions, and independent genuine datasets. Test against conventional deduplication, SQL `COUNT(DISTINCT ...)`, and constrained program-synthesis baselines. If a traditional method ties or beats MOTIF, report it and retain the simpler method.
