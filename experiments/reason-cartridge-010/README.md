# REASON-CARTRIDGE-010 — THE STRANGE COURT

**Theme: put the reasoning system in front of real court opinions with apparently absurd facts.** That produces opportunities for legal/evidentiary category errors that a generic Boolean graph reasoner would miss.

**Status:** source-pinned, read-only, historical-opinion *annotation* and typed-applicability experiment, stacked on unmerged REASON-009 PR #95. Not a legal service, not a judicial outcome predictor, not production, not a deployed law agent, not a source of current legal advice.

## Four actual court cases, not invented lawsuits

| Source opinion | The bizarre scenario | The legal trap |
|---|---|---|
| [Stambovsky v. Ackley](https://govt.westlaw.com/nyofficial/Document/I3785d6c8dbd711d9a489ee624f1f6e1a), 169 A.D.2d 254 (N.Y. App. Div. 1991), **official NY reports** | A seller publicized a reputation for ghosts and the purchaser sought relief | The court's legal-estoppel treatment of the reputation **is not an empirical proof of paranormal activity**. The court **reinstated the rescission claim**, not a final damages or rescission award. |
| [Leonard v. Pepsico](https://law.justia.com/cases/federal/appellate-courts/F3/210/88/483989/), 210 F.3d 88 (2d Cir. 2000) | A promotional commercial seemingly offered a Harrier jet for points | The litigant's demand is **not** the majority holding. The appellate court affirmed **summary judgment for PepsiCo**, rather than ordering a jet delivered. |
| [Naruto v. Slater](https://law.justia.com/cases/federal/appellate-courts/ca9/16-15469/16-15469-2018-04-23.html), 888 F.3d 418 (9th Cir. 2018) | A macaque allegedly took its own selfies; a copyright lawsuit followed | The panel treated the complaint as satisfying **Article III standing under existing circuit precedent** while concluding Naruto lacked **statutory standing under the Copyright Act**. The concurrence raised additional next-friend jurisdiction concerns. These are distinct legal tests. |
| [Pierson v. Post](https://law.justia.com/cases/new-york/other-courts/1805/3-caines-175.html), 3 Cai. R. 175 (N.Y. 1805), with [NY Courts Historical Society](https://history.nycourts.gov/case/pierson-v-post/) | An argument about who owned a hunted fox | The **majority** held that pursuit alone was insufficient to support Post's claim; the **dissent** favored rights arising from hot pursuit. A dissent cannot silently become the historical majority rule. |

These source URLs point to opinions or a court-history collection. The experiment stores **short, manually prepared paraphrase cards**, not the full judgment text or automatically extracted evidence. Its tiny hand-curated corpus and labels are part of the source owner. Citation links were checked while building the experiment; the workflow **does not** redownload or independently re-parse court websites. This matters.

## The missing operator: legal applicability is typed

REASON-009 used only Boolean edge variables and AND/OR expression shapes. Legal reasoning requires *typed* distinctions such as the authorial voice, question being decided, and epistemic category of a claimed fact.

Here the interpreter learns a **minimal equality-guard conjunction** over six bounded, predeclared metadata axes:

- Which **case** is being quoted?
- Which **legal issue** does the statement address?
- Whose **voice** is it: majority, dissent, party, etc.?
- Is it a court **holding**, a party position, a rationale, or a separate opinion?
- Is its epistemic **layer** legal estoppel, empirical allegation, procedural judgment, statutory standing, etc.?
- Does its **source status** indicate an anchored curator card or a simulated/unverified intrusion?

These six field names and string-equality operations are supplied by the developer. The system searches **all 63 nonempty conjunctions** and selects the smallest one that uniquely identifies the source-owned target among contrastive choices. It proves each selected gate necessary on the synthetic training fixtures by removing it and showing a counterexample.

This is **composed typed applicability**, not the spontaneous invention of novel legal ontologies or general-purpose jurisprudence from natural-language text.

### Training and genuinely disjoint case-family tests

**Teaching (6 questions):** *Stambovsky* (ghost-house reputation, limited rescission procedure, broker) and *Leonard* (ad vs offer, summary judgment, writing requirement).

**Heldout (6 questions):** *Naruto* (Article III vs statutory copyright standing; dismissal), *Pierson* (majority pursuit rule; dissent; reversal). The heldout questions are **not passed to the selector during fitting**.

Training includes **synthetic, explicitly marked** near-miss metadata cards that differ along one relevant axis, plus actual curated party/dissent/reasoning positions. These decoys are *not new court statements*. The benchmark is intentionally adversarial: a first-hit / shared-keyword retrieval baseline will be unreliable. An appropriately typed hand-built classical selector can match our program. This experiment does **not** demonstrate automatic interpretation of complex appellate opinions.

### Verification and refusal

- A separate receiver verifies selected answers against **the complete original pinned source-owned card**, including citation, court and paraphrase, not merely a user-supplied authority tag. It uses the two withheld case families, yielding **6/6** card identifications after source-bound review.
- Unsupported prompts **HOLD**: empirical proof of real ghosts, a generic factual copyright-ownership question not answered by the stored holding, or a claim that the 1805 New York opinion controls a modern Minnesota court.
- The system distinguishes **concurrence/dissent** from majority holdings and respects the limited procedural posture. It never infers that a minority opinion is controlling or that an appealed dismissal is a universal statutory rule.
- Modified or rehashed training evidence, false source card, unauthorized action fields and missing receiver admission must HOLD. A Git blob hash checks stored source **content identity**, not authentication of remote online court records.
- Every admitted response is **SUGGEST_ONLY**, references its exact historical court opinion, says it is a curator paraphrase, and gives **no live-law conclusion or external action**.

## Reproducible results

```sh
python -m unittest discover -s experiments/reason-cartridge-010 -p 'test_*.py' -v
python experiments/reason-cartridge-010/trial.py reason-010-evidence
```

The GitHub Actions workflow `.github/workflows/reason-cartridge-010.yml` additionally runs inherited REASON-001 through 009 regressions and saves:

```text
reason-010-evidence/
  typed-operator.json
  benchmark.json
```

The benchmark documents its source links, six typed selector gates, one omitted-gate counterexample per guard, curated training split, heldout predictions, and three out-of-scope refusals. **These are synthetic metadata reasoning tests built around four real case outcomes—not a law school examination or a blinded legal interpretation task.** No legal advice is delivered.

## Bigger architectural direction

This is the right adversarial domain for the next experiment because the oddest cases force a reasoner to separate:
- legal fiction / judicial estoppel from claims about physical reality,
- constitutional jurisdiction from statutory causes of action,
- a litigant's or dissenting judge's position from a court's holding,
- a procedural reopening from a final merits award,
- historical precedent in one forum from current law elsewhere.

A stronger REASON-011 would use **actual unstructured opinion excerpts** and independently annotated novel opinions, ask for the legal test and its procedural dependency graph, then pit source-quote-grounded answers against hand-tagged controls and a strong classical rules engine. The system should abstain when it cannot identify a supported legal proposition or relevant jurisdiction. An especially useful twist would be new fictitious courtroom hypotheticals whose contradictions are detected **before** predicting an outcome. That remains unimplemented here.

**This is a research experiment, not a substitute for checking current law with a qualified professional.**
