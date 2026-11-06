# REASON-CARTRIDGE-012 — THE COURT RETURNS TO REALITY

**Status:** experimental, historical, read-only evidence-type lab. Stacked on unmerged REASON-011 draft PR #102, which itself is stacked on the earlier REASON-010 → REASON-001 experimental branches. Not merged, not deployed, not legal advice.

## The harder question

REASON-011 manipulated **fictional, hand-written typed propositions** and preserved contradictions without explosion.

This experiment takes **actual short verbatim passages from six published U.S. judicial opinions**, exercises a simple text-to-epistemic-type learner, verifies it on two **new judicial cases not used in the prior strange-court experiment**, and reuses the original REASON-011 four-valued evaluator to prevent false contradictions.

**Do not overread this:** the passages are tiny, hand-selected quotation fragments. We have **not** parsed whole opinions, generated legal issue names from unstructured text, or extracted judicial reasoning through a general language model. This is an inspectable bridge between real text snippets, curator-defined labels, and typed logical representation.

### Original judicial material

| Case | Training? | What makes it strange | Risk of a bad inference |
|---|---|---|---|
| [Stambovsky v. Ackley](https://law.justia.com/cases/new-york/appellate-division-first-department/1991/169-a-d-2d-254-572-n-y-s-2d-672.html), N.Y. App. Div. (1991) | Yes | A reputedly haunted house | The legal use of estoppel **is not** evidence that physical ghosts exist; an opportunity to seek rescission isn't a final rescission award. |
| [Leonard v. Pepsico](https://tortwell.com/cases/210-f3d-88), 2d Cir. (2000) | Yes | The advertised Harrier fighter jet | A party's claim that an ad constituted an offer isn't the court's holding; the panel affirmed judgment against that claim. |
| [Naruto v. Slater](https://law.justia.com/cases/federal/appellate-courts/ca9/16-15469/16-15469-2018-04-23.html), 9th Cir. (2018) | Yes | A macaque's camera self-portraits | **Article III** and **statutory Copyright Act** standing involve different legal questions despite sharing the word “standing.” |
| [Pierson v. Post](https://law.justia.com/cases/new-york/other-courts/1805/3-caines-175.html), N.Y. (1805) | Yes | Who possessed a hunted fox | A dissent or an earlier lower-court judgment is not the appellate majority's controlling disposition. |
| [United States v. One Book Called “Ulysses”](https://law.justia.com/cases/federal/district-courts/FSupp/5/182/2250768/), S.D.N.Y. (1933) | **Held out** | Customs seized a supposedly obscene book | A judicial finding about pornographic intent, and rejection of the forfeiture motion, are distinct from any sweeping pronouncement about all books or future law. |
| [United States v. Forty Barrels and Twenty Kegs of Coca-Cola](https://www.law.cornell.edu/supremecourt/text/241/265), U.S. Supreme Court (1916) | **Held out** | Barrels of soda, caffeine, and the Food and Drugs Act | Caffeine could be considered an **added ingredient** under the old statute, while the separate health-harm question had to go to the factfinder. The Court did **not** conclusively decide the scientific health question. |

The original **judicial opinions** were consulted while curating the short excerpts. The runnable code stores two short quoted spans per case, with citation, court/year, opinion URL, paragraph locator, revision and word count. Each court-opinion source contributes at most **25 quoted words total** to this research repository. Quotes are fragments and do not replace reading the opinions. The CI workflow works from these **pinned local snippets**, not by redownloading and verifying the remote publisher's current bytes.

## The actual executable learning problem

`classifier.py` receives eight quotations and eight explicitly human-annotated types:

`LEGAL_TREATMENT`, `PROCEDURAL_POSTURE`, `PARTY_ALLEGATION`, and `SEPARATE_OPINION`.

It learns a feature → type mapping from a **developer-supplied vocabulary** of five bounded lexical cue families. It does not see the independent curator's two-case heldout **type labels** during fitting. The fifth lexical cue (a question expressly left to the factfinder) has no training example, so when encountered the system must **HOLD**, not extrapolate a known legal ruling.

This is an epistemic **text-tagging/routing** experiment, not the invention of new legal interpretation methods. A competent classical keyword/rule classifier with the same features can tie it.

### New-opinion heldouts

The two entirely new case titles are **Ulysses** and **Forty Barrels**:

| Excerpt | Curated evaluation type | Result |
|---|---|---|
| Ulysses: opinion discusses pornographic intent | Legal treatment | Correctly tagged |
| Ulysses: forfeiture motion denied | Procedural posture | Correctly tagged |
| Coca-Cola: caffeine is an “added” ingredient | Legal treatment | Correctly tagged |
| Coca-Cola: unresolved question of injurious effect | Previously untrained factual issue | **Correctly abstains** |

**3/4 supported type identifications, 1/4 explicitly justified abstention, 0/4 mislabeled.** A deliberately weak always-legal-tag baseline gets **2/4 correct** without the ability to distinguish an unseen evidence type. The strong rules baseline may match or outperform MOTIF. The heldout content can be read in the same Git repository by an authorized researcher, so this is **import/usage-based holdout discipline, not a cryptographically isolated blind benchmark**.

`receiver.py` independently checks the selected source snippets against the original full curator-owned card (including citation, court, URL, and exact quotation), confirms the learning annotations, tests the unfamiliar opinions, and grants only explicitly digest-bound `ADMIT_READ_ONLY` / `SUGGEST_ONLY`. A fabricated quote, court URL, source code revision or training role is rejected, even when the content checksum is recomputed. Content hashes do not authenticate an external court website.

## Link to the original four-valued REASON-011

`bridge011.py` imports the **actual pinned REASON-011 `engine.verdict` function**, not a rewritten clone.

A separate curator supplies the **legal issue identifiers and YES/NO/UNDECIDED polarities** attached to the accurately classified quotations. **Those legal semantics are not inferred by the classifier.** The bridge then encodes each reviewed proposition with explicit **court, historical year, source case, issue, sign**. Party allegations, dissents, unknown semantic types and undetermined factual issues cannot be silently promoted into majority legal facts.

The resulting read-only evidence register shows:

- **Naruto**: Article III standing is **SUPPORTED** under the historical panel's analysis; statutory standing under the Copyright Act is **REFUTED**. They are not contradictions because they answer **different questions**.
- **Coca-Cola**: caffeine qualifying as an added ingredient is **SUPPORTED**; whether caffeine rendered the product deleterious remains **UNDETERMINED** in the opinion's remand posture. No present-day health determination is inferred.
- **Stambovsky**: the seller's estoppel and the house's legal reputation are **SUPPORTED**; the actual physical existence of ghosts remains **UNDETERMINED**.
- **Ulysses**: the particular findings on pornographic intent and the government's forfeiture request are represented as negative under the 1933 judgment, without extending the ruling to contemporary obscenity law.

These four-valued judgments are entirely within the **hand-annotated source-proposition model**. They do not determine real-world truth or current precedential authority, and the model is not interpreting an opinion de novo.

## Falsifiers and permission boundaries

- If an unseen opinion introduces a fifth source type, `HOLD` is correct; outputting an invented holding is not.
- If an appellate argument is treated as a controlling holding or a dissent as a majority vote, the independent source review fails.
- If legal fiction or judicial estoppel implies a physical supernatural fact, the typing boundary fails.
- If Naruto's two types of standing collapse into “both yes and no” for one issue, the inherited engine interface has been misused.
- If the Supreme Court's remand on caffeine is portrayed as an established health verdict, the result is unsupported.
- If a court quote, URL, citation, role, packet, or proposed legal authority is forged, fail or HOLD. Changing a checksum must not bypass a full source-owned replay.
- No external actions, current law predictions, legal service, remote data authentication, production builds, GRAFT import, or CANNON canon selection.

## Reproduce

```sh
python -m unittest discover -s experiments/reason-cartridge-012 -p 'test_*.py' -v
python experiments/reason-cartridge-012/trial.py reason-012-evidence
```

`.github/workflows/reason-cartridge-012.yml` also runs inherited REASON-001..011 regression tests and uploads:

```
reason-012-evidence/
  type-cartridge.json
  typed-four-value-bridge.json
  benchmark.json
```

## Next rigorous frontier

The next step toward genuinely **reasoning from court opinions** is a legal-research evaluator with separately versioned raw judicial texts, passage-level annotation by independent reviewers, source-text pointer verification, case-law dependency and procedural graphs, **human-derived question sets withheld from the learner**, and adversarial contradictions that are not inserted artificially. Strong comparisons should include classic rule-based NLP, retrieval with source-grounding, and actual legal experts reviewing accuracy/abstention. Until then, REASON-012 demonstrates narrow **quotation-type extraction and honest uncertainty handling**, not a general legal inference system.
