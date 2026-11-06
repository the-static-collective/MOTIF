# REASON-CARTRIDGE-013 — THE ADVERSARIAL READER

**Status:** source-pinned, read-only, reproducible research branch, stacked on unmerged REASON-012 draft PR #107 and the preceding experimental branches. No merge, deployment, autonomous legal service, current-law statement, GRAFT transplant or CANNON canon selection.

## What changed from REASON-012?

REASON-012 classified a few short **preselected quotations** from judicial opinions and relied on a human annotator to provide issue identities and signs. REASON-013 instead receives **contiguous sequences of untagged, manually normalized judicial prose paragraphs**, with source citation and link only. The reader must infer where an opinion's **author/voice changes**, track which arguments and dispositions belong to which judge, and build an independently inspectable span-anchored argument graph.

This is more realistic than typed cards, but **not full-text processing**. The 8/9/9/21 included paragraphs are **editor-selected, sometimes lightly shortened/normalized source prose**. They are not an exact downloaded full source; the selection and developer-authored lexical cues were designed with knowledge of the cases. The heldout split excludes the *reference answer keys* from `reader.py`, but is not a blinded generalization benchmark. **Do not claim autonomous legal comprehension, unseen legal test accuracy, neutral end-to-end reading of all court opinions, or expert-grade statutory interpretation.**

## Primary judicial sources

