# REASON-CARTRIDGE-014 — THE COMPLETE OPINION READER

**Research status:** committed and CI-tested read-only **retrieval experiment** stacked on unmerged REASON-013 PR #111 (and the prior draft lineage). Not merged, deployed, a legal advisor, an autonomous judicial analyst or a new machine-learning foundation model.

## The next frontier, without a cherry-picked source excerpt

Previous REASON-013 experiments gave MOTIF **editor-selected portions** of real court opinions. That can inadvertently place the necessary answer in an artificially convenient paragraph.

For REASON-014, the new source acquisition code downloads **the complete body of each Cornell LII Supreme Court opinion reproduction**, reads **every paragraph** including parties' arguments, the majority's opinion, dissenting opinions, procedural history and notes, and stores **both the entire HTML bytes and the entire extracted body**. The reader receives all these paragraphs and **none of the evaluation's answer locations**.

The source is not a cryptographically signed official Supreme Court document: it is a public third-party reproduction. We pin BOTH the original webpage SHA-256 and the canonical extracted full-body SHA-256. A changed page or missing section fails closed and requires a new source review.

### Four source documents: two for development, two not in prior MOTIF cases

| Split | Actual Supreme Court opinion | The unusual problem | Extracted body |
|---|---|---|---:|
| Development | [McBoyle v. United States, 283 U.S. 25 (1931)](https://www.law.cornell.edu/supremecourt/text/283/25) | Does a stolen airplane fit the old motor vehicle theft statute? | 773 words, 15 source paragraphs |
| Development | [Nix v. Hedden, 149 U.S. 304 (1893)](https://www.law.cornell.edu/supremecourt/text/149/304) | Tomato = fruit botanically; vegetable for a particular tariff? | 1,058 words, 25 source paragraphs |
| **Previously unseen** | [United States v. Kirby, 74 U.S. 482 (1868)](https://www.law.cornell.edu/supremecourt/text/74/482) | Can a sheriff arrest a murder-indicted mail carrier without violating the general federal mail-obstruction law? Illustrations involve a bleeding patient and a prison on fire. | 1,544 words, 31 source paragraphs |
| **Previously unseen** | [United States v. Ballard, 322 U.S. 78 (1944)](https://www.law.cornell.edu/supremecourt/text/322/78) | Religious visions, divine messengers and healing claims raised First Amendment and mail-fraud questions. **Justice Douglas's Court opinion; Chief Justice Stone's dissent; Justice Jackson's separate dissent.** | 5,756 words, 56 source paragraphs |

**9,131 words in total, every paragraph used.** The collector retains occasional reproduction metadata/footnotes as part of the audited full body, but marks site license boilerplate as not useful judicial evidence. The full body isn't truncated to hand-curated winning passages.

The corpus is acquired afresh by GitHub Actions and checked against the exact pinned external HTML and extracted text. It is preserved in GitHub Actions artifacts, not committed as a giant file, so plain-local replays require the downloadable source artifact or a live download from those exact URLs. The no-network retriever is deterministic after acquisition.

## What is and is not being tested

- `acquire.py` uses Python's standard-library HTML parser to collect **all** `<p>` elements inside Cornell's judicial `div.bodytext`. It writes the complete original fetched HTML and a structured paragraph register with position, site anchor, SHA-256, word count and source citation.
- `contract.py` pins both raw and extracted SHA-256 for all four source documents; download drift causes an explicit failure, not a silent result change.
- `reader.py` performs **classical BM25 paragraph ranking** (and an ordinary term-overlap comparison) over the full source; unlike the earlier examples, the input has not been reduced to a short informative quote by the operator.
- It detects authorial boundaries from actual text, distinguishing background/advocacy from a justice's opinion and **Stone/Jackson dissents from Douglas's Court opinion**.
- Every retrieved span carries exact paragraph ordinal/anchor, judicial attribution where detected, original source URL, citation, SHA-256 and a warning that a retrieved paragraph is **candidate evidence rather than a holding or judicial fact**.
- Queries with insufficient source vocabulary support **HOLD**. Even plausible evidence queries do **not** trigger unsupported judicial conclusions: the result is `EVIDENCE_CANDIDATES_REQUIRE_REVIEW` with sources, **not** an automated yes/no.
- Retrieval receipts are **replayed from the original complete pinned source**, so bogus quotes, changed citations, spoofed judicial voices and fake authority cannot be laundered by recomputing a checksum.
- `review_keys.py` defines **11 separately curated questions** about Kirby and Ballard, with independently selected short target substrings and expected opinion voice. `reader.py` never imports the labels. Development source cases are **McBoyle and Nix**; Kirby and Ballard had not appeared in the earlier strange-court corpus.

### Actual CI benchmark, not claimed perfection

On 11 source-grounded evaluation questions, the full-document retrieval results were:

| Classical retrieval system | Relevant paragraph in first result | Within top 3 | Within top 5 |
|---|---:|---:|---:|
| **BM25** | **6/11** | **9/11** | **9/11** |
| **Term-overlap baseline** | **7/11** | **9/11** | **9/11** |

These results are intentionally unimpressive relative to a realistic legal expert: **2/11 questions were missed even at top 5** for both retrieval methods. Term-overlap even beat BM25 at rank 1. The experiment therefore does not support a claim of improved retrieval accuracy versus conventional classical methods. The specific misses are preserved in `retrieval-evidence.json` so further changes can be assessed on *new* data rather than tuning against these same heldout examples.

Two irrelevant cheese/fantasy questions returned **HOLD** with no invented source. A separate query asking whether the Court *scientifically proved* supernatural healings receives, at most, source evidence; it never becomes an answer asserting that supernatural claims were scientifically verified.

The 11 questions were prepared by an informed researcher from the public opinions, not an independently recruited human-blind third party. The retrieval rules and scorer do not consume target labels, but source and gold data are inspectable in the repository. Treat this as a transparent, source-grounded engineering benchmark, **not a blinded generalization or legal expertise measure**.

## The particularly instructive Ballard split

The full 5,756-word Court text includes more than one judicial stance:

- **Douglas for the Court:** the Supreme Court rejected submitting the truth of religious doctrines to the jury, and reversed/remanded to the Court of Appeals for issues it had not decided.
- **Stone dissent:** thought the criminal conviction should be reinstated, emphasizing the distinction between religious freedom and knowingly fraudulent representations.
- **Jackson dissent:** warned of the dangers of prosecuting religious experiences or beliefs and would dismiss the indictment.

A reader that retrieves a Stone paragraph and then attributes it to Douglas would be seriously misleading. The system stores those judicial voices separately, but **does not yet independently infer their legal tests from free text**.

Nor is a court's treatment of religious belief a scientific demonstration that a particular miracle either happened or did not happen. It is a statement about adjudication under the historical First Amendment question.

## Reproduce and inspect

```sh
python experiments/reason-cartridge-014/acquire.py reason-014-sources
python -m unittest discover -s experiments/reason-cartridge-014 -p 'test_*.py' -v
python experiments/reason-cartridge-014/trial.py reason-014-sources reason-014-evidence
```

CI: `.github/workflows/reason-cartridge-014.yml`, which also runs inherited REASON-001 through REASON-013 unit tests.

Artifacts:

```
reason-014-full-source-raw-html-and-paragraphs/
  mcboyle.raw.html          # entire downloaded page
  mcboyle.full.json         # all judicial body paragraphs with SHA/anchor
  nix.raw.html / nix.full.json
  kirby.raw.html / kirby.full.json
  ballard.raw.html / ballard.full.json
  manifest.json

reason-014-retrieval-benchmark-and-evidence/
  benchmark.json
  retrieval-evidence.json
```

The source artifact includes the actual full acquired text. The evidence artifact contains exact rank-by-rank targets, which judicial voice was required, and where retrieval missed.

## Falsifiers and next serious work

This passes an **entire-source retrieval** threshold that REASON-013 did not attempt; it does *not* pass an expert-level interpretation threshold.

A sound next vertical would:
1. Freeze new unseen opinions and human-created questions **before** any model or vocabulary development.
2. Use the complete, directly downloaded source documents—some with majority, plurality, concurrence, multiple dissents and complicated remands—and preserve byte-level source pins.
3. Test **full-sentence retrieval**, context/voice agreement, negative/contradictory evidence, and answer abstention together.
4. Benchmark against a serious cross-encoder, modern embedding retrieval, multiple BM25 variants and human legal researchers, not only an overlap baseline.
5. Ask the reasoner to construct **the legal test and its procedural dependency graph**, supported by quoted source spans—while treating missing or disputed reasoning as unproven.
6. Keep real-world legal advice and legal authority out of the experimental output unless separately reviewed for a specific jurisdiction and time.

The next honest improvement is **source-grounded interpretation and explicit uncertainty**, not declaring every retrieval hit to be a court holding.
