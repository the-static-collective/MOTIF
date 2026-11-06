# MOTIF RING-005 — Close the Loop: Evidence-Adaptive Cartridge Routing

**Status:** passed source-native experimental CI in a draft research branch. Not production, not real-world decision software, and not autonomous code self-modification.

The previous RING-004 was a credible cross-source benchmark but always ran the three methods on all test cases. RING-005 asks a different, stricter question:

> Can MOTIF use earlier experimental outcomes to **preselect a smaller source-native method set for a new case**, actually avoid running unneeded native methods, measure correctness on separately hidden labels, and revise the policy when evidence contradicts an assumption?

## Actual closed loop

```text
 source-pinned old experiments and case data (64 authored training cases)
            |
            v
    train-only typed contextual analysis (policy.py)
            |
            v
    FROZEN policy with source commits, support and source-bounded costs
            |
            v
    NEW public source case (heldout seeds, 64 cases)
            |
            v
   classify from *public observable data only*
            |
            v
   create immutable SHA256 route manifest BEFORE native inference
            |
            v
   sandbox: invoke ONLY the selected original source methods
            |
            v
   controller opens withheld expected labels AFTER sandbox exits
            |
            v
   compare on identical cases with native-all and exact classical controls
            |
            v
    review: record no-change or DEMOTE unsupported shortcut to full triad
            |
            v
    next distinct heldout packet, using reviewed frozen successor
```

**This is evidence-conditioned experimental routing**, not learning new semantics about an unseen world or automatically merging new code. All context categories and candidate bundles were **hand-specified** before the empirical tests. The train-only policy learns whether each predefined shortcut is supported by prior scored receipts, with a minimum-sample condition and zero-error threshold.

## Five public-input contexts

The very narrow synthetic source model remains the same as RING-004: a route S → A → T after the direct S → T edge is ablated. One edge is an independent known gate; the other is measured through parity of declared unique event IDs in the original GEOM-013 channels. THOUGHT-014 interprets eligible questions and rejects external-effect requests; REASON-006 may produce source-bound graph proof receipts.

| Context | Selected experimental strategy if supported in prior training |
| --- | --- |
| Effectful phrase, missing trace, or invalid declared event ID | HOLD before any source-owned method call |
| Known gate absent and no separate proof requested | Classical source-structure cut proof; no additional native method |
| Gate open with no duplicate record | Original THOUGHT-014 + original GEOM-013 **raw** instrument + simple classical graph |
| Gate open with duplicate record | Original THOUGHT-014 + GEOM-013 **learned repaired** instrument + simple classical graph |
| Task has an explicit source-owned proof receipt requirement | Original THOUGHT-014 + GEOM-013 repaired instrument + source-native REASON-006 council |

The benchmark's proof-receipt requirement is a fixed **public, author-chosen task designation** (every seventh case) independent of the secret answer. It is not a demonstration that the agent inferred a real person's intent. Invalid case evidence still HOLDs even if a proof was requested.

**Safety and correctness gates:** Both the controller and the sandbox independently derive the allowed context from the case's visible data. The worker rejects a pre-selected route whose context disagrees with the evidence, a missing mandatory council, an effectful command forwarded to arbitrary execution, an out-of-order route, or a changed policy/manifest receipt. A context with fewer than two successful prior examples or any observed training error is routed to the fuller source-owned fallback. An observed heldout failure **demotes** its context; no code or runtime permissions are ever auto-promoted.

## Provenance and real execution

- `policy.py`: validates RING-004 per-case source-native scored receipts and their pinned source commits, derives a bounded public observable context, freezes permitted branches to existing method IDs only. It stores training support, objective and source receipt identities and no authority.
- `selective_worker.py`: runs **inside** the read-only, unprivileged, no-network Docker container. It calls actual original THOUGHT-014 `LanguageSpace.explore`, GEOM-013 `Revision.measure`, and REASON-006 `run_council` only for cases whose *precommitted routes* demand them. Source code is extracted from the three **exact Git commit pins**; no outside credentials, private labels or unconstrained new branch scripts are mounted.
- `adaptive.py`: runs old source-native training receipts on the author-designed seeds, freezes the router, tests it on **disjoint** generated seeds, separately runs the full-native RING-004 benchmark on exactly the same cases, opens labels only **after** selective execution, computes audited per-case comparisons and undergoes a constrained revision before the second heldout seed.
- `test_policy.py`: adversarial checks including unknown method admission, forged source pin, duplicate evidence, precommit disagreement, fake source proof status, hidden-label separation and failure-induced demotion. The fast test's manufactured source receipts are marked unit stubs. Full GitHub Actions independently executes original code.

## Verified synthetic outcomes

GitHub Actions source-native experiment:

- 64 source-native training cases from **two distinct seed packets** (seed 2026110615 and 2026110616).
- 64 further **previously unseen-to-the-trained-source implementation, author-designed** heldout cases from distinct seeds (2026110617 and 2026110618), 32 each.
- **Selective evidence-learned routing:** 32/32 and 32/32 correct, including intended HOLD decisions.
- **Always-full native** and **strong classical dedup/parity/BFS** controls: also 32/32 and 32/32.
- **Actually recorded native source method invocations on heldouts: 64** versus a **declared proxy budget of 192** calls for a hypothetical fixed-three-per-case plan. This is a **66.7% reduction in counted per-case native method invocations**, **not** a verified CPU-cost, wall-clock speed, energy, API-cost or total execution time improvement. Fixed source import, initialization, frozen GEOM development and Docker startup are real overheads outside the per-case call tally.
- First heldout had no error, so evidence-backed reinspection returned `NO_CHANGE_NO_MEASURED_ERROR` rather than fabricating an improvement. An adversarial unit test verifies that a counterexample *would* demote a shortcut, not magically construct new source code.
- No evidence of superiority to a fully informed conventional classical solution on this toy world. No independently authored naturalistic tasks. No model or browser API, outside-world authentication, delegated external actions, universal utility calibration, or third-party admission.

## Reproduce

```bash
# No Docker needed to inspect bounded policy and fake-receipt refusal tests:
python -m unittest discover -s experiments/cartridge-ring-005 -p 'test_*.py' -v

# Requires Docker + all exact pinned original source commits in the repo's
# local Git object store. The separate task labels are never mounted in Docker.
docker pull python:3.11-slim
python experiments/cartridge-ring-005/adaptive.py \
  --count 32 --out /tmp/motif-ring005-feedback.json
```

A reproduction using independently frozen Docker image digest is preferable outside this draft experiment. GitHub Actions fetches full history (`fetch-depth: 0`) to make exact original source commit copies available to the sandbox. All code remains a draft stacked successor to RING-004, RING-003, RING-002 and RING-001.

## What to test next

This is promising **in the extremely narrow supported setting** but the next frontier must attack the system's assumptions:

1. Independently authored human questions and alternative multi-route graph structures (not just S → A → T) with previously unencountered identifiers and contradictory witnesses.
2. Measured end-to-end wall-clock latency, memory and initialization overhead against **real native always-on** and **optimized classical** runtimes. A reduction in method call counts is not automatically a time or resource gain.
3. Explicit marginal **proof value** metrics: source-native REASON-006 can have value even if a classical solver already answers the yes/no question, e.g. reviewable objections and source attribution.
4. Online counterexample discovery and *review-gated* adjustment of conditional hyperedge evidence, with an untouched independent audit and auditable rollback.

The source-only branch garden remains open to future public GitHub references; **none become executable simply because they appear or have overlapping words.**
