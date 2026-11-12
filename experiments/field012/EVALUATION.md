# FIELD-012 evaluation and falsification plan

### Core hypothesis
A source-faithful photo-to-object affordance layer and direct graphical editing reduce human clarification burden, while preserving or increasing downstream plan accuracy, relative to a text-only planner. Failure to beat matched baselines is an informative result.

### Arms and budgets

- A: text-only assistant supplied the one-sentence goal and photo/sketch attachments; no editing board.
- B: shared FIELD-011 board, with human correction of automatically detected lines only.
- C: FIELD-012 board with manual photo-region annotations and conditional object placement.
- D: FIELD-012 with real local open-weights VLM proposals, same human confirmation steps, followed by the visual scratchpad and critic.

Control equal task time, operator familiarity, model call allowance and safety instructions; report both a total-cost and equal-inference comparison. The current authored synthetic demo and mocked VLM tests are **not evidence** of superiority.

### Test families

Freeze unseen annotated images of 20+ real spaces and 20+ salvage collections spanning fences, shelving, accessible storage and temporary workstations. Recruit annotators who did not write the operators. Preserve measured reference dimensions, the actual human preferred zones, object inventory, available fasteners and physical hazards. Include paper drawings of unknown scale and negative controls: perspective illusion, repeated patterns, objects that cannot move, dangerously unstable bracing, a wrong model recognition and an intentionally cropped-out connector.

### Primary metrics

- Correct source-bound object recall, bounding-box IoU and type accuracy.
- Human correction time, number of conversational clarification turns, and direct manipulation events.
- Reuse idea novelty *and verified utility* (separate evaluations) compared to baselines.
- Violation rate for photograph-to-map coordinate transfer, fabricated physical measurements and unsupported safety claims.
- Number of source-supported intended boundaries retained, versus original sketch.
- Actual material usage, revised fit success under supervised physical trial and unsafe proposal rate.
- Replanning latency after a user says a component is fixed, absent or incorrect.
- Human independent assessment of whether proposed next input changed the best feasible strategy.

### Disqualifiers / HOLD conditions

No route to dog access/escape safety may be concluded from zip-tie ratings, anecdotal obedience, or a screenshot. A specific module can be a *candidate support* without having sufficient buckling or tipping resistance. Wire edges, netting entrapment, vehicle proximity and access/egress must be reviewed. Rejected photo observations and disconnected image coordinates may not become positive plan facts. Generated geometry must remain identifiable as a hypothesis.

### Graduations

Progress only after the real perception adapter has run against independently labeled examples and an ordinary VLM baseline; verify coverage/false positive tradeoffs and a human usability study. A synthetic suite with scripted labels confirms protocol correctness but not autonomous spatial understanding. Production deployment requires explicit handling of source-image privacy, project save/restore and versioned reconciliations between both reasoning streams.
