# FIELD-010 — Evaluation Program (preregister *before* blind trial)

## Questions
1. Can non-specialists correct a visual scene faster and more accurately than describing it again in prose?
2. Do edits improve the autonomous branch's **downstream** plan validity, not only its apparent interactivity?
3. Can the system propose only the most consequential optional interaction instead of burdening the user?
4. Does preserving the original drawing prevent hallucinated completeness, mistaken metric units, and false photo-to-map registration?

## Four matched arms
A. Text chat alone, with the same raw source images and question.
B. Static annotated image, no editing, with the same reasoning model.
C. Shared board with editable geometry and fixed, always-visible measurement fields.
D. Shared board + versioned autonomous branch + dynamically ranked optional interaction prompts (FIELD-010).

Keep the same perception model, task budgets, image access, time caps and compute cost across comparable arms. Explicitly measure differences if compute cannot be equalized. The offline prototype uses authored rules; do **not** describe D as proven AI-mediated visual understanding until it includes a real model and a genuine blind run.

## Data and ground truth
At least 36 previously unseen, consenting, independently annotated cases: 12 repurposed fencing/temporary barriers, 12 shelving/storage, 12 practical non-load-bearing layouts. Include (a) unscaled cartoons, (b) rough measured sketches, (c) conflicting measurements, (d) misleading dashed marks, (e) items placed at different photographic depths, (f) support objects that look plausible but are not safe. Annotators record intended boundaries, true dimensions where measurable, item movability, actual material function, hazard constraints, and hidden intended corrections. Annotators do not write the test prompts or the program's heuristic rules. Real dog-yard footage/images require user permission, privacy review, and no public repository uploading.

## Metrics and denominators

| Metric | Definition | Desired threshold, **not a result** |
| --- | --- | --- |
| Geometry retention | Correct relevant landmarks/line roles retained after editing ÷ independently annotated relevant items | ≥ 90% for D |
| Phantom geometry | Unsupported segments treated as confirmed ÷ all confirmed segments | 0 for ambiguous perspective and dashed marks |
| Correction efficiency | Median time and user actions until target ground-truth geometry is represented | D ≤ 75% of A median time |
| Clarification burden | Optional prompts accepted or required before acceptable route created | Fewer than A without missed critical facts |
| Ratio/measurement reliability | Valid intervals covering measured lengths in sketches with **validated** distortion assumptions | Measure error; no target without empirical calibration |
| Decision relevance | Questions whose answer changes the selected hypothetical layout ÷ questions offered | Compare B, C, D; record unanswered |
| Work saved | Actual field-fit attempts and material used for human-approved prototype | Improve over A without hazard regression |
| Safety abstention | Known dangerous/unknown supports explicitly marked HOLD | ≥ 95% on pre-labeled risky cases |
| Evidence attribution | Final useful claims citing corresponding visual/user evidence or marked hypothetical | ≥ 95% on blind annotations |

Do not silently exclude abandoned cases, timeouts, negative results, disagreements or user corrections that make the solution worse. Report each arm's costs, failures, and all model-generated interface prompts, not just accepted ones.

## Experimental sequence

1. Freeze a source-only dataset and human annotations **before** any model sees them.
2. Run each arm on randomized task order, counterbalanced between participants; never re-use the same individual as a knowledgeable tester across identical case arms without addressing learning effects.
3. Independently judge intermediate scene geometry, physical plausibility, missing hazards, and whether a specific next question was worthwhile.
4. If an interface edit arrives while computation is underway, assert that stale-version proposals are discarded; verify board JSON round-trip and undo replay.
5. For actual field construction, keep human approval and appropriate physical safety controls. Count what happened physically separately from paper agreement.
6. Report confidence intervals and the number of cases/participants; don't infer improvement from authored fixtures or weak controls.

## Immediate verified tests vs future studies

Present repository tests cover schema validity, rigid movement and endpoint updates, source immutability, event reversibility, no scale from guessed measurements, abstention on contradictory anchors, and worker-branch outputs. This establishes deterministic behavior only. No person completed a timed usability study yet, no blind real VLM interpreted the actual original sketch and photos, and no physical fence was built or evaluated by this software.

## Specific falsifiers

- A blank/ambiguous sketch yields a claimed complete perimeter.
- A photographed chair or trampoline gets silently promoted to a verified anchor.
- A single physical width in an arbitrary perspective photo generates yard-wide estimates.
- More widgets increase interaction count without improving final plan correctness.
- Visual edits are mistaken for physical acts or independent observations.
- Two measurement references contradict yet yield confident lengths.
- Late results computed from older states replace newer user corrections.

A single severe instance is an architectural finding, not merely another score in an average.
