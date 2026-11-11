# COGNITION-001 — Four-Speed Mind / Foreground Contemplation
**Frozen research contract, 2026-11-11. Research HOLD.** This user-inspired experiment is a local, read-only, opt-in **foreground idle** thinking loop, not a persistent Android service or a deployed agent. No claim of consciousness, independent self-improvement, human-device use, or a production GHoT coupling.

## Question
Can MOTIF use four separate routes for computation—**reflex** (verified cached action recommendation), **deliberation** (open problem/next evidence request), **reflection** (compare evidence and errors across days), and **contemplation** (bounded imaginative cross-thread hypothesis generation)—while conserving resources, explicitly preserving uncertainty and source custody, and producing useful falsifiable questions without unsupervised action?

## Research constraints
- Call native `experiments/003/affordance.py` for bounded counterfactual ranking, never present possible worlds as current facts.
- Call **actual pinned GHoT** `ghot/energy_scheduler.py:decide_from_candidates`, from commit `9748a0772c4a13135421c4fa84a9991e0a51e05f`, with explicitly synthetic, local-only, advertised `motif.contemplate.v0` candidate. No actual BODY daemon registration, real hardware probe, real GHOT execution, remote dispatch or energy receipts. The original GHoT algorithm, not an imitation, decides HOLD vs run; second gate always enforces local, visible, opted-in, idle, and power/thermal/CPU/user-priority limits.
- Simulated `app_visible` is required for work and toggles off instantly; **no background OS service** and no automatic post-close processing. The user can disable contemplation at any point. Process at most one small job per eligible `tick`.
- Enforce user idle >= 20 seconds, battery >= 35% unless externally powered, thermal < 75C if known, CPU pressure <= 0.6, no active task; hold if unknown thermal/power on battery; conservative scheduling; capped daily units. No remote execution, services, paid model calls, source scraping, or UI device inspection.
- Input is a **researcher-written synthetic two-day journal** of bounded structured records; no current user's notes, emails, court details, memory, or other personal content is collected. Hypotheses and interpretations go only into local return values. Real user data would require explicit consent, source permissions and separate adapter.
- Keep independent observed/report vs hypothetical/proposal categories; never rewrite original records or promote a persuasive story into a verified cause.
- Genius perspectives are deliberately **heuristic lenses** (e.g. structural analogy, skeptic, storyteller, planner, experimentalist), not instantiated historical geniuses, independent LLM agents, or activated GENIUS-011.
- Reflection compares earlier+later source-bound records and creates falsifiers/review questions; contemplation combines perspectives and can propose future tests, without model retraining or code modification. The only self-optimization in this experiment is an **operator-reviewed optimization proposal** with an offline counterfactual workload estimate.

## Frozen fixtures and falsifiers
Use at least 2 distinct days and >= 5 synthetic records from distinct origin roots; include a successful repeated workflow, a failed earlier workflow, a disputed later witness, and independently observed contradictory later result. Test evidence duplication and source isolation, revoked opt-in and hidden app, active user, low battery, overheating, high CPU, GHOT missing/no-offer state, daily cap, deterministic multi-thread outputs and ability to interrupt/cancel between ticks. Test native GHoT HOLD on conserve/critical and local RUN under favorable power; never count remote worker as authorized. `--demo` emits exact result and typed proposed followup; default import performs no work.

## Measurements / audit
- Actual permitted contemplation ticks, GHOT HOLD decisions, simulated cpu-unit budget consumption, number of candidate/falsifier cards, independent-source root count, duplicate drops, and zero external actions.
- Distinguish the number of proposed questions from their **verified external validity**. In this phase proposals have NOT been answered/tested by an independent party; no competitive gain over a standard reflection loop is claimed.
- Falsifier: no human authorization bypass; every actual admitted step checkable and bounded. Passing unit tests alone do not establish real Android use or actual power savings.
