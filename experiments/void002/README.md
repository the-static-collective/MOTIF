# VOID-002 — Natural Crafter opportunity-discovery test

**STACKED DRAFT ON VOID-001 / PR #281. RESEARCH HOLD.** Compare MOTIF's original affordance reasoning against strong classical lookahead on **30 episodes of real, unmodified Crafter 1.8.3**, without paying for any language-model API calls.

VOID-001 only ran author-designed synthetic questions; its external map replay measured interoperability and classical path parity, not discovery policy quality. This experiment changes that: alternative information-seeking actions are executed in a separately authored game engine and verified from its actual state transitions.

## What is reused, exactly?

The inherited main-research MOTIF-003 `analyze_first_moves` is invoked by `frontier.py`. Source-pinned QC-017's conventional BFS plan/observation/actual outcome checker and QC-012's privileged local tile sensor are checked out in the CI workflow at `7e35ab7157755c83c6353e939a2ae1b018d70667`. Both competing policies use **that same BFS planner** when a currently witnessed target can be approached. They differ only in how they explore when a resource is not accessible.

Potential future sensor coordinates are treated as hypothetical, **never actual map observations**. Only the game owner's post-action inventories, achievements, positions and termination notices can establish outcomes. No engine maps or inventories are patched for this study.

## Reproduce using GitHub Actions (no paid keys)

The push/PR workflow `.github/workflows/void-002.yml` checks out the exact QC-017 source and installs `crafter==1.8.3` on Python 3.11. It runs:

```bash
python -m unittest discover -s experiments/void002 -p 'test_*.py' -v
python experiments/void002/crafter_trial.py
```

The runner creates `void002-crafter-audit.json`, and CI verifies 30 episode receipts, all receipt hashes, game-only authority, witnessed goal evidence, dependency pin and source constraints. The full file is uploaded as a workflow artifact. **A pending run is not a successful result; verify the Actions conclusion and inspect the audit.**

The locally runnable pure test suite requires no Crafter installation. The full actual-game run requires the pinned checkout at `sources/qc017` plus the Crafter package.

## Predeclared evaluation

See [PREREGISTRATION.md](PREREGISTRATION.md). Four historically examined seeds are used for development comparison and six new, researcher-chosen seeds for the primary heldout comparison. Up to 70 native game actions per policy/seed; goal order is game wood then game drink. Main comparison is **MOTIF-003 versus classical two-ply frontier exploration**; classical one-ply is the diagnostic ablation. All use the same seven-tile privileged sensor and shared conventional observed-target BFS.

Net score = two maximum actual resource goals minus modest action and no-effect penalties. We preserve lower or negative outcomes, false holds, deaths, and failure receipts rather than retune after evaluating.

## Limits

This is a natural game state, not an independently blinded agent contest. It uses programmer-supplied game mechanics, an unusually privileged engine sensor and handcrafted, deterministic exploration criteria; it is not a language-model agent, an invented general algorithm or human-world assistance. Same seed does not guarantee identical subsequent random events when policies choose different actions. No model inference was used, so it cannot establish superiority over a competent LLM agent or the official tau2 benchmark.

After this, the meaningful escalation is a blind read-only task set with actor/tool-state changes, strong same-budget baselines and verified *actual* outcomes; the τ-bench 2.0 source catalog is included in VOID-001, but task execution awaits an explicitly budgeted inference provider.
