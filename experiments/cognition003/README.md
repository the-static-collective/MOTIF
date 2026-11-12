# COGNITION-003 — Associative Resurfacing: Old Knowledge, New Emergency

**DRAFT / RESEARCH HOLD.** This is the first measurable two-day downstream-usefulness challenge for the COGNITION-001/002 architecture, not a claim of independent AGI, involuntary biological memory or mobile deployment.

### The experiment
Day one: a simulator records **four separate first-hand contacts** forming **two possible two-edge associations**: an observed cue may correspond to a mark; a mark may help identify a component. The relations remain `unresolved` and **cannot certify a repair**.

Day two: an unprompted incident arrives with a cue, without a user request to search historical memory. The system must resurface the older two-hop information as a **testable question**. It may perform up to two explicit, individually witnessed simulated diagnostic probes and repair ONLY after a positive independent probe. Hidden owner-world truth may drift. Duplicate source origins are excluded from independent corroboration.

### Native organs
- Actual native [Free Graph](https://github.com/the-static-collective/free-graph) `fg_core` + `fg_ops.neighbors`, pinned SHA `ec0ad8743c5faac3f3675760bbafcbcb1df846c1`. The packet retains its unresolved task-world cut and all edges are nonconstituting. A native neighborhood is a projection, not authority.
- Original MOTIF-003 affordance observer is called on hypothetical **test** actions, not on known faults.
- Actual pinned GHoT energy policy from COGNITION-001 governs **idle** compilation, visibility and opt-in. When no permission to contemplate exists, a task-directed online traversal can still respond, but it is never called background thinking.
- PRIVATE MEMENTO owner validator from COGNITION-002 is called only when an **owner-allowed private checkout** is explicitly supplied. It checks four past contacts, two unresolved Understory association records and one **later activation** through native `validateUnderstoryRecords`. No MEMENTO history, personal information or private code enters the public packet. Public CI observes explicit HOLD; private MEMENTO CI may run the synthetic case end-to-end.
- No background daemon, no real-world external act, no retraining, no private note access, no auto adoption.

### Fixed policies and falsifiers
The frozen source and evaluation contract is [PREREGISTRATION.md](PREREGISTRATION.md), committed at `2af4905777eeeadd7ab213db323ce12fe5b92a45` **before** the method and evaluation.

1. `motif_resurface` — source-aware precompiled associations in idle; new event triggers old Understory-style activation and native MOTIF-003 affordance proposals.
2. `classical_cached` — **strong matched** provenance-aware classical two-hop index with **same idle compute, event access and allowed probes**; may tie on actual outcomes.
3. `classical_online_bfs` — **strong** classical graph query with the same records, old/new source access and action budget, but computes reachable paths after the event instead of caching; may tie.
4. `recent_only` — explicit weak diagnostic ablation that has no old archive; not a competitive representation of classical retrieval.

Five regimes: `stable`, `drift_alternative`, `drift_unmodeled`, `echo_source`, `unrelated_trigger`. The last two test unearned certainty. Main evaluation is **32 new authored seeds × 5 regimes × 4 policies = 640** individually measured cases, plus 80 development cases. Per-policy benchmark uses 160 case events; some have no possible answer from permitted source evidence. The primary outcome is **independently simulator-verified repair**, not a linguistic claim of solving it.

Computed "idle ops" and "wake ops" count instrumented graph/index work; they are **not wall-clock latency**, energy use or neural activity. A speed advantage over `classical_online_bfs` doesn't establish a novel architectural advantage because `classical_cached` performs the same precomputation. This prototype tests mechanism and source-bound usefulness under controlled synthetic conditions.

### Run locally
Checkout public GHoT and Free Graph at the pinned SHAs under `sources/ghot` and `sources/free-graph`. Then:

```bash
python -m unittest discover -s experiments/cognition003 -p 'test_*.py' -v
python experiments/cognition003/resurface.py --split development > cog003-development.json
python experiments/cognition003/resurface.py --split heldout --full > cog003-heldout.json
```

The separately authorized private MEMENTO integration can use:

```bash
python experiments/cognition003/resurface.py --one-seed 71001 --one-regime stable --memento-root /authorized/private/MEMENTO
```

### What future results would mean
If MOTIF and cached classical tie, this is a working implementation of *source-validated associative reactivation*, not a superior retrieval algorithm. If neither finds a repair in an unmodeled drift, count the abstention and missing knowledge. The next genuine test needs an independently authored multi-day incident dataset with unexpected vocabulary, trusted external task owner and a real app lifecycle to evaluate whether unprompted resurfacing saves actual time or prevents mistakes.
