# MOTIF-023 — THE OPEN QUESTION FIELD

**Status:** Working experimental, two-round read-only *live public GitHub* source-to-research-to-plan-to-compiled-execution-to-feedback-to-new-question circuit. This genuinely extends MOTIF-022's original frozen five-document corpus. It does **not** grant general autonomy, private-source access, production installation, unbounded internet search, autonomous human contact or verified independent witness ancestry.

## What is actually implemented

1. **New question / public collection selection.** The source-owning **ALEX-023** adapter chooses from an explicit allowlist of five independently verified PUBLIC GitHub repositories (MOTIF, ALEX.2, planZ, GRAFT and the-daily-slice) based on words in the operator question or an explicitly chosen subset. It reads at most **two repositories and two small public Markdown files per repository per round**. It fetches the actual live branch commit and tree using the GitHub REST API; reads selected source files at immutable Git **blob** identifiers; independently verifies hashes; returns exact repository/commit/file/line excerpts with partial-coverage and failed-source receipts. A private repository cannot enter just because some user token has access.
2. **Classical source-specific plan.** Original **planZ-023** code receives the newly observed ALEX result and computes a real STRIPS-style minimum-cost plan using the original planZ Dijkstra engine. Different questions and different observed source counts produce different plans. Failed or unsupported source evidence HOLDs.
3. **Compose and RUN a new capability candidate.** Original **GRAFT-023** code replays the plan under the exact original planZ source validator. It constructs deterministic **new ES module source** using only audited program fragments plus the actual validated classical plan metadata. It verifies the expected SHA-256 and executes the reconstructed module locally, returning source-locus observations and actual evidence gaps. User-source content is **never inserted into program code**. This is generated executable candidate code, **not installed production code**.
4. **Observe, revise the plan, ask a BETTER question.** The original planZ REPLAN consumes the actual execution result. It distinguishes a **single-repo or failed-source gap** from a **shared-source independence issue**, computes another minimum-cost question-formation plan, then selects NEW bounded PUBLIC source collections. ALEX performs a second real read; planZ produces its next plan; GRAFT composes and executes a second reviewed module. The cycle is hard-bounded to two rounds. This is actual **new source acquisition based on the previous program's output**, unlike the fixed original MOTIF-021 demonstration.
5. **Original machinery stays intact.** MOTIF-023 inherits byte-pinned original National Treasure and native Dogram via 014–019, the original deterministic MADD Maxhinal 020, and the original 021/022 donor imports. The demonstration produces the original Maxhinal's unresolved custody question without treating creative resemblance as provenance evidence.

### Exact source custody

Six original source-owned code Git blobs are copied into `experiments/023` and verified byte-for-byte before use. The pinned source owners are:

- ALEX.2 `research/023-public-source-observations`, commit `e678b0a0596a6391f92e18b6b8135477ad49658d`;
- planZ `research/023-observation-replanning`, commit `a36ab06e2ac151a03b769bad9162a61946430270`;
- GRAFT `graft/023-observation-composed-capability`, commit `9d02b83bc259ee0eaa68d4e6da7b526d9afc8ee4`.

The original 021 **16** and 022 **7** source code/data SHA checks remain active. The experiment is stacked on MOTIF-022 PR #36. No original source owners' main branches were mutated.

## Example

```sh
node experiments/023/open_field.mjs "Which original Maxhinal Fiber and Pressure chambers preserve source custody?"
```

The first round may select public Maxhinal/ALEX documentation. A source-review program then observes **lack of independently certified source family** and partial coverage. planZ proposes a new question aimed at ALEX/GRAFT or planZ/GRAFT records depending on actually observed gaps; the second round fetches those current public source documents and executes another local review capability.

CI runs eight transport-isolated tests (including private repo refusal, wrong source blob and new-source continuation), plus inherited 021 and 022 tests, then runs the two-round **live** GitHub probe. It must verify at least one real PUBLIC source read and a second actual compiled/replayed capability. The live JSON research result is preserved as a GitHub Actions artifact.

## What this cannot establish

- Public document visibility **is not** permission to redistribute any hidden or private content. Explicit private repository names are refused and the adapter checks visibility before Git blob access.
- Exact source commit and blob **is not** independent human testimony. Two different Git paths may originate from one text source. Source ancestry remains unresolved.
- Live default branch reads represent **one observed moment**. No all-history crawl, GitHub code search, private or non-GitHub connector, arbitrary URL, broad document classification or offline remote source cache is claimed.
- Lexical path/line overlap may miss relevant documents; only two documents per repository are inspected, max 20 result snippets. A search miss is not a source absence.
- No automatic code installation, source-owner admission, open-ended self-modification, unrestricted browsing, human contact or autonomous scheduled execution.
- GitHub authenticated read tokens in CI are ephemeral and not included in outputs.
- The max two-round loop is explicitly limited; no infinite recursion.

**Research may recommend where to look. Planning may propose what to do. GRAFT can execute locally bounded, verified source-owned fragments. None of these steps authenticates human evidence or grants deployment rights.**
