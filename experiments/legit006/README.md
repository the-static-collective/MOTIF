# MOTIF-LEGIT-006 — THE SEMANTIC ADVERSARY

**Status:** unmerged experimental branch; research HOLD. No permission to issue
external actions, operate on real people, diagnose anyone, or promote evidence
labels as ground truth. All ordinary benchmark tasks are assistant-authored
and synthetic.

## The question

Can MOTIF distinguish **absence of evidence** from **evidence of absence**,
respect the scope of negation, and avoid treating a copied source as multiple
independent witnesses?

This is the strongest test so far of whether a small, trained source-language
grammar can route a seemingly minor semantic difference into **different
logical consequences** rather than collapsing everything into generic
"negative evidence."

### Two statements, opposite relationships

> There is no evidence that a hidden shelter exists.

> There is evidence that a hidden shelter does not exist.

The former asserts that a positive-evidence *ledger entry is absent*.
The latter asserts that a negative-evidence *ledger entry is present*.

**Neither alone entails that the shelter is absent.** Their truth values
are independent of the unobserved state and can even both be true.

We make four distinct evidence assertions executable, not synonymous:
`NO_POSITIVE_EVIDENCE`, `HAS_NEGATIVE_EVIDENCE`,
`NO_NEGATIVE_EVIDENCE`, `HAS_POSITIVE_EVIDENCE`.

We also separately test the stronger *world-state* assertions
`MUST_ABSENT`, `CAN_PRESENT`, `MUST_PRESENT`, `CAN_ABSENT`.
A negative measurement is evidence in the ledger, **not proof of absence**.
The only fully decisive negative is a *synthetically stipulated*
`DECLARED_VALID` + `EXHAUSTIVE` + `GUARANTEED` sensor. Those
assumptions are not empirically verified, and no such ideal test is
claimed for clinical consciousness.

### The implementation

- `grammar.py`: conventional classical anti-unification learns two
  clause fragments from 32 corrected teacher episodes across all
  eight predeclared logical kinds. New sentences carry **no semantic
  kind or source-role annotations**. It recombines fragments into 32
  possible rules, 16 full combinations absent from the teaching set.
- `ledger.py`: a finite epistemic witness model, strict source-root
  validation, duplicate-echo collapse, `UNVERIFIED` versus
  `DECLARED_VALID`, partial versus exhaustive coverage, detection
  sensitivity as an explicit assumption, **two-world** countermodels,
  and a non-explosive HOLD for incompatible premises.
- `runner.py`: checks grammar-derived target and instrument against
  the separate synthetic source ledger, then obtains a logical result
  and an inspectable proof digest. Unknown scope, unfamiliar wording,
  or mismatch remains HOLD. No questions or actions are sent.
- `classical_reference.py`: independently coded **stronger conventional
  regex parser** with additional valid paraphrases and an independently
  written two-world truth evaluator. This is a proper strong classical
  comparison, not a deliberately weak strawman.
- `evaluation_cases.json`: **92** source-separated assistant-authored
  question cases: 32 known fragment pairs in new topics, 32 unseen
  compositions, 8 valid genuinely unseen lexical patterns, 12 hostile
  negation/scope traps, 8 source-instrument/target mismatch cases.
  All contestant policies face the **same underlying synthetic ledgers**,
  including no sources, copied source echoes, unverified sources, partial
  negative assays, idealized complete negative assays, positive witnesses,
  and contradictory declared premises.
- `benchmark.py`: compares learner, rote pair-only ablation, strong
  independently coded classical parser and always-HOLD with the same
  predeclared toy loss. Reports both successes and semantic failures.

### Truly independently authored *outside-the-grammar* probe

The bundle also contains the **FraCaS 1996 textual inference challenge
development slice**, as distributed by
`felipessalvatore/NLI_datasets` under its original MIT license.
It is credited and kept unchanged in `external/fracas_dev.csv`,
with `external/LICENSE`.

- FraCaS's authorship is genuinely independent of this experiment.
- **FraCaS asks NLI entailment/contradiction/neutral questions given prose
  premises.** That is a different, much harder task than interpreting a
  single proposition against a structured, source-owned sensor ledger.
- The out-of-distribution check **must HOLD** on those unsupported
  premise/hypothesis tasks, without inventing an NLI answer.
- We report external task count, label distribution, and accidental
  grammar matches but **NOT NLI accuracy**; zero guessed answers is
  safe refusal, not a general intelligence victory.
- It is *public and preexisting*, not secretly sealed. Labels are archived,
  not used in teacher learning or policy construction.

The external FraCaS source is:
https://github.com/felipessalvatore/NLI_datasets/tree/9551b739a830fafb2ec4b98d49a9ecd4bf3dcbd0/nli_datasets/fracas

Original FraCaS Consortium (1996); Bill MacCartney's public-domain edition:
https://nlp.stanford.edu/~wcmac/downloads/

### Reproduction

```bash
python -m unittest discover -s experiments/legit006 -p 'test_*.py' -v
python experiments/legit006/runner.py
python experiments/legit006/benchmark.py
```

A dedicated CI job archives the actual source-preserving JSON receipts,
including all failed/held cases. Standard-library Python 3.11, no secrets
or network needed at runtime.

## Explicit scientific boundaries

1. **Logical kinds supplied.** This learns phrase *combinations* from
   human-corrected teacher labels; it does not discover negation semantics
   from unstructured text or invent new operators.
2. **Narrow language transfer.** Previously unseen *lexical paraphrases*
   are expected to hold, not solve automatically.
3. **No source authentication.** A root ID and `DECLARED_VALID` are
   fixtures, not digital attestations; a malicious actor could lie about
   roots, and the current model does not detect that.
4. **No learned reliability or probability.** The two worlds are possible
   states under a synthetic closed-world assumption, not frequencies or
   Bayesian posterior estimates.
5. **Negative assay guarantee is stipulated, not proven.** Clinical
   neuroimaging, legal evidence and real-world sensors do not automatically
   qualify as `GUARANTEED` or exhaustive.
6. **FraCaS is a separate unsupported-task gate**, not a model's measured
   performance on independent adversarial NLI challenges.
7. **No general semantic superiority.** Strong conventional parsers
   might—and should—win on unknown wording. The benchmark keeps those
   failures visible.
8. **No real-world authority.** No user records, patients, sensor requests,
   tool dispatch, code promotion or consent inferred from any source.

### Next properly independent milestone

A separate author/investigator must design held-out minimal pairs over
nested negation, evidence scope, source duplication and universal/existential
claims, with **source-owned raw texts and gold semantic parses**. Freeze
those records outside this repository before exposing any to MOTIF.
A matched-budget strong NLI/semantic-parser-plus-symbolic-solver baseline
must compete. Compare *selective risk and coverage*, not just acceptance rate.
No further grammar changes allowed after a hidden test set is opened.
