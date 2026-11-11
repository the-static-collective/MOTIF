# VOID-003 — The Memory Dividend: When two opportunities exist

**Research HOLD / draft on VOID-002 (#283).** User hypothesis: a first run that explores more distinct places can become better than a locally successful classical controller **if its observations are available for another run**. More territory is not itself success; test the *verified second-run resource outcomes*. The prior example 652 vs 580 coordinates is one diagnostic case, not a general result.

## What runs

A **first natural, unmodified Crafter 1.8.3 episode** uses either original MOTIF-003 exploration or VOID-002 classical two-ply exploration; both use identical source-pinned conventional observed-target BFS and seven-tile current sensor. Every actually seen tile (material, position, transient occupant) becomes an explicitly **historical, provisional** map packet.

After resetting the *same seeded game*, a **second episode** uses the same classical two-ply controller in every arm: (a) no memory, (b) historical MOTIF map memory, or (c) historical classical map memory. Memory can inform (i) which positions were searched before, and (ii) where a resource was formerly encountered, but any first move requires a current source-observed safe next tile. Historical remote targets are hypotheses, never present facts. A mismatched seed, initial world fingerprint, corrupt map or stale blocked first move is rejected.

The central comparison is MOTIF-scout-memory vs classical-scout-memory; secondary comparisons disable each scout's memory while keeping its scout cost. This isolates **what each first-run explorer learned**, not second-run model sophistication. Equal 70-action scout and 70-action follow-up budget per treatment, actual game resets, actual engine inventory checks, and full per-step receipts. **No LLM calls, training, source-engine edits or real-world actions.**

## Freeze and evaluation

Read [PREREGISTRATION.md](PREREGISTRATION.md) **before results**. Ten source seeds, four already examined (development only) and six predeclared NEW heldout seeds. The primary is second-run goal count minus costs of BOTH runs. Report negative/tie results and source-first failure traces. The unmodified independently authored game is not a blind independent agent evaluation; same seed does not guarantee identical later stochastic trajectories.

## Reproduce

On the stacked branch after checkout of pinned QC-017 as specified in the workflow:

```sh
python -m unittest discover -s experiments/void003 -p 'test_*.py' -v
python -m pip install 'crafter==1.8.3' pillow
python experiments/void003/two_run.py
```

`.github/workflows/void-003.yml` checks immutable QC-017 source, executes actual game, independently validates each outcome receipt and archives `void003-two-run-crafter-audit.json`. Do not report a result before the real third-party game workflow passes.

## Interpretation boundaries

A positive memory effect does NOT establish a superior learning algorithm, general understanding, useful transfer to a *different* environment, or an optimal two-episode exploration/exploitation policy. A negative effect does not show exploration is never useful. This first controlled test only asks whether historically remembered source observations can repay their actual first-run costs in a reset of the same game.
