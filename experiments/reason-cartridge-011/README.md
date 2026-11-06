# REASON-CARTRIDGE-011 — THE IMPOSSIBLE COURT

**Research status:** experimental, source-pinned and **entirely fictional** judicial thought experiments. Stacked on unmerged REASON-010 PR #99 (and its earlier draft dependencies). No hypothetical rule is a statement of binding law. No court records or personal legal cases are read, no judicial outcomes are predicted, no external services are contacted.

## The point

Ordinary binary reasoning can be forced to falsely choose between two conclusions when the underlying premises contradict, refer to different times, represent different court findings, or are only a litigant's allegation.

This experiment supplies a source-owned court **that cannot exist**. MOTIF must avoid treating contradictions as arbitrary proof, or a legal finding as a fact about physical reality. The result is a **typed, proof-carrying, four-valued inference layer**, not a free-form lawyer.

### Four fully fictional scenarios

| Case | Absurd legal dispute | What the reasoner actually returns |
|---|---|---|
| **Mara v. Future Mara** | A person sues their future self for refusing to sign a past contract. A signature exists nine years later. | Present enforceability **REFUTED** by stipulated nonacceptance; future enforceability **UNDETERMINED**. Neither future signature nor litigant's contrary allegation is silently applied to the earlier identity/time. |
| **Estate of Unit Seven** | A robot was designated to inherit land. The invented tribunal simultaneously stipulates that the machine **is** and **is not** a legally eligible person for title. | `TAKES_TITLE = BOTH`: competing proofs with named facts and rules. The engine proposes two possible source-owner clarifications, not an automatic ruling. Unrelated claims remain **UNDETERMINED**. |
| **Two Impossible Courts** | One tribunal admits impossible footage and records an affirmative finding; another excludes it and rejects the event claim. | `COURT_A = SUPPORTED`, `COURT_B = REFUTED`, while `EXTERNAL_WORLD = UNDETERMINED`. A finding in one forum never becomes the physical truth in another. |
| **The Self-Nullifying Order** | An invented court's own order makes itself void, and voidness makes the order invalid; an additional rule reverses the voidness. | `ORDER_VALID = BOTH`, `ORDER_VOID = BOTH`, unrelated claims still **UNDETERMINED**. The fixed point terminates without logical explosion. |

**All parties, cases, courts, facts, and norms above are inventions for this experiment.** They are not real case citations, court documents, future predictions or claims about what the law *should* be.

## Four-valued truth instead of forced binary answers

The reasoning engine records **positive and negative evidence separately**:

| Positive support | Negative support | Result |
|---|---|---|
| Yes | No | `SUPPORTED` |
| No | Yes | `REFUTED` |
| Yes | Yes | `BOTH` |
| No | No | `UNDETERMINED` |

This is a finite, **paraconsistent-style** positive/negative inference procedure. It is not classical explosive entailment, but it also is not proof that a contradictory legal system is ultimately valid. It makes the *limits* of current stipulated premises explicit.

### Strong boundaries

- Every proposition has explicit **forum, time, subject, issue predicate and polarity**.
- Source case rules can connect facts **only within the same forum/time/subject**. Cross-court findings, future signatures and identity changes cannot silently jump scopes.
- An `STIPULATED_HYPOTHESIS` is allowed into the synthetic reasoning system; `PARTY_ALLEGATION` is preserved but **not promoted to fact**.
- Norms are labeled `HYPOTHETICAL_NORM_NOT_REAL_LAW`, not court holdings.
- Missing evidence does **not** mean evidence of a negative. Negative support requires an explicit source stipulation or proof.
- A contradiction yields **both** named proof witnesses, not any arbitrary additional assertion.
- A source owner may *hypothetically* withdraw one explicitly revisable stipulation. MOTIF recomputes the consequence and labels it **unobserved, conditional**. It cannot retract a nonrevisable fact, claim ownership of a real verdict, or mutate the canonical casebook.
- The returned contradiction core is **one explicit pair of supporting proofs**, not a claim of globally minimum inconsistent premises.
- A source-pinned, strict replay-validated dossier refuses attempts to forge outcomes, source witnesses, scope, proof dependencies or a fabricated completed correction, **even when the attacker recomputes the content digest**. A Git blob hash establishes repository file identity, not real-world source authentication.

## Independent controls and evidence

An entirely separate `reference.py` implementation uses a direct **set-of-facts least-fixed-point**, without importing the inference engine or its provenance algorithm. Every fictional query must agree with this classical explicit-negation reference before the experiment is considered successful.

The four cases contain **10 queries**:

| Outcome | Count |
|---|---:|
| SUPPORTED | 1 |
| REFUTED | 2 |
| BOTH | 3 |
| UNDETERMINED | 4 |

All **10/10** match the independent classical implementation. Forcing these outcomes into a single Boolean result would lose the distinction between contradictory and missing support on **7/10** questions.

This is a comparison with an intentionally inadequate **binary response interface**, not evidence that four-valued logic outperforms established Belnap-style paraconsistent logics, theorem provers or logic programming languages. A classical program can implement the same semantics and reproduce all results; our independent reference does exactly that.

The workflow runs all inherited REASON-001 through REASON-010 regression tests and the new source-scope, contradiction, recursion, forged-revision, unsupported assertion and nonexplosion tests.

## Reproduce

```sh
python -m unittest discover -s experiments/reason-cartridge-011 -p 'test_*.py' -v
python experiments/reason-cartridge-011/trial.py reason-011-evidence
```

The GitHub Actions workflow `.github/workflows/reason-cartridge-011.yml` publishes inspectable source-bound packets:

```text
reason-011-evidence/
    benchmark.json
    future_self_contract.json
    robot_inheritance.json
    rival_courts.json
    self_nullifying_order.json
```

The packets contain each explicit hypothetical premise, proof dependencies, contradictory source witnesses, conditional clarifying questions, source revision and no-authority flags. All artifacts are **read-only**; no GRAFT import, CANNON selection, third-party adapter, real court docket or personal legal data is involved.

## What would actually falsify the result?

- If evidence from `2040` is used to prove `2031` acceptance, the time scope is broken.
- If a majority decision from `COURT_A` proves the physical event globally, the authority scope is broken.
- If contradictory robot-personhood premises entail unrelated `COURT_MADE_OF_CHEESE`, inference is explosive and the experiment fails.
- If self-referential rules run forever, finite closure is broken.
- If party allegation is silently treated as a stipulated fact, provenance is broken.
- If a contradiction is resolved without a reviewed factual/interpretive premise, the correction engine is unsound.
- If a forged report is accepted after recalculating its hash, replay validation is insufficient.
- If the separate classical reference disagrees with a single reported four-value, the benchmark fails.

## Next meaningful vertical

Bring this **typed conflict representation** to real historical opinions from REASON-010. Require independently sourced quote spans, procedure/holding/argument annotation, competing interpretations separated by forum and time, and human review where the evidence is genuinely ambiguous. A much stronger test would withhold entirely new natural-language opinions and see whether MOTIF can **extract** a typed proof before reasoning with it. No such raw-opinion interpretation is implemented here.

For now this is an accurate, inspectable synthetic demonstration of non-explosive reasoning under explicitly conflicting assumptions.
