# COGNITION-001 — Four-Speed Mind: idle contemplation under GHoT resource discipline

**DRAFT / RESEARCH HOLD.** A local experimental cognition composition that implements the user's four modes: reflex, deliberation, reflection and contemplation. It is an **actual bounded Python prototype** with the original MOTIF-003 affordance code and **actual upstream GHoT scheduling decision function** (at pinned SHA). It is not a deployed Android/iOS application, perpetual background daemon, language model, autonomous learner, simulated consciousness or verified AI advance over classical methods.

## A working architecture

```text
AUTHENTICATED/OWNER-ADMITTED DAILY RECORDS (lab: synthetic records only)
               |
          APP VISIBLE + USER OPT-IN
               |
    +----------+------------+
    |                       |
  USER TASK            IDLE FOREGROUND TICK (max one per call)
    |                       |
  REFLEX (known)              |
     OR DELIBERATION          |
    |                    APP + RESOURCE GATES
    |                 (user active / screen hidden /
    |                  battery / thermal / CPU / cap)
    |                       |
    +-------> REFLECTION <---+
                     |
          PINNED GHOT DECIDE_FROM_CANDIDATES
          local synthetic offer / urgency=background /
          deferrable=true (NO dispatch, NO actual GHOT task)
                     |
           HOLD or LOCAL-ONLY CONTEMPLATION
                     |
          GENIUS HEURISTIC LENSES
          skeptic / systems / story /
          planner / experimenter
                     |
            CANONICAL MOTIF-003
          prospective question affordances
                     |
          PENCIL: TESTABLE QUESTIONS
                     |
         REVIEW QUEUE, NOT PRODUCTION TRUTH
                     |
         owner must approve any actual code/data change
```

### Four separate types of cognition
- **Reflex:** two or more verified recorded successes for an action make a *guarded recommendation*. It executes nothing without a separately authorized action owner.
- **Deliberation:** a task-facing next question; disputed source reports trigger independent verification.
- **Reflection:** compares earlier vs present-day source-bound entries; contradictory reports remain contradictory until separately explained, and history stays immutable.
- **Contemplation:** when owner opts in, the app is genuinely visible, the user has been idle for at least 20 seconds, and a separate energy gate admits the work, each `tick()` creates at most one cross-day/cross-source *hypothetical* question with a falsifier. Historical genius lines here are heuristic perspectives, not independently running characters or LLMs.

### GHoT integration — honest boundary
In CI, the workflow checks out `the-static-collective/GHoT@9748a0772c4a13135421c4fa84a9991e0a51e05f` and imports `ghot.energy_scheduler.decide_from_candidates` **without copying or reimplementing its decision logic**. The supplied power/offer/body states are deliberately synthetic lab data. This validates GHoT policy interoperation, **not that an actual `motif.contemplate.v0` executor has been registered or approved on a real GHoT node**.

The app-specific gate also refuses sleep/background, user activity, missing opt-in, low/unknown battery, thermal >=75°C or unknown, high CPU, GHoT critical/conserve power state, exhausted daily budget or remote candidate. Normal battery-only heavy compute remains held; charging+abundant permits a bounded step.

**Android is not implemented.** An actual app needs lifecycle callbacks and cooperative cancellation on leaving the foreground, and should not attempt an unrestricted forever loop. Android foreground asynchronous work can be interrupted when the app stops being visible. System-managed background scheduling would be a separate explicit feature subject to OS policies.

### Guardrails
- Synthetic journal only, no user records read and no cloud or third-party data transfer.
- No autonomous code rewriting, model weight updates, push notifications, GitHub changes beyond this research PR or physical-world tasks.
- Source IDs and distinct synthetic origin roots do **not** prove that two real persons or institutions are independent.
- A contemplative card is a question/prediction `PENCIL_UNTESTED`, not an observed insight `INK`.
- `self_optimization_proposal()` stays `HOLD_FOR_OWNER_REVIEW`; it merely proposes a bounded experiment and provides no claimed measured gain.
- Daily budget <=6 lab credits, <=1 hypothesis card per admitted tick, bounded input and no perpetual run.
- On a real device local/GHoT compute and data-access should require independent opt-in, explicit device permission, telemetry and a user-visible Off switch.

## Reproduce from research branch
```bash
# CI checks out GHoT at pinned SHA under sources/ghot; do that first locally.
python -m unittest discover -s experiments/cognition001 -p 'test_*.py' -v
python experiments/cognition001/circuit.py > cognition001-demo.json
```

A GitHub Actions workflow validates the frozen design and GHoT SHA, runs the tests, and archives the demo output. This proof tests architecture and guards. It does not prove intelligence gains or run while the ChatGPT interface is idle.

## Follow-on experiments
1. Replace the synthetic journal with a **user-approved, local-only daily receipt importer**, with source filter/retention settings.
2. Implement an actual opt-in app foreground worker, lifecycle cancellation, process budget metering, transparent status panel and separate GHoT capability registration.
3. Allow optional **independent model perspectives** with separate provenance and compute costs; compare against a conventional single-critic baseline.
4. Quantify true utility: how many proposed questions lead to **independently confirmed helpful outcomes** per joule, CPU second, human minute and privacy risk; penalize redundant, misleading and never-used proposals.