| Split | Opinion and link | The absurd dispute | Main provenance challenge |
|---|---|---|---|
| Development | [McBoyle v. United States, 283 U.S. 25 (1931)](https://www.law.cornell.edu/supremecourt/text/283/25) | Is an airplane a motor vehicle under the original auto-theft act? | Ordinary statutory meaning; reverse a conviction without claiming aviation theft was lawful under all laws. |
| Development | [United States v. 95 Barrels Alleged Apple Cider Vinegar, 265 U.S. 438 (1924)](https://www.law.cornell.edu/supremecourt/text/265/438) | Can vinegar made using rehydrated apples be sold under the original label? | Distinguish the lower tribunal's findings, party allegations and Supreme Court's disposition. |
| **Held out** | [Nix v. Hedden, 149 U.S. 304 (1893)](https://www.law.cornell.edu/supremecourt/text/149/304) | Are imported tomatoes fruits or vegetables **under the 1883 tariff**? | Botanical fruit and ordinary commercial-language vegetable are DIFFERENT issue definitions, not a contradiction in one court holding. The Court affirmed. |
| **Held out** | [Yates v. United States, 574 U.S. 528 (2015)](https://www.law.cornell.edu/supremecourt/text/13-7451) | Can destroying undersized fish violate a records-tampering statute aimed at obstructing investigations? | **4–1–4 Court:** Ginsburg's four-Justice opinion announcing reversal, Alito's one-Justice concurrence in the judgment, Kagan's four-Justice dissent. The **5–4 judgment alignment is NOT a single five-Justice majority rationale**. Section 1519 should not be confused with the uncontested separate §2232(a) charge. |

The links are to public representations of U.S. Supreme Court opinions. The repo's curated paragraph prose is intended to be checked against those sources. The CI currently tests **local source ownership and structured outputs**; it does **not** freshly download, verify every word, or parse entire historical opinions.

## Mechanism

`reader.py` is a deterministic **limited lexical and structural baseline**, not a pretrained model:

1. Verify the source-owned repository Git blob for `opinions.py`.
2. Split the untagged prose sequence at natural textual judge headers (e.g. a Justice delivering the Court opinion, announcing the judgment, concurring in that judgment, or dissenting). Record the specifically named authors and joiners **as written**.
3. Identify a handful of developer-supplied lexical features such as a proposed **restricted reading**, an **expansive reading**, statutory context, ordinary/common use versus botany, and a reversal or affirmance.
4. Exclude party allegations and lower-court statements from judicial proof nodes if clearly marked. Preserve every triggered feature with the **exact source paragraph, SHA-256, citation, year, voice and opinion URL**.
5. Produce explicit association/competing-view edges; these are **lexical evidence associations**, not an automatically inferred doctrinal entailment graph.
6. Reuse the actual Git-blob-pinned **REASON-011 `engine.verdict`** for four-valued evidence status, separately per judge and issue. Opposite voices do not create a `BOTH` result within one judicial speaker.
7. With a plain-English question, return *only* relevant anchored paragraphs or a **HOLD**, not a fabricated judicial yes/no answer. A request about whether the courthouse is made of cheese produces no cited evidence and therefore HOLD.
8. A replay validator reconstructs every graph from the original pinned local prose. Tampering with dissent roles, vote counts, paragraphs, evidence links, court year or execution authority fails—even with a fresh packet checksum.

No human-approved source signature, authoritative current-law oracle or arbitrary text-mining module is present.

## Heldout interpretation tests

The answer/role reference keys are stored in a separate **evaluation-only** `gold.py` that `reader.py` and `bridge011.py` do **not** import.

The two heldout opinions produce **16/16** expected role, disposition, court-vote and interpretive-signal fields:

- **Nix**: Justice Gray, opinion of the Court, botanical-fruit and ordinary-vegetable evidence tagged distinctly, lower judgment **affirmed**.
- **Yates**: Ginsburg **4** votes for reversal / narrower reading, Alito **1** additional vote in concurrence for judgment, Kagan **4** dissenters favoring broader reading and affirmance. The Court's judgment aligned **5–4**. Neither all nine Justices nor all five favoring reversal are incorrectly credited to Ginsburg's rationale.
- **No incorrect source contradiction**: separate Yates voices are separately labeled `SUPPORTED` (restricted interpretation) or `REFUTED` (expansive interpretation) within each named voice scope; no individual voice incorrectly reports `BOTH`.
- **Unsupported legal conclusion withheld**: a question about a cheese courthouse does not invent a source.
- **Unverified legal generalization withheld**: a statement about physical objecthood or a tariff is not automatically treated as binding contemporary law.

The 16 fields are **curator-identified metadata checks on selected known texts**, not statistically independent legal opinions or law-school reasoning questions. A strong classical rule-based parser can match them, and the grammar was created with knowledge of the heldout sources. The first-hit word matching control is intentionally weak; we do not claim empirical model superiority.

## Reproducibility

```sh
python -m unittest discover -s experiments/reason-cartridge-013 -p 'test_*.py' -v
python experiments/reason-cartridge-013/trial.py reason-013-evidence
```

The GitHub Actions workflow `.github/workflows/reason-cartridge-013.yml` runs all prior REASON-001…012 tests, the new adversarial source/role/forgery checks, and a deterministic heldout evidence audit. It uploads:

```text
reason-013-evidence/
    benchmark.json
    mcboyle-argument-graph.json
    vinegar-argument-graph.json
    nix-argument-graph.json
    yates-argument-graph.json
    unanswered-question.json
```

## Honest scientific status and next hard falsifier

This experiment advances the system from curator-supplied **typed findings** toward **attributed passages and explicitly separated judicial voices**, while demonstrating safe abstention. It **does not** parse entire unmodified source texts, infer statutory tests from free prose, establish source authenticity from the open internet, apply Shepard/KeyCite-style subsequent treatment, construct judicial holdings across other forums, or give contemporary legal advice.

The next meaningful falsifier should fetch **complete original opinion texts**, fix independent train/test splits and annotation guidelines **before writing retrieval rules**, keep a true cryptographically sealed holdout until after model publication, and evaluate on very different court opinions, including majority/plurality/dissent, remand, procedural vs merits outcomes and contradictory testimony. Benchmark against citation-grounded retrieval, a strong classical legal parser and expert human annotations. Unsupported judgments must HOLD. Anything short of that is a useful engineering demonstration, not general-purpose legal reasoning.
