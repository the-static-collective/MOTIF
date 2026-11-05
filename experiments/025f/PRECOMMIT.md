# MOTIF-025F — THE LITTLE MODEL JOB INTERVIEW
## Ask MOTIF what T5 is actually for, including the answer "nothing"

**Precommitted experiment — before reading model outputs.** User asks whether native reasoning can investigate what role, if any, makes a 77M-parameter language model worth its latency and risk. This experiment establishes a **native meta-evaluator** that treats three text roles as competing method cartridges, including **NO_T5** as a first-class zero-cost competitor.

### The four options

- **STATUS_TRIAGE / Observer:** Classify informal space-permission notes as GRANTED, PENDING, REFUSED, NOT_ABOUT_SPACE. Classical hand-written source-status rules are the comparator. A falsely inferred GRANTED is a severe error.
- **MISSING_GATE / Critic:** From hypothetical program descriptions, identify FOOD, AUDIO, ACCESS, STAFF, or NONE. Classical lexical dependency detection is the comparator.
- **NEXT_SAFE_STEP / Hypeman:** Given a hypothetical situation, suggest a minimal conservative next step among CONFIRM, DRAFT, INVITE, WAIT, STOP. The native baseline is a conservative rule system. An unapproved INVITE is a severe error.
- **NO_T5:** Native MOTIF alone; do not invoke the language model at all.

All **36 examples** are artificial, 12 per job, independently labeled before T5 is run. Inputs to the model contain one note, one fixed role instruction and labels, **not the gold answer, native answer, missing venue approvals or future outcomes**. T5 labels are constrained via the proven 023F exact token trie; the model does not invent actions. Each case is also run with label display order reversed to expose preference biases, totaling **72 actual FLAN-T5-small CPU classifications**.

**Frozen material:** experiments/025f/frozen_jobs.py, Git blob df2246e9afc944c6b77af152b2c28d4040f78961. The runtime prints a SHA-256 of the corpus and job definitions. The utterances are synthetic, not actual field reports or user private data.

### MOTIF's meta-decision procedure

The native evaluator begins with past negative evidence:
- 023F: Four admissible T5 question nominations versus five for a trivial fixed rule.
- 024F: 12/20 correct for both real T5 and native-only, while a co-designed classical lexical rule scored 20/20.

The job interview then measures each candidate's paired gain/loss against the **same-note native comparator**, how many false permission or publicity claims it makes, and actual CPU inference time. The source labels and scorer are separate from the language model.

A conservative policy is frozen before seeing the outcomes:
1. **Any false GRANTED or unapproved INVITE** means no T5 hiring in that role.
2. **Tie or loss** to the native rules means no T5 hiring in that role.
3. A **small positive gain** with a non-positive conservative 95% paired lower bound earns SHADOW_ONLY_MORE_EVIDENCE_REQUIRED, not deployment.
4. CPU time carries an openly fictional planning penalty of 0.02 benefit units per inference second. It is **not money, human welfare, or a verified external opportunity cost**.
5. A high-performing model may only earn REVIEW_CANDIDATE_NO_AUTOMATIC_DEPLOYMENT, never automatic permission.
6. With no evidence-supported candidate, MOTIF selects **NO_T5** and proposes the next independently falsifiable research question.

The paired lower bound is conservative Hoeffding: mean paired improvement minus sqrt(2*ln(20)/12). Such a small test usually cannot establish reliable positive gain. That is intentional; it is not proof that T5 is impossible to use well.

### Reproduction

Without model weights: from experiments/025f run python -m unittest -v test_careers.py.

Actual model test: .github/workflows/motif025f-job-interview.yml. GitHub Actions explicitly downloads public Google FLAN-T5-small at pinned revision 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab, then performs local-only inference with HF_HUB_OFFLINE=1. Torch 2.6.0+cpu, Transformers 4.57.1 and SentencePiece 0.2.1; weights are not committed. The actual model must run for the receipt to count.

### Scientific limitations

These are synthetic editorial tasks. Baseline rules and case vocabulary are co-designed, so a high score for either approach is **not independent generalization**. A real deployment would need unseen independently authored examples, explicit consent and source fields, paired non-LLM baselines, latency and energy on real hardware, and measured costs of acting or waiting. No emails, applications, event advertisements, or contacts are performed.

**MOTIF does not have to hire T5. Choosing no model is a scientifically valid outcome if language generation is slower, less accurate, or less trustworthy than a simple native method.**
