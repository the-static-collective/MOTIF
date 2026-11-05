# MOTIF-026F — PRECOMMIT: Tiny semantic sensor into native Question Machine

Question: Having discovered that FLAN-T5-small's decoder performs poorly, can its passive encoder contribute a missing assumption that native MOTIF can independently review? If yes, which restricted job should T5 have, if any?

## Candidate methods (NO_T5 is always a competitor)

- NO_T5: native keyword gate identification, native 022F validation and original 016 Forest.
- CLASSICAL_TFIDF: same 12 source examples as the encoder, classical word/bigram/character nearest neighbor, then the exact same native review and planning.
- REAL_T5: one cached real FLAN-T5-small encoder; source similarity nominates FOOD, AUDIO, ACCESS, STAFF, or NONE; native 022F and 016 handle every typed question thereafter.
- Decoder Observer/Critic/Hypeman: rejected previously on 025F due poor performance; not rerun here.
- Semantic source indexing and representation-drift detection: SPECULATIVE RESEARCH ROLES, not tested in this experiment.

## Source and safety rules

1. Every input is a synthetic, public-safe operator projection. Simple privacy filters do not guarantee that genuine private material would be safe.
2. Existing native lexical recognition gets first refusal and avoids loading a model for clear cases.
3. T5 encoder outputs are unverified similarity labels, NOT facts, permission, evidence or event decisions.
4. A trusted structural adapter maps FOOD to the predeclared simulated FOOD_SERVICE_GATE. AUDIO maps to REPEAT_AUDIO_TEST (duplicate to already-present AUDIO_PATH_TEST). ACCESS and STAFF have no registered instrument in this toy, hence HOLD. NONE stays HOLD.
5. Actual 022F independently checks registered test names, authorization flags, duplicate source, and synthetic calibration. Actual 016 LivingForest independently selects the revised plan. A separate simulated oracle supplies run observations. The structural adapter is NOT an actual 021F Chorus response; it cannot grant execution.
6. Neither fake simulation nor model output may change any person, public event, permit, application, source record, or original native plan.

## Prospective evaluation

Research-author froze 25 NEW synthetic notes BEFORE actual 026F model execution: five each FOOD/AUDIO/ACCESS/STAFF/NONE. File experiments/026f/frozen_cases.py, Git blob 329911abfbccf7ae62163ec68aad48846224963c. The model sees each note and original 12 reference texts, never the new gold label.

Score all three methods on EXACT same source notes and SAME 022F/016 question mechanisms: correct held label, missed or wrongly indicated gate, false alert on NONE, independently calibrated and actually selected *synthetic* questions relevant to declared note gold versus irrelevant questions, real T5 encoder CPU latency, and no-model fallback.

Native meta-evaluator then asks the broad question again, preserving NO_T5, comparing same-text classical features, listing untested uses and deciding only whether a particular low-authority research role deserves more testing. Uncalibrated real opportunity loss prevents live welfare calculations or deployment.

The 25 examples and classical vocabulary were developed by this researcher, NOT collected independently from actual organizers; small test results are non-generalizable. Any improvement is only a reason to design a stronger field-blinded follow-up.

## Run

Standard-library-only: cd experiments/026f and python -m unittest -v test_relay.py.
Real public checkpoint: .github/workflows/motif026f-feedback.yml downloads pinned google/flan-t5-small revision 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab into an ephemeral runner; CPU inference is local-only and the receipt contains no weights.
