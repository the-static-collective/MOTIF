# FIELD-014 — Test whether depth improves practical problem-solving

## Primary research question
Does an editable, source-scoped 3D workspace lead to *fewer material/geometry errors* than the previous 2D-only shared board for unfamiliar real-world improvisation tasks, holding input evidence and user effort constant?

## Arms (same source, blinded scene assignments)

A. FIELD-013 2D board; no depth properties.
B. FIELD-014 3D board with arbitrary heights/positions marked as *assumptions*, no extra source facts.
C. FIELD-014 with one independently known measurement and measured panel-height/ground-clearance witnesses.
D. Optional: FIELD-014 plus genuine local VLM/photogrammetry proposals that MUST be cross-checked with human references and source frames. Compare to same model without editable 3D scratchpad; budget match model calls/tokens.

## Frozen independent challenges

- A planar route that is continuous in 2D but has a gap under the fence in the physical scene.
- Two boundaries crossing in plan but at different elevations.
- An unanchored temporary panel that falls under a gentle specified lateral load (requires independent material physics or field observer; our current engine must HOLD).
- A supporting object that is depicted but must not be moved or drilled.
- A single photo with strong perspective but no camera intrinsics; explicit noncalibration test.
- A false scale anchor, mismatched sketch-to-photo registration, contradictory measurements.
- A harmless-but-visually-salient pile of leaves versus actually usable cage panels.
- A route where moving one existing fence segment outperforms adding more salvage.
- Unfamiliar domains (warehouse aisle, accessible ramp mockup, storage rig), not just dog-fence vocabulary.

## Measures

- **3D geometry truth:** measured clearance/collisions/volumes versus independently annotated measurements, normalized errors when scale is present.
- **Calibration:** rate of false metric claims without verified source correspondence, appropriate abstentions, conditional interval coverage.
- **Practical task:** number of useful alternatives that survive physical fit and human safety review; cost and time of corrections; lost landmark count.
- **Human cognitive load:** number of explanations in prose; number of visual interactions; median time to correct four inserted diagram mistakes.
- **Adverse control:** false approval of safe pet containment, sharp/wired entanglement, falling supports, or unverified connector capacity is a hard failure.
- **Model question:** does independent 3D representation induce new useful questions rather than merely increasing candidate drawings?

## Evidence integrity

Scripted geometry fixtures only verify the software contracts. Browser screenshots are visual smoke checks, not evaluation of real spatial reasoning. An open-weights model running on actual independent photographs is not demonstrated here. Physical safe assembly requires independent manual inspection; photos, models, and simulated geometry cannot certify it. No user property photos/annotated private plan are committed to the public repository.
