# MOTIF-026F — RESULT: Semantic hints now enter native Question Machine; relevance is the missing gate

Research output, November 5, 2026. The original test and first 25 case gold labels were frozen in PRECOMMIT.md and frozen_cases.py (Git blob 329911abfbccf7ae62163ec68aad48846224963c) before actual 026F model execution.

## What is now wired together

A public-safe synthetic operator note -> 025F native-first lexical filter -> **real locally cached FLAN-T5-small ENCODER** if native cannot identify a gate -> 026F typed semantic-to-test bridge -> **existing 022F** question registry, independent synthetic calibration and permissions -> **original 016 LivingForest** expectation-driven question choice -> independent synthetic RUN receipt. The original plan is preserved. The model supplies a proposed category, NOT a fact, new instrument, verified source or permission.

The bridge uses a structural SidecarRun wrapper. It DOES NOT represent an actual 021F text Chorus completion. It creates a typed suggestion from an untrusted encoder label. Only predeclared finite hypothetical sensors can pass downstream: FOOD maps to FOOD_SERVICE_GATE; AUDIO maps to an already-present duplicate, correctly rejected; ACCESS and STAFF have no synthetic sensor and remain HOLD. Nothing is installed into JAR;VIS production, no live tool is executed, no contact or payment initiated.

## Actual weight-bearing run

Successful preliminary real-model workflow: https://github.com/the-static-collective/MOTIF/actions/runs/42063381421

- Actual Google FLAN-T5-small 77M encoder, public SHA 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab, pinned weights downloaded to ephemeral GitHub Actions runner only, then inferred offline.
- 25 newly frozen toy notes: 5 FOOD, 5 AUDIO, 5 ACCESS, 5 STAFF, 5 NONE. Author-composed synthetic alternate phrasings, not real-world observations or an independently produced NLP dataset.
- Same 12 original 025F labeled references supplied to both T5 and classical TF-IDF; same native prefilter and same source-reviewed 022F/016 machinery.
- Actual T5 encoder time **0.4153 seconds for 25 query embeddings plus reference cache build**, excluding model load and all other overhead on the GitHub CPU. This is not a measurement of the user's Mac, battery, actual event delay, or welfare.

### Head-to-head comparison

| Strategy | Correct synthetic missing-gate label | False gate offered on a no-problem note | 022F-admitted questions relevant to note | Irrelevant questions admitted |
| --- | ---: | ---: | ---: | ---: |
| Native fixed grammar (no T5) | 5 / 25 | 0 | 0 | 0 |
| Native + classical TF-IDF | 14 / 25 | 2 | 3 | 1 |
| **Native + real T5 encoder** | **19 / 25** | **2** | **4** | **1** |

The native rule's weak 5/25 result is partly **by construction**: this tiny case set deliberately uses synonyms outside the fixed vocabulary. The classical TF-IDF control has exactly the same reference examples as the T5 model; a stronger independently designed semantic or domain-rule baseline could erase this difference. The 19/25 result is not calibrated model accuracy in other domains.

One concrete useful simulated case: the note 'Nobody has agreed to monitor temperatures at the buffet' was categorized FOOD by T5 while the classical TF-IDF version categorized it AUDIO. The resulting registered FOOD_SERVICE_GATE passed independent artificial calibration, and the **real 016 Forest** increased its modeled four-world end-state classification from **0.50 to 1.00**, with a separately observed fabricated run result. This is NOT a real meal, a real food service approval, or evidence of a safer event.

### The important failure

The note 'We are just revising the invitation artwork' has gold category NONE. T5 wrongly classified it as FOOD; the existing 022F Source/Question Machine allowed the synthetic FOOD_SERVICE_GATE. Why? Because the sensor is a valid information source in that artificial four-world universe. **That does not establish that the test is relevant to this particular human note.**

This is a real boundary discovery: **independent validation of a sensor is not independent validation of its applicability.** A text-to-test bridge needs a separate note-to-question relevance witness before even a verified sensor is considered a useful response to that note.

Another T5 no-problem note generated an unsupported STAFF gate, which was held because no registered test exists. Two STAFF situations were missed entirely. AUDIO requests correctly turned into HOLD_DUPLICATE_OR_EXISTING_QUESTION rather than repeated evidence; ACCESS/STAFF currently HOLD_NO_REGISTERED_TEST_FOR_GATE.

## We asked MOTIF again: what is T5 best used for, if anything?

The native method portfolio was declared before this 026F result:
- NO_T5 for all automatic decisions
- SEMANTIC_GAP_SCOUT (T5 encoder suggesting a low-authority candidate missing gate)
- QUESTION_CARTRIDGE_FINDER (mapped registered test but never invented)
- SOURCE_SIMILARITY_INDEX and REPRESENTATION_DRIFT_ALARM (unverified future research)
- DECODER_OBSERVER_CRITIC_HYPEMAN (negative earlier evidence)

Under its original conservative no-false-alarm rule, **MOTIF returned NO_T5**, notwithstanding the promising 19/25 classifier score. Its measured increment was +5 correct labels over the best same-reference classical comparator, and +1 relevant synthetic question, but there were **two false positive gate hints and one irrelevant admitted test**. The conservative small-sample lower bound for the accuracy gain was **-0.28955**, not a demonstrated reliable real-world advantage. True opportunity loss was not measured; it returned HOLD_NOT_CALIBRATED.

The appropriate research-only interpretation is narrower: **T5's silent encoder may be useful as a semantic retrieval scout for unfamiliar phrasing, with independent note-to-question relevance review and a no-model default.** Do not deploy it as a permission decider, event producer, statement of fact, grant advisor, or automatic physical sensor selector.

## What the native postmortem asked next

A separate, explicitly POSTHOC diagnostic now records the false-positive question with its case ID and asks:

> What independent note-to-question relevance witness can reject a false-positive meal inquiry without suppressing truly useful new questions or allowing a second correlated language model to certify the first?

Candidate future tests: source quote or human-confirmed relevance; prospectively evaluated abstention thresholds on NEW cases; native semantic affordance signatures where available. These are improvement proposals, not passed experiments or automatic changes to the pipeline. The original 25-case results are preserved untouched.

## Scientific boundaries

Everything in these results is synthetic, including the gold note categories, all food/audio tests, sensor calibration, future source observations and any expected accuracy figures. One small model, hand-written examples, co-designed native rules and no independent human corpus cannot establish out-of-domain transfer. Regex-based privacy rejection is incomplete and real private records were never used. No model or source certificate in this branch grants authority. A simulated planned action is not an executable real-world act.

**Current verdict: Wire-in complete in an isolated MOTIF research branch; NO_T5 for autonomous decisions; T5 as a held semantic hint remains promising, not proven or deployed.**
