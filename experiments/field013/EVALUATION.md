# FIELD-013 evaluation contract

## Pre-register the actual question

Does automatically proposed *source-scoped object inventory* reduce labor and increase accuracy of alternative physical arrangements compared with: (1) user-drawn regions, (2) a simple visual saliency detector, (3) a matched ordinary VLM with no reasoning loop, and (4) a VLM with a source-citation/pixel review loop?

## Primary metrics

**Perception:** independently labeled object/region IoU, precision/recall over target reusable materials, named role correctness, false confidence, background/clutter false proposals, and distinct-photo object identity mistakes.

**Reasoning:** novel but plausible repurposing hypotheses *not present in the initial user instruction*, fraction surviving independent human feasibility review, whether it recognizes movable existing barriers and opportunistic supports, irrelevant alternative count, missed constraints.

**Human interaction:** corrections made in the visual board, elapsed time to a reviewable plan, required conversational turns, number of user supplied measurements, ability to reject misleading drafts, and usefulness of next measurement selected.

**Safety:** number of times an unmeasured length, unstable chair, unverified trampoline attachment, sharp mesh, pinched gate, or weak/incorrect fastening is treated as proven suitable. Target zero unsupported certificates.

## Experimental integrity

- Freeze previously unseen test scenes, labels and expected real-world facts *before* scoring.
- Per-image model calls and CPU/GPU time are logged. Correlated second looks from the same vision model are not independent witnesses.
- Score alternative hypothesis *quality*, not just count. A system that produces 20 arbitrary configurations is not better.
- Run saliency-only negative controls on foliage, wallpaper, repeated chain-link, and empty grass. Use actual human-confirmed salvage boxes as the reference for novel scenes.
- Candidate geometry, proposed placement, observed source and physical measurement must stay separate.
- A hypothetical proposal never triggers physical building or dog release; require a human safe cold-fit test if the user chooses.

## Current evidence (November 12, 2026)

- FIELD-013 source tests and regression tests executed locally; see console logs/CI receipts.
- Actual pixel processing of nine privately provided yard photos found 4 unclassified high-saliency windows per photo (36 total), but qualitative inspection found many concentrated on ground/leaf texture instead of actual reusable panels. These *cannot* be counted as 36 material detections.
- Open-weights VLM code path mocked, not executed; no model benchmark results yet.
- Source UI wiring and self-contained output are testable; standalone browser rendering not independently confirmed in this runtime if browser navigation is restricted.
