# MOTIF THOUGHT-006 — The Pencil and the Pen

**Status:** Executable, isolated, local-first **synthetic research**. This is the first code slice in [THOUGHT-FIELDS-006–010-FULL-STACK-RFC](../../docs/THOUGHT-FIELDS-006-010-FULL-STACK-RFC.md). It does not implement the non-fungible multi-manifestation identity model (THOUGHT-007), multi-view cognition (008), selection/learning (009), or any live JAR;VIS connector (010).

## The experiment

Can we preserve a provisional **PENCIL** idea, record separately scoped **PEN** commitments, challenge/revise them without erasing previous reasoning, and replay a deterministic record? Can we stop visual closeness, repeated source echoes and unexamined contradictions from becoming pen conclusions by accident?

This is an event-sourced **working-belief ledger**, not a truth machine.

- **PENCIL:** the model's/current operator's speculative assertion: "This is what I'm thinking." A reported GEOM-005 edge is imported here as a sketch regardless of the upstream `observed` flag.
- **PEN:** a scoped, revisable *locally reviewed working model*: "This is what I currently think." PEN does not mean a proof, authenticated source, or real-world truth. A pen assertion can be challenged, withdrawn, or reopened as pencil.
- **External authority:** always `NONE`, including after PEN. No permission to execute tools, contact anyone or mutate an outside system follows from a pen commitment.

### State transitions

```text
  SKETCH (PENCIL) -> SUPPORT (+ source)
      |           -> CHALLENGE (+ counterexample) -> PENCIL_CHALLENGED
      |                     [promotion blocked; create a narrower sketch]
      v
  COMMIT (only when strict gate passes) -> PEN_SCOPED
      |                                       |
      v                                       v
  WITHDRAW -> WITHDRAWN (RETIRED)       CHALLENGE -> PEN_CHALLENGED
      |                                       |
      +----------------+----------------------+
                       |
         REOPEN (new revision, PENCIL)
                       |
               re-evaluate evidence
```

The log keeps all prior source IDs, objections, outcomes and receipts. A reopened revision starts with *no active support/objections*; it must review and explicitly restate its evidence. No historical event is removed.

### Strict local pen gate

A `COMMIT` must identify a bounded scope, a concrete assertion with known concept endpoints and allowed typed predicate, an explicit reviewer actor label and justification, and **two claimed distinct eligible provenance roots**, with **no unresolved challenges** on that revision. Reposted sources sharing a root count only once. Sources tagged inference/analogy alone cannot support PEN. A failed gate throws `LedgerError` and adds **no event**.

**Crucial limitation:** a `source.root` string and `actor` string are declarations, not independently authenticated witnesses. The gate only enforces local structural discipline. It cannot certify that two witnesses are actually independent or that the conclusion is true. Even a successful `COMMIT` should remain a working assumption subject to real-world evidence review.

### Deterministic audit and replay

`events.jsonl` contains canonical JSON records with `schema`, monotonically ordered `sequence`, `event_id`, `type`, exact `payload`, prior SHA-256 digest and a SHA-256 of the event body. Replay verifies the chain, exact key sets, canonical bytes and the validity of all state transitions; a torn/incomplete final line fails closed. The snapshot is reconstructed from the log and never treated as the source of truth.

SHA-256 here catches accidental corruption or inconsistent history, **not** a dishonest party who rewrites the entire log or genuine authorship. The prototype uses an optimistic stale-writer check and fsync but is **not a transactional multi-process or cross-host store**; simultaneous writers must be excluded by an outer lock or a future transactional storage layer. The v1 log is capped at 4 MB and intentionally uses a small permitted event vocabulary.

### GEOM-005 crossing

`adapter.py` accepts an existing GEOM-005 JSON source graph (`nodes`, `edges`) and registers typed local node identities, source declarations and pencil assertions. An upstream `observed=True` means only "the graph author supplied this edge"; it is retained as `observed_input` and **not elevated to a validated fact or PEN**. The source labels are left unauthenticated. This adapter is a write to the local thought ledger only; it never changes the original graph or remote GitHub.

### Reproduce

```bash
cd experiments/thought-006
python -m unittest -v test_ledger.py
python demo.py > experiment-results.json
python interface.py /tmp/my-thought-events.jsonl
# For one explicitly provided local command:
python interface.py /tmp/my-thought-events.jsonl command.json
```

The synthetic demo (not a real food-shelf claim) shows:
1. A broad claim sketched as PENCIL; counterexample blocks PEN.
2. A narrower scoped sketch with two copied sources sharing one declared root; strict pen gate blocks duplicates.
3. A second declared evidence root and explicit fixture-review actor yield `PEN_SCOPED` **within the toy test**.
4. A new counterexample changes status to `PEN_CHALLENGED`; reviewer withdraws the conclusion, and reopens it as fresh pencil.
5. A new ledger replays the exact JSONL history and reproduces the same semantic snapshot.

Unit tests cover the complete loop, echo-root deduplication, unsupported nodes, invalid predicates, unbounded scopes, challenges blocking admission, no promotion from layout, pen supersession, source provenance, tamper detection, partial final lines, stale external edits, GEOM-005 import, and denial of import-to-pen.

### What is still missing

- Real independent fact-checking, secure reviewer identities, countersigned records, and evidence permissions.
- Atomic/concurrent writer control and shared stores; v1 is single-writer local-only.
- True multi-meaning/non-fungible `Concept`/`Expression`/`Manifestation`/`Placement` separation, planned for THOUGHT-007.
- Multi-projection layout and view-selection, planned for THOUGHT-008/009.
- Independent blind tests proving better decisions than a classical ledger or no-map baseline. **No performance or intelligence improvement is claimed yet.**

**Next experiment: THOUGHT-007 — concept identity versus multiple non-fungible manifestations.**
