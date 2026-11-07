# THOUGHT-020 — A development critic for a real generative model

**Status:** Experimental source branch stacked on THOUGHT-019. No merge, deployment, live-service change, authority delegation or self-installed patch.

## Research question

A real Qwen2.5 1.5B model made three direct, grammar-valid generation calls in THOUGHT-019, but repeated the refuted `GROW` program every time. Can a deterministic **semantic novelty critic**, operating exclusively on already observed development failures, help that same model spend its next call on a meaningfully different candidate? What does that intervention cost relative to the original baseline?

## Experimental design

`critic.py` wraps the **actual source-owned `DirectLocalLLM`** transport from THOUGHT-019 and runs the **actual THOUGHT-018 ResearchDirector**, which in turn uses the independent THOUGHT-017 bitmask evaluator and the typed fixed-template executable graph solver. It does not define a second oracle or decide ground truth.

Two arms request the *same explicit installed model*, the same brief, the same generation limit, temperature and task family:

- **Control**: source-owned direct model, original development feedback, with source-owner hypothesis-survivor name labels removed to avoid revealing `FLIP`.
- **Critic**: same gateway and feedback, but when a newly generated model expression is **semantically identical on the entire 8×8 finite input domain** to a previously refuted candidate, the critic **does not spend another oracle probe**. It records the duplicate as a failed model call and asks the model again, giving it only its earlier development counterexample, within the original total model-call budget.

The critic does **not** replace the proposal with a correct expression, use evaluator labels from the frozen audit, name the correct mechanism, give arbitrary code, or install anything. Its semantic signature is computed by executing the submitted typed expression (not calling the independent target oracle). Identical syntax with different semantics is not conflated; distinct syntax with identical semantics is recognized.

The result can be a failure. If the model repeats the same semantics until its allocation is exhausted, the system returns HOLD with no selected mechanism. A favorable test run cannot establish general self-improvement: the domain is finite and synthetic, the task is familiar to the LLM, and prompt lengths/time differ between arms.

## Reproduce tests

```sh
cd experiments/thought-020
python -m unittest -v test_critic.py
# the actual source-owner regressions
cd ../thought-019 && python -m unittest -v test_direct_model.py
```

A real locally provisioned Ollama model may be run by the operator:

```sh
cd experiments/thought-020
python run.py --model qwen2.5:1.5b --rounds 3 --timeout 120 --output critic-vs-control.json
```

`run.py` uses the fixed `127.0.0.1:11434` local endpoint. The model is not downloaded or installed by this script. Its source does not accept custom URLs or model-supplied commands. GitHub Actions optionally downloads the existing open-weight research model in an ephemeral runner and runs the same comparison. Each arm starts from a clean model-conversation context. The output records actual HTTP inference receipts (not raw private prompts), semantic replay count, number of genuine oracle probes, test disposition and separate token/time counters. Real CI outcomes, including failure, should be inspected before citing.

## Falsifiers and limitations

- If critic and control both return HOLD, do **not** call this an improvement.
- If a critic succeeds because the prompt leaks hidden answers, the trial is invalid. The filter refuses unexpected feedback fields and strips survivor labels.
- If the model fails to return valid typed JSON, the director holds. No synthetic substitution.
- If the critic detects a semantically repeated candidate, it can request a new model proposal but **cannot create one**.
- If the critic consumes extra model calls, it must stay within the *same maximum generations* as the control; actual prompt tokens and CPU time remain separately recorded and may differ.
- Any selected source patch is `PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED`; the graph oracle, frozen audit, stress and PEN gates are unchanged.
- The previous 019 public model install script is unpinned. This CI research environment is not a trusted supply-chain/prod deployment or security sandbox.

The next scientifically stronger experiment should add independently authored test families and matched multi-seed repetitions, including other local models and grammar-deficient tasks. A single small-model demonstration is not evidence of generalized self-improvement.
