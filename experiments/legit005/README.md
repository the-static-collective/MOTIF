# MOTIF LEGIT-005 — THE MEANING / CONSEQUENCE FRONTIER

**Experiment status:** DRAFT / RESEARCH HOLD; no `main` merge, clinical tool,
source authentication, live network operation, autonomous semantic reasoning,
or claim of consciousness detection.

**Research question:** Can a small reason router generalize from corrected
*phrases* to new combinations, distinguish logical necessity from compatible
possibility, and prove its interpretations against countermodels—while
refusing truly unfamiliar expressions?

This addresses LEGIT-004's precise failure: it knew four full question
templates, transferred them to new nouns, but handled **zero** novel
paraphrases. It could not explicitly distinguish an alleged necessity
("must the hidden thing be absent?") from its converse possibility
("can it be present despite a negative measurement?").

## Actual new executable stack

1. **Teacher corrections, not pre-defined question-worlds.**
   `teacher.json` carries 16 assistant-annotated examples across distinct
   subject areas. During *teaching*, each example supplies the exact
   observed-proxy/hidden-target phrases, two clause spans, and one of
   **four developer-declared semantic operators**. These are human labels,
   not automatically discovered concepts.

2. **Classical compositional anti-unification.** `meaning.py` abstracts
   subject nouns into `{proxy}` and `{target}`, learns two independently
   observed left and two right phrase forms for each operator, then produces
   all cross-pair combinations. Each component must have been seen in
   at least two different teacher domains.
   The 16 teacher examples demonstrate eight distinct full phrase pairs,
   but the learned grammar includes **16 combined rules**, including **eight
   combinations absent from training**.

3. **Explicit logical duals.** The four query kinds represent:
   - `U_NEG`: Does a negative proxy *entail* hidden-target absence?
   - `CAN_NEG`: Is a countermodel with negative proxy and target present
      logically *compatible* with these admitted observations?
   - `U_POS`: Does a positive proxy *entail* target presence?
   - `CAN_POS`: Is a countermodel with positive proxy and target absent
      logically *compatible* with these admitted observations?

   In two-atom truth tables, the corresponding `U` / `CAN` pairs inspect
   **the exact same violating condition** and ask opposite quantifier
   questions: `forall compatible models: no violation` versus
   `exists compatible model: violation`.

   This is elementary classical logic, not a discovered theory of language.

4. **Real LEGIT-003 countermodel evaluation.** `runner.py` takes a question
   and a source-owned structured numeric table, **without** supplying
   semantic role labels at evaluation time. The learned grammar extracts
   terms and logical question kind. It requires that the extracted observed
   proxy matches the source instrument. The existing finite countermodel
   compiler generates compatible latent-target bounds. The router tests
   the logical query against these bounds and emits a formal certificate.

5. **HOLD and unsent clarification.** Unrecognized paraphrases, conflicting
   scopes, suspicious nested negation, unknown source instruments and
   unsupported research authority are held. Clarification is a proposal,
   **not** a message dispatched to anybody.

## Actual head-to-head (assistant-authored, nonblind)

**Frozen challenge:** `evaluation_cases.json`, 48 problems:
- 16 new-subject instances of full phrase pairs shown during teaching;
- 16 new-subject recombinations of known phrase fragments whose *complete
  sentences were never present in training*;
- 4 valid **new lexical paraphrases** using constructions the learner had
  not learned;
- 8 hostile/reversed/unsupported formulations;
- 4 source-instrument mismatches.

Every task contains a small synthetic observation table with controlled
partial hidden-target labels, **not source-provided answers**. Four strategies
face precisely the same cases and simulated proof constraints. The actual
countermodel proof for each accepted question is checked by an **independent
exhaustive truth-assignment oracle**, not by importing the LEGIT-003 compiler.

