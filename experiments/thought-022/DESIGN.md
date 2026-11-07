# MOTIF THOUGHT-022 — Classical synthesis vs LLM vs grammar-aware hybrid

**State:** executable research branch, stacked on THOUGHT-021. No real model result until separate Ollama run completes. No automatic installation, PEN or merge. The language model is a proposer, never a grader or code-execution authority.

## Research question

On several deterministic *author-designed, previously unused* state-transition task descriptions, how much does a generative LLM contribute beyond an exhaustive classical program synthesizer? Can a hybrid conserve model calls by asking for language-model assistance **only after it has identified a missing operation**? Compare with the same maximum independent oracle-query budget, while separately recording model calls, generated tokens, wall-time and result quality. **Do not claim equal total computation.** These are finite synthetic tasks, not independent externally-authored problems or blind tests.

## Three arms

1. **Classical.** Enumerate expressions over `state.on`, `arrival.toggles`, `union`, `difference`, validating every typed AST against THOUGHT-017. Evaluate its complete finite signature using the existing source-owned *set* interpreter. Deduplicate semantically identical expressions. An independent evaluator calculates the desired behavior using integer bit operations. A coverage check at `on=0,toggles=0` detects impossible output; otherwise select the most discriminating probe among remaining candidates. Every surviving candidate needs a final full-domain audit after selection.
2. **Direct LLM.** Use the existing THOUGHT-019 fixed-loopback Ollama gateway with a task-general prompt. The model must generate a valid typed AST; MOTIF never invents a successful model proposal. Use the *same* independent probe selection and maximum oracle-query budget. Reject a new proposal if it already contradicts a source-owned DEV observation, without spending a new oracle call. All model generations and negative results count toward the model budget. After selection evaluate all 64 input pairs independently. No frozen labels or winning expression appear in the model prompt.
3. **Hybrid.** Run classical synthesis first. For expressible tasks, **zero model calls**; don't waste inference to reproduce known classical solutions. If no expression fits a witnessed development input, stop with `HOLD_GRAMMAR_INADEQUATE` and optionally call an actual local LLM *once* for a review-only missing-vocabulary suggestion (`complement`, `constant_universe`, or `unknown`). The model cannot dynamically install new syntax or certify that its proposal fixes the problem.

## Tasks and deliberately hard boundary

| Evaluator-owned brief | Target behavior | In the bounded grammar? |
| --- | --- | --- |
| FLIP: switch each marked bit | XOR | yes, constructed from union/difference |
| INTERSECTION: keep only previously-on and event-marked bits | AND | yes, **not in THOUGHT-018's reviewed named patterns** |
| DRAIN: turn marked bits off | A AND NOT B | yes |
| REPLACE: overwrite entire set | B | yes |
| INVERT: reverse every bit regardless of event | NOT A within all 3 colors | **no**; union/difference of two empty sets cannot make new ON bits |

The **semantic closure** of the two-operand, two-operator grammar is just **8 possible bitwise functions** over these finite masks. A single well-chosen discriminating test distinguishes them once the `(0,0)` coverage check is passed. This is a very small search space. A model that loses to classical synthesis here is not evidence it cannot reason more generally, and a model that wins adds no novel algorithmic capability unless tested on harder grammars with real independent tasks.

## Evidence boundaries

- The candidate expression is checked using source-owned MOTIF-017 set semantics; target observations are from a **different bitmask implementation** (`independent_oracle` in `synth.py`). They are not independent physical observations.
- Input fixtures are in repository source and therefore not genuinely blind to researchers or model builders; only the model's request path omits audit labels. The `frozen_full_domain_passed` score is evaluated **only after** the synthesis arm freezes a candidate.
- Python `-I` is not an OS security sandbox; this trial never executes arbitrary model-authored Python. Model output is typed data, evaluated through a finite DSL.
- `HOLD_GRAMMAR_INADEQUATE` is a constructive failure, not a proof of AGI; changing the grammar requires a separate design/test/review cycle.
- Model identity metadata is daemon-advertised, not independently verified. GitHub Actions downloads model weights to an ephemeral runner; the research Ollama installer is still unpinned.
- LLM vs classical budget matching is **oracle-query ceiling**, not equivalent energy, latency, generated tokens or GPU/CPU cycles. Retain negative results and exact measured receipts.

## Reproduce without a model

```bash
cd experiments/thought-022
python -m unittest -v test_race.py
python benchmark.py
python run.py --tasks flip intersection drain replace invert
```

## Run actual larger local model

```bash
# Separately install Ollama and qwen2.5:3b (larger than prior 1.5b)
cd experiments/thought-022
python run.py --model qwen2.5:3b --tasks intersection invert \
   --model-budget 3 --oracle-budget 2 --timeout 150 --output comparison.json
```

This code does not install models or connect to arbitrary endpoints. GitHub Actions provides an optional isolated real-model research job and preserves its raw receipts even if results HOLD. No deployment or merge happens from a favorable score.
