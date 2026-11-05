# REASON-CARTRIDGE-001 — Learn from being schooled

**Status:** isolated experimental branch; source-owned offline synthetic proof. No production integration, external teacher, live tool execution or human field validation.

## The distinction

MOTIF-007 already demonstrates transporting a learned *operator* between simulated worlds. MOTIF-009 already has inspectable decision-tree *cartridges*. This experiment instead asks:

> Can a pupil observe the moments a teacher corrects its *choice of reasoning method*, ask for discriminating new lessons, and export an explicit method-selection program that still works on different problems?

We do **not** acquire the teacher's internal chain-of-thought. The teacher exposes only verifiable **case, initial choice, correction, evidence reference, source-revision**. A private internal explanation is neither necessary nor claimed. The portable cartridge contains *derived rules and hashed correction references*, not raw conversations or teacher software.

## Executable protocol

1. A synthetic **pupil** sees five declared reasoning situations: missing authority, contradictory evidence, stale source, an available exact lookup, or a possible hypothetical plan. Each has a fixed, harmless **read-only advisory move**.
2. The pupil starts without knowing which concern the teacher ranks first. It asks two-signal contrastive questions, receives explicit observed corrections, and learns a transitive precedence graph.
3. If its graph still has an unordered pair, or any correction creates a cycle, it **HOLDs**, asking a new contrast instead of guessing.
4. Once all five priorities are resolved, it emits a strict data-only `motif.reason-cartridge.v1` JSON artifact with typed move names, source revision, count, correction receipt hashes and content checksum.
5. A separate **local receiver** must revalidate source revision, run **withheld independent multifeature cases** and record an explicit review bound to the preview digest before `ADMIT_READ_ONLY`. Admission allows only suggesting an instrument/method, never running one.

`HOLD_FOR_AUTHORITY` is a *synthetic label*, not an identity, consent or authorization system. No actual external access is granted by a method choice.

## Reproduction

Python 3.10+, standard library only:

```sh
python -m unittest discover -s experiments/reason-cartridge-001 -p 'test_*.py' -v
python experiments/reason-cartridge-001/demo.py
```

The teacher fixture and the pupil are separate modules. Teaching uses isolated two-signal cases; **review uses only cases with three, four or five active signals**. Neither pupil inference nor training probes are given the teacher's hidden order, though the evaluator explicitly knows it.

Local baseline on the synthetic fixture: the static alphabetical pupil gets **5/16** withheld composite cases; the learned priority program gets **16/16**; a teacher given the full priority list gets **16/16**. There are at most ten pairwise lessons. The full-knowledge classical teacher matches the learned program: **no superiority over classical sorting/inference is claimed**. These numbers describe a tightly designed toy curriculum, not performance on language tasks.

## What the cartridge can and cannot inherit

It inherits a **specific executable data-only method-routing rule**, not teacher identity, trustworthy authority, private thoughts, a neural policy, tool credentials, arbitrary algorithm synthesis, authenticated provenance or a real-world permission. A SHA-256 digest detects unintentional mutation, not a malicious sender who can recompute it. Its origin is explicitly marked unverified.

The method grammar (five signals and five moves) is developer-supplied. The pupil learns only their **relative priority** from corrective comparisons, not a novel reasoning primitive. That is the experiment's deliberate falsifiable boundary.

Failure cases include unresolved or inconsistent comparisons, duplicate or malformed lessons, unexpected signals, stale source revisions, schema injection, rehashed corrupted priority programs, privilege escalation, missing review and modified preview digest.

## Next vertical: teach the teacher's *procedure*, not just its priority

The natural next experiment would allow an independent, source-pinned teacher (ALEX, Dogram, classical lookup, T5 critic or human expert) to contribute **public, explicitly volunteered inspectable procedure traces**. Compete typed candidate programs against rote caching and a strong classical baseline on unfamiliar tasks, independently falsify them, then propose portable `reason-cartridge` programs to the Door Foundry/GRAFT under their own owner-led review. No native integration with these projects is implemented here. Any permission to run a real tool must be separately negotiated.

**Do not merge or deploy automatically.** This branch is a research slice for review.
