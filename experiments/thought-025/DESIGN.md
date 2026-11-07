# MOTIF THOUGHT-025 — The Abstraction Discoverer

**Status:** experimental, synthetic, review-only. This work proposes an abstract-language bridge. It does **not** install a general natural-language reasoner.

## Research question

Can a separately run generative language model read ordinary descriptions of two domain-specific lists and propose **both** their abstract input-variable bindings **and** a finite set-algebra expression, without being handed a prewired domain-to-mathematics adapter? Can MOTIF independently test whether that representation preserves the developer-authored problem semantics?

## Actual architecture

1. `specimens.py`: evaluator-owned 10 synthetic stories, including two deliberately reversed minimal-pair scenarios and two negative controls. Ground-truth `policy` and `roles` are never present in the model prompt. Only story, opaque input field IDs, field descriptions, and closed three-category universe are public.
2. `abstraction_llm.py`: local Ollama inference through THOUGHT-019's `DirectLocalLLM` fixed loopback transport. The LLM proposes `bindings.current`, `bindings.event`, and a typed syntax tree over `state.on`, `arrival.toggles`, and `universe` using `union` and `difference`. No arbitrary source/text can execute.
3. `abstraction.py`: strict binding (both fields used exactly once) + AST validation. Independent evaluator-owned integer-bitmask oracle runs only on development inputs. If a proposal fails, only the witnessed counterexample is fed back, and at most one further generative attempt occurs.
4. After development selection is frozen, a complete 64-input independent truth-table audit checks it. If it passes, a separate **fixed-template Python implementation** of the candidate is executed and checked against the oracle across all 64 inputs. Any failure HOLDs.
5. `classical_without_language` is a strong **oracle-aided** control: enumerate all 16 finite functions with either variable binding, choose discriminating oracle queries, and freeze the candidate. It does not claim to infer semantics from language; it receives labelled oracle examples and hence cannot be compared directly to LLM zero-shot comprehension.

Two stories are evaluator-declared unrepresentable or underdetermined. They HOLD before model invocation. This is an **evaluator-owned semantic gate**, not a claim that the model independently recognized ambiguity.

### Falsification

A reversed-description pair is used to ensure fixed first-field binding is not silently credited as correct. A mapping can pass a handful of development checks and still fail the 64-input audit. Changed syntax with identical mathematical behavior does not count as a different solution. The model is never given expected functions, policies, answer expressions, or held-out labels.

### Baselines / limits

- Source-owned classical oracle-assisted search is tiny and fast. It can identify all eight Boolean expressible tasks with two development oracle calls per case. It has access to an oracle, not to human-language meaning.
- Real LLM trial, if provisioned, uses Qwen2.5 3B under Ollama in **ephemeral GitHub Actions**, max two generations per task, max four unique development oracle examples, then a frozen 64-cell semantic and fixed Python check. Four category-flag semantic roles are *not* assigned by an adapter: both generic variable bindings originate from the LLM.
- This is not blind/independent dataset construction. Stories, truth policies, and evaluator were authored for the experiment. Three-bit closed-world features and a limited DSL are artificial. No evidence of unrestricted abstraction discovery or real-world state fidelity.
- The existing abstract syntax is supplied by developers. A model that selects correct bindings/operators within it has demonstrated **bounded semantic translation**, not novel mathematics.
- Tiny closed world does not license conversion of open-world truth into Boolean absence. Negative controls correctly HOLD only because evaluator declared those tasks nonboolean/underspecified.
- Current CI Ollama install uses the unpinned official installation script in a disposable research runner; this is a supply-chain limitation, not a production deployment design.
- GitHub workflows can run after push. Offline HTTP fixtures are **not** a real LLM. No LLM success claims until actual model receipts and CI results are checked. No secrets or user/private project content are sent to inference.

## Reproduce

```bash
cd experiments/thought-025
python -m unittest -v test_abstraction.py
python benchmark.py
# On a host with Ollama running and qwen2.5:3b explicitly downloaded:
python abstraction_cli.py --backend ollama --model qwen2.5:3b --max-calls 2 \
  --output real-model-results.json
```

The project only emits review reports and receipts. All outputs have `installed:false`, `external_authority:NONE`; no GitHub merge, PEN crossing, deployment, email or database write results from a model proposal.

## First direct Qwen observation and compiler iteration

The first real Qwen2.5:3B CI run (GitHub Actions `42415732280`) made **six** genuine generation calls. All six returned syntactically valid outer JSON but failed the original strict core AST validator (`GrammarError`); therefore **zero model proposals advanced to development oracle tests** and **zero abstractions were validated**. Both workflow jobs passed because handling invalid proposals as HOLD is an expected experimental outcome. Those runs used 2,356 prompt tokens and 672 response tokens in total (server-reported). The two nonBoolean/underspecified controls were explicitly held by the evaluator without LLM calls.

This is useful negative evidence: the model-to-core-grammar interface itself was a bottleneck. The follow-up source-only change adds a **reviewed surface-math compiler**: `intersection`, `xor` / `symmetric_difference`, and `complement` lower into the already-licensed `union`/`difference` AST, then the existing core validator applies its depth/node bounds. This does not expand the underlying 16-function Boolean semantics, does not accept model-written Python, and does not grant new authority. The prompt now contains a structural example using deliberately *reversed* abstract field bindings, identified as an example rather than the answer. Additional bounded diagnostics record only proposed operator/referent labels, not raw model text. Any new real-model outcome is a distinct run and should be reported separately.
