# MACHINE-FACING RESEARCH HANDOFF — GROK BUILD × MOTIF LAW-FORGE-011

**Purpose:** Give Grok Build a useful, bounded, independently inspectable contribution rather than copying its entire app workspace into MOTIF. This is a **task packet**, not a command to assume repo authority.

**Available evidence:** [signed critic DESIGN](DESIGN.md), [measured RESULTS](RESULTS.md), [011 source evaluator](source_owner.py), [signed reasoning cartridge](signed_critic.py), [frozen benchmark](trial.py), [Grok-015C donor review](GROK-015C-INTAKE.md). Current branch is draft, stacked on experimental 010, not deployed.

## Challenge for an independent implementer

**Find a real counterexample to the strong claim** that counterfactual mutation questioning beats classical source-owned diversity. The current measured result shows the **opposite**: 24 vs 24 grammar gaps, with classical diversity costing 338 source units and signed mutants 342, across 48 authored synthetic 12-input worlds.

Submit a separate, non-invasive research branch or patch with:
1. A newly designed **hidden evaluator source** not created by copying the 011 model's signed-exception rule list. Keep hidden truth and test labels out of the reason-cartridge module. Define exact typed contracts and query cards with 12/12 budget and separate review/test configurations.
2. One or more **strong classical baselines**, including the *actual classical diversity* policy from 011 and a cost-aware alternative. Same inputs, source permissions, time, and outcome budgets.
3. Preregister a winner rule **before** seeing hidden evaluation outcomes. Do not tune the critic grammar after examining heldout failures.
4. A challenge suite with at least one deliberately out-of-grammar mechanism, a source-version change, duplicated/forged witnesses, and an adversarial all-zeros/all-ones anchor case.
5. An exact JSON receipt (source ID/digest, budgets, policy, review status, mistakes, covered/held cases) with reproducible offline tests, no real endpoint access, no credential use, and no auto merge.
6. A negative-result section describing any cases where ordinary diversity or lookup decisively wins.

**Optional separate task:** Keep your existing `MOTIF-015C Forged Choir` project **isolated**. Extend its exact Bayesian finite-grid witness-dependence test with a time-local false origin tag and independently scored reliability drift. Do not combine Bayesian evidence probabilities with the 011 noiseless Boolean source without a new, reviewed bridge contract.

## Submission boundaries

- Preserve `experiments/law-forge-011/**` and previous experiment history unchanged; new source paths only, or a focused human-review draft PR with a clear base SHA.
- Add no arbitrary network, browser automation, OAuth, real user data ingestion, source authority, plugin install or deploy action.
- Emit a provenance statement for every donor file and independent test set; distinguish developer-authored fixture from independently measured outside data.
- Never imply that multiple Grok models or different origin strings automatically constitute independent evidence. The 015C research already showed why false.
- If the new candidate fails classical controls, publish that result.

**Human review needed before any GRAFT or ALEX import.** The owner of MOTIF controls branch admission. A repository-writing agent must operate within the user's actual connected permissions; this task card grants none.

## Why this is a useful Grok Build task

The uploaded Grok Build workspace contained a substantial portable Python research patch and passing tests, while its React/Vite frontend remained mostly generic scaffold. Treat Grok Build as an **isolated challenger/research engineer** whose patches can be verified with native Python and CI, not as an already integrated production agent.
