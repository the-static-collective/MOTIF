# MOTIF THOUGHT-014 — Language as a Thought Space, MOTIF as Model Developer/Tester

**Status:** Python 3.11+ *standard-library* local synthetic research, stacked on THOUGHT-013. This is a candidate laboratory, not autonomous self-modifying code, a hosted service, a model release, an authenticated human-language understanding system, or production JAR;VIS integration. **Nothing is automatically merged, activated, deployed, exported, or granted PEN authority.**

## The user proposal

Let MOTIF think with human utterances as a native reasoning instrument, *and* allow MOTIF to **run a language model as a component of its own development tests**. The same system that makes hypotheses can request model interpretations, test proposed revisions, analyze failures, and retain a reviewable experiment record. The independent test harness—not the model's own confidence—decides whether a candidate passes a controlled experiment.

### Source-owned inspirations

- Full Measure World Layer `src/lib/humanTerminal/interpret.ts`, `types.ts`, `operator.ts` and Human Terminal v0.1 design. Human talk becomes a **known typed intention** before an allowed local operation; unknown phrases don't become shell commands. Full Measure's authority/runtime isn't copied into MOTIF.
- MOTIF THOUGHT-013 `human_talk.py` remains the deterministic baseline and source-ID-bound validator. THOUGHT-013 `InquiryCycle` remains the classical question-planning evaluator. THOUGHT-007/008 continue to own idea identity and graph evidence.
- The user has suggested lightweight specialized language models as observer/critic/translator; this is an experimental optional capability rather than a requirement for every question.

## Two model backends, with precise claims

1. **`TinyTextModel`:** an *actual trained* offline supervised multinomial word/bigram Naive Bayes **classifier**, not a generative LLM or T5. Training examples are fictional and tiny. It predicts candidate speech acts, ranks candidate groups, and feeds a bounded model-driven development loop. This backend runs without extra packages or an external service, including in CI.
2. **`OllamaLocalModel`:** an explicitly opted-in model **client** to a previously running model at fixed `127.0.0.1:11434/api/generate`. It can ask a local LLM to propose a speech act or a **code-free prefix-rule candidate**. Every reply must parse as bounded JSON. The model cannot choose another host, run tools, change code, grant authority, create concept IDs or bypass the test harness. The experiment does not download a model or start Ollama. The CI transport test talks to a deliberately fake local daemon and **does not constitute a real LLM inference test**.

**No local Ollama installation/model is provisioned in the execution environment of the initial experiment.** Actual 014 demonstration and benchmark use the offline trained classifier; the real LLM connection remains an available, unexercised option. Never count stub HTTP tests as live LLM work.

## Actual executable dataflow

```text
operator-provided human utterance + exact manifestation IDs
       |
       v
THOUGHT-013 conservative interpreter (always first)
       | if UNKNOWN and not an effect request
       v
optional MOTIF-managed model invocation (tiny or local Ollama)
       |
       v
bounded speech-act proposal → fixed schema + existing ID validation
       |
       +── HOLD if unknown/malformed/effectful/IDs mismatched
       |
       v
PENCIL utterance with immutable ID, original source fingerprint,
claimed interpretation origin, preserved alternative, no new graph facts
       |
       v
MOTIF's Dev Lab requests candidate **non-executable rules**
       |
       v
train-only proposal → development tests → feedback → reconsider
       |
       v
one frozen audit after proposal selection → human review packet
       |
       +── NEVER auto-install, edit code, commit PEN or call third parties
```

**Human talk is a reasoning substrate, not automatically a verified source.** A person can say "I wonder whether…", MOTIF can record a precise proposed speech act, use that to choose a question, and ask "What would disprove this?". It does not pretend that a generative model's narration is its private reasoning or evidence for an actual relationship. When multiple interpretations remain possible, the alternatives remain inspectable.

## Running the model as the developer and test subject

`SelfDevelopmentLab.run(max_rounds=4)` is a bounded **proposal → test → critique → next proposal** cycle. The `TinyModelDeveloper` uses an actually trained classifier to evaluate source training phrases and induce concrete typed `prefix` patterns; the optional `OllamaDeveloper` asks the local LLM for one JSON candidate per round. Neither can write executable code or change the evaluator. Candidate syntax is a five-field strict DSL:

