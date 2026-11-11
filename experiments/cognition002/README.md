# COGNITION-002 — Subconscious Crossroads: MOTIF × UNDERSTORY × Free Graph

**DRAFT research HOLD**, stacked on COGNITION-001 (#296). This is an intentionally small native-source integration, not autonomous consciousness, automatic memory harvesting, continuous background work, or a deployed mobile app.

## What is connected and what isn't

The user's analogy is precise: **MOTIF contemplates**, **UNDERSTORY preserves attributable traces that haven't entered declared belief**, and **Free Graph allows weak, inspectable relations to be rediscovered without owning truth**.

- **MOTIF**: a real COGNITION-001 `FourSpeedMind.tick` must pass simulated user permission/visibility/idle and **native pinned GHoT energy scheduling**. Only then does the native MOTIF-003 affordance mechanism generate a prospective research question. The journal is fictional.
- **UNDERSTORY (private MEMENTO)**: `bridge.py` prepares a four-record synthetic owner-local envelope (two explicitly encountered past contacts, one unresolved association, one later activation). It invokes the real owner repository `scripts/validate-understory-contemplation.mjs` by explicit `--memento-root`; that companion invokes actual `validateUnderstoryRecords` from MEMENTO's `scripts/lib/understory.mjs`. The owner validator does not write, echo source contents, or open a MEMENTO admission gate. Without the private companion it explicitly **HOLDs**; never impersonates successful native validation.
- **Free Graph**: `bridge.py` imports the **actual source** `scripts/fg_core.py` from pinned public repository `ec0ad8743c5faac3f3675760bbafcbcb1df846c1`, and constructs a fully canonical `free-graph.packet/v0` with 3 synthetic sources, 4 nodes and 3 **unresolved, nonconstituting** links. Native graph validation is mandatory; no `descends-from` or `constitutes` inferred. Private Understory records NEVER enter this public-safe graph.
- **Private owner companion**: MEMENTO branch `experiment/understory-contemplation-input-20261111` adds the owner-local native validation surface and its tests. MEMENTO is private; these files are **not copied into public MOTIF**. MEMENTO's own CI may exercise end-to-end integration on synthetic data with an explicit source checkout. A public MOTIF CI cannot checkout MEMENTO using its ordinary repo token.

## Source/authority invariants

```text
EVENT E0           EVENT E1
    |                 |
    +--- UNDERSTORY explicit CONTACT receipts, separate observer-local sources
                      |
                      v
             tentative ASSOCIATION (status unresolved)
                      |
               later observed trigger
                      |
                      v
              new ACTIVATION receipt (E1)
                      |
                      v
          MOTIF bounded CONtemplation question
                      |
                      v
          Free Graph PROPOSED traversal
                      |
                 EVIDENCE TEST?
                      |
                    HOLD
      (MEMENTO owning ADMIT/REFUSE/FOG gate remains distinct)
```

No absent attention is called ignored. No historical trace is overwritten on activation. Every Free Graph source says **invented fixture**, not authenticated real-world origin. The task-world cut remains unresolved. Private owner validation is a local structural check, not approval to alter canon or deploy.

## Run

Public MOTIF CI checks out GHoT and Free Graph at immutable commits and tests them. Run from the checked-out MOTIF research branch after providing the pinned public source checkouts:

```bash
python -m unittest discover -s experiments/cognition002 -p 'test_*.py' -v
python experiments/cognition002/bridge.py > cognition002-public-graph-demo.json
```

For the separate private owner test, from a workspace with a personally authorized MEMENTO checkout:

```bash
python experiments/cognition002/bridge.py --memento-root /path/to/MEMENTO
```

This input contains only invented synthetic source records and executes only a read-only owner validator. **Do not** pass private source content to public graph generation or commit genuine Understory history without owner-specific export approval.

## Comparison with a conventional single critic

The included matched-budget **question-portfolio mechanism diagnostic** gives a conventional skeptical critic and the five-lens contemplation council the same five source pairs and five proposal slots. The council produces multiple *kinds* of questions; the critic produces independent-source questions. **No prospective experiment has verified whether either portfolio leads to more useful outcomes**; both have zero **observed** validated downstream wins, not measured failure scores. The next controlled experiment needs independent outcome adjudication with matched compute/energy/human review budgets and source release policy. Count results, not inspiring associations.

## Current scope
No live app, no OS background service, no model-to-model conversations, no consentless diary ingestion, no repeated model training, no cross-project writes, no automatic acceptance of analogies, no claim of subconscious mental states. User opt-in and local app-visible work are still *simulated* in current tests.
