# MOTIF RING-002 — The Living Cartridge Garden

**State:** isolated experimental successor to RING-001. This project distinguishes **a discoverable branch**, **a usable read-only source cartridge**, and **a runnable reasoning method**. They are not the same thing.

## The user request

> Circle every experimental branch. Let MOTIF recruit any combination when useful. Never stop admitting new source candidates when someone creates another branch.

### Implemented — unbounded by the original 149, bounded for safety

- `discovery.py`: retrieves **every GitHub branches API page** for `the-static-collective/MOTIF` on each invocation, validates every ref and its exact commit SHA, and emits `motif.branch-garden.v2` non-executable source passports. It has no fixed ceiling of 149; it has a deliberate safety cap of 2,000 and a 20-page completeness check. A truncated or unavailable API yields **HOLD**, not a false complete scan.
- `source_reader.py`: a **genuine reusable source-only cartridge** that can read a named, pinned branch's `experiments/` or `docs/` text files by Git commit, search bounded text, and return exact file and line witnesses. This works for current and future indexed branches once their source commit is locally present. It never imports or runs branch code. Budget exhaustion is visibly **PARTIAL**.
- `triad.py`: only three **explicitly pinned native executable adapters**: GEOM-013, THOUGHT-014, REASON-CARTRIDGE-006. They run their actual, original source-owned `demo.py` / `trial.py` in separate disposable **no-network, read-only, non-root Docker containers** with memory/CPU/PID/time limits and no credentials or host socket mount. Each original source is retrieved by its exact Git commit; branch movement cannot silently change the code.
- Independent evidence receipts keep geometry's instrument repair, THOUGHT's tiny trained language rules, and REASON's graph council **separate**. Their invented synthetic worlds do not constitute a jointly tested real-world question. The adapter receipts cannot silently become verified world observations or permission.
- `.github/workflows/cartridge-ring-002.yml`: checks new branches every six hours **when this workflow exists on the repository default branch**; also runs on review-branch push and relevant pull requests. It retains bounded catalog + triad receipts as GitHub Actions artifacts. The GitHub scheduler does **not** run experimental-branch-only schedules.
- Test suites cover pagination and later-added branches, renamed/moved branches, refuse duplicates/traversal, source-only lookup, no-execution and budget limits, triad scope checks, original RING-001 routing, and original Door Foundry in its own job.

## What "install everything" can safely mean right now

| Layer | Scope | Actual state |
| --- | --- | --- |
| Catalog | Every observed MOTIF branch, including future discoveries | Available as source-identified **read-only** passports after each live scan |
| Read-only source adapter | Any indexed branch with its pinned Git commit present in the local checkout | One actual universal static source reader, zero branch-code execution |
| Active executable reasoning methods | Original pinned MOTIF-002, -003, -006 (RING-001), plus the three named native triad experiments | Selectively executed **only** through reviewed local handlers/isolated runners |
| Arbitrary future branch source | Newly discovered code without an independently tested typed adapter | `INDEXED_NON_EXECUTABLE`; **not** automatically executable or admitted |
| Real-world external actions | Any external email, network write, publication, tool authority | **NONE** |

A branch can include half-finished code, synthetic fixtures, contradictory interfaces, missing dependencies, accidental side effects, or an entirely non-executable research note. Treating its `git ref` as authorization to run arbitrary code would be a false and potentially dangerous definition of "installed." The useful uniform first installation is **inspectability**; executable admission follows a local source review, a typed adapter, independent tests, and an explicitly authorized effect boundary.

## Current reproducible commands

```bash
python -m unittest discover -s experiments/cartridge-ring-001 -p 'test_*.py' -v

# No live network: reproduce RING-001's originally observed 149 experimental refs.
python experiments/cartridge-ring-001/discovery.py --offline-frozen --output /tmp/garden.json

# Live: fetch every CURRENT branch page (public GitHub API).
python experiments/cartridge-ring-001/discovery.py --output /tmp/garden-live.json

# Read the exact pinned source of a branch, without executing its source code.
# The branch commit must be fetched into the local git object store first.
python experiments/cartridge-ring-001/source_reader.py \
  --catalog /tmp/garden-live.json \
  --ref experiment/geometry-013-self-redesigning-instrument \
  --query 'RedesignLab'

# Actually run the explicitly reviewed native triad, with Docker installed:
# git fetch origin --prune '+refs/heads/*:refs/remotes/origin/*'
docker pull python:3.11-slim
python experiments/cartridge-ring-001/triad.py --output /tmp/triad.json
```

Docker is a mandatory condition for the native triad: the runner will HOLD rather than fall back to running unreviewed code in the host Python environment. Docker image tag choice should be pinned by digest for deployment beyond this experimental review.

## Why the triad is not yet a real "joint reasoning breakthrough"

GEOM-013 repairs a duplicate-record measurement procedure in its own toy cases. THOUGHT-014 learns and stages **non-installed** tiny-classifier language rules in its own toy cases. REASON-006 challenges graph conclusions in its own toy cases. All three run original code, but **their input schemas and fictional worlds are not yet naturally the same**. An aggregator cannot declare a shared truth from three unrelated benchmarks.

A real successor needs a named, jointly usable case; a source-owned adapter translating the same exact evidence and observations to each instrument; contradictory predictions; independent review; and four measured controls: each method alone, fixed all-method routing, dynamically selected set, and a strong conventional planner. Until that succeeds, `cross_method_compatibility: UNPROVEN` is the correct receipt.

## The future branch workflow

A branch appears → next live scan creates a pinned, non-executable source passport → universal source reader can inspect it → classifier examines its declared interfaces and tests → a bounded adapter is proposed → independently reviewed sandbox tests run → explicit human admission to the runnable registry → MOTIF may choose it *when needed*.

This is open to 149, 152, 500 or more new branches; it does not infer that any branch deserves runtime authority. Every scan reports observed coverage; branches missing from later snapshots remain in earlier historical receipts.

**Limits:** public GitHub availability; rate-limits; Git commit must be fetched locally for source reading; 2,000-branch safety cap; sandboxed experiments are source-owned synthetic cases; scheduled Actions only activates on default branch; all external effects remain forbidden.