| Strategy | Correctly interpreted / 36 valid | Invalid accepted / 12 | Toy selective loss |
| --- | ---: | ---: | ---: |
| **Induced compositional grammar** | **32 / 36** | **0** | **1.0** |
| Rote memorization of teacher-seen phrase pairs (ablation) | 16 / 36 | 0 | 5.0 |
| **Strong hand-written classical compositional regex** | **34 / 36** | **0** | **0.5** |
| Always HOLD | 0 / 36 | 0 | 9.0 |

The loss is an arbitrary declared research rubric: incorrect confident
interpretation costs 1, justified abstention 0, valid unanswered question
0.25. This is not a calibrated utility model.

The induced grammar handled **16/16 unseen phrase recombinations**,
compared with **0/16 for its phrase-pair memorization ablation**, but
**0/4 genuinely unseen lexical expressions**. The strong conventional
parser handled 2/4 new lexical expressions and **won overall**.
All accepted cases agreed with the independent finite classical oracle on
their logical answer. This is **bounded compositionality**, not free-form
meaning understanding.

Our synthetic benchmark and teacher examples were authored by the
*same assistant*. This is not a human-independent or investigator-blinded
generalization demonstration.

### Reproduce and inspect failures

```bash
python -m unittest discover -s experiments/legit005 -p 'test_*.py' -v
python experiments/legit005/runner.py
python experiments/legit005/benchmark.py
```

CI runs the tests, source-backed neuroscience distinction, and full exact
48-case competitor comparison; archives both JSON receipts for 30 days.

## The consciousness question, with a sharper answer

Our manually curated 2024 six-center neuroimaging cohort includes
250 negative task-based neural command-following results across the
two previously documented behavior groups. These are aggregate observations,
**not the ground-truth labels for subjective experience**.

Two different sentences can now route to exactly the same logical
counterexample witness:

> Does missing neural command response rule out subjective experience?

> Can subjective experience exist without neural command response?

Given the **admitted source counts alone**, a compatible assignment exists
in which a neural-test-negative case has the latent target true. Therefore:

- `U_NEG`: **No, target absence does not logically follow from these
  admitted observations.**
- `CAN_NEG`: **Yes, such a countermodel is compatible with the evidence
  representation.**

Neither means that an actual patient is conscious. Both follow from the
absence of certified latent-state labels in the input. This is a logical
compatibility test, **not evidence of actual incidence or possibility under
all physical/clinical constraints**. "Can" in this parser specifically
means *satisfiable in the finite admitted model*, not unrestricted modal
possibility or proof of individual experience.

## What is missing (HOLD)

- **The underlying semantic operators were provided.** We have learned
  phrase combinations from annotations but not invented quantifier logic,
  selected philosophical interpretation, or proved the teacher's semantics.
- **No raw-document ingestion.** Source evidence is an already structured
  and previously hand-curated table. The method is not reading PDFs or
  extracting results from scientific prose.
- **No external source verification.** URLs and hashes are addresses and
  content witnesses, not provenance signatures or trustworthy clinical
  reference standards.
- **No unrestricted language understanding.** New lexical paraphrases and
  unfamiliar negation still HOLD, and an existing conventional parser wins.
- **No authority.** Not a clinical decision system, no actual question
  is sent, and no external operation or code write can be dispatched.
- **No superiority over classical methods.** Everything here is finite
  classical logic and conventional teacher-assisted pattern induction.
- **No independent holdout.** A separate investigator must author unseen
  questions and verify ground-truth intended logical relations before
  any claim of general semantic inference.

## Next adversarial experiment

Have an independent evaluator supply unfamiliar source text and
**minimal-pair questions** where shifting a single modifier reverses the
intended meaning (negation, scope, conditional reversal, "some" vs "all",
"no evidence" vs "evidence of no"). A baseline should include an
independently implemented conventional semantic parser + symbolic
countermodel solver, with matched evidence and a documented abstention
policy. Keep all teacher labels and unobserved test data out of MOTIF's
runtime. Only independent transfer improvement warrants graduation.
