# MOTIF THOUGHT-023 — Grammar Gardener (review-only)

**Status:** Experimental, source-owned. THOUGHT-023 is stacked on THOUGHT-022. No grammar or algorithm installed; no model-written Python executed, no deployment, no merge, no PEN authority.

## Research question

Can MOTIF detect that a finite reasoning vocabulary is *inexpressive*, accept an untrusted LLM-suggested **new vocabulary primitive**, and independently demonstrate that it strictly expands the functions MOTIF can represent? Can the evaluator compare a minimal alternative, guard against useless additions, and retain a reviewable candidate rather than simply believing the model?

The old language has set variables `state.on = A` and `arrival.toggles = B`, with only binary union and difference. Exhaustive closure of all 3-bit set transitions under that grammar has **8 distinct Boolean functions**. In particular every expression maps empty A and B to empty, so it cannot express bitwise inversion, where `invert(∅)=U`.

THOUGHT-022's *real* Qwen2.5:3B grammar advisor suggested `constant_universe` in [GitHub Actions run 42397463098](https://github.com/the-static-collective/MOTIF/actions/runs/42397463098). **The default offline experiment replays that previously recorded recommendation** as untrusted data. It is **not** a fresh LLM call. A separate optional Ollama job can make a new genuine model call, independently recorded and checked.

## New bounded vocabulary laboratory

Only four source-owner-declared mutually exclusive alternatives can be compared:

| Extension | Extra typed construct | Expressive functions (old: 8) | Can synthesize invert? | Extra implementation concept |
|---|---|---:|---|---|
| `none` | none | 8 | No | Baseline |
| `empty_constant` | `{"ref":"empty"}` | 8 | No | Negative control: redundant |
| `universe_constant` | `{"ref":"universe"}` = {red, blue, green} | **16** | **Yes** | New constant; reuse difference |
| `set_complement` | `{"op":"complement","args":[X]}` | **16** | **Yes** | New unary operator |

The finite grammar can express all **16 Boolean functions of two Boolean inputs**, evaluated independently at each color bit. This is not unrestricted set theory or evidence of more general algorithm intelligence.

The *model cannot define an extension*: it can nominate only the previously declared `constant_universe`, `complement`, or `unknown` option through a strict code-free JSON schema. The source-owned evaluator decides whether the extension is useful. It does not promote an addition to any production grammar.

## Experiment chronology

1. Use THOUGHT-022's preexisting CEGIS to demonstrate an **observed development witness**: `A=∅, B=∅`, independently required inversion output `U` (mask 7), impossible under the old grammar. No held-out test is shown to the model.
2. Receive a model advice label. Validate exact JSON shape, allowlisted token, and textual rationale; reject extra keys, arbitrary expressions, code, URLs or effects.
3. Construct a **temporary finite candidate language**, enumerate every distinct semantic signature under depth ≤4 and AST size ≤19; preserve old signatures and count genuinely new functions.
4. Repeat development CEGIS with a strict oracle-query limit and freeze a candidate expression. Source-owner code uses independent integer bitmask target semantics.
5. Audit the candidate on all 64 3-bit input pairs with a separate frozenset AST interpreter **and** execute a trusted fixed Python template in a separate subprocess; compare every output to the independent bitmask specification. Python `-I` is not an OS security sandbox; no model-provided Python is accepted into the template.
6. **After** choosing the extension, measure a source-owner-designed transfer family: inverted A, NAND(A,B), NOR(A,B), and the all-on constant. These four are *not* genuinely externally blind tasks; they are an ablation of finite expressivity, not a model creativity benchmark.
7. Report all alternatives including a redundant `empty_constant` negative control; retain `CANDIDATE_GRAMMAR_FOR_HUMAN_REVIEW_NOT_INSTALLED` only for an independently verified candidate. Never automatically install.

## Measured offline result

`constant_universe` grows the closure **8→16 distinct semantic functions** (+8) and synthesizes `U−A` (3 AST nodes) using 2 development oracle probes; it passes 64/64 frozen bitmask checks, 64/64 independent frozenset checks, 64/64 executed fixed-template checks. It also makes all four transfer-family functions expressible. The equally expressive `complement` alternative builds `complement(A)` (2 AST nodes) but adds an operation rather than a constant; the experiment **does not establish which representation is globally better**. The `empty_constant` negative control adds no new semantic functions and correctly returns HOLD.

The known inversion task, a very small fixed grammar and a simple finite test distribution prevent strong generalization. Closure measurements and the exact failure witness are inspectable, but they do **not** demonstrate independent model invention, performance gains on realistic problems, model-weight improvement, novel mathematics, or generalized self-directed evolution.

## Reproduce

```bash
cd experiments/thought-023
python -m unittest -v test_gardener.py
python gardener_benchmark.py
python gardener_cli.py --backend offline --output reproduced-offline.json
```

Explicitly with a running, locally installed Ollama server/model (no automatic install in the CLI):

```bash
python gardener_cli.py --backend ollama --model qwen2.5:3b --output live-results.json
```

A failed LLM output is recorded as HOLD rather than replaced by the archived suggestion. The GitHub Actions live-model job is separate from the offline tests and uses a research-only unpinned Ollama installation, which is a supply-chain limitation. The real model fingerprint from the daemon is self-reported metadata, not a signed identity.

## Next falsification boundary

The next meaningful trial must use independently authored problems in a new state domain (not three colors or simple Boolean switches), a fresh held-out evaluator, and matched token/time budgets. Compare automatically extended vocabularies with an explicit human-designed basis, finite classical synthesis, and an LLM with no grammar advice. A true adaptive grammar should generalize, not simply add a constant already known to solve a familiar puzzle.
