# SOURCE COUNCIL 002 — choose which branch deserves investigation

Main's Branch Garden already indexes all Git-visible experimental heads, reads exact pinned source files and can run a specifically approved unmerged test profile. Source Council adds an early **evidence-oriented triage** step so keyword-matching a branch name is not mistaken for learning.

## Run

    python -m unittest discover -s tests -v
    python -m motif.source_council --query "reciprocal" --budget 3

It first enumerates the live full Git head set through the original Branch Garden (not just open PRs). A lexical branch-name first pass yields up to 1–6 leads by explicit budget. For each, it fetches that original head to FETCH_HEAD, verifies the observed SHA, and reads at most four exact original README/DESIGN/VISION/PREREGISTRATION documents. Its score reflects whether question words actually occur in the document. It notes visible test filenames as a lead without executing or claiming a pass.

Unlike the branch-name-only control, the second pass uses real content evidence. No natural-language inference, LLM or algorithm invention is claimed. It is still a deliberately weak retrieval control, not semantic understanding.

## Why it matters

Before: the name "reciprocal" could imply something works. Now: a selected candidate is accompanied by its immutable original commit, separately hashed source documents, the actual query terms found and the explicit distinction between visible test names, passed tests, real-world correctness and owner adoption.

A branch can keep influencing MOTIF's investigations as an unmerged source. Execution needs the separate reviewed no-network runner profile. Reuse as a planning lens needs a reviewed contract. Merge review requires the full independently evidenced and owner-approved promotion policy; this council has **no Git write/merge path**.

## Failures, budgets and research progression

- Stale/moved refs, unavailable documents, binary/non-UTF8 content, excessive source sizes or unrecognized data are HOLD, not guessed.
- A 1–6 branch budget bounds work and avoids silently crawling the entire research forest. All visible heads are discovered, not all their content inspected.
- Branch selection remains lexical and biased toward names, with only a small document corroboration. We need a strong lexical/BM25 and embedding retrieval baseline and external task success outcomes before claiming improvement.
- A source document can contain false claims, malicious directions, fictional results or outdated benchmarks. It is processed as data only; no document is executed or promoted.
- Independent testing, source-owned GRAFT cartridge admission, JAR;VIS integration and automatic candidate PR composition remain distinct future steps.
- Most important remaining falsifier: does this evidence-aware shortlist produce better independently verified methods than simple branch-name retrieval under equal cost and budget? We have not measured that.

**Status:** candidate-retrieval prototype, not autonomous merge selection, not agent autonomy and not proof of self-improving intelligence.
