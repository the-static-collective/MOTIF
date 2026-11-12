# FIELD-017 independent evidence plan

**Primary falsifier:** Given the same images, materials and budget, can a conventional planner + strong VLM produce safer, more correct, cheaper layouts than MOTIF's assembly, while requiring fewer corrections?

Treat the following as **separate measurements**:

| Question | Metric | Falsification control |
|---|---|---|
| Can the program revise after a failure? | Changed arrangement and explicit failure receipt | Keep original failing arrangement fixed |
| Is it efficient? | Model-evaluation count and elapsed wall time | Identical full critic calls to random full-catalogue and greedy baselines |
| Does the result physically fit? | Independent tape-measure fit and panel positioning by authorized practitioner | Do not use constructed model's own numbers as test labels |
| Is the plan actually safe? | Independently reviewed hazards, edge/gap/contact, loads/anchors, egress | Preserve unknowns, do not count HOLD as safe |
| Did visual reasoning help? | Correct object identity and relations, 3D distance/occlusion error | Source-only VLM, CV-only, pre-supplied inventories and nonregistered views |
| Did the shared board help? | Correction count, time, loss-of-source-facts, confidence calibration | Text-only Q&A with same information |
| Is uncertainty kept honest? | Rate of false physical-certification claims | Contradictory measurements, misleading images, and no scale |

For **open-world** testing, use separate photographer-provided materials, nondisclosed goals and site permission; avoid personally identifying source imagery in a public repository. Timebox work and ensure no animals are exposed to unverified arrangements. Unknown structural validity is a HOLD, not a permission to try on an animal.

The included benchmark is deliberately **not blind** and its 10 worlds are sourced from variations of one fixture. It is useful as a software regression and a baseline sanity check only. It does not establish real-world superiority, autonomous physical understanding or scientific novelty.
