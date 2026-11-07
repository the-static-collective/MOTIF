# MOTIF THOUGHT-024 — Cross-domain vocabulary transfer (bounded test)

**Status:** Experimental, source-owned review branch stacked on THOUGHT-023. No merge, source installation, real-world action, PEN authority, self-improvement claim, or model-authored Python execution.

## Question

Can the **universe** vocabulary addition from THOUGHT-023 be reused for set-like transformations described in different human domains, without referring to the switch example? And can the system **refuse** transfer when the new problem does not fit the source-owned Boolean language?

## Experiment

1. The developer supplies distinct **natural-language task descriptions** about permissions, pantry supplies, a finite endorsement register, access controls, shift rosters and membership. The descriptions do not cite the earlier switch puzzle, though they specify what the input and output sets mean.
2. **Classical comparator:** Independently enumerate the exact 8-function old grammar vs 16-function universe-extended grammar, query a separate task oracle on at most six development inputs, freeze a program, and only then evaluate all 64 possible `(current,event)` pairs.
3. **Generative comparison:** A directly invoked, operator-selected local Ollama Qwen model gets only task text and *developer* counterexamples and proposes a **generic code-free AST** with `current`, `event`, and `universe`. A trusted adapter maps those generic references to the previous THOUGHT-023 grammar. The model does not receive the task function's name, its oracle implementation, frozen test labels, or source-writing permissions.
4. Every model candidate is checked on six fixed developer cases; bad proposals may receive one observed developer counterexample and retry within a two-call budget. Only after passing all development cases is a candidate frozen for a full-domain 64-case evaluator and a separate, trusted fixed-template executable Python check.
5. **Negative controls:** (a) a cross-category threshold rule (not expressible by pointwise set operators); (b) a three-valued true/false/unknown belief state (not encodable as three Boolean membership flags without loss). Both must HOLD and never be automatically coerced into a solution. Other controls are already expressible under the previous grammar.

## Source separation

| Component | Responsibility |
|---|---|
| `tasks.py` | Evaluator-owned, integer-mask target definitions and domain descriptions; never included wholesale in model prompts |
| `transfer.py` | Classical grammar search, dev-only probes, deferred finite-domain audit and trusted runtime comparison |
| `transfer_llm.py` | Fixed loopback Ollama transport, generic AST JSON validation and source-owned translation |
| `test_transfer.py` | Adversarial and loopback-*stub* integration tests; transport fixture is **not** an LLM |
| `run.py` | Offline benchmark or explicit real Ollama direct-inference experiment; receives model name only from operator |

### Known experimental limitations

- **The domain adapters are human-designed.** Every admissible task has exactly three binary features and two set-valued input roles preassigned. This tests transfer of *representation and typed-expression selection*, not open-ended extraction of mathematical structure from arbitrary language.
- **The same developers wrote all task briefs and expected functions**. These are not independently authored blind problems, and success is not proof of generalizable machine understanding.
- The full 64-input check contains the six development inputs. It is exhaustive for the tiny finite domain but not statistically independent. The later test is deliberately delayed until the candidate is frozen, with no post-audit retries.
- Mathematical inversion for the endorsement register means **not currently endorsed** in a finite closed-world ledger; it does **not** equate unknown with false. The separate open-world, ternary task is rejected.
- Passing verification means only this tiny semantic mapping was correct on its finite synthetic data. It does not grant real access, alter inventories, make factual claims about beliefs or validate real-world policies.
- The prior fixed runtime runs trusted static Python in `python -I` subprocess: it is **not** an OS sandbox for arbitrary model-written code. Never execute model-supplied Python.
- Offline tests cannot establish real model use; only a separate Ollama GitHub Actions job can, with its explicit inference receipts. Ollama's CI installer is unpinned research infrastructure, not a production supply-chain setup.
- Independent oracle call ceilings are comparable across source-only approaches but model calls, tokens and elapsed time are separately reported; no claims of matched compute or causal superiority.

## Reproduce

```sh
cd experiments/thought-024
python -m unittest -v test_transfer.py
python benchmark.py
# Only on a machine with a model already installed and Ollama running:
python run.py --backend ollama --model qwen2.5:3b --rounds 2 \
  --tasks permits_reverse,missing_supplies,not_endorsed,expire_names,cross_category_threshold,open_world_truth \
  --output live-results.json
```

### Scientific next step

Test on independently authored problems with different cardinalities, type systems, real-world uncertainty, composition of multiple primitives, and externally verified outcomes. Then compare real model vs static classical, mixed-initiative, and a language-only baseline under matched token/time and oracle budgets. Do not merge any prototype code without reviewing the stacked PR chain and source isolation.
