# MOTIF THOUGHT-013 — Self-directed questions, and a Human Talk membrane

**Status:** executable, local-only, Python standard-library **synthetic research**; a stacked experimental branch of THOUGHT-012. **No live JAR;VIS or Full Measure service changed.** No external tools, data collection, automatic speech recognition, large language model, PEN promotion, donor permissions, or deployed UI.

## The two hypotheses

1. **Inquiry direction.** Given an explicit finite set of competing hypothetical worlds, a bounded engine can choose its next **testable question**, inspect the declared relation through the suitable lens, receive a separately supplied outcome, and change its next question accordingly. The measurable aim is to reduce question cost to resolve a *predeclared decision*, not to claim that geometric arrangements prove something.
2. **Native conversational form.** Language can be a **first-class typed reasoning event**, not just the final caption: an incoming utterance identifies a limited speech act; it changes a question-selection objective; MOTIF formulates a QUESTION_ONLY utterance tied to an exact source relation and manifestation IDs; a test returns a held observation; the next utterance and next inquiry are contingent on that outcome. This is a small formal model of human talk, **not proof of humanlike language understanding**.

## The actual Human Terminal donor

Inspected the **Full Measure — World Layer** implementation: [`the-static-collective/full-measure-world-layer`](https://github.com/the-static-collective/full-measure-world-layer) → `src/lib/humanTerminal/interpret.ts`, `src/lib/humanTerminal/types.ts`, `src/lib/humanTerminal/operator.ts`, and `docs/superpowers/specs/2026-08-17-human-terminal-v0.1-design.md`. Full Measure's Human Terminal maps basic-human phrases to a **finite local intent vocabulary**; unknown input remains unknown; read-only explanations derive from source projections; a proposed crossing still needs an existing Garden confirmation. This experiment **adopts the membrane pattern**, including some input aliases such as “Where am I?” and “What can I safely do?”. It does **not** import or impersonate Full Measure's actual worldRuntimeClient, execution operator, donor state or permissions. The repos are independently owned.

```
  Human utterance (optional)
       |    conservative local grammar, or validated external proposal
       v
  Typed dialogue act + EXACT manifestation IDs + unchanged source digest
       |    no explicit referent? → CLARIFY / HOLD
       v
  Finite hypothetical-world model / source graph
       |    choose next source-anchored test: decision-relevance or world entropy
       v
  Human-talk QUESTION_ONLY ('Could we check whether ...?')
       |    separate test/oracle; UNKNOWN remains UNKNOWN
       v
  Revised hypothetical-world set; encounter countermodels/mismatch → HOLD
       |    all surviving models agree? CONDITIONAL ONLY, not fact or PEN
       v
  New question / bounded provisional spoken result / review receipt
```

## Technical implementation

- **`inquiry.py`** uses THOUGHT-008's real `ThoughtViews` and THOUGHT-012's fixture format. It constructs a local catalog from `AUTHORED` typed source edges touching a bounded inquiry cut around two exact manifestation IDs. `HYPOTHESIS_ONLY` edges cannot become source witnesses. The algorithm optionally renders the *real* source-owned lens but calculates all choices from non-geometric symbolic inputs.
- **Hypothesis model** is explicitly supplied: 2..64 distinct complete worlds with known boolean answers to catalog questions and a modeled binary decision. These are *assumptions*, not knowledge automatically learned from observations or a probabilistic world model. Priors are uniform. All answers come from a separate fixture oracle; none are fabricated from node proximity or natural-language plausibility.
- **Decision relevance** maximizes expected information gain about the *declared decision outcome*. The strong classical **world entropy** comparator maximizes entropy reduction about the **entire possible-world ID** instead. Both are exact Shannon-entropy enumerative classical algorithms, not inventions or trained policies. After each answer, the candidate pool and remaining world set are re-examined. Missing `UNKNOWN` does not narrow hypotheses; contradiction with every surviving hypothetical world triggers `HOLD_MODEL_MISMATCH` instead of 'hallucinating' a new model.
- **`human_talk.py`** implements typed speech acts (`EXPLORE_POSSIBILITY`, `CHALLENGE`, `INSPECT_EVIDENCE`, `COMPARE`, `ORIENT`, `INSPECT_MOVES`, `REVIEW_PRIOR`, `UNKNOWN`, `HOLD_EFFECT_REQUEST`). A *bounded* recognized phrase changes which question-selection objective is used. Internal dialogue turns include `HUMAN` / `MOTIF`, exact `question_id`/`relation_id`, source digest, pencil status and spoken text. This is an alternative internal representation mode alongside source-graph and geometry; no model is actually run.
- **Optional external interpreter seam**: a hypothetical local T5/LLM could later supply a versioned candidate `motif.human-talk.interpreter-proposal.v1`, bound to the SHA-256 digest of the **exact utterance**, a bounded speech-act allowlist, exact manifestation IDs and an explanation. Validation rejects unknown actions, unbound refs, fabricated identities and mutations; successful proposals are tagged `UNVERIFIED_EXTERNAL_PROPOSAL`. **This experiment does not invoke any model** or silently use an external service.
- **All effects held:** a `PENCIL` question/answer is not a PEN commitment, empirical truth, verified source, or external action permission. The 006 ledger remains unchanged. The hypothetical oracle is a test fixture; asking an unrecognized sentence or effectful instruction does **not** execute anything.

## Demonstration, benchmarks, controls

`fixtures.py` reuses the source-owned THOUGHT-012 synthetic community-meal graph (food, meal, venue, volunteer, storage, and duplicate-label Home). It defines **16 explicit hypothetical worlds** over four variable binary source claims; the toy decision depends on venue and volunteer enablement, while van and food storage are deliberately irrelevant to the toy decision. Every test answer is looked up from the single selected toy-world oracle, **outside the inquiry model**.

The benchmark independently runs 16 toy-world cases with a maximum **three questions per case** and no external actions:

- `decision_map`: decision-relevant selection with optional source-lens projections.
- `decision_no_map`: **same decision-relevant classical strategy without geometry** (strongest spatial ablation; expect exact parity).
- `strong_world_entropy`: classical greedy information gain about whole-world identity with no layout.
- `dependency_only`: restricted single-family query strategy, included as a weaker negative control.

**Actual local results (20 unit tests):** under those *designed* hypothetical worlds, decision-relevant with geometry **16/16 toy decisions resolved using 24 total questions**; decision-relevant without geometry **16/16, also 24 questions**; whole-world greedy entropy **16/16, using 40 questions**; dependency-only **8/16** with the same per-case budget. This is an **objective function comparison in a toy model**, *not* evidence that geometry or a language layer improves accuracy. The no-map decision-relevant classical algorithm ties the multi-view engine in correctness **and** questions used. The benchmark was developed with the code, not blind, independently adjudicated or a claimed real-world result.

Human Talk alternates the speech acts `ASK` and `RECORD_TEST_RESULT` during the reasoning loop and ends with a conditional `PROVISIONAL_SUMMARY`, or HOLD. It retains duplicate labels as distinct manifestation IDs and refuses to guess references from text. If a language model were plugged into the optional proposal seam, its output would still be a *hypothesis to validate*, never an executable command.

### Run

From repo root:

```sh
cd experiments/thought-013
python -m unittest -v test_inquiry.py
python benchmark.py > benchmark-results.json
python demo.py > demo-results.json
```

All code is stdlib Python 3.10+. Deterministic input digests and step receipts are **integrity and provenance pointers, not authenticity or truth proofs**. No local personal data or network IO needed. The CI workflow also runs THOUGHT-012 regression tests.

## Falsifiers and next gates

Mandatory HOLD if unknown language, ambiguous referents, attempted external effect, unsupported operation, missing oracle, contradictory model, or changed source. Falsify the experiment if coordinates influence the chosen question, hypothetical link is treated as witnessed fact, source/pen is mutated, under-specified language becomes a command, same-label concepts merge, or a proposed interpreter frame acquires authority.

Before claiming a genuine “native human-language cognition” mechanism: test a frozen, independently judged corpus of paraphrases and ambiguous utterances; compare a basic rule interpreter, compact T5 parser, and general LLM under equal tools; audit referent ambiguity and false promotion; measure reasoning/decision improvement relative to a **no-geometry, language-aware** classical baseline; include counterexamples that invalidate the proposed world-model vocabulary. The input grammar should expand only with falsifiable new examples, not with a declared set of magic keywords. A human-facing JAR;VIS feature needs its own local opt-in UI/permission/read-only PR; Full Measure's independent runtime must not be silently crossed.

**Core law:** Human words may suggest how to investigate. A source-grounded test determines what survived. A thought and its drawing never grant authority.
