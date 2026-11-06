# MOTIF THOUGHT-018 — The Model Research Director

**Stage:** executable local synthetic research prototype, stacked on THOUGHT-017. The model can propose a typed mechanism and a discriminating test. An independent director can reject the proposed test, choose a more informative question, send development feedback back to the model, verify candidate behavior against a separate oracle, and prepare a human-review-only result. The underlying model is not re-trained by this workflow and no production source is modified.

## Research hypothesis

Can a reasoning engine **direct experiments involving its own model** instead of accepting model answers as conclusions? Can a model propose **both a mechanism and how to test it**, then see experimentally observed failures and reconsider? Can the engine preserve independent testing and measure whether active inquiry buys information over a fixed-control strategy?

## Actual mechanism

```
Human brief (task data)
    -> ACTUAL model inference: trained Naive Bayes classifier ranks a finite set
       of five human-reviewed typed transition mechanisms
    -> model proposes one typed AST + an optional proposed diagnostic test
    -> validation of EXACT model contract and THOUGHT-017's trusted AST grammar
    -> MOTIF inquiry director searches for an information-rich, unasked probe
       (may reject the model's proposed probe as insufficiently discriminating)
    -> independent integer-bitmask evaluator grades what the tested operation does
    -> model receives development-only observations and surviving hypotheses
    -> model can reconsider, propose a different candidate; finite round budget
    -> selected candidate frozen; complete 64-case truth table checked
    -> source-owned THOUGHT-017 fixed-template Python candidate actually executes
    -> source-owner independent route oracle checks real paths on 8 dev, 4 safety,
       60 frozen synthetic audit, 80 stress graph cases
    -> HOLD or PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED (no install/commit)
```

The model is **not** the oracle, cannot choose the target truth function, cannot alter the audit cases, cannot manufacture authority, and has no ability to run model-supplied source code. Only source-reviewed typed ASTs are compiled into a fixed Python template, as in THOUGHT-017.

### Model backends

- **Default:** actually trained offline multinomial Naive Bayes *ranker*. It learns from 15 human-authored text/mechanism examples and selects between `KEEP`, `GROW`, `DRAIN`, `REPLACE`, `FLIP` templates. These candidates are not new algorithms discovered by the model. The model is invoked on each proposal and development feedback changes which candidate it proposes next. It does **not** modify its statistical weights in this experiment.
- **Optional:** a genuinely generative **operator-provisioned local Ollama model** can return a strict JSON object containing a new typed AST and a proposed probe. It can compose available `union` and `difference` operators, but never submit Python code or supply tool calls. The only endpoint is `http://127.0.0.1:11434/api/generate`, no proxy/redirect or model-specified endpoint. An HTTP transport stub was tested; **no actual Ollama model was installed or run in the default trial**. Missing models result in HOLD.

### Tests are not model-defined truth

One test suggestion from the model is checked against all active candidate hypotheses. If it cannot separate them as well as the director's best available probe, the director defers that suggestion. For the synthetic demo, the model initially picks `GROW` from an ambiguous brief. The director selects a more informative test and the independent oracle refutes `GROW`. The feedback reduces the candidate set to `FLIP`; the model then proposes `FLIP`, which independently passes exhaustive and graph tests. Its later answer is not accepted merely because the development director had one surviving candidate.

We independently run **five task types** through the finite truth-table simulator, comparing adaptive query selection to a predeclared task-agnostic sequence. This is a *query count comparison*, not CPU timing, energy saving, generalization, or a proof of intelligence. Fixed control was designed by the same developers, not an independent state-of-the-art search baseline.

### Scientific limitations

- The independent XOR oracle is a conventional, correct algebraic specification; the testing environment is synthetic and author-designed. The source-owner THOUGHT-017 graph oracle validates the actual path outcomes, including history-dependent switch behavior, but these fixtures come from the same project.
- The model already has `FLIP` in its finite human-designed candidate grammar. It **does not invent new operators** or solve an unfamiliar open-world problem in this demonstration. The optional LLM can compose AST nodes but has not been validated with a real model.
- Query information utility measures how well the query partitions the **known finite hypothesis space**, not usefulness of a real-world research question. Allowing the model to see the surviving set after each dev observation is appropriate developer feedback; the **frozen graph audit is not passed into the model**.
- The held-out audit graph seeds are fixed and only evaluated after selection, but not independently authored or externally blind. Never claim self-improving general intelligence, model consciousness, breakthrough mathematics, or field utility based on these numbers.
- SHA-256 receipts are reproducible fingerprints, not signatures or independent evidence. There is no immutable external event journal, feedback persistence, operator authentication, real developer OS sandbox, authenticated model identity or deployment authority.
- Python `-I` provides interpreter isolation but not OS-level security. Arbitrary code must never be executed through this lab.

## Reproduction

At repo root:

```sh
cd experiments/thought-018
python -m unittest -v test_director.py
python benchmark.py > experiment-results.json
python model_probe.py --backend tiny
```

**Optional** once an Ollama daemon and model are deliberately installed on the operator's machine:

```sh
python model_probe.py --backend ollama --model YOUR_INSTALLED_MODEL
```

The optional command uses synthetic descriptions only. It may HOLD if the daemon or model is absent, invalid, times out, or proposes an unsupported AST. No model is automatically installed or downloaded.

GitHub Actions runs the 018 unit tests, benchmark and 017 regression suite. The attached results are generated by this local experiment, not independently re-run CI evidence until Actions confirms it.

## Next research frontier

The missing test is *transfer*: can a model propose a new typed primitive for a distinct, independently authored domain, write useful discriminating tests without getting the evaluator's answers, and produce an improvement that holds against strong classical synthesis baselines at an equal compute budget? Hold all modifications for explicit human review. A proper future runtime for unrestricted generated code must have OS-enforced isolation and no external network or writable project mounts.

**Law:** model proposal ≠ oracle truth; inquiry ≠ independent witness; test passed ≠ installed; model-selected experiment ≠ authority.
