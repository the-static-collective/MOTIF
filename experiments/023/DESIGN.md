# MOTIF-023 — The Human Goal Handshake

**Research question:** Who gets to decide when an answer is enough?

MOTIF-022 showed that a GHoT agent correctly stopped after **one** river report for a task requiring *any* report, but continued until **two** named reports for a task requiring *both* Blue Earth and Le Sueur. That does not establish that the assistant can identify the *human's real criterion for success*. A computer can perfectly solve the wrong task.

This experiment implements a **bounded, offline, credits-free question-first handshake**:

1. Recognize only two narrowly supported public-river information contracts using a small conservative finite grammar, not an LLM. Any person asking "Check the rivers" is **not** assumed to mean either one report or two.
2. Ask the **one question that changes the downstream completion rule**, using GHoT-004's **actual** historical 1-vs-2 public GETs as examples, not future predicted cost.
3. Ask for an explicit freshness cutoff (1, 6, 12, 24 hours), without fabricating a default. Only the 12h contracts have existing physical outcome evidence from GHoT-004.
4. Draft an exact public-source contract: which stations, how recent, what counts as finished. Show this to the human. If they confirm, require the exact SHA-256 digest of that contract to match; otherwise HOLD.
5. **Even with confirmation, no requests are sent.** The result is `READY_HELD_NO_EXECUTION`; a separately reviewed consented execution interface is still required.

The original human text is not included in the reply, stored in a journal, sent to an LLM, or forwarded to an external network. The only observation budget is the fixed GHoT-004 source-owned receipt, validated by the previous `experiments/022/cost_of_knowing.py` inspector. This protocol does not spend money or hosted AI credits. Joules are unknown, not zero.

## Unsupported and dangerous interpretations

- Flood, bridge, road, evacuation or water safety language → `HOLD_HIGH_STAKES`; a streamflow reading is not a safety verdict.
- One specifically named station (e.g. Mankato) → `HOLD_UNSUPPORTED_SOURCE_SPECIFICATION` rather than switching to an arbitrary gauge.
- Community organizing, donated coffee, volunteering, and other real human goals → `HOLD_OUTSIDE_RESEARCH_SCOPE`. This shows the finite grammar's boundary rather than falsely claiming broad understanding.
- Conflicting clarification vs explicit human wording, invalid freshness, changed contract digest → HOLD.

The parser is **not** robust natural-language understanding. It may miss paraphrases and is unsuitable for general production use. Its exact supported dimensions and high-stakes red flags are intentionally visible and adversarially tested. The future authority model must require human review beyond a single lexical classification.

## Concrete execution

From the repository root:

```sh
python3 -m unittest discover -s experiments/023 -p 'test_*.py' -v
printf '%s' '{"text":"Could you check the rivers?"}' | python3 experiments/023/human_goal.py
printf '%s' '{"text":"Need both Blue Earth and Le Sueur river reports within 12 hours."}' | python3 experiments/023/human_goal.py
```

The CI separately tests that ambiguous inputs generate a single decision-consequential question, and that even an unambiguous request produces a confirmation draft rather than unauthorized network activity.

## Proposed human-facing crossing

JAR;VIS can use a byte-pinned subprocess bridge to this **native MOTIF-owned** logic, exposing a local workflow:

**Explain goal → answer one relevant clarification → inspect exact proposed evidence contract → confirm → HOLD pending separately authorized physical action.**

The UI should say explicitly that a raw question is processed by a **local** Python subprocess, never uploaded. It should not reuse the older "questions never cross to MOTIF" statement without explaining this new *local* boundary.

## Falsification

Synthetic tests do not measure real human comprehension. Genuine progress would require independent human-reported success criteria, disagreements with the proposed contract, whether the clarification was worthwhile, and physical resource consumption on tasks *beyond river source readings*. A next research question is whether the machine can learn to detect when its own goal grammar is inadequate, without silently changing a person's goals.

**A fast answer to a misunderstood question is not useful work.**
