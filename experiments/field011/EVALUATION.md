# FIELD-011 — TESTS THAT COULD DISPROVE THE BENEFIT

## Question
Does the source-image → tentative editable board → user correction → two reasoning branches workflow yield better practical-reasoning inputs with **fewer clarification turns and less correction work** than (a) plain chat, (b) a static annotated image, (c) a standalone VLM answer, and (d) the FIELD-010 blank manual board? This research-only phase has **not** answered that question.

## Controlled experiment

1. Obtain 30–60 consented **unfamiliar** images/sketches of movable-object tasks across at least five domains (repair, storage, temporary routing, furniture, gardening). Do not use the personally identifiable yard pictures as a public test fixture.
2. Independent human annotators mark the intended vs actual lines, movable objects, no-go zones, relevant measurements and ambiguous marks. Adjudicate unresolved labels. Retain original pixels and disallow the evaluation authors from creating the model's test targets.
3. Freeze the input set, code version and per-arm compute budget before trying the systems. Include rotated paper, inconsistent scale, lined pages, false dashed handwriting, disconnected views and a source swap.
4. Compare FIELD-010 blank, FIELD-011 browser CV, FIELD-011 Python CV, VLM-only, VLM+FIELD-008 pixel critic and VLM+critic+editable board. Equalize exposure to measurements and downstream solver rules. Include a real human-only baseline with identical time allowance.
5. Track the first unprompted proposal, the final corrected board and the actual physical check results (for genuinely low-risk, voluntarily checked tasks). Stop trials before unsafe animal-access or structurally hazardous deployments.

## Outcome measures

- **Geometry recall / precision** on independently identified *source marks*, separate from correct *meaning* of those marks.
- **Accepted/held false-positive rate:** especially false full-route claims and unconstrained photo-to-sketch correspondences.
- **Direct correction work:** number of drags/taps, seconds to a usable board and conversational turns avoided.
- **Preserved uncertainty:** does the user see what is unverified, and can they refuse a machine proposal easily?
- **Plan impact:** did the new correct mark or measurement change the proposed actions or the best next probe?
- **Context integrity:** a new image, source replacement or undo must not carry stale geometry or a stale worker response forward.
- **Transfer:** new objects and domains not hard-coded in the fixtures.
- **Practical relevance:** whether the user could actually construct/test the low-risk proposal with available materials, excluding safety-critical unsupported assumptions.

## Failure cases to retain

- An attractive, neatly traced line with no supporting ink.
- OCR text mistaken for dashes; notebook rules mistaken for boundaries.
- Detected dashes joined across missing paper.
- One measured chair span used to infer distance to a building in a perspective photo.
- A model mislabels existing fencing as desired new fencing or vice versa.
- An unverified photo coordinate transferred to the plan.
- Reimported proposals overwrite human corrections.
- Resetting to a different image silently inherits old events.
- Open-weights model and deterministic critic agree because they share one mistaken assumption.

**Passing scripted tests is not evidence of advantage over a matched VLM or human.** Publish negative results, runtime costs, abstentions and independent corrections, not just successful illustrations.