```json
{"schema":"motif.thought014.rule-candidate.v1", "pattern":"i wonder whether", "speech_act":"EXPLORE_POSSIBILITY", "match":"prefix", "origin":"tiny-supervised-language-model"}
```

The evaluator rejects unknown verbs, code, wildcard patterns, invalid punctuation, weak two-word matches, unsafe action requests, unsupported act classes, regressions on development examples or failures on adversarial safety controls. Existing recognized THOUGHT-013 language patterns keep precedence. Exact selected concept IDs must survive. The model sees training records and development feedback, **not the held-out audit labels**. After the model finishes proposing, a separate audit measures its selected candidate once. The audit is *developer-authored synthetic data*—not independent third-party blind validation. Candidate rules stay `CANDIDATE_FOR_HUMAN_REVIEW_NOT_INSTALLED` even if all conditions pass.

`reasoning_policy_trial()` separately asks MOTIF to evaluate **two bounded inquiry strategies** (`decision` vs `world`) on eight developer-worlds; it selects by number of correct modeled decisions, then question count, and reports a separate eight-world audit. This proves that the system can benchmark a reasoning strategy and prefer a lower-cost choice **inside a fully specified toy world**. It does not let a model decide its own testing labels, edit Python, or claim real-world correctness.

## First local measurements (synthetic, author-designed)

- 26 local unit/integration tests, including a real localhost HTTP transport to a fake inference daemon, malicious candidate rejection, reproducible source provenance, training/development/audit partitioning, and no geometry-to-fact promotion.
- On 16 development phrases, recognized speech-act accuracy increases from **8/16 to 15/16** with four staged prefix candidates; safety controls **8/8** remain held/unknown. On 15 frozen-after-selection audit phrases, **7/15 → 14/15**. These are tiny deliberate pattern variations, not general conversational competence.
- Reasoning strategy on eight dev worlds: `decision` and `world` each resolve **8/8**, but `decision` asks **12** total questions versus **20**; the eight audit worlds repeat that comparison. No geometric accuracy gain demonstrated.
- Four model candidate rounds, four model critique receipts, twelve tiny-model inference calls for candidate scoring; the model also interprets an unknown human phrase via the validated membrane. **Zero real LLM calls in the initial experiment.**

## Reproduce without any LLM installation

```bash
cd experiments/thought-014
python -m unittest -v test_thought014.py
python benchmark.py > benchmark-results.json
python demo.py
python model_probe.py --backend tiny --dev-test
```

To **explicitly try a genuinely generative local model** on a machine with a running Ollama model already installed (operator controls the name):

```bash
python model_probe.py --backend ollama --model YOUR_LOCAL_MODEL_NAME \
  --utterance 'I wonder whether these are connected' --dev-test
```

That will use the fixed local endpoint only. It can fail with HOLD if the model is absent, times out, replies with invalid JSON, or proposes an unsafe rule. There is no automatic web/API usage, provider login, private-data upload or model download in the code. The explicit local model might independently have configuration outside this Python prototype; operators must review that before using private information.

## Acceptance, falsification and follow-up

**Mandatory:** no model-selected concept binding, no unknown-intent execution, no model-to-PEN crossing, no new asserted edge from proximity or language-model confidence, every candidate tested before staging, no hidden audit labels in proposal prompts, and no self-update of production runtime. Fail-closed under missing model/invalid response. Changed source graph requires a fresh experiment rather than carrying stale semantics.

**Still unproven:** T5/LLM improves abstraction, model self-test produces genuinely novel executable algorithms, useful spontaneous linguistic distinctions, transferable semantics on human conversations, long-horizon self-correction, lower real-world mistakes, and deployment value. Compare against stronger source-only and conventional LLM baselines with human-reviewed, truly unseen prompts; fix evaluation tasks and outcomes in advance. A future autonomous coding worker should use ephemeral worktrees, strict test sandboxes, signed review receipts and explicit human merge approval; this experiment deliberately does not execute model-written code.

**Proposed THOUGHT-015:** give MOTIF limited model-generated **test case proposals** and **source-change proposals**, route each through a disposable test workspace + independent untouched holdout + counterexample search, retain auditable patch suggestions, and require operator approval before any repository write. The model gets *agency to suggest experiments*, not authority to certify itself.
