# LEGIT-004 — THE UNKNOWN QUESTION
## Learning a small grammar from teacher corrections, then failing honestly on new language

**Branch:** `experiment/legit-004-question-grammar-induction`
**Status:** source-scoped experimental HOLD; no deployment, medical advice, unrestricted NLP, or real-world action.

### The frontier

LEGIT-001 needed an explicitly supplied hypothesis space.
LEGIT-002 met an actual neuroscience question and correctly HOLDed its unfamiliar scientific evidence schema; a separate authored evidence adapter reproduced published rates.
LEGIT-003 generated contrasting mathematical completions of *unobserved* latent labels from admitted aggregate counts, without fabricated Bayesian priors. But its `latent_target`, `observed_proxy` and implication were still manually typed in.

LEGIT-004 removes **one** of those hand-authored crutches: a *new case does not supply the observed-proxy and latent-target slots or the direction of the implication to be tested*. The case provides an ordinary question string, a source-owned structured count table with the named instrument, and source references.

From **eight** teacher-corrected question/span/claim examples across unrelated subjects, `grammar.py` induces **four** reusable source-token templates. At evaluation time, its learner is not given the answer annotation or subject slots; it captures the terms from the question itself, detects whether the claim runs from positive/negative proxy to present/absent latent target, and routes this into the actual LEGIT-003 countermodel compiler.

### What really crosses the boundary

For example, the original source-backed question can now arrive without preannotated proxy, latent-target or semantic label:

> If task based neural command following is negative, must subjective experience be absent?

The induced grammar proposes:
- observed proxy: `task based neural command following`
- latent target: `subjective experience`
- logical claim: `PROXY_NEGATIVE_IMPLIES_TARGET_ABSENT`

The source instrument label must match the extracted proxy. The original 2024 clinical research counts remain **hand curated** by LEGIT-002. The actual LEGIT-003 compiler runs and constructs compatible extreme completions for the 250 negative-test cases, yielding target-true count bounds `[0,250]`, no patient-level probability, and `NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE`.

A positive-test implication such as:

> If packet anomaly alert is positive, must network intrusion be present?

routes differently, testing `PROXY_POSITIVE_IMPLIES_TARGET_PRESENT` against the positive-test stratum. Neither rule supplies hidden truth.

### Controls and falsifiers

- Training: **8 explicitly labeled teacher examples**, two contrasting topics for each of four wording patterns. Labels are teacher-supplied; method names are **not** autonomously invented.
- Evaluation: **30 assistant-authored, source-separated, nonblinded questions**, including 16 held-aside instances of learned wording with unfamiliar subjects, 4 valid but unseen paraphrases, 8 unsupported/adversarial reversals and negations, and 2 source-instrument mismatches.
- Strong comparator: independently written, **conventional regex grammar** containing the four learned wording classes plus two additional valid paraphrases. It does not import the learned patterns or training file. Always-abstain is a second control.
- A deliberately explicit toy scoring rule: each unsupported question answered incorrectly costs 1, each valid unanswered question 0.25, correct answers cost 0. It is *not* a calibrated real-world loss model.
- Precise falsifiers: new synonyms and negation must not be treated as previously learned; sample counts cannot imply hidden latent truth; mismatched instruments are held; unlabeled researcher-created priors and source authority must not be fabricated.

### GitHub Actions observed result (2026-11-06)

**Run:** https://github.com/the-static-collective/MOTIF/actions/runs/42242912620 — 21/21 tests passed. Both exact JSON receipts and the 30-case benchmark were archived under `MOTIF-LEGIT004-GRAMMAR-HOLD`.

| Policy | Correctly accepted / 20 valid | Unjustified accepts / 10 invalid | Toy selective loss |
| --- | ---: | ---: | ---: |
| Induced four-template grammar | **16 / 20** | 0 | 1.0 |
| **Strong classical hand-written regex** | **18 / 20** | 0 | **0.5** |
| Always HOLD | 0 / 20 | 0 | 5.0 |

The induced grammar covers 100% of the 16 held-aside instances in previously learned phrasing, but **0/4 new paraphrases**. The classical baseline recognizes two new paraphrases. This is a **real negative result for unrestricted transfer**, not a reason to lower the evaluation standard.

Each source-count reasoning case in the evaluation remains logically underidentified because the synthetic cases intentionally contain **no latent-label anchors**. The arithmetic proof is performed by the already-tested LEGIT-003 solver; this experiment tests whether the router supplies the correct symbolic question in the first place.

### What is *not* being claimed

1. **Not arbitrary language understanding.** The architecture is a tiny classical anti-unification grammar over corrected sentence templates. It cannot infer the semantics of new connectives not shown in teaching.
2. **Not autonomous scientific reading.** Numeric evidence comes pre-structured from a source-owned table, not from raw PDF pages, and source URLs are not authenticated.
3. **Not a discovery of new logic.** Both the abstraction method and legal claim classes are predetermined. Strong classical methods are expected to be competitive or better.
4. **Not a blinded independent evaluation.** Both teachers and cases were authored by the assistant; test cases are separated from training only by repository artifact, not investigator independence.
5. **Not a decision-maker for people.** All output is read-only research HOLD; no patient diagnosis, test order, tool call, or automatic GRAFT/CANNON admission.
6. **Not generalizable outside the grammar.** Unknown paraphrases, reversed implications, mismatches and unsupported statements are held rather than converted into assumptions.

### Reproduce

```bash
python -m unittest discover -s experiments/legit004 -p 'test_*.py' -v
python experiments/legit004/bridge.py
python experiments/legit004/benchmark.py
```

Python 3.11 standard library, no credentials or external service.

### The correct next hard experiment

Keep the public research packet and strong classical baseline, but add an **independent source-language examination**: a frozen set of raw paragraphs from original primary sources in previously unseen fields, annotated by another investigator, with numerical table extraction separate from method recognition. Introduce ambiguity and source echo traps. Match a strong conventional information-extraction + symbolic solver baseline on the same text and compute.

Promotion requires independent generalization, not only recognizing the same connector phrases with new nouns. Until that evidence exists: **HOLD**.
